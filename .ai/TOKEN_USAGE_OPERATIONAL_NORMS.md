# Token Usage Operational Norms — Annex A

Status: effective operating discipline under `TOKEN_USAGE_PROFILE.md`. These norms do
not alter protocol semantics, frozen seven fields, Human gates, or GitHub authority.

## Roles and invocation

| Role | Default use | Invocation / resume |
| --- | --- | --- |
| Fable (Claude Desktop) | audit, acceptance, dispatch, architecture, synthesis, arbitration; execution only at T3 | Human sets effort (default high); request escalation before work and downgrade after it. |
| Codex CLI | default executor for batch generation, fixes, validation, and publication chains | `codex exec '<prompt>' -p citystate_t0|t1|t2 -o <lastmsg> [-C <dir>]`; resume with `codex exec resume <session-id>`. |
| Claude Code CLI | Human-requested quality work, protocol-sensitive work, cross-checking, or Codex exhaustion/repeated failure | `claude -p '<prompt>' --model <haiku|sonnet|opus> --effort <e> --output-format json --allowedTools '<scope>' --permission-mode acceptEdits`; resume with `claude --resume <session-id>`. |

Do not use “latest session”, implicit `-c`, or `--last`. Long executor-to-executor
content does not transit Fable: Fable reads an executive core and decisive evidence.

## Seven-step dispatch

1. Fable writes a task packet with `task_id`, tier, sole assigned executor,
   definition of done, stop rules, and metering.
2. The assigned executor is unique; another executor does not claim that task ID.
3. C1 stateful dispatch uses the GitHub mailbox and seven-field pointer; C0 uses chat.
4. Driving prompts contain role, pointers, and acknowledgement only—never long bodies.
5. The executor returns the C1 seven-field handoff or C0 message and writes one run
   record to the token ledger.
6. Fable dereferences the report and independently reads decisive evidence against DoD.
7. Close with the established Obsidian 00/01/02 brief set; the Human reads that brief.

## C0 chat channel

Root: `C:/Users/gk/AppData/Local/CityState/local_bus/chat/<topic>/`.

- A message is `NNN_<sender>.md`; `NNN` is monotonically increasing, publication uses
  a temporary file and atomic rename, and `_channel.yml` records participants,
  `task_ref`, status, and creation time.
- Message front matter contains `seq`, `sender`, `session_id`, `reply_to`, and `ts`.
  Body is at most 30 lines and uses pointers instead of copied content.
- Channel files carry deltas only. Each participant keeps its own explicit-ID session.
- Modes in increasing cost: relay (default), baton (executors alternate and Fable reads
  `999_summary.md` at the end), then terminal direct-connect only for short debugging.
- C0 never carries claim/acceptance/publication/gate state. Delete messages after 30
  days via controlled GC.
