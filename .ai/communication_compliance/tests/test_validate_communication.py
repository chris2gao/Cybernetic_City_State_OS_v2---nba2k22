from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from referencing import Registry, Resource


REPO_ROOT = Path(__file__).resolve().parents[3]
GATE_DIR = REPO_ROOT / ".ai" / "communication_compliance"
VALIDATOR_PATH = GATE_DIR / "validate_communication.py"

spec = importlib.util.spec_from_file_location("communication_gate", VALIDATOR_PATH)
if spec is None or spec.loader is None:
    raise RuntimeError("cannot load communication validator")
gate = importlib.util.module_from_spec(spec)
spec.loader.exec_module(gate)


def run_git(root: Path, *args: str, input_bytes: bytes | None = None) -> str:
    completed = subprocess.run(
        ["git", "-C", str(root), *args],
        input=input_bytes,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    )
    return completed.stdout.decode("utf-8").strip()


class CommunicationComplianceGateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.policy, cls.policy_sha = gate.load_policy(GATE_DIR / "material_event_policy.yml")
        cls.suite = gate.load_document(GATE_DIR / "fixtures" / "fixture_suite.json")

    def test_release_heads_have_separate_meanings(self) -> None:
        self.assertEqual(self.policy["release_binding_status"], "bound")
        self.assertRegex(self.policy["source_mailbox_base_head"], r"^[0-9a-f]{40}$")
        self.assertRegex(self.policy["protocol_release_head"], r"^[0-9a-f]{40}$")
        self.assertNotEqual(
            self.policy["source_mailbox_base_head"], self.policy["protocol_release_head"]
        )
        self.assertTrue(
            run_git(
                REPO_ROOT,
                "merge-base",
                "--is-ancestor",
                self.policy["source_mailbox_base_head"],
                self.policy["protocol_release_head"],
            )
            == ""
        )

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

    def test_frozen_pointer_keys_human_role_and_direct_route(self) -> None:
        self.assertEqual(
            self.policy["wire_schemas"]["chatgpt_to_codex_v1"]["core_keys"],
            ["signal_id", "decision", "task_ref", "packet_ref", "brief_ref", "source_head", "human_gate"],
        )
        self.assertEqual(
            self.policy["wire_schemas"]["codex_to_chatgpt_v1"]["core_keys"],
            ["packet_id", "status", "report_ref", "brief_ref", "source_head", "review_branch_head", "human_gate"],
        )
        human = self.policy["role_mapping"]["Human"]
        self.assertEqual(human["occupied_role"], "human_speaker")
        self.assertIsNone(human["wire_schema"])
        self.assertEqual(human["direct_dispatch_wire_schema"], "chatgpt_to_codex_v1")

    def test_real_state_graph_is_reachable_and_aliases_are_exact(self) -> None:
        graph: dict[str, set[str]] = {}
        for transition in self.policy["transitions"].values():
            for source in transition["from_states"]:
                graph.setdefault(source, set()).add(transition["to_state"])
        reached = {"closed"}
        frontier = ["closed"]
        while frontier:
            source = frontier.pop()
            for target in graph.get(source, set()):
                if target not in reached:
                    reached.add(target)
                    frontier.append(target)
        self.assertTrue(
            {"backend_assigned", "foreground_review_pending", "human_gate_pending", "publication_in_progress"}.issubset(reached)
        )
        aliases = self.policy["state_evidence"]["aliases"]
        self.assertEqual(aliases["awaiting_codex"], "backend_assigned")
        self.assertEqual(aliases["awaiting_chatgpt_review"], "foreground_review_pending")
        self.assertNotIn("chatgpt_review", aliases)

    def test_every_transition_has_exact_provider_neutral_actor_roles(self) -> None:
        expected = {
            "dispatch_to_backend": {"human_speaker", "foreground_review_and_task_dispatch"},
            "backend_completion": {"backend_execution_and_handoff"},
            "foreground_revision_dispatch": {"human_speaker", "foreground_review_and_task_dispatch"},
            "foreground_acceptance": {"human_speaker", "foreground_review_and_task_dispatch"},
            "publication_candidate": {"human_speaker", "foreground_review_and_task_dispatch"},
            "protected_publication_entry": {"human_speaker", "foreground_review_and_task_dispatch"},
        }
        self.assertEqual(set(self.policy["transitions"]), set(expected))
        for transition_id, roles in expected.items():
            with self.subTest(transition_id=transition_id):
                self.assertEqual(
                    set(self.policy["transitions"][transition_id]["allowed_actor_roles"]),
                    roles,
                )

    def test_all_json_schemas_are_valid(self) -> None:
        schema_paths = sorted(GATE_DIR.glob("*.schema.json"))
        self.assertGreaterEqual(len(schema_paths), 12)
        for path in schema_paths:
            gate.Draft202012Validator.check_schema(gate.load_document(path))

    def test_ledger_schema_hash_chain_and_migration_anchor(self) -> None:
        ledger = gate.load_document(REPO_ROOT / ".ai" / "COMMUNICATION_DRIFT_LEDGER.yml")
        schema = gate.load_document(GATE_DIR / "communication_drift_ledger.schema.json")
        registry = Registry().with_resource(
            "drift_record.schema.json",
            Resource.from_contents(gate.load_schema("drift_record.schema.json")),
        )
        gate.Draft202012Validator(schema, registry=registry).validate(ledger)
        prior_hash = None
        for index, record in enumerate(ledger["records"], 1):
            self.assertEqual(record["sequence"], index)
            self.assertEqual(record["previous_record_sha256"], prior_hash)
            expected = gate.digest_object(
                {key: value for key, value in record.items() if key != "record_sha256"},
                preserve_mapping_order=False,
            )
            self.assertEqual(record["record_sha256"], expected)
            prior_hash = expected
        result = gate.validate_drift_ledger(
            ledger, REPO_ROOT, self.policy, self.policy_sha
        )
        self.assertEqual(result["result"], "pass", result["violations"])

    def test_strict_parser_rejects_duplicate_multidoc_and_alias_yaml(self) -> None:
        raw = GATE_DIR / "fixtures" / "raw"
        for name in ("pointer_duplicate_keys.yml", "pointer_multidoc.yml", "pointer_anchor_alias.yml"):
            with self.subTest(name=name), self.assertRaises(gate.InputDocumentError):
                gate.load_document(raw / name)
        with self.assertRaises(gate.InputDocumentError):
            gate.load_text_document('{"x":1,"x":2}', ".json")

    def test_fixture_suite_matches_all_expected_results(self) -> None:
        result, exit_code = gate.run_fixture_suite(
            self.suite, REPO_ROOT, self.policy, self.policy_sha
        )
        self.assertEqual(exit_code, gate.EXIT_PASS, [case for case in result["cases"] if not case["matched"]])
        self.assertEqual(result["result"], "pass")
        self.assertEqual(result["inherited_inventory_cases"], 79)
        self.assertEqual(result["inherited_behavioral_coverage"], 79)
        self.assertGreaterEqual(result["executed_cases"], 170)
        self.assertEqual(result["total_cases"], result["executed_cases"])
        self.assertEqual(result["matched_cases"], result["total_cases"])
        self.assertEqual(
            result["aggregate_inventory_count"],
            result["inherited_inventory_cases"] + result["executed_cases"],
        )
        self.assertFalse(any(item["id"].startswith("inherited::") for item in result["cases"]))

    def test_fixture_inventory_covers_proof_chain_attacks(self) -> None:
        ids = {case["id"] for case in self.suite["cases"]}
        required = {
            "bootstrap_stale_release_head",
            "human_direct_dispatch_event_pass",
            "human_role_impersonation_rejected",
            "transition_exact_validation_artifact_pass",
            "transition_event_mutation_after_result",
            "transition_fabricated_pass_result",
            "transition_fabricated_resolved_status_rejected",
            "transition_validation_from_other_event_task",
            "transition_claimed_from_state_mismatch",
            "transition_missing_event_ref",
            "transition_state_task_mismatch",
            "transition_unreachable",
            "transition_full_real_workflow",
            "transition_backend_self_acceptance_rejected",
            "transition_backend_material_review_close_rejected",
            "transition_backend_publication_candidate_rejected",
            "transition_foreground_self_completion_rejected",
            "transition_human_self_completion_rejected",
            "transition_provider_role_edge_mismatch_rejected",
            "transition_model_origin_missing",
            "transition_actor_origin_wrong_provider",
            "transition_actor_origin_wrong_role",
            "transition_actor_origin_wrong_transition",
            "transition_actor_origin_event_digest_transplant",
            "transition_actor_origin_cross_event_transplant",
            "transition_actor_origin_replay",
            "transition_c2_authority_event_digest_mismatch",
            "transition_c2_authority_cross_actor_transplant",
            "transition_c2_trusted_host_verifiers_pass",
            "transition_human_acceptance_pass",
            "transition_c2_no_authority",
            "transition_human_c2_no_authority",
            "transition_c2_authority_wrong_task",
            "transition_c2_authority_replay",
            "transition_c2_forged_trusted_context",
            "drift_recurring_immutable_fixture_pass",
            "drift_mutable_fixture_rejected",
            "drift_ledger_delete_rejected",
            "drift_ledger_mutation_rejected",
            "drift_ledger_reorder_rejected",
            "drift_ledger_sequence_rollback",
        }
        self.assertTrue(required.issubset(ids), sorted(required - ids))
        migrated = {item["current_case_id"] for item in gate.load_document(GATE_DIR / "inherited_fixture_coverage_map.json")["mappings"]}
        self.assertEqual(len(migrated), 79)
        self.assertTrue(migrated.issubset(ids), sorted(migrated - ids))
        for label in ("event", "state", "pointer", "validation_artifact"):
            for attack in ("mutable", "missing", "tree", "digest_mismatch", "symlink", "submodule"):
                self.assertIn(f"{label}_ref_{attack}_rejected", ids)

    def test_actor_origin_and_authority_schemas_bind_exact_event(self) -> None:
        origin = gate.load_schema("actor_origin_context.schema.json")
        authority = gate.load_schema("authorization_context.schema.json")
        origin_required = set(origin["required"])
        authority_required = set(authority["required"])
        self.assertTrue(
            {
                "provider",
                "occupied_role",
                "event_id",
                "task_id",
                "transition_id",
                "protocol_release_head",
                "event_input_sha256",
                "replay_protected",
            }.issubset(origin_required)
        )
        self.assertTrue(
            {
                "event_input_sha256",
                "actor_origin_context_id",
                "actor_origin_context_sha256",
            }.issubset(authority_required)
        )

    def test_inherited_coverage_map_is_complete_one_to_one_source(self) -> None:
        coverage = gate.load_document(GATE_DIR / "inherited_fixture_coverage_map.json")
        gate.Draft202012Validator(
            gate.load_schema("inherited_fixture_coverage_map.schema.json")
        ).validate(coverage)
        mappings = coverage["mappings"]
        prior_ids = self.suite["prior_case_ids"]
        self.assertEqual([item["prior_case_id"] for item in mappings], prior_ids)
        self.assertEqual(len({item["current_case_id"] for item in mappings}), len(prior_ids))
        self.assertTrue(all(item["mapping_kind"] == "one_to_one" for item in mappings))

    def test_git_reference_requires_commit_and_rejects_special_entries(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            run_git(root, "init")
            run_git(root, "config", "user.email", "fixture@example.invalid")
            run_git(root, "config", "user.name", "Fixture")
            (root / "regular.txt").write_text("regular\n", encoding="utf-8")
            run_git(root, "add", "regular.txt")
            run_git(root, "commit", "-m", "base")
            commit = run_git(root, "rev-parse", "HEAD")
            tree = run_git(root, "rev-parse", "HEAD^{tree}")
            digest = hashlib.sha256(b"regular\n").hexdigest()
            resolved, _content, findings = gate.resolve_reference(
                root,
                {"kind": "git_blob", "commit": tree, "path": "regular.txt", "content_sha256": digest},
                test_mode=False,
            )
            self.assertEqual(resolved["status"], "unresolved")
            self.assertIn("REFERENCE_UNRESOLVED", {item["code"] for item in findings})

            link_blob = run_git(root, "hash-object", "-w", "--stdin", input_bytes=b"regular.txt")
            run_git(root, "update-index", "--add", "--cacheinfo", "120000", link_blob, "link")
            run_git(root, "commit", "-m", "symlink entry")
            link_commit = run_git(root, "rev-parse", "HEAD")
            resolved, _content, _findings = gate.resolve_reference(
                root,
                {"kind": "git_blob", "commit": link_commit, "path": "link", "content_sha256": hashlib.sha256(b"regular.txt").hexdigest()},
                test_mode=False,
            )
            self.assertEqual(resolved["status"], "unresolved")

            run_git(root, "update-index", "--add", "--cacheinfo", "160000", commit, "submodule")
            run_git(root, "commit", "-m", "submodule entry")
            submodule_commit = run_git(root, "rev-parse", "HEAD")
            resolved, _content, _findings = gate.resolve_reference(
                root,
                {"kind": "git_blob", "commit": submodule_commit, "path": "submodule", "content_sha256": "0" * 64},
                test_mode=False,
            )
            self.assertEqual(resolved["status"], "unresolved")

    def test_test_fixture_reference_is_not_cached_across_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            path = root / "artifact.json"
            path.write_text('{"value":1}\n', encoding="utf-8")
            first = path.read_bytes()
            ref = {"kind": "test_fixture_blob", "path": "artifact.json", "content_sha256": hashlib.sha256(first).hexdigest(), "test_only": True}
            resolved, _content, _findings = gate.resolve_reference(root, ref, test_mode=True)
            self.assertEqual(resolved["status"], "resolved")
            path.write_text('{"value":2}\n', encoding="utf-8")
            resolved, _content, findings = gate.resolve_reference(root, ref, test_mode=True)
            self.assertEqual(resolved["status"], "unresolved")
            self.assertIn("REFERENCE_DIGEST_MISMATCH", {item["code"] for item in findings})

    def test_cli_output_is_environment_independent(self) -> None:
        command = [sys.executable, str(VALIDATOR_PATH), "classify", "--repo-root", str(REPO_ROOT), "--event-type", "backend_dispatch"]
        outputs = []
        for timezone, seed in (("UTC", "1"), ("Pacific/Kiritimati", "98765")):
            env = os.environ.copy()
            env["TZ"] = timezone
            env["PYTHONHASHSEED"] = seed
            run = subprocess.run(command, cwd=REPO_ROOT, env=env, capture_output=True, check=False)
            self.assertEqual(run.returncode, 0, run.stderr.decode("utf-8", errors="replace"))
            outputs.append(run.stdout)
        self.assertEqual(outputs[0], outputs[1])

    def test_release_receipt_files_are_identical_between_semantics_and_binding(self) -> None:
        release = self.policy["protocol_release_head"]
        for path in self.policy["bootstrap_required_loaded_files"] + sorted(
            {item for values in self.policy["bootstrap_on_demand_requirements"].values() for item in values}
        ):
            with self.subTest(path=path):
                release_blob = run_git(REPO_ROOT, "rev-parse", f"{release}:{path}")
                candidate_blob = run_git(REPO_ROOT, "rev-parse", f"HEAD:{path}")
                self.assertEqual(candidate_blob, release_blob)

    def test_source_mailboxes_are_byte_identical_to_neutral_base(self) -> None:
        base = self.policy["source_mailbox_base_head"]
        for path in (".ai/INBOX.md", ".ai/OUTBOX.md", ".ai/STATE.yml", ".ai/HUMAN_BRIEF.md"):
            with self.subTest(path=path):
                self.assertEqual(
                    run_git(REPO_ROOT, "rev-parse", f"{base}:{path}"),
                    run_git(REPO_ROOT, "hash-object", "--path", path, path),
                )


if __name__ == "__main__":
    unittest.main()
