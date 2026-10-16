from pathlib import Path

import pytest

from evidence_rag.answers import service
from evidence_rag.config import Settings
from evidence_rag.contracts import QuestionRequest
from evidence_rag.db.repository import AccessScope, Repository
from evidence_rag.models.local import PROJECT, ModelLock


def test_generation_backend_changes_the_answer_cache_key(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    lock = ModelLock.model_validate_json((PROJECT / "config/models.lock.json").read_text())
    lock.models["generator"] = lock.models["generator"].model_copy(
        update={"backend": "transformers"}
    )

    def configured(_root: Path) -> ModelLock:
        return lock

    monkeypatch.setattr(service, "snapshots", configured)
    answers = service.AnswerService(
        Repository(tmp_path / "cache.sqlite3"), Settings(tmp_path, "local")
    )
    request = QuestionRequest(question="A supported fact?", generation_mode="local")
    scope = AccessScope("reader", "reader", 0)
    before = answers.cache.key(scope, request, answers.revisions(request))
    lock.models["generator"] = lock.models["generator"].model_copy(update={"backend": "mlx"})
    after = answers.cache.key(scope, request, answers.revisions(request))
    assert before != after
