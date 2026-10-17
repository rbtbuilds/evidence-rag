# Quality-v1 development record

The frozen challenge was withheld from implementation. These are development
diagnostics with dirty working trees, not the final clean-source evaluation.
All inference was local under the shared lease, with the unchanged Qwen3 14B
snapshot, decoder bounds and public validation. Baseline replay uses the exact
v4 system prompt; no source-grounding oracles enter a generation request.

## First iteration

The original six-pair native regression failed on the exposed quoted-request
case before implementation (24.25 seconds). Iteration 1 fixed that pair but
returned only `No` for a correctable current-value question (19.45 seconds).
The expanded eight-pair regression then failed on that correction and an
answer omitting the counted noun (21.87 seconds). It retained legitimate
quoted assertions and questions about quoted instructions.

| Policy | Proper refusals | Answerable responses | Oracle-verified complete answers | Unverified non-refused answers |
| --- | --- | --- | --- | --- |
| Unchanged baseline | 12/16 | 32/32 | 27/32 | 9 |
| Iteration 1 | 12/16 | 32/32 | 24/32 | 12 |

Both blocks used all four actual retrieval methods over 12 new development
cases. Neither had invalid outputs, forbidden disclosure or unresolved emitted
citations (36/36 each). A reader-only question about an inaccessible manual's
replay card was answered with a public value from another subject. That is a
grounding error, not evidence that access filtering disclosed the private card.
Other unverified responses omitted a counted noun or included unnecessary
explanation. Finite oracles can also reject correct unanticipated wording;
their rejections are not automatically factual-error labels.

Iteration 1 is rejected as a quality improvement. Its exact prompt/settings
are retained in `config/quality-iteration1.json`; small results and raw hashes
are in `reports/quality-development-v1.json`. Baseline and intermediate output
files remain distinct. No frozen challenge output selected a change.

Scorer regressions failed before implementation, including full-answer versus
extra claims, missing support, immutable manifest anchoring and case-insensitive
disclosure. A real frozen-input test caught a criteria-path variable collision
before candidate inference; the failing log is retained. The corrected scorer
passes its checks. Actual matrix reports now require a fresh, contained output
name rather than overwriting prior evidence.
