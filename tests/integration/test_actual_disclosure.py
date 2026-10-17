"""Explicit actual-model matrix. CI excludes this leased, snapshot-dependent test."""

import hashlib
import json
import os
import tempfile
from pathlib import Path
from typing import cast

import pytest
from fastapi.testclient import TestClient

from evidence_rag.answers.service import AnswerService, PendingAnswer
from evidence_rag.app import create_app
from evidence_rag.auth.sessions import initialize
from evidence_rag.config import Settings
from evidence_rag.contracts import QuestionRequest, RetrievalMode, Role
from evidence_rag.db.repository import AccessScope, Repository
from evidence_rag.documents.chunking import CHUNKER_REVISION, Chunk
from evidence_rag.documents.ingest import FIXTURES, contained, seed, validate_corpus
from evidence_rag.documents.jobs import JobService
from evidence_rag.models.local import snapshots
from evidence_rag.models.runner import ModelRunner, ModelSession
from evidence_rag.retrieval.service import build_index
from evidence_rag.retrieval.types import IndexDraft
from tests.helpers import ORIGIN, RESTRICTED_MARKERS, DemoHarness, disclosed_markers
from tests.integration.test_jobs import wait_job


class BorrowedService(AnswerService):
    def __init__(self, repo: Repository, settings: Settings, shared: ModelSession) -> None:
        super().__init__(repo, settings)
        self.shared = shared

    def answer(
        self, scope: AccessScope, request: QuestionRequest, session: ModelSession | None = None
    ) -> PendingAnswer:
        self.shared.begin_request()
        return super().answer(scope, request, self.shared)


def new_report_path(root: Path, name: str) -> Path:
    path = contained(root, name)
    if path.exists():
        raise ValueError("Choose a new actual-report name; existing evidence is immutable")
    return path


@pytest.mark.real_model
def test_actual_models_respect_access_cache_and_lifecycle() -> None:
    root = Settings.from_env().root
    report_path = new_report_path(
        root, os.environ.get("EVIDENCE_ACTUAL_REPORT", "actual-access-matrix.json")
    )
    corpus = validate_corpus()
    source = next(d for d in corpus.documents if d.logical_id == "calibration" and d.label == "v2")
    modes: tuple[RetrievalMode, ...] = ("bm25", "dense", "hybrid", "hybrid_rerank")
    rows: list[dict[str, object]] = []
    with ModelRunner(root).session(
        "actual disclosure and lifecycle matrix", timeout=600
    ) as session:
        for mode in modes:
            with tempfile.TemporaryDirectory(prefix="actual-access-", dir=root) as directory:
                runtime = Path(directory)
                codes = initialize(runtime)
                app = create_app(Settings(runtime, "local"))
                repo = cast(Repository, app.state.repo)
                seed(repo)
                service = cast(AnswerService, app.state.answers)
                service.settings = Settings(root, "local")
                borrowed = BorrowedService(repo, Settings(root, "local"), session)
                service.answer = borrowed.answer
                jobs = cast(JobService, app.state.jobs)

                def builder(chunks: tuple[Chunk, ...]) -> IndexDraft:
                    session.begin_request(600)
                    return build_index(chunks, session)

                jobs.builder = builder
                with TestClient(app, base_url="http://127.0.0.1:8115") as client:
                    credentials: dict[Role, dict[str, str]] = {}
                    for role, code in codes.items():
                        response = client.post(
                            "/api/session", json={"code": code}, headers={"Origin": ORIGIN}
                        )
                        assert response.status_code == 200
                        credentials[role] = {
                            "Origin": ORIGIN,
                            "X-CSRF-Token": str(response.json()["csrf_token"]),
                            "Cookie": f"evidence_session={response.cookies['evidence_session']}",
                        }
                        client.cookies.clear()
                    demo = DemoHarness(client, repo, credentials)
                    rebuilt = client.post("/api/admin/rebuild", json={}, headers=demo.maintainer())
                    assert rebuilt.status_code == 202
                    # Actual indexing has a ten-minute bound, rather than the lightweight helper's two seconds.
                    import time

                    state = "queued"
                    for _ in range(6000):
                        state = client.get(
                            "/api/admin/jobs/" + rebuilt.json()["job_id"], headers=demo.maintainer()
                        ).json()["status"]
                        if state not in {"queued", "running"}:
                            break
                        time.sleep(0.1)
                    assert state == "succeeded"
                    old_ids: list[str] = []
                    for lifecycle in ("active", "replaced", "deleted"):
                        for generation in ("extractive", "local"):
                            for role in ("maintainer", "reader"):
                                for heat in ("cold", "warm"):
                                    response = client.post(
                                        "/api/questions",
                                        json={
                                            "question": "What is the calibration marker?",
                                            "retrieval_mode": mode,
                                            "generation_mode": generation,
                                        },
                                        headers=credentials[role],
                                    )
                                    assert response.status_code == 200
                                    data = response.json()
                                    assert data["execution_profile"] == "local"
                                    forbidden = disclosed_markers(response.text, role, lifecycle)
                                    assert not forbidden
                                    if generation == "local":
                                        if role == "reader" or lifecycle == "deleted":
                                            assert data["abstained"], (mode, lifecycle, role, data)
                                            assert data["reason"] == "insufficient_evidence"
                                            assert data["answer"] == ""
                                            assert data["citations"] == []
                                        else:
                                            marker = (
                                                "MAINTAINER-CAL-7391"
                                                if lifecycle == "active"
                                                else "REPLACED-MARKER"
                                            )
                                            assert not data["abstained"]
                                            assert marker in data["answer"]
                                    if (
                                        lifecycle == "active"
                                        and role == "maintainer"
                                        and generation == "extractive"
                                    ):
                                        assert "MAINTAINER-CAL-7391" in data["answer"]
                                        old_ids = [
                                            c["chunk_id"]
                                            for c in data["citations"]
                                            if c["document_id"] == source.document_id
                                        ]
                                    for citation in data["citations"]:
                                        assert (
                                            client.get(
                                                "/api/citations/" + citation["chunk_id"],
                                                headers=credentials[role],
                                            ).status_code
                                            == 200
                                        )
                                    rows.append(
                                        {
                                            "mode": mode,
                                            "generation": generation,
                                            "role": role,
                                            "lifecycle": lifecycle,
                                            "cache": heat,
                                            "status": response.status_code,
                                            "abstained": data["abstained"],
                                            "reason": data["reason"],
                                            "answer_empty": data["answer"] == "",
                                            "citation_count": len(data["citations"]),
                                            "forbidden_disclosure": bool(forbidden),
                                        }
                                    )
                        if lifecycle == "active":
                            replaced = client.post(
                                f"/api/admin/documents/{source.document_id}/versions",
                                json={
                                    "title": "Calibration manual",
                                    "min_role": "maintainer",
                                    "label": "v3",
                                    "effective_date": "2026-10-15",
                                    "markdown": "# Calibration overview\nThe calibration marker is REPLACED-MARKER.",
                                    "expected_revision": 2,
                                },
                                headers=demo.maintainer(),
                            )
                            assert replaced.status_code == 202
                            assert wait_job(demo, replaced.json()["job_id"]) == "succeeded"
                            for chunk in old_ids:
                                assert (
                                    client.get(
                                        "/api/citations/" + chunk, headers=demo.maintainer()
                                    ).status_code
                                    == 404
                                )
                        elif lifecycle == "replaced":
                            assert (
                                client.delete(
                                    "/api/admin/documents/" + source.document_id,
                                    headers={**demo.maintainer(), "If-Match": "3"},
                                ).status_code
                                == 204
                            )
            print(f"Actual-model access matrix passed: {mode}", flush=True)
    report = {
        "execution_profile": "local",
        "chunker_revision": CHUNKER_REVISION,
        "test_source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "request_count": len(rows),
        "restricted_markers_checked": list(RESTRICTED_MARKERS),
        "model_revisions": {name: model.revision for name, model in snapshots(root).models.items()},
        "corpus_manifest_sha256": hashlib.sha256(
            (FIXTURES / "corpus/manifest.json").read_bytes()
        ).hexdigest(),
        "scope": "Two roles, four retrieval modes, two generation modes, cold/warm cache, active/replaced/deleted source; serial actual API requests, no race claim. Local reader/deleted requests must explicitly refuse with empty answers and no citations; authorised active/replaced requests must answer the current marker. No prompt-obedience or entailment claim.",
        "rows": rows,
    }
    with report_path.open("x") as handle:
        handle.write(json.dumps(report, indent=2) + "\n")
