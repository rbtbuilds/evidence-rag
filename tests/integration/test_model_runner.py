import sys
from pathlib import Path

import pytest

from evidence_rag.errors import DomainError
from evidence_rag.models.lease import ModelLease
from evidence_rag.models.runner import EmbedRequest, ModelRunner


@pytest.mark.parametrize(
    "program,code",
    [
        ("import time;time.sleep(5)", "model_timeout"),
        ("print('not json',flush=True)", "model_unavailable"),
    ],
)
def test_worker_failure_joins_before_releasing_lease(
    tmp_path: Path, program: str, code: str
) -> None:
    lease = tmp_path / "lease"
    runner = ModelRunner(
        tmp_path, lease=ModelLease(lease), command=[sys.executable, "-c", program], timeout=0.15
    )
    with pytest.raises(DomainError) as error, runner.session("test") as session:
        session.run(EmbedRequest(texts=["hello"]))
    assert error.value.code == code
    assert not lease.exists()
    assert runner.process is None


def test_missing_snapshots_do_not_load_model(tmp_path: Path) -> None:
    runner = ModelRunner(tmp_path, lease=ModelLease(tmp_path / "lease"))
    with pytest.raises(DomainError) as error, runner.session("missing"):
        pass
    assert error.value.code == "model_unavailable"
    assert not (tmp_path / "lease").exists()


def test_rss_cap_and_busy_and_queue_limit(tmp_path: Path) -> None:
    import threading

    from evidence_rag.models.lease import ModelBusy

    lease = ModelLease(tmp_path / "lease")
    runner = ModelRunner(
        tmp_path,
        lease=lease,
        command=[sys.executable, "-c", "import time;time.sleep(5)"],
        rss_limit=1,
    )
    with pytest.raises(DomainError) as error, runner.session("rss") as session:
        session.run(EmbedRequest(texts=["x"]))
    assert error.value.code == "model_memory_limit"
    held = lease.acquire("other")
    try:
        with pytest.raises(ModelBusy), runner.session("busy"):
            pass
    finally:
        held.close()
    runner.slots = threading.BoundedSemaphore(1)
    assert runner.slots.acquire(False)
    try:
        with pytest.raises(DomainError) as error, runner.session("overflow"):
            pass
        assert error.value.code == "queue_full"
    finally:
        runner.slots.release()


@pytest.mark.parametrize(
    "payload",
    [
        '{"kind":"error","code":"model_memory_limit"}',
        '{"kind":"generation","revision":"test-worker","output":"{}","peak_accelerator_bytes":13958643712}',
    ],
)
def test_accelerator_failure_joins_before_releasing_lease(tmp_path: Path, payload: str) -> None:
    lease = tmp_path / "lease"
    runner = ModelRunner(
        tmp_path,
        lease=ModelLease(lease),
        command=[
            sys.executable,
            "-c",
            "import sys\nfor line in sys.stdin:\n print(" + repr(payload) + ",flush=True)",
        ],
    )
    with pytest.raises(DomainError) as error, runner.session("accelerator cap") as session:
        session.generate("What fact?", [])
    assert error.value.code == "model_memory_limit"
    assert not lease.exists() and runner.process is None


def test_queued_request_has_a_bounded_admission_deadline(tmp_path: Path) -> None:
    import time
    from concurrent.futures import ThreadPoolExecutor

    runner = ModelRunner(
        tmp_path,
        lease=ModelLease(tmp_path / "lease"),
        command=[sys.executable, "-c", "import time;time.sleep(10)"],
        timeout=0.1,
    )

    def queued() -> str:
        try:
            with runner.session("queued", timeout=0.05):
                return "unexpected_success"
        except DomainError as error:
            return error.code

    with ThreadPoolExecutor(max_workers=1) as pool:
        with runner.session("held"):
            future = pool.submit(queued)
            time.sleep(0.15)
            completed_before_release = future.done()
        result = future.result(timeout=3)
    assert completed_before_release and result == "model_timeout"


def test_index_embedding_respects_backend_batch_limit_and_order(tmp_path: Path) -> None:
    program = """import json,sys
for line in sys.stdin:
 request=json.loads(line)
 if len(request['texts'])>4: raise RuntimeError('backend batch limit exceeded')
 vectors=[]
 for text in request['texts']:
  vector=[0.0]*384;vector[int(text)]=1.0;vectors.append(vector)
 print(json.dumps({'kind':'embedding','vectors':vectors,'revision':'test-worker','truncations':0}),flush=True)
"""
    runner = ModelRunner(
        tmp_path,
        lease=ModelLease(tmp_path / "lease"),
        command=[sys.executable, "-u", "-c", program],
    )
    with runner.session("batch-contract") as session:
        vectors = session.embed([str(i) for i in range(9)])
    assert len(vectors) == 9 and all(vector[i] == 1 for i, vector in enumerate(vectors))


def test_native_peak_within_the_documented_model_budget_is_accepted(tmp_path: Path) -> None:
    payload = '{"kind":"generation","revision":"test-worker","output":"{}","peak_accelerator_bytes":9663676416}'
    runner = ModelRunner(
        tmp_path,
        lease=ModelLease(tmp_path / "lease"),
        command=[
            sys.executable,
            "-c",
            "import sys\nfor line in sys.stdin:\n print(" + repr(payload) + ",flush=True)",
        ],
    )
    with runner.session("native bounded result") as session:
        result = session.generate("What fact?", [])
        assert result.peak_accelerator_bytes == 9663676416
    assert runner.process is None and not (tmp_path / "lease").exists()


def test_cancellation_during_startup_prevents_launch_and_allows_next_session(tmp_path: Path) -> None:
    import threading
    from concurrent.futures import ThreadPoolExecutor

    from evidence_rag.models.lease import LeaseHandle

    acquired = threading.Event()
    resume = threading.Event()

    class PausedLease(ModelLease):
        def acquire(self, purpose: str) -> LeaseHandle:
            handle = super().acquire(purpose)
            acquired.set()
            if not resume.wait(timeout=5):
                handle.close()
                raise RuntimeError("Startup barrier timed out")
            return handle

    path = tmp_path / "lease"
    runner = ModelRunner(
        tmp_path,
        lease=PausedLease(path),
        command=[sys.executable, "-c", "import time;time.sleep(5)"],
    )

    def start() -> str:
        try:
            with runner.session("cancel during startup"):
                return "worker_started_after_cancellation"
        except DomainError as error:
            return error.code

    with ThreadPoolExecutor(max_workers=1) as pool:
        future = pool.submit(start)
        try:
            assert acquired.wait(timeout=3)
            runner.cancel()
            assert runner.process is None
        finally:
            resume.set()
        result = future.result(timeout=5)
    assert result == "model_cancelled"
    assert runner.process is None and not path.exists()
    with runner.session("later operation") as session:
        assert session.process.poll() is None
    assert runner.process is None and not path.exists()
