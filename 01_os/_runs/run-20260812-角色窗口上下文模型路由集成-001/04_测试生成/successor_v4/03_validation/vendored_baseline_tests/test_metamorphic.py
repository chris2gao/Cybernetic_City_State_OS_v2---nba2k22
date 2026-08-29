"""Metamorphic and property tests.

Mutation testing answers "is this change caught".  These answer the question
three review generations were actually lost to:

    equivalent meaning  -> equivalent acceptance result
    different meaning   -> different acceptance result

An invariance test compares the FULL result vector, not just the predicate the
transformation targets, so a transformation cannot fix one predicate while
quietly perturbing another.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import _bootstrap
from _bootstrap import BASELINE

from semantic_acceptance.corpus import METAMORPHIC, copy_tree
from semantic_acceptance.evaluate import evaluate_tree, overall, result_vector
from semantic_acceptance.predicates import FAIL, PASS


def baseline_vector() -> dict[str, str]:
    return result_vector(evaluate_tree(BASELINE))


def run_metamorphic(td: Path, mt) -> dict:
    tree = copy_tree(BASELINE, td / mt.name)
    mt.transform(tree)
    results = evaluate_tree(tree)
    vec = result_vector(results)
    base = baseline_vector()
    if mt.expectation == "invariant":
        holds = vec == base
        note = "" if holds else f"changed: { {k: (base.get(k), v) for k, v in vec.items() if base.get(k) != v} }"
    else:
        deciding = {p: vec.get(p) for p in mt.deciding_predicates}
        holds = overall(results) == FAIL and any(v == FAIL for v in deciding.values())
        note = "" if holds else f"expected a fail on {mt.deciding_predicates}, got {deciding}"
    return {
        "name": mt.name,
        "property_id": mt.property_id,
        "description": mt.description,
        "expectation": mt.expectation,
        "baseline_vector": base,
        "variant_vector": vec,
        "holds": holds,
        "note": note,
        "failure_details": [f"{r.predicate_id}: {r.detail}" for r in results if r.status != PASS],
    }


def test_all_metamorphic_properties_hold():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        broken = []
        for mt in METAMORPHIC:
            got = run_metamorphic(root, mt)
            if not got["holds"]:
                broken.append(f"{mt.name} ({mt.property_id}): {got['note']}")
        assert broken == [], broken


def test_every_required_property_family_is_covered():
    """The eight property families named in the dispatch, all present."""
    required = {
        "container-shape invariance",
        "ordering invariance",
        "unknown-provider-name invariance",
        "negative-vs-positive polarity correctness",
        "reference-vs-ownership distinction",
        "mention-vs-grant distinction",
        "pointer-vs-mutable-state distinction",
        "optional-B-field removal invariance",
    }
    covered = {mt.property_id for mt in METAMORPHIC}
    missing = required - covered
    # normative-selector vs provenance is an additional family this run added.
    assert not missing, missing


def write_results(out_path: Path) -> dict:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        rows = [run_metamorphic(root, mt) for mt in METAMORPHIC]
    report = {
        "corpus": "metamorphic_and_property",
        "total": len(rows),
        "holding": sum(1 for r in rows if r["holds"]),
        "property_families": sorted({r["property_id"] for r in rows}),
        "properties": rows,
    }
    out_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return report


if __name__ == "__main__":
    test_all_metamorphic_properties_hold()
    test_every_required_property_family_is_covered()
    print("metamorphic corpus ok")
