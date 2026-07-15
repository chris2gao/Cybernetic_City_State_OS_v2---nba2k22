from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

from referencing import Registry, Resource


REPO_ROOT = Path(__file__).resolve().parents[3]
GATE_DIR = REPO_ROOT / ".ai" / "communication_compliance"
VALIDATOR_PATH = GATE_DIR / "validate_communication.py"
BASE_HEAD = "d235e602c14250d16b91f2897cb8308e031cc13c"

spec = importlib.util.spec_from_file_location("communication_gate", VALIDATOR_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError("cannot load communication validator")
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


class CommunicationComplianceGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.policy, cls.policy_sha = gate.load_policy(GATE_DIR / "material_event_policy.yml")
        cls.suite = gate.load_document(GATE_DIR / "fixtures" / "fixture_suite.json")

    def test_policy_classification_is_disjoint_and_fail_closed(self) -> None:
        seen: dict[str, str] = {}
        for event_class, config in self.policy["event_classes"].items():
            for event_type in config["event_types"]:
                self.assertNotIn(event_type, seen)
                seen[event_type] = event_class
                self.assertEqual(gate.classify_event(event_type, self.policy), (event_class, []))
        event_class, findings = gate.classify_event("future_unknown_transition", self.policy)
        self.assertEqual(event_class, "unknown")
        self.assertEqual([item["code"] for item in findings], ["UNKNOWN_EVENT_TYPE"])

    def test_frozen_pointer_keys_and_provider_roles(self) -> None:
        self.assertEqual(
            self.policy["wire_schemas"]["chatgpt_to_codex_v1"]["core_keys"],
            ["signal_id", "decision", "task_ref", "packet_ref", "brief_ref", "source_head", "human_gate"],
        )
        self.assertEqual(
            self.policy["wire_schemas"]["codex_to_chatgpt_v1"]["core_keys"],
            ["packet_id", "status", "report_ref", "brief_ref", "source_head", "review_branch_head", "human_gate"],
        )
        self.assertEqual(
            self.policy["wire_schemas"]["codex_to_chatgpt_v1"]["optional_tail_keys"],
            ["detail_ref"],
        )
        self.assertEqual(self.policy["role_mapping"]["Human"]["occupied_role"], "human_speaker")
        for provider in ("ChatGPT", "Claude"):
            self.assertEqual(
                self.policy["role_mapping"][provider]["occupied_role"],
                "foreground_review_and_task_dispatch",
            )
        for provider in ("Codex", "Claude Code"):
            self.assertEqual(
                self.policy["role_mapping"][provider]["occupied_role"],
                "backend_execution_and_handoff",
            )

    def test_expression_sentence_count_supports_chinese_boundaries(self) -> None:
        self.assertEqual(gate.sentence_count("这条门禁把遗漏变成可见证据。它不会授予受保护权限。"), 2)
        self.assertEqual(gate.sentence_count("Evidence is visible. Authority stays external."), 2)

    def test_all_json_schemas_are_valid(self) -> None:
        schema_paths = sorted(GATE_DIR.glob("*.schema.json"))
        self.assertGreaterEqual(len(schema_paths), 7)
        for schema_path in schema_paths:
            schema = gate.load_document(schema_path)
            gate.Draft202012Validator.check_schema(schema)

    def test_ledger_schema_and_privacy_invariants(self) -> None:
        ledger = gate.load_document(REPO_ROOT / ".ai" / "COMMUNICATION_DRIFT_LEDGER.yml")
        schema = gate.load_document(GATE_DIR / "communication_drift_ledger.schema.json")
        registry = Registry().with_resource(
            "drift_record.schema.json",
            Resource.from_contents(gate.load_schema("drift_record.schema.json")),
        )
        gate.Draft202012Validator(schema, registry=registry).validate(ledger)
        self.assertFalse(ledger["privacy"]["contains_private_reasoning"])
        self.assertFalse(ledger["privacy"]["contains_secret_content"])
        for record in ledger["records"]:
            self.assertEqual(gate.schema_findings(record, "drift_record.schema.json", "DRIFT_RECORD"), [])

    def test_strict_parser_rejects_duplicate_multidoc_and_alias_yaml(self) -> None:
        raw_dir = GATE_DIR / "fixtures" / "raw"
        for name in ("pointer_duplicate_keys.yml", "pointer_multidoc.yml", "pointer_anchor_alias.yml"):
            with self.subTest(name=name), self.assertRaises(gate.InputDocumentError):
                gate.load_document(raw_dir / name)
        with self.assertRaises(gate.InputDocumentError):
            gate.load_text_document('{"x":1,"x":2}', ".json")

    def test_schema_invalid_types_fail_closed_without_invalid_result(self) -> None:
        malformed_event = {
            "schema_version": "wrong",
            "event_id": [],
            "task_id": {},
            "event_type": [],
            "provider": "unmapped",
            "occupied_role": 3,
            "proposed_transition": [],
        }
        event_result = gate.validate_event(
            malformed_event,
            REPO_ROOT,
            self.policy,
            self.policy_sha,
        )
        self.assertEqual(event_result["result"], "fail")
        gate.ensure_result_schema(event_result)

        malformed_request = {
            "transition_id": {},
            "event_id": [],
            "task_id": [],
            "event_type": [],
            "event_class": [],
        }
        malformed_validation = {
            "result": "pass",
            "violations": "not-a-list",
            "resolved_refs": "not-a-list",
        }
        transition_result = gate.check_transition(
            malformed_request,
            malformed_validation,
            REPO_ROOT,
            self.policy,
            self.policy_sha,
        )
        self.assertEqual(transition_result["result"], "fail")
        gate.ensure_result_schema(transition_result)

    def test_fixture_suite_matches_all_expected_results(self) -> None:
        result, exit_code = gate.run_fixture_suite(
            self.suite,
            REPO_ROOT,
            self.policy,
            self.policy_sha,
        )
        self.assertEqual(exit_code, gate.EXIT_PASS)
        self.assertEqual(result["result"], "pass")
        self.assertEqual(result["total_cases"], 79)
        self.assertEqual(result["matched_cases"], 79)
        self.assertEqual(result["mismatch_count"], 0)
        self.assertTrue(all(case["matched"] for case in result["cases"]))

    def test_fixture_inventory_covers_required_boundaries(self) -> None:
        ids = [case["id"] for case in self.suite["cases"]]
        self.assertEqual(len(ids), len(set(ids)))
        required = {
            "bootstrap_chatgpt_pass",
            "bootstrap_claude_pass",
            "bootstrap_codex_pass",
            "bootstrap_claude_code_pass",
            "c0_project_mention_pass",
            "classify_unknown_fail_closed",
            "pointer_extra_authorization_key",
            "pointer_key_order_invalid",
            "pointer_nested_human_gate_rejected",
            "pointer_mutable_review_head_rejected",
            "dispatch_recommendation_ref_must_be_explicit",
            "expression_cannot_authorize",
            "expression_structured_authorization_rejected",
            "human_content_structured_authorization_rejected",
            "hidden_reasoning_request_rejected",
            "mixed_nonseparable_complete_brief_pass",
            "pointer_only_waiver_missing_brief",
            "transition_validation_absent",
            "transition_c2_payload_gate_not_authority",
            "transition_c2_test_authority_pass",
            "transition_forged_trusted_context_without_host_verifier",
            "transition_test_harness_trusted_host_pass",
            "transition_validation_policy_binding_mismatch",
            "transition_validation_pass_with_violations",
            "drift_recurring_fixture_missing",
            "drift_recurring_fixture_pass",
        }
        self.assertTrue(required.issubset(ids))

    def test_cli_output_is_environment_independent(self) -> None:
        command = [
            sys.executable,
            str(VALIDATOR_PATH),
            "classify",
            "--repo-root",
            str(REPO_ROOT),
            "--event-type",
            "backend_dispatch",
        ]
        outputs = []
        for timezone, hash_seed in (("UTC", "1"), ("Pacific/Kiritimati", "98765")):
            env = os.environ.copy()
            env["TZ"] = timezone
            env["PYTHONHASHSEED"] = hash_seed
            run = subprocess.run(command, cwd=REPO_ROOT, env=env, capture_output=True, check=False)
            self.assertEqual(run.returncode, 0, run.stderr.decode("utf-8", errors="replace"))
            outputs.append(run.stdout)
        self.assertEqual(outputs[0], outputs[1])
        parsed = json.loads(outputs[0])
        self.assertEqual(parsed["event_class"], "C1")

    def test_cli_invocation_error_is_json_without_traceback(self) -> None:
        run = subprocess.run(
            [sys.executable, str(VALIDATOR_PATH), "classify"],
            cwd=REPO_ROOT,
            capture_output=True,
            check=False,
        )
        self.assertEqual(run.returncode, gate.EXIT_INVOCATION)
        payload = json.loads(run.stdout)
        self.assertEqual(payload["result"], "error")
        self.assertNotIn("Traceback", run.stdout.decode("utf-8"))
        self.assertNotIn(str(REPO_ROOT), run.stdout.decode("utf-8"))

    def test_canonical_documents_bind_the_gate_and_keep_pointer_core_frozen(self) -> None:
        gate_path = ".ai/communication_compliance/validate_communication.py"
        for path in (
            ".ai/PROTOCOL.md",
            ".ai/PROTOCOL_ADHERENCE.md",
            ".ai/HANDOFF_INIT_PROMPT.md",
            ".ai/CODEX_WORK_MECHANISM_PROTOCOL.md",
        ):
            with self.subTest(path=path):
                self.assertIn(gate_path, (REPO_ROOT / path).read_text(encoding="utf-8"))
        task_contract = (REPO_ROOT / ".ai" / "CODEX_TASK_INPUT_CONTRACT.md").read_text(
            encoding="utf-8"
        )
        self.assertIn("separately labeled routing envelope", task_contract)
        self.assertIn("must not be added to the seven-key pointer mapping", task_contract)

    def test_source_mailboxes_are_byte_identical_to_base(self) -> None:
        for path in (".ai/INBOX.md", ".ai/OUTBOX.md", ".ai/STATE.yml", ".ai/HUMAN_BRIEF.md"):
            with self.subTest(path=path):
                baseline_blob = subprocess.run(
                    ["git", "-C", str(REPO_ROOT), "rev-parse", f"{BASE_HEAD}:{path}"],
                    capture_output=True,
                    check=True,
                    text=True,
                ).stdout.strip()
                candidate_blob = subprocess.run(
                    ["git", "-C", str(REPO_ROOT), "hash-object", "--path", path, path],
                    capture_output=True,
                    check=True,
                    text=True,
                ).stdout.strip()
                self.assertEqual(candidate_blob, baseline_blob)


if __name__ == "__main__":
    unittest.main()
