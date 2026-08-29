#!/usr/bin/env python3
"""A-level predicates for the v4 coverage extension: A03, A04, A05, A07, A08, A10, A12.

Registered into the shared `semantic_acceptance.predicates.REGISTRY`, so
`evaluate_all` returns the accepted seven and these seven together, ordered by
predicate id.

Ids start at P21 rather than P08. P00 and P09 are already reserved inside
`semantic_acceptance.predicates.evaluate_all` for the unsupported-representation
and untraced-rule reports; reusing either would have silently overwritten a
report the accepted package emits. The gap is deliberate and is the reason this
module does not renumber the accepted predicates.

Every predicate here obeys the same three constraints as the accepted seven:

  * it reads typed decision facts only — no file, no container, no file name,
    no vendor token;
  * absence is never a pass. A region that was never declared fails, because A
    states a positive obligation and "nothing said" does not discharge it;
  * an unrecognised value fails rather than passes. ST04-V3-IR-008 and
    ST04-V3-IR-010 were both a closed POSITIVE vocabulary treating the unknown
    case as safe.
"""

from __future__ import annotations

from semantic_acceptance.core import ENABLED, UNKNOWN
from semantic_acceptance.facts import FactSet
from semantic_acceptance.predicates import FAIL, PASS, UNSUPPORTED, predicate

from . import vocabulary_v4 as V
from .facts_v4 import V4_FACT_SET_ATTRIBUTES


def _facts(fs: FactSet, name: str) -> list:
    return list(getattr(fs, name, ()) or ())


# --------------------------------------------------------------------------
# V4-FND-01: an unaugmented FactSet is not a fact set with nothing in it
# --------------------------------------------------------------------------
#
# Registering into the shared REGISTRY means `semantic_acceptance.evaluate_tree`
# also calls these predicates once this module has been imported anywhere in the
# process.  That entry point builds its FactSet with the accepted
# `build_fact_set`, which never runs `augment_fact_set`, so the v4 fact lists do
# not exist on it.
#
# Read through `_facts`, a missing attribute and an empty list are the same
# thing, and "absence is never a pass" then turns a tree that is fully
# conforming into a confident FAIL.  Measured on fixtures/baseline_v4:
# evaluate_full returned 14/14 pass while evaluate_tree returned overall fail on
# P21 P22 P23 P24 P25 P27 — same tree, same process, opposite verdicts.
#
# The rule "absence is not a pass" is about the *candidate* declaring nothing.
# It was never about the harness failing to populate the facts.  Conflating the
# two is a category error, and the fix is to separate them: a FactSet that was
# never augmented cannot support a judgement either way, which is exactly what
# the accepted contract's third outcome already means.  `UNSUPPORTED` is part of
# V-FACT-08 and `evaluate.overall` already treats it as not-pass, so this is
# fail-closed and needs no change to the vendored engine — whose bytes stay
# identical to 19c39ed37f14c97cfa132ffafabcb9afa33dd7f0.
#
# Human ruling of 2026-08-15 (option R-A of
# 03_validation/findings/V4-FND-01_shared_registry_false_fail_v1.yml).

_UNAUGMENTED_DETAIL = (
    "this FactSet was not augmented with the v4 fact lists, so {pid} has nothing to "
    "judge; call semantic_acceptance_v4.evaluate_v4.evaluate_full (or "
    "augment_fact_set) rather than semantic_acceptance.evaluate.evaluate_tree"
)


def _is_augmented(fs: FactSet) -> bool:
    return all(hasattr(fs, name) for name in V4_FACT_SET_ATTRIBUTES)


def v4_predicate(pid: str, title: str, a_trace: list[str]):
    """`predicate`, plus a fail-closed guard for an unaugmented FactSet.

    Deliberately a wrapper around the accepted decorator rather than a second
    registry: the shared REGISTRY is what makes the C-09 provenance ledger cover
    v4 rules on the same terms as accepted rules, and that property is worth
    keeping.  What is removed here is only the wrong *answer*, not the sharing.
    """

    def deco(fn):
        def guarded(fs: FactSet):
            if not _is_augmented(fs):
                return UNSUPPORTED, _UNAUGMENTED_DETAIL.format(pid=pid), []
            return fn(fs)

        guarded.__name__ = getattr(fn, "__name__", pid)
        guarded.__doc__ = getattr(fn, "__doc__", None)
        guarded.__wrapped__ = fn
        return predicate(pid, title, a_trace)(guarded)

    return deco


# --------------------------------------------------------------------------


@v4_predicate(
    "P21",
    "the window lifecycle declares the A-required states with deterministic stale conditions",
    ["A03", "R03_window_lifecycle"],
)
def p21_window_lifecycle(fs: FactSet):
    lifecycles = _facts(fs, "v4_lifecycles")
    conditions = _facts(fs, "v4_lifecycle_conditions")
    evidence = [
        f"{l.source_id}:{l.key_path} roles={list(l.state_roles)} declared={l.declared_state_count} "
        f"unmapped={l.unmapped_state_count}"
        for l in lifecycles
    ] + [
        f"cond {c.source_id}:{c.key_path} deterministic={c.deterministic} "
        f"subject={c.subject_resolved} observation={c.observation_role!r} "
        f"consequence={c.consequence_role!r} unresolved={list(c.unresolved_slots)}"
        for c in conditions
    ]

    if not lifecycles:
        return FAIL, "no window lifecycle is declared anywhere; absence is not a lifecycle", evidence

    covered: set[str] = set()
    for l in lifecycles:
        covered |= set(l.state_roles)
    missing = [r for r in V.A_REQUIRED_LIFECYCLE_ROLES if r not in covered]
    if missing:
        return FAIL, f"lifecycle does not declare A-required state role(s): {missing}", evidence

    if not conditions:
        return (
            FAIL,
            "no condition governs when a window can no longer continue on cached context",
            evidence,
        )
    # Ruling F03-D. A condition is deterministic only when the adapter resolved
    # all three semantic slots. The unresolved slot names travel with the fact,
    # so the failure says WHICH obligation the declaration did not discharge
    # rather than naming a vagueness word it happened to match.
    nondeterministic = [c for c in conditions if not c.deterministic]
    if nondeterministic:
        shown = ", ".join(
            f"{c.key_path} (unresolved: {', '.join(c.unresolved_slots)})"
            for c in nondeterministic[:3]
        )
        return FAIL, f"continuation condition is not a typed determinism fact: {shown}", evidence

    return (
        PASS,
        f"{len(V.A_REQUIRED_LIFECYCLE_ROLES)} A-required state role(s) covered; "
        f"{len(conditions)} deterministic continuation condition(s)",
        evidence,
    )


# --------------------------------------------------------------------------


@v4_predicate(
    "P22",
    "minimum effective context derives from the A-stated inputs with an exact, non-preloading load set",
    ["A04", "R04_minimum_effective_context"],
)
def p22_minimum_effective_context(fs: FactSet):
    contracts = _facts(fs, "v4_context_contracts")
    entries = _facts(fs, "v4_context_load_entries")
    preloads = _facts(fs, "v4_preload_positions")
    evidence = [
        f"{c.source_id}:{c.key_path} inputs={list(c.input_roles)}" for c in contracts
    ] + [
        f"entry {e.source_id}:{e.key_path} exact={e.exact} historical={e.historical_region} "
        f"excluded_material={e.excluded_material}"
        for e in entries
    ] + [
        f"preload {p.source_id}:{p.key_path} enablement={p.enablement} negated_key={p.key_is_negated}"
        for p in preloads
    ]

    if not contracts:
        return FAIL, "no minimum-effective-context derivation contract is declared", evidence

    covered: set[str] = set()
    for c in contracts:
        covered |= set(c.input_roles)
    missing = [r for r in V.A_REQUIRED_CONTEXT_INPUT_ROLES if r not in covered]
    if missing:
        return FAIL, f"context derivation does not declare A-required input(s): {missing}", evidence

    if not entries:
        return FAIL, "the contract declares no load set, so nothing is derived", evidence

    inexact = [e for e in entries if not e.exact]
    if inexact:
        shown = ", ".join(e.key_path for e in inexact[:3])
        return FAIL, f"load set entry is not exact: {shown}", evidence

    excluded = [e for e in entries if e.excluded_material]
    if excluded:
        shown = ", ".join(e.key_path for e in excluded[:3])
        return FAIL, f"load set carries material A R04 excludes: {shown}", evidence

    live_preload = [
        p for p in preloads if not p.key_is_negated and p.enablement in (ENABLED, UNKNOWN)
    ]
    if live_preload:
        shown = ", ".join(f"{p.key_path}@{p.deciding_leaf or 'self'}" for p in live_preload[:3])
        return FAIL, f"default preload is enabled: {shown}", evidence

    historical = [e for e in entries if e.historical_region and not e.exact]
    if historical:
        shown = ", ".join(e.key_path for e in historical[:3])
        return FAIL, f"historical region loaded without an exact entry: {shown}", evidence

    return (
        PASS,
        f"{len(V.A_REQUIRED_CONTEXT_INPUT_ROLES)} A-required input(s) declared; "
        f"{len(entries)} exact load entr(ies); no enabled default preload",
        evidence,
    )


# --------------------------------------------------------------------------


@v4_predicate(
    "P23",
    "every A-named change trigger forces a fresh read or stale status, never cached continuation",
    ["A05", "R05_context_freshness_and_reentry"],
)
def p23_freshness_and_reentry(fs: FactSet):
    bindings = _facts(fs, "v4_freshness_bindings")
    triggers = _facts(fs, "v4_freshness_triggers")
    evidence = [
        f"{b.source_id}:{b.key_path} fingerprint_bound={b.fingerprint_bound}" for b in bindings
    ] + [
        f"trigger {t.source_id}:{t.key_path} role={t.trigger_role} effect={t.effect_role or 'UNKNOWN'}"
        for t in triggers
    ]

    if not bindings:
        return FAIL, "no freshness or invalidation region is declared", evidence
    if not any(b.fingerprint_bound for b in bindings):
        return FAIL, "no context dependency fingerprint is bound to the window", evidence
    if not triggers:
        return FAIL, "no change trigger is declared; absence is not an invalidation rule", evidence

    covered = {t.trigger_role for t in triggers}
    missing = [r for r in V.A_REQUIRED_FRESHNESS_TRIGGERS if r not in covered]
    if missing:
        return FAIL, f"no declared trigger for A-named change(s): {missing}", evidence

    compliant = set(V.COMPLIANT_FRESHNESS_EFFECTS)
    bad = [t for t in triggers if t.effect_role not in compliant]
    if bad:
        shown = ", ".join(f"{t.key_path} -> {t.effect_role or 'UNKNOWN'}" for t in bad[:3])
        return (
            FAIL,
            f"trigger effect is neither a fresh read nor a stale status: {shown}",
            evidence,
        )

    return (
        PASS,
        f"fingerprint bound; {len(V.A_REQUIRED_FRESHNESS_TRIGGERS)} A-named trigger(s) covered, "
        f"all with a compliant effect",
        evidence,
    )


# --------------------------------------------------------------------------


@v4_predicate(
    "P24",
    "each routed window binds a receipt carrying the A-stated concepts with authority routing_only",
    ["A07", "R07_model_route_binding"],
)
def p24_route_receipt_binding(fs: FactSet):
    receipts = _facts(fs, "v4_route_receipts")
    evidence = [
        f"{r.source_id}:{r.key_path} window_bound={r.window_bound} concepts={list(r.concept_roles)} "
        f"authority_declared={r.authority_declared} routing_only={r.authority_is_routing_only}"
        for r in receipts
    ]

    if not receipts:
        return FAIL, "no model-routing receipt is bound anywhere", evidence

    unbound = [r for r in receipts if not r.window_bound]
    if unbound:
        shown = ", ".join(r.key_path for r in unbound[:3])
        return FAIL, f"receipt is not bound to a window: {shown}", evidence

    for r in receipts:
        missing = [c for c in V.A_REQUIRED_RECEIPT_CONCEPTS if c not in r.concept_roles]
        if missing:
            return (
                FAIL,
                f"receipt {r.key_path} does not carry A-required concept(s): {missing}",
                evidence,
            )
        if not r.authority_declared:
            return FAIL, f"receipt {r.key_path} declares no authority value", evidence
        if not r.authority_is_routing_only:
            return (
                FAIL,
                f"receipt {r.key_path} authority is not {V.ROUTING_ONLY_AUTHORITY_VALUE}",
                evidence,
            )

    return (
        PASS,
        f"{len(receipts)} window-bound receipt(s), each carrying "
        f"{len(V.A_REQUIRED_RECEIPT_CONCEPTS)} A-required concept(s) with "
        f"authority {V.ROUTING_ONLY_AUTHORITY_VALUE}",
        evidence,
    )


# --------------------------------------------------------------------------


@v4_predicate(
    "P25",
    "review independence is machine-checkable and obvious self-review is rejected",
    ["A08", "R08_independence_constraints"],
)
def p25_independence(fs: FactSet):
    independence = _facts(fs, "v4_independence")
    families = _facts(fs, "v4_family_requirements")
    evidence = [
        f"{i.source_id}:{i.key_path} distinct_session={i.distinct_session_enablement} "
        f"self_review_effect_declared={i.self_review_effect_declared} rejected={i.self_review_rejected}"
        for i in independence
    ] + [
        f"family {f.source_id}:{f.key_path} expressed_as_constraint={f.expressed_as_constraint}"
        for f in families
    ]

    if not independence:
        return FAIL, "no review-independence constraint is declared", evidence

    enabled = [i for i in independence if i.distinct_session_enablement == ENABLED]
    if not enabled:
        return (
            FAIL,
            "no declaration requires implementation and final review to be distinct sessions",
            evidence,
        )

    declaring = [i for i in independence if i.self_review_effect_declared]
    if not declaring:
        return (
            FAIL,
            "no declaration states what happens when obvious self-review is detected",
            evidence,
        )
    if not any(i.self_review_rejected for i in declaring):
        return (
            FAIL,
            "self-review is described but never rejected; a note is not a machine-checkable gate",
            evidence,
        )

    hard_coded = [f for f in families if not f.expressed_as_constraint]
    if hard_coded:
        shown = ", ".join(f.key_path for f in hard_coded[:3])
        return (
            FAIL,
            f"model-family requirement sits in a selection slot rather than a routing constraint: {shown}",
            evidence,
        )

    return (
        PASS,
        f"{len(enabled)} distinct-session requirement(s); self-review rejected; "
        f"{len(families)} family position(s), all expressed as routing constraints",
        evidence,
    )


# --------------------------------------------------------------------------


@v4_predicate(
    "P26",
    "the composition references the upstream mechanisms and copies none of their mutable semantics",
    ["A10", "R10_existing_mechanism_separation"],
)
def p26_mechanism_separation(fs: FactSet):
    copied = _facts(fs, "v4_mechanism_separation")
    evidence = [
        f"{c.source_id}({c.surface}):{c.key_path} upstream={c.upstream_role} "
        f"entries={c.copied_entry_count} pointer_only={c.pointer_only}"
        for c in copied
    ]
    if copied:
        shown = "; ".join(
            f"{c.key_path} copies {c.upstream_role} ({c.copied_entry_count} entries)"
            for c in copied[:3]
        )
        return FAIL, f"composition copies upstream mutable semantics: {shown}", evidence
    return (
        PASS,
        "no composition region copies an upstream mechanism's rules, catalog or evidence ledger",
        evidence,
    )


# --------------------------------------------------------------------------


@v4_predicate(
    "P27",
    "every A-named broken binding fails visibly and no silent fallback is enabled",
    ["A12", "R12_failure_surfacing"],
)
def p27_failure_surfacing(fs: FactSet):
    cases = _facts(fs, "v4_failure_cases")
    fallbacks = _facts(fs, "v4_fallback_positions")
    evidence = [
        f"case {c.source_id}:{c.key_path} role={c.case_role} declared={c.effect_declared} "
        f"visible={c.visible_failure}"
        for c in cases
    ] + [
        f"fallback {f.source_id}:{f.key_path} enablement={f.enablement} negated_key={f.key_is_negated}"
        for f in fallbacks
    ]

    if not cases:
        return FAIL, "the validation design declares no failure case", evidence

    covered = {c.case_role for c in cases}
    missing = [r for r in V.A_REQUIRED_FAILURE_CASES if r not in covered]
    if missing:
        return FAIL, f"validation design omits A-required failure case(s): {missing}", evidence

    silent = [c for c in cases if not c.visible_failure]
    if silent:
        shown = ", ".join(f"{c.key_path} ({c.case_role})" for c in silent[:3])
        return FAIL, f"failure case does not fail visibly: {shown}", evidence

    live_fallback = [
        f for f in fallbacks if not f.key_is_negated and f.enablement in (ENABLED, UNKNOWN)
    ]
    if live_fallback:
        shown = ", ".join(f"{f.key_path}@{f.deciding_leaf or 'self'}" for f in live_fallback[:3])
        return FAIL, f"a silent fallback is enabled: {shown}", evidence

    # T2-PARENT-IR-002. A R12 requires a missing or invalid routing receipt to
    # fail visibly with no arbitrary-model fallback. The candidate declared that
    # policy and nothing read it, so flipping it to `best_effort` left all
    # fourteen predicates passing. The policy is now decision-bearing here:
    # absent, unknown, inverted, `continue_cached` and anything else that is not
    # the accepted visible-failure role are all non-pass, and none of that is a
    # blacklist of one spelling.
    receipts = _facts(fs, "v4_route_receipts")
    evidence += [
        f"route_receipt {r.source_id}:{r.key_path} failure_policy_declared="
        f"{r.failure_policy_declared} role={r.failure_policy_role or 'unresolved'}"
        for r in receipts
    ]
    undeclared = [r for r in receipts if not r.failure_policy_declared]
    if undeclared:
        shown = ", ".join(r.key_path for r in undeclared[:3])
        return (
            FAIL,
            f"route receipt declares no missing/stale/inconsistent policy: {shown}",
            evidence,
        )
    not_visible = [
        r for r in receipts if r.failure_policy_role != V.ROUTE_RECEIPT_VISIBLE_FAILURE_ROLE
    ]
    if not_visible:
        shown = ", ".join(
            f"{r.key_path} -> {r.failure_policy_role or 'unresolved'}" for r in not_visible[:3]
        )
        return (
            FAIL,
            f"route-receipt failure policy is not a visible failure: {shown}",
            evidence,
        )

    return (
        PASS,
        f"{len(V.A_REQUIRED_FAILURE_CASES)} A-required failure case(s) covered, each failing "
        f"visibly; {len(fallbacks)} fallback position(s), none enabled",
        evidence,
    )
