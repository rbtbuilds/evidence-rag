import os
import secrets
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path

import psutil
from pydantic import BaseModel

from evidence_rag.errors import DomainError

LEASE_PATH = Path("/tmp/bentolabs-portfolio-ml.lock")


class ModelBusy(DomainError):
    def __init__(self) -> None:
        super().__init__(503, "model_busy", "Another model operation owns the machine lease.")


class Owner(BaseModel):
    project: str
    pid: int
    started_at: str
    process_started_at: float
    purpose: str
    token: str


@dataclass
class LeaseHandle:
    path: Path
    token: str
    closed: bool = False

    def close(self) -> None:
        if self.closed:
            return
        stored = Owner.model_validate_json((self.path / "owner.json").read_text())
        if stored.token != self.token or stored.pid != os.getpid():
            raise RuntimeError("Refusing to release a different lease owner")
        (self.path / "owner.json").unlink()
        self.path.rmdir()
        self.closed = True


class ModelLease:
    def __init__(self, path: Path = LEASE_PATH) -> None:
        self.path = path

    def acquire(self, purpose: str) -> LeaseHandle:
        try:
            self.path.mkdir(mode=0o700)
        except FileExistsError as error:
            raise ModelBusy() from error
        token = secrets.token_hex(32)
        owner = Owner(
            project="evidence-rag",
            pid=os.getpid(),
            started_at=datetime.now(UTC).isoformat(),
            process_started_at=psutil.Process().create_time(),
            purpose=purpose,
            token=token,
        )
        try:
            (self.path / "owner.json").write_text(owner.model_dump_json())
        except BaseException:
            self.path.rmdir()
            raise
        return LeaseHandle(self.path, token)
