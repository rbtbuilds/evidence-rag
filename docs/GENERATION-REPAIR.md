# Local Qwen generation repair

Repair and evaluation completed locally, 2026-10-16. Baseline: commit 30f06cd, strict local generation rejected all 96 development and 192 test outputs. The original reports remain intact.

## Diagnosis before implementation

The pinned model and tokenizer loaded successfully. The smoke output answered 35 units but renamed cited_chunk_ids to citation_ids and omitted insufficient_evidence. Development-only probes over one smoke case and four stratum cases reproduced renamed/missing keys, incorrect ID characters and a long citation list cut off at the 256-token output budget. These raw outputs were rejected by the existing validator correctly.

The snapshot generation_config.json sets repetition_penalty to 1.1. Transformers applies this to prompt tokens as well as generated tokens, discouraging exact schema/ID copying. An ablation forcing 1.0 alone still failed all five diagnostic outputs. Adding an inline JSON example enabled some valid output but introduced copied placeholder text; worked chat examples remained unreliable and could hallucinate. Those prompt-only attempts were not adopted. No held-out test examples were used to select the repair.

Diagnostic bulk records stay private under .runtime/qwen-diagnosis-v1.json and qwen-diagnosis-v2.json. These probes use actual pinned Qwen and real FTS5 BM25; fixture vectors are unused. They are diagnosis, not a quality benchmark or human review.

## Chosen boundary

The local worker uses pinned MIT lm-format-enforcer 0.11.3 to mask next-token choices against the same Pydantic JSON schema used by the existing validator. Its cited_chunk_ids enum is rebuilt from only the current request's authorised evidence. The schema forbids extra keys and retains the application's answer/type limits. A development probe with constrained keys/IDs still copied five 64-character IDs and hit 256 tokens on all four full-context cases, so decoding now permits at most two citations within the existing 256-token budget. The public validator remains unchanged with its original five-citation ceiling. This is a stricter generation subset, not post-hoc list trimming. The token trie is built once per owned worker; parser/request state is fresh for each question. The package's bundled Transformers adapter imports a symbol removed in Transformers 5, so a typed bridge uses the documented core token-enforcement API. It retains explicit parser settings after the core constructor replaces them with environment defaults; The allowed alphabet combines the pinned tokenizer characters with the current question and evidence characters. Decoding remains greedy, CPU float32, four threads, 2,048 input and 256 output tokens. Repetition penalty is explicitly neutral at 1.0.

No malformed JSON is repaired, no field alias is accepted, no ID is guessed or fuzzily matched, and no schema guard is relaxed. The application validator, authoritative current-version lookup, session/epoch revalidation and response publication gate still decide whether an answer can be shown. Empty evidence abstains explicitly; it does not enter the parser's empty-enum edge case. A new prompt revision prevents old answers being reused from cache.

Formatting constraints cannot prove factual support or a correct decision to abstain. The revised evaluation reports accepted answers, invalid outputs, abstention decisions, actual citation validity and output-limit hits separately. Human support/completeness review remains unmeasured. Actual-model verification and browser results are recorded below; every model operation held the shared lease and exited its worker before release.

## Review and regression evidence

A focused read-only judgment review found an Important loss of parser configuration and two measurement/curation issues. The bridge now restores the supplied configuration and unions request characters with the tokenizer alphabet. A worker Unicode regression failed before the request characters were added, then passed. A real-core UTF-8 byte-token test verifies 🛰 and 𐐷, nondefault field order, and environment overrides without loading weights. Output-limit totals now sum measured row deltas, excluding warmup; its regression failed with 7 instead of 0, then passed. Curation validates all six inputs before writing any new review sheet, and a missing-later-run regression confirms no partial revision is emitted. Existing evidence overwrite was refused and its original hash stayed unchanged.

Review boundaries remain explicit: human support/completeness need human review; broad multilingual quality is unmeasured; other model families, beams and batching are excluded; production identity/hosting/multiple processes remain excluded; the actual-generation browser launcher is a dedicated serial verification helper. Costs of these boundaries are unproven factual/translation quality, unsupported alternate inference paths, unsafe use outside loopback, and no general concurrency claim from the helper. The concrete Unicode decoding defect was in scope and fixed.

The prior fixture/browser run passed five scenarios and explicitly skipped the new actual-generation scenario. The separate command is `uv run --extra ml python -m scripts.actual_generation_browser`. It holds one shared lease, runs a genuine local API and browser session, generates with actual Qwen over real BM25 evidence, and opens the cited current source. It uses no embedding/reranking result in that BM25-only check. At frozen source e3823ce the actual scenario passed in 10.5 seconds (11.4-second Playwright run), generating an accepted answer containing 35 and opening its checked current v2 source. The ordinary suite still explicitly skips it.

Candidate d686d9e passed a clean checkout (85 Python/11 web tests, five fixture browser scenarios with one actual scenario explicitly skipped). Its real constrained smoke answered 35 units with valid JSON; all four full-context development probes hit the output cap while listing five hash IDs. The bounded policy is versioned evidence-json-v3-bounded and was frozen at e3823ce before held-out evaluation.

## Frozen repair results

Source: e3823ce2a47d78b336aa0b6476c663f0b3206d6e. Policy: evidence-json-v3-bounded; lm-format-enforcer 0.11.3; exact request-ID enum; at most two generated citations; repetition penalty 1.0; no sampling; seed 17; CPU float32/four threads; 2,048/256 token budgets. The original application validator, exact ID/version/access lookup and publication gate remain strict. No held-out outputs changed this policy.

| Split | Accepted answers | Insufficient evidence | Invalid output | Citations resolved | Output-limit hits | Correct expected abstentions |
| --- | --- | --- | --- | --- | --- | --- |
| Development | 83/96 | 11 | 2 | 160/160 | 2 | 2/24 |
| Test | 183/192 | 2 | 7 | 347/347 | 9 | 1/48 |

The repaired local Qwen block accepted 183/192 test answers, returned 2 insufficient-evidence abstentions and rejected 7 invalid outputs. All 347/347 emitted citations resolved to accessible current passages; 9 outputs hit the 256-token budget. Expected-abstention decisions were correct in 1/48 method/question cases. The sole correct test expected-abstention decision came from invalid-output rejection; no explicit insufficient-evidence response correctly handled an expected-abstention case. This measures format/citation validity and abstention, not factual support or completeness.

All six refreshed blocks total 864 rows. No forbidden marker disclosure, embedding truncation or passage dropping occurred. Current corpus/question/model-lock hashes match the baseline, and all new manifests record the same clean source/dependency hash. Original artifacts were hash-checked and retained unchanged. The new [curated report](../reports/evaluation-v3.json) and three review-v3 sheets retain provenance; human support/completeness remain unmeasured.

The development lunar-alloy answer was "Aster bench-top circulation trainer" with valid citations, an observed semantic failure. The two development rejections hit 256 tokens and were retained as failures. Both development correct expected-abstention decisions came from these invalid-output rejections; none came from a correct explicit insufficient-evidence decision. Constrained decoding makes output operational; it does not make this small model reliable at unsupported questions. Exact quotations remain the default.

Verification: 85 Python fixture tests, strict Pyright/Ruff/TypeScript, 11 web tests/build/contracts/corpus checks; clean checkout at e3823ce with five fixture browser scenarios and the actual scenario explicitly skipped; separate actual-generation browser pass; 96-request actual-model access/cache/replacement/deletion matrix; new actual embedding/reranking/generation smoke. No public CI, human citation review, screen-reader session, deployment or external send occurred.
