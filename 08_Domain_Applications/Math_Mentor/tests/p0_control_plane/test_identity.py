from __future__ import annotations

import json
import sys
import unittest
import uuid
from pathlib import Path


MATH_MENTOR = Path(__file__).resolve().parents[2]
if str(MATH_MENTOR) not in sys.path:
    sys.path.insert(0, str(MATH_MENTOR))

from p0_control_plane.identity import (
    IdentityError,
    attach_payload_sha256,
    canonical_json_bytes,
    canonical_node_uuid,
    distinct_claim_ids,
    namespace_uuid,
    normalize_repo_path,
    self_alias_claims,
    strict_identity,
    unparsed_fullwidth_alias_claims,
)


class IdentityPrimitiveTests(unittest.TestCase):
    def test_namespace_and_bootstrap_uuid_are_fixed_uuidv5(self) -> None:
        namespace = namespace_uuid(
            "https://github.com/chris2gao/"
            "Cybernetic_City_State_OS_v2---teacher#Math_Mentor/control-plane/v1"
        )
        self.assertEqual("e70d71ef-5916-5991-9e88-9e93fc07c31e", str(namespace))
        value = canonical_node_uuid(
            namespace,
            "08_Domain_Applications/Math_Mentor/"
            "Pure_Math_Intuition_DB/ALGEBRA-001.yaml",
        )
        self.assertEqual("aa56f098-034c-5faa-a061-94fe12e862cf", value)
        self.assertEqual(5, uuid.UUID(value).version)

    def test_path_normalization_is_exact_and_fail_closed(self) -> None:
        self.assertEqual("a/b.yaml", normalize_repo_path("a\\b.yaml"))
        with self.assertRaises(IdentityError):
            normalize_repo_path("../a.yaml")
        with self.assertRaises(IdentityError):
            normalize_repo_path("C:/a.yaml")

    def test_strict_identity_never_falls_back_to_filename_or_fuzzy_fields(self) -> None:
        missing = strict_identity({"filename": "NODE-001.yaml", "title": "NODE-001"})
        self.assertEqual("missing", missing.status)
        self.assertIsNone(missing.value)
        resolved = strict_identity({"concept_node": {"node_meta": {"id": "NODE-001"}}})
        self.assertEqual("NODE-001", resolved.value)
        self.assertEqual("concept_node.node_meta.id", resolved.locator)

    def test_redundant_and_conflicting_strict_locators_are_distinct(self) -> None:
        redundant = strict_identity({"id": "NODE-001", "node_id": "NODE-001"})
        self.assertEqual("resolved_redundant", redundant.status)
        conflicting = strict_identity({"id": "NODE-001", "node_id": "NODE-002"})
        self.assertEqual("conflicting", conflicting.status)
        self.assertIsNone(conflicting.value)

    def test_ascii_claims_bind_but_fullwidth_claims_are_diagnostic_only(self) -> None:
        document = {
            "concept_name": "ASCII (n_12)",
            "concept_node": {"concept_name": "alternate (n_13)"},
            "metadata": {"title": "fullwidth （n_14）"},
        }
        self.assertEqual(
            ("n_12", "n_13"),
            distinct_claim_ids(self_alias_claims(document)),
        )
        self.assertEqual(
            ("n_14",),
            distinct_claim_ids(unparsed_fullwidth_alias_claims(document)),
        )

    def test_canonical_json_is_sorted_lf_terminated_and_hash_stable(self) -> None:
        rendered = canonical_json_bytes({"z": 1, "a": "数学"})
        self.assertEqual(b'{"a":"\xe6\x95\xb0\xe5\xad\xa6","z":1}\n', rendered)
        first = attach_payload_sha256({"z": 1, "a": "数学"})
        second = attach_payload_sha256(json.loads(canonical_json_bytes(first)))
        self.assertEqual(first, second)


if __name__ == "__main__":
    unittest.main()
