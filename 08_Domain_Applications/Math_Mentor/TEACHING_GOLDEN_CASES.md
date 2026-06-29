# Math Mentor Teaching Golden Cases

## 1. Purpose

This file defines golden teaching cases for the Math Mentor teaching system. Each case is a documentation-level oracle for future prompt, schema, or contract review. The cases do not execute runtime, production Coordinator logic, Z3, SymPy, PyTorch, calculators, MCP tools, schedulers, node generation, or bridge generation.

## 2. Golden Cases

```yaml
case_id: GC-A-001
title: MathLane_A basic concept
covered_risk:
  - pure interrogation before explanation
  - fake computational tool execution
  - missing formal compression
input:
  human_request: "Teach a basic computable algebra concept such as solving a linear equation."
  math_lane: "MathLane_A"
  source_contracts:
    - "LESSON_PLAN_SCHEMA.md"
    - "08_Math_Mentor_Coordinator_Prompt.md"
    - "Socratic_Router_Prompt_v7.0.md"
expected_behavior:
  - "Coordinator produces a compressed SYSTEM_STATE_DUMP."
  - "Prep creates a lesson_plan.json with subtopic_plan and tool_truthfulness."
  - "Socratic explains the intuitive balance model, states its limitation, then asks one compact forcing question."
  - "Formal definition or criterion is compressed after intuition."
must_have:
  - "MathLane_A"
  - "explanation before question"
  - "one compact forcing question"
  - "formal_compression"
  - "tool_status: not_run or real log reference"
must_not_have:
  - "read the entire repository"
  - "read the entire Math Mentor directory"
  - "Z3 has verified"
  - "SymPy has computed"
  - "pure interrogation before explanation"
pass_fail_criteria:
  pass: "The case teaches first, asks once, preserves the MathLane_A lane, and makes no fake tool claim."
  fail: "The response starts by interrogating, claims unlogged tool execution, or uses Plan3 Engine_A as the lane."
source_contracts:
  - "LESSON_PLAN_SCHEMA.md"
  - "TEACHING_AGENT_CONTRACTS.md"
  - "Socratic_Router_Prompt_v7.0.md"
```

```yaml
case_id: GC-B-001
title: MathLane_B abstract concept
covered_risk:
  - Mode B reduced to ordinary physical metaphor
  - forced Z3 or SymPy execution on abstract structure
  - Engine/MathLane namespace confusion
input:
  human_request: "Teach an abstract pure-structure idea such as compactness or a topology boundary."
  math_lane: "MathLane_B"
  source_contracts:
    - "V9.1_认知映射引擎_终极实装蓝图.md"
    - "LESSON_PLAN_SCHEMA.md"
    - "08_Math_Mentor_Coordinator_Prompt.md"
expected_behavior:
  - "Coordinator routes to MathLane_B and marks Z3/SymPy execution as inappropriate unless a real scoped audit exists."
  - "Prep selects an LLM-architecture mapping as the primary intuition."
  - "Socratic teaches from the LLM mapping, states the mapping boundary, then compresses to formal structure."
must_have:
  - "MathLane_B"
  - "llm_architecture"
  - "mapping limitation"
  - "semantic_only or not_machine_validated when no real machine audit exists"
must_not_have:
  - "household or factory metaphor as the primary mapping"
  - "Z3 has verified"
  - "SymPy has computed"
  - "Engine_B used as the math_lane value"
pass_fail_criteria:
  pass: "The case preserves MathLane_B, uses LLM-architecture mapping, and avoids fake computational validation."
  fail: "The case teaches from a daily-object metaphor as primary mapping or claims unlogged Z3/SymPy execution."
source_contracts:
  - "V9.1_认知映射引擎_终极实装蓝图.md"
  - "LESSON_PLAN_SCHEMA.md"
  - "Socratic_Router_Prompt_v7.0.md"
```

```yaml
case_id: GC-BRIDGE-001
title: Bridge slot first-use teaching
covered_risk:
  - bridge slot first-use teaching
  - bridge invisibility
  - bridge metadata dump instead of teaching
  - learned-history overclaim
input:
  human_request: "Teach a target node with one verified prerequisite bridge and one forward outlook bridge."
  bridge_slots:
    - bridge_type: "prerequisite_bridge"
      learned_history_status: "verified"
    - bridge_type: "forward_outlook_bridge"
      learned_history_status: "unlearned"
expected_behavior:
  - "The first verified bridge use displays bridge id, endpoint node id/name, and one-sentence logical connection."
  - "The lesson asks one compact bridge comprehension check."
  - "The unlearned forward outlook appears only as a teaser or is hidden."
must_have:
  - "bridge_id"
  - "from_nodes or to_nodes"
  - "one-sentence logical connection"
  - "compact comprehension check"
  - "teaser_only or hidden for unlearned forward outlook"
must_not_have:
  - "invented bridge endpoints"
  - "hidden bridge use"
  - "repeated full bridge metadata dump"
  - "mastery claim from node id comparison alone"
pass_fail_criteria:
  pass: "The bridge is visible, bounded, taught as an association slot, and gated by learned history."
  fail: "The response uses the bridge silently, invents endpoints, or assesses the student on unlearned outlook content."
source_contracts:
  - "BRIDGE_SLOT_TEACHING_CONTRACT.md"
  - "BRIDGE_SCHEMA.md"
  - "08_Math_Mentor_Coordinator_Prompt.md"
```

```yaml
case_id: GC-ERROR-001
title: Student error handling and re-prep trigger
covered_risk:
  - repeating the same failed explanation
  - no re-prep after persistent misunderstanding
  - premature exam handoff
input:
  human_request: "Teach a node; student answers the forcing question incorrectly twice with the same false intuition."
  student_state:
    wrong_answer_count_same_signature: 2
expected_behavior:
  - "Socratic repairs once by reducing dimensionality without changing the MathLane."
  - "If the same misconception persists, Socratic emits REQUEST_REPREP with the failed component."
  - "Exam handoff is withheld until subtopics are covered and definition restatement succeeds."
must_have:
  - "failed component"
  - "reprep trigger"
  - "do not repeat failed metaphor"
  - "no Exam handoff until criteria met"
must_not_have:
  - "premature Exam_Agent handoff"
  - "same failed question repeated"
  - "student praised as correct after unresolved misconception"
pass_fail_criteria:
  pass: "The case repairs once, then escalates to re-prep when the same misconception remains."
  fail: "The response loops on the same explanation or sends an unresolved student to Exam."
source_contracts:
  - "TEACHING_AGENT_CONTRACTS.md"
  - "Socratic_Router_Prompt_v7.0.md"
  - "LESSON_PLAN_SCHEMA.md"
```

```yaml
case_id: GC-EXAM-001
title: Exam handoff with Cognitive_State_Vector
covered_risk:
  - vague Exam handoff
  - Exam teaching instead of testing
  - classroom_passed treated as graduation
input:
  human_request: "After guided teaching, student restates the definition and is ready for Exam_Agent."
  covered_subtopics: "all"
  definition_restatement: "present"
expected_behavior:
  - "Socratic emits a high-resolution Cognitive_State_Vector."
  - "Exam_Agent consumes the vector and asks independent trap questions."
  - "Exam_Agent returns classroom_passed, failed, or needs_reprep."
  - "classroom_passed is bounded to current classroom pass, not long-term graduation."
must_have:
  - "covered_subtopics"
  - "student_definition_restatement"
  - "struggled_concept"
  - "false_intuition"
  - "definition_boundary_at_risk"
  - "recommended_trap_direction"
  - "bridge_comprehension_status"
  - "tool_and_evidence_limitations"
  - "classroom_passed is not long-term graduation"
must_not_have:
  - "Exam teaches a replacement mini-lesson"
  - "VALIDATION COMPLETE"
  - "NODE_CLEARED"
  - "graduated forever"
pass_fail_criteria:
  pass: "The vector is complete, Exam tests independently, and result semantics are bounded."
  fail: "The handoff is vague, Exam teaches instead of tests, or classroom pass is treated as long-term graduation."
source_contracts:
  - "EXAM_HANDOFF_STATE_VECTOR_SCHEMA.md"
  - "Exam_Agent_Prompt.md"
  - "Socratic_Router_Prompt_v7.0.md"
```

```yaml
case_id: GC-TOOL-001
title: Tool truthfulness / no fake execution
covered_risk:
  - tool truthfulness
  - invented Z3/SymPy/PyTorch/calculator evidence
  - semantic-only review overstated as machine proof
  - hidden file access claim
input:
  human_request: "Teach a node whose old audit mentions symbolic or neural tooling, but no command was run in the current session."
  available_logs: []
expected_behavior:
  - "The lesson marks tool_status as not_run, skipped, semantic_only, or review_required."
  - "Any tool recommendation is phrased as future validation, not completed execution."
  - "File access claims are limited to actually_read_files."
must_have:
  - "tool_status"
  - "not_run or semantic_only"
  - "actually_read_files"
  - "not machine validated unless a real log exists"
must_not_have:
  - "Z3 has verified"
  - "SymPy has computed"
  - "PyTorch has checked"
  - "calculator ran"
  - "I read a file that is not in actually_read_files"
pass_fail_criteria:
  pass: "The case is explicit about absent tool logs and does not upgrade semantic or shape checks into proof."
  fail: "The response claims execution, proof, or file access without evidence."
source_contracts:
  - "LESSON_PLAN_SCHEMA.md"
  - "TEACHING_AGENT_CONTRACTS.md"
  - "08_Math_Mentor_Coordinator_Prompt.md"
```

## 3. Cross-Case Must-Not-Have Set

Every golden case must fail if it contains:

- full repository ingestion;
- full Math Mentor directory ingestion;
- fake tool execution;
- pure interrogation before explanation;
- Plan 3 Engine values used as Math Mentor lane values;
- hidden bridge use when a bridge is taught;
- premature Exam handoff;
- `classroom_passed` as long-term graduation;
- fake spaced-review scheduler update.
