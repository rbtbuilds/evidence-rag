# V1 verification evidence

This is a local source-checkout demonstration over owned fictional data. It has not been published, pushed, deployed or run on a customer workload. GitHub-hosted CI has not been run; its fixture workflow is committed for future authorised publication.

## Verified application checks

- `./scripts/check.sh`: Ruff passes; strict Pyright reports zero errors/warnings; 110 Python fixture tests pass with one actual-model test deselected and sockets denied except loopback/Unix; strict TypeScript includes source/tests/configs; 11 Vitest tests pass; Vite production build passes; exported OpenAPI/generated TypeScript drift checks and corpus hashes pass.
- `uv run --extra ml python scripts/e2e_server.py`: five fixture-profile browser-to-API tests pass. They cover reader login/question/current citation; invalid code and unsupported question; privileged cache warmup then reader isolation; import, replacement, deletion and stale source links; escaped HTML; both themes at 360/900/1440 px; no horizontal overflow; citation heading/return focus and Escape returning delete-dialog focus.
- An emoji regression failed with the wrong highlighted substring, then passed after converting UTF-16 strings to Unicode code points before slicing. A sign-out concurrency regression failed before sign-in was held until sign-out completed. A dark secondary-button contrast regression measured 1.15:1 before the specificity fix; the rendered-button check then passed its 4.5:1 threshold in both themes.
- Application errors use a generic typed envelope and request identifiers. A log capture proves raw URL query content is absent. Five parallel failed logins share one atomic per-source limit; successful logins do not consume it. Preflight accepts only the exact configured origin.

The test launcher owns a fresh temporary database, passes ephemeral codes through child environment, redacts stdout, disables browser traces/videos and stops only its own processes. Tests do not intercept application fetch. Failed import/replacement drafts retain their inputs and original revision for explicit recovery; component tests cover retry and cancellation, and a browser regression covers job status across citation navigation. Browser screenshots were visually reviewed; the README image is an inspected fixture capture with no credentials.

## Access, lifecycle and resource checks

The fixture matrix exercises two roles, four methods and active/replaced/deleted sources with repeated cache calls. Its privileged warmup precedes reader checks. Both the original and replacement restricted markers are checked for every reader response and for all roles after deletion. Three injected-leak regressions prove the guard detects the replacement marker. Forbidden reader strings are absent, and emitted sources resolve only while active and accessible. Reader BM25 rankings stay unchanged after adding a private document; corrupt private vectors do not affect reader scoring.

Blocking drafts prove deletion wins over late replacement and invalidates a pending full rebuild with stale_job. Simultaneous generation barriers keep reader and maintainer responses isolated across all four methods; repeated calls exercise their separate caches. An injected SQLite failure preserves the previous revision and FTS rows. Rebuilds reject source/chunk mismatches. Deleted source titles and version labels are replaced by system tombstone metadata, in addition to clearing bodies/chunks/vectors/FTS/cache/job payloads. Logical removal is tested; disk/WAL forensic erasure is not promised.

Generation/deletion barriers prove both publication orders: delete first yields 409 without stale text; an answer body holding the gate finishes before delete success. Expiry is rechecked before publication. Cache is user/role/epoch/request/revision scoped, limited to 128 entries and five minutes.

Lease tests cover competing owners, wrong ownership tokens, worker termination/join before release, malformed JSON, unavailable snapshots, RSS/time limits, bounded interactive queue admission and four-item embedding batches. Version, document, staged-chunk, input-body and queue limits reject work before publication. Model preparation is tested to reuse existing immutable SHAs and preserve the recorded lock; workers verify snapshot file hashes before weight loading.

## Actual-model abstention repair evidence

The retained v2 model policy rejected all 288 development/test outputs. The v3 generation-format repair made JSON/IDs usable but explicitly refused no expected-abstention test case; its one legacy abstention credit came from invalid-output rejection. Original reports and the exact archived Qwen2.5 lock remain unchanged. [Abstention diagnosis](ABSTENTION-REPAIR.md) records rejected models/classifiers, the larger native choice and coverage cost. The public validator, access/version checks and publication gate remain strict.

| Split | Proper expected refusals | Answerable responses | Unnecessary refusals | Invalid output | Citations resolved | Output-limit hits |
| --- | --- | --- | --- | --- | --- | --- |
| Development | 24/24 | 51/72 | 21 | 0 | 55/55 | 0 |
| Test | 46/48 | 109/144 | 35 | 0 | 120/120 | 0 |


The local Qwen3 14B block correctly returned explicit empty insufficient-evidence refusals in 46/48 expected-abstention test method/question cases, compared with 0/48 in v3. It answered 109/144 answerable cases and unnecessarily refused 35; 0 outputs were invalid. All 120/120 emitted citations resolved to accessible current passages. These are abstention and format/access measurements, not human factual-support or completeness scores. Two remaining errors are the same reader question under BM25 and hybrid: the model treats a quoted hostile instruction as evidence for a calibration marker. No restricted marker is disclosed.

All six canonical runs use clean source c4b3fffb049a448c4bddaefcfa23128188b0f8df, heading-window-v2, evidence-json-v4-abstention and the same frozen corpus/questions. They total 864 method/question rows. Model and dependency locks, raw hashes, machine, stage timings, per-role/stratum metrics and paired bootstrap intervals are retained. No forbidden-marker disclosure, embedding truncation or passage dropping occurred.

The generated blocks recorded at most 9,229,360,168 peak accelerator bytes (8.60 GiB) and 2,376,171,520 sampled worker RSS bytes (2.21 GiB). Do not add these as independent allocations on unified memory. Native generation uses a 12 GiB detected-peak threshold and 256 MiB allocator cache guideline; sampled worker RSS remains capped at 6 GiB. MLX allocation limits are guidelines, so transient overshoot can precede detection.

The final actual browser/API/Qwen scenario passed in 17.4 seconds (18.3-second Playwright run): genuine reader session, local profile/real BM25, 35-unit answer, current v2 source, empty lunar-alloy and reader-private-marker refusals, and supported cached-answer retention. The dedicated helper holds one worker/lease and uses no fetch interception. It does not claim dense browser coverage; the serial actual API matrix covers all retrieval methods separately.

The stricter actual matrix passed 96 requests in 82.59 seconds over roles, methods, generation modes, cold/warm caches and active/replaced/deleted sources. The 32 local reader/deleted rows explicitly refused with empty answers/no citations; 16 authorised local active/replaced rows answered the correct marker. Both restricted markers were checked; emitted citations opened while current/access permitted and old links failed after mutation. Fixture barriers establish race ordering independently. [Actual matrix](../reports/actual-access-matrix-v4.json).

The actual smoke returned a 384-dimensional embedding, a rerank score and valid 35-unit JSON in 23 tokens, with no output-limit hit. [Smoke provenance](../reports/local-smoke-v4.json). Re-preparation preserved the model lock and pinned hashes. The matrix/smoke ran during implementation before the source commit; their curated records identify the unchanged source tree subsequently frozen for canonical evaluation. All workers exited before their own lease release.

## Clean checkout and remaining limits

`./scripts/clean_clone_check.sh` passed at c4b3fffb049a448c4bddaefcfa23128188b0f8df: frozen ordinary installs, 110 Python tests, 11 web tests, strict checks/build/contracts, five fixture browser scenarios (one actual scenario explicitly skipped) and 192 fixture evaluation rows on 8115/5115. Its task-owned temporary clone was removed. No optional model weights loaded in that check; actual model evidence is separate.

Runtime: Python 3.12.14, project-local Node 24.22.0, uv 0.12.5, Apple M5 Pro with 24 GiB. Actual generation requires Apple Silicon/Metal. No public CI, publication, push or deployment occurred.

The reused frozen test is regression evidence after earlier disclosed runs, not a new unseen generalisation study. Policy/model selection used development evidence only; test outputs did not change the policy. The corpus is small, repetitive and fictional. The model still misses two expected refusals and sacrifices answerable response coverage; accepted answers can still be incomplete or unsupported. Exact quotations remain the default. Human source support/completeness, screen-reader use and customer impact remain unmeasured.

Original whole-branch review decisions remain in [REVIEW.md](REVIEW.md). The focused native/decision/resource/provenance review and one author fix pass are in [ABSTENTION-REPAIR.md](ABSTENTION-REPAIR.md). Separate classifiers were removed after empirical rejection; unlisted weights and non-finite masking were fixed. Production identity/public hosting, multiple API processes and non-Apple native execution remain excluded.
