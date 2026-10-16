"""Optional Apple-silicon generation; application validation remains authoritative."""

import importlib
from collections.abc import Callable, Generator
from contextlib import closing
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, cast

from pydantic import BaseModel

from evidence_rag.models.decoding import TokenSequence
from evidence_rag.models.generation import GENERATION_SETTINGS
from evidence_rag.models.local import verify_native_weight_files


class NativeArray(Protocol):
    @property
    def shape(self) -> tuple[int, ...]: ...
    @property
    def dtype(self) -> object: ...
    def __setitem__(self, key: object, value: object) -> None: ...
    def __getitem__(self, key: object) -> "NativeArray": ...
    def item(self) -> bool: ...


class MaskRuntime(Protocol):
    int32: object

    def full(self, shape: tuple[int, ...], value: float, *, dtype: object) -> NativeArray: ...
    def array(self, values: list[int], *, dtype: object) -> object: ...
    def isfinite(self, values: NativeArray) -> NativeArray: ...
    def all(self, values: NativeArray) -> NativeArray: ...


class Random(Protocol):
    def seed(self, value: int) -> None: ...


class NativeRuntime(MaskRuntime, Protocol):
    gpu: object
    random: Random

    def set_default_device(self, device: object) -> None: ...
    def set_memory_limit(self, value: int) -> int: ...
    def set_cache_limit(self, value: int) -> int: ...
    def reset_peak_memory(self) -> None: ...
    def get_peak_memory(self) -> int: ...


class StreamItem(Protocol):
    @property
    def text(self) -> str: ...
    @property
    def generation_tokens(self) -> int: ...
    @property
    def finish_reason(self) -> str | None: ...


class NativeConfig(BaseModel):
    model_type: str
    quantization: dict[str, int]


@dataclass(frozen=True)
class NativeOutput:
    output: str
    output_tokens: int
    hit_output_limit: bool
    peak_accelerator_bytes: int


class AcceleratorMemoryLimit(MemoryError):
    pass


def function(module: str, name: str) -> Callable[..., object]:
    return cast(Callable[..., object], getattr(importlib.import_module(module), name))


def mask_logits(
    runtime: MaskRuntime,
    prefix: Callable[[int, TokenSequence], list[int]],
    tokens: TokenSequence,
    logits: NativeArray,
) -> NativeArray:
    choices = prefix(0, tokens)
    if not choices or len(logits.shape) != 2 or logits.shape[0] != 1:
        raise ValueError("Invalid native constraint state")
    if any(token < 0 or token >= logits.shape[1] for token in choices):
        raise ValueError("Constraint token escapes native vocabulary")
    mask = runtime.full(logits.shape, -float("inf"), dtype=logits.dtype)
    indices = runtime.array(choices, dtype=runtime.int32)
    allowed = logits[:, indices]
    if not runtime.all(runtime.isfinite(allowed)).item():
        raise ValueError("Non-finite allowed native logits")
    mask[:, indices] = allowed
    return mask


class NativeGenerator:
    def __init__(self, path: Path, *, expected_files: list[str]) -> None:
        if not path.is_dir() or not (path / "config.json").is_file():
            raise ValueError("Native snapshot must exist locally")
        verify_native_weight_files(path, expected_files)
        config = NativeConfig.model_validate_json((path / "config.json").read_text())
        if config.model_type != "qwen3" or config.quantization != {"group_size": 64, "bits": 4}:
            raise ValueError("Unexpected native model/quantization policy")
        self.runtime = cast(NativeRuntime, importlib.import_module("mlx.core"))
        self.runtime.set_default_device(self.runtime.gpu)
        self.runtime.random.seed(17)
        self.runtime.set_memory_limit(int(GENERATION_SETTINGS["accelerator_budget_bytes"]))
        self.runtime.set_cache_limit(int(GENERATION_SETTINGS["allocator_cache_bytes"]))
        self.runtime.reset_peak_memory()
        loaded = cast(
            tuple[object, object],
            function("mlx_lm", "load")(
                str(path),
                tokenizer_config={"local_files_only": True, "trust_remote_code": False},
                trust_remote_code=False,
            ),
        )
        self.model = loaded[0]
        self.tokenizer = loaded[1]
        self.sampler = function("mlx_lm.sample_utils", "make_sampler")(temp=0.0)
        self.stream = cast(
            Callable[..., Generator[StreamItem, None, None]], function("mlx_lm", "stream_generate")
        )
        self.check_budget()

    def check_budget(self) -> None:
        if self.runtime.get_peak_memory() > int(GENERATION_SETTINGS["accelerator_budget_bytes"]):
            raise AcceleratorMemoryLimit("Native accelerator budget exceeded")

    def generate(
        self,
        ids: list[int],
        prefix: Callable[[int, TokenSequence], list[int]],
        *,
        max_tokens: int | None = None,
    ) -> NativeOutput:
        self.check_budget()

        def processor(tokens: TokenSequence, logits: NativeArray) -> NativeArray:
            self.check_budget()
            return mask_logits(self.runtime, prefix, tokens, logits)

        parts: list[str] = []
        last: StreamItem | None = None
        limit = max_tokens if max_tokens is not None else int(GENERATION_SETTINGS["max_new_tokens"])
        if not 1 <= limit <= int(GENERATION_SETTINGS["max_new_tokens"]):
            raise ValueError("Native token budget exceeds policy")
        with closing(
            self.stream(
                self.model,
                prompt=ids,
                tokenizer=self.tokenizer,
                max_tokens=limit,
                sampler=self.sampler,
                logits_processors=[processor],
                prompt_cache=None,
            )
        ) as stream:
            for item in stream:
                self.check_budget()
                parts.append(item.text)
                last = item
        if last is None or last.finish_reason not in {"stop", "length"}:
            raise ValueError("Incomplete native generation stream")
        if not 1 <= last.generation_tokens <= limit:
            raise ValueError("Invalid native output count")
        return NativeOutput(
            "".join(parts),
            last.generation_tokens,
            last.finish_reason == "length",
            self.runtime.get_peak_memory(),
        )
