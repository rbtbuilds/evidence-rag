"""Build small provenance-preserving summaries from completed owned evaluations."""

import hashlib
import json
from collections import Counter
from datetime import UTC, datetime

from pydantic import TypeAdapter

from evidence_rag.evaluation.report import EvaluationReport
from evidence_rag.models.local import PROJECT

RUNS = {
    "fixture-dev-extractive": "eval-fixture-dev-v2",
    "fixture-test-extractive": "eval-fixture-test-v2",
    "local-dev-extractive": "eval-local-dev-extractive-v1",
    "local-dev-generated": "eval-local-dev-local-v1",
    "local-test-extractive": "eval-local-test-extractive-v1",
    "local-test-generated": "eval-local-test-local-v1",
}


def main() -> None:
    runs: dict[str, object] = {}
    for name, directory in RUNS.items():
        path = PROJECT / ".runtime" / directory / "report.json"
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
            (PROJECT / "reports" / f"review-{name}.json").write_bytes(source.read_bytes())
    summary = {
        "curated_at": datetime.now(UTC).isoformat(),
        "cpu": "Apple M5 Pro (observed with sysctl machdep.cpu.brand_string)",
        "interpretation": "Synthetic owned scenario; no customer-impact claim. Warm model timing excludes separately recorded load/index warmup. Light development ran concurrently. Actual generation abstained on invalid output; this is a failure, not evidence of useful answer quality. Human support/completeness remain unmeasured.",
        "runs": runs,
    }
    (PROJECT / "reports/evaluation-v1.json").write_text(json.dumps(summary, indent=2) + "\n")
    smoke = PROJECT / ".runtime/model-smoke.json"
    (PROJECT / "reports/local-smoke.json").write_bytes(smoke.read_bytes())


if __name__ == "__main__":
    main()
