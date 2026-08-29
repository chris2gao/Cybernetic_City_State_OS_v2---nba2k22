#!/usr/bin/env python3
"""Adapter applicability negative tests.  P2-2 work item 1.

Every v4 adapter passes through one gate, `adapters_v4._applicable`, which
requires a parsed YAML document with a mapping root on a declaring surface.
The suite already measures at length what the adapters DO claim.  Nothing
measured whether they stay out of documents they do NOT claim, and an adapter
that quietly reaches into an unclaimed document would make an unowned surface
look compliant - the same shape of defect as V4-FND-01, arriving from the
other direction.

Two things have to be true for a negative test like this to mean anything:

  1. the payload must be fact-bearing, or "produced nothing" is trivial.  The
     source document here is the one baseline_v4 document that the adapters
     demonstrably do read, asserted below rather than assumed;
  2. the emptiness must come from the GATE and not from the shape of the
     mutation.  `test_the_gate_is_what_produces_the_inertness` removes the
     gate and shows the same documents then produce output.  Without that
     control these tests would pass just as happily against an adapter set
     that had no applicability rule at all.

01_os/开发入口与单窗口任务规范_v1.md#1.2: imported by module name after the
`sys.path` insert `_bootstrap_v4` performs; this directory is not a package.
"""

from __future__ import annotations

import dataclasses

import _bootstrap_v4  # noqa: F401  - performs the sys.path insert
from _bootstrap_v4 import BASELINE_V4

from semantic_acceptance.decision_facts import EvidenceSet
from semantic_acceptance.facts import build_fact_set
from semantic_acceptance.vocabulary import DECLARING_SURFACES
from semantic_acceptance_v4 import adapters_v4 as A


# Every adapter `augment_fact_set` calls, in that order.  Kept explicit rather
# than discovered by `dir()`: a new adapter that nobody added here should show
# up as a gap in `test_this_list_covers_every_adapter_the_pipeline_calls`,
# not be silently skipped by a clever loop.
ADAPTERS = (
    ("adapt_lifecycle", A.adapt_lifecycle),
    ("adapt_lifecycle_conditions", A.adapt_lifecycle_conditions),
    ("adapt_context_contract", A.adapt_context_contract),
    ("adapt_context_load_entries", A.adapt_context_load_entries),
    ("adapt_preload_positions", A.adapt_preload_positions),
    ("adapt_freshness_binding", A.adapt_freshness_binding),
    ("adapt_freshness_triggers", A.adapt_freshness_triggers),
    ("adapt_route_receipts", A.adapt_route_receipts),
    ("adapt_independence", A.adapt_independence),
    ("adapt_family_requirements", A.adapt_family_requirements),
    ("adapt_mechanism_separation", A.adapt_mechanism_separation),
    ("adapt_failure_cases", A.adapt_failure_cases),
    ("adapt_fallback_positions", A.adapt_fallback_positions),
    ("adapt_v4_ambiguities", A.adapt_v4_ambiguities),
)

# Deliberately not "other".  "other" is a real value `_surface_of` returns, and
# a test that used it would be measuring one production value rather than the
# membership rule.  This string cannot appear in any surface declaration, and
# `test_the_non_declaring_surface_really_is_not_declared` proves it.
NON_DECLARING_SURFACE = "surface_that_no_declaration_can_name_" + "x" * 8

_CACHE: dict[str, object] = {}


def _documents():
    if "documents" not in _CACHE:
        _CACHE["documents"] = list(build_fact_set(BASELINE_V4).documents)
    return _CACHE["documents"]


def _run_all(doc):
    """Every adapter against one document.  Returns (facts, evidence_count)."""
    ev = EvidenceSet()
    produced: list[tuple[str, int]] = []
    for name, fn in ADAPTERS:
        produced.append((name, len(fn(doc, ev))))
    return produced, len(ev)


def _fact_bearing_document():
    """The baseline_v4 document these adapters demonstrably read.

    Chosen by measurement, not by name: whichever applicable document yields the
    most facts.  If the corpus changes shape the test follows it instead of
    quietly measuring an empty document.
    """
    if "bearing" not in _CACHE:
        best = None
        for doc in _documents():
            if not A._applicable(doc):
                continue
            produced, _ = _run_all(doc)
            total = sum(n for _, n in produced)
            if best is None or total > best[1]:
                best = (doc, total)
        _CACHE["bearing"] = best
    return _CACHE["bearing"]


def _variants():
    """The four ways a document can fail `_applicable`, each from a real doc."""
    doc, _ = _fact_bearing_document()
    return (
        ("not_yaml", dataclasses.replace(doc, fmt="markdown")),
        ("not_parsed", dataclasses.replace(doc, parse_error="deliberate parse failure")),
        ("root_not_a_mapping", dataclasses.replace(doc, data=[doc.data])),
        ("surface_not_declaring", dataclasses.replace(doc, surface=NON_DECLARING_SURFACE)),
    )


# ---------------------------------------------------------------------------
# guards: without these the negatives below could pass vacuously
# ---------------------------------------------------------------------------


def test_this_list_covers_every_adapter_the_pipeline_calls():
    """ADAPTERS must be the same set `augment_fact_set` invokes."""
    from semantic_acceptance_v4 import evaluate_v4

    import inspect

    body = inspect.getsource(evaluate_v4.augment_fact_set)
    called = {name for name in dir(A) if name.startswith("adapt_") and f"A.{name}(" in body}
    listed = {name for name, _ in ADAPTERS}
    assert called == listed, {"called_but_not_listed": sorted(called - listed),
                              "listed_but_not_called": sorted(listed - called)}


def test_the_non_declaring_surface_really_is_not_declared():
    assert NON_DECLARING_SURFACE not in DECLARING_SURFACES, NON_DECLARING_SURFACE


def test_the_source_document_is_fact_bearing_when_applicable():
    """If this document produced nothing, every negative below would be empty air."""
    found = _fact_bearing_document()
    assert found is not None, "no applicable document in baseline_v4"
    doc, total = found
    assert total > 0, f"{doc.rel_path} produced no v4 facts; negatives would be vacuous"


def test_the_source_document_passes_the_gate():
    doc, _ = _fact_bearing_document()
    assert A._applicable(doc) is True, doc.rel_path


# ---------------------------------------------------------------------------
# the negatives
# ---------------------------------------------------------------------------


def test_the_gate_rejects_each_non_applicable_variant():
    bad = [name for name, doc in _variants() if A._applicable(doc)]
    assert bad == [], bad


def test_no_adapter_produces_a_fact_for_a_document_it_does_not_claim():
    bad = []
    for variant, doc in _variants():
        for name, count in _run_all(doc)[0]:
            if count:
                bad.append(f"{variant}:{name}={count}")
    assert bad == [], bad


def test_no_adapter_writes_evidence_for_a_document_it_does_not_claim():
    """Silence has to be total.

    An adapter that returned no facts but still recorded a rendering
    observation would put an unclaimed document into the evidence ledger, and
    a later reader would reasonably take its presence there as ownership.
    """
    bad = []
    for variant, doc in _variants():
        _, evidence = _run_all(doc)
        if evidence:
            bad.append(f"{variant}:{evidence} observations")
    assert bad == [], bad


# ---------------------------------------------------------------------------
# the control that makes the negatives mean something
# ---------------------------------------------------------------------------


def test_the_gate_is_what_produces_the_inertness():
    """Remove the gate; the same document must stop being inert.

    This is the difference between "these adapters decline this document" and
    "this mutation happens to yield nothing".  Only the surface variant is used:
    its data is still a parsed mapping, so the adapters can run normally and any
    output is attributable to the gate alone rather than to a crash.
    """
    doc = dict(_variants())["surface_not_declaring"]

    before_facts, before_evidence = _run_all(doc)
    assert sum(n for _, n in before_facts) == 0 and before_evidence == 0

    original = A._applicable
    try:
        A._applicable = lambda _doc: True
        after_facts, after_evidence = _run_all(doc)
    finally:
        A._applicable = original

    assert A._applicable is original
    produced = sum(n for _, n in after_facts)
    assert produced > 0 or after_evidence > 0, (
        "with the gate removed the adapters still produced nothing, so the "
        "negative tests above prove nothing about the gate"
    )
