# Stage 1 Semantic-Gated Candidate Review Plan

packet_id: codex-math-mentor-stage-1-semantic-gated-candidate-review-plan-0001
task_id: math-mentor-stage-1-semantic-gated-candidate-review-plan-0001
status: completed_for_review

## 1. Scope

This is a non-mutating Stage 1 semantic-gated candidate review plan.

It does not modify teaching nodes, assign `mode: A` or `mode: B`, create formal definitions, create prerequisites, create mapping boundaries, edit roadmaps, edit bridges, mutate prompts/schemas/validators, activate runtime, activate Coordinator, or write scheduler/learning state.

## 2. Evidence Basis

- source branch: `master`
- verified source head: `e8a226cd355faf5db170c51dced7833c581bd077`
- Batch-2 selection plan is published on master and states `next_batch_type: no_safe_metadata_batch`.
- Stage 0 inventory identifies 16 mode-missing identity-stable DIFF_GEO candidates.
- All 16 have stable `id`, stable filename identity, split-roadmap alias, and 4 `sub_topics`.
- All 16 already carry:
  - `formal_definition_status: missing`
  - `prerequisites_status: missing`
  - `mapping_boundary_status: missing`
  - `validation_status: manual_review_required`
  - `bridge_readiness_status: manual_review_required`

Teaching authority constraints:

- `MathLane_B` requires LLM-architecture mapping as the primary mapping.
- Household, factory, fluid, or ordinary-object metaphors cannot be primary Mode B/MathLane_B mapping.
- No deterministic tool claim is valid without `run_with_log` and a concrete log reference.
- Full subtopic coverage and definition restatement are required before Exam handoff in future teaching tasks.

## 3. Cohort Summary

### Cohort 1: Foundational Smooth Manifold Entry

Nodes:

- `DIFF_GEO-653` 光滑流形, occurrence/genesis framing.
- `DIFF_GEO-654` 光滑流形, engineering framing.

Planning judgment:

- `DIFF_GEO-653` is the safest first semantic review pilot because it is the conceptual root for the DIFF_GEO chain.
- `DIFF_GEO-654` appears duplicative/alternate-framing relative to `DIFF_GEO-653`; it should be reviewed after 653 to decide whether it is a separate node, companion application node, or merge/defer candidate.

### Cohort 2: Local Differential Calculus On Manifolds

Nodes:

- `DIFF_GEO-655` tangent vector fields.
- `DIFF_GEO-656` differential forms.
- `DIFF_GEO-657` Riemannian metric.
- `DIFF_GEO-661` connection.

Planning judgment:

- These depend on a reviewed smooth-manifold foundation.
- Future repair should not start here before `DIFF_GEO-653` has a formal definition, prerequisites, lane decision, and mapping boundary.

### Cohort 3: Curvature / Generative Geometry / Transport

Nodes:

- `DIFF_GEO-658` curvature tensor and hyperbolic LLM mapping.
- `DIFF_GEO-659` curvature tensor and hallucination-law mapping.
- `DIFF_GEO-660` geodesics and flow matching mapping.
- `DIFF_GEO-664` submanifold theory and second fundamental form.

Planning judgment:

- These nodes have stronger AI/LLM-architecture relevance in concept text, but also higher semantic risk because they mix advanced geometry with model behavior claims.
- They require explicit Human/ChatGPT semantic review before any mapping or validation status change.

### Cohort 4: Topology / Bundles / Global Invariants

Nodes:

- `DIFF_GEO-662` Chern classes.
- `DIFF_GEO-663` Gauss-Bonnet theorem.
- `DIFF_GEO-665` de Rham cohomology.
- `DIFF_GEO-667` vector bundles and principal bundles.

Planning judgment:

- These require prerequisite graph review across differential geometry, algebraic topology, and bundle theory.
- They are not safe first-pilot candidates.

### Cohort 5: Symmetry And Hamiltonian Structure

Nodes:

- `DIFF_GEO-666` Lie groups and Lie algebras with RoPE mapping.
- `DIFF_GEO-668` introductory symplectic geometry.

Planning judgment:

- These are high-value AI mapping candidates, but they are not root repairs.
- They require prior decisions about lane routing and prerequisite graph placement.

## 4. Candidate Table

| node id | concept | existing status fields | subtopics | mode/lane evidence | semantic risk | candidate repair type | Human Speaker required |
| --- | --- | --- | --- | --- | --- | --- | --- |
| DIFF_GEO-653 | Smooth manifolds, atlas/charts | formal/prereq/boundary missing; validation/bridge manual | 4 | no explicit mode; physical metaphor only | medium | mode routing policy + formal definition + prerequisites + mapping boundary | yes |
| DIFF_GEO-654 | Smooth manifolds, engineering framing | same | 4 | no explicit mode; engineering metaphor only | high duplicate/alternate-frame risk | defer until 653 reviewed; possible companion/merge decision | yes |
| DIFF_GEO-655 | Tangent vector fields | same | 4 | no explicit mode; physical metaphor only | medium-high | formal definition + prerequisites from 653 + mapping boundary | yes |
| DIFF_GEO-656 | Differential forms | same | 4 | no explicit mode; physical metaphor only | high | formal definition + prerequisites + mapping boundary | yes |
| DIFF_GEO-657 | Riemannian metric | same | 4 | no explicit mode; physical metaphor only | medium-high | formal definition + prerequisites + mapping boundary | yes |
| DIFF_GEO-658 | Curvature tensor / hyperbolic LLM mapping | same | 4 | concept has LLM mapping; stored mapping is physical | high | lane policy + LLM mapping boundary + formal definition | yes |
| DIFF_GEO-659 | Curvature tensor / hallucination law | same | 4 | concept has AI claim; stored mapping is physical | very high | semantic claim review before repair | yes |
| DIFF_GEO-660 | Geodesics / flow matching | same | 4 | concept has generative-flow mapping; stored mapping is physical | high | semantic claim review + formal definition + prerequisite graph | yes |
| DIFF_GEO-661 | Connections / covariant derivative | same | 4 | no explicit mode; physical metaphor only | high | formal definition + prerequisites from 653/655/657 | yes |
| DIFF_GEO-662 | Chern classes | same | 4 | no explicit mode; physical/topology metaphor | very high | defer; needs bundle/cohomology prerequisites | yes |
| DIFF_GEO-663 | Gauss-Bonnet theorem | same | 4 | no explicit mode; physical/global metaphor | very high | defer; theorem-level semantic repair | yes |
| DIFF_GEO-664 | Submanifold theory / second fundamental form | same | 4 | no explicit mode; physical embedding metaphor | high | formal definition + prerequisite graph | yes |
| DIFF_GEO-665 | de Rham cohomology | same | 4 | no explicit mode; physical topology metaphor | very high | defer; topology prerequisite review | yes |
| DIFF_GEO-666 | Lie groups / Lie algebra / RoPE mapping | same | 4 | concept has AI/RoPE mapping; stored mapping is physical | high | lane policy + AI mapping boundary + prerequisites | yes |
| DIFF_GEO-667 | Vector bundles and principal bundles | same | 4 | concept has model-layer mapping; stored mapping is physical | very high | defer until bundle prerequisites reviewed | yes |
| DIFF_GEO-668 | Symplectic geometry | same | 4 | concept has neural-network/physics mapping; stored mapping is physical | high | defer until Hamiltonian prerequisites reviewed | yes |

## 5. Safest First Semantic Review Pilot

Recommended first semantic pilot:

```text
DIFF_GEO-653.yaml
```

Reason:

- It is the smooth-manifold root node.
- It has stable identity and complete `sub_topics`.
- It is prerequisite-like for most other DIFF_GEO nodes.
- It has lower semantic coupling than curvature, cohomology, bundles, Lie theory, or symplectic geometry.

Future repair for `DIFF_GEO-653` should be one-node only unless Human explicitly authorizes a larger cohort.

## 6. Required Human Speaker Decisions

### Lane-Routing Policy Question

Should DIFF_GEO nodes be routed as:

- `MathLane_B` by default because differential geometry is pure-structure/advanced geometry;
- `mixed` when a node explicitly bridges computable calculus intuition to pure structure;
- or node-specific routing based on subtopic evidence?

No `mode: A/B` or `MathLane_A/B` assignment should be written until this policy is decided.

### Formal-Definition Content Question

For `DIFF_GEO-653`, Human/ChatGPT must approve a compact definition of smooth manifold, likely involving:

- second-countable Hausdorff topological space;
- atlas of charts to Euclidean space;
- smooth transition maps;
- fixed dimension.

This task does not create that definition.

### Prerequisite Graph Question

For `DIFF_GEO-653`, likely prerequisite classes include:

- topology basics;
- Euclidean space / coordinate maps;
- differentiability of maps between open subsets of Euclidean space;
- possibly inverse function theorem context.

Exact prerequisite nodes must be selected in a future authorized repair task.

### Mapping-Boundary Question

Existing mappings are mostly ordinary physical/factory metaphors. If DIFF_GEO is routed to `MathLane_B`, future repair must either:

- replace primary mapping with LLM-architecture mapping;
- mark existing ordinary metaphors as secondary teaser only;
- or trigger re-prep because primary mapping evidence is missing.

### Bridge-Readiness Question

No DIFF_GEO node should become bridge-ready during the first semantic pilot. Bridge readiness should remain `manual_review_required` until formal definition, prerequisites, mapping boundary, and bridge endpoint review are completed.

## 7. Future Authorized Repair Scope

A future one-node `DIFF_GEO-653` repair may edit only:

- `mode` or `math_lane` metadata after lane policy approval;
- `mode_routing_status`;
- `formal_definition_status` and a reviewed formal definition field if authorized;
- `prerequisites_status` and explicit prerequisite refs if authorized;
- `mapping_boundary_status` and mapping boundary text if authorized;
- `validation_status` only as `semantic_only` or `review_required`, unless a real deterministic log exists;
- `bridge_readiness_status` only as `manual_review_required` unless bridge review is separately authorized;
- `migration_review` notes.

It must not edit unrelated mathematical body fields, other nodes, roadmaps, bridges, prompts, schemas, validators, runtime files, learning state, or scheduler files.

## 8. Future Validation And Stop Rules

Minimum validation for a future authorized one-node semantic repair:

```powershell
python 08_Domain_Applications/Math_Mentor/tests/teaching_flow_static_validator.py
git diff --check
```

Additional required checks:

- parse touched YAML with PyYAML;
- confirm only the authorized node and `.ai` reports changed;
- confirm no `run_with_log`, SymPy, Z3, PyTorch, calculator, sandbox, or machine-proof claim was added without concrete log refs;
- confirm `MathLane_B` does not use ordinary physical metaphor as primary mapping;
- confirm every future `sub_topics` item remains present unless Human authorizes subtopic repair;
- run scoped secret scan over changed files.

Stop before mutation if:

- lane policy is undecided;
- formal definition wording is not approved;
- prerequisite refs are not selected;
- mapping boundary would require inventing an LLM architecture mapping;
- any edit would promote validation or bridge readiness without evidence;
- any forbidden path changes.

## 9. Final Recommendation

Do not run another metadata-only batch.

Proceed only to a Human-approved one-node semantic pilot for:

```text
08_Domain_Applications/Math_Mentor/Pure_Math_Intuition_DB/DIFF_GEO-653.yaml
```

Recommended pilot type:

```text
human_semantic_gate_required
```
