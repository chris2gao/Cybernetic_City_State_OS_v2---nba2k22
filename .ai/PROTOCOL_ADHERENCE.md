# Protocol Adherence

## 1. Purpose

A compatible foreground or backend model instance—currently ChatGPT or Claude in the foreground role and Codex or Claude Code in the backend role—must not rely on hidden chat memory, prior-thread assumptions, or unversioned conventions. Repository protocol files are the shared coordination layer for task identity, evidence, authority, execution, Git, review, and output behavior.

This file explains how a new model loads and obeys that layer. It is operational guidance, not a repository constitution or platform-safety override.

## 2. Instruction Authority And State Freshness

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

Freshness establishes state only; it does not grant mutation or publication authority. Report authority conflicts separately from freshness conflicts. Higher-priority safety, privacy, secret, and permission rules always remain active.

## 3. Bootstrap Procedure

At a new model, thread, session, or uncertain context boundary:

1. read `.ai/HANDOFF_INIT_PROMPT.md` first;
2. follow its always-loaded protocol-stack read order;
3. identify the inherited-on-demand protocols and the conditions that trigger them;
4. read repository `AGENTS.md` and load a relevant domain protocol only when the current task triggers it;
5. read `.ai/STATE.yml` and optional `.ai/INBOX.md`;
6. read the current signal;
7. dereference every non-null ref required by that signal;
8. load `.ai/CODEX_WORK_MECHANISM_PROTOCOL.md` for backend execution-role tasks, whether occupied by Codex or Claude Code, and `.ai/CODEX_TASK_INPUT_CONTRACT.md` for long-packet parsing;
9. confirm source head, Human gate, task level, output, and next action before execution.

For a Human-authorized long-duration program, load `.ai/LONG_RUN_AUTONOMOUS_PROGRAM_PROTOCOL.md` before preflight. A long-run launch must pass its preflight-first rule and carry the complete project-level permission pre-grant before any execution stage begins.

Do not assume previous chat context. Durable repository state and authenticated external state are authoritative.

## 4. Fast-Path Procedure

In a continuous review loop with unchanged protocol and intact context, read only:

1. `.ai/STATE.yml`;
2. `.ai/INBOX.md` when it is needed to locate the current signal;
3. the current signal;
4. each non-null ref required for the current task or review.

Do not reload the full protocol stack unless the protocol head changed, context was lost or uncertain, a pointer is malformed/contradictory, automation starts a fresh run, or the current task explicitly requires reinitialization.

## 5. Mandatory Dereference Rule

Before acting, read every non-null `packet_ref`, `task_ref`, `report_ref`, `brief_ref`, and `detail_ref` applicable to the message intent.

If a required ref is missing:

- check that exact path once at the observed review head;
- return `blocked` with the missing ref and required sender action;
- do not infer task intent from the filename or chat history;
- do not inspect unrelated files;
- retry only after a new signal or changed review head.

Missing protocol input is not an execution repair-budget failure.

## 6. Task Input Contract Compliance

Short signals carry identity, decision, pointers, source head, and Human gate. Long goals and execution detail live in `.ai/TASKS/*.md` or `.ai/USER_UPLOADS/*.md`.

Future long task packets follow `.ai/CODEX_TASK_INPUT_CONTRACT.md`. They declare the task goal, mode, task level, definition of done, evidence refs, output paths, and return identity. They add allowed/forbidden files, validation, stop rules, semantic reviewer, local files, or overrides only when the task needs them.

Do not reconstruct missing long-task intent from a filename, old chat, or adjacent work.

## 7. Local-First Execution Rule

Use the normal successful path:

1. perform one initial signal/ref read;
2. work directly in authorized local files;
3. run one consolidated validation proportional to task level;
4. create one source commit/checkpoint when source files changed;
5. publish one review handoff when review is required;
6. return the canonical short handoff.

Do not perform defensive remote/status/diff checks repeatedly. Re-check remote state only when a required ref is missing, publication fails, a real conflict is detected, or a Human gate is triggered.

### Long-Run Exception

An authorized Long-Run Autonomous Program follows `.ai/LONG_RUN_AUTONOMOUS_PROGRAM_PROTOCOL.md`. It may resolve current remote refs before launch, but after the launch checkpoint it performs no GitHub fetch, push, polling, or API call until final publication. Internal small batches and checkpoints do not create repeated Human gates when the launch packet already pre-grants their project-level permissions.

## 8. Output Schema Compliance

The backend execution-and-handoff occupant returns the canonical Codex-to-ChatGPT wire handoff defined by `.ai/PROTOCOL.md`. The foreground review-and-task-dispatch occupant returns the canonical ChatGPT-to-Codex wire signal or review decision. Claude and Claude Code use those frozen schemas according to role. Normal model-to-model chat contains pointers, not task bodies, reports, command logs, full diffs, or Human Brief text.

Long backend-role output belongs in `.ai/CODEX_REPORTS/*.md`, `.ai/OUTBOX.md`, or another explicitly authorized path. Human-facing status belongs in `.ai/HUMAN_BRIEF.md`.

Machine pointer output and Human operational output are separate channels. Classify mixed-recipient output by intended recipient and consumption mode, not UI/provider brand. When Human and machine recipients share an interface, keep the canonical pointer block byte-structurally separate and append Human operational content outside it. If safe separation is impossible, publish the Human Brief first, emit pointer-only with a non-null resolvable `brief_ref`, and preserve every required Human element there—including a complete recommendation for backend dispatch; otherwise return blocked.

A material Human-facing response must provide grounded factual status, the canonical pointer when dispatching or handing off, bounded independent expression, and—when the Human is expected to start or continue Codex or Claude Code—a complete execution recommendation. The recommendation and expression remain outside the canonical seven-field pointer core.

## 9. Review-Gate Correction Loop

Protocol adherence is enforced by review, not assumption.

When a model misses required refs, writes outside scope, oversteps authority, emits low-value transcript output, uses the wrong task level, violates the handoff schema, omits a required backend execution recommendation, omits required independent expression, or fails to separate it from evidence and authority, the reviewing model must:

1. mark the result `revise`, `blocked`, or `conflict` as appropriate;
2. identify the exact violated rule and evidence;
3. create a narrow correction task or request the missing input;
4. preserve valid work and avoid broad restart when targeted repair is sufficient;
5. require a new handoff before advancing the stage.

Repeated protocol failure does not silently become accepted behavior.

For a Human-facing completeness omission, acknowledge protocol drift plainly and correct the response in the same turn when possible. Do not blame context length or the Human. Do not create a fake cleanup/finalize microtask solely to restore an omitted chat section, and preserve valid repository work. If the durable source protocol itself is deficient, use one coherent reviewed protocol-correction task.

### Human-Response Preflight

Before sending a material Human-facing response, verify:

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

The execution recommendation must contain `recommended_model`, `recommended_thinking_level`, `mode`, `subagents`, `task_ref_or_plan_ref` resolving to exactly one applicable durable ref, `short_complexity_rationale`, and `human_gate`; use `runtime_dependent` or `not_applicable` instead of omission. Independent expression is 2 to 5 sentences, visibly separated from evidence and authority, and possesses no authorization or gate-resolving force.

### Executable Gate Check

Before advancing a durable `C1` or protected `C2` workflow event, run `.ai/communication_compliance/validate_communication.py` as documented in `.ai/communication_compliance/README.md`. Transition proof must physically resolve the immutable event, actual STATE and ordered pointer, bind STATE to a trusted externally observed current review head, and recompute event validation including receipts and every required ref. A stored result is optional comparison evidence and cannot self-authorize; if present it must equal the fresh result in canonical bytes and semantics. Human-origin context, active-state context, and C2 authorization context are externally injected, separate, and non-interchangeable.

`C0` ordinary discussion does not require this artifact. `C2` additionally requires a separately injected trusted-host Human `AuthorizationContext`; payload `human_gate` fields, independent expression, pointers, and validator output cannot authorize the action. The gate reports eligibility only and must not be represented as live middleware or an executed state change.

## 10. Minimal Audit Checklist

Before claiming completion or approval, verify:

- [ ] required protocol state and every non-null ref were read;
- [ ] source head and Human gate matched the intended action;
- [ ] the lowest sufficient task/Git level was used;
- [ ] allowed and forbidden file/action scope was respected;
- [ ] no unauthorized source push, destructive Git, secret access, or gated transition occurred;
- [ ] validation matched the task level and definition of done;
- [ ] mailbox artifacts and canonical short handoff were produced when required;
- [ ] detailed output was written to durable files instead of pasted into chat.
- [ ] the Human-response preflight passed for every material Human-facing event;
- [ ] every proposed C1/C2 transition carried a passing recomputed physical proof chain and trusted active-state anchor; Human events carried authenticated origin, and any C2 transition also carried separate external Human authority;
- [ ] a backend execution recommendation contained every required field when the Human was asked to start or continue Codex or Claude Code;
- [ ] bounded independent expression was present, separated from evidence/authority, and preserved through `brief_ref` when the machine channel had to stay pointer-only;
- [ ] no hidden chain-of-thought was requested or disclosed;
- [ ] a long-run task, if applicable, passed preflight, used an explicit permission pre-grant, remained local-only after launch, and produced its long-run log.

## 11. New Model Onboarding Test

A new independent model passes onboarding when, after reading `.ai/HANDOFF_INIT_PROMPT.md`, it can identify from durable evidence:

1. repository and active source branch;
2. its current role and authority boundary;
3. `always_loaded_protocol_files`: the files actually read during initialization;
4. `inherited_on_demand_protocol_files`: known inherited protocols, their trigger conditions, and whether they were loaded for the current task;
5. current workflow state and current signal;
6. every non-null ref that must be read;
7. current Human gate;
8. next required action, task level, and canonical response shape.

It must also be able to answer:

9. how the machine pointer, Human operational, and durable Human Brief channels differ;
10. when a backend execution recommendation is mandatory and which seven fields it contains;
11. when bounded independent expression is required and when it may be waived;
12. where Codex or Claude Code preserves expression without changing the pointer schema;
13. which authority independent expression does not possess;
14. how to correct a Human-facing omission without inventing a cleanup microtask or discarding valid work.
15. which stable protocol role it occupies and which frozen wire schema that role uses, whether the instance is ChatGPT, Claude, Codex, or Claude Code;
16. how a mixed Human+machine recipient interface preserves structural separation or falls back to pointer-only plus `brief_ref`.

The model should summarize these items without executing the task. Failure to locate a required item produces a blocked onboarding result, not a guessed answer.

An onboarding-only result must not claim that an inherited-on-demand file was loaded when it was only identified. Conversely, an execution task must not omit an inherited protocol whose trigger condition applies.
