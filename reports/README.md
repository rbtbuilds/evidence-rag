# Retained evidence

The current bounded pass is [quality-v1.json](quality-v1.json): one clean-source frozen final comparison, with 96 baseline challenge, 96 selected-candidate challenge and 192 exposed original-test rows. Its [answer records](quality-v1-answers.json) retain all public fictional outputs. The summary hashes those records and the raw blocks, and includes per-mode/role/category counts, pins, settings and resource observations. Human metrics stay null.

The pre-registered quality gate failed: regression_refusals, regression_coverage, challenge_no_unverified_answers. Exact quotations remain the default. No final-output tuning, oracle relaxation or third policy iteration occurred.

| Challenge policy | Proper refusals | Answerable responses | Oracle-verified complete | Unverified responses | Invalid | Citations resolve |
| --- | --- | --- | --- | --- | --- | --- |
| Unchanged v4 baseline | 30/32 | 64/64 | 56/64 | 10 | 0 | 66/66 |
| Selected candidate | 32/32 | 60/64 | 57/64 | 3 | 0 | 60/60 |

| Exposed test | Proper refusals | Answerable responses | Invalid | Citations resolve |
| --- | --- | --- | --- | --- |
| Recorded v4 | 46/48 | 109/144 | 0 | 120/120 |
| Selected candidate | 47/48 | 109/144 | 0 | 126/126 |

Interpret the finite oracle conservatively. Bare `date` can be source-supported yet fail a pattern that admits only `The date`; no adjusted aggregate metric replaces the frozen rejection. Citation resolution is not entailment. The exposed original test and reused fictional corpus do not establish generalisation or statistical independence. See [methods and failures](../docs/QUALITY-RESULTS.md).

[quality-development-v1.json](quality-development-v1.json) retains baseline/first-candidate development diagnostics; [quality-development-v2.json](quality-development-v2.json) retains the rejected second policy. Those working trees were dirty diagnostics; final source was clean 9a324b8. Selection used development and disclosed native/access regression evidence before opening challenge failures. No third policy exists.

[actual-access-quality-v1.json](actual-access-quality-v1.json) separately retains 96 actual API requests over methods, roles, answer modes, cache states and active/replaced/deleted sources. It passed 32 proper reader/deleted local refusals, 16 authorized local answers and zero forbidden disclosure; old links failed after mutation. It records the exact test hash/uncommitted-tooling context. Fixture barriers separately establish race ordering.

[quality-v1-preservation.json](quality-v1-preservation.json) protects all 24 pre-pass JSONs. Historical [evaluation-v4.json](evaluation-v4.json) uses clean c4b3fff and retains the recorded 46/48 refusal, 109/144 response, 35 unnecessary-refusal, 0 invalid, 120/120 resolving-citation baseline; its six fixture/actual blocks total 864 rows. V1/v2/v3, smoke/access reports and unfilled review sheets are unchanged. Old absent counters remain null, not invented zeros. Keys/weights/databases/codes/raw runtime logs remain ignored.

[dependency-provenance.json](dependency-provenance.json) inventories installed Python metadata/notice hashes and locked web licence labels, including optional ML dependencies. It is not a comprehensive legal audit or a grant of rights; root MIT does not relicense third-party assets. Model/card/file provenance remains in [models.lock.json](../config/models.lock.json).

All evidence remains local. No human review, hosted CI, customer pilot, push, model upload or deployment is claimed. [Publication audit](../docs/PUBLICATION-AUDIT.md) records content and demo checks.
