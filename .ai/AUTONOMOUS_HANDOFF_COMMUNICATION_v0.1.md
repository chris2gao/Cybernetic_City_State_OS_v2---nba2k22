# Autonomous Handoff Communication v0.1

## 1. Purpose

This mechanism supports high-density, traceable, human-triggered communication between ChatGPT and Codex through GitHub. It uses pointer-based messaging: chat carries only compact references, while long tasks, reports, and human-facing briefs live in versioned GitHub files. Autonomous polling is not part of this version.

All packets inherit `.ai/HANDOFF_COMMON_CONVENTIONS.md` unless explicitly overridden by a human-approved task.

## 2. Current Scope

- Human-triggered GitHub communication.
- ChatGPT review, planning, architecture decisions, and stage gates.
- Codex local execution, tests, commits, and review-branch publication.
- GitHub-based human briefs and explicit human interrupt gates.
- No autonomous polling.
- No cron or subagent context-pack design.

## 3. Non-goals

- Do not automate progression from P2.9 through P10+.
- Do not enable a ChatGPT scheduled watcher or Codex cron/subagent automation.
- Do not allow ChatGPT to modify business files.
- Do not use direct long executable INBOX writes as the default carrier.
- Do not paste human briefs into model-to-model chat by default.
- Do not bypass platform safety checks.
- Do not push the source branch through this protocol.
- Do not enter P2.10 or P3 through this documentation task.

## 4. Roles

### Human

- Sets goals and boundaries.
- Approves source-branch publication and major phase transitions.
- Resolves conflicts, disagreement, and blocked states.
- Reads `.ai/HUMAN_BRIEF.md` or archived briefs when needed.
- Acts as the interrupt gate.

### ChatGPT

- Performs architecture and code review, risk judgment, task decomposition, and stage-gate decisions.
- Writes long task content to an approved GitHub carrier.
- Sends only a short signal that points to the task, packet, and human brief.
- Writes or updates a minimal human brief when useful.
- Does not modify business files.

### Codex

- Performs local file changes, commands, tests, commits, and review-branch publication.
- Updates OUTBOX and active review STATE, writes execution reports, and records exhausted failures.
- Returns only a short handoff that points to the durable execution report and human brief.
- Writes or updates a minimal human brief when useful.
- Does not push the source branch without explicit human approval.

## 5. Branches

- Source branch: `legacy-mode-a-outsourcing`.
- Review branch: `ai/review/latest`.
- Source-branch publication requires explicit human approval.
- The review branch is the communication bus and may contain `.ai` communication files.
- Business changes remain local on the source branch until separately approved.
- With multiple writers, every review-branch write must preserve the observed remote head and use an explicit expected-SHA lease or an equivalent compare-and-swap check.

## 6. Communication Channels

### Codex to ChatGPT

- `.ai/STATE.yml`
- `.ai/OUTBOX.md`
- `.ai/CODEX_REPORTS/*.md`

### ChatGPT to Codex

- `.ai/SIGNAL_CHATGPT_*.yml`
- `.ai/USER_UPLOADS/*.md`
- `.ai/TASKS/*.md`

### Human Briefs

- `.ai/HUMAN_BRIEF.md`
- `.ai/HUMAN_BRIEFS/*.md`

### Optional Index

- `.ai/INBOX.md`

`INBOX.md` is an optional pointer or index to the latest signal, uploaded packet, task template, report, or brief. It is not the only carrier for long executable instructions.

## 7. Short Signal Policy

ChatGPT sends only this compact signal shape:

```yaml
signal_id: "chatgpt-0002"
decision: "approved"
task_ref: ".ai/TASKS/P2.9-A.md"
packet_ref: null
brief_ref: ".ai/HUMAN_BRIEF.md"
source_head: "<commit>"
human_gate: "not_required"
```

All seven fields are required; unused pointers are `null`. Short signals may record review approval, review required, blocked, selected next task, a stage-gate result, a required human gate, or a conflict. They must not contain task bodies, long explanations, command logs, executable prompt text, or long human summaries.

## 8. Long Packet Carrier Policy

The verified writeback behavior is:

- Direct short signal writeback succeeded.
- Direct writing of a long formal executable INBOX packet was unstable or blocked.
- A human-uploaded long packet carrier succeeded.

Long tasks and packets use only `.ai/TASKS/*.md` or `.ai/USER_UPLOADS/*.md`. They become actionable only after explicit human approval when required and Codex validation of packet identity, source branch/head, scope, and human gate. Codex must not execute an uploaded packet blindly. The consumed identity must be recorded.

Verified carrier example: `.ai/USER_UPLOADS/formal_INBOX_blocked_original.md`.

## 9. Task Template Policy

Reusable task templates live under `.ai/TASKS/*.md`, for example `.ai/TASKS/P2.9-A.md`. Templates reduce repeated long prompts, keep execution boundaries versioned, and let a short ChatGPT signal select a task while Codex retains ownership of executable details.

## 10. Pointer Message Requirements

ChatGPT-to-Codex chat contains only the seven-field signal defined in Section 7. Codex-to-ChatGPT chat contains only this handoff shape:

```yaml
packet_id: "codex-0002"
status: "awaiting_chatgpt_review"
report_ref: ".ai/OUTBOX.md"
brief_ref: ".ai/HUMAN_BRIEF.md"
source_head: "<commit>"
review_branch_head: "<commit>"
human_gate: "not_required"
```

All seven handoff fields are required. The detailed execution report lives in `.ai/CODEX_REPORTS/*.md`, `.ai/OUTBOX.md`, or `.ai/STATE.yml`; the human-facing summary lives in `.ai/HUMAN_BRIEF.md` or `.ai/HUMAN_BRIEFS/*.md`; neither is pasted into chat. Malformed, missing, or stale pointers are reported rather than inferred or executed.

Because a Git commit cannot contain its own SHA, a neutral source-branch report uses `review_branch_head: null`, while the committed active review artifact uses `review_branch_head: "self"`. The short handoff sent after publication resolves `self` to the concrete remote review-branch SHA.

Pointer messages should normally remain below approximately 300 tokens. Every non-null ref must be dereferenced, but large referenced artifacts are read with `rg`, headings, summaries, or targeted line ranges. Do not load multiple large evidence files in one `Get-Content -Raw` operation. Keep `OUTBOX.md` concise and move detailed logs to `.ai/CODEX_REPORTS/*.md`.

Use full protocol initialization only at a context boundary or when the protocol head changes. In a stable context, read the current state, signal, report, and brief through the fast path. Similar planning tasks should target approximately 12k to 18k visible tokens while preserving all required evidence.

### Publication Order

Every writer publishes and verifies the referenced task, packet, report, or brief first; publishes the short pointer second; and updates optional `INBOX.md` last. A signal must never advertise a path that is not present at its published review head.

### Missing-Reference Handling

If a required non-null ref is absent, the receiver checks that exact path once and returns `blocked`. It must not infer the task from the filename, audit unrelated files, or read `HUMAN_BRIEF.md` before the required task/report artifact exists. It retries only after a new signal or changed review head. This is malformed protocol input, not a retry-budget failure.

### Cost Guardrails

- First-pass protocol/code search uses `rg -n` without context and returns at most 80 match lines.
- Read context only around selected matches; do not repeat overlapping match blocks.
- Successful commands and validation emit consolidated summaries only.
- Do not echo packet bodies or Human Brief bodies on the successful path.
- Progress narration is reserved for blocked state, conflict, required permission, destructive risk, or a Human gate, subject to higher-priority update requirements.
- Spend enough context for correctness; optimize repeated reads, duplicate output, and narration rather than necessary evidence or reasoning.

## 11. Human Brief Requirement

Human-facing summaries live in GitHub by default.

Latest brief:

```text
.ai/HUMAN_BRIEF.md
```

Optional archive:

```text
.ai/HUMAN_BRIEFS/*.md
```

A normal completion brief states only what changed, the result, whether a problem exists, the next step, and whether a human decision is required. It should be 3 to 5 lines.

Write a detailed human brief only for conflict, disagreement, blocked state, exhausted retry budget, permission escalation, source-branch publication, a major phase transition, security/privacy risk, or stage completion. Detailed technical evidence remains in the referenced GitHub report.

ChatGPT may include a short Codex execution recommendation in human-facing chat when advising the Human to start a Codex task. The recommendation is not required in the GitHub Human Brief and is not part of the machine handoff unless a signal, task, or packet explicitly references it. A recommendation never authorizes a future stage by itself.

## 12. Retry Budget

The same failure class receives at most three materially different repair attempts. After the third failure, stop that line of work, mark it blocked, record evidence in OUTBOX or a failure report, and request ChatGPT/human review.

Failure classes include permission, Git conflict, test failure, schema failure, path not found, import/dependency failure, writeback failure, and unknown.

A missing required handoff ref is excluded from this budget. It is checked once and remains blocked until the review head changes or a new signal is published.

## 13. State Machine

Allowed coordination states are:

- `idle`
- `awaiting_codex`
- `codex_running`
- `awaiting_chatgpt_review`
- `chatgpt_reviewing`
- `awaiting_human_gate`
- `blocked`
- `conflict`
- `completed`

## 14. Consumed Packet Tracking

Active review STATE should track duplicate prevention with:

```yaml
last_consumed_by_codex: "<packet_id>"
last_consumed_by_chatgpt: "<packet_id>"
last_outbox_packet: "<packet_id>"
last_signal: "<signal_id>"
task_ref: ".ai/TASKS/<task>.md"
packet_ref: ".ai/USER_UPLOADS/<packet>.md"
report_ref: ".ai/OUTBOX.md"
brief_ref: ".ai/HUMAN_BRIEF.md"
```

Neither model may execute or review the same packet twice unless the human explicitly requests replay.

## 15. Current Automation Status

- The ChatGPT watcher is disabled.
- The Codex `ai-handoff-inbox-monitor` heartbeat has been deleted.
- Codex cron and subagent automation are outside this version.
- Future automation requires a dedicated context pack.
- The current mechanism is human-triggered.

## 16. Future Automation Deferred

Deferred capabilities include a ChatGPT scheduled watcher, Codex cron/subagent context packs, multi-model debate, human interrupt delivery, stage-completion notifications, and a full Cybernetic City-State OS orchestrator. They belong to a dedicated automation phase or P10+ and must not block current Math Mentor work.

## 17. Safety and Authority Boundaries

- System and developer instructions override this protocol.
- A current explicit human instruction overrides repository protocol.
- Secrets and credential protections always remain active.
- ChatGPT does not modify business files.
- Codex does not push the source branch without explicit human approval.
- Destructive Git operations require explicit human approval.
