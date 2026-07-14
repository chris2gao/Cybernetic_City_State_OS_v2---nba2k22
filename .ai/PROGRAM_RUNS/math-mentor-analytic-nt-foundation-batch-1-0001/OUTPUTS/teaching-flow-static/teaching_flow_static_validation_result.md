# Teaching Flow Static Validation Result

overall_status: pass
repo_head_assumed: 2c597ec59a79c5d31adcc262b6422eee900c9ff3

## Fixture Results

### TRIG_006

- status: pass
- expected_behavior: `{"handoff_status": "ready", "scheduler_write": false, "tool_status": "not_run"}`
- observed_signals: `{"execution_claim_without_log": false, "has_pure_math_definition": true, "has_subtopics": true, "lane": "MathLane_A", "node_id": "TRIG-006", "scheduler_write": false, "subtopic_count": 4, "tool_status": "not_run", "v8_sanity_audit_present": true}`

### CALCULUS_265

- status: pass
- expected_behavior: `{"exam_handoff_allowed_after_coverage": true, "handoff_status": "ready", "scheduler_write": false, "socratic_teaching_allowed": true, "tool_status": "not_run"}`
- observed_signals: `{"exam_handoff_allowed_after_coverage": true, "fake_sympy_execution_claim_produced": false, "formal_definition_status": "present", "handoff_status": "ready", "has_common_misconceptions": true, "has_mapping_boundary": true, "has_physical_intuition": true, "has_pure_math_definition": true, "has_required_prerequisites": true, "has_subtopics": true, "lane": "MathLane_A", "mapping_boundary_status": "present", "node_id": "CALCULUS-265", "prerequisites_status": "present", "scheduler_write": false, "socratic_teaching_allowed": true, "subtopic_count": 5, "tool_status": "not_run"}`

## Tests

### static.teaching_flow_spec.required_phrases

- status: pass
- failure_reason: None

### static.coordinator.required_phrases

- status: pass
- failure_reason: None

### static.prep.required_phrases

- status: pass
- failure_reason: None

### static.socratic.required_phrases

- status: pass
- failure_reason: None

### static.exam.required_phrases

- status: pass
- failure_reason: None

### static.tool_truthfulness_states.teaching_flow_spec

- status: pass
- failure_reason: None

### static.tool_truthfulness_states.coordinator

- status: pass
- failure_reason: None

### static.tool_truthfulness_states.prep

- status: pass
- failure_reason: None

### static.tool_truthfulness_states.socratic

- status: pass
- failure_reason: None

### static.tool_truthfulness_states.exam

- status: pass
- failure_reason: None

### forbidden.affirmative_tool_execution_phrases

- status: pass
- failure_reason: None

### fixture.TRIG_006.ready_mathlane_a

- status: pass
- failure_reason: None

### fixture.CALCULUS_265.ready_mathlane_a

- status: pass
- failure_reason: None

## Forbidden Actions

- forbidden_actions_observed: []
- tool_execution_performed: False
- runtime_activation_performed: False
- coordinator_activation_performed: False
- learning_state_write_performed: False
- scheduler_write_performed: False
