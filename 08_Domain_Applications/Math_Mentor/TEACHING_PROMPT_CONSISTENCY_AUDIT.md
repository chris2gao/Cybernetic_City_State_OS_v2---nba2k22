# Teaching Prompt Consistency Audit

Status: LRP-03 audit and repair record.

## 1. Actually Read Files Summary

The LRP-03 repair used targeted reading and search over the required references. It did not ingest the full repository or the full Math Mentor directory.

Required refs read or queried:

- `.ai/TASKS/math-mentor-lrp-03-teaching-prompt-consistency-repair-0001.md`
- `08_Domain_Applications/Math_Mentor/Math Mentor Teaching System Design implement plan.md`
- `08_Domain_Applications/Math_Mentor/Math Mentor Teaching System Design.md`
- `08_Domain_Applications/Math_Mentor/TEACHER_INITIALIZATION_FLOW.md`
- `08_Domain_Applications/Math_Mentor/TEACHER_CONTEXT_LOADING_RULES.md`
- `08_Domain_Applications/Math_Mentor/TEACHER_INITIALIZATION_DRY_RUNS.md`
- `08_Domain_Applications/Math_Mentor/LESSON_PLAN_SCHEMA.md`
- `08_Domain_Applications/Math_Mentor/TEACHING_AGENT_CONTRACTS.md`
- `08_Domain_Applications/Math_Mentor/EXAM_HANDOFF_STATE_VECTOR_SCHEMA.md`
- `08_Domain_Applications/Math_Mentor/BRIDGE_SLOT_TEACHING_CONTRACT.md`
- `08_Domain_Applications/Math_Mentor/08_Math_Mentor_Coordinator_Prompt.md`
- `08_Domain_Applications/Math_Mentor/学习期prompt/Prep_Architect_Prompt.md`
- `08_Domain_Applications/Math_Mentor/学习期prompt/Socratic_Router_Prompt_v7.0.md`
- `08_Domain_Applications/Math_Mentor/学习期prompt/Exam_Agent_Prompt.md`
- `08_Domain_Applications/Math_Mentor/V9.1_教学流程系统规范_Teaching_Flow_Spec.md`
- `08_Domain_Applications/Math_Mentor/V9.1_认知映射引擎_终极实装蓝图.md`
- `08_Domain_Applications/Math_Mentor/Math_Mentor_V9.1_从生成到教学的完整流程.md`
- `08_Domain_Applications/Math_Mentor/BRIDGE_SCHEMA.md`
- `3号方案.md`
- `06_Silicon_Index/AI_Bootstrap_Sequence.md`
- `06_Silicon_Index/06_Cybernetic_Citizen_Awakening.md`
- `.ai/PROTOCOL.md`
- `.ai/CODEX_WORK_MECHANISM_PROTOCOL.md`
- `.ai/CODEX_TASK_INPUT_CONTRACT.md`
- `.ai/LONG_RUN_AUTONOMOUS_PROGRAM_PROTOCOL.md`

No required ref was missing.

## 2. Prompt Files Audited

- `08_Domain_Applications/Math_Mentor/08_Math_Mentor_Coordinator_Prompt.md`
- `08_Domain_Applications/Math_Mentor/学习期prompt/Prep_Architect_Prompt.md`
- `08_Domain_Applications/Math_Mentor/学习期prompt/Socratic_Router_Prompt_v7.0.md`
- `08_Domain_Applications/Math_Mentor/学习期prompt/Exam_Agent_Prompt.md`

## 3. Issue Matrix

```yaml
- issue_id: LRP03-001
  prompt_file: "08_Domain_Applications/Math_Mentor/08_Math_Mentor_Coordinator_Prompt.md"
  evidence_before: "Coordinator used legacy Mode A / Mode B labels without an explicit Plan 3 Engine versus Math Mentor lane namespace boundary."
  conflict_with: ["LRP-02 namespace rule", "Plan 3 authority distinction"]
  repair_decision: "rewrite"
  evidence_after: "Added namespace isolation and mapped legacy Mode labels to MathLane_A / MathLane_B / mixed."
  validation_status: "pass"
- issue_id: LRP03-002
  prompt_file: "08_Domain_Applications/Math_Mentor/08_Math_Mentor_Coordinator_Prompt.md"
  evidence_before: "COMPUTATIONAL_AUDIT_STRICT could be read as direct tool execution."
  conflict_with: ["tool truthfulness", "LRP-02 tool_truthfulness"]
  repair_decision: "rewrite"
  evidence_after: "Audit paths are validation requirements; execution claims require a real command log or report."
  validation_status: "pass"
- issue_id: LRP03-003
  prompt_file: "08_Domain_Applications/Math_Mentor/学习期prompt/Prep_Architect_Prompt.md"
  evidence_before: "Old output schema only had systemic_context, crisis_scenario, metaphor_framework, and verification_contract."
  conflict_with: ["LRP-02 lesson_plan schema", "Prep-to-Socratic contract"]
  repair_decision: "rewrite"
  evidence_after: "Prompt now requires all canonical LESSON_PLAN_SCHEMA.md top-level fields."
  validation_status: "pass"
- issue_id: LRP03-004
  prompt_file: "08_Domain_Applications/Math_Mentor/学习期prompt/Prep_Architect_Prompt.md"
  evidence_before: "Old prompt did not require full subtopic coverage map or learned-history limits."
  conflict_with: ["subtopic full coverage", "bridge learned-history gating"]
  repair_decision: "rewrite"
  evidence_after: "Prompt now requires every source sub_topics entry in subtopic_plan and explicit bridge/learned-history status."
  validation_status: "pass"
- issue_id: LRP03-005
  prompt_file: "08_Domain_Applications/Math_Mentor/学习期prompt/Socratic_Router_Prompt_v7.0.md"
  evidence_before: "Old prompt called itself an emotionless Socratic questioning machine and used high-pressure interrogation framing."
  conflict_with: ["teach-before-interrogation", "LRP-02 Socratic-to-Exam contract"]
  repair_decision: "rewrite"
  evidence_after: "Prompt now requires compact explanation, intuition/formal boundary, then one compact forcing question."
  validation_status: "pass"
- issue_id: LRP03-006
  prompt_file: "08_Domain_Applications/Math_Mentor/学习期prompt/Socratic_Router_Prompt_v7.0.md"
  evidence_before: "Old prompt required the teacher to claim the underlying Z3 engine had run calculations."
  conflict_with: ["tool truthfulness", "no fake tool execution claims"]
  repair_decision: "remove"
  evidence_after: "Prompt now forbids deterministic execution claims unless tool_status is run_with_log and a log reference exists."
  validation_status: "pass"
- issue_id: LRP03-007
  prompt_file: "08_Domain_Applications/Math_Mentor/学习期prompt/Socratic_Router_Prompt_v7.0.md"
  evidence_before: "Old prompt did not require the full high-resolution Cognitive_State_Vector defined in LRP-02."
  conflict_with: ["EXAM_HANDOFF_STATE_VECTOR_SCHEMA.md"]
  repair_decision: "rewrite"
  evidence_after: "Prompt now outputs target_node plus Cognitive_State_Vector with subtopic, definition, bridge, tool/evidence, prerequisite, and trap fields."
  validation_status: "pass"
- issue_id: LRP03-008
  prompt_file: "08_Domain_Applications/Math_Mentor/学习期prompt/Exam_Agent_Prompt.md"
  evidence_before: "Old prompt could praise, teach replacement questions, and emit NODE_CLEARED without the LRP-02 state taxonomy."
  conflict_with: ["Exam-to-learning-state placeholder", "no empty praise", "Exam Agent must not teach"]
  repair_decision: "rewrite"
  evidence_after: "Prompt now returns classroom_passed, failed, or needs_reprep and forbids teaching during exam."
  validation_status: "pass"
- issue_id: LRP03-009
  prompt_file: "08_Domain_Applications/Math_Mentor/学习期prompt/Exam_Agent_Prompt.md"
  evidence_before: "Old prompt lacked explicit long-term graduation boundary."
  conflict_with: ["spaced-review handoff", "no long-term graduation claim"]
  repair_decision: "rewrite"
  evidence_after: "Prompt states classroom_passed is not long-term graduation and defers spaced-review validation."
  validation_status: "pass"
```

## 4. Repairs Applied

- Coordinator prompt now explicitly separates Plan 3 `Engine_A` / `Engine_B` from Math Mentor `MathLane_A` / `MathLane_B`.
- Coordinator state dump now exposes `Math_Lane`, `lesson_plan_contract`, `tool_truthfulness`, and `actually_read_files`.
- Coordinator computational-audit wording now requires a real log/report before any tool-execution claim.
- Prep_Architect prompt now produces an LRP-02-compliant `lesson_plan.json`.
- Prep_Architect prompt now requires full `subtopic_plan` coverage, `occurrence_crisis` before `formal_compression`, bridge slot evidence, learned-history limits, and tool truthfulness.
- Socratic_Router prompt now implements teach-before-interrogation and one compact forcing question after explanation.
- Socratic_Router prompt now consumes `lesson_plan.json`, validates required fields, handles bridge slots and re-prep triggers, and outputs a high-resolution `Cognitive_State_Vector`.
- Exam_Agent prompt now consumes `Cognitive_State_Vector`, tests without teaching, returns only classroom result states, and forbids long-term graduation claims.

## 5. Invariant Preservation

- LRP-01 lazy loading and `actually_read_files` evidence rules were preserved.
- LRP-02 contracts were treated as alignment targets and were not modified.
- No `Pure_Math_Intuition_DB` files were modified.
- No bridge files or `BRIDGE_SCHEMA.md` were modified.
- No evaluator, runtime, production Coordinator, learning-state, or spaced-review files were modified.
- No source branch or master branch publication was performed.
- No `git reset --hard`, force push, push-all, node generation, or bridge generation was performed.

## 6. Validation Checklist

- [x] Coordinator preflight lazy-load behavior remains present.
- [x] Coordinator old upload/refusal behavior remains absent.
- [x] Prep_Architect requires LRP-02-compliant `lesson_plan.json`.
- [x] Prep_Architect requires full subtopic coverage.
- [x] Socratic_Router no longer enforces pure interrogation before explanation.
- [x] Socratic_Router preserves one compact forcing question after explanation.
- [x] Socratic_Router removes fake deterministic tool-execution claims.
- [x] Socratic_Router produces `Cognitive_State_Vector`.
- [x] Exam_Agent consumes `Cognitive_State_Vector`.
- [x] Exam_Agent tests without teaching.
- [x] Exam_Agent forbids long-term graduation claims.
- [x] All four prompts distinguish Plan 3 engine namespace from Math Mentor lane namespace.
- [x] Changed files are limited to allowed LRP-03 files.

## 7. Remaining Non-Blocking Follow-Up Candidates

- LRP-04 can turn these prompt contracts into golden teaching tests.
- LRP-05 can implement the persistent learning-state / spaced-review schema.
- LRP-06 can formalize deterministic capability handoff and tool-log evidence contracts.
