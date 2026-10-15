"""Own the test database/API process and pass ephemeral codes only to the browser child."""

import os
import socket
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from pathlib import Path

from evidence_rag.auth.sessions import initialize
from evidence_rag.db.repository import Repository
from evidence_rag.documents.ingest import seed

ROOT = Path(__file__).resolve().parents[1]


def free_ports() -> None:
    for port in (8115, 5115):
        with socket.socket() as connection:
            connection.settimeout(0.2)
            if connection.connect_ex(("127.0.0.1", port)) == 0:
                raise RuntimeError(
                    f"Port {port} is occupied; inspect its owner. No process was stopped."
                )


def main() -> None:
    free_ports()
    (ROOT / ".runtime").mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix="e2e-", dir=ROOT / ".runtime") as directory:
        root = Path(directory)
        codes = initialize(root)
        seed(Repository(root / "evidence.sqlite3"))
        env = {
            **os.environ,
            "EVIDENCE_HOME": str(root),
            "npm_config_cache": str(ROOT / ".runtime/npm-cache"),
            "EVIDENCE_PROFILE": "fixture",
            "EVIDENCE_TEST_READER_CODE": codes["reader"],
            "EVIDENCE_TEST_MAINTAINER_CODE": codes["maintainer"],
            "PLAYWRIGHT_BROWSERS_PATH": os.getenv(
                "PLAYWRIGHT_BROWSERS_PATH", str(ROOT / ".runtime/ms-playwright")
            ),
            "PATH": str(ROOT / ".runtime/toolchain/node_modules/.bin")
            + os.pathsep
            + os.environ["PATH"],
        }
        server = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "evidence_rag.app:create_default_app",
                "--factory",
                "--host",
                "127.0.0.1",
                "--port",
                "8115",
                "--no-access-log",
            ],
            cwd=ROOT,
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        try:
            deadline = time.monotonic() + 20
            while True:
                if server.poll() is not None:
                    raise RuntimeError("Owned API exited before readiness")
                try:
                    with urllib.request.urlopen(
                        "http://127.0.0.1:8115/health", timeout=0.5
                    ) as response:
                        if response.status == 200:
                            break
                except (urllib.error.URLError, TimeoutError):
                    if time.monotonic() > deadline:
                        raise RuntimeError("API readiness timed out") from None
                    time.sleep(0.1)
            result = subprocess.run(
                ["npm", "exec", "--", "playwright", "test", *sys.argv[1:]],
                cwd=ROOT / "web",
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                check=False,
            )
            output = result.stdout
            for code in codes.values():
                output = output.replace(code, "[redacted launch code]")
            print(output, end="")
            if result.returncode:
                raise SystemExit(result.returncode)
        finally:
            server.terminate()
            try:
                server.wait(timeout=5)
            except subprocess.TimeoutExpired:
                server.kill()
                server.wait(timeout=5)


if __name__ == "__main__":
    main()
