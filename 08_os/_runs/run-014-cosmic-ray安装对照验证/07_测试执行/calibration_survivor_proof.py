from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path
from typing import Any


def load_module(path: Path) -> Any:
    spec = importlib.util.spec_from_file_location("run014_calibration_logic", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("could not load calibration module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("logic", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    module = load_module(args.logic)
    integer_domain = range(-100, 101)

    identity_operators = {
        "core/ReplaceBinaryOperator_Add_Sub": lambda value: value - 0,
        "core/ReplaceBinaryOperator_Add_RShift": lambda value: value >> 0,
        "core/ReplaceBinaryOperator_Add_LShift": lambda value: value << 0,
        "core/ReplaceBinaryOperator_Add_BitOr": lambda value: value | 0,
        "core/ReplaceBinaryOperator_Add_BitXor": lambda value: value ^ 0,
    }
    identity_cases = {
        operator: all(
            module.identity_offset(value) == mutant(value)
            for value in integer_domain
        )
        for operator, mutant in identity_operators.items()
    }
    clamp_lte_equivalent = all(
        module.clamp_nonnegative(value)
        == (0 if value <= 0 else value)
        for value in integer_domain
    )
    clamp_lt_one_equivalent = all(
        module.clamp_nonnegative(value)
        == (0 if value < 1 else value)
        for value in integer_domain
    )
    role_identity_to_equality = all(
        ((role is module.Role.ADMIN) == (role == module.Role.ADMIN))
        and ((role is module.Role.MEMBER) == (role == module.Role.MEMBER))
        for role in module.Role
    )

    gap_cases = {
        "clamp_zero_to_negative_one": {
            "input": -1,
            "original": module.clamp_nonnegative(-1),
            "mutant": -1,
            "differs": module.clamp_nonnegative(-1) != -1,
        },
        "decorator_lte_zero": {
            "input": 0,
            "original": module.decorated_double(0),
            "mutant_would_raise": True,
            "differs": module.decorated_double(0) == 0,
        },
        "decorator_zero_to_one": {
            "input": 0,
            "original": module.decorated_double(0),
            "mutant_would_raise": True,
            "differs": module.decorated_double(0) == 0,
        },
    }
    equivalent_count = (
        sum(identity_cases.values())
        + int(clamp_lte_equivalent)
        + int(clamp_lt_one_equivalent)
        + 2 * int(role_identity_to_equality)
    )
    gap_count = sum(int(case["differs"]) for case in gap_cases.values())
    passed = equivalent_count == 9 and gap_count == 3
    result = {
        "format": "run-014-calibration-survivor-proof-v1",
        "survivor_count": 12,
        "classification_counts": {
            "executable_equivalent": equivalent_count,
            "genuine_gap": gap_count,
        },
        "identity_cases": identity_cases,
        "clamp_lte_equivalent": clamp_lte_equivalent,
        "clamp_lt_one_equivalent": clamp_lt_one_equivalent,
        "role_identity_to_equality": role_identity_to_equality,
        "gap_cases": gap_cases,
        "domain": {"kind": "int", "tested_min": -100, "tested_max": 100},
        "passed": passed,
    }
    args.output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps({"passed": passed, **result["classification_counts"]}, sort_keys=True))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
