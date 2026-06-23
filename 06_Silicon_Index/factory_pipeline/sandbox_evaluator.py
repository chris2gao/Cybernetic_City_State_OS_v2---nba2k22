import ast
import json
import math
import sys

import sympy as sp
import yaml


STATUS_PASSED = "passed"
STATUS_FAILED = "failed"
STATUS_REVIEW_REQUIRED = "review_required"
STATUS_SKIPPED = "skipped"
STATUS_WARNING = "warning"

EXIT_CODES = {
    STATUS_PASSED: 0,
    STATUS_WARNING: 0,
    STATUS_FAILED: 1,
    STATUS_REVIEW_REQUIRED: 2,
    STATUS_SKIPPED: 3,
}

RESULT_PREFIX = "EVALUATOR_RESULT_JSON:"
OPTIONAL_IMPLEMENTATION_DEPENDENCIES = {"torch", "tensorflow", "scipy", "matplotlib"}
YAML_LATEX_ESCAPES = [
    "\\a", "\\b", "\\c", "\\d", "\\e", "\\f", "\\g", "\\h", "\\i", "\\j",
    "\\k", "\\l", "\\m", "\\n", "\\o", "\\p", "\\q", "\\r", "\\s", "\\t",
    "\\u", "\\v", "\\w", "\\x", "\\y", "\\z", "\\A", "\\B", "\\C", "\\D",
    "\\E", "\\F", "\\G", "\\H", "\\I", "\\J", "\\K", "\\L", "\\M", "\\N",
    "\\O", "\\P", "\\Q", "\\R", "\\S", "\\T", "\\U", "\\V", "\\W", "\\X",
    "\\Y", "\\Z",
]

STRUCTURAL_ATTRIBUTES = {"shape", "size", "ndim", "dim"}
STRUCTURAL_CALLS = {"len", "isinstance", "numel"}


def make_result(status, message, warnings=None, details=None):
    return {
        "status": status,
        "message": message,
        "warnings": list(warnings or []),
        "details": dict(details or {}),
    }


def optional_dependency_available(name):
    try:
        __import__(name)
        return True
    except Exception:
        return False


def imported_optional_dependencies(code):
    try:
        tree = ast.parse(code)
    except (SyntaxError, TypeError):
        return set()

    dependencies = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            dependencies.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            dependencies.add(node.module.split(".")[0])
    return dependencies & OPTIONAL_IMPLEMENTATION_DEPENDENCIES


def create_restricted_globals():
    try:
        import torch
    except Exception:
        torch = None

    return {
        "__builtins__": {
            "__build_class__": __build_class__,
            "abs": abs, "all": all, "any": any, "bin": bin, "bool": bool,
            "complex": complex, "dict": dict, "divmod": divmod, "enumerate": enumerate,
            "filter": filter, "float": float, "format": format, "frozenset": frozenset,
            "getattr": getattr, "hasattr": hasattr, "hash": hash, "hex": hex,
            "int": int, "isinstance": isinstance, "issubclass": issubclass,
            "iter": iter, "len": len, "list": list, "map": map, "max": max,
            "min": min, "next": next, "object": object, "oct": oct, "pow": pow,
            "print": print, "property": property, "range": range, "repr": repr,
            "reversed": reversed, "round": round, "set": set, "slice": slice,
            "sorted": sorted, "str": str, "sum": sum, "super": super,
            "tuple": tuple, "type": type, "zip": zip,
            "AssertionError": AssertionError, "Exception": Exception,
            "ValueError": ValueError, "TypeError": TypeError, "KeyError": KeyError,
            "IndexError": IndexError, "RecursionError": RecursionError,
            "StopIteration": StopIteration, "__import__": __import__,
        },
        "math": math,
        "sympy": sp,
        "sp": sp,
        "torch": torch,
        "__name__": "__sandbox__",
    }


def evaluate_snippet(code, label):
    if isinstance(code, dict):
        code = code.get("code") or code.get("snippet") or ""

    if not isinstance(code, str):
        return make_result(
            STATUS_FAILED,
            f"{label} must be a string code block, got {type(code).__name__}.",
        )

    if label == "code_implementation":
        missing = sorted(
            dependency
            for dependency in imported_optional_dependencies(code)
            if not optional_dependency_available(dependency)
        )
        if missing:
            warnings = [f"dependency_missing:{dependency}" for dependency in missing]
            return make_result(
                STATUS_SKIPPED,
                f"{label} skipped because optional dependencies are unavailable: {', '.join(missing)}",
                warnings,
                {"missing_dependencies": missing},
            )

    restricted_globals = create_restricted_globals()

    try:
        compiled_code = compile(code, f"<{label}>", "exec")
    except SyntaxError as error:
        return make_result(STATUS_FAILED, f"{label} Syntax Error: {error}")

    try:
        exec(compiled_code, restricted_globals)
        return make_result(STATUS_PASSED, f"{label} executable sanity passed")
    except AssertionError as error:
        return make_result(STATUS_FAILED, f"{label} Assertion Failed: {error}")
    except ModuleNotFoundError as error:
        missing = getattr(error, "name", "")
        if label == "code_implementation" and missing in OPTIONAL_IMPLEMENTATION_DEPENDENCIES:
            return make_result(
                STATUS_SKIPPED,
                f"{label} skipped because optional dependency is unavailable: {missing}",
                [f"dependency_missing:{missing}"],
                {"missing_dependencies": [missing]},
            )
        return make_result(
            STATUS_FAILED,
            f"{label} Runtime Error: {type(error).__name__}: {error}",
        )
    except Exception as error:
        return make_result(
            STATUS_FAILED,
            f"{label} Runtime Error: {type(error).__name__}: {error}",
        )


def run_snippet(code, label):
    """Compatibility wrapper for callers that still expect (success, message)."""
    result = evaluate_snippet(code, label)
    success = result["status"] in {STATUS_PASSED, STATUS_WARNING}
    return success, result["message"]


def call_name(node):
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return node.attr
    return None


def assertion_is_structural_only(test):
    if isinstance(test, ast.Constant) and test.value is True:
        return True

    has_structural_signal = False
    for node in ast.walk(test):
        if isinstance(node, ast.Attribute) and node.attr in STRUCTURAL_ATTRIBUTES:
            has_structural_signal = True
        elif isinstance(node, ast.Call):
            name = call_name(node.func)
            if name in STRUCTURAL_CALLS:
                has_structural_signal = True
            else:
                return False
    return has_structural_signal


def detect_shape_only_or_shallow_audit(code):
    try:
        tree = ast.parse(code)
    except (SyntaxError, TypeError):
        return False

    assertions = [node for node in ast.walk(tree) if isinstance(node, ast.Assert)]
    if not assertions:
        return True
    return all(assertion_is_structural_only(node.test) for node in assertions)


def load_yaml_content(yaml_content):
    if "\\n" in yaml_content and yaml_content.count("\n") <= 2:
        yaml_content = yaml_content.replace("\\n", "\n")

    try:
        return yaml.safe_load(yaml_content)
    except yaml.YAMLError:
        escaped_content = yaml_content
        for escape in YAML_LATEX_ESCAPES:
            escaped_content = escaped_content.replace(escape, "\\" + escape)
        return yaml.safe_load(escaped_content)


def evaluate_yaml_content(yaml_content):
    try:
        data = load_yaml_content(yaml_content)
        if not isinstance(data, dict):
            return make_result(STATUS_FAILED, "YAML root must be a mapping.")

        concept = data.get("concept_node", data)
        if not isinstance(concept, dict):
            return make_result(STATUS_FAILED, "concept_node must be a mapping.")

        audit = concept.get("v8_sanity_audit") or {}
        semantic_audit = concept.get("v9_semantic_audit") or concept.get("semantic_audit") or {}
        implementation_code = concept.get("code_implementation", "")
        sanity_code = audit.get("sympy_pseudo_code", "") if isinstance(audit, dict) else ""
        node_id = concept.get("id", "UNKNOWN")
        semantic_only = bool(semantic_audit) and not sanity_code

        warnings = []
        implementation_status = None
        if implementation_code:
            implementation_result = evaluate_snippet(implementation_code, "code_implementation")
            implementation_status = implementation_result["status"]
            warnings.extend(implementation_result["warnings"])
            if implementation_status == STATUS_FAILED:
                if semantic_only:
                    warnings.append("code_anchor_execution_failed")
                else:
                    implementation_result["details"]["node_id"] = node_id
                    return implementation_result

        if not sanity_code:
            if semantic_audit:
                warnings.append("semantic_audit_not_machine_validated")
                if implementation_status == STATUS_SKIPPED:
                    warnings.append("implementation_not_executed")
                return make_result(
                    STATUS_REVIEW_REQUIRED,
                    "Semantic audit present; review required because it is not machine validated.",
                    warnings,
                    {"node_id": node_id, "semantic_audit_present": True},
                )
            if implementation_status == STATUS_SKIPPED:
                warnings.append("sanity_audit_missing")
                return make_result(
                    STATUS_SKIPPED,
                    "Implementation skipped and no executable sanity audit is available.",
                    warnings,
                    {"node_id": node_id},
                )
            return make_result(
                STATUS_FAILED,
                "No v8_sanity_audit.sympy_pseudo_code or semantic audit found in YAML.",
                warnings,
                {"node_id": node_id},
            )

        sanity_result = evaluate_snippet(sanity_code, "v8_sanity_audit.sympy_pseudo_code")
        warnings.extend(sanity_result["warnings"])
        if sanity_result["status"] == STATUS_FAILED:
            sanity_result["warnings"] = warnings
            sanity_result["details"]["node_id"] = node_id
            return sanity_result

        if detect_shape_only_or_shallow_audit(sanity_code):
            warnings.append("shape_only_or_shallow_audit_risk")

        if implementation_status == STATUS_SKIPPED:
            warnings.append("implementation_not_executed")
            return make_result(
                STATUS_SKIPPED,
                "Executable sanity completed, but code_implementation was skipped.",
                warnings,
                {"node_id": node_id},
            )

        if "shape_only_or_shallow_audit_risk" in warnings:
            return make_result(
                STATUS_WARNING,
                "Executable sanity passed with a shape-only or shallow-audit warning.",
                warnings,
                {"node_id": node_id},
            )

        return make_result(
            STATUS_PASSED,
            "Executable sanity passed; this result does not establish mathematical correctness.",
            warnings,
            {"node_id": node_id},
        )
    except Exception as error:
        return make_result(STATUS_FAILED, f"YAML Parsing Error: {error}")


def run_sanity_audit(yaml_content):
    """Compatibility wrapper for callers that still expect (success, message)."""
    result = evaluate_yaml_content(yaml_content)
    success = result["status"] in {STATUS_PASSED, STATUS_WARNING}
    return success, result["message"]


def print_result(result):
    print(f"[{result['status'].upper()}] {result['message']}")
    for warning in result["warnings"]:
        print(f"[WARNING] {warning}")
    print(f"{RESULT_PREFIX}{json.dumps(result, ensure_ascii=False, sort_keys=True)}")


def main(argv=None):
    argv = argv or sys.argv
    if len(argv) < 2:
        print("Usage: python sandbox_evaluator.py <path_to_yaml>")
        return 1

    with open(argv[1], "r", encoding="utf-8") as file_handle:
        content = file_handle.read()

    result = evaluate_yaml_content(content)
    print_result(result)
    return EXIT_CODES[result["status"]]


if __name__ == "__main__":
    sys.exit(main())
