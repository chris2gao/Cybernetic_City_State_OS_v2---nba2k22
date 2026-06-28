# Math Mentor LRP-01 Teacher Initialization And Context Loading Report

packet_id: codex-math-mentor-lrp-01-teacher-initialization-context-loading-0001
task_id: math-mentor-lrp-01-teacher-initialization-context-loading-0001
status: completed_for_review
source_branch: dev/protocol-human-cost-and-drift-control-0001
source_head: 2c2e0591f41b9209b6707213516e8ae045c491a2
dev_branch: dev/math-mentor-lrp-01-teacher-initialization-context-loading-0001
master_head: eb918a55becefe609e27723073a38be319f10586
human_gate: required

## Objective

LRP-01 formalizes how a new independent model initializes as a Math Mentor teacher and loads only task-scoped teaching context. It also repairs the narrow Coordinator preflight blocker that required the V9.1 cognitive mapping manual to already be present in the current context.

## Completed Outputs

- `08_Domain_Applications/Math_Mentor/TEACHER_INITIALIZATION_FLOW.md`
- `08_Domain_Applications/Math_Mentor/TEACHER_CONTEXT_LOADING_RULES.md`
- `08_Domain_Applications/Math_Mentor/TEACHER_INITIALIZATION_DRY_RUNS.md`
- narrow update to `08_Domain_Applications/Math_Mentor/08_Math_Mentor_Coordinator_Prompt.md`

## Coordinator Preflight Repair

Old behavior:

- If `V9.1_认知映射引擎_终极实装蓝图.md` was not already physically present in current context, the Coordinator refused to proceed and asked the Human to upload it.

New behavior:

- The Coordinator first checks current context.
- If the manual is absent from current context, it must load `08_Domain_Applications/Math_Mentor/V9.1_认知映射引擎_终极实装蓝图.md` by repository path.
- If the path can be read, it records the path in `actually_read_files` and proceeds.
- If the path cannot be read, it blocks with the exact missing path.

This repair preserves the invariant that the teacher must not invent or claim access to unread files.

## Loading Model

The new documents define:

- City-State bootstrap to Math Mentor payload loading.
- Engine B domain teaching classification.
- Human Speaker authority boundaries.
- Target-node routing.
- Minimal target node, prerequisite, bridge, and learned-history loading.
- `SYSTEM_STATE_DUMP` structure with compressed fields.
- `actually_read_files` evidence requirements.
- context-boundary reload.
- drift recovery reload.
- irreversible drift new-window reset.

## Non-Goals Preserved

This task did not:

- generate Math Mentor nodes;
- generate bridges;
- edit bridge schema;
- mutate `Pure_Math_Intuition_DB`;
- edit evaluator code;
- activate runtime;
- activate production Coordinator;
- start LRP-02 or later LRPs;
- push `master`;
- push the source branch.

## Drift And Human Decision Fields

drift_cause: null
avoided_extra_gates:
  - "file-level microtask split"
  - "separate validation task"
  - "separate report task"
  - "separate handoff task"
final_original_task_status: "completed_for_review"
remaining_real_human_decisions_only:
  - "ChatGPT/Human review of LRP-01 outputs"
  - "future authorization before LRP-02 or later LRPs"
  - "future authorization before source/master publication"
known_followup_candidates:
  - "LRP-02 lesson plan schema and agent contract"
  - "LRP-03 teaching prompt consistency repair"

