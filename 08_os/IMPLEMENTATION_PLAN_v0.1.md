# Second-generation system — implementation plan v0.1

Status: **draft for discussion.** Not yet reviewed by any other model, by decision.

The design is settled far enough to plan against: `01_workflow/WORKFLOW_BACKBONE_v0.2.md`
fixes the four stages, `01_workflow/WORKFLOW_MECHANISM_v0.1.md` fixes how they connect.
This says how the system gets built, in what order, and what has to be decided before
anything starts.

---

## 1. The principle that sets the order

**Build what the workflow demands, when it demands it.** Not seven areas in parallel,
not a complete platform waiting for a first user.

The first-generation system was built the other way and the cost was measured: 855
tracked files, of which a third belonged to one domain, with two working mechanism
files deleted by a correct analysis because nothing recorded that they were loaded from
outside. Structure that arrives before its use has nothing to check it against.

So the order below is a dependency order, not a wish list. An area is built when
something concrete is blocked without it.

## 2. Current state

| Area | State |
| :--- | :--- |
| `01_workflow` | designed — backbone v0.2, mechanism v0.1. Stage contract unsettled |
| `02_boot` | empty, purpose stated |
| `03_mechanisms` | empty, purpose stated |
| `04_skills_and_tools` | empty, purpose stated |
| `05_registry` | empty, purpose stated |
| `06_execution` | empty, purpose stated |
| `07_content` | empty, purpose stated |

The first-generation system is tidied and stays available as a donor: mechanisms that
already work there are ported selectively, assessed one at a time, never copied
wholesale.

## 3. Two decisions that block the start

Neither is a detail and neither can be deferred by starting anyway.

**D1 — the stage contract.** Does a workflow stage adopt, adapt, or replace the shape
already in production at `.ai/CODEX_TASK_INPUT_CONTRACT.md`: intent, definition of
done, allowed scope, stop rules, return contract. Adopting is cheapest and carries
known-good semantics. Replacing is cleaner conceptually and costs a re-derivation of
everything that contract learned the hard way.

**D2 — who executes.** A backend executor under the existing machinery, or a role
defined inside this system. This determines whether `06_execution` loads an external
agent or drives an internal one, and it changes what the loaders look like.

Everything in section 4 assumes these are answered. They are the first thing to
discuss with another model.

## 4. Build order

### Step 1 — run one workflow by hand, end to end

Before automating a workflow, run one manually through all four stages and the
execution loop. The obvious candidate is **building this system itself**: requirement,
evidence, result model, tests, steps, execute.

This is deliberate and it is the cheapest available validation. A workflow that cannot
carry its own construction will not carry anything else, and every gap shows up as a
question the person running it cannot answer from the design.

There is a bootstrap limit worth stating: the run is manual, so it validates the
**stages**, not the loaders or the context partitioning. Those cannot be tested until
they exist. What the manual run produces is the list of what they must do.

**Produces:** one complete workflow instance under
`01_workflow/<workflow-id>/`, and a list of everything the design failed to specify.

### Step 2 — registry v0, from what step 1 actually needed

Not a schema designed in advance. The registry's first entries are the artifacts step 1
produced and the mechanisms it turned out to require.

The field set is already drafted in `05_registry/README.md`, including `loader_class`
and `failure_surfacing` — both present because the first-generation system lost files
for want of them.

**Produces:** `05_registry/` with real entries and a validator that fails on a
registered path that does not exist, an existing path with no entry, and a declared
cache directory that is neither present nor correctly ignored.

### Step 3 — context partitioning, because the design depends on it

Role separation with partial context is what makes test tampering structurally
impossible rather than merely forbidden. That property is load-bearing in the mechanism
document, so it has to become real before the workflow runs unattended.

This is where `02_boot` and `06_execution` get built, together, because a loader and
the context it establishes are the same problem seen from two ends.

The enforcement question is open and should be settled here: partitioned **loading** is
a discipline; per-role **worktrees** are a boundary. Thirty-two worktrees are already
registered in this repository and both Codex and Antigravity run subagents in their
own, so the mechanism exists and the choice is whether to use it.

**Produces:** `02_boot/` context model, `06_execution/` loaders for at least the roles
step 1 used.

### Step 4 — port mechanisms on demand

One at a time, when a workflow run needs one. Candidates in rough order of likely
demand: the communication protocol, release binding, compliance validation, lane
coordination.

Each port carries its failure history with it, not just its code. The release binding
mechanism is worth more with the knowledge that its two binding surfaces can disagree
silently than without it.

**Produces:** `03_mechanisms/<name>/` per ported mechanism, each with a registry entry.

### Step 5 — skills, tools, content

`04_skills_and_tools` and `07_content` fill as real work arrives. Neither is on the
critical path; both are where the system stops being infrastructure and starts being
useful.

## 5. What "done" means for the migration

The second-generation system is complete when a workflow can be run through it without
consulting the first-generation repository. Until then the old system is a donor, not a
dependency — and the difference should be checkable rather than assumed.

`os/second-generation` becomes `master` at that point, by Human decision, not
automatically.

## 6. Risks recorded now

**Designing further before running anything.** The design is already deeper than
anything that has been tried. Step 1 exists to correct that, and its value drops the
longer it is deferred.

**The registry drifting from the code it describes.** The stated rule is that the
registry updates in the same change as the development. That rule is exactly the kind
this repository has watched fail — declarations that nothing checks. The validator in
step 2 is not optional garnish; it is what makes the rule true.

**Porting by sympathy rather than by demand.** Mechanisms in the old system work and
are tempting to bring across wholesale. A third of the old repository turned out to be
one domain's material precisely because things arrived without being asked for.

---

## 7. Immediate next action

Settle D1 and D2. Then step 1, with the requirement being the construction of this
system.
