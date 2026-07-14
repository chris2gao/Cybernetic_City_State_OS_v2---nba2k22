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

from p0_control_plane.authorization import (  # noqa: E402
    AUTH_CONTEXT_MISSING,
    AUTH_EFFECT_CEILING_EXCEEDED,
    AUTH_EXPIRED,
    AUTH_FIXTURE_IN_PRODUCTION,
    AUTH_NONCE_REPLAY,
    AUTH_OPERATION_NOT_GRANTED,
    AUTH_PAYLOAD_GATE_IGNORED,
    AUTH_POST_COMPLETION_GATE_REQUIRED,
    AUTH_RESOURCE_NOT_GRANTED,
    AUTH_SECRET_SCOPE_FORBIDDEN,
    AUTH_SOURCE_HEAD_MISMATCH,
    AuthorizationInputError,
    AuthorizationRequest,
    DeterministicTestTrustBoundaryAdapter,
    ProductionTrustBoundaryAdapter,
    ReadonlyReplaySnapshot,
    TrustBoundaryError,
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

        expired_record = deepcopy(self.fixture["grant"])
        expired_record["validity"]["expires_at"] = "2026-07-14T11:00:00Z"
        expired = verify_authorization(
            self.request(), self.production_grant(expired_record), now=self.now
        )
        self.assertEqual("deny", expired.status)
        self.assertIn(AUTH_EXPIRED, expired.reason_codes)

    def test_secret_path_is_denied_even_if_payload_claims_approval(self):
        request_data = deepcopy(self.fixture["request"])
        request_data["operation"] = "repository.read"
        request_data["effect_class"] = "read_only"
        request_data["resources"][0]["path"] = ".env"
        decision = verify_authorization(
            self.request(request_data), self.production_grant(), now=self.now
        )

        self.assertEqual("deny", decision.status)
        self.assertIn(AUTH_SECRET_SCOPE_FORBIDDEN, decision.reason_codes)

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


if __name__ == "__main__":
    unittest.main()
