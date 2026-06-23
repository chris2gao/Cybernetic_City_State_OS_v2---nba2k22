# Math Mentor Targeted Node Repair Plan

## 1. Current Understanding

P2.7 identified teaching-readiness risks in a stratified nine-node sample. P2.8 corrected evaluator status semantics, but it did not repair node content. P3 bridge design remains blocked because a bridge cannot make an incomplete or misrouted endpoint reliable.

This plan defines targeted repair only. It does not modify nodes, authorize P2.10, generate bridges, or approve regeneration. ChatGPT main-thread High remains the final reviewer for mathematics, mode routing, teaching readiness, and stage progression.

## 2. Evidence Base

The plan uses:

- `NODE_QUALITY_AUDIT_PLAN.md` for Mode A/B quality gates and regeneration rules;
- `NODE_QUALITY_AUDIT_SAMPLE_PACK.md` for nine sampled-node records and provisional failure labels;
- `BRIDGE_SCHEMA.md` for endpoint, prerequisite, mode, validation, and Coordinator-consumption requirements;
- `sandbox_evaluator.py` for per-node structured status semantics;
- `bulk_evaluator.py` for aggregate status semantics.

Sample evidence is not a database-wide failure rate. Its provisional counts are:

| Failure type | Sample count |
| --- | ---: |
| `missing_formal_definition` | 9 |
| `schema_gap` | 7 |
| `code_not_testing_stated_concept` | 7 |
| `shallow_sanity_audit` | 6 |
| `missing_mapping_boundary` | 5 |
| `missing_prerequisites` | 4 |
| `daily_metaphor_in_mode_b` | 3 |
| `mode_mismatch` | 3 |
| `shape_only_test` | 2 |
| `misleading_mapping` | 1 |
| `regeneration_required` | 0 |

The former `evaluator_overclaim` label is handled by P2.8 and is not a node-repair action. Current evaluator meanings are:

- `passed`: executable sanity passed; mathematical correctness is not established;
- `warning`: executable sanity passed with shallow/shape-only risk;
- `review_required`: semantic evidence exists but is not machine validated;
- `skipped`: an optional dependency or executable path was not run;
- `failed`: parsing, syntax, runtime, assertion, or required-audit failure.

## 3. Why P3 Remains Blocked

`BRIDGE_SCHEMA.md` requires explicit present endpoints, verified prerequisites, a mode-correct validation path, and a precise formal connection before formal Coordinator consumption. The sample shows unresolved endpoint risks in all three target levels:

- Mode A samples can execute while lacking formal definitions or complete concept-level assertions.
- Mode B samples use everyday mechanical mappings, v8 checks, or code anchors that do not validate the stated abstract structure.
- Sampled Mode B nodes lack explicit prerequisites and analogy boundaries.
- No node evaluator currently establishes definition accuracy, complete `sub_topics`, mapping safety, or teaching readiness.

P3 may begin only after a reviewed repair batch demonstrates that endpoint content can satisfy the quality gates without evaluator overclaim.

## 4. Failure Taxonomy

### Structural repair

- `schema_gap`: add required explicit fields without changing mathematical meaning.
- `missing_formal_definition`: add a definition, axiom skeleton, or theorem skeleton appropriate to the node.
- `missing_prerequisites`: add only verified existing node references; do not invent IDs.

### Computational audit repair

- `shallow_sanity_audit`: replace narrow examples with mathematical properties or invariants.
- `shape_only_test`: test the stated mathematical relationship, not only dimensions, length, or construction.
- `code_not_testing_stated_concept`: align code and assertions with declared `sub_topics`; label special cases honestly.

### Mapping and mode repair

- `missing_mapping_boundary`: state where the analogy applies and what it does not prove.
- `daily_metaphor_in_mode_b`: replace the primary mapping with an LLM-architecture mapping; an everyday image may remain only as a clearly secondary teaser.
- `mode_mismatch`: route the node through the protocol-defined lane and use the matching audit type.
- `misleading_mapping`: repair or replace only the mapping when the underlying mathematics is sound.

### Regeneration escalation

- `regeneration_required` is assigned only after ChatGPT High finds materially incorrect formal content or `sub_topics` that targeted repair cannot safely preserve.
- No sampled node currently has an approved regeneration decision.

## 5. Repair Categories

1. **Field completion**: `domain`, `formal_definition`, verified `prerequisite_nodes`, and mapping boundaries.
2. **Mode A audit strengthening**: property, identity, invariant, edge-case, or counterexample assertions tied to the named concept.
3. **Mode B semantic repair**: LLM-architecture primary mapping, explicit analogy boundary, prerequisite graph, and reviewable `v9_semantic_audit` criteria.
4. **Code-anchor correction**: keep a computable example only when it is labeled as an intuition anchor or special case rather than proof.
5. **Single-node regeneration**: use only when formal mathematics or topic coverage is materially defective and ChatGPT High approves escalation.

## 6. Prioritization Rules

Repairs proceed from the narrowest adequate remedy:

1. Prefer field completion over rewriting a node.
2. Repair Mode A audit depth before considering regeneration.
3. Repair Mode B mapping, boundary, prerequisites, and semantic audit together so routing is internally coherent.
4. Prioritize Level 4-6 nodes because they are candidate endpoints for the blocked bridge program.
5. Include both modes in the first batch to validate both repair paths.
6. Defer nodes with unresolved mode unless ChatGPT High first decides their routing.
7. Do not infer database-wide repair scope from the nine-node sample.

## 7. First Repair Batch Recommendation

Recommend four nodes. P2.10 must not start until ChatGPT High approves this exact batch and each proposed repair boundary.

| Order | Node | File | Observed failure types | Proposed repair type | Expected evaluator status | Review gate |
| ---: | --- | --- | --- | --- | --- | --- |
| 1 | `COMPLEX_ANALYSIS-418` (`n_418`) | `08_Domain_Applications/Math_Mentor/Pure_Math_Intuition_DB/COMPLEX_ANALYSIS-418.yaml` | `schema_gap`, `missing_formal_definition` | Add explicit domain and a formal Euler/polar-representation definition skeleton; preserve the working symbolic identity audit and add only verified prerequisites if needed. | `passed` after executable property checks; not a mathematical-correctness claim. | ChatGPT High reviews definition scope, prerequisites, and `sub_topics` coverage. |
| 2 | `PDE-487` (`n_487`) | `08_Domain_Applications/Math_Mentor/Pure_Math_Intuition_DB/PDE-487.yaml` | `schema_gap`, `missing_formal_definition`, `shallow_sanity_audit` | Add domain and formal Fourier-derivative statement with assumptions; expand v8 assertions beyond one symbolic function; separate the FNO analogy from the mathematical theorem and state its boundary. | `passed` only if non-structural executable properties pass without warnings. | ChatGPT High reviews assumptions, FNO boundary, and whether tests match all repaired claims. |
| 3 | `ABSTRACT_ALGEBRA-468` (`n_468`) | `08_Domain_Applications/Math_Mentor/Pure_Math_Intuition_DB/ABSTRACT_ALGEBRA-468.yaml` | `schema_gap`, `missing_formal_definition`, `missing_prerequisites`, `shallow_sanity_audit`, `code_not_testing_stated_concept`, `missing_mapping_boundary`, `daily_metaphor_in_mode_b`, `mode_mismatch` | Repair as Mode B: add field-extension definition skeleton and verified prerequisites; replace the primary pipe metaphor with an LLM-architecture structural mapping; add a boundary; relabel any root calculation as a special-case anchor; use reviewable semantic-audit criteria. | `review_required`, intentionally, because semantic review is not machine validation. | ChatGPT High reviews field-extension mathematics, Mode B mapping, boundary, and semantic criteria. |
| 4 | `ALG_TOPOLOGY-676` (`n_676`) | `08_Domain_Applications/Math_Mentor/Pure_Math_Intuition_DB/ALG_TOPOLOGY-676.yaml` | `schema_gap`, `missing_formal_definition`, `missing_prerequisites`, `shallow_sanity_audit`, `code_not_testing_stated_concept`, `missing_mapping_boundary`, `daily_metaphor_in_mode_b`, `mode_mismatch` | Repair as Mode B: define base, total space, projection, fiber, and local trivialization; add verified prerequisites; make the LLM-architecture relation primary with an explicit boundary; demote/remove the loom metaphor; treat scalar code as an anchor only; add semantic-audit criteria. | `review_required`, intentionally, pending semantic and mathematical review. | ChatGPT High reviews bundle definitions, transition/local-triviality coverage, mapping safety, and teaching readiness. |

This batch is a process-validation batch, not a declaration that these four nodes are the only defects. `ALGEBRAIC_GEO-632`, `COMBINATORICS-577`, and `LINEAR_ALGEBRA-328` are strong second-batch candidates after the first batch is reviewed.

## 8. Per-Node Repair Contract

For every approved node in P2.10:

- preserve the existing node identity and filename;
- preserve correct content and rewrite only fields implicated by evidence;
- verify every prerequisite against the node index/database before adding it;
- cover every existing `sub_topics` item or explicitly report a scope defect;
- use Mode A everyday intuition plus computational audit, or Mode B LLM-architecture mapping plus semantic review, as routed;
- state analogy limitations;
- do not convert a code anchor into a proof claim;
- record the before/after failure classifications and evaluator result;
- stop for ChatGPT High review before committing a mathematically disputed repair.

## 9. What Must Not Be Repaired Yet

- Nodes outside the ChatGPT-approved first batch.
- `BRIDGE_SCHEMA.md`, bridge YAML, bridge registry, or node mapping index.
- Evaluator scripts or their status model; P2.8 is a separate completed stage.
- Roadmap files or node identities.
- Legacy schemas through a bulk migration.
- Unknown-mode nodes such as `COMBINATORICS-577` until routing is reviewed.
- Any whole level, domain, or database through regeneration.
- Any node whose proposed definition or mapping remains mathematically disputed.

## 10. Stop Rules

Stop the repair batch and request review when any condition applies:

1. The same failure class remains after three materially different repair attempts; record it in `三次修复仍失败_待后续处理.md`.
2. A proposed prerequisite cannot be resolved to an existing stable node.
3. The existing `sub_topics` conflict with the title or formal mathematics.
4. Mode routing is unknown or conflicts with `Universal_Layer_Execution_Protocol.md`.
5. A Mode B mapping requires an unsupported claim about LLM architecture.
6. A Mode A property cannot be tested without a new heavy dependency or a changed evaluator.
7. Repair would require changing node identity, roadmap order, bridge schema, or unrelated files.
8. Evidence suggests a level/domain failure rate above 30%; expand the audit before deciding regeneration.
9. Any security, credential, destructive Git, merge, or source-push gate is encountered.

## 11. Validation Commands

Run from the repository root in PowerShell. P2.10 should evaluate only the approved small batch, one node at a time.

```powershell
python '06_Silicon_Index/factory_pipeline/sandbox_evaluator.py' '08_Domain_Applications/Math_Mentor/Pure_Math_Intuition_DB/COMPLEX_ANALYSIS-418.yaml'
python '06_Silicon_Index/factory_pipeline/sandbox_evaluator.py' '08_Domain_Applications/Math_Mentor/Pure_Math_Intuition_DB/PDE-487.yaml'
python '06_Silicon_Index/factory_pipeline/sandbox_evaluator.py' '08_Domain_Applications/Math_Mentor/Pure_Math_Intuition_DB/ABSTRACT_ALGEBRA-468.yaml'
python '06_Silicon_Index/factory_pipeline/sandbox_evaluator.py' '08_Domain_Applications/Math_Mentor/Pure_Math_Intuition_DB/ALG_TOPOLOGY-676.yaml'
```

Interpret Mode B exit code `2` as expected `review_required`, not failure or pass. Confirm the structured JSON status and warnings for every command.

Additional checks:

```powershell
python -c "import pathlib,yaml; [yaml.safe_load(pathlib.Path(p).read_text(encoding='utf-8')) for p in ['08_Domain_Applications/Math_Mentor/Pure_Math_Intuition_DB/COMPLEX_ANALYSIS-418.yaml','08_Domain_Applications/Math_Mentor/Pure_Math_Intuition_DB/PDE-487.yaml','08_Domain_Applications/Math_Mentor/Pure_Math_Intuition_DB/ABSTRACT_ALGEBRA-468.yaml','08_Domain_Applications/Math_Mentor/Pure_Math_Intuition_DB/ALG_TOPOLOGY-676.yaml']]; print('YAML parse passed')"
git diff --name-only
git diff --check
```

Do not use a root-level bulk run as evidence for this batch. Perform manual/ChatGPT review for formal definitions, prerequisites, `sub_topics`, mappings, boundaries, and Coordinator readiness because the evaluator cannot adjudicate them.

## 12. Review Gate Before P2.10

P2.10 requires an explicit ChatGPT main-thread High decision that:

- approves the exact first-batch node list;
- confirms Mode A/B routing for each node;
- approves each repair category and mathematical boundary;
- confirms no regeneration is authorized;
- accepts the expected evaluator outcomes, including Mode B `review_required`;
- confirms bridge generation remains blocked.

The human is interrupted only if ChatGPT reports conflict, mathematical disagreement, permission escalation, regeneration, source publication, or another major-stage gate.

## 13. Relationship to `BRIDGE_SCHEMA.md`

This repair plan stabilizes possible bridge endpoints; it does not define bridge edges. A future bridge may be formally consumed only when endpoint references are present, prerequisites are verified, the declared mode has the appropriate reviewed validation status, and the bridge itself is indexed and validated.

The schema example `n_418 -> n_442` remains illustrative only. Repairing `n_418` does not approve that bridge, validate `n_442`, or change the example's `pending`/`unindexed` status.

## 14. Why No Bridge Generation Yet

Generating bridges now would encode relationships on top of endpoints that still lack reviewed definitions, prerequisites, mapping boundaries, or mode-correct audit evidence. The first repair batch must be completed and reviewed, its process must demonstrate acceptable endpoint quality, and ChatGPT High must explicitly reopen P3 before any bridge candidate design or YAML landing begins.

## 15. Next Stage

Next stage: **P2.9-A Review**.

Do not enter P2.10 from this plan alone. After ChatGPT High approves or revises the plan, execute only the confirmed small batch and stop again for repair-effect review.
