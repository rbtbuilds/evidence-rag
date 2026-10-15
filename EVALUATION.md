# Evidence RAG evaluation

Current repair results are in [reports/evaluation-v3.json](reports/evaluation-v3.json), separately labelled fixture/extractive, actual local/extractive and actual local/Qwen generation. All six runs used clean source commit e3823ce2a47d78b336aa0b6476c663f0b3206d6e, heading-window-v2 and the frozen evidence-json-v3-bounded policy. Original [evaluation-v2.json](reports/evaluation-v2.json) and v1 evidence remain unchanged. The benchmark is an owned fictional scenario; it makes no customer-impact claim.

## Frozen inputs and comparisons

The manifest contains 12 logical manuals with active v2 and superseded v1, eight sections each, plus a deleted tombstone. Eight manuals are reader-visible and four are restricted. All current documents remain indexed. Original content and provenance are MIT; third-party models retain their own licences.

Questions are fixed in `fixtures/questions`: 24 development (12 supported, 4 unsupported, 4 version-conflict, 4 restricted) and 48 test (24/8/8/8). Source section families and authored template IDs are disjoint between splits; conflicting and restricted questions refer to split-specific section families. Repeated scenario vocabulary and shared document context make this an easy synthetic benchmark, not a generalisation study. Hashes are frozen in `split.json`; changes require a new evaluation revision.

Compare BM25, BGE dense cosine, hybrid RRF, and hybrid plus MiniLM reranking on the same snapshot with K=5, at most 20 candidates and the same fixed generation policy. Fixture dense/reranking use deterministic doubles. Actual generation is Qwen2.5-0.5B-Instruct: CPU float32, four threads, seed 17, no sampling, 2,048 input and 256 output tokens. Greedy decoding is masked by pinned lm-format-enforcer 0.11.3 against the strict object schema and only the current request's authorised citation IDs. Generation allows at most two citations within 256 tokens; the unchanged application validator still allows five. Repetition penalty is explicitly 1.0. Whole low-ranked passages are dropped if needed. Embedding truncation must be zero for a curated actual run. No parameter thresholds were tuned; held-out results did not select a method.

## Arithmetic and denominators

Deduplicate section IDs before scoring. Recall@5 is relevant sections found divided by labelled relevant sections; empty relevance sets are null and excluded. MRR@5 is reciprocal first relevant section rank, otherwise zero; retrieval aggregates use the same nonempty-relevance denominator. Test retrieval denominator: 36 of 48 questions per method; 12 are excluded. Development denominator: 18 of 24.

Report all role/stratum counts, per-query paired differences and 2,000 bootstrap resamples with seed 17. Report abstention decisions separately: expected-abstention test denominator is 12 per method, whereas overall abstention-decision accuracy includes all 48. A system abstaining on everything can score 100% on expected abstentions and still fail its useful task.

Citation-ID/version/offset validity is mechanical. Citation support precision and answer completeness require the separate 24-answer human review sheet per generation block. Reviewer/date and disagreements must be recorded. They remain unmeasured in v1. An emitted valid citation does not establish entailment; zero emitted citations is not a perfect citation-resolution score.

## Actual test observations

| Actual retrieval | Recall@5 (36) | MRR@5 (36) | Warm quotation p50/p95 ms | Warm Qwen p50/p95 ms |
| --- | --- | --- | --- | --- |
| BM25 | 1.000 | 0.9861 | 2.15 / 2.81 | 4369.25 / 9031.13 |
| Dense BGE | 1.000 | 1.0000 | 8.37 / 13.96 | 4427.46 / 8039.85 |
| Hybrid RRF | 1.000 | 1.0000 | 9.25 / 12.57 | 4821.80 / 8914.75 |
| Hybrid + MiniLM | 1.000 | 0.9861 | 90.23 / 158.75 | 4832.51 / 8954.77 |

| Split | Accepted answers | Insufficient evidence | Invalid output | Citations resolved | Output-limit hits | Correct expected abstentions |
| --- | --- | --- | --- | --- | --- | --- |
| Development | 83/96 | 11 | 2 | 160/160 | 2 | 2/24 |
| Test | 183/192 | 2 | 7 | 347/347 | 9 | 1/48 |

The repaired local Qwen block accepted 183/192 test answers, returned 2 insufficient-evidence abstentions and rejected 7 invalid outputs. All 347/347 emitted citations resolved to accessible current passages; 9 outputs hit the 256-token budget. Two of those still completed valid JSON and were accepted; the other seven were rejected. Expected-abstention decisions were correct in 1/48 method/question cases. The sole correct test expected-abstention decision came from invalid-output rejection; no explicit insufficient-evidence response correctly handled an expected-abstention case. This measures format/citation validity and abstention, not factual support or completeness.

These runs held one machine lease per complete benchmark on the M5 Pro, excluded separately recorded load/index/decode warmup, and ran during light local development. They are not end-user cold-start latency. No embedding truncation or passage dropping occurred. The repaired policy was frozen before held-out evaluation. No forbidden markers appeared in any of the six evaluation blocks.

The baseline policy failed all 288 development/test generation outputs. Format and exact-ID enforcement plus a bounded citation list make generation operational, but cannot establish support or a sound abstention decision. For example, development BM25 answered "Which lunar alloy is used?" with "Aster bench-top circulation trainer" despite valid citations. The two development output-limit failures remained rejected; they were not repaired or excused. They account for both correct expected-abstention decisions in development; explicit insufficient-evidence responses contributed none. See [diagnosis](docs/GENERATION-REPAIR.md).

Quotation mode correctly abstained on 8/12 expected-abstention cases per actual test method. Adding MiniLM reduced hybrid test MRR from 1.0 to 0.9861. Human support/completeness remain unmeasured; valid IDs are not a quality score.

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

The explicit actual-model matrix test adds serial API requests over both roles, all four methods, both generation modes, two cache states and three source states. It uses actual snapshot-backed indexing/retrieval/generation. Neither Qwen abstention nor an accepted structured answer establishes prompt obedience or factual support. Race control is tested independently through deterministic barriers. See [VERIFICATION.md](docs/VERIFICATION.md) for exact run outcomes and limits.
