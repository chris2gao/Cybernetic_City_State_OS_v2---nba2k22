# AI Handoff Protocol v0.3-core

## Purpose

This protocol provides a compact, auditable handoff channel between ChatGPT, Codex, and the human operator. It reduces copied logs, stale context, and ambiguous task state while preserving human control.

Independent model instances follow `.ai/PROTOCOL_ADHERENCE.md` to bootstrap, apply authority order, validate required refs and task input, and enter the review correction loop when protocol rules are missed.

All packets inherit `.ai/HANDOFF_COMMON_CONVENTIONS.md` unless explicitly overridden by a current human-approved task. Codex execution tasks also inherit `.ai/CODEX_WORK_MECHANISM_PROTOCOL.md` unless explicitly overridden by a current human-approved task.

## Scope

This protocol governs only:

- AI-to-AI handoff and execution coordination;
- mailbox structure and packet identity;
- review requests and review-branch publication;
- source/review branch boundaries;
- human approval gates and GitHub-based human briefs.

It is not a repository constitution. It does not override:

- system or developer instructions;
- explicit current human instructions;
- secrets, credentials, or safety boundaries;
- mathematical content or validation rules;
- domain protocols, including Math Mentor execution protocols;
- software architecture decisions outside the handoff workflow.

`.ai/CODEX_WORK_MECHANISM_PROTOCOL.md` governs Codex execution mechanics only. It does not govern mathematical/domain semantics, override higher-priority instructions, or authorize a gated project stage or business change by itself.

## Roles

### Codex

- Performs approved local edits and tests.
- Creates business commits on the source branch.
- Writes `STATE.yml` and `OUTBOX.md`.
- Returns a short pointer handoff instead of pasting execution reports into chat.
- Writes or updates a human-facing brief when useful.
- Publishes disposable review snapshots when authorized by this protocol.
- Does not push the source branch without explicit human approval.

### ChatGPT

- Reads the exact paths and commit range declared by the current signal or handoff.
- Performs review, writes long tasks to approved GitHub paths, and sends only a short pointer signal.
- Writes or updates a human-facing brief when useful.
- May write back only to approved `.ai` communication paths.
- Must not write business files.

### Human

- Reads short summaries or GitHub brief files, asks questions, and resolves approval gates.
- Retains final authority over source-branch publication, merge, destructive Git, secrets, major architecture or mathematics decisions, and broad regeneration.

## Mailbox Files

- `PROTOCOL.md`: stable handoff rules.
- `HANDOFF_INIT_PROMPT.md`: session bootstrap prompt for context boundaries.
- `PROTOCOL_ADHERENCE.md`: bootstrap, compliance, and correction rules for independent model instances.
- `HANDOFF_COMMON_CONVENTIONS.md`: shared default rules inherited by all packets.
- `CODEX_WORK_MECHANISM_PROTOCOL.md`: canonical Codex execution-workflow mechanics.
- `CODEX_TASK_INPUT_CONTRACT.md`: canonical task signal and long-packet input requirements.
- `STATE.yml`: current machine-readable handoff state.
- `INBOX.md`: optional pointer/index for the current signal, packet, task, or brief.
- `OUTBOX.md`: durable Codex report and handoff target.
- `DECISIONS.md`: compact long-lived handoff decisions, not a turn log.
- `HUMAN_BRIEF.md`: latest human-facing brief.
- `HUMAN_BRIEFS/*.md`: optional archive for significant human-facing briefs.

The source branch stores the stable protocol and neutral mailbox baseline. Active per-turn state is published on `ai/review/latest` and must not be merged back into the source branch.

## Durable Protocol And Active Mailbox Separation

Durable protocol files define behavior and may be carried by the source branch. Active mailbox files describe one current exchange and are safe to reset to neutral baseline on source publication.

Durable protocol files include:

- `.ai/PROTOCOL.md`
- `.ai/PROTOCOL_ADHERENCE.md`
- `.ai/HANDOFF_INIT_PROMPT.md`
- `.ai/HANDOFF_COMMON_CONVENTIONS.md`
- `.ai/AUTONOMOUS_HANDOFF_COMMUNICATION_v0.1.md`
- `.ai/CODEX_WORK_MECHANISM_PROTOCOL.md`
- `.ai/CODEX_TASK_INPUT_CONTRACT.md`
- `.ai/LONG_RUN_AUTONOMOUS_PROGRAM_PROTOCOL.md`
- `.ai/DECISIONS.md`

Active mailbox files include:

- `.ai/INBOX.md`
- `.ai/OUTBOX.md`
- `.ai/HUMAN_BRIEF.md`
- `.ai/STATE.yml`

On final master or another published source baseline, the active mailbox files should be neutral unless a current Human-approved task explicitly says otherwise. Live handoff state belongs on `ai/review/latest` or a task-specific review branch. Do not infer an active task from source-branch mailbox state when it is marked `neutral_baseline`.

### Source Publication Mailbox Neutralization Gate

Before a work branch is published to a durable source branch or `master`, its source-side mailbox must be neutralized. Active task snapshots must not be merged into the published source baseline.

Required source publication checks:

- `.ai/INBOX.md` parses and declares `intent: neutral_baseline`, with no active signal/task/packet pointer;
- `.ai/STATE.yml` parses and declares `status: neutral_baseline`, with no active packet ID, task ID, work branch, report ref, or pending Human gate;
- `.ai/OUTBOX.md` parses and declares `status: neutral_baseline`, with no active packet/report/branch fields;
- `.ai/HUMAN_BRIEF.md` is a short neutral notice and does not describe an active or pending task;
- post-publication read-back confirms those four neutral source artifacts at the published source HEAD.

If any source mailbox file contains an active `packet_id`, task identity, work branch, report pointer, or pending Human gate, source publication is blocked until the source mailbox is neutralized. Active handoff state remains on `ai/review/latest`; neutralizing source does not delete durable `.ai/CODEX_REPORTS/` evidence.

## Pointer-Based Message Format

ChatGPT-to-Codex signals contain these seven required fields:

- `signal_id`
- `decision`
- `task_ref`
- `packet_ref`
- `brief_ref`
- `source_head`
- `human_gate`

Long task content lives in `.ai/TASKS/*.md` or `.ai/USER_UPLOADS/*.md`; it is never pasted into the short signal. `brief_ref` points to the human-facing brief when one exists, usually `.ai/HUMAN_BRIEF.md`; otherwise it may be `null`.

Future ChatGPT/Human-authored long task packets follow `.ai/CODEX_TASK_INPUT_CONTRACT.md`. That contract defines required packet fields, risk-triggered task modules, evidence and output refs, validation, stop rules, and missing-input behavior.

Codex-to-ChatGPT handoffs contain these seven required core fields:

- `packet_id`
- `status`
- `report_ref`
- `brief_ref`
- `source_head`
- `review_branch_head`
- `human_gate`

`detail_ref` is an optional eighth field. Include it when a separate long Codex report, plan, analysis, or execution detail exists; omit it when `report_ref` is sufficient. Codex-generated long details live under `.ai/CODEX_REPORTS/*.md` unless the task names another approved Codex-owned path.

Detailed execution reports live in `.ai/CODEX_REPORTS/*.md`, `.ai/OUTBOX.md`, or `.ai/STATE.yml`. IDs prevent duplicate consumption, source heads bind messages to business state, reference fields identify the durable content to read, and `brief_ref` points to the human-facing summary.

A source-branch baseline may use `review_branch_head: null`. An active committed review artifact uses `review_branch_head: "self"` because a commit cannot embed its own SHA; the post-publication short handoff resolves it to the actual remote SHA.

## Pointer Dereference Obligation

Reading a short pointer message is not enough to complete a handoff. The receiver must follow every non-null reference needed by the message intent before deciding to execute, acknowledge, block, or wait.

For ChatGPT-to-Codex signals:

- If `task_ref` is non-null, Codex must read that task template.
- If `packet_ref` is non-null, Codex must read that uploaded packet or long task body.
- If `brief_ref` is non-null, Codex should read or update the human brief when the task affects the human-facing status.
- If both `task_ref` and `packet_ref` are null, there is no long task body; Codex should act directly on `decision`, such as acknowledge a protocol update, accept approval, report blocked, or request clarification.

For Codex-to-ChatGPT handoffs:

- If `report_ref` is non-null, ChatGPT must read it before review.
- If `brief_ref` is non-null, ChatGPT should read it before producing or updating a human-facing summary.
- If optional `detail_ref` is non-null, ChatGPT must read it before completing review.

An optional index such as `.ai/INBOX.md` may include additional pointers such as `current_signal` or `init_ref`. If those fields are non-null, the receiver must read them before continuing. The receiver must not stop after reading only `INBOX.md` or only the short signal when a non-null `packet_ref`, `task_ref`, or `report_ref` exists. If a referenced file is missing, stale, malformed, or contradictory, stop and return a short blocked handoff instead of guessing.

### Writer-Side Publish Order

The sender publishes durable referenced content before publishing its pointer:

1. publish the `packet_ref`, `task_ref`, `report_ref`, or `brief_ref` artifact;
2. verify that the referenced path exists at the intended review-branch head;
3. publish the short signal or handoff;
4. update optional `.ai/INBOX.md` last.

### Missing-Reference Fast Fail

When a required non-null ref is absent, check that exact ref once at the current review-branch head and immediately return `blocked`. Do not infer work from the filename, audit unrelated files, or read `HUMAN_BRIEF.md` before the required task/report ref exists. Retry only after the remote review head changes or a new signal is published. A missing ref is invalid protocol input and does not consume the execution repair budget.

```yaml
packet_id: "codex-<id>"
status: "blocked"
missing_ref: "ai/review/latest:<path>"
review_branch_head: "<observed-head>"
required_action: "publish_packet_ref"
```

## Human Brief Channel

Human-facing summary text lives in GitHub by default.

- Latest brief: `.ai/HUMAN_BRIEF.md`
- Optional archive: `.ai/HUMAN_BRIEFS/*.md`

Normal briefs are 3 to 5 lines and state only what changed, result, problem status, next step, and whether human action is required.

Detailed briefs are reserved for conflict, blocked state, retry exhaustion, permission escalation, source-branch publication, major phase transition, safety/privacy risk, model disagreement, or stage completion.

Model-to-model chat should carry `brief_ref`, not paste the full brief. If the human explicitly asks for the brief in chat, keep it short unless an interrupt condition applies.

## Handoff Initialization

Load `.ai/HANDOFF_INIT_PROMPT.md` only at a context boundary, not before every review iteration.

Context boundaries include:

- new ChatGPT/Codex thread;
- new Codex current-thread session;
- context reset or context uncertainty;
- protocol file changed;
- malformed, stale, or contradictory pointer message;
- automation or cron/subagent entry point, if automation is later enabled.

During a continuous review loop in the same active context, use the fast path: read `.ai/STATE.yml`, `.ai/INBOX.md` if needed, and only the pointer files referenced by the latest signal or handoff. Do not reread the whole protocol stack every turn.

If a referenced file is missing, stale, malformed, or contradictory, the agent must stop and return a short blocked handoff instead of guessing.

## Context Limits

- Do not paste task bodies, execution reports, full diffs, command logs, large files, tokens, private keys, `.env` contents, or long human briefs into model-to-model chat.
- Short messages contain only the canonical signal or handoff fields and should normally remain below approximately 300 tokens.
- Put durable detail in a GitHub artifact and reference its exact path and commit.
- Keep human-facing chat minimal; prefer `brief_ref`.
- Every non-null ref must still be dereferenced. Token limits govern how evidence is read, not whether required evidence is read.
- For large files, prefer `rg`, headings, summaries, and targeted line ranges. Do not load multiple large evidence files with a single `Get-Content -Raw` operation.
- Keep `OUTBOX.md` short and place detailed execution logs in `.ai/CODEX_REPORTS/*.md`.

The canonical context budget is inherited from `.ai/HANDOFF_COMMON_CONVENTIONS.md`. Similar planning tasks should target approximately 12k to 18k visible tokens. Full protocol initialization is required only at a context boundary or when the protocol head changes; otherwise use the fast path.

For recurring evidence sources, target the relevant sections first:

- Sample Pack: Issues Summary, Sample Records, and conclusion or recommendation.
- Evaluator: status constants, `evaluate_yaml_content()`, and bulk summary.
- `BRIDGE_SCHEMA.md`: endpoint, mode, validation, and Coordinator-consumption sections.

Quiet Git/worktree output is preferred. If a first read is truncated, reread only the missing targeted section. Generated documents should be complete on disk without echoing their entire body into tool output or chat.

```yaml
targeted_search_policy:
  first_pass: "rg -n without context"
  context_lines: "only for selected matches"
  max_match_output: "80_lines"
  duplicate_match_blocks: "forbidden"

successful_path_output_policy:
  packet_body_echo: "forbidden"
  human_brief_echo: "forbidden"
  command_output: "summary_only"
  grep_output: "file_and_line_only_first"
  validation_output: "consolidated_summary_only"
  expand_logs_only_on_failure: true

progress_narration_policy:
  default: "forbidden"
  allowed_only_when:
    - "blocked"
    - "conflict"
    - "permission_needed"
    - "destructive_risk"
    - "human_gate_required"
```

These are successful-path defaults. Higher-priority instructions may still require concise progress updates or pre-edit notice, and correctness always takes precedence over output reduction.

## Human-Facing Execution Recommendation

ChatGPT may include a short Codex execution recommendation in human-facing chat when advising the Human to start a Codex task. This may mention model, thinking level, mode, task/plan ref, local files, plugins/apps, or a Human gate when useful.

This recommendation is not a required field in `.ai/HUMAN_BRIEF.md` and is not part of the machine handoff unless a signal, task, or packet explicitly references it. It never crosses a stage gate by itself.

## Git Rules

- The source branch contains business history and the one-time protocol bootstrap.
- Pushing the source branch requires explicit human approval.
- `ai/review/latest` is a disposable review snapshot and must not be merged into a source branch.
- Business commits and per-turn handoff commits remain separate.
- Use explicit paths for staging; do not use `git add .`.
- Do not use destructive Git operations without explicit human approval.

### Local-First Handoff Workflow

Default to local file work and one consolidated commit. Do not perform defensive remote checks unless a push fails, a required ref is missing, a Human gate is triggered, or an actual conflict is detected.

For a normal successful task, read the current signal and all required refs once, edit locally, run consolidated task-level validation, create one source commit when needed, publish one review handoff when needed, and return the canonical short handoff. Do not repeatedly poll remote heads or repeat status/diff/scope checks without new evidence.

Final review publication still uses fast-forward or expected-SHA lease protection. If the review branch advanced and publication fails, fetch the new head and inspect only overlapping files. Retry safely when there is no overlap; return `blocked` or `conflict` when overlap or ownership is uncertain. Source-branch push remains Human-gated.

### Phase 1: Codex-only review publication

Codex is the only writer to `ai/review/latest`. Publication may use:

```powershell
git push origin HEAD:ai/review/latest --force-with-lease
```

### Phase 2: Restricted ChatGPT writeback

ChatGPT communication writeback has been tested and human-approved for `.ai` communication paths only. It must not write business files. Codex must use an explicit expected-SHA lease or equivalent compare-and-swap check before updating the review branch so that an unconsumed ChatGPT write cannot be overwritten.

## Autonomous Handoff Communication v0.1

- The current communication mechanism is documented in `.ai/AUTONOMOUS_HANDOFF_COMMUNICATION_v0.1.md`.
- Polling automation is deferred; the current mode is human-triggered GitHub communication.
- Model-to-model chat uses pointer-based messages rather than long prompts or reports.
- Long ChatGPT tasks use `.ai/TASKS/*.md` or a human-approved carrier under `.ai/USER_UPLOADS/`.
- Short ChatGPT decisions use `.ai/SIGNAL_CHATGPT_*.yml` and the canonical pointer signal with `brief_ref`.
- Codex responses use the canonical pointer handoff with `brief_ref` and point to `.ai/OUTBOX.md` or `.ai/CODEX_REPORTS/*.md`.
- `.ai/INBOX.md` may serve as an index or pointer and is not the only long-packet carrier.
- Human-facing summaries should be read through `.ai/HUMAN_BRIEF.md` or `.ai/HUMAN_BRIEFS/*.md`.

## Human Gates

Explicit human approval is required for:

- pushing a source branch;
- merging or rebasing protected branches;
- destructive Git operations;
- handling secrets, credentials, permissions, or private keys;
- broad node or domain regeneration;
- major mathematical, architectural, or validation-policy decisions;
- expanding this protocol beyond the handoff scope.

ChatGPT and Codex must not claim that a human gate is approved without evidence from a current human instruction or an authenticated approval channel.

## Long-Run Task Defaults

Human-authorized long-run programs inherit `.ai/LONG_RUN_AUTONOMOUS_PROGRAM_PROTOCOL.md`.

By default, long-run execution is completion-preserving: discovered cleanup, validation, alignment, report, and repair steps are folded into the original authorized task when they are necessary for completion and remain within scope. Internal checkpoints replace repeated small Human gates.

Human escalation is required only when a discovered item requires new authority, changes the objective, touches forbidden paths, requires destructive Git, requires source or master push, creates security, privacy, or secrets risk, requests Coordinator or runtime activation, or blocks all safe independent progress.

This rule is an execution-efficiency rule. It does not authorize P3, bridge generation, source publication, master merge, runtime activation, secrets access, broad regeneration, or unrelated business changes.

## City-State OS Alignment

The `.ai` handoff layer is the communication and review layer for ChatGPT, Codex, and the Human. It should align with the broader Cybernetic City-State OS structure without silently becoming runtime governance.

- `.ai/CODEX_REPORTS/*.md` stores model-to-model review evidence.
- `campaigns/campaign_manifest_template.yaml` remains the template for future campaign state when a task explicitly opens a campaign.
- `system_backbone/audit_ledger/system_record.jsonl` remains the audit-ledger substrate; this protocol does not authorize ledger writes by itself.
- `02_Protocols/` contains broader OS protocol doctrine. `.ai` files provide executable handoff mechanics.

Runtime integration, Coordinator activation, automatic routing, and repository-level AI control-plane changes require separate Human-approved tasks.

## Failure Handling

- Reject stale packets whose `source_head` does not match the intended business commit.
- Do not process a consumed `packet_id` twice.
- Stop on an unexpected sender, recipient, file scope, or unrelated worktree change.
- If a review push lease fails, fetch and inspect the remote state before retrying.
- If a packet is malformed, report the missing field instead of inferring it.
- If GitHub is unavailable, retain the local handoff and provide only a short human summary.
- If sensitive content is detected, stop before commit or push.

## Deferred Evolution

Automatic validation, multi-agent conflict handling, mandatory ChatGPT writeback, packet replay protection, repository-level governance, automated human brief delivery, and full Cybernetic City-State OS communication/control-layer activation are deferred unless a current Human-approved task opens that scope. Their roadmap is recorded in the post-P2 execution memory and P10+ protocol evolution reports.
