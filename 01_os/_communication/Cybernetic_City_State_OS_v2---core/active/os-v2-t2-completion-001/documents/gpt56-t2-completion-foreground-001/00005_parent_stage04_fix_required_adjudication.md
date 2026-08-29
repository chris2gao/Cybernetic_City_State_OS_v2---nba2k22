---
document_id: os-v2-t2-completion-001::gpt56-t2-completion-foreground-001::parent-stage04-adjudication-00005
task_id: os-v2-t2-completion-001
author_endpoint_id: gpt56-t2-completion-foreground-001
author_task_role: foreground_t2_completion_coordinator
purpose: adjudicate_codex_parent_stage04_FIX_REQUIRED_and_bound_successor_correction
privacy_class: repository_shareable
---

# Foreground adjudication of parent Stage04 FIX_REQUIRED

Verdict: **ACCEPT_REVIEW_FIX_REQUIRED** for frozen candidate
`4ce3e09e8c75881165f7705ab3a0398a4d3acf9c` at publication head
`4f6bd40518ff7dc652d1e5819f9a10781cc2e425`.

The independent result at
`5f4520dd123ba634b1082f3ac7dbb6284a79849c` is formally valid and its four
material findings are supported by primary evidence. Parent Stage04 remains
`PASS=false`; Stage05, canonical and master writes remain prohibited.

## Work performed or requested

Foreground read the exact result, review document, constitution and receipt;
re-entered from current remote master; inspected the exact candidate source and
the original F02-A / F03-D rulings; and compared every finding with Human-confirmed
A03/A07/A12 and correction-003 structural-provenance invariants.
## Finding adjudication

### IR-001 — supported: v4 cross-adapter ownership leakage

`semantic_acceptance_v4.adapters_v4._regions()` currently selects nodes by
`walk_nodes + key-token intersection` and does not consult `Document.provenance`.
That bypasses correction-003's evaluator-owned `declaration_name` coordinate.
An admitted keyed-collection representation can therefore expose a failure-case
instance identity as a route-receipt region. This violates the accepted
structural-provenance contract.

Required correction: every v4 semantic claim made from a key/region name must be
gated by evaluator-owned position provenance. `instance_identity`, `unknown` and
conflicting positions remain unclaimable. Audit all v4 key-token discovery sites,
not only the reported P24 site. Do not restore tail matching or payload heuristics.

### IR-002 — supported: A12 route-receipt policy false PASS

A/R12 requires missing or invalid model-routing receipts to fail visibly and
forbids arbitrary-model fallback. The candidate already declares
`route_receipt.missing_or_stale_or_inconsistent: fail_closed`, but P27 does not
consume that policy; it only searches generic fallback-named positions.

Required correction: represent the contract-owned missing/stale/inconsistent
route-receipt policy as an explicit typed fact and require the fail-closed outcome.
Missing, unknown or non-fail-closed policy is non-pass. Do not patch only the
literal `best_effort` spelling with a blacklist.
### IR-003 — supported: F02-A polarity coverage incomplete

The original F02-A ruling required every v4 token-vocabulary polarity decision
to use accepted whole-token negation parity. The current `_effect_role()` is a
plain token-set intersection and is still used by observation/consequence role
normalization. Consequently `not_changed` and `not_fail_closed` can normalize to
positive compliant roles.

Required correction: route all v4 polarity-bearing vocabulary decisions through
a parity-aware role resolver. An inverted or ambiguous assertion must not produce
the positive role. Re-audit every v4 polarity decision site rather than patching
only the three reproduced strings.

### IR-004 — supported: F03-D machine-binding closure incomplete

The original foreground F03-D ruling states that `deterministic=true` requires a
**machine-observable subject/binding**, and explicitly states
`arbitrary_prose_is_deterministic: false`. Current code instead defines
`subject_resolved = bool(subject) and bool(_value_tokens(subject))`; any non-empty
subject therefore passes, including the independent subjective counterexample.

Required correction: subject resolution must prove an explicit machine-observable
binding from physical candidate content. A subject keyword whitelist remains
prohibited. Mere non-empty placement in a subject slot is insufficient. Where the
current baseline uses semantic labels that are not independently machine-bound,
make the candidate declare an explicit binding/reference and verify it structurally.
Unknown, dangling or subjective bindings are non-pass.
## Implementation or review method

Use one bounded successor-correction pass from exact implementation head
`4f6bd40518ff7dc652d1e5819f9a10781cc2e425`. Preserve Stage01-03 and the P2-2
mechanical framework. Add regression attacks for all four independent findings,
rerun inherited v3/v4, regenerate affected decision provenance / trace / inventory,
then produce a new freeze receipt, refreeze report and exact result pointer.

Do not mutate the old frozen receipt to pretend the old candidate passed. The old
candidate and independent FIX_REQUIRED remain immutable historical evidence.

## Supportability rationale

All four corrections derive from already accepted sources: Human-confirmed A,
F02-A parity, F03-D typed determinism, and correction-003 evaluator-owned
structural provenance. No new Human semantic choice is needed to establish that
the current candidate is defective or to define the safe direction of correction.

## Feasibility rationale

The defects are confined to the existing v4 acceptance/corpus/evidence surface and
are inside the existing implementation allowlist. No Stage01-03 rewrite, canonical
implementation, master publication or history rewrite is required.

## Success and stop conditions

Success requires all four independent counterexamples to become non-pass for the
correct reason, inherited suites to remain green, exact provenance/receipt closure
to be regenerated, and a newly frozen exact successor candidate to be published.
A fresh relationship-isolated review is required after that candidate exists.

Return to foreground only if correction requires a new semantic choice not fixed
by the cited rulings, exceeds allowed paths, invalidates Stage01-03, or requires
Stage05/master/history rewrite. Test greenness alone is not acceptance.
