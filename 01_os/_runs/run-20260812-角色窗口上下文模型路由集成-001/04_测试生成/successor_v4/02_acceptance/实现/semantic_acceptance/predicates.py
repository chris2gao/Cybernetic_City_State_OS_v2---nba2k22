#!/usr/bin/env python3
"""A-level requirement predicates over typed decision facts.

Trace: 03_语义模型/requirement_traceability_v1.yml
Provenance of every constant these predicates rest on: semantic_acceptance/provenance.py

The independent review found this file reading `source_container`, `source_form`
and `entry_forms` — rendering evidence that records how an artifact was written.
Those fields no longer exist on any decision fact (`decision_facts.py`), so the
violation is now impossible rather than discouraged, and
`test_representation_boundary.py` asserts that this module's source text contains
no reference to any of them.

A predicate receives a FactSet and returns PASS / FAIL / UNSUPPORTED.  No
predicate opens a file, sees a container type, sees a file name or sees a vendor
name.  Nothing in this file enumerates a subject: the closest it comes is
counting how many sources own a thing, which is what A01 asks.
"""

from __future__ import annotations

from dataclasses import dataclass, field as dc_field
from typing import Callable

from .core import ENABLED, NEGATIVE, UNKNOWN, tokens
from .facts import FactSet
from .provenance import rule
from .decision_facts import (
    AUTHORITY_GRANT,
    LATEST_ALLOWED,
    MUTABLE_DELIVERY_STATE,
    NORMATIVE_SELECTOR,
    OWNS_SEMANTICS,
    PRIVATE_REASONING,
)
from .vocabulary import (
    A_REQUIRED_IDENTITY_FACTS,
    B_ONLY_IDENTITY_FACTS,
    DELIVERY_STATE_TOKENS,
    EXACT_PREDECESSOR_MATCH,
    PRIVATE_REASONING_TOKENS,
    ROLE_OWNER_REQUIRED_SURFACE,
)

PREDICATE_OUTCOMES = tuple(
    rule(
        "V-FACT-08",
        kind="mapping",
        authority="C-08 end_to_end_semantic_boundary",
        interpretation="The exhaustive externally visible outcomes of an A-level predicate.",
        value=("pass", "fail", "unsupported_or_ambiguous_representation"),
    )
)
PASS, FAIL, UNSUPPORTED = PREDICATE_OUTCOMES


@dataclass
class PredicateResult:
    predicate_id: str
    title: str
    a_trace: list[str]
    status: str
    detail: str
    evidence: list[str] = dc_field(default_factory=list)

    @property
    def passed(self) -> bool:
        return self.status == PASS


REGISTRY: dict[str, tuple[str, list[str], Callable[[FactSet], PredicateResult]]] = {}


def predicate(pid: str, title: str, a_trace: list[str]):
    def deco(fn):
        def wrapper(fs: FactSet) -> PredicateResult:
            status, detail, evidence = fn(fs)
            return PredicateResult(pid, title, a_trace, status, detail, evidence)

        REGISTRY[pid] = (title, a_trace, wrapper)
        return wrapper

    return deco


# --------------------------------------------------------------------------


@predicate(
    "P01",
    "exactly one document owns role semantics; pointer-only role references are permitted",
    ["A01", "R01_role_contract", "R11_workflow_and_entry_thinness"],
)
def p01_single_role_source(fs: FactSet):
    owning: dict[str, list[str]] = {}
    referencing: dict[str, list[str]] = {}
    surfaces: dict[str, str] = {}
    for role in fs.roles:
        target = owning if role.ownership == OWNS_SEMANTICS else referencing
        target.setdefault(role.source_id, []).append(role.role_id)
        surfaces[role.source_id] = role.surface

    evidence = [
        f"{doc}: owns_semantics roles={sorted(rs)}" for doc, rs in sorted(owning.items())
    ] + [f"{doc}: references_only roles={sorted(rs)}" for doc, rs in sorted(referencing.items())]

    if not owning:
        return FAIL, "no document owns role semantics", evidence
    if len(owning) > 1:
        return (
            FAIL,
            f"{len(owning)} documents own role semantics: {sorted(owning)}",
            evidence,
        )
    owner_doc = next(iter(owning))
    surface = surfaces.get(owner_doc)
    if surface != ROLE_OWNER_REQUIRED_SURFACE:
        return (
            FAIL,
            f"the single role source is on the {surface} surface, not the mechanism surface",
            evidence,
        )
    return (
        PASS,
        f"single role source {owner_doc}; {len(referencing)} pointer-only reference document(s)",
        evidence,
    )


# --------------------------------------------------------------------------


@predicate(
    "P02",
    "window identity binds the A-stated facts and fresh/reentry are distinguishable",
    ["A02", "R02_window_identity"],
)
def p02_window_identity(fs: FactSet):
    if not fs.window_identities:
        return FAIL, "no window identity block found", []
    evidence: list[str] = []
    for wi in fs.window_identities:
        evidence.append(f"{wi.source_id}.{wi.key_path}: bound={list(wi.bound_facts)}")
        missing = [f for f in A_REQUIRED_IDENTITY_FACTS if f not in wi.bound_facts]
        if missing:
            return FAIL, f"window identity does not bind A-required facts: {missing}", evidence
        if wi.latest_session_pointer_status == LATEST_ALLOWED:
            return FAIL, "a latest-session pointer is usable as formal identity", evidence
        if wi.b_only_facts:
            evidence.append(
                f"{wi.source_id}: B_ONLY facts present and ignored for acceptance: "
                f"{list(wi.b_only_facts)}"
            )

    fresh = [m for m in fs.entry_modes if m.is_fresh]
    reentry = [m for m in fs.entry_modes if m.is_reentry]
    for m in fs.entry_modes:
        evidence.append(
            f"{m.source_id}.{m.key_path}: fresh={m.is_fresh} reentry={m.is_reentry} "
            f"predecessor_required={m.predecessor_required} match={m.predecessor_match}"
        )
    if not fresh:
        return FAIL, "no fresh entry mode", evidence
    if not reentry:
        return FAIL, "no reentry entry mode", evidence
    for m in reentry:
        if not m.predecessor_required:
            return FAIL, f"reentry mode {m.mode_id} does not require a predecessor", evidence
        if m.predecessor_match != EXACT_PREDECESSOR_MATCH:
            return (
                FAIL,
                f"reentry mode {m.mode_id} predecessor match is {m.predecessor_match!r}, "
                f"not {EXACT_PREDECESSOR_MATCH}",
                evidence,
            )
    return (
        PASS,
        f"identity binds {A_REQUIRED_IDENTITY_FACTS}; {len(fresh)} fresh and "
        f"{len(reentry)} reentry mode(s) with exact predecessor",
        evidence,
    )


# --------------------------------------------------------------------------


@predicate(
    "P03",
    "no positive normative provider selector in the role architecture",
    ["A06", "R06_role_to_model_requirements", "R08_independence_constraints"],
)
def p03_provider_independence(fs: FactSet):
    evidence = [
        f"{b.source_id}:{b.key_path} kind={b.selector_kind} polarity={b.polarity} "
        f"label={b.provider_label!r}"
        for b in fs.provider_bindings
    ]
    offenders = [b for b in fs.provider_bindings if b.selector_kind == NORMATIVE_SELECTOR]
    if offenders:
        shown = ", ".join(f"{b.key_path}={b.provider_label!r}" for b in offenders[:3])
        return FAIL, f"provider pinned by a normative selector: {shown}", evidence
    kinds = sorted({b.selector_kind for b in fs.provider_bindings})
    return (
        PASS,
        f"{len(fs.provider_bindings)} provider binding(s), none a normative selector; kinds={kinds}",
        evidence,
    )


# --------------------------------------------------------------------------


def _matches(field: str, vocab) -> bool:
    return bool(set(tokens(field)) & vocab)


@predicate(
    "P04",
    "handoff declares the prohibitions AND carries no mutable delivery or reasoning state",
    ["A09", "R09_structured_handoff"],
)
def p04_handoff_payload(fs: FactSet):
    evidence = [
        f"decl {d.source_id}:{d.key_path} field={d.field!r} polarity={d.polarity}"
        for d in fs.declarations
    ] + [
        f"carried {c.source_id}:{c.key_path} field={c.field!r} kind={c.kind}"
        for c in fs.carried_fields
    ]

    negatives = [d for d in fs.declarations if d.polarity == NEGATIVE]
    if not negatives:
        return FAIL, "the handoff declares no prohibitions in any form", evidence
    if not any(_matches(d.field, PRIVATE_REASONING_TOKENS) for d in negatives):
        return (
            FAIL,
            f"no private-reasoning prohibition; declared={sorted({d.field for d in negatives})}",
            evidence,
        )
    if not any(_matches(d.field, DELIVERY_STATE_TOKENS) for d in negatives):
        return (
            FAIL,
            f"no delivery/read/acceptance prohibition; declared={sorted({d.field for d in negatives})}",
            evidence,
        )

    # Independently of every declaration above:
    carried = [
        c for c in fs.carried_fields if c.kind in (MUTABLE_DELIVERY_STATE, PRIVATE_REASONING)
    ]
    if carried:
        shown = ", ".join(f"{c.key_path} ({c.kind})" for c in carried[:3])
        return FAIL, f"the handoff payload carries prohibited state: {shown}", evidence
    return (
        PASS,
        f"{len(negatives)} prohibition(s) declared and no prohibited field carried",
        evidence,
    )


# --------------------------------------------------------------------------


@predicate(
    "P05",
    "the composition grants no authority",
    ["A13", "R13_no_authority_escalation", "R01_role_contract"],
)
def p05_no_authority_grant(fs: FactSet):
    evidence = [
        f"{a.source_id}:{a.key_path} kind={a.kind} enablement={a.enablement} "
        f"deciding_leaf={a.deciding_leaf!r}"
        for a in fs.authority
    ]
    grants = [a for a in fs.authority if a.kind == AUTHORITY_GRANT]
    if grants:
        shown = ", ".join(f"{a.key_path}@{a.deciding_leaf or 'self'}" for a in grants[:3])
        return FAIL, f"authority granted: {shown}", evidence
    return PASS, f"{len(fs.authority)} authority position(s), none a grant", evidence


# --------------------------------------------------------------------------


@predicate(
    "P06",
    "no automatic progression, delivery, spawn, scheduler, watcher or daemon is enabled",
    ["A14", "R14_Human_triggered_progression"],
)
def p06_no_automation(fs: FactSet):
    evidence = [
        f"{a.source_id}:{a.key_path} behaviour={a.behaviour} enablement={a.enablement} "
        f"negated_key={a.key_is_negated} deciding_leaf={a.deciding_leaf!r}"
        for a in fs.autonomy
    ]
    if not fs.autonomy:
        return FAIL, "no autonomy position is declared anywhere; absence is not a denial", evidence
    live = [
        a for a in fs.autonomy if not a.key_is_negated and a.enablement in (ENABLED, UNKNOWN)
    ]
    if live:
        shown = ", ".join(f"{a.key_path}@{a.deciding_leaf or 'self'}" for a in live[:3])
        return FAIL, f"autonomous behaviour enabled: {shown}", evidence
    return PASS, f"{len(fs.autonomy)} autonomy position(s), none enabled", evidence


# --------------------------------------------------------------------------


@predicate(
    "P07",
    "the workflow and entry surface holds no second mutable catalog",
    ["A11", "R11_workflow_and_entry_thinness", "R10_existing_mechanism_separation"],
)
def p07_no_second_catalog(fs: FactSet):
    """A11 states no size exception, so this predicate applies none.

    The v1 candidate carried `CATALOG_RESTATEMENT_THRESHOLD = 3`, which let a
    two-entry authoritative mutable catalog pass (S43).  The independent review
    named that constant as the proof of AB-02.  It is deleted; what remains is
    `CATALOG_MIN_ENTRIES = 2`, which is not a tolerance but the definition of a
    collection, and is traced at vocabulary.V-CAT-01.
    """
    evidence = [
        f"{c.source_id}: detector={c.detector} entries={c.entry_count} "
        f"restated={list(c.identifiers_restated)[:4]}"
        for c in fs.catalogs
    ]
    if fs.catalogs:
        shown = "; ".join(
            f"{c.source_id} ({c.detector}, {c.entry_count} entries)" for c in fs.catalogs[:3]
        )
        return FAIL, f"second mutable catalog: {shown}", evidence
    return (
        PASS,
        f"{len(fs.live_catalog_identifiers)} live identifiers checked; no second catalog claim",
        evidence,
    )


# --------------------------------------------------------------------------


def evaluate_all(fs: FactSet) -> list[PredicateResult]:
    results = [wrapper(fs) for _, (_, _, wrapper) in sorted(REGISTRY.items())]
    for u in fs.unsupported:
        results.append(
            PredicateResult(
                "P00",
                "every discovered document is interpretable",
                [],
                UNSUPPORTED,
                f"{u.source_id}: {u.reason}",
                [u.key_path],
            )
        )
    for r in fs.untraced_rules:
        # C-09: a decision rule without authority is reported, never applied.
        results.append(
            PredicateResult(
                "P09",
                "every decision-bearing rule has an A or Human authority",
                ["C-09"],
                UNSUPPORTED,
                f"{r.rule_id} ({r.kind}) has no traced authority: {r.interpretation}",
                [r.rule_id],
            )
        )
    return results
