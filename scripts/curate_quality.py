"""Retain small immutable quality evidence without relabelling narrow oracles."""

import argparse
import json
from collections import Counter
from pathlib import Path

from pydantic import BaseModel

from evidence_rag.evaluation.quality import QUALITY_ROOT, load_cases, sha256
from evidence_rag.evaluation.quality_acceptance import acceptance_gates, rate
from evidence_rag.evaluation.report import EvaluationReport
from evidence_rag.evaluation.run import MODES
from evidence_rag.models.local import PROJECT


class QualityReport(BaseModel):
    counts: dict[str, int]
    by_mode: dict[str, dict[str, int]]
    provenance: dict[str, object]
    rows_sha256: str


def regression_counts(report: EvaluationReport) -> dict[str, int]:
    groups = [report.aggregates[f"{mode}/all/all"] for mode in MODES]
    return {
        "cases": sum(g.count for g in groups),
        "expected_refusals": sum(g.expected_abstention_count for g in groups),
        "proper_refusals": sum(g.explicit_correct_abstentions or 0 for g in groups),
        "answerable": sum(g.answerable_count or 0 for g in groups),
        "answerable_responses": sum(g.answered_answerable_count or 0 for g in groups),
        "unnecessary_refusals": sum(g.unnecessary_abstentions or 0 for g in groups),
        "invalid_outputs": sum(g.invalid_generation_count or 0 for g in groups),
        "forbidden_disclosures": sum(g.forbidden_disclosures for g in groups),
        "citations": sum(g.citations_total for g in groups),
        "resolved_citations": sum(g.citations_valid for g in groups),
    }


def read_quality(path: Path) -> dict[str, object]:
    report = QualityReport.model_validate_json((path / "report.json").read_text())
    if sha256(path / "rows.jsonl") != report.rows_sha256:
        raise ValueError("Raw row hash mismatch")
    breakdowns: dict[str, Counter[str]] = {}
    rows = [json.loads(line) for line in (path / "rows.jsonl").read_text().splitlines()]
    if len(rows) != report.counts["cases"]:
        raise ValueError("Incomplete raw rows")
    for row in rows:
        for group in (f"role/{row['role']}", f"category/{row['category']}"):
            counts = breakdowns.setdefault(group, Counter())
            counts.update(
                {
                    "cases": 1,
                    "expected_refusals": int(row["expected_abstention"]),
                    "proper_refusals": int(row["score"]["proper_refusal"]),
                    "answerable": int(not row["expected_abstention"]),
                    "answerable_responses": int(
                        not row["expected_abstention"] and not row["answer"]["abstained"]
                    ),
                    "oracle_verified_complete": int(row["score"]["oracle_verified"]),
                    "oracle_unverified_responses": int(
                        not row["answer"]["abstained"] and not row["score"]["oracle_verified"]
                    ),
                }
            )
    return {
        **json.loads((path / "report.json").read_text()),
        "raw_rows": str((path / "rows.jsonl").relative_to(PROJECT)),
        "raw_report_sha256": sha256(path / "report.json"),
        "breakdowns": {k: dict(v) for k, v in breakdowns.items()},
        "proper_refusal_rate": rate(
            report.counts["proper_refusals"], report.counts["expected_refusals"]
        ),
        "useful_answer_coverage": rate(
            report.counts["oracle_verified_complete"], report.counts["answerable"]
        ),
        "citation_resolution": rate(
            report.counts["resolved_citations"], report.counts["citations"]
        ),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    args = parser.parse_args()
    root = args.input.resolve()
    if not root.is_relative_to(PROJECT / ".runtime") or not (root / "complete.json").is_file():
        raise ValueError("Require one completed project-local frozen final evaluation")
    load_cases("challenge")
    old = json.loads((PROJECT / "reports/quality-v1-preservation.json").read_text())["files"]
    for name, digest in old.items():
        if sha256(PROJECT / name) != digest:
            raise ValueError("Original frozen report changed")
    baseline = read_quality(root / "baseline")
    candidate = read_quality(root / "candidate")
    candidate_counts = QualityReport.model_validate_json(
        (root / "candidate/report.json").read_text()
    ).counts
    regression = EvaluationReport.model_validate_json((root / "regression/report.json").read_text())
    legacy = regression_counts(regression)
    flags = acceptance_gates(legacy, candidate_counts)
    retained: dict[str, object] = {
        "measurement": "AI-authored frozen narrow oracles, not human-reviewed or statistically independent",
        "dataset_manifest_sha256": sha256(QUALITY_ROOT / "manifest.json"),
        "baseline": baseline,
        "candidate": candidate,
        "regression": {
            "counts": legacy,
            "manifest": regression.manifest.model_dump(),
            "raw_sha256": sha256(root / "regression/report.json"),
        },
        "unchanged_recorded_regression_baseline": {
            "source": "reports/evaluation-v4.json",
            "sha256": sha256(PROJECT / "reports/evaluation-v4.json"),
            "proper_refusals": 46,
            "expected_refusals": 48,
            "answerable_responses": 109,
            "answerable": 144,
            "unnecessary_refusals": 35,
            "invalid_outputs": 0,
            "citations": 120,
            "resolved_citations": 120,
        },
        "quality_gates": flags,
        "quality_gate_passed": all(flags.values()),
        "default": "extractive quotations retained",
        "human_support_precision": None,
        "human_completeness": None,
        "limits": "Oracle rejection is not proof of falsehood. Citation resolution is not entailment. Existing test is exposed regression evidence. Security/release checks are recorded separately.",
        "original_reports_preserved": len(old),
    }
    destination = PROJECT / "reports/quality-v1.json"
    with destination.open("x") as handle:
        json.dump(retained, handle, indent=2)
        handle.write("\n")
    print(
        json.dumps(
            {"quality_gates": flags, "regression": legacy, "candidate": candidate_counts}, indent=2
        )
    )


if __name__ == "__main__":
    main()
