import hashlib
import json
import time
from dataclasses import asdict, dataclass

from evidence_rag.contracts import Answer, QuestionRequest
from evidence_rag.db.repository import AccessScope, Repository
from evidence_rag.errors import DomainError


@dataclass(frozen=True)
class RevisionSet:
    chunker: str
    embedding: str
    reranker: str
    generator: str
    prompt: str
    profile: str


class Cache:
    def __init__(self, repo: Repository) -> None:
        self.repo = repo

    def key(self, scope: AccessScope, request: QuestionRequest, revisions: RevisionSet) -> str:
        payload = {
            "scope": asdict(scope),
            "request": request.model_dump(),
            "revisions": asdict(revisions),
        }
        return hashlib.sha256(json.dumps(payload, sort_keys=True).encode()).hexdigest()

    def get(self, scope: AccessScope, key: str) -> Answer | None:
        with self.repo.connection() as db:
            row = db.execute(
                "SELECT payload_json FROM answer_cache WHERE key=? AND user_id=? AND role=? AND epoch=? AND expires_at>?",
                (key, scope.user_id, scope.role, scope.epoch, time.time()),
            ).fetchone()
        if row is None:
            return None
        try:
            answer = Answer.model_validate_json(row["payload_json"])
            self.repo.check_citations(scope, [c.chunk_id for c in answer.citations])
            return answer
        except (ValueError, DomainError):
            return None

    def put(self, scope: AccessScope, key: str, answer: Answer) -> None:
        with self.repo.transaction() as db:
            db.execute("DELETE FROM answer_cache WHERE expires_at<=?", (time.time(),))
            db.execute("DELETE FROM answer_cache WHERE key=?", (key,))
            if db.execute("SELECT count(*) FROM answer_cache").fetchone()[0] >= 128:
                db.execute(
                    "DELETE FROM answer_cache WHERE key=(SELECT key FROM answer_cache ORDER BY expires_at,key LIMIT 1)"
                )
            db.execute(
                "INSERT INTO answer_cache VALUES(?,?,?,?,?,?)",
                (
                    key,
                    scope.user_id,
                    scope.role,
                    scope.epoch,
                    answer.model_dump_json(),
                    time.time() + 300,
                ),
            )
