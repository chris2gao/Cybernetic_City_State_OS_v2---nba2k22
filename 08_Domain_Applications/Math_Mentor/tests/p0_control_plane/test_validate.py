from __future__ import annotations

import sys
from tempfile import TemporaryDirectory
import unittest
from pathlib import Path


MATH_MENTOR = Path(__file__).resolve().parents[2]
REPO_ROOT = Path(__file__).resolve().parents[4]
if str(MATH_MENTOR) not in sys.path:
    sys.path.insert(0, str(MATH_MENTOR))

from p0_control_plane.validate import (  # noqa: E402
    EXPECTED_SOURCE_HEAD,
    ValidationError,
    _validate_materialized_output,
    validate_control_plane,
)
from p0_control_plane.identity import canonical_json_bytes  # noqa: E402
from p0_control_plane.registry_builder import current_head  # noqa: E402


class ControlPlaneValidationTests(unittest.TestCase):
    def test_materialization_is_schema_valid_deterministic_and_fail_closed(self) -> None:
        result = validate_control_plane(REPO_ROOT, EXPECTED_SOURCE_HEAD)

        self.assertEqual("passed", result["status"])
        self.assertEqual(2, result["repeat_builds"])
        self.assertTrue(result["byte_identical_repeatability"])
        self.assertTrue(result["materialized_outputs_match"])
        self.assertRegex(result["committed_materialization_head"], r"^[0-9a-f]{40}$")
        self.assertEqual(current_head(REPO_ROOT), result["committed_materialization_head"])
        self.assertTrue(result["committed_blob_bytes_match_generated"])
        self.assertTrue(result["worktree_json_content_matches_generated"])
        self.assertFalse(result["worktree_raw_bytes_used_for_commit_proof"])
        self.assertEqual(667, result["quantitative"]["root_candidates_parsed"])
        self.assertEqual(229, result["quantitative"]["staging_assets_excluded"])
        self.assertEqual(213, result["quantitative"]["staging_yaml_parse_pass"])
        self.assertEqual(15, result["quantitative"]["staging_yaml_parse_fail"])
        self.assertEqual(420, result["quantitative"]["candidate_edges_unapproved"])
        self.assertEqual(0, result["quantitative"]["consumer_allowed"])
        self.assertFalse(result["runtime_activation_performed"])

    def test_crlf_worktree_does_not_replace_or_break_committed_blob_proof(self) -> None:
        document = {"schema_version": "test.v1", "value": 1}
        generated_bytes = canonical_json_bytes(document)

        with TemporaryDirectory() as temp_dir:
            worktree_path = Path(temp_dir) / "REGISTRY.json"
            worktree_path.write_bytes(generated_bytes[:-1] + b"\r\n")
            self.assertNotEqual(generated_bytes, worktree_path.read_bytes())

            parsed = _validate_materialized_output(
                "REGISTRY.json",
                document,
                generated_bytes,
                generated_bytes,
                worktree_path,
            )
            self.assertEqual(document, parsed)

            worktree_path.write_bytes(b'{"schema_version":"test.v1","value":2}\r\n')
            with self.assertRaisesRegex(
                ValidationError, "worktree materialized JSON content differs"
            ):
                _validate_materialized_output(
                    "REGISTRY.json",
                    document,
                    generated_bytes,
                    generated_bytes,
                    worktree_path,
                )


if __name__ == "__main__":
    unittest.main()
