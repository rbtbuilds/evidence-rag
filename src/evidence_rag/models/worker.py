"""Private JSON-lines child. Only the leased supervisor starts this process."""

import importlib
import os
import sys
from collections.abc import Callable
from contextlib import AbstractContextManager
from pathlib import Path
from typing import Protocol, cast

import numpy as np
from numpy.typing import NDArray

from evidence_rag.answers.generation import StructuredGeneration
from evidence_rag.models.decoding import (
    DecodingTokenizer,
    allowed_tokens,
    build_tokenizer_data,
    tokenizer_alphabet,
)
from evidence_rag.models.generation import (
    GENERATION_SETTINGS,
    generation_alphabet,
    generation_messages,
    generation_schema,
)
from evidence_rag.models.local import snapshots
from evidence_rag.models.runner import (
    MAX_MESSAGE,
    REQUEST,
    EmbeddingResult,
    EmbedRequest,
    GenerateRequest,
    GenerationResult,
    ModelResult,
    RerankRequest,
    RerankResult,
)


class Tokenizer(DecodingTokenizer, Protocol):
    def apply_chat_template(self, messages: list[dict[str, str]], **kwargs: object) -> str: ...
    def decode(self, ids: list[int], **kwargs: object) -> str: ...


class Encoder(Protocol):
    tokenizer: Tokenizer

    def encode(self, texts: list[str], **kwargs: object) -> NDArray[np.float32]: ...


class CrossEncoder(Protocol):
    def predict(self, pairs: list[tuple[str, str]], **kwargs: object) -> NDArray[np.float32]: ...


class TensorLike(Protocol):
    def tolist(self) -> list[list[int]]: ...


class Generator(Protocol):
    def generate(self, **kwargs: object) -> TensorLike: ...
    def eval(self) -> object: ...


def factory(module: str, name: str) -> Callable[..., object]:
    return cast(Callable[..., object], getattr(importlib.import_module(module), name))


def pretrained(name: str, path: Path, **kwargs: object) -> object:
    cls = getattr(importlib.import_module("transformers"), name)
    load = cast(Callable[..., object], cls.from_pretrained)
    return load(str(path), local_files_only=True, trust_remote_code=False, **kwargs)


class Backends:
    def __init__(self, root: Path) -> None:
        self.root = root
        self.lock = snapshots(root)
        self.encoder: Encoder | None = None
        self.cross: CrossEncoder | None = None
        self.generator: Generator | None = None
        self.tokenizer: Tokenizer | None = None
        self.tokenizer_data: object | None = None
        factory("torch", "set_num_threads")(4)
        factory("torch", "manual_seed")(17)

    def path(self, name: str) -> Path:
        return self.root / self.lock.models[name].path

    def handle(self, request: EmbedRequest | RerankRequest | GenerateRequest) -> ModelResult:
        if isinstance(request, EmbedRequest):
            if self.encoder is None:
                self.encoder = cast(
                    Encoder,
                    factory("sentence_transformers", "SentenceTransformer")(
                        str(self.path("embedding")),
                        device="cpu",
                        local_files_only=True,
                        trust_remote_code=False,
                    ),
                )
            texts = [
                (
                    "Represent this sentence for searching relevant passages: "
                    if request.is_query
                    else ""
                )
                + text
                for text in request.texts
            ]
            truncated = sum(len(self.encoder.tokenizer.encode(text)) > 512 for text in texts)
            vectors = self.encoder.encode(
                texts,
                normalize_embeddings=True,
                batch_size=4,
                show_progress_bar=False,
                convert_to_numpy=True,
            )
            return EmbeddingResult(
                vectors=vectors.astype(np.float32).tolist(),
                revision="bge:" + self.lock.models["embedding"].revision,
                truncations=truncated,
            )
        if isinstance(request, RerankRequest):
            if self.cross is None:
                self.cross = cast(
                    CrossEncoder,
                    factory("sentence_transformers", "CrossEncoder")(
                        str(self.path("reranker")),
                        device="cpu",
                        local_files_only=True,
                        trust_remote_code=False,
                    ),
                )
            scores = self.cross.predict(
                list(
                    zip([request.question] * len(request.passages), request.passages, strict=True)
                ),
                batch_size=4,
                activation_fn=factory("torch.nn", "Identity")(),
                show_progress_bar=False,
            )
            return RerankResult(
                scores=[float(v) for v in scores.reshape(-1)],
                revision="minilm:" + self.lock.models["reranker"].revision,
            )
        if self.tokenizer is None:
            self.tokenizer = cast(Tokenizer, pretrained("AutoTokenizer", self.path("generator")))
            self.generator = cast(
                Generator,
                pretrained(
                    "AutoModelForCausalLM",
                    self.path("generator"),
                    dtype="float32",
                    use_safetensors=True,
                ),
            )
            self.generator.eval()
        assert self.generator is not None
        if self.tokenizer_data is None:
            self.tokenizer_data = build_tokenizer_data(self.tokenizer)
        if not request.citations:
            return GenerationResult(
                output=StructuredGeneration(
                    answer="", cited_chunk_ids=[], insufficient_evidence=True
                ).model_dump_json(),
                revision="qwen:" + self.lock.models["generator"].revision,
            )
        citations = list(request.citations)
        dropped = 0
        while True:
            messages = generation_messages(request.question, citations)
            text = self.tokenizer.apply_chat_template(
                messages, tokenize=False, add_generation_prompt=True
            )
            ids = self.tokenizer.encode(text, add_special_tokens=False)
            if len(ids) <= 2048:
                break
            if not citations:
                return GenerationResult(
                    output=StructuredGeneration(
                        answer="", cited_chunk_ids=[], insufficient_evidence=True
                    ).model_dump_json(),
                    revision="qwen:" + self.lock.models["generator"].revision,
                    dropped_passages=dropped,
                )
            citations.pop()
            dropped += 1
        if not citations:
            return GenerationResult(
                output=StructuredGeneration(
                    answer="", cited_chunk_ids=[], insufficient_evidence=True
                ).model_dump_json(),
                revision="qwen:" + self.lock.models["generator"].revision,
                dropped_passages=dropped,
            )
        tensor = factory("torch", "tensor")([ids])
        config = factory("lmformatenforcer", "CharacterLevelParserConfig")(
            alphabet=generation_alphabet(
                tokenizer_alphabet(self.tokenizer_data), request.question, citations
            ),
            force_json_field_order=GENERATION_SETTINGS["force_json_field_order"],
            max_consecutive_whitespaces=GENERATION_SETTINGS["max_consecutive_whitespaces"],
            max_json_array_length=5,
        )
        parser = factory("lmformatenforcer", "JsonSchemaParser")(
            generation_schema(citations), config=config
        )
        prefix = allowed_tokens(self.tokenizer_data, parser)
        output = self.generator.generate(
            input_ids=tensor,
            **{
                key: GENERATION_SETTINGS[key]
                for key in ("max_new_tokens", "do_sample", "repetition_penalty")
            },
            prefix_allowed_tokens_fn=prefix,
        )
        generated = output.tolist()[0][len(ids) :]
        return GenerationResult(
            output=self.tokenizer.decode(generated, skip_special_tokens=True),
            revision="qwen:" + self.lock.models["generator"].revision,
            dropped_passages=dropped,
            output_tokens=len(generated),
            hit_output_limit=len(generated) >= int(GENERATION_SETTINGS["max_new_tokens"]),
        )


def main() -> None:
    root = Path(os.environ["EVIDENCE_MODEL_ROOT"])
    backend = Backends(root)
    for _ in range(10000):
        line = sys.stdin.buffer.readline(MAX_MESSAGE + 1)
        if not line:
            return
        if len(line) > MAX_MESSAGE or not line.endswith(b"\n"):
            raise ValueError("IPC message exceeds limit")
        request = REQUEST.validate_json(line)
        # Library progress and warnings must never corrupt the IPC stdout channel.
        original = sys.stdout
        try:
            sys.stdout = sys.stderr
            with cast(AbstractContextManager[object], factory("torch", "inference_mode")()):
                result = backend.handle(request)
        finally:
            sys.stdout = original
        print(result.model_dump_json(), flush=True)


if __name__ == "__main__":
    main()
