from __future__ import annotations

from copy import copy, deepcopy
from datetime import datetime
import json
from pathlib import Path
import sys
import unittest

from jsonschema import Draft202012Validator


MATH_MENTOR_ROOT = Path(__file__).resolve().parents[2]
if str(MATH_MENTOR_ROOT) not in sys.path:
    sys.path.insert(0, str(MATH_MENTOR_ROOT))

from p0_control_plane.authorization import (  # noqa: E402
    AUTH_CONTEXT_MISSING,
    AUTH_EFFECT_CEILING_EXCEEDED,
    AUTH_ENVELOPE_UNTRUSTED,
    AUTH_EXPIRED,
    AUTH_FIXTURE_IN_PRODUCTION,
    AUTH_NONCE_REPLAY,
    AUTH_OPERATION_NOT_GRANTED,
    AUTH_PAYLOAD_GATE_IGNORED,
    AUTH_POST_COMPLETION_GATE_REQUIRED,
    AUTH_REQUEST_SCHEMA_INVALID,
    AUTH_RESOURCE_NOT_GRANTED,
    AUTH_SECRET_SCOPE_FORBIDDEN,
    AUTH_SOURCE_HEAD_MISMATCH,
    AuthorizationInputError,
    AuthorizationRequest,
    DeterministicTestTrustBoundaryAdapter,
    ProductionTrustBoundaryAdapter,
    ReadonlyAuthorizationPolicy,
    ReadonlyReplaySnapshot,
    TrustBoundaryError,
    is_verified_authorization_decision,
    verify_authorization,
)


FIXTURE_PATH = (
    Path(__file__).parent / "fixtures" / "authorization" / "base_cases.json"
)


class AuthorizationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
        cls.now = datetime.fromisoformat(
            cls.fixture["now"].replace("Z", "+00:00")
        )

    def request(self, data=None) -> AuthorizationRequest:
        return AuthorizationRequest.from_mapping(
            deepcopy(data if data is not None else self.fixture["request"])
        )

    def production_grant(self, record=None):
        grant_record = deepcopy(
            record if record is not None else self.fixture["grant"]
        )
        adapter = ProductionTrustBoundaryAdapter(
            lambda handle: grant_record if handle == "opaque-human-envelope" else None
        )
        return adapter.authenticate("opaque-human-envelope", mode="production")

    def test_external_grant_allows_exact_effect_but_payload_gate_is_only_audit(self):
        decision = verify_authorization(
            self.request(), self.production_grant(), now=self.now
        )

        self.assertEqual("allow", decision.status)
        self.assertIn(AUTH_PAYLOAD_GATE_IGNORED, decision.reason_codes)
        self.assertFalse(
            decision.audit["payload_human_gate_used_for_authorization"]
        )
        self.assertEqual(
            "approved", decision.audit["payload_human_gate_observed"]
        )
        self.assertTrue(
            decision.authorization_context["authority"]["authenticated"]
        )
        self.assertFalse(
            decision.authorization_context["verification"]
            ["payload_human_gate_used_for_authorization"]
        )
        self.assertNotIn(
            "runtime.activate",
            decision.authorization_context["grant"]["allowed_operations"],
        )
        validity = decision.authorization_context["validity"]
        self.assertEqual("snapshot_not_supplied", validity["replay_status"])
        self.assertEqual(
            "host_supplied_readonly_snapshot_only",
            validity["replay_snapshot_scope"],
        )
        self.assertFalse(validity["atomic_nonce_consumption_implemented"])
        self.assertFalse(validity["nonce_persistence_implemented"])
        self.assertFalse(validity["cross_process_replay_protection_implemented"])

    def test_payload_approved_does_not_authorize_without_external_context(self):
        decision = verify_authorization(self.request(), None, now=self.now)

        self.assertEqual("human_required", decision.status)
        self.assertIn(AUTH_CONTEXT_MISSING, decision.reason_codes)
        self.assertIn(AUTH_PAYLOAD_GATE_IGNORED, decision.reason_codes)
        self.assertIsNone(decision.authorization_context)

    def test_deterministic_adapter_is_test_only_at_both_boundaries(self):
        adapter = DeterministicTestTrustBoundaryAdapter(
            {"fixture": deepcopy(self.fixture["grant"])}
        )
        with self.assertRaises(TrustBoundaryError) as caught:
            adapter.authenticate("fixture", mode="production")
        self.assertEqual(AUTH_FIXTURE_IN_PRODUCTION, caught.exception.code)

        test_grant = adapter.authenticate("fixture", mode="test")
        production_decision = verify_authorization(
            self.request(),
            test_grant,
            now=self.now,
            environment_mode="production",
        )
        self.assertEqual("deny", production_decision.status)
        self.assertIn(
            AUTH_FIXTURE_IN_PRODUCTION, production_decision.reason_codes
        )

        test_decision = verify_authorization(
            self.request(), test_grant, now=self.now, environment_mode="test"
        )
        self.assertEqual("allow", test_decision.status)

    def test_copied_or_object_mutated_grant_is_untrusted(self):
        original = self.production_grant()
        mutated = self.production_grant()
        object.__setattr__(mutated, "resource_selectors", ())
        object.__setattr__(mutated, "is_factory_issued", lambda: True)
        for candidate in (copy(original), deepcopy(original), mutated):
            with self.subTest(candidate_type=type(candidate).__name__):
                decision = verify_authorization(
                    self.request(),
                    candidate,
                    now=self.now,
                )
                self.assertEqual("deny", decision.status)
                self.assertIn(AUTH_ENVELOPE_UNTRUSTED, decision.reason_codes)

    def test_object_mutated_or_copied_decision_loses_verified_identity(self):
        request_data = deepcopy(self.fixture["request"])
        request_data["operation"] = "secret.read"
        request_data["effect_class"] = "secret_or_privacy"
        request_data["resources"][0]["path"] = "public/example.txt"
        denied = verify_authorization(
            self.request(request_data),
            None,
            now=self.now,
        )
        self.assertTrue(is_verified_authorization_decision(denied))
        object.__setattr__(denied, "status", "allow")
        object.__setattr__(denied, "is_factory_issued", lambda: True)
        self.assertFalse(is_verified_authorization_decision(denied))

        allowed = verify_authorization(
            self.request(),
            self.production_grant(),
            now=self.now,
        )
        self.assertTrue(is_verified_authorization_decision(allowed))
        self.assertFalse(is_verified_authorization_decision(copy(allowed)))
        self.assertFalse(is_verified_authorization_decision(allowed.to_dict()))

    def test_source_head_is_bound(self):
        request_data = deepcopy(self.fixture["request"])
        request_data["source_head"] = "dddddddddddddddddddddddddddddddddddddddd"
        decision = verify_authorization(
            self.request(request_data), self.production_grant(), now=self.now
        )

        self.assertEqual("deny", decision.status)
        self.assertIn(AUTH_SOURCE_HEAD_MISMATCH, decision.reason_codes)

    def test_prefix_selector_does_not_match_similar_sibling_path(self):
        request_data = deepcopy(self.fixture["request"])
        request_data["resources"][0]["path"] = (
            "08_Domain_Applications/Math_Mentor/p0_control_plane_evil/file.py"
        )
        decision = verify_authorization(
            self.request(request_data), self.production_grant(), now=self.now
        )

        self.assertEqual("human_required", decision.status)
        self.assertIn(AUTH_RESOURCE_NOT_GRANTED, decision.reason_codes)

    def test_effect_ceiling_and_operation_are_both_enforced(self):
        low_ceiling = deepcopy(self.fixture["grant"])
        low_ceiling["grant"]["effect_ceiling"] = "read_only"
        ceiling_decision = verify_authorization(
            self.request(), self.production_grant(low_ceiling), now=self.now
        )
        self.assertEqual("human_required", ceiling_decision.status)
        self.assertIn(
            AUTH_EFFECT_CEILING_EXCEEDED, ceiling_decision.reason_codes
        )

        runtime_request = deepcopy(self.fixture["request"])
        runtime_request["operation"] = "runtime.activate"
        runtime_request["effect_class"] = "runtime_activation"
        operation_decision = verify_authorization(
            self.request(runtime_request), self.production_grant(), now=self.now
        )
        self.assertEqual("human_required", operation_decision.status)
        self.assertIn(
            AUTH_OPERATION_NOT_GRANTED, operation_decision.reason_codes
        )

    def test_operation_cannot_understate_its_effect(self):
        malformed = deepcopy(self.fixture["request"])
        malformed["operation"] = "runtime.activate"
        malformed["effect_class"] = "read_only"
        with self.assertRaises(AuthorizationInputError):
            self.request(malformed)

    def test_direct_copied_mutated_and_duck_requests_fail_closed(self):
        request_data = self.fixture["request"]
        direct = AuthorizationRequest(
            schema_version=request_data["schema_version"],
            request_id=request_data["request_id"],
            task_id=request_data["task_id"],
            objective_sha256=request_data["objective_sha256"],
            source_head=request_data["source_head"],
            operation=request_data["operation"],
            effect_class=request_data["effect_class"],
            resources=(),
        )
        issued = self.request()
        mutated = self.request()
        object.__setattr__(mutated, "resources", ())
        object.__setattr__(mutated, "is_factory_issued", lambda: True)

        class ExplosiveDuck:
            def __getattribute__(self, name):
                raise AssertionError(f"duck attribute was inspected: {name}")

        candidates = (
            direct,
            copy(issued),
            deepcopy(issued),
            mutated,
            ExplosiveDuck(),
        )
        for candidate in candidates:
            with self.subTest(candidate_type=type(candidate).__name__):
                decision = verify_authorization(
                    candidate,
                    self.production_grant(),
                    now=self.now,
                )
                self.assertEqual("deny", decision.status)
                self.assertEqual(
                    (AUTH_REQUEST_SCHEMA_INVALID,),
                    decision.reason_codes,
                )
                self.assertIsNone(decision.authorization_context)
                self.assertEqual((), decision.requested_effect["resources"])
                self.assertTrue(is_verified_authorization_decision(decision))

    def test_post_completion_gate_needs_new_external_approval(self):
        request_data = deepcopy(self.fixture["request"])
        request_data["gate_phase"] = "post_completion"
        decision = verify_authorization(
            self.request(request_data), self.production_grant(), now=self.now
        )

        self.assertEqual("human_required", decision.status)
        self.assertIn(
            AUTH_POST_COMPLETION_GATE_REQUIRED, decision.reason_codes
        )

    def test_nonce_replay_and_expiry_fail_closed(self):
        grant = self.production_grant()
        replay = verify_authorization(
            self.request(),
            grant,
            now=self.now,
            replay_snapshot=ReadonlyReplaySnapshot(
                consumed_nonces=frozenset({grant.nonce})
            ),
        )
        self.assertEqual("deny", replay.status)
        self.assertIn(AUTH_NONCE_REPLAY, replay.reason_codes)

        snapshot_allow = verify_authorization(
            self.request(),
            grant,
            now=self.now,
            replay_snapshot=ReadonlyReplaySnapshot(),
        )
        self.assertEqual("allow", snapshot_allow.status)
        self.assertEqual(
            "not_present_in_supplied_snapshot",
            snapshot_allow.authorization_context["validity"]["replay_status"],
        )
        self.assertFalse(
            snapshot_allow.authorization_context["validity"]
            ["atomic_nonce_consumption_implemented"]
        )

        expired_record = deepcopy(self.fixture["grant"])
        expired_record["validity"]["expires_at"] = "2026-07-14T11:00:00Z"
        expired = verify_authorization(
            self.request(), self.production_grant(expired_record), now=self.now
        )
        self.assertEqual("deny", expired.status)
        self.assertIn(AUTH_EXPIRED, expired.reason_codes)

    def test_replay_snapshot_is_readonly_and_verifier_does_not_claim_consumption(self):
        with self.assertRaises(AuthorizationInputError):
            ReadonlyReplaySnapshot(consumed_nonces=set())

        snapshot = ReadonlyReplaySnapshot()
        first = verify_authorization(
            self.request(),
            self.production_grant(),
            now=self.now,
            replay_snapshot=snapshot,
        )
        second = verify_authorization(
            self.request(),
            self.production_grant(),
            now=self.now,
            replay_snapshot=snapshot,
        )
        self.assertEqual("allow", first.status)
        self.assertEqual("allow", second.status)
        self.assertEqual(frozenset(), snapshot.consumed_nonces)
        for decision in (first, second):
            validity = decision.authorization_context["validity"]
            self.assertFalse(validity["atomic_nonce_consumption_implemented"])
            self.assertFalse(validity["nonce_persistence_implemented"])
            self.assertFalse(validity["cross_process_replay_protection_implemented"])

    def test_secret_paths_are_denied_case_insensitively_without_reading_them(self):
        protected_paths = (
            ".env",
            ".env.local",
            ".env.production",
            ".ENV.Production",
            ".ssh/id_ed25519",
            "users/example/.SSH/id_rsa",
            "keys/id_rsa",
            "keys/id_ed25519",
            "keys/private-key.pem",
            "keys/PRIVATE.KEY",
            "credentials.json",
            "config/APPLICATION_DEFAULT_CREDENTIALS.JSON",
            "secrets/service.json",
            "config/credentials/service.json",
            "private_keys/signing-material",
        )
        for protected_path in protected_paths:
            with self.subTest(path=protected_path):
                request_data = deepcopy(self.fixture["request"])
                request_data["operation"] = "repository.read"
                request_data["effect_class"] = "read_only"
                request_data["resources"][0]["path"] = protected_path
                decision = verify_authorization(
                    self.request(request_data), self.production_grant(), now=self.now
                )

                self.assertEqual("deny", decision.status)
                self.assertIn(
                    AUTH_SECRET_SCOPE_FORBIDDEN,
                    decision.reason_codes,
                )

    def test_secret_read_operation_is_unconditionally_denied(self):
        request_data = deepcopy(self.fixture["request"])
        request_data["operation"] = "secret.read"
        request_data["effect_class"] = "secret_or_privacy"
        request_data["resources"][0]["path"] = "public/example.txt"
        decision = verify_authorization(
            self.request(request_data), None, now=self.now
        )

        self.assertEqual("deny", decision.status)
        self.assertIn(AUTH_SECRET_SCOPE_FORBIDDEN, decision.reason_codes)

    def test_windows_ads_colon_and_trailing_dot_space_paths_are_rejected(self):
        malformed_paths = (
            "08_Domain_Applications/Math_Mentor/p0_control_plane/.env::$DATA",
            "08_Domain_Applications/Math_Mentor/p0_control_plane/.env ",
            "08_Domain_Applications/Math_Mentor/p0_control_plane/credentials.json.",
            "08_Domain_Applications/Math_Mentor/p0_control_plane/private-key.pem ",
            "08_Domain_Applications/Math_Mentor/p0_control_plane/safe./file.txt",
            "08_Domain_Applications/Math_Mentor/p0_control_plane/safe /file.txt",
        )
        for malformed_path in malformed_paths:
            with self.subTest(path=malformed_path):
                request_data = deepcopy(self.fixture["request"])
                request_data["operation"] = "repository.read"
                request_data["effect_class"] = "read_only"
                request_data["resources"][0]["path"] = malformed_path
                with self.assertRaises(AuthorizationInputError):
                    self.request(request_data)

    def test_secret_policy_subclass_cannot_override_protected_path_classifier(self):
        class BypassPolicy(ReadonlyAuthorizationPolicy):
            def resource_is_secret(self, resource):
                return False

        request_data = deepcopy(self.fixture["request"])
        request_data["operation"] = "repository.read"
        request_data["effect_class"] = "read_only"
        request_data["resources"][0]["path"] = ".env.local"
        with self.assertRaisesRegex(
            AuthorizationInputError,
            "policy must be a ReadonlyAuthorizationPolicy",
        ):
            verify_authorization(
                self.request(request_data),
                self.production_grant(),
                now=self.now,
                policy=BypassPolicy(),
            )

    def test_authorization_context_schema_is_json_and_marks_payload_untrusted(self):
        schema_path = MATH_MENTOR_ROOT / "AUTHORIZATION_CONTEXT_SCHEMA.json"
        schema = json.loads(schema_path.read_text(encoding="utf-8"))

        self.assertEqual(
            "math_mentor.authorization_context.v1",
            schema["properties"]["schema_version"]["const"],
        )
        verification = schema["$defs"]["verification"]["properties"]
        self.assertFalse(
            verification["payload_human_gate_used_for_authorization"]["const"]
        )
        self.assertIn("Verifier output only", schema["description"])
        validity = schema["$defs"]["validity"]["properties"]
        self.assertEqual(
            {"not_present_in_supplied_snapshot", "snapshot_not_supplied"},
            set(validity["replay_status"]["enum"]),
        )
        self.assertFalse(validity["atomic_nonce_consumption_implemented"]["const"])
        self.assertFalse(validity["nonce_persistence_implemented"]["const"])
        self.assertFalse(
            validity["cross_process_replay_protection_implemented"]["const"]
        )
        decision = verify_authorization(
            self.request(),
            self.production_grant(),
            now=self.now,
            replay_snapshot=ReadonlyReplaySnapshot(),
        )
        errors = sorted(
            Draft202012Validator(schema).iter_errors(
                decision.to_dict()["authorization_context"]
            ),
            key=lambda error: list(error.path),
        )
        self.assertEqual([], [error.message for error in errors])

        resource_validator = Draft202012Validator(
            schema["$defs"]["resource_ref"]
        )
        for malformed_path in (
            "safe/.env::$DATA",
            "safe/credentials.json.",
            "safe/private-key.pem ",
            "safe./file.txt",
            "safe /file.txt",
        ):
            with self.subTest(schema_path=malformed_path):
                errors = list(
                    resource_validator.iter_errors(
                        {
                            "repo_id": "repo",
                            "path": malformed_path,
                            "match": "exact",
                        }
                    )
                )
                self.assertTrue(errors)


if __name__ == "__main__":
    unittest.main()
