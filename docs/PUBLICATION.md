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


## Published application checkpoint

Public URL: https://github.com/rbtbuilds/evidence-rag . Default branch: `main`.
Reviewed application commit: `7213efc3b99e6b9f3248bbd1cd490d39d4a46893`. All earlier source history is retained; no force push or history rewrite occurred. HTTPS initially rejected workflow publication because the existing OAuth credential lacked workflow scope. The already configured SSH key authenticated as the same owner and published the full history without changing credential scopes.

[Hosted fixture CI](https://github.com/rbtbuilds/evidence-rag/actions/runs/39137272692) completed successfully at exactly `7213efc3b99e6b9f3248bbd1cd490d39d4a46893`: 126 Python tests (2 native deselected), 13 web tests, strict checks including test files, build/contracts/corpus, 5 real-API browser passes (1 native scenario skipped), and 192 fixture evaluation rows. The fixture job took 1 minute 16 seconds. Native checks and known failed semantic tests were deliberately not rerun; no new native claim or tuning occurred. GitHub's ubuntu-latest migration annotation is retained in local logs; this is evidence for the executed image, not a promise that future hosted images never change.

`./scripts/clean_clone_check.sh` passed at the same application commit on this Mac, including frozen installs, init/seed, full checks, browser lifecycle and fixture evaluation. A separate anonymous HTTPS public clone with the README's exact branch/URL also passed frozen Python/web installation, init, seed, doctor and Git fsck. Temporary clones were removed. Local Node 24/Chromium support was used; hosted CI supplies the separate Linux check. Log SHA-256: `597d00ea0a99399036d5e4b9b6573ededaec06faa53ad01ce728a96a2889662d`.

Anonymous HTTP returned 200 for the repository, README, screenshot and MP4; downloaded media matched local hashes. GitHub's rendered README was inspected with AI assistance, including the screenshot, clone instructions, native experimental disclosure, quality tables and rendered Mermaid architecture. The MP4 is served as application/octet-stream and is presented as a downloadable demo. No hosted application, tag, release or model-weight upload was created.

Current/history heuristic scan at the application checkpoint: 235 tracked files, 431 reachable historical blobs, zero selected token/path matches, 64 existing local Markdown references and all 24 older report hashes preserved. Source/model/oracle/criteria and all frozen report files are unchanged from the prior quality pass except the resource-management fix explicitly recorded above. The new experimental-label UI and tests do not change generation policy. These checks do not establish arbitrary-secret absence, legal clearance, semantic correctness or human review.

## Portfolio recovery checkpoint

Matthew explicitly authorized helper-managed portfolio-wide backup. Current helper `~/.local/bin/bl-project` resolves to `~/.claude/scripts/bl-project.sh`; its installed help and sync/audit/verify/filter implementation and prior QUALITY-PASS procedure were read. Supported temporary `.bl-filter` exclusions cover child `.runtime`, web test output, Playwright reports and the task-owned filter itself. No tracked source matched these exclusions; prior excluded archived runtimes are protected rather than deleted. No ad hoc copy/move/rsync, forced warnings, deactivation, sibling source edits or process stops were used.

Commands: `bl-project sync portfolio --dry-run`, `bl-project audit portfolio`, `bl-project sync portfolio`, `bl-project verify portfolio`. The audit found no missing tracked files in 11 discovered repositories (including ignored runtime checkout metadata). The source inventory separately covers the four active source repositories outside runtime trees.

The source sync passed its immediate verification and preserved 53 overwritten/deleted destination files through the helper's recovery snapshot `/Volumes/BentoLabs/_archive/portfolio/20261018-164539`. The Evidence RAG recovery copy at `/Volumes/BentoLabs/portfolio/evidence-rag` has Git HEAD `7213efc3b99e6b9f3248bbd1cd490d39d4a46893`; all 235 tracked files match SHA-256 and local/archive Git fsck passed. Git fsck reports harmless dangling blobs, with no integrity failure. Earlier `d01f3d723e19634e194a8af9ca22ebecfeacd878` history and helper snapshots remain recoverable.

Across the four source repositories, all 946 tracked working-tree hashes in the pre-sync inventory matched the archive. Inventory SHA-256: `b7a9032f6abc2c96af0554c7157411093eb2e7fbf885c048f1418d53621208ec`. Scene Search was dirty at its recorded commit `1e61448545ed7259135f225a9290e720ad44668d`; its hash inventory is private runtime evidence, not a claim that its working copy was committed. A later whole-portfolio content verification returned differences for new Scene Search jobs/retrieval/worker files, settings changes and directory timestamps; Evidence RAG source remained verified. This is an explicit source recovery point, not zero global drift or a transaction-consistent database backup.

## Documentation closure and final receipt

This record's final documentation commit is identified by `git log -1 --format=%H -- docs/PUBLICATION.md` on public `main`. Its exact hosted result is discoverable through the [main fixture workflow](https://github.com/rbtbuilds/evidence-rag/actions/workflows/ci.yml?query=branch%3Amain) or `gh run list --repo rbtbuilds/evidence-rag --commit <that-commit>`.

After that documentation commit passes CI, the helper refreshes and verifies the archived current source again. A local Git publication note attached to that exact final commit records its full hash, exact CI run URL and verified backup receipt without creating a self-referential documentation commit. Read it with `git notes --ref=publication show HEAD`. The helper also archives this note; it is local recovery metadata, not an additional public branch or model artifact. The final completion receipt reports any remaining sibling drift and filter cleanup exactly.

Remaining limitations: failed native grounding/coverage gate, frozen finite-oracle false negatives, known native completeness failures, possible quotation irrelevance, loopback-only demo authentication, one API process and no forensic deletion promise. Human support/completeness, screen-reader accessibility, broad generalisation and customer outcomes remain unmeasured. All review and visual inspection claims here are AI-assisted.
