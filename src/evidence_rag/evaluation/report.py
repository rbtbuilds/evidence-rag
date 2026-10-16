from typing import Literal

from pydantic import BaseModel

from evidence_rag.contracts import Answer, GenerationMode, RetrievalMode, Role
from evidence_rag.models.local import ModelLock


class EvaluationManifest(BaseModel):
    execution_profile: Literal["fixture", "local"]
    split: str
    generation_mode: GenerationMode
    question_count: int
    k: int = 5
    source_hashes: dict[str, str]
    question_hashes: dict[str, str]
    code_hash: str
    git_head: str
    dirty_worktree: bool
    machine: dict[str, str | int]
    revisions: dict[str, str]
    model_lock: ModelLock | None
    dependency_lock_sha256: str = ""
    generation_settings: dict[str, str | int | float | bool] = {}
    generation_limit_hits: int = 0
    warmup_seconds: float
    embedding_truncations: int
    dropped_passages: int
    peak_worker_rss_bytes: int
    peak_accelerator_bytes: int | None = None
    seed: int = 17
    bootstrap_resamples: int = 2000
    tuning: str = (
        "Model selected using development probes only; no score threshold tuning. "
        "Frozen test is reused after prior disclosed runs: regression evidence, not fresh unseen data."
    )
    context_budget: dict[str, int] = {
        "passages": 5,
        "input_tokens": 2048,
        "output_tokens": 256,
        "max_answer_characters": 180,
        "candidate_limit": 20,
        "batch_size": 4,
        "cpu_threads": 4,
    }


class EvaluationRow(BaseModel):
    query_id: str
    question: str
    role: Role
    stratum: str
    mode: RetrievalMode
    relevant_sections: list[str]
    retrieved_sections: list[str]
    expected_facts: list[str]
    expected_abstention: bool
    answer: Answer
    recall_at_5: float | None
    mrr_at_5: float
    forbidden_disclosure: bool
    citations_valid: int
    generated_tokens: int = 0
    generation_hit_limit: bool = False
    latency_ms: float
    embedding_truncations: int
    dropped_passages: int


class Aggregate(BaseModel):
    count: int
    relevant_count: int
    recall_at_5: float | None
    mrr_at_5: float | None
    expected_abstention_count: int
    correct_abstentions: int
    correct_abstention_rate: float | None
    explicit_correct_abstentions: int | None = None
    invalid_generation_count: int | None = None
    answerable_count: int | None = None
    answered_answerable_count: int | None = None
    unnecessary_abstentions: int | None = None
    abstention_decision_accuracy: float | None
    forbidden_disclosures: int
    citations_total: int
    citations_valid: int
    latency_p50_ms: float | None
    latency_p95_ms: float | None


class PairDifference(BaseModel):
    mode: RetrievalMode
    baseline: str = "bm25"
    metric: str
    count: int
    mean_difference: float
    ci_low: float
    ci_high: float
    per_query: dict[str, float]


class EvaluationReport(BaseModel):
    manifest: EvaluationManifest
    rows: list[EvaluationRow]
    aggregates: dict[str, Aggregate]
    paired_differences: list[PairDifference]
    citation_support_precision: float | None = None
    answer_completeness: float | None = None
    human_review: str = "Unmeasured. Review sheets have not been completed by a human."
