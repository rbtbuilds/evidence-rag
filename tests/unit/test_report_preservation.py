from pathlib import Path

import pytest

from tests.integration.test_actual_disclosure import new_report_path


def test_actual_report_destination_refuses_overwrite_and_escape(tmp_path: Path) -> None:
    existing = tmp_path / "frozen.json"
    existing.write_text("original")
    with pytest.raises(ValueError):
        new_report_path(tmp_path, "frozen.json")
    assert existing.read_text() == "original"
    for name in ("../outside.json", "/tmp/outside.json"):
        with pytest.raises(ValueError):
            new_report_path(tmp_path, name)


def test_actual_report_destination_accepts_a_fresh_local_name(tmp_path: Path) -> None:
    assert new_report_path(tmp_path, "new.json") == tmp_path / "new.json"
