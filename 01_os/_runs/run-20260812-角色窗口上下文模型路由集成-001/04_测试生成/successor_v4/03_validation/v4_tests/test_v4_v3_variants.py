"""Replay the fifteen independent v3 adversarial variants against the v4 method.

`vendored_baseline_tests/test_v3_adversarial_regression.py` already replays these
against the accepted seven-predicate engine, byte-identically to the accepted
package.  That test proves its own exact proposition and no more: the accepted
engine still classifies them.  It says nothing about the fourteen-predicate
package, which is what a Stage04 candidate would actually be judged by.

So the same fifteen variants are run again here, through
`evaluate_v4.evaluate_full`, on `fixtures/baseline_v4`.

Two properties are checked, and they are different:

  1. every variant is still classified as the v3 reviewer expected;
  2. a nonconforming variant still fails *on its own deciding predicate*.

(2) is the one that matters.  A fourteen-predicate package has seven more ways
to fail, so a nonconforming variant could come out FAIL for a reason completely
unrelated to what it was built to probe — and the corpus would look green while
having stopped testing anything.  That is the exact shape of ST04-V3 finding
S14, where a variant failed overall through P05 while the deciding predicate
P01 wrongly passed.

The variant objects are read from the vendored corpus.  Expectations are the
corpus's own `expectation` and `deciding_predicates` fields, never retyped here.
"""

from __future__ import annotations

import json
import shutil
import tempfile
from pathlib import Path
from typing import Any

import _bootstrap_v4
from _bootstrap_v4 import BASELINE, BASELINE_V4

from semantic_acceptance.corpus import (
    CONFORMING,
    FULL_SURFACE_SENTINEL,
    NONCONFORMING,
    V3_VARIANTS,
)
from semantic_acceptance.predicates import FAIL, PASS, UNSUPPORTED
from semantic_acceptance.evaluate import overall
from semantic_acceptance_v4.evaluate_v4 import (
    build_full_fact_set,
    evaluate_full,
    result_vector,
)

ACCEPTED_PREDICATES = ("P01", "P02", "P03", "P04", "P05", "P06", "P07")


def _run(variant, root: Path, base: Path) -> dict[str, Any]:
    tree = Path(shutil.copytree(base, root / variant.name))
    variant.mutate(tree)
    results = evaluate_full(tree)
    vector = result_vector(results)
    expected = PASS if variant.expectation == CONFORMING else FAIL
    deciding = {p: vector.get(p) for p in variant.deciding_predicates}
    return {
        "name": variant.name,
        "description": variant.description,
        "expectation": variant.expectation,
        "expected_overall": expected,
        "actual_overall": overall(results),
        "deciding_predicates": list(variant.deciding_predicates),
        "deciding_results": deciding,
        "root_cause_classes": list(variant.root_cause_classes),
        "v3_harness_result": variant.v3_harness_result,
        "vector": vector,
        "nonpass": [
            f"{r.predicate_id}({r.status}): {r.detail}" for r in results if r.status != PASS
        ],
    }


def _all(base: Path, label: str) -> list[dict[str, Any]]:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / label
        root.mkdir(parents=True)
        return [_run(v, root, base) for v in V3_VARIANTS]


def test_fifteen_variants_classified_correctly_under_v4():
    rows = _all(BASELINE_V4, "cls")
    assert len(rows) == 15, len(rows)
    wrong = [
        f"{r['name']}: expected {r['expected_overall']}, got {r['actual_overall']} ({r['nonpass']})"
        for r in rows
        if r["actual_overall"] != r["expected_overall"]
    ]
    assert wrong == [], wrong


def test_nonconforming_variants_still_fail_on_their_deciding_predicate():
    rows = _all(BASELINE_V4, "deciding")
    bad = [
        f"{r['name']}: failed, but not on {r['deciding_predicates']} -> {r['deciding_results']}"
        for r in rows
        if r["expectation"] == NONCONFORMING
        and not any(v == FAIL for v in r["deciding_results"].values())
    ]
    assert bad == [], bad


def test_no_variant_is_decided_by_an_extension_predicate_it_was_not_probing():
    """A v3 variant must not be knocked over by a v4 predicate by accident.

    Every one of the fifteen was written against the accepted seven.  If a v4
    predicate fails on a variant, the variant is no longer measuring what the v3
    reviewer built it to measure, whatever the overall verdict happens to be.
    """
    rows = _all(BASELINE_V4, "extension")
    contaminated = []
    for r in rows:
        extension_failures = [
            pid
            for pid, status in r["vector"].items()
            if pid not in ACCEPTED_PREDICATES and status != PASS
        ]
        if extension_failures:
            contaminated.append(f"{r['name']}: {extension_failures} ({r['nonpass']})")
    assert contaminated == [], contaminated


def test_no_variant_produces_an_unsupported_result():
    """UNSUPPORTED here would mean the v4 fact augmentation silently did not run.

    V4-FND-01's guard reports UNSUPPORTED for an unaugmented FactSet.  That is
    the right answer to the wrong question in this suite: `evaluate_full` always
    augments, so any UNSUPPORTED means the augmentation itself broke on a
    mutated tree.
    """
    rows = _all(BASELINE_V4, "unsup")
    bad = [f"{r['name']}: {r['nonpass']}" for r in rows if UNSUPPORTED in r["vector"].values()]
    assert bad == [], bad


def test_i14_sentinel_is_seen_by_the_v4_fact_builder():
    """The v3 topology assertion, restated for the augmented fact set.

    Discovery must read the whole declared surface.  If it ever narrowed to a
    reachability closure over the boot manifest, this unreferenced document
    would vanish from the fact set.  `vendored_baseline_tests` asserts this for
    `build_fact_set`; the augmented builder is a different function and gets its
    own assertion rather than inheriting the claim.
    """
    variant = next(v for v in V3_VARIANTS if v.name == "I14_full_surface_sentinel")
    with tempfile.TemporaryDirectory() as td:
        tree = Path(shutil.copytree(BASELINE_V4, Path(td) / "i14"))
        variant.mutate(tree)
        fs = build_full_fact_set(tree)
        doc_ids = {d.doc_id for d in fs.documents}
        assert FULL_SURFACE_SENTINEL in doc_ids, sorted(doc_ids)
        assert overall(evaluate_full(tree)) == PASS


# The accepted baseline is the seven-predicate package's own fixture, and it is
# byte-identical to root-cause-001/05_原型/fixtures/baseline. It was never written
# to satisfy the fourteen-criterion package, and each place it does not is a
# criterion the accepted package did not cover:
#
#   P22 / A04 — it declares no minimum-effective-context derivation contract.
#   P21 / A03 — it declares lifecycle invalidation conditions as bare strings
#               with no structured definitions.  Under ruling F03-D a bare string
#               resolves only through an explicit structured definition, so slots
#               1 and 2 do not resolve and the conditions are not typed
#               determinism facts.  Before F03-D the closed NEGATIVE vocabulary
#               scored them deterministic because they matched no vagueness word,
#               which is precisely the false pass V4-FND-03 recorded.
#
# So this list growing from [P22] to [P21, P22] is not a regression: it is the
# accepted fixture becoming visibly non-conforming on a second criterion that the
# accepted package never claimed. Anything OUTSIDE this list is still unaccounted
# for and still fails the control.
FIXTURE_ROOT_ACCOUNTED_DIFFERENCES = ["P21", "P22"]


def test_accepted_baseline_variant_run_differs_only_by_accounted_predicates():
    """Control: the fixture choice does not change any variant's classification.

    Run the same fifteen on the accepted baseline.  Only the accounted-for
    predicates may differ, and they must differ on every case in the same
    direction.  If some other predicate moved, the two fixture roots differ in a
    way that has not been accounted for.
    """
    on_v4 = {r["name"]: r["vector"] for r in _all(BASELINE_V4, "ctlv4")}
    on_acc = {r["name"]: r["vector"] for r in _all(BASELINE, "ctlacc")}
    unexpected = {}
    for name, vec in on_v4.items():
        moved = sorted(k for k in vec if vec[k] != on_acc[name].get(k))
        if moved != FIXTURE_ROOT_ACCOUNTED_DIFFERENCES:
            unexpected[name] = {"moved": moved, "v4": vec, "accepted": on_acc[name]}
    assert unexpected == {}, unexpected


def write_results(out_path: Path) -> dict[str, Any]:
    rows = _all(BASELINE_V4, "emit")
    correct = sum(1 for r in rows if r["actual_overall"] == r["expected_overall"])
    report = {
        "corpus": "independent_v3_adversarial_variants_replayed_against_successor_v4",
        "source_corpus": "semantic_acceptance.corpus.V3_VARIANTS (vendored, byte-identical)",
        "source_probe_script": "04_测试生成/独立接收审核/v3/independent_v3_probes.py",
        "evaluator": "semantic_acceptance_v4.evaluate_v4.evaluate_full",
        "fixture_root": "02_acceptance/fixtures/baseline_v4",
        "total": len(rows),
        "correct": correct,
        "conforming_total": sum(1 for r in rows if r["expectation"] == CONFORMING),
        "nonconforming_total": sum(1 for r in rows if r["expectation"] == NONCONFORMING),
        "decided_by_extension_predicate": [
            r["name"]
            for r in rows
            if any(
                pid not in ACCEPTED_PREDICATES and status != PASS
                for pid, status in r["vector"].items()
            )
        ],
        "variants": rows,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",  # byte-reproducible; the repository is eol=lf
    )
    return report


if __name__ == "__main__":
    test_fifteen_variants_classified_correctly_under_v4()
    test_nonconforming_variants_still_fail_on_their_deciding_predicate()
    test_no_variant_is_decided_by_an_extension_predicate_it_was_not_probing()
    test_no_variant_produces_an_unsupported_result()
    test_i14_sentinel_is_seen_by_the_v4_fact_builder()
    test_accepted_baseline_variant_run_differs_only_by_P22()
    print("v3 variant replay under v4 ok")
