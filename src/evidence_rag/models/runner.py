import os
import selectors
import subprocess
import sys
import threading
import time
from collections.abc import Generator
from contextlib import contextmanager
from pathlib import Path
from typing import Annotated, Literal

import psutil
from pydantic import Field, TypeAdapter

from evidence_rag.contracts import Citation, StrictModel
from evidence_rag.errors import DomainError
from evidence_rag.models.lease import ModelLease
from evidence_rag.models.local import ModelLock, snapshots

MAX_MESSAGE = 16 * 1024 * 1024


class EmbedRequest(StrictModel):
    kind: Literal["embed"] = "embed"
    texts: list[str] = Field(max_length=2000)
    is_query: bool = False


class RerankRequest(StrictModel):
    kind: Literal["rerank"] = "rerank"
    question: str = Field(max_length=500)
    passages: list[str] = Field(max_length=20)


class GenerateRequest(StrictModel):
    kind: Literal["generate"] = "generate"
    question: str = Field(max_length=500)
    citations: list[Citation] = Field(max_length=5)


ModelRequest = Annotated[
    EmbedRequest | RerankRequest | GenerateRequest, Field(discriminator="kind")
]
REQUEST = TypeAdapter(ModelRequest)


class EmbeddingResult(StrictModel):
    kind: Literal["embedding"] = "embedding"
    vectors: list[list[float]]
    revision: str
    truncations: int = 0


class RerankResult(StrictModel):
    kind: Literal["rerank"] = "rerank"
    scores: list[float]
    revision: str


class GenerationResult(StrictModel):
    kind: Literal["generation"] = "generation"
    output: str
    revision: str
    dropped_passages: int = 0


ModelResult = Annotated[
    EmbeddingResult | RerankResult | GenerationResult, Field(discriminator="kind")
]
RESULT = TypeAdapter(ModelResult)


class ModelSession:
    def __init__(
        self, runner: "ModelRunner", process: subprocess.Popen[bytes], timeout: float
    ) -> None:
        self.runner, self.process = runner, process
        self.timeout = timeout
        self.deadline = time.monotonic() + timeout
        self.embedding_truncations = 0
        self.dropped_passages = 0

    @property
    def revision(self) -> str:
        lock = self.runner.lock_info
        return "bge:" + lock.models["embedding"].revision if lock else "test-worker"

    def embed(self, texts: list[str], *, is_query: bool = False) -> tuple[tuple[float, ...], ...]:
        result = self.run(EmbedRequest(texts=texts, is_query=is_query))
        if not isinstance(result, EmbeddingResult) or result.revision != self.revision:
            raise DomainError(503, "model_unavailable")
        self.embedding_truncations += result.truncations
        return tuple(tuple(v) for v in result.vectors)

    def rerank(self, question: str, passages: list[str]) -> list[float]:
        result = self.run(RerankRequest(question=question, passages=passages))
        if not isinstance(result, RerankResult):
            raise DomainError(503, "model_unavailable")
        return result.scores

    def generate(self, question: str, citations: list[Citation]) -> GenerationResult:
        result = self.run(GenerateRequest(question=question, citations=citations))
        if not isinstance(result, GenerationResult):
            raise DomainError(503, "model_unavailable")
        self.dropped_passages += result.dropped_passages
        return result

    def run(self, request: ModelRequest) -> ModelResult:
        payload = (request.model_dump_json() + "\n").encode()
        if len(payload) > MAX_MESSAGE:
            raise DomainError(413, "limit_exceeded")
        process = self.process
        if process.stdin is None or process.stdout is None:
            raise DomainError(503, "model_unavailable")
        deadline = self.deadline
        output = bytearray()
        written = 0
        try:
            os.set_blocking(process.stdin.fileno(), False)
            os.set_blocking(process.stdout.fileno(), False)
            with selectors.DefaultSelector() as selector:
                selector.register(process.stdin, selectors.EVENT_WRITE)
                selector.register(process.stdout, selectors.EVENT_READ)
                while True:
                    if time.monotonic() > deadline:
                        raise DomainError(504, "model_timeout")
                    if process.poll() is not None:
                        raise DomainError(503, "model_unavailable")
                    if psutil.Process(process.pid).memory_info().rss > self.runner.rss_limit:
                        raise DomainError(503, "model_memory_limit")
                    for key, _ in selector.select(0.025):
                        if key.fileobj is process.stdin:
                            written += os.write(
                                process.stdin.fileno(), payload[written : written + 65536]
                            )
                            if written == len(payload):
                                selector.unregister(process.stdin)
                        else:
                            data = os.read(process.stdout.fileno(), 65536)
                            if not data:
                                raise DomainError(503, "model_unavailable")
                            output.extend(data)
                            if len(output) > MAX_MESSAGE:
                                raise DomainError(503, "model_unavailable")
                            if b"\n" in output:
                                line, rest = output.split(b"\n", 1)
                                if rest.strip():
                                    raise DomainError(503, "model_unavailable")
                                return RESULT.validate_json(line)
        except (OSError, ValueError, psutil.Error) as error:
            raise DomainError(503, "model_unavailable") from error


class ModelRunner:
    def __init__(
        self,
        root: Path,
        *,
        lease: ModelLease | None = None,
        command: list[str] | None = None,
        timeout: float = 90,
        rss_limit: int = 6 * 1024**3,
    ) -> None:
        self.root, self.lease, self.command = root, lease or ModelLease(), command
        self.timeout, self.rss_limit = timeout, rss_limit
        self.process: subprocess.Popen[bytes] | None = None
        self.lock_info: ModelLock | None = None
        self.slots = threading.BoundedSemaphore(3)
        self.serial = threading.Lock()

    def cancel(self) -> None:
        process = self.process
        if process:
            if process.poll() is None:
                process.terminate()
                try:
                    process.wait(timeout=3)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait(timeout=3)
            for stream in (process.stdin, process.stdout, process.stderr):
                if stream:
                    stream.close()
            self.process = None

    @contextmanager
    def session(self, purpose: str, *, timeout: float | None = None) -> Generator[ModelSession]:
        if not self.slots.acquire(blocking=False):
            raise DomainError(429, "queue_full")
        try:
            with self.serial:
                if not self.command:
                    self.lock_info = snapshots(self.root)
                handle = self.lease.acquire(purpose)
                try:
                    env = {
                        **os.environ,
                        "HF_HOME": str(self.root / "hf-cache"),
                        "HF_HUB_OFFLINE": "1",
                        "TRANSFORMERS_OFFLINE": "1",
                        "TOKENIZERS_PARALLELISM": "false",
                        "OMP_NUM_THREADS": "4",
                        "MKL_NUM_THREADS": "4",
                        "EVIDENCE_MODEL_ROOT": str(self.root),
                    }
                    self.process = subprocess.Popen(
                        self.command or [sys.executable, "-m", "evidence_rag.models.worker"],
                        stdin=subprocess.PIPE,
                        stdout=subprocess.PIPE,
                        stderr=subprocess.DEVNULL,
                        env=env,
                    )
                    yield ModelSession(self, self.process, timeout or self.timeout)
                finally:
                    self.cancel()
                    handle.close()
        finally:
            self.slots.release()
