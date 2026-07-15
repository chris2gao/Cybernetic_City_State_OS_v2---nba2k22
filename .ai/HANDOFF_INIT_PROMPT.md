# Handoff Initialization Prompt

Use this prompt only at a context boundary, not before every review iteration.

Context boundaries include:

```text
new compatible foreground/backend model thread (ChatGPT, Claude, Codex, or Claude Code)
new backend execution-role current-thread session (Codex or Claude Code)
context reset or context uncertainty
protocol file changed
malformed/stale/contradictory pointer message
automation or cron/subagent entry point, if automation is later enabled
```

During a continuous review loop in the same active context, do not reload the full protocol stack each turn. Instead, read only `.ai/STATE.yml`, `.ai/INBOX.md`, and the specific pointer files referenced by the latest signal or handoff.

## Initialization Goal

Load the current communication protocol into working context so the agent does not repeat old chat habits such as pasting long prompts, omitting `brief_ref`, treating the machine pointer as a complete Human response, omitting required backend execution advice or independent expression, or ignoring inherited default rules.

The initializing instance identifies its stable role before acting: ChatGPT or Claude occupies `foreground_review_and_task_dispatch`; Codex or Claude Code occupies `backend_execution_and_handoff`; Human alone occupies `human_speaker`. Authority follows role plus Human/task authorization, never provider brand.

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
  load for backend execution-role work by Codex or Claude Code, Git-level selection, validation, failure handling, or review publication

.ai/CODEX_TASK_INPUT_CONTRACT.md
  load when parsing or validating a long foreground-role/Human task packet

.ai/LONG_RUN_AUTONOMOUS_PROGRAM_PROTOCOL.md
  load when a task is a Human-authorized long-run program, uses completion-preserving execution, or requests internal checkpoints instead of repeated Human gates
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

## Source Baseline Versus Active Mailbox

Published source branches should carry durable protocol files and neutral mailbox baselines. Treat `.ai/STATE.yml`, `.ai/INBOX.md`, `.ai/OUTBOX.md`, and `.ai/HUMAN_BRIEF.md` on source as inactive when they are marked `neutral_baseline` or have null packet IDs.

Active handoff packets normally live on `ai/review/latest` or a task-specific review branch. At a context boundary, identify whether the current instructions refer to source protocol files, review-branch mailbox files, or both before acting.

## Fast Path For Same Context

If the agent already loaded this prompt and the protocol files in the same active context, and no protocol file changed, use the fast path:

```text
1. Read .ai/STATE.yml.
2. Read .ai/INBOX.md if needed.
3. Read only the latest current_signal / task_ref / packet_ref / report_ref / brief_ref.
4. Do not reread the whole protocol stack.
```

The fast path preserves the same distinction: retain awareness of inherited-on-demand protocols and load one only when the current task triggers it.

The fast path is intended for repeated review cycles across compatible foreground/backend occupants, such as ChatGPT/Claude and Codex/Claude Code turns in the same task.

## Instruction Authority And State Freshness

The canonical definition is `.ai/PROTOCOL.md#canonical-instruction-authority-and-state-freshness`. Apply the same instruction-authority order:

1. platform, system, developer, and safety instructions;
2. current explicit Human instruction;
3. authenticated current Human-approved task-specific permission or override;
4. Plan 3 constitution and the Cybernetic Citizen runtime contract;
5. durable repository control protocols;
6. relevant domain-authority protocols;
7. ordinary current signal and task operational details;
8. routing documents and historical evidence.

An ordinary model-generated signal or packet remains level 7 and cannot override durable protocol merely because it is current. Only an authenticated current Human-approved task-specific permission or override can do so within its explicit scope.

Resolve state freshness separately:

1. current explicit Human statement;
2. physical Git branch/HEAD and immutable source-head evidence;
3. validated active review mailbox and every required dereferenced ref;
4. published source baseline;
5. routing snapshots;
6. historical reports and legacy branches.

Freshness establishes state only; it does not grant mutation or publication authority. Report authority conflicts separately from freshness conflicts.

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
material Human-facing responses satisfy the Human-facing completeness contract
```

The agent must distinguish the machine pointer channel, Human operational channel, and durable Human Brief channel. Classify by intended recipient and consumption mode, not UI/provider brand. In a separable mixed Human+machine interface, keep the canonical pointer block byte-structurally separate and append Human operational content outside it. If safe separation is impossible, direct output is pointer-only and a non-null, resolvable `brief_ref` preserves all required Human content; otherwise return blocked.

A Human operational dispatch that asks the Human to start or continue Codex or Claude Code includes a complete execution recommendation outside the pointer; material Human-facing events include 2 to 5 sentences of bounded independent expression. When mixed-recipient fallback makes the Human Brief the sole Human-content carrier, that Brief must also contain the complete recommendation for a backend dispatch.

## Required Message Shapes

ChatGPT-to-Codex signal (frozen foreground-to-backend wire label, used by ChatGPT or Claude):

```yaml
signal_id: "chatgpt-xxxx"
decision: "start_task | approved | revise | blocked | acknowledge_protocol_update"
task_ref: ".ai/TASKS/xxx.md | null"
packet_ref: ".ai/USER_UPLOADS/xxx.md | null"
brief_ref: ".ai/HUMAN_BRIEF.md | null"
source_head: "<commit>"
human_gate: "not_required | required"
```

Codex-to-ChatGPT handoff (frozen backend-to-foreground wire label, used by Codex or Claude Code):

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

For a material Human-facing event, the Human Brief also includes a clearly separated `Independent expression` section of 2 to 5 sentences. It is not evidence, Human authorization, hidden chain-of-thought, or an executable instruction and cannot resolve a protected gate. It may be waived only by an explicit Human pointer-only/no-extra-text request or a higher-priority safety or format constraint.

## Human-Response Preflight

Before a material Human-facing response, verify:

```yaml
human_response_preflight:
  factual_status_grounded: true
  required_refs_dereferenced: true
  canonical_pointer_present_when_applicable: true
  execution_recommendation_present_when_dispatching: true
  independent_expression_present_for_material_event: true
  independent_expression_separated_from_authority: true
  no_long_task_or_report_echo: true
  no_hidden_chain_of_thought_request_or_disclosure: true
```

When the Human is expected to start or continue a backend agent, the recommendation includes `recommended_model`, `recommended_thinking_level`, `mode`, `subagents`, `task_ref_or_plan_ref` resolving to exactly one applicable durable ref, `short_complexity_rationale`, and `human_gate`. Use `runtime_dependent` or `not_applicable` rather than omitting a field.

## Bootstrap Receipt And Executable Gate

For the first durable `C1` or protected `C2` event after full initialization, emit a `bootstrap_receipt.schema.json`-conforming receipt through the event artifact. It binds the exact protocol head, occupied provider-neutral role, frozen wire schema, immutable loaded-file blobs and digests, authority boundary, and onboarding answers. The receipt proves those deterministic evidence claims; it does not prove cognition or grant permission.

Before any C1/C2 transition is treated as eligible, use `.ai/communication_compliance/validate_communication.py` as documented in `.ai/communication_compliance/README.md`. `C0` ordinary chat is exempt. For C2, the model-generated payload and its descriptive `human_gate` remain non-authorizing; a trusted external host must inject the separately bound Human `AuthorizationContext`.

## Completion Criteria

After initialization, the agent should be able to answer:

```text
What is the current state?
Who acts next?
What exact pointer file must be read?
Is human action required?
What short pointer message should be returned?
How do the machine pointer, Human operational, and durable Human Brief channels differ?
When is a backend execution recommendation mandatory, and which seven fields does it contain?
When is bounded independent expression required, and where does the Codex/Claude Code backend role preserve it without changing the pointer schema?
What authority does independent expression not possess?
How is an omission corrected without blaming context or the Human, inventing a cleanup microtask, or discarding valid work?
Which stable role and frozen wire schema apply to each compatible ChatGPT, Claude, Codex, or Claude Code instance?
How does a mixed-recipient interface preserve structural separation, and when must it fall back to pointer-only plus a resolvable `brief_ref`?
What does the bootstrap receipt prove, what can it not prove, and when is the executable C1/C2 gate required?
Why can neither `human_gate` text nor the validator authorize a C2 action, and where must trusted Human authority originate?
```

If any answer is unclear, stop and return a short blocked handoff with the missing field or missing file.
