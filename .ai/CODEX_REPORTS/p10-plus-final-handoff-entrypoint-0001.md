# P10+ Final Handoff Entrypoint 0001

## Stable Entrypoint

Use `.ai/HANDOFF_INIT_PROMPT.md` as the stable session bootstrap entrypoint.

At a context boundary, load:

- `.ai/PROTOCOL.md`
- `.ai/PROTOCOL_ADHERENCE.md`
- `.ai/HANDOFF_COMMON_CONVENTIONS.md`
- `.ai/AUTONOMOUS_HANDOFF_COMMUNICATION_v0.1.md`
- `.ai/STATE.yml`
- `.ai/INBOX.md`

Then load inherited-on-demand protocols when triggered:

- `.ai/CODEX_WORK_MECHANISM_PROTOCOL.md` for Codex execution, validation, Git, or review publication.
- `.ai/CODEX_TASK_INPUT_CONTRACT.md` for long task packets.
- `.ai/LONG_RUN_AUTONOMOUS_PROGRAM_PROTOCOL.md` for Human-authorized long-run programs or completion-preserving execution.
- Relevant domain protocols only when the task enters that domain.

## Source Baseline

On final master and source branches, `.ai/STATE.yml`, `.ai/INBOX.md`, `.ai/OUTBOX.md`, and `.ai/HUMAN_BRIEF.md` may be neutral baselines. Active mailbox state should normally be read from `ai/review/latest` or a task-specific review branch.

## Execution Rule

If a long-run task is active and authorized, use completion-preserving execution: fold necessary in-scope cleanup, validation, alignment, report, and repair steps into the current objective. Escalate only when a protected gate is reached.
