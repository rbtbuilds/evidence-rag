import time
from collections.abc import Callable

from evidence_rag.contracts import RetrievalMode
from evidence_rag.db.repository import AccessScope, Repository
from evidence_rag.documents.chunking import Chunk
from evidence_rag.errors import DomainError
from evidence_rag.models.fixture import tokens
from evidence_rag.models.protocols import Embedder, Reranker
from evidence_rag.retrieval.dense import dense
from evidence_rag.retrieval.fusion import rrf
from evidence_rag.retrieval.lexical import lexical
from evidence_rag.retrieval.rerank import rerank
from evidence_rag.retrieval.types import Candidate, IndexDraft


def build_index(chunks: tuple[Chunk, ...], embedder: Embedder) -> IndexDraft:
    return IndexDraft(chunks, embedder.embed([chunk.text for chunk in chunks]), embedder.revision)


class Retriever:
    def __init__(self, repo: Repository, embedder: Embedder, reranker: Reranker) -> None:
        self.repo, self.embedder, self.reranker = repo, embedder, reranker
        self.timings_ms: dict[str, float] = {}

    def measure(self, name: str, action: Callable[[], list[Candidate]]) -> list[Candidate]:
        start = time.perf_counter()
        result = action()
        self.timings_ms[name] = (time.perf_counter() - start) * 1000
        return result

    def retrieve(self, scope: AccessScope, question: str, mode: RetrievalMode) -> list[Candidate]:
        self.timings_ms = {}
        if len(question) > 500:
            raise DomainError(413, "limit_exceeded")
        if not tokens(question):
            return []
        lexical_items = (
            self.measure("lexical", lambda: lexical(self.repo, scope, question))
            if mode != "dense"
            else []
        )
        if mode == "bm25":
            return lexical_items[:5]
        dense_items = self.measure(
            "dense", lambda: dense(self.repo, scope, question, self.embedder)
        )
        if mode == "dense":
            return dense_items[:5]
        combined = self.measure("fusion", lambda: rrf([lexical_items, dense_items]))[:20]
        if mode == "hybrid_rerank":
            combined = self.measure("rerank", lambda: rerank(question, combined, self.reranker))
        return combined[:5]
