import hashlib
from pathlib import Path
from typing import Literal

from pydantic import BaseModel

from evidence_rag.errors import DomainError

PROJECT = Path(__file__).resolve().parents[3]


class Snapshot(BaseModel):
    id: str
    revision: str
    license: str
    path: str
    files: dict[str, str]
    backend: Literal["transformers", "mlx"] = "transformers"


class ModelLock(BaseModel):
    prepared_at: str
    models: dict[str, Snapshot]
    libraries: dict[str, str]


def generation_revision(lock: ModelLock) -> str:
    model = lock.models["generator"]
    prefix = "mlx-qwen:" if model.backend == "mlx" else "qwen:"
    return prefix + model.revision


def verify_native_weight_files(directory: Path, expected_files: list[str]) -> None:
    expected = {
        name
        for name in expected_files
        if Path(name).match("model*.safetensors") and "/" not in name
    }
    actual = {path.name for path in directory.glob("model*.safetensors")}
    if not expected or actual != expected:
        raise ValueError("Native weight file set differs from the pinned manifest")


def snapshots(root: Path, *, verify_hashes: bool = False) -> ModelLock:
    try:
        lock = ModelLock.model_validate_json((PROJECT / "config/models.lock.json").read_text())
        for name in ("embedding", "reranker", "generator"):
            model = lock.models[name]
            directory = (root / model.path).resolve()
            if not directory.is_relative_to(root.resolve()) or not model.files:
                raise ValueError("Invalid snapshot path")
            if model.backend == "mlx":
                verify_native_weight_files(directory, list(model.files))
            for relative, digest in model.files.items():
                path = (directory / relative).resolve()
                if not path.is_relative_to(directory) or not path.is_file():
                    raise ValueError("Snapshot missing")
                if verify_hashes:
                    with path.open("rb") as handle:
                        if hashlib.file_digest(handle, "sha256").hexdigest() != digest:
                            raise ValueError("Hash mismatch")
        return lock
    except (OSError, ValueError, KeyError) as error:
        raise DomainError(
            503, "model_unavailable", "Prepare pinned local snapshots before using local models."
        ) from error
