import subprocess
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    subprocess.run(
        ["uv", "run", "--no-sync", "python", "scripts/export_openapi.py", "--check"],
        cwd=ROOT,
        check=True,
    )
    with tempfile.TemporaryDirectory(prefix="contracts-", dir=ROOT / ".runtime") as directory:
        output = Path(directory) / "api.ts"
        subprocess.run(
            [
                str(ROOT / "web/node_modules/.bin/openapi-typescript"),
                str(ROOT / "contracts/openapi.json"),
                "-o",
                str(output),
            ],
            cwd=ROOT,
            check=True,
        )
        if output.read_bytes() != (ROOT / "web/src/generated/api.ts").read_bytes():
            raise SystemExit("Generated TypeScript drift: run npm --prefix web run generate:types")


if __name__ == "__main__":
    main()
