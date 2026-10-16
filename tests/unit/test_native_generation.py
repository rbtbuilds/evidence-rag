from collections.abc import Generator
from dataclasses import dataclass
from pathlib import Path
from typing import cast

import numpy as np
import pytest

from evidence_rag.models.native import (
    AcceleratorMemoryLimit,
    NativeArray,
    NativeGenerator,
    mask_logits,
)
from tests.unit.test_decoding import Sequence


class Runtime:
    int32: object = np.int32

    def __init__(self) -> None:
        self.peak = 10

    def full(self, shape: tuple[int, ...], value: float, *, dtype: object) -> NativeArray:
        return cast(NativeArray, np.full(shape, value, dtype=cast(np.dtype[np.float32], dtype)))

    def array(self, values: list[int], *, dtype: object) -> object:
        return np.array(values, dtype=cast(np.dtype[np.int32], dtype))

    def isfinite(self, values: NativeArray) -> NativeArray:
        return cast(
            NativeArray,
            np.isfinite(cast(np.ndarray[tuple[int, ...], np.dtype[np.float32]], values)),
        )

    def all(self, values: NativeArray) -> NativeArray:
        return cast(
            NativeArray, np.all(cast(np.ndarray[tuple[int, ...], np.dtype[np.float32]], values))
        )

    def get_peak_memory(self) -> int:
        return self.peak


@dataclass
class Item:
    text: str
    generation_tokens: int
    finish_reason: str | None


def allowed(batch: int, tokens: object) -> list[int]:
    return [2, 5]


def test_native_mask_removes_even_the_highest_illegal_logit() -> None:
    logits = np.array([[0, 1, 2, 10000, 4, 5]], dtype=np.float32)
    result = cast(
        np.ndarray[tuple[int, int], np.dtype[np.float32]],
        mask_logits(Runtime(), allowed, Sequence([65]), cast(NativeArray, logits)),
    )
    assert np.argmax(result) == 5
    assert np.isneginf(result[0, 3])
    assert result.dtype == logits.dtype
    assert result[0, 2] == logits[0, 2]


def test_empty_constraint_choices_fail_closed() -> None:
    def empty(batch: int, tokens: object) -> list[int]:
        return []

    with pytest.raises(ValueError):
        mask_logits(Runtime(), empty, Sequence([]), cast(NativeArray, np.zeros((1, 5))))


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), -float("inf")])
def test_illegal_nonfinite_logits_never_taint_allowed_choices(bad: float) -> None:
    logits = np.array([[0, 1, 2, bad, 4, 5]], dtype=np.float32)
    result = cast(
        np.ndarray[tuple[int, int], np.dtype[np.float32]],
        mask_logits(Runtime(), allowed, Sequence([]), cast(NativeArray, logits)),
    )
    assert not np.isnan(result).any() and np.argmax(result) == 5


@pytest.mark.parametrize("bad", [float("nan"), float("inf"), -float("inf")])
def test_nonfinite_allowed_scores_are_an_error(bad: float) -> None:
    with pytest.raises(ValueError):
        mask_logits(
            Runtime(), allowed, Sequence([]), cast(NativeArray, np.array([[0, 1, bad, 3, 4, 5]]))
        )


@pytest.mark.parametrize("budget", [None, 32])
def test_native_stream_records_budget_and_does_not_reuse_prompt_cache(
    monkeypatch: pytest.MonkeyPatch,
    budget: int | None,
) -> None:
    backend = object.__new__(NativeGenerator)
    runtime = Runtime()
    monkeypatch.setattr(backend, "runtime", runtime, raising=False)
    monkeypatch.setattr(backend, "model", object(), raising=False)
    monkeypatch.setattr(backend, "tokenizer", object(), raising=False)
    monkeypatch.setattr(backend, "sampler", object(), raising=False)

    def stream(*args: object, **kwargs: object) -> Generator[Item, None, None]:
        assert kwargs["max_tokens"] == (budget or 256)
        assert kwargs["prompt_cache"] is None
        assert kwargs["logits_processors"]
        yield Item('{"answer":', 1, None)
        yield Item('"35"}', 2, "stop")

    monkeypatch.setattr(backend, "stream", stream, raising=False)
    result = backend.generate([1, 2], allowed, max_tokens=budget)
    assert result.output == '{"answer":"35"}'
    assert result.output_tokens == 2 and not result.hit_output_limit
    assert result.peak_accelerator_bytes == 10


def test_memory_failure_closes_the_owned_generation_stream(monkeypatch: pytest.MonkeyPatch) -> None:
    backend = object.__new__(NativeGenerator)
    runtime = Runtime()
    monkeypatch.setattr(backend, "runtime", runtime, raising=False)
    monkeypatch.setattr(backend, "model", object(), raising=False)
    monkeypatch.setattr(backend, "tokenizer", object(), raising=False)
    monkeypatch.setattr(backend, "sampler", object(), raising=False)
    closed: list[bool] = []

    def stream(*args: object, **kwargs: object) -> Generator[Item, None, None]:
        try:
            runtime.peak = 13 * 1024**3
            yield Item("", 1, "length")
        finally:
            closed.append(True)

    monkeypatch.setattr(backend, "stream", stream, raising=False)
    with pytest.raises(AcceleratorMemoryLimit):
        backend.generate([1], allowed)
    assert closed == [True]


def test_missing_local_snapshot_cannot_trigger_a_hub_download() -> None:
    with pytest.raises(ValueError):
        NativeGenerator(Path("/nonexistent-evidence-rag-model"), expected_files=[])
