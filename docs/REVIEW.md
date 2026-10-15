# V1 whole-branch review and decisions

A fresh read-only reviewer examined baseline 63df9d3 through cf846a6 using the approved specification, plan, five review focus areas and native ledger. The reviewer did not run tests or load models. Its verdict was "With fixes": no Critical findings, four Important findings and one Minor finding. The author accepted those grades and made one fix pass, with no second reviewer.

## Important findings closed

1. Failed asynchronous import/replacement drafts were inaccessible. A submitted draft and its original target revision now remain in session memory until success or a later submission. Edit/retry draft restores the inputs after failure, cancellation or interruption. Import/replacement component regressions failed before the action existed, then passed, including revision preservation.
2. Another job or citation navigation lost the prior job control. The browser now admits one pending job, keeps the workbench mounted during source navigation, and permits explicit cancellation. The pending-job component regression failed before submission controls were blocked, then passed. The real-API browser lifecycle test failed when navigation discarded job state, then passed with retained status.
3. Repeated headings mixed with suffixed headings collided. Anchors now check every previously allocated anchor, with a nonempty fallback. heading-window-v2 separates the changed identifier scheme. Unit uniqueness and source-section boundary regressions failed first, then passed.
4. Replacement disclosure checks missed the new restricted marker. Both matrices use the same guard over both restricted markers for every reader response and for both roles after deletion. The actual report derives its disclosure field from the guard. Deliberately injected replacement-marker responses escaped the original matrix (three failing mutation checks), then were caught after the fix. This was a validation gap; no runtime leak was observed.

The fix pass also added deterministic simultaneous reader/maintainer generation and warm-cache isolation checks for all methods, plus deletion during a blocked full rebuild. These passed without a production-code change. The complete strict fixture suite passes: 73 Python tests and 11 web tests; all five actual browser-to-API scenarios pass.

## Rulings, in decision order

- Include interrupted as a sixth job state. The lifecycle/recovery contract requires it despite the older five-state SQL list. Cost if wrong: an additional public state.
- Install Node 24 inside this project because no suitable existing manager/binary was found. Cost if wrong: local disk and installation time; no global runtime changed.
- Keep pytest temporary output under .runtime and use httpx2 for the installed Starlette TestClient. Cost if wrong: disposable local output and one development dependency.
- Introduce the real-API browser launcher during Task8 rather than Task10 so interface acceptance runs end to end. Cost if wrong: test-helper sequencing only.
- Continue light independent development during leased evaluation. Cost if wrong: latency contamination; all timings are labelled local development measurements.
- Keep production identity, public hosting, TLS and multiple processes outside this single-process loopback application, as approved. Cost if wrong: unsafe operation if exposed outside its documented boundary.
- Logical deletion does not promise forensic erasure or retract material already delivered to a browser. Cost if wrong: residual disk/WAL/backups or previously seen content remain recoverable.
- Public fictional fixture constants are separate from access to mutable runtime sources. Runtime checks still apply. Cost if wrong: this demonstration cannot establish confidentiality for real data.
- Keep enterprise generalization and a minimum Qwen quality threshold outside acceptance; report the synthetic corpus and failed generation contract explicitly. Cost if wrong: generated answers remain unusable and measured recall may not generalize.
- Keep OCR/PDF, external connectors, agent tools, fine-tuning and customer workloads outside v1. Cost if wrong: those broader workflows are absent.

## Deferred minor

A valid 120-character unbroken title can overflow some mobile text containers. Existing viewport checks cover ordinary fixture titles. This is recorded for a later focused layout change, following the native execution rule to defer Minors from the final fix pass.

Human citation support/completeness and screen-reader usability remain unverified. Review does not convert them into passing evidence. Refreshed actual-model evidence and clean-checkout outcomes are recorded separately in STATE and VERIFICATION after execution.
