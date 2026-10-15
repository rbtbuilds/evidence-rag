import json
from pathlib import Path

import pytest

from evidence_rag.models.lease import ModelBusy, ModelLease


def test_busy_lease_is_not_removed(tmp_path: Path) -> None:
    path = tmp_path / "lease"
    first = ModelLease(path).acquire("first")
    with pytest.raises(ModelBusy):
        ModelLease(path).acquire("second")
    assert path.is_dir()
    first.close()
    assert not path.exists()


def test_other_owner_token_cannot_be_released(tmp_path: Path) -> None:
    path = tmp_path / "lease"
    first = ModelLease(path).acquire("first")
    original = (path / "owner.json").read_text()
    record = json.loads(original)
    record["token"] = "another-owner"
    (path / "owner.json").write_text(json.dumps(record))
    with pytest.raises(RuntimeError):
        first.close()
    assert path.exists()
    (path / "owner.json").write_text(original)
    first.close()
