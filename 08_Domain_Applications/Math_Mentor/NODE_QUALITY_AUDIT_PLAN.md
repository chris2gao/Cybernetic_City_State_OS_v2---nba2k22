# Math Mentor Node Quality Audit Plan

## 1. Purpose

P3 bridge design must not begin until the teaching readiness of the nodes in `Pure_Math_Intuition_DB` has been assessed.

- A bridge connects knowledge nodes; it cannot repair an unstable endpoint.
- If a node has an incorrect definition, incomplete `sub_topics`, a misleading mapping, or a shallow audit, building bridges first would propagate that defect through the teaching graph.
- This stage does not regenerate or repair nodes. It establishes the quality gates and sampling plan used by the later audit.
- The audit outcome determines whether the project proceeds to P3, performs local field or audit repair, upgrades the evaluator, regenerates individual nodes, or considers domain- or level-specific regeneration.

ChatGPT 主线程 High 最终裁决；Codex Extra High 可用于深度辅助分析，但不做最终裁决。ChatGPT 主线程负责最终 review / judge，且主线程最高使用 High。Subagents may only prepare evidence as Extractors or Auditors.

## 2. Current Generation Model

The current generation protocol has two lanes. Routing is determined by the domain and subdomain rules in `Universal_Layer_Execution_Protocol.md`, not by level number alone.

### Mode A - Computable Algebra Lane

Mode A is used when the concept has a meaningful computational representation and can support executable assertions.

- `sub_topics` must cover the complete teaching scope of the node.
- Everyday physical intuition is the primary low-friction mapping.
- `llm_physical_mapping` must serve the teaching objective and must not distort the mathematics.
- `code_implementation` provides an executable representation of the stated concept.
- `v8_sanity_audit.sympy_pseudo_code` provides assertions for computational validation.
- `sandbox_evaluator.py` and `bulk_evaluator.py` are the current execution paths.
- The generation target is a 100% executable pass for the applicable snippets.
- An executable pass is not proof of mathematical soundness, definition completeness, or teaching readiness.

### Mode B - Pure Structure Lane

Mode B is used for abstract structural mathematics where forced computational proof or an everyday metaphor would be misleading.

- The Cognitive Mapping Engine supplies the primary intuition model.
- `llm_physical_mapping` must map the mathematical structure to LLM architecture rather than to household, factory, fluid, or other everyday objects.
- Generation and review should consult these three architecture references when Mode B mapping evidence is required:
  - `学习期prompt/backup/大模型解剖图：深入解析.md` - present at planning time.
  - `学习期prompt/backup/大语言模型数学底层架构全阶段深度解析整合报告.md` - present at planning time.
  - `学习期prompt/backup/英语算子直觉与语义架构索引.md` - present at planning time.
- A code anchor is an intuition aid only. It must not be represented as a complete proof of the abstract result.
- `v9_semantic_audit` should evaluate semantic consistency, definition accuracy, analogy boundaries, prerequisite clarity, and misleading-mapping risk.
- Everyday physical metaphor must not be the primary Mode B mapping.
- A semantic audit must not be presented as a machine proof.

## 3. Audit Scope

This stage designs the audit. It does not perform the P2.7-B node sample extraction or make node-level quality decisions.

The stage must not:

- modify any node;
- regenerate any node;
- create or modify a bridge;
- modify `知识图谱_节点映射索引.md`;
- modify an evaluator;
- stage or commit changes;
- push changes or merge branches.

The only permitted artifact is this plan. P3 remains blocked until P2.7 produces a reviewed quality decision.

## 4. Mode A Quality Gate

A Mode A node is teaching-ready only when all applicable checks below pass or are explicitly resolved by the final reviewer.

| Gate | Required check |
| --- | --- |
| Identity | A stable `id`, a `title` or `name`, and a coherent `domain` are present. |
| Coverage | `sub_topics` is non-empty, internally coherent, and covers the concept promised by the title and definition. |
| Formal content | A correct `formal_definition` or an adequate definition skeleton is present. |
| Physical intuition | The everyday physical intuition is mathematically relevant, low-friction, and free of misleading implications. |
| Teaching mapping | `llm_physical_mapping`, when present, supports teaching and obeys Mode A gating rather than replacing the primary everyday intuition without justification. |
| Implementation | `code_implementation` is present when required, parses, runs with declared dependencies, and represents the stated concept. |
| Audit presence | `v8_sanity_audit.sympy_pseudo_code` exists for the computational lane. |
| Audit depth | Assertions test a mathematical property of the concept, not only type, shape, length, or successful execution. |
| Edge cases | Relevant degenerate, boundary, singular, empty, zero, or minimal cases are covered or explicitly declared inapplicable. |
| Strong checks | Property-based, symbolic, invariant, counterexample, or equivalent checks are used where practical. |
| Mapping safety | No metaphor creates a false mathematical rule or hides a required condition. |
| Coordinator readiness | The node can support intuition before definition, full `sub_topics` coverage, guided questioning, definition restatement, and Exam Agent handoff. |

Recommended tools for later validation are `sympy`, `numpy`, `scipy`, `hypothesis`, `z3-solver`, `networkx`, `pyyaml`, and `jsonschema`. Tool choice must follow the concept; installing a tool does not by itself satisfy a quality gate.

## 5. Mode B Quality Gate

A Mode B node is teaching-ready only when all applicable checks below pass or are explicitly resolved by the final reviewer.

| Gate | Required check |
| --- | --- |
| Identity | A stable `id`, a `title` or `name`, and a coherent `domain` are present. |
| Coverage | `sub_topics` is non-empty and covers the structural concept promised by the node. |
| Formal content | A correct formal definition, axiom skeleton, or theorem skeleton is present, as appropriate to the node. |
| Prerequisites | `prerequisite_nodes` exists where prerequisites are required, and every reference can be resolved. |
| Primary mapping | LLM architecture mapping is the primary intuition model and is materially related to the mathematical structure. |
| Mapping boundary | The node states where the LLM analogy applies, where it stops, and which mathematical properties it does not establish. |
| Semantic audit presence | `v9_semantic_audit` exists and contains reviewable criteria rather than an empty acceptance marker. |
| Semantic audit depth | The audit addresses definition accuracy, analogy boundaries, misleading risk, prerequisite dependencies, and teaching usefulness. |
| Mode integrity | An everyday physical metaphor is not used as the primary mapping. |
| Code-anchor honesty | Any code example is explicitly described as an intuition anchor or computable special case, not a proof of the full structure. |
| Coordinator readiness | The node can support LLM-architecture intuition, formal compression, full `sub_topics` coverage, guided questioning, definition restatement, and Exam Agent handoff. |

## 6. Evaluator Limitation

The current evaluator establishes executable sanity, not mathematical soundness.

### What it currently verifies

- `sandbox_evaluator.py` parses YAML and supports both top-level and `concept_node` schemas.
- It compiles and executes `code_implementation` when present.
- It compiles and executes `v8_sanity_audit.sympy_pseudo_code` when present.
- It reports syntax errors, runtime errors, and failed Python assertions, including `AssertionError`.
- `bulk_evaluator.py` invokes the sandbox evaluator for YAML files in one directory and aggregates process exit status.

### What it does not establish

- A non-empty `v9_semantic_audit` currently returns `Passed semantic-only audit` without evaluating its claims.
- An optional dependency skip can return success for `code_implementation`; that means the implementation was not executed and cannot count as mathematical validation.
- Successful execution does not show that an assertion tests the stated concept. Shape-only, type-only, and tautological assertions can pass.
- The evaluator does not judge formal-definition accuracy, analogy boundaries, prerequisite completeness, `sub_topics` completeness, mathematical completeness, or Coordinator teaching readiness.
- It does not distinguish a strong property test from a weak smoke test.

The bulk success message `Entire graph is mathematically sound` is an overclaim risk. P2.8 should consider reporting precise states such as `executable sanity passed`, `semantic audit accepted`, `skipped optional dependency`, and `not mathematically adjudicated` instead of claiming mathematical soundness.

## 7. Sampling Plan

P2.7-B will create `NODE_QUALITY_AUDIT_SAMPLE_PACK.md`. It will use stratified sampling and may reuse one node across multiple categories, but every category below must contain at least two qualifying samples:

- Mode A nodes: 2;
- Mode B nodes: 2;
- Level 4 nodes: 2;
- Level 5 nodes: 2;
- Level 6 nodes: 2;
- `concept_node` schema nodes: 2;
- top-level schema nodes: 2;
- nodes with `v8_sanity_audit`: 2;
- nodes with `v9_semantic_audit`: 2;
- suspected shape-only audit nodes: 2;
- suspected LLM architecture mapping nodes: 2.

Selection should maximize coverage across levels, domains, modes, schema families, and audit styles. Suspected cases are evidence-seeking samples, not pre-judged failures. If a category cannot supply two nodes, the sample pack must record the registry gap rather than invent a match.

Each sample record must extract:

- `file_path`;
- `id`;
- `title_or_name`;
- `domain`;
- `detected_level`;
- `detected_mode`;
- `schema_family`;
- `sub_topics_count`;
- `has_formal_definition`;
- `has_prerequisite_nodes`;
- `has_llm_physical_mapping`;
- `has_code_implementation`;
- `has_v8_sanity_audit`;
- `has_v9_semantic_audit`;
- `audit_type`;
- `suspicious_issues`;
- `preliminary_teaching_readiness_note`.

Unknown or absent values must be recorded explicitly. P2.7-B may use a subagent only as an Extractor or Auditor. A subagent must not decide mathematical correctness, final mode, regeneration scope, or teaching readiness.

ChatGPT 主线程 High 最终裁决；Codex Extra High 可用于深度辅助分析，但不做最终裁决。

## 8. Failure Classification

Each sample may receive zero, one, or multiple provisional failure codes. Codes describe evidence and do not by themselves authorize repair or regeneration.

- `schema_gap`: required structural fields are missing or inconsistent.
- `missing_formal_definition`: no adequate formal definition, axiom skeleton, or theorem skeleton is present.
- `missing_prerequisites`: required prerequisites are absent, unresolved, or too vague to validate.
- `shallow_sanity_audit`: an audit exists but does not test enough of the stated concept.
- `shape_only_test`: assertions check only shape, type, dimensions, length, or successful construction.
- `code_not_testing_stated_concept`: executable code is unrelated or insufficiently related to the mathematical claim.
- `misleading_mapping`: the intuition mapping implies a false rule or suppresses a necessary limitation.
- `missing_mapping_boundary`: a structural analogy lacks an explicit limit of applicability.
- `daily_metaphor_in_mode_b`: an everyday metaphor is used as the primary Mode B mapping.
- `mode_mismatch`: the node content and protocol routing disagree.
- `missing_teaching_usefulness`: the node cannot support the Coordinator teaching flow despite containing descriptive material.
- `evaluator_overclaim`: validation output claims more certainty than the checks establish.
- `regeneration_required`: the core mathematical content is defective enough that targeted field repair is insufficient; this code requires final-review approval.

## 9. Regeneration Decision Rule

Full-database regeneration is not the default response. Decisions proceed from the narrowest adequate remedy:

1. If only schema fields are missing, use schema migration or targeted field completion.
2. If `v8_sanity_audit` is too shallow, strengthen the tests without regenerating the whole node.
3. If `llm_physical_mapping` is misleading, regenerate or repair only the mapping and semantic audit when the underlying mathematics remains correct.
4. If the formal definition or `sub_topics` is materially incorrect, regenerate the individual node.
5. If a reviewed sample for one level or domain has a failure rate greater than 30%, consider level- or domain-specific expanded audit and regeneration. The threshold triggers consideration, not automatic regeneration.
6. Consider full-database regeneration only when reviewed evidence shows broad failure across multiple levels and both modes.
7. Full-database regeneration must be a separate approved stage. It must use small batches, strong validators, and Codex Extra High for deep auxiliary generation or analysis, while ChatGPT 主线程 High performs final review and judgment.

Any regeneration decision must preserve an evidence trail from sample finding to failure classification to selected remedy.

## 10. Recommended Docker / Python Tooling

Lightweight tools that may be considered for the P2.8 evaluator and container environment:

- `sympy`
- `numpy`
- `scipy`
- `hypothesis`
- `z3-solver`
- `networkx`
- `pyyaml`
- `jsonschema`

Heavy tools that require a separate cost, environment, and maintenance decision:

- SageMath
- Lean / Lake
- Coq
- Isabelle

No tool is installed during this stage. P2.8 will decide whether evaluator changes or Docker/Python dependency additions are justified by P2.7 evidence.

## 11. Stage Outputs and Stop Rule

The only output of this stage is `08_Domain_Applications/Math_Mentor/NODE_QUALITY_AUDIT_PLAN.md`.

After the file is written:

- stop the stage;
- do not stage or commit it;
- do not begin sample extraction;
- wait for ChatGPT main-thread review.

## 12. Next Stage Recommendation

The next stage is **P2.7-A Review**.

If review passes:

1. enter **P2.7-A Commit** and commit only this plan;
2. then enter **P2.7-B** and create `NODE_QUALITY_AUDIT_SAMPLE_PACK.md`;
3. keep P2.7-B limited to sample evidence extraction;
4. use ChatGPT 主线程 High for final quality judgment; Codex Extra High may provide deep auxiliary analysis but does not make the final judgment;
5. keep subagents limited to Extractor or Auditor roles;
6. do not begin P3 bridge design until the P2.7 quality decision is complete.
