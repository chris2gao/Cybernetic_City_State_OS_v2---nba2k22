# Manual Test 05 CALCULUS-265 Results Validation

packet_id: codex-math-mentor-manual-test-05-calculus-265-results-0001
status: pass

## Validation Commands

Manual-test JSON/Markdown consistency assertions:

```text
python - <inline manual_test_05 assertion script>
```

Result:

```text
json_parses=pass
test_id=pass
target_node=pass
expected_behavior=pass
final_result_pass=pass
coordinator_ready_SYSTEM_STATE_DUMP=pass
prep_lesson_plan=pass
subtopic_coverage_5_of_5=pass
socratic_chain=pass
four_common_error_repairs=pass
exam_agent_trap_test=pass
classroom_pass_claimed_false=pass
scheduler_write_performed_false=pass
learning_state_write_performed_false=pass
runtime_activation_performed_false=pass
production_coordinator_activation_performed_false=pass
tool_execution_performed_false=pass
```

Static teaching-flow validator:

```text
python 08_Domain_Applications/Math_Mentor/tests/teaching_flow_static_validator.py
```

Result:

```text
overall_status=pass
json_result=08_Domain_Applications\Math_Mentor\tests\results\teaching_flow_static_validation_result.json
markdown_result=08_Domain_Applications\Math_Mentor\tests\results\teaching_flow_static_validation_result.md
```

Diff whitespace check:

```text
git diff --check -- 08_Domain_Applications/Math_Mentor/tests/results/manual_test_05_calculus_265_ready_teaching_flow.json 08_Domain_Applications/Math_Mentor/tests/results/manual_test_05_calculus_265_ready_teaching_flow.md
```

Result: pass.

Scoped secret scan over changed files:

```text
scoped_secret_scan=pass
```

## Validation Requirements

- JSON parses: pass
- JSON/MD agree on test id: pass
- JSON/MD agree on target node: pass
- JSON/MD agree on expected behavior: pass
- JSON/MD agree on final result: pass
- Coordinator ready state dump: pass
- Prep lesson plan: pass
- Subtopic coverage 5/5: pass
- Socratic chain: pass
- Four common error repairs: pass
- Exam_Agent trap test: pass
- No classroom pass claimed: pass
- No scheduler write: pass
- No learning-state write: pass
- No runtime activation: pass
- No production Coordinator activation: pass
- No tool execution: pass
- Static validator overall status: pass
- Changed files limited to allowed files: pass
- No prompt/node/schema/validator/runtime/Coordinator/scheduler files changed: pass
