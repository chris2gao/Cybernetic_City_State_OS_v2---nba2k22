# Exam Handoff State Vector Schema

Status: LRP-02 canonical contract draft for review.

This document defines the high-resolution `Cognitive_State_Vector` sent from `Guided_Socratic_Router` to `Exam_Agent`. It is a documentation contract only. It does not activate Exam_Agent runtime, prompt mutation, learning-state writes, spaced-review writes, bridge generation, node generation, or deterministic tool execution.

## 1. Purpose

Exam_Agent needs a precise state vector, not a loose summary. The vector tells the examiner what the student has learned, where the student's false intuition is likely to break, what definition boundary is at risk, and which trap direction should be used.

Exam_Agent may decide classroom pass or failure for the current lesson. It cannot claim long-term graduation. Long-term graduation depends on later spaced-review validation.

## 2. Handoff Envelope

```json
{
  "signal": "SYSTEM_INTERRUPT: EXAM_HANDOVER",
  "schema_version": "1.0",
  "target_node": {},
  "Cognitive_State_Vector": {},
  "exam_constraints": {},
  "evidence_trace": {}
}
```

The signal may be emitted only after all subtopics are covered and the student has restated the formal definition or criterion.

## 3. `target_node`

```json
{
  "node_id": "n_xxx",
  "file": "DOMAIN-000.yaml",
  "name": "concept name",
  "math_lane": "MathLane_A | MathLane_B | mixed",
  "routing_basis": "domain/subdomain evidence",
  "definition": "formal definition or criterion"
}
```

Rules:

- `math_lane` uses Math Mentor lane names, not Plan 3 engine names.
- `definition` must be the version the student was asked to restate.

## 4. `Cognitive_State_Vector`

Canonical fields:

```json
{
  "covered_subtopics": [],
  "student_definition_restatement": {},
  "struggled_concept": {},
  "false_intuition": {},
  "definition_boundary_at_risk": {},
  "recommended_trap_direction": {},
  "subtopic_coverage_evidence": {},
  "bridge_comprehension_status": {},
  "tool_and_evidence_limitations": {},
  "unresolved_prerequisites": [],
  "exam_pass_fail_criteria": {}
}
```

### 4.1 `covered_subtopics`

Each item:

```json
{
  "subtopic_id": "s1",
  "name": "subtopic name",
  "role": "core | auxiliary",
  "teaching_status": "explained_and_checked | confirmed | failed",
  "student_response_summary": "compact evidence"
}
```

Rules:

- Every `lesson_plan.subtopic_plan` item must appear.
- Any `failed` or missing item blocks Exam handoff.

### 4.2 `student_definition_restatement`

```json
{
  "required": true,
  "status": "complete | incomplete | missing",
  "student_words_summary": "student's restatement in compact form",
  "definition_match": "accurate | partial | incorrect",
  "missing_boundaries": []
}
```

`status: complete` and `definition_match: accurate` are required for normal Exam handoff.

### 4.3 `struggled_concept`

```json
{
  "concept": "what the student struggled with",
  "evidence": "specific answer or hesitation",
  "severity": "low | medium | high",
  "related_subtopics": []
}
```

This gives Exam_Agent the likely pressure point for the trap.

### 4.4 `false_intuition`

```json
{
  "intuition": "student's misleading mental model",
  "source": "answer | question | silence | repeated error",
  "why_false": "where it breaks",
  "correction_attempted": true
}
```

The trap should distinguish corrected understanding from memorized wording.

### 4.5 `definition_boundary_at_risk`

```json
{
  "boundary": "condition or exception likely to be missed",
  "risk_type": "overgeneralization | missing_condition | wrong_direction | edge_case",
  "counterexample_seed": "compact seed for Exam_Agent"
}
```

Examples include missing quantifier order, confusing sufficient and necessary conditions, or treating a local intuition as global.

### 4.6 `recommended_trap_direction`

```json
{
  "trap_goal": "what the trap should reveal",
  "trap_type": "concept_boundary | computation_edge | proof_gap | geometric_misread | probability_condition_shift | mode_mapping_confusion",
  "prompt_seed": "short examiner seed",
  "must_not_teach": true
}
```

Exam_Agent may adapt the trap but must not teach new content as part of the exam.

### 4.7 `subtopic_coverage_evidence`

```json
{
  "all_subtopics_covered": true,
  "coverage_count": 0,
  "source_count": 0,
  "uncovered_subtopics": [],
  "coverage_limits": []
}
```

`coverage_count` must equal `source_count` for normal handoff.

### 4.8 `bridge_comprehension_status`

```json
{
  "bridge_slots_used": [],
  "first_use_display_completed": true,
  "comprehension_checks": [],
  "unresolved_or_teaser_bridges": [],
  "limits": []
}
```

Each bridge comprehension check must be compact and tied to the current target lesson. Teaser-only or unresolved bridge records cannot become exam prerequisites.

### 4.9 `tool_and_evidence_limitations`

```json
{
  "tool_status": "not_run",
  "available_evidence": "semantic_only",
  "log_ref": null,
  "unsupported_claims": [],
  "actually_read_files": []
}
```

Allowed `tool_status` values:

- `not_run`;
- `run_with_log`;
- `unavailable`;
- `semantic_only`.

The state vector records what evidence exists. It does not convert semantic-only evidence into deterministic execution.

### 4.10 `unresolved_prerequisites`

Each item:

```json
{
  "node_id": "n_xxx",
  "reason": "missing | unlearned | learned_history_unavailable | ambiguous_bridge",
  "impact": "blocks_exam | teaser_only | does_not_block"
}
```

Any `blocks_exam` item prevents handoff.

### 4.11 `exam_pass_fail_criteria`

```json
{
  "classroom_pass_requires": [
    "correct muscle-memory check",
    "trap boundary recognized",
    "no reliance on false intuition"
  ],
  "failure_routes": [
    "request_reprep",
    "return_to_subtopic",
    "clarify_definition_boundary"
  ],
  "graduation_claim_allowed": false
}
```

`graduation_claim_allowed` must remain `false` for this handoff. Classroom pass can later be scheduled for review.

## 5. Valid Handoff Conditions

Exam handoff is valid only when:

- every subtopic is covered;
- the student restates the formal definition or criterion;
- bridge comprehension checks are complete for formal bridge slots;
- unresolved prerequisites do not block the current target;
- evidence limitations are explicit;
- no tool execution is implied without a log;
- the state vector recommends a concrete trap direction.

## 6. Invalid Handoff Conditions

Invalid:

- missing `Cognitive_State_Vector`;
- covered-subtopic count differs from source count;
- definition restatement is missing;
- bridge slots are used without first-use display evidence;
- false intuition is not described after repeated student errors;
- `recommended_trap_direction` is generic or empty;
- classroom pass is described as long-term graduation;
- deterministic evidence is implied without log reference.

## 7. Review-Scheduler Boundary

If Exam_Agent records `classroom_passed`, the next authorized layer may place the node into `数学间隔重复调度表.md`. LRP-02 only defines the placeholder contract. It does not write the scheduler and does not define long-term graduation rules.
