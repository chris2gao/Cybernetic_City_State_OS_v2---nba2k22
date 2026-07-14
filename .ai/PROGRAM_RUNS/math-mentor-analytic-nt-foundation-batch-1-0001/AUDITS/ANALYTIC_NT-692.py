"""Bounded audit for finite Dirichlet-polynomial product identities."""

from __future__ import annotations

import argparse
import cmath
import json
import math
import platform
from pathlib import Path


def decode_complex(pair: list[float]) -> complex:
    return complex(pair[0], pair[1])


def encode_complex(value: complex) -> list[float]:
    return [value.real, value.imag]


def decode_coefficients(raw: dict[str, list[float]]) -> dict[int, complex]:
    return {int(index): decode_complex(value) for index, value in raw.items()}


def dirichlet_polynomial(coefficients: dict[int, complex], s: complex) -> complex:
    return sum(
        value * cmath.exp(-s * math.log(index))
        for index, value in coefficients.items()
    )


def dirichlet_convolution(
    left: dict[int, complex], right: dict[int, complex]
) -> dict[int, complex]:
    result: dict[int, complex] = {}
    for m, a_m in left.items():
        for n, b_n in right.items():
            result[m * n] = result.get(m * n, 0j) + a_m * b_n
    return result


def run_audit(payload: dict) -> dict:
    tolerance = float(payload["tolerance"])
    case_results = []
    for case in payload["cases"]:
        s = decode_complex(case["s"])
        left = decode_coefficients(case["left"])
        right = decode_coefficients(case["right"])
        convolution = dirichlet_convolution(left, right)
        direct = dirichlet_polynomial(left, s) * dirichlet_polynomial(right, s)
        regrouped = dirichlet_polynomial(convolution, s)
        absolute_error = abs(direct - regrouped)
        passed = absolute_error <= tolerance
        if not passed:
            raise AssertionError(
                f"{case['id']}: {absolute_error} exceeds tolerance {tolerance}"
            )
        case_results.append(
            {
                "id": case["id"],
                "s": case["s"],
                "left_support": sorted(
                    index for index, value in left.items() if value != 0j
                ),
                "right_support": sorted(
                    index for index, value in right.items() if value != 0j
                ),
                "direct_product": encode_complex(direct),
                "convolution_evaluation": encode_complex(regrouped),
                "absolute_error": absolute_error,
                "convolution_support": sorted(
                    index for index, value in convolution.items() if value != 0j
                ),
                "passed": passed,
            }
        )
    return {
        "audit_id": payload["audit_id"],
        "status": "passed",
        "scope": "finite_Dirichlet_polynomial_product_and_convolution_identity",
        "case_count": len(case_results),
        "tolerance": tolerance,
        "cases": case_results,
        "environment": {
            "python_version": platform.python_version(),
            "implementation": platform.python_implementation(),
            "system": platform.system(),
            "machine": platform.machine(),
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
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.log.parent.mkdir(parents=True, exist_ok=True)
    serialized = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    args.output.write_text(serialized, encoding="utf-8")
    args.log.write_text(serialized, encoding="utf-8")
    print(serialized, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
