from fastapi.testclient import TestClient

ORIGIN = "http://127.0.0.1:5115"


def test_user_header_is_not_identity(client: TestClient) -> None:
    response = client.get("/api/session", headers={"X-User": "maintainer"})
    assert response.status_code == 401
    assert "csrf_token" not in response.text


def test_cross_origin_login_is_denied(client: TestClient) -> None:
    response = client.post(
        "/api/session", json={"code": "not-a-code"}, headers={"Origin": "https://unrelated.invalid"}
    )
    assert response.status_code == 403


def test_wrong_code_does_not_create_a_session(client: TestClient) -> None:
    response = client.post("/api/session", json={"code": "not-a-code"}, headers={"Origin": ORIGIN})
    assert response.status_code == 401
    assert "evidence_session" not in response.cookies


def test_body_is_bounded_before_json_parsing(client: TestClient) -> None:
    response = client.post(
        "/api/session",
        content=b"x" * (270 * 1024),
        headers={"Origin": ORIGIN, "Content-Type": "application/json"},
    )
    assert response.status_code == 413


def test_host_is_not_an_arbitrary_dns_name(client: TestClient) -> None:
    assert client.get("/health", headers={"Host": "unrelated.invalid"}).status_code == 400


import hashlib
import stat
from pathlib import Path

import pytest

from evidence_rag.auth.sessions import initialize
from evidence_rag.errors import DomainError
from tests.helpers import DemoHarness


def test_real_sessions_csrf_and_logout(demo: DemoHarness) -> None:
    for role, headers in demo.credentials.items():
        response = demo.client.get("/api/session", headers=headers)
        assert response.status_code == 200
        assert response.json()["role"] == role
        assert response.headers["cache-control"] == "no-store"
    assert (
        demo.client.delete(
            "/api/session", headers={**demo.reader(), "X-CSRF-Token": "wrong"}
        ).status_code
        == 403
    )
    assert demo.client.delete("/api/session", headers=demo.reader()).status_code == 204
    assert demo.client.get("/api/session", headers=demo.reader()).status_code == 401
    assert demo.client.get("/api/session", headers=demo.maintainer()).status_code == 200


def test_only_failed_logins_count_towards_limit(tmp_path: Path) -> None:
    from evidence_rag.app import create_app
    from evidence_rag.config import Settings

    codes = initialize(tmp_path)
    with TestClient(create_app(Settings(tmp_path)), base_url="http://127.0.0.1:8115") as client:
        for _ in range(6):
            response = client.post(
                "/api/session", json={"code": codes["reader"]}, headers={"Origin": ORIGIN}
            )
            assert response.status_code == 200
            assert "HttpOnly" in response.headers["set-cookie"]
            assert "SameSite=strict" in response.headers["set-cookie"]
        for _ in range(5):
            assert (
                client.post(
                    "/api/session", json={"code": "bad"}, headers={"Origin": ORIGIN}
                ).status_code
                == 401
            )
        assert (
            client.post(
                "/api/session", json={"code": "bad"}, headers={"Origin": ORIGIN}
            ).status_code
            == 429
        )


def test_codes_are_private_digests_and_reset_revokes(demo: DemoHarness) -> None:
    root = demo.repo.path.parent
    assert stat.S_IMODE((root / "demo-codes.json").stat().st_mode) == 0o600
    with pytest.raises(DomainError):
        initialize(root)
    codes = initialize(root, reset=True)
    stored = (root / "demo-codes.json").read_text()
    assert codes["reader"] not in stored
    assert hashlib.sha256(codes["reader"].encode()).hexdigest() in stored
    assert demo.client.get("/api/session", headers=demo.reader()).status_code == 401


def test_expired_session_and_admin_authorization(demo: DemoHarness) -> None:
    assert demo.client.get("/api/admin/jobs/unknown", headers=demo.reader()).status_code == 403
    with demo.repo.transaction() as db:
        db.execute("UPDATE sessions SET expires_at=0")
    assert demo.client.get("/api/session", headers=demo.maintainer()).status_code == 401
