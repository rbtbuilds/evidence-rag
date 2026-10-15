# V1 verification evidence

This is a local source-checkout demonstration over owned fictional data. It has not been published, pushed, deployed or run on a customer workload. GitHub-hosted CI has not been run; its fixture workflow is committed for future authorised publication.

## Verified application checks

- `./scripts/check.sh`: Ruff passes; strict Pyright reports zero errors/warnings; 63 Python fixture tests pass with one actual-model test deselected and sockets denied except loopback/Unix; strict TypeScript includes source/tests/configs; eight Vitest tests pass; Vite production build passes; exported OpenAPI/generated TypeScript drift checks and corpus hashes pass.
- `uv run --extra ml python scripts/e2e_server.py`: five actual browser-to-API tests pass. They cover reader login/question/current citation; invalid code and unsupported question; privileged cache warmup then reader isolation; import, replacement, deletion and stale source links; escaped HTML; both themes at 360/900/1440 px; no horizontal overflow; citation heading/return focus and Escape returning delete-dialog focus.
- An emoji regression failed with the wrong highlighted substring, then passed after converting UTF-16 strings to Unicode code points before slicing. A sign-out concurrency regression failed before sign-in was held until sign-out completed. A dark secondary-button contrast regression measured 1.15:1 before the specificity fix; the rendered-button check then passed its 4.5:1 threshold in both themes.
- Application errors use a generic typed envelope and request identifiers. A log capture proves raw URL query content is absent. Five parallel failed logins share one atomic per-source limit; successful logins do not consume it. Preflight accepts only the exact configured origin.

The test launcher owns a fresh temporary database, passes ephemeral codes through child environment, redacts stdout, disables browser traces/videos and stops only its own processes. Tests do not intercept application fetch. Browser screenshots were visually reviewed; the README image is an inspected fixture capture with no credentials.

## Access, lifecycle and resource checks

The fixture matrix exercises two roles, four methods and active/replaced/deleted sources with repeated cache calls. Its privileged warmup precedes reader checks. Forbidden reader strings are absent, and emitted sources resolve only while active and accessible. Reader BM25 rankings stay unchanged after adding a private document; corrupt private vectors do not affect reader scoring.

A blocking draft proves deletion wins over late replacement. An injected SQLite failure preserves the previous revision and FTS rows. Rebuilds reject source/chunk mismatches. Deleted source titles and version labels are replaced by system tombstone metadata, in addition to clearing bodies/chunks/vectors/FTS/cache/job payloads. Logical removal is tested; disk/WAL forensic erasure is not promised.

Generation/deletion barriers prove both publication orders: delete first yields 409 without stale text; an answer body holding the gate finishes before delete success. Expiry is rechecked before publication. Cache is user/role/epoch/request/revision scoped, limited to 128 entries and five minutes.

Lease tests cover competing owners, wrong ownership tokens, worker termination/join before release, malformed JSON, unavailable snapshots, RSS/time limits, bounded interactive queue admission and four-item embedding batches. Version, document, staged-chunk, input-body and queue limits reject work before publication. Model preparation is tested to reuse existing immutable SHAs and preserve the recorded lock; workers verify snapshot file hashes before weight loading.

## Actual-model evidence

Three pinned public snapshots were downloaded and exercised locally. A final smoke run returned a 384-dimensional embedding, a raw rerank logit and Qwen output in a leased CPU worker; the child exited before release. The Qwen output used an invalid citation key and is not an accepted application answer.

Separate development/test reports cover all four actual retrieval methods with quotation and Qwen generation fixed per block. See [EVALUATION.md](../EVALUATION.md) and [reports](../reports/README.md). No embedding truncations occurred in the recorded runs. Model generation failed its contract and abstained on every recorded Qwen test output; this is a failure, not a successful quality result. Human support/completeness fields remain unmeasured.

`uv run --extra ml pytest -m real_model tests/integration/test_actual_disclosure.py -q -s` passed a separate 96-request serial matrix over both roles, both generation modes, all four retrieval methods, cold/warm caches and active/replaced/deleted sources. Its report is [actual-access-matrix.json](../reports/actual-access-matrix.json). Fixture barrier tests establish race ordering separately; serial actual requests do not prove races. A busy-lease retry returned `model_busy` and did not remove another owner's lock.

## Clean checkout and remaining limits

The task-owned clean-clone script passed at source commit a7dafa12a7915c38f8b149c12ade081a431b1c58. It completed frozen ordinary installs, 63 fixture tests, eight web tests, strict checks/build/contracts, five real browser scenarios and the 192-row fixture test evaluation on ports 8115/5115. It clones locally without shared Git object hardlinks, installs frozen ordinary dependencies into the clone, initialises/seeds a new database, runs full fixture checks and the actual browser flow on 8115/5115, then runs fixture evaluation. Its cleanup removes only its own mktemp directory. It does not load models or contact a hosted inference service.

No human citation-support/completeness review or screen-reader session has occurred. The small repetitive synthetic corpus cannot establish enterprise retrieval performance, factual correctness, production authentication or a general security proof. No hosted CI, deployment, external integration, OCR/PDF ingestion or real customer data was exercised. These are explicit limits, not silently skipped passing checks.

The build runtime was Python 3.12.14, project-local Node v24.22.0 and uv 0.12.5 on Apple M5 Pro. A post-hardening refresh of the separately retained actual-model reports is running; it does not substitute fixtures for model evidence. Final review findings are recorded in STATE when the fresh reviewer completes.
