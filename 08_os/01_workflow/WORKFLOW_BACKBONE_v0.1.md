# Workflow backbone v0.1 — initial draft for discussion

Status: **draft, not agreed.** Human proposal of 2026-07-27, recorded faithfully in
part 1, with open questions in part 2. Part 2 items are not decisions and not
objections; they are the places where this draft does not yet say what happens.

The workflow is the entry point of the second-generation system. Everything else —
boot, mechanisms, skills, registry, execution — exists to serve it, and is built
outward from what the workflow turns out to need.

---

## Part 1 — the four stages, as proposed

### Stage 1 — requirement realization

Reach task consensus on a concrete requirement through sustained questioning and
dialogue. Refine the requirement and model the information it involves. Produce
**requirement model A**.

Artifact: `01_workflow/<workflow-id>/requirement/` — model A.

### Stage 2 — information base

Working from model A, collect and refine the evidence the requirement depends on.
Combine it with existing domain expertise already held.

Artifact: `07_content/<domain>/information/` — raw material, treated as source rather
than conclusion.

### Stage 3 — requirement result modeling

From model A plus the information base, produce **result model B**: what the realized
requirement looks like. Verify feasibility. The defining relation:

> If B is achieved, A is satisfied.

### Stage 4 — feasibility, steps, and generated tests

Establish the connection between A and B. Generate verification test steps against B,
so that B is checkable: passing tests mean B satisfies the requirement.

Working back from the tests, build the implementation steps for A. Decompose into
multiple steps. Multi-step testing produces B.

---

## Part 2 — open questions

### Q1. What happens when a later stage invalidates an earlier model?

The flow as drawn is linear: A → information → B → steps. In practice information
gathering routinely contradicts the requirement that requested it. In this repository
on a single day, measurement contradicted a written dispatch at least five times, and
in each case the measurement was right.

A linear workflow has nowhere to put that. It needs a declared backflow: any stage may
invalidate an upstream model, and doing so is a finding rather than a failure.

Undecided: whether invalidation restarts the stage, forks a revision of the model, or
suspends the workflow for a human decision. Also undecided: whether A is versioned, so
that "A as of the information base" and "A after revision" are distinguishable.

### Q2. Who declares that consensus has been reached?

Stage 1 ends when consensus exists. The failure mode is a model concluding it has asked
enough. The dialogue converges by construction — the questioner and the answerer are
optimising the same thing — so convergence is not evidence of completeness.

Options, undecided: an explicit human confirmation as the stage gate; or a decidable
completeness criterion, such as every clause in A tracing to a specific exchange, with
unresolved items listed rather than smoothed over.

### Q3. What falsifies B?

Stage 3 says feasibility is verified. By whom, against what.

If B is written and judged by the same party, that is an author designing the
verification of their own work. This project has a standing rule against it and paid for
the rule across six review rounds on one subsystem, where the same shape of error
recurred: a claim slightly wider than the thing actually checked.

Undecided: whether B requires an independent reviewer before stage 4, or whether the
tests of stage 4 are considered sufficient falsification. If the latter, Q4 applies.

### Q4. Should the tests derive from B, or from A?

This draft generates tests against B, and reads a passing suite as evidence that B
satisfies A.

That inference holds only if the tests encode **A's satisfaction conditions**. Tests
derived from B check B's internal consistency, and when the same reasoning produced both
B and its tests, they pass by construction. The discipline already in force here states
it directly: a passing test proves its own exact proposition and nothing wider.

Proposal for discussion: derive tests from A — "what evidence would convince us the
requirement is met" — and then check B against them. The tests become the written form
of the A→B relation rather than a description of B. This inverts the direction in the
draft and is the single change most likely to matter.

### Q5. Where does the workflow end?

The four stages end at producing B. Execution, acceptance and landing are outside them.

The first-generation system already runs that part: a backend executor implements, an
independent reviewer reads primary evidence from GitHub, the human holds the gates, and
conclusions land in the repository or the brief vault before anything is called done.
Whether stages 5 and 6 are added here, or the workflow deliberately hands off to that
existing machinery, is undecided — but the boundary must be drawn somewhere explicit
rather than left as an assumption.

### Q6. Artifact placement

A is placed. Information is placed. B, the tests, and the step decomposition are not.

Undecided, and worth settling before the first workflow runs, because it determines
what the registry records and what the loaders load.

---

## Part 3 — what this draft is not yet

It does not define the stage schema — what a stage declares, what makes it complete,
what it hands on. The first-generation system has a working version of exactly that in
`.ai/CODEX_TASK_INPUT_CONTRACT.md`: intent, definition of done, allowed scope, stop
rules, return contract. Whether the workflow stage adopts that shape, adapts it, or
replaces it is the next design conversation.

It also does not say how a workflow is registered, loaded or reloaded. That is
`05_registry/` and `06_execution/`, and both are downstream of this being settled.
