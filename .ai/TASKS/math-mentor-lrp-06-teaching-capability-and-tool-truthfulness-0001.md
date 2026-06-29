---
task_version: "1.0"
task_id: "math-mentor-lrp-06-teaching-capability-and-tool-truthfulness-0001"
title: "Math Mentor LRP-06 Teaching Capability And Tool Truthfulness"
mode: "goal"
task_level: 2

intent:
  goal: "Complete LRP-06 by defining Math Mentor capability registration, tool truthfulness policy, deterministic calculation handoff, and visualization/app capability planning without running tools, activating runtime, or connecting external apps."
  why_now: "LRP-01 closed initialization/loading, LRP-02 closed lesson and agent contracts, LRP-03 aligned prompts, LRP-04 created regression tests, and LRP-05 fixed learning-state/spaced-review boundaries. The remaining blocker before future tool-enhanced teaching is a precise evidence contract for when Math Mentor may say a tool ran, when it may say semantic-only, and how future runtime work must hand back logs."
  definition_of_done:
    - "MATH_MENTOR_CAPABILITY_REGISTRY.md exists and classifies deterministic_calculation, semantic_audit, visualization, human_brief, and future_app_skill capabilities."
    - "TOOL_TRUTHFULNESS_POLICY.md exists and defines allowed claim states: not_run, run_with_log, unavailable, semantic_only, planned, and review_required."
    - "DETERMINISTIC_CALCULATION_HANDOFF.md exists and defines required command/log/report evidence before any Z3/SymPy/Python/calculator/PyTorch execution claim."
    - "VISUALIZATION_AND_APP_CAPABILITY_PLAN.md exists and defines visualization/app capability boundaries without generating real visualizations or connecting apps."
    - "The documents preserve Plan 3 Human Speaker authority, LRP-01 through LRP-05 boundaries, no fake tool execution, no runtime activation, and no production Coordinator activation."
    - "Validation and handoff reports are produced."

outputs:
  primary: "08_Domain_Applications/Math_Mentor/MATH_MENTOR_CAPABILITY_REGISTRY.md"
  additional:
    - "08_Domain_Applications/Math_Mentor/TOOL_TRUTHFULNESS_POLICY.md"
    - "08_Domain_Applications/Math_Mentor/DETERMINISTIC_CALCULATION_HANDOFF.md"
    - "08_Domain_Applications/Math_Mentor/VISUALIZATION_AND_APP_CAPABILITY_PLAN.md"
    - ".ai/CODEX_REPORTS/math-mentor-lrp-06-teaching-capability-and-tool-truthfulness-0001.md"
    - ".ai/CODEX_REPORTS/math-mentor-lrp-06-teaching-capability-validation-0001.md"
    - ".ai/CODEX_REPORTS/math-mentor-lrp-06-teaching-capability-changed-files-0001.md"
    - ".ai/CODEX_REPORTS/math-mentor-lrp-06-teaching-capability-actually-read-files-0001.md"

inputs:
  required_refs:
    - ".ai/TASKS/math-mentor-lrp-06-teaching-capability-and-tool-truthfulness-0001.md"
    - "08_Domain_Applications/Math_Mentor/Math Mentor Teaching System Design implement plan.md"
    - "08_Domain_Applications/Math_Mentor/Math Mentor Teaching System Design.md"
    - "08_Domain_Applications/Math_Mentor/TEACHER_INITIALIZATION_FLOW.md"
    - "08_Domain_Applications/Math_Mentor/TEACHER_CONTEXT_LOADING_RULES.md"
    - "08_Domain_Applications/Math_Mentor/LESSON_PLAN_SCHEMA.md"
    - "08_Domain_Applications/Math_Mentor/TEACHING_AGENT_CONTRACTS.md"
    - "08_Domain_Applications/Math_Mentor/EXAM_HANDOFF_STATE_VECTOR_SCHEMA.md"
    - "08_Domain_Applications/Math_Mentor/BRIDGE_SLOT_TEACHING_CONTRACT.md"
    - "08_Domain_Applications/Math_Mentor/TEACHING_PROMPT_CONSISTENCY_AUDIT.md"
    - "08_Domain_Applications/Math_Mentor/TEACHING_SYSTEM_TEST_PLAN.md"
    - "08_Domain_Applications/Math_Mentor/TEACHING_GOLDEN_CASES.md"
    - "08_Domain_Applications/Math_Mentor/E2E_TEACHING_SESSION_SIMULATION.md"
    - "08_Domain_Applications/Math_Mentor/STUDENT_LEARNING_STATE_SCHEMA.md"
    - "08_Domain_Applications/Math_Mentor/SPACED_REVIEW_SCHEDULER_SCHEMA.md"
    - "08_Domain_Applications/Math_Mentor/LEARNED_HISTORY_RULES.md"
    - "08_Domain_Applications/Math_Mentor/GRADUATION_CRITERIA.md"
    - "08_Domain_Applications/Math_Mentor/08_Math_Mentor_Coordinator_Prompt.md"
    - "08_Domain_Applications/Math_Mentor/学习期prompt/Prep_Architect_Prompt.md"
    - "08_Domain_Applications/Math_Mentor/学习期prompt/Socratic_Router_Prompt_v7.0.md"
    - "08_Domain_Applications/Math_Mentor/学习期prompt/Exam_Agent_Prompt.md"
    - "08_Domain_Applications/Math_Mentor/V9.1_教学流程系统规范_Teaching_Flow_Spec.md"
    - "08_Domain_Applications/Math_Mentor/V9.1_认知映射引擎_终极实装蓝图.md"
    - "08_Domain_Applications/Math_Mentor/Math_Mentor_V9.1_从生成到教学的完整流程.md"
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
    name: "dev/math-mentor-lrp-06-teaching-capability-and-tool-truthfulness-0001"
    create_from: "the exact source_head in the short signal that points to this task packet"
  allowed_files:
    - "08_Domain_Applications/Math_Mentor/MATH_MENTOR_CAPABILITY_REGISTRY.md"
    - "08_Domain_Applications/Math_Mentor/TOOL_TRUTHFULNESS_POLICY.md"
    - "08_Domain_Applications/Math_Mentor/DETERMINISTIC_CALCULATION_HANDOFF.md"
    - "08_Domain_Applications/Math_Mentor/VISUALIZATION_AND_APP_CAPABILITY_PLAN.md"
    - ".ai/CODEX_REPORTS/math-mentor-lrp-06-teaching-capability-and-tool-truthfulness-0001.md"
    - ".ai/CODEX_REPORTS/math-mentor-lrp-06-teaching-capability-validation-0001.md"
    - ".ai/CODEX_REPORTS/math-mentor-lrp-06-teaching-capability-changed-files-0001.md"
    - ".ai/CODEX_REPORTS/math-mentor-lrp-06-teaching-capability-actually-read-files-0001.md"
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
    - "08_Domain_Applications/Math_Mentor/TEACHING_PROMPT_CONSISTENCY_AUDIT.md"
    - "08_Domain_Applications/Math_Mentor/TEACHING_SYSTEM_TEST_PLAN.md"
    - "08_Domain_Applications/Math_Mentor/TEACHING_GOLDEN_CASES.md"
    - "08_Domain_Applications/Math_Mentor/E2E_TEACHING_SESSION_SIMULATION.md"
    - "08_Domain_Applications/Math_Mentor/STUDENT_LEARNING_STATE_SCHEMA.md"
    - "08_Domain_Applications/Math_Mentor/SPACED_REVIEW_SCHEDULER_SCHEMA.md"
    - "08_Domain_Applications/Math_Mentor/LEARNED_HISTORY_RULES.md"
    - "08_Domain_Applications/Math_Mentor/GRADUATION_CRITERIA.md"
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
    - "create the four LRP-06 capability/policy/handoff/plan documents"
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
    - "external app or MCP activation"
    - "actual Python/SymPy/Z3/PyTorch/calculator execution"
    - "visualization generation as runtime output"
    - "node generation"
    - "bridge generation"
    - "bridge schema mutation"
    - "prompt mutation"
    - "schema mutation outside the four LRP-06 outputs"
    - "evaluator mutation"
    - "actual student-state, learned-history, or scheduler writes"

requirements:
  invariants:
    - "Plan 3 Human Speaker authority remains the top-level route, translation, and final-decision model."
    - "Math Mentor teaching remains an Engine B domain teaching task; deterministic tools may support but never replace teaching judgment or Human authority."
    - "LRP-01 lazy-loading and actually_read_files evidence rules remain the context-loading baseline."
    - "LRP-02 lesson_plan.tool_truthfulness and Exam handoff contracts remain the upstream evidence baseline."
    - "LRP-03 prompt behavior remains the prompt alignment baseline."
    - "LRP-04 tests remain the anti-regression baseline."
    - "LRP-05 learning-state/spaced-review contracts remain the state boundary baseline."
    - "Only run_with_log plus a concrete log/report may support a claim that a deterministic tool has run."
    - "When no log exists, use not_run, semantic_only, unavailable, planned, or review_required; never say verified/computed/checked by tool."
    - "LRP-06 does not connect runtime; it defines the contract that a later Engine A implementation must satisfy."
    - "Completion-preserving execution is mandatory: read, design, create docs, validate, report, commit, branch push, and handoff are one task."
  required_documents:
    capability_registry:
      - "capability categories: deterministic_calculation, semantic_audit, visualization, human_brief, future_app_skill"
      - "per-capability availability states: available, unavailable, planned, human_only, runtime_required"
      - "who may request or authorize each capability"
      - "which agent may consume the result"
      - "what evidence is required before a claim is allowed"
    tool_truthfulness_policy:
      - "allowed claim states: not_run, run_with_log, unavailable, semantic_only, planned, review_required"
      - "forbidden phrases when no log exists"
      - "safe replacement wording"
      - "semantic audit versus machine proof distinction"
      - "failure and contradiction handling"
    deterministic_calculation_handoff:
      - "future command/log/report schema"
      - "input, command, output, error, timestamp, environment, dependency, and source refs"
      - "how a future tool run updates lesson_plan.tool_truthfulness"
      - "how to handle timeout, missing dependency, unsafe input, or contradictory result"
      - "explicit no-execution boundary for this LRP"
    visualization_and_app_plan:
      - "visualization types and future app/skill capability map"
      - "generation boundary: planned only unless future task authorizes runtime"
      - "what counts as a visual artifact versus a verbal sketch"
      - "privacy and student-data boundary"
      - "future implementation gate"
  validation:
    - "all required refs were read or any missing ref is explicitly reported with path, branch, and failure reason"
    - "the four new LRP-06 documents exist on the working branch"
    - "MATH_MENTOR_CAPABILITY_REGISTRY.md defines all required capability categories and availability states"
    - "TOOL_TRUTHFULNESS_POLICY.md defines all allowed claim states and forbidden no-log claims"
    - "DETERMINISTIC_CALCULATION_HANDOFF.md defines command/log/report evidence schema and no-execution boundary"
    - "VISUALIZATION_AND_APP_CAPABILITY_PLAN.md defines visualization/app capability plan and no-runtime boundary"
    - "documents distinguish semantic audit from deterministic machine proof"
    - "documents require real command/log/report before claiming Z3/SymPy/Python/PyTorch/calculator execution"
    - "documents define safe wording when no tool log exists"
    - "documents do not claim any actual tool execution occurred"
    - "documents do not activate runtime, production Coordinator, MCP, external app, or visualization generator"
    - "changed files are limited to allowed_files"
    - "forbidden_files are not modified"
    - "no git reset --hard is used"
    - "scoped secret scan passes"
    - "remote read-back verifies the pushed working branch and report refs"
  stop_rules:
    - "source head mismatch before working branch creation"
    - "required refs missing in a way that prevents safe capability-policy design"
    - "need to modify forbidden files"
    - "need to alter LRP-01 through LRP-05 artifacts instead of creating LRP-06 policy documents"
    - "need for actual Python/SymPy/Z3/PyTorch/calculator execution, visualization generation, app/MCP activation, runtime activation, Coordinator activation, prompt mutation, evaluator mutation, node/bridge generation, student-state writes, learned-history writes, or scheduler writes"
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
  runtime_activation_authorized: false
  production_coordinator_activation_authorized: false
  external_app_or_mcp_authorized: false
  actual_tool_execution_authorized: false
  visualization_generation_authorized: false

return:
  packet_id: "codex-math-mentor-lrp-06-teaching-capability-and-tool-truthfulness-0001"
  report_ref: ".ai/CODEX_REPORTS/math-mentor-lrp-06-teaching-capability-and-tool-truthfulness-0001.md"
  validation_ref: ".ai/CODEX_REPORTS/math-mentor-lrp-06-teaching-capability-validation-0001.md"
  changed_files_ref: ".ai/CODEX_REPORTS/math-mentor-lrp-06-teaching-capability-changed-files-0001.md"
  actually_read_files_ref: ".ai/CODEX_REPORTS/math-mentor-lrp-06-teaching-capability-actually-read-files-0001.md"
  brief_ref: ".ai/HUMAN_BRIEF.md"

completion_policy: "completion_preserving"
---

# Math Mentor LRP-06 Teaching Capability And Tool Truthfulness

## 1. Task Position

This is the sixth long-running task in the Math Mentor Teaching System LRP suite.

It is based on:

- accepted LRP-01 teacher initialization and context-loading documents;
- accepted LRP-02 lesson plan schema and teaching agent contracts;
- accepted LRP-03 prompt consistency repairs;
- accepted LRP-04 teaching test harness and golden cases;
- accepted LRP-05 student learning-state and spaced-review contracts;
- the original Math Mentor teaching-system design implementation plan.

LRP-06 must define capability registration and tool-truthfulness contracts. It must not run tools, connect external apps, generate visual artifacts, activate runtime, activate production Coordinator logic, mutate prompts, generate nodes/bridges, or write student state.

Do not split this task into file-level microtasks. This packet authorizes one coherent LRP-06 execution path: read, design, create the four capability/policy/handoff/plan documents, validate, report, commit, push working branch, and handoff.

## 2. Core Problem

The teaching system wants future access to capabilities such as Python, SymPy, Z3, PyTorch, calculators, visualization, app blocks, and human-facing reports. But without a truthfulness contract, the system may claim a tool has run when it has only reasoned semantically.

LRP-06 must define the evidence law:

- when a capability exists;
- who can request it;
- who can authorize it;
- what output/log counts as evidence;
- what the teacher may say when no log exists;
- how semantic audit differs from machine proof;
- how future Engine A runtime tasks must hand results back to Engine B teaching.

This is the circuit breaker before future tool-enhanced teaching.

## 3. Required Documents

### 3.1 `MATH_MENTOR_CAPABILITY_REGISTRY.md`

Define capability classes and availability states.

Required sections:

1. purpose and authority;
2. capability category table;
3. availability state taxonomy;
4. per-agent request/consume permissions;
5. Human authorization requirements;
6. evidence required before claim;
7. forbidden capability claims;
8. future runtime implementation gate.

### 3.2 `TOOL_TRUTHFULNESS_POLICY.md`

Define how Math Mentor may talk about tools.

Required sections:

1. purpose;
2. allowed claim states;
3. safe wording table;
4. forbidden no-log phrases;
5. semantic audit versus machine proof;
6. contradiction handling;
7. missing dependency/timeout/unavailable handling;
8. citation/log/reference requirements.

### 3.3 `DETERMINISTIC_CALCULATION_HANDOFF.md`

Define the future handoff contract for deterministic calculation tools.

Required sections:

1. purpose and no-execution boundary;
2. supported future tool families;
3. command/log/report schema;
4. required input/output/error/environment fields;
5. result integration into `lesson_plan.tool_truthfulness`;
6. failure modes;
7. unsafe input and privacy boundaries;
8. future Engine A implementation checklist.

### 3.4 `VISUALIZATION_AND_APP_CAPABILITY_PLAN.md`

Define future visualization/app capability planning without activating it.

Required sections:

1. purpose and no-runtime boundary;
2. visualization capability classes;
3. verbal sketch versus generated artifact distinction;
4. app/skill/MCP future integration constraints;
5. student privacy and state boundaries;
6. Human authorization gates;
7. future implementation checklist.

## 4. Required Validation Detail

The validation report must include:

```yaml
validation_result:
  required_refs_read:
    status: pass | fail
    missing_refs: []
  new_documents_exist:
    capability_registry: pass | fail
    tool_truthfulness_policy: pass | fail
    deterministic_calculation_handoff: pass | fail
    visualization_and_app_capability_plan: pass | fail
  capability_registry:
    required_categories: pass | fail
    availability_states: pass | fail
    authorization_rules: pass | fail
    evidence_required_before_claim: pass | fail
  tool_truthfulness_policy:
    allowed_claim_states: pass | fail
    forbidden_no_log_phrases: pass | fail
    safe_replacement_wording: pass | fail
    semantic_audit_vs_machine_proof: pass | fail
  deterministic_calculation_handoff:
    command_log_report_schema: pass | fail
    integration_with_tool_truthfulness: pass | fail
    failure_modes: pass | fail
    no_execution_boundary: pass | fail
  visualization_and_app_plan:
    no_runtime_boundary: pass | fail
    verbal_sketch_vs_artifact: pass | fail
    future_app_gate: pass | fail
    privacy_boundary: pass | fail
  scope:
    allowed_only: pass | fail
    forbidden_changes: []
  execution_safety:
    no_actual_tool_execution: pass | fail
    no_runtime_activation: pass | fail
    no_coordinator_activation: pass | fail
    no_external_app_or_mcp_activation: pass | fail
    no_visualization_generation: pass | fail
  git_safety:
    no_git_reset_hard: pass | fail
    no_force_push: pass | fail
    no_push_all: pass | fail
  security_privacy:
    scoped_secret_scan: pass | fail
    no_private_student_data: pass | fail
```

## 5. Expected Handoff

Codex must publish a handoff on `ai/review/latest` with:

```yaml
packet_id: codex-math-mentor-lrp-06-teaching-capability-and-tool-truthfulness-0001
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
