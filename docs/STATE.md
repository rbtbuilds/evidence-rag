# Evidence RAG state

Updated: 2026-10-15. State: implementation in progress on feat/evidence-rag-v1.

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
| 5: Jobs/lifecycle | Not started | Transaction/race contract only |
| 6: Local models | Not started | Cards verified; no downloads, weight loads or benchmarks |
| 7: Answers/citations/cache | Not started | No implementation |
| 8: Web interface | Not started | Design specified, no rendered UI |
| 9: Evaluation | Not started | No measured metrics or human review |
| 10: Full verification | Not started | No application checks or clean-clone evidence |

## Limits and next action

No tests, strict type checks, browser flow, model readiness check or quality benchmark can be reported as passing: no product has been implemented. Python/Node/dependency compatibility, exact model SHAs, observed memory/latency and quality are execution evidence, not planning assumptions. Human citation support/completeness review is pending and cannot be inferred from valid citation IDs.

Next action: Matthew pastes CHAT-HANDOFF.md's prompt into the intended fork. Execute Task 1 after rereading the actual state. Required local branch if Git remains absent: `feat/evidence-rag-v1`. No public repository, push, deployment or paid usage is authorised.

## Native execution evidence

Task1: isolated Git root initialized on feat/evidence-rag-v1; baseline63df9d3. Installed locked project dependencies and project-local Node24 without global runtime changes. Health test failed404 then passed200. Doctor confirms FTS5. Ruff,strict Pyright(including tests),strict TypeScript and Vite production build pass. pytest temp is isolated under .runtime. Added httpx2 because current Starlette TestClient explicitly requires it.

Next: Task2 server-side sessions,CSRF and transactional schema. No app servers or ML lease owned.

Task2: Session suite RED -> GREEN (successful login rate-limit regression corrected). 10 tests pass; strict Pyright 0 errors. Codes are mode0600 digests; session IDs hashed in SQLite. Next: corpus and transactional indexes.

Task3: corpus validator passes hashes, 12 document pairs, section word limits and disjoint family/template groups. Five focused tests pass; strict Pyright 0 errors. SQLite trigger failure proves old FTS and revision survive rollback. No model work performed.

Task4: retrieval/access tests RED missing modules -> GREEN. Fixture seeding now uses normalized hash embeddings. Four pipelines retain at most five authorized current chunks; revision mismatches refuse dense use. No actual models loaded.
