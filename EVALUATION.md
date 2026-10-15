# Evidence RAG evaluation

Measured v1 results are in [reports/evaluation-v1.json](reports/evaluation-v1.json), separately labelled fixture/extractive, actual local/extractive and actual local/Qwen generation. The benchmark is an owned fictional scenario; it makes no customer-impact claim.

## Frozen inputs and comparisons

The manifest contains 12 logical manuals with active v2 and superseded v1, eight sections each, plus a deleted tombstone. Eight manuals are reader-visible and four are restricted. All current documents remain indexed. Original content and provenance are MIT; third-party models retain their own licences.

Questions are fixed in `fixtures/questions`: 24 development (12 supported, 4 unsupported, 4 version-conflict, 4 restricted) and 48 test (24/8/8/8). Source section families and authored template IDs are disjoint between splits; conflicting and restricted questions refer to split-specific section families. Repeated scenario vocabulary and shared document context make this an easy synthetic benchmark, not a generalisation study. Hashes are frozen in `split.json`; changes require a new evaluation revision.

Compare BM25, BGE dense cosine, hybrid RRF, and hybrid plus MiniLM reranking on the same snapshot with K=5, at most 20 candidates and the same fixed generation policy. Fixture dense/reranking use deterministic doubles. Actual generation is Qwen2.5-0.5B-Instruct: CPU float32, four threads, seed 17, no sampling, 2,048 input and 256 output tokens. Whole low-ranked passages are dropped if needed. Embedding truncation must be zero for a curated actual run. No parameter thresholds were tuned; held-out results did not select a method.

## Arithmetic and denominators

Deduplicate section IDs before scoring. Recall@5 is relevant sections found divided by labelled relevant sections; empty relevance sets are null and excluded. MRR@5 is reciprocal first relevant section rank, otherwise zero; retrieval aggregates use the same nonempty-relevance denominator. Test retrieval denominator: 36 of 48 questions per method; 12 are excluded. Development denominator: 18 of 24.

Report all role/stratum counts, per-query paired differences and 2,000 bootstrap resamples with seed 17. Report abstention decisions separately: expected-abstention test denominator is 12 per method, whereas overall abstention-decision accuracy includes all 48. A system abstaining on everything can score 100% on expected abstentions and still fail its useful task.

Citation-ID/version/offset validity is mechanical. Citation support precision and answer completeness require the separate 24-answer human review sheet per generation block. Reviewer/date and disagreements must be recorded. They remain unmeasured in v1. An emitted valid citation does not establish entailment; zero emitted citations is not a perfect citation-resolution score.

## Actual test observations

| Actual retrieval | Recall@5 (36) | MRR@5 (36) | Warm quotation p50/p95 ms |
| --- | --- | --- | --- |
| BM25 | 1.000 | 0.9861 | 2.28 / 3.01 |
| Dense BGE | 1.000 | 1.0000 | 8.36 / 9.65 |
| Hybrid RRF | 1.000 | 0.9861 | 9.24 / 11.96 |
| Hybrid + MiniLM | 1.000 | 0.9861 | 89.81 / 99.90 |

These measurements exclude separately recorded index/load warmup, use one leased worker, and were collected during light local development on the M5 Pro. They are not end-user cold-start latency. Peak sampled worker RSS was about 0.59 GiB for the actual quotation test block and 2.65 GiB for Qwen generation; all recorded embedding truncation and dropped-passage counts were zero.

Qwen output was rejected as `invalid_generation` for all 192 test outputs and all 96 development outputs. No generated claim was accepted. A smoke output used the wrong citation key and omitted the insufficient-evidence flag. The contract was kept strict and quotation mode remains the default. This is a reported model/prompt/configuration failure, not an assertion that the model can never follow JSON instructions.

Quotation mode found supported facts but also selected unrelated matching sentences. On each actual test method it correctly abstained on 8/12 expected-abstention cases. Citation support/completeness remain unmeasured. The small corpus does not show that adding a reranker improves the baseline.

## Reproduction

From the checkout after frozen dependency setup:

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

Output directories must be new and inside this checkout. Every run creates its own database, captures fixed corpus/question/model revisions, holds one lease across all four actual methods, and writes `report.json`, `human-review.json` and an ignored method key. Do not tune on test results. Check the shared lease once; if busy, finish light work and try only after its owner has finished.

## Access and lifecycle evidence

Quality averages do not replace boundary tests. Fixture regressions cover both roles, all methods, cold/warm caches, active/replaced/deleted sources, forged identity headers, guessed citations/jobs, source instructions, failed publication, expiry and both orders of response/deletion races. The real browser flow uses actual HTTP/API sessions and verifies source access after identity switching, replacement, deletion and escaped source rendering.

The explicit actual-model matrix test adds serial API requests over both roles, all four methods, both generation modes, two cache states and three source states. It uses actual snapshot-backed indexing/retrieval/generation; Qwen abstention is not evidence of prompt obedience. Race control is tested independently through deterministic barriers. See [VERIFICATION.md](docs/VERIFICATION.md) for exact run outcomes and limits.
