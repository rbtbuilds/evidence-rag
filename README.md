# Evidence RAG

A document question-answering application that shows exactly which document version supports an answer and prevents retrieval across user access boundaries. The demonstration corpus is a fictional equipment service manual with revisions and restricted appendices.

Status: proposed project. This repository contains a project brief and evaluation design; it has no running retrieval application.

## What it demonstrates

Hybrid retrieval, reranking, citation evaluation, access control and document lifecycle handling. [Mistral's applied AI role](https://jobs.ashbyhq.com/mistral.ai/4c57adc5-5beb-49d2-9202-1db0807b9cb7) names advanced retrieval use cases. [OpenAI's FDE role](https://openai.com/careers/forward-deployed-engineer-london-london-uk/) supplies the delivery context. Authorisation and version handling are the proposed project's engineering focus.

## First release

Import a small owned corpus, sign in as one of two local demo users and ask a question. Return an answer with passage-level citations and visible version dates. Mark superseded guidance and unsupported questions clearly. An administrator can replace or remove a document and verify that it disappears from retrieval and caches.

Compare lexical retrieval, dense retrieval and a hybrid with reranking. Keep the reader interface simple: question, answer, cited passages and document viewer. This is a distinct public retrieval experiment, not a copy of an existing private town assistant.

## Proposed design

Document import -> version and permission metadata -> parsing and chunking -> lexical and vector indexes -> authorised retrieval -> reranking -> bounded generation -> citation viewer. Enforce access before retrieval and again when opening a citation. Scope caches to identity permissions and index version. Queue indexing work and expose its status.

Use Python for ingestion and retrieval, a transactional store plus an appropriate local search index, and a small web client. Keep APIs typed and record index and model versions. No particular database vendor or embedding service is committed before an offline feasibility check.

## Acceptance criteria

Citations open the actual supporting passage. A restricted appendix cannot leak through retrieval, answer text, snippets or cached responses. Replacing a manual changes the next answer and citation version; deleting it invalidates affected index entries and caches. The report isolates retrieval quality from answer generation quality.

## Scope limits

One fictional manual corpus, two permission roles and a local deployment first. No legal advice, client documents, broad enterprise connector catalogue or claimed real customer rollout. More retrieval is not assumed to improve answer quality; compare against the simplest baseline.

## Next implementation decision

Write the version and access rules alongside the test questions before implementing ingestion. See [evaluation design](EVALUATION.md).

## Licence

Original code and documentation: [MIT](LICENSE). Third-party datasets, models and media retain their own terms.

## Completed implementation plan

The v1 planning package now settles the earlier open design choices: Python/FastAPI, SQLite FTS5 with role-specific indexes, local dense vectors, RRF and reranking, opaque loopback demo sessions, atomic lifecycle changes, and a React interface. The repository still contains documentation only; no application or results exist yet.

- [Specification and acceptance criteria](docs/SPEC.md)
- [Ten-task implementation plan](docs/superpowers/plans/2026-10-15-v1.md)
- [Copyable fork execution prompt](CHAT-HANDOFF.md)
- [Project execution instructions](AGENTS.md)
- [Actual state and next action](docs/STATE.md)

Start the future build with the complete handoff prompt. It explicitly selects native execution in this child directory, and avoids accidentally building in a fork's inherited resume workspace.
