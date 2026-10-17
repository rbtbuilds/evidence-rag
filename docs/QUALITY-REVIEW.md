# Quality pass code review

A fresh clean-context AI reviewer examined d01f3d7..354d3f8 before the single final evaluation. This was AI-assisted code review, not human factual review or an independent statistical study. The reviewer did not open challenge questions/oracles or load models.

No critical findings or deferred minor findings were reported. Two important findings were accepted by effect and repaired in one author pass:

1. The outer benchmark released its machine lease even when a borrowed worker's post-kill join timed out. An in-memory Popen failure reproduces the actual runner/final-driver path. Before repair the owner vanished while the borrower remained active. The shared coordinator now refuses outer release until borrowers close; completion is written only after cleanup succeeds. Normal serial/double close, changed ownership and competing benchmarks remain covered.
2. The legacy evaluator checked forbidden values case-sensitively, allowing changed capitalization to evade the final regression disclosure count. A real fixture retrieval/evaluation/curation path emits a synthetic forbidden value in four methods. Before repair none were counted. Both evaluator families now case-fold values and answer payloads. Historical reports remain immutable.

RED: three failures in the focused seven-test run (one missing coordinator method, premature release, disclosure undercount). GREEN: seven passed. Full strict suite: 125 Python tests passed, two real-model tests deselected; Ruff, strict Pyright, strict TypeScript, 11 web tests, build, contracts and corpus passed. Logs are under .runtime/quality-review-{red,green}.log and quality-review-fixed-check.log. No policy/model/decoder changes were made in this review pass.

## Review boundaries and author rulings

- Challenge adequacy was deliberately withheld from code review. The frozen AI-authored source-grounded oracle is used as specified; its finite wording families can reject correct paraphrases. Cost if wrong: automatic coverage can undercount useful answers and cannot establish broad factuality.
- Final evaluation, publication audit and clean checkout occur after code review. Their evidence receives an author audit rather than a second review cycle. Cost if wrong: a reporting defect in final documentation could remain without another fresh reader.
- Broad factuality, human usefulness and complete video credential clearance were not established by the reviewer. Human metrics stay unmeasured. Login is excluded from capture; retained images and sampled frames receive AI-assisted inspection, not a claim of human/full-frame clearance. Cost if wrong: unmeasured semantic failures or an unsampled visual issue can remain.
- The reviewer could not execute actual-model/browser flows. Existing actual API/browser evidence is retained with its exact source/context; the clean-source final benchmark is separate. Cost if wrong: those shown flows do not prove all interactive model paths.
- Clean checkout is deferred until the complete evidence/documentation commit so it checks the publication artifact set once. Cost if wrong: the fresh reviewer does not inspect that later checkout evidence.
- The exposed original failure is a legitimate regression target, not an unseen holdout. It is used for diagnosis and candidate selection with disclosure. Cost if wrong: improvement can reflect regression familiarity; no broad generalisation claim follows.

The selected native semantic regression remains failed on current-value correction and counted-noun completeness (one test, two failing pairs, 21.31 seconds). The user-limited two policy iterations are exhausted. Exact quotations remain the default; failure is retained, not waived or converted to a pass.
