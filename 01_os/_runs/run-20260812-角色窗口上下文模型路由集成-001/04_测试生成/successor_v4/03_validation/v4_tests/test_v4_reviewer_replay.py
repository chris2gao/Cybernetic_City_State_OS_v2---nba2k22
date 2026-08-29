"""Replay the independent reviewer's 63-case probe corpus against the v4 method.

The reviewer's corpus is 46 semantic cases plus 17 receipt-attack cases.  Against
the package it was written for it found 29 counterexamples; after the
FIX_REQUIRED correction the accepted package met 63/63
(root-cause-001/09_FIX_REQUIRED修正/29反例关闭矩阵_v1.yml, whose own source of
truth is the suite, not that document).

successor_v4 must not lose that.  Three measurements are taken, and they answer
three different questions:

  A. accepted engine, accepted baseline, IN A SEPARATE PROCESS
     Reproduces the reviewer's own measurement from the *vendored* copy.  If
     this does not come out 46/46 the vendoring is not faithful and nothing
     downstream means anything.  This is the reproduce-before-change step.

     It has to be a subprocess.  Importing `semantic_acceptance_v4` registers
     P21..P27 into the shared REGISTRY, so in this interpreter `evaluate_tree`
     is a fourteen-predicate function by the time any test runs.  Measuring the
     "accepted engine" here would be the extension grading itself.  See
     `accepted_only_probe.py` and
     03_validation/findings/V4-FND-01_shared_registry_false_fail_v1.yml.

  B. v4 engine, baseline_v4
     The actual replay.  Same mutations, same reviewer expectations, evaluated
     through the fourteen-predicate entry point on the tree that satisfies all
     fourteen criteria.

  C. v4 engine, accepted baseline  (diagnostic, not a pass/fail gate)
     Establishes *why* B uses baseline_v4: the accepted baseline declares no
     A04 minimum-effective-context contract, so P22 fails on it before any
     mutation is applied.  C exists so that the choice of base tree in B is a
     measured fact rather than a convenient assumption.  It asserts the narrow
     proposition it can actually prove: the only predicate that separates the
     two fixture roots is P22.

Why not simply call the reviewer's `run_semantic_case`: it is hard-wired to the
seven-predicate `evaluate_tree`.  The cases are reused; the runner is not.  The
expectations below are read off the reviewer's own dataclass fields, never
retyped.
"""

from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import _bootstrap_v4
from _bootstrap_v4 import BASELINE, BASELINE_V4

import reviewer_corpus

from semantic_acceptance.evaluate import evaluate_tree, overall
from semantic_acceptance.predicates import FAIL, PASS, UNSUPPORTED
from semantic_acceptance_v4.evaluate_v4 import evaluate_full, result_vector

A04_PREDICATE = "P22"
V4_PREDICATES = ("P21", "P22", "P23", "P24", "P25", "P26", "P27")
_HERE = Path(__file__).resolve().parent


def _accepted_only_measurement() -> dict[str, Any]:
    """Measurement A, run in a clean interpreter (see module docstring)."""
    with tempfile.TemporaryDirectory() as td:
        out = Path(td) / "accepted_only.json"
        proc = subprocess.run(
            [sys.executable, str(_HERE / "accepted_only_probe.py"), str(out)],
            cwd=str(_HERE),
            capture_output=True,
        )
        if proc.returncode != 0:
            raise AssertionError(
                f"accepted_only_probe exited {proc.returncode}: "
                f"{proc.stderr.decode('utf-8', 'replace')[-2000:]}"
            )
        return json.loads(out.read_text(encoding="utf-8"))


def _copy(src: Path, dest: Path) -> Path:
    shutil.copytree(src, dest)
    return dest


def _judge(case, results) -> dict[str, Any]:
    """Apply the reviewer's own correctness rule to a result set."""
    vector = result_vector(results)
    actual_overall = overall(results)
    deciding = {pid: vector.get(pid) for pid in case.deciding_predicates}
    correct = actual_overall == case.expected_overall
    if case.expected_overall == FAIL and case.deciding_predicates:
        correct = correct and any(value == FAIL for value in deciding.values())
    return {
        "case_id": case.case_id,
        "category": case.category,
        "description": case.description,
        "expected_overall": case.expected_overall,
        "actual_overall": actual_overall,
        "deciding_predicates": list(case.deciding_predicates),
        "deciding_results": deciding,
        "correct": correct,
        "counterexample": not correct,
        "result_vector": vector,
        "nonpass": [
            {"predicate_id": r.predicate_id, "status": r.status, "detail": r.detail}
            for r in results
            if r.status != PASS
        ],
    }


def _run_semantic(evaluator, base: Path, label: str) -> list[dict[str, Any]]:
    suite = reviewer_corpus.load_suite()
    reviewer_corpus.assert_engine_is_vendored()
    rows = []
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / label
        root.mkdir(parents=True)
        for case in suite.SEMANTIC_CASES:
            tree = _copy(base, root / case.case_id)
            case.mutate(tree)
            rows.append(_judge(case, evaluator(tree)))
    return rows


# ---------------------------------------------------------------------------
# A. reproduce the reviewer's measurement from the vendored engine
# ---------------------------------------------------------------------------


def test_A_accepted_engine_reproduces_reviewer_46_of_46():
    report = _accepted_only_measurement()
    wrong = [
        f"{r['case_id']}({r['description']}): expected {r['expected_overall']}, "
        f"got {r['actual_overall']}, nonpass={r['nonpass']}"
        for r in report["cases"]
        if not r["correct"]
    ]
    assert report["total"] == 46, report["total"]
    assert wrong == [], wrong


def test_A_control_really_ran_seven_predicates():
    """The control is only a control if it was seven-predicate.

    Without this, a future change that leaks the v4 import into the subprocess
    would leave test_A green while silently measuring something else.
    """
    report = _accepted_only_measurement()
    sets = {tuple(s) for s in report["distinct_predicate_id_sets"]}
    assert sets == {("P01", "P02", "P03", "P04", "P05", "P06", "P07")}, sorted(sets)


# ---------------------------------------------------------------------------
# B. the replay proper
# ---------------------------------------------------------------------------


def test_B_v4_engine_meets_all_46_reviewer_expectations():
    rows = _run_semantic(evaluate_full, BASELINE_V4, "B")
    wrong = [
        f"{r['case_id']}({r['description']}): expected {r['expected_overall']}, "
        f"got {r['actual_overall']}, deciding={r['deciding_results']}, nonpass={r['nonpass']}"
        for r in rows
        if not r["correct"]
    ]
    assert len(rows) == 46, len(rows)
    assert wrong == [], wrong


def test_B_v4_returns_fourteen_predicates_for_every_case():
    rows = _run_semantic(evaluate_full, BASELINE_V4, "Bcount")
    bad = [f"{r['case_id']}: {len(r['result_vector'])}" for r in rows if len(r["result_vector"]) != 14]
    assert bad == [], bad


# ---------------------------------------------------------------------------
# C. why B uses baseline_v4
# ---------------------------------------------------------------------------


# A03's predicate, named here for the same reason A04_PREDICATE is: the test
# below asserts an exact set, and an exact set written as bare strings drifts.
A03_PREDICATE = "P21"

# Exactly which criteria the accepted baseline does not satisfy, and why. Each
# entry is a criterion the accepted seven-predicate package never covered, so the
# fixture was never written to satisfy it:
#
#   P22 / A04 — no minimum-effective-context derivation contract is declared.
#   P21 / A03 — invalidation conditions are bare strings with no structured
#               definitions. Ruling F03-D admits a bare string only when the
#               document also carries an explicit structured definition for it,
#               so the subject and observation slots do not resolve. Before
#               F03-D these strings were scored deterministic because they
#               matched no vagueness word — the false pass V4-FND-03 recorded.
#
# The set grew from one to two when F03-D landed. That is the accepted fixture
# becoming visibly non-conforming on a second uncovered criterion, not a
# regression in the fixture. Anything outside this set is still unaccounted for.
UNSATISFIED_BY_ACCEPTED_BASELINE = [A03_PREDICATE, A04_PREDICATE]


def test_C_only_accounted_predicates_separate_the_two_fixture_roots():
    """The accepted baseline differs from baseline_v4 by exactly P21 and P22.

    Stated narrowly on purpose: this proves the fixture choice does not mask a
    third difference, and proves nothing about whether P21 or P22 is a good
    predicate.  That is `test_v4_predicates`' job, not this module's.
    """
    on_v4 = result_vector(evaluate_full(BASELINE_V4))
    on_accepted = result_vector(evaluate_full(BASELINE))
    differing = sorted(k for k in on_v4 if on_v4[k] != on_accepted.get(k))
    assert differing == UNSATISFIED_BY_ACCEPTED_BASELINE, {
        "differing": differing,
        "baseline_v4": on_v4,
        "baseline": on_accepted,
    }
    for pid in UNSATISFIED_BY_ACCEPTED_BASELINE:
        assert on_v4[pid] == PASS, pid
        assert on_accepted[pid] == FAIL, pid


def test_C_accepted_baseline_passes_all_seven_accepted_predicates():
    """The accepted baseline is still conforming under the accepted engine.

    Measured in the isolated subprocess, not here: in this interpreter
    `evaluate_tree` is no longer the accepted engine's seven-predicate function.
    """
    report = _accepted_only_measurement()
    # Every expected-PASS case in the reviewer corpus starts from this baseline
    # and is expected to stay conforming; if the baseline itself had regressed,
    # all of them would be wrong at once.
    conforming = [r for r in report["cases"] if r["expected_overall"] == PASS]
    broken = [r["case_id"] for r in conforming if r["actual_overall"] != PASS]
    assert conforming, "reviewer corpus has no expected-PASS case"
    assert broken == [], broken


# ---------------------------------------------------------------------------
# V4-FND-01: the guard that keeps the finding closed
# ---------------------------------------------------------------------------


def test_FND01_unaugmented_factset_is_unsupported_not_fail():
    """A FactSet the v4 augmentation never touched cannot support a judgement.

    Human ruling R-A, 2026-08-15.  Before it, these seven predicates read a
    missing attribute as an empty fact list and reported a conforming tree as
    FAIL.  `UNSUPPORTED` is already the accepted contract's third outcome
    (V-FACT-08) and `overall` already treats it as not-pass, so the guard is
    fail-closed and needed no change to the vendored engine.
    """
    results = evaluate_tree(BASELINE_V4)  # accepted build_fact_set, no augmentation
    by_id = {r.predicate_id: r for r in results}
    for pid in V4_PREDICATES:
        assert pid in by_id, sorted(by_id)
        assert by_id[pid].status == UNSUPPORTED, (pid, by_id[pid].status, by_id[pid].detail)
    assert overall(results) == UNSUPPORTED, overall(results)


def test_FND01_accepted_seven_are_unaffected_by_the_guard():
    """The guard must not change what the accepted seven say about the tree."""
    by_id = {r.predicate_id: r.status for r in evaluate_tree(BASELINE_V4)}
    accepted = {k: v for k, v in by_id.items() if k in ("P01", "P02", "P03", "P04", "P05", "P06", "P07")}
    assert accepted == {p: PASS for p in accepted}, accepted
    assert len(accepted) == 7, accepted


def test_FND01_augmented_factset_still_judges_normally():
    """The guard must not swallow real verdicts on a properly built fact set."""
    on_v4 = result_vector(evaluate_full(BASELINE_V4))
    on_accepted = result_vector(evaluate_full(BASELINE))
    assert UNSUPPORTED not in on_v4.values(), on_v4
    assert on_v4[A04_PREDICATE] == PASS
    assert on_accepted[A04_PREDICATE] == FAIL, on_accepted


# ---------------------------------------------------------------------------
# Receipt attacks: engine-level, untouched by the extension
# ---------------------------------------------------------------------------


def test_receipt_attacks_all_seventeen_classified_correctly():
    suite = reviewer_corpus.load_suite()
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "receipt"
        root.mkdir(parents=True)
        rows = [suite.run_receipt_case(case, root) for case in suite.RECEIPT_CASES]
    wrong = [
        f"{r['case_id']}({r['description']}): expected_valid={r['expected_valid']} "
        f"actual_valid={r['actual_valid']} exception={r['exception']}"
        for r in rows
        if not r["correct"]
    ]
    assert len(rows) == 17, len(rows)
    assert wrong == [], wrong


def test_v4_import_does_not_change_receipt_validation():
    """P21..P27 register into the shared REGISTRY at import time.

    `receipt.py` is engine code the extension must not perturb.  Importing the
    v4 package has already happened by this point in the module, so if the
    seventeen receipt cases still classify correctly the proposition holds for
    this corpus.  Asserted separately from the previous test so a failure names
    the right cause.
    """
    import semantic_acceptance_v4.predicates_v4  # noqa: F401
    from semantic_acceptance import receipt

    suite = reviewer_corpus.load_suite()
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "receipt_after_v4"
        root.mkdir(parents=True)
        rows = [suite.run_receipt_case(case, root) for case in suite.RECEIPT_CASES]
    assert all(r["correct"] for r in rows), [r["case_id"] for r in rows if not r["correct"]]
    assert receipt.SELF_HASH_SENTINEL


# ---------------------------------------------------------------------------
# evidence emission
# ---------------------------------------------------------------------------


def write_results(out_path: Path) -> dict[str, Any]:
    suite = reviewer_corpus.load_suite()
    a_report = _accepted_only_measurement()
    a_rows = a_report["cases"]
    b_rows = _run_semantic(evaluate_full, BASELINE_V4, "emitB")
    with tempfile.TemporaryDirectory() as td:
        root = Path(td) / "receipt"
        root.mkdir(parents=True)
        r_rows = [suite.run_receipt_case(case, root) for case in suite.RECEIPT_CASES]

    report = {
        "corpus": "independent_reviewer_probe_suite_replayed_against_successor_v4",
        "provenance": reviewer_corpus.provenance(),
        "measurement_A_accepted_engine_accepted_baseline": {
            "isolation": "separate interpreter; semantic_acceptance_v4 never imported",
            "predicate_id_sets_observed": a_report["distinct_predicate_id_sets"],
            "total": len(a_rows),
            "expected_classifications_met": a_report["expected_classifications_met"],
            "counterexample_ids": a_report["counterexample_ids"],
            "proves": "the vendored engine reproduces the reviewer's own measurement",
            "does_not_prove": "anything about the v4 extension predicates",
        },
        "measurement_B_v4_engine_baseline_v4": {
            "total": len(b_rows),
            "expected_classifications_met": sum(1 for r in b_rows if r["correct"]),
            "counterexample_ids": [r["case_id"] for r in b_rows if r["counterexample"]],
            "predicates_per_case": sorted({len(r["result_vector"]) for r in b_rows}),
            "proves": "the reviewer's 46 semantic expectations still hold under 14 predicates",
        },
        "measurement_receipt_attacks": {
            "total": len(r_rows),
            "expected_classifications_met": sum(1 for r in r_rows if r["correct"]),
            "counterexample_ids": [r["case_id"] for r in r_rows if not r["correct"]],
        },
        "combined_total": len(b_rows) + len(r_rows),
        "combined_expected_classifications_met": (
            sum(1 for r in b_rows if r["correct"]) + sum(1 for r in r_rows if r["correct"])
        ),
        "semantic_cases_A": a_rows,
        "semantic_cases_B": b_rows,
        "receipt_cases": r_rows,
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(
        json.dumps(report, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",  # byte-reproducible; the repository is eol=lf
    )
    return report


if __name__ == "__main__":
    test_A_accepted_engine_reproduces_reviewer_46_of_46()
    test_A_control_really_ran_seven_predicates()
    test_B_v4_engine_meets_all_46_reviewer_expectations()
    test_B_v4_returns_fourteen_predicates_for_every_case()
    test_C_only_P22_separates_the_two_fixture_roots()
    test_C_accepted_baseline_passes_all_seven_accepted_predicates()
    test_FND01_unaugmented_factset_is_unsupported_not_fail()
    test_FND01_accepted_seven_are_unaffected_by_the_guard()
    test_FND01_augmented_factset_still_judges_normally()
    test_receipt_attacks_all_seventeen_classified_correctly()
    test_v4_import_does_not_change_receipt_validation()
    print("reviewer replay ok")
