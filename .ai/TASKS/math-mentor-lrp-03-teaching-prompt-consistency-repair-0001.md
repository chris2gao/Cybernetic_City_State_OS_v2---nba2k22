---
task_version: "1.0"
task_id: "math-mentor-lrp-03-teaching-prompt-consistency-repair-0001"
title: "Math Mentor LRP-03 Teaching Prompt Consistency Repair"
mode: "goal"
task_level: 2

intent:
  goal: "Complete LRP-03 by auditing and repairing Math Mentor teaching prompts so they align with Plan 3 authority, LRP-01 lazy loading, LRP-02 contracts, teach-before-interrogation, namespace separation, and tool truthfulness."
  why_now: "LRP-01 closed teacher initialization/context loading, and LRP-02 closed lesson_plan/agent contracts. The next blocker is that existing Coordinator/Prep/Socratic/Exam prompts may still contain old assumptions that conflict with the accepted contracts."
  definition_of_done:
    - "TEACHING_PROMPT_CONSISTENCY_AUDIT.md exists and records each prompt issue, evidence path, repair decision, and validation status."
    - "Coordinator Prompt remains aligned with LRP-01 lazy-loading and LRP-02 contract terminology without regressing preflight behavior."
    - "Prep_Architect Prompt is aligned to produce a LRP-02-compliant lesson_plan.json and coverage map without runtime/tool/execution claims."
    - "Socratic_Router Prompt is aligned to teach before interrogation, use one compact forcing question after explanation, preserve full subtopic coverage, expose bridge slots correctly, and remove fake Z3/SymPy/PyTorch/tool-execution claims."
    - "Exam_Agent Prompt is aligned to receive Cognitive_State_Vector, test without teaching, return classroom pass/fail only, and avoid long-term graduation or empty praise."
    - "Validation and handoff reports are produced."

outputs:
  primary: "08_Domain_Applications/Math_Mentor/TEACHING_PROMPT_CONSISTENCY_AUDIT.md"
  additional:
    - "08_Domain_Applications/Math_Mentor/08_Math_Mentor_Coordinator_Prompt.md"
    - "08_Domain_Applications/Math_Mentor/学习期prompt/Prep_Architect_Prompt.md"
    - "08_Domain_Applications/Math_Mentor/学习期prompt/Socratic_Router_Prompt_v7.0.md"
    - "08_Domain_Applications/Math_Mentor/学习期prompt/Exam_Agent_Prompt.md"
    - ".ai/CODEX_REPORTS/math-mentor-lrp-03-teaching-prompt-consistency-repair-0001.md"
    - ".ai/CODEX_REPORTS/math-mentor-lrp-03-teaching-prompt-consistency-validation-0001.md"
    - ".ai/CODEX_REPORTS/math-mentor-lrp-03-teaching-prompt-consistency-changed-files-0001.md"
    - ".ai/CODEX_REPORTS/math-mentor-lrp-03-teaching-prompt-consistency-actually-read-files-0001.md"

inputs:
  required_refs:
    - ".ai/TASKS/math-mentor-lrp-03-teaching-prompt-consistency-repair-0001.md"
    - "08_Domain_Applications/Math_Mentor/Math Mentor Teaching System Design implement plan.md"
    - "08_Domain_Applications/Math_Mentor/Math Mentor Teaching System Design.md"
    - "08_Domain_Applications/Math_Mentor/TEACHER_INITIALIZATION_FLOW.md"
    - "08_Domain_Applications/Math_Mentor/TEACHER_CONTEXT_LOADING_RULES.md"
    - "08_Domain_Applications/Math_Mentor/TEACHER_INITIALIZATION_DRY_RUNS.md"
    - "08_Domain_Applications/Math_Mentor/LESSON_PLAN_SCHEMA.md"
    - "08_Domain_Applications/Math_Mentor/TEACHING_AGENT_CONTRACTS.md"
    - "08_Domain_Applications/Math_Mentor/EXAM_HANDOFF_STATE_VECTOR_SCHEMA.md"
    - "08_Domain_Applications/Math_Mentor/BRIDGE_SLOT_TEACHING_CONTRACT.md"
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
    name: "dev/math-mentor-lrp-03-teaching-prompt-consistency-repair-0001"
    create_from: "the exact source_head in the short signal that points to this task packet"
  allowed_files:
    - "08_Domain_Applications/Math_Mentor/TEACHING_PROMPT_CONSISTENCY_AUDIT.md"
    - "08_Domain_Applications/Math_Mentor/08_Math_Mentor_Coordinator_Prompt.md"
    - "08_Domain_Applications/Math_Mentor/学习期prompt/Prep_Architect_Prompt.md"
    - "08_Domain_Applications/Math_Mentor/学习期prompt/Socratic_Router_Prompt_v7.0.md"
    - "08_Domain_Applications/Math_Mentor/学习期prompt/Exam_Agent_Prompt.md"
    - ".ai/CODEX_REPORTS/math-mentor-lrp-03-teaching-prompt-consistency-repair-0001.md"
    - ".ai/CODEX_REPORTS/math-mentor-lrp-03-teaching-prompt-consistency-validation-0001.md"
    - ".ai/CODEX_REPORTS/math-mentor-lrp-03-teaching-prompt-consistency-changed-files-0001.md"
    - ".ai/CODEX_REPORTS/math-mentor-lrp-03-teaching-prompt-consistency-actually-read-files-0001.md"
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
    - "未完成任务备忘录.yml"
  allowed_actions:
    - "create the working branch from the exact source head"
    - "read required refs"
    - "create/update TEACHING_PROMPT_CONSISTENCY_AUDIT.md"
    - "repair only the four allowed Math Mentor prompt files"
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
    - "evaluator mutation"
    - "learning-state or spaced-review writes"

requirements:
  invariants:
    - "Plan 3 Human Speaker authority remains the top-level route, translation, and final-decision model."
    - "Math Mentor teaching remains an Engine B domain teaching task; deterministic tool use may support but not replace teaching judgment."
    - "Plan 3 Engine_A / Engine_B must not be confused with Math Mentor MathLane_A / MathLane_B."
    - "LRP-01 lazy-loading and actually_read_files evidence rules are preserved."
    - "LRP-02 lesson_plan schema and agent contracts are the alignment target."
    - "No prompt may claim a tool has run unless a real command/log/report exists."
    - "Prompt wording must say can be verified by tool, semantic audit only, or tool log required when no tool was run."
    - "Teach-before-interrogation is mandatory: explanation and bridge first, then one compact forcing question."
    - "Exam_Agent must not teach new content and must not claim long-term graduation."
    - "Completion-preserving execution is mandatory: read, audit, repair, validate, report, commit, branch push, and handoff are one task."
  repair_targets:
    coordinator_prompt:
      - "preserve LRP-01 lazy-load preflight repair"
      - "align output/state wording with LRP-02 lesson_plan and agent contracts"
      - "distinguish Plan3_Engine_A/B from MathLane_A/B"
    prep_architect_prompt:
      - "require LRP-02-compliant lesson_plan.json"
      - "require full subtopic coverage map"
      - "require occurrence_crisis before formal_compression"
      - "require bridge slot evidence and learned-history limits"
      - "forbid fake tool execution claims"
    socratic_router_prompt:
      - "remove or rewrite high-pressure interrogation framing that conflicts with teach-before-interrogation"
      - "remove single-question-only constraints when they block required explanation; preserve one compact forcing question after explanation"
      - "remove or rewrite claims such as 'Z3 has run' unless a real tool log exists"
      - "consume lesson_plan.json, bridge slot contract, subtopic coverage, and re-prep triggers"
      - "produce Socratic-to-Exam Cognitive_State_Vector when handoff conditions are met"
    exam_agent_prompt:
      - "consume Cognitive_State_Vector"
      - "test muscle-memory and edge-case trap without teaching"
      - "return classroom_passed | failed | needs_reprep only"
      - "use structural confirmation, not empty praise"
      - "forbid long-term graduation claims"
  validation:
    - "all required refs were read or any missing ref is explicitly reported with path, branch, and failure reason"
    - "TEACHING_PROMPT_CONSISTENCY_AUDIT.md exists and maps issue -> evidence -> repaired file -> validation status"
    - "Coordinator preflight lazy-load behavior remains present and old upload/refusal behavior is absent"
    - "Prep_Architect prompt requires LRP-02-compliant lesson_plan.json and full subtopic coverage"
    - "Socratic_Router prompt no longer contains fake Z3/SymPy/PyTorch/tool execution claims"
    - "Socratic_Router prompt no longer enforces pure interrogation before explanation"
    - "Socratic_Router preserves one compact forcing question after explanation"
    - "Exam_Agent prompt consumes Cognitive_State_Vector, tests without teaching, and forbids long-term graduation"
    - "all four prompts distinguish Plan 3 Engine_A/B from Math Mentor MathLane_A/B or equivalent wording"
    - "no full-repository ingestion or full Math Mentor ingestion rule is introduced"
    - "changed files are limited to allowed_files"
    - "forbidden_files are not modified"
    - "no git reset --hard is used"
    - "scoped secret scan passes"
    - "remote read-back verifies the pushed working branch and report refs"
  stop_rules:
    - "source head mismatch before working branch creation"
    - "required refs missing in a way that prevents safe prompt repair"
    - "need to modify forbidden files"
    - "need for node generation, bridge generation, bridge schema mutation, evaluator mutation, runtime activation, or Coordinator activation"
    - "need to alter LRP-01 or LRP-02 contracts instead of aligning prompts to them"
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
  packet_id: "codex-math-mentor-lrp-03-teaching-prompt-consistency-repair-0001"
  report_ref: ".ai/CODEX_REPORTS/math-mentor-lrp-03-teaching-prompt-consistency-repair-0001.md"
  validation_ref: ".ai/CODEX_REPORTS/math-mentor-lrp-03-teaching-prompt-consistency-validation-0001.md"
  changed_files_ref: ".ai/CODEX_REPORTS/math-mentor-lrp-03-teaching-prompt-consistency-changed-files-0001.md"
  actually_read_files_ref: ".ai/CODEX_REPORTS/math-mentor-lrp-03-teaching-prompt-consistency-actually-read-files-0001.md"
  brief_ref: ".ai/HUMAN_BRIEF.md"

completion_policy: "completion_preserving"
---

# Math Mentor LRP-03 Teaching Prompt Consistency Repair

## 1. Task Position

This is the third long-running task in the Math Mentor Teaching System LRP suite.

It is based on:

- accepted LRP-01 teacher initialization and context-loading documents;
- accepted LRP-02 lesson plan schema and teaching agent contracts;
- the original Math Mentor teaching-system design implementation plan.

LRP-03 is the prompt-alignment task. It must repair existing prompt files so they obey the accepted system contracts. It must not create a new teaching system from scratch.

Do not split this task into file-level microtasks. This packet authorizes one coherent LRP-03 execution path: read, audit, repair the allowed prompt files, validate, report, commit, push working branch, and handoff.

## 2. Core Problem

The Math Mentor system now has:

1. LRP-01: a stable teacher initialization and lazy-loading path;
2. LRP-02: a stable `lesson_plan.json`, agent handoff, exam state vector, and bridge-slot contract.

But the older prompts may still contain conflicting assumptions:

- requiring context to already contain repository files instead of loading by path;
- confusing Plan 3 Engine A/B with Math Mentor Mode A/B;
- using Mode A/B language where `MathLane_A` / `MathLane_B` would reduce ambiguity;
- pressuring Socratic_Router into pure interrogation before explanation;
- forcing short question-only turns that prevent teaching-first behavior;
- claiming Z3, SymPy, PyTorch, or other tools have run without logs;
- allowing Exam_Agent to praise, teach, or imply long-term graduation.

LRP-03 must align the prompt layer to the contracts without touching node data, bridge data, schema files, runtime, or master/source publication.

## 3. Required Audit Document

Create or update:

- `08_Domain_Applications/Math_Mentor/TEACHING_PROMPT_CONSISTENCY_AUDIT.md`

Required sections:

1. `actually_read_files` summary;
2. prompt files audited;
3. issue matrix;
4. repairs applied;
5. invariant preservation;
6. validation checklist;
7. remaining non-blocking follow-up candidates.

The issue matrix should include rows shaped like:

```yaml
- issue_id: LRP03-001
  prompt_file: "..."
  evidence_before: "line/pattern or quoted fragment"
  conflict_with:
    - "LRP-01 lazy loading"
    - "LRP-02 lesson_plan schema"
    - "teach-before-interrogation"
    - "tool truthfulness"
  repair_decision: "rewrite | remove | preserve_with_note | defer"
  evidence_after: "line/pattern or summary"
  validation_status: "pass | blocked | deferred"
```

## 4. Allowed Prompt Repairs

### 4.1 Coordinator Prompt

Allowed repair intent:

- preserve the LRP-01 lazy-load preflight repair;
- ensure Coordinator output/handoff language points to LRP-02 contracts;
- separate Plan 3 `Engine_A` / `Engine_B` from Math Mentor `MathLane_A` / `MathLane_B`;
- preserve no-runtime and no-production-Coordinator-activation boundaries.

Do not rewrite Coordinator identity wholesale.

### 4.2 Prep_Architect Prompt

Allowed repair intent:

- require `LESSON_PLAN_SCHEMA.md`-compliant `lesson_plan.json`;
- require full `subtopic_plan` coverage;
- require `occurrence_crisis` before `formal_compression`;
- require bridge slots to follow `BRIDGE_SLOT_TEACHING_CONTRACT.md`;
- require evidence trace and tool truthfulness fields;
- forbid hidden learned-history assumptions.

Do not generate new node YAML or bridge files.

### 4.3 Socratic_Router Prompt

Allowed repair intent:

- rewrite high-pressure or pure-interrogation framing into teach-before-interrogation;
- preserve one compact forcing question after explanation;
- remove fake Z3/SymPy/PyTorch/tool execution claims;
- consume `lesson_plan.json`, `subtopic_plan`, `bridge_slots`, `reprep_triggers`, and evidence trace;
- require Exam handoff only after all subtopics and definition restatement;
- output Cognitive_State_Vector for Exam_Agent when handoff is valid.

This is the highest-risk part of LRP-03. Use extra-high reasoning and validate carefully.

### 4.4 Exam_Agent Prompt

Allowed repair intent:

- consume `Cognitive_State_Vector`;
- test muscle memory and edge-case trap;
- avoid teaching during exam;
- return `classroom_passed | failed | needs_reprep`;
- use structural confirmation, not empty praise;
- forbid long-term graduation claims;
- pass classroom result to future learning-state/spaced-review placeholder only.

Do not write learning-state or spaced-review files.

## 5. Required Validation Detail

The validation report must include:

```yaml
validation_result:
  required_refs_read:
    status: pass | fail
    missing_refs: []
  audit_document:
    exists: pass | fail
    issue_matrix_present: pass | fail
  prompt_repairs:
    coordinator_lazy_load_preserved: pass | fail
    coordinator_contract_alignment: pass | fail
    prep_lesson_plan_schema_alignment: pass | fail
    prep_full_subtopic_coverage: pass | fail
    socratic_teach_before_interrogation: pass | fail
    socratic_no_fake_tool_execution_claims: pass | fail
    socratic_exam_handoff_state_vector: pass | fail
    exam_state_vector_consumption: pass | fail
    exam_no_teaching: pass | fail
    exam_no_long_term_graduation: pass | fail
  namespace_and_authority:
    plan3_engine_vs_math_lane_distinguished: pass | fail
    human_speaker_authority_preserved: pass | fail
    no_runtime_or_coordinator_activation: pass | fail
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

## 6. Expected Handoff

Codex must publish a handoff on `ai/review/latest` with:

```yaml
packet_id: codex-math-mentor-lrp-03-teaching-prompt-consistency-repair-0001
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
