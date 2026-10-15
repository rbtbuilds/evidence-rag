import numpy as np

from evidence_rag.db.repository import AccessScope, Repository
from evidence_rag.errors import DomainError
from evidence_rag.models.protocols import Embedder
from evidence_rag.retrieval.types import Candidate


def dense(
    repo: Repository, scope: AccessScope, question: str, embedder: Embedder
) -> list[Candidate]:
    with repo.connection() as db:
        rows = db.execute(
            "SELECT c.id,c.section_id,c.text,x.vector,x.model_revision FROM vectors x JOIN chunks c ON x.chunk_id=c.id JOIN versions v ON c.version_id=v.id JOIN documents d ON v.document_id=d.id AND d.active_version_id=v.id WHERE v.status='active' AND d.deleted_at IS NULL AND (?='maintainer' OR d.min_role='reader')",
            (scope.role,),
        ).fetchall()
    if any(row["model_revision"] != embedder.revision for row in rows):
        raise DomainError(
            503,
            "model_unavailable",
            "Index revision differs from selected embedding model; rebuild explicitly.",
        )
    if not rows:
        return []
    query = np.asarray(embedder.embed([question], is_query=True)[0], dtype=np.float32)
    if query.shape != (384,) or not np.isfinite(query).all() or np.linalg.norm(query) == 0:
        raise DomainError(503, "model_unavailable")
    query = query / np.linalg.norm(query)
    candidates: list[Candidate] = []
    for row in rows:
        vector = np.frombuffer(row["vector"], dtype=np.float32)
        if not np.isfinite(vector).all() or not np.isclose(np.linalg.norm(vector), 1, atol=1e-4):
            raise DomainError(503, "model_unavailable")
        candidates.append(
            Candidate(
                str(row["id"]),
                str(row["section_id"]),
                str(row["text"]),
                float(np.dot(vector, query)),
            )
        )
    return sorted(candidates, key=lambda c: (-c.score, c.chunk_id))[:20]
