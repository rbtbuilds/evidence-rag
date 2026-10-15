"""Mutation check: the lifecycle matrix must detect a leak of the new source."""

import httpx2
import pytest

from evidence_rag.contracts import Role
from evidence_rag.documents.ingest import validate_corpus
from tests.helpers import DemoHarness
from tests.integration.test_disclosure_matrix import test_disclosure_matrix as run_matrix


@pytest.mark.parametrize(
    "role,state", [("reader", "replaced"), ("reader", "deleted"), ("maintainer", "deleted")]
)
def test_matrix_detects_replacement_marker_leak(
    demo: DemoHarness, monkeypatch: pytest.MonkeyPatch, role: Role, state: str
) -> None:
    source_id = next(
        d.document_id for d in validate_corpus().documents if d.logical_id == "calibration"
    )
    original = demo.client.post

    def injected(url: str, *, json: dict[str, object], headers: dict[str, str]) -> httpx2.Response:
        response = original(url, json=json, headers=headers)
        with demo.repo.connection() as db:
            row = db.execute(
                "SELECT revision,deleted_at FROM documents WHERE id=?", (source_id,)
            ).fetchone()
        phase = (
            "active"
            if row is None or row["revision"] < 3
            else "deleted"
            if row["deleted_at"]
            else "replaced"
        )
        if url == "/api/questions" and headers == demo.credentials[role] and phase == state:
            data = response.json()
            data["answer"] = "REPLACED-MARKER"
            return httpx2.Response(200, json=data)
        return response

    monkeypatch.setattr(demo.client, "post", injected)
    with pytest.raises(AssertionError):
        run_matrix(demo, "bm25", role)
