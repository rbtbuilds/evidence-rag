# Evidence RAG build-chat handoff

This is an independent project. Plans are complete; no application, dependency installation, Git repository, model run or benchmark existed at handoff. A fork may inherit `/Users/matthewgoralczyk/Desktop/BentoLabs/resume`; the prompt below deliberately anchors every operation to this child. Paste the entire block into the fork to authorise execution.

```text
Matthew, implement Evidence RAG v1 in /Users/matthewgoralczyk/BentoLabs/portfolio/evidence-rag using the completed specification and plan.

Before writing anything, set every shell tool workdir explicitly to /Users/matthewgoralczyk/BentoLabs/portfolio/evidence-rag and prove it with pwd. A fork can inherit the resume workspace and its desktop Git panel; do not edit or commit that workspace. Read /Users/matthewgoralczyk/BentoLabs/portfolio/AGENTS.md, /Users/matthewgoralczyk/BentoLabs/portfolio/evidence-rag/AGENTS.md, CHAT-HANDOFF.md, README.md, docs/SPEC.md, EVALUATION.md, docs/superpowers/plans/2026-10-15-v1.md and docs/STATE.md. Read docs/RELEASE-STANDARD.md if present. Inspect actual files, Git root/status, runtime versions and listeners; documentation is not proof of implementation.

Use the native superpowers:executing-plans skill and carry out the ten tasks in this chat. The product and design choices are settled in SPEC; do not repeat discovery or ask for the execution method again. Do not create an automatic subagent cascade, new chats or monitors. Reversible local implementation, dependency preparation, testing and scoped local commits are authorised. If Git is still absent, git init only this child on branch feat/evidence-rag-v1; inspect existing Git state instead if it has appeared. Do not change global configuration or touch siblings/parent coordination files.

Use Python 3.12 with uv, Node 24 LTS where available, API 127.0.0.1:8115 and web 127.0.0.1:5115 with strictPort and the exact origin. Verify runtime compatibility and record actual resolved dependency/model revisions. Implement the specified role-partitioned FTS5 BM25, dense cosine, RRF, lightweight reranking, loopback demo sessions, current-version citations, transactionally published lifecycle changes and response revalidation. Do not trust client role headers, substitute fixture results for model evidence, or claim production authentication.

Each project owns its .venv, web/node_modules, .runtime database and model cache. Before loading weights or performing actual model evaluation/heavy indexing, atomically acquire /tmp/bentolabs-portfolio-ml.lock using the specified owner record. A busy lease defers dependent heavy work; continue light work without deleting another owner's lock. Terminate/unload the model worker before releasing your own lease. No resident model server runs outside the lease, and the full benchmark holds it throughout.

For each task run meaningful tests and strict checks including test files, record exact results in docs/STATE.md, inspect the diff and commit locally if identity is already configured. Finish the actual browser-to-API flow and clean-clone runbook checks. Report actual model evaluation and human citation review separately; leave missing evidence explicitly open. Complete all independent work if a model download or resource is unavailable. Stop for a real scope change or destructive action only. Public GitHub creation, push, release, deployment, external sends, model uploads and paid compute are not authorised by this prompt.

Finish with the implemented behaviour, exact verification outcomes, evidence paths, limitations and remaining decisions. The first word of every reply must be Matthew.
```

The default fixture application can be completed offline after dependency installation. Real model preparation uses public model downloads explicitly, with child-local snapshots and checked licences; no hosted inference service is required. Actual benchmark results must remain absent until measured.
