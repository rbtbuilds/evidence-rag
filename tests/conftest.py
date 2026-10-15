from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from evidence_rag.app import create_app
from evidence_rag.config import Settings


@pytest.fixture
def client(tmp_path: Path) -> Iterator[TestClient]:
    with TestClient(create_app(Settings(tmp_path)), base_url="http://127.0.0.1:8115") as value:
        yield value


from evidence_rag.auth.sessions import initialize
from evidence_rag.contracts import Role
from tests.helpers import ORIGIN, DemoHarness


@pytest.fixture
def demo(tmp_path: Path) -> Iterator[DemoHarness]:
    codes = initialize(tmp_path)
    app = create_app(Settings(tmp_path))
    with TestClient(app, base_url="http://127.0.0.1:8115") as value:
        credentials: dict[Role, dict[str, str]] = {}
        for role, code in codes.items():
            response = value.post("/api/session", json={"code": code}, headers={"Origin": ORIGIN})
            assert response.status_code == 200
            credentials[role] = {
                "Origin": ORIGIN,
                "X-CSRF-Token": str(response.json()["csrf_token"]),
                "Cookie": f"evidence_session={response.cookies['evidence_session']}",
            }
            value.cookies.clear()
        yield DemoHarness(value, app.state.repo, credentials)
