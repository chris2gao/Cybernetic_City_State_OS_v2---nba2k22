import contextlib
import io
import os
import tempfile
import unittest
from unittest import mock

import bulk_evaluator
import sandbox_evaluator


def node_yaml(sanity_code=None, semantic_audit=None, implementation_code=None, wrapped=False):
    fields = ["id: TEST-001"]
    if implementation_code is not None:
        fields.extend([
            "code_implementation: |",
            *[f"  {line}" for line in implementation_code.splitlines()],
        ])
    if sanity_code is not None:
        fields.extend([
            "v8_sanity_audit:",
            "  sympy_pseudo_code: |",
            *[f"    {line}" for line in sanity_code.splitlines()],
        ])
    if semantic_audit is not None:
        fields.extend([
            "v9_semantic_audit:",
            f"  review_note: {semantic_audit}",
        ])
    if wrapped:
        fields = ["concept_node:", *[f"  {line}" for line in fields]]
    return "\n".join(fields) + "\n"


class SandboxEvaluatorStatusTests(unittest.TestCase):
    def test_assertion_error_is_failed(self):
        result = sandbox_evaluator.evaluate_yaml_content(
            node_yaml(sanity_code="assert 1 == 2")
        )
        self.assertEqual(result["status"], "failed")
        self.assertIn("Assertion Failed", result["message"])

    def test_normal_executable_sanity_is_passed(self):
        result = sandbox_evaluator.evaluate_yaml_content(
            node_yaml(sanity_code="import sympy as sp\nx = sp.Symbol('x')\nassert sp.diff(x**2, x) == 2*x")
        )
        self.assertEqual(result["status"], "passed")
        self.assertEqual(result["warnings"], [])

    def test_semantic_only_requires_review_for_wrapped_schema(self):
        result = sandbox_evaluator.evaluate_yaml_content(
            node_yaml(semantic_audit="present", wrapped=True)
        )
        self.assertEqual(result["status"], "review_required")
        self.assertIn("not machine validated", result["message"])
        self.assertIn("semantic_audit_not_machine_validated", result["warnings"])

    def test_semantic_only_code_anchor_failure_still_requires_review(self):
        result = sandbox_evaluator.evaluate_yaml_content(
            node_yaml(
                implementation_code="raise RuntimeError('anchor failure')",
                semantic_audit="present",
            )
        )
        self.assertEqual(result["status"], "review_required")
        self.assertIn("code_anchor_execution_failed", result["warnings"])

    def test_semantic_audit_alias_requires_review(self):
        yaml_content = "id: TEST-ALIAS\nsemantic_audit:\n  review_note: present\n"
        result = sandbox_evaluator.evaluate_yaml_content(yaml_content)
        self.assertEqual(result["status"], "review_required")
        self.assertIn("semantic_audit_not_machine_validated", result["warnings"])

    def test_optional_dependency_skip_is_not_a_pass(self):
        with mock.patch.object(
            sandbox_evaluator,
            "optional_dependency_available",
            return_value=False,
        ):
            result = sandbox_evaluator.evaluate_yaml_content(
                node_yaml(
                    implementation_code="import torch\nvalue = torch.tensor([1])",
                    sanity_code="assert 2 + 2 == 4",
                )
            )
        self.assertEqual(result["status"], "skipped")
        self.assertIn("dependency_missing:torch", result["warnings"])
        self.assertIn("implementation_not_executed", result["warnings"])

    def test_shape_only_audit_passes_with_warning(self):
        result = sandbox_evaluator.evaluate_yaml_content(
            node_yaml(
                sanity_code=(
                    "import sympy as sp\n"
                    "matrix = sp.zeros(2, 2)\n"
                    "assert matrix.shape == (2, 2)"
                )
            )
        )
        self.assertEqual(result["status"], "warning")
        self.assertIn("shape_only_or_shallow_audit_risk", result["warnings"])


class BulkEvaluatorStatusTests(unittest.TestCase):
    def test_bulk_summary_uses_precise_statuses_without_overclaim(self):
        with tempfile.TemporaryDirectory() as directory:
            fixtures = {
                "passed.yaml": node_yaml(sanity_code="assert 2 + 2 == 4"),
                "semantic.yaml": node_yaml(semantic_audit="present", wrapped=True),
                "shape.yaml": node_yaml(sanity_code="value = [1, 2]\nassert len(value) == 2"),
            }
            for filename, content in fixtures.items():
                with open(os.path.join(directory, filename), "w", encoding="utf-8") as handle:
                    handle.write(content)

            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                report = bulk_evaluator.run_bulk_evaluation(directory)

        rendered = output.getvalue()
        self.assertEqual(report["status_counts"]["passed"], 1)
        self.assertEqual(report["status_counts"]["review_required"], 1)
        self.assertEqual(report["status_counts"]["warning"], 1)
        self.assertIn("Review Required: 1", rendered)
        self.assertIn("Warning Status: 1", rendered)
        self.assertNotIn("Entire graph is mathematically sound", rendered)


if __name__ == "__main__":
    unittest.main()
