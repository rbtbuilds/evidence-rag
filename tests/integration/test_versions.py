from uuid import uuid4

import pytest

from evidence_rag.contracts import VersionInput
from evidence_rag.documents.chunking import chunk_document
from evidence_rag.errors import DomainError
from evidence_rag.retrieval.types import IndexDraft
from tests.helpers import DemoHarness


def draft(text: str, *, invalid: bool = False) -> IndexDraft:
    chunks = chunk_document(str(uuid4()), text)
    vector = tuple([1.0] + [0.0] * 383) if not invalid else (1.0,)
    return IndexDraft(chunks, tuple(vector for _ in chunks), "fixture-hash-v1")


def metadata(text: str, label: str = "v2", role: str = "reader") -> VersionInput:
    return VersionInput.model_validate(
        {
            "title": "Circulation",
            "min_role": role,
            "label": label,
            "effective_date": "2026-10-15",
            "markdown": text,
        }
    )


def test_publish_rollback_and_delete(demo: DemoHarness) -> None:
    repo = demo.repo
    doc = str(uuid4())
    text = "# Flow\nLimit 35 units."
    assert repo.publish(doc, 0, draft(text), metadata(text)) == 1
    with pytest.raises(DomainError):
        repo.publish(doc, 1, draft("# Flow\nnew"), metadata("# Flow\nnew"))
    with pytest.raises((DomainError, ValueError)):
        repo.publish(
            doc, 1, draft("# Flow\nbroken", invalid=True), metadata("# Flow\nbroken", "v3")
        )
    assert (
        repo.document(repo.resolve_scope(demo.reader()["Cookie"].split("=", 1)[1]), doc).text
        == text
    )
    repo.publish(
        doc,
        1,
        draft("# Flow\nLimit 40 units."),
        metadata("# Flow\nLimit 40 units.", "v3", "maintainer"),
    )
    with repo.connection() as db:
        assert db.execute("SELECT count(*) FROM fts_reader").fetchone()[0] == 0
    repo.delete(doc, 2)
    with repo.connection() as db:
        assert db.execute("SELECT count(*) FROM versions WHERE text IS NOT NULL").fetchone()[0] == 0
        assert db.execute("SELECT count(*) FROM chunks").fetchone()[0] == 0
        assert db.execute("SELECT count(*) FROM fts_maintainer").fetchone()[0] == 0


def test_seed_and_transaction_rollback(demo: DemoHarness) -> None:
    import sqlite3

    from evidence_rag.documents.ingest import seed, validate_corpus

    seed(demo.repo)
    manifest = validate_corpus()
    public = next(
        d for d in manifest.documents if d.logical_id == "circulation" and d.label == "v2"
    )
    with demo.repo.connection() as db:
        assert (
            db.execute(
                "SELECT count(*) FROM fts_reader WHERE text LIKE '%MAINTAINER-CAL-7391%'"
            ).fetchone()[0]
            == 0
        )
        before = [tuple(row) for row in db.execute("SELECT * FROM fts_reader ORDER BY chunk_id")]
    with demo.repo.transaction() as db:
        db.execute(
            "CREATE TRIGGER fail_vector BEFORE INSERT ON vectors BEGIN SELECT RAISE(ABORT,'injected failure'); END"
        )
    with pytest.raises(sqlite3.IntegrityError):
        demo.repo.publish(
            public.document_id,
            2,
            draft("# Flow\nLimit 99 units."),
            metadata("# Flow\nLimit 99 units.", "v3"),
        )
    with demo.repo.connection() as db:
        assert before == [
            tuple(row) for row in db.execute("SELECT * FROM fts_reader ORDER BY chunk_id")
        ]
        assert (
            db.execute(
                "SELECT revision FROM documents WHERE id=?", (public.document_id,)
            ).fetchone()[0]
            == 2
        )


def test_corpus_document_budget_rejects_without_partial_rows(demo: DemoHarness) -> None:
    text = "# Budget\nOwned fictional text."
    with demo.repo.transaction() as db:
        for _ in range(50):
            db.execute(
                "INSERT INTO documents VALUES(?, 'tombstone','reader',NULL,'2026-01-01',1)",
                (str(uuid4()),),
            )
    with pytest.raises(DomainError) as error:
        demo.repo.publish(str(uuid4()), 0, draft(text), metadata(text))
    assert error.value.status == 413
    with demo.repo.connection() as db:
        assert db.execute("SELECT count(*) FROM versions").fetchone()[0] == 0
