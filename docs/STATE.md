# Evidence RAG state

Updated: 2026-10-18. Published source/history: [rbtbuilds/evidence-rag](https://github.com/rbtbuilds/evidence-rag), default branch `main`. Exact quotations remain default; native generation is explicitly experimental and its failed frozen gate remains disclosed. No deployment, tagged release or weights upload.

## Current publication and verification

Reviewed application commit: `7213efc3b99e6b9f3248bbd1cd490d39d4a46893`. [Hosted CI](https://github.com/rbtbuilds/evidence-rag/actions/runs/39137272692) passed at exactly that commit: Ruff, strict Pyright/TypeScript including tests, 126 non-model Python tests (2 native deselected), 13 web tests, build/contracts/corpus, 5 actual-API fixture browser flows (1 native skipped), 192 fixture evaluation rows. Clean-checkout checks passed at that same commit; an anonymous public clone also passed frozen installs, init/seed/doctor and Git fsck. Public README/architecture, clone URL, screenshot and MP4 were verified; media hashes match local files.

A fresh-context AI reviewer found one Important startup-cancellation race, no Critical findings or deferred Minors. The author reproduced it RED, synchronized cancellation with process creation, then passed GREEN, 20 focused runner/lease/job tests and the full strict suite. Normal cleanup still joins before lease release and does not cancel queued work. CodeRabbit's 221-file scope exceeded its free 150-file limit; no CodeRabbit clean review or paid use is claimed. Full review scope and limitations are in [publication record](PUBLICATION.md).

No model loads, new tuning or new native evaluation occurred. Frozen generation results predate the resource-management fix. Generation policy/decoder/models, corpus/oracles/criteria and frozen reports remain unchanged; UI labels now explicitly disclose experimental status. Human support/completeness, screen-reader use and customer impact remain unmeasured. Resolving citations and copied quotations do not prove factual support/relevance.

## Backup and final documentation receipt

The installed helper completed the authorized parent dry-run/audit/sync and established archive Evidence RAG at `7213efc3b99e6b9f3248bbd1cd490d39d4a46893`. All 235 child tracked files matched SHA-256 and Git fsck passed. All 946 pre-sync tracked hashes across four active source repositories matched the recovery copy. A later content verification reported new concurrent Scene Search source changes plus directory metadata drift; no zero-global-drift or live-database-consistency claim is made. The helper preserved overwritten files at `/Volumes/BentoLabs/_archive/portfolio/20261018-164539`; prior `d01f3d7` recovery history is retained. Supported task-owned exclusions protect regenerable runtimes; no source exclusion, sibling edit/process stop, ad hoc archive transfer or deactivation was used.

This STATE/publication update is a documentation closure after the application checkpoint. Its final public commit is the commit that last changes this file on `main`; the exact post-commit CI/backup outcome is attached locally using `git notes --ref=publication show HEAD` and preserved by the helper. The final completion receipt reports that exact commit and any remaining sibling drift. See [PUBLICATION.md](PUBLICATION.md) for commands, hashes and evidence boundaries.

## Historical local checkpoint

Historical local checkpoint (2026-10-17): The bounded answer-quality and local publication pass is complete. Its quality gate failed; exact quotations remain the default. The documented local repository is ready for publication review in its quotation mode, with experimental native generation clearly limited. No publication or generation promotion is claimed.

## Owned scope and recovery

Checkout/Git root: /Users/matthewgoralczyk/BentoLabs/portfolio/evidence-rag, branch feat/evidence-rag-v1. All commands use this child explicitly; the desktop chat may still display the resume workspace. API 8115/web 5115 stay loopback. No sibling source, parent coordination, vault or operations record was edited. No remote, push, deployment, paid use, model upload or external message.

Matthew authorized the helper-managed parent backup scope. The installed Bento helper tracked audit, sync and content verify passed after safely surfacing live sibling runtime drift and using a temporary supported exclusion filter. The unchanged temporary filter was removed. Recovery copy /Volumes/BentoLabs/portfolio/evidence-rag is at d01f3d723e19634e194a8af9ca22ebecfeacd878: Git fsck passed and all 194 tracked files matched SHA-256. Archived live runtimes are not claimed transaction-consistent. New commits are later than this pre-pass recovery point; no later archive sync is claimed. Full history: QUALITY-PASS.md.

## Frozen experiment and outcome

Criteria were fixed before challenge opening. A separate clean-context AI agent authored 12 development and 24 challenge cases from the original fictional sources, with its limited required-guidance aggregate exposure disclosed. Inputs/oracles, criteria and source hashes were frozen; no human review or statistical independence is claimed. All 24 pre-pass JSON reports remain unchanged.

Two substantive policies were developed; the second regressed quoted-request handling and was rejected. Iteration 1 was restored byte-identically and selected for the frozen comparison. The one final invocation ran on clean 9a324b82e446f9ac3ddc6ff834846cd0e30c5d80 with unchanged end provenance: 96 baseline challenge, 96 candidate challenge and 192 exposed regression rows. One outer ML lease covered all phases; workers exited/joined before successful release and completion. No resident model process remained afterward. No third tuning iteration or post-final oracle change occurred.

| Evidence | Recorded baseline | Selected candidate |
| --- | --- | --- |
| Exposed-test proper refusals | 46/48 | 47/48 |
| Exposed-test answerable responses | 109/144 | 109/144 |
| Exposed-test unnecessary refusals | 35 | 35 |
| Exposed-test resolving citations | 120/120 | 126/126 |
| Challenge proper refusals | 30/32 | 32/32 |
| Challenge answerable responses | 64/64 | 60/64 |
| Challenge finite-oracle complete | 56/64 | 57/64 |
| Challenge unverified responses | 10 | 3 |

All final blocks had zero invalid outputs/disclosures, embedding truncations, passage drops and output-limit hits. Citation resolution is not factual support. Failed gates: exposed-test 48/48 refusal target, 116/144 response target and challenge zero-unverified requirement. Hybrid still returns the marker category from the hostile quotation for test-041; no private marker is disclosed. The three challenge unverified rows are supported bare date responses outside a pattern that admits The date. Their frozen rejections remain, with no adjusted aggregate metric. Four challenge refusals unnecessarily reject a current training-handover correction. Results/outputs: QUALITY-RESULTS.md and reports/quality-v1*.json.

## Checks and recorded negative evidence

- ./scripts/check.sh at 9a324b8: Ruff, strict Pyright zero errors/warnings, 125 Python tests passed with 2 real-model tests deselected, strict TypeScript including tests/configuration, 11 web tests, build, contracts and corpus passed. Log .runtime/quality-review-fixed-check.log.
- Fixture browser: 5 passed, 1 actual scenario skipped. Genuine API sessions, role/cache isolation, import/replacement/deletion, stale links, escaped HTML, both themes/sizes and focus. Log .runtime/quality-fixture-browser.log.
- Actual API matrix: 96 requests passed in 85.72s; 32 proper local reader/deleted refusals, 16 authorized current-marker answers, zero forbidden disclosure. Exact test hash and uncommitted-tooling context retained in reports/actual-access-quality-v1.json. Log .runtime/quality-actual-access-selected-v1.log.
- Actual browser: 1 scenario passed in 19.1s (20.1s runner). Paced capture passed in 35.6s (36.6s runner), with current 35/v2 source, three proper unsupported refusals and supported cached answer. Login excluded from captured context; no fetch interception or persisted cookie/trace file. The 34.92s MP4/screenshots received AI-assisted sampled inspection. Logs .runtime/quality-actual-browser-v1.log and quality-actual-browser-paced-v1.log.
- Native paired semantic test remains FAILED: 1 test, two completeness pairs, 21.31s (bare No/current correction and 13/count-noun). Log .runtime/quality-native-selected-v1.log. Rejected iteration 2 also failed the quoted-request pair and actual reader-refusal assertion. No weakened test/xfail hides this evidence.
- Fresh AI code review: two Important lease/disclosure-reporting defects reproduced RED, fixed GREEN in one author pass; focused 7/7 and full 125 Python/11 web passed. No critical/deferred-minor findings. QUALITY-REVIEW.md records boundaries and author rulings. No further policy/model change.
- Final command: UV_CACHE_DIR="$PWD/.runtime/uv-cache" uv run --no-sync python -m scripts.quality_evaluate --phase final --output .runtime/quality-v1-final. Exit 0. Log .runtime/quality-v1-final.log; complete.json and start marker retained under ignored runtime. Write-once curation retained summary and all 384 fictional answer records without modifying originals.

- Clean checkout: ./scripts/clean_clone_check.sh passed at 46fa2b4cf7577330a5eb84ce7b97ab6f1adb7f2f: 36 ordinary dependency installs, frozen npm install, Ruff, strict Pyright zero errors/warnings, 125 Python tests/2 deselected, strict TypeScript, 11 web tests, build/contracts/corpus, 5 browser passes/1 actual skip (3.7s), 192 fixture evaluation rows. The task-owned clone was removed. Log .runtime/quality-clean-checkout.log SHA-256 713ad8da9156b270bd18b7859298567d398fd78ef7949f7fe4d8062e34993f93. Existing host Node 24/Chromium were used; no native weights loaded. This is a clean checkout on this Mac, not a fresh operating system or hosted CI.
- Fixture evaluation in that checkout: 32/48 proper refusals, 143/144 answerable responses, zero invalid/disclosure, 236/236 resolving citations. These are fixture results, separate from native quality. Exact quotations can still be irrelevant to an unsupported value question; their copied text is not a semantic correctness guarantee.
- Publication artifact scan: 232 current tracked files, no token-pattern/path findings, local Markdown file references resolve, all 24 historical reports preserved. Git history was scanned heuristically; model/corpus/oracle/criteria hashes remain frozen. Demo asset hashes, source/scan scope and limits are in PUBLICATION-AUDIT.md. No remote is configured. Later changes record evidence/formatting only; application/model/test source remains identical to 9a324b8.

Human factual support/completeness, screen-reader use, customer outcomes and broad generalisation remain unmeasured. No manual annotation/review work is assigned to Matthew. The deterministic quotation application and experimental native generator have separate evidence; a failed model gate does not become a passing claim through a citation score.
