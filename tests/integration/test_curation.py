from pathlib import Path

import pytest

from evidence_rag.evaluation.run import evaluate
from scripts import curate_reports


def test_missing_later_run_does_not_publish_partial_revision(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    source = tmp_path / "complete-fixture"
    evaluate("fixture", "dev", "extractive", source)
    root = tmp_path / "curation"
    (root / "reports").mkdir(parents=True)
    for name in ("eval-fixture-dev", "eval-fixture-test"):
        folder = root / ".runtime" / (name + "-trial")
        folder.mkdir(parents=True)
        for filename in ("report.json", "human-review.json"):
            (folder / filename).write_bytes((source / filename).read_bytes())
    monkeypatch.setattr(curate_reports, "PROJECT", root)
    monkeypatch.setattr("sys.argv", ["curate", "--run-suffix", "trial", "--revision", "v-next"])
    with pytest.raises(FileNotFoundError):
        curate_reports.main()
    assert list((root / "reports").iterdir()) == []
