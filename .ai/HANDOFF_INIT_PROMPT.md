# Handoff Initialization Prompt

Use this prompt only at a context boundary, not before every review iteration.

Context boundaries include:

```text
new ChatGPT/Codex thread
new Codex current-thread session
context reset or context uncertainty
protocol file changed
malformed/stale/contradictory pointer message
automation or cron/subagent entry point, if automation is later enabled
```

During a continuous review loop in the same active context, do not reload the full protocol stack each turn. Instead, read only `.ai/STATE.yml`, `.ai/INBOX.md`, and the specific pointer files referenced by the latest signal or handoff.

## Initialization Goal

Load the current communication protocol into working context so the agent does not repeat old chat habits such as pasting long prompts, omitting `brief_ref`, or ignoring inherited default rules.

## Full Initialization Read Order

At a context boundary, read these always-loaded files from the active GitHub handoff branch before acting:

```text
.ai/PROTOCOL.md
.ai/PROTOCOL_ADHERENCE.md
.ai/HANDOFF_COMMON_CONVENTIONS.md
.ai/AUTONOMOUS_HANDOFF_COMMUNICATION_v0.1.md
.ai/STATE.yml
.ai/INBOX.md
```

`PROTOCOL_ADHERENCE.md` defines the independent-model bootstrap audit, fast path, mandatory dereference behavior, task-input compliance, and review correction loop. Do not assume prior chat memory in place of this stack.

Record these separately as inherited-on-demand protocols. A model must know they govern applicable tasks, but onboarding-only initialization does not require reading them in full:

```text
.ai/CODEX_WORK_MECHANISM_PROTOCOL.md
  load for Codex execution, Git-level selection, validation, failure handling, or review publication

.ai/CODEX_TASK_INPUT_CONTRACT.md
  load when parsing or validating a long ChatGPT/Human task packet
```

Relevant domain protocols are also inherited on demand when a task enters that domain. Before execution, load every inherited protocol triggered by the current role and packet type.

Then read only the referenced files required by the current pointer message:

```text
current_signal
signal_id
task_ref
packet_ref
report_ref
brief_ref
```

If a referenced file is missing, malformed, stale, or contradictory, stop and return a short blocked handoff instead of guessing.

## Fast Path For Same Context

If the agent already loaded this prompt and the protocol files in the same active context, and no protocol file changed, use the fast path:

```text
1. Read .ai/STATE.yml.
2. Read .ai/INBOX.md if needed.
3. Read only the latest current_signal / task_ref / packet_ref / report_ref / brief_ref.
4. Do not reread the whole protocol stack.
```

The fast path preserves the same distinction: retain awareness of inherited-on-demand protocols and load one only when the current task triggers it.

The fast path is intended for repeated review cycles, such as several ChatGPT/Codex turns in the same task.

## Authority Order

Apply instructions in this order:

```text
1. system / developer / platform instructions
2. current explicit human instruction
3. authenticated human-approved task or packet
4. .ai/PROTOCOL.md
5. .ai/HANDOFF_COMMON_CONVENTIONS.md
6. .ai/AUTONOMOUS_HANDOFF_COMMUNICATION_v0.1.md
7. referenced task, packet, report, or brief files
```

Repository protocol never overrides system, developer, safety, secret-protection, or current human instructions.

## Active Communication Mode

Current mode is human-triggered GitHub communication.

Default rules:

```text
no polling unless explicitly enabled
no cron/subagent unless explicitly enabled
no long prompts in chat
no long reports in chat
short messages carry pointers only
human briefs live in GitHub by default
```

## Required Message Shapes

ChatGPT-to-Codex signal:

```yaml
signal_id: "chatgpt-xxxx"
decision: "start_task | approved | revise | blocked | acknowledge_protocol_update"
task_ref: ".ai/TASKS/xxx.md | null"
packet_ref: ".ai/USER_UPLOADS/xxx.md | null"
brief_ref: ".ai/HUMAN_BRIEF.md | null"
source_head: "<commit>"
human_gate: "not_required | required"
```

Codex-to-ChatGPT handoff:

```yaml
packet_id: "codex-xxxx"
status: "completed | awaiting_review | blocked | conflict"
report_ref: ".ai/OUTBOX.md | .ai/CODEX_REPORTS/xxx.md"
brief_ref: ".ai/HUMAN_BRIEF.md | null"
source_head: "<commit>"
review_branch_head: "<commit>"
human_gate: "not_required | required"
```

## Human Brief Rule

Do not paste normal human briefs into model-to-model chat.

Use `brief_ref` instead.

Normal brief content belongs in:

```text
.ai/HUMAN_BRIEF.md
```

Detailed human-facing explanation is reserved for conflict, blocked state, permission escalation, source-branch publication, major phase transition, safety/privacy risk, model disagreement, or stage completion.

## Completion Criteria

After initialization, the agent should be able to answer:

```text
What is the current state?
Who acts next?
What exact pointer file must be read?
Is human action required?
What short pointer message should be returned?
```

If any answer is unclear, stop and return a short blocked handoff with the missing field or missing file.
