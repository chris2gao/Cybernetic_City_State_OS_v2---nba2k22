---
task_version: "1.0"
task_id: "math-mentor-lrp-02-lesson-plan-agent-contract-0001"
title: "Math Mentor LRP-02 Lesson Plan Schema And Agent Contract"
mode: "goal"
task_level: 2

intent:
  goal: "Complete LRP-02 by formalizing the shared lesson_plan.json schema and the Coordinator/Prep/Socratic/Exam agent contracts for Math Mentor teaching."
  why_now: "LRP-01 has closed the teacher initialization and context-loading path. The next blocker is that the Math Mentor teaching pipeline has agents, but no hard shared data contract for what Coordinator requests, what Prep_Architect produces, what Socratic_Router consumes, and what Exam_Agent receives."
  definition_of_done:
    - "LESSON_PLAN_SCHEMA.md exists and defines the canonical lesson_plan.json schema with required fields, optional fields, invariants, examples, and validation rules."
    - "TEACHING_AGENT_CONTRACTS.md exists and defines the handoff contracts among Coordinator, Prep_Architect, Socratic_Router, Exam_Agent, and later review/learning-state layers without activating runtime."
    - "EXAM_HANDOFF_STATE_VECTOR_SCHEMA.md exists and defines the high-resolution Cognitive_State_Vector and Exam_Agent handoff payload."
    - "BRIDGE_SLOT_TEACHING_CONTRACT.md exists and defines bridge-slot display, learned-history gating, teaser-only behavior, endpoint evidence, and first-use comprehension checks."
    - "The new contracts preserve LRP-01 lazy-loading, Plan 3 Human Speaker authority, teach-before-interrogation, no fake tool execution, and no runtime/Coordinator activation."
    - "Validation and handoff reports are produced."

outputs:
  primary: "08_Domain_Applications/Math_Mentor/LESSON_PLAN_SCHEMA.md"
  additional:
    - "08_Domain_Applications/Math_Mentor/TEACHING_AGENT_CONTRACTS.md"
    - "08_Domain_Applications/Math_Mentor/EXAM_HANDOFF_STATE_VECTOR_SCHEMA.md"
    - "08_Domain_Applications/Math_Mentor/BRIDGE_SLOT_TEACHING_CONTRACT.md"
    - ".ai/CODEX_REPORTS/math-mentor-lrp-02-lesson-plan-agent-contract-0001.md"
    - ".ai/CODEX_REPORTS/math-mentor-lrp-02-lesson-plan-agent-contract-validation-0001.md"
    - ".ai/CODEX_REPORTS/math-mentor-lrp-02-lesson-plan-agent-contract-changed-files-0001.md"
    - ".ai/CODEX_REPORTS/math-mentor-lrp-02-lesson-plan-agent-contract-actually-read-files-0001.md"

inputs:
  required_refs:
    - ".ai/TASKS/math-mentor-lrp-02-lesson-plan-agent-contract-0001.md"
    - "08_Domain_Applications/Math_Mentor/Math Mentor Teaching System Design implement plan.md"
    - "08_Domain_Applications/Math_Mentor/Math Mentor Teaching System Design.md"
    - "08_Domain_Applications/Math_Mentor/TEACHER_INITIALIZATION_FLOW.md"
    - "08_Domain_Applications/Math_Mentor/TEACHER_CONTEXT_LOADING_RULES.md"
    - "08_Domain_Applications/Math_Mentor/TEACHER_INITIALIZATION_DRY_RUNS.md"
    - "08_Domain_Applications/Math_Mentor/08_Math_Mentor_Coordinator_Prompt.md"
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
    name: "dev/math-mentor-lrp-02-lesson-plan-agent-contract-0001"
    create_from: "the exact source_head in the short signal that points to this task packet"
  allowed_files:
    - "08_Domain_Applications/Math_Mentor/LESSON_PLAN_SCHEMA.md"
    - "08_Domain_Applications/Math_Mentor/TEACHING_AGENT_CONTRACTS.md"
    - "08_Domain_Applications/Math_Mentor/EXAM_HANDOFF_STATE_VECTOR_SCHEMA.md"
    - "08_Domain_Applications/Math_Mentor/BRIDGE_SLOT_TEACHING_CONTRACT.md"
    - ".ai/CODEX_REPORTS/math-mentor-lrp-02-lesson-plan-agent-contract-0001.md"
    - ".ai/CODEX_REPORTS/math-mentor-lrp-02-lesson-plan-agent-contract-validation-0001.md"
    - ".ai/CODEX_REPORTS/math-mentor-lrp-02-lesson-plan-agent-contract-changed-files-0001.md"
    - ".ai/CODEX_REPORTS/math-mentor-lrp-02-lesson-plan-agent-contract-actually-read-files-0001.md"
    - ".ai/OUTBOX.md"
    - ".ai/HUMAN_BRIEF.md"
    - ".ai/STATE.yml"
  forbidden_files:
    - "08_Domain_Applications/Math_Mentor/Pure_Math_Intuition_DB/**"
    - "08_Domain_Applications/Math_Mentor/bridges/**"
    - "08_Domain_Applications/Math_Mentor/BRIDGE_SCHEMA.md"
    - "08_Domain_Applications/Math_Mentor/BRIDGE_REGISTRY*.md"
    - "08_Domain_Applications/Math_Mentor/KNOWLEDGE_COMPLETION_PROGRAM.md"
    - "08_Domain_Applications/Math_Mentor/08_Math_Mentor_Coordinator_Prompt.md"
    - "08_Domain_Applications/Math_Mentor/学习期prompt/Prep_Architect_Prompt.md"
    - "08_Domain_Applications/Math_Mentor/学习期prompt/Socratic_Router_Prompt_v7.0.md"
    - "08_Domain_Applications/Math_Mentor/学习期prompt/Exam_Agent_Prompt.md"
    - "08_Domain_Applications/Math_Mentor/TEACHER_INITIALIZATION_FLOW.md"
    - "08_Domain_Applications/Math_Mentor/TEACHER_CONTEXT_LOADING_RULES.md"
    - "08_Domain_Applications/Math_Mentor/TEACHER_INITIALIZATION_DRY_RUNS.md"
    - "未完成任务备忘录.yml"
  allowed_actions:
    - "create the working branch from the exact source head"
    - "read required refs"
    - "create the four LRP-02 schema/contract documents"
    - "write consolidated reports"
    - "commit explicit paths on the working branch"
    - "push only the working branch"
    - "publish final handoff to ai/review/latest"

requirements:
  invariants:
    - "Plan 3 Human Speaker authority remains the top-level route, translation, and final-decision model."
    - "Math Mentor teaching remains an Engine B domain teaching task; deterministic tool use may support but not replace teaching judgment."
    - "LRP-01 lazy-loading and actually_read_files evidence rules are preserved."
    - "No prompt may claim a tool has run unless this task actually ran it and recorded a command/log/report."
    - "This task does not activate runtime, production Coordinator execution, external apps, automation, or MCP/app integrations."
    - "This task does not generate new math nodes, bridges, bridge schema, evaluator code, or production runtime code."
    - "This task does not repair Socratic_Router, Prep_Architect, Exam_Agent, or Coordinator prompt wording; prompt consistency repair belongs to LRP-03 unless a reference is needed inside the new contract documents."
    - "Completion-preserving execution is mandatory: reading, design, document creation, validation, reporting, commit, branch push, and handoff are one task."
  validation:
    - "all required refs were read or any missing ref is explicitly reported with path, branch, and failure reason"
    - "the four new LRP-02 documents exist on the working branch"
    - "LESSON_PLAN_SCHEMA.md contains canonical top-level fields for target_node, math_lane, routing_basis, student_state, subtopic_plan, occurrence_crisis, intuition_model, formal_compression, bridge_slots, learned_history_reference, exam_handoff_conditions, and reprep_triggers"
    - "TEACHING_AGENT_CONTRACTS.md defines at least Coordinator-to-Prep, Prep-to-Socratic, Socratic-to-Exam, Exam-to-learning-state/review-scheduler placeholder, and failure/re-prep handoff contracts"
    - "EXAM_HANDOFF_STATE_VECTOR_SCHEMA.md defines high-resolution Cognitive_State_Vector fields for struggled concept, false intuition, definition boundary, trap direction, subtopic coverage, bridge comprehension, and tool/evidence limitations"
    - "BRIDGE_SLOT_TEACHING_CONTRACT.md defines first-use display, learned-history gating, teaser-only behavior, endpoint evidence, legacy bridge omission, and one compact comprehension check"
    - "the contracts distinguish Plan 3 Engine A/B from Math Mentor Mode/Lane A/B to avoid namespace confusion"
    - "no fake Z3/SymPy/PyTorch/tool execution claim is introduced"
    - "no full-repository ingestion or full Math Mentor ingestion rule is introduced"
    - "changed files are limited to allowed_files"
    - "forbidden_files are not modified"
    - "scoped secret scan passes"
    - "remote read-back verifies the pushed working branch and report refs"
  stop_rules:
    - "source head mismatch before working branch creation"
    - "required refs missing in a way that prevents safe contract design"
    - "need to modify forbidden files"
    - "need for new node generation, bridge generation, bridge schema mutation, runtime activation, or Coordinator activation"
    - "need to repair Prep/Socratic/Exam prompts directly"
    - "security/privacy/secret risk"
    - "merge/master/source publication requirement not authorized by this task"
    - "validation failure after one safe repair pass"

authority:
  semantic_reviewer: "chatgpt"
  human_gate: "required_after_completion"
  master_push_authorized: false
  source_branch_push_authorized: false
  working_branch_push_authorized: true

return:
  packet_id: "codex-math-mentor-lrp-02-lesson-plan-agent-contract-0001"
  report_ref: ".ai/CODEX_REPORTS/math-mentor-lrp-02-lesson-plan-agent-contract-0001.md"
  validation_ref: ".ai/CODEX_REPORTS/math-mentor-lrp-02-lesson-plan-agent-contract-validation-0001.md"
  changed_files_ref: ".ai/CODEX_REPORTS/math-mentor-lrp-02-lesson-plan-agent-contract-changed-files-0001.md"
  actually_read_files_ref: ".ai/CODEX_REPORTS/math-mentor-lrp-02-lesson-plan-agent-contract-actually-read-files-0001.md"
  brief_ref: ".ai/HUMAN_BRIEF.md"

completion_policy: "completion_preserving"
---

# Math Mentor LRP-02 Lesson Plan Schema And Agent Contract

## 1. Task Position

This is the second long-running task in the Math Mentor Teaching System LRP suite.

It is based on:

- `08_Domain_Applications/Math_Mentor/Math Mentor Teaching System Design implement plan.md`
- `08_Domain_Applications/Math_Mentor/Math Mentor Teaching System Design.md`
- accepted LRP-01 outputs on the source branch

LRP-01 established how a new independent model becomes a Math Mentor teacher and loads context. LRP-02 must now define the data contracts that let the teaching pipeline operate without hidden assumptions.

Do not split this task into file-level microtasks. This packet authorizes one coherent LRP-02 execution path: read, design, create the four schema/contract documents, validate, report, commit, push working branch, and handoff.

## 2. Core Problem

The Math Mentor system already has conceptual agents:

1. Coordinator;
2. Prep_Architect;
3. Socratic_Router;
4. Exam_Agent;
5. later learning-state / spaced-review layer.

But the shared data shape between them is not yet formalized. Without a shared contract:

- Prep may produce a `lesson_plan.json` that Socratic cannot reliably consume;
- Socratic may fail to cover all `sub_topics`;
- bridge slots may be hidden, over-dumped, or used without learned-history evidence;
- Exam handoff may lack the precise cognitive state needed for trap design;
- later LRP-03 prompt repairs may have no stable contract to align against.

LRP-02 must solve the contract problem without mutating node/bridge data, existing agent prompts, or runtime code.

## 3. Required LRP-02 Documents

### 3.1 `LESSON_PLAN_SCHEMA.md`

This document must define the canonical `lesson_plan.json` schema.

It should include:

- purpose and authority;
- JSON schema-style structure;
- required top-level fields;
- optional fields;
- validation rules;
- failure cases;
- at least one compact valid example;
- at least one invalid example with explanation.

Required semantic fields:

```json
{
  "target_node": {
    "id": "n_xxx",
    "name": "...",
    "definition": "...",
    "math_lane": "MathLane_A | MathLane_B | mixed",
    "routing_basis": "..."
  },
  "student_state": {
    "known_nodes": [],
    "blocked_prerequisites": [],
    "misconceptions": [],
    "learned_history_state": "loaded | unavailable | not_needed",
    "frustration_index": 0
  },
  "subtopic_plan": [
    {
      "subtopic_id": "s1",
      "name": "...",
      "role": "core | auxiliary",
      "explanation_goal": "...",
      "forcing_question": "...",
      "completion_check": "..."
    }
  ],
  "occurrence_crisis": {
    "old_tool_failure": "...",
    "why_this_concept_must_exist": "..."
  },
  "intuition_model": {
    "kind": "everyday_physical | llm_architecture | mixed_transition",
    "content": "...",
    "limitation": "..."
  },
  "formal_compression": {
    "definition": "...",
    "boundary_conditions": [],
    "common_counterexamples": []
  },
  "bridge_slots": [],
  "learned_history_reference": {
    "source": "persisted_state | unavailable | strict_sequential_fallback",
    "limits": "..."
  },
  "exam_handoff_conditions": {
    "all_subtopics_covered": false,
    "definition_restatement_required": true,
    "trap_direction": "..."
  },
  "reprep_triggers": {
    "metaphor_failure": "...",
    "student_frustration_threshold": 3,
    "missing_mapping_status": "..."
  }
}
```

The exact final schema may differ, but it must preserve these semantics.

### 3.2 `TEACHING_AGENT_CONTRACTS.md`

This document must define explicit handoff contracts:

1. Human/Coordinator input contract;
2. Coordinator-to-Prep request contract;
3. Prep-to-Socratic `lesson_plan.json` contract;
4. Socratic-to-Exam handoff contract;
5. Exam-to-learning-state / spaced-review placeholder contract;
6. re-prep / failure / drift handoff contract.

It must clarify:

- who produces the payload;
- who consumes the payload;
- required fields;
- forbidden assumptions;
- stop conditions;
- how `actually_read_files` and evidence traces travel through the pipeline.

### 3.3 `EXAM_HANDOFF_STATE_VECTOR_SCHEMA.md`

This document must define the high-resolution `Cognitive_State_Vector` needed by Exam_Agent.

Required semantic fields:

- target node;
- covered subtopics;
- student restated definition;
- struggled concept;
- false intuition;
- definition boundary at risk;
- bridge comprehension status;
- recommended trap direction;
- evidence limits;
- tool/evidence status;
- unresolved prerequisites;
- pass/fail criteria for Exam_Agent.

It must state that Exam_Agent cannot claim long-term graduation. Classroom pass is not spaced-review graduation.

### 3.4 `BRIDGE_SLOT_TEACHING_CONTRACT.md`

This document must define how bridges become teaching slots.

Required semantics:

- bridge slot is a first-class learning object;
- first use must show node id or bridge id, name, bridge type, learned status, and one-sentence logical connection;
- bridge learned status must come from persisted learned history when available;
- `forward_outlook_bridge` to unlearned knowledge is teaser-only;
- legacy bridge records with ambiguous endpoints must be omitted and flagged, not invented;
- one compact comprehension check is required on first use;
- repeated bridge metadata dumping within one target lesson is forbidden.

## 4. Namespace Rule

LRP-02 must clearly distinguish:

- Plan 3 `Engine_A` / `Engine_B`, which are city-state authority and task-routing categories;
- Math Mentor `Mode A` / `Mode B` or `MathLane_A` / `MathLane_B`, which are domain teaching lanes.

The new documents may recommend `MathLane_A` and `MathLane_B` as clearer names, but must not require prompt mutation in LRP-02. Direct prompt rename belongs to LRP-03.

## 5. Tool Truthfulness Rule

LRP-02 documents must not introduce tool-execution claims.

Allowed wording:

- "can be verified by a deterministic tool";
- "requires a tool log before claiming execution";
- "semantic audit only";
- "tool status: not_run | run_with_log | unavailable".

Forbidden wording unless a real command/log/report exists in this task:

- "Z3 has verified";
- "SymPy has computed";
- "PyTorch has checked";
- "the calculator ran".

## 6. Relationship To Later LRPs

LRP-02 must not do LRP-03, LRP-04, LRP-05, or LRP-06 work.

It may include placeholder references for later tasks:

- LRP-03 will align existing prompts to these contracts.
- LRP-04 will build golden tests and E2E simulations from these contracts.
- LRP-05 will implement persistent learning-state / spaced-review schemas.
- LRP-06 will formalize tool/capability truthfulness and future deterministic calculation handoff.

## 7. Required Validation Detail

The validation report must include:

```yaml
validation_result:
  required_refs_read:
    status: pass | fail
    missing_refs: []
  new_documents_exist:
    lesson_plan_schema: pass | fail
    teaching_agent_contracts: pass | fail
    exam_handoff_state_vector_schema: pass | fail
    bridge_slot_teaching_contract: pass | fail
  schema_semantics:
    target_node: pass | fail
    math_lane: pass | fail
    subtopic_plan: pass | fail
    occurrence_crisis: pass | fail
    intuition_model: pass | fail
    formal_compression: pass | fail
    bridge_slots: pass | fail
    learned_history_reference: pass | fail
    exam_handoff_conditions: pass | fail
    reprep_triggers: pass | fail
  agent_contracts:
    coordinator_to_prep: pass | fail
    prep_to_socratic: pass | fail
    socratic_to_exam: pass | fail
    exam_to_learning_state_placeholder: pass | fail
    drift_or_reprep_handoff: pass | fail
  bridge_contract:
    first_use_visibility: pass | fail
    learned_history_gating: pass | fail
    teaser_only_forward_outlook: pass | fail
    ambiguous_legacy_bridge_omission: pass | fail
    comprehension_check: pass | fail
  namespace_and_truthfulness:
    plan3_engine_vs_math_lane_distinguished: pass | fail
    no_fake_tool_execution_claims: pass | fail
    no_full_ingestion_rule_introduced: pass | fail
  scope:
    allowed_only: pass | fail
    forbidden_changes: []
  secret_scan:
    status: pass | fail
```

## 8. Expected Handoff

Codex must publish a handoff on `ai/review/latest` with:

```yaml
packet_id: codex-math-mentor-lrp-02-lesson-plan-agent-contract-0001
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
