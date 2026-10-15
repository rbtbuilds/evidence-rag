# Local Qwen generation repair

Work in progress, 2026-10-16. Baseline: commit 30f06cd, strict local generation rejected all 96 development and 192 test outputs. The original reports remain intact.

## Diagnosis before implementation

The pinned model and tokenizer loaded successfully. The smoke output answered 35 units but renamed cited_chunk_ids to citation_ids and omitted insufficient_evidence. Development-only probes over one smoke case and four stratum cases reproduced renamed/missing keys, incorrect ID characters and a long citation list cut off at the 256-token output budget. These raw outputs were rejected by the existing validator correctly.

The snapshot generation_config.json sets repetition_penalty to 1.1. Transformers applies this to prompt tokens as well as generated tokens, discouraging exact schema/ID copying. An ablation forcing 1.0 alone still failed all five diagnostic outputs. Adding an inline JSON example enabled some valid output but introduced copied placeholder text; worked chat examples remained unreliable and could hallucinate. Those prompt-only attempts were not adopted. No held-out test examples were used to select the repair.

Diagnostic bulk records stay private under .runtime/qwen-diagnosis-v1.json and qwen-diagnosis-v2.json. These probes use actual pinned Qwen and real FTS5 BM25; fixture vectors are unused. They are diagnosis, not a quality benchmark or human review.

## Chosen boundary

The local worker uses pinned MIT lm-format-enforcer 0.11.3 to mask next-token choices against the same Pydantic JSON schema used by the existing validator. Its cited_chunk_ids enum is rebuilt from only the current request's authorised evidence. The schema forbids extra keys and keeps existing answer/list/type limits. The token trie is built once per owned worker; parser/request state is fresh for each question. The package's bundled Transformers adapter imports a symbol removed in Transformers 5, so a typed bridge uses the documented core token-enforcement API. It retains explicit parser settings after the core constructor replaces them with environment defaults; Unicode support comes from the pinned tokenizer alphabet. Decoding remains greedy, CPU float32, four threads, 2,048 input and 256 output tokens. Repetition penalty is explicitly neutral at 1.0.

No malformed JSON is repaired, no field alias is accepted, no ID is guessed or fuzzily matched, and no schema guard is relaxed. The application validator, authoritative current-version lookup, session/epoch revalidation and response publication gate still decide whether an answer can be shown. Empty evidence abstains explicitly; it does not enter the parser's empty-enum edge case. A new prompt revision prevents old answers being reused from cache.

Formatting constraints cannot prove factual support or a correct decision to abstain. The revised evaluation will report accepted answers, invalid outputs, abstention decisions, actual citation validity and output-limit hits separately. Human support/completeness review remains unmeasured. Actual-model verification and browser results will be recorded here after they run under the shared lease.

## Review and regression evidence so far

A focused read-only judgment review found an Important loss of parser configuration and two measurement/curation issues. The bridge now restores the supplied configuration and unions request characters with the tokenizer alphabet. A worker Unicode regression failed before the request characters were added, then passed. A real-core UTF-8 byte-token test verifies 🛰 and 𐐷, nondefault field order, and environment overrides without loading weights. Output-limit totals now sum measured row deltas, excluding warmup; its regression failed with 7 instead of 0, then passed. Curation validates all six inputs before writing any new review sheet, and a missing-later-run regression confirms no partial revision is emitted. Existing evidence overwrite was refused and its original hash stayed unchanged.

Review boundaries remain explicit: human support/completeness need human review; broad multilingual quality is unmeasured; other model families, beams and batching are excluded; production identity/hosting/multiple processes remain excluded; the actual-generation browser launcher is a dedicated serial verification helper. Costs of these boundaries are unproven factual/translation quality, unsupported alternate inference paths, unsafe use outside loopback, and no general concurrency claim from the helper. The concrete Unicode decoding defect was in scope and fixed.

The prior fixture/browser run passed five scenarios and explicitly skipped the new actual-generation scenario. The separate command is `uv run --extra ml python -m scripts.actual_generation_browser`. It holds one shared lease, runs a genuine local API and browser session, generates with actual Qwen over real BM25 evidence, and opens the cited current source. It uses no embedding/reranking result in that BM25-only check. Actual execution is still pending the other project's lease; no passing model/browser result is claimed yet.
