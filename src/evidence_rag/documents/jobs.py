import asyncio
import sqlite3
from collections.abc import Callable
from datetime import UTC, datetime
from typing import Literal
from uuid import uuid4

from evidence_rag.contracts import ImportInput, JobView, RebuildInput, ReplaceInput, VersionInput
from evidence_rag.db.repository import Repository
from evidence_rag.documents.chunking import Chunk, chunk_document
from evidence_rag.errors import DomainError
from evidence_rag.models.fixture import FixtureEmbedder
from evidence_rag.retrieval.service import build_index
from evidence_rag.retrieval.types import IndexDraft

JobKind = Literal["import", "replace", "rebuild"]


def now() -> str:
    return datetime.now(UTC).isoformat()


def fixture_builder(chunks: tuple[Chunk, ...]) -> IndexDraft:
    return build_index(chunks, FixtureEmbedder())


class JobService:
    def __init__(
        self,
        repo: Repository,
        lock: asyncio.Lock,
        builder: Callable[[tuple[Chunk, ...]], IndexDraft] = fixture_builder,
    ) -> None:
        self.repo, self.lock, self.builder = repo, lock, builder
        self.current_job_id: str | None = None
        self.cancel_models: Callable[[], None] = lambda: None
        self.wake = asyncio.Event()
        self.task: asyncio.Task[None] | None = None

    def start(self) -> None:
        with self.repo.transaction() as db:
            db.execute(
                "UPDATE jobs SET status='interrupted',error_code='interrupted',payload_json=NULL,updated_at=? WHERE status='running'",
                (now(),),
            )
        self.task = asyncio.create_task(self.work())
        self.wake.set()

    async def stop(self) -> None:
        self.cancel_models()
        if self.task:
            self.task.cancel()
            try:
                await self.task
            except asyncio.CancelledError:
                pass

    def enqueue(
        self,
        kind: JobKind,
        request: ImportInput | ReplaceInput | RebuildInput,
        document_id: str | None = None,
    ) -> str:
        job_id = str(uuid4())
        target = document_id or (str(uuid4()) if kind == "import" else None)
        revision = request.expected_revision if isinstance(request, ReplaceInput) else 0
        with self.repo.transaction() as db:
            pending = db.execute(
                "SELECT kind,payload_json FROM jobs WHERE status IN ('queued','running')"
            ).fetchall()
            if len(pending) >= 8:
                raise DomainError(429, "queue_full")
            if kind == "replace":
                doc = db.execute(
                    "SELECT * FROM documents WHERE id=? AND deleted_at IS NULL", (target,)
                ).fetchone()
                if doc is None:
                    raise DomainError(404, "not_found")
                if doc["revision"] != revision:
                    raise DomainError(409, "revision_conflict")
            if isinstance(request, VersionInput):
                staged = 0
                staged_bytes = 0
                staged_versions = 0
                for row in pending:
                    if row["payload_json"] and row["payload_json"] != "{}":
                        item = VersionInput.model_validate_json(row["payload_json"])
                        staged += len(chunk_document("admission", item.markdown))
                        staged_bytes += len(item.markdown.encode())
                        staged_versions += 1
                retained_bytes = db.execute(
                    "SELECT coalesce(sum(length(cast(text AS BLOB))),0) FROM versions"
                ).fetchone()[0]
                versions = db.execute("SELECT count(*) FROM versions").fetchone()[0]
                documents = db.execute("SELECT count(*) FROM documents").fetchone()[0]
                imports = sum(row["kind"] == "import" for row in pending)
                if (
                    retained_bytes + staged_bytes + len(request.markdown.encode())
                    > 20 * 1024 * 1024
                    or versions + staged_versions + 1 > 200
                    or (kind == "import" and documents + imports + 1 > 50)
                ):
                    raise DomainError(413, "limit_exceeded")
                active = db.execute("SELECT count(*) FROM chunks").fetchone()[0]
                if active + staged + len(chunk_document("admission", request.markdown)) > 2000:
                    raise DomainError(413, "limit_exceeded")
            payload = request.model_dump(exclude={"expected_revision"})
            import json

            db.execute(
                "INSERT INTO jobs VALUES(?,?,?,?, 'queued',?,NULL,?,?)",
                (job_id, kind, target, revision, json.dumps(payload), now(), now()),
            )
        self.wake.set()
        return job_id

    def view(self, job_id: str) -> JobView:
        with self.repo.connection() as db:
            row = db.execute(
                "SELECT id,status,error_code,created_at,updated_at FROM jobs WHERE id=?", (job_id,)
            ).fetchone()
        if row is None:
            raise DomainError(404, "not_found")
        return JobView.model_validate(dict(row))

    def cancel(self, job_id: str) -> JobView:
        self.view(job_id)
        with self.repo.transaction() as db:
            db.execute(
                "UPDATE jobs SET status='cancelled',payload_json=NULL,updated_at=? WHERE id=? AND status IN ('queued','running')",
                (now(), job_id),
            )
        if job_id == self.current_job_id:
            self.cancel_models()
        return self.view(job_id)

    def cancel_document(self, document_id: str) -> None:
        with self.repo.connection() as db:
            row = db.execute(
                "SELECT document_id FROM jobs WHERE id=?", (self.current_job_id,)
            ).fetchone()
        if row is not None and row["document_id"] == document_id:
            self.cancel_models()

    async def work(self) -> None:
        while True:
            await self.wake.wait()
            self.wake.clear()
            while True:
                with self.repo.connection() as db:
                    row = db.execute(
                        "SELECT id FROM jobs WHERE status='queued' ORDER BY created_at,id LIMIT 1"
                    ).fetchone()
                if row is None:
                    break
                await self.run_one(str(row["id"]))

    async def run_one(self, job_id: str) -> None:
        with self.repo.transaction() as db:
            if (
                db.execute(
                    "UPDATE jobs SET status='running',updated_at=? WHERE id=? AND status='queued'",
                    (now(), job_id),
                ).rowcount
                != 1
            ):
                return
            row = db.execute("SELECT * FROM jobs WHERE id=?", (job_id,)).fetchone()
        self.current_job_id = job_id
        try:
            if row["kind"] == "rebuild":
                with self.repo.connection() as db:
                    snapshot = db.execute(
                        "SELECT d.id,d.revision,d.active_version_id,v.text FROM documents d JOIN versions v ON d.active_version_id=v.id WHERE d.deleted_at IS NULL ORDER BY d.id"
                    ).fetchall()
                    epoch = tuple(
                        db.execute("SELECT reader_epoch,maintainer_epoch FROM meta").fetchone()
                    )
                all_chunks = tuple(
                    c
                    for r in snapshot
                    for c in chunk_document(str(r["active_version_id"]), str(r["text"]))
                )
                combined = (
                    await asyncio.to_thread(self.builder, all_chunks)
                    if all_chunks
                    else IndexDraft((), (), "empty")
                )
                pairs = list(zip(combined.chunks, combined.vectors, strict=True))
                drafts = [
                    IndexDraft(
                        tuple(c for c, _ in pairs if c.version_id == r["active_version_id"]),
                        tuple(v for c, v in pairs if c.version_id == r["active_version_id"]),
                        combined.revision,
                    )
                    for r in snapshot
                ]
                async with self.lock:
                    with self.repo.transaction() as db:
                        self.require_running(db, job_id)
                        current = db.execute(
                            "SELECT id,revision,active_version_id FROM documents WHERE deleted_at IS NULL AND active_version_id IS NOT NULL ORDER BY id"
                        ).fetchall()
                        if [tuple(r) for r in current] != [
                            (r["id"], r["revision"], r["active_version_id"]) for r in snapshot
                        ] or epoch != tuple(
                            db.execute("SELECT reader_epoch,maintainer_epoch FROM meta").fetchone()
                        ):
                            raise DomainError(409, "stale_job")
                        for source, draft in zip(snapshot, drafts, strict=True):
                            self.repo.replace_index(db, str(source["id"]), draft)
                        self.repo.invalidate(db, "reader", "reader")
                        self.succeed(db, job_id)
            else:
                metadata = VersionInput.model_validate_json(row["payload_json"])
                draft = await asyncio.to_thread(
                    self.builder, chunk_document(str(uuid4()), metadata.markdown)
                )
                async with self.lock:
                    with self.repo.transaction() as db:
                        self.require_running(db, job_id)
                        self.repo.publish_in_transaction(
                            db,
                            str(row["document_id"]),
                            int(row["expected_revision"]),
                            draft,
                            metadata,
                        )
                        self.succeed(db, job_id)
        except (DomainError, ValueError, sqlite3.Error) as error:
            code = error.code if isinstance(error, DomainError) else "index_failed"
            with self.repo.transaction() as db:
                db.execute(
                    "UPDATE jobs SET status='failed',error_code=?,payload_json=NULL,updated_at=? WHERE id=? AND status='running'",
                    (code, now(), job_id),
                )
        except Exception:  # noqa: BLE001 - redact unexpected builder failures at the job boundary.
            with self.repo.transaction() as db:
                db.execute(
                    "UPDATE jobs SET status='failed',error_code='index_failed',payload_json=NULL,updated_at=? WHERE id=? AND status='running'",
                    (now(), job_id),
                )

        finally:
            self.current_job_id = None

    def require_running(self, db: sqlite3.Connection, job_id: str) -> None:
        row = db.execute("SELECT status FROM jobs WHERE id=?", (job_id,)).fetchone()
        if row is None or row["status"] != "running":
            raise DomainError(409, "stale_job")

    def succeed(self, db: sqlite3.Connection, job_id: str) -> None:
        db.execute(
            "UPDATE jobs SET status='succeeded',payload_json=NULL,updated_at=? WHERE id=?",
            (now(), job_id),
        )
