import json
from pathlib import Path

import pytest

from evidence_rag.evaluation.lease import BorrowedLease
from evidence_rag.models.lease import ModelBusy, ModelLease


def test_serial_borrowers_cannot_release_outer_lease(tmp_path: Path) -> None:
    path = tmp_path / "lease"
    owner = ModelLease(path).acquire("whole benchmark")
    shared = BorrowedLease(owner)
    first = shared.acquire("phase1")
    with pytest.raises(ModelBusy):
        shared.acquire("parallel phase")
    first.close()
    first.close()
    assert path.exists()
    second = shared.acquire("phase2")
    second.close()
    assert path.exists()
    owner.close()
    assert not path.exists()
    with pytest.raises(RuntimeError, match="owner"):
        shared.acquire("after close")


def test_changed_owner_is_never_borrowed_or_removed(tmp_path: Path) -> None:
    path = tmp_path / "lease"
    owner = ModelLease(path).acquire("whole benchmark")
    original = (path / "owner.json").read_text()
    replacement = json.loads(original)
    replacement["token"] = "another-owner"
    (path / "owner.json").write_text(json.dumps(replacement))
    with pytest.raises(RuntimeError, match="owner"):
        BorrowedLease(owner).acquire("phase")
    assert json.loads((path / "owner.json").read_text())["token"] == "another-owner"
    (path / "owner.json").write_text(original)
    owner.close()


def test_busy_final_does_not_create_marker_or_start_inference(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import sys

    from scripts import quality_evaluate as driver

    (tmp_path / ".runtime").mkdir()
    path = tmp_path / "lease"
    owner = ModelLease(path).acquire("another project")
    monkeypatch.setattr(driver, "PROJECT", tmp_path)
    monkeypatch.setattr(driver, "ModelLease", lambda: ModelLease(path), raising=False)
    monkeypatch.setattr(driver, "provenance", lambda: {"dirty_worktree": False})

    def no_inference(*args: object, **kwargs: object) -> dict[str, object]:
        pytest.fail("inference started before acquiring the complete benchmark lease")

    monkeypatch.setattr(driver, "run_quality", no_inference)
    monkeypatch.setattr(
        sys, "argv", ["quality", "--phase", "final", "--output", str(tmp_path / ".runtime/final")]
    )
    try:
        with pytest.raises(ModelBusy):
            driver.main()
        assert not (tmp_path / ".runtime/quality-v1-final-started.json").exists()
    finally:
        owner.close()
