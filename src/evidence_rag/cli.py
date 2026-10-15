import argparse
import json
import sqlite3
import sys

from evidence_rag.auth.sessions import initialize
from evidence_rag.config import Settings
from evidence_rag.db.repository import Repository
from evidence_rag.documents.ingest import seed, validate_corpus


def main() -> None:
    parser = argparse.ArgumentParser(description="Evidence RAG local workbench")
    parser.add_argument(
        "command", choices=["doctor", "init", "reset", "seed-fixtures", "validate-corpus"]
    )
    args = parser.parse_args()
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
