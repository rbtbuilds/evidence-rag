import math
from dataclasses import replace

from evidence_rag.errors import DomainError
from evidence_rag.models.protocols import Reranker
from evidence_rag.retrieval.types import Candidate


def rerank(question: str, items: list[Candidate], model: Reranker) -> list[Candidate]:
    if not items:
        return []
    scores = model.rerank(question, [item.text for item in items[:20]])
    if len(scores) != len(items[:20]) or any(not math.isfinite(s) for s in scores):
        raise DomainError(503, "model_unavailable")
    return sorted(
        [replace(item, score=score) for item, score in zip(items[:20], scores, strict=True)],
        key=lambda c: (-c.score, c.chunk_id),
    )
