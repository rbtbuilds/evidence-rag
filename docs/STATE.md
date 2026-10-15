# Evidence RAG state

Updated: 2026-10-15. State: all ten tasks implemented; final review fixes verified; refreshed model evidence and clean-checkout verification pending on feat/evidence-rag-v1.

## Verified during planning

- Read parent AGENTS.md, existing README.md, EVALUATION.md, .gitignore and LICENSE, plus the writing-plans skill.
- Directory initially held only README.md, EVALUATION.md, .gitignore and LICENSE. `git rev-parse --show-toplevel` failed with `fatal: not a git repository (or any of the parent directories): .git`.
- Primary source cards for BGE-small-en-v1.5, ms-marco-MiniLM-L6-v2 and Qwen2.5-0.5B-Instruct were read. Chosen capabilities/licences are documented in SPEC; exact immutable model revisions remain unresolved until execution.
- Parent probe reports uv Python 3.12.14 available, shell Python 3.14.7, Node 26.7.0, npm 11.19.0, no reserved-port listeners and no machine model lease at that time. Future execution must probe again.
- Created a concrete specification, ten-task native execution plan, child instructions and copyable handoff. Planning self-review checked all seven owned Markdown files for ASCII text, balanced code fences, Python-fence AST syntax and resolvable local Markdown links; all passed. The plan has ten tasks and 335 lines. A red-flag scan found no unresolved implementation markers or incomplete SQL/function placeholders. These are document checks only, not product tests.

- Read the parent-created docs/RELEASE-STANDARD.md and aligned Task 10 release files and evidence requirements. No parent-owned files were edited.

## Execution ledger

| Task | State | Evidence |
| --- | --- | --- |
| 1: Application shell | Complete | Health404 RED ->1pass GREEN; Ruff/Pyright strict0errors; TS strict/build pass; Python3.12.14,project-local Node24. |
| 2: Sessions/storage | Complete | 10 pytest pass, strict Pyright 0 errors; real cookies, CSRF, expiry/reset, rate limit and role denial. |
| 3: Corpus/version transactions | Complete | 24 owned versions, 72 frozen questions, validator passes; 5 chunk/version tests including injected SQL rollback and budget limit. |
| 4: Retrieval | Complete | Real FTS5, authorised dense cosine, deduplicated RRF and bounded rerank; fixture doubles labelled; access/rank invariance tests pass. |
| 5: Jobs/lifecycle | Complete | Import/replace/delete API, single worker, bounded jobs/cancel/recovery; staged-delete barrier and failed-build rollback pass. |
| 6: Local models | Complete | Pinned public snapshots downloaded/hash recorded; actual leased smoke 33.64s, 384 dimensions, 0 embedding truncations; JSON generation fails required schema and must abstain. |
| 7: Answers/citations/cache | Complete | 48 disclosure cells plus cache repeats, exact citations, malformed generation abstention, expiry and bidirectional publication/deletion barriers pass. |
| 8: Web interface | Complete | OpenAPI types plus Zod; 6 component/API tests; 2 real-browser flows, both themes at 360/900/1440, focus and contrast regression pass. |
| 9: Evaluation | Complete | Six frozen fixture/actual dev/test runs; all four methods, model hashes, paired metrics, 24-answer review sheets per block. Human review unmeasured. |
| 10: Full verification | Complete | 63 socket-restricted fixture tests, 8 web tests, 5 real browser scenarios; clean clone at a7dafa1 passes frozen setup, all checks and fixture evaluation. Fresh branch review follows. |

## Current limits and next action

The application is implemented and current local strict/offline/browser checks pass. Actual-model evidence is separate from fixture evidence; Qwen generation currently abstains on invalid output, and human citation support/completeness is unmeasured. The single fresh whole-branch review found four Important findings, all fixed with failing-then-passing regressions. Current checks: 73 Python fixture tests, 11 web tests and five real-API browser scenarios; strict checks/build/contracts pass. Next: retain refreshed evidence under heading-window-v2 and verify the new source commit in a clean checkout. Publication, push and deployment remain unauthorised.

## Native execution evidence

Task1: isolated Git root initialized on feat/evidence-rag-v1; baseline63df9d3. Installed locked project dependencies and project-local Node24 without global runtime changes. Health test failed404 then passed200. Doctor confirms FTS5. Ruff,strict Pyright(including tests),strict TypeScript and Vite production build pass. pytest temp is isolated under .runtime. Added httpx2 because current Starlette TestClient explicitly requires it.

Historical next step at Task1: Task2 server-side sessions, CSRF and transactional schema. No app servers or ML lease were owned then.

Task2: Session suite RED -> GREEN (successful login rate-limit regression corrected). 10 tests pass; strict Pyright 0 errors. Codes are mode0600 digests; session IDs hashed in SQLite. Next: corpus and transactional indexes.

Task3: corpus validator passes hashes, 12 document pairs, section word limits and disjoint family/template groups. Five focused tests pass; strict Pyright 0 errors. SQLite trigger failure proves old FTS and revision survive rollback. No model work performed.

Task4: retrieval/access tests RED missing modules -> GREEN. Fixture seeding now uses normalized hash embeddings. Four pipelines retain at most five authorized current chunks; revision mismatches refuse dense use. No actual models loaded.

Task5: real API lifecycle suite passes import, replacement, stale revision, deletion and absence of source marker across stored payloads/indexes. Eight pending jobs bounded; cancellation idempotent; running jobs interrupted on restart. Next: leased optional inference.

Task6: exclusive lease/ownership/timeout/RSS/malformed-output/missing-snapshot/queue tests pass. Public snapshots recorded in config/models.lock.json; CPU four-thread float32 worker exits before lease release. Actual smoke returned an unsupported citation_ids key and omitted insufficient_evidence: this is a real generation failure, not a valid answer. Task7 will enforce abstention. No resident model process or owned lease remains.

Task7: full Python suite 46 tests passes; strict Pyright 0 errors. Responses recheck session/role/epoch/current citations and cache only inside the publication lock. Deletion during generation returns 409 without source text; a blocked ASGI body holds deletion until full publication. Public prompt instructions cannot change access.

Task8: real browser verified login, question, current source and focus return; Escape restores delete opener. Visual review found dark secondary-button contrast 1.15:1; regression failed then passed after specificity fix. Strict TypeScript/build and six Vitest tests pass. Screenshots inspected; raw captures remain ignored.

Task9: metric tests RED -> GREEN. Six runs completed: fixture/extractive dev+test, local/extractive dev+test and local/Qwen dev+test. All actual embedding truncation counts zero; fixed Qwen output rejected on 96 dev and 192 test method/question outputs. Curated manifests and review sheets are in reports. No human support/completeness claim.

Task10 audit so far: full Python fixture suite includes access, staged budgets, safe logging, bounded model admission, source/chunk rebuild validation and metadata deletion. Actual-model matrix passed 96 serial HTTP-ASGI requests (1 test, 43.93s); a separate retry observed model_busy and did not steal the lease. Model preparation now reuses committed SHAs/file hashes without rewriting provenance. Browser Unicode code-point highlighting regression corrected.

Task10: clean-clone verification passed at a7dafa12a7915c38f8b149c12ade081a431b1c58 with 63 Python fixture tests, 8 web tests, 5 real browser tests, strict checks/build/contracts and frozen fixture evaluation. Runtime Node24.22.0, Python3.12.14, uv0.12.5. No public Git operation or deployment occurred. Post-hardening actual evidence refresh and the native workflow's one fresh whole-branch review remain before final sign-off.
