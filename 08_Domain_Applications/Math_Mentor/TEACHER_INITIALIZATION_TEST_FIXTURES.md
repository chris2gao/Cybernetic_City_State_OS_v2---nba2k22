# Math Mentor Teacher Initialization Test Fixtures

## 1. Purpose

These fixtures make LRP-01 teacher initialization and context-loading behavior auditable. They are reusable documentation fixtures, not runtime activation, production Coordinator execution, node generation, bridge generation, learning-state writes, or scheduler writes.

Each fixture includes input condition, expected loading order, expected `actually_read_files`, expected output/state, and must_not_have.

## 2. Fixtures

### INIT-FIXTURE-01: Empty Context To Teacher Initialization

input_condition:

- A new model window has no trusted current Math Mentor context.
- Human asks the model to initialize as Math Mentor teacher.

expected_loading_order:

1. Read `06_Silicon_Index/AI_Bootstrap_Sequence.md`.
2. Read `06_Silicon_Index/06_Cybernetic_Citizen_Awakening.md` when needed for AI operating contract.
3. Read `08_Domain_Applications/Math_Mentor/08_Math_Mentor_Coordinator_Prompt.md`.
4. Read `08_Domain_Applications/Math_Mentor/V9.1_认知映射引擎_终极实装蓝图.md` if not already in current context.
5. Record physically read files.

expected_actually_read_files:

- Includes each repository path physically read.
- Does not include the full repository.
- Does not include the full Math Mentor directory.

expected_output_state:

- `teacher_initialized: true`
- `city_state_engine: Plan3_Engine_B`
- `math_lane: unresolved_until_target_node`
- `runtime_activation: false`
- `production_coordinator_activation: false`

must_not_have:

- full repository ingestion;
- full Math Mentor ingestion;
- hidden memory claim;
- runtime activation;
- production Coordinator activation.

### INIT-FIXTURE-02: Target Node Request To SYSTEM_STATE_DUMP

input_condition:

- Teacher is initialized.
- Human requests a specific target node lesson.
- Target node path is available or can be resolved from exact routing evidence.

expected_loading_order:

1. Read target node YAML or exact target evidence.
2. Read immediate prerequisite nodes only as needed.
3. Read matching bridge records only when explicit endpoint fields or unambiguous legacy content match target/prerequisite.
4. Read learned-history or spaced-review state only when available and authorized.
5. Produce one compressed `[SYSTEM_STATE_DUMP]`.

expected_actually_read_files:

- Includes target node evidence.
- Includes only matching prerequisite and bridge files.
- Includes no full node database scan.

expected_output_state:

- `Target_Node`
- `Math_Lane`
- `Routing_Basis`
- `Sub_Topics`
- `Bridge_Slots`
- `Next_Node_Outlook`
- `Mapping_Status`
- `lesson_plan_contract`
- `tool_truthfulness`
- `actually_read_files`

must_not_have:

- full YAML dump;
- invented bridge endpoints;
- learned-history mastery claim from node id order alone;
- repeated bridge metadata dumps.

### INIT-FIXTURE-03: Manual Absent From Current Context But Present In Repository

input_condition:

- Coordinator prompt says the operational manual is required.
- The manual text is not present in current context.
- Repository path exists and can be read.

expected_loading_order:

1. Check current context.
2. Read `08_Domain_Applications/Math_Mentor/V9.1_认知映射引擎_终极实装蓝图.md` from repository path.
3. Record that path in `actually_read_files`.
4. Continue initialization.

expected_actually_read_files:

- Includes the operational manual path.
- Does not claim the manual was already known.

expected_output_state:

- `manual_loading_status: loaded_from_repository`
- `teacher_initialized: true`

must_not_have:

- refusal solely because current context lacked the manual;
- invented manual content;
- request for the Human to paste the manual when repository read succeeds.

### INIT-FIXTURE-04: Manual Absent From Repository

input_condition:

- Required operational manual is absent from current context.
- Repository read of the exact path fails.

expected_loading_order:

1. Attempt only the exact required path.
2. Stop with a missing-path error.
3. Do not substitute unrelated files.

expected_actually_read_files:

- Lists files successfully read before the failure.
- Does not list the missing manual as read.

expected_output_state:

- `status: blocked_missing_required_manual`
- exact missing repository path.

must_not_have:

- invented manual content;
- runtime activation as workaround;
- broad repository search as a substitute for the exact path unless a later Human task authorizes recovery.

### INIT-FIXTURE-05: Learned-History Unavailable

input_condition:

- Target node and bridge candidates exist.
- Persisted learned-history or spaced-review state is missing or unauthorized.

expected_loading_order:

1. Read target and matching bridge evidence.
2. Attempt to locate learned-history state only through authorized paths.
3. Mark learned-history evidence unavailable if not found.

expected_actually_read_files:

- Includes target and bridge evidence actually read.
- Includes no fake learning-state path.

expected_output_state:

- `learned_history_status: unavailable`
- prerequisite bridges with unverifiable history use `teaser_only`, `hidden`, or `unavailable`.
- no classroom pass or mastery claim.

must_not_have:

- mastery inferred only from lower node id;
- classroom pass claim without Exam_Agent evidence;
- scheduler update claim.

### INIT-FIXTURE-06: Context Drift To Smallest Reload

input_condition:

- Teacher detects stale target, stale MathLane, mismatched bridge endpoint, or file claim outside `actually_read_files`.

expected_loading_order:

1. Identify the smallest stale authority/context area.
2. Reload only the needed prompt, schema, target, bridge, or history evidence.
3. Replace stale claims in the state dump.

expected_actually_read_files:

- Adds newly read paths.
- Keeps prior paths only if still relevant and trustworthy.

expected_output_state:

- `drift_status: recovered_by_smallest_reload`
- updated `actually_read_files`
- corrected state dump.

must_not_have:

- full repository reload;
- stale bridge claim;
- stale tool execution claim.

### INIT-FIXTURE-07: Irreversible Drift To New-Window Reset

input_condition:

- Teacher mixes Plan 3 Engine and MathLane authority, references files not in `actually_read_files`, or cannot repair corrupted context with a bounded reload.

expected_loading_order:

1. Stop current teaching attempt.
2. Emit reset requirement.
3. In a new window, restart from AI bootstrap and Math Mentor payload.

expected_actually_read_files:

- Current window records the evidence that became untrustworthy.
- New window starts a fresh list after re-bootstrap.

expected_output_state:

- `status: reset_required`
- `reason: irreversible_context_drift`
- `next_action: new_window_bootstrap`

must_not_have:

- continuing with mixed authority state;
- invented bridge or tool evidence;
- silent correction without telling the student/operator.
