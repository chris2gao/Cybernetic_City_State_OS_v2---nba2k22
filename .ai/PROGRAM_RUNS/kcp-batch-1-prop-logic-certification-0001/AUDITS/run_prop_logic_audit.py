"""Deterministic finite audits for PROP_LOGIC-002 through PROP_LOGIC-005."""

from __future__ import annotations

import argparse
import itertools
import json
import platform
from pathlib import Path

import sympy
from sympy.logic.boolalg import And, Equivalent, Implies, Not, Or, Xor


def value(expression: object, substitutions: dict) -> bool:
    return bool(sympy.sympify(expression).subs(substitutions))


def audit_truth_tables() -> dict:
    p, q, r = sympy.symbols("P Q R")
    assignments = list(itertools.product((False, True), repeat=3))
    if len(assignments) != 2**3 or len(set(assignments)) != len(assignments):
        raise AssertionError("three-variable truth-table enumeration is incomplete")
    identities = {
        "implication_elimination": (Implies(p, q), Or(Not(p), q)),
        "biconditional_two_implications": (
            Equivalent(p, q),
            And(Implies(p, q), Implies(q, p)),
        ),
        "double_negation": (Not(Not(p)), p),
        "contrapositive": (Implies(p, q), Implies(Not(q), Not(p))),
        "excluded_middle": (Or(p, Not(p)), sympy.true),
        "conjunction_identity": (And(r, sympy.true), r),
    }
    results = []
    for name, (left, right) in identities.items():
        checked = 0
        for p_value, q_value, r_value in assignments:
            substitutions = {p: p_value, q: q_value, r: r_value}
            if value(left, substitutions) is not value(right, substitutions):
                raise AssertionError(f"{name} failed at {substitutions}")
            checked += 1
        results.append({"identity": name, "assignment_count": checked, "passed": True})
    return {
        "scope": "truth_table_enumeration_and_common_equivalences",
        "truth_table_variable_count": 3,
        "truth_table_row_count": len(assignments),
        "identity_count": len(results),
        "identity_assignment_checks": sum(item["assignment_count"] for item in results),
        "identities": results,
    }


def audit_algebra_laws() -> dict:
    p, q, r = sympy.symbols("P Q R")
    identities = {
        "de_morgan_and": (Not(And(p, q)), Or(Not(p), Not(q))),
        "de_morgan_or": (Not(Or(p, q)), And(Not(p), Not(q))),
        "and_commutative": (And(p, q), And(q, p)),
        "or_commutative": (Or(p, q), Or(q, p)),
        "and_associative": (And(And(p, q), r), And(p, And(q, r))),
        "or_associative": (Or(Or(p, q), r), Or(p, Or(q, r))),
        "and_distributive": (And(p, Or(q, r)), Or(And(p, q), And(p, r))),
        "or_distributive": (Or(p, And(q, r)), And(Or(p, q), Or(p, r))),
        "and_absorption": (And(p, Or(p, q)), p),
        "or_absorption": (Or(p, And(p, q)), p),
        "and_idempotent": (And(p, p), p),
        "or_idempotent": (Or(p, p), p),
        "complement_or": (Or(p, Not(p)), sympy.true),
        "complement_and": (And(p, Not(p)), sympy.false),
        "identity_and": (And(p, sympy.true), p),
        "identity_or": (Or(p, sympy.false), p),
        "domination_or": (Or(p, sympy.true), sympy.true),
        "domination_and": (And(p, sympy.false), sympy.false),
    }
    assignments = list(itertools.product((False, True), repeat=3))
    results = []
    for name, (left, right) in identities.items():
        for p_value, q_value, r_value in assignments:
            substitutions = {p: p_value, q: q_value, r: r_value}
            if value(left, substitutions) is not value(right, substitutions):
                raise AssertionError(f"{name} failed at {substitutions}")
        results.append({"identity": name, "assignment_count": 8, "passed": True})
    return {
        "scope": "exhaustive_three_variable_boolean_algebra_identities",
        "identity_count": len(results),
        "assignment_count_per_identity": len(assignments),
        "total_identity_assignment_checks": len(results) * len(assignments),
        "identities": results,
    }


def audit_tautologies() -> dict:
    p, q = sympy.symbols("P Q")
    assignments = list(itertools.product((False, True), repeat=2))
    tautology = Or(p, Not(p))
    contradiction = And(p, Not(p))
    satisfiable = Xor(p, q)
    tautology_values = [value(tautology, {p: a, q: b}) for a, b in assignments]
    contradiction_values = [value(contradiction, {p: a, q: b}) for a, b in assignments]
    satisfiable_values = [value(satisfiable, {p: a, q: b}) for a, b in assignments]
    if not all(tautology_values):
        raise AssertionError("excluded middle was not true on every assignment")
    if any(contradiction_values):
        raise AssertionError("P and not P was true on an assignment")
    if not any(satisfiable_values) or all(satisfiable_values):
        raise AssertionError("XOR did not exhibit satisfiable non-tautological behavior")

    entailment_counterexamples = []
    non_entailment_counterexamples = []
    premise = And(p, Implies(p, q))
    for p_value, q_value in assignments:
        substitutions = {p: p_value, q: q_value}
        if value(premise, substitutions) and not value(q, substitutions):
            entailment_counterexamples.append({"p": p_value, "q": q_value})
        if value(Or(p, q), substitutions) and not value(p, substitutions):
            non_entailment_counterexamples.append({"p": p_value, "q": q_value})
    if entailment_counterexamples:
        raise AssertionError("modus ponens entailment has a counterexample")
    if non_entailment_counterexamples != [{"p": False, "q": True}]:
        raise AssertionError("declared non-entailment countermodel mismatch")
    return {
        "scope": "tautology_contradiction_satisfiability_and_entailment_examples",
        "assignment_count": len(assignments),
        "tautology_all_true": True,
        "contradiction_all_false": True,
        "satisfiable_non_tautology_true_rows": sum(satisfiable_values),
        "modus_ponens_entailment_counterexamples": entailment_counterexamples,
        "or_does_not_entail_left_counterexamples": non_entailment_counterexamples,
    }


def literal_for(symbol: object, truth_value: bool) -> object:
    return symbol if truth_value else Not(symbol)


def maxterm_literal_for(symbol: object, truth_value: bool) -> object:
    return Not(symbol) if truth_value else symbol


def audit_normal_forms() -> dict:
    symbols = sympy.symbols("P Q R")
    assignments = list(itertools.product((False, True), repeat=3))
    total_evaluations = 0
    signatures = set()
    for mask in range(2 ** len(assignments)):
        truth_vector = tuple(bool(mask & (1 << index)) for index in range(len(assignments)))
        signatures.add(truth_vector)
        minterms = [
            And(*[literal_for(symbol, bit) for symbol, bit in zip(symbols, assignment)])
            for assignment, expected in zip(assignments, truth_vector)
            if expected
        ]
        maxterms = [
            Or(*[maxterm_literal_for(symbol, bit) for symbol, bit in zip(symbols, assignment)])
            for assignment, expected in zip(assignments, truth_vector)
            if not expected
        ]
        pdnf = Or(*minterms) if minterms else sympy.false
        pcnf = And(*maxterms) if maxterms else sympy.true
        for assignment, expected in zip(assignments, truth_vector):
            substitutions = dict(zip(symbols, assignment))
            if value(pdnf, substitutions) is not expected:
                raise AssertionError(f"PDNF reconstruction failed for mask {mask}")
            if value(pcnf, substitutions) is not expected:
                raise AssertionError(f"PCNF reconstruction failed for mask {mask}")
            total_evaluations += 2
    if len(signatures) != 256:
        raise AssertionError("three-variable truth-function census is incomplete")
    return {
        "scope": "canonical_pdnf_pcnf_reconstruction_for_all_three_variable_truth_functions",
        "variable_count": 3,
        "truth_function_count": len(signatures),
        "assignment_count_per_function": len(assignments),
        "normal_form_evaluation_count": total_evaluations,
        "all_reconstructions_passed": True,
        "constant_false_and_true_cases_included": True,
    }


AUDITORS = {
    "truth_tables": audit_truth_tables,
    "algebra_laws": audit_algebra_laws,
    "tautologies": audit_tautologies,
    "normal_forms": audit_normal_forms,
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--log", required=True, type=Path)
    args = parser.parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    audit_kind = payload["audit_kind"]
    if audit_kind not in AUDITORS:
        raise ValueError(f"unsupported audit kind: {audit_kind}")
    details = AUDITORS[audit_kind]()
    result = {
        "audit_id": payload["audit_id"],
        "node_id": payload["node_id"],
        "timestamp": payload["execution_timestamp"],
        "status": "passed",
        **details,
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
    serialized = json.dumps(result, ensure_ascii=False, indent=2) + "\n"
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.log.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(serialized, encoding="utf-8")
    args.log.write_text("command_status=passed\nexit_code=0\n" + serialized, encoding="utf-8")
    print(f"audit_id={result['audit_id']}")
    print(f"node_id={result['node_id']}")
    print("status=passed")
    print(f"scope={result['scope']}")
    print(f"output_ref={args.output.as_posix()}")
    print(f"log_ref={args.log.as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
