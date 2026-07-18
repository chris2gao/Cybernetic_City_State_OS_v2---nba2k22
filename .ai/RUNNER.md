# Windows CLI Runner Harness (`agent-run`)

## Purpose and authority

The runner fills one narrow control-plane gap: durable Windows process ownership for
Codex CLI and Claude CLI workers. It reads the existing `.ai/TASKS/<task-id>` packet,
checks its exact Git base and unique executor, creates an isolated worktree, and records
process evidence. It is not a second task registry, state authority, permission source,
reviewer, merger, or replacement for `.ai/PROTOCOL.md`.

GitHub remains authoritative for C1/C2. A model payload, `human_gate` string, runner
status, successful process, or generated report cannot authorize publication or a state
transition. The task owner still publishes the canonical seven-field handoff after the
task's authorized checks and Git workflow complete.

## Windows-native layout

The implementation targets Windows 10 and Windows PowerShell 5.1. It uses
`Start-Process -WindowStyle Hidden`, `System.Diagnostics.Process`, PID files,
heartbeat timestamps, CIM process-tree discovery, and atomic same-directory file
replacement. It does not require tmux, Bash, WSL, terminal sandboxes, a polling service,
or a permanently active Coordinator.

Each launch keeps evidence under `.ai/runs/<task-id>/`:

- `status.json`: state, engine PID, heartbeat, explicit session ID, base and worktree;
- `session.json`: parsed DoD, stop rules, path boundaries, validation commands and locks;
- `run.log` / `stderr.log`: sensitive-looking lines redacted before persistence;
- `validation.log`: every declared command and exit code;
- `final-report.md`: at most 60 lines plus direct evidence pointers;
- `LOCK`: present only while the worker is owned; removed on exit or explicit stop.

The actual Git worktree and shared branch lock live outside the repository at
`%LOCALAPPDATA%\CityState\agent_runs\<repo-key>\`. This avoids a nested worktree inside
the source checkout, keeps transient branch ownership shared across repository
worktrees, and prevents runtime process data from entering a commit. A retained
worktree is deliberate recovery evidence, not a claim that the task is complete.

## Invocation

Fetch the authorized base and review mailbox first, then run from the repository root.
The runner prefers a task packet present in the working tree; when master intentionally
does not carry mailbox tasks, it reads the already-fetched immutable Git object at
`origin/ai/review/latest:.ai/TASKS/<task-id>` without checking out or mutating review:

```powershell
.\agent-run.ps1 -TaskId example-task-0001 -Engine codex -Tier citystate_t1
.\agent-run.ps1 -TaskId example-task-0001 -Engine claude -Resume 019f-example-session
.\agent-status.ps1 -TaskId example-task-0001
.\agent-stop.ps1 -TaskId example-task-0001
```

`agent-run.ps1` returns after starting a hidden detached worker. `-Wait` is available
for CI or interactive verification. Production executable overrides are forbidden;
the narrowly scoped `-TestMode` parameters exist only for deterministic fake-engine
tests. The runner never enables Codex danger-full-access or Claude bypass permissions
on its own. Such flags require an explicit task packet and Human authorization and are
not synthesized by this implementation.

For Codex, a new run uses JSON events and captures `thread.started.thread_id`.
For Claude, the runner captures a returned `session_id` when present. Recovery always
requires `-Resume <explicit-id>`; “latest”, implicit continuation, and guessed sessions
are unsupported. Tier selects the Codex profile; Claude keeps its host configuration
unless its separately authorized task invocation specifies a model.

## Task packet contract

The packet must expose `base.branch`, full `base.head`, `work_branch`, and
`assigned_executor`. Markdown sections are copied into `session.json` for
`definition_of_done`, `stop_rules`, `allowed`, and `forbidden`. Optional deterministic
validation commands use a top-level list:

```yaml
validation_commands:
  - "python -m pytest .ai/runs/tests -q"
  - "python generate_repository_indexes.py check"
```

No list means “no machine-readable validation declared”; the runner records that fact
instead of inventing a check. A mismatched base, missing packet field, unassigned
engine, active task lock, or active branch lock rejects launch before a worker exists.

## Locking, heartbeat, and cleanup

The task `LOCK` and OS-local branch lock are created with create-new semantics. A live
lock rejects a second writer; a dead, well-formed lock may be reclaimed. A malformed
lock fails closed for inspection. Once started, `status.pid` is the CLI PID and the
lock PID is the supervising worker. Heartbeat defaults to 30 seconds.

On natural exit the supervisor captures the CLI exit code, runs declared validation,
recursively terminates descendant processes, writes the report and one
`token_profile_run.v1` record, then releases both locks. `agent-stop.ps1` kills the CLI
and supervisor trees, marks `stopped`, produces stopped-run evidence and metering, and
releases locks. Worktrees are never deleted automatically.

## Reload versus restart

- **Reload**: the worker is alive but context changed; let the explicit-ID session
  reload immutable task/protocol/source pointers without starting a second writer.
- **Resume**: the prior worker ended and its worktree is retained; verify repository,
  task, protocol release, source head and context epoch, then use `-Resume <id>`.
- **Restart**: use only when no reliable session exists. Preserve the old run evidence,
  create a new task ID or Human-authorized recovery packet, and do not guess “latest”.
- **Stale/malformed lock**: query status first. A live lock is authoritative process
  evidence; a malformed lock requires Human-visible inspection rather than deletion.

## When ChatGPT review is required

Escalate for independent foreground review when work changes architecture or crosses
modules; touches protocol/schema, permission, identity, protected branches, runtime or
activation; produces conflicting conclusions; cannot validate; or reaches a task's
explicit review/Human gate. Ordinary heartbeat, exit, validation and metering evidence
does not create a new Human gate, and it never closes an existing one.

## Security boundary

The runner does not read `.env`, SSH keys, credential stores, tokens, or signing keys.
It persists only a pointer prompt and sanitizes output lines matching common secret,
authorization, token and private-key patterns. Secret-sensitive tasks remain a stop
condition; redaction is defense in depth, not permission to process secrets. Runtime,
Coordinator, Gateway, writer, scheduler, polling and unattended automation remain
inactive.
