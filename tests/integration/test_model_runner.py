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
