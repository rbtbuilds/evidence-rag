# Evidence RAG state

Updated: 2026-10-16. The local abstention implementation and evaluation are recorded, with two remaining refusal errors and an explicit response-coverage limitation. The local Qwen3 14B block correctly returned explicit empty insufficient-evidence refusals in 46/48 expected-abstention test method/question cases, compared with 0/48 in v3. It answered 109/144 answerable cases and unnecessarily refused 35; 0 outputs were invalid. All 120/120 emitted citations resolved to accessible current passages. These are abstention and format/access measurements, not human factual-support or completeness scores. Two remaining errors are the same reader question under BM25 and hybrid: the model treats a quoted hostile instruction as evidence for a calibration marker. No restricted marker is disclosed. Human support/completeness remain unmeasured. No publication, push, deployment, paid compute, model upload or external message occurred.

## Ownership and frozen source

Owned checkout/Git root: /Users/matthewgoralczyk/BentoLabs/portfolio/evidence-rag, branch feat/evidence-rag-v1, no remote. Only this project changed. API 8115/web 5115 stay loopback and strict-port. Model workers atomically acquire the shared /tmp/bentolabs-portfolio-ml.lock, then exit/join before their own lease is released. Other projects' leases were respected; no sibling message was sent.

The original ten-task v1 plan is complete. This follow-up used systematic debugging, failing regressions, local native implementation and one focused existing judgment reviewer. Final canonical implementation source: c4b3fffb049a448c4bddaefcfa23128188b0f8df. Later evidence/document commits do not change that measured source.

All six canonical runs use clean source c4b3fffb049a448c4bddaefcfa23128188b0f8df, heading-window-v2, evidence-json-v4-abstention and the same frozen corpus/questions. They total 864 method/question rows. Model and dependency locks, raw hashes, machine, stage timings, per-role/stratum metrics and paired bootstrap intervals are retained. No forbidden-marker disclosure, embedding truncation or passage dropping occurred.

## Implementation and decisions

Pinned generator: mlx-community/Qwen3-14B-4bit at a4d9b2df59d2c150bef02fcbe0d91046b7ca33a4, Apache-2.0, native MLX on Apple Silicon, four bits/group size 64, thinking disabled. BGE/MiniLM remain pinned CPU float32/four threads. MLX/MLX-LM/MLX Metal 0.32.2 are optional pinned dependencies. Fixture execution remains portable and does not import/load MLX.

The one-pass evidence-json-v4-abstention prompt gives the exact empty-refusal object and distinguishes correction from absence. The decoder retains exact supplied-ID enums, strict JSON, 2,048 input/256 output tokens and two generated citations, with a new 180-character answer bound. Public validate_generation, access/version lookup and final publication checks are unchanged. Native loading rejects any extra/missing consumed weight file; masking copies only finite allowed logits into an otherwise negative-infinity array. Backend and model SHA enter cache provenance.

Separate pre-answer classifiers lost useful corrections and were removed. Qwen2.5 1.5B and a SQuAD2 reader were rejected. Native Qwen3 4B passed BM25/browser checks but failed an expected refusal under dense retrieval. The final 14B development diagnostic refused 12/12 unsupported cases but answered only 19/24 answerable cases, missing the full-coverage target. That cost was accepted explicitly in favour of reliable refusal, then the policy was frozen before test regression. [Full trials and review rulings](ABSTENTION-REPAIR.md).

The generated blocks recorded at most 9,229,360,168 peak accelerator bytes (8.60 GiB) and 2,376,171,520 sampled worker RSS bytes (2.21 GiB). Do not add these as independent allocations on unified memory. Native generation uses a 12 GiB detected-peak threshold and 256 MiB allocator cache guideline; sampled worker RSS remains capped at 6 GiB. MLX allocation limits are guidelines, so transient overshoot can precede detection.

## Results

| Split | Proper expected refusals | Answerable responses | Unnecessary refusals | Invalid output | Citations resolved | Output-limit hits |
| --- | --- | --- | --- | --- | --- | --- |
| Development | 24/24 | 51/72 | 21 | 0 | 55/55 | 0 |
| Test | 46/48 | 109/144 | 35 | 0 | 120/120 | 0 |


Actual test retrieval recall@5 is 1.0 for each method on 36 eligible questions. Dense/hybrid MRR is 1.0, BM25/reranked hybrid 0.9861. MiniLM did not improve ranking. Quote mode correctly refuses 8/12 expected-abstention test cases per actual method. These small repetitive fictional data do not establish enterprise retrieval quality. The reused frozen test is regression evidence after earlier disclosed runs, not a new unseen generalisation study. Policy/model selection used development evidence only; test outputs did not change the policy. The corpus is small, repetitive and fictional. The model still misses two expected refusals and sacrifices answerable response coverage; accepted answers can still be incomplete or unsupported. Exact quotations remain the default. Human source support/completeness, screen-reader use and customer impact remain unmeasured.

The retained v3 source is e3823ce2a47d78b336aa0b6476c663f0b3206d6e. Its model produced valid JSON but explicitly refused 0/48 expected-abstention test cases; the one legacy correct-abstention credit was invalid-output rejection. Its exact lock is archived at config/models.qwen25.lock.json, SHA-256 0576443c6287c8ca3fff8116a6f4a1a9aa97d1b2d04c4fc5c6f98a50f868f469. All 18 original evidence JSON artifacts remain unchanged. [Generation-format history](GENERATION-REPAIR.md) remains historical evidence.

## Exact verification

- `./scripts/check.sh`: Ruff; strict Pyright, zero errors/warnings; 110 Python fixture tests, one actual test deselected, external sockets disabled except loopback/Unix; strict TypeScript including tests/configs; 11 web tests; production build; contracts/corpus checks.
- `./scripts/clean_clone_check.sh`: passed at c4b3fffb049a448c4bddaefcfa23128188b0f8df, frozen fresh installs, 110/11 tests, five fixture browser scenarios with one actual scenario explicitly skipped, and 192 fixture evaluation rows. Its owned temporary clone was removed.
- `uv run --no-sync python -m scripts.actual_generation_browser`: one genuine native browser/API scenario passed in 17.4 seconds (18.3-second Playwright run), including 35/current source, two proper refusals and supported cache retention. No fetch interception or fake generation.
- `uv run --no-sync pytest -m real_model tests/integration/test_actual_disclosure.py -q -s`: 96 serial actual API requests passed in 82.59 seconds. All methods/roles/cache/source states checked; 32 local reader/deleted rows explicitly refused and 16 authorised local rows answered the current marker. Fixture barriers independently cover race/publication ordering.
- `uv run --no-sync --extra ml evidence-rag prepare-models`: re-preparation reused pinned SHAs/hashes and preserved the active lock. `doctor --models` verified local files; all pre-existing dependency versions were retained.
- `uv run --no-sync --extra ml python scripts/model_smoke.py`: actual 384-dimensional embedding, rerank score, valid 35-unit JSON, 23 output tokens, no output-limit hit; resource measurements retained.
- Six canonical commands and raw .runtime/eval-*-v5 paths are in [EVALUATION](../EVALUATION.md). `uv run --no-sync python scripts/curate_reports.py --run-suffix v5 --revision v4` retains the summary and three new unfilled 24-answer review sheets. Original artifact hashes and all 864 clean-source rows were checked.

## Pickup

Start with [README](../README.md), [RUNBOOK](RUNBOOK.md), [VERIFICATION](VERIFICATION.md), [abstention decisions](ABSTENTION-REPAIR.md) and [reports](../reports/README.md). Abstention is not fully solved: test-041 is still answered under BM25 and hybrid, using a quoted hostile instruction rather than a marker fact. No restricted marker was disclosed. Full answerable coverage was not achieved. Human support/completeness and screen-reader testing remain pending; production identity, multiple API processes, public hosting, real customer data and broad generalisation are excluded. Public actions require specific authorisation.
