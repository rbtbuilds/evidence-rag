from fastapi.testclient import TestClient


def test_health_has_no_private_metadata(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "execution_profile": "fixture"}
