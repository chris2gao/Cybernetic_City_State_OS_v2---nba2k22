# Math Mentor Node Quality Audit Sample Pack

## 1. Purpose

This file is the P2.7-B sampling evidence pack. It is not a final node-quality judgment.

It provides structured evidence for the later P2.7-C review by ChatGPT 主线程 High. Codex and any subagent may extract facts and mark suspected issues, but they must not decide mathematical correctness, teaching readiness, regeneration scope, or whether P3 should begin.

ChatGPT 主线程 High performs the final review and judgment. Codex Extra High may be used for deep auxiliary analysis but does not make the final decision. A subagent is limited to Extractor or Auditor work.

## 2. Sampling Method

The sample uses stratified, evidence-seeking selection across routing mode, roadmap level, schema family, and audit style.

- One sample may satisfy multiple coverage categories.
- Every required category has at least two matching samples.
- Roadmap levels are verified against the split level roadmap files, not `数学知识路线图_全部.yaml`.
- Mode is taken from explicit routing rules in `Universal_Layer_Execution_Protocol.md` when those rules identify the domain. When the routing table does not identify the node clearly, the value is `unknown`.
- Missing fields are recorded as `missing`; information that cannot be resolved is recorded as `unknown`.
- No missing content is reconstructed from likely intent.
- Inferred concerns are recorded only as suspected issues or preliminary observations, never as verified mathematical conclusions.
- The sample is intentionally small and cannot establish a database-wide failure rate.

The selected files are read-only evidence. No node, evaluator, bridge, index, or roadmap file is changed by this stage.

## 3. Coverage Matrix

| Category | Sample 1 | Sample 2 | Notes |
| -------- | -------- | -------- | ----- |
| Mode A nodes | `COMPLEX_ANALYSIS-418.yaml` | `PDE-487.yaml` | Both domains are explicitly routed to Mode A. |
| Mode B nodes | `ZFC-001.yaml` | `ABSTRACT_ALGEBRA-468.yaml` | ZFC and abstract field/ring structure are explicitly routed to Mode B. |
| Level 4 nodes | `COMPLEX_ANALYSIS-418.yaml` | `ABSTRACT_ALGEBRA-468.yaml` | `n_418` and `n_468` occur in the Level 4 split roadmap. |
| Level 5 nodes | `PDE-487.yaml` | `COMBINATORICS-577.yaml` | `n_487` and `n_577` occur in the Level 5 split roadmap. |
| Level 6 nodes | `ALG_TOPOLOGY-676.yaml` | `ALGEBRAIC_GEO-632.yaml` | `n_676` and `n_632` occur in the Level 6 split roadmap. |
| `concept_node` schema nodes | `CARDINALS-001.yaml` | `ZFC-001.yaml` | Both wrap node fields under `concept_node`. |
| top-level schema nodes | `COMPLEX_ANALYSIS-418.yaml` | `PDE-487.yaml` | Both place node fields at the YAML top level. |
| nodes with `v8_sanity_audit` | `COMPLEX_ANALYSIS-418.yaml` | `PDE-487.yaml` | Both contain executable SymPy assertions. |
| nodes with `v9_semantic_audit` | `CARDINALS-001.yaml` | `ZFC-001.yaml` | Both use the current semantic-only evaluator path. |
| suspected shape-only audit nodes | `COMBINATORICS-577.yaml` | `LINEAR_ALGEBRA-328.yaml` | Assertions are limited to container cardinality/shape, with an additional tautological assertion in the combinatorics sample. |
| suspected LLM architecture mapping nodes | `CARDINALS-001.yaml` | `ZFC-001.yaml` | Both explicitly map the concept to tensor or computation-graph architecture. |

## 4. Evaluator Capability Summary

The current evaluator is better described as an **executable sanity checker** than a mathematical soundness validator.

- `sandbox_evaluator.py` can parse YAML with top-level or `concept_node` schema.
- It can compile and execute `code_implementation`.
- It can compile and execute `v8_sanity_audit.sympy_pseudo_code`.
- It reports syntax errors, runtime errors, and `AssertionError` failures.
- A non-empty `v9_semantic_audit` can return `Passed semantic-only audit` without evaluating the semantic claims.
- A missing optional implementation dependency can be reported as a successful skip, so that result does not prove execution or mathematics.
- Shape, length, type, or successful-construction checks do not by themselves verify the stated mathematical property.
- `bulk_evaluator.py` aggregates subprocess exit codes but does not inspect whether an assertion is deep, relevant, or complete.
- The bulk message `Entire graph is mathematically sound` is an overclaim risk because the underlying checks do not establish that claim.

## 5. Sample Records

### Sample 1 - `Pure_Math_Intuition_DB/CARDINALS-001.yaml`

```yaml
file_path: "08_Domain_Applications/Math_Mentor/Pure_Math_Intuition_DB/CARDINALS-001.yaml"
id: "CARDINALS-001"
title_or_name: "基数与序数 - 集合的等势 (Equinumerosity) (n_21)"
domain: "Set_Theory"
detected_level: 1
detected_mode: unknown
schema_family: concept_node
sub_topics_count: 4
has_formal_definition: no
has_prerequisite_nodes: no
has_llm_physical_mapping: yes
has_code_implementation: yes
has_v8_sanity_audit: no
has_v9_semantic_audit: yes
audit_type: semantic_only
suspicious_issues:
  - missing_formal_definition
  - code_not_testing_stated_concept
  - missing_mapping_boundary
  - evaluator_overclaim
preliminary_teaching_readiness_note: "The roadmap confirms n_21 at Level 1. The tensor reshape example supplies an architecture anchor for finite tensors, while the node does not state the boundary between finite tensor element counts and general cardinal equivalence. Routing remains unknown because the protocol names countability exceptions but does not explicitly classify this exact equinumerosity node."
```

### Sample 2 - `Pure_Math_Intuition_DB/ZFC-001.yaml`

```yaml
file_path: "08_Domain_Applications/Math_Mentor/Pure_Math_Intuition_DB/ZFC-001.yaml"
id: "ZFC-001"
title_or_name: "朴素集合论的危机 (The Crisis of Naive Set Theory)"
domain: "axiomatic_set_theory"
detected_level: 1
detected_mode: B
schema_family: concept_node
sub_topics_count: 4
has_formal_definition: no
has_prerequisite_nodes: no
has_llm_physical_mapping: yes
has_code_implementation: yes
has_v8_sanity_audit: no
has_v9_semantic_audit: yes
audit_type: semantic_only
suspicious_issues:
  - missing_formal_definition
  - missing_prerequisites
  - code_not_testing_stated_concept
  - misleading_mapping
  - missing_mapping_boundary
  - evaluator_overclaim
preliminary_teaching_readiness_note: "The title matches the Level 1 roadmap topic n_33, and ZFC is explicitly routed to Mode B. The computation-graph cycle analogy is concrete, but the record does not delimit the roles of unrestricted comprehension, separation, and regularity; that relationship requires main-thread mathematical review."
```

### Sample 3 - `Pure_Math_Intuition_DB/COMPLEX_ANALYSIS-418.yaml`

```yaml
file_path: "08_Domain_Applications/Math_Mentor/Pure_Math_Intuition_DB/COMPLEX_ANALYSIS-418.yaml"
id: "COMPLEX_ANALYSIS-418"
title_or_name: "复数与复平面 - 欧拉公式 (e^iθ = cosθ + i sinθ) 与复平面的极坐标表示 (n_418)"
domain: missing
detected_level: 4
detected_mode: A
schema_family: top_level
sub_topics_count: 4
has_formal_definition: no
has_prerequisite_nodes: no
has_llm_physical_mapping: yes
has_code_implementation: yes
has_v8_sanity_audit: yes
has_v9_semantic_audit: no
audit_type: symbolic_property_check
suspicious_issues:
  - schema_gap
  - missing_formal_definition
  - evaluator_overclaim
preliminary_teaching_readiness_note: "The split roadmap confirms Level 4 and the protocol routes complex-analysis calculations to Mode A. The SymPy assertion checks Euler's identity symbolically, but the YAML has no explicit domain or formal-definition field."
```

### Sample 4 - `Pure_Math_Intuition_DB/ABSTRACT_ALGEBRA-468.yaml`

```yaml
file_path: "08_Domain_Applications/Math_Mentor/Pure_Math_Intuition_DB/ABSTRACT_ALGEBRA-468.yaml"
id: "ABSTRACT_ALGEBRA-468"
title_or_name: "域与域扩张 - 通过添加方程虚根（如 i）不断扩大数系物理版图的扩张理论 (n_468)"
domain: missing
detected_level: 4
detected_mode: B
schema_family: top_level
sub_topics_count: 4
has_formal_definition: no
has_prerequisite_nodes: no
has_llm_physical_mapping: yes
has_code_implementation: yes
has_v8_sanity_audit: yes
has_v9_semantic_audit: no
audit_type: algebraic_property_check
suspicious_issues:
  - schema_gap
  - missing_formal_definition
  - missing_prerequisites
  - shallow_sanity_audit
  - code_not_testing_stated_concept
  - missing_mapping_boundary
  - daily_metaphor_in_mode_b
  - mode_mismatch
  - evaluator_overclaim
preliminary_teaching_readiness_note: "The split roadmap confirms Level 4, and abstract field structure is routed to Mode B. The node instead uses a telescoping-pipe metaphor and a v8 root check. That check covers one algebraic example but not the stated splitting-field, algebraic/transcendental, or extension-degree scope."
```

### Sample 5 - `Pure_Math_Intuition_DB/PDE-487.yaml`

```yaml
file_path: "08_Domain_Applications/Math_Mentor/Pure_Math_Intuition_DB/PDE-487.yaml"
id: "PDE-487"
title_or_name: "Fourier方法 - 大模型映射：将空间域微分转化为频域代数乘法，傅里叶神经算子 (FNO) 的数学底座 (n_487)"
domain: missing
detected_level: 5
detected_mode: A
schema_family: top_level
sub_topics_count: 4
has_formal_definition: no
has_prerequisite_nodes: no
has_llm_physical_mapping: yes
has_code_implementation: yes
has_v8_sanity_audit: yes
has_v9_semantic_audit: no
audit_type: symbolic_property_check
suspicious_issues:
  - schema_gap
  - missing_formal_definition
  - shallow_sanity_audit
  - evaluator_overclaim
preliminary_teaching_readiness_note: "The split roadmap confirms Level 5 and the protocol routes PDE to Mode A. The audit checks the Fourier derivative identity for one symbolic function, while the broader FNO, global-receptive-field, and operator-learning subtopics are not represented in the assertion."
```

### Sample 6 - `Pure_Math_Intuition_DB/COMBINATORICS-577.yaml`

```yaml
file_path: "08_Domain_Applications/Math_Mentor/Pure_Math_Intuition_DB/COMBINATORICS-577.yaml"
id: "COMBINATORICS-577"
title_or_name: "排列组合 - 核心直觉：离散状态集合的内存精确测算。 (n_577)"
domain: missing
detected_level: 5
detected_mode: unknown
schema_family: top_level
sub_topics_count: 4
has_formal_definition: no
has_prerequisite_nodes: no
has_llm_physical_mapping: yes
has_code_implementation: yes
has_v8_sanity_audit: yes
has_v9_semantic_audit: no
audit_type: shape_check
suspicious_issues:
  - schema_gap
  - missing_formal_definition
  - shallow_sanity_audit
  - shape_only_test
  - code_not_testing_stated_concept
  - evaluator_overclaim
preliminary_teaching_readiness_note: "The split roadmap confirms Level 5. The audit checks only that one three-element example produces three two-element combinations and then executes `assert True`; repeated arrangements, multiset behavior, search growth, and non-redundancy are not tested. The protocol does not explicitly route combinatorics, so mode is recorded as unknown."
```

### Sample 7 - `Pure_Math_Intuition_DB/ALG_TOPOLOGY-676.yaml`

```yaml
file_path: "08_Domain_Applications/Math_Mentor/Pure_Math_Intuition_DB/ALG_TOPOLOGY-676.yaml"
id: "ALG_TOPOLOGY-676"
title_or_name: "纤维丛 - 【核心 AI 映射】：多头注意力机制中词向量（底空间）与特征子空间（纤维）结合的终极解构。揭示权重在不同维度演化时的几何缠绕。 (n_676)"
domain: missing
detected_level: 6
detected_mode: B
schema_family: top_level
sub_topics_count: 4
has_formal_definition: no
has_prerequisite_nodes: no
has_llm_physical_mapping: yes
has_code_implementation: yes
has_v8_sanity_audit: yes
has_v9_semantic_audit: no
audit_type: symbolic_property_check
suspicious_issues:
  - schema_gap
  - missing_formal_definition
  - missing_prerequisites
  - shallow_sanity_audit
  - code_not_testing_stated_concept
  - missing_mapping_boundary
  - daily_metaphor_in_mode_b
  - mode_mismatch
  - evaluator_overclaim
preliminary_teaching_readiness_note: "The split roadmap confirms Level 6 and algebraic topology is explicitly routed to Mode B. Although the title invokes attention, the primary mapping is a weaving loom, the v8 assertion reduces to scalar multiplication/division, and no local-triviality or transition-function property is checked."
```

### Sample 8 - `Pure_Math_Intuition_DB/ALGEBRAIC_GEO-632.yaml`

```yaml
file_path: "08_Domain_Applications/Math_Mentor/Pure_Math_Intuition_DB/ALGEBRAIC_GEO-632.yaml"
id: "ALGEBRAIC_GEO-632"
title_or_name: "仿射/射影簇 - 物理直觉：仿射簇即多元多项式方程公共解在多维空间中切出的骨架。射影簇通过引入“无穷远地平线”消除平行线不相交特例，实现几何规律的完美对称。 (n_632)"
domain: missing
detected_level: 6
detected_mode: B
schema_family: top_level
sub_topics_count: 4
has_formal_definition: no
has_prerequisite_nodes: no
has_llm_physical_mapping: yes
has_code_implementation: yes
has_v8_sanity_audit: yes
has_v9_semantic_audit: no
audit_type: algebraic_property_check
suspicious_issues:
  - schema_gap
  - missing_formal_definition
  - missing_prerequisites
  - shallow_sanity_audit
  - code_not_testing_stated_concept
  - missing_mapping_boundary
  - daily_metaphor_in_mode_b
  - mode_mismatch
  - evaluator_overclaim
preliminary_teaching_readiness_note: "The split roadmap confirms Level 6 and algebraic geometry is explicitly routed to Mode B. The record uses a factory/laser/conveyor metaphor and v8 point substitution. The check shows one point satisfies two equations but does not audit projective space, ideals, dimension, singularities, or mapping boundaries."
```

### Sample 9 - `Pure_Math_Intuition_DB/LINEAR_ALGEBRA-328.yaml`

```yaml
file_path: "08_Domain_Applications/Math_Mentor/Pure_Math_Intuition_DB/LINEAR_ALGEBRA-328.yaml"
id: "LINEAR_ALGEBRA-328"
title_or_name: "张量初步 - 发生学溯源：起源于物理应力分析，将向量转化的‘物理机器’ (n_328)"
domain: missing
detected_level: 3
detected_mode: A
schema_family: top_level
sub_topics_count: 4
has_formal_definition: no
has_prerequisite_nodes: no
has_llm_physical_mapping: yes
has_code_implementation: yes
has_v8_sanity_audit: yes
has_v9_semantic_audit: no
audit_type: shape_check
suspicious_issues:
  - schema_gap
  - missing_formal_definition
  - shallow_sanity_audit
  - shape_only_test
  - code_not_testing_stated_concept
  - evaluator_overclaim
preliminary_teaching_readiness_note: "The split roadmap confirms Level 3 and the default L1-L3 route is Mode A. The assertion verifies only that one outer product has shape 2x2; it does not test multilinearity, tensor order, coordinate transformation, or the stated stress-tensor interpretation."
```

## 6. Suspected Issues Summary

Counts below aggregate provisional labels in the nine sample records. They are not database-wide rates or final findings.

| Issue Type | Count | Sample Files | Notes |
| ---------- | ----: | ------------ | ----- |
| `schema_gap` | 7 | `COMPLEX_ANALYSIS-418`, `ABSTRACT_ALGEBRA-468`, `PDE-487`, `COMBINATORICS-577`, `ALG_TOPOLOGY-676`, `ALGEBRAIC_GEO-632`, `LINEAR_ALGEBRA-328` | These top-level samples omit an explicit `domain` field. |
| `missing_formal_definition` | 9 | all samples | No selected record contains a field explicitly serving as a formal definition, axiom skeleton, or theorem skeleton. |
| `missing_prerequisites` | 4 | `ZFC-001`, `ABSTRACT_ALGEBRA-468`, `ALG_TOPOLOGY-676`, `ALGEBRAIC_GEO-632` | These explicitly routed Mode B samples have no `prerequisite_nodes` field. |
| `shallow_sanity_audit` | 6 | `ABSTRACT_ALGEBRA-468`, `PDE-487`, `COMBINATORICS-577`, `ALG_TOPOLOGY-676`, `ALGEBRAIC_GEO-632`, `LINEAR_ALGEBRA-328` | The assertions cover only a narrow example or a small subset of the stated concept. |
| `shape_only_test` | 2 | `COMBINATORICS-577`, `LINEAR_ALGEBRA-328` | Checks are limited to result count/shape; the combinatorics audit also contains `assert True`. |
| `code_not_testing_stated_concept` | 7 | `CARDINALS-001`, `ZFC-001`, `ABSTRACT_ALGEBRA-468`, `COMBINATORICS-577`, `ALG_TOPOLOGY-676`, `ALGEBRAIC_GEO-632`, `LINEAR_ALGEBRA-328` | Code or audit evidence does not cover the full concept named by the record. |
| `misleading_mapping` | 1 | `ZFC-001` | The mapping's treatment of computation-graph cycles, regularity, and the naive-set-theory crisis requires mathematical review. |
| `missing_mapping_boundary` | 5 | `CARDINALS-001`, `ZFC-001`, `ABSTRACT_ALGEBRA-468`, `ALG_TOPOLOGY-676`, `ALGEBRAIC_GEO-632` | The mapping does not state where the analogy stops. |
| `daily_metaphor_in_mode_b` | 3 | `ABSTRACT_ALGEBRA-468`, `ALG_TOPOLOGY-676`, `ALGEBRAIC_GEO-632` | Explicit Mode B domains use pipes, a loom, or factory machinery as the primary mapping. |
| `mode_mismatch` | 3 | `ABSTRACT_ALGEBRA-468`, `ALG_TOPOLOGY-676`, `ALGEBRAIC_GEO-632` | Protocol-routed Mode B records use Mode A-style everyday mappings and v8 audits. |
| `missing_teaching_usefulness` | 0 | none | The sample does not establish this issue; Coordinator usefulness still requires review. |
| `evaluator_overclaim` | 9 | all samples | A successful process exit could contribute to the graph-wide soundness claim even though the evaluator does not establish that claim. |
| `regeneration_required` | 0 | none | Regeneration is outside P2.7-B and has not been decided. |

## 7. Initial Observations Without Final Judgment

These observations describe this sample only and are not final quality judgments.

- Both selected v9 records can pass the current evaluator through field presence alone; their semantic claims are not machine-evaluated.
- The two suspected shape-only records demonstrate that executable assertions can be structurally valid while covering little of the stated concept.
- All nine selected records lack an explicit formal-definition field. This warrants broader sampling before any database-wide conclusion.
- The three sampled Level 4/6 Mode B records use everyday mechanical mappings and v8 assertions despite the current Mode B protocol.
- The sampled Mode B mappings generally omit explicit analogy boundaries and prerequisite references.
- The strongest sampled v8 checks are symbolic identities or point/property checks, but even these do not establish complete `sub_topics` coverage or teaching readiness.
- Current evaluator output cannot assess definition accuracy, mapping boundaries, prerequisite validity, metaphor risk, or Coordinator consumption quality.

P2.7-C must distinguish schema-era drift from mathematical-content defects. No repair, regeneration, or P3 decision follows automatically from this evidence pack.

## 8. Next Stage Recommendation

The next stage is **P2.7-C Node Quality Review**.

- ChatGPT 主线程 High performs the final judgment.
- Codex Extra High may provide deep auxiliary analysis but does not make the final judgment.
- Subagents remain limited to Extractor or Auditor roles.

P2.7-C must decide whether to:

- continue to P3;
- first enter P2.8 for evaluator wording or quality-gate upgrades;
- perform targeted field, mapping, or audit repair;
- regenerate individual nodes;
- consider level- or domain-specific regeneration;
- defer bridge generation pending stronger evidence.

P3 bridge design must not begin until the P2.7 quality decision is complete.
