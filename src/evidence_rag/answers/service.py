import time
from collections.abc import Callable
from dataclasses import dataclass
from uuid import uuid4

from evidence_rag.answers.cache import Cache, RevisionSet
from evidence_rag.answers.generation import (
    GENERATOR_REVISION,
    PROMPT_REVISION,
    Generated,
    extractive,
    validate_generation,
)
from evidence_rag.config import Settings
from evidence_rag.contracts import Answer, Citation, QuestionRequest
from evidence_rag.db.repository import AccessScope, Repository
from evidence_rag.documents.chunking import CHUNKER_REVISION
from evidence_rag.errors import DomainError
from evidence_rag.models.fixture import FixtureEmbedder, FixtureReranker
from evidence_rag.models.local import generation_revision, snapshots
from evidence_rag.models.runner import ModelRunner, ModelSession
from evidence_rag.retrieval.service import Retriever


@dataclass(frozen=True)
class PendingAnswer:
    scope: AccessScope
    answer: Answer
    key: str
    retrieved_sections: tuple[str, ...] = ()
    retrieved_chunk_ids: tuple[str, ...] = ()


class AnswerService:
    def __init__(self, repo: Repository, settings: Settings) -> None:
        self.repo, self.settings, self.cache = repo, settings, Cache(repo)
        self.generator: Callable[[str, list[Citation]], Generated] = extractive
        self.runner = ModelRunner(settings.root)

    def revisions(self, request: QuestionRequest) -> RevisionSet:
        embedding, reranker, generator = (
            FixtureEmbedder.revision,
            FixtureReranker.revision,
            GENERATOR_REVISION,
        )
        if self.settings.profile == "local":
            lock = snapshots(self.settings.root)
            embedding = "bge:" + lock.models["embedding"].revision
            reranker = "minilm:" + lock.models["reranker"].revision
            if request.generation_mode == "local":
                generator = generation_revision(lock)
        return RevisionSet(
            CHUNKER_REVISION, embedding, reranker, generator, PROMPT_REVISION, self.settings.profile
        )

    def answer(
        self, scope: AccessScope, request: QuestionRequest, session: ModelSession | None = None
    ) -> PendingAnswer:
        if request.generation_mode == "local" and self.settings.profile == "fixture":
            raise DomainError(422, "mode_unavailable")
        revisions = self.revisions(request)
        key = self.cache.key(scope, request, revisions)
        cached = self.cache.get(scope, key)
        if cached:
            return PendingAnswer(scope, cached.model_copy(update={"request_id": str(uuid4())}), key)
        if self.settings.profile == "local" and session is None:
            with self.runner.session("interactive evidence question") as model:
                return self.compute(scope, request, key, model)
        return self.compute(scope, request, key, session)

    def compute(
        self, scope: AccessScope, request: QuestionRequest, key: str, session: ModelSession | None
    ) -> PendingAnswer:
        begin = time.perf_counter()
        retriever = Retriever(self.repo, session or FixtureEmbedder(), session or FixtureReranker())
        candidates = retriever.retrieve(scope, request.question, request.retrieval_mode)
        retrieved = time.perf_counter()
        try:
            citations = self.repo.check_citations(scope, [c.chunk_id for c in candidates])
        except DomainError as error:
            raise DomainError(409, "corpus_changed") from error
        if request.generation_mode == "local":
            if session is None:
                raise DomainError(422, "mode_unavailable")
            if not citations:
                generated = Generated("", [], True, "insufficient_evidence")
            else:
                result = session.generate(request.question, citations)
                kept = citations[: len(citations) - result.dropped_passages]
                generated = validate_generation(result.output, kept)
        else:
            generated = self.generator(request.question, citations)
        answer = Answer(
            request_id=str(uuid4()),
            execution_profile=self.settings.profile,
            retrieval_mode=request.retrieval_mode,
            generation_mode=request.generation_mode,
            answer=generated.text,
            abstained=generated.abstained,
            reason=generated.reason,
            citations=generated.citations,
            timings_ms={
                **retriever.timings_ms,
                "retrieval": (retrieved - begin) * 1000,
                "generation": (time.perf_counter() - retrieved) * 1000,
            },
        )
        return PendingAnswer(
            scope,
            answer,
            key,
            tuple(c.section_id for c in candidates),
            tuple(c.chunk_id for c in candidates),
        )
