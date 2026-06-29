---
task_version: "1.0"
task_id: "math-mentor-lrp-04-teaching-test-harness-and-golden-cases-0001"
title: "Math Mentor LRP-04 Teaching Test Harness And Golden Cases"
mode: "goal"
task_level: 2

intent:
  goal: "Complete LRP-04 by turning the accepted Math Mentor initialization, schema, contract, and prompt rules into auditable teaching-system tests, golden cases, fixtures, and an E2E teaching-session simulation."
  why_now: "LRP-01 closed initialization/loading, LRP-02 closed lesson_plan and agent contracts, and LRP-03 aligned the prompts. The next blocker is that the system still lacks regression tests and golden cases to prevent future prompt or contract changes from breaking teach-before-interrogation, tool truthfulness, bridge-slot visibility, initialization lazy loading, and exam handoff."
  definition_of_done:
    - "TEACHING_SYSTEM_TEST_PLAN.md exists and defines static consistency tests, initialization dry-run tests, golden teaching case tests, E2E simulation tests, and validation gates."
    - "TEACHING_GOLDEN_CASES.md exists and defines golden cases with input, expected_behavior, must_have, must_not_have, and pass/fail criteria."
    - "TEACHER_INITIALIZATION_TEST_FIXTURES.md exists and defines reusable fixtures for empty-context bootstrap, target-node request, missing current-context manual, missing repository file, learned-history unavailable, drift recovery, and new-window reset."
    - "E2E_TEACHING_SESSION_SIMULATION.md exists and walks through a full simulated session from Human request to Coordinator state dump, lesson_plan, guided teaching, wrong answer, repair, definition restatement, Exam handoff, trap, classroom result, and missing spaced-review scheduler warning."
    - "The test materials preserve LRP-01, LRP-02, and LRP-03 as authoritative inputs and do not mutate prompts, schemas, nodes, bridges, runtime, evaluator, learning-state, or scheduler files."
    - "Validation and handoff reports are produced."

outputs:
  primary: "08_Domain_Applications/Math_Mentor/TEACHING_SYSTEM_TEST_PLAN.md"
  additional:
    - "08_Domain_Applications/Math_Mentor/TEACHING_GOLDEN_CASES.md"
    - "08_Domain_Applications/Math_Mentor/TEACHER_INITIALIZATION_TEST_FIXTURES.md"
    - "08_Domain_Applications/Math_Mentor/E2E_TEACHING_SESSION_SIMULATION.md"
    - ".ai/CODEX_REPORTS/math-mentor-lrp-04-teaching-test-harness-and-golden-cases-0001.md"
    - ".ai/CODEX_REPORTS/math-mentor-lrp-04-teaching-test-harness-validation-0001.md"
    - ".ai/CODEX_REPORTS/math-mentor-lrp-04-teaching-test-harness-changed-files-0001.md"
    - ".ai/CODEX_REPORTS/math-mentor-lrp-04-teaching-test-harness-actually-read-files-0001.md"

inputs:
  required_refs:
    - ".ai/TASKS/math-mentor-lrp-04-teaching-test-harness-and-golden-cases-0001.md"
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
    name: "dev/math-mentor-lrp-04-teaching-test-harness-and-golden-cases-0001"
    create_from: "the exact source_head in the short signal that points to this task packet"
  allowed_files:
    - "08_Domain_Applications/Math_Mentor/TEACHING_SYSTEM_TEST_PLAN.md"
    - "08_Domain_Applications/Math_Mentor/TEACHING_GOLDEN_CASES.md"
    - "08_Domain_Applications/Math_Mentor/TEACHER_INITIALIZATION_TEST_FIXTURES.md"
    - "08_Domain_Applications/Math_Mentor/E2E_TEACHING_SESSION_SIMULATION.md"
    - ".ai/CODEX_REPORTS/math-mentor-lrp-04-teaching-test-harness-and-golden-cases-0001.md"
    - ".ai/CODEX_REPORTS/math-mentor-lrp-04-teaching-test-harness-validation-0001.md"
    - ".ai/CODEX_REPORTS/math-mentor-lrp-04-teaching-test-harness-changed-files-0001.md"
    - ".ai/CODEX_REPORTS/math-mentor-lrp-04-teaching-test-harness-actually-read-files-0001.md"
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
    - "08_Domain_Applications/Math_Mentor/08_Math_Mentor_Coordinator_Prompt.md"
    - "08_Domain_Applications/Math_Mentor/学习期prompt/Prep_Architect_Prompt.md"
    - "08_Domain_Applications/Math_Mentor/学习期prompt/Socratic_Router_Prompt_v7.0.md"
    - "08_Domain_Applications/Math_Mentor/学习期prompt/Exam_Agent_Prompt.md"
    - "未完成任务备忘录.yml"
  allowed_actions:
    - "create the working branch from the exact source head"
    - "read required refs"
    - "create the four LRP-04 test/golden/simulation documents"
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
    - "evaluator mutation"
    - "learning-state or spaced-review writes"

requirements:
  invariants:
    - "Plan 3 Human Speaker authority remains the top-level route, translation, and final-decision model."
    - "Math Mentor teaching remains an Engine B domain teaching task; deterministic tools may support but not replace teaching judgment."
    - "LRP-01 lazy-loading and actually_read_files evidence rules are the initialization test baseline."
    - "LRP-02 lesson_plan schema and agent contracts are the contract test baseline."
    - "LRP-03 prompt repairs are the prompt behavior test baseline."
    - "No document may claim runtime, Coordinator, Z3, SymPy, PyTorch, calculator, app, MCP, scheduler, or external tool execution unless a real command/log/report exists."
    - "E2E simulation is a documented simulation, not production runtime execution."
    - "Exam classroom_passed must not be described as long-term graduation."
    - "If spaced-review scheduler is missing or unauthorized, the E2E simulation must output a warning/placeholder instead of pretending a scheduler update occurred."
    - "Completion-preserving execution is mandatory: read, design, create docs, validate, report, commit, branch push, and handoff are one task."
  required_test_layers:
    static_consistency_tests:
      - "no full repo ingestion"
      - "no full Math Mentor ingestion"
      - "no fake tool execution"
      - "no Plan3 Engine vs MathLane namespace confusion"
      - "teach-before-interrogation preserved"
      - "lesson_plan schema fields preserved"
      - "Cognitive_State_Vector handoff preserved"
      - "bridge-slot first-use visibility preserved"
      - "classroom_passed != long-term graduation"
    initialization_dry_runs:
      - "empty context -> teacher initialization"
      - "target node request -> SYSTEM_STATE_DUMP"
      - "manual absent from current context but present in repository -> lazy load, not refusal"
      - "manual absent from repository -> exact missing path stop"
      - "learned-history unavailable -> warning/fallback, not mastery claim"
      - "context drift -> smallest authority/context reload"
      - "irreversible drift -> new-window reset"
    golden_teaching_cases:
      - "MathLane_A basic concept"
      - "MathLane_B abstract concept"
      - "bridge slot first-use teaching"
      - "student error handling and re-prep trigger"
      - "Exam handoff with Cognitive_State_Vector"
      - "tool truthfulness / no fake execution"
    e2e_session_simulation:
      - "Human request"
      - "Coordinator state dump"
      - "Prep lesson_plan"
      - "Guided Socratic teaching"
      - "student wrong once"
      - "repair"
      - "student definition restatement"
      - "Exam handoff"
      - "Exam trap"
      - "classroom result"
      - "spaced-review placeholder or missing scheduler warning"
  validation:
    - "all required refs were read or any missing ref is explicitly reported with path, branch, and failure reason"
    - "the four new LRP-04 documents exist on the working branch"
    - "TEACHING_SYSTEM_TEST_PLAN.md defines static consistency, initialization, golden case, and E2E simulation test layers"
    - "TEACHING_GOLDEN_CASES.md includes each golden case with input, expected_behavior, must_have, must_not_have, and pass_fail_criteria"
    - "golden cases cover MathLane_A, MathLane_B, bridge slot, error/re-prep, exam handoff, and tool truthfulness"
    - "TEACHER_INITIALIZATION_TEST_FIXTURES.md covers all required initialization dry-runs"
    - "E2E_TEACHING_SESSION_SIMULATION.md includes a full simulated session and does not fake scheduler/runtime/tool execution"
    - "E2E simulation explicitly states classroom_passed is not long-term graduation"
    - "E2E simulation emits a warning or placeholder when spaced-review scheduler is unavailable or unauthorized"
    - "test cases include must_not_have checks for full repo ingestion, fake tool execution, pure interrogation before explanation, Mode/Engine confusion, bridge invisibility, premature exam handoff, and graduation misclaim"
    - "changed files are limited to allowed_files"
    - "forbidden_files are not modified"
    - "no git reset --hard is used"
    - "scoped secret scan passes"
    - "remote read-back verifies the pushed working branch and report refs"
  stop_rules:
    - "source head mismatch before working branch creation"
    - "required refs missing in a way that prevents safe test design"
    - "need to modify forbidden files"
    - "need to alter LRP-01, LRP-02, or LRP-03 artifacts instead of creating tests for them"
    - "need for node generation, bridge generation, bridge schema mutation, prompt mutation, evaluator mutation, runtime activation, Coordinator activation, learning-state writes, or scheduler writes"
    - "need to use git reset --hard"
    - "security/privacy/secret risk"
    - "merge/master/source publication requirement not authorized by this task"
    - "validation failure after one safe repair pass"

authority:
  semantic_reviewer: "chatgpt"
  human_gate: "required_after_completion"
  recommended_codex_reason_level: "extra_high"
  master_push_authorized: false
  source_branch_push_authorized: false
  working_branch_push_authorized: true
  hard_reset_authorized: false

return:
  packet_id: "codex-math-mentor-lrp-04-teaching-test-harness-and-golden-cases-0001"
  report_ref: ".ai/CODEX_REPORTS/math-mentor-lrp-04-teaching-test-harness-and-golden-cases-0001.md"
  validation_ref: ".ai/CODEX_REPORTS/math-mentor-lrp-04-teaching-test-harness-validation-0001.md"
  changed_files_ref: ".ai/CODEX_REPORTS/math-mentor-lrp-04-teaching-test-harness-changed-files-0001.md"
  actually_read_files_ref: ".ai/CODEX_REPORTS/math-mentor-lrp-04-teaching-test-harness-actually-read-files-0001.md"
  brief_ref: ".ai/HUMAN_BRIEF.md"

completion_policy: "completion_preserving"
---

# Math Mentor LRP-04 Teaching Test Harness And Golden Cases

## 1. Task Position

This is the fourth long-running task in the Math Mentor Teaching System LRP suite.

It is based on:

- accepted LRP-01 teacher initialization and context-loading documents;
- accepted LRP-02 lesson plan schema and teaching agent contracts;
- accepted LRP-03 prompt consistency repairs;
- the original Math Mentor teaching-system design implementation plan.

LRP-04 must convert the accepted contracts and prompt behavior into auditable tests and simulations. It must not repair prompts, mutate schemas, generate nodes, generate bridges, activate runtime, or write learning-state.

Do not split this task into file-level microtasks. This packet authorizes one coherent LRP-04 execution path: read, design, create the four test/golden/simulation documents, validate, report, commit, push working branch, and handoff.

## 2. Core Problem

The Math Mentor system now has a coherent initialization path, data contract layer, and prompt layer. But without tests, future prompt edits can silently regress into:

- full repository or full Math Mentor ingestion;
- hidden file claims without `actually_read_files`;
- Plan 3 Engine A/B versus MathLane A/B confusion;
- pure interrogation before explanation;
- fake Z3/SymPy/PyTorch/tool execution claims;
- bridge slots disappearing or being dumped as metadata instead of taught;
- missing `Cognitive_State_Vector` in Exam handoff;
- `classroom_passed` being mistaken for long-term graduation;
- pretending a spaced-review scheduler exists when it has not been authorized.

LRP-04 must make these regressions auditable.

## 3. Required Documents

### 3.1 `TEACHING_SYSTEM_TEST_PLAN.md`

Define the test harness as a documentation and validation layer.

Required sections:

1. purpose and authority;
2. test layers;
3. static consistency test matrix;
4. initialization dry-run test matrix;
5. golden teaching case matrix;
6. E2E simulation acceptance rules;
7. failure taxonomy;
8. validation commands/checks Codex can run without activating runtime.

### 3.2 `TEACHING_GOLDEN_CASES.md`

Each golden case must include:

```yaml
case_id:
title:
covered_risk:
input:
expected_behavior:
must_have:
must_not_have:
pass_fail_criteria:
source_contracts:
```

Required cases:

- MathLane_A basic concept;
- MathLane_B abstract concept;
- bridge slot first-use teaching;
- student error handling and re-prep trigger;
- Exam handoff with Cognitive_State_Vector;
- tool truthfulness / no fake execution.

### 3.3 `TEACHER_INITIALIZATION_TEST_FIXTURES.md`

Define reusable fixtures for:

- empty context -> teacher initialization;
- target node request -> compressed SYSTEM_STATE_DUMP;
- manual absent from current context but present in repository -> lazy load, not refusal;
- manual absent from repository -> exact missing path stop;
- learned-history unavailable -> warning/fallback, not mastery claim;
- context drift -> smallest authority/context reload;
- irreversible drift -> new-window reset.

Each fixture must include input condition, expected loading order, expected `actually_read_files`, expected output/state, and must_not_have.

### 3.4 `E2E_TEACHING_SESSION_SIMULATION.md`

Simulate a full session using compact invented teaching content that does not require reading or generating real node YAML.

Required flow:

1. Human request;
2. Coordinator state dump;
3. Prep lesson_plan;
4. Guided Socratic teaching;
5. student wrong once;
6. repair;
7. student definition restatement;
8. Exam handoff with Cognitive_State_Vector;
9. Exam trap;
10. classroom result;
11. spaced-review placeholder or missing scheduler warning.

The simulation must explicitly state that it is not runtime execution, not Coordinator activation, not tool execution, and not a learning-state write.

## 4. Required Validation Detail

The validation report must include:

```yaml
validation_result:
  required_refs_read:
    status: pass | fail
    missing_refs: []
  new_documents_exist:
    teaching_system_test_plan: pass | fail
    teaching_golden_cases: pass | fail
    teacher_initialization_test_fixtures: pass | fail
    e2e_teaching_session_simulation: pass | fail
  test_layers:
    static_consistency_tests: pass | fail
    initialization_dry_runs: pass | fail
    golden_teaching_cases: pass | fail
    e2e_session_simulation: pass | fail
  golden_case_coverage:
    mathlane_a: pass | fail
    mathlane_b: pass | fail
    bridge_slot: pass | fail
    error_reprep: pass | fail
    exam_handoff: pass | fail
    tool_truthfulness: pass | fail
  anti_regression_must_not_have:
    no_full_repo_ingestion: pass | fail
    no_fake_tool_execution: pass | fail
    no_engine_mathlane_confusion: pass | fail
    no_pure_interrogation_before_explanation: pass | fail
    no_bridge_invisibility: pass | fail
    no_premature_exam_handoff: pass | fail
    no_graduation_misclaim: pass | fail
  e2e_boundaries:
    simulation_not_runtime: pass | fail
    no_scheduler_write_claim: pass | fail
    missing_scheduler_warning_or_placeholder: pass | fail
  scope:
    allowed_only: pass | fail
    forbidden_changes: []
  git_safety:
    no_git_reset_hard: pass | fail
    no_force_push: pass | fail
    no_push_all: pass | fail
  secret_scan:
    status: pass | fail
```

## 5. Expected Handoff

Codex must publish a handoff on `ai/review/latest` with:

```yaml
packet_id: codex-math-mentor-lrp-04-teaching-test-harness-and-golden-cases-0001
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
