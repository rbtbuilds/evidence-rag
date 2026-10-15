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
