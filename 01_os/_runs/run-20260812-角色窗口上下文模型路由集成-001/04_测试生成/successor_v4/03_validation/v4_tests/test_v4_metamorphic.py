"""Metamorphic, poisoned-vocabulary, polarity and double-negation tests for v4.

An invariance case compares the FULL fourteen-entry result vector, not just the
predicate the transformation targets.  Comparing only the target would let a
transformation fix one predicate while quietly perturbing another - the failure
mode the accepted corpus documents and the reason it does the same.

A difference case has to fail *on its own deciding predicate*.  "It failed" is
not the proposition; "it failed for the reason it was built to probe" is.  With
fourteen predicates there are thirteen other ways to be red by accident.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path
from typing import Any

import _bootstrap_v4
from _bootstrap_v4 import BASELINE_V4

import corpus_v4
from corpus_v4 import (
    DIFFERENCES,
    INVARIANTS,
    OPEN_HOLES,
    OPEN_INVARIANCE_HOLES,
    copy_tree,
)

OPEN_INVARIANCE_NAMES = {h.name for h in OPEN_INVARIANCE_HOLES}

from semantic_acceptance.evaluate import overall
from semantic_acceptance.predicates import FAIL, PASS, UNSUPPORTED
from semantic_acceptance_v4.evaluate_v4 import evaluate_full, result_vector

V4_PREDICATES = ("P21", "P22", "P23", "P24", "P25", "P26", "P27")


def baseline_vector() -> dict[str, str]:
    return result_vector(evaluate_full(BASELINE_V4))


def run_invariant(td: Path, case) -> dict[str, Any]:
    tree = copy_tree(BASELINE_V4, td / case.name)
    case.transform(tree)
    vec = result_vector(evaluate_full(tree))
    base = baseline_vector()
    moved = {k: (base.get(k), v) for k, v in vec.items() if base.get(k) != v}
    return {
        "name": case.name,
        "property_id": case.property_id,
        "description": case.description,
        "expectation": "invariant",
        "holds": not moved,
        "moved": moved,
        "vector": vec,
    }


def run_difference(td: Path, case) -> dict[str, Any]:
    tree = copy_tree(BASELINE_V4, td / case.name)
    case.transform(tree)
    results = evaluate_full(tree)
    vec = result_vector(results)
    deciding = {p: vec.get(p) for p in case.deciding_predicates}
    holds = overall(results) != PASS and any(v == FAIL for v in deciding.values())
    return {
        "name": case.name,
        "attack_class": case.attack_class,
        "description": case.description,
        "expectation": "difference",
        "deciding_predicates": list(case.deciding_predicates),
        "deciding_results": deciding,
        "overall": overall(results),
        "holds": holds,
        "vector": vec,
        "nonpass": [f"{r.predicate_id}({r.status}): {r.detail}" for r in results if r.status != PASS],
    }


def _all_invariants() -> list[dict[str, Any]]:
    with tempfile.TemporaryDirectory() as td:
        return [run_invariant(Path(td), c) for c in INVARIANTS]


def _all_differences() -> list[dict[str, Any]]:
    with tempfile.TemporaryDirectory() as td:
        return [run_difference(Path(td), c) for c in DIFFERENCES]


def test_baseline_v4_is_conforming_before_any_transformation():
    """Every case below is meaningless if the base tree is not green."""
    base = baseline_vector()
    assert len(base) == 14, base
    nonpass = {k: v for k, v in base.items() if v != PASS}
    assert nonpass == {}, nonpass


def test_all_invariance_properties_hold():
    """Excluding the four recorded as open under V4-FND-02 and V4-FND-04.

    The exclusions are named individually rather than by a blanket allowance, so
    a fifth broken invariant is a failure rather than a quiet addition to a
    tolerated set.
    """
    broken = [
        f"{r['name']} ({r['property_id']}): {r['moved']}"
        for r in _all_invariants()
        if not r["holds"] and r["name"] not in OPEN_INVARIANCE_NAMES
    ]
    assert broken == [], broken


def test_recorded_invariance_holes_are_still_open():
    """Same direction-of-measurement discipline as test_known_open_holes.

    An invariance case here is a representation change with no change of
    meaning that nevertheless moves a predicate. That is RC-01 reappearing
    inside the v4 adapters, and it is freeze-blocking; the finding files carry
    that status. This test only keeps the description true.
    """
    rows = {r["name"]: r for r in _all_invariants()}
    closed = []
    for hole in OPEN_INVARIANCE_HOLES:
        row = rows[hole.name]
        if row["holds"]:
            closed.append(f"{hole.name} ({hole.finding_id}) now holds")
        elif hole.predicate_that_moves not in row["moved"]:
            closed.append(
                f"{hole.name}: expected {hole.predicate_that_moves} to move, moved={row['moved']}"
            )
    assert closed == [], (
        "update corpus_v4.OPEN_INVARIANCE_HOLES, the finding file and this test "
        f"together: {closed}"
    )


def test_all_difference_cases_fail_on_their_deciding_predicate():
    rows = _all_differences()
    broken = [
        f"{r['name']} ({r['attack_class']}): overall={r['overall']} "
        f"deciding={r['deciding_results']} nonpass={r['nonpass']}"
        for r in rows
        if not r["holds"]
    ]
    assert broken == [], broken


def test_every_attack_class_is_represented():
    """The classes the dispatch names, present rather than assumed."""
    required = {"poisoned_vocabulary", "polarity_inversion", "double_negation"}
    covered = {c.attack_class for c in DIFFERENCES}
    assert required <= covered, required - covered


def test_every_v4_predicate_is_probed_by_at_least_one_difference_case():
    """A predicate no adversarial case can move has not been tested.

    This is the check that would have caught a predicate wired to a region
    nothing in the corpus touches: it would be green in every run and prove
    nothing.
    """
    probed = {p for c in DIFFERENCES for p in c.deciding_predicates}
    missing = [p for p in V4_PREDICATES if p not in probed]
    assert missing == [], missing


def test_difference_cases_do_not_rely_on_unsupported():
    """A difference case must FAIL, not merely become uninterpretable.

    UNSUPPORTED is a legitimate outcome for an ambiguous representation, but a
    corpus that reaches its verdicts through UNSUPPORTED has stopped
    distinguishing "this is wrong" from "I could not tell".
    """
    rows = _all_differences()
    weak = [
        f"{r['name']}: deciding={r['deciding_results']}"
        for r in rows
        if not any(v == FAIL for v in r["deciding_results"].values())
        and any(v == UNSUPPORTED for v in r["deciding_results"].values())
    ]
    assert weak == [], weak


def test_no_invariant_transformation_silently_removes_a_predicate():
    """An invariance case must still return all fourteen predicates."""
    bad = [f"{r['name']}: {sorted(r['vector'])}" for r in _all_invariants() if len(r["vector"]) != 14]
    assert bad == [], bad


def _run_open_hole(td: Path, hole) -> dict[str, Any]:
    tree = copy_tree(BASELINE_V4, td / hole.name)
    hole.transform(tree)
    results = evaluate_full(tree)
    vec = result_vector(results)
    return {
        "name": hole.name,
        "finding_id": hole.finding_id,
        "kind": hole.kind,
        "description": hole.description,
        "predicate": hole.predicate,
        "expected_by_requirement": hole.required_by,
        "observed_status": vec.get(hole.predicate),
        "overall": overall(results),
        "still_open": vec.get(hole.predicate) == PASS,
        "why_it_matters": hole.why_it_matters,
    }


def _all_open_holes() -> list[dict[str, Any]]:
    with tempfile.TemporaryDirectory() as td:
        return [_run_open_hole(Path(td), h) for h in OPEN_HOLES]


def test_known_open_holes_are_still_open():
    """Asserted in the direction it measures, on purpose.

    Each of these transformations SHOULD be caught and currently is not.  This
    test pins the present behaviour so the corpus states something true, and so
    that closing a hole turns it red and forces the table, the finding file and
    this test to be updated in the same change.  A suite that silently dropped
    its failing cases would be green and would be lying - which is the exact
    failure ST04-V3 was lost to.

    Freeze-blocking status lives in the finding files, not here.  This test
    passing does NOT mean the package is sound; it means the package's soundness
    is accurately described.
    """
    rows = _all_open_holes()
    closed = [f"{r['name']} ({r['finding_id']}): {r['predicate']}={r['observed_status']}" for r in rows if not r["still_open"]]
    assert closed == [], (
        "a hole recorded as open is now closed; update corpus_v4.OPEN_HOLES, the "
        f"finding file and this test together: {closed}"
    )


def test_open_holes_are_each_backed_by_a_finding_file():
    """A hole with no written finding is a hole nobody will act on."""
    findings_dir = _bootstrap_v4.SUCCESSOR_V4_ROOT / "03_validation" / "findings"
    missing = []
    for hole in OPEN_HOLES:
        if not list(findings_dir.glob(f"{hole.finding_id}_*.yml")):
            missing.append(hole.finding_id)
    assert missing == [], missing


def test_false_pass_holes_are_distinguished_from_observations():
    """The two kinds must not be blurred; only one is a false verdict.

    The false-pass list is now empty. V4-FND-02 closed under ruling F02-A and
    V4-FND-03 under ruling F03-D, and each closure turned
    `test_known_open_holes_are_still_open` red first, which is what forced this
    line to be updated in the same change rather than drifting behind the code.

    Empty here means "no false verdict is currently RECORDED", which is a much
    narrower claim than "no false verdict exists". The two remaining entries are
    `declared_but_unread` observations, not false passes, and V4-OBS-03 is
    reported to the foreground rather than carried here because it sits in the
    vendored accepted engine, outside this package's write boundary.
    """
    kinds = {h.kind for h in OPEN_HOLES}
    assert kinds <= {"false_pass", "declared_but_unread"}, kinds
    false_pass = [h.finding_id for h in OPEN_HOLES if h.kind == "false_pass"]
    assert sorted(false_pass) == [], false_pass


def test_invariance_holes_are_each_backed_by_a_finding_file():
    findings_dir = _bootstrap_v4.SUCCESSOR_V4_ROOT / "03_validation" / "findings"
    missing = [
        h.finding_id
        for h in OPEN_INVARIANCE_HOLES
        if not list(findings_dir.glob(f"{h.finding_id}_*.yml"))
    ]
    assert missing == [], missing


def write_results(out_path: Path) -> dict[str, Any]:
    inv = _all_invariants()
    dif = _all_differences()
    rows_by_name = {r["name"]: r for r in inv}
    report = {
        "corpus": "successor_v4_metamorphic_and_adversarial",
        "fixture_root": "02_acceptance/fixtures/baseline_v4",
        "evaluator": "semantic_acceptance_v4.evaluate_v4.evaluate_full",
        "invariants": {
            "total": len(inv),
            "holding": sum(1 for r in inv if r["holds"]),
            "property_families": sorted({r["property_id"] for r in inv}),
            "cases": inv,
        },
        "differences": {
            "total": len(dif),
            "holding": sum(1 for r in dif if r["holds"]),
            "attack_classes": sorted({r["attack_class"] for r in dif}),
            "predicates_probed": sorted({p for c in DIFFERENCES for p in c.deciding_predicates}),
            "cases": dif,
        },
        "open_holes": {
            "total": len(OPEN_HOLES),
            "false_pass": sum(1 for h in OPEN_HOLES if h.kind == "false_pass"),
            "declared_but_unread": sum(1 for h in OPEN_HOLES if h.kind == "declared_but_unread"),
            "cases": _all_open_holes(),
            "meaning": (
                "transformations that SHOULD be caught and are not. This package "
                "is not sound while a false_pass entry remains open; the suite "
                "being green means the description is accurate, not that the "
                "holes are closed."
            ),
        },
        "open_invariance_holes": {
            "total": len(OPEN_INVARIANCE_HOLES),
            "root_cause_class": "RC-01",
            "cases": [
                {
                    "name": h.name,
                    "finding_id": h.finding_id,
                    "description": h.description,
                    "predicate_that_moves": h.predicate_that_moves,
                    "observed_fact_effect": h.observed_fact_effect,
                    "equivalent_form_precedent": h.equivalent_form_precedent,
                    "still_open": not rows_by_name[h.name]["holds"],
                }
                for h in OPEN_INVARIANCE_HOLES
            ],
            "meaning": (
                "representation changes with no change of meaning that move a "
                "predicate. All are false FAILs, so nothing nonconforming is "
                "admitted by them, but a predicate that only works on the "
                "fixture's spelling is syntactic, not semantic."
            ),
        },
        "total": len(inv) + len(dif),
        "holding": sum(1 for r in inv if r["holds"]) + sum(1 for r in dif if r["holds"]),
        "suite_green_does_not_mean_package_sound": (
            "Two false-pass holes (V4-FND-02, V4-FND-03) and four invariance "
            "holes (V4-FND-02, V4-FND-04) are open. The suite is green because "
            "it describes them accurately, not because they are closed."
        ),
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )
    return report


if __name__ == "__main__":
    for _n, _f in sorted(list(globals().items())):
        if _n.startswith("test_"):
            _f()
    print("v4 metamorphic and adversarial corpus ok")
