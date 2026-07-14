from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path

from jsonschema import Draft202012Validator


MATH_MENTOR = Path(__file__).resolve().parents[2]
if str(MATH_MENTOR) not in sys.path:
    sys.path.insert(0, str(MATH_MENTOR))

from p0_control_plane.normalization import normalize_node, parse_and_normalize_node


class NormalizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        schema = json.loads((MATH_MENTOR / "NORMALIZED_NODE_SCHEMA.json").read_text(encoding="utf-8"))
        cls.validator = Draft202012Validator(schema)

    def assert_valid(self, value: dict) -> None:
        errors = sorted(self.validator.iter_errors(value), key=lambda item: list(item.path))
        self.assertEqual([], [error.message for error in errors])

    def test_e1_wrapper_is_structurally_normalized_without_promotion(self) -> None:
        raw = b"""concept_node:\n  id: ARITHMETIC-001\n  mode: A\n  title: arithmetic\n  sub_topics: [addition]\n"""
        result = parse_and_normalize_node(raw, path="db/ARITHMETIC-001.yaml")
        self.assertEqual("E1", result["schema_era"])
        self.assertEqual("ARITHMETIC-001", result["identity"]["strict_id"])
        self.assertEqual("MathLane_A", result["routing"]["math_lane"])
        self.assertFalse(result["consumer_allowed"])
        self.assertEqual("not_evaluated", result["mathematical_truth_status"])
        self.assert_valid(result)

    def test_e2_flat_schema(self) -> None:
        raw = b"id: ABSTRACT-001\nmode: B\nconcept_name: structure\nsub_topics: []\n"
        result = parse_and_normalize_node(raw, path="db/ABSTRACT-001.yaml")
        self.assertEqual("E2", result["schema_era"])
        self.assertEqual("MathLane_B", result["routing"]["math_lane"])
        self.assert_valid(result)

    def test_e3_and_e4_use_provenance_not_guessing(self) -> None:
        document = {"id": "CALCULUS-265", "mode": "A"}
        e3_path = "db/CALCULUS-265.yaml"
        e4_path = "db/ANALYTIC_NT-684.yaml"
        e3 = normalize_node(
            document,
            path=e3_path,
            source_sha256="0" * 64,
            stage0_canonical_paths=[e3_path],
        )
        e4 = normalize_node(
            document,
            path=e4_path,
            source_sha256="1" * 64,
            stage0_canonical_paths=[e4_path],
            changed_since_stage0_paths=[e4_path],
        )
        self.assertEqual("E3", e3["schema_era"])
        self.assertEqual("E4", e4["schema_era"])
        self.assert_valid(e3)
        self.assert_valid(e4)

    def test_missing_identity_never_falls_back_to_filename(self) -> None:
        result = normalize_node(
            {"Concept": "compactness"},
            path="db/topology_compactness.yaml",
            source_sha256="2" * 64,
        )
        self.assertEqual("missing", result["identity"]["status"])
        self.assertIsNone(result["identity"]["strict_id"])
        self.assertFalse(result["consumer_allowed"])
        self.assert_valid(result)

    def test_conflicting_strict_locators_fail_closed(self) -> None:
        result = normalize_node(
            {"id": "NODE-001", "node_id": "NODE-002"},
            path="db/NODE-001.yaml",
            source_sha256="3" * 64,
        )
        self.assertEqual("conflict", result["identity"]["status"])
        self.assertIsNone(result["identity"]["strict_id"])
        self.assertFalse(result["consumer_allowed"])
        self.assert_valid(result)


if __name__ == "__main__":
    unittest.main()
