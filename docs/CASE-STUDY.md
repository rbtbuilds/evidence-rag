# Case study: evidence that survives document changes

Evidence RAG is a local simulation for someone who searches technical manuals, checks the current edition and copies a supporting passage. The fictional Aster trainer gives the project a repeatable, shareable corpus without customer documents or real equipment instructions. There is no pilot, measured time saving or customer impact claim.

## The delivery problem

An answer can become unsafe for several different reasons: it uses a document the reader cannot access, cites a retired edition, survives deletion through cache, or states a claim the cited passage does not support. The first three need application guarantees; the fourth needs a separate quality measurement. Treating all of them as a single citation score hides important failures.

The application uses FastAPI, SQLite and React with typed contracts. It compares role-partitioned BM25, dense cosine search, reciprocal-rank fusion and a MiniLM reranker. Opaque server sessions determine reader/maintainer scope. One SQLite transaction publishes versions, chunks, vectors, role-specific FTS and cache invalidation. Final response publication rechecks session, version and epoch under the same gate used by mutation publication. Deletion clears application bodies and pending payloads; it is not forensic disk erasure.

## A failure that changed the evaluation

The earlier local Qwen3 14B policy produced valid outputs and 120/120 accessible current citations, yet it treated a quoted hostile request as evidence of the requested marker value. No private marker leaked. The answer still failed grounding: a request to reveal a value does not state the value.

The repair therefore tested pairs: quoted requests versus genuine quoted assertions, questions about the quoted wording versus requests for missing values, and outdated premises versus current facts. Native inference reproduced the original bug before a general policy change. A second policy tried to improve subject matching and completeness but regressed the quoted-request case. With the two-iteration budget exhausted, the first candidate was restored exactly. Known incomplete corrections and quantity answers remain in the failing native regression.

A separate AI author created a versioned source-grounded development/challenge set before final evaluation. Finite full-answer patterns and required cited source quotes make automatic support/completeness checks inspectable. They also reject some correct paraphrases. The reports retain response coverage, oracle verification, proper refusals and citation resolution separately; none substitutes for a human usefulness score.

## Measured outcome

On the exposed test, proper refusals changed from 46/48 to 47/48 and answerable responses from 109/144 to 109/144; unnecessary refusals changed from 35 to 35. On the new challenge, proper refusals changed from 30/32 to 32/32 and finite-oracle complete coverage from 56/64 to 57/64, while response coverage changed from 64/64 to 60/64.

The pre-registered quality gate failed: regression_refusals, regression_coverage, challenge_no_unverified_answers. Exact quotations remain the default. No final-output tuning, oracle relaxation or third policy iteration occurred. The challenge's finite-form false negatives are reported separately from unsupported claims. The known native completeness test still fails. This is evidence for a bounded experimental generator, not a production reliability claim. [Results and exact outputs](QUALITY-RESULTS.md) make the tradeoff inspectable.

The exposed-test targets were 48/48 proper refusals and at least 116/144 answerable responses; observed 47/48 and 109/144 miss both. Hybrid still answers test-041 with `restricted calibration review marker`, citing the public training quotation instead of refusing a value question. No private marker is disclosed. The general grounding defect is reduced, not eliminated, and answerable response coverage did not improve.

## How to inspect the work

Start with the account-free fixture quickstart. Ask for the circulation limit, open its dated v2 citation, then ask an unsupported question. As maintainer, replace a document and verify that the old source link fails; delete it and verify that subsequent answers and source opens cannot use it. Fixture vectors/reranking are test doubles, visibly labelled. Optional local model inference is a distinct profile with pinned snapshots and one shared machine lease.

The retained 35-second native browser capture shows a supported answer, the current source, three unsupported refusals and a cached supported answer. It uses real API calls and local Qwen, with authentication outside the recorded context and reading pauses for clarity. It demonstrates that shown path, not universal reliability or browser coverage of every retrieval method.

## Engineering decisions supported by evidence

- Keep exact quotations as the default when the bounded generation-quality gate fails.
- Preserve strict citation IDs, access and lifecycle checks rather than granting a model permission to resolve its own sources.
- Freeze baseline policy, criteria, sources, questions and oracles before final comparison; keep failed candidates and all historical reports.
- Keep the machine lease across the complete comparison. A failed worker join must keep ownership occupied, not merely log an error and admit another benchmark.
- Record failures plainly. Valid JSON, an openable citation and a confident answer are different properties.

All development and code review were AI-assisted. Human factual support/completeness, screen-reader use, broad generalisation and customer impact are unmeasured. The source is published as a portfolio artifact; the publication record identifies exact commits and checks. No hosted application or customer deployment is claimed.
