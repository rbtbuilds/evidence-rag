import time

from tests.helpers import DemoHarness


def wait_job(demo: DemoHarness, job_id: str) -> str:
    for _ in range(200):
        response = demo.client.get("/api/admin/jobs/" + job_id, headers=demo.maintainer())
        assert response.status_code == 200
        status = str(response.json()["status"])
        if status not in {"queued", "running"}:
            return status
        time.sleep(0.01)
    raise AssertionError("Job did not finish")


def test_import_replace_delete_and_stale_sources(demo: DemoHarness) -> None:
    body = {
        "title": "New manual",
        "min_role": "reader",
        "label": "v1",
        "effective_date": "2026-10-15",
        "markdown": "# Flow\nThe display limit is 35 units.",
    }
    response = demo.client.post("/api/admin/documents", json=body, headers=demo.maintainer())
    assert response.status_code == 202
    assert wait_job(demo, response.json()["job_id"]) == "succeeded"
    docs = demo.client.get("/api/documents", headers=demo.reader()).json()
    assert len(docs) == 1
    doc = docs[0]
    response = demo.client.post(
        f"/api/admin/documents/{doc['id']}/versions",
        json={
            **body,
            "label": "v2",
            "expected_revision": 1,
            "markdown": "# Flow\nThe display limit is 40 units.",
        },
        headers=demo.maintainer(),
    )
    assert response.status_code == 202
    assert wait_job(demo, response.json()["job_id"]) == "succeeded"
    assert "40" in demo.client.get("/api/documents/" + doc["id"], headers=demo.reader()).text
    assert (
        demo.client.delete(
            "/api/admin/documents/" + doc["id"], headers={**demo.maintainer(), "If-Match": "1"}
        ).status_code
        == 409
    )
    assert (
        demo.client.delete(
            "/api/admin/documents/" + doc["id"], headers={**demo.maintainer(), "If-Match": "2"}
        ).status_code
        == 204
    )
    assert demo.client.get("/api/documents/" + doc["id"], headers=demo.reader()).status_code == 404
    assert (
        demo.client.delete(
            "/api/admin/documents/" + doc["id"], headers={**demo.maintainer(), "If-Match": "2"}
        ).status_code
        == 404
    )


def test_reader_cannot_inspect_admin_job(demo: DemoHarness) -> None:
    response = demo.client.get("/api/admin/jobs/guessed", headers=demo.reader())
    assert response.status_code == 403
    assert "payload" not in response.text


def test_bounded_queue_cancellation_and_restart(demo: DemoHarness) -> None:
    import asyncio

    import pytest

    from evidence_rag.contracts import RebuildInput
    from evidence_rag.documents.jobs import JobService
    from evidence_rag.errors import DomainError

    service = JobService(demo.repo, asyncio.Lock())
    ids = [service.enqueue("rebuild", RebuildInput()) for _ in range(8)]
    with pytest.raises(DomainError) as error:
        service.enqueue("rebuild", RebuildInput())
    assert error.value.code == "queue_full"
    assert service.cancel(ids[0]).status == "cancelled"
    assert service.cancel(ids[0]).status == "cancelled"
    with demo.repo.transaction() as db:
        db.execute("UPDATE jobs SET status='running' WHERE id=?", (ids[1],))

    async def restart() -> None:
        service.start()
        assert service.view(ids[1]).status == "interrupted"
        await service.stop()

    asyncio.run(restart())


def test_failed_builder_preserves_old_version(demo: DemoHarness) -> None:
    from typing import cast
    from uuid import uuid4

    from fastapi import FastAPI

    from evidence_rag.documents.chunking import Chunk
    from evidence_rag.documents.jobs import JobService
    from evidence_rag.retrieval.types import IndexDraft
    from tests.integration.test_versions import draft, metadata

    doc = str(uuid4())
    text = "# Flow\nLimit 35 units."
    demo.repo.publish(doc, 0, draft(text), metadata(text))
    jobs: JobService = cast(FastAPI, demo.client.app).state.jobs

    def failed(_chunks: tuple[Chunk, ...]) -> IndexDraft:
        raise ValueError("owned test failure")

    jobs.builder = failed
    response = demo.client.post(
        f"/api/admin/documents/{doc}/versions",
        json={**metadata("# Flow\nLimit 40 units.", "v3").model_dump(), "expected_revision": 1},
        headers=demo.maintainer(),
    )
    assert wait_job(demo, response.json()["job_id"]) == "failed"
    assert "35" in demo.client.get("/api/documents/" + doc, headers=demo.reader()).text


def test_staged_version_budget_is_rejected_before_work(demo: DemoHarness) -> None:
    import asyncio
    from uuid import uuid4

    import pytest

    from evidence_rag.contracts import ImportInput
    from evidence_rag.documents.jobs import JobService
    from evidence_rag.errors import DomainError
    from tests.integration.test_versions import draft, metadata

    doc = str(uuid4())
    text = "# Budget\nFictional body."
    demo.repo.publish(doc, 0, draft(text), metadata(text))
    with demo.repo.transaction() as db:
        for i in range(198):
            db.execute(
                "INSERT INTO versions VALUES(?,?,?,'2026-10-15','superseded',NULL,'hash')",
                (str(uuid4()), doc, f"old-{i}"),
            )
    jobs = JobService(demo.repo, asyncio.Lock())
    request = ImportInput(title="New", label="v1", effective_date="2026-10-15", markdown=text)
    jobs.enqueue("import", request)
    with pytest.raises(DomainError) as error:
        jobs.enqueue("import", request)
    assert error.value.code == "limit_exceeded"


def test_import_byte_cap_is_413_before_queueing(demo: DemoHarness) -> None:
    body = {
        "title": "Too large",
        "min_role": "reader",
        "label": "v1",
        "effective_date": "2026-10-15",
        "markdown": "# Flow\n" + "a" * (256 * 1024),
    }
    response = demo.client.post("/api/admin/documents", json=body, headers=demo.maintainer())
    assert response.status_code == 413 and response.json()["error"]["code"] == "limit_exceeded"
    with demo.repo.connection() as db:
        assert db.execute("SELECT count(*) FROM jobs").fetchone()[0] == 0
