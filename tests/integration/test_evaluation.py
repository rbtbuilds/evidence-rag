from pathlib import Path

import pytest

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
    assert report.manifest.model_dump().get("peak_accelerator_bytes") == 0


def test_measured_output_limits_exclude_warmup(tmp_path: Path) -> None:
    from evidence_rag.config import Settings
    from evidence_rag.db.repository import Repository
    from evidence_rag.documents.ingest import seed
    from evidence_rag.evaluation.run import run_rows
    from evidence_rag.models.fixture import FixtureEmbedder, FixtureReranker
    from evidence_rag.models.runner import ModelSession

    class WarmSession(ModelSession):
        def __init__(self) -> None:
            self.peak_rss = self.embedding_truncations = self.dropped_passages = 0
            self.peak_accelerator_bytes = 0
            self.generation_tokens = 0
            self.generation_limit_hits = 7

        @property
        def revision(self) -> str:
            return FixtureEmbedder.revision

        def begin_request(self, timeout: float = 90) -> None:
            pass

        def embed(
            self, texts: list[str], *, is_query: bool = False
        ) -> tuple[tuple[float, ...], ...]:
            return FixtureEmbedder().embed(texts, is_query=is_query)

        def rerank(self, question: str, passages: list[str]) -> list[float]:
            return FixtureReranker().rerank(question, passages)

    repo = Repository(tmp_path / "warmup.sqlite3")
    seed(repo)
    report = run_rows(repo, Settings(tmp_path), "dev", "extractive", WarmSession(), 0)
    assert sum(row.generation_hit_limit for row in report.rows) == 0
    assert report.manifest.generation_limit_hits == 0


def test_case_changed_forbidden_value_reaches_final_disclosure_gate(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from evidence_rag.config import Settings
    from evidence_rag.db.repository import Repository
    from evidence_rag.documents.ingest import Question, load_questions, seed
    from evidence_rag.evaluation import run
    from scripts.curate_quality import regression_counts

    question = load_questions("dev")[8].model_copy(update={"forbidden_strings": ["AMBER LOOP"]})

    def synthetic_question(split: str) -> list[Question]:
        return [question]

    monkeypatch.setattr(run, "load_questions", synthetic_question)
    repo = Repository(tmp_path / "casefold.sqlite3")
    seed(repo)
    report = run.run_rows(repo, Settings(tmp_path), "dev", "extractive", None, 0)
    assert len(report.rows) == 4
    assert all("amber loop" in row.answer.model_dump_json().casefold() for row in report.rows)
    assert all(row.forbidden_disclosure for row in report.rows)
    assert regression_counts(report)["forbidden_disclosures"] == 4
