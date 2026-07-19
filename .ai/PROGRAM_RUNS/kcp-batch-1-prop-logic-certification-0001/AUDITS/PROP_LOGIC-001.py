"""Deterministic finite truth-function audit for PROP_LOGIC-001."""

from __future__ import annotations

import argparse
import itertools
import json
import platform
from pathlib import Path

import sympy
from sympy.logic.boolalg import And, Equivalent, Implies, Not, Or


def run_audit(payload: dict) -> dict:
    p_symbol, q_symbol = sympy.symbols("P Q")
    expressions = {
        "and": And(p_symbol, q_symbol),
        "or": Or(p_symbol, q_symbol),
        "implies": Implies(p_symbol, q_symbol),
        "iff": Equivalent(p_symbol, q_symbol),
    }
    expected_rows = {
        (bool(row["p"]), bool(row["q"])): row
        for row in payload["expected_binary_rows"]
    }
    observed_rows = []
    for p_value, q_value in itertools.product((False, True), repeat=2):
        substitutions = {p_symbol: p_value, q_symbol: q_value}
        observed = {
            name: bool(expression.subs(substitutions))
            for name, expression in expressions.items()
        }
        observed["not_p"] = bool(Not(p_symbol).subs(substitutions))
        expected = expected_rows[(p_value, q_value)]
        for key in ("not_p", "and", "or", "implies", "iff"):
            if observed[key] is not bool(expected[key]):
                raise AssertionError(
                    f"row P={p_value}, Q={q_value}: {key}={observed[key]} "
                    f"expected {expected[key]}"
                )
        material_equivalence = observed["implies"] is bool(
            Or(Not(p_symbol), q_symbol).subs(substitutions)
        )
        if not material_equivalence:
            raise AssertionError("material implication identity failed")
        observed_rows.append(
            {
                "p": p_value,
                "q": q_value,
                **observed,
                "implies_equals_not_p_or_q": material_equivalence,
                "passed": True,
            }
        )

    negation_rows = []
    for p_value in (False, True):
        observed = bool(Not(p_symbol).subs({p_symbol: p_value}))
        expected = not p_value
        if observed is not expected:
            raise AssertionError(f"negation P={p_value}: {observed} != {expected}")
        negation_rows.append(
            {"p": p_value, "not_p": observed, "passed": True}
        )

    return {
        "audit_id": payload["audit_id"],
        "timestamp": payload["execution_timestamp"],
        "status": "passed",
        "scope": "complete_truth_assignments_for_five_connectives",
        "binary_assignment_count": len(observed_rows),
        "unary_assignment_count": len(negation_rows),
        "binary_rows": observed_rows,
        "negation_rows": negation_rows,
        "all_declared_cases_passed": True,
        "environment": {
            "python_version": platform.python_version(),
            "implementation": platform.python_implementation(),
            "sympy_version": sympy.__version__,
            "system": platform.system(),
            "machine": platform.machine(),
        },
        "finite_assertion_only": True,
        "semantic_only_claims_not_machine_validated": payload[
            "semantic_only_claims_not_machine_validated"
        ],
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
    args.log.write_text(
        "command_status=passed\nexit_code=0\n" + serialized,
        encoding="utf-8",
    )
    print(f"audit_id={result['audit_id']}")
    print("status=passed")
    print("binary_assignment_count=4")
    print("unary_assignment_count=2")
    print(f"output_ref={args.output.as_posix()}")
    print(f"log_ref={args.log.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
