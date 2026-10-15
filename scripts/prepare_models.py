"""Explicit public snapshot download; no inference and no hosted service."""

import hashlib
import importlib.metadata
import json
import os
import urllib.request
from collections.abc import Callable
from datetime import UTC, datetime
from importlib import import_module
from pathlib import Path
from typing import cast

from pydantic import BaseModel, Field

from evidence_rag.config import Settings
from evidence_rag.models.lease import ModelLease
from evidence_rag.models.local import PROJECT, ModelLock, Snapshot


class FileInfo(BaseModel):
    rfilename: str


class Card(BaseModel):
    license: str


class Info(BaseModel):
    sha: str = Field(pattern=r"^[0-9a-f]{40}$")
    cardData: Card
    siblings: list[FileInfo]


SPECS = {
    "embedding": ("BAAI/bge-small-en-v1.5", "mit"),
    "reranker": ("cross-encoder/ms-marco-MiniLM-L6-v2", "apache-2.0"),
    "generator": ("Qwen/Qwen2.5-0.5B-Instruct", "apache-2.0"),
}


def configure_downloads(root: Path) -> Callable[..., str]:
    os.environ["HF_HOME"] = str(root / "hf-cache")
    os.environ["HF_HUB_CACHE"] = str(root / "hf-cache/hub")
    os.environ["HF_XET_CACHE"] = str(root / "hf-cache/xet")
    os.environ["HF_HUB_DISABLE_IMPLICIT_TOKEN"] = "1"
    return cast(Callable[..., str], import_module("huggingface_hub").hf_hub_download)


def main() -> None:
    root = Settings.from_env().root
    root.mkdir(parents=True, exist_ok=True)
    target = PROJECT / "config/models.lock.json"
    known = ModelLock.model_validate_json(target.read_text()) if target.exists() else None
    libraries = {
        name: importlib.metadata.version(name)
        for name in ("torch", "transformers", "sentence-transformers", "huggingface-hub")
    }
    if known and known.libraries != libraries:
        raise ValueError(
            "Install the locked ml dependencies; changing runtime provenance requires a new reviewed lock."
        )
    hf_hub_download = configure_downloads(root)
    handle = ModelLease().acquire("prepare public pinned snapshots")
    models: dict[str, Snapshot] = {}
    try:
        for name, (model_id, license_id) in SPECS.items():
            pinned = known.models[name] if known else None
            if pinned and (pinned.id != model_id or pinned.license != license_id):
                raise ValueError("Pinned model differs from declared specification")
            suffix = "/revision/" + pinned.revision if pinned else ""
            with urllib.request.urlopen(
                "https://huggingface.co/api/models/" + model_id + suffix, timeout=30
            ) as response:
                info = Info.model_validate_json(response.read())
            if pinned and info.sha != pinned.revision:
                raise ValueError("Pinned revision mismatch")
            if info.cardData.license != license_id:
                raise ValueError("Unexpected model licence")
            files = [
                f.rfilename
                for f in info.siblings
                if "/" not in f.rfilename or f.rfilename.startswith("1_Pooling/")
            ]
            files = [
                f
                for f in files
                if f.endswith((".json", ".txt", ".md", ".safetensors", ".model"))
                or f.upper() in {"LICENSE", "NOTICE"}
            ]
            if pinned:
                if not set(pinned.files).issubset(set(files)):
                    raise ValueError("Pinned file is missing from snapshot metadata")
                files = list(pinned.files)
            if not any(f.endswith(".safetensors") for f in files):
                raise ValueError("No safetensors snapshot")
            directory = (
                root / pinned.path if pinned else root / "models" / name / info.sha
            ).resolve()
            if not directory.is_relative_to(root.resolve()):
                raise ValueError("Snapshot path escapes runtime")
            hashes: dict[str, str] = {}
            for filename in files:
                if Path(filename).is_absolute() or not (
                    directory / filename
                ).resolve().is_relative_to(directory):
                    raise ValueError("Snapshot filename escapes model directory")
                path = Path(
                    hf_hub_download(
                        repo_id=model_id,
                        filename=filename,
                        revision=info.sha,
                        local_dir=directory,
                        cache_dir=root / "hf-cache/hub",
                        token=False,
                    )
                )
                if not path.resolve().is_relative_to(directory):
                    raise ValueError("Download path differs from snapshot destination")
                with path.open("rb") as handle_file:
                    hashes[filename] = hashlib.file_digest(handle_file, "sha256").hexdigest()
                if pinned and hashes[filename] != pinned.files[filename]:
                    raise ValueError("Downloaded file does not match pinned hash")
                print(f"{name}: {filename}", flush=True)
            models[name] = Snapshot(
                id=model_id,
                revision=info.sha,
                license=license_id,
                path=str(directory.relative_to(root)),
                files=hashes,
            )
        lock = ModelLock(
            prepared_at=datetime.now(UTC).isoformat(),
            models=models,
            libraries=libraries,
        )
        if known is None:
            temporary = target.with_suffix(".tmp")
            with temporary.open("x") as handle_file:
                handle_file.write(lock.model_dump_json(indent=2) + "\n")
            temporary.replace(target)
        elif models != known.models:
            raise ValueError("Prepared snapshots differ from the committed provenance")
        print(json.dumps({"prepared": list(models), "lock": str(target.relative_to(PROJECT))}))
    finally:
        handle.close()


if __name__ == "__main__":
    main()
