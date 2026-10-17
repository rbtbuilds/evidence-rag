# Verification evidence

This is a local demonstration over owned fictional sources, with exact quotations as default. Native generation is optional and has known semantic failures. No public CI run, customer pilot, publication, push or deployment is claimed.

## Strict application checks

At frozen source 9a324b8, ./scripts/check.sh passed Ruff, strict Pyright with zero errors/warnings, 125 Python tests with two actual-model tests deselected, strict TypeScript including tests/configuration, 11 Vitest tests, the production build, OpenAPI/generated-type drift and corpus validation. Python tests denied outbound sockets except loopback/Unix sockets. The log is .runtime/quality-review-fixed-check.log. The final checkout check is recorded separately after the complete publication artifact commit.

Five fixture browser scenarios passed, with the actual-model scenario explicitly skipped. They use genuine API sessions and no intercepted fetches: reader question/current citation, invalid/unsupported requests, privileged cache warmup then reader isolation, import/replacement/deletion and stale links, escaped HTML, both themes at 360/900/1440 pixels, overflow and keyboard/dialog focus. Fixture embeddings/reranking are test doubles, not measured native model results.

## Boundary guarantees exercised

Reader scope is enforced before scoring/reranking/generation and source opens; role-specific FTS prevents private statistics changing reader rank. Fixture tests cover private-vector corruption, separate role caches and simultaneous generation barriers. Mutation tests cover atomic SQLite rollback, deletion winning against late replacement/rebuild, body/metadata/job-payload removal and stale links. Publication barriers exercise both orders: deletion first discards a pending answer with 409; an answer already publishing finishes before deletion returns success. Session expiry is rechecked at publication. Logical removal is tested; disk/WAL/backups forensic erasure is not promised.

The serial actual API matrix passed 96 requests in 85.72 seconds, with four retrieval methods, two roles, both generation modes, cold/warm cache calls and active/replaced/deleted sources. Its 32 local reader/deleted rows properly refused; 16 authorized active/replaced rows answered current markers; forbidden disclosure count was zero. Emitted citations opened while current/access permitted; old links failed after mutation. reports/actual-access-quality-v1.json retains the exact test hash and uncommitted-tooling context. It is separate from the clean-source final quality evaluation. Fixture barriers establish race ordering independently of this serial matrix.

## Native browser and demo

The genuine local Qwen/API/BM25 scenario passed in 19.1 seconds (20.1-second runner). The paced capture passed in 35.6 seconds (36.6-second runner): supported 35-unit answer, current v2 source, three empty unsupported refusals including the quoted marker request, and a cached supported answer. Login occurs outside a separate recorded context; cookies transfer only in memory. No fetch interception or fabricated progress is used. Reading pauses explain the 34.92-second retained recording and are not latency measurements. Images and sampled video frames received AI-assisted inspection, not human/full-frame review.

## Deliberate negative quality evidence

The selected native eight-pair semantic test remains failed (one test, two failing pairs, 21.31 seconds): a current-value correction returns only No; a quantity answer returns 13 without the counted noun. The second development policy fixed those but regressed quoted-request grounding and failed the API reader-refusal assertion. It was rejected. Neither test nor oracle was weakened to obtain a pass. Both substantive iterations are exhausted; no final-output tuning is allowed. See QUALITY-DEVELOPMENT.md and QUALITY-REVIEW.md.

The fresh AI code reviewer found two important coordination/reporting bugs. Failed worker joins now retain the outer machine lease; case-changed forbidden values now reach regression disclosure counts. Focused tests failed before repair, then 7/7 passed; full strict checks passed 125 Python/11 web. No critical/deferred-minor findings remained. This is AI-assisted review, not human source-support certification.

## Frozen final evaluation

On the exposed test, proper refusals changed from 46/48 to 47/48 and answerable responses from 109/144 to 109/144; unnecessary refusals changed from 35 to 35. On the new challenge, proper refusals changed from 30/32 to 32/32 and finite-oracle complete coverage from 56/64 to 57/64, while response coverage changed from 64/64 to 60/64.

The pre-registered quality gate failed: regression_refusals, regression_coverage, challenge_no_unverified_answers. Exact quotations remain the default. No final-output tuning, oracle relaxation or third policy iteration occurred. Exactly 384 actual-model rows completed at clean source `9a324b82e446f9ac3ddc6ff834846cd0e30c5d80` with unchanged provenance. All 24 original reports remain preserved. [QUALITY-RESULTS.md](QUALITY-RESULTS.md) explains finite-oracle false negatives and keeps citation resolution separate from support.

The exposed-test targets were 48/48 proper refusals and at least 116/144 answerable responses; observed 47/48 and 109/144 miss both. Hybrid still answers test-041 with `restricted calibration review marker`, citing the public training quotation instead of refusing a value question. No private marker is disclosed. The general grounding defect is reduced, not eliminated, and answerable response coverage did not improve.

## Reproducibility and limits

Use RUNBOOK.md for ordinary and explicit actual-model commands; EVALUATION.md defines denominators, frozen gates and final provenance. Model loads use pinned local snapshots under the shared machine lease. Busy means defer, not fixture fallback. The final comparison holds the lease across all phases and writes completion only after successful cleanup. No resident model server is retained.

Human factual support/completeness, screen-reader use, real customer outcomes, broad generalisation, throughput and production authentication remain unmeasured. Accessible current citations are a mechanical guarantee, not proof of factual support. The new finite AI-authored oracle is narrower than general entailment and can reject correct paraphrases.

## Complete artifact checkout

`./scripts/clean_clone_check.sh` passed at `46fa2b4cf7577330a5eb84ce7b97ab6f1adb7f2f`: 36 ordinary Python packages installed, frozen web install, strict checks, 125 Python tests (2 actual tests deselected), 11 web tests, build/contracts/corpus, five genuine fixture browser flows (3.7s; one actual scenario skipped) and 192 fixture evaluation rows. The task-owned clone was removed. Log SHA-256: `713ad8da9156b270bd18b7859298567d398fd78ef7949f7fe4d8062e34993f93`. The host supplied Node 24/Chromium; this is checkout reproducibility on the same Mac, not a fresh operating system or hosted CI.

The fixture evaluation produced 32/48 proper expected refusals and 143/144 answerable responses, with zero invalid/disclosed outputs and 236/236 resolving citations. These doubles/quotation results are distinct from native generation. Quoting a current accessible passage can still fail question relevance or refusal correctness. Later changes record verification evidence/formatting only; runtime source is unchanged from 9a324b8.
