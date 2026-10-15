# Evidence RAG state

Updated: 2026-10-15. Local v1 implementation and verification are complete on feat/evidence-rag-v1. Human citation review remains unmeasured. No publication, push or deployment occurred.

## Ownership and checkout

This repository is /Users/matthewgoralczyk/BentoLabs/portfolio/evidence-rag. Its Git root is the same directory; the fork's inherited resume workspace was not used. All ten approved tasks ran natively through superpowers:executing-plans in this chat. Only this child was edited. API/web ports are 8115/5115, loopback only. Model work used the shared atomic machine lease and exited its owned worker before release.

The baseline planning commit is 63df9d3ba709c63341aa279a821ce9610566db6c. Final application/source fix commit: 5ca23d349e79916a22fb084cf58a41c7bdcda0b6. Subsequent changes retain evidence and document verification. No Git remote is configured. The branch and checkout are preserved locally.

## Ten-task outcome

| Task | Outcome |
| --- | --- |
| 1: Shell | FastAPI health/profile, Python package, React/TypeScript/Vite shell, frozen dependencies and isolated runtimes. |
| 2: Sessions/storage | SQLite WAL migrations, hashed opaque sessions, role launch codes, CSRF, exact Origin/Host, expiry and atomic failed-login rate limit. |
| 3: Corpus/versions | 12 owned fictional manual pairs, 72 frozen questions, exact Unicode windows, unique heading anchors and atomic version publication. |
| 4: Retrieval | Role-partitioned real FTS5 BM25, authorised dense cosine, deduplicated RRF and lightweight reranking; four comparison modes. |
| 5: Lifecycle | Bounded single-worker import/replace/rebuild jobs, cancellation/restart handling, transactional deletion, stale-snapshot rejection. |
| 6: Models | Pinned public BGE/MiniLM/Qwen snapshots, hashes/licences, exclusive lease, bounded supervised CPU worker, four-item IPC batches. |
| 7: Answers/citations | Exact current-version source passages, strict generated-output validation, scoped bounded cache, final session/epoch/citation revalidation through complete response publication. |
| 8: Interface | Generated OpenAPI types and Zod validation, reader/maintainer workbench, both themes, source focus flow, retained pending jobs and explicit failed-draft recovery. |
| 9: Evaluation | Six measured fixture/actual dev/test runs, 864 method/question rows, paired metrics, provenance and three anonymised review sheets; human fields unmeasured. |
| 10: Verification | Strict checks, 73 fixture Python tests, 11 web tests, five real-API browser scenarios, clean checkout and a separate 96-request actual-model access matrix. |

## Exact verification

- `./scripts/check.sh`: Ruff passes; strict Pyright has zero errors/warnings; 73 Python fixture tests pass with one real-model test deselected and external sockets denied; strict TypeScript including tests/configs, 11 Vitest tests, production build, OpenAPI/type drift and corpus hashes pass.
- `uv run --extra ml python scripts/e2e_server.py`: five Chromium scenarios pass against the actual API on 8115 and web on 5115, with genuine sessions and no intercepted fetch. Includes access isolation, replacement, deletion, stale citations, literal HTML, job status across source navigation, both themes at 360/900/1440, contrast and keyboard focus.
- `./scripts/clean_clone_check.sh`: passed at source commit 5ca23d3 with frozen installs in a fresh venv/node_modules, all 73/11 checks, five browser scenarios and 192 fixture test evaluation rows. The task-owned temporary clone was removed by its scoped trap.
- `uv run --extra ml pytest -m real_model tests/integration/test_actual_disclosure.py -q -s`: passed 96 serial actual-model API requests covering two roles, four retrieval methods, both generation modes, cold/warm caches and active/replaced/deleted sources. Both restricted markers are checked throughout. This serial matrix makes no race claim.
- Deterministic fixture barriers cover simultaneous privileged/reader generation and separate warm caches for all methods, deletion during full rebuild, deletion during staged replacement and both answer-publication/deletion orders. Injection and transaction-failure tests verify stale work cannot publish.

All six final evaluation runs used clean source commit 5ca23d3 and heading-window-v2. The full raw report paths and hashes are retained in reports/evaluation-v2.json. No embedding truncation or dropped passage occurred. The original evaluation-v1 and review/smoke/matrix records remain unchanged. The strengthened access report is reports/actual-access-matrix-v2.json.

## Review and decisions

One fresh read-only whole-branch reviewer examined 63df9d3..cf846a6. No Critical finding; four Important findings closed in one author fix pass with failing-then-passing regressions: draft recovery, pending job/navigation state, unique section anchors and replacement-marker checks. The full suite then passed. No second reviewer was dispatched. All execution rulings, their costs and the deferred Minor are preserved in [REVIEW.md](REVIEW.md).

Deferred Minor: valid 120-character unbroken titles can overflow some mobile text containers. Existing viewport evidence covers normal fixture titles.

## Results and practical limits

All four actual retrieval methods achieved recall@5 1.0 on 36 eligible test questions per method. BM25 and reranked hybrid MRR were 0.9861; dense and hybrid MRR were 1.0. The small repetitive fictional corpus is an easy benchmark. Quotation mode correctly abstained on 8/12 expected-abstention cases per actual test method and can select irrelevant matching sentences.

Qwen failed the strict output/citation contract on all 96 development and 192 test method/question outputs. Every one abstained; no useful generated-answer quality is claimed. Exact quotations remain the default. Human citation support/completeness and screen-reader use are unverified. Hosted CI, production identity, public hosting, multi-process deployment, OCR/PDF/connectors, real customer data and forensic erasure were not exercised or promised.

Runtime: Python 3.12.14, project-local Node v24.22.0, uv 0.12.5, Apple M5 Pro. No global runtime/configuration, parent/sibling project, vault, operations record or archive was changed.

## Pickup

No implementation task remains from the approved ten-task plan. Start with [README](../README.md), [RUNBOOK](RUNBOOK.md), [VERIFICATION](VERIFICATION.md), [EVALUATION](../EVALUATION.md) and [reports](../reports/README.md). Human citation review can be completed separately using the three current review-v2 sheets. Any public repository creation, push, deployment, paid compute, model upload or external message still needs Matthew's specific authorisation.
