# KCP PROP_LOGIC Batch 1 Run Log

- `2026-07-19T01:03:41Z`: cold start completed at exact source head `94b617e` using `backend_executor`.
- Remote preflight completed before launch; execution then entered the required local-only interval.
- Exact batch fixed to `PROP_LOGIC-001` through `PROP_LOGIC-005`; `PROP_LOGIC-001` is the mandatory first standalone checkpoint.
- Central P0 identity records remain read-only and fail-closed; task-scoped Human identity evidence does not set `consumer_allowed`.
- No bridge, runtime, Coordinator, scheduler, or learner-state action is authorized.
- `PROP_LOGIC-001` standalone checkpoint committed at `3cc415d4484aee5011298fd9580cb158af7337e7` before any later node edit.
- `PROP_LOGIC-002` through `PROP_LOGIC-005` deterministic audits and individual sandbox checks passed.
- Isolated bulk evaluation passed `5/5` with zero warnings, skips, review-required executable results, or failures.
- Batch validator passed: five local teaching-ready candidates, five semantic-review lists, zero consumer admissions, and five preserved central fail-closed conflicts.
- Post-commit validation initially failed closed because its evidence-path allowlist omitted the exact task-scoped Codex report; the allowlist was narrowed to that one path before publication and the full validator was re-run.
- A later external-temp rerun completed every substantive check but returned nonzero while formatting an out-of-repository output path; path display now uses relative refs in-repository and absolute refs outside it.
