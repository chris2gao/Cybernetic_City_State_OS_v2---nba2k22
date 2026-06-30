# Protocol Human Cost And Drift Control Report

packet_id: codex-protocol-human-cost-and-drift-control-0001
task_id: protocol-human-cost-and-drift-control-0001
status: completed_for_review
dev_branch: dev/protocol-human-cost-and-drift-control-0001
master_head: eb918a55becefe609e27723073a38be319f10586
human_gate: required

## Objective

Add a protocol-level Human Cost And Drift Control Rule so future Human-authorized tasks are completed as coherent units instead of being split into avoidable micro-tasks.

## Protocol Updates

Updated the required protocol surfaces:

- `.ai/LONG_RUN_AUTONOMOUS_PROGRAM_PROTOCOL.md`
- `.ai/CODEX_WORK_MECHANISM_PROTOCOL.md`
- `.ai/CODEX_TASK_INPUT_CONTRACT.md`

The rule now states that Human time, attention, and token budget are protected project resources.

## Effective Behavior

When a task is already authorized, Codex and ChatGPT should keep necessary cleanup, validation, report writing, mailbox neutralization, authorized branch commit and push, post-publication verification, and protocol alignment inside the original task when those steps remain safe and within scope.

Routine internal checkpoints should not become separate Human gates. Separate gates remain required for new authority, objective changes, destructive Git, source or master push without explicit approval, secrets or privacy risk, runtime or Coordinator activation, forbidden paths, new domain authority, or whole-task blockers.

## Drift Recovery Fields

Recovered or drift-prone task reports should include:

- `drift_cause`
- `avoided_extra_gates`
- `final_original_task_status`
- `remaining_real_human_decisions_only`

## Drift Control Evidence

drift_cause: "Prior workflows sometimes converted cleanup, validation, handoff, and closure into separate prompts after the original task was already authorized."
avoided_extra_gates:
  - "routine cleanup gate"
  - "routine validation gate"
  - "routine mailbox-neutralization gate"
  - "routine closure/readiness gate"
final_original_task_status: "completed_for_review"
remaining_real_human_decisions_only:
  - "Human review of this protocol patch"
  - "Any future source/master publication or protected runtime action"

## Non-Goals Preserved

This task did not authorize or perform:

- Math Mentor generation;
- bridge generation;
- node mutation;
- evaluator mutation;
- runtime activation;
- Coordinator activation;
- source branch push;
- master push;
- force push.
