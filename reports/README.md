# Recorded evaluation evidence

[evaluation-v4.json](evaluation-v4.json) retains six canonical runs: development/test for fixture quotations, actual local quotations and native Qwen generation. All six canonical runs use clean source c4b3fffb049a448c4bddaefcfa23128188b0f8df, heading-window-v2, evidence-json-v4-abstention and the same frozen corpus/questions. They total 864 method/question rows. Model and dependency locks, raw hashes, machine, stage timings, per-role/stratum metrics and paired bootstrap intervals are retained. No forbidden-marker disclosure, embedding truncation or passage dropping occurred. The source commit is c4b3fffb049a448c4bddaefcfa23128188b0f8df. File hashes/revisions are in [models.lock.json](../config/models.lock.json); the exact original model lock remains archived separately.

| Split | Proper expected refusals | Answerable responses | Unnecessary refusals | Invalid output | Citations resolved | Output-limit hits |
| --- | --- | --- | --- | --- | --- | --- |
| Development | 24/24 | 51/72 | 21 | 0 | 55/55 | 0 |
| Test | 46/48 | 109/144 | 35 | 0 | 120/120 | 0 |


The local Qwen3 14B block correctly returned explicit empty insufficient-evidence refusals in 46/48 expected-abstention test method/question cases, compared with 0/48 in v3. It answered 109/144 answerable cases and unnecessarily refused 35; 0 outputs were invalid. All 120/120 emitted citations resolved to accessible current passages. These are abstention and format/access measurements, not human factual-support or completeness scores. Two remaining errors are the same reader question under BM25 and hybrid: the model treats a quoted hostile instruction as evidence for a calibration marker. No restricted marker is disclosed.

Legacy correct_abstentions can include invalid generation; explicit_correct_abstentions excludes it. answered_answerable_count/unnecessary_abstentions expose the conservative policy's coverage loss. These new counters are null for legacy reports that did not record them.

The reused frozen test is regression evidence after earlier disclosed runs, not a new unseen generalisation study. Policy/model selection used development evidence only; test outputs did not change the policy. The corpus is small, repetitive and fictional. The model still misses two expected refusals and sacrifices answerable response coverage; accepted answers can still be incomplete or unsupported. Exact quotations remain the default. Human source support/completeness, screen-reader use and customer impact remain unmeasured.

Actual generation uses pinned Qwen3 14B, four-bit MLX on Apple Silicon with thinking disabled. CPU BGE/MiniLM remain unchanged. Timing uses warmed workers and cold answer caches; index/load/decode warmup is separate. Light development ran concurrently. Model, policy and backend changed together from the CPU baseline, so speed differences have no single-component attribution. Interactive uncached calls can reload weights.

The generated blocks recorded at most 9,229,360,168 peak accelerator bytes (8.60 GiB) and 2,376,171,520 sampled worker RSS bytes (2.21 GiB). Do not add these as independent allocations on unified memory. Native generation uses a 12 GiB detected-peak threshold and 256 MiB allocator cache guideline; sampled worker RSS remains capped at 6 GiB. MLX allocation limits are guidelines, so transient overshoot can precede detection.

The three review-v4-*-test-*.json files are new anonymised 24-answer review sheets, six per method across the frozen strata. Keys remain ignored. Reviewer/date/support/completeness are null. No human review or substitute judge is claimed.

[actual-access-matrix-v4.json](actual-access-matrix-v4.json) retains 96 serial actual API requests over roles, all methods, both answer modes, cache states and active/replaced/deleted sources. Local reader/deleted rows must explicitly refuse; authorised local active/replaced rows must answer the current marker. Emitted citations open while accessible/current; fixture barriers separately establish race ordering. [local-smoke-v4.json](local-smoke-v4.json) retains embedding/reranking/valid generation and resource measurements. These acceptance checks ran before source commit and were frozen unchanged; canonical evaluation and clean-clone checks used the clean committed source.

Original v1/v2/v3 reports, review sheets, smoke and access artifacts are unchanged. The v2 baseline rejected every generation output; v3 repaired format and IDs but explicitly refused 0/48 expected-abstention test cases. Its sole legacy credit was an invalid output. [Generation-format repair](../docs/GENERATION-REPAIR.md) remains historical; [abstention repair](../docs/ABSTENTION-REPAIR.md) records new trials and review decisions. The archived original lock SHA-256 is 0576443c6287c8ca3fff8116a6f4a1a9aa97d1b2d04c4fc5c6f98a50f868f469.

Raw paths and SHA-256 hashes are retained in the summary; bulk outputs remain ignored under .runtime. Reproduce with [EVALUATION.md](../EVALUATION.md). Weights, databases, credentials and private source text are excluded. All evidence remains local.
