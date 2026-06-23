# Math Mentor Canonical Bridge Schema

## 1. Purpose

A bridge is the connection layer of the Math Mentor knowledge graph. It turns isolated YAML concept nodes from a knowledge tree into a cognitive topology network.

- A bridge is a teaching-system consumable object.
- A bridge must serve `08_Math_Mentor_Coordinator_Prompt.md` directly.
- A bridge must support intra-layer association, cross-layer association, prerequisite backtracking, and forward outlook.
- A bridge is not an explanatory note. It is a typed structural edge in the knowledge graph.

## 2. Current Audit Findings

The P1 registry audit established the following baseline:

- Bridge files: 14.
- Unique bridge IDs: 10.
- Duplicated IDs: `BRIDGE-001` through `BRIDGE-004`.
- Schema families: 2.
- Family A: 9 files with fields directly at the YAML top level.
- Family B: 5 files wrapped by `concept_node`.
- Indexed files: 5.
- Unindexed files: 9.
- Dangling index entries: 0.
- Explicit missing references: 0.
- Unresolved references: 14.
- Root cause: every legacy bridge lacks explicit node-reference fields.

The absence of an explicit missing reference does not prove endpoint validity. All 14 legacy bridges remain unresolved until a separate migration stage establishes canonical endpoints.

## 3. Canonical ID Rule

- New canonical bridge IDs start at `BRIDGE-015`.
- `BRIDGE-001` through `BRIDGE-014` are reserved and must not be reused.
- IDs use uppercase `BRIDGE-` followed by a zero-padded numeric component of at least three digits.
- The filename must equal `<bridge_id>.yaml`; for example, `BRIDGE-015.yaml`.
- Existing duplicate IDs are not deleted or renamed during P2.
- A later canonical replacement records its legacy relationship through `migration_notes`.
- Schema migration is a separate stage and must not be mixed into P2.

## 4. Canonical Top-Level Schema

Canonical schema version `1.0` contains exactly 16 top-level fields:

```yaml
schema_version: "1.0"
bridge_id: "BRIDGE-015"
title: "<canonical bridge title>"
bridge_type: "intra_layer"
source_level: 4
target_level: 4
from_nodes: []
to_nodes: []
mode: "A"
conceptual_connection: "<formal mathematical connection>"
teaching_use: {}
learned_history_rule: {}
prerequisite_status: "unresolved"
validation_status: "pending"
index_status: "unindexed"
migration_notes: {}
```

Rules:

- `schema_version` must be the string `"1.0"`.
- `concept_node` wrapping is forbidden for new bridges.
- All 16 fields are required and must appear directly at the YAML top level.
- Unknown top-level fields are forbidden under schema version `1.0`.
- `from_nodes` and `to_nodes` must both be explicit, non-empty lists of reference objects.
- Natural-language-only and ambiguous references are invalid.

## 5. Field Definitions

| Field | Purpose | Required | Coordinator use | Validator check |
|---|---|---:|---|---|
| `schema_version` | Selects the canonical contract. | yes | Chooses the parser and consumption rules. | Must equal string `"1.0"`. |
| `bridge_id` | Provides globally unique bridge identity. | yes | Displays and deduplicates the bridge slot. | Must match `BRIDGE-<number>`, be at least 015, be unique, and match the filename. |
| `title` | Gives the human-readable connection name. | yes | Displays the bridge on first use. | Must be a non-empty string. |
| `bridge_type` | Declares the edge's teaching and graph role. | yes | Selects backtracking, association, or outlook behavior. | Must be an allowed value and satisfy its level constraints. |
| `source_level` | Declares the level containing all source endpoints. | yes | Supports routing and level-aware loading. | Integer 1-6; must match every source reference. |
| `target_level` | Declares the level containing all target endpoints. | yes | Supports routing and level-aware loading. | Integer 1-6; must match every target reference. |
| `from_nodes` | Lists explicit source endpoint objects. | yes | Locates bridges from a current or learned node. | Non-empty object list; each reference must satisfy Section 6. |
| `to_nodes` | Lists explicit target endpoint objects. | yes | Locates target, prerequisite, or outlook endpoints. | Non-empty object list; each reference must satisfy Section 6. |
| `mode` | Selects Mode A, Mode B, or mixed teaching/validation. | yes | Chooses the intuition model and audit lane. | Must be `A`, `B`, or `mixed`; teaching contract must agree. |
| `conceptual_connection` | States the precise mathematical relationship. | yes | Supplies the one-sentence logical connection and formal explanation. | Must be non-empty and cannot rely on metaphor alone. |
| `teaching_use` | Defines lesson insertion, intuition mapping, boundary, and comprehension check. | yes | Drives bridge-slot teaching behavior. | Must satisfy the structure and mode conditions in Section 9. |
| `learned_history_rule` | Defines mastery evidence and fallback order. | yes | Decides formal content, teaser, or hidden behavior. | Must satisfy Section 10; ID comparison cannot imply mastery. |
| `prerequisite_status` | Records static prerequisite review status. | yes | Gates formal teaching. | Must be an allowed state; only `verified` can enter formal teaching. |
| `validation_status` | Records mode-specific audit outcome. | yes | Gates bridge consumption. | Must be an allowed state and agree with `mode`. |
| `index_status` | Records registry availability. | yes | Prevents unregistered bridge loading. | Must be `indexed` or `unindexed`; only `indexed` is formally consumable. |
| `migration_notes` | Records legacy sources, replacements, and migration context. | yes | Exposes provenance without loading legacy records. | Must contain `legacy_sources`, `replaces`, and `notes`. |

`source_level` and `target_level` are scalar by design. If a proposed edge requires source or target endpoints from multiple levels, split it into separate bridge records rather than weakening level validation.

## 6. Node Reference Rule

`from_nodes` and `to_nodes` use explicit objects, never bare strings:

```yaml
from_nodes:
  - node_id: "n_000"
    file: "DOMAIN-000.yaml"
    title: "<node title>"
    status: "present"

to_nodes:
  - node_id: "n_000"
    file: "DOMAIN-000.yaml"
    title: "<node title>"
    status: "present"
```

`status` allows only:

- `present`: the file exists and resolves to the declared global node identity.
- `missing`: the expected node does not exist.
- `deferred`: the node is planned but intentionally not generated yet.
- `unknown`: the reference cannot be resolved reliably.

Validation rules:

- `node_id` must use the global `n_<integer>` form.
- `file` must be an exact YAML basename in `Pure_Math_Intuition_DB/` when status is `present`.
- Existing node files may use domain-qualified internal IDs such as `COMPLEX_ANALYSIS-418`. Matching means that the internal ID or authoritative roadmap identity resolves to the same global numeric identity as `n_418`; literal string equality is not required.
- The reference title must be non-empty and agree with the referenced concept.
- The node's roadmap level must agree with `source_level` or `target_level`.
- `missing`, `deferred`, and `unknown` references cannot enter formal teaching.
- Natural-language-only references and ambiguous inferred endpoints are invalid.

## 7. Allowed `bridge_type` Values

- `intra_layer`: horizontal connection between concepts in the same level. `source_level` must equal `target_level`.
- `cross_layer`: vertical structural connection between different levels. `source_level` must differ from `target_level`.
- `prerequisite_bridge`: backtracks to knowledge required for the target lesson. Formal use requires verified prerequisite and learned-history status.
- `forward_outlook_bridge`: points to a next or future concept. It may provide only a teaser when the future node is unlearned and cannot replace formal teaching.

`prerequisite_bridge` and `forward_outlook_bridge` describe teaching direction and may be same-level or cross-level. Their level relationship is declared by `source_level` and `target_level` rather than inferred from the type name.

## 8. Allowed `mode` Values

- `A`: Computable Algebra Lane. Uses low-friction everyday physical intuition and computational audit.
- `B`: Pure Structure Lane. Uses an LLM-architecture mapping and semantic audit. Everyday physical metaphor is forbidden as the primary mapping.
- `mixed`: crosses Mode A and Mode B, or explicitly carries a student from computable intuition into pure structural reasoning.

Mixed-mode rules:

- `mixed` is not a fallback for an uncertain A/B decision.
- It is valid when Mode A endpoints connect to Mode B endpoints, when the direction is reversed, or when the bridge's explicit teaching purpose is a computable-to-structural transition.
- It must use `mixed_transition` and provide a concrete, non-empty `mode_transition`.
- Its validation must test both lane-specific evidence and the accuracy of the transition explanation.

## 9. Teaching Use Contract

```yaml
teaching_use:
  association_slot: "<lesson insertion point>"
  formal_link: "<definition or theorem connection>"
  intuition_mapping:
    kind: "everyday_physical | llm_architecture | mixed_transition"
    content: "<mapping used in teaching>"
    limitation: "<where the analogy stops being valid>"
  forcing_question: "<one comprehension-check question>"
  mode_transition: null
```

Rules:

- Every nested field shown above is required.
- Mode A requires `kind: everyday_physical` and `mode_transition: null`.
- Mode B requires `kind: llm_architecture` and `mode_transition: null`.
- Mixed mode requires `kind: mixed_transition` and a specific, non-empty `mode_transition`.
- `association_slot` identifies where the bridge appears in the target lesson.
- `formal_link` identifies the definition, theorem, representation, or proof step supported by the bridge.
- `limitation` must state the analogy boundary.
- `forcing_question` must contain exactly one compact understanding-check question.

## 10. Learned History Rule

```yaml
learned_history_rule:
  required_nodes:
    - "n_000"
  evidence_priority:
    - "classroom_passed_after_exam_agent"
    - "spaced_review_state"
    - "registered_learned_state"
  fallback: "strict_sequence_node_id_comparison"
  node_id_comparison_implies_mastery: false
  when_satisfied: "formal_teaching_content"
  when_unsatisfied: "teaser_only_or_hidden"
```

Evidence order is fixed:

1. Actual classroom pass after the Exam Agent trap.
2. Persisted spaced-review state.
3. Registered learned state.
4. As a final fallback only, node-ID comparison in an explicitly strict sequential course.

A smaller node number cannot prove mastery. `node_id_comparison_implies_mastery` must always be `false` under schema version `1.0`.

## 11. State Enumerations

`prerequisite_status`:

- `verified`
- `blocked`
- `unresolved`

`validation_status`:

- `pending`
- `computational_audit_passed`
- `semantic_audit_passed`
- `mixed_audit_passed`
- `failed`
- `legacy_unresolved`

`index_status`:

- `indexed`
- `unindexed`

Formal-consumption rules:

- Mode A requires `computational_audit_passed`.
- Mode B requires `semantic_audit_passed`.
- Mixed mode requires `mixed_audit_passed`.
- `mixed_audit_passed` requires all of the following:
  1. Computational audit for every Mode A endpoint and claim.
  2. Semantic audit for every Mode B endpoint and claim.
  3. Review that the A/B transition explanation is not misleading.
  4. A concrete, non-empty `mode_transition`.
- `pending`, `failed`, and `legacy_unresolved` cannot enter formal teaching.
- `unindexed` cannot enter formal teaching.

## 12. Coordinator Consumption Contract

The Coordinator must:

1. Locate matching bridges through explicit `from_nodes` and `to_nodes` references.
2. On first use, display `bridge_id`, `title`, `from_nodes`, `to_nodes`, and `conceptual_connection` in compressed form.
3. During teaching, read `teaching_use`, `learned_history_rule`, `prerequisite_status`, and `mode`.
4. Admit a bridge to formal teaching only when:
   - every endpoint status is `present`;
   - `prerequisite_status` is `verified`;
   - `validation_status` has passed for the declared mode;
   - `index_status` is `indexed`;
   - learned-history requirements are satisfied.
5. Treat unindexed, unvalidated, unresolved, failed, or missing-endpoint bridges as audit warnings only.
6. Allow a fully validated and indexed `forward_outlook_bridge` to provide a one-sentence teaser when its present target node is not yet learned.
7. Never treat node-ID ordering as proof of mastery.

Bridge metadata is displayed once per target-node lesson. The bridge then remains an embedded association slot rather than a repeated data dump.

## 13. Validation Checklist

- [ ] `schema_version` exists and equals string `"1.0"`.
- [ ] `bridge_id` is unique, has numeric value at least 015, and matches the filename exactly.
- [ ] No `concept_node` wrapper exists.
- [ ] All 16 canonical top-level fields exist and no unknown top-level field exists.
- [ ] `bridge_type`, `mode`, and every state value are legal.
- [ ] `source_level` and `target_level` are integers from 1 through 6.
- [ ] Level fields agree with every referenced node.
- [ ] Every endpoint has `node_id`, `file`, `title`, and `status`.
- [ ] Every `present` file exists and resolves to the declared global node identity.
- [ ] `missing`, `deferred`, and `unknown` endpoints are excluded from formal teaching.
- [ ] `conceptual_connection` is non-empty and mathematically meaningful.
- [ ] `teaching_use` is complete and mode-consistent.
- [ ] `learned_history_rule` is complete and cannot equate ID ordering with mastery.
- [ ] Mode B uses an LLM-architecture primary mapping.
- [ ] Mixed mode provides a specific `mode_transition`.
- [ ] Mode A, B, and mixed use computational, semantic, and mixed audit status respectively.
- [ ] `index_status: unindexed` or `validation_status: pending` prevents formal consumption.

## 14. Legacy Migration Policy

- P2 performs no migration.
- Legacy bridges are not deleted, renamed, overwritten, or selected as collision winners.
- Family A and Family B remain legacy schemas.
- Before migration, every legacy bridge is treated as `validation_status: legacy_unresolved`, regardless of current index presence.
- Canonical replacements use IDs from `BRIDGE-015` onward.
- `migration_notes` must use this structure:

```yaml
migration_notes:
  legacy_sources: []
  replaces: []
  notes: "<migration decision or explicit no-migration statement>"
```

- `legacy_sources` records source filenames.
- `replaces` records legacy bridge IDs or canonical records superseded by the new bridge.
- A replacement does not become formally consumable until canonical validation and index registration are complete.

## 15. Example Canonical Bridge YAML

The following example demonstrates schema format only. It is not an approved P3 bridge and cannot be consumed formally by the Coordinator.

```yaml
schema_version: "1.0"
bridge_id: "BRIDGE-015"
title: "复指数表示与线性 ODE 复根振荡"
bridge_type: "intra_layer"
source_level: 4
target_level: 4

from_nodes:
  - node_id: "n_418"
    file: "COMPLEX_ANALYSIS-418.yaml"
    title: "Euler公式与复平面极坐标表示"
    status: "present"

to_nodes:
  - node_id: "n_442"
    file: "ODE-442.yaml"
    title: "复特征根与阻尼振荡"
    status: "present"

mode: "A"

conceptual_connection: >-
  e^((alpha+i*omega)t) decomposes into the exponential envelope
  e^(alpha*t) and the rotation cos(omega*t)+i*sin(omega*t). The real
  part controls growth or decay, while the imaginary part controls
  oscillation frequency.

teaching_use:
  association_slot: "Activate while ODE-442 introduces complex characteristic roots."
  formal_link: "Connect Euler's formula to the complex-root solution of a linear ODE."
  intuition_mapping:
    kind: "everyday_physical"
    content: "A rotating motion combined with exponential damping produces a damped oscillation."
    limitation: "This model explains the decomposition of the solution but does not replace the characteristic-equation derivation."
  forcing_question: "Which parts of alpha+i*omega control damping and oscillation?"
  mode_transition: null

learned_history_rule:
  required_nodes:
    - "n_418"
  evidence_priority:
    - "classroom_passed_after_exam_agent"
    - "spaced_review_state"
    - "registered_learned_state"
  fallback: "strict_sequence_node_id_comparison"
  node_id_comparison_implies_mastery: false
  when_satisfied: "formal_teaching_content"
  when_unsatisfied: "teaser_only_or_hidden"

prerequisite_status: "unresolved"
validation_status: "pending"
index_status: "unindexed"

migration_notes:
  legacy_sources: []
  replaces: []
  notes: "Schema example only; mathematical bridge requires P3 review."
```

Both endpoints belong to computable branches, so the example is Mode A. It must not be relabeled as mixed merely to demonstrate that enum value.

## 16. Next Stage Recommendation

The next stage is **P2 Review**. After review approval:

1. Enter **P2.5** and commit only `BRIDGE_SCHEMA.md`.
2. Enter **P2.7 Knowledge Node Quality Audit**.
3. Begin P3 bridge design only after the P2.7 quality decision.

P2-B does not generate bridge YAML, migrate legacy records, update the index, modify knowledge nodes, commit, push, or merge branches.
