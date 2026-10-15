import hashlib
import json
import platform
import random
import subprocess
import sys
import tempfile
import time
from collections.abc import Sequence
from pathlib import Path

import numpy as np
import psutil

from evidence_rag.answers.service import AnswerService
from evidence_rag.config import Profile, Settings
from evidence_rag.contracts import Citation, GenerationMode, QuestionRequest, RetrievalMode
from evidence_rag.db.repository import AccessScope, Repository
from evidence_rag.documents.chunking import chunk_document
from evidence_rag.documents.ingest import FIXTURES, load_questions, seed, validate_corpus
from evidence_rag.evaluation.metrics import mrr_at_k, paired_interval, recall_at_k
from evidence_rag.evaluation.report import (
    Aggregate,
    EvaluationManifest,
    EvaluationReport,
    EvaluationRow,
    PairDifference,
)
from evidence_rag.models.local import PROJECT, snapshots
from evidence_rag.models.runner import ModelRunner, ModelSession
from evidence_rag.retrieval.service import build_index

MODES: tuple[RetrievalMode, ...] = ("bm25", "dense", "hybrid", "hybrid_rerank")


def digest(path: Path) -> str:
    with path.open("rb") as handle:
        return hashlib.file_digest(handle, "sha256").hexdigest()


def aggregate(rows: Sequence[EvaluationRow]) -> Aggregate:
    relevant = [row for row in rows if row.recall_at_5 is not None]
    abstention = [row for row in rows if row.expected_abstention]
    correct = sum(row.answer.abstained for row in abstention)
    return Aggregate(
        count=len(rows),
        relevant_count=len(relevant),
        recall_at_5=float(
            np.mean([row.recall_at_5 for row in relevant if row.recall_at_5 is not None])
        )
        if relevant
        else None,
        mrr_at_5=float(np.mean([row.mrr_at_5 for row in relevant])) if relevant else None,
        expected_abstention_count=len(abstention),
        correct_abstentions=correct,
        correct_abstention_rate=correct / len(abstention) if abstention else None,
        abstention_decision_accuracy=sum(
            row.answer.abstained == row.expected_abstention for row in rows
        )
        / len(rows)
        if rows
        else None,
        forbidden_disclosures=sum(row.forbidden_disclosure for row in rows),
        citations_total=sum(len(row.answer.citations) for row in rows),
        citations_valid=sum(row.citations_valid for row in rows),
        latency_p50_ms=float(np.quantile([row.latency_ms for row in rows], 0.5)) if rows else None,
        latency_p95_ms=float(np.quantile([row.latency_ms for row in rows], 0.95)) if rows else None,
    )


def summary(rows: list[EvaluationRow]) -> tuple[dict[str, Aggregate], list[PairDifference]]:
    groups: dict[str, Aggregate] = {}
    for mode in MODES:
        for role in ("all", "reader", "maintainer"):
            for stratum in ("all", "supported", "unsupported", "version-conflict", "restricted"):
                subset = [
                    r
                    for r in rows
                    if r.mode == mode
                    and (role == "all" or r.role == role)
                    and (stratum == "all" or r.stratum == stratum)
                ]
                groups[f"{mode}/{role}/{stratum}"] = aggregate(subset)
    pairs: list[PairDifference] = []
    baseline = {
        row.query_id: row for row in rows if row.mode == "bm25" and row.recall_at_5 is not None
    }
    for mode in MODES[1:]:
        current = {
            row.query_id: row for row in rows if row.mode == mode and row.recall_at_5 is not None
        }
        for metric in ("recall_at_5", "mrr_at_5"):
            differences = {
                key: float(getattr(current[key], metric)) - float(getattr(value, metric))
                for key, value in baseline.items()
            }
            low, high = paired_interval(list(differences.values()))
            pairs.append(
                PairDifference(
                    mode=mode,
                    metric=metric,
                    count=len(differences),
                    mean_difference=float(np.mean(list(differences.values())))
                    if differences
                    else 0,
                    ci_low=low,
                    ci_high=high,
                    per_query=differences,
                )
            )
    return groups, pairs


def review_sheet(rows: list[EvaluationRow], repo: Repository, output: Path) -> None:
    selected: list[EvaluationRow] = []
    rng = random.Random(17)
    for mode in MODES:
        for stratum, count in [
            ("supported", 3),
            ("unsupported", 1),
            ("version-conflict", 1),
            ("restricted", 1),
        ]:
            candidates = [row for row in rows if row.mode == mode and row.stratum == stratum]
            rng.shuffle(candidates)
            selected.extend(candidates[:count])
    rng.shuffle(selected)
    sheet: list[dict[str, object]] = []
    key: dict[str, str] = {}
    for i, row in enumerate(selected, 1):
        review_id = f"review-{i:03}"
        scope = AccessScope(row.role, row.role, 0)
        sections = [repo.citation(scope, c.chunk_id).model_dump() for c in row.answer.citations]
        sheet.append(
            {
                "review_id": review_id,
                "question": row.question,
                "role": row.role,
                "stratum": row.stratum,
                "answer": row.answer.answer,
                "abstained": row.answer.abstained,
                "expected_abstention": row.expected_abstention,
                "expected_facts": row.expected_facts,
                "sources": sections,
                "supported_cited_claims": None,
                "total_cited_claims": None,
                "supported_expected_facts": None,
                "reviewer": None,
                "review_date": None,
                "disagreements": [],
            }
        )
        key[review_id] = row.mode
    (output / "human-review.json").write_text(json.dumps(sheet, indent=2) + "\n")
    (output / "human-review-key.json").write_text(json.dumps(key, indent=2) + "\n")


def evaluate(
    profile: Profile, split: str, generation: GenerationMode, output: Path
) -> EvaluationReport:
    output = output.resolve()
    if not output.is_relative_to(PROJECT) or output.exists():
        raise ValueError("Use a new output folder inside this project")
    if profile == "fixture" and generation == "local":
        raise ValueError("Local generation requires local models")
    manifest = validate_corpus()
    output.mkdir(parents=True)
    with tempfile.TemporaryDirectory(prefix="evaluation-", dir=PROJECT / ".runtime") as directory:
        repo = Repository(Path(directory) / "evidence.sqlite3")
        seed(repo)
        settings = Settings(Path(directory), profile)
        # Snapshots belong to the configured project runtime; the benchmark database is isolated.
        model_root = Settings.from_env().root
        if profile == "local":
            with ModelRunner(model_root).session(
                "complete retrieval benchmark", timeout=600
            ) as session:
                start = time.perf_counter()
                with repo.connection() as db:
                    sources = db.execute(
                        "SELECT d.id,v.id version_id,v.text FROM documents d JOIN versions v ON d.active_version_id=v.id WHERE d.deleted_at IS NULL"
                    ).fetchall()
                chunks = tuple(
                    c
                    for row in sources
                    for c in chunk_document(str(row["version_id"]), str(row["text"]))
                )
                draft = build_index(chunks, session)
                from evidence_rag.retrieval.types import IndexDraft

                with repo.transaction() as db:
                    for row in sources:
                        pairs = [
                            (c, v)
                            for c, v in zip(draft.chunks, draft.vectors, strict=True)
                            if c.version_id == row["version_id"]
                        ]
                        repo.replace_index(
                            db,
                            str(row["id"]),
                            IndexDraft(
                                tuple(c for c, _ in pairs),
                                tuple(v for _, v in pairs),
                                draft.revision,
                            ),
                        )
                session.rerank("warmup", ["Fictional warmup passage."])
                if generation == "local":
                    warmup_quote = "The fictional warmup value is 17 units."
                    session.generate(
                        "What is the warmup value?",
                        [
                            Citation(
                                chunk_id="warmup",
                                document_id="warmup",
                                version_id="warmup",
                                title="Warmup",
                                version_label="v1",
                                effective_date="2026-10-16",
                                section_id="warmup",
                                start_char=0,
                                end_char=len(warmup_quote),
                                quote=warmup_quote,
                            )
                        ],
                    )
                warmup = time.perf_counter() - start
                report = run_rows(
                    repo, Settings(model_root, profile), split, generation, session, warmup
                )
        else:
            report = run_rows(repo, settings, split, generation, None, 0)
        report.manifest.source_hashes = {
            "corpus/manifest.json": digest(FIXTURES / "corpus/manifest.json"),
            **{f"corpus/{r.path}": r.sha256 for r in manifest.documents},
        }
        (output / "report.json").write_text(report.model_dump_json(indent=2) + "\n")
        review_sheet(report.rows, repo, output)
    return report


def run_rows(
    repo: Repository,
    settings: Settings,
    split: str,
    generation: GenerationMode,
    session: ModelSession | None,
    warmup: float,
) -> EvaluationReport:
    questions = load_questions(split)
    service = AnswerService(repo, settings)
    rows: list[EvaluationRow] = []
    for mode in MODES:
        for question in questions:
            request = QuestionRequest(
                question=question.question, retrieval_mode=mode, generation_mode=generation
            )
            with repo.connection() as db:
                meta = db.execute("SELECT * FROM meta").fetchone()
            scope = AccessScope(question.role, question.role, int(meta[f"{question.role}_epoch"]))
            if session:
                session.begin_request()
            truncations = session.embedding_truncations if session else 0
            dropped = session.dropped_passages if session else 0
            generated_tokens = session.generation_tokens if session else 0
            generation_limit_hits = session.generation_limit_hits if session else 0
            start = time.perf_counter()
            pending = service.answer(scope, request, session)
            latency = (time.perf_counter() - start) * 1000
            valid = len(repo.check_citations(scope, [c.chunk_id for c in pending.answer.citations]))
            text = pending.answer.model_dump_json()
            rows.append(
                EvaluationRow(
                    query_id=question.id,
                    question=question.question,
                    role=question.role,
                    stratum=question.stratum,
                    mode=mode,
                    relevant_sections=question.relevant_sections,
                    retrieved_sections=list(pending.retrieved_sections),
                    expected_facts=question.expected_facts,
                    expected_abstention=question.expected_abstention,
                    answer=pending.answer,
                    recall_at_5=recall_at_k(
                        pending.retrieved_sections, set(question.relevant_sections), 5
                    ),
                    mrr_at_5=mrr_at_k(
                        pending.retrieved_sections, set(question.relevant_sections), 5
                    ),
                    forbidden_disclosure=any(value in text for value in question.forbidden_strings),
                    citations_valid=valid,
                    latency_ms=latency,
                    generated_tokens=session.generation_tokens - generated_tokens if session else 0,
                    generation_hit_limit=session.generation_limit_hits > generation_limit_hits
                    if session
                    else False,
                    embedding_truncations=(session.embedding_truncations - truncations)
                    if session
                    else 0,
                    dropped_passages=(session.dropped_passages - dropped) if session else 0,
                )
            )
        print(
            f"Evaluated {settings.profile}/{generation}/{split}/{mode}: {len(questions)} questions",
            flush=True,
        )
    revisions = service.revisions(
        QuestionRequest(question="provenance", generation_mode=generation)
    )
    from dataclasses import asdict

    source_files = sorted((PROJECT / "src").rglob("*.py"))
    code_hash = hashlib.sha256(
        json.dumps(
            {str(path.relative_to(PROJECT)): digest(path) for path in source_files}, sort_keys=True
        ).encode()
    ).hexdigest()
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=PROJECT, text=True).strip()
    dirty = bool(
        subprocess.check_output(["git", "status", "--porcelain"], cwd=PROJECT, text=True).strip()
    )
    from evidence_rag.models.generation import GENERATION_SETTINGS

    manifest = EvaluationManifest(
        execution_profile=settings.profile,
        split=split,
        generation_mode=generation,
        question_count=len(questions),
        source_hashes={},
        question_hashes={
            f"questions/{name}": digest(FIXTURES / "questions" / name)
            for name in ("dev.jsonl", "test.jsonl", "split.json")
        },
        code_hash=code_hash,
        dependency_lock_sha256=digest(PROJECT / "uv.lock"),
        generation_settings=GENERATION_SETTINGS if generation == "local" else {},
        generation_limit_hits=sum(row.generation_hit_limit for row in rows),
        git_head=head,
        dirty_worktree=dirty,
        machine={
            "system": platform.system(),
            "release": platform.release(),
            "architecture": platform.machine(),
            "python": sys.version.split()[0],
            "ram_bytes": psutil.virtual_memory().total,
        },
        revisions=asdict(revisions),
        model_lock=snapshots(settings.root) if settings.profile == "local" else None,
        warmup_seconds=warmup,
        embedding_truncations=session.embedding_truncations if session else 0,
        dropped_passages=session.dropped_passages if session else 0,
        peak_worker_rss_bytes=session.peak_rss if session else 0,
    )
    groups, pairs = summary(rows)
    return EvaluationReport(
        manifest=manifest, rows=rows, aggregates=groups, paired_differences=pairs
    )
