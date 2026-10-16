# Local abstention repair

Completed local implementation/evaluation, 2026-10-16, with two remaining refusal errors and a conservative-coverage cost. Baseline: 6f503b1 and evaluation-v3.json. The baseline generated valid JSON but explicitly refused none of the expected-abstention test cases; its one legacy credit came from invalid-output rejection. Final measured source is c4b3fffb049a448c4bddaefcfa23128188b0f8df. Citation validation, access filtering, version checks and response publication remain strict.

## Acceptance and measurement

Select the policy with development questions only. Count explicit correct insufficient-evidence responses separately from invalid generation, and report unnecessary refusals on answerable questions. Response coverage is not factual accuracy or completeness. A policy that refuses everything fails acceptance. Preserving every answerable development response was an initial target, not achieved by the selected conservative 14B configuration; report that miss explicitly rather than treating refusal alone as overall quality.

Keep original snapshots, lock and reports. The exact original lock is archived in config/models.qwen25.lock.json (SHA-256 0576443c6287c8ca3fff8116a6f4a1a9aa97d1b2d04c4fc5c6f98a50f868f469). Eighteen existing evidence JSON hashes are retained in .runtime/abstention-baseline-hashes.json. New raw runs use suffix v5, curated evidence v4. All 18 original evidence JSON hashes were checked unchanged after curation. No question-specific keywords, forbidden-answer lists, expected labels or hidden sources enter inference.

The frozen test questions have already been evaluated and disclosed. New test results are a regression comparison on the same synthetic scenario, not fresh unseen generalisation evidence. Human source support/completeness remain unmeasured.

## Development diagnostics

All trials used actual local inference under the shared lease. Early BM25-only trials used real FTS with unused fixture embedding/reranking doubles. The later 14B probe built an actual BGE index and also checked dense, hybrid and reranked retrieval. These are diagnostics, not the canonical six-run evaluation. Bulk records remain ignored under .runtime.

| Candidate and policy | Development result | Decision |
| --- | --- | --- |
| Qwen2.5 0.5B, insufficient flag first | All 12 diagnostic questions refused; seven answerable responses lost | Reject |
| Qwen2.5 1.5B, insufficient flag first | All 24 refused; 18 answerable responses lost | Reject |
| Qwen2.5 1.5B, original answer first | 0/6 proper refusals; 16/18 answerable responses | Reject model swap alone |
| Qwen2.5 0.5B, boolean answerability gate | All 24 accepted; six unsupported errors | Reject |
| Qwen2.5 1.5B, boolean answerability gate | 6/6 proper refusals; nine answerable responses lost | Reject |
| RoBERTa SQuAD2 span/null gate, margin zero | 18/24 decisions correct; private-reader false support overlaps missed answerable scores | Reject; no single threshold fixes both |
| Qwen3 4B MLX, original answer first | 6/6 proper refusals and 18/18 answerable responses in standalone probe | Select larger backend for production diagnosis |
| Same Qwen3, ordinary production/browser prompt | Reader-private marker produced a long missing-evidence explanation, then hit the answer cap | Reject as complete repair |
| Qwen3, strict boolean gate before answer | 6/6 proper refusals, but six answerable responses lost | Reject gate policy |
| Qwen3, evidence-first decision gate | 6/6 proper refusals, but four correction responses lost | Reject separate classifier |
| Qwen3, insufficient flag first in one pass | 4/6 proper refusals; 15/18 answerable responses | Reject |
| Qwen3 4B, answer first with explicit empty-refusal instruction and 180-character answer bound | 6/6 BM25 proper refusals; 18/18 answerable responses; subsequent actual dense refusal failure | Reject as complete repair |
| Qwen3 14B, same policy with thinking explicitly disabled | 12/12 proper refusals across 36 development probes; 19/24 answerable responses, including 13/18 in BM25 | Select conservative candidate; coverage target missed |

The 1.5B candidate is Qwen/Qwen2.5-1.5B-Instruct at 989aa7980e4cf806f80c7fef2b1adb7bc71aa306, Apache-2.0. The diagnostic used a disclosed 10 GiB RSS bound and reached roughly 6.495 GiB; it was not promoted. The application retains its 6 GiB RSS ceiling.

The rejected QA model is deepset/roberta-base-squad2 at adc3b06f79f797d1c575d5479d6f5efe54a9e3b4, CC-BY-4.0. A zero null-score margin missed the theme and four correction questions, while a reader-inaccessible marker question scored positive. Threshold tuning cannot separate the overlapping scores. Its provisional tested code was removed from the app and retained only in ignored diagnostic storage. No QA weights or model are part of the active bundle.

## Selected native backend and policy

The active model lock now selects mlx-community/Qwen3-14B-4bit at a4d9b2df59d2c150bef02fcbe0d91046b7ca33a4, Apache-2.0, converted from Qwen/Qwen3-14B. Its quantisation is four bits, group size 64, with two manifest-pinned safetensors shards. The chat template is invoked with enable_thinking=False before constrained output begins. BGE and MiniLM remain unchanged. The rejected 4B candidate and its separate chat_template.jinja remain in ignored diagnostic storage with hashes; the preparation regression preserves templates whether embedded or separate.

MLX, MLX-LM and MLX Metal 0.32.2 are optional Apple Silicon dependencies in pyproject.toml/uv.lock. Fixture checks do not import MLX or load weights. CPU embedding/reranking retains four threads. Native generation is greedy, local-files-only and has no reused prompt cache. The 14B diagnostic sampled 1,938,931,712 RSS bytes and 9,224,821,784 peak accelerator bytes. Its diagnostic RSS allowance was 10 GiB, but the application retains 6 GiB because the observed process stayed below it. The accelerator detected-peak threshold increases explicitly from the 4B trial's 5 GiB to 12 GiB; the allocator cache guideline remains 256 MiB. Do not add RSS and accelerator peaks as independent allocations on unified memory.

MLX's memory limit is a guideline, not an instantaneous hard ceiling. The worker checks recorded peak after load and around generation steps; transient overshoot can occur before detection. A typed memory failure causes the parent to terminate/join its own worker before releasing the lease. Native 9 GiB result admission and explicit thinking-disable regressions failed under the prior policy, then all 29 targeted generation/resource checks passed. Values above 12 GiB remain rejected, including a 13 GiB fake result and stream-closure regression. Test doubles establish control flow, not measured model memory.

The selected policy uses one generation pass. Its prompt explicitly separates a requested fact or correction from a discussion of missing information, provides the complete empty-refusal JSON (without any placeholder citation IDs), and says a contradicted assumption should be corrected from current evidence. The decoder bounds answer text to 180 characters, at most two exact supplied IDs, 2,048 input tokens and 256 output tokens. Field order remains free, with the model normally writing the answer first. The public validator retains its stricter type/ID/access/version rules and five-citation ceiling; no fuzzy matching or output repair was added.

Separate boolean and evidence-first classifiers were rejected, removed from application code and retained only as ignored diagnostic artifacts. They were too likely to label a false assumption as unanswerable. No classification prompt, decision flag, extra decision tokens or QA model remain in the selected application.

The one-pass 4B policy diagnostic got all 24 BM25 abstention decisions right: six proper refusals and 18 answerable responses. This was not a human factual-support score and did not predict the later dense failure. The final prompt addition was checked byte-for-byte against that development policy; the selected 14B model and its explicit thinking-disable setting were then frozen before canonical evaluation.

The 4B actual browser trial passed one scenario in 9.9 seconds (10.8-second Playwright run): supported 35-unit answer/current citation, proper empty lunar-alloy and reader-private-marker refusals, and supported cached-answer retention. The stricter actual lifecycle matrix passed BM25 but then failed because a local reader/deleted request under dense retrieval answered instead of refusing. The 4B candidate was therefore rejected as a complete repair. Its failed log is .runtime/abstention-onepass-actual-matrix.log. Canonical evaluation had not run at that point.

The subsequent 14B development probe used all 24 BM25 development questions plus supported, unsupported, reader-private and authorised-marker cases for each other actual retrieval method. It refused all 12 expected-abstention cases correctly and emitted no invalid output, but refused five answerable BM25 cases (dev-005, dev-006, dev-011, dev-018, dev-019). The target of retaining every answerable response was missed. Reliable refusal is the priority for this repair, so the larger conservative configuration proceeded to actual boundary checks and evaluation with that coverage cost explicit. No frozen test output selected it. Raw report: .runtime/abstention-qwen14b-development-probe.json.

## Focused review: one author fix pass

One existing judgment reviewer audited the new native boundary, decision handling, resource policy and provenance. No new reviewer cascade was created.

- Important: a malformed separate decision could itself match the public answer schema and gain refusal/answer credit. An authoritative invalid-decision flag and service regressions first closed that trial defect. The final design removes the rejected classifier and its entire decision protocol, eliminating this crossover path. Its trial tests are retained only in ignored diagnostic storage.
- Important: MLX loads every root model*.safetensors file; an unlisted file could override verified tensors. Native readiness and the final loader now require the complete consumed filename set to equal the manifest, before optional imports or weight load. Existing snapshots had no extra files. The loader regression was red before the guard; readiness also has a direct rejection regression.
- The reviewer classified non-finite additive masking as Minor. This task treats decoder integrity as Important and fixes it in the same pass: start with negative infinity, copy only allowed finite logits, and fail closed for non-finite allowed logits. NaN/infinity regressions failed before the change; no such numeric failure was observed in actual inference.

All 27 targeted trial decision/mask/native-loader checks passed after the review fixes. The subsequent one-pass/answer-bound regressions failed before the selected policy was implemented, then all 11 generation/decoding checks passed. The final 14B-policy suite passes 110 Python tests (one actual test deselected), strict Python/TypeScript checks, 11 web tests, build/contracts/corpus checks. Five real-API fixture browser scenarios passed earlier (one actual scenario explicitly skipped). The 14B actual browser scenario passed in 17.4 seconds (18.3-second Playwright run). The stricter 96-request actual access/lifecycle matrix passed all four methods in 82.59 seconds, including 32 explicit local reader/deleted refusals and 16 authorised local marker responses. Clean-checkout verification subsequently passed at c4b3fffb049a448c4bddaefcfa23128188b0f8df: frozen installs, 110 Python tests, 11 web tests, strict checks/build/contracts, five fixture browser scenarios (one actual scenario skipped) and 192 fixture test rows.

Explicit review limits: factual entailment and completeness need human review; non-Apple native execution is unsupported; rejected transformer/QA candidates are not automatically promoted; production identity, public hosting and multiple API processes are outside v1. Historic records remain intact. Completed canonical runs below supply measured quality/timing/memory and clean-checkout evidence; the remaining refusal and coverage failures stay open.

## Completed evidence and limits

| Split | Proper expected refusals | Answerable responses | Unnecessary refusals | Invalid output | Citations resolved | Output-limit hits |
| --- | --- | --- | --- | --- | --- | --- |
| Development | 24/24 | 51/72 | 21 | 0 | 55/55 | 0 |
| Test | 46/48 | 109/144 | 35 | 0 | 120/120 | 0 |


The local Qwen3 14B block correctly returned explicit empty insufficient-evidence refusals in 46/48 expected-abstention test method/question cases, compared with 0/48 in v3. It answered 109/144 answerable cases and unnecessarily refused 35; 0 outputs were invalid. All 120/120 emitted citations resolved to accessible current passages. These are abstention and format/access measurements, not human factual-support or completeness scores. Two remaining errors are the same reader question under BM25 and hybrid: the model treats a quoted hostile instruction as evidence for a calibration marker. No restricted marker is disclosed.

All six canonical blocks total 864 rows on the same clean source c4b3fffb049a448c4bddaefcfa23128188b0f8df, source/question hashes and dependency lock. Actual blocks use the same pinned model bundle; fixture blocks load no models. There were no forbidden-marker disclosures, embedding truncations or dropped passages. Counters keep invalid output separate from proper refusals and expose unnecessary refusal. The refusal target is also not fully met: test-041 is answered under BM25 and hybrid by treating a quoted hostile instruction as the requested marker. Actual restricted markers remain absent. The full-coverage target remains missed; no overall factual-quality or completeness claim follows from the refusal gain.

The stronger native browser flow passed its supported/current-source, lunar-alloy refusal, reader-private-marker refusal and supported-cache checks. The strict actual API matrix passed 96 serial requests across roles, four retrieval methods, answer modes, caches and active/replaced/deleted sources. Its local cells include 32 explicit reader/deleted refusals and 16 correct authorised marker answers. Deterministic fixture barriers independently cover mutation/publication races.

Re-preparation reused the pinned SHAs/hashes and preserved the active lock. The actual smoke returned a 384-dimensional embedding, a rerank score and valid 35-unit JSON in 23 output tokens. Clean-checkout and strict checks passed. Canonical raw paths are .runtime/eval-*-v5; immutable [v4 summary](../reports/evaluation-v4.json), [actual matrix](../reports/actual-access-matrix-v4.json) and [smoke](../reports/local-smoke-v4.json) retain provenance. Three new human review sheets remain unfilled.

The generated blocks recorded at most 9,229,360,168 peak accelerator bytes (8.60 GiB) and 2,376,171,520 sampled worker RSS bytes (2.21 GiB). Do not add these as independent allocations on unified memory. Native generation uses a 12 GiB detected-peak threshold and 256 MiB allocator cache guideline; sampled worker RSS remains capped at 6 GiB. MLX allocation limits are guidelines, so transient overshoot can precede detection.

The reused frozen test is regression evidence after prior disclosed runs, not newly unseen data. Selection used development evidence only, including the disclosed failure of the full-coverage target; no test output changed the policy. Human source support/completeness remain unmeasured. The repetitive fictional corpus and serial model tests do not establish broad generalisation, prompt obedience, production identity or a general security proof. Model, policy and backend changed together; timing differences have no single-cause attribution.

Exact commands and current pickup state are in [STATE](STATE.md), [evaluation](../EVALUATION.md) and [runbook](RUNBOOK.md). All model inference and evidence stayed local. No publication, push, deployment, model upload, paid compute or external message occurred.
