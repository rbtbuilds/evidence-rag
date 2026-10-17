"""Leased paired evaluation. Oracle data never enters an inference request."""

import argparse
import json
import platform
import subprocess
import sys
import tempfile
import time
from collections import Counter
from dataclasses import asdict
from pathlib import Path
from typing import Literal

from evidence_rag.answers.service import AnswerService
from evidence_rag.config import Settings
from evidence_rag.contracts import QuestionRequest
from evidence_rag.db.repository import AccessScope, Repository
from evidence_rag.documents.chunking import chunk_document
from evidence_rag.documents.ingest import seed
from evidence_rag.evaluation.quality import QUALITY_ROOT, load_cases, score_answer, sha256
from evidence_rag.evaluation.run import MODES, evaluate
from evidence_rag.models.generation import GENERATION_SETTINGS
from evidence_rag.models.local import PROJECT, snapshots
from evidence_rag.models.runner import ModelRunner, ModelSession
from evidence_rag.retrieval.service import build_index
from evidence_rag.retrieval.types import IndexDraft


def provenance() -> dict[str, object]:
    return {
        "git_head": subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip(),
        "dirty_worktree": bool(
            subprocess.check_output(
                ["git", "--no-optional-locks", "status", "--porcelain"], text=True
            ).strip()
        ),
        "source_hashes": {
            str(p.relative_to(PROJECT)): sha256(p)
            for folder in ("src", "scripts")
            for p in sorted((PROJECT / folder).rglob("*.py"))
        },
        "dataset_manifest_sha256": sha256(QUALITY_ROOT / "manifest.json"),
        "criteria_sha256": sha256(PROJECT / "docs/QUALITY-PASS.md"),
        "baseline_policy_sha256": sha256(PROJECT / "config/quality-baseline-v4.json"),
        "model_lock_sha256": sha256(PROJECT / "config/models.lock.json"),
        "dependency_lock_sha256": sha256(PROJECT / "uv.lock"),
        "machine": platform.platform(),
        "python": platform.python_version(),
        "human_support_precision": None,
        "human_completeness": None,
    }


def index(repo: Repository, session: ModelSession) -> None:
    with repo.connection() as db:
        sources = db.execute(
            "SELECT d.id,v.id version_id,v.text FROM documents d JOIN versions v "
            "ON d.active_version_id=v.id WHERE d.deleted_at IS NULL"
        ).fetchall()
    chunks = tuple(
        c for row in sources for c in chunk_document(str(row["version_id"]), str(row["text"]))
    )
    draft = build_index(chunks, session)
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
                IndexDraft(tuple(c for c, _ in pairs), tuple(v for _, v in pairs), draft.revision),
            )


def run_quality(
    split: Literal["dev", "challenge"], policy: Literal["baseline", "candidate"], output: Path
) -> dict[str, object]:
    cases = load_cases(split)
    if output.exists():
        raise ValueError("Never overwrite an evaluation block")
    root = Settings.from_env().root
    runner = ModelRunner(
        root,
        command=[sys.executable, "-m", "scripts.quality_baseline_worker"]
        if policy == "baseline"
        else None,
    )
    totals: Counter[str] = Counter()
    by_mode: dict[str, dict[str, int]] = {}
    with runner.session(f"quality-v1 {split} {policy} four-method block", timeout=600) as session:
        # A custom benchmark worker must receive the normal pinned-revision admission checks.
        if runner.lock_info is None:
            runner.lock_info = snapshots(root, verify_hashes=True)
        output.mkdir(parents=True)
        with tempfile.TemporaryDirectory(prefix="quality-", dir=root) as directory:
            repo = Repository(Path(directory) / "evidence.sqlite3")
            seed(repo)
            index(repo, session)
            service = AnswerService(repo, Settings(root, "local"))
            with (output / "rows.jsonl").open("x") as log:
                for mode in MODES:
                    counts: Counter[str] = Counter()
                    for case in cases:
                        with repo.connection() as db:
                            meta = db.execute("SELECT * FROM meta").fetchone()
                        scope = AccessScope(case.role, case.role, int(meta[f"{case.role}_epoch"]))
                        session.begin_request()
                        begin = time.monotonic()
                        result = service.answer(
                            scope,
                            QuestionRequest(
                                question=case.question, retrieval_mode=mode, generation_mode="local"
                            ),
                            session,
                        )
                        answer = result.answer
                        valid = len(
                            repo.check_citations(scope, [c.chunk_id for c in answer.citations])
                        ) == len(answer.citations)
                        score = score_answer(case, answer, citations_valid=valid)
                        disclosure = any(
                            value.casefold() in answer.model_dump_json().casefold()
                            for value in case.forbidden_strings
                        )
                        row = {
                            "case_id": case.id,
                            "category": case.category,
                            "mode": mode,
                            "question": case.question,
                            "role": case.role,
                            "expected_abstention": case.expected_abstention,
                            "answer": answer.model_dump(),
                            "score": asdict(score),
                            "citations_valid": valid,
                            "forbidden_disclosure": disclosure,
                            "seconds": time.monotonic() - begin,
                        }
                        log.write(json.dumps(row) + "\n")
                        log.flush()
                        counts.update(
                            {
                                "cases": 1,
                                "expected_refusals": int(case.expected_abstention),
                                "proper_refusals": int(score.proper_refusal),
                                "answerable": int(not case.expected_abstention),
                                "answerable_responses": int(
                                    not case.expected_abstention and not answer.abstained
                                ),
                                "oracle_verified_complete": int(score.oracle_verified),
                                "oracle_unverified_responses": int(
                                    not answer.abstained and not score.oracle_verified
                                ),
                                "invalid_outputs": int(answer.reason == "invalid_generation"),
                                "forbidden_disclosures": int(disclosure),
                                "citations": len(answer.citations),
                                "resolved_citations": len(answer.citations) if valid else 0,
                            }
                        )
                    totals.update(counts)
                    by_mode[mode] = dict(counts)
                    print(
                        json.dumps({"split": split, "policy": policy, "mode": mode, **counts}),
                        flush=True,
                    )
        report: dict[str, object] = {
            "provenance": provenance(),
            "policy": policy,
            "split": split,
            "settings": json.loads((PROJECT / "config/quality-baseline-v4.json").read_text())[
                "generation_settings"
            ]
            if policy == "baseline"
            else GENERATION_SETTINGS,
            "counts": dict(totals),
            "by_mode": by_mode,
            "categories": dict(Counter(c.category for c in cases)),
            "rows_sha256": sha256(output / "rows.jsonl"),
            "peak_worker_rss_bytes": session.peak_rss,
            "peak_accelerator_bytes": session.peak_accelerator_bytes,
            "embedding_truncations": session.embedding_truncations,
            "dropped_passages": session.dropped_passages,
            "output_limit_hits": session.generation_limit_hits,
            "measurement": "Frozen narrow AI-authored oracle verification; not general entailment or human review.",
        }
        (output / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", choices=["development", "final"], required=True)
    parser.add_argument("--policy", choices=["baseline", "candidate"], default="candidate")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    output = args.output.resolve()
    if not output.is_relative_to(PROJECT / ".runtime") or output.exists():
        raise ValueError("Use a new project-private runtime directory")
    if args.phase == "development":
        run_quality("dev", args.policy, output)
        return
    frozen = provenance()
    if frozen["dirty_worktree"]:
        raise ValueError("Freeze and commit source before the one final evaluation")
    # Exclusive marker makes a second final invocation an explicit error.
    marker = PROJECT / ".runtime/quality-v1-final-started.json"
    with marker.open("x") as handle:
        json.dump(frozen, handle, indent=2)
    output.mkdir(parents=True)
    run_quality("challenge", "baseline", output / "baseline")
    run_quality("challenge", "candidate", output / "candidate")
    evaluate("local", "test", "local", output / "regression")
    if provenance() != frozen:
        raise ValueError("Frozen evaluation provenance changed during execution")
    (output / "complete.json").write_text(json.dumps(frozen, indent=2) + "\n")


if __name__ == "__main__":
    main()
