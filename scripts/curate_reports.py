"""Build small provenance-preserving summaries from completed owned evaluations."""

import argparse
import hashlib
import json
import re
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

from pydantic import TypeAdapter

from evidence_rag.evaluation.report import EvaluationReport
from evidence_rag.models.local import PROJECT

RUNS = {
    "fixture-dev-extractive": "eval-fixture-dev",
    "fixture-test-extractive": "eval-fixture-test",
    "local-dev-extractive": "eval-local-dev-extractive",
    "local-dev-generated": "eval-local-dev-local",
    "local-test-extractive": "eval-local-test-extractive",
    "local-test-generated": "eval-local-test-local",
}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-suffix", required=True)
    parser.add_argument("--revision", required=True)
    args = parser.parse_args()
    for value in (args.run_suffix, args.revision):
        if not re.fullmatch(r"[a-z0-9-]{1,40}", value):
            raise ValueError("Use short lowercase revision identifiers")
    destination = PROJECT / "reports" / f"evaluation-{args.revision}.json"
    outputs = [destination] + [
        PROJECT / "reports" / f"review-{args.revision}-{name}.json"
        for name in RUNS
        if "-test-" in name
    ]
    if any(path.exists() for path in outputs):
        raise ValueError("Evidence revision exists; use a new revision")
    runs: dict[str, object] = {}
    review_sheets: dict[Path, bytes] = {}
    for name, directory in RUNS.items():
        path = PROJECT / ".runtime" / f"{directory}-{args.run_suffix}" / "report.json"
        report = EvaluationReport.model_validate_json(path.read_text())
        if len(report.rows) != report.manifest.question_count * 4:
            raise ValueError("Incomplete run")
        if any(row.forbidden_disclosure for row in report.rows):
            raise ValueError("Disclosure regression")
        if report.manifest.embedding_truncations:
            raise ValueError("Embedding truncation")
        runs[name] = {
            "raw_report": str(path.relative_to(PROJECT)),
            "raw_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
            "manifest": report.manifest.model_dump(exclude={"model_lock"}),
            "model_lock_sha256": hashlib.sha256(
                (PROJECT / "config/models.lock.json").read_bytes()
            ).hexdigest()
            if report.manifest.model_lock
            else None,
            "aggregates": {key: value.model_dump() for key, value in report.aggregates.items()},
            "paired_differences": [value.model_dump() for value in report.paired_differences],
            "answer_reasons": dict(Counter(row.answer.reason or "answered" for row in report.rows)),
            "citation_support_precision": None,
            "answer_completeness": None,
        }
        if "-test-" in name:
            source = path.parent / "human-review.json"
            sheet = TypeAdapter(list[dict[str, object]]).validate_json(source.read_text())
            if len(sheet) != 24 or any(row["reviewer"] is not None for row in sheet):
                raise ValueError("Unexpected review status")
            review_sheets[PROJECT / "reports" / f"review-{args.revision}-{name}.json"] = (
                source.read_bytes()
            )
    summary = {
        "curated_at": datetime.now(UTC).isoformat(),
        "cpu": "Apple M5 Pro (observed with sysctl machdep.cpu.brand_string)",
        "interpretation": "Synthetic owned scenario; no customer-impact claim. Warm model timing excludes separately recorded load/index warmup. Light development ran concurrently. Format/citation validity does not prove factual support. Human support/completeness remain unmeasured.",
        "runs": runs,
    }
    for path, contents in review_sheets.items():
        with path.open("xb") as output:
            output.write(contents)
    with destination.open("x") as output:
        output.write(json.dumps(summary, indent=2) + "\n")


if __name__ == "__main__":
    main()
