# Evidence RAG evaluation design

Status: planned evaluation. No results have been measured.

## Baseline and split

Compare lexical, dense and hybrid-reranked retrieval with generation fixed. Use a fictional owned corpus and independently authored questions: supported, unsupported, conflicting versions and restricted content. Hold out document sections and question templates. Evaluate retrieval before model generation so an answer error can be attributed to the correct stage.

## Measurements

Report retrieval recall at K, reciprocal rank, citation support precision, answer completeness and correct abstention. Audit citation support manually on a labelled subset rather than relying only on an LLM judge. Track latency by stage, model cost where used and document update visibility. Report access-boundary tests separately from average answer quality.

## End to end scenario

Import manuals, ask a supported question and open its cited passage. Switch to a user without appendix access and attempt the same restricted query, including after a privileged user's cache has warmed. Replace the manual, then delete it; verify retrieval, citations and caches respect the active version and removal. Inject instructions into a source passage and verify that they cannot grant access or override tool permissions.

## Release evidence

Save corpus provenance, version manifest, permission fixtures, question set, model and index revisions, baseline comparison and a deletion/update runbook. Zero cross-user disclosure in the stated regression matrix is a release gate; do not generalise it into a claim of formal security proof.

## Concrete v1 protocol

The [specification](docs/SPEC.md) fixes four pipelines: BM25, dense cosine, hybrid reciprocal rank fusion, and hybrid plus MiniLM reranking. Use the same current corpus, authorised candidates, chunks, K=5 and fixed generation configuration in each comparison. Extractive generation and actual Qwen generation are separate report blocks; deterministic fixture embeddings/reranking validate plumbing only.

Use 72 owned questions: 24 development and 48 frozen test, partitioned by section family and question template. Test strata contain 24 supported, 8 unsupported, 8 conflicting-version and 8 restricted questions. Relevant section IDs and atomic expected facts are labelled before evaluation. Record corpus/questions/model/prompt hashes and actual sample counts. Deduplicate repeated chunks of a section when scoring recall@5 and reciprocal rank. Report per-role/stratum metrics and paired differences with seeded bootstrap confidence intervals.

Review 24 test answers manually, balanced across methods (6 per method: 3 supported, 1 unsupported, 1 version conflict, 1 restricted), with method labels hidden. Citation support and completeness remain unmeasured until this review occurs. Valid citation IDs alone do not establish factual support.

Access gates are separate from quality averages: both roles, all four retrieval modes, cold and warmed caches, active/replaced/deleted sources, forged identity headers, source instructions, guessed citation/job IDs, and mutations during in-flight generation/rebuild. No forbidden-string disclosure, every emitted citation resolving to an authorised active version, and no stale answer cache after a completed mutation are release requirements. They are regression results over this matrix, not a general security proof.

Run offline fixture evaluation in CI; execute actual models only with pinned local snapshots and the shared machine lease held for the full benchmark. Keep small reviewed reports under `reports/` and raw runs under ignored `.runtime/`. As of planning, every measured metric and reviewer field is absent.
