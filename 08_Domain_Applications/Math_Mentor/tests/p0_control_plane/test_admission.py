from __future__ import annotations

from copy import deepcopy
from datetime import datetime
import json
from pathlib import Path
import sys
import unittest


MATH_MENTOR_ROOT = Path(__file__).resolve().parents[2]
if str(MATH_MENTOR_ROOT) not in sys.path:
    sys.path.insert(0, str(MATH_MENTOR_ROOT))

from p0_control_plane.admission import (  # noqa: E402
    ADM_AUTH_DENIED,
    ADM_AUTH_HUMAN_REQUIRED,
    ADM_AUTH_SCOPE_MISMATCH,
    ADM_BLOB_MISMATCH,
    ADM_BRIDGE_ADMISSION_NOT_IMPLEMENTED,
    ADM_EVIDENCE_STALE,
    ADM_IDENTITY_CONFLICT,
    ADM_LEGACY_EXECUTION_FORBIDDEN,
    ADM_LEGACY_STATUS_NOT_CANONICAL,
    ADM_MANUAL_REVIEW_REQUIRED,
    ADM_NON_CANONICAL_ASSET,
    ADM_STAGING_ASSET,
    ADM_STATE_WRITE_FORBIDDEN,
    AdmissionInputError,
    AdmissionRequest,
    evaluate_admission,
)
from p0_control_plane.authorization import (  # noqa: E402
    AuthorizationDecision,
    AuthorizationRequest,
    DeterministicTestTrustBoundaryAdapter,
    TrustBoundaryError,
    verify_authorization,
)


FIXTURE_PATH = Path(__file__).parent / "fixtures" / "admission" / "base_cases.json"
AUTH_FIXTURE_PATH = (
    Path(__file__).parent / "fixtures" / "authorization" / "base_cases.json"
)


class AdmissionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
        auth_fixture = json.loads(AUTH_FIXTURE_PATH.read_text(encoding="utf-8"))
        auth_request = AuthorizationRequest.from_mapping(auth_fixture["request"])
        adapter = DeterministicTestTrustBoundaryAdapter(
            {"admission-auth": auth_fixture["grant"]}
        )
        test_grant = adapter.authenticate("admission-auth", mode="test")
        now = datetime.fromisoformat(auth_fixture["now"].replace("Z", "+00:00"))
        cls.sealed_unrelated_allow = verify_authorization(
            auth_request,
            test_grant,
            now=now,
            environment_mode="test",
        )
        cls.sealed_deny = verify_authorization(
            auth_request,
            test_grant,
            now=now,
            environment_mode="production",
        )
        cls.auth_fixture = auth_fixture
        cls.auth_now = now

    def request(self, data=None) -> AdmissionRequest:
        return AdmissionRequest.from_mapping(
            deepcopy(data if data is not None else self.fixture["canonical_request"])
        )

    @property
    def allow(self):
        return self.allow_for()

    def allow_for(self, data=None):
        admission_data = deepcopy(
            data if data is not None else self.fixture["canonical_request"]
        )
        asset = admission_data["asset"]
        auth_fixture = deepcopy(self.auth_fixture)
        auth_fixture["request"]["operation"] = "repository.read"
        auth_fixture["request"]["effect_class"] = "read_only"
        auth_fixture["request"]["source_head"] = asset["source_head"]
        auth_fixture["request"]["resources"] = [
            {"repo_id": asset["repo_id"], "path": asset["path"]}
        ]
        auth_fixture["grant"]["binding"]["source_head"] = asset["source_head"]
        auth_fixture["grant"]["grant"]["allowed_operations"] = [
            "repository.read"
        ]
        auth_fixture["grant"]["grant"]["effect_ceiling"] = "read_only"
        auth_fixture["grant"]["grant"]["resource_selectors"] = [
            {
                "repo_id": asset["repo_id"],
                "path": asset["path"],
                "match": "exact",
                "operations": ["repository.read"],
            }
        ]
        adapter = DeterministicTestTrustBoundaryAdapter(
            {"asset-read": auth_fixture["grant"]}
        )
        grant = adapter.authenticate("asset-read", mode="test")
        return verify_authorization(
            AuthorizationRequest.from_mapping(auth_fixture["request"]),
            grant,
            now=self.auth_now,
            environment_mode="test",
        )

    def test_exact_canonical_asset_is_admitted_read_only(self):
        decision = evaluate_admission(self.request(), self.allow)

        self.assertEqual("admitted_manual_read_only", decision.status)
        self.assertTrue(decision.restrictions["read_only"])
        self.assertFalse(decision.restrictions["state_write_allowed"])
        self.assertIsNone(decision.canonical_learning_status)

    def test_authorization_and_admission_do_not_raise_each_other(self):
        denied = evaluate_admission(
            self.request(), self.sealed_deny
        )
        self.assertEqual("blocked", denied.status)
        self.assertIn(ADM_AUTH_DENIED, denied.reason_codes)

        unverified_allow = evaluate_admission(
            self.request(), deepcopy(self.fixture["authorization_allow"])
        )
        self.assertEqual("blocked", unverified_allow.status)
        self.assertIn(ADM_AUTH_HUMAN_REQUIRED, unverified_allow.reason_codes)

    def test_serialized_or_directly_constructed_allow_cannot_bypass_verifier(self):
        serialized = self.allow.to_dict()
        serialized_decision = evaluate_admission(self.request(), serialized)
        self.assertEqual("blocked", serialized_decision.status)
        self.assertIn(
            ADM_AUTH_HUMAN_REQUIRED, serialized_decision.reason_codes
        )

        with self.assertRaises(TrustBoundaryError):
            AuthorizationDecision(
                status="allow",
                reason_codes=("AUTH_OK",),
                authorization_context={"authorization_id": "forged"},
                requested_effect={},
                audit={},
                _seal=object(),
            )

    def test_sealed_allow_cannot_be_reused_for_an_unrelated_asset(self):
        decision = evaluate_admission(
            self.request(), self.sealed_unrelated_allow
        )
        self.assertEqual("blocked", decision.status)
        self.assertIn(ADM_AUTH_SCOPE_MISMATCH, decision.reason_codes)

    def test_serializing_does_not_expose_mutable_internal_context(self):
        decision = self.allow
        snapshot = decision.to_dict()
        snapshot["authorization_context"]["binding"]["source_head"] = (
            "dddddddddddddddddddddddddddddddddddddddd"
        )
        self.assertEqual(
            "764d03d7d0a9ad553f4f3868699b06d9de5553ea",
            decision.authorization_context["binding"]["source_head"],
        )
        with self.assertRaises(TypeError):
            decision.authorization_context["binding"]["source_head"] = "forged"

    def test_staging_path_is_quarantined_even_when_role_claims_canonical(self):
        data = deepcopy(self.fixture["canonical_request"])
        staging_path = (
            "08_Domain_Applications/Math_Mentor/Pure_Math_Intuition_DB/"
            "_Staging_Level6_Part2/ANALYTIC_NT-684.yaml"
        )
        data["asset"]["path"] = staging_path
        data["asset"]["asset_role"] = "canonical_node"
        data["identity_evidence"]["canonical_path"] = staging_path
        decision = evaluate_admission(self.request(data), self.allow_for(data))

        self.assertEqual("quarantined", decision.status)
        self.assertIn(ADM_STAGING_ASSET, decision.reason_codes)

    def test_nested_and_bridge_yaml_cannot_masquerade_as_canonical_node(self):
        for path in (
            "08_Domain_Applications/Math_Mentor/Pure_Math_Intuition_DB/nested/X.yaml",
            "08_Domain_Applications/Math_Mentor/Pure_Math_Intuition_DB/BRIDGE-X.yaml",
            "08_Domain_Applications/Math_Mentor/Pure_Math_Intuition_DB/tool.py",
        ):
            with self.subTest(path=path):
                data = deepcopy(self.fixture["canonical_request"])
                data["asset"]["path"] = path
                data["identity_evidence"]["canonical_path"] = path
                decision = evaluate_admission(
                    self.request(data), self.allow_for(data)
                )
                self.assertEqual("blocked", decision.status)
                self.assertIn(ADM_NON_CANONICAL_ASSET, decision.reason_codes)

    def test_canonical_bridge_admission_is_not_implemented_in_p0(self):
        data = deepcopy(self.fixture["canonical_request"])
        data["asset"]["asset_role"] = "canonical_bridge"
        decision = evaluate_admission(self.request(data), self.allow)

        self.assertEqual("blocked", decision.status)
        self.assertIn(
            ADM_BRIDGE_ADMISSION_NOT_IMPLEMENTED, decision.reason_codes
        )

    def test_identity_conflict_and_crosswalk_mismatch_are_quarantined(self):
        conflict = deepcopy(self.fixture["canonical_request"])
        conflict["identity_evidence"] = {
            "status": "conflict",
            "canonical_node_id": None,
            "registry_ref": None,
        }
        conflict_decision = evaluate_admission(self.request(conflict), self.allow)
        self.assertEqual("quarantined", conflict_decision.status)
        self.assertIn(ADM_IDENTITY_CONFLICT, conflict_decision.reason_codes)

        mismatch = deepcopy(self.fixture["canonical_request"])
        mismatch["identity_evidence"]["canonical_blob_oid"] = (
            "dddddddddddddddddddddddddddddddddddddddd"
        )
        mismatch_decision = evaluate_admission(self.request(mismatch), self.allow)
        self.assertEqual("quarantined", mismatch_decision.status)
        self.assertIn(ADM_IDENTITY_CONFLICT, mismatch_decision.reason_codes)

    def test_resolved_identity_requires_lowercase_uuidv5_and_exact_ref_shape(self):
        invalid_uuid = deepcopy(self.fixture["canonical_request"])
        invalid_uuid["identity_evidence"]["canonical_node_id"] = "ARITHMETIC-001"
        with self.assertRaises(AdmissionInputError):
            self.request(invalid_uuid)

        invalid_ref = deepcopy(self.fixture["canonical_request"])
        invalid_ref["identity_evidence"]["registry_ref"] = "trust-me"
        with self.assertRaises(AdmissionInputError):
            self.request(invalid_ref)

    def test_manual_review_status_is_never_promoted(self):
        data = deepcopy(self.fixture["canonical_request"])
        data["readiness_evidence"]["source_status"] = "manual_review_required"
        decision = evaluate_admission(self.request(data), self.allow)

        self.assertEqual("review_required", decision.status)
        self.assertIn(ADM_MANUAL_REVIEW_REQUIRED, decision.reason_codes)

    def test_stale_and_wrong_blob_evidence_fail_closed(self):
        stale = deepcopy(self.fixture["canonical_request"])
        stale["provenance_evidence"]["status"] = "stale"
        stale_decision = evaluate_admission(self.request(stale), self.allow)
        self.assertEqual("blocked", stale_decision.status)
        self.assertIn(ADM_EVIDENCE_STALE, stale_decision.reason_codes)

        wrong_blob = deepcopy(self.fixture["canonical_request"])
        wrong_blob["readiness_evidence"]["validated_blob_oid"] = (
            "dddddddddddddddddddddddddddddddddddddddd"
        )
        blob_decision = evaluate_admission(self.request(wrong_blob), self.allow)
        self.assertEqual("blocked", blob_decision.status)
        self.assertIn(ADM_BLOB_MISMATCH, blob_decision.reason_codes)

    def test_legacy_r5_passed_is_only_a_historical_import_claim(self):
        legacy = self.request(self.fixture["legacy_r5_request"])
        decision = evaluate_admission(
            legacy, self.allow_for(self.fixture["legacy_r5_request"])
        )

        self.assertEqual("admitted_legacy_import_read_only", decision.status)
        self.assertIsNone(decision.canonical_learning_status)
        self.assertFalse(decision.restrictions["state_write_allowed"])

        promoted = deepcopy(self.fixture["legacy_r5_request"])
        promoted["legacy_claim"]["requested_canonical_status"] = "graduated"
        rejected = evaluate_admission(
            self.request(promoted), self.allow_for(promoted)
        )
        self.assertEqual("blocked", rejected.status)
        self.assertIn(
            ADM_LEGACY_STATUS_NOT_CANONICAL, rejected.reason_codes
        )

    def test_legacy_path_cannot_masquerade_as_canonical_node(self):
        data = deepcopy(self.fixture["canonical_request"])
        legacy_path = "08_Domain_Applications/Math_Mentor/已毕业知识点.md"
        data["asset"]["path"] = legacy_path
        data["asset"]["asset_role"] = "canonical_node"
        data["identity_evidence"]["canonical_path"] = legacy_path
        decision = evaluate_admission(self.request(data), self.allow_for(data))

        self.assertEqual("blocked", decision.status)
        self.assertIn(ADM_NON_CANONICAL_ASSET, decision.reason_codes)

    def test_arbitrary_path_cannot_claim_legacy_state_table_role(self):
        data = deepcopy(self.fixture["legacy_r5_request"])
        data["asset"]["path"] = (
            "08_Domain_Applications/Math_Mentor/not-a-legacy-state-table.md"
        )
        decision = evaluate_admission(self.request(data), self.allow_for(data))

        self.assertEqual("blocked", decision.status)
        self.assertIn(ADM_NON_CANONICAL_ASSET, decision.reason_codes)

    def test_legacy_prompt_never_executes(self):
        data = deepcopy(self.fixture["legacy_r5_request"])
        data["asset"]["path"] = (
            "08_Domain_Applications/Math_Mentor/复习巩固期prompt/"
            "交互式演化引擎生成提示词.md"
        )
        data["asset"]["asset_role"] = "legacy_prompt"
        decision = evaluate_admission(self.request(data), self.allow_for(data))

        self.assertEqual("blocked", decision.status)
        self.assertIn(ADM_LEGACY_EXECUTION_FORBIDDEN, decision.reason_codes)

    def test_teaser_is_limited_and_state_write_is_always_blocked(self):
        teaser = deepcopy(self.fixture["canonical_request"])
        teaser["requested_use"] = "teaser_read_only"
        teaser["prerequisite_evidence"]["status"] = "unresolved"
        teaser_decision = evaluate_admission(self.request(teaser), self.allow)
        self.assertEqual("admitted_teaser_only", teaser_decision.status)

        write = deepcopy(self.fixture["canonical_request"])
        write["state_write_requested"] = True
        write_decision = evaluate_admission(self.request(write), self.allow)
        self.assertEqual("blocked", write_decision.status)
        self.assertIn(ADM_STATE_WRITE_FORBIDDEN, write_decision.reason_codes)


if __name__ == "__main__":
    unittest.main()
