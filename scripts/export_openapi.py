import argparse
import json
import tempfile
from pathlib import Path

from evidence_rag.app import create_app
from evidence_rag.config import Settings


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    (root / ".runtime").mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(dir=root / ".runtime") as directory:
        schema = create_app(Settings(Path(directory))).openapi()
    value = json.dumps(schema, sort_keys=True, indent=2) + "\n"
    path = root / "contracts/openapi.json"
    if args.check:
        if path.read_text() != value:
            raise SystemExit("OpenAPI drift: regenerate contracts")
    else:
        path.write_text(value)


if __name__ == "__main__":
    main()
