"""Bounded standard-library audit for the declared chi_4 example."""

from __future__ import annotations

import argparse
import json
import math
import platform
from fractions import Fraction
from pathlib import Path


def chi4(n: int) -> int:
    """Return the real nonprincipal Dirichlet character modulo four."""

    residue = n % 4
    if residue in (0, 2):
        return 0
    if residue == 1:
        return 1
    return -1


def exact_partial_sum(term_count: int) -> Fraction:
    return sum(
        (
            Fraction(1, (2 * n + 1) ** 2)
            if n % 2 == 0
            else Fraction(-1, (2 * n + 1) ** 2)
        )
        for n in range(term_count)
    )


def floating_partial_sum(term_count: int) -> float:
    return math.fsum(
        (1.0 if n % 2 == 0 else -1.0) / ((2 * n + 1) ** 2)
        for n in range(term_count)
    )


def run_audit(payload: dict) -> dict:
    modulus = int(payload["modulus"])
    if modulus != 4:
        raise AssertionError("This bounded audit is authorized only for chi_4 modulo 4")

    table_results = []
    for case in payload["declared_value_cases"]:
        n = int(case["n"])
        expected = int(case["expected"])
        observed = chi4(n)
        if observed != expected:
            raise AssertionError(
                f"declared value case n={n}: observed {observed}, expected {expected}"
            )
        table_results.append(
            {"n": n, "expected": expected, "observed": observed, "passed": True}
        )

    zero_rule = payload["zero_rule_range"]
    zero_rule_count = 0
    unit_value_count = 0
    for n in range(int(zero_rule["start"]), int(zero_rule["end"]) + 1):
        value = chi4(n)
        if math.gcd(n, modulus) > 1:
            if value != 0:
                raise AssertionError(f"non-unit zero rule failed at n={n}")
            zero_rule_count += 1
        else:
            if abs(value) != 1:
                raise AssertionError(f"unit character magnitude failed at n={n}")
            unit_value_count += 1

    periodicity = payload["periodicity_range"]
    shift = int(periodicity["shift"])
    periodicity_count = 0
    for n in range(int(periodicity["start"]), int(periodicity["end"]) + 1):
        if chi4(n + shift) != chi4(n):
            raise AssertionError(f"periodicity failed at n={n}")
        periodicity_count += 1

    grid = payload["multiplicativity_grid"]
    grid_start = int(grid["start"])
    grid_end = int(grid["end"])
    multiplicativity_pair_count = 0
    for m in range(grid_start, grid_end + 1):
        for n in range(grid_start, grid_end + 1):
            if chi4(m * n) != chi4(m) * chi4(n):
                raise AssertionError(f"complete multiplicativity failed at ({m}, {n})")
            multiplicativity_pair_count += 1

    units = [int(value) for value in payload["unit_residues"]]
    unit_group_pair_count = 0
    if chi4(1) != 1:
        raise AssertionError("the identity residue must map to 1")
    for a in units:
        if math.gcd(a, modulus) != 1:
            raise AssertionError(f"declared unit residue {a} is not a unit modulo 4")
        for b in units:
            if chi4((a * b) % modulus) != chi4(a) * chi4(b):
                raise AssertionError(f"unit-group character law failed at ({a}, {b})")
            unit_group_pair_count += 1

    exact_sum_results = []
    for case in payload["small_exact_partial_sums"]:
        term_count = int(case["term_count"])
        expected = Fraction(int(case["numerator"]), int(case["denominator"]))
        observed = exact_partial_sum(term_count)
        if observed != expected:
            raise AssertionError(
                f"exact partial sum N={term_count}: observed {observed}, expected {expected}"
            )
        exact_sum_results.append(
            {
                "term_count": term_count,
                "expected": f"{expected.numerator}/{expected.denominator}",
                "observed": f"{observed.numerator}/{observed.denominator}",
                "passed": True,
            }
        )

    catalan = payload["catalan_partial_sum"]
    term_count = int(catalan["term_count"])
    if term_count <= 0:
        raise AssertionError("Catalan partial-sum term_count must be positive")
    declared_catalan_text = str(catalan["declared_catalan_decimal"])
    declared_catalan = float(declared_catalan_text)
    numeric_allowance = float(catalan["numeric_allowance"])
    partial_sum = floating_partial_sum(term_count)
    next_term = (1.0 if term_count % 2 == 0 else -1.0) / (
        (2 * term_count + 1) ** 2
    )
    adjacent_partial_sum = partial_sum + next_term
    alternating_remainder_bound = abs(next_term)
    tolerance = alternating_remainder_bound + numeric_allowance
    absolute_error = abs(partial_sum - declared_catalan)
    bracket_lower = min(partial_sum, adjacent_partial_sum)
    bracket_upper = max(partial_sum, adjacent_partial_sum)
    bracket_passed = (
        bracket_lower - numeric_allowance
        <= declared_catalan
        <= bracket_upper + numeric_allowance
    )
    if absolute_error > tolerance:
        raise AssertionError(
            f"Catalan partial sum error {absolute_error} exceeds {tolerance}"
        )
    if not bracket_passed:
        raise AssertionError("declared Catalan value is outside the adjacent-sum bracket")

    timestamp = str(payload["execution_timestamp"])
    return {
        "audit_id": payload["audit_id"],
        "status": "passed",
        "scope": "finite_chi4_character_properties_and_declared_Catalan_partial_sum",
        "timestamp": timestamp,
        "modulus": modulus,
        "declared_value_cases": table_results,
        "zero_rule": {
            "range": zero_rule,
            "nonunit_case_count": zero_rule_count,
            "unit_case_count": unit_value_count,
            "passed": True,
        },
        "periodicity": {
            "range": periodicity,
            "case_count": periodicity_count,
            "passed": True,
        },
        "complete_multiplicativity": {
            "grid": grid,
            "pair_count": multiplicativity_pair_count,
            "passed": True,
        },
        "unit_group_character": {
            "unit_residues": units,
            "pair_count": unit_group_pair_count,
            "passed": True,
        },
        "small_exact_partial_sums": exact_sum_results,
        "catalan_partial_sum": {
            "term_count": term_count,
            "declared_catalan_decimal": declared_catalan_text,
            "observed_partial_sum": partial_sum,
            "adjacent_partial_sum": adjacent_partial_sum,
            "absolute_error": absolute_error,
            "alternating_remainder_bound": alternating_remainder_bound,
            "numeric_allowance": numeric_allowance,
            "tolerance": tolerance,
            "adjacent_sum_bracket": [bracket_lower, bracket_upper],
            "bracket_passed": bracket_passed,
            "passed": True,
        },
        "environment": {
            "python_version": platform.python_version(),
            "implementation": platform.python_implementation(),
            "system": platform.system(),
            "machine": platform.machine(),
        },
        "explicitly_not_validated": payload["explicitly_not_validated"],
    }


def write_log(path: Path, result: dict, input_ref: Path, output_ref: Path) -> None:
    catalan = result["catalan_partial_sum"]
    limitations = "\n".join(
        f"limitation={item}" for item in result["explicitly_not_validated"]
    )
    text = (
        f"timestamp={result['timestamp']}\n"
        f"audit_id={result['audit_id']}\n"
        f"status={result['status']}\n"
        f"scope={result['scope']}\n"
        f"input_ref={input_ref.as_posix()}\n"
        f"output_ref={output_ref.as_posix()}\n"
        f"declared_value_case_count={len(result['declared_value_cases'])}\n"
        f"periodicity_case_count={result['periodicity']['case_count']}\n"
        f"multiplicativity_pair_count={result['complete_multiplicativity']['pair_count']}\n"
        f"unit_group_pair_count={result['unit_group_character']['pair_count']}\n"
        f"catalan_term_count={catalan['term_count']}\n"
        f"catalan_observed_partial_sum={catalan['observed_partial_sum']:.17g}\n"
        f"catalan_absolute_error={catalan['absolute_error']:.17g}\n"
        f"catalan_alternating_remainder_bound={catalan['alternating_remainder_bound']:.17g}\n"
        f"catalan_numeric_allowance={catalan['numeric_allowance']:.17g}\n"
        f"catalan_total_tolerance={catalan['tolerance']:.17g}\n"
        f"python_version={result['environment']['python_version']}\n"
        f"python_implementation={result['environment']['implementation']}\n"
        f"{limitations}\n"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--log", required=True, type=Path)
    args = parser.parse_args()

    payload = json.loads(args.input.read_text(encoding="utf-8"))
    result = run_audit(payload)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    write_log(args.log, result, args.input, args.output)
    print(
        json.dumps(
            {
                "audit_id": result["audit_id"],
                "status": result["status"],
                "timestamp": result["timestamp"],
                "periodicity_case_count": result["periodicity"]["case_count"],
                "multiplicativity_pair_count": result["complete_multiplicativity"][
                    "pair_count"
                ],
                "catalan_absolute_error": result["catalan_partial_sum"][
                    "absolute_error"
                ],
                "catalan_tolerance": result["catalan_partial_sum"]["tolerance"],
            },
            ensure_ascii=False,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
