# Public source publication

Authorization: Matthew explicitly approved public `rbtbuilds/evidence-rag`, reviewed source/history push, `main` as default and hosted Actions on 2026-10-18. The child repository alone is published. No deployment, tagged release or weight upload is authorized or performed.

## Publication contract

- Exact quotations remain the application default even with local models installed. Native generation is visibly experimental and failed the frozen quality gate.
- Generation policy, access/version/deletion/cache/citation checks, frozen reports and null human-review fields are preserved. Citation resolution and quotation copying do not establish factual support or relevance.
- The public quickstart uses fixture search/embedding/reranking doubles separately from historical native-model evidence. Native checks are not rerun in this publication pass; no new tuning or model load is needed.
- Source, current/history heuristic secret scan, licences/provenance, relative links and media are audited. An independent automated review and strict tests must precede publication.
- Final commit, hosted CI, public rendering and helper-managed backup recovery checkpoints are recorded below after verification. A record cannot contain its own Git object hash; the final documentation closure is identified by the public `main` ref and exact hash in the completion receipt.

## Execution evidence

Preflight: authenticated GitHub account `rbtbuilds`; target repository returned 404; local root verified, clean feature branch at `7175c77ea9b1dbcc82b75e6884efdbff1ff7672c`, no remote. Heuristic scan: 232 tracked files, 414 historical blobs, zero token/path matches, 56 local file links resolve, all 24 earlier reports hash-preserved. This is not comprehensive secret or licence clearance.

The scope and limitations of retained demo media and model quality remain in [PUBLICATION-AUDIT.md](PUBLICATION-AUDIT.md), [PROVENANCE.md](PROVENANCE.md) and [QUALITY-RESULTS.md](QUALITY-RESULTS.md).


## Independent automated review and author fix

CodeRabbit CLI 0.7.5 (installed Homebrew distribution, authenticated free account) rejected the full 221-file range because of its 150-file limit. Its rejection is not a clean review and no paid credits were used. A separate fresh-context AI reviewer (GPT-6 Astra, xhigh) reviewed the whole application and staged publication changes, with read-only access and no source edits. This is automated AI-assisted review, not human sign-off.

The reviewer found one Important issue and no Critical issues: cancellation before process creation could allow a later model worker to start and hold the lease despite job cancellation. A harmless subprocess/private-lease barrier reproduced it independently. The author added a failing deterministic regression, then synchronized cancellation state with process creation. Cleanup joins workers before releasing leases and does not count normal session completion as cancellation. Twenty runner/lease/job regressions passed after the fix. Generation policy, decoder and frozen data/reports were not changed; historical native results predate this resource-management fix.

The reviewer separately ran 47 focused tests and a heuristic scan of 235 tracked files/427 historical blobs, finding no selected secret-pattern or forbidden-artifact matches; all 24 preserved reports matched hashes. It inspected sessions/CSRF/Host, role-filtered retrieval, final publication gates/cache, atomic lifecycle, Unicode citations, source escaping, experimental labels and upstream notice.

Review limits explicitly accepted: human factual quality, screen-reader accessibility, comprehensive legal compliance, arbitrary private-secret absence and full-frame media clearance remain unmeasured/unproven. The reviewer did not load native models or independently exercise fresh-clone/browser/hosted CI/public rendering; separate executor checks cover those actually run. No deferred Minor findings were reported.

The author fix passed the full non-model gate: Ruff, strict Pyright zero errors/warnings, 126 Python tests (2 native deselected), strict TypeScript including tests, 13 web tests, production build, contracts and corpus. The regression uses harmless subprocesses and a private lease, not real weights or the shared machine slot.
