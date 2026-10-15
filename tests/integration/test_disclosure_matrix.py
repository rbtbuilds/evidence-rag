from uuid import uuid4

import pytest

from evidence_rag.contracts import RetrievalMode, Role
from evidence_rag.documents.chunking import chunk_document
from evidence_rag.documents.ingest import seed, validate_corpus
from evidence_rag.models.fixture import FixtureEmbedder
from evidence_rag.retrieval.service import build_index
from tests.helpers import DemoHarness, disclosed_markers
from tests.integration.test_versions import metadata


@pytest.mark.parametrize("mode", ["bm25", "dense", "hybrid", "hybrid_rerank"])
@pytest.mark.parametrize("role", ["reader", "maintainer"])
def test_disclosure_matrix(demo: DemoHarness, mode: RetrievalMode, role: Role) -> None:
    seed(demo.repo)
    source = next(
        d for d in validate_corpus().documents if d.logical_id == "calibration" and d.label == "v2"
    )
    body = {"question": "What is the calibration marker?", "retrieval_mode": mode}
    # Privileged warmup precedes every role check.
    warm = demo.client.post("/api/questions", json=body, headers=demo.maintainer())
    assert "MAINTAINER-CAL-7391" in warm.text
    old_ids = [
        c["chunk_id"] for c in warm.json()["citations"] if c["document_id"] == source.document_id
    ]
    for state in ("active", "replaced", "deleted"):
        for _ in range(2):
            response = demo.client.post("/api/questions", json=body, headers=demo.credentials[role])
            assert response.status_code == 200
            assert not disclosed_markers(response.text, role, state)
        if state == "active":
            text = "# Calibration overview\nThe calibration marker is REPLACED-MARKER."
            demo.repo.publish(
                source.document_id,
                2,
                build_index(chunk_document(str(uuid4()), text), FixtureEmbedder()),
                metadata(text, "v3", "maintainer"),
            )
            for chunk in old_ids:
                assert (
                    demo.client.get(
                        "/api/citations/" + chunk, headers=demo.maintainer()
                    ).status_code
                    == 404
                )
        elif state == "replaced":
            demo.repo.delete(source.document_id, 3)
