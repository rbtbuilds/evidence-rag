# V1 verification evidence

This is a local source-checkout demonstration over owned fictional data. It has not been published, pushed, deployed or run on a customer workload. GitHub-hosted CI has not been run; its fixture workflow is committed for future authorised publication.

## Verified application checks

- `./scripts/check.sh`: Ruff passes; strict Pyright reports zero errors/warnings; 85 Python fixture tests pass with one actual-model test deselected and sockets denied except loopback/Unix; strict TypeScript includes source/tests/configs; 11 Vitest tests pass; Vite production build passes; exported OpenAPI/generated TypeScript drift checks and corpus hashes pass.
- `uv run --extra ml python scripts/e2e_server.py`: five actual browser-to-API tests pass. They cover reader login/question/current citation; invalid code and unsupported question; privileged cache warmup then reader isolation; import, replacement, deletion and stale source links; escaped HTML; both themes at 360/900/1440 px; no horizontal overflow; citation heading/return focus and Escape returning delete-dialog focus.
- An emoji regression failed with the wrong highlighted substring, then passed after converting UTF-16 strings to Unicode code points before slicing. A sign-out concurrency regression failed before sign-in was held until sign-out completed. A dark secondary-button contrast regression measured 1.15:1 before the specificity fix; the rendered-button check then passed its 4.5:1 threshold in both themes.
- Application errors use a generic typed envelope and request identifiers. A log capture proves raw URL query content is absent. Five parallel failed logins share one atomic per-source limit; successful logins do not consume it. Preflight accepts only the exact configured origin.

The test launcher owns a fresh temporary database, passes ephemeral codes through child environment, redacts stdout, disables browser traces/videos and stops only its own processes. Tests do not intercept application fetch. Failed import/replacement drafts retain their inputs and original revision for explicit recovery; component tests cover retry and cancellation, and a browser regression covers job status across citation navigation. Browser screenshots were visually reviewed; the README image is an inspected fixture capture with no credentials.

## Access, lifecycle and resource checks

The fixture matrix exercises two roles, four methods and active/replaced/deleted sources with repeated cache calls. Its privileged warmup precedes reader checks. Both the original and replacement restricted markers are checked for every reader response and for all roles after deletion. Three injected-leak regressions prove the guard detects the replacement marker. Forbidden reader strings are absent, and emitted sources resolve only while active and accessible. Reader BM25 rankings stay unchanged after adding a private document; corrupt private vectors do not affect reader scoring.

Blocking drafts prove deletion wins over late replacement and invalidates a pending full rebuild with stale_job. Simultaneous generation barriers keep reader and maintainer responses isolated across all four methods; repeated calls exercise their separate caches. An injected SQLite failure preserves the previous revision and FTS rows. Rebuilds reject source/chunk mismatches. Deleted source titles and version labels are replaced by system tombstone metadata, in addition to clearing bodies/chunks/vectors/FTS/cache/job payloads. Logical removal is tested; disk/WAL forensic erasure is not promised.

Generation/deletion barriers prove both publication orders: delete first yields 409 without stale text; an answer body holding the gate finishes before delete success. Expiry is rechecked before publication. Cache is user/role/epoch/request/revision scoped, limited to 128 entries and five minutes.

Lease tests cover competing owners, wrong ownership tokens, worker termination/join before release, malformed JSON, unavailable snapshots, RSS/time limits, bounded interactive queue admission and four-item embedding batches. Version, document, staged-chunk, input-body and queue limits reject work before publication. Model preparation is tested to reuse existing immutable SHAs and preserve the recorded lock; workers verify snapshot file hashes before weight loading.

## Actual-model generation repair evidence

The original v1 Qwen policy rejected all 96 development and 192 test outputs; [evaluation-v2.json](../reports/evaluation-v2.json) and its smoke/matrix reports remain unchanged. [Diagnosis and repair](GENERATION-REPAIR.md) document development-only probes, the selected constrained decoder, exact-ID schema, two-citation generation bound and focused review fixes. The public validator, access/version checks and response publication gate remain strict.

Development: 83/96 answers accepted, 11 insufficient-evidence abstentions, 2 invalid outputs, 160/160 citations resolved and 2 output-limit hits. The repaired local Qwen block accepted 183/192 test answers, returned 2 insufficient-evidence abstentions and rejected 7 invalid outputs. All 347/347 emitted citations resolved to accessible current passages; 9 outputs hit the 256-token budget. Expected-abstention decisions were correct in 1/48 method/question cases. The sole correct test expected-abstention decision came from invalid-output rejection; no explicit insufficient-evidence response correctly handled an expected-abstention case. This measures format/citation validity and abstention, not factual support or completeness.

All six refreshed runs used clean source e3823ce2a47d78b336aa0b6476c663f0b3206d6e, the same pinned snapshots/corpus/questions, and one lease per complete benchmark. [evaluation-v3.json](../reports/evaluation-v3.json) records hashes, timings, token-limit counts and separated fixture/actual results. There were no forbidden-marker disclosures, embedding truncations or dropped passages. These are synthetic local observations; factual support/completeness remain unmeasured.

`uv run --extra ml python -m scripts.actual_generation_browser` passed one actual browser/API/Qwen scenario: genuine reader session, local profile, BM25, accepted answer containing 35, resolved citations and opened current v2 passage. This dedicated serial helper holds one model worker/lease and uses no fetch interception or fake generation. It does not claim dense/reranking browser coverage. Ordinary browser runs pass five scenarios and explicitly skip the actual one.

`uv run --extra ml pytest -m real_model tests/integration/test_actual_disclosure.py -q -s` passed a new 96-request matrix over roles, all retrieval methods, both answer modes, cold/warm caches and active/replaced/deleted sources. See [actual-access-matrix-v3.json](../reports/actual-access-matrix-v3.json). Both restricted markers were checked and every emitted citation opened only while current and accessible. This is serial evidence; the fixture barriers above prove race ordering separately.

The new actual smoke returned a 384-dimensional embedding, a rerank logit and valid Qwen JSON answering 35 units. [local-smoke-v3.json](../reports/local-smoke-v3.json) records the settings and token count. All owned workers exited before their leases were released.

## Clean checkout and remaining limits

`./scripts/clean_clone_check.sh` passed at e3823ce2a47d78b336aa0b6476c663f0b3206d6e: frozen ordinary installs, 85 Python tests, 11 web tests, strict checks/build/contracts, five fixture browser scenarios (one actual scenario explicitly skipped), and 192 fixture test evaluation rows on 8115/5115. Its task-owned temporary clone was removed by its scoped cleanup. The separate actual browser check above supplies model evidence; clean-clone verification does not load weights.

Runtime: Python 3.12.14, project-local Node v24.22.0, uv 0.12.5, Apple M5 Pro. No global configuration, parent/sibling repository, vault, operations record or archive changed. No publication, push, public CI or deployment occurred.

Human citation support/completeness and screen-reader use remain unmeasured. Qwen still gives incorrect answers to unsupported questions, and valid source IDs do not prove entailment. The small repetitive corpus cannot establish enterprise retrieval quality, production identity or a general security proof. Original whole-branch review decisions remain in [REVIEW.md](REVIEW.md); the focused generation review and its resolved findings are in [GENERATION-REPAIR.md](GENERATION-REPAIR.md).
