from __future__ import annotations

import sys
import unittest
from pathlib import Path


MATH_MENTOR = Path(__file__).resolve().parents[2]
REPO_ROOT = Path(__file__).resolve().parents[4]
if str(MATH_MENTOR) not in sys.path:
    sys.path.insert(0, str(MATH_MENTOR))

from p0_control_plane.validate import (  # noqa: E402
    EXPECTED_SOURCE_HEAD,
    validate_control_plane,
)


class ControlPlaneValidationTests(unittest.TestCase):
    def test_materialization_is_schema_valid_deterministic_and_fail_closed(self) -> None:
        result = validate_control_plane(REPO_ROOT, EXPECTED_SOURCE_HEAD)

        self.assertEqual("passed", result["status"])
        self.assertEqual(2, result["repeat_builds"])
        self.assertTrue(result["byte_identical_repeatability"])
        self.assertTrue(result["materialized_outputs_match"])
        self.assertEqual(667, result["quantitative"]["root_candidates_parsed"])
        self.assertEqual(229, result["quantitative"]["staging_assets_excluded"])
        self.assertEqual(213, result["quantitative"]["staging_yaml_parse_pass"])
        self.assertEqual(15, result["quantitative"]["staging_yaml_parse_fail"])
        self.assertEqual(420, result["quantitative"]["candidate_edges_unapproved"])
        self.assertEqual(0, result["quantitative"]["consumer_allowed"])
        self.assertFalse(result["runtime_activation_performed"])


if __name__ == "__main__":
    unittest.main()
