# Answer quality and local publication readiness

Execute natively with superpowers:executing-plans. Matthew requested autonomous
routine decisions. Scope is Evidence RAG, except the explicitly authorized
helper-managed parent recovery backup already verified in QUALITY-PASS.md.

**Design:** retain exact quotations by default. Improve the optional local
one-pass answer policy using general distinctions between assertions, requests,
fictional facts and correctable premises. Preserve the public validator and all
authorization/version/deletion/cache/publication gates. No model swap unless
development evidence requires it. Frozen automatic oracles are narrow and
AI-authored; human support/completeness remain null.

**Review Focus:** imperative quotations mistaken for values; legitimate quoted
facts/questions; fabricated extra claims; incomplete multi-fact responses;
oracle/source drift; challenge leakage into development; baseline prompt parity;
cache revision; demo credential leakage; resource lease and final-run bounds.

### Task 1: Freeze criteria, provenance and evaluation inputs

Files: docs/QUALITY-PASS.md, config/quality-baseline-v4.json,
reports/quality-v1-preservation.json, fixtures/quality-v1/* (separate AI author).
Interfaces: produces frozen cases with reference_answer, accepted_claims,
support_sections and exact support_quotes; Task 2 consumes them.
Record original report hashes, freeze the unchanged baseline policy, and review
the author metadata without opening challenge cases. Verify input/oracle hashes
and canonical reference-answer consistency mechanically.
Expected: immutable old reports, frozen 12 dev/24 challenge cases with disclosure.
Commit scoped input/provenance files.

### Task 2: Reproduce, score and improve grounding

Files: tests/integration/test_grounding_quality.py,
tests/unit/test_quality.py, src/evidence_rag/evaluation/quality.py,
scripts/quality_evaluate.py, scripts/quality_baseline_worker.py,
src/evidence_rag/models/generation.py, src/evidence_rag/answers/generation.py.
Interfaces: consumes Task 1 inputs; produces a frozen candidate and runner for
Task 3. The prompt revision also enters existing cache keys.
Write failing regressions first: native hostile-request/value versus quote/fact
pairs, full-answer support/completeness, irrelevant citations, invalid refusals,
hash drift and reference-oracle consistency. Run RED before implementation.
Implement strict scoring and a benchmark-only frozen-baseline adapter. Run
baseline development then at most two recorded candidate development iterations.
Expected: real failure reproduced, tests green, useful-answer and proper-refusal
counts recorded separately. Run ./scripts/check.sh. Commit scoped code/tests.

### Task 3: Verify flow, capture demo and review before final freeze

Files: browser capture test/helper, docs/CASE-STUDY.md, docs/PROVENANCE.md,
docs/PUBLICATION-AUDIT.md, README.md, CHANGELOG.md, docs/QUALITY-PASS.md.
Interfaces: consumes candidate; produces reviewed source for one final run.
Run actual lifecycle matrix and browser generation under shared lease; capture
only an authenticated, fictional-data browser context, never codes/cookies.
Run complete fixture browser and clean-checkout checks. Use one fresh judgment
code reviewer; one RED/GREEN author fix pass for material findings. Any semantic
fix counts toward the two-iteration limit. Freeze and commit source.
Expected: all boundary/strict checks pass and a concise inspected local demo.

### Task 4: One final evaluation and publication audit

Files: new reports/quality-v1*.json, demo assets, EVALUATION.md, README.md,
docs/STATE.md, docs/QUALITY-PASS.md, docs/PUBLICATION-AUDIT.md.
Interfaces: consumes frozen source and challenge; changes only evidence/docs.
Run one frozen final evaluation, all four retrieval methods, paired unchanged
baseline/candidate challenge plus original test regression. Preserve all old
reports. Report refusals, response coverage, oracle support/completeness,
resolution, invalid outputs and failures separately. Keep human metrics null.
If the gate fails keep quotations default and document it; no final-output tuning.
Audit tracked artifacts, licenses, provenance, secret exclusions, links and
recovery evidence. Update STATE with exact commands/counts/gaps. Commit locally.
Expected: reviewable local repository, no push/publication/deploy/external sends.
