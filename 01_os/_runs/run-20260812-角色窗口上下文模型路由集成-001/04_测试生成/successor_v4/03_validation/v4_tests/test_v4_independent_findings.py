#!/usr/bin/env python3
"""Direct regressions for the four independent parent-Stage04 findings.

Codex review `5f4520dd123ba634b1082f3ac7dbb6284a79849c` returned FIX_REQUIRED
with four reproducible counterexamples. At that time the inherited suite was
57/57 green and missed every one of them, which is the whole reason these live
here as persisted cases rather than as a one-shot probe: a finding that only
ever existed in a transcript is a finding the next round cannot re-run.

Each case states the mutation, the predicate it must move, and the reason the
move is correct. The control asserts the unmutated tree passes, without which
"the mutation fails" would be satisfied by a package that fails everything.

  T2-PARENT-IR-001  cross-adapter ownership leakage
      `failure_states` rewritten from `[X]` to the admitted `[{X: {}}]` moved
      P24 pass -> fail, because a RouteReceiptFact was sourced from
      `failure_states[5].missing_or_stale_route_receipt`. A representation
      change that changes no content must not move a verdict.

  T2-PARENT-IR-002  A12 route-receipt false PASS
      `missing_or_stale_or_inconsistent: best_effort` left all fourteen
      predicates passing. A/R12 requires a missing or invalid routing receipt
      to fail visibly with no arbitrary-model fallback.

  T2-PARENT-IR-003  polarity false PASS
      `not_stale`, `not_changed` and `not_fail_closed` each normalized to the
      positive role, so an inverted declaration passed. F02-A requires whole-
      token negation parity at every v4 vocabulary decision.

  T2-PARENT-IR-004  determinism false PASS
      Every subject replaced with `whatever_the_operator_feels_has_drifted_enough`
      still passed, because any non-empty subject slot counted as resolved.
      F03-D requires a machine-observable subject and states that arbitrary
      prose is not deterministic.
"""

from __future__ import annotations

import shutil
import tempfile
from pathlib import Path

import _bootstrap_v4  # noqa: F401
from _bootstrap_v4 import BASELINE_V4

from semantic_acceptance.core import dump_yaml, load_yaml_strict
from semantic_acceptance_v4.evaluate_v4 import evaluate_full, result_vector

WINDOWS = "mechanism/windows_v1.yml"
SUBJECTIVE = "whatever_the_operator_feels_has_drifted_enough"


_CACHE: dict[str, dict[str, str]] = {}


def _vector(mutate=None, key: str = "control") -> dict[str, str]:
    """Evaluate baseline_v4, optionally mutated, in a private temporary copy."""
    if key in _CACHE:
        return _CACHE[key]
    with tempfile.TemporaryDirectory(prefix="ir_") as td:
        root = Path(td) / "tree"
        shutil.copytree(BASELINE_V4, root)
        if mutate is not None:
            p = root / WINDOWS
            doc = load_yaml_strict(p.read_text(encoding="utf-8"))
            mutate(doc)
            p.write_bytes(dump_yaml(doc).encode("utf-8"))
        _CACHE[key] = result_vector(evaluate_full(root))
    return _CACHE[key]


def _m_failure_states_single_entry(doc):
    doc["failure_states"] = [{s: {}} for s in doc["failure_states"]]


def _m_route_policy_best_effort(doc):
    doc["model_route_binding"]["route_receipt"]["missing_or_stale_or_inconsistent"] = "best_effort"


def _m_route_policy_absent(doc):
    del doc["model_route_binding"]["route_receipt"]["missing_or_stale_or_inconsistent"]


def _m_route_policy_inverted(doc):
    doc["model_route_binding"]["route_receipt"]["missing_or_stale_or_inconsistent"] = "not_fail_closed"


def _m_not_stale(doc):
    doc["lifecycle"]["states"] = [
        "not_stale" if s == "stale" else s for s in doc["lifecycle"]["states"]
    ]


def _m_not_changed(doc):
    for rec in doc["lifecycle"]["invalidation_conditions"].values():
        if isinstance(rec, dict) and "observation" in rec:
            rec["observation"] = "not_changed"


def _m_not_fail_closed(doc):
    doc["lifecycle"]["stale_effect"] = "not_fail_closed"


def _m_subjective_subject(doc):
    for rec in doc["lifecycle"]["invalidation_conditions"].values():
        if isinstance(rec, dict) and "subject" in rec:
            rec["subject"] = SUBJECTIVE


# ---------------------------------------------------------------------------
# control
# ---------------------------------------------------------------------------


def test_the_unmutated_baseline_passes_every_predicate():
    """Without this, every case below is satisfied by a package that fails all."""
    v = _vector()
    failing = {p: s for p, s in v.items() if s != "pass"}
    assert failing == {}, failing


# ---------------------------------------------------------------------------
# T2-PARENT-IR-001
# ---------------------------------------------------------------------------


def test_ir001_representation_change_moves_no_verdict():
    """The exact witness: `failure_states` in single-entry-mapping form.

    Asserted over the WHOLE vector, not just P24. The finding was ownership
    leakage; restricting the assertion to the predicate that happened to move
    would let the same leak reappear at a different adapter.
    """
    control = _vector()
    mutated = _vector(_m_failure_states_single_entry, "ir001")
    moved = {p: (control[p], mutated[p]) for p in control if control[p] != mutated[p]}
    assert moved == {}, moved


# ---------------------------------------------------------------------------
# T2-PARENT-IR-002
# ---------------------------------------------------------------------------


def test_ir002_best_effort_route_policy_is_non_pass():
    assert _vector(_m_route_policy_best_effort, "ir002_best")["P27"] != "pass"


def test_ir002_absent_route_policy_is_non_pass():
    """Family, not spelling: an undeclared policy is as non-compliant as a bad one."""
    assert _vector(_m_route_policy_absent, "ir002_absent")["P27"] != "pass"


def test_ir002_inverted_route_policy_is_non_pass():
    """`not_fail_closed` must not normalize to the compliant role."""
    assert _vector(_m_route_policy_inverted, "ir002_inverted")["P27"] != "pass"


# ---------------------------------------------------------------------------
# T2-PARENT-IR-003
# ---------------------------------------------------------------------------


def test_ir003_inverted_lifecycle_state_is_non_pass():
    assert _vector(_m_not_stale, "ir003a")["P21"] != "pass"


def test_ir003_inverted_observation_is_non_pass():
    assert _vector(_m_not_changed, "ir003b")["P21"] != "pass"


def test_ir003_inverted_consequence_is_non_pass():
    assert _vector(_m_not_fail_closed, "ir003c")["P21"] != "pass"


def test_ir003_parity_is_applied_at_the_role_resolvers_not_at_three_strings():
    """The fix must be the resolver, or the next inverted spelling reopens it.

    Both v4 role resolvers are asked directly. `_observation_role` and
    `_consequence_role` delegate to `_effect_role`, so these two cover every v4
    observation, consequence and lifecycle-state decision.
    """
    from semantic_acceptance_v4 import adapters_v4 as A
    from semantic_acceptance_v4 import vocabulary_v4 as V

    assert A._role_of("stale", V.LIFECYCLE_STATE_ROLES) != ""
    assert A._role_of("not_stale", V.LIFECYCLE_STATE_ROLES) == ""
    assert A._effect_role("fail_closed", V.FRESHNESS_EFFECT_ROLES) == "stale_status"
    assert A._effect_role("not_fail_closed", V.FRESHNESS_EFFECT_ROLES) == ""
    assert A._effect_role("never_not_fail_closed", V.FRESHNESS_EFFECT_ROLES) == "stale_status"


# ---------------------------------------------------------------------------
# T2-PARENT-IR-004
# ---------------------------------------------------------------------------


def test_ir004_subjective_subject_is_non_pass():
    assert _vector(_m_subjective_subject, "ir004")["P21"] != "pass"


def test_ir004_subject_binding_is_resolution_not_a_word_list():
    """A real declared position passes and an invented one does not, and the
    difference is whether the candidate declares it - never what it is called.
    """
    from semantic_acceptance.facts import build_fact_set
    from semantic_acceptance_v4 import adapters_v4 as A

    doc = next(d for d in build_fact_set(BASELINE_V4).documents if d.rel_path.endswith(WINDOWS))
    assert A._subject_is_machine_bound(doc, "context_binding.dependency_fingerprints")
    assert not A._subject_is_machine_bound(doc, SUBJECTIVE)
    assert not A._subject_is_machine_bound(doc, "")
    assert not A._subject_is_machine_bound(doc, None)


# ---------------------------------------------------------------------------
# Second independent review, 04e7a7ba492e8e6037b150809e12cdb0e941d682
#
# The first correction round closed IR-001 to IR-004 and was itself reviewed.
# Reviewer-002 found that two of those closures were witness-deep rather than
# family-deep, which is the failure mode the first round's own residual-limits
# section had named and not prevented:
#
#   T2-PARENT-SR-001  the route policy was resolved by FIRST asserted role, so
#       the contradictory `[fail_closed, best_effort]` resolved to the compliant
#       half and passed. IR-002 had only closed the single-value spellings.
#   T2-PARENT-SR-002  a dotted subject was checked as a BAG of component names,
#       so `context_binding.route_receipt` - two real names, no such path -
#       resolved. IR-004 had only closed the wholly-invented subject.
#
# Both are corrected at the resolver, and the matrices below include the
# order-reversal controls that distinguish a family fix from a literal one.
# ---------------------------------------------------------------------------


def _policy(value):
    def m(doc):
        doc["model_route_binding"]["route_receipt"]["missing_or_stale_or_inconsistent"] = value
    return m


def _subject(value):
    def m(doc):
        for rec in doc["lifecycle"]["invalidation_conditions"].values():
            if isinstance(rec, dict) and "subject" in rec:
                rec["subject"] = value
    return m


def test_sr001_contradictory_route_policy_is_non_pass_in_either_order():
    """The reviewer's witness and its reversal.

    Order matters here in exactly one way: it must not matter. A first-match
    resolver passes one ordering and fails the other, so both are asserted.
    """
    assert _vector(_policy(["fail_closed", "best_effort"]), "sr001_a")["P27"] != "pass"
    assert _vector(_policy(["best_effort", "fail_closed"]), "sr001_b")["P27"] != "pass"


def test_sr001_two_recognised_but_disagreeing_roles_are_non_pass():
    """Not just compliant-plus-unknown: compliant plus a recognised
    non-compliant role is a contradiction too, and neither element is unknown.
    """
    assert _vector(_policy(["fail_closed", "continue_cached"]), "sr001_c")["P27"] != "pass"


def test_sr001_an_unambiguous_policy_still_passes():
    """Without this the family rule could be satisfied by rejecting everything."""
    assert _vector(_policy("fail_closed"), "sr001_ok1")["P27"] == "pass"
    assert _vector(_policy(["fail_closed", "fail_closed"]), "sr001_ok2")["P27"] == "pass"


def test_sr002_spliced_subject_paths_are_non_pass():
    """Both reviewer witnesses. Every component of each is a real declared name
    somewhere in the document; neither path exists.
    """
    assert _vector(_subject("context_binding.route_receipt"), "sr002_a")["P21"] != "pass"
    assert _vector(_subject("lifecycle.dependency_fingerprints"), "sr002_b")["P21"] != "pass"


def test_sr002_a_reversed_real_path_is_non_pass():
    """`dependency_fingerprints.context_binding` uses the same two components as
    a path that does exist. A bag cannot tell the two apart; an ordered walk can.
    """
    assert _vector(_subject("dependency_fingerprints.context_binding"), "sr002_rev")["P21"] != "pass"


def test_sr002_a_real_ordered_path_still_passes():
    assert _vector(_subject("context_binding.dependency_fingerprints"), "sr002_ok")["P21"] == "pass"


def test_sr002_path_resolution_walks_rather_than_collects():
    """Asserted at the resolver, so the fix cannot be a per-witness patch."""
    from semantic_acceptance.facts import build_fact_set
    from semantic_acceptance_v4 import adapters_v4 as A

    doc = next(d for d in build_fact_set(BASELINE_V4).documents if d.rel_path.endswith(WINDOWS))
    assert A._resolves_ordered_path(doc, ["context_binding", "dependency_fingerprints"])
    assert A._resolves_ordered_path(doc, ["window_identity", "bound_facts", "entry_repository_head"])
    assert not A._resolves_ordered_path(doc, ["context_binding", "route_receipt"])
    assert not A._resolves_ordered_path(doc, ["dependency_fingerprints", "context_binding"])
    assert not A._resolves_ordered_path(doc, ["window_identity", "entry_repository_head"])
