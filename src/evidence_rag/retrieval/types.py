from dataclasses import dataclass

from evidence_rag.documents.chunking import Chunk


@dataclass(frozen=True)
class IndexDraft:
    chunks: tuple[Chunk, ...]
    vectors: tuple[tuple[float, ...], ...]
    revision: str


@dataclass(frozen=True)
class Candidate:
    chunk_id: str
    section_id: str
    text: str
    score: float
