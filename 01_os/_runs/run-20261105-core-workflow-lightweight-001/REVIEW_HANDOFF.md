# Core Workflow lightweight development

- Task `OS-CORE-WORKFLOW-LIGHTWEIGHT-IMPLEMENTATION-20261105-001`
- Base `08d8e534a3438269aa7d7eb1b080ab11c172f462`
- Verified source `be6774e37b7ece6d3ecc401aa2701cb60dd2c4dc`
- Branch `task/core-workflow-lightweight-20261105`
- Next owner is the independent GPT-6 reviewer. This is the executor's candidate and evidence handoff.

## Review surface

1. The existing Stage Collaborative Deliberation validator exposes `ordinary-work` through the active v2 entry. It reuses task scope and Current Model readiness, requires `ordinary_task_work` and dormant/incremental activation, and refuses formal completion fields. The regular instance and formal acceptance paths retain their existing checks.
2. The minimum Workflow runner exposes `sync-candidate`. It previews the actual diff by default and applies only on explicit request. It refreshes dependency bindings, Manifest digests and versions in topological order. It refuses version regressions and runs with formal acceptance history or records. The sync scope is draft artifacts in the run directory, including a partial stage prefix.
3. Managed Verification exposes `checkpoint`. It uses `inspect` to derive command and result data from the existing attempt, adds the change, unresolved issues and recovery location, and emits one summary without changing attempt records.

## Observed regression and replay

The ordinary-route fixture used two source checkpoints with the same task packet. Both ordinary validations passed, both full instance validations rejected the reduced input, and Git listed two tracked files under the task path with zero seven-stage Run files. The sync test checked read-only preview, downstream refresh, an empty second diff and refusal after formal history. The checkpoint test refused altered logs. Formal tests exercised missing owner acceptance, independent completion review and reused plan acceptance. Protected operation, frozen test and Native/REA checks ran in the corresponding existing suites.

Managed Verification ran 571 standard pytest cases and all 90 Publication Gate history cases, plus the static Workflow check. All three planned commands exited 0. `inspect` recomputed the result and `checkpoint` produced its compact output. See [verification_receipt.json](verification_receipt.json) for actual command vectors, output digests and exit codes. The preceding unsharded launch timed out at 2,400 seconds. The final plan separates history replay into four shards and runs mechanism activation from its own directory.

For replay, check out the verified source in a clean worktree. Run `managed_verify.py run` with that candidate, this Run's [verification plan](verification_plan.json), and a new external attempt directory, then call `inspect` on the same attempt. The engine files in the delivery commit remain at the verified source. The publisher hook, Publication Gate, activation implementation and Native/REA execution code have zero diff from the base. Live game and native writes are outside this task's test scope.
