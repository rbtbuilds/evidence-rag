# Local operation

## Fresh checkout

Use Python 3.12.x, uv, and Node 24 LTS. Node 26 is not the CI target. Do not replace a machine runtime; put an existing Node 24 binary on PATH. On the build Mac a project-local Node 24 binary is available under `.runtime/toolchain/node_modules/.bin`, which is ignored and is not part of a checkout.

Run from the repository root:

```sh
export UV_CACHE_DIR="$PWD/.runtime/uv-cache"
export npm_config_cache="$PWD/.runtime/npm-cache"
uv sync --frozen
npm --prefix web ci
uv run evidence-rag init
uv run evidence-rag seed-fixtures
uv run evidence-rag doctor
uv run uvicorn evidence_rag.app:create_default_app --factory --host 127.0.0.1 --port 8115 --no-access-log
```

In another terminal in the same checkout:

```sh
npm --prefix web run dev
```

Open `http://127.0.0.1:5115`. The API accepts Host `127.0.0.1:8115` and mutations only from that exact web Origin. Vite uses strictPort. Use one API process; multiple Uvicorn workers are unsupported because publication ordering uses one process lock. Do not change reserved ports to bypass an unknown listener; inspect its owner first.

`init` prints independent reader/maintainer launch codes once. Save them privately in your terminal session. Only code hashes are stored in `.runtime/demo-codes.json` with mode 0600. `init` refuses an existing setup; `uv run evidence-rag reset` is the explicit code rotation and session-revocation command. Reset does not reseed, delete documents or repair indexes. Run it with the API stopped. No login code is committed or stored in browser storage.

The app reads exported environment variables, not `.env` automatically. `EVIDENCE_PROFILE` is fixture or local. `EVIDENCE_HOME`, if set, must stay under this checkout's `.runtime`; it cannot point at a sibling or archive. Profile changes do not reinterpret an existing vector index.

## Reader walkthrough

Sign in using the reader code. Ask `What is the circulation display limit?`; the v2 quotation contains 35 units. Open the Circulation citation and inspect the underlined exact text and date. Ask `Which lunar alloy is used?` to see an evidence abstention. Sign out before changing identities. Source text and hostile quoted instructions are displayed literally; no remote images or raw HTML execute.

## Replacement and deletion

Sign in as maintainer. In Document maintenance choose Replace, supply a fresh version label, date, title, explicit minimum role and heading-led Markdown, then Queue replacement. The old active edition stays available until the job succeeds. Refresh job reads status; Cancel job is idempotent. The worker admits at most eight queued/running jobs and clears terminal payloads. A failed or cancelled draft cannot retire the active version.

On success the next question uses the new version and old ordinary citation links return 404. A maintainer may explicitly inspect non-deleted superseded history through the documented admin endpoint. Reader history/jobs are forbidden before ID lookup.

Delete names the document in an in-app confirmation and uses its revision as `If-Match`. A stale revision returns 409. Success invalidates affected role caches, cancels pending replacements, removes chunks/vectors/FTS bodies, nulls every source version body and removes source title/labels from tombstones before publishing 204. This is logical removal; it does not promise disk/WAL/backups forensic erasure or recall of already seen information. Deleted history is inaccessible. No late draft may restore it.

## Optional actual models

The default is account-free fixture mode: real FTS5, deterministic embedding/reranker doubles and source quotations. It is labelled visibly. Model weights are optional, separately licensed and never committed.

```sh
uv sync --frozen --extra ml
uv run --extra ml evidence-rag prepare-models
uv run --extra ml evidence-rag doctor --models
export EVIDENCE_PROFILE=local
uv run --extra ml uvicorn evidence_rag.app:create_default_app --factory --host 127.0.0.1 --port 8115 --no-access-log
```

Preparation downloads only public safetensors/config/tokenizer/card/licence files, checks expected licences, resolves immutable SHAs and records actual file hashes. HF and Xet caches stay in this runtime and implicit account tokens are disabled. Preparation is a network action; requests never download models. `doctor --models` hashes snapshots without loading weights. Runtime uses CPU float32, four threads, no remote code and local-only files. `config/models.lock.json` is the provenance record for the snapshots actually prepared, not a model upload.

After switching to local profile, use Rebuild index as maintainer before dense/hybrid requests. Missing/mismatched revisions return `model_unavailable`; fixture vectors are never silently treated as real embeddings. Switching back similarly requires an explicit fixture rebuild. Pending work stays single-worker. Actual requests acquire a machine lease, use one supervised child and exit it before release. Uncached interactive requests may reload weights; do not confuse warm benchmark times with that load cost.

Qwen currently fails this v1 generation contract in the recorded benchmark, so local generated answers abstain. Exact quotations remain useful in local profile. Do not relax output/citation validation to make the displayed success rate look better.

## Shared machine lease and failures

Heavy operations atomically mkdir `/tmp/bentolabs-portfolio-ml.lock` and record project, PID, process start time, UTC start, purpose and a random ownership token. A busy lease returns `model_busy`; it is never polled or stolen. Continue light work. Each complete benchmark holds one lease. No model process stays resident after release.

For suspected stale ownership, inspect `owner.json`, `ps -p <recorded-pid> -o pid,lstart,command`, and the actual process start time. Check the project and purpose as well as PID; PID reuse alone proves nothing. Do not delete another project's lock or stop an unknown process. The normal supervisor terminates, waits, escalates only its own child if needed, and compares its token before release. Any manual recovery requires separate evidence and authorisation.

Interactive admission/model work has a 90-second deadline, indexing ten minutes, worker RSS 6 GiB, IPC 16 MiB, embedding batch four, final context at most five passages, and at most two queued interactive requests. Failure codes distinguish busy, unavailable, timeout, memory limit and full queue. The client does not retry mutations automatically. Keep the old version while investigating an indexing failure.

A source change during generation returns `corpus_changed` with no stale answer text. Session expiry returns 401 even if generation already finished. Ask again explicitly after refreshing state. Restart marks running jobs interrupted and clears their payload; it does not silently replay them. Queued jobs remain queued for the one worker. No progress percentage is invented.

For storage errors, stop this API, retain the runtime unchanged, and inspect SQLite integrity on a task-owned backup. Never delete an existing database, force-remove WAL files, or reseed over work to hide an error. Recovery of real data is outside this demo's scope. Application HTTP logs contain templates/status/request ID/duration; raw URL logging is disabled.

## Verification

```sh
./scripts/check.sh
export PLAYWRIGHT_BROWSERS_PATH="$PWD/.runtime/ms-playwright"
npm --prefix web exec -- playwright install chromium
npm --prefix web run test:e2e
./scripts/clean_clone_check.sh
```

Dependencies/browsers install with network access; Python application tests then disable external sockets and allow loopback/Unix sockets. Browser tests launch a new temporary database and owned API/web processes on 8115/5115, pass test codes through child environment only, and stop only their own servers. Their traces/videos are disabled and stdout redacts test codes. Do not leave manual servers on these ports during acceptance checks.

Ordinary CI excludes actual model work. The explicit command is `uv run --extra ml pytest -m real_model tests/integration/test_actual_disclosure.py -q -s`; it requires snapshots and the shared lease. Evaluation commands and interpretation are in [EVALUATION.md](../EVALUATION.md). Human citation review remains a separate pending step.
