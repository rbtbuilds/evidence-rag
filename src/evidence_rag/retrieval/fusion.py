from collections.abc import Sequence
from dataclasses import replace

from evidence_rag.retrieval.types import Candidate


def rrf(rankings: Sequence[Sequence[Candidate]], k: int = 60) -> list[Candidate]:
    scores: dict[str, float] = {}
    items: dict[str, Candidate] = {}
    for ranking in rankings:
        unique = list({item.chunk_id: item for item in ranking}.values())
        for rank, item in enumerate(unique, 1):
            items[item.chunk_id] = item
            scores[item.chunk_id] = scores.get(item.chunk_id, 0) + 1 / (k + rank)
    return [
        replace(items[key], score=scores[key])
        for key in sorted(scores, key=lambda key: (-scores[key], key))
    ]
