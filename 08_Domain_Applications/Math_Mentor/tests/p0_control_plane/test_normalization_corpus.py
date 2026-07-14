from __future__ import annotations

import json
import subprocess
import sys
import unittest
from collections import Counter
from pathlib import Path

from jsonschema import Draft202012Validator


MATH_MENTOR = Path(__file__).resolve().parents[2]
REPO_ROOT = Path(__file__).resolve().parents[4]
if str(MATH_MENTOR) not in sys.path:
    sys.path.insert(0, str(MATH_MENTOR))

from p0_control_plane.normalization import parse_and_normalize_node


STAGE0_SOURCE_HEAD = "cefd164472ecbb7095c1aa2c243c34fbec5b51f4"


class LiveCorpusNormalizationTests(unittest.TestCase):
    def test_all_667_candidates_normalize_fail_closed_across_four_eras(self) -> None:
        inventory = REPO_ROOT / ".ai" / "PROGRAM_RUNS" / "math-mentor-knowledge-completion-stage-0-inventory-0001" / "inventory" / "node_classification.json"
        stage0 = json.loads(inventory.read_text(encoding="utf-8"))
        records = stage0["records"]
        candidate_paths = {record["path"] for record in records}
        stage0_canonical = {
            record["path"]
            for record in records
            if record["classification"] == "canonical_teaching_node"
        }
        changed_output = subprocess.check_output(
            [
                "git",
                "diff",
                "--name-only",
                STAGE0_SOURCE_HEAD,
                "HEAD",
                "--",
                "08_Domain_Applications/Math_Mentor/Pure_Math_Intuition_DB",
            ],
            cwd=REPO_ROOT,
            text=True,
            encoding="utf-8",
        )
        changed_candidates = set(changed_output.splitlines()) & candidate_paths

        schema = json.loads((MATH_MENTOR / "NORMALIZED_NODE_SCHEMA.json").read_text(encoding="utf-8"))
        validator = Draft202012Validator(schema)
        eras: Counter[str] = Counter()
        identities: Counter[str] = Counter()
        invalid: list[tuple[str, str]] = []
        missing_identity_paths: list[str] = []

        for relative_path in sorted(candidate_paths):
            normalized = parse_and_normalize_node(
                (REPO_ROOT / relative_path).read_bytes(),
                path=relative_path,
                stage0_canonical_paths=stage0_canonical,
                changed_since_stage0_paths=changed_candidates,
            )
            eras[normalized["schema_era"]] += 1
            identities[normalized["identity"]["status"]] += 1
            if normalized["identity"]["status"] == "missing":
                missing_identity_paths.append(relative_path)
            self.assertFalse(normalized["consumer_allowed"])
            for error in validator.iter_errors(normalized):
                invalid.append((relative_path, error.message))

        self.assertEqual(667, len(records))
        self.assertEqual({"E1": 143, "E2": 496, "E3": 8, "E4": 20}, dict(eras))
        self.assertEqual({"resolved": 666, "missing": 1}, dict(identities))
        self.assertEqual(
            [
                "08_Domain_Applications/Math_Mentor/Pure_Math_Intuition_DB/topology_compactness.yaml"
            ],
            missing_identity_paths,
        )
        self.assertEqual([], invalid)


if __name__ == "__main__":
    unittest.main()
