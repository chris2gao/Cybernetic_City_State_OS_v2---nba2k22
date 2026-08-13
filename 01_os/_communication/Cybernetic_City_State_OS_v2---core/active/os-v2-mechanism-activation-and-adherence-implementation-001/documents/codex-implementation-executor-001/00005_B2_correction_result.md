---
document_id: os-v2-mechanism-activation-and-adherence-implementation-001-b2-correction-result-001
task_id: os-v2-mechanism-activation-and-adherence-implementation-001
author_endpoint_id: codex-implementation-executor-001
author_task_role: implementation_executor
purpose: B2_observation_provenance_binding_corrected_candidate_result
privacy_class: repository_shareable
supersedes: documents/codex-implementation-executor-001/00003_implementation_result_correction.md
---

# B2 observation-provenance correction result

Exact corrected candidate `67c668d038c94e4de9935d0ee0bab3cb526d6c6e`
supersedes candidate `8fa49cc3a7eb082d4ffcee984652b77080d1b9f9` for
acceptance. Architecture A/B was not reopened.

The generic material verifier now requires a `MaterialObservationContext` populated
outside the receipt. Each claim ID is bound to an independently resolved expected
source/ref/value and a consumed physical observation ref/source/value. Missing
context, unresolved refs, source/ref mismatch, unconsumed principal or freshness
references, and claim/context value mismatches all produce a non-PASS result.

Exact replay evidence shows all five reviewer counterexamples returned `VERIFIED`
at reviewed candidate `8fa49cc3a7eb082d4ffcee984652b77080d1b9f9` and all five return
`UNVERIFIABLE` at the corrected candidate. Candidate-bound regression is `101/101`;
frozen Stage04 full and mutation suites are each `50/50`; nine material claims are
`VERIFIED`; old and corrected v2 pointers both receiver-bootstrap successfully.

Evidence is under the implementation run in `candidate_spec_v4.yml`,
`bound_candidate_checks_v4.yml`, `candidate_material_receipt_v4.yml`, the two
`B2_counterexamples_*.yml` files, and the two Stage04 candidate-v4 results.

Fresh independent implementation acceptance remains required. No L4,
operationally-active, master publication, or automatic progression claim is made.
