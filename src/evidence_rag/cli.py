import argparse
import json
import sqlite3
import sys

from evidence_rag.auth.sessions import initialize
from evidence_rag.config import Settings


def main() -> None:
    parser = argparse.ArgumentParser(description="Evidence RAG local workbench")
    parser.add_argument("command", choices=["doctor", "init", "reset"])
    args = parser.parse_args()
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
