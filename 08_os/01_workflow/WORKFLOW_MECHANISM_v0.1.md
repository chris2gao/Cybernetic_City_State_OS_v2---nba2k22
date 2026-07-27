# Workflow mechanism v0.1 — proposal

Status: **proposal.** The four stages are settled in `WORKFLOW_BACKBONE_v0.2.md`. This
describes how they connect: what a stage declares, what makes it complete, what it
hands on, and how a workflow instance is tracked.

Open choices are marked. They are choices, not oversights.

---

## 1. The governing property: state is derived, never declared

A workflow instance has no state file.

Its stage is **computed** from which artifacts exist and validate. Artifacts present and
consistent means the stage is reached; an artifact invalidated means the stage is not.

This is the one design decision taken on direct evidence rather than preference. Every
significant defect found in the first-generation system had the same shape: a
declaration that nothing checked, drifting from what it described. The ownership
manifest declared no content under paths holding 337 files. A generated index claimed
1883 tracked files against a real 503. Load-profile digests described files that had
moved. An execution record stated that directories were untouched after they had been
moved.

A `state: stage_3` field would acquire the same capacity on the day it is written.
Deriving the stage removes the capacity rather than promising to check it.

**Consequence:** every stage's completion condition must be decidable from artifacts on
disk. A stage that can only be judged by asking someone is not finished being designed.

## 2. Instance layout

```
08_os/01_workflow/<workflow-id>/
  requirement/        A — the requirement model
  evidence/           what stage 2 gathered, including negative results
  result/             B — the result model, naming the evidence it rests on
  tests/              test steps derived from the evidence
  steps/              the decomposition
  verdicts/           invalidation verdicts, appended, never edited
```

`<workflow-id>` is stable and human-readable. The information base itself lives in
`07_content/<domain>/information/`; `evidence/` here holds the workflow's *use* of it —
which items were consulted, what was searched and returned nothing, and where a search
hit a result limit.

That last part is not bookkeeping. It is the only mechanism by which the boundary of the
evidence set becomes visible, and the reason is recorded in the backbone's residual-risk
section.

## 3. Stage contract

Every stage declares the same five things:

```yaml
stage: "<number and name>"
consumes: ["<artifact paths this stage reads>"]
produces: "<the single artifact path this stage writes>"
complete_when: "<a condition decidable from artifacts on disk>"
may_invalidate: ["<upstream artifacts this stage is entitled to reject>"]
```

One stage, one durable artifact. A stage that wants to produce two is two stages, or one
of the two is scratch and is not kept.

### The four stages under this contract

| Stage | consumes | produces | complete_when |
| :--- | :--- | :--- | :--- |
| 1 requirement | — | `requirement/` | A exists and the Human has confirmed it reads as the same requirement they meant |
| 2 evidence | `requirement/` | `evidence/` | evidence recorded **with** its negative results, and a feasibility verdict written |
| 3 result | `requirement/`, `evidence/` | `result/` | B exists and every claim in it names the evidence item it rests on |
| 4 tests and steps | `evidence/`, `result/` | `tests/`, `steps/` | every test traces to an evidence item; steps decompose to those tests |

Stage 4 is the one exception to one-stage-one-artifact, and it is deliberate: the tests
fix what the steps must achieve, so separating them would allow steps to be written
before the tests they answer to. **Open choice:** split them into 4a and 4b with the
same rule enforced by ordering instead.

## 4. Invalidation is a first-class transition

Any stage may reject an upstream artifact. This is not an error path.

A verdict is appended to `verdicts/` naming the rejected artifact, the evidence for the
rejection, and what must change. The rejected artifact is **not edited in place** — it
is superseded by a new version, so that "A as the evidence was gathered against" and "A
after revision" stay distinguishable.

Stage 2 rejecting A is expected often enough that it is part of the stage's purpose:
evidence gathered on behalf of a requirement contradicts it regularly. Stages 3 and 4
may reject upward for the same reason, and the mechanism is identical.

Derived state follows automatically: once A is superseded, the artifacts built on the
old A no longer validate, and the instance is back at the stage where its inputs are
sound. Nothing needs to be reset by hand, which is the point of deriving rather than
declaring.

## 5. Who performs, who confirms

| Stage | performs | confirms |
| :--- | :--- | :--- |
| 1 | model and Human together | Human — this is the one place a human confirmation is structural rather than procedural |
| 2 | model | the negative-results record makes the boundary checkable by anyone |
| 3 | model | evidence-dependency naming makes each claim traceable |
| 4 | model | test-to-evidence tracing is mechanically checkable |

Stage 1 needs the Human because its completion condition is that two parties mean the
same thing, and no artifact can establish that on its own.

The other three are designed so that a reader who did not perform them can check them
from the artifacts. That is deliberate and it is what makes independent review possible
without re-running the work.

**Open choice:** whether stage 3's B additionally requires an independent reviewer
before stage 4 begins. The evidence-tracing requirement may already be sufficient. This
is the point where the project's existing rule — an author should not design the
verification of their own work — either applies or is judged already satisfied.

## 6. Execution and completion

The steps are executed and the tests run. Tests passing is completion, because that is
exactly the condition under which A is satisfied. There is no separate acceptance.

**Open choice:** whether execution is a workflow stage or a handoff to the machinery
that already exists — backend executor, independent reviewer, human gates. The boundary
must be explicit either way; what must not happen is execution being assumed to belong
to whoever is nearby.

## 7. What this proposal does not settle

- Whether the stage contract adopts, adapts or replaces the first-generation
  `CODEX_TASK_INPUT_CONTRACT.md` shape. That contract already carries intent, definition
  of done, allowed scope, stop rules and a return contract, all in production use.
- How a workflow instance is registered and loaded — `05_registry/` and `06_execution/`,
  both downstream of this.
- Whether workflows can depend on other workflows.
