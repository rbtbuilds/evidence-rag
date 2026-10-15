import argparse
import json
import sqlite3
import sys

from evidence_rag.config import Settings


def main() -> None:
    parser = argparse.ArgumentParser(description="Evidence RAG local workbench")
    parser.add_argument("command", choices=["doctor"])
    parser.parse_args()
    with sqlite3.connect(":memory:") as db:
        db.execute("CREATE VIRTUAL TABLE probe USING fts5(text)")
    print(
        json.dumps(
            {"python": sys.version.split()[0], "fts5": True, "profile": Settings.from_env().profile}
        )
    )


if __name__ == "__main__":
    main()
