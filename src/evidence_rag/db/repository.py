import hashlib
import sqlite3
import time
from collections.abc import Generator
from contextlib import closing, contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import cast

from evidence_rag.contracts import Role
from evidence_rag.errors import DomainError


@dataclass(frozen=True)
class AccessScope:
    user_id: str
    role: Role
    epoch: int


class Repository:
    def __init__(self, path: Path) -> None:
        self.path = path
        path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        with closing(self.connect()) as db:
            db.execute("PRAGMA journal_mode=WAL")
            if (
                db.execute("SELECT 1 FROM sqlite_master WHERE name='schema_migrations'").fetchone()
                is None
            ):
                sql = (Path(__file__).parent / "migrations/001_initial.sql").read_text()
                db.executescript("BEGIN IMMEDIATE;\n" + sql + "\nCOMMIT;")

    def connect(self) -> sqlite3.Connection:
        db = sqlite3.connect(self.path, timeout=5, isolation_level=None)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys=ON")
        db.execute("PRAGMA busy_timeout=5000")
        return db

    @contextmanager
    def transaction(self) -> Generator[sqlite3.Connection]:
        db = self.connect()
        try:
            db.execute("BEGIN IMMEDIATE")
            yield db
            db.execute("COMMIT")
        except BaseException:
            db.execute("ROLLBACK")
            raise
        finally:
            db.close()

    def resolve_scope(self, session_id: str) -> AccessScope:
        digest = hashlib.sha256(session_id.encode()).hexdigest()
        with closing(self.connect()) as db:
            row = db.execute(
                "SELECT u.id,u.role,m.reader_epoch,m.maintainer_epoch FROM sessions s JOIN users u ON u.id=s.user_id CROSS JOIN meta m WHERE s.token_hash=? AND s.expires_at>? AND u.enabled=1",
                (digest, time.time()),
            ).fetchone()
        if row is None:
            raise DomainError(401, "session_required")
        role = cast(Role, row["role"])
        return AccessScope(str(row["id"]), role, int(row[f"{role}_epoch"]))

    def csrf(self, session_id: str) -> str:
        self.resolve_scope(session_id)
        with closing(self.connect()) as db:
            row = db.execute(
                "SELECT csrf_token FROM sessions WHERE token_hash=?",
                (hashlib.sha256(session_id.encode()).hexdigest(),),
            ).fetchone()
        if row is None:
            raise DomainError(401, "session_required")
        return str(row["csrf_token"])
