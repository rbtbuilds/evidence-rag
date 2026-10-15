import hashlib
import json
import os
import secrets
import time
from dataclasses import dataclass
from pathlib import Path

from pydantic import TypeAdapter

from evidence_rag.contracts import Role
from evidence_rag.db.repository import Repository
from evidence_rag.errors import DomainError


@dataclass(frozen=True)
class SessionBundle:
    session_id: str
    csrf_token: str
    user_id: str
    role: Role


def initialize(root: Path, *, reset: bool = False) -> dict[Role, str]:
    repo = Repository(root / "evidence.sqlite3")
    target = root / "demo-codes.json"
    if target.exists() and not reset:
        raise DomainError(
            409,
            "already_initialized",
            "Launch codes already exist; use explicit reset to revoke old sessions.",
        )
    codes: dict[Role, str] = {
        "reader": secrets.token_urlsafe(32),
        "maintainer": secrets.token_urlsafe(32),
    }
    digests = {role: hashlib.sha256(value.encode()).hexdigest() for role, value in codes.items()}
    temp = target.with_suffix(".tmp")
    fd = os.open(temp, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, "w") as handle:
        json.dump(digests, handle)
    os.replace(temp, target)
    with repo.transaction() as db:
        db.execute("DELETE FROM sessions")
    return codes


class SessionService:
    def __init__(self, repo: Repository) -> None:
        self.repo = repo

    def login(self, code: str) -> SessionBundle:
        path = self.repo.path.parent / "demo-codes.json"
        stored = (
            TypeAdapter(dict[str, str]).validate_json(path.read_text()) if path.exists() else {}
        )
        digest = hashlib.sha256(code.encode()).hexdigest()
        role: Role | None = None
        for candidate in ("reader", "maintainer"):
            if secrets.compare_digest(stored.get(candidate, "0" * 64), digest):
                role = candidate
        if role is None:
            raise DomainError(
                401, "invalid_code", "Use a launch code printed by the local init command."
            )
        token, csrf = secrets.token_urlsafe(32), secrets.token_urlsafe(32)
        with self.repo.transaction() as db:
            db.execute(
                "INSERT INTO sessions VALUES(?,?,?,?)",
                (hashlib.sha256(token.encode()).hexdigest(), role, csrf, time.time() + 3600),
            )
        return SessionBundle(token, csrf, role, role)

    def logout(self, token: str) -> None:
        with self.repo.transaction() as db:
            db.execute(
                "DELETE FROM sessions WHERE token_hash=?",
                (hashlib.sha256(token.encode()).hexdigest(),),
            )
