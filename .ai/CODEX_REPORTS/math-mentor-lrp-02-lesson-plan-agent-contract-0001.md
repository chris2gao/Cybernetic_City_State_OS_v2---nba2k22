# Math Mentor LRP-02 Lesson Plan Agent Contract Report

packet_id: codex-math-mentor-lrp-02-lesson-plan-agent-contract-0001
task_id: math-mentor-lrp-02-lesson-plan-agent-contract-0001
status: completed_for_review
source_branch: dev/protocol-human-cost-and-drift-control-0001
source_head: ae055692fd8352cadd637b30e95586fde2c9d778
dev_branch: dev/math-mentor-lrp-02-lesson-plan-agent-contract-0001
master_head: eb918a55becefe609e27723073a38be319f10586
human_gate: required

## 1. Scope

LRP-02 formalized the data contracts needed before LRP-03 prompt alignment:

- canonical `lesson_plan.json` schema;
- Coordinator / Prep_Architect / Guided_Socratic_Router / Exam_Agent handoff contracts;
- high-resolution Exam `Cognitive_State_Vector`;
- bridge-slot teaching contract.

The task was completed as a documentation and protocol contract task. It did not mutate nodes, bridges, bridge schema, evaluator code, prompts, runtime code, learning-state files, or production Coordinator behavior.

## 2. Created Documents

- `08_Domain_Applications/Math_Mentor/LESSON_PLAN_SCHEMA.md`
- `08_Domain_Applications/Math_Mentor/TEACHING_AGENT_CONTRACTS.md`
- `08_Domain_Applications/Math_Mentor/EXAM_HANDOFF_STATE_VECTOR_SCHEMA.md`
- `08_Domain_Applications/Math_Mentor/BRIDGE_SLOT_TEACHING_CONTRACT.md`

## 3. Contract Summary

`LESSON_PLAN_SCHEMA.md` defines required top-level `lesson_plan.json` fields, examples, invalid cases, and validation rules. It uses `MathLane_A`, `MathLane_B`, and `mixed` to avoid confusion with Plan 3 engine names.

`TEACHING_AGENT_CONTRACTS.md` defines:

- Human / Coordinator input;
- Coordinator-to-Prep;
- Prep-to-Socratic;
- Socratic-to-Exam;
- Exam-to-learning-state / review-scheduler placeholder;
- failure, drift, and re-prep handoff.

`EXAM_HANDOFF_STATE_VECTOR_SCHEMA.md` defines the `Cognitive_State_Vector` with subtopic coverage, student definition restatement, struggled concept, false intuition, definition boundary risk, trap direction, bridge comprehension, tool/evidence limitations, unresolved prerequisites, and classroom pass/fail criteria.

`BRIDGE_SLOT_TEACHING_CONTRACT.md` defines first-use bridge display, learned-history gating, teaser-only forward outlook, endpoint evidence, ambiguous legacy bridge omission, and one compact comprehension check.

## 4. Preserved Boundaries

- Plan 3 Human Speaker authority remains the top-level route, translation, and final decision model.
- Math Mentor teaching remains an Engine B domain teaching task.
- LRP-01 lazy-loading and `actually_read_files` evidence rules are preserved.
- The new contracts do not introduce full-repository or full Math Mentor ingestion rules.
- Tool execution is represented through explicit truthfulness fields and log requirements.
- LRP-03 prompt repair was not started.
- LRP-04 tests, LRP-05 learning-state implementation, and LRP-06 tool handoff design were not started.

## 5. Drift Control

drift_cause: null
avoided_extra_gates:
- validation, reports, branch commit, branch push, and review handoff were folded into the original LRP-02 task.
final_original_task_status: completed_for_review
remaining_real_human_decisions_only:
- ChatGPT / Human review of LRP-02 contracts.
- Separate authorization before LRP-03.
- Separate authorization before publishing back to the source branch.

## 6. Related Artifacts

- Validation: `.ai/CODEX_REPORTS/math-mentor-lrp-02-lesson-plan-agent-contract-validation-0001.md`
- Changed files: `.ai/CODEX_REPORTS/math-mentor-lrp-02-lesson-plan-agent-contract-changed-files-0001.md`
- Actually read files: `.ai/CODEX_REPORTS/math-mentor-lrp-02-lesson-plan-agent-contract-actually-read-files-0001.md`
- Human brief: `.ai/HUMAN_BRIEF.md`
