from pathlib import Path

from evidence_rag.evaluation.run import evaluate


def test_fixture_report_counts_and_honest_provenance(tmp_path: Path) -> None:
    report = evaluate("fixture", "dev", "extractive", tmp_path / "report")
    assert report.manifest.execution_profile == "fixture"
    assert report.manifest.question_count == 24
    assert len(report.rows) == 96
    assert len(report.manifest.source_hashes) == 25
    assert report.citation_support_precision is None
    assert report.answer_completeness is None
    assert {row.mode for row in report.rows} == {"bm25", "dense", "hybrid", "hybrid_rerank"}
    assert not any(row.forbidden_disclosure for row in report.rows)
    assert report.manifest.model_lock is None
