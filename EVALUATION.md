# Evidence RAG evaluation

The pre-registered quality gate failed: regression_refusals, regression_coverage, challenge_no_unverified_answers. Exact quotations remain the default. No final-output tuning, oracle relaxation or third policy iteration occurred.

| Challenge policy | Proper refusals | Answerable responses | Oracle-verified complete | Unverified responses | Invalid | Citations resolve |
| --- | --- | --- | --- | --- | --- | --- |
| Unchanged v4 baseline | 30/32 | 64/64 | 56/64 | 10 | 0 | 66/66 |
| Selected candidate | 32/32 | 60/64 | 57/64 | 3 | 0 | 60/60 |

| Exposed test | Proper refusals | Answerable responses | Invalid | Citations resolve |
| --- | --- | --- | --- | --- |
| Recorded v4 | 46/48 | 109/144 | 0 | 120/120 |
| Selected candidate | 47/48 | 109/144 | 0 | 126/126 |

These are actual local-model results from one frozen run at `9a324b82e446f9ac3ddc6ff834846cd0e30c5d80`. All 24 historical reports remain unchanged. Exact outputs and per-role/category/method breakdowns are in [quality-v1.json](reports/quality-v1.json) and [answer records](reports/quality-v1-answers.json). See [full methods, criteria, false-negative examples and limits](docs/QUALITY-RESULTS.md).

The exposed-test targets were 48/48 proper refusals and at least 116/144 answerable responses; observed 47/48 and 109/144 miss both. Hybrid still answers test-041 with `restricted calibration review marker`, citing the public training quotation instead of refusing a value question. No private marker is disclosed. The general grounding defect is reduced, not eliminated, and answerable response coverage did not improve.

## Distinct evidence classes

- Fixture: real FTS5, deterministic embedding/reranking doubles and extractive quotations. The account-free quickstart and ordinary CI use this mode.
- Actual model: pinned BGE/MiniLM plus optional native Qwen3 14B through the real service/repository. Quality-v1 totals 384 method/question rows: 96+96 paired challenge and 192 exposed regression. The actual access matrix is 96 separate requests; browser generation is separate again.
- Human review: source-support/completeness, usefulness and screen-reader metrics remain unmeasured. Frozen AI-authored finite oracles are not human review or general entailment.

The challenge has 24 questions (16 answerable, 8 expected refusal), each repeated across four methods. The original exposed test has 48 questions (36 answerable, 12 expected refusal), also across four methods. Repeated method/question rows are paired measurements, not independent samples. The separate AI author reused the fictional corpus and related fact families, with limited required-guidance aggregate exposure. Do not call this statistically independent or a test on new documents.

A proper refusal is empty answer/no citations/reason insufficient_evidence. Invalid-generation rejection earns no proper-refusal credit. Response coverage is non-refusal on answerable rows. Oracle verification requires a complete finite full-answer match plus required exact cited support and current/access-valid citations; it can reject correct wording, including bare `date` where `The date` was enumerated. No post-hoc rescoring is reported. All forbidden-value checks now case-fold answer payloads; older frozen reports are preserved rather than recalculated.

The unchanged original corpus has 12 two-version manuals, eight reader-visible and four restricted, plus a deleted tombstone. Source and split hashes remain fixed. Retrieval compares BM25, BGE cosine, RRF and RRF+MiniLM with five final passages and 20 candidates. Original recall/MRR deduplicate section IDs, exclude empty relevance sets, and use 36 eligible test questions per method. Historical v4 retrieval recall@5 was 1.0 for all methods; its timing/bootstrap evidence remains in [evaluation-v4.json](reports/evaluation-v4.json), not a new quality-pass latency claim.

## Reproduce locally

The ordinary portable path requires Python 3.12, uv and Node 24:

```sh
export UV_CACHE_DIR="$PWD/.runtime/uv-cache"
uv sync --frozen
npm --prefix web ci
./scripts/check.sh
uv run evidence-rag evaluate --profile fixture --split test --generation extractive --output .runtime/fixture-replication
```

Use a fresh contained output path. Optional actual models require pinned snapshots, Apple Silicon/Metal for Qwen, and the shared lease; see [RUNBOOK.md](docs/RUNBOOK.md). For a research replication, use the recorded source/configuration and a separately named revision rather than deleting the one-final marker or overwriting retained reports. The original final command and curation boundary are recorded in QUALITY-RESULTS.md. No further tuning is part of quality-v1.

The original v2 all-invalid, v3 format repair, v4 abstention repair and unfilled historical review sheets remain evidence with their original provenance. [Generation repair](docs/GENERATION-REPAIR.md), [abstention repair](docs/ABSTENTION-REPAIR.md) and [bounded development](docs/QUALITY-DEVELOPMENT.md) explain rejected choices. Citations, authorization, version/deletion/cache/publication checks were not loosened. Default quotations are retained; production authentication, real customer data, broad factuality and industrial use are outside the measured scope.
