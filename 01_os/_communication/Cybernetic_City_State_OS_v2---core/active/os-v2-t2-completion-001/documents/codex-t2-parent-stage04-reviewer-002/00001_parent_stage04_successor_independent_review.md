---
document_id: os-v2-t2-completion-001::codex-t2-parent-stage04-reviewer-002::review-00001
task_id: os-v2-t2-completion-001
author_endpoint_id: codex-t2-parent-stage04-reviewer-002
author_task_role: parent_stage04_independent_acceptance_reviewer
purpose: durable_parent_stage04_successor_independent_acceptance_result
privacy_class: repository_shareable
---

# Parent T2 Stage04 successor independent acceptance result

Verdict: **FIX_REQUIRED** for frozen successor candidate
`628dd60e3505516254bf37956bcde5fb93c2723a` at publication head
`8be63c167b16882cf0136d668c86e5e6796be30c`. Parent Stage04 PASS is not
supported and Stage05 remains unauthorized.

## Work performed or requested

I entered only through the exact Human-relayed v2 pointer at
`a34faa291a01317e642c46533b292ab2b940bfc8`, revalidated the live delegation,
and reconstructed the parent Stage04 contract, correction-003, R1-R6, the
previous candidate and independent FIX_REQUIRED result, V4-FND-01 through
V4-FND-04, V4-OBS-01, the successor refreeze, freeze receipt and result pointer
from primary Git evidence. I reran the inherited suites, replayed the persisted
IR-001 through IR-004 regressions, audited every v4 document-wide semantic
selector, checked the R6 structural profiles, verified the exact freeze and
publication topology, and ran new family-level representation, route-policy,
polarity and subject-binding attacks.

## Implementation or review method

Fresh isolated Codex session; clean detached review worktree at exact
publication head `8be63c16`; immutable review object `628dd60e`; no candidate,
implementation-branch or master edits. Every mutation ran on a fresh temporary
copy of the committed baseline. Receipt hashes were recomputed from immutable
Git blobs at the candidate SHA, avoiding worktree newline conversion. The
review used only durable rulings and primary repository evidence, not executor
or foreground private reasoning.

## Supportability rationale

The successor closes the four historical exact witnesses and most of their
families, but two new independently reproducible material false-PASS cases
remain. One accepts a contradictory A12 route-receipt failure policy. The
other accepts a dotted subject path whose components exist separately but whose
path does not exist. These are direct counterexamples to fail-closed route
policy resolution and F03-D machine-bound determinism. Green inherited suites,
a valid freeze receipt and honest provenance cannot override them. The evidence
is complete and internally coherent, so the correct verdict is FIX_REQUIRED,
not BLOCKED.

## Feasibility rationale

Both defects are bounded to successor-v4 semantic resolution. Route-policy
resolution must reject multiple or contradictory positive roles instead of
returning the first positive match. Subject resolution must verify one real
declared path or an otherwise exact structural binding instead of checking
whether dotted components occur independently anywhere in the document. A new
successor can fix those resolvers, persist both counterexamples, regenerate the
derived evidence, refreeze and request another fresh independent review. No
Stage01-03 rewrite, history rewrite or master write is required or authorized.

## Primary evidence and measurements

- Vendored v3 suite: 65/65 passed; actual process exit code 0.
- Successor v4 suite, including persisted IR-001 through IR-004 regressions:
  68/68 passed; actual process exit code 0.
- Freeze audit: declared and actual `3002d617..628dd60e` changed-path sets are
  exactly equal at 34 paths; all 85 artifact SHA-256 values recomputed from
  candidate Git blobs match; zero hash mismatches.
- Publication topology: exact frozen candidate `628dd60e` is an ancestor of
  exact publication head `8be63c16`. The candidate-to-publication delta is
  limited to the freeze receipt, R6 correction evidence, result pointer v2 and
  run state.
- Provenance and trace: 130 decision rules, zero untraced; 14/14 criteria have
  exactly one deciding predicate and no untested criterion; inventory is 16
  modules and 133 tests. The committed artifacts were revalidated by the v4
  suite against freshly derived values.
- IR-001 family attack: six semantic-token-colliding instance identifiers were
  added to `failure_states`; bare-list and admitted singleton-mapping forms
  produced identical full result vectors. No representation delta remained.
- IR-002 family attack: absent, unknown, inverted and non-fail-closed route
  policies each made P27 non-pass. The conflicting representation
  `[fail_closed, best_effort]` instead left P27 `pass`.
- IR-003 family attack: odd negation (`never_stale`, `never_changed`,
  `never_fail_closed`) resolved to no positive role, while the corresponding
  double-negated forms restored the positive role. The polarity family passed.
- IR-004 family attack: arbitrary prose, a self-vouching label and a dangling
  path were rejected; a real exact path was accepted. Two nonexistent spliced
  paths, `context_binding.route_receipt` and
  `lifecycle.dependency_fingerprints`, were incorrectly accepted. Replacing
  every lifecycle subject with the first spliced path left P21 `pass`.

## Findings and residuals

### T2-PARENT-SR-001 — material A12 contradictory-policy false PASS

Set
`model_route_binding.route_receipt.missing_or_stale_or_inconsistent` to the
conflicting YAML list `[fail_closed, best_effort]`. P27 remains `pass` even
though the same declaration explicitly permits the non-fail-closed behavior
that A12 forbids. The route adapter sends the complete value to
`_consequence_role`; `_effect_role` returns immediately on the first asserted
role and never establishes that exactly one non-conflicting role was declared.
This is a family-level residual of historical IR-002, not the already-fixed
`best_effort`, absent, unknown or inverted spelling.

Required correction: policy resolution must fail closed when more than one
role is asserted or when a compliant and non-compliant effect coexist, and the
exact conflicting representation must become a persisted non-pass regression.

### T2-PARENT-SR-002 — material F03-D spliced-path false PASS

The baseline declares `context_binding.dependency_fingerprints` and separately
declares `model_route_binding.route_receipt`; it does not declare
`context_binding.route_receipt`. It likewise declares `lifecycle` and
`context_binding.dependency_fingerprints`, but not
`lifecycle.dependency_fingerprints`. `_subject_is_machine_bound` nevertheless
accepts both strings because it splits a dotted subject and requires only that
each component name appear somewhere in the document. It does not resolve the
ordered parent-child path. Replacing all lifecycle condition subjects with
`context_binding.route_receipt` therefore leaves P21 `pass`.

Required correction: a dotted subject must resolve as one actual declared
structural path, with parent-child ordering and no component splicing. Persist
both a real-path control and the two spliced-path non-pass regressions.

## Structural-provenance and R6 audit

No unconverted seventh document-wide semantic claim selector was found. V4
semantic claim sites use evaluator-owned `_claim_sites` or `_claim_leaves`.
The remaining raw document-wide walks are confined to a parent-mapping subscan
whose yielded node is already structurally claimable and to the non-owning
referential-existence scan used by subject resolution; those uses do not mint
semantic ownership by themselves.

The committed `context_contract_v1` binding profile matches R6: root,
`minimum_effective_context`, `derivation_inputs`, `load_set` and `exactness`
are declaration-name positions, the transparent wrapper is explicit, and no
instance-identity expansion was introduced. The window-contract
`context_binding` declaration-name rule is structurally consistent with the
adjacent `model_route_binding` declaration and does not recreate IR-001. The
new SR-002 defect is downstream reference resolution: the declaration is
claimable, but the subject string is not resolved as an exact path.

## Open-item adjudication

- V4-FND-01: independent closure supported; not a current blocker.
- V4-FND-02: independent closure supported, including new odd/double-negation
  variants.
- V4-FND-03: closure not supported because SR-002 is a material residual in the
  same machine-bound determinism family.
- V4-FND-04: independent closure supported for the accepted-equivalence and
  field-mapping defect; the IR-001 family-level representation attack also
  passed.
- V4-OBS-01: remains non-blocking; actual load-entry exactness still decides
  acceptance and the unbounded-entry negative remains non-pass.
- Historical IR-002: exact witnesses are closed, but SR-001 is a material
  contradictory-policy residual in the same A12 family.

## Executor rationale assessment

The successor evidence is candid and mechanically strong. Its 34-path freeze,
85 artifact hashes, 130-rule ledger, complete trace, current inventory and
persisted historical regressions are supported. The correction also correctly
converts the six identified v4 semantic selector families and closes the four
historical exact strings. The remaining issue is test adequacy: the corpus does
not require route-role uniqueness and tests dotted subjects by component
existence rather than exact path existence. Consequently the executor's
greenness and refreeze rationale are reliable evidence about what was run, but
not sufficient evidence of parent Stage04 semantic acceptance.

## Exact candidate binding

This result is bound only to base `3002d6177779abf81e6d476bfc434ee5d6dbe3c8`,
previous candidate `4ce3e09e8c75881165f7705ab3a0398a4d3acf9c`, previous independent result
`5f4520dd123ba634b1082f3ac7dbb6284a79849c`, successor implementation
`d7bc2320`, frozen successor `628dd60e3505516254bf37956bcde5fb93c2723a`,
and publication head `8be63c167b16882cf0136d668c86e5e6796be30c`.
The result does not transfer to later commits without a new review.

## Required next state

Keep `parent_Stage04_PASS=false`, `Stage05_authorized=false`,
`canonical_write_authorized=false` and
`automatic_progression_authorized=false`. A newly corrected and frozen exact
successor must persist SR-001 and SR-002 and receive another fresh
relationship-isolated independent review. This review authorizes and performs
no implementation fix.
