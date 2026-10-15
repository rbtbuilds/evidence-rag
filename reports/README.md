# Recorded evaluation evidence

[evaluation-v3.json](evaluation-v3.json) retains summaries and raw-report SHA-256 hashes for six completed runs: development/test for fixture quotations, actual local quotations and actual local Qwen generation. All 864 method/question rows use clean source e3823ce2a47d78b336aa0b6476c663f0b3206d6e. Model file hashes/revisions remain in [models.lock.json](../config/models.lock.json); the dependency lock hash, generation policy, machine, source/question hashes, counts, per-role/stratum metrics and paired bootstrap intervals are recorded per run.

| Split | Accepted answers | Insufficient evidence | Invalid output | Citations resolved | Output-limit hits | Correct expected abstentions |
| --- | --- | --- | --- | --- | --- | --- |
| Development | 83/96 | 11 | 2 | 160/160 | 2 | 2/24 |
| Test | 183/192 | 2 | 7 | 347/347 | 9 | 1/48 |

The repaired local Qwen block accepted 183/192 test answers, returned 2 insufficient-evidence abstentions and rejected 7 invalid outputs. All 347/347 emitted citations resolved to accessible current passages; 9 outputs hit the 256-token budget. Expected-abstention decisions were correct in 1/48 method/question cases. The sole correct test expected-abstention decision came from invalid-output rejection; no explicit insufficient-evidence response correctly handled an expected-abstention case. This measures format/citation validity and abstention, not factual support or completeness.

Development: 83/96 answers accepted, 11 insufficient-evidence abstentions, 2 invalid outputs, 160/160 citations resolved and 2 output-limit hits. No forbidden marker disclosure, embedding truncation or passage dropping occurred across the six blocks. Format/citation validity does not measure factual entailment. Qwen still answers unsupported questions incorrectly. Exact quotations remain the default and correctly abstained on 8/12 expected-abstention test cases per actual method.

Fixture vectors/reranking are deterministic doubles; real FTS5 is used in every profile. Actual runs loaded pinned BGE/MiniLM/Qwen in a leased CPU worker with four threads. Timing uses warmed models and cold answer caches; index/load/decode warmup is separate. Light development ran concurrently. Interactive uncached requests can reload weights; these are local development timings, not cold-start or isolated hardware measurements.

The three `review-v3-*-test-*.json` files are new anonymised 24-answer review sheets. Each selects six answers per method across the frozen strata; keys stay in ignored raw-run directories. Reviewer/date/support/completeness remain null. No human review or substitute model judge is claimed.

[actual-access-matrix-v3.json](actual-access-matrix-v3.json) records 96 serial actual API requests: both roles, four retrieval methods, both answer modes, cold/warm caches and active/replaced/deleted sources. Both restricted markers are checked for readers throughout and for all roles after deletion. Fixture barriers establish race ordering separately. [local-smoke-v3.json](local-smoke-v3.json) records actual embedding, reranking and valid Qwen smoke output with decoding settings.

Original evaluation-v1/v2, review sheets, smoke and access reports are retained unchanged. The v2 baseline rejected every one of its 96 development and 192 test Qwen outputs, including a smoke with the wrong citation key and missing flag. [Generation repair](../docs/GENERATION-REPAIR.md) records development-only diagnosis and the exact frozen policy. Corpus/question/model hashes are unchanged across the comparison; code and decoding policy differ. Held-out results did not select parameters.

Raw outputs and diagnostic bulk records remain in their recorded ignored `.runtime` paths. Reproduce with [EVALUATION.md](../EVALUATION.md). Keep weights, databases, credentials and private source text out of this directory. All evidence remains local; no publication occurred.
