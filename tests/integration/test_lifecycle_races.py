import threading
from collections.abc import Callable
from typing import cast
from uuid import uuid4

from fastapi import FastAPI

from evidence_rag.documents.chunking import Chunk
from evidence_rag.documents.jobs import JobService
from evidence_rag.models.fixture import FixtureEmbedder
from evidence_rag.retrieval.service import build_index
from evidence_rag.retrieval.types import IndexDraft
from tests.helpers import DemoHarness
from tests.integration.test_jobs import wait_job
from tests.integration.test_versions import draft, metadata


def test_delete_wins_against_staged_replacement(demo: DemoHarness) -> None:
    reached = threading.Event()
    release = threading.Event()
    jobs: JobService = cast(
        FastAPI, demo.client.app
    ).state.jobs  # app is the actual FastAPI instance
    original: Callable[[tuple[Chunk, ...]], IndexDraft] = jobs.builder

    def blocked(chunks: tuple[Chunk, ...]) -> IndexDraft:
        result = build_index(chunks, FixtureEmbedder())
        reached.set()
        assert release.wait(3)
        return result

    jobs.builder = blocked
    doc = str(uuid4())
    text = "# Flow\nMarker ERASE-ME."
    demo.repo.publish(
        doc,
        0,
        draft(text),
        metadata(text).model_copy(update={"title": "ERASE-ME", "label": "ERASE-ME"}),
    )
    try:
        body = {
            **metadata("# Flow\nMarker ERASE-ME new.", "v3").model_dump(),
            "expected_revision": 1,
        }
        response = demo.client.post(
            f"/api/admin/documents/{doc}/versions", json=body, headers=demo.maintainer()
        )
        assert response.status_code == 202
        assert reached.wait(3)
        assert (
            demo.client.delete(
                f"/api/admin/documents/{doc}", headers={**demo.maintainer(), "If-Match": "1"}
            ).status_code
            == 204
        )
        release.set()
        assert wait_job(demo, response.json()["job_id"]) == "cancelled"
        with demo.repo.connection() as db:
            for table, column in [
                ("versions", "text"),
                ("versions", "label"),
                ("documents", "title"),
                ("chunks", "text"),
                ("fts_reader", "text"),
                ("fts_maintainer", "text"),
                ("jobs", "payload_json"),
                ("answer_cache", "payload_json"),
            ]:
                assert (
                    db.execute(
                        f"SELECT count(*) FROM {table} WHERE {column} LIKE '%ERASE-ME%'"
                    ).fetchone()[0]
                    == 0
                )
    finally:
        release.set()
        jobs.builder = original


import asyncio

import pytest
from starlette.types import Message

from evidence_rag.answers.publish import PublicationGate
from evidence_rag.answers.service import AnswerService
from evidence_rag.config import Settings
from evidence_rag.contracts import QuestionRequest
from evidence_rag.documents.ingest import seed, validate_corpus


@pytest.mark.asyncio
async def test_complete_answer_body_precedes_delete_success(demo: DemoHarness) -> None:
    seed(demo.repo)
    token = demo.reader()["Cookie"].split("=", 1)[1]
    pending = AnswerService(demo.repo, Settings(demo.repo.path.parent)).answer(
        demo.repo.resolve_scope(token), QuestionRequest(question="circulation display limit")
    )
    source = next(
        d for d in validate_corpus().documents if d.logical_id == "circulation" and d.label == "v2"
    )
    lock = asyncio.Lock()
    entered = asyncio.Event()
    release = asyncio.Event()
    deleted = asyncio.Event()
    bodies: list[bytes] = []

    async def send(message: Message) -> None:
        if message["type"] == "http.response.body":
            entered.set()
            await release.wait()
            bodies.append(message["body"])

    async def remove() -> None:
        async with lock:
            demo.repo.delete(source.document_id, 2)
            deleted.set()

    answer = asyncio.create_task(
        PublicationGate(demo.repo, lock).send_checked(token, pending, send)
    )
    await asyncio.wait_for(entered.wait(), 2)
    deletion = asyncio.create_task(remove())
    await asyncio.sleep(0.02)
    assert not deleted.is_set()
    release.set()
    await asyncio.gather(answer, deletion)
    assert b"35 units" in bodies[0] and deleted.is_set()


def test_delete_during_rebuild_cannot_restore_snapshot(demo: DemoHarness) -> None:
    seed(demo.repo)
    source = next(
        d for d in validate_corpus().documents if d.logical_id == "circulation" and d.label == "v2"
    )
    jobs = cast(JobService, cast(FastAPI, demo.client.app).state.jobs)
    reached, release = threading.Event(), threading.Event()
    original = jobs.builder

    def blocked(chunks: tuple[Chunk, ...]) -> IndexDraft:
        result = build_index(chunks, FixtureEmbedder())
        reached.set()
        assert release.wait(3)
        return result

    jobs.builder = blocked
    try:
        response = demo.client.post("/api/admin/rebuild", json={}, headers=demo.maintainer())
        assert response.status_code == 202 and reached.wait(3)
        deleted = demo.client.delete(
            "/api/admin/documents/" + source.document_id,
            headers={**demo.maintainer(), "If-Match": "2"},
        )
        assert deleted.status_code == 204
        release.set()
        assert wait_job(demo, response.json()["job_id"]) == "failed"
        job = demo.client.get(
            "/api/admin/jobs/" + response.json()["job_id"], headers=demo.maintainer()
        ).json()
        assert job["error_code"] == "stale_job"
        assert (
            demo.client.get(
                "/api/documents/" + source.document_id, headers=demo.reader()
            ).status_code
            == 404
        )
        with demo.repo.connection() as db:
            assert (
                db.execute(
                    "SELECT count(*) FROM chunks c JOIN versions v ON c.version_id=v.id WHERE v.document_id=?",
                    (source.document_id,),
                ).fetchone()[0]
                == 0
            )
    finally:
        release.set()
        jobs.builder = original
