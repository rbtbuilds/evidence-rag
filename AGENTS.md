# Evidence RAG execution instructions

Read `/Users/matthewgoralczyk/BentoLabs/portfolio/AGENTS.md` first; its ownership, resource, publication and runtime rules apply. This chat owns only `/Users/matthewgoralczyk/BentoLabs/portfolio/evidence-rag`. The first word of every user-facing reply is `Matthew`.

## Entry and authorisation

V1 implementation and verification are recorded in docs/STATE.md; inspect actual state before continuing. Before any write, explicitly set the shell workdir to this directory, prove it with `pwd`, and read CHAT-HANDOFF.md, README.md, docs/SPEC.md, EVALUATION.md, docs/superpowers/plans/2026-10-15-v1.md and docs/STATE.md. Inspect files, Git root/status and listeners before acting. A fork may still display the resume workspace; do not use its Git panel for these files.

Matthew's pasted execution prompt authorises reversible local implementation, checks and scoped local commits. Use `superpowers:executing-plans` natively in the current chat. Do not repeat settled discovery or automatically create subagents, other chats or monitors. Do not implement during the planning pass. Public repositories, pushes, deployments, uploads, external sends and paid use require specific authorisation.

No Git repository was present during planning. If still absent, initialise only this child with branch `feat/evidence-rag-v1`. If Git exists, inspect its root, branch and changes and preserve unrelated work. Never initialise the parent, alter global Git settings or assume desktop app checkout controls target this child.

## Non-negotiable application rules

- API 8115, web 5115, loopback only, one API process, exact web origin and strictPort. Identify a port owner before changing ports or stopping anything.
- Python 3.12 through uv; Node 24 LTS for CI. Pin actually resolved dependencies. Strict Pyright and TypeScript checks include tests and config files.
- Use server-side opaque demo sessions from printed per-role launch codes. Client user/role headers are not credentials. Describe this as loopback demo authentication.
- Enforce role/current-version access before scoring, reranking/generation and source opens; recheck session/citations/epoch at final response publication. Role-specific FTS tables prevent hidden corpus statistics affecting reader ranking.
- SQLite publishes versions, chunks, vectors, FTS and cache invalidation in one transaction. Delete cancels staged jobs and removes source bodies from application storage. Never let a late worker restore deleted data.
- Fixture mode uses real FTS5 but deterministic embedding/reranking doubles and extractive quotations. Label it. Actual model evidence uses pinned local snapshots with recorded hashes and fixed generation settings.
- All mutable runtime files and caches are private to this directory's `.runtime/`. No private documents, client material or sibling data enters the corpus.
- Acquire `/tmp/bentolabs-portfolio-ml.lock` atomically before any model load/heavy evaluation. Do not hold resident weights after release. Busy means defer only that work; do not replace a real run with fixtures silently.

## Execution and evidence

Gather, decide, execute, verify. Read changed files and relevant consumers/tests first. Follow the concrete tasks in order; update STATE with task, exact checks, outcome and next action. Source/code punctuation is ASCII. Use the SPEC's design system and an available design skill before UI work; review both themes, keyboard use and small screens at the end.

Run changed flows through the actual API and browser, not only mocks or type checks. Keep access/lifecycle regressions separate from quality averages. Do not claim manual citation review, real-model performance or clean-clone reproducibility until those checks happened. Review delegated changes before integration if Matthew later requests delegation.

Read `docs/RELEASE-STANDARD.md` if present before final sign-off. Parent coordination records belong to the parent; report needed changes without editing them. Do not update the Obsidian vault or operations records from this isolated project task without the applicable owner workflow.
