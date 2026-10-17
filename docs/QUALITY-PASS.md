# Grounded answering pass v1

Acceptance fixed on 2026-10-17 before opening the new challenge. The existing
48-question test has been exposed; it is regression evidence only.

## Acceptance criteria

- Existing test, four methods: 48/48 explicit proper refusals (baseline 46/48),
  at least 116/144 answerable responses (baseline 109/144), zero invalid outputs.
- New 24-case challenge, four methods: at least 95% proper expected refusals,
  at least 85% oracle-verified complete useful answers among answerable cases,
  zero non-abstained answers outside the frozen support/completeness oracle.
- Zero forbidden disclosures, 100% accessible current citation resolution,
  passing access, lifecycle, cache and publication-order regressions.
- Strict Python/TypeScript checks including tests, complete fixture browser
  flow, actual API/browser generation and clean-checkout verification.

The narrow full-answer oracles are conservative automatic checks. Rejection
means not verified by that oracle, not necessarily factually false. They do not
establish general semantic entailment. Human metrics remain unmeasured.
Challenge authoring uses a separate clean-context AI author and reused fictional
source documents. It is neither human-reviewed nor statistically independent.
Authorship exposure and frozen hashes belong in the dataset manifest.

## Bounded procedure

Freeze inputs/oracles before final evaluation. Develop on development cases
only, with at most two substantive prompt/model/grounding iterations. Record
each iteration before running it. Then freeze source and run one final paired
evaluation of baseline and candidate on the challenge, plus the unchanged
existing regression. Never tune after opening final outputs. If any acceptance
gate fails, retain exact quotations as the default and report the miss.
The default remains quotations throughout this pass.

## Recovery point

The installed helper is `~/.local/bin/bl-project`, backed by
`~/.claude/scripts/bl-project.sh`. Its registered unit is the parent portfolio;
Matthew explicitly authorized this parent backup. No sibling source was edited.

The first full copy ended with exit 23 after a live sibling browser output
vanished. A deep read-only retry was stopped before mutation to avoid redundant
runtime scans. A normal retry correctly reported live sibling database/docs
drift. A task-owned supported project filter then excluded ignored runtimes,
browser output and itself; a tracked-file audit passed for 10 repositories.
Normal helper sync succeeded, followed by `bl-project verify portfolio`:
`identical (excludes aside)`. The unchanged temporary filter was removed.
Existing archived runtime copies were protected, not deleted. They are not
claimed to be transaction-consistent backups of live sibling databases.

Recovery copy: `/Volumes/BentoLabs/portfolio/evidence-rag`, Git HEAD
`d01f3d723e19634e194a8af9ca22ebecfeacd878`. Read-only `git fsck --full` passed;
SHA-256 comparison matched all 194 tracked files. The helper preserved overwritten
volume files under its portfolio archives at `20261017-212026`,
`20261017-212215` and `20261017-212222`. No ad hoc archive transfer occurred.

## Execution ledger

- Pre-flight: generation policy -> cache prompt revision: bump together.
- Pre-flight: challenge manifest -> scorer/runner: validate hashes before use;
  keep reference answers and oracles out of model requests.
- Pre-flight: baseline prompt -> paired evaluation: retain its exact system
  text, model/dependency locks, context and decoder settings.
- Ruling: stay in the expressly owned checkout, use runtime-scoped execution
  bookkeeping, and perform final code review before frozen evaluation. This
  prevents review fixes from consuming another final run. Cost if wrong:
  documentation-only final changes receive an author audit rather than a
  second code-review cycle.
- Task 2 RED: native six-pair regression failed on the exposed quoted-request
  case (24.25 seconds); five other pairs passed. Unit scorer/adapter tests failed
  before their modules existed, then passed 4/4. Raw logs are runtime-private.
- Iteration 1 begins: clarify stated fictional facts, missing values, quoted
  requests versus quotation questions, and current-fact corrections. One-pass
  generation, unchanged model/decoder/limits and public validation. No challenge
  content or output has been opened by the implementer.
- Development iterations used: 1/2. Final evaluation: not started.

## Final evidence

Pending execution; no quality improvement or publication readiness is claimed.
