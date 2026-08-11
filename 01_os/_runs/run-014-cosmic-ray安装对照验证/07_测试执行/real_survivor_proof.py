from __future__ import annotations

import argparse
from contextlib import redirect_stderr, redirect_stdout
from io import StringIO
import json
from pathlib import Path
import sys
import tempfile
from typing import Any


ANNOTATION_REPLACEMENTS = [
    "str + int",
    "str - int",
    "str * int",
    "str / int",
    "str // int",
    "str % int",
    "str ** int",
    "str >> int",
    "str << int",
    "str & int",
    "str ^ int",
]


def load_namespace(source: str, name: str = "target.inspect_schema_refs") -> dict[str, Any]:
    namespace: dict[str, Any] = {"__name__": name}
    exec(compile(source, "inspect_schema_refs.py", "exec"), namespace)
    return namespace


def execute_module(source: str, name: str) -> dict[str, Any]:
    original_argv = sys.argv
    stdout = StringIO()
    stderr = StringIO()
    exit_code: int | None = None
    sys.argv = ["inspect_schema_refs.py"]
    try:
        with redirect_stdout(stdout), redirect_stderr(stderr):
            try:
                load_namespace(source, name)
            except SystemExit as exc:
                exit_code = int(exc.code)
    finally:
        sys.argv = original_argv
    return {
        "exit_code": exit_code,
        "stdout": stdout.getvalue(),
        "stderr": stderr.getvalue(),
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("canonical_source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    source = args.canonical_source.read_text(encoding="utf-8")
    original = load_namespace(source)

    annotation_cases: list[dict[str, Any]] = []
    original_outputs = [
        original["_child_location"]("$", 3),
        original["_child_location"]("$", "雪"),
    ]
    for replacement in ANNOTATION_REPLACEMENTS:
        mutated_source = source.replace(
            "key: str | int",
            f"key: {replacement}",
            1,
        )
        mutated = load_namespace(mutated_source)
        mutated_outputs = [
            mutated["_child_location"]("$", 3),
            mutated["_child_location"]("$", "雪"),
        ]
        annotation_cases.append(
            {
                "replacement": replacement,
                "classification": "annotation_only_runtime_equivalent",
                "outputs_match": mutated_outputs == original_outputs,
                "annotation_is_string": isinstance(
                    mutated["_child_location"].__annotations__["key"],
                    str,
                ),
            }
        )

    guard_original = "if __name__ == \"__main__\":"
    guard_lt_source = source.replace(
        guard_original,
        "if __name__ < \"__main__\":",
        1,
    )
    guard_lte_source = source.replace(
        guard_original,
        "if __name__ <= \"__main__\":",
        1,
    )
    guard_is_source = source.replace(
        guard_original,
        "if __name__ is \"__main__\":",
        1,
    )
    distinct_main_name = "".join(["__", "main", "__"])
    interned_main_name = "__main__"
    guard_cases = {
        "eq_to_lt": {
            "classification": "genuine_gap",
            "original": execute_module(source, "__main__"),
            "mutant": execute_module(guard_lt_source, "__main__"),
        },
        "eq_to_lte": {
            "classification": "reachable_context_equivalent",
            "original_main": execute_module(source, "__main__"),
            "mutant_main": execute_module(guard_lte_source, "__main__"),
            "original_import": execute_module(source, "target.inspect_schema_refs"),
            "mutant_import": execute_module(
                guard_lte_source,
                "target.inspect_schema_refs",
            ),
        },
        "eq_to_is": {
            "classification": "genuine_semantic_gap",
            "equal_but_distinct_name": (
                distinct_main_name == interned_main_name
                and distinct_main_name is not interned_main_name
            ),
            "original": execute_module(source, distinct_main_name),
            "mutant": execute_module(guard_is_source, distinct_main_name),
        },
    }

    len_mutant = load_namespace(
        source.replace("if len(argv) != 2:", "if len(argv) < 2:", 1)
    )
    suffix_mutant = load_namespace(
        source.replace(
            'if path.suffix.lower() != ".json":',
            'if path.suffix.lower() > ".json":',
            1,
        )
    )
    with tempfile.TemporaryDirectory(prefix="run014-survivor-proof-") as temporary:
        temporary_path = Path(temporary)
        json_path = temporary_path / "valid.json"
        alternate_path = temporary_path / "valid.abc"
        json_path.write_text("{}", encoding="utf-8")
        alternate_path.write_text("{}", encoding="utf-8")

        with redirect_stdout(StringIO()), redirect_stderr(StringIO()):
            original_extra_args = original["main"](
                ["inspect_schema_refs.py", str(json_path), "extra"]
            )
            mutant_extra_args = len_mutant["main"](
                ["inspect_schema_refs.py", str(json_path), "extra"]
            )

        original_suffix_code = None
        try:
            original["inspect_schema"](alternate_path)
        except original["SchemaPolicyError"] as exc:
            original_suffix_code = exc.code
        suffix_mutant["inspect_schema"](alternate_path)

    gap_cases = {
        "argv_not_equal_to_less_than": {
            "classification": "genuine_gap",
            "original_exit": original_extra_args,
            "mutant_exit": mutant_extra_args,
            "behavior_differs": original_extra_args != mutant_extra_args,
        },
        "suffix_not_equal_to_greater_than": {
            "classification": "genuine_gap",
            "original_error_code": original_suffix_code,
            "mutant_accepts_valid_json_with_abc_suffix": True,
        },
    }

    annotation_passed = all(
        case["outputs_match"] and case["annotation_is_string"]
        for case in annotation_cases
    )
    guard_lt_differs = (
        guard_cases["eq_to_lt"]["original"]
        != guard_cases["eq_to_lt"]["mutant"]
    )
    guard_lte_matches = (
        guard_cases["eq_to_lte"]["original_main"]
        == guard_cases["eq_to_lte"]["mutant_main"]
        and guard_cases["eq_to_lte"]["original_import"]
        == guard_cases["eq_to_lte"]["mutant_import"]
    )
    guard_is_differs = (
        guard_cases["eq_to_is"]["original"]
        != guard_cases["eq_to_is"]["mutant"]
    )
    passed = (
        annotation_passed
        and guard_lt_differs
        and guard_lte_matches
        and guard_is_differs
        and gap_cases["argv_not_equal_to_less_than"]["behavior_differs"]
        and original_suffix_code == "CJV-R01-JSON-SUFFIX"
    )
    result = {
        "format": "run-014-real-survivor-proof-v1",
        "survivor_count": 16,
        "classification_counts": {
            "annotation_only_runtime_equivalent": 11,
            "reachable_context_equivalent": 1,
            "genuine_gap": 3,
            "genuine_semantic_gap": 1,
        },
        "annotation_cases": annotation_cases,
        "guard_cases": guard_cases,
        "gap_cases": gap_cases,
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
