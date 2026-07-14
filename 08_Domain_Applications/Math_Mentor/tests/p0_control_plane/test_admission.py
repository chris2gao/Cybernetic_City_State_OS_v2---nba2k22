from __future__ import annotations

from copy import copy, deepcopy
from datetime import datetime
import json
from pathlib import Path
import sys
import unittest


MATH_MENTOR_ROOT = Path(__file__).resolve().parents[2]
if str(MATH_MENTOR_ROOT) not in sys.path:
    sys.path.insert(0, str(MATH_MENTOR_ROOT))

import p0_control_plane.admission_evidence as admission_evidence_module  # noqa: E402
from p0_control_plane.admission import (  # noqa: E402
    ADM_AUTH_DENIED,
    ADM_AUTH_HUMAN_REQUIRED,
    ADM_AUTH_SCOPE_MISMATCH,
    ADM_BLOB_MISMATCH,
    ADM_BRIDGE_ADMISSION_NOT_IMPLEMENTED,
    ADM_EVIDENCE_STALE,
    ADM_EVIDENCE_BLOB_MISMATCH,
    ADM_EVIDENCE_CROSSWALK_MISMATCH,
    ADM_EVIDENCE_FIXTURE_IN_PRODUCTION,
    ADM_EVIDENCE_PATH_MISMATCH,
    ADM_EVIDENCE_PAYLOAD_HASH_MISMATCH,
    ADM_EVIDENCE_PREREQUISITE_MISMATCH,
    ADM_EVIDENCE_REPO_MISMATCH,
    ADM_EVIDENCE_SCHEMA_VERSION_MISMATCH,
    ADM_EVIDENCE_SOURCE_HEAD_MISMATCH,
    ADM_EVIDENCE_VALIDATOR_BLOB_MISMATCH,
    ADM_IDENTITY_CONFLICT,
    ADM_LEGACY_EXECUTION_FORBIDDEN,
    ADM_LEGACY_STATUS_NOT_CANONICAL,
    ADM_MANUAL_REVIEW_REQUIRED,
    ADM_NON_CANONICAL_ASSET,
    ADM_REQUEST_UNTRUSTED,
    ADM_STAGING_ASSET,
    ADM_STATE_WRITE_FORBIDDEN,
    ADM_TRUSTED_EVIDENCE_MISSING,
    ADM_TRUSTED_EVIDENCE_UNTRUSTED,
    ADM_VALIDATOR_REJECTED,
    AdmissionInputError,
    AdmissionRequest,
    evaluate_admission,
)
from p0_control_plane.admission_evidence import (  # noqa: E402
    EVIDENCE_FIXTURE_IN_PRODUCTION,
    EVIDENCE_PROVIDER_INACTIVE,
    AdmissionEvidenceError,
    DeterministicTestAdmissionEvidenceProvider,
    ProductionAdmissionEvidenceProvider,
    TrustedAdmissionEvidence,
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

    def evidence_record_for(
        self,
        data=None,
        *,
        binding_overrides=None,
        finding_overrides=None,
    ):
        admission_data = deepcopy(
            data if data is not None else self.fixture["canonical_request"]
        )
        request = self.request(admission_data)
        asset = admission_data["asset"]
        identity = admission_data["identity_evidence"]
        schema = admission_data["schema_evidence"]
        readiness = admission_data["readiness_evidence"]
        provenance = admission_data["provenance_evidence"]
        prerequisites = admission_data["prerequisite_evidence"]
        is_legacy = asset["asset_role"] == "legacy_state_table"
        record = {
            "schema_version": "math_mentor.trusted_admission_evidence.v1",
            "evidence_id": f"evidence-{request.request_payload_sha256[:20]}",
            "evidence_class": (
                "legacy_state_table" if is_legacy else "canonical_node"
            ),
            "provider_ref": "deterministic-test-provider:admission",
            "binding": {
                "repo_id": asset["repo_id"],
                "source_head": asset["source_head"],
                "path": asset["path"],
                "blob_oid": asset["blob_oid"],
                "canonical_node_id": (
                    None if is_legacy else identity["canonical_node_id"]
                ),
                "crosswalk_source_head": (
                    None if is_legacy else identity["registry_source_head"]
                ),
                "crosswalk_blob_oid": (
                    None if is_legacy else identity["registry_blob_oid"]
                ),
                "crosswalk_payload_sha256": (
                    None if is_legacy else identity["crosswalk_payload_sha256"]
                ),
                "admission_request_payload_sha256": (
                    request.request_payload_sha256
                ),
                "admission_request_schema_version": request.schema_version,
                "normalized_schema_version": (
                    None if is_legacy else schema["normalized_schema_version"]
                ),
                "validator_ref": (
                    None if is_legacy else readiness["validator_ref"]
                ),
                "validated_blob_oid": (
                    None if is_legacy else readiness["validated_blob_oid"]
                ),
                "prerequisite_status": prerequisites["status"],
                "prerequisite_evidence_ref": prerequisites["evidence_ref"],
                "prerequisite_evidence_sha256": prerequisites[
                    "evidence_sha256"
                ],
            },
            "findings": {
                "asset_role": (
                    "legacy_state_table" if is_legacy else "canonical_node"
                ),
                "schema_era": asset["schema_era"],
                "identity_status": identity["status"],
                "schema_status": schema["status"],
                "readiness_status": readiness["source_status"],
                "validator_status": readiness["validator_status"],
                "provenance_status": provenance["status"],
                "consumer_allowed": False,
                "conflict_status": "not_evaluated",
            },
        }
        record["binding"].update(binding_overrides or {})
        record["findings"].update(finding_overrides or {})
        return record

    def evidence_for(self, data=None, **kwargs):
        record = self.evidence_record_for(data, **kwargs)
        provider = DeterministicTestAdmissionEvidenceProvider(
            {"admission-evidence": record}
        )
        return provider.authenticate("admission-evidence", mode="test")

    def evaluate_with_evidence(self, data=None, *, evidence=None, authorization=None):
        admission_data = deepcopy(
            data if data is not None else self.fixture["canonical_request"]
        )
        return evaluate_admission(
            self.request(admission_data),
            authorization if authorization is not None else self.allow_for(admission_data),
            evidence if evidence is not None else self.evidence_for(admission_data),
            environment_mode="test",
        )

    def test_exact_canonical_asset_is_admitted_read_only(self):
        decision = self.evaluate_with_evidence()

        self.assertEqual("admitted_manual_read_only", decision.status)
        self.assertTrue(decision.restrictions["read_only"])
        self.assertFalse(decision.restrictions["state_write_allowed"])
        self.assertIsNone(decision.canonical_learning_status)

    def test_raw_ready_request_cannot_substitute_for_trusted_evidence(self):
        request = self.request()
        self.assertEqual("ready", request.readiness_status)
        self.assertEqual("accepted", request.validator_status)
        self.assertEqual("exact_blob_verified", request.provenance_status)

        decision = evaluate_admission(
            request, self.allow, environment_mode="test"
        )

        self.assertEqual("blocked", decision.status)
        self.assertIn(ADM_TRUSTED_EVIDENCE_MISSING, decision.reason_codes)

    def test_serialized_copy_duck_and_direct_evidence_cannot_reenter(self):
        request = self.request()
        evidence = self.evidence_for()

        class DuckEvidence:
            pass

        duck = DuckEvidence()
        duck.__dict__.update(evidence.__dict__)
        direct = TrustedAdmissionEvidence(**dict(evidence.__dict__))
        forged_values = (
            evidence.to_dict(),
            copy(evidence),
            deepcopy(evidence),
            duck,
            direct,
        )
        for forged in forged_values:
            with self.subTest(forged_type=type(forged).__name__):
                decision = evaluate_admission(
                    request,
                    self.allow,
                    forged,
                    environment_mode="test",
                )
                self.assertEqual("blocked", decision.status)
                self.assertIn(
                    ADM_TRUSTED_EVIDENCE_UNTRUSTED,
                    decision.reason_codes,
                )

        forged_fields = dict(evidence.__dict__)
        forged_fields["_seal"] = object()
        with self.assertRaises(AdmissionEvidenceError):
            TrustedAdmissionEvidence(**forged_fields)

    def test_copied_or_direct_admission_request_cannot_reenter(self):
        request = self.request()
        evidence = self.evidence_for()
        direct = AdmissionRequest(**dict(request.__dict__))

        for forged in (copy(request), deepcopy(request), direct):
            with self.subTest(forged_type=type(forged).__name__):
                decision = evaluate_admission(
                    forged,
                    self.allow,
                    evidence,
                    environment_mode="test",
                )
                self.assertEqual("blocked", decision.status)
                self.assertIn(ADM_REQUEST_UNTRUSTED, decision.reason_codes)

        forged_fields = dict(request.__dict__)
        forged_fields["_seal"] = object()
        with self.assertRaises(AdmissionInputError):
            AdmissionRequest(**forged_fields)

    def test_provider_boundaries_fail_closed(self):
        with self.assertRaises(AdmissionEvidenceError) as inactive:
            ProductionAdmissionEvidenceProvider().authenticate("opaque")
        self.assertEqual(EVIDENCE_PROVIDER_INACTIVE, inactive.exception.code)

        provider = DeterministicTestAdmissionEvidenceProvider(
            {"admission-evidence": self.evidence_record_for()}
        )
        with self.assertRaises(AdmissionEvidenceError) as production_fixture:
            provider.authenticate("admission-evidence", mode="production")
        self.assertEqual(
            EVIDENCE_FIXTURE_IN_PRODUCTION,
            production_fixture.exception.code,
        )

        test_evidence = provider.authenticate("admission-evidence", mode="test")
        decision = evaluate_admission(
            self.request(), self.allow, test_evidence
        )
        self.assertEqual("blocked", decision.status)
        self.assertIn(
            ADM_EVIDENCE_FIXTURE_IN_PRODUCTION,
            decision.reason_codes,
        )

    def test_issued_request_and_evidence_mutation_invalidates_trust(self):
        request = self.request()
        evidence = self.evidence_for()
        object.__setattr__(request, "requested_use", "lesson_planning_read_only")
        request_decision = evaluate_admission(
            request,
            self.allow,
            evidence,
            environment_mode="test",
        )
        self.assertEqual("blocked", request_decision.status)
        self.assertIn(ADM_REQUEST_UNTRUSTED, request_decision.reason_codes)

        review_evidence = self.evidence_for(
            finding_overrides={"readiness_status": "manual_review_required"}
        )
        object.__setattr__(review_evidence, "readiness_status", "ready")
        evidence_decision = evaluate_admission(
            self.request(),
            self.allow,
            review_evidence,
            environment_mode="test",
        )
        self.assertEqual("blocked", evidence_decision.status)
        self.assertIn(
            ADM_TRUSTED_EVIDENCE_UNTRUSTED,
            evidence_decision.reason_codes,
        )

        fixture_evidence = self.evidence_for()
        object.__setattr__(
            fixture_evidence, "trust_source", "external_platform"
        )
        production_decision = evaluate_admission(
            self.request(), self.allow, fixture_evidence
        )
        self.assertEqual("blocked", production_decision.status)
        self.assertIn(
            ADM_TRUSTED_EVIDENCE_UNTRUSTED,
            production_decision.reason_codes,
        )

    def test_internal_issuer_cannot_create_production_evidence(self):
        directly_issued = admission_evidence_module._issue_evidence(
            self.evidence_record_for()
        )
        self.assertEqual("test_fixture", directly_issued.trust_source)
        decision = evaluate_admission(
            self.request(), self.allow, directly_issued
        )
        self.assertEqual("blocked", decision.status)
        self.assertIn(
            ADM_EVIDENCE_FIXTURE_IN_PRODUCTION,
            decision.reason_codes,
        )

        with self.assertRaises(TypeError):
            admission_evidence_module._issue_evidence(
                self.evidence_record_for(),
                trust_source="external_platform",
            )

    def test_admission_decision_mappings_are_immutable_snapshots(self):
        decision = self.evaluate_with_evidence()
        with self.assertRaises(TypeError):
            decision.restrictions["consumer_allowed"] = True
        with self.assertRaises(TypeError):
            decision.dimensions["readiness"] = "ready"

        snapshot = decision.to_dict()
        snapshot["restrictions"]["consumer_allowed"] = True
        snapshot["dimensions"]["readiness"] = "forged"
        self.assertFalse(decision.restrictions["consumer_allowed"])
        self.assertEqual("ready", decision.dimensions["readiness"])

    def test_evidence_binding_mismatches_fail_closed(self):
        mismatch_cases = (
            (
                "repo",
                {"repo_id": "different-repo"},
                ADM_EVIDENCE_REPO_MISMATCH,
            ),
            (
                "source_head",
                {"source_head": "d" * 40},
                ADM_EVIDENCE_SOURCE_HEAD_MISMATCH,
            ),
            (
                "path",
                {
                    "path": (
                        "08_Domain_Applications/Math_Mentor/"
                        "Pure_Math_Intuition_DB/OTHER.yaml"
                    )
                },
                ADM_EVIDENCE_PATH_MISMATCH,
            ),
            (
                "blob",
                {"blob_oid": "d" * 40},
                ADM_EVIDENCE_BLOB_MISMATCH,
            ),
            (
                "request_payload",
                {"admission_request_payload_sha256": "d" * 64},
                ADM_EVIDENCE_PAYLOAD_HASH_MISMATCH,
            ),
            (
                "crosswalk_payload",
                {"crosswalk_payload_sha256": "d" * 64},
                ADM_EVIDENCE_CROSSWALK_MISMATCH,
            ),
            (
                "canonical_node_id",
                {
                    "canonical_node_id": (
                        "00000000-0000-5000-8000-000000000000"
                    )
                },
                ADM_EVIDENCE_CROSSWALK_MISMATCH,
            ),
            (
                "crosswalk_source_head",
                {"crosswalk_source_head": "d" * 40},
                ADM_EVIDENCE_CROSSWALK_MISMATCH,
            ),
            (
                "crosswalk_blob",
                {"crosswalk_blob_oid": "d" * 40},
                ADM_EVIDENCE_CROSSWALK_MISMATCH,
            ),
            (
                "normalized_schema_version",
                {"normalized_schema_version": "math_mentor.normalized_node.v2"},
                ADM_EVIDENCE_SCHEMA_VERSION_MISMATCH,
            ),
            (
                "validator_blob",
                {"validated_blob_oid": "d" * 40},
                ADM_EVIDENCE_VALIDATOR_BLOB_MISMATCH,
            ),
            (
                "prerequisite",
                {"prerequisite_evidence_sha256": "d" * 64},
                ADM_EVIDENCE_PREREQUISITE_MISMATCH,
            ),
        )
        for name, overrides, expected_code in mismatch_cases:
            with self.subTest(binding=name):
                evidence = self.evidence_for(binding_overrides=overrides)
                decision = evaluate_admission(
                    self.request(),
                    self.allow,
                    evidence,
                    environment_mode="test",
                )
                self.assertEqual("blocked", decision.status)
                self.assertIn(expected_code, decision.reason_codes)

    def test_authorized_raw_ready_claim_cannot_override_sealed_findings(self):
        finding_cases = (
            (
                {"readiness_status": "manual_review_required"},
                ADM_MANUAL_REVIEW_REQUIRED,
            ),
            ({"validator_status": "rejected"}, ADM_VALIDATOR_REJECTED),
        )
        for findings, expected_code in finding_cases:
            with self.subTest(findings=findings):
                evidence = self.evidence_for(finding_overrides=findings)
                decision = evaluate_admission(
                    self.request(),
                    self.allow,
                    evidence,
                    environment_mode="test",
                )
                self.assertFalse(decision.status.startswith("admitted_"))
                self.assertIn(expected_code, decision.reason_codes)

    def test_provider_cannot_activate_consumers_or_adjudicate_conflicts(self):
        invalid_findings = (
            {"consumer_allowed": True},
            {"conflict_status": "resolved"},
        )
        for findings in invalid_findings:
            with self.subTest(findings=findings):
                with self.assertRaises(AdmissionEvidenceError):
                    self.evidence_for(finding_overrides=findings)

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

    def test_raw_identity_conflict_is_not_adjudicated_without_trusted_evidence(self):
        conflict = deepcopy(self.fixture["canonical_request"])
        conflict["identity_evidence"] = {
            "status": "conflict",
            "canonical_node_id": None,
            "registry_ref": None,
        }
        conflict_decision = evaluate_admission(self.request(conflict), self.allow)
        self.assertEqual("blocked", conflict_decision.status)
        self.assertIn(
            ADM_TRUSTED_EVIDENCE_MISSING, conflict_decision.reason_codes
        )

    def test_crosswalk_mismatch_is_quarantined_only_with_sealed_evidence(self):
        mismatch = deepcopy(self.fixture["canonical_request"])
        mismatch["identity_evidence"]["canonical_blob_oid"] = (
            "dddddddddddddddddddddddddddddddddddddddd"
        )
        mismatch_decision = self.evaluate_with_evidence(mismatch)
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
        decision = self.evaluate_with_evidence(data)

        self.assertEqual("review_required", decision.status)
        self.assertIn(ADM_MANUAL_REVIEW_REQUIRED, decision.reason_codes)

    def test_stale_and_wrong_blob_evidence_fail_closed(self):
        stale = deepcopy(self.fixture["canonical_request"])
        stale["provenance_evidence"]["status"] = "stale"
        stale_decision = self.evaluate_with_evidence(stale)
        self.assertEqual("blocked", stale_decision.status)
        self.assertIn(ADM_EVIDENCE_STALE, stale_decision.reason_codes)

        wrong_blob = deepcopy(self.fixture["canonical_request"])
        wrong_blob["readiness_evidence"]["validated_blob_oid"] = (
            "dddddddddddddddddddddddddddddddddddddddd"
        )
        blob_decision = self.evaluate_with_evidence(wrong_blob)
        self.assertEqual("blocked", blob_decision.status)
        self.assertIn(
            ADM_EVIDENCE_VALIDATOR_BLOB_MISMATCH,
            blob_decision.reason_codes,
        )

    def test_legacy_r5_passed_is_only_a_historical_import_claim(self):
        decision = self.evaluate_with_evidence(self.fixture["legacy_r5_request"])

        self.assertEqual("admitted_legacy_import_read_only", decision.status)
        self.assertIsNone(decision.canonical_learning_status)
        self.assertFalse(decision.restrictions["state_write_allowed"])

        promoted = deepcopy(self.fixture["legacy_r5_request"])
        promoted["legacy_claim"]["requested_canonical_status"] = "graduated"
        rejected = self.evaluate_with_evidence(promoted)
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
        teaser_decision = self.evaluate_with_evidence(teaser)
        self.assertEqual("admitted_teaser_only", teaser_decision.status)

        write = deepcopy(self.fixture["canonical_request"])
        write["state_write_requested"] = True
        write_decision = evaluate_admission(self.request(write), self.allow)
        self.assertEqual("blocked", write_decision.status)
        self.assertIn(ADM_STATE_WRITE_FORBIDDEN, write_decision.reason_codes)


if __name__ == "__main__":
    unittest.main()
