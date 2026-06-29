---
task_version: "1.0"
task_id: "math-mentor-lrp-05-student-learning-state-spaced-review-0001"
title: "Math Mentor LRP-05 Student Learning State And Spaced Review"
mode: "goal"
task_level: 2

intent:
  goal: "Complete LRP-05 by defining the persistent student learning-state schema, spaced-review scheduler schema, learned-history rules, and long-term graduation criteria for Math Mentor without writing real student state or activating any scheduler/runtime."
  why_now: "LRP-01 closed initialization/loading, LRP-02 closed lesson_plan and agent contracts, LRP-03 aligned prompts, and LRP-04 created regression tests. The next blocker is that the system still needs a precise persistent-state contract so classroom_passed is not confused with long-term mastery and bridge learned status can be grounded in persisted evidence."
  definition_of_done:
    - "STUDENT_LEARNING_STATE_SCHEMA.md exists and defines durable student learning-state records, allowed status transitions, evidence fields, and privacy boundaries."
    - "SPACED_REVIEW_SCHEDULER_SCHEMA.md exists and defines review scheduling records, due dates/windows, review result transitions, scheduler warnings/placeholders, and no-runtime boundaries."
    - "LEARNED_HISTORY_RULES.md exists and defines how learned status is read, prioritized, degraded when unavailable, and used for bridge-slot gating."
    - "GRADUATION_CRITERIA.md exists and defines why classroom_passed is not graduated, how review_passed accumulates, and when long-term graduation may be claimed."
    - "The new documents preserve LRP-01 lazy loading, LRP-02 lesson/exam contracts, LRP-03 prompt behavior, LRP-04 test boundaries, and Plan 3 Human Speaker authority."
    - "Validation and handoff reports are produced."

outputs:
  primary: "08_Domain_Applications/Math_Mentor/STUDENT_LEARNING_STATE_SCHEMA.md"
  additional:
    - "08_Domain_Applications/Math_Mentor/SPACED_REVIEW_SCHEDULER_SCHEMA.md"
    - "08_Domain_Applications/Math_Mentor/LEARNED_HISTORY_RULES.md"
    - "08_Domain_Applications/Math_Mentor/GRADUATION_CRITERIA.md"
    - ".ai/CODEX_REPORTS/math-mentor-lrp-05-student-learning-state-spaced-review-0001.md"
    - ".ai/CODEX_REPORTS/math-mentor-lrp-05-student-learning-state-validation-0001.md"
    - ".ai/CODEX_REPORTS/math-mentor-lrp-05-student-learning-state-changed-files-0001.md"
    - ".ai/CODEX_REPORTS/math-mentor-lrp-05-student-learning-state-actually-read-files-0001.md"

inputs:
  required_refs:
    - ".ai/TASKS/math-mentor-lrp-05-student-learning-state-spaced-review-0001.md"
    - "08_Domain_Applications/Math_Mentor/Math Mentor Teaching System Design implement plan.md"
    - "08_Domain_Applications/Math_Mentor/Math Mentor Teaching System Design.md"
    - "08_Domain_Applications/Math_Mentor/TEACHER_INITIALIZATION_FLOW.md"
    - "08_Domain_Applications/Math_Mentor/TEACHER_CONTEXT_LOADING_RULES.md"
    - "08_Domain_Applications/Math_Mentor/TEACHER_INITIALIZATION_DRY_RUNS.md"
    - "08_Domain_Applications/Math_Mentor/LESSON_PLAN_SCHEMA.md"
    - "08_Domain_Applications/Math_Mentor/TEACHING_AGENT_CONTRACTS.md"
    - "08_Domain_Applications/Math_Mentor/EXAM_HANDOFF_STATE_VECTOR_SCHEMA.md"
    - "08_Domain_Applications/Math_Mentor/BRIDGE_SLOT_TEACHING_CONTRACT.md"
    - "08_Domain_Applications/Math_Mentor/TEACHING_PROMPT_CONSISTENCY_AUDIT.md"
    - "08_Domain_Applications/Math_Mentor/TEACHING_SYSTEM_TEST_PLAN.md"
    - "08_Domain_Applications/Math_Mentor/TEACHING_GOLDEN_CASES.md"
    - "08_Domain_Applications/Math_Mentor/TEACHER_INITIALIZATION_TEST_FIXTURES.md"
    - "08_Domain_Applications/Math_Mentor/E2E_TEACHING_SESSION_SIMULATION.md"
    - "08_Domain_Applications/Math_Mentor/08_Math_Mentor_Coordinator_Prompt.md"
    - "08_Domain_Applications/Math_Mentor/学习期prompt/Prep_Architect_Prompt.md"
    - "08_Domain_Applications/Math_Mentor/学习期prompt/Socratic_Router_Prompt_v7.0.md"
    - "08_Domain_Applications/Math_Mentor/学习期prompt/Exam_Agent_Prompt.md"
    - "08_Domain_Applications/Math_Mentor/V9.1_教学流程系统规范_Teaching_Flow_Spec.md"
    - "08_Domain_Applications/Math_Mentor/V9.1_认知映射引擎_终极实装蓝图.md"
    - "08_Domain_Applications/Math_Mentor/Math_Mentor_V9.1_从生成到教学的完整流程.md"
    - "08_Domain_Applications/Math_Mentor/BRIDGE_SCHEMA.md"
    - "3号方案.md"
    - "06_Silicon_Index/AI_Bootstrap_Sequence.md"
    - "06_Silicon_Index/06_Cybernetic_Citizen_Awakening.md"
    - ".ai/PROTOCOL.md"
    - ".ai/CODEX_WORK_MECHANISM_PROTOCOL.md"
    - ".ai/CODEX_TASK_INPUT_CONTRACT.md"
    - ".ai/LONG_RUN_AUTONOMOUS_PROGRAM_PROTOCOL.md"

scope:
  source_branch: "dev/protocol-human-cost-and-drift-control-0001"
  working_branch:
    name: "dev/math-mentor-lrp-05-student-learning-state-spaced-review-0001"
    create_from: "the exact source_head in the short signal that points to this task packet"
  allowed_files:
    - "08_Domain_Applications/Math_Mentor/STUDENT_LEARNING_STATE_SCHEMA.md"
    - "08_Domain_Applications/Math_Mentor/SPACED_REVIEW_SCHEDULER_SCHEMA.md"
    - "08_Domain_Applications/Math_Mentor/LEARNED_HISTORY_RULES.md"
    - "08_Domain_Applications/Math_Mentor/GRADUATION_CRITERIA.md"
    - ".ai/CODEX_REPORTS/math-mentor-lrp-05-student-learning-state-spaced-review-0001.md"
    - ".ai/CODEX_REPORTS/math-mentor-lrp-05-student-learning-state-validation-0001.md"
    - ".ai/CODEX_REPORTS/math-mentor-lrp-05-student-learning-state-changed-files-0001.md"
    - ".ai/CODEX_REPORTS/math-mentor-lrp-05-student-learning-state-actually-read-files-0001.md"
    - ".ai/OUTBOX.md"
    - ".ai/HUMAN_BRIEF.md"
    - ".ai/STATE.yml"
  forbidden_files:
    - "08_Domain_Applications/Math_Mentor/Pure_Math_Intuition_DB/**"
    - "08_Domain_Applications/Math_Mentor/bridges/**"
    - "08_Domain_Applications/Math_Mentor/BRIDGE_SCHEMA.md"
    - "08_Domain_Applications/Math_Mentor/BRIDGE_REGISTRY*.md"
    - "08_Domain_Applications/Math_Mentor/KNOWLEDGE_COMPLETION_PROGRAM.md"
    - "08_Domain_Applications/Math_Mentor/LESSON_PLAN_SCHEMA.md"
    - "08_Domain_Applications/Math_Mentor/TEACHING_AGENT_CONTRACTS.md"
    - "08_Domain_Applications/Math_Mentor/EXAM_HANDOFF_STATE_VECTOR_SCHEMA.md"
    - "08_Domain_Applications/Math_Mentor/BRIDGE_SLOT_TEACHING_CONTRACT.md"
    - "08_Domain_Applications/Math_Mentor/TEACHER_INITIALIZATION_FLOW.md"
    - "08_Domain_Applications/Math_Mentor/TEACHER_CONTEXT_LOADING_RULES.md"
    - "08_Domain_Applications/Math_Mentor/TEACHER_INITIALIZATION_DRY_RUNS.md"
    - "08_Domain_Applications/Math_Mentor/TEACHING_PROMPT_CONSISTENCY_AUDIT.md"
    - "08_Domain_Applications/Math_Mentor/TEACHING_SYSTEM_TEST_PLAN.md"
    - "08_Domain_Applications/Math_Mentor/TEACHING_GOLDEN_CASES.md"
    - "08_Domain_Applications/Math_Mentor/TEACHER_INITIALIZATION_TEST_FIXTURES.md"
    - "08_Domain_Applications/Math_Mentor/E2E_TEACHING_SESSION_SIMULATION.md"
    - "08_Domain_Applications/Math_Mentor/08_Math_Mentor_Coordinator_Prompt.md"
    - "08_Domain_Applications/Math_Mentor/学习期prompt/Prep_Architect_Prompt.md"
    - "08_Domain_Applications/Math_Mentor/学习期prompt/Socratic_Router_Prompt_v7.0.md"
    - "08_Domain_Applications/Math_Mentor/学习期prompt/Exam_Agent_Prompt.md"
    - "08_Domain_Applications/Math_Mentor/数学间隔重复调度表.md"
    - "08_Domain_Applications/Math_Mentor/STUDENT_LEARNING_STATE/**"
    - "08_Domain_Applications/Math_Mentor/LEARNED_HISTORY/**"
    - "未完成任务备忘录.yml"
  allowed_actions:
    - "create the working branch from the exact source head"
    - "read required refs"
    - "create the four LRP-05 schema/rules documents"
    - "write consolidated reports"
    - "commit explicit paths on the working branch"
    - "push only the working branch"
    - "publish final handoff to ai/review/latest"
  forbidden_actions:
    - "git reset --hard unless the Human explicitly authorizes it in this task"
    - "force push"
    - "push --all"
    - "git add ."
    - "source branch push"
    - "master push"
    - "runtime activation"
    - "production Coordinator activation"
    - "node generation"
    - "bridge generation"
    - "bridge schema mutation"
    - "prompt mutation"
    - "schema mutation outside the four LRP-05 outputs"
    - "evaluator mutation"
    - "actual student-state write"
    - "actual learned-history write"
    - "actual spaced-review scheduler write"

requirements:
  invariants:
    - "Plan 3 Human Speaker authority remains the top-level route, translation, and final-decision model."
    - "Math Mentor teaching remains an Engine B domain teaching task; deterministic tools may support but not replace teaching judgment."
    - "LRP-01 lazy-loading and actually_read_files evidence rules remain the context-loading baseline."
    - "LRP-02 lesson_plan and Exam handoff contracts remain the upstream classroom evidence baseline."
    - "LRP-03 prompt behavior remains the production-prompt alignment baseline."
    - "LRP-04 test harness remains the anti-regression baseline."
    - "classroom_passed is not graduated."
    - "node id ordering cannot prove mastery except as an explicitly bounded strict-sequential fallback."
    - "bridge slot learned status must be read from persisted state, spaced-review state, registered learned state, or an explicitly valid fallback; unavailable state must degrade to unavailable/hidden/teaser, not mastery."
    - "No document may claim a real student-state write, scheduler update, runtime activation, Coordinator activation, or external tool execution occurred."
    - "Completion-preserving execution is mandatory: read, design, create docs, validate, report, commit, branch push, and handoff are one task."
  required_status_model:
    learning_status:
      - "not_seen"
      - "introduced"
      - "classroom_passed"
      - "review_due"
      - "review_passed"
      - "graduated"
      - "stale"
      - "blocked"
  required_documents:
    student_learning_state_schema:
      - "student/session identity fields with privacy-safe placeholders"
      - "per-node learning record"
      - "status transitions"
      - "evidence provenance"
      - "Exam_Agent classroom pass evidence"
      - "bridge learned-status read model"
      - "privacy and secret boundaries"
    spaced_review_scheduler_schema:
      - "review item record"
      - "schedule generation placeholder"
      - "due/review windows"
      - "review result transitions"
      - "scheduler unavailable warning"
      - "no write without future authorization"
    learned_history_rules:
      - "evidence priority order"
      - "persisted state read rule"
      - "classroom_passed as minimum classroom criterion only"
      - "node id ordering fallback limitations"
      - "missing learned-history degradation"
      - "bridge slot gating"
    graduation_criteria:
      - "classroom_passed != graduated"
      - "minimum review pass requirements"
      - "stability over time"
      - "trap/definition boundary retention"
      - "downgrade/stale criteria"
      - "graduation claim wording constraints"
  validation:
    - "all required refs were read or any missing ref is explicitly reported with path, branch, and failure reason"
    - "the four new LRP-05 documents exist on the working branch"
    - "STUDENT_LEARNING_STATE_SCHEMA.md defines all required learning_status values and allowed transitions"
    - "STUDENT_LEARNING_STATE_SCHEMA.md includes evidence provenance and privacy-safe placeholders"
    - "SPACED_REVIEW_SCHEDULER_SCHEMA.md defines scheduler records, due windows, review result transitions, and unavailable-scheduler warning"
    - "LEARNED_HISTORY_RULES.md defines evidence priority and bridge-slot learned-status gating"
    - "GRADUATION_CRITERIA.md states classroom_passed is not graduated and defines review-based graduation criteria"
    - "documents explicitly reject node-id ordering as mastery proof except bounded strict-sequential fallback"
    - "documents require warning/placeholder when scheduler or persisted state is unavailable"
    - "documents do not claim actual student-state, learned-history, or scheduler writes"
    - "changed files are limited to allowed_files"
    - "forbidden_files are not modified"
    - "no git reset --hard is used"
    - "scoped secret scan passes"
    - "remote read-back verifies the pushed working branch and report refs"
  stop_rules:
    - "source head mismatch before working branch creation"
    - "required refs missing in a way that prevents safe state-schema design"
    - "need to modify forbidden files"
    - "need to alter LRP-01, LRP-02, LRP-03, or LRP-04 artifacts instead of creating LRP-05 schemas/rules"
    - "need for actual student-state writes, learned-history writes, spaced-review scheduler writes, node generation, bridge generation, bridge schema mutation, prompt mutation, evaluator mutation, runtime activation, or Coordinator activation"
    - "need to use git reset --hard"
    - "security/privacy/secret risk"
    - "merge/master/source publication requirement not authorized by this task"
    - "validation failure after one safe repair pass"

authority:
  semantic_reviewer: "chatgpt"
  human_gate: "required_after_completion"
  recommended_codex_reason_level: "high"
  master_push_authorized: false
  source_branch_push_authorized: false
  working_branch_push_authorized: true
  hard_reset_authorized: false
  actual_state_write_authorized: false
  scheduler_write_authorized: false

return:
  packet_id: "codex-math-mentor-lrp-05-student-learning-state-spaced-review-0001"
  report_ref: ".ai/CODEX_REPORTS/math-mentor-lrp-05-student-learning-state-spaced-review-0001.md"
  validation_ref: ".ai/CODEX_REPORTS/math-mentor-lrp-05-student-learning-state-validation-0001.md"
  changed_files_ref: ".ai/CODEX_REPORTS/math-mentor-lrp-05-student-learning-state-changed-files-0001.md"
  actually_read_files_ref: ".ai/CODEX_REPORTS/math-mentor-lrp-05-student-learning-state-actually-read-files-0001.md"
  brief_ref: ".ai/HUMAN_BRIEF.md"

completion_policy: "completion_preserving"
---

# Math Mentor LRP-05 Student Learning State And Spaced Review

## 1. Task Position

This is the fifth long-running task in the Math Mentor Teaching System LRP suite.

It is based on:

- accepted LRP-01 teacher initialization and context-loading documents;
- accepted LRP-02 lesson plan schema and teaching agent contracts;
- accepted LRP-03 prompt consistency repairs;
- accepted LRP-04 teaching test harness and golden cases;
- the original Math Mentor teaching-system design implementation plan.

LRP-05 must define the persistent learning-state and spaced-review memory contract. It must not write real student records, update a scheduler file, activate runtime, modify prompts, or mutate source data.

Do not split this task into file-level microtasks. This packet authorizes one coherent LRP-05 execution path: read, design, create the four schema/rules documents, validate, report, commit, push working branch, and handoff.

## 2. Core Problem

The teaching system now has classroom teaching and exam contracts, but it still needs a durable state model for what the student has learned over time.

Without this layer, the system can regress into:

- treating `classroom_passed` as long-term mastery;
- inferring mastery from lower node id alone;
- using bridge slots as learned prerequisites without persisted evidence;
- silently pretending a spaced-review scheduler exists;
- writing learning history without explicit authority;
- making graduation claims before spaced-review evidence exists.

LRP-05 must define the state contract and boundaries that prevent these errors.

## 3. Required Documents

### 3.1 `STUDENT_LEARNING_STATE_SCHEMA.md`

Define durable student learning-state records.

Required sections:

1. purpose and authority;
2. privacy and identity placeholders;
3. per-node learning record schema;
4. allowed learning statuses;
5. status transition table;
6. evidence provenance;
7. Exam_Agent classroom evidence fields;
8. bridge learned-status read model;
9. forbidden claims and writes.

### 3.2 `SPACED_REVIEW_SCHEDULER_SCHEMA.md`

Define the scheduler record contract without activating a scheduler.

Required sections:

1. purpose and no-runtime boundary;
2. review item schema;
3. due window and interval fields;
4. review result taxonomy;
5. transition rules from `classroom_passed` to `review_due`, `review_passed`, `graduated`, `stale`, or `blocked`;
6. scheduler unavailable warning contract;
7. future implementation handoff constraints.

### 3.3 `LEARNED_HISTORY_RULES.md`

Define how learned status is read and used.

Required sections:

1. evidence priority order;
2. persisted state read rule;
3. classroom pass rule;
4. spaced-review evidence rule;
5. node id ordering fallback limits;
6. missing state degradation;
7. bridge slot gating;
8. actually_read_files and unavailable-files requirements.

### 3.4 `GRADUATION_CRITERIA.md`

Define long-term graduation criteria.

Required sections:

1. classroom pass boundary;
2. minimum review pass requirements;
3. definition-boundary and trap-retention requirements;
4. stability-over-time requirement;
5. stale/downgrade rules;
6. graduation claim wording constraints;
7. forbidden shortcuts.

## 4. Required Validation Detail

The validation report must include:

```yaml
validation_result:
  required_refs_read:
    status: pass | fail
    missing_refs: []
  new_documents_exist:
    student_learning_state_schema: pass | fail
    spaced_review_scheduler_schema: pass | fail
    learned_history_rules: pass | fail
    graduation_criteria: pass | fail
  learning_state_schema:
    learning_status_values: pass | fail
    transition_table: pass | fail
    evidence_provenance: pass | fail
    privacy_boundary: pass | fail
  scheduler_schema:
    review_item_record: pass | fail
    due_windows: pass | fail
    review_result_transitions: pass | fail
    unavailable_warning: pass | fail
    no_runtime_or_write_claim: pass | fail
  learned_history_rules:
    evidence_priority: pass | fail
    classroom_passed_not_mastery: pass | fail
    node_id_ordering_not_mastery: pass | fail
    bridge_slot_gating: pass | fail
    missing_state_degradation: pass | fail
  graduation_criteria:
    classroom_passed_not_graduated: pass | fail
    review_based_graduation: pass | fail
    stale_or_downgrade_rules: pass | fail
    wording_constraints: pass | fail
  scope:
    allowed_only: pass | fail
    forbidden_changes: []
  git_safety:
    no_git_reset_hard: pass | fail
    no_force_push: pass | fail
    no_push_all: pass | fail
  security_privacy:
    scoped_secret_scan: pass | fail
    no_real_student_private_data: pass | fail
```

## 5. Expected Handoff

Codex must publish a handoff on `ai/review/latest` with:

```yaml
packet_id: codex-math-mentor-lrp-05-student-learning-state-spaced-review-0001
status:
report_ref:
validation_ref:
changed_files_ref:
actually_read_files_ref:
brief_ref:
dev_branch:
dev_branch_head:
source_branch:
source_head:
master_head:
review_branch_head:
human_gate: required
```

The task ends at Human/ChatGPT review. It does not publish to the source branch or master unless separately authorized after review.
