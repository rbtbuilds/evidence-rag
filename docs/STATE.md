# Evidence RAG state

Updated: 2026-10-16. Abstention repair is in progress; see [ABSTENTION-REPAIR.md](ABSTENTION-REPAIR.md). Active local generation is now pinned native Qwen3 14B four-bit, thinking disabled, explicit empty-refusal/current-fact policy and 180-character answer bound. In 36 development probes it correctly refused all 12 unsupported cases and answered 19/24 answerable cases; five false refusals remain a known coverage cost. The 4B candidate passed BM25/browser checks but failed a dense-reader refusal and was rejected as a complete repair. The 14B actual browser flow passed, as did the stricter 96-request actual access/lifecycle matrix across all four methods (82.59 seconds). Strict checks pass 110 Python tests, 11 web tests and build/contracts/corpus checks. Canonical evaluation and final clean-checkout verification remain pending. Resource policy: 6 GiB sampled worker RSS, 12 GiB detected accelerator peak, 256 MiB allocator cache guideline. Strict citation/access/version/publication checks remain unchanged. No publication, push, deployment, paid work or external send occurred. Human citation support/completeness remain unmeasured.

The generation-format repair and evaluation below remain the retained v3 baseline on feat/evidence-rag-v1.

## Ownership and frozen source

Owned checkout/Git root: /Users/matthewgoralczyk/BentoLabs/portfolio/evidence-rag. The inherited resume workspace was not used. Only this child was edited. Ports 8115/5115 bind loopback. Every actual model run held the shared atomic lease and exited its owned worker before release. No remote is configured.

The original ten approved tasks were completed using superpowers:executing-plans; their application includes server-side opaque demo sessions, four access-filtered retrieval methods, versioned exact citations, scoped caches, transactional replacement/deletion, bounded model/index workers and the React workbench. Baseline implementation source: 5ca23d349e79916a22fb084cf58a41c7bdcda0b6; original final evidence/docs: 30f06cd. Retained baseline evidence: reports/evaluation-v2.json.

Repair implementation: d686d9e (schema/ID-constrained generation, typed core adapter, regression tests, provenance and dedicated browser helper), followed by e3823ce (two-citation decoding bound). All six new canonical evaluation blocks use clean source e3823ce2a47d78b336aa0b6476c663f0b3206d6e, heading-window-v2 and evidence-json-v3-bounded. Subsequent commits document/retain those measured results only. Corpus, questions and pinned model lock are unchanged.

## Diagnosis and implementation

Qwen renamed/missed required keys and mistyped long citation IDs. Explicit repetition penalty 1.0 alone did not fix it; JSON examples sometimes copied placeholders and were rejected as the solution. A pinned lm-format-enforcer schema and per-request authorised-ID enum fix format/copying, while a two-citation decoding limit leaves room within 256 tokens. The public validator remains unchanged with a five-citation ceiling; malformed JSON, unknown IDs, stale versions and inaccessible sources still fail closed. No fuzzy repair or alias acceptance was added. [Full diagnosis and review](GENERATION-REPAIR.md).

## Current results

| Split | Accepted answers | Insufficient evidence | Invalid output | Citations resolved | Output-limit hits | Correct expected abstentions |
| --- | --- | --- | --- | --- | --- | --- |
| Development | 83/96 | 11 | 2 | 160/160 | 2 | 2/24 |
| Test | 183/192 | 2 | 7 | 347/347 | 9 | 1/48 |

The repaired local Qwen block accepted 183/192 test answers, returned 2 insufficient-evidence abstentions and rejected 7 invalid outputs. All 347/347 emitted citations resolved to accessible current passages; 9 outputs hit the 256-token budget. Expected-abstention decisions were correct in 1/48 method/question cases. The sole correct test expected-abstention decision came from invalid-output rejection; no explicit insufficient-evidence response correctly handled an expected-abstention case. This measures format/citation validity and abstention, not factual support or completeness.

All six blocks total 864 rows, with no forbidden-marker disclosure, embedding truncation or passage dropping. Actual test retrieval recall@5 remains 1.0 for every method on 36 eligible questions per method. Dense/hybrid MRR is 1.0; BM25/reranked hybrid is 0.9861. Quotation expected-abstention result remains 8/12 per actual test method. This repetitive fictional corpus is easy; no customer-impact or enterprise-quality claim is made.

The baseline rejected all 288 generation outputs. The repair makes generation operational, but Qwen still answers unsupported questions incorrectly. Exact quotations remain the default. Citation support/completeness need the new review-v3 sheets and remain unmeasured; no automated score is substituted for human review.

## Exact verification

- `./scripts/check.sh`: Ruff; strict Pyright with zero errors/warnings; 85 Python fixture tests, one real-model test deselected; strict TypeScript including test/config files; 11 Vitest tests; production build; OpenAPI/type and corpus drift checks.
- `./scripts/clean_clone_check.sh`: passed at e3823ce with frozen fresh installs, 85/11 tests, five real-API fixture browser scenarios, the actual-model scenario explicitly skipped, and 192 fixture test evaluation rows. Its owned temporary clone was removed.
- `uv run --extra ml python -m scripts.actual_generation_browser`: one separate genuine browser/API/Qwen scenario passed (10.5-second scenario, 11.4-second Playwright run). BM25 over real FTS, accepted 35 answer, checked current v2 source opened. No fake generation or fetch interception.
- `uv run --extra ml pytest -m real_model tests/integration/test_actual_disclosure.py -q -s`: passed 96 serial actual-model API requests over two roles, four retrieval methods, both answer modes, cold/warm cache and active/replaced/deleted sources. Both restricted markers checked. Fixture barriers independently verify races/publication ordering.
- `uv run --extra ml python scripts/model_smoke.py`: actual embedding/reranking/Qwen smoke; 384 dimensions and valid 35-unit JSON; no output-limit hit.
- Six new evaluation runs: `.runtime/eval-fixture-{dev,test}-v4`, `.runtime/eval-local-{dev,test}-extractive-v4`, `.runtime/eval-local-{dev,test}-local-v4`. Commands are in [EVALUATION](../EVALUATION.md); complete raw hashes/provenance in reports/evaluation-v3.json.
- `uv run --no-sync python scripts/curate_reports.py --run-suffix v4 --revision v3`: new immutable summary and three anonymised review sheets. Original evidence hashes remained unchanged.

Focused generation review findings were fixed with regression evidence: parser configuration/Unicode preservation, exclusion of warmup token-limit counts, and staging all curation inputs before writes. Strict malformed/unknown-ID/bool/extra-field checks remain covered. Existing original review decisions and deferred long-title mobile overflow remain in [REVIEW.md](REVIEW.md).

## Pickup and limits

No implementation task remains in the requested repair. Start with [README](../README.md), [RUNBOOK](RUNBOOK.md), [VERIFICATION](VERIFICATION.md), [generation diagnosis](GENERATION-REPAIR.md) and [reports](../reports/README.md). Review-v3 human fields are pending. Qwen semantic/abstention quality, broad multilingual quality, screen-reader use, production identity/public hosting, multiple processes and real customer data are unverified or excluded. No public CI was run. Public repository creation, push, deployment, paid compute, model upload or external send requires specific authorisation.
