from pathlib import Path

import pytest

from evidence_rag.models.native import NativeGenerator


def test_native_load_rejects_any_unlisted_matching_weight_file(tmp_path: Path) -> None:
    (tmp_path / "config.json").write_text(
        '{"model_type":"qwen3","quantization":{"group_size":64,"bits":4}}'
    )
    (tmp_path / "model.safetensors").write_bytes(b"unit fixture, not model weights")
    (tmp_path / "model-override.safetensors").write_bytes(b"unlisted fixture")
    with pytest.raises(ValueError, match="weight file set"):
        NativeGenerator(tmp_path, expected_files=["config.json", "model.safetensors"])


def test_snapshot_readiness_rejects_unlisted_native_weights(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import json

    from evidence_rag.errors import DomainError
    from evidence_rag.models import local

    directory = tmp_path / "models"
    directory.mkdir()
    (directory / "model.safetensors").write_bytes(b"listed")
    (directory / "model-extra.safetensors").write_bytes(b"unlisted")
    model = {
        "id": "local-unit",
        "revision": "unit",
        "license": "unit",
        "path": "models",
        "files": {"model.safetensors": "unused-without-hash-check"},
        "backend": "mlx",
    }
    (tmp_path / "config").mkdir()
    (tmp_path / "config/models.lock.json").write_text(
        json.dumps(
            {
                "prepared_at": "unit",
                "models": {name: model for name in ("embedding", "reranker", "generator")},
                "libraries": {},
            }
        )
    )
    monkeypatch.setattr(local, "PROJECT", tmp_path)
    with pytest.raises(DomainError) as caught:
        local.snapshots(tmp_path)
    assert caught.value.code == "model_unavailable"
