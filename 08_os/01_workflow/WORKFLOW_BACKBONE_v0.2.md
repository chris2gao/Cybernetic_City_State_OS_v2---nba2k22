# Workflow backbone v0.2

Supersedes v0.1. The six open questions of v0.1 were answered by the Human on
2026-07-27; this version folds the answers into the stages rather than leaving them
beside it. One residual risk is recorded at the end.

The workflow is the entry point of the second-generation system. Everything else —
boot, mechanisms, skills, registry, execution — is built outward from what the workflow
turns out to need.

---

## The shape

```
A ──────────────► evidence ──────────────► B
requirement       information base         result model
   │                    │                    │
   │                    ├── feasibility ─────┤
   │                    │   assessment       │
   │                    │                    │
   └──────── tests derived from evidence ────┘
                        │
                  step decomposition
                        │
                     execute → tests pass → A is satisfied
```

The load-bearing relation is **B achieved implies A satisfied**. B is a proposition
about A, not a deliverable beside it. That is what stops a project completing something
nobody can demonstrate was the thing asked for.

---

## Stage 1 — requirement modeling

Reach consensus through sustained questioning: the model and the Human specify the
requirement's information together until it stands in three dimensions rather than in a
few sentences.

The point is not agreement. It is that both parties can state the same requirement and
mean the same thing. A requirement described in a sentence is under-specified in ways
neither party can see until the questioning exposes them. Existing continuous-questioning
skills are a reference for the technique.

**Output:** requirement model A, in `01_workflow/<workflow-id>/requirement/`.

**Complete when:** the requirement is modeled to where the Human and the model both
understand it accurately — materially more concrete than the sentence it started as.

## Stage 2 — information base, and the feasibility verdict

Working from A, collect and refine the evidence the requirement depends on — deep
research and equivalent gathering — and combine it with domain knowledge already held.

**This stage has two outputs, not one.** The information base is the visible one. The
second is a feasibility assessment: whether the evidence supports building anything
that would satisfy A.

That verdict may be negative, and a negative verdict is a finding rather than a
failure. Evidence gathered on behalf of a requirement routinely contradicts it. The
workflow does not treat that as an exception path because it is not exceptional; it is
what stage 2 is partly for.

**Output:** information base in `07_content/<domain>/information/`, treated as source
material rather than as conclusion. Plus the feasibility verdict.

## Stage 3 — result modeling

From A and the evidence, derive **B** dialectically: what the realized requirement
looks like, and why the evidence supports it.

Feasibility is not asserted separately. If B can be constructed on the evidence, that
construction is the feasibility argument — and B must record **which evidence it rests
on**, so that a later failure can be traced to the specific insufficient item rather
than to a general misjudgement.

**Output:** result model B, with its evidence dependencies named.

## Stage 4 — tests, then steps

**Tests derive from the evidence, not from B.**

This is the stage's defining rule and it is worth stating why. Tests generated from B
check B's internal consistency; when one line of reasoning produced both B and its
tests, they pass by construction and prove nothing. Evidence is the third party — it
was authored by neither A nor B — so a test grounded in an external fact can fail
honestly.

The same evidence therefore does two jobs: it establishes that B is feasible, and it
supplies what the tests must demonstrate.

With the tests fixed, work backwards to the implementation steps for A. Decompose into
multiple steps. Multi-step testing produces B.

**Output:** test steps and step decomposition.

## Completion

B implemented and its tests passing **is** the end of the workflow, because that is
exactly the condition under which A is satisfied. There is no separate acceptance
stage, and adding one would imply the tests were not sufficient — in which case the
defect is in the tests.

---

## Residual risk, recorded not solved

Constructibility is not identical to achievability. A model can be coherent on the
available evidence and still not be buildable, if the evidence is incomplete in a way
nobody noticed. Stage 3's requirement that B name its evidence dependencies is the
mitigation: it does not prevent the failure, but it makes the post-mortem specific —
which evidence was insufficient, rather than which judgement was wrong.

---

## What v0.2 still does not define

- **The stage schema.** What a stage declares, what makes it complete, what it hands
  on. The first-generation system has a working version in
  `.ai/CODEX_TASK_INPUT_CONTRACT.md` — intent, definition of done, allowed scope, stop
  rules, return contract. Adopt, adapt, or replace: undecided.
- **Placement of B, the tests and the steps.** A and the information base are placed.
  These are not, and the answer determines what the registry records and what the
  loaders load.
- **Who executes the steps.** Outside the workflow definition, but the boundary should
  be explicit rather than assumed.
