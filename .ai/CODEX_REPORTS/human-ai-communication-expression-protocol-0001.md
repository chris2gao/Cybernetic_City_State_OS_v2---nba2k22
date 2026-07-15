# Human-AI Communication And Expression Protocol Candidate

```yaml
task_id: human-ai-communication-expression-protocol-0001
status: complete_awaiting_chatgpt_review
source_branch: master
source_head: eb46be9dadf9672091883e4e69bcaaa70b0cb163
work_branch: codex/human-ai-communication-expression-protocol
source_or_master_publication_authorized: false
pr_creation_authorized: false
human_gate: required_after_chatgpt_review
```

## Outcome

The existing canonical communication stack now governs material Human↔AI operational communication as well as machine-to-machine handoff. The patch does not create a detached protocol and does not alter either canonical seven-field pointer core.

The candidate establishes three separate channels:

1. a parseable machine pointer channel for identity, refs, state, and gates;
2. a Human operational channel for grounded status, dispatch advice, review, completion, risk, and gates;
3. a durable Human Brief channel for versioned evidence pointers and bounded independent expression.

## Implemented Contract

- Material Human-facing events have a mechanically reviewable pre-send contract.
- A backend execution recommendation is mandatory when ChatGPT or Claude asks the Human to start or continue Codex or Claude Code work.
- The recommendation contains `recommended_model`, `recommended_thinking_level`, `mode`, `subagents`, `task_ref_or_plan_ref`, `short_complexity_rationale`, and `human_gate`.
- Unknown or inapplicable recommendation values use `runtime_dependent` or `not_applicable`; fields are not silently omitted.
- Material Human-facing events require 2 to 5 sentences of clearly separated independent professional expression.
- Codex or Claude Code preserves that expression in the referenced Human Brief; a strict machine-only response remains pointer-only.
- Independent expression is explicitly separated from evidence, authorization, hidden chain-of-thought, executable instructions, and mandatory positivity.
- Omission drift is corrected in the same turn when possible without blaming context or the Human, inventing a cleanup microtask, or discarding valid repository work.

## Authority Preservation

The patch does not grant models new authority. Execution recommendations and independent expression cannot route engines, change objectives, adjudicate protected disputes, approve or publish source/master, activate runtime or Coordinator, handle secrets, authorize destructive work, or resolve a protected Human gate.

Human Speaker authority and the existing safety, evidence, privacy, Git, publication, runtime, Coordinator, bridge, writer, consumer, and destructive-operation boundaries remain intact.

## File-Level Result

- `.ai/PROTOCOL.md`: expands canonical scope, defines the three channels, material-event taxonomy, response contract, dispatch example, expression boundary, Codex preservation, preflight, and drift correction.
- `.ai/HANDOFF_COMMON_CONVENTIONS.md`: makes backend dispatch advice mandatory, reconciles concise Brief/chat rules, and adds shared expression defaults.
- `.ai/AUTONOMOUS_HANDOFF_COMMUNICATION_v0.1.md`: aligns purpose, roles, channels, Human Brief behavior, dispatch requirements, and pointer-only fallback while preserving Human-triggered/no-polling operation.
- `.ai/PROTOCOL_ADHERENCE.md`: adds Human-response preflight, correction-loop enforcement, audit checks, and fresh-model onboarding questions.
- `.ai/HANDOFF_INIT_PROMPT.md`: initializes the three-channel distinction, mandatory dispatch profile, expression preservation, negative chain-of-thought guard, and drift-correction questions without expanding the always-loaded set.
- `.ai/CODEX_WORK_MECHANISM_PROTOCOL.md`: aligns backend dispatch wording and adds Codex/Claude Code material-output and bounded-expression behavior without weakening quiet output.
- `.ai/DECISIONS.md`: records accepted decision D-0005 and its authority boundary.

## Independent Reviews

Three task-authorized read-only reviewers independently checked:

- Human-AI channel separation, pointer purity, and Plan 3 Human Speaker authority;
- Codex/Claude Code output placement, strict machine fallback, and quiet-output compatibility;
- canonical pointer regression, onboarding, chain-of-thought guards, allowlist, and validation scenarios.

Their findings were incorporated into the candidate. The final candidate keeps 8 of 8 canonical pointer definitions unchanged and removes all four pre-existing statements that made backend dispatch recommendations optional.

## Deliberate Non-Changes

- no new standalone source protocol;
- no canonical pointer field additions or reorderings;
- no source mailbox mutation;
- no business or domain file mutation;
- no runtime, Coordinator, polling, or automation activation;
- no source/master publication and no PR creation;
- no unrelated protocol-version migration or legacy decision cleanup.

## Review Request

ChatGPT should review the candidate for cross-file consistency, Human Speaker authority preservation, mandatory dispatch semantics, expression boundaries, pointer purity, and the validation evidence in `.ai/CODEX_REPORTS/human-ai-communication-expression-protocol-validation-0001.md`.
