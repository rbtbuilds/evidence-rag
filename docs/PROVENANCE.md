# Licence and provenance

Original application code, documentation, fictional Aster manuals and authored
question/oracle sets use the repository's MIT licence, copyright 2026 Matthew
Goralczyk. Development and review were AI-assisted. The fictional trainer is a
software demonstration, with no real machinery procedures or customer records.
No customer impact, human usefulness score or human factual review is claimed.

The quality-v1 questions and oracles were authored by a separate clean-context
AI agent from the original source documents. Its limited exposure to aggregate
historical results in required guidance is disclosed in the frozen dataset
README/manifest. It did not consult individual model outputs or implementation
changes. Reused source context and related facts prevent statistical-independence
claims. All original frozen reports are preserved by SHA-256 in
`reports/quality-v1-preservation.json`.

## Third-party model assets

| Purpose | Snapshot | Revision | Terms |
| --- | --- | --- | --- |
| Embedding | BAAI/bge-small-en-v1.5 | 5c38ec7c405ec4b44b94cc5a9bb96e735b38267a | MIT |
| Reranking | cross-encoder/ms-marco-MiniLM-L6-v2 | 233902d25c440f23af6f7d6e94d2946bac0bee0a | Apache-2.0 |
| Optional native generation | mlx-community/Qwen3-14B-4bit | a4d9b2df59d2c150bef02fcbe0d91046b7ca33a4 | Apache-2.0 |

The generator is a four-bit/group-64 conversion of Qwen/Qwen3-14B. Full file
hashes, preparation paths, model-card hashes and backend identities are in
`config/models.lock.json`. Local preparation downloads only public pinned
assets; inference uses local files with remote code disabled. Model weights,
download caches and downloaded model cards are excluded from Git. The MIT
code licence does not relicense those assets. Historical candidate models and
their failures are documented separately; they are not automatic fallbacks.

Python and web dependency versions are frozen in `uv.lock` and
`web/package-lock.json`. Third-party dependencies retain their own terms.
No third-party application implementation, client material, private source
documents, model weights or credentials are included in the intended release.

Browser demo assets, when explicitly retained, depict this application's owned
fictional data. Authentication codes are entered outside the recorded browser
context; cookies are transferred in memory and never retained as a release
artifact. Capture/encoding commands, asset hashes and visual inspection belong
in the publication audit. A demo is evidence of the shown local path, not a
customer deployment or broad quality validation.
