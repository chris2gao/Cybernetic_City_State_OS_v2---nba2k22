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

## Residual risk, stated precisely

An earlier draft framed this as "constructibility is not achievability". That framing
was too loose and is withdrawn: because B is **derived from** the evidence rather than
designed first and justified afterwards, the derivation direction already answers most
of it. Deriving B from evidence and finding evidence for a chosen B are different
activities, and this workflow does the first.

What remains is narrower and sits in one place.

**The completeness of the evidence set cannot be established by the evidence set.**
Stage 2 ends when the gatherer judges the evidence sufficient, and that gatherer is the
same party who then derives B. Every other link in the chain rests on evidence; the
stopping rule does not.

Worked example from this repository, 2026-07-26. An agent searched for the release
rebinding procedure, received a result list truncated at its limit, concluded that no
document described the procedure, and reconstructed one from commit history. The
reconstruction was correct in shape. The evidence set was incomplete —
`.ai/communication_compliance/README.md#release-binding` described the procedure in
full — and **nothing inside the evidence set could indicate that**. The reconstruction
also omitted that `lane_epoch.yml` must be bound in the same cycle, which the missed
document stated plainly. Executing the reconstructed version would have completed half
a release binding.

**Mitigation, already house doctrine rather than a new rule.**
`AGENT_WORKING_DISCIPLINE.md` requires recording what was examined and rejected, and
why, on the grounds that no research tool produces it and every one of them is biased
toward positive synthesis.

Applied here: the information base records **what was searched and returned nothing**,
alongside what was found, including where a search hit a result limit. A later reader
can then see the boundary of the evidence set instead of mistaking it for the whole.
This does not make the set complete. It makes its incompleteness visible, which is the
difference between a gap that can be noticed and one that cannot.

Stage 3's requirement that B name the evidence it rests on remains, for the same
reason: it makes a later failure specific — which evidence was insufficient — rather
than a general verdict that some judgement was wrong.

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
