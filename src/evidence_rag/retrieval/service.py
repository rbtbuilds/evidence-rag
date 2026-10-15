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

    def retrieve(self, scope: AccessScope, question: str, mode: RetrievalMode) -> list[Candidate]:
        if len(question) > 500:
            raise DomainError(413, "limit_exceeded")
        if not tokens(question):
            return []
        if mode == "bm25":
            return lexical(self.repo, scope, question)[:5]
        if mode == "dense":
            return dense(self.repo, scope, question, self.embedder)[:5]
        combined = rrf(
            [lexical(self.repo, scope, question), dense(self.repo, scope, question, self.embedder)]
        )[:20]
        if mode == "hybrid_rerank":
            combined = rerank(question, combined, self.reranker)
        return combined[:5]
