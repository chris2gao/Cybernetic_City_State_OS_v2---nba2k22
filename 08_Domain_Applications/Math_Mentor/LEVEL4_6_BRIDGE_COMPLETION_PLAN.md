# Level 4-6 Bridge Completion Plan

## 1. Current Goal

Complete the missing knowledge associations for the generated Level 4, Level 5, and Level 6 nodes without changing the teaching philosophy or regenerating the underlying concept nodes. The result should make bridge concepts visible, teachable association slots that support an intuition-to-definition lesson, full `sub_topics` coverage, Exam Agent handoff, and later spaced review.

Current audit baseline:

- The database contains 14 `BRIDGE-*.yaml` files but only 10 distinct IDs (`BRIDGE-001` through `BRIDGE-010`). IDs 001-004 each have two files with different schemas.
- `知识图谱_节点映射索引.md` lists only five of those 14 bridge files.
- None of the current bridge records explicitly declares Level 4-6 endpoints using `from_nodes` and `to_nodes`; no Level 4-6 bridge can currently be routed reliably.
- Level 4 split roadmap: 90 nodes (`n_390`-`n_479`); 63 files are present. `n_390`-`n_416` are absent.
- Level 5 split roadmap: 152 nodes (`n_480`-`n_631`); 105 files are present. `n_502`-`n_548` are absent.
- Level 6 split roadmap: 139 nodes (`n_632`-`n_770`); all 139 files are present.
- Within Level 6 Part 1, 31 algebraic-geometry/algebraic-topology files contain explicit mundane/factory mapping markers even though those domains route to Mode B. Bridge generation must not copy those mappings as canonical Mode B teaching content.

Bridge generation must therefore use only endpoints that physically exist. Bridges involving missing Level 4 or Level 5 nodes remain planned but cannot be merged until those nodes are available and validated.

## 2. Out Of Scope

- Do not read `数学知识路线图_全部.yaml` for routine batch work.
- Do not regenerate or broadly rewrite Level 4-6 concept nodes.
- Do not repair noncompliant Mode B endpoint mappings as part of bridge generation; report them for a separate node-remediation batch.
- Do not repair the legacy duplicate bridge IDs inside a content-generation batch; handle that as a separate schema-migration decision.
- Do not infer endpoints from a suggestive metaphor or filename when the mathematical dependency is not explicit.
- Do not generate all bridges at once, merge `master`, or change the review scheduler.

## 3. Bridge Type Definitions

- `intra_layer`: connects concepts at the same level when one structure, representation, or theorem clarifies another branch at that level.
- `cross_layer`: connects different levels through a bidirectional structural equivalence or reusable pattern that is not merely a one-way prerequisite.
- `prerequisite_bridge`: connects already learned source nodes to a target node whose definition or proof depends on them. It is eligible for formal teaching only after the required source nodes have passed the classroom exam.
- `forward_outlook_bridge`: connects the current node to unlearned future knowledge. It is visible only as a short motivational teaser and cannot introduce assessable definitions or notation.

## 4. Recommended Bridge YAML Schema

```yaml
id: "BRIDGE-XXX"
concept_name: "<short mathematical connection name>"
from_nodes:
  - "n_000"
to_nodes:
  - "n_000"
source_level: 4
target_level: 5
bridge_type: "intra_layer | cross_layer | prerequisite_bridge | forward_outlook_bridge"
conceptual_connection: >-
  <precise statement of the shared structure, dependency, or transformation>
teaching_use:
  association_slot: "<where this bridge appears in the target lesson>"
  formal_link: "<definition, theorem, representation, or proof step it supports>"
  forcing_question: "<one compact question that checks the connection>"
mode: "A | B | mixed"
learned_history_rule:
  required_nodes:
    - "n_000"
  evidence: "classroom_passed_after_exam_agent"
  when_satisfied: "formal_teaching_content"
  when_unsatisfied: "teaser_only_or_hidden"
sub_topics:
  - "<connection checkpoint 1>"
  - "<connection checkpoint 2>"
llm_physical_mapping: >-
  <Mode A everyday physical model, Mode B LLM-architecture mapping, or both parts for mixed mode>
validation:
  strategy: "computational_audit | semantic_consistency_audit | mixed"
  acceptance_rule: "<specific executable assertion or semantic criteria>"
```

Schema rules:

- `from_nodes` and `to_nodes` use canonical roadmap IDs (`n_XXX`); filenames remain index metadata, not graph identity.
- `mode` follows the domain routing table in `Universal_Layer_Execution_Protocol.md`, not the level number alone.
- A `mixed` bridge must separate its computable claim from its structural claim so each part can use the correct validation path.
- Mode B mappings must use LLM architecture. Everyday physical metaphors are not valid canonical Mode B mappings.
- Every bridge is itself a learning object: its `sub_topics` and forcing question must be completed before the target lesson can close.

## 5. Batched Execution Plan

Every batch contains at most five bridge nodes. Each batch reads only the relevant split roadmap and exact endpoint YAML files, then runs the applicable computational or semantic audit before index registration.

### Batch 1: Level 4 Intra-Layer Bridges

Start with five candidate connections whose endpoint files already exist:

1. `n_418 -> n_442`: complex exponentials connect Euler representation to oscillatory ODE characteristic roots.
2. `n_431 -> n_445/n_463`: complex power-series convergence connects to ordinary and Frobenius series solutions.
3. `n_423-n_427 -> n_446/n_447`: complex path integration and residues connect to Laplace-domain ODE solution methods.
4. `n_430 -> n_468/n_469`: multivalued analytic functions and Riemann surfaces connect to field extensions and Galois symmetry.
5. `n_433 -> n_472`: matrix representations of Möbius transformations connect to representation theory.

Before creation, verify the exact `sub_topics` at every endpoint and decide whether each candidate is `intra_layer`, `prerequisite_bridge`, or `mixed`.

### Batch 2: Level 4 -> Level 5 Cross-Layer Bridges

Prioritize existing endpoint families:

- ODE spectral/boundary-value methods -> PDE separation of variables and eigenvalue construction.
- ODE stability/flow methods -> stochastic processes and probability-flow dynamics.
- complex/Fourier/Laplace methods -> PDE transform methods.
- finite fields and algebraic structure -> combinatorial constructions where an explicit dependency exists.

Defer candidates requiring absent `n_390`-`n_416` or `n_502`-`n_548` files.

### Batch 3: Level 5 Intra-Layer Bridges

Prioritize PDE <-> stochastic-process connections such as heat kernels/Brownian motion and Feynman-Kac, then connect combinatorial counting to stochastic state spaces only where the formal relation is explicit. Local-geometry connections remain blocked while `n_502`-`n_548` are absent.

### Batch 4: Level 5 -> Level 6 Cross-Layer Bridges

Prioritize:

- variational PDE methods -> optimization;
- stochastic processes -> information theory and machine-learning probability models;
- combinatorics -> information-theoretic coding and discrete optimization;
- local differential geometry -> Level 6 differential/algebraic geometry after the missing Level 5 files exist.

### Batch 5: Level 6 Intra-Layer Bridges

Prioritize algebraic geometry <-> algebraic topology/differential geometry, analytic number theory -> cryptography, information theory -> machine learning, and optimization -> machine learning. Split mixed computational/structural claims into separate validation sections.

### Batch 6: Index Update And Coordinator Integration

1. Register every accepted bridge filename and endpoint summary in `知识图谱_节点映射索引.md`.
2. Detect duplicate bridge IDs and dangling endpoint IDs before merge.
3. Test Coordinator lookup from both a `from_nodes` endpoint and a `to_nodes` endpoint.
4. Verify first-use compressed display, learned-history filtering, forward-teaser filtering, and one bridge comprehension question.
5. Verify Exam Agent handoff and spaced-review handoff remain unchanged.

## 6. Per-Batch Acceptance Checklist

- No more than five bridge YAML files are created or reviewed together.
- Every endpoint file exists and matches the split roadmap.
- All required schema fields are present.
- The conceptual connection is mathematically directional and does not rely on metaphor alone.
- Mode A claims pass the applicable evaluator; Mode B claims receive `SEMANTIC_AUDIT_PASSED`; mixed bridges pass both relevant checks.
- Learned prerequisites become formal content; unlearned future nodes remain teaser-only.
- The index is updated only after validation succeeds.
- After three failed repair attempts, record the bridge in `三次修复仍失败_待后续处理.md` and stop retrying it.
