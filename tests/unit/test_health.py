import pytest
from fastapi.testclient import TestClient


def test_health_has_no_private_metadata(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "execution_profile": "fixture"}


def test_runtime_environment_cannot_escape_this_project(monkeypatch: pytest.MonkeyPatch) -> None:
    from pathlib import Path

    from evidence_rag.config import Settings

    monkeypatch.setenv(
        "EVIDENCE_HOME", str(Path(__file__).resolve().parents[3] / "unowned-runtime")
    )
    with pytest.raises(ValueError):
        Settings.from_env()
