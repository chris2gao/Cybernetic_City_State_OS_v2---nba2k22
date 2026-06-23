# Protocol Adherence

## 1. Purpose

An independent ChatGPT or Codex instance must not rely on hidden chat memory, prior-thread assumptions, or unversioned conventions. Repository protocol files are the shared coordination layer for task identity, evidence, authority, execution, Git, review, and output behavior.

This file explains how a new model loads and obeys that layer. It is operational guidance, not a repository constitution or platform-safety override.

## 2. Authority Boundary

Apply instructions in this order:

1. platform, system, and developer instructions;
2. current explicit Human instructions;
3. repository `AGENTS.md` guidance;
4. current repository protocol stack;
5. authenticated current signal and referenced task packet;
6. older project records and historical chat.

Higher-priority safety, privacy, secret, and permission rules always remain active. A current explicit Human instruction may override an older repository convention when they conflict, but repository protocol never overrides platform safety.

## 3. Bootstrap Procedure

At a new model, thread, session, or uncertain context boundary:

1. read `.ai/HANDOFF_INIT_PROMPT.md` first;
2. follow its always-loaded protocol-stack read order;
3. identify the inherited-on-demand protocols and the conditions that trigger them;
4. read repository `AGENTS.md` and load a relevant domain protocol only when the current task triggers it;
5. read `.ai/STATE.yml` and optional `.ai/INBOX.md`;
6. read the current signal;
7. dereference every non-null ref required by that signal;
8. load `.ai/CODEX_WORK_MECHANISM_PROTOCOL.md` for Codex execution tasks and `.ai/CODEX_TASK_INPUT_CONTRACT.md` for long-packet parsing;
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

Codex returns the canonical short handoff defined by `.ai/PROTOCOL.md`. ChatGPT returns the canonical short signal or review decision. Normal model-to-model chat contains pointers, not task bodies, reports, command logs, full diffs, or Human Brief text.

Long Codex output belongs in `.ai/CODEX_REPORTS/*.md`, `.ai/OUTBOX.md`, or another explicitly authorized path. Human-facing status belongs in `.ai/HUMAN_BRIEF.md`.

## 9. Review-Gate Correction Loop

Protocol adherence is enforced by review, not assumption.

When a model misses required refs, writes outside scope, oversteps authority, emits low-value transcript output, uses the wrong task level, or violates the handoff schema, the reviewing model must:

1. mark the result `revise`, `blocked`, or `conflict` as appropriate;
2. identify the exact violated rule and evidence;
3. create a narrow correction task or request the missing input;
4. preserve valid work and avoid broad restart when targeted repair is sufficient;
5. require a new handoff before advancing the stage.

Repeated protocol failure does not silently become accepted behavior.

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

The model should summarize these items without executing the task. Failure to locate a required item produces a blocked onboarding result, not a guessed answer.

An onboarding-only result must not claim that an inherited-on-demand file was loaded when it was only identified. Conversely, an execution task must not omit an inherited protocol whose trigger condition applies.
