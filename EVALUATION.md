# Evidence RAG evaluation

Current results are in [reports/evaluation-v4.json](reports/evaluation-v4.json), separately labelled fixture quotations, actual local quotations and actual local Qwen generation. All six canonical runs use clean source c4b3fffb049a448c4bddaefcfa23128188b0f8df, heading-window-v2, evidence-json-v4-abstention and the same frozen corpus/questions. They total 864 method/question rows. Model and dependency locks, raw hashes, machine, stage timings, per-role/stratum metrics and paired bootstrap intervals are retained. No forbidden-marker disclosure, embedding truncation or passage dropping occurred.

## Frozen inputs and comparisons

The manifest contains 12 logical manuals with active v2 and superseded v1, eight sections each, plus a deleted tombstone. Eight manuals are reader-visible and four are restricted. Original content/provenance are MIT; third-party models retain their own licences.

The fixed questions in fixtures/questions contain 24 development cases (12 supported, 4 unsupported, 4 version-conflict, 4 restricted) and 48 test cases (24/8/8/8). Section families and authored template IDs are disjoint between splits; repeated vocabulary and shared document context make this an easy synthetic benchmark. Hashes in split.json remain unchanged. The reused frozen test is regression evidence after earlier disclosed runs, not a new unseen generalisation study. Policy/model selection used development evidence only; test outputs did not change the policy. The corpus is small, repetitive and fictional. The model still misses two expected refusals and sacrifices answerable response coverage; accepted answers can still be incomplete or unsupported. Exact quotations remain the default. Human source support/completeness, screen-reader use and customer impact remain unmeasured.

Compare real FTS5 BM25, BGE dense cosine, hybrid RRF and hybrid plus MiniLM reranking with K=5 and at most 20 candidates. Fixture vectors/reranking are deterministic doubles. Actual embedding/reranking remain pinned CPU float32, four threads and batch four. Generation is mlx-community/Qwen3-14B-4bit at a4d9b2df59d2c150bef02fcbe0d91046b7ca33a4: four bits, group size 64, native MLX GPU, enable_thinking=False, seed 17 and greedy decoding. No hosted inference or automatic fallback is used.

The final policy gives the exact empty-refusal object and distinguishes a correction from absent information. A fresh LM Format Enforcer 0.11.3 parser masks each request to strict JSON and its authorised citation IDs. Input is at most 2,048 tokens; output at most 256 tokens, 180 answer characters and two generated citations. The public validator remains unchanged with its five-citation ceiling. Low-ranked whole passages are dropped if needed; embedding truncation must be zero for curation. No extra classifier or decision-token stage remains. [Development diagnosis](docs/ABSTENTION-REPAIR.md) records rejected candidates and the missed response-coverage target.

## Arithmetic and denominators

Deduplicate section IDs before scoring. Recall@5 is labelled relevant sections found divided by labelled relevant sections. Empty relevance sets are null/excluded. MRR@5 is reciprocal first relevant rank or zero, using the same nonempty-relevance denominator: 18/24 development and 36/48 test questions per method.

Report roles/strata, per-query pairs and 2,000 bootstrap resamples with seed 17. Test expected-abstention denominator is 12 per method, 48 across four methods; answerable denominator is 36 per method, 144 across methods. Development denominators are 6/18 per method. Repeated method/question cases are not distinct independently sampled questions.

Legacy correct_abstentions includes any abstained response, including invalid-output rejection. New explicit_correct_abstentions requires reason=insufficient_evidence; invalid_generation_count is separate. answered_answerable_count and unnecessary_abstentions expose coverage lost to conservative refusal. Old reports lacking these fields stay null when parsed, not fabricated zeros. A system refusing everything can pass the unsupported denominator while failing its task.

Citation-ID/version/offset validity is mechanical. Human citation support and answer completeness require the separate 24-answer review sheet per generation block. Reviewer/date/disagreements remain unfilled; no model judge substitutes for human review. Zero emitted citations is not a perfect citation-resolution score.

## Actual observations

| Split | Proper expected refusals | Answerable responses | Unnecessary refusals | Invalid output | Citations resolved | Output-limit hits |
| --- | --- | --- | --- | --- | --- | --- |
| Development | 24/24 | 51/72 | 21 | 0 | 55/55 | 0 |
| Test | 46/48 | 109/144 | 35 | 0 | 120/120 | 0 |


The local Qwen3 14B block correctly returned explicit empty insufficient-evidence refusals in 46/48 expected-abstention test method/question cases, compared with 0/48 in v3. It answered 109/144 answerable cases and unnecessarily refused 35; 0 outputs were invalid. All 120/120 emitted citations resolved to accessible current passages. These are abstention and format/access measurements, not human factual-support or completeness scores. Two remaining errors are the same reader question under BM25 and hybrid: the model treats a quoted hostile instruction as evidence for a calibration marker. No restricted marker is disclosed.

| Actual retrieval | Recall@5 (36) | MRR@5 (36) | Warm quotation p50/p95 ms | Warm Qwen p50/p95 ms |
| --- | --- | --- | --- | --- |
| BM25 | 1.000 | 0.9861 | 2.51 / 3.39 | 3977.55 / 6637.74 |
| Dense BGE | 1.000 | 1.0000 | 8.35 / 9.15 | 3988.08 / 6003.28 |
| Hybrid RRF | 1.000 | 1.0000 | 8.76 / 10.18 | 4011.82 / 4655.75 |
| Hybrid + MiniLM | 1.000 | 0.9861 | 85.92 / 97.09 | 4036.53 / 4653.93 |


Timing uses warmed workers with cold answer caches; separately recorded index/load/decode warmup is excluded. Each full actual block owns one lease. Light development ran concurrently, so these are local development measurements, not isolated hardware or end-user cold-start latency. Uncached interactive requests may reload weights. Model, policy and backend changed together from CPU Qwen2.5 0.5B; there is no single-component speedup claim.

The generated blocks recorded at most 9,229,360,168 peak accelerator bytes (8.60 GiB) and 2,376,171,520 sampled worker RSS bytes (2.21 GiB). Do not add these as independent allocations on unified memory. Native generation uses a 12 GiB detected-peak threshold and 256 MiB allocator cache guideline; sampled worker RSS remains capped at 6 GiB. MLX allocation limits are guidelines, so transient overshoot can precede detection.

The v3 baseline explicitly refused 0/48 expected-abstention test cases; its sole legacy correct-abstention credit was an invalid output. The original v2 policy rejected all 288 generation outputs. Those reports remain unchanged, as does the exact archived [Qwen2.5 lock](config/models.qwen25.lock.json). The new model improves measured refusal while losing answerable coverage; it does not establish factual accuracy or broad generalisation.

## Reproduction

Use Python 3.12 and Node 24 LTS. Ordinary fixture setup needs no model weights. Actual generation requires Apple Silicon/Metal and optional pinned ML dependencies.

```sh
uv run evidence-rag evaluate --profile fixture --split dev --generation extractive --output .runtime/fixture-dev-new
uv run evidence-rag evaluate --profile fixture --split test --generation extractive --output .runtime/fixture-test-new
uv sync --frozen --extra ml
uv run --extra ml evidence-rag prepare-models
uv run --extra ml evidence-rag doctor --models
uv run --extra ml evidence-rag evaluate --profile local --split dev --generation extractive --output .runtime/local-dev-quotes-new
uv run --extra ml evidence-rag evaluate --profile local --split dev --generation local --output .runtime/local-dev-generation-new
uv run --extra ml evidence-rag evaluate --profile local --split test --generation extractive --output .runtime/local-test-quotes-new
uv run --extra ml evidence-rag evaluate --profile local --split test --generation local --output .runtime/local-test-generation-new
```

Use new output directories inside this checkout. Each run creates an isolated database and writes report.json, human-review.json and an ignored method key. Raw retained names are .runtime/eval-fixture-{dev,test}-v5, .runtime/eval-local-{dev,test}-extractive-v5 and .runtime/eval-local-{dev,test}-local-v5. Curation command: `uv run --no-sync python scripts/curate_reports.py --run-suffix v5 --revision v4`. Do not tune on test results. Busy leases defer work; never spin, steal a lease or silently use fixtures.

## Access and lifecycle evidence

Fixture tests cover forged role headers, guessed sources/jobs, private statistics/vectors, cache isolation, source instructions, failed publication, expiry and deterministic barriers for both response/deletion orders. The actual browser uses genuine sessions and HTTP, with no intercepted fetch. The dedicated native flow requires the supported 35-unit answer/current citation, lunar-alloy and reader-private-marker empty refusals, then retention of the supported cached answer.

The actual 96-request serial API matrix spans both roles, four retrieval methods, both generation modes, cold/warm caches and active/replaced/deleted sources. Local reader/deleted requests must explicitly refuse with empty answers/no citations; authorised active/replaced requests must give the current marker. All emitted citations must open while current and accessible; old links fail after replacement/deletion. Serial model checks do not replace the fixture race barriers. See [VERIFICATION.md](docs/VERIFICATION.md).
