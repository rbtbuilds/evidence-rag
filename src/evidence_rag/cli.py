import argparse
import json
import sqlite3
import sys
from pathlib import Path

from evidence_rag.auth.sessions import initialize
from evidence_rag.config import Settings
from evidence_rag.db.repository import Repository
from evidence_rag.documents.ingest import seed, validate_corpus


def main() -> None:
    parser = argparse.ArgumentParser(description="Evidence RAG local workbench")
    parser.add_argument(
        "command",
        choices=[
            "doctor",
            "init",
            "reset",
            "seed-fixtures",
            "validate-corpus",
            "prepare-models",
            "evaluate",
        ],
    )
    parser.add_argument("--models", action="store_true")
    parser.add_argument("--profile", choices=["fixture", "local"], default="fixture")
    parser.add_argument("--split", choices=["dev", "test"], default="dev")
    parser.add_argument("--generation", choices=["extractive", "local"], default="extractive")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if args.command == "evaluate":
        from evidence_rag.evaluation.run import evaluate

        if args.output is None:
            parser.error("evaluate requires --output pointing to a new project folder")
        report = evaluate(args.profile, args.split, args.generation, args.output)
        print(
            json.dumps(
                {
                    mode: report.aggregates[mode + "/all/all"].model_dump()
                    for mode in ("bm25", "dense", "hybrid", "hybrid_rerank")
                }
            )
        )
        return
    if args.command == "prepare-models":
        import runpy

        from evidence_rag.models.local import PROJECT

        runpy.run_path(str(PROJECT / "scripts/prepare_models.py"), run_name="__main__")
        return
    if args.models:
        from evidence_rag.models.local import snapshots

        print(snapshots(Settings.from_env().root, verify_hashes=True).model_dump_json())
        return
    if args.command == "validate-corpus":
        print(validate_corpus().model_dump_json())
        return
    if args.command == "seed-fixtures":
        seed(Repository(Settings.from_env().database))
        print("Fixture corpus seeded.")
        return
    if args.command in {"init", "reset"}:
        print(json.dumps(initialize(Settings.from_env().root, reset=args.command == "reset")))
        return
    with sqlite3.connect(":memory:") as db:
        db.execute("CREATE VIRTUAL TABLE probe USING fts5(text)")
    print(
        json.dumps(
            {"python": sys.version.split()[0], "fts5": True, "profile": Settings.from_env().profile}
        )
    )


if __name__ == "__main__":
    main()
