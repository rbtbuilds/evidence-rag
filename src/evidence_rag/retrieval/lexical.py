from evidence_rag.db.repository import AccessScope, Repository
from evidence_rag.models.fixture import tokens
from evidence_rag.retrieval.types import Candidate


def lexical(repo: Repository, scope: AccessScope, question: str) -> list[Candidate]:
    query = " OR ".join('"' + token + '"' for token in tokens(question)[:32])
    if not query:
        return []
    table = "fts_reader" if scope.role == "reader" else "fts_maintainer"
    with repo.connection() as db:
        rows = db.execute(
            f"SELECT c.id,c.section_id,c.text,bm25({table}) score FROM {table} JOIN chunks c ON c.id={table}.chunk_id JOIN versions v ON c.version_id=v.id JOIN documents d ON v.document_id=d.id AND d.active_version_id=v.id WHERE {table} MATCH ? AND v.status='active' AND d.deleted_at IS NULL AND (?='maintainer' OR d.min_role='reader') ORDER BY score,c.id LIMIT 20",
            (query, scope.role),
        ).fetchall()
    return [
        Candidate(str(row["id"]), str(row["section_id"]), str(row["text"]), float(row["score"]))
        for row in rows
    ]
