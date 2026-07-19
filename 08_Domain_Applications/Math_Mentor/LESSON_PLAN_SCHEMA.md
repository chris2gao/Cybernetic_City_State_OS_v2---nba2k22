# Math Mentor Lesson Plan Schema

Status: LRP-02 canonical contract draft for review.

This document defines the canonical `lesson_plan.json` payload produced by `Prep_Architect` and consumed by `Guided_Socratic_Router`. It is a documentation contract only. It does not activate runtime, production Coordinator execution, external apps, tool execution, node generation, bridge generation, or prompt mutation.

## 1. Purpose And Authority

`lesson_plan.json` is the shared state object that keeps one Math Mentor teaching session aligned across:

- the Human-authorized Math Mentor request;
- Coordinator lazy loading and routing;
- Prep_Architect lesson construction;
- Guided_Socratic_Router teaching;
- Exam_Agent handoff;
- later learning-state and spaced-review layers.

It preserves these invariants:

- teach before interrogation;
- intuition before formal definition;
- full `sub_topics` coverage before Exam handoff;
- bridge slots are visible first-class association objects;
- no bridge, learned-history, tool, or file-access claim is made without evidence;
- classroom pass after Exam_Agent is not long-term graduation;
- Plan 3 `Engine_A` / `Engine_B` is distinct from Math Mentor `MathLane_A` / `MathLane_B`.

## 2. Namespace Rule

Use these names inside `lesson_plan.json`:

- `Plan3_Engine_A`: city-state implementation and deterministic execution route.
- `Plan3_Engine_B`: city-state Human-led semantic review and teaching route.
- `MathLane_A`: Math Mentor computable algebra lane.
- `MathLane_B`: Math Mentor pure structure lane.
- `mixed`: a reviewed transition between `MathLane_A` and `MathLane_B`.

Do not use Plan 3 engine names as Math Mentor lane values.

## 3. Canonical Top-Level Fields

The canonical payload contains these required top-level fields:

```json
{
  "schema_version": "1.0",
  "lesson_plan_id": "lesson-n_xxx-YYYYMMDD",
  "target_node": {},
  "math_lane": "MathLane_A",
  "routing_basis": {},
  "student_state": {},
  "subtopic_plan": [],
  "occurrence_crisis": {},
  "intuition_model": {},
  "formal_compression": {},
  "bridge_slots": [],
  "learned_history_reference": {},
  "exam_handoff_conditions": {},
  "reprep_triggers": {},
  "evidence_trace": {},
  "tool_truthfulness": {}
}
```

The field names above are stable for LRP-03 prompt alignment and LRP-04 golden tests.

## 4. Field Definitions

### 4.1 `target_node`

```json
{
  "node_id": "n_xxx",
  "file": "DOMAIN-000.yaml",
  "name": "concept name",
  "definition": "compact formal definition or criterion",
  "sub_topics_source": "target YAML path",
  "status": "loaded"
}
```

Rules:

- `node_id` must be the global roadmap identity when known.
- `file` must be an exact path or basename actually read.
- `definition` is used for formal compression, not dumped before intuition.
- `status` is `loaded`, `missing`, or `unresolved`.

### 4.2 `math_lane`

Allowed values:

- `MathLane_A`: computable algebra lane; use low-friction everyday physical intuition.
- `MathLane_B`: pure structure lane; use LLM architecture mapping as the primary mapping.
- `mixed`: reviewed A/B transition; cannot be a fallback for uncertainty.

### 4.3 `routing_basis`

```json
{
  "plan3_engine": "Plan3_Engine_B",
  "math_lane_reason": "domain/subdomain evidence, not level number alone",
  "domain_evidence": "route from Coordinator/domain protocol",
  "mode_b_required_files": [],
  "limits": "what was not loaded or verified"
}
```

Rules:

- Math Mentor teaching remains a Plan 3 `Engine_B` domain task.
- Deterministic tools may support evidence, but do not replace teaching judgment.
- `math_lane_reason` must not depend only on node number.

### 4.4 `student_state`

```json
{
  "known_nodes": [],
  "blocked_prerequisites": [],
  "misconceptions": [],
  "learned_history_state": "loaded",
  "frustration_index": 0,
  "definition_restatement_status": "not_requested"
}
```

Allowed `learned_history_state` values:

- `loaded`;
- `unavailable`;
- `not_needed`.

Node-ID ordering alone cannot imply mastery.

### 4.5 `subtopic_plan`

Each item:

```json
{
  "subtopic_id": "s1",
  "name": "subtopic name",
  "role": "core",
  "source": "target_node.sub_topics[0]",
  "explanation_goal": "what must be explained",
  "forcing_question": "one question after explanation",
  "completion_check": "observable student response",
  "status": "pending"
}
```

Rules:

- Every source `sub_topics` item must appear exactly once.
- Core subtopics require explanation plus a forcing question.
- Auxiliary subtopics may use a shorter confirmation question.
- Phase 2 cannot close while any item is `pending` or `failed`.

### 4.6 `occurrence_crisis`

```json
{
  "old_tool_failure": "what previous concept cannot handle",
  "why_this_concept_must_exist": "mathematical pressure forcing the new concept",
  "student_facing_summary": "compact explanation"
}
```

This field creates the need for the concept before symbols are compressed into formal definition.

### 4.7 `intuition_model`

```json
{
  "kind": "everyday_physical",
  "content": "primary intuition model",
  "limitation": "where the analogy stops",
  "lane_consistency": "matches MathLane_A"
}
```

Allowed `kind` values:

- `everyday_physical` for `MathLane_A`;
- `llm_architecture` for `MathLane_B`;
- `mixed_transition` for reviewed lane transitions.

Mode B canonical teaching must not use ordinary household, factory, fluid, or object metaphors as the primary mapping. If a required Mode B mapping is missing, the lesson plan must trigger re-prep instead of silently teaching from an invalid mapping.

### 4.8 `formal_compression`

```json
{
  "definition": "formal definition after intuition",
  "boundary_conditions": [],
  "common_counterexamples": [],
  "symbol_introduction_order": []
}
```

Formal compression follows occurrence crisis and intuition. It does not precede them.

### 4.9 `bridge_slots`

Each item:

```json
{
  "slot_id": "bridge-slot-1",
  "bridge_id": "BRIDGE-015",
  "title": "bridge title",
  "bridge_type": "intra_layer",
  "from_nodes": [],
  "to_nodes": [],
  "learned_status": "verified",
  "teaching_status": "formal_teaching_content",
  "one_sentence_connection": "logical connection",
  "first_use_display_required": true,
  "comprehension_check": "one compact question",
  "evidence": {}
}
```

Bridge slots follow `BRIDGE_SLOT_TEACHING_CONTRACT.md`.

### 4.10 `learned_history_reference`

```json
{
  "source": "persisted_state",
  "read_status": "loaded",
  "required_nodes": [],
  "evidence_priority": [
    "classroom_passed_after_exam_agent",
    "spaced_review_state",
    "registered_learned_state",
    "strict_sequential_fallback"
  ],
  "node_id_comparison_implies_mastery": false,
  "limits": "unavailable state, stale evidence, or strict course assumptions"
}
```

If learned history is unavailable, bridge-dependent formal content must become `teaser_only`, `hidden`, or `blocked` according to the bridge contract.

### 4.11 `exam_handoff_conditions`

```json
{
  "all_subtopics_covered": false,
  "definition_restatement_required": true,
  "definition_restatement_status": "not_requested",
  "bridge_checks_complete": false,
  "trap_direction": "pending",
  "handoff_allowed": false
}
```

Exam handoff is allowed only after every subtopic is covered and the student restates the formal definition or criterion in their own words.

### 4.12 `reprep_triggers`

```json
{
  "metaphor_failure": "student destroys or cannot use the intuition model",
  "student_frustration_threshold": 3,
  "missing_mapping_status": "request_mode_b_mapping",
  "missing_evidence_status": "reload_or_block",
  "drift_status": "reload_smallest_missing_authority_file"
}
```

Re-prep asks Coordinator and Prep_Architect to regenerate or repair the lesson plan. It does not authorize runtime activation by itself.

### 4.13 `evidence_trace`

```json
{
  "actually_read_files": [],
  "unavailable_files": [],
  "node_files_read": [],
  "bridge_files_read": [],
  "learned_history_files_read": [],
  "limits": []
}
```

Only files physically read in the current teaching context may appear in `actually_read_files`.

### 4.14 `tool_truthfulness`

```json
{
  "tool_status": "not_run",
  "available_evidence": "semantic_only",
  "required_before_execution_claim": "command log or report reference",
  "limits": "No deterministic execution is implied by this lesson plan."
}
```

Allowed `tool_status` values:

- `not_run`;
- `run_with_log`;
- `unavailable`;
- `semantic_only`.

The plan may say a claim is suitable for deterministic validation, or that a command log is required before an execution claim. It must not report tool execution unless a real log is attached.

## 5. Optional Fields

Optional fields are allowed only when they are consumed by a named downstream contract:

- `next_node_outlook`;
- `student_language_level`;
- `session_constraints`;
- `human_notes`;
- `review_scheduler_placeholder`;
- `restatement_rubric`: an array of required elements that the student's definition restatement must contain; consumed by the Socratic-to-Exam restatement acceptance check.

Unknown top-level fields should fail validation unless a later schema version explicitly adds them.

## 6. Compact Valid Example

```json
{
  "schema_version": "1.0",
  "lesson_plan_id": "lesson-n_418-20260627",
  "target_node": {
    "node_id": "n_418",
    "file": "COMPLEX_ANALYSIS-418.yaml",
    "name": "Euler formula and complex exponential",
    "definition": "e^(i theta) = cos(theta) + i sin(theta)",
    "sub_topics_source": "COMPLEX_ANALYSIS-418.yaml",
    "status": "loaded"
  },
  "math_lane": "MathLane_A",
  "routing_basis": {
    "plan3_engine": "Plan3_Engine_B",
    "math_lane_reason": "computable complex-plane representation",
    "domain_evidence": "complex-analysis calculation branch",
    "mode_b_required_files": [],
    "limits": "example only"
  },
  "student_state": {
    "known_nodes": [],
    "blocked_prerequisites": [],
    "misconceptions": [],
    "learned_history_state": "unavailable",
    "frustration_index": 0,
    "definition_restatement_status": "not_requested"
  },
  "subtopic_plan": [
    {
      "subtopic_id": "s1",
      "name": "complex exponential as rotation",
      "role": "core",
      "source": "target_node.sub_topics[0]",
      "explanation_goal": "connect exponentials to rotation on the complex plane",
      "forcing_question": "Which part of e^(i theta) tells you the point has rotated?",
      "completion_check": "student identifies sine and cosine as coordinates",
      "status": "pending"
    }
  ],
  "occurrence_crisis": {
    "old_tool_failure": "real exponentials alone cannot encode circular motion",
    "why_this_concept_must_exist": "oscillation needs algebraic packaging",
    "student_facing_summary": "we need one symbol that carries rotation and coordinates together"
  },
  "intuition_model": {
    "kind": "everyday_physical",
    "content": "a point moving around a wheel while its shadow gives coordinates",
    "limitation": "the wheel image does not replace the formal power-series identity",
    "lane_consistency": "matches MathLane_A"
  },
  "formal_compression": {
    "definition": "e^(i theta) = cos(theta) + i sin(theta)",
    "boundary_conditions": ["theta is real in this introductory form"],
    "common_counterexamples": [],
    "symbol_introduction_order": ["e", "i", "theta", "cos", "sin"]
  },
  "bridge_slots": [],
  "learned_history_reference": {
    "source": "unavailable",
    "read_status": "unavailable",
    "required_nodes": [],
    "evidence_priority": [
      "classroom_passed_after_exam_agent",
      "spaced_review_state",
      "registered_learned_state",
      "strict_sequential_fallback"
    ],
    "node_id_comparison_implies_mastery": false,
    "limits": "no learned-history file loaded in this example"
  },
  "exam_handoff_conditions": {
    "all_subtopics_covered": false,
    "definition_restatement_required": true,
    "definition_restatement_status": "not_requested",
    "bridge_checks_complete": true,
    "trap_direction": "separate rotation frequency from coordinate values",
    "handoff_allowed": false
  },
  "reprep_triggers": {
    "metaphor_failure": "replace wheel model with smaller coordinate walk",
    "student_frustration_threshold": 3,
    "missing_mapping_status": "not_applicable",
    "missing_evidence_status": "reload_or_block",
    "drift_status": "reload_smallest_missing_authority_file"
  },
  "evidence_trace": {
    "actually_read_files": ["COMPLEX_ANALYSIS-418.yaml"],
    "unavailable_files": [],
    "node_files_read": ["COMPLEX_ANALYSIS-418.yaml"],
    "bridge_files_read": [],
    "learned_history_files_read": [],
    "limits": ["example only"]
  },
  "tool_truthfulness": {
    "tool_status": "not_run",
    "available_evidence": "semantic_only",
    "required_before_execution_claim": "command log or report reference",
    "limits": "No deterministic execution is implied by this lesson plan."
  }
}
```

## 7. Invalid Examples

### 7.1 Missing Subtopic Coverage

Invalid when `target_node.sub_topics` has three entries but `subtopic_plan` has only two entries. Socratic_Router cannot prove full coverage before Exam handoff.

### 7.2 Wrong Lane Mapping

Invalid when `math_lane` is `MathLane_B` but `intuition_model.kind` is `everyday_physical`. Pure structure teaching requires an LLM-architecture primary mapping unless a reviewed `mixed_transition` is declared.

### 7.3 Bridge Endpoint Invention

Invalid when a legacy bridge is included with guessed endpoints. Ambiguous legacy records must be omitted and flagged for migration.

### 7.4 Premature Exam Handoff

Invalid when `handoff_allowed` is `true` while any subtopic is not covered or the student's definition restatement is missing.

## 8. Validation Checklist

- [ ] All canonical top-level fields exist.
- [ ] No unknown top-level field exists under schema version `1.0`.
- [ ] `math_lane` is `MathLane_A`, `MathLane_B`, or `mixed`.
- [ ] Plan 3 engine fields are not used as Math Mentor lane values.
- [ ] Every target `sub_topics` item is represented in `subtopic_plan`.
- [ ] `occurrence_crisis` precedes formal compression in the planned teaching order.
- [ ] `intuition_model.kind` matches the lane.
- [ ] `bridge_slots` follow `BRIDGE_SLOT_TEACHING_CONTRACT.md`.
- [ ] Learned-history evidence does not rely on node-ID ordering as mastery proof.
- [ ] Exam handoff requires all subtopics and definition restatement.
- [ ] Re-prep triggers are explicit.
- [ ] `actually_read_files` contains only files read in the current context.
- [ ] `tool_truthfulness.tool_status` is honest and does not imply unlogged execution.
- [ ] If `restatement_rubric` is declared, the definition restatement is accepted only after checking every rubric element against the student's restatement, item by item.
- [ ] wrapper 层含 `coverage_map`（不在 schema 顶层）——见 `TEACHING_AGENT_CONTRACTS.md` §5。
