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
    demo.repo.publish(doc, 0, draft(text), metadata(text))
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
