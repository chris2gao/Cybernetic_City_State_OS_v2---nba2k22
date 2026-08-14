---
document_id: os-v2-mechanism-activation-and-adherence-implementation-001-second-b2-correction-result-001
task_id: os-v2-mechanism-activation-and-adherence-implementation-001
author_endpoint_id: codex-implementation-executor-001
author_task_role: implementation_executor
purpose: second_B2_provenance_minting_corrected_candidate_result
privacy_class: repository_shareable
supersedes: documents/codex-implementation-executor-001/00005_B2_correction_result.md
---

# Second B2 provenance-minting correction result

Exact corrected candidate `4e03c7a7beda4a02330f81a66a7d41d200132d17`
supersedes vulnerable candidate `67c668d038c94e4de9935d0ee0bab3cb526d6c6e`.
Architecture A and the accepted non-B2 dimensions were not reopened.

`MaterialObservationContext` no longer exposes an ordinary-caller fact-binding API.
The acceptance boundary consumes only opaque, one-use handles recorded in an
execution issuance ledger after a controlled expected-source resolver physically
reads the cited source and a controlled observation adapter physically consumes its
source. Caller-supplied values, resolver or adapter identifiers, consumed-ref sets,
constructed lookalike handles, and markers not bound to execution cannot establish
provenance.

Exact-ref replay proves that the five second-round attacks all returned `VERIFIED`
at `67c668d038c94e4de9935d0ee0bab3cb526d6c6e` and all return `UNVERIFIABLE` at the
new candidate. Candidate-bound regression is `102/102`; frozen Stage04 full and
mutation suites are each `50/50`; nine execution-issued material claims are
`VERIFIED`; the historical long-path pointer and both B2 correction pointers all
receiver-bootstrap successfully.

Evidence is under the implementation run in `candidate_spec_v5.yml`,
`bound_candidate_checks_v5.yml`, `second_B2_exact_ref_replay_v1.yml`,
`candidate_material_receipt_v5.yml`, and the two Stage04 candidate-v5 results.

Fresh independent implementation acceptance remains required. No L4,
operationally-active, master publication, or automatic progression claim is made.
