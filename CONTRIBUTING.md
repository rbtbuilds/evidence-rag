# Contributing

Use Python 3.12 and Node 24 LTS. Run `uv sync --frozen` and `npm --prefix web ci`, then `./scripts/check.sh`. Install the browser under the project runtime with `PLAYWRIGHT_BROWSERS_PATH="$PWD/.runtime/ms-playwright" npm --prefix web exec -- playwright install chromium`; `npm --prefix web run test:e2e` owns its temporary database and servers. Keep 8115 and 5115 free. The launcher refuses occupied ports and stops only processes it starts.

Keep changes scoped and include a failing regression before fixing behavior. Python and TypeScript checks include tests. Acceptance tests use the actual API and opaque sessions; do not intercept fetch or replace sessions with identity headers. Python tests deny outbound sockets and permit loopback/Unix sockets only. Dependency and browser installation are separate network-enabled setup steps.

`contracts/openapi.json` is exported from the app. After changing contracts, run `uv run python scripts/export_openapi.py` and `npm --prefix web run generate:types`; the check script rejects drift. Keep runtime Zod schemas aligned and reject unknown response fields.

All original code, documentation and fictional fixtures are MIT licensed. Models retain their own licences. Add no client documents, personal data, launch codes, model weights or local databases. Bulk reports stay in `.runtime`; inspect small curated evidence before adding it to `reports/`.

The evaluation split is frozen. Dataset edits require a new named corpus/evaluation revision, updated hashes and a clear explanation. Do not tune on held-out results. Keep generation settings fixed across retrieval methods, and keep fixture, actual-model and human-review evidence separate.

Heavy inference must acquire the shared machine lease. Read [RUNBOOK.md](docs/RUNBOOK.md) before model work. No hosted inference or paid compute is needed. Publication, push and deployment are separate maintainer decisions.
