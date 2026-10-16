"""Exercise the actual generation call boundary without optional model weights."""

import json
from collections.abc import Callable
from pathlib import Path

import pytest

from evidence_rag.contracts import Citation
from evidence_rag.models import worker
from evidence_rag.models.decoding import TokenSequence
from evidence_rag.models.local import PROJECT, ModelLock
from evidence_rag.models.native import NativeOutput
from evidence_rag.models.runner import GenerateRequest, GenerationResult
from tests.unit.test_generation import source


class Tensor:
    def __init__(self, values: list[list[int]]) -> None:
        self.values = values

    def tolist(self) -> list[list[int]]:
        return self.values


class Tokenizer:
    eos_token_id: int = 0

    def __len__(self) -> int:
        return 128

    def __init__(self, force_trim: bool = False) -> None:
        self.force_trim = force_trim
        self.all_special_ids: list[int] = [0]
        self.messages: list[dict[str, str]] = []
        self.template_kwargs: dict[str, object] = {}

    def encode(self, text: str, **kwargs: object) -> list[int]:
        if self.force_trim and json.loads(self.messages[-1]["content"])["evidence"]:
            return [1] * 2049
        return [1, 2, 3]

    def apply_chat_template(self, messages: list[dict[str, str]], **kwargs: object) -> str:
        self.messages = messages
        self.template_kwargs = kwargs
        return "rendered prompt"

    def decode(self, ids: list[int], **kwargs: object) -> str:
        return '{"answer":"35 units.","cited_chunk_ids":["known"],"insufficient_evidence":false}'


class Generator:
    def __init__(self) -> None:
        self.arguments: dict[str, object] = {}
        self.schema: object = None
        self.configuration: dict[str, object] = {}
        self.native_calls = 0
        self.native_limits: list[int | None] = []

    def generate(self, **kwargs: object) -> Tensor:
        self.arguments = kwargs
        return Tensor([[1, 2, 3, 4]])

    def eval(self) -> object:
        return self


def run_backend(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    *,
    citations: list[Citation] | None = None,
    force_trim: bool = False,
    native: bool = False,
    native_output: str = '{"answer":"35 units.","cited_chunk_ids":["known"],"insufficient_evidence":false}',
) -> tuple[Tokenizer, Generator, GenerationResult]:
    backend = object.__new__(worker.Backends)
    backend.root = tmp_path
    backend.lock = ModelLock.model_validate_json((PROJECT / "config/models.lock.json").read_text())
    tokenizer, generator = Tokenizer(force_trim), Generator()
    backend.tokenizer, backend.generator = tokenizer, generator
    backend.encoder = backend.cross = None
    backend.tokenizer_data = None
    backend.lock.models["generator"] = backend.lock.models["generator"].model_copy(
        update={"backend": "mlx" if native else "transformers"}
    )
    if native:

        class NativeDouble:
            def generate(
                self,
                ids: list[int],
                prefix: Callable[[int, TokenSequence], list[int]],
                *,
                max_tokens: int | None = None,
            ) -> NativeOutput:
                generator.native_calls += 1
                generator.native_limits.append(max_tokens)
                assert ids == [1, 2, 3] and callable(prefix)
                return NativeOutput(
                    native_output,
                    23,
                    False,
                    123,
                )

        monkeypatch.setattr(backend, "native", NativeDouble(), raising=False)

    def factory(module: str, name: str) -> Callable[..., object]:
        if (module, name) == ("torch", "tensor"):
            return Tensor
        if name == "CharacterLevelParserConfig":

            def config(**kwargs: object) -> object:
                generator.configuration = kwargs
                return kwargs

            return config
        if name == "JsonSchemaParser":

            def parser(schema: object, **kwargs: object) -> object:
                return schema

            return parser
        raise AssertionError((module, name))

    def build_data(tokenizer: object) -> object:
        return object()

    def build_prefix(data: object, schema: object) -> Callable[[int, object], list[int]]:
        generator.schema = schema

        def prefix(batch: int, tokens: object) -> list[int]:
            return [1]

        return prefix

    monkeypatch.setattr(worker, "factory", factory)
    monkeypatch.setattr(worker, "build_tokenizer_data", build_data)
    monkeypatch.setattr(worker, "allowed_tokens", build_prefix)

    def alphabet(data: object) -> str:
        return "abc"

    monkeypatch.setattr(worker, "tokenizer_alphabet", alphabet)
    result = backend.handle(
        GenerateRequest(
            question="What is the circulation limit?",
            citations=[source()] if citations is None else citations,
        )
    )
    assert isinstance(result, GenerationResult)
    return tokenizer, generator, result


def test_generation_does_not_inherit_repetition_penalty(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _, generator, result = run_backend(monkeypatch, tmp_path)
    assert generator.arguments.get("repetition_penalty") == 1.0
    assert generator.arguments["do_sample"] is False
    assert generator.arguments["max_new_tokens"] == 256
    assert result.output_tokens == 1 and not result.hit_output_limit


def test_generation_enforces_exact_schema_and_supplied_ids(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    tokenizer, generator, _ = run_backend(monkeypatch, tmp_path)
    assert callable(generator.arguments.get("prefix_allowed_tokens_fn"))
    from evidence_rag.models.generation import generation_schema

    assert generator.schema == generation_schema([source()])
    final = json.loads(tokenizer.messages[-1]["content"])
    assert final["question"] == "What is the circulation limit?"
    assert final["evidence"] == [{"id": "known", "quote": source().quote}]


@pytest.mark.parametrize("force_trim", [False, True])
def test_no_remaining_evidence_abstains_without_sampling(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, force_trim: bool
) -> None:
    _, generator, result = run_backend(
        monkeypatch, tmp_path, citations=[source()] if force_trim else [], force_trim=force_trim
    )
    assert generator.arguments == {}
    assert json.loads(result.output) == {
        "answer": "",
        "cited_chunk_ids": [],
        "insufficient_evidence": True,
    }
    assert result.dropped_passages == int(force_trim)
    assert result.output_tokens == 0


def test_worker_keeps_unicode_from_authorised_request(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    from typing import cast

    quoted = source().model_copy(update={"quote": "The marker is 🛰𐐷."})
    _, generator, _ = run_backend(monkeypatch, tmp_path, citations=[quoted])
    alphabet = cast(str, generator.configuration["alphabet"])
    assert "🛰" in alphabet and "𐐷" in alphabet


def test_declared_native_backend_uses_the_same_request_constraints(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    _, generator, result = run_backend(monkeypatch, tmp_path, native=True)
    assert generator.native_calls == 1 and generator.arguments == {}
    assert generator.native_limits == [256]
    assert generator.schema is not None
    assert result.output_tokens == 23
    assert result.model_dump().get("peak_accelerator_bytes") == 123


def test_native_refusal_preserves_the_strict_empty_output(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    from evidence_rag.answers.generation import validate_generation

    _, generator, result = run_backend(
        monkeypatch,
        tmp_path,
        native=True,
        native_output='{"answer":"","cited_chunk_ids":[],"insufficient_evidence":true}',
    )
    validated = validate_generation(result.output, [source()])
    assert validated.abstained and validated.reason == "insufficient_evidence"
    assert validated.text == "" and validated.citations == []
    assert generator.native_calls == 1


def test_native_chat_template_explicitly_disables_thinking(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    tokenizer, _, _ = run_backend(monkeypatch, tmp_path, native=True)
    assert tokenizer.template_kwargs.get("enable_thinking") is False
