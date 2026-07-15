# Human-AI Communication And Expression Protocol Candidate

```yaml
task_id: human-ai-communication-expression-protocol-0001
status: complete_awaiting_chatgpt_review
source_branch: master
source_head: eb46be9dadf9672091883e4e69bcaaa70b0cb163
work_branch: codex/human-ai-communication-expression-protocol
parent_candidate: 8f0eec213484d16a97956d356a9ef1e163fc45fe
candidate_revision: provider_neutral_correction_0002
source_or_master_publication_authorized: false
pr_creation_authorized: false
human_gate: required_after_chatgpt_review
```

## Outcome

The existing canonical communication stack now governs material Human↔AI operational communication as well as machine-to-machine handoff. The same-task correction closes the exact-head review finding by making compatible role occupancy explicit across every canonical entrypoint and resolving mixed Human+machine recipient output normatively. The patch does not create a detached protocol and does not alter either canonical seven-field pointer core.

The candidate establishes three separate channels:

1. a parseable machine pointer channel for identity, refs, state, and gates;
2. a Human operational channel for grounded status, dispatch advice, review, completion, risk, and gates;
3. a durable Human Brief channel for versioned evidence pointers and bounded independent expression.

Provider-neutral role compatibility is now explicit: Human alone occupies `human_speaker`; ChatGPT or Claude occupies `foreground_review_and_task_dispatch`; Codex or Claude Code occupies `backend_execution_and_handoff`. Authority follows the occupied role plus current Human/task authorization, never provider brand.

## Implemented Contract

- Material Human-facing events have a mechanically reviewable pre-send contract.
- A backend execution recommendation is mandatory when ChatGPT or Claude asks the Human to start or continue Codex or Claude Code work.
- The recommendation contains `recommended_model`, `recommended_thinking_level`, `mode`, `subagents`, `task_ref_or_plan_ref`, `short_complexity_rationale`, and `human_gate`.
- Unknown or inapplicable recommendation values use `runtime_dependent` or `not_applicable`; fields are not silently omitted.
- Material Human-facing events require 2 to 5 sentences of clearly separated independent professional expression.
- Codex or Claude Code preserves that expression in the referenced Human Brief; a strict machine-only response remains pointer-only.
- Independent expression is explicitly separated from evidence, authorization, hidden chain-of-thought, executable instructions, and mandatory positivity.
- Omission drift is corrected in the same turn when possible without blaming context or the Human, inventing a cleanup microtask, or discarding valid repository work.
- `ChatGPT-to-Codex` and `Codex-to-ChatGPT` remain frozen historical wire labels used by any compatible occupant of the corresponding role; no key or authority changes.
- Mixed recipients are classified by intended recipient and consumption mode rather than UI/provider brand.
- A separable interface keeps the pointer block byte-structurally isolated and appends Human content outside it.
- A non-separable interface publishes a Human Brief first and emits pointer-only with a non-null resolvable `brief_ref`; the Brief preserves every required Human element, including a complete dispatch recommendation. Missing durable fallback is blocked.

## Authority Preservation

The patch does not grant models new authority. Execution recommendations and independent expression cannot route engines, change objectives, adjudicate protected disputes, approve or publish source/master, activate runtime or Coordinator, handle secrets, authorize destructive work, or resolve a protected Human gate.

Human Speaker authority and the existing safety, evidence, privacy, Git, publication, runtime, Coordinator, bridge, writer, consumer, and destructive-operation boundaries remain intact.

## File-Level Result

- `.ai/PROTOCOL.md`: defines the canonical role mapping, frozen wire-label semantics, three channels, mixed-recipient resolution, material-event contract, expression boundary, preflight, and drift correction.
- `.ai/HANDOFF_COMMON_CONVENTIONS.md`: aligns inherited roles/ownership, dispatch advice, frozen labels, concise Brief/chat rules, and fail-closed mixed fallback.
- `.ai/AUTONOMOUS_HANDOFF_COMMUNICATION_v0.1.md`: aligns scope, roles, channel/state/key compatibility labels, Human Brief behavior, dispatch requirements, and mixed fallback while preserving Human-triggered/no-polling operation.
- `.ai/PROTOCOL_ADHERENCE.md`: applies compatibility during bootstrap/output, adds mixed-recipient enforcement, Human-response preflight, correction-loop checks, and four-occupant onboarding questions.
- `.ai/HANDOFF_INIT_PROMPT.md`: initializes stable role/wire identification and mixed-recipient behavior for ChatGPT, Claude, Codex, and Claude Code without expanding the always-loaded set.
- `.ai/CODEX_WORK_MECHANISM_PROTOCOL.md`: explicitly applies the historical Codex mechanism to compatible Claude Code backend occupants and adds fail-closed mixed-recipient output without weakening quiet output.
- `.ai/DECISIONS.md`: clarifies D-0003 compatibility and records role/wire/mixed-recipient meaning under D-0005.

## Independent Reviews

Three task-authorized read-only reviewers independently checked:

- Human-AI channel separation, pointer purity, and Plan 3 Human Speaker authority;
- Codex/Claude Code output placement, strict machine fallback, and quiet-output compatibility;
- canonical pointer regression, onboarding, chain-of-thought guards, allowlist, and validation scenarios.

Their findings were incorporated into the candidate. The final candidate keeps 8 of 8 canonical pointer definitions unchanged and removes all four pre-existing statements that made backend dispatch recommendations optional.

The same-task correction also used two task-authorized read-only reviewers for provider-neutral role/wire consistency and mixed-recipient/onboarding regression design. Their findings exposed and closed the sole-carrier edge case where a mandatory dispatch recommendation could otherwise be lost during pointer-only fallback.

## Deliberate Non-Changes

- no new standalone source protocol;
- no canonical pointer field additions or reorderings;
- no source mailbox mutation;
- no business or domain file mutation;
- no runtime, Coordinator, polling, or automation activation;
- no source/master publication and no PR creation;
- no unrelated protocol-version migration or legacy decision cleanup.

## Review Request

ChatGPT should review the corrected candidate for provider-neutral role occupancy, frozen wire-schema preservation, mixed-recipient fail-closed behavior, Human Speaker authority, and the validation evidence in `.ai/CODEX_REPORTS/human-ai-communication-expression-protocol-validation-0001.md`.
