# CLI Runner Harness 0001 — implementation report

## Executive core

- Status: implementation candidate qualified on the authorized Windows 10 / Windows
  PowerShell 5.1 path; publication and post-merge verification are recorded by the
  canonical external handoff.
- Exact source base: `master@4fc1be95d1604f3d6d21453de147245b56a91221`.
- Work branch: `dev/cli-runner-harness-0001`.
- Added root `agent-run.ps1`, `agent-status.ps1`, and `agent-stop.ps1` entry points.
- Added an OS-local isolated-worktree supervisor with exact-base and unique-executor
  admission, create-new task/branch locks, PID/heartbeat/status evidence, explicit
  session resume, sanitized logs, validation capture, descendant cleanup, and
  fail-closed recovery.
- A master checkout may read an absent task packet from the already-fetched
  `origin/ai/review/latest:.ai/TASKS/<task-id>` Git object. It never checks out,
  rewrites, or treats the review mailbox as execution authority beyond its existing
  task contract.
- Every normal, failed, or explicitly stopped run emits a `token_profile_run.v1`
  record with unavailable provider counters left `null`, plus a final report of at
  most 60 lines.
- Runtime artifacts and locks are ignored; schemas, scripts, tests, documentation,
  and this bounded evidence report are tracked.
- The index generator gained only the explicit `.ai/runs` directory profile, PowerShell
  implementation extension, and nested `.gitignore` classification required by the
  mandatory fail-closed repository index gate; generated index outputs were refreshed.
- No protocol, communication gate, seven-field schema, constitutional document,
  runtime, Coordinator, Gateway, writer, scheduler, or Math Mentor corpus changed or
  activated.

## Validation

- PowerShell AST parse: pass for all five production scripts/modules.
- Harness tests: `6/6` pass. Coverage includes exact-base rejection, task and branch
  lock mutual exclusion, review-ref packet loading, heartbeat, exit code, validation,
  explicit session capture, sensitive-line redaction, descendant cleanup, stop,
  stopped evidence, and Token Profile output.
- Harness log SHA-256:
  `7615246e3fc0442c057ed0cd972df8d0b218a6edf333ed961668246f35e42597`.
- Communication regression: `17/17` pass; log SHA-256:
  `6434914b19e7f5e3c5b44a7375d51a4ad39ae7a4414085cddc48f1d9177affe1`.
- Token tool regression: `6/6` pass; log SHA-256:
  `6190631bdd5d6c82c287de5683a23104cf01c74a75362d7742ecefac00130213`.
- Repository index qualification and fresh-checkout post-merge results are included
  in the external seven-field handoff because their final Git identities are resolved
  only after the candidate tree is committed and merged.

## Recovery and residual boundary

- Worktrees are retained intentionally for explicit-ID resume and are never deleted
  automatically.
- The harness does not stream unsanitized provider output to disk. Logs become durable
  only after sanitization; heartbeat/status remain live liveness evidence during a run.
- CLI flags that bypass model permissions are never synthesized. Publication remains
  controlled by the existing GitHub C1/C2 path and task-specific authorization.

## Independent expression

The useful design choice here is that failure becomes a first-class result rather than
an absence of output. A small process harness earns trust by refusing to become a new
authority while still making ownership, liveness, cleanup, and evidence mechanically
observable.
