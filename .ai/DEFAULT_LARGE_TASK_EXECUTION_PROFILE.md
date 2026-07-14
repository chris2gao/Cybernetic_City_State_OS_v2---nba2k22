# Default Large-Task Execution Profile

Status: active operational profile; non-authorizing routing layer.

## 1. Purpose

This document provides one concise default entrypoint for Human-authorized, multi-step Codex work that should be completed as one coherent task with minimal routine Human interruption.

It consolidates, but does not replace or outrank:

- `.ai/PROTOCOL.md`;
- `.ai/PROTOCOL_ADHERENCE.md`;
- `.ai/CODEX_WORK_MECHANISM_PROTOCOL.md`;
- `.ai/CODEX_TASK_INPUT_CONTRACT.md`;
- `.ai/LONG_RUN_AUTONOMOUS_PROGRAM_PROTOCOL.md`;
- applicable domain-authority protocols.

If this profile conflicts with a canonical protocol, the canonical protocol wins. This profile creates no authority, grants no protected action, and does not activate runtime, Coordinator, automation, source publication, or destructive Git.

## 2. Default Policy

When the Human authorizes one stable outcome and the work is expected to require multiple implementation, validation, reporting, or repair steps, use one completion-preserving large task by default.

The normal lifecycle is:

```text
Human defines and authorizes one coherent objective
        ↓
ChatGPT or Human issues one complete task packet
        ↓
Codex performs preflight and continuous bounded execution
        ↓
Codex validates, commits, and publishes only the authorized development branch
        ↓
Codex returns one consolidated exact-head handoff
        ↓
ChatGPT performs exact-head review
        ↓
If correction is needed, Codex continues the same task on the same branch
        ↓
Human decides only the remaining protected publication or policy gates
```

Routine internal progress is not a Human gate.

## 3. When This Profile Applies

Use this profile when all of the following are true:

1. the objective and definition of done are stable enough for Goal mode;
2. implementation or durable artifact creation is explicitly authorized;
3. the task is likely to require multiple files, commands, tests, checkpoints, or repair passes;
4. allowed branches, paths, actions, validation, and stop rules can be bounded before launch;
5. discovered cleanup, validation, report, handoff, or repair work can remain inside the same objective.

Typical examples:

- multi-file implementation with tests;
- protocol or architecture landing across several related artifacts;
- evaluator, schema, registry, or migration work;
- bounded corpus repair or certification batches;
- control-plane hardening;
- exact-head review correction on an existing task branch.

Do not use this profile to bypass unresolved product, mathematical, legal, privacy, security, or architecture decisions. Use Plan mode first when the objective itself is still disputed or materially ambiguous.

## 4. One Objective, Not One Giant Permission

A large task is large because completion work is consolidated, not because permissions are broad.

Every task must still bind:

- exact source branch and immutable source head;
- one stable task ID;
- one coherent objective;
- observable definition of done;
- exact or bounded allowed paths;
- explicit forbidden paths and protected classes;
- allowed actions and publication boundary;
- validation and evidence requirements;
- stop-only conditions;
- final handoff contract.

Missing permission means the action is not authorized.

## 5. Completion-Preserving Rule

Codex internalizes work that is necessary to complete the original authorized objective when that work remains safe and within scope.

The following normally remain inside the same task:

- required reading and bounded discovery;
- implementation;
- local refactoring needed by the implementation;
- cleanup caused by the implementation;
- focused and proportional validation;
- safe retry and repair after test failure;
- exact changed-path verification;
- report and evidence generation;
- explicit-path staging;
- authorized development-branch commit and non-force push;
- review mailbox or handoff update;
- post-push exact-head readback;
- same-task correction after ChatGPT review.

Do not create separate readiness, candidate, closure, cleanup, validation, report, handoff, finalize, or mailbox-neutralization tasks when those steps are already necessary and authorized parts of the original objective.

Internal checkpoints are evidence boundaries, not routine Human gates.

## 6. Real Stop Conditions

Stop or return `completed_with_blockers` only when continuing requires one or more of the following:

- new Human authority;
- an objective change;
- source or master push without explicit approval;
- destructive or irreversible Git;
- force push;
- secrets, credentials, privacy, or security-sensitive access;
- runtime activation;
- Coordinator activation;
- unattended mutation or automation enablement;
- mutation outside the allowed paths;
- a protected file required for completion but not authorized;
- source/master head mismatch against the approved baseline;
- new domain authority or disputed high-impact semantics;
- validation failure after bounded safe retry;
- a blocker that prevents all safe independent progress.

For local non-blocking issues:

- record the issue;
- quarantine only the affected item or subgraph;
- continue independent authorized work;
- report unresolved items in the consolidated handoff.

## 7. Default Review-Correction Loop

ChatGPT exact-head review is part of the original workflow, not a new project phase.

When ChatGPT identifies defects that remain inside the original objective and authorization:

1. keep the same `task_id`;
2. keep the same development branch unless a real branch conflict requires otherwise;
3. identify the rejected exact candidate head;
4. preserve accepted components;
5. issue one consolidated continuation packet;
6. add ordinary non-force correction commits;
7. rerun all affected and regression validation;
8. return a new exact candidate head;
9. do not create artificial `P0.1`, `finalize`, `closure`, or similar micro-phases.

A new task is appropriate only when the objective, authority, protected action, domain decision, or allowed mutation surface genuinely changes.

## 8. Default Publication Boundary

Unless the current Human instruction explicitly says otherwise:

```yaml
publication_policy:
  local_commit_authorized: true
  development_branch_push_authorized: true
  source_branch_push_authorized: false
  master_push_authorized: false
  force_push_authorized: false
  chatgpt_exact_head_review_required: true
  human_gate_after_review: required
```

A development-branch push is not source publication.

Source publication, master merge, protected-branch update, or runtime activation remains separately Human-gated even when all implementation tests pass.

## 9. Default Task Packet

Use the canonical fields from `.ai/CODEX_TASK_INPUT_CONTRACT.md`. The following profile is the recommended large-task expansion:

```yaml
decision: start_task
task_id: <stable-task-id>
task_type: <explicit-task-type>
human_gate: required_after_completion

base:
  branch: <source-branch>
  head: <immutable-full-sha>

work_branch:
  name: <authorized-development-branch>
  create_from_exact_base_only: true
  non_force_push_only: true

objective:
  Complete the original Human-authorized outcome as one coherent objective.

definition_of_done:
  - <observable result>
  - <required validation result>
  - <required durable report or handoff>

completion_policy:
  completion_preserving: true
  finish_original_task_A: true
  do_not_fragment_into_micro_tasks: true
  fold_required_reading_implementation_cleanup_validation_reporting_commit_dev_push_and_handoff_into_this_task: true
  same_task_review_correction: true

scope:
  allowed_paths: []
  forbidden_paths: []
  allowed_actions: []

must_do:
  - verify exact base and clean or understood worktree
  - read required protocols and bounded domain evidence
  - implement only within authorized scope
  - validate proportionally to blast radius
  - stage explicit paths only
  - commit intentionally
  - push only the authorized development branch
  - read back the remote exact head
  - return one consolidated handoff

must_not_do:
  - no git add .
  - no push --all
  - no force push
  - no source or master push unless explicitly authorized
  - no secrets or credentials
  - no unrelated mutation
  - no runtime activation unless explicitly authorized
  - no Coordinator activation unless explicitly authorized
  - no destructive Git unless explicitly authorized

only_stop_for:
  - missing Human authority
  - source or master head mismatch
  - destructive or irreversible operation
  - force push requirement
  - secrets/privacy/security risk
  - runtime or Coordinator activation
  - forbidden path mutation
  - objective change
  - new domain-authority decision
  - validation failure after bounded safe retry
  - whole-task blocker

validation:
  - <focused tests>
  - <regression tests>
  - exact changed-path verification
  - git diff --check
  - scoped credential scan
  - remote development-branch readback
  - remote source branch unchanged readback

publication_policy:
  development_branch_push_authorized: true
  source_branch_push_authorized: false
  master_push_authorized: false
  chatgpt_exact_head_review_required: true

return_handoff:
  packet_id:
  status:
  report_ref:
  validation_ref:
  changed_files_ref:
  work_branch:
  candidate_head:
  source_head:
  exact_changed_paths:
  tests:
  unresolved_blockers:
  drift_cause:
  avoided_extra_gates:
  final_original_task_status:
  remaining_real_human_decisions_only:
  human_gate:
```

Omit irrelevant optional fields, but never omit a material permission, protected boundary, or stop condition.

## 10. Preflight Requirements

Before execution, Codex verifies and records:

- current Human authorization and task identity;
- source branch and exact source head;
- development branch ownership and creation base;
- required refs and protocol inheritance;
- allowed and forbidden paths;
- publication policy;
- baseline tests or known failure counts;
- optional dependencies and fallback behavior;
- clean or explicitly understood worktree state;
- rollback point;
- exact final validation commands;
- whether parallel work could overlap the branch or paths.

Known mandatory blockers are resolved before implementation begins. Do not start a partial run merely to rediscover a preflight blocker later.

## 11. Git And Branch Isolation

For long tasks:

- use a dedicated development branch;
- create it from the exact approved source head;
- do not reuse another active task's branch;
- avoid editing the branch currently owned by another Codex run;
- use explicit-path staging;
- prefer domain-coherent commits;
- never force push;
- do not move local or remote master merely to prepare the task;
- verify the remote development branch after push;
- verify the protected source branch remains unchanged when publication is not authorized.

When two tasks overlap in files or semantic ownership, serialize them or obtain a new Human decision. Branch separation alone does not make conflicting semantic edits safe.

## 12. Context And Reporting Budget

Large tasks should reduce Human interaction without producing unbounded transcripts.

Codex should:

- lazy-load only required repository evidence;
- use internal checkpoints and concise issue logs;
- avoid repeated status polling and repeated broad scans;
- report partial findings internally unless they trigger a real stop;
- publish one consolidated candidate report;
- include exact heads, changed paths, commands, results, limitations, and unresolved Human decisions;
- distinguish implementation evidence from runtime, production, mathematical, or semantic claims.

The final handoff must be pointer-first and exact-head bound. Large raw logs belong in durable report artifacts, not in the chat response.

## 13. Human-Cost And Drift Recovery

If a task begins fragmenting:

1. acknowledge the drift without defending it;
2. identify the original Human-authorized objective;
3. collapse cleanup, validation, repair, reporting, and handoff back into that objective when still authorized;
4. issue one consolidated continuation packet;
5. preserve the same task ID and branch when safe;
6. list only real remaining Human decisions.

Required final fields for drift-prone work:

```yaml
drift_cause: <reason-or-null>
avoided_extra_gates: []
final_original_task_status: completed | completed_with_blockers | blocked | superseded
remaining_real_human_decisions_only: []
```

## 14. Relationship To Long-Run Programs

This profile is the default operational wrapper for ordinary large tasks.

Use `.ai/LONG_RUN_AUTONOMOUS_PROGRAM_PROTOCOL.md` in full when the work additionally needs:

- an explicit multi-stage program graph;
- internal batch checkpoints across a large corpus;
- rollback across many stages;
- a long-run issue ledger;
- local-only execution after launch;
- completion statuses such as `completed_with_review_log` or `failed_and_reverted`.

Every Long-Run Autonomous Program is a large task. Not every large task requires the full autonomous-program machinery.

## 15. Non-Goals

This profile does not:

- create standing Codex autonomy;
- authorize work merely because it is useful;
- let Codex redefine the Human objective;
- let ChatGPT or Codex authenticate its own Human approval;
- authorize source/master publication;
- authorize secrets access or destructive Git;
- authorize runtime, Coordinator, bridge, or unattended automation activation;
- replace semantic review or Human adjudication;
- turn test success into production readiness.

## 16. Canonical Default

Unless the Human explicitly requests small-step review, an authorized large task should use:

```yaml
mode: goal
completion_policy: completion_preserving
human_interruption_policy: real_gates_only
review_policy: exact_head_then_same_task_correction
publication_policy: development_branch_only_until_explicit_human_approval
```

The governing principle is:

> Complete the Human-authorized objective with the fewest avoidable Human interventions, while preserving exact authority, scope, evidence, and protected gates.
