# Publication audit

Matthew explicitly authorized public rbtbuilds/evidence-rag creation, source/history push, main as default and hosted Actions on 2026-10-18. Publication status and commit-specific evidence are in [PUBLICATION.md](PUBLICATION.md). No deployment, tagged release, model upload or paid action is included. The child repository is the publication unit; parent legacy/client folders are excluded.

## Recovery and ownership

The installed Bento helper registers the parent portfolio. Matthew explicitly authorized that backup scope. A helper dry-run/tracked audit, supported temporary exclusions, sync and content verification established the pre-pass recovery copy at /Volumes/BentoLabs/portfolio/evidence-rag, source d01f3d7. All 194 tracked files matched SHA-256 and Git fsck passed. Live sibling runtime drift was surfaced before verification; existing archived runtimes are not claimed transaction-consistent. The task-owned temporary filter was removed. No ad hoc archive transfers or sibling source edits were performed. New local commits are later than this recovery point; no later archive sync is claimed.

## Content and licence boundary

Original source/docs, fictional Aster corpus and authored question/oracle sets use the MIT licence. Development, source inspection, dataset authorship and code review were AI-assisted. The separate challenge author had required-guidance aggregate exposure; data reuse precludes statistical independence. Human source-support/completeness, accessibility screen-reader tests and customer impact remain unmeasured.

Third-party model snapshots and card/file hashes are in config/models.lock.json: BGE MIT, MiniLM Apache-2.0 and converted Qwen3 Apache-2.0. They are optional downloaded assets, not redistributed weights. Code MIT terms do not relicense those assets or dependencies. Python/web dependency versions are locked separately. A local installed-metadata inventory and package-lock licence-label summary were recorded as inventory, not comprehensive legal clearance. The tokenizer bridge adapts an attributed LM Format Enforcer algorithm; its full upstream MIT notice is retained in THIRD-PARTY-NOTICES.md and was verified against installed and upstream 0.11.3 text. No real equipment/customer manuals were imported.

The deliberate role-restricted marker strings in fictional fixtures/public evaluation records are test data, not credentials. Opaque runtime session/CSRF tokens and launch codes stay excluded. The committed .env.example contains only public profile/path settings. No weights, local databases, caches, cookies or raw model-worker logs are release artifacts.

## Automated inspection limits

The current/history heuristic scan searches reachable blob content for private-key headers and recognizable GitHub, provider, Slack and AWS token patterns. A filename audit checks runtime/cache/environment/weight/database paths, with .env.example and application Python models modules distinguished from weight assets. The staged-artifact scan and later complete-checkout checks are recorded below. Zero matches is not proof that arbitrary secrets or private information cannot exist.

Local Markdown references are checked after documentation is complete. Historical local checks did not exercise HTTP links or hosted CI; the publication record separately records the current public checks. Existing historical reports are hash-checked against the 24-file preservation record rather than rewritten. Criteria, sources, dataset inputs/oracles and model locks remain unchanged after final freeze.

## Browser demonstration

The actual browser capture is docs/demo/quality-v1.mp4: H.264, yuv420p, 1280x900, 34.92 seconds, faststart. The capture test signs in outside a separate recorded context, transfers session state in memory, exercises real API/Qwen/BM25 calls and closes the context in finally. Traces and persisted cookie storage remain disabled. Reading pauses are capture-only and must not be used as latency measurements.

The three screenshots and sampled frames were inspected with AI assistance: supported 35-unit answer, current v2 passage, empty unsupported refusals and cached supported answer. This is not human review or a full-frame forensic credential-clearance claim. Retained assets depict owned fictional text and the application UI, with no audio or third-party imagery. Original raw captures remain ignored in .runtime.

Encoding used the task-owned paced WebM as input with ffmpeg/libx264, CRF25, yuv420p and movflags +faststart. Asset SHA-256 hashes and validation evidence follow. No authentication frame or runtime code is intentionally retained.

## Recorded artifact checks

The staged publication set contains 232 tracked files. At source 9a324b8, current working-tree token/path checks and 394 reachable historical blob checks found no matching token patterns or forbidden runtime/database/weight/environment paths. All 56 checked local Markdown file references existed. External URLs and heading anchors were not checked. All 24 prior frozen reports matched their preservation hashes. The final post-commit scan is recorded with the checkout result below.

The dependency inventory records 69 installed Python distributions and 161 locked web entries; absent licence metadata remains null.

| Asset | SHA-256 |
| --- | --- |
| docs/demo/quality-v1.mp4 | 4f50b8688686f050bed9377718fa852a0478c17cc6f0b04e30dd7dfe35b20d41 |
| docs/images/quality-v1-citation.png | a11061dcc8389644d025f7f49acc01abd12011a941a1cecd7b1701af9fa1bdef |
| docs/images/quality-v1-supported.png | b3daf91a94e0d0dc5db6e291db1b45fcd7ec85f7e5e3e352b86fb6b1dea3d24c |
| docs/images/quality-v1-unsupported.png | 485f8f0abd10798eb4a8e3842f0043c278b8c2f244d89093492079db4fba794d |
| docs/images/workbench.png | bfc1ad2bccbee661f20c8afea8464dfb39c8e2ff329009e007f0ac53edb41c92 |

The final quality run completed 384 local-model rows at clean 9a324b8 with unchanged provenance; all final blocks had zero invalid/disclosed outputs, truncations, passage drops and output-limit hits. Peak sampled worker RSS was 2,619,080,704 bytes and peak MLX allocation 9,274,155,072 bytes. Unified memory peaks must not be added as separate independent allocations. The quality gate failed 47/48 refusals versus 48/48, 109/144 response coverage versus 116/144, and three finite-oracle unverified date responses. Exact quotations remain default; current-correction/count-noun native tests remain negative evidence.

## Clean checkout and evidence closure

The complete publication candidate `46fa2b4cf7577330a5eb84ce7b97ab6f1adb7f2f` passed `./scripts/clean_clone_check.sh`: frozen ordinary installs, strict checks, 125 Python tests (2 real-model tests deselected), 11 web tests, build/contracts/corpus, 5 genuine fixture browser passes (1 actual scenario skipped), 192 fixture evaluation rows. No native weights were loaded. The same Mac supplied Node 24 and Chromium; no fresh-OS/hosted-CI claim follows. The owned temporary clone was removed. Log SHA-256: `713ad8da9156b270bd18b7859298567d398fd78ef7949f7fe4d8062e34993f93`. Fixture refusal correctness is 32/48, response coverage 143/144 and citation resolution 236/236, with zero invalid/disclosure; these are not native results or a claim that quotations guarantee relevance.

At that historical closure, source/application/test files were unchanged from 9a324b8. The publication pass adds explicit experimental UI labelling and regression tests; generation policy, models, frozen inputs and reports remain unchanged. Later commits record documentation/evidence closure. Human metrics remain unmeasured, and the known native quality gate/semantic failures are retained without waiver. This paragraph records the historical local checkpoint; the separately authorized public publication is recorded in PUBLICATION.md.

Final post-candidate scan (2026-10-17T20:34:44Z, HEAD 46fa2b4 plus documentation closure): 232 current tracked files and 409 reachable historical blobs, zero token-pattern or forbidden-path findings, 56 existing local Markdown file references, all 24 original report hashes preserved. Scope is heuristic and excludes external URLs/anchor validity. Runtime scan details stay in .runtime/publication-final-scan.json; later closure text changes no application/model inputs.


## Public publication pass (2026-10-18)

The interface now labels local generation experimental beside the mode control and on generated answers, while quotation submission stays default. Two regressions were observed failing before the copy fix and passing afterward. Strict checks passed: 125 non-model Python tests (2 native deselected), 13 web tests, zero strict type errors, build/contracts/corpus. Five real-API fixture browser tests passed; one native test was explicitly skipped. No native evaluation was rerun or retuned.

The current fixture screenshot is `docs/images/publication-fixture.png`, SHA-256 `b16376cf1037e47e269a719adeaad3159e731bcf9418d6ede98ce1004098c9ce`. It was captured automatically from the real fixture API/browser flow and inspected with AI assistance. The original screenshot and native recording remain unchanged; the latter predates the explicit experimental UI label and is captioned accordingly. Both themes and mobile/desktop widths were exercised. This is not human accessibility or factual support review.

CodeRabbit's free 150-file limit rejected the complete 221-file review. It produced no completed review; no clean result is inferred and no credits were used. A fresh-context automated reviewer supplies the independent review instead, with findings and fixes recorded in PUBLICATION.md. Full upstream MIT notice for the adapted tokenizer conversion bridge is retained and byte-verified against the installed and upstream 0.11.3 licence.


Public source checkpoint `7213efc3b99e6b9f3248bbd1cd490d39d4a46893` passed [hosted CI](https://github.com/rbtbuilds/evidence-rag/actions/runs/39137272692), strict 126 Python/13 web checks, 5 fixture browser flows and the clean-checkout/public-clone checks. Public screenshot and MP4 returned anonymous HTTP 200 and matched their recorded hashes. The README rendered its architecture and disclosures correctly. The helper established a verified source recovery point at the same commit while later Scene Search source drift was explicitly reported. Full commit-specific closure and recovery qualifications are in PUBLICATION.md; no fresh native measurement or human-review claim is added.
