# Handoff Common Conventions

These conventions are inherited by all ChatGPT, Codex, and human-facing handoff packets unless a current human-approved task explicitly overrides them. Codex execution tasks additionally inherit `.ai/CODEX_WORK_MECHANISM_PROTOCOL.md` under the same override rule.

Future long task packets also follow `.ai/CODEX_TASK_INPUT_CONTRACT.md`. They state task-specific intent and differences without repeating these common conventions.

Human-authorized long-run programs additionally follow `.ai/LONG_RUN_AUTONOMOUS_PROGRAM_PROTOCOL.md`. Such programs default to completion-preserving execution: necessary cleanup, validation, alignment, report, and repair steps are folded into the original authorized objective when they remain within scope.

## 1. Role Defaults

- Human: sets goals and boundaries, resolves conflicts, approves source-branch publication, and makes final decisions for major stage transitions.
- ChatGPT: performs review, planning, architecture decisions, risk judgment, and stage gates.
- Codex: performs local execution, tests, commits, review-branch handoff, and execution reporting.

## 2. Default Forbidden Actions

Unless explicitly enabled by a human-approved task:

- no polling;
- no cron or subagent automation;
- no next-stage entry;
- no business-code modification;
- no evaluator modification;
- no node or bridge YAML modification;
- no source-branch push;
- no `git add .`;
- no destructive Git operation;
- no secrets, `.env`, SSH key, token, or private-configuration modification.

## 3. Git Defaults

- The source branch stays local unless the human explicitly approves a push.
- The review branch is `ai/review/latest`.
- The review branch is the communication bus for `.ai` handoff files.
- Stage exact file paths only; never stage broad paths by default.
- With multiple writers, review-branch publication must use expected-SHA lease protection or an equivalent compare-and-swap check.
- Use the local-first handoff workflow: one initial state read, direct authorized local work, one consolidated validation, one commit per required branch artifact, and one review publication attempt.
- Do not poll remote heads or repeat status/diff/scope checks on the successful path. Re-fetch after a failed publish, missing ref, Human gate, or detected conflict.
- Avoid isolated worktrees for small `.ai` work unless branch separation, remote-only file preservation, or overlapping changes make isolation necessary.

## 4. Communication Defaults

- Model-to-model chat carries only short pointer messages.
- Long ChatGPT task packets live in `.ai/USER_UPLOADS/*.md` or `.ai/TASKS/*.md`.
- Codex detailed reports live in `.ai/CODEX_REPORTS/*.md`, `.ai/OUTBOX.md`, or `.ai/STATE.yml`.
- `.ai/USER_UPLOADS/` is owned by Human/ChatGPT long input carriers; `.ai/CODEX_REPORTS/` is owned by Codex reports, plans, and analysis; `.ai/TASKS/` contains reusable task templates.
- `.ai/HUMAN_BRIEF.md` is the latest Human-facing brief.
- Latest machine state lives in `.ai/STATE.yml`.
- `.ai/INBOX.md` is only an optional index or pointer.
- Do not paste long prompts, long execution reports, full diffs, command logs, or private data into chat.
- Source branches carry durable protocol files and neutral mailbox baselines. Active mailbox state belongs on `ai/review/latest` or a task-specific review branch.

## 5. Pointer Dereference Defaults

- A short pointer message is not complete when it has merely been read.
- The receiver must immediately dereference every non-null ref that is required by the message intent.
- For ChatGPT-to-Codex signals, non-null `init_ref`, `task_ref`, `packet_ref`, and `brief_ref` must be read as applicable before the receiver decides to execute, acknowledge, block, or wait.
- For Codex-to-ChatGPT handoffs, non-null `report_ref`, optional `detail_ref`, and `brief_ref` must be read as applicable before review or summary.
- If `task_ref` and `packet_ref` are both null, there is no long task body. The receiver should act on `decision` or `status` directly, such as acknowledge, approve, mark blocked, or request clarification.
- The receiver must not stop after reading only `INBOX.md` or a signal when a non-null `packet_ref`, `task_ref`, or `report_ref` exists.
- If a referenced file is missing, stale, malformed, or contradictory, stop and return a short blocked handoff instead of guessing.
- Writers publish and verify referenced artifacts before publishing the signal or handoff, then update optional `INBOX.md` last.
- For a missing required ref, check the exact path once at the current review head, return `blocked`, and do not inspect unrelated files or read the brief first.
- Retry a missing ref only after the review head changes or a new signal appears. Missing protocol input does not consume the three-attempt execution repair budget.

## 6. Human Brief Defaults

- Human-facing brief text lives in GitHub, not in model-to-model chat, by default.
- The latest brief lives in `.ai/HUMAN_BRIEF.md`.
- Optional archived briefs live in `.ai/HUMAN_BRIEFS/*.md`.
- Pointer messages should include `brief_ref` when a human brief exists.
- Normal human briefs should be 3 to 5 lines.
- Detailed human briefs are reserved for conflict, blocked state, permission escalation, source-branch publication, major phase transition, safety/privacy risk, model disagreement, or stage completion.

## 7. Canonical ChatGPT-to-Codex Signal

```yaml
signal_id: "chatgpt-0001"
decision: "start_task"
task_ref: ".ai/TASKS/example.md"
packet_ref: null
brief_ref: ".ai/HUMAN_BRIEF.md"
source_head: "<commit>"
human_gate: "not_required"
```

## 8. Canonical Codex-to-ChatGPT Handoff

```yaml
packet_id: "codex-0001"
status: "completed"
report_ref: ".ai/OUTBOX.md"
brief_ref: ".ai/HUMAN_BRIEF.md"
source_head: "<commit>"
review_branch_head: "<commit>"
human_gate: "not_required"
```

The seven handoff fields above remain the canonical required core. Add optional `detail_ref` when a separate long Codex artifact exists:

```yaml
detail_ref: ".ai/CODEX_REPORTS/example.md"
```

## 9. Brief Discipline

The chat window should normally contain only the canonical pointer message. The human can read the human-facing summary from `brief_ref`. If the human explicitly asks for a summary in chat, keep it short unless an interrupt condition applies.

## 10. Token And Context Defaults

- Short model-to-model handoffs should normally stay below approximately 300 tokens.
- Dereference every non-null ref, but read large artifacts by heading, summary, `rg`, or targeted line range before expanding scope.
- Do not use one `Get-Content -Raw` operation to load multiple large evidence files.
- Read the full protocol stack only at a context boundary or when the protocol head changes. Otherwise use the fast path through `STATE.yml`, the current signal or `INBOX.md`, `OUTBOX.md`, and `HUMAN_BRIEF.md`.
- Keep `.ai/OUTBOX.md` concise. Put detailed execution logs in `.ai/CODEX_REPORTS/*.md` and point to them.
- For repeated planning tasks of similar scope, target approximately 12k to 18k visible tokens. This is an operating target, not a correctness guarantee or a reason to skip required evidence.

```yaml
context_policy:
  full_protocol_read: "only_when_protocol_head_changes"
  max_tool_output_lines: 250
  max_combined_raw_files: 1
  evidence_read_mode: "targeted_sections"
  repeated_read: "forbidden_unless_first_read_truncated"
```

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

These defaults remove avoidable output. They do not permit skipping evidence or reasoning needed for correctness.

## 11. Long-Run Completion Defaults

- Do not split a Human-authorized long-run program into micro-tasks when discovered sub-steps remain necessary, safe, and in scope.
- Use internal checkpoints, bounded issue logs, and one consolidated review package instead of repeated small Human gates.
- Escalate only for new authority, objective change, forbidden paths, destructive Git, source/master push, security/privacy/secrets risk, Coordinator or runtime activation, or whole-task blockers.
- Completion-preserving execution does not weaken protected gates or authorize unrelated business/domain changes.

## 12. Human-Facing Execution Recommendation Defaults

ChatGPT may include a short Codex execution recommendation in human-facing chat when advising the Human to start a Codex task. It may include, when useful:

- `recommended_model`
- `recommended_thinking_level`
- `mode`: `plan | goal | pursue_goal | review | implementation`
- `goal`
- exactly one applicable `plan_ref` or `task_ref`
- `local_files_to_load`, only when local files are required
- `plugins_or_apps`, only when a plugin or app is required
- `human_gate`

The recommendation is optional, is not required in `.ai/HUMAN_BRIEF.md`, and is not part of the machine handoff unless a signal, task, or packet explicitly references it. A separate valid signal is still required to authorize execution.
