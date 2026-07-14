"""Bounded finite audit for ANALYTIC_NT-684 prime-counting claims."""

from __future__ import annotations

import argparse
import json
import math
import platform
from pathlib import Path


def prime_count_prefix(limit: int) -> tuple[list[bool], list[int]]:
    if limit < 0:
        raise ValueError("limit must be nonnegative")
    is_prime = [True] * (limit + 1)
    if limit >= 0:
        is_prime[0] = False
    if limit >= 1:
        is_prime[1] = False
    for prime in range(2, math.isqrt(limit) + 1):
        if is_prime[prime]:
            for multiple in range(prime * prime, limit + 1, prime):
                is_prime[multiple] = False

    prefix: list[int] = []
    running = 0
    for flag in is_prime:
        running += int(flag)
        prefix.append(running)
    return is_prime, prefix


def prime_count_at(prefix: list[int], x: float, finite_range_max: int) -> int:
    if not math.isfinite(x) or x < 0:
        raise ValueError("x must be a finite nonnegative real number")
    cutoff = math.floor(x)
    if cutoff > finite_range_max:
        raise ValueError("x exceeds the declared finite audit range")
    return prefix[cutoff]


def run_audit(payload: dict, input_ref: str, output_ref: str, log_ref: str) -> dict:
    finite_range_max = int(payload["finite_range_max"])
    tolerance = float(payload["comparison_tolerance"])
    _, prefix = prime_count_prefix(finite_range_max)

    exact_results = []
    for case in payload["exact_prime_count_cases"]:
        x = float(case["x"])
        expected = int(case["expected"])
        observed = prime_count_at(prefix, x, finite_range_max)
        passed = observed == expected
        if not passed:
            raise AssertionError(
                f"{case['id']}: observed π({x})={observed}, expected {expected}"
            )
        exact_results.append(
            {
                "id": case["id"],
                "x": case["x"],
                "observed_prime_count": observed,
                "expected_prime_count": expected,
                "passed": passed,
            }
        )

    increments = [prefix[index] - prefix[index - 1] for index in range(1, len(prefix))]
    monotone = all(delta >= 0 for delta in increments)
    unit_step_only = all(delta in (0, 1) for delta in increments)
    step_check_passed = monotone and unit_step_only
    if not step_check_passed:
        raise AssertionError("finite prime-count prefix failed its declared step check")

    approximation_results = []
    for case in payload["declared_approximation_table"]:
        x = float(case["x"])
        if x <= 1:
            raise ValueError("declared x/log(x) table requires x>1")
        observed_count = prime_count_at(prefix, x, finite_range_max)
        expected_count = int(case["expected_prime_count"])
        if observed_count != expected_count:
            raise AssertionError(
                f"{case['id']}: prime count {observed_count} != {expected_count}"
            )

        main_term = x / math.log(x)
        normalized_ratio = observed_count * math.log(x) / x
        main_term_passed = math.isclose(
            main_term,
            float(case["expected_x_over_log_x"]),
            rel_tol=0.0,
            abs_tol=tolerance,
        )
        ratio_passed = math.isclose(
            normalized_ratio,
            float(case["expected_normalized_ratio"]),
            rel_tol=0.0,
            abs_tol=tolerance,
        )
        passed = main_term_passed and ratio_passed
        if not passed:
            raise AssertionError(f"{case['id']}: declared finite table mismatch")
        approximation_results.append(
            {
                "id": case["id"],
                "x": case["x"],
                "prime_count": observed_count,
                "x_over_log_x": main_term,
                "normalized_ratio_pi_log_x_over_x": normalized_ratio,
                "relative_error_against_prime_count": abs(observed_count - main_term)
                / observed_count,
                "comparison_tolerance": tolerance,
                "passed": passed,
            }
        )

    return {
        "audit_id": payload["audit_id"],
        "status": "passed",
        "scope": "finite_prime_counting_and_declared_sample_approximations",
        "finite_range": [0, finite_range_max],
        "exact_case_count": len(exact_results),
        "exact_prime_count_cases": exact_results,
        "finite_step_function_check": {
            "monotone_on_every_integer_in_declared_range": monotone,
            "increments_are_only_zero_or_one": unit_step_only,
            "observed_increment_values": sorted(set(increments)),
            "passed": step_check_passed,
        },
        "declared_approximation_table": approximation_results,
        "execution": {
            "input_ref": input_ref,
            "output_ref": output_ref,
            "log_ref": log_ref,
        },
        "environment": {
            "python_version": platform.python_version(),
            "implementation": platform.python_implementation(),
            "system": platform.system(),
            "machine": platform.machine(),
            "standard_library_only": True,
        },
        "finite_assertion_only": True,
        "explicitly_not_validated": payload["explicitly_not_validated"],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--log", required=True, type=Path)
    args = parser.parse_args()

    payload = json.loads(args.input.read_text(encoding="utf-8"))
    result = run_audit(
        payload,
        args.input.as_posix(),
        args.output.as_posix(),
        args.log.as_posix(),
    )
    serialized = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.log.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(serialized, encoding="utf-8")
    args.log.write_text(serialized, encoding="utf-8")
    print(f"audit_id={result['audit_id']}")
    print(f"status={result['status']}")
    print(f"output_ref={args.output.as_posix()}")
    print(f"log_ref={args.log.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
