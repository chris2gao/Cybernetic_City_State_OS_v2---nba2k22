# Bridge Registry Audit

## 1. Audit Scope

This audit covers the existing `BRIDGE-*.yaml` files in `Pure_Math_Intuition_DB/` and their registration in `知识图谱_节点映射索引.md`.

This stage is audit-only. It does not generate bridge nodes, modify existing YAML, rename or delete files, update the index, merge branches, or push commits. Mathematical endpoint relationships are not inferred from filenames, titles, metaphors, or prose when explicit node-reference fields are absent.

## 2. Current Summary

| metric | count | notes |
|---|---:|---|
| Bridge files | 14 | All 14 contain a detectable `id` field; none is `missing_id_field`. |
| Unique bridge IDs | 10 | `BRIDGE-001` through `BRIDGE-010`. |
| Duplicate IDs | 4 | `BRIDGE-001` through `BRIDGE-004`; eight files are affected. |
| Schema families | 2 | `schema_family_A` and `schema_family_B`; no unknown schema. |
| Indexed files | 5 | All five are `schema_family_B` files. |
| Unindexed files | 9 | All nine are `schema_family_A` files. |
| Index entries without a file | 0 | No dangling bridge filename was found in the index. |
| Bridges with missing node references | 0 | No explicit node reference was available to resolve as missing. |
| Bridges with unresolved references | 14 | Every file lacks explicit endpoint/reference fields, `n_XXX` references, and YAML filename references. |

`missing reference = 0` does not establish that the conceptual endpoints are valid. It means there is no explicit reference that can be tested. All 14 records therefore remain `unresolved_reference`.

## 3. Bridge File Inventory

| file | detected_id | schema_family | indexed | reference_status | notes |
|---|---|---|---|---|---|
| `BRIDGE-001.yaml` | `BRIDGE-001` | `schema_family_A` | no | unresolved | Duplicate ID; schema lacks explicit node reference fields. |
| `BRIDGE-001_Logic_and_Sets.yaml` | `BRIDGE-001` | `schema_family_B` | yes | unresolved | Duplicate ID; schema lacks explicit node reference fields. |
| `BRIDGE-002.yaml` | `BRIDGE-002` | `schema_family_A` | no | unresolved | Duplicate ID; schema lacks explicit node reference fields. |
| `BRIDGE-002_Relations_and_Posets.yaml` | `BRIDGE-002` | `schema_family_B` | yes | unresolved | Duplicate ID; schema lacks explicit node reference fields. |
| `BRIDGE-003.yaml` | `BRIDGE-003` | `schema_family_A` | no | unresolved | Duplicate ID; schema lacks explicit node reference fields. |
| `BRIDGE-003_Functions_and_Cardinality.yaml` | `BRIDGE-003` | `schema_family_B` | yes | unresolved | Duplicate ID; schema lacks explicit node reference fields. |
| `BRIDGE-004.yaml` | `BRIDGE-004` | `schema_family_A` | no | unresolved | Duplicate ID; schema lacks explicit node reference fields. |
| `BRIDGE-004_Russell_and_ZFC.yaml` | `BRIDGE-004` | `schema_family_B` | yes | unresolved | Duplicate ID; schema lacks explicit node reference fields. |
| `BRIDGE-005_Godel_and_Diagonalization.yaml` | `BRIDGE-005` | `schema_family_B` | yes | unresolved | Unique ID; schema lacks explicit node reference fields. |
| `BRIDGE-006.yaml` | `BRIDGE-006` | `schema_family_A` | no | unresolved | Unique ID; schema lacks explicit node reference fields. |
| `BRIDGE-007.yaml` | `BRIDGE-007` | `schema_family_A` | no | unresolved | Unique ID; schema lacks explicit node reference fields. |
| `BRIDGE-008.yaml` | `BRIDGE-008` | `schema_family_A` | no | unresolved | Unique ID; schema lacks explicit node reference fields. |
| `BRIDGE-009.yaml` | `BRIDGE-009` | `schema_family_A` | no | unresolved | Unique ID; schema lacks explicit node reference fields. |
| `BRIDGE-010.yaml` | `BRIDGE-010` | `schema_family_A` | no | unresolved | Unique ID; schema lacks explicit node reference fields. |

## 4. Duplicate ID Findings

| duplicate_id | files |
|---|---|
| `BRIDGE-001` | `BRIDGE-001.yaml`; `BRIDGE-001_Logic_and_Sets.yaml` |
| `BRIDGE-002` | `BRIDGE-002.yaml`; `BRIDGE-002_Relations_and_Posets.yaml` |
| `BRIDGE-003` | `BRIDGE-003.yaml`; `BRIDGE-003_Functions_and_Cardinality.yaml` |
| `BRIDGE-004` | `BRIDGE-004.yaml`; `BRIDGE-004_Russell_and_ZFC.yaml` |

These are content-level ID collisions, not merely similar filenames. In each pair, the plain filename uses `schema_family_A`, while the descriptive filename uses `schema_family_B`. No precedence or migration winner can be established from the registry evidence alone.

## 5. Schema Family Findings

### Family Definitions

- `schema_family_A` (9 files): bridge fields are direct top-level keys.
  - Top-level keys: `id`, `concept_name`, `sub_topics`, `llm_physical_mapping`, `code_implementation`, `v8_sanity_audit`.
- `schema_family_B` (5 files): the only top-level key is `concept_node`.
  - Nested keys: `id`, `name` or `title`, `domain`, `sub_topics`, `llm_physical_mapping`, `code_implementation`, `v8_sanity_audit`.
  - The nested display-name field is itself inconsistent: three files use `name`; two use `title`.

### Per-File Top-Level Keys

| file | top-level keys |
|---|---|
| `BRIDGE-001.yaml` | `id`, `concept_name`, `sub_topics`, `llm_physical_mapping`, `code_implementation`, `v8_sanity_audit` |
| `BRIDGE-001_Logic_and_Sets.yaml` | `concept_node` |
| `BRIDGE-002.yaml` | `id`, `concept_name`, `sub_topics`, `llm_physical_mapping`, `code_implementation`, `v8_sanity_audit` |
| `BRIDGE-002_Relations_and_Posets.yaml` | `concept_node` |
| `BRIDGE-003.yaml` | `id`, `concept_name`, `sub_topics`, `llm_physical_mapping`, `code_implementation`, `v8_sanity_audit` |
| `BRIDGE-003_Functions_and_Cardinality.yaml` | `concept_node` |
| `BRIDGE-004.yaml` | `id`, `concept_name`, `sub_topics`, `llm_physical_mapping`, `code_implementation`, `v8_sanity_audit` |
| `BRIDGE-004_Russell_and_ZFC.yaml` | `concept_node` |
| `BRIDGE-005_Godel_and_Diagonalization.yaml` | `concept_node` |
| `BRIDGE-006.yaml` | `id`, `concept_name`, `sub_topics`, `llm_physical_mapping`, `code_implementation`, `v8_sanity_audit` |
| `BRIDGE-007.yaml` | `id`, `concept_name`, `sub_topics`, `llm_physical_mapping`, `code_implementation`, `v8_sanity_audit` |
| `BRIDGE-008.yaml` | `id`, `concept_name`, `sub_topics`, `llm_physical_mapping`, `code_implementation`, `v8_sanity_audit` |
| `BRIDGE-009.yaml` | `id`, `concept_name`, `sub_topics`, `llm_physical_mapping`, `code_implementation`, `v8_sanity_audit` |
| `BRIDGE-010.yaml` | `id`, `concept_name`, `sub_topics`, `llm_physical_mapping`, `code_implementation`, `v8_sanity_audit` |

There are no explicit `bridge_id`, `node_id`, `from_nodes`, `to_nodes`, `source_node`, `target_node`, `prerequisite_nodes`, or `related_nodes` fields in either family.

## 6. Index Registration Findings

### Indexed And Present (5)

- `BRIDGE-001_Logic_and_Sets.yaml`
- `BRIDGE-002_Relations_and_Posets.yaml`
- `BRIDGE-003_Functions_and_Cardinality.yaml`
- `BRIDGE-004_Russell_and_ZFC.yaml`
- `BRIDGE-005_Godel_and_Diagonalization.yaml`

### Present But Unindexed (9)

- `BRIDGE-001.yaml`
- `BRIDGE-002.yaml`
- `BRIDGE-003.yaml`
- `BRIDGE-004.yaml`
- `BRIDGE-006.yaml`
- `BRIDGE-007.yaml`
- `BRIDGE-008.yaml`
- `BRIDGE-009.yaml`
- `BRIDGE-010.yaml`

### Indexed But Missing From The Database (0)

None.

## 7. Missing / Unresolved Reference Findings

No bridge contains any of the requested explicit reference fields:

- `from_nodes`
- `to_nodes`
- `source_node`
- `target_node`
- `prerequisite_nodes`
- `related_nodes`

The 14 files also contain no canonical `n_XXX` reference and no YAML filename reference. Therefore:

- Bridges with verified existing endpoints: 0.
- Bridges with explicit references to missing endpoints: 0.
- Bridges with `unresolved_reference`: all 14.

Per-file result: `schema lacks explicit node reference fields`. Titles and prose may suggest conceptual domains, but they are not a registry-safe substitute for canonical node IDs.

## 8. Recommended Canonical Bridge Schema Draft

This is a review draft only. It does not select a migration winner or modify existing files.

```yaml
bridge_id: "BRIDGE-XXX"
title: "<canonical bridge title>"
bridge_type: "intra_layer | cross_layer | prerequisite_bridge | forward_outlook_bridge"
source_level: 4
target_level: 5
from_nodes:
  - "n_000"
to_nodes:
  - "n_000"
mode: "A | B | mixed"
conceptual_connection: "<formal mathematical relationship>"
teaching_use: "<association slot and comprehension-check behavior>"
learned_history_rule: "<evidence required before formal teaching>"
prerequisite_status: "verified | blocked | unresolved"
validation_status: "pending | computational_audit_passed | semantic_audit_passed | mixed_audit_passed"
index_status: "indexed | unindexed"
migration_notes: "<legacy source, collision handling, and unresolved decisions>"
```

P2 must decide whether canonical bridges remain compatible with the existing concept-node teaching fields such as `sub_topics` and `llm_physical_mapping`, and how Mode A, Mode B, and mixed validation evidence is stored. That decision requires architecture review before migration.

## 9. Next Stage Recommendation

Proceed to **P2: Canonical Bridge Schema** only after this audit is reviewed. P2 should define the canonical identity, endpoint representation, learned-history policy, validation evidence, index contract, and migration treatment for duplicate IDs. Recommended reasoning level: **Extra High**.

P2 must not infer Level 4-6 mathematical bridge candidates. Candidate design belongs to the later Extra High bridge-design stage after the schema is approved.
