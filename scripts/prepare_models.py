"""Explicit public snapshot download; no inference and no hosted service."""

import hashlib
import importlib.metadata
import json
import urllib.request
from collections.abc import Callable
from datetime import UTC, datetime
from importlib import import_module
from pathlib import Path
from typing import cast

from pydantic import BaseModel, Field

hf_hub_download = cast(Callable[..., str], import_module("huggingface_hub").hf_hub_download)
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


def main() -> None:
    root = Settings.from_env().root
    root.mkdir(parents=True, exist_ok=True)
    handle = ModelLease().acquire("prepare public pinned snapshots")
    models: dict[str, Snapshot] = {}
    try:
        for name, (model_id, license_id) in SPECS.items():
            with urllib.request.urlopen(
                "https://huggingface.co/api/models/" + model_id, timeout=30
            ) as response:
                info = Info.model_validate_json(response.read())
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
            if not any(f.endswith(".safetensors") for f in files):
                raise ValueError("No safetensors snapshot")
            directory = root / "models" / name / info.sha
            hashes: dict[str, str] = {}
            for filename in files:
                path = Path(
                    hf_hub_download(
                        repo_id=model_id,
                        filename=filename,
                        revision=info.sha,
                        local_dir=directory,
                        cache_dir=root / "hf-cache",
                    )
                )
                hashes[filename] = hashlib.sha256(path.read_bytes()).hexdigest()
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
            libraries={
                name: importlib.metadata.version(name)
                for name in ("torch", "transformers", "sentence-transformers", "huggingface-hub")
            },
        )
        target = PROJECT / "config/models.lock.json"
        target.write_text(lock.model_dump_json(indent=2) + "\n")
        print(json.dumps({"prepared": list(models), "lock": str(target.relative_to(PROJECT))}))
    finally:
        handle.close()


if __name__ == "__main__":
    main()
