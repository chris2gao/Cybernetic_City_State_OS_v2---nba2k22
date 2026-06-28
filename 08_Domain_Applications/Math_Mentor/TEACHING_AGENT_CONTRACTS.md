# Math Mentor Teaching Agent Contracts

Status: LRP-02 canonical contract draft for review.

This document defines the handoff contracts among Math Mentor teaching agents. It is a documentation layer only. It does not activate runtime, production Coordinator execution, automation, external apps, tool execution, prompt mutation, node generation, bridge generation, or learning-state writes.

## 1. Agent Boundary Model

The teaching pipeline has these conceptual agents:

1. Human / Coordinator input layer;
2. Coordinator;
3. Prep_Architect;
4. Guided_Socratic_Router;
5. Exam_Agent;
6. later learning-state / spaced-review layer.

Plan 3 `Engine_A` and `Engine_B` remain city-state authority categories. Math Mentor `MathLane_A`, `MathLane_B`, and `mixed` remain domain teaching lanes. A payload must not confuse these namespaces.

## 2. Shared Evidence Rules

Every handoff payload must carry evidence boundaries:

```json
{
  "actually_read_files": [],
  "unavailable_files": [],
  "evidence_limits": [],
  "tool_truthfulness": {
    "tool_status": "not_run",
    "available_evidence": "semantic_only",
    "log_ref": null
  }
}
```

Rules:

- Only files physically read in the current context can be listed under `actually_read_files`.
- Indexes and filenames are locators, not proof that content was read.
- No payload may imply deterministic tool execution without a real log reference.
- Full-repository ingestion and full Math Mentor ingestion are forbidden loading strategies.

## 3. Human / Coordinator Input Contract

Producer: Human, ChatGPT, or current task signal.

Consumer: Coordinator.

Purpose: define the target teaching request and authority boundary.

Required fields:

```json
{
  "request_id": "human-request-id",
  "requested_target": "natural language, node id, or exact file",
  "human_goal": "what the student wants to learn",
  "authorized_scope": "teaching | planning | review",
  "plan3_engine": "Plan3_Engine_B",
  "human_gate": "not_required | required | approved",
  "source_context": {
    "task_ref": null,
    "packet_ref": null
  }
}
```

Forbidden assumptions:

- Do not assume target-node mastery from node number.
- Do not assume all roadmaps, all nodes, or all bridges are loaded.
- Do not treat a Human learning request as authorization to modify prompts, nodes, runtime, or bridge registry.

Stop conditions:

- target cannot be resolved;
- required authority file is missing and cannot be loaded by path;
- request crosses into prompt repair, runtime activation, generation, or source publication without explicit authorization.

## 4. Coordinator-To-Prep Contract

Producer: Coordinator.

Consumer: Prep_Architect.

Purpose: provide the minimum loaded evidence needed to build `lesson_plan.json`.

Required payload:

```json
{
  "coordinator_request_id": "coord-n_xxx-001",
  "target_node": {
    "node_id": "n_xxx",
    "file": "DOMAIN-000.yaml",
    "name": "concept name",
    "definition": "compact definition",
    "sub_topics": [],
    "status": "loaded"
  },
  "routing": {
    "plan3_engine": "Plan3_Engine_B",
    "math_lane": "MathLane_A | MathLane_B | mixed",
    "routing_basis": "domain/subdomain evidence",
    "mode_b_context_status": "not_required | loaded | missing"
  },
  "adjacent_context": {
    "prerequisite_nodes": [],
    "matching_bridge_records": [],
    "learned_history_reference": {}
  },
  "evidence_trace": {
    "actually_read_files": [],
    "unavailable_files": [],
    "limits": []
  }
}
```

Coordinator obligations:

- load the smallest required context by exact path;
- record every loaded file in `actually_read_files`;
- select matching bridge records only through explicit endpoints or unambiguous legacy content;
- preserve `MathLane_A` / `MathLane_B` routing evidence;
- pass missing learned-history state as `unavailable`, not as learned.

Coordinator must not:

- load every YAML node;
- load `数学知识路线图_全部.yaml` for routine layer work;
- invent bridge endpoints;
- treat unindexed or unresolved bridge records as formal teaching content;
- claim hidden-memory access to files not listed in `actually_read_files`.

## 5. Prep-To-Socratic Contract

Producer: Prep_Architect.

Consumer: Guided_Socratic_Router.

Purpose: provide the canonical `lesson_plan.json` defined in `LESSON_PLAN_SCHEMA.md`.

Required payload:

```json
{
  "lesson_plan": "LESSON_PLAN_SCHEMA.md compliant object",
  "coverage_map": {
    "source_subtopic_count": 0,
    "planned_subtopic_count": 0,
    "coverage_status": "complete | incomplete"
  },
  "handoff_status": "ready | blocked | request_reprep"
}
```

Prep obligations:

- map every source `sub_topics` item into `subtopic_plan`;
- construct occurrence crisis before formal compression;
- choose lane-consistent intuition;
- include bridge slots only when evidence supports them;
- include re-prep triggers when mapping, evidence, or student-state conditions may fail.

Prep must not:

- skip a subtopic because it is inconvenient;
- move Exam handoff conditions into a default-passed state;
- use everyday physical intuition as primary Mode B mapping;
- convert unavailable learned history into mastery;
- add deterministic execution claims without logs.

## 6. Socratic-To-Exam Contract

Producer: Guided_Socratic_Router.

Consumer: Exam_Agent.

Purpose: hand over only after teaching coverage and definition restatement are complete.

Required payload:

```json
{
  "signal": "SYSTEM_INTERRUPT: EXAM_HANDOVER",
  "target_node": {},
  "Cognitive_State_Vector": {},
  "handoff_conditions": {
    "all_subtopics_covered": true,
    "definition_restatement_complete": true,
    "bridge_checks_complete": true
  },
  "evidence_trace": {}
}
```

Socratic obligations:

- teach and explain before forcing a question;
- cover all `subtopic_plan` entries;
- ask exactly one compact bridge comprehension check on first bridge use;
- require the student to restate the formal definition or criterion;
- record struggled concepts, false intuitions, and definition boundaries for Exam_Agent.

Socratic must not:

- interrogate before explanation;
- send Exam_Agent an incomplete subtopic state;
- treat a bridge teaser as formal prerequisite teaching;
- claim a classroom pass before Exam_Agent trap completion;
- claim long-term graduation.

## 7. Exam-To-Learning-State / Review-Scheduler Placeholder

Producer: Exam_Agent.

Consumer: future learning-state and spaced-review layer.

Purpose: record classroom pass or failure without claiming long-term graduation.

Required placeholder:

```json
{
  "target_node": {},
  "exam_result": "classroom_passed | failed | needs_reprep",
  "trap_result": {
    "trap_direction": "what was tested",
    "student_response_summary": "compact result",
    "examiner_notes": []
  },
  "learning_state_write": {
    "authorized": false,
    "placeholder_target": "数学间隔重复调度表.md",
    "status": "deferred_to_future_lrp"
  },
  "graduation_claim": "not_allowed"
}
```

Exam obligations:

- test muscle memory and a trap based on the `Cognitive_State_Vector`;
- return classroom result only;
- route classroom pass to a future spaced-review scheduler contract.

Exam must not:

- teach new content during the exam;
- claim spaced-review graduation;
- write learning-state files unless a future task explicitly authorizes it.

## 8. Failure / Re-Prep / Drift Handoff Contract

Producer: Coordinator, Prep_Architect, Socratic_Router, or Exam_Agent.

Consumer: Coordinator and Prep_Architect.

Purpose: stop unsafe teaching and rebuild the smallest failed part.

Required payload:

```json
{
  "signal": "SYSTEM_INTERRUPT: REQUEST_REPREP",
  "failure_type": "metaphor_failure | lane_mismatch | missing_mapping | evidence_missing | subtopic_failure | bridge_ambiguity | tool_claim_risk",
  "target_node": {},
  "failed_component": "occurrence_crisis | intuition_model | formal_compression | bridge_slots | subtopic_plan | exam_handoff",
  "evidence": {
    "actually_read_files": [],
    "unsupported_reference": null,
    "student_feedback_summary": null
  },
  "required_repair": "specific local repair request"
}
```

Re-prep obligations:

- continue only after the failed evidence, lane, or mapping issue is corrected;
- keep the same target unless Human changes the objective;
- reload only the smallest missing authority file or target evidence;
- preserve already valid subtopic coverage evidence when safe.

Stop instead of re-prep when:

- fixing the problem requires prompt mutation;
- fixing the problem requires node or bridge generation;
- fixing the problem requires runtime activation;
- fixing the problem requires source or master publication;
- secrets, privacy, or destructive operations would be involved.

## 9. Contract Validation Checklist

- [ ] Human/Coordinator request has target, scope, and authority state.
- [ ] Coordinator-to-Prep includes target node, routing, adjacent context, and evidence trace.
- [ ] Prep-to-Socratic produces a schema-compliant `lesson_plan.json`.
- [ ] Socratic-to-Exam includes a high-resolution `Cognitive_State_Vector`.
- [ ] Exam-to-learning-state placeholder does not claim long-term graduation.
- [ ] Failure/re-prep payload includes failure type, evidence, and repair request.
- [ ] Every handoff preserves `actually_read_files`.
- [ ] Tool truthfulness is explicit and does not imply unlogged execution.
- [ ] No handoff requires full-repository or full Math Mentor ingestion.
- [ ] No handoff activates runtime, Coordinator, external apps, prompt repair, node generation, bridge generation, or learning-state writes.
