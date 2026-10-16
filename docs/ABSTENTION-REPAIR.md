# Local abstention repair

In progress, 2026-10-16. Baseline: 6f503b1 and evaluation-v3.json. The baseline generated valid answers but explicitly refused none of the expected-abstention test cases. Its one legacy abstention credit came from invalid-output rejection. This repair keeps citation validation, access filtering, version checks and response publication strict.

## Acceptance and measurement

Select the policy with development questions only. Count explicit correct insufficient-evidence responses separately from invalid generation, and report unnecessary refusals on answerable questions. Response coverage is not factual accuracy or completeness. A policy that refuses everything fails acceptance. Preserving every answerable development response was an initial target, not achieved by the selected conservative 14B configuration; report that miss explicitly rather than treating refusal alone as overall quality.

Keep original snapshots, lock and reports. The exact original lock is archived in config/models.qwen25.lock.json (SHA-256 0576443c6287c8ca3fff8116a6f4a1a9aa97d1b2d04c4fc5c6f98a50f868f469). Eighteen existing evidence JSON hashes are retained in .runtime/abstention-baseline-hashes.json. New raw runs will use suffix v5, curated evidence v4. No question-specific keywords, forbidden-answer lists, expected labels or hidden sources enter inference.

The frozen test questions have already been evaluated and disclosed. New test results will be a regression comparison on the same synthetic scenario, not fresh unseen generalisation evidence. Human source support/completeness remain unmeasured.

## Development diagnostics

All trials used actual local inference under the shared lease, with real BM25 and unused fixture embedding/reranking doubles. These are diagnostics, not the canonical six-run evaluation. Bulk records remain ignored under .runtime.

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

## Selected native backend and current policy work

The active model lock now selects mlx-community/Qwen3-14B-4bit at a4d9b2df59d2c150bef02fcbe0d91046b7ca33a4, Apache-2.0, converted from Qwen/Qwen3-14B. Its quantisation is four bits, group size 64, with two manifest-pinned safetensors shards. The chat template is invoked with enable_thinking=False before constrained output begins. BGE and MiniLM remain unchanged. The rejected 4B candidate and its separate chat_template.jinja remain in ignored diagnostic storage with hashes; the preparation regression preserves templates whether embedded or separate.

MLX, MLX-LM and MLX Metal 0.32.2 are optional Apple Silicon dependencies in pyproject.toml/uv.lock. Fixture checks do not import MLX or load weights. CPU embedding/reranking retains four threads. Native generation is greedy, local-files-only and has no reused prompt cache. The 14B diagnostic sampled 1,938,931,712 RSS bytes and 9,224,821,784 peak accelerator bytes. Its diagnostic RSS allowance was 10 GiB, but the application retains 6 GiB because the observed process stayed below it. The accelerator detected-peak threshold increases explicitly from the 4B trial's 5 GiB to 12 GiB; the allocator cache guideline remains 256 MiB. Do not add RSS and accelerator peaks as independent allocations on unified memory.

MLX's memory limit is a guideline, not an instantaneous hard ceiling. The worker checks recorded peak after load and around generation steps; transient overshoot can occur before detection. A typed memory failure causes the parent to terminate/join its own worker before releasing the lease. Native 9 GiB result admission and explicit thinking-disable regressions failed under the prior policy, then all 29 targeted generation/resource checks passed. Values above 12 GiB remain rejected, including a 13 GiB fake result and stream-closure regression. Test doubles establish control flow, not measured model memory.

The selected policy uses one generation pass. Its prompt explicitly separates a requested fact or correction from a discussion of missing information, provides the complete empty-refusal JSON (without any placeholder citation IDs), and says a contradicted assumption should be corrected from current evidence. The decoder bounds answer text to 180 characters, at most two exact supplied IDs, 2,048 input tokens and 256 output tokens. Field order remains free, with the model normally writing the answer first. The public validator retains its stricter type/ID/access/version rules and five-citation ceiling; no fuzzy matching or output repair was added.

Separate boolean and evidence-first classifiers were rejected, removed from application code and retained only as ignored diagnostic artifacts. They were too likely to label a false assumption as unanswerable. No classification prompt, decision flag, extra decision tokens or QA model remain in the selected application.

The selected one-pass policy got all 24 BM25 development abstention decisions right. This is six proper refusals and 18 answerable responses, not a human factual-support score. The final production prompt was checked byte-for-byte against the successful diagnostic addition. This was a 4B policy diagnostic, not the final 14B canonical result. Source-freeze and the six canonical evaluation blocks remain pending.

The stronger actual browser flow passed one scenario in 9.9 seconds (10.8-second Playwright run): supported 35-unit answer/current citation, proper empty lunar-alloy and reader-private-marker refusals, and supported cached-answer retention. The stricter actual lifecycle matrix passed BM25 but then failed because a local reader/deleted request under dense retrieval answered instead of refusing. The 4B candidate is therefore not accepted as a complete repair. Its failed log is .runtime/abstention-onepass-actual-matrix.log. No canonical evaluation has run yet.

The subsequent 14B development probe used all 24 BM25 development questions plus supported, unsupported, reader-private and authorised-marker cases for each other actual retrieval method. It refused all 12 expected-abstention cases correctly and emitted no invalid output, but refused five answerable BM25 cases (dev-005, dev-006, dev-011, dev-018, dev-019). The target of retaining every answerable response was missed. Reliable refusal is the priority for this repair, so the larger conservative configuration proceeds to actual boundary checks and evaluation with that coverage cost explicit. No frozen test output selected it. Raw report: .runtime/abstention-qwen14b-development-probe.json.

## Focused review: one author fix pass

One existing judgment reviewer audited the new native boundary, decision handling, resource policy and provenance. No new reviewer cascade was created.

- Important: a malformed separate decision could itself match the public answer schema and gain refusal/answer credit. An authoritative invalid-decision flag and service regressions first closed that trial defect. The final design removes the rejected classifier and its entire decision protocol, eliminating this crossover path. Its trial tests are retained only in ignored diagnostic storage.
- Important: MLX loads every root model*.safetensors file; an unlisted file could override verified tensors. Native readiness and the final loader now require the complete consumed filename set to equal the manifest, before optional imports or weight load. Existing snapshots had no extra files. The loader regression was red before the guard; readiness also has a direct rejection regression.
- The reviewer classified non-finite additive masking as Minor. This task treats decoder integrity as Important and fixes it in the same pass: start with negative infinity, copy only allowed finite logits, and fail closed for non-finite allowed logits. NaN/infinity regressions failed before the change; no such numeric failure was observed in actual inference.

All 27 targeted trial decision/mask/native-loader checks passed after the review fixes. The subsequent one-pass/answer-bound regressions failed before the selected policy was implemented, then all 11 generation/decoding checks passed. The final 14B-policy suite passes 110 Python tests (one actual test deselected), strict Python/TypeScript checks, 11 web tests, build/contracts/corpus checks. Five real-API fixture browser scenarios passed earlier (one actual scenario explicitly skipped); The 14B actual browser scenario passed in 17.4 seconds (18.3-second Playwright run). The stricter 96-request actual access/lifecycle matrix passed all four methods in 82.59 seconds, including 32 explicit local reader/deleted refusals and 16 authorised local marker responses. Fresh clean-checkout results remain pending.

Explicit review limits: factual entailment and completeness need human review; non-Apple native execution is unsupported; rejected transformer/QA candidates are not automatically promoted; production identity, public hosting and multiple API processes are outside v1. Historic records remain intact. Final canonical model quality/timing/memory and clean-checkout reproducibility require fresh completed runs before a completion claim.

## Remaining verification

1. Completed development policy selection with actual supported/unsupported/correction/private-reader cases.
2. Passed the stronger actual browser test: supported answer/current source, lunar-alloy refusal, reader-private-marker refusal, supported cached answer retained. .runtime/abstention-actual-browser-green.log is a failed historical run despite its filename; never call it passing.
3. Passed the stricter 96-request actual API matrix: local reader/deleted requests explicitly refuse with empty answer/no citations; maintainer active/replaced requests answer the current marker; every emitted citation opens only while accessible/current.
4. Run strict checks, freeze clean source in a local commit, then run all six fixture/actual development/test blocks on that same clean head and curate immutable v4 reports. Verify all original evidence hashes.
5. Verify a clean checkout, update STATE/README/evaluation/runbook/verification/changelog, and record exact counts, resource costs and remaining limits. Keep all inference and artifacts local. No push, deployment, model upload, paid service or external message is authorised.
