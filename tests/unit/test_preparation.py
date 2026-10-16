"""Preparation policy test doubles never create project model provenance."""

import hashlib
import io
import json
from collections.abc import Callable
from pathlib import Path
from typing import cast

import pytest

from evidence_rag.models.lease import ModelLease
from evidence_rag.models.local import ModelLock, Snapshot
from scripts import prepare_models


@pytest.mark.parametrize("template", [False, True])
def test_repreparation_uses_existing_revisions_and_preserves_the_lock(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch, template: bool
) -> None:
    runtime = tmp_path / "runtime"
    runtime.mkdir()
    config = tmp_path / "config"
    config.mkdir()
    revision = "a" * 40
    data = b"unit-test fixture, not model weights"
    lock = ModelLock(
        prepared_at="2026-10-15T00:00:00Z",
        models={
            name: Snapshot(
                id=model_id,
                revision=revision,
                license=license_id,
                path=f"models/{name}/{revision}",
                backend=prepare_models.BACKENDS.get(name, "transformers"),
                files={
                    filename: hashlib.sha256(data).hexdigest()
                    for filename in (
                        ["model.safetensors", "chat_template.jinja"]
                        if template
                        else ["model.safetensors"]
                    )
                },
            )
            for name, (model_id, license_id) in prepare_models.SPECS.items()
        },
        libraries={name: "test-library" for name in prepare_models.LIBRARIES},
    )
    target = config / "models.lock.json"
    target.write_text(lock.model_dump_json(indent=2) + "\n")
    before = target.read_bytes()
    monkeypatch.setattr(prepare_models, "PROJECT", tmp_path)
    monkeypatch.setenv("EVIDENCE_HOME", str(runtime))
    monkeypatch.setattr(prepare_models, "ModelLease", lambda: ModelLease(tmp_path / "lease"))

    def version(_name: str) -> str:
        return "test-library"

    monkeypatch.setattr(prepare_models.importlib.metadata, "version", version)

    def download(**kwargs: object) -> str:
        assert kwargs["revision"] == revision and kwargs["token"] is False
        path = cast(Path, kwargs["local_dir"]) / cast(str, kwargs["filename"])
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(data)
        return str(path)

    def configured(_root: Path) -> Callable[..., str]:
        return download

    monkeypatch.setattr(prepare_models, "configure_downloads", configured)

    def info(url: str, timeout: int) -> io.BytesIO:
        assert url.endswith("/revision/" + revision)
        assert timeout == 30
        model_id = url.removeprefix("https://huggingface.co/api/models/").split("/revision/")[0]
        license_id = next(
            value[1] for value in prepare_models.SPECS.values() if value[0] == model_id
        )
        return io.BytesIO(
            json.dumps(
                {
                    "sha": revision,
                    "cardData": {"license": license_id},
                    "siblings": [
                        {"rfilename": filename}
                        for filename in (
                            ["model.safetensors", "chat_template.jinja"]
                            if template
                            else ["model.safetensors"]
                        )
                    ],
                }
            ).encode()
        )

    monkeypatch.setattr(prepare_models.urllib.request, "urlopen", info)
    prepare_models.main()
    assert target.read_bytes() == before
