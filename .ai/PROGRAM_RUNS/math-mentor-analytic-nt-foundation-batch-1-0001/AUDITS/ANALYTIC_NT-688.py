"""Bounded audit for declared finite exponential-sum identities."""

from __future__ import annotations

import argparse
import cmath
import json
import math
import platform
from pathlib import Path


def encode_complex(value: complex) -> list[float]:
    return [value.real, value.imag]


def decode_complex(pair: list[float]) -> complex:
    return complex(pair[0], pair[1])


def e(phase: float) -> complex:
    """The Human-approved convention e(t)=exp(2*pi*i*t)."""
    return cmath.exp(2j * math.pi * phase)


def unweighted_linear_sum(term_count: int, alpha: float) -> complex:
    return sum((e(index * alpha) for index in range(term_count)), 0j)


def weighted_sum(weights: list[complex], phases: list[float]) -> complex:
    if len(weights) != len(phases):
        raise ValueError("weights and phases must have equal length")
    return sum(
        (weight * e(phase) for weight, phase in zip(weights, phases)), 0j
    )


def run_audit(payload: dict) -> dict:
    tolerance = float(payload["tolerance"])
    if payload["convention"] != "e(t)=exp(2*pi*i*t)":
        raise AssertionError("unexpected exponential convention")

    roots_results = []
    for case in payload["roots_of_unity_cases"]:
        term_count = int(case["N"])
        frequency = int(case["k"])
        if term_count < 1 or frequency % term_count == 0:
            raise AssertionError(f"{case['id']}: cancellation precondition is false")
        actual = unweighted_linear_sum(term_count, frequency / term_count)
        absolute_error = abs(actual)
        passed = absolute_error <= tolerance
        if not passed:
            raise AssertionError(
                f"{case['id']}: residual {absolute_error} exceeds {tolerance}"
            )
        roots_results.append(
            {
                "id": case["id"],
                "N": term_count,
                "k": frequency,
                "gcd_N_k": math.gcd(term_count, frequency),
                "sum": encode_complex(actual),
                "absolute_error_from_zero": absolute_error,
                "passed": passed,
            }
        )

    geometric_results = []
    for case in payload["geometric_identity_cases"]:
        term_count = int(case["N"])
        alpha = int(case["alpha_numerator"]) / int(case["alpha_denominator"])
        if term_count < 1 or alpha.is_integer():
            raise AssertionError(f"{case['id']}: geometric precondition is false")
        direct = unweighted_linear_sum(term_count, alpha)
        closed_form = (1 - e(term_count * alpha)) / (1 - e(alpha))
        absolute_error = abs(direct - closed_form)
        passed = absolute_error <= tolerance
        if not passed:
            raise AssertionError(
                f"{case['id']}: residual {absolute_error} exceeds {tolerance}"
            )
        geometric_results.append(
            {
                "id": case["id"],
                "N": term_count,
                "alpha": alpha,
                "direct_sum": encode_complex(direct),
                "closed_form": encode_complex(closed_form),
                "absolute_error": absolute_error,
                "passed": passed,
            }
        )

    triangle_results = []
    for case in payload["triangle_bound_cases"]:
        weights = [decode_complex(pair) for pair in case["weights"]]
        phases = [float(value) for value in case["phases"]]
        total = weighted_sum(weights, phases)
        magnitude = abs(total)
        trivial_bound = sum(abs(weight) for weight in weights)
        slack = trivial_bound - magnitude
        passed = magnitude <= trivial_bound + tolerance
        if not passed:
            raise AssertionError(
                f"{case['id']}: magnitude {magnitude} exceeds {trivial_bound}"
            )
        triangle_results.append(
            {
                "id": case["id"],
                "sum": encode_complex(total),
                "magnitude": magnitude,
                "trivial_bound": trivial_bound,
                "bound_slack": slack,
                "passed": passed,
            }
        )

    edge_results = []
    for case in payload["edge_cases"]:
        case_type = case["type"]
        if case_type == "N_equals_1":
            alpha = int(case["alpha_numerator"]) / int(case["alpha_denominator"])
            actual = unweighted_linear_sum(1, alpha)
            expected = 1 + 0j
        elif case_type == "integral_alpha":
            term_count = int(case["N"])
            alpha = int(case["alpha"])
            actual = unweighted_linear_sum(term_count, alpha)
            expected = complex(term_count, 0)
        elif case_type == "zero_weights":
            weights = [decode_complex(pair) for pair in case["weights"]]
            phases = [float(value) for value in case["phases"]]
            if any(weight != 0j for weight in weights):
                raise AssertionError(f"{case['id']}: expected all weights to be zero")
            actual = weighted_sum(weights, phases)
            expected = 0j
        else:
            raise AssertionError(f"{case['id']}: unknown edge-case type {case_type}")
        absolute_error = abs(actual - expected)
        passed = absolute_error <= tolerance
        if not passed:
            raise AssertionError(
                f"{case['id']}: residual {absolute_error} exceeds {tolerance}"
            )
        edge_results.append(
            {
                "id": case["id"],
                "type": case_type,
                "actual": encode_complex(actual),
                "expected": encode_complex(expected),
                "absolute_error": absolute_error,
                "passed": passed,
            }
        )

    all_results = roots_results + geometric_results + triangle_results + edge_results
    return {
        "audit_id": payload["audit_id"],
        "status": "passed",
        "scope": "declared_finite_exponential_sum_identities_and_bounds",
        "convention": payload["convention"],
        "tolerance": tolerance,
        "case_count": len(all_results),
        "category_counts": {
            "roots_of_unity": len(roots_results),
            "geometric_identity": len(geometric_results),
            "triangle_bound": len(triangle_results),
            "edge_cases": len(edge_results),
        },
        "roots_of_unity_cases": roots_results,
        "geometric_identity_cases": geometric_results,
        "triangle_bound_cases": triangle_results,
        "edge_cases": edge_results,
        "environment": {
            "python_version": platform.python_version(),
            "implementation": platform.python_implementation(),
            "system": platform.system(),
            "machine": platform.machine(),
            "numeric_model": "Python binary64 complex arithmetic",
        },
        "explicitly_not_validated": payload["explicitly_not_validated"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--log", required=True, type=Path)
    args = parser.parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    result = run_audit(payload)
    serialized = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.log.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(serialized, encoding="utf-8")
    args.log.write_text(serialized, encoding="utf-8")
    print(serialized, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
