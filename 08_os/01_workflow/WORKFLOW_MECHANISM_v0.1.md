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

## 6. Stage 5 — execution, as a loop

Settled by Human decision 2026-07-27: **execution is inside the workflow**, and it is
not a straight line. The full chain:

```
requirement → A → evidence → B → test program → step decomposition
                                                      │
                                        ┌─────────────┘
                                        ▼
                            execute one step ──► verify
                                        ▲            │
                                        │       pass │ fail
                                        │            ▼
                                        └──────── retry ──► next step
                                                              │
                                                    all steps done
                                                              ▼
                                                          complete
```

Verification gates progress step by step. A step is not left until its tests pass, so a
defect is caught against the step that caused it rather than at the end against
everything at once.

### The loop needs an exit that is not success

"Retry until done" has no terminating condition when a step cannot be done, and that
produces two failures, the second worse than the first.

**Unbounded spin.** A step that is not achievable retries forever. The
first-generation system already answered this with a bounded repair budget — three
attempts, after which the task escalates rather than continuing. That precedent is
adopted here rather than reinvented.

**Termination by weakening the check.** Under retry pressure the cheapest way to make a
test pass is to change the test. A loop with no exit but success will find that exit.
This is the failure mode the loop must be built against, not merely warned about.

Two rules follow, and they are the load-bearing part of this section:

1. **Tests are frozen once the loop begins.** They were derived from evidence in stage
   4; changing them inside the loop is not a repair, it is a redefinition of what
   success means. A test that turns out to be wrong invalidates upward — see below —
   it is not edited in place.
2. **Repeated failure is a finding, not just a retry.** After the repair budget is
   exhausted, the correct question is not "how else can this step be implemented" but
   "which upstream artifact was wrong".

### Three exits, not two

| Exit | When | Action |
| :--- | :--- | :--- |
| pass | tests pass | proceed to the next step |
| retry | failure looks like an implementation defect, budget remains | re-execute the same step |
| invalidate | budget exhausted, or the failure indicates the evidence was wrong | append a verdict against `steps/`, `tests/`, `result/` or `evidence/` and return to that stage |

The third exit is the one that makes the loop honest. A step that cannot be made to
pass is evidence about the model that produced it — most often that B claimed something
the evidence did not actually support, which is exactly the case stage 3's
evidence-dependency naming exists to make traceable.

### Completion

All steps executed, all tests passing. That **is** completion, because it is exactly the
condition under which A is satisfied. There is no separate acceptance stage; adding one
would imply the tests were insufficient, and in that case the defect is in the tests.

**Open choice:** who performs execution — a backend executor under the existing
machinery, or a role defined inside this system. The boundary must be explicit either
way. What must not happen is execution being assumed to belong to whoever is nearby.

## 7. What this proposal does not settle

- Whether the stage contract adopts, adapts or replaces the first-generation
  `CODEX_TASK_INPUT_CONTRACT.md` shape. That contract already carries intent, definition
  of done, allowed scope, stop rules and a return contract, all in production use.
- How a workflow instance is registered and loaded — `05_registry/` and `06_execution/`,
  both downstream of this.
- Whether workflows can depend on other workflows.
