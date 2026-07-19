# Math Mentor E2E Teaching Session Simulation

## 1. Boundary Statement

This is a compact documented simulation. It is not runtime execution, not production Coordinator activation, not tool execution, not Z3/SymPy/PyTorch/calculator execution, not MCP/app execution, not node generation, not bridge generation, not a learning-state write, and not a spaced-review scheduler write.

The teaching content is invented for regression testing and does not require reading or generating real node YAML.

## 2. Simulated Session

### Step 1: Human Request

Human:

> Teach me a simple MathLane_A idea: why a linear equation solution is the point where two sides balance.

Expected system boundary:

- Use Math Mentor as a Plan3_Engine_B teaching domain task.
- Do not treat MathLane_A as Plan3_Engine_A.
- Do not claim any tool execution.

### Step 2: Coordinator State Dump

Coordinator emits one compressed state dump:

```json
{
  "Target_Node": {
    "node_id": "sim_n_linear_equation",
    "title": "Linear equation as balance condition",
    "source": "simulation_fixture_not_real_node_yaml"
  },
  "Math_Lane": "MathLane_A",
  "Routing_Basis": "computable algebra teaching lane; no production runtime activation",
  "Sub_Topics": [
    "meaning of equality",
    "operation preserving equality",
    "solution as value satisfying both sides"
  ],
  "Bridge_Slots": [
    {
      "bridge_id": "sim_bridge_balance_to_function_zero",
      "display_status": "teaser_only",
      "connection": "A balance equation can later be reframed as finding zero of a function."
    }
  ],
  "Next_Node_Outlook": "Solving equations as root finding, teaser only.",
  "tool_truthfulness": "not_run",
  "Mapping_Status": "mode_a_physical_primary",
  "actually_read_files": [
    "simulation_fixture_not_real_node_yaml"
  ]
}
```

Acceptance checks:

- The dump is compressed.
- It does not dump full YAML.
- Bridge slot is visible.
- `tool_status` is honest.

### Step 3: Prep lesson_plan

Prep creates a simulated `lesson_plan.json`:

```json
{
  "lesson_plan_id": "lesson-sim-linear-equation",
  "target_node": {
    "node_id": "sim_n_linear_equation",
    "title": "Linear equation as balance condition"
  },
  "math_lane": "MathLane_A",
  "routing_basis": "computable algebra teaching lane",
  "student_state": {
    "learned_history_status": "unavailable",
    "mastery_claim": "not_claimed"
  },
  "subtopic_plan": [
    {
      "subtopic_id": "eq_meaning",
      "teaching_goal": "Equality means both expressions name the same value.",
      "status": "pending"
    },
    {
      "subtopic_id": "preserve_equality",
      "teaching_goal": "Applying the same reversible operation to both sides preserves equality.",
      "status": "pending"
    },
    {
      "subtopic_id": "solution_check",
      "teaching_goal": "A solution is a value that makes the statement true.",
      "status": "pending"
    }
  ],
  "occurrence_crisis": "Blindly moving symbols hides that each move must preserve equality.",
  "intuition_model": {
    "kind": "everyday_physical",
    "content": "A balance scale remains balanced only when the same allowed change is applied to both pans.",
    "limitation": "A scale picture does not replace the algebraic rule; it only explains why symmetric operations are safe."
  },
  "formal_compression": "x is a solution of f(x)=g(x) exactly when substituting x makes f(x) and g(x) equal.",
  "bridge_slots": [
    {
      "bridge_id": "sim_bridge_balance_to_function_zero",
      "teaching_use": "teaser_only",
      "connection": "Later, f(x)=g(x) can be rewritten as f(x)-g(x)=0."
    }
  ],
  "exam_handoff_conditions": {
    "all_subtopics_covered": false,
    "definition_restatement_required": true
  },
  "tool_truthfulness": {
    "tool_status": "not_run",
    "machine_validation_claim": "none"
  }
}
```

### Step 4: Guided Socratic Teaching

Socratic teaches first:

> Think of equality as a balance condition. If both sides are equal, doing the same reversible operation to each side keeps the equality true. That is why subtracting the same number from both sides is allowed. The formal version is: a value is a solution exactly when substituting it makes the equation true.

Then Socratic asks one compact forcing question:

> If 2x+3=7, why is subtracting 3 from both sides allowed, and what must be checked at the end?

Acceptance checks:

- Explanation precedes question.
- Exactly one compact forcing question is asked at this step.
- No fake calculator/SymPy/Z3 claim appears.

### Step 5: Student Wrong Once

Student:

> I subtract 3 only from the left because that is where the 3 is.

Detected misconception:

- The student treats algebraic transformation as local symbol deletion instead of equality-preserving operation.

### Step 6: Repair

Socratic repairs without changing lane:

> If you remove weight from only one pan, the scale tilts. Algebraically, subtracting 3 only from the left changes the truth condition. You subtract 3 from both sides because the equality relation is what must be preserved.

Repair forcing question:

> What equality-preserving operation turns 2x+3=7 into 2x=4?

Expected student answer:

> Subtract 3 from both sides.

### Step 7: Student Definition Restatement

Student:

> A solution is a value that makes the original equation true, and each algebra step must preserve equality so the solution set stays the same.

Socratic marks:

- all simulated subtopics covered;
- false intuition repaired for this classroom attempt;
- definition restatement present.

### Step 8: Exam Handoff With Cognitive_State_Vector

Socratic emits:

```json
{
  "handoff_to": "Exam_Agent",
  "Cognitive_State_Vector": {
    "covered_subtopics": [
      "eq_meaning: covered",
      "preserve_equality: covered_after_repair",
      "solution_check: covered"
    ],
    "student_definition_restatement": "A solution makes the original equation true; steps must preserve equality.",
    "struggled_concept": "operation must be applied to both sides",
    "false_intuition": "local symbol deletion",
    "definition_boundary_at_risk": "confusing expression simplification with equation-preserving transformation",
    "recommended_trap_direction": "ask about applying an operation to only one side",
    "subtopic_coverage_evidence": "3/3 simulated subtopics covered",
    "bridge_comprehension_status": "teaser acknowledged; not assessed as required knowledge",
    "tool_and_evidence_limitations": "simulation only; tool_status not_run; no real node YAML",
    "unresolved_prerequisites": [],
    "exam_pass_fail_criteria": "student must reject one-sided operation and verify in original equation"
  }
}
```

### Step 9: Exam Trap

Exam_Agent does not teach a replacement mini-lesson. It asks:

> A student solves 2x+3=7 by changing only the left side to 2x=7. Is this valid? If not, give the corrected first step and explain the check.

Expected correct answer:

> It is not valid because it changes only one side. The corrected first step is subtract 3 from both sides, giving 2x=4, then x=2. Check in the original equation: 2*2+3=7.

### Step 10: Classroom Result

Exam_Agent returns:

```json
{
  "result": "classroom_passed",
  "reason": "Student rejected one-sided operation, gave corrected step, and checked in original equation.",
  "long_term_graduation": false
}
```

Boundary:

- `classroom_passed` means the current classroom trap was passed.
- It is not long-term graduation.
- Long-term graduation requires later spaced-review validation.

### Step 11: Spaced-Review Placeholder / Missing Scheduler Warning

Because this simulation is not authorized to write learning-state or scheduler files, it emits:

```json
{
  "review_scheduler_status": "placeholder_not_written",
  "warning": "Spaced-review scheduler write is unavailable or unauthorized in this simulation. Do not pretend that 数学间隔重复调度表.md was updated.",
  "next_authorized_action": "Human or later scheduler task may enqueue this node after real classroom pass evidence."
}
```

Acceptance checks:

- No scheduler file write is claimed.
- No learning-state write is claimed.
- The warning is explicit.

## 3. E2E Anti-Regression Must-Not-Have

The simulation fails if it contains:

- production runtime activation;
- production Coordinator activation;
- Z3/SymPy/PyTorch/calculator execution claim;
- node or bridge generation;
- hidden bridge teaching;
- pure interrogation before explanation;
- premature Exam handoff;
- `classroom_passed` as long-term graduation;
- fake scheduler update;
- learning-state write.

## 4. Negative-Path Simulation: Second Same-Signature Error Triggers REQUEST_REPREP

This section adds a scenario only; it does not change any contract text. It reuses the Section 2 fixture and follows `TEACHING_AGENT_CONTRACTS.md` Section 8.

### Step N1: First Error And Single Repair

Student (first error):

> I subtract 3 only from the left because that is where the 3 is.

Socratic repairs once with a reduced-dimension explanation (scale tilts when one pan changes), then asks one compact repair question. This consumes the single allowed repair for this error signature.

### Step N2: Second Error With The Same Signature

Student (same false intuition, signature `local_symbol_deletion`):

> Fine, then for 5x+2=12 I just delete the 2 on the left again.

Detection: `wrong_answer_count_same_signature: 2`. Socratic must not repeat the failed metaphor, must not invent a third explanation, and must not proceed toward Exam handoff.

### Step N3: REQUEST_REPREP Emission

```json
{
  "signal": "SYSTEM_INTERRUPT: REQUEST_REPREP",
  "failure_type": "metaphor_failure",
  "target_node": { "node_id": "sim_n_linear_equation" },
  "failed_component": "intuition_model",
  "evidence": {
    "actually_read_files": ["simulation_fixture_not_real_node_yaml"],
    "unsupported_reference": null,
    "student_feedback_summary": "Same local-deletion intuition after one repair; balance-scale model rejected twice."
  },
  "required_repair": "Prep_Architect regenerates intuition_model with a different low-friction model (e.g., equal-length rod cuts); keep MathLane_A, keep covered subtopic evidence for eq_meaning."
}
```

### Step N4: Bounded Continuation

Coordinator and Prep_Architect regenerate only the failed component. Teaching resumes from the repaired intuition model; already covered subtopics are preserved. Exam handoff remains withheld until all subtopics are covered and the definition restatement succeeds.

Acceptance checks:

- exactly one repair before escalation;
- the failed metaphor is not repeated after the second same-signature error;
- REQUEST_REPREP carries failure_type, failed_component, evidence, and required_repair;
- no Exam handoff occurs while the misconception is unresolved;
- no runtime, prompt mutation, or node generation is claimed.
