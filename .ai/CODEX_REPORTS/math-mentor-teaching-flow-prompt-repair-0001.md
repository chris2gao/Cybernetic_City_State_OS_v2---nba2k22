# Math Mentor Teaching Flow Prompt Repair Report

packet_id: codex-math-mentor-teaching-flow-prompt-repair-0001
status: completed_for_review

## Summary

This task repaired the manual chat teaching-flow and prompt layer after Math Mentor LRP-01 through LRP-06 were published to master.

Updated files:

- `08_Domain_Applications/Math_Mentor/V9.1_教学流程系统规范_Teaching_Flow_Spec.md`
- `08_Domain_Applications/Math_Mentor/08_Math_Mentor_Coordinator_Prompt.md`
- `08_Domain_Applications/Math_Mentor/学习期prompt/Prep_Architect_Prompt.md`
- `08_Domain_Applications/Math_Mentor/学习期prompt/Socratic_Router_Prompt_v7.0.md`
- `08_Domain_Applications/Math_Mentor/学习期prompt/Exam_Agent_Prompt.md`

The repair aligns these files with the accepted contracts from LRP-01 through LRP-06:

- lazy loading and `actually_read_files`;
- Plan 3 `Engine_A/B` versus Math Mentor `MathLane_A/B` namespace separation;
- Prep wrapper containing `lesson_plan`, `coverage_map`, `handoff_status`, `evidence_trace`, and `tool_truthfulness`;
- Socratic teach-before-interrogation behavior;
- Exam_Agent independent testing boundary;
- tool truthfulness states: `not_run`, `run_with_log`, `unavailable`, `semantic_only`, `planned`, `review_required`;
- classroom pass as current classroom evidence only, not long-term graduation.

## Manual Test Readiness

manual_test_ready: true

The corrected flow supports manual chat-based teaching tests without runtime activation:

1. Human names a target node or concept.
2. Coordinator loads minimal authority and target evidence.
3. Coordinator emits compressed `SYSTEM_STATE_DUMP`.
4. Prep_Architect emits the wrapper JSON.
5. Socratic_Router teaches first, then asks one compact question.
6. Exam_Agent tests independently.
7. Spaced-review output remains a placeholder unless future authorization exists.

## No-Runtime Boundary

This task did not activate runtime, production Coordinator, external apps, MCP, deterministic tools, visualization, node generation, bridge generation, learning-state writes, learned-history writes, or scheduler writes.

## Dry-Run Outline: MathLane_A

- Use a basic computable concept.
- Coordinator reports `Math_Lane: MathLane_A`.
- Prep uses `intuition_model.kind: everyday_physical`.
- Socratic explains the low-friction model before asking one question.
- Tool status remains `not_run` unless a real `run_with_log` exists.
- No claim of actual target YAML loading is allowed unless the target YAML path appears in `actually_read_files`.

## Dry-Run Outline: MathLane_B

- Use an abstract pure-structure concept.
- Coordinator reports `Math_Lane: MathLane_B`.
- Prep uses `intuition_model.kind: llm_architecture`.
- Socratic teaches from LLM architecture mapping and states the boundary.
- Tool evidence remains `semantic_only` or `not_run` unless a real `run_with_log` exists.
- Household or factory metaphors are not primary MathLane_B teaching models.
