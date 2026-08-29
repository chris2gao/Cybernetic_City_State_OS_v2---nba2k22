"""All fifteen independent v3 adversarial variants must be classified correctly.

Source of the variants:
  04_测试生成/独立接收审核/v3/independent_v3_probes.py
Observed behaviour of the package they were built against:
  04_测试生成/独立接收审核/v3/independent_v3_probe_results_v1.json

Fourteen of the fifteen were misclassified there.  This module is the regression
corpus that keeps them classified.
"""

from __future__ import annotations

import json
import tempfile
from pathlib import Path

import _bootstrap
from _bootstrap import BASELINE, PROTOTYPE_ROOT

from semantic_acceptance.corpus import (
    CONFORMING,
    FULL_SURFACE_SENTINEL,
    NONCONFORMING,
    V3_VARIANTS,
    copy_tree,
)
from semantic_acceptance.evaluate import evaluate_tree, overall, result_vector
from semantic_acceptance.facts import build_fact_set
from semantic_acceptance.predicates import FAIL, PASS


def run_variant(td: Path, variant) -> dict:
    tree = copy_tree(BASELINE, td / variant.name)
    variant.mutate(tree)
    results = evaluate_tree(tree)
    vec = result_vector(results)
    return {
        "name": variant.name,
        "description": variant.description,
        "expectation": variant.expectation,
        "overall": overall(results),
        "vector": vec,
        "deciding_predicates": list(variant.deciding_predicates),
        "deciding_results": {p: vec.get(p) for p in variant.deciding_predicates},
        "root_cause_classes": list(variant.root_cause_classes),
        "v3_harness_result": variant.v3_harness_result,
        "v3_finding_refs": list(variant.v3_finding_refs),
        "failure_details": [
            f"{r.predicate_id}: {r.detail}" for r in results if r.status != PASS
        ],
        "tree": tree,
    }


def test_all_fifteen_variants_classified_correctly():
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        wrong = []
        for variant in V3_VARIANTS:
            got = run_variant(root, variant)
            expected_overall = PASS if variant.expectation == CONFORMING else FAIL
            if got["overall"] != expected_overall:
                wrong.append(
                    f"{variant.name}: expected {expected_overall}, got {got['overall']} "
                    f"({got['failure_details']})"
                )
                continue
            if variant.expectation == NONCONFORMING:
                deciding = got["deciding_results"]
                if not any(v == FAIL for v in deciding.values()):
                    wrong.append(
                        f"{variant.name}: failed, but not on its deciding predicate {deciding}"
                    )
        assert wrong == [], wrong


def test_i14_sentinel_is_actually_seen():
    """The topology assertion, carried over from v3's I14.

    Discovery must read the whole declared surface.  If it ever narrows to a
    reachability closure over the boot manifest, this unreferenced document
    disappears from the fact set and this test goes red.  That is the same
    proposition v3's full-candidate-tree probe established, and the reason a
    dependency crawler must not come back.
    """
    with tempfile.TemporaryDirectory() as td:
        tree = copy_tree(BASELINE, Path(td) / "i14")
        variant = next(v for v in V3_VARIANTS if v.name == "I14_full_surface_sentinel")
        variant.mutate(tree)
        fs = build_fact_set(tree)
        doc_ids = {d.doc_id for d in fs.documents}
        assert FULL_SURFACE_SENTINEL in doc_ids, sorted(doc_ids)
        assert overall(evaluate_tree(tree)) == PASS


def test_no_dependency_crawler_symbols_present():
    """The v3 reviewer verified crawler absence by symbol search; so do we."""
    forbidden = ("stage_dependency_closure", "probe_mech_validator", "REPO_PATH_RX")
    pkg = PROTOTYPE_ROOT / "semantic_acceptance"
    hits = []
    for path in sorted(pkg.rglob("*.py")):
        text = path.read_text(encoding="utf-8")
        for sym in forbidden:
            if sym in text:
                hits.append(f"{path.name}:{sym}")
    assert hits == [], hits


def write_results(out_path: Path) -> dict:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        rows = []
        for variant in V3_VARIANTS:
            got = run_variant(root, variant)
            got.pop("tree", None)
            expected_overall = PASS if variant.expectation == CONFORMING else FAIL
            got["expected_overall"] = expected_overall
            got["correct"] = got["overall"] == expected_overall
            rows.append(got)
    report = {
        "corpus": "independent_v3_adversarial_variants",
        "source_probe_script": "04_测试生成/独立接收审核/v3/independent_v3_probes.py",
        "source_probe_results": "04_测试生成/独立接收审核/v3/independent_v3_probe_results_v1.json",
        "total": len(rows),
        "correct": sum(1 for r in rows if r["correct"]),
        "conforming_total": sum(1 for r in rows if r["expectation"] == CONFORMING),
        "nonconforming_total": sum(1 for r in rows if r["expectation"] == NONCONFORMING),
        "previously_misclassified": 14,
        "previously_correct": 1,
        "variants": rows,
    }
    out_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    return report


if __name__ == "__main__":
    test_all_fifteen_variants_classified_correctly()
    test_i14_sentinel_is_actually_seen()
    test_no_dependency_crawler_symbols_present()
    print("v3 regression corpus ok")
