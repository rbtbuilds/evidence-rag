import hashlib
import sqlite3
import time
from collections.abc import Generator
from contextlib import closing, contextmanager
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import cast
from uuid import UUID

import numpy as np

from evidence_rag.contracts import (
    Citation,
    CitationView,
    DocumentSummary,
    DocumentView,
    Role,
    VersionInput,
)
from evidence_rag.errors import DomainError
from evidence_rag.retrieval.types import IndexDraft


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
    def connection(self) -> Generator[sqlite3.Connection]:
        with closing(self.connect()) as db:
            yield db

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

    def _invalidate(self, db: sqlite3.Connection, old: str | None, new: str | None) -> None:
        roles = ("reader", "maintainer") if "reader" in (old, new) else ("maintainer",)
        for role in roles:
            db.execute(f"UPDATE meta SET {role}_epoch={role}_epoch+1")
            db.execute("DELETE FROM answer_cache WHERE role=?", (role,))

    def _remove_indexes(self, db: sqlite3.Connection, document_id: str) -> None:
        for table in ("fts_reader", "fts_maintainer"):
            db.execute(
                f"DELETE FROM {table} WHERE chunk_id IN (SELECT c.id FROM chunks c JOIN versions v ON c.version_id=v.id WHERE v.document_id=?)",
                (document_id,),
            )
        db.execute(
            "DELETE FROM chunks WHERE version_id IN (SELECT id FROM versions WHERE document_id=?)",
            (document_id,),
        )

    def publish(
        self, document_id: str, expected_revision: int, draft: IndexDraft, metadata: VersionInput
    ) -> int:
        with self.transaction() as db:
            return self.publish_in_transaction(db, document_id, expected_revision, draft, metadata)

    def publish_in_transaction(
        self,
        db: sqlite3.Connection,
        document_id: str,
        expected_revision: int,
        draft: IndexDraft,
        metadata: VersionInput,
    ) -> int:
        UUID(document_id)
        if not draft.chunks or len(draft.chunks) != len(draft.vectors):
            raise ValueError("Incomplete draft")
        version = draft.chunks[0].version_id
        UUID(version)
        vectors: list[bytes] = []
        for chunk, vector in zip(draft.chunks, draft.vectors, strict=True):
            a = np.asarray(vector, dtype=np.float32)
            if (
                a.shape != (384,)
                or not np.isfinite(a).all()
                or not np.isclose(np.linalg.norm(a), 1, atol=1e-4)
            ):
                raise ValueError("Invalid normalized embedding")
            if (
                chunk.version_id != version
                or metadata.markdown[chunk.start_char : chunk.end_char] != chunk.text
            ):
                raise ValueError("Draft does not match source")
            vectors.append(a.tobytes())
        old = db.execute("SELECT * FROM documents WHERE id=?", (document_id,)).fetchone()
        if (
            old is None
            and expected_revision != 0
            or old is not None
            and (old["revision"] != expected_revision or old["deleted_at"] is not None)
        ):
            raise DomainError(409, "revision_conflict")
        if db.execute(
            "SELECT 1 FROM versions WHERE document_id=? AND label=?", (document_id, metadata.label)
        ).fetchone():
            raise DomainError(409, "revision_conflict", "Version label already exists.")
        count = db.execute("SELECT count(*) FROM documents").fetchone()[0]
        versions = db.execute("SELECT count(*) FROM versions").fetchone()[0]
        size = db.execute(
            "SELECT coalesce(sum(length(cast(text AS BLOB))),0) FROM versions"
        ).fetchone()[0]
        chunks = db.execute(
            "SELECT count(*) FROM chunks WHERE version_id NOT IN (SELECT id FROM versions WHERE document_id=?)",
            (document_id,),
        ).fetchone()[0]
        if (
            (old is None and count >= 50)
            or versions >= 200
            or size + len(metadata.markdown.encode()) > 20 * 1024 * 1024
            or chunks + len(draft.chunks) > 2000
        ):
            raise DomainError(413, "limit_exceeded")
        if old is None:
            db.execute(
                "INSERT INTO documents VALUES(?,?,?,NULL,NULL,0)",
                (document_id, metadata.title, metadata.min_role),
            )
        self._remove_indexes(db, document_id)
        db.execute(
            "UPDATE versions SET status='superseded' WHERE document_id=? AND status='active'",
            (document_id,),
        )
        db.execute(
            "INSERT INTO versions VALUES(?,?,?,?, 'active',?,?)",
            (
                version,
                document_id,
                metadata.label,
                metadata.effective_date,
                metadata.markdown,
                hashlib.sha256(metadata.markdown.encode()).hexdigest(),
            ),
        )
        for chunk, vector in zip(draft.chunks, vectors, strict=True):
            db.execute(
                "INSERT INTO chunks VALUES(?,?,?,?,?,?)",
                (chunk.id, version, chunk.section_id, chunk.start_char, chunk.end_char, chunk.text),
            )
            db.execute("INSERT INTO vectors VALUES(?,?,384,?)", (chunk.id, draft.revision, vector))
            for table in (
                ("fts_reader", "fts_maintainer")
                if metadata.min_role == "reader"
                else ("fts_maintainer",)
            ):
                db.execute(
                    f"INSERT INTO {table}(chunk_id,text) VALUES(?,?)", (chunk.id, chunk.text)
                )
        db.execute(
            "UPDATE documents SET title=?,min_role=?,active_version_id=?,revision=revision+1 WHERE id=?",
            (metadata.title, metadata.min_role, version, document_id),
        )
        self._invalidate(db, str(old["min_role"]) if old else None, metadata.min_role)
        return expected_revision + 1

    def delete(self, document_id: str, expected_revision: int) -> None:
        with self.transaction() as db:
            row = db.execute(
                "SELECT * FROM documents WHERE id=? AND deleted_at IS NULL", (document_id,)
            ).fetchone()
            if row is None:
                raise DomainError(404, "not_found")
            if row["revision"] != expected_revision:
                raise DomainError(409, "revision_conflict")
            self._remove_indexes(db, document_id)
            db.execute(
                "UPDATE jobs SET status='cancelled',payload_json=NULL,updated_at=? WHERE document_id=? AND status IN ('queued','running')",
                (datetime.now(UTC).isoformat(), document_id),
            )
            db.execute(
                "UPDATE versions SET status='deleted',text=NULL WHERE document_id=?", (document_id,)
            )
            db.execute(
                "UPDATE documents SET active_version_id=NULL,deleted_at=?,revision=revision+1 WHERE id=?",
                (datetime.now(UTC).isoformat(), document_id),
            )
            self._invalidate(db, str(row["min_role"]), None)

    def documents(self, scope: AccessScope) -> list[DocumentSummary]:
        with self.connection() as db:
            rows = db.execute(
                "SELECT d.id,d.title,d.revision,v.id version_id,v.label version_label,v.effective_date FROM documents d JOIN versions v ON d.active_version_id=v.id AND v.document_id=d.id WHERE d.deleted_at IS NULL AND v.status='active' AND (?='maintainer' OR d.min_role='reader') ORDER BY d.title,d.id",
                (scope.role,),
            ).fetchall()
        return [DocumentSummary.model_validate(dict(row)) for row in rows]

    def document(self, scope: AccessScope, document_id: str) -> DocumentView:
        with self.connection() as db:
            row = db.execute(
                "SELECT d.id,d.title,d.revision,v.id version_id,v.label version_label,v.effective_date,v.text FROM documents d JOIN versions v ON d.active_version_id=v.id AND v.document_id=d.id WHERE d.id=? AND d.deleted_at IS NULL AND v.status='active' AND (?='maintainer' OR d.min_role='reader')",
                (document_id, scope.role),
            ).fetchone()
        if row is None:
            raise DomainError(404, "not_found")
        return DocumentView.model_validate(dict(row))

    def check_citations(self, scope: AccessScope, ids: list[str]) -> list[Citation]:
        result: list[Citation] = []
        with self.connection() as db:
            for chunk_id in ids:
                row = db.execute(
                    "SELECT c.id chunk_id,d.id document_id,v.id version_id,d.title,v.label version_label,v.effective_date,c.section_id,c.start_char,c.end_char,c.text quote FROM chunks c JOIN versions v ON c.version_id=v.id JOIN documents d ON v.document_id=d.id AND d.active_version_id=v.id WHERE c.id=? AND v.status='active' AND d.deleted_at IS NULL AND (?='maintainer' OR d.min_role='reader')",
                    (chunk_id, scope.role),
                ).fetchone()
                if row is None:
                    raise DomainError(404, "not_found")
                result.append(Citation.model_validate(dict(row)))
        return result

    def citation(self, scope: AccessScope, chunk_id: str) -> CitationView:
        citation = self.check_citations(scope, [chunk_id])[0]
        with self.connection() as db:
            row = db.execute(
                "SELECT text FROM versions WHERE id=?", (citation.version_id,)
            ).fetchone()
        text = str(row["text"])
        from evidence_rag.documents.chunking import chunk_document

        chunks = chunk_document(citation.version_id, text)
        section = [c for c in chunks if c.section_id == citation.section_id]
        start = min(c.start_char for c in section)
        end = max(c.end_char for c in section)
        return CitationView(
            **citation.model_dump(),
            section_text=text[start:end],
            section_start_char=start,
            highlight_start=citation.start_char - start,
            highlight_end=citation.end_char - start,
        )
