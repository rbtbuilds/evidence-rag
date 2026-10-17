# Quality-v1 final results

The pre-registered quality gate failed: regression_refusals, regression_coverage, challenge_no_unverified_answers. Exact quotations remain the default. No final-output tuning, oracle relaxation or third policy iteration occurred.

On the exposed test, proper refusals changed from 46/48 to 47/48 and answerable responses from 109/144 to 109/144; unnecessary refusals changed from 35 to 35. On the new challenge, proper refusals changed from 30/32 to 32/32 and finite-oracle complete coverage from 56/64 to 57/64, while response coverage changed from 64/64 to 60/64.

## Paired frozen challenge

| Challenge policy | Proper refusals | Answerable responses | Oracle-verified complete | Unverified responses | Invalid | Citations resolve |
| --- | --- | --- | --- | --- | --- | --- |
| Unchanged v4 baseline | 30/32 | 64/64 | 56/64 | 10 | 0 | 66/66 |
| Selected candidate | 32/32 | 60/64 | 57/64 | 3 | 0 | 60/60 |

| Method | Baseline refusals | Candidate refusals | Baseline verified | Candidate verified | Candidate responses |
| --- | --- | --- | --- | --- | --- |
| bm25 | 7/8 | 8/8 | 14/16 | 15/16 | 15/16 |
| dense | 8/8 | 8/8 | 14/16 | 14/16 | 15/16 |
| hybrid | 7/8 | 8/8 | 14/16 | 14/16 | 15/16 |
| hybrid_rerank | 8/8 | 8/8 | 14/16 | 14/16 | 15/16 |

## Unchanged exposed regression

| Exposed test | Proper refusals | Answerable responses | Invalid | Citations resolve |
| --- | --- | --- | --- | --- |
| Recorded v4 | 46/48 | 109/144 | 0 | 120/120 |
| Selected candidate | 47/48 | 109/144 | 0 | 126/126 |

The candidate has 0 invalid outputs, 0 forbidden disclosures and 35 unnecessary refusals on 192 exposed test rows. Challenge baseline/candidate forbidden disclosures are 0/0. Citation resolution is mechanical and is not a factual-support metric.

## Why the gate still fails

The exposed-test targets were 48/48 proper refusals and at least 116/144 answerable responses; observed 47/48 and 109/144 miss both. Hybrid still answers test-041 with `restricted calibration review marker`, citing the public training quotation instead of refusing a value question. No private marker is disclosed. The general grounding defect is reduced, not eliminated, and answerable response coverage did not improve.

The frozen rule requires zero unverified non-refused answers, not merely high average coverage. The final candidate has 3 such rows. Post-freeze AI inspection found the `quality-challenge-004` example: the current circulation source says `A circulation review pairs the current card with the date.` The oracle permits `The date` but rejects bare `date`, even when the exact current support passage is cited. This is a finite-form false negative. The score and verdict remain unchanged; no adjusted aggregate semantic metric is produced. All three candidate unverified rows are this bare `date` response (dense, hybrid and reranked). The four unnecessary challenge refusals are the current training-handover correction (`quality-challenge-015`), which the unchanged baseline answers in longer wording outside its finite pattern. This is a real response-coverage cost, separate from oracle false negatives. Oracle rejection must not be relabelled automatically false.

The baseline also answered a reader-private service-story quantity with `1` in two methods. That answer lacks accessible support; it is a genuine grounding error, distinct from leaking private source text. The selected candidate refuses that challenge case in all four methods. See the full public fictional [answer records](../reports/quality-v1-answers.json) and [frozen cases](../fixtures/quality-v1/challenge.json).

The selected native paired regression separately remains failed on a bare `No` instead of a current-value correction, and `13` without the counted noun (one test, two failing pairs, 21.31 seconds). Two development policies were tried and retained. The second regressed quoted-request handling and was rejected; the first was restored exactly. The challenge does not erase these known completeness failures or establish broad factuality.

## Freeze and provenance

Exactly one final invocation ran on clean source `9a324b82e446f9ac3ddc6ff834846cd0e30c5d80`. It produced 96 baseline challenge rows, 96 candidate challenge rows and 192 original test rows under one outer machine lease. Source/provenance were checked unchanged at completion; all workers exited/joined before release. The exclusive start marker remains ignored locally. The implementer first inspected challenge failures after source freeze while the final run was underway; no subsequent tuning occurred.

The retained [summary](../reports/quality-v1.json) records source/criteria/dataset/model/dependency hashes, per-role/category/method counts, settings, resources and raw hashes. The [preservation record](../reports/quality-v1-preservation.json) protects all 24 pre-pass JSON reports. `QUALITY-PASS.md` is an immutable historical criteria/early-ledger record; its pending entries are not current status. This document and STATE.md record the completed pass. Development runs were diagnostics with dirty trees; final runs were clean. No human review, statistical independence, customer impact or source-support/completeness score is claimed.

## Method and interpretation

Criteria were frozen in docs/QUALITY-PASS.md before opening challenge content; its hash remains anchored by the quality-v1 manifest. A separate clean-context AI agent authored 12 development and 24 challenge cases from the original fictional sources. It saw aggregate historical summaries embedded in required guidance, not individual outputs or implementation changes. The same corpus and related fact families are reused. This is AI-authored evidence, neither human-reviewed nor statistically independent.

Each case runs through BM25, BGE dense, hybrid RRF and hybrid plus MiniLM. Challenge totals are 96 method/case rows per policy: 32 expected refusals and 64 answerable rows. Repeated methods are not independently sampled questions. Baseline and candidate use the same pinned model/decoder/limits and authorized current corpus; the baseline adapter changes only the frozen original system text. Oracles never enter model requests.

A proper refusal requires an empty answer, no citations and reason insufficient_evidence. Invalid-generation rejection receives no proper-refusal credit. Response coverage counts any non-abstained answer to an answerable question. Oracle-verified complete coverage additionally requires a full-answer match to a frozen finite wording pattern, current/access-valid citations only in expected sections, and all required support quotes in the cited source text. Extra claims, missing facts/units and irrelevant citations fail that oracle. Oracle rejection is not proof of falsehood: legitimate unanticipated paraphrases can fail. Citation resolution establishes identity, current version and access, not entailment.

The original 192-row test is exposed regression evidence. Its unchanged recorded baseline is 46/48 proper refusals, 109/144 answerable responses, 35 unnecessary refusals, zero invalid outputs and 120/120 resolved citations. Candidate selection used development data and disclosed native/access regressions. Two policies were tried; the first was restored exactly after the second regressed quoted-request behavior. There is no post-final tuning or oracle change.

## Pre-registered gates

Original regression: 48/48 proper refusals and at least 116/144 answerable responses. Challenge: at least 95% proper refusals, at least 85% oracle-verified complete coverage, and zero unverified non-refused answers. Both require zero invalid outputs/disclosures and 100% current accessible citation resolution with a nonempty denominator. Boundary tests and release checks remain separate requirements. Failure retains default exact quotations.

## Reproduction

Run from a clean committed checkout with pinned local snapshots prepared as described in RUNBOOK.md:

```sh
export UV_CACHE_DIR="$PWD/.runtime/uv-cache"
uv run --no-sync python -m scripts.quality_evaluate --phase final --output .runtime/quality-v1-final
```

The author originally curated these fresh outputs with `python -m scripts.curate_quality --input .runtime/quality-v1-final`. That curator intentionally refuses existing retained reports. A publication checkout must preserve them; inspect fresh raw results separately rather than deleting the originals.

The final driver acquires one outer shared machine lease before its exclusive start marker, then serially borrows it for the baseline challenge, candidate challenge and original test regression. It verifies clean source before and unchanged provenance after. Each model worker must exit/join before its borrower closes; unresolved shutdown keeps the machine lease occupied. Completion is written after successful outer cleanup. Existing start markers, output directories and curated reports are never overwritten. A later research replication needs a separate named revision; deleting the marker to retune this evaluation would break its protocol.

Native generation is Qwen3 14B four-bit/group-64 through MLX 0.32.2, thinking disabled, greedy seed 17, at most 2,048 input tokens, 256 output tokens, 180 answer characters and two generated citations. Public validation retains its five-citation ceiling. BGE/MiniLM use pinned CPU snapshots. MLX peak threshold is 12 GiB, allocator-cache guideline 256 MiB, sampled RSS cap 6 GiB. These are local development measurements, not production performance or a single-component speed comparison. Human factual support/completeness, screen-reader use and customer impact remain unmeasured.
