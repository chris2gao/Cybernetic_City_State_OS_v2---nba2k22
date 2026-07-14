from __future__ import annotations

import sys
import unittest
from pathlib import Path


MATH_MENTOR = Path(__file__).resolve().parents[2]
REPO_ROOT = Path(__file__).resolve().parents[4]
if str(MATH_MENTOR) not in sys.path:
    sys.path.insert(0, str(MATH_MENTOR))

from p0_control_plane.staging_diagnostics import scan_staging  # noqa: E402


SOURCE_HEAD = "764d03d7d0a9ad553f4f3868699b06d9de5553ea"


class StagingDiagnosticsTests(unittest.TestCase):
    def test_staging_is_fully_measured_but_never_identity_capable(self) -> None:
        result = scan_staging(REPO_ROOT, SOURCE_HEAD)

        self.assertEqual(
            {
                "tracked_staging_assets": 229,
                "staging_yaml_files": 228,
                "staging_non_yaml_files": 1,
                "yaml_parse_pass": 213,
                "yaml_parse_fail": 15,
                "parsed_non_mapping": 0,
                "parsed_without_top_level_id": 7,
                "basename_shadows_of_root_candidates": 195,
                "strict_identity_overlap_with_root": 180,
                "raw_content_identical_to_root": 0,
                "identity_resolution_from_staging": 0,
            },
            result["summary"],
        )
        self.assertEqual(15, len(result["parse_failure_paths"]))
        self.assertTrue(result["policy"]["diagnostic_only"])
        self.assertFalse(result["policy"]["identity_resolution_allowed"])
        self.assertFalse(result["policy"]["staging_precedence_allowed"])
        self.assertFalse(result["policy"]["runtime_activation_performed"])

if __name__ == "__main__":
    unittest.main()
