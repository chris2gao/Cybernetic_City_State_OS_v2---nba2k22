---
document_id: os-v2-t2-completion-001::codex-t2-parent-stage04-reviewer-001::review-00001
task_id: os-v2-t2-completion-001
author_endpoint_id: codex-t2-parent-stage04-reviewer-001
author_task_role: parent_stage04_independent_acceptance_reviewer
purpose: durable_parent_stage04_independent_acceptance_result
privacy_class: repository_shareable
---

# Parent T2 Stage04 independent acceptance result

Verdict: **FIX_REQUIRED** for frozen candidate
`4ce3e09e8c75881165f7705ab3a0398a4d3acf9c` at publication head
`4f6bd40518ff7dc652d1e5819f9a10781cc2e425`. Parent Stage04 PASS is not
supported and Stage05 must not begin.

## Work performed or requested

I reconstructed Human-confirmed A v1, the parent successor-v4 acceptance
contract, V4-FND-01 through V4-FND-04, V4-OBS-01 through V4-OBS-03,
correction-003, foreground R1-R3, P2-2, the refreeze and exact result pointer
from primary Git objects. I reproduced the inherited v3 and final v4 suites,
audited exact lineage and publication topology, validated the receipt and
provenance from immutable Git blobs, and ran independent representation,
ownership, polarity, determinism and fallback attacks.

## Implementation or review method

Fresh isolated Codex session; detached clean review entry at exact
`4f6bd405`; immutable candidate `4ce3e09e`; no candidate,
implementation-branch or master edits. The adversarial plan was fixed from A
and the open findings before source-level inspection. Each material attack ran
on a fresh temporary copy; process-sensitive attacks were repeated in two
independent processes and produced identical evidence hashes.

## Supportability rationale

Four independently reproducible material defects remain. They are direct
counterexamples to A03, A07 and A12 and to the v4 representation/polarity
construction invariants; executor-green suites and foreground rulings cannot
substitute for those counterexamples. Conversely, exact-Git
receipt/provenance/R1-R3 checks passed, so the result is not BLOCKED by missing
or contradictory evidence.

## Feasibility rationale

Each defect is bounded to the v4 acceptance layer and its corpus/semantic
contract. A successor candidate can correct the ownership, stale-receipt
behavior, complete polarity normalization and machine-observable determinism
rule, regenerate evidence, refreeze and request a new fresh independent review.
No Stage01-03 rewrite, history rewrite or master write is required.

## Primary evidence and measurements

- v3 inherited suite: 65/65 passed, actual process exit code 0.
- final v4 inherited suite: 57/57 passed, actual process exit code 0.
- exact-Git receipt/provenance audit: 27/27 changed paths, 83/83 artifact
  SHA-256 values, direct publication parent, external receipt closure, 128
  unique rules with zero untraced, A01-A14 each with one unique decider, and
  exact R1-R3 binding delta all passed. Receipt publication-blob SHA-256:
  `9817cedbaf47ec493465fd3f2b448682b2cc7ac6447ad1c375ef30710c5d6a28`.
- cross-adapter/fallback probe repeated twice with identical normalized output
  SHA-256:
  `21de38e9349f3b7416f8135c555fe4a70dad7f956ee294ca0f9c5093d128c3c2`.
- polarity/determinism probe repeated twice with identical normalized output
  SHA-256:
  `a29f4c5f8efb0c8304a6c16ef7955b89032e40c96fd67cc4ff9e3128accba9ae`.

## Findings and residuals

### T2-PARENT-IR-001 — material representation-coupling false FAIL

Rewriting `failure_states` from the admitted bare-identifier form `[X]` to the
admitted single-entry-mapping form `[{X: {}}]` leaves the accepted seven
completely stable after correction-003, but full v4 changes P24 `pass -> fail`.
The new `RouteReceiptFact` is physically sourced from
`failure_states[5].missing_or_stale_route_receipt`. This is v4 route-receipt
cross-adapter ownership leakage, not a remaining vendored P02 defect.
V4-OBS-03 is therefore materially reclassified for the current candidate.

### T2-PARENT-IR-002 — material A12 false PASS

Changing the explicit route-receipt policy
`missing_or_stale_or_inconsistent` from `fail_closed` to `best_effort` leaves
all fourteen predicates PASS and creates no fallback fact. Human-confirmed R12
requires missing or invalid routing receipts to fail visibly with no
arbitrary-model fallback. V4-OBS-02 is therefore a blocking finding, not a
non-blocking observation.

### T2-PARENT-IR-003 — material polarity false PASS

Independently replacing the required stale state with `not_stale`, every
observation with `not_changed`, or the consequence with `not_fail_closed`
leaves all fourteen predicates PASS. `not_changed` is normalized as `changed`;
`not_fail_closed` is normalized to the compliant `stale_status` role. F02-A
parity was not applied to every v4 vocabulary decision site, so V4-FND-02 does
not pass independent closure.

### T2-PARENT-IR-004 — material determinism false PASS

Replacing every machine subject with
`whatever_the_operator_feels_has_drifted_enough` leaves P21 and all fourteen
predicates PASS; every subjective value is marked `subject_resolved` and
deterministic merely because it is non-empty in a subject slot. That does not
establish F03-D's machine-observable subject or binding, so V4-FND-03 does not
pass independent closure.

## Open-item adjudication

- V4-FND-01: scoped closure supported; not a current blocker.
- V4-FND-02: independent closure failed by T2-PARENT-IR-003.
- V4-FND-03: independent closure failed by T2-PARENT-IR-004.
- V4-FND-04: field-mapping correction supported, but OBS-03 is reclassified as
  the material v4 ownership finding T2-PARENT-IR-001.
- V4-OBS-01: remains a non-blocking observation because A04 decides actual load
  entry exactness; the real unbounded-entry negative still fails.
- V4-OBS-02: promoted to material A12 finding T2-PARENT-IR-002.
- V4-OBS-03: promoted to material v4 cross-adapter finding
  T2-PARENT-IR-001.

## Executor rationale assessment

The executor measurements, disclosure of the earlier pycache topology
discovery, correction-003 integration ordering error, and refreeze history are
internally honest. The P2-2 mechanical obligations, receipt topology, merged
provenance ledger, trace and inventory are supported. FND-01's scoped
applicability guard and the surviving FND-04-b field-mapping correction are
supported by the inherited reproductions. But the test corpus encodes OBS-03
as outside the writable v4 defect surface and does not attack the remaining
role/effect polarity sites or subject observability; therefore its 57/57 result
is insufficient for semantic acceptance.

## Exact candidate binding

Reviewed publication head `4f6bd405` is the direct child of frozen candidate
`4ce3e09e`. Candidate ancestry from parent checkpoint `3002d617` through
correction-003 `9c50a4fe` and P2-2 `a1d376c0` is proven. The publication-only
delta contains `freeze_receipt_v4.yml` and `stage04_result_pointer_v1.yml`.
This result applies only to those exact objects.

## Required next state

Keep `parent_Stage04_PASS=false`, `Stage05_authorized=false`,
`canonical_write_authorized=false` and
`automatic_progression_authorized=false`. A corrected, newly frozen exact
candidate needs the inherited suites plus regression cases for all four
findings and a new relationship-isolated independent review. This result does
not authorize or perform any fix.
