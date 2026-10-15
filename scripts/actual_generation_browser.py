"""Explicit leased browser/API/Qwen check, using one real borrowed model worker."""

import os
import subprocess
import tempfile
import threading
import time
from pathlib import Path
from typing import cast

import uvicorn

from evidence_rag.answers.service import AnswerService, PendingAnswer
from evidence_rag.app import create_app
from evidence_rag.auth.sessions import initialize
from evidence_rag.config import Settings
from evidence_rag.contracts import QuestionRequest
from evidence_rag.db.repository import AccessScope, Repository
from evidence_rag.documents.ingest import seed
from evidence_rag.models.runner import ModelRunner, ModelSession
from scripts.e2e_server import ROOT, free_ports


def main() -> None:
    free_ports()
    model_root = Settings.from_env().root
    with tempfile.TemporaryDirectory(prefix="actual-browser-", dir=ROOT / ".runtime") as directory:
        runtime = Path(directory)
        codes = initialize(runtime)
        seed(Repository(runtime / "evidence.sqlite3"))
        app = create_app(Settings(runtime, "local"))
        answers = cast(AnswerService, app.state.answers)
        answers.settings = Settings(model_root, "local")
        real_answer = answers.answer
        with ModelRunner(model_root).session("actual Qwen browser flow", timeout=600) as shared:

            def answer(
                scope: AccessScope, request: QuestionRequest, session: ModelSession | None = None
            ) -> PendingAnswer:
                shared.begin_request()
                return real_answer(scope, request, shared)

            answers.answer = answer
            server = uvicorn.Server(
                uvicorn.Config(app, host="127.0.0.1", port=8115, access_log=False, log_config=None)
            )
            thread = threading.Thread(target=server.run, daemon=True, name="owned-actual-api")
            thread.start()
            try:
                deadline = time.monotonic() + 20
                while not server.started:
                    if not thread.is_alive() or time.monotonic() > deadline:
                        raise RuntimeError("Owned actual API did not become ready")
                    time.sleep(0.05)
                env = {
                    **os.environ,
                    "PATH": str(ROOT / ".runtime/toolchain/node_modules/.bin")
                    + os.pathsep
                    + os.environ["PATH"],
                    "npm_config_cache": str(ROOT / ".runtime/npm-cache"),
                    "PLAYWRIGHT_BROWSERS_PATH": str(ROOT / ".runtime/ms-playwright"),
                    "EVIDENCE_TEST_READER_CODE": codes["reader"],
                    "EVIDENCE_TEST_MAINTAINER_CODE": codes["maintainer"],
                    "EVIDENCE_TEST_ACTUAL_GENERATION": "1",
                }
                completed = subprocess.run(
                    ["npm", "exec", "--", "playwright", "test", "local-generation.spec.ts"],
                    cwd=ROOT / "web",
                    env=env,
                    text=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    check=False,
                )
                output = completed.stdout
                for code in codes.values():
                    output = output.replace(code, "[redacted launch code]")
                print(output, end="")
                if completed.returncode:
                    raise SystemExit(completed.returncode)
            finally:
                server.should_exit = True
                thread.join(10)
                if thread.is_alive():
                    raise RuntimeError("Owned actual API failed to stop")


if __name__ == "__main__":
    main()
