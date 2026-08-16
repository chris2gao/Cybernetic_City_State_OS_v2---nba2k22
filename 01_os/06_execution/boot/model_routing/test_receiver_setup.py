from pathlib import Path
import sys
import unittest

import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))
from route_receiver import (  # noqa: E402
    ReceiverSetupError,
    build_receiver_setup,
    validate_receiver_setup,
)


REPO = Path(__file__).resolve().parents[4]
CATALOG = yaml.safe_load(
    (REPO / "01_os/03_mechanisms/model_routing/模型与产品面目录_v1.yml").read_text(encoding="utf-8")
)
SOURCE_INDEX = yaml.safe_load(
    (REPO / "01_os/03_mechanisms/model_routing/来源索引_v1.yml").read_text(encoding="utf-8")
)
ROLES = yaml.safe_load(
    (REPO / "01_os/03_mechanisms/model_routing/协作角色与接收者设置契约_v1.yml").read_text(encoding="utf-8")
)


def selection(**overrides):
    value = {
        "collaboration_role": "execution",
        "provider": "OpenAI",
        "surface": "codex_desktop",
        "model": "GPT-5.6 Sol",
        "reasoning_or_parameter_profile": "codex_sol_strongest_exposed",
        "session_mode": "standard",
        "isolation_level": "task_branch",
        "repository_access_mode": "local_worktree",
        "repository_or_worktree_requirement": "authorized_task_branch",
        "required_branch_or_sha": "dev/task",
        "local_files_required": True,
        "github_publication_required_before_start": False,
        "communication_carrier": "local",
        "routing_basis_ref": "routing_receipt.yml",
        "availability_assumption_or_observation_ref": "routing_receipt.yml#availability",
        "limitations": ["role_grants_no_authority"],
    }
    value.update(overrides)
    return value


def cowork_selection(**overrides):
    return selection(
        provider="Anthropic",
        surface="claude_desktop_cowork",
        model="Claude Opus 5",
        reasoning_or_parameter_profile="claude_desktop_cowork_opus5_task_time",
        **overrides,
    )


class ReceiverSetupTests(unittest.TestCase):
    def test_builds_exact_human_visible_setup_from_registered_route(self):
        setup = build_receiver_setup(selection(), catalog=CATALOG, role_contract=ROLES)
        self.assertEqual(setup["product"], "Codex Desktop")
        self.assertEqual(setup["collaboration_role"], "execution")
        self.assertNotIn("authority", setup)

    def test_unregistered_or_unsupported_route_fails_closed(self):
        with self.assertRaisesRegex(ReceiverSetupError, "catalog_identity"):
            build_receiver_setup(selection(model="imaginary"), catalog=CATALOG, role_contract=ROLES)
        with self.assertRaisesRegex(ReceiverSetupError, "profile_unsupported"):
            build_receiver_setup(
                selection(reasoning_or_parameter_profile="unsupported"),
                catalog=CATALOG,
                role_contract=ROLES,
            )

    def test_cowork_opus5_registered_route_builds_exact_product_surface_identity(self):
        setup = build_receiver_setup(cowork_selection(), catalog=CATALOG, role_contract=ROLES)
        self.assertEqual(setup["provider"], "Anthropic")
        self.assertEqual(setup["product"], "Claude Desktop")
        self.assertEqual(setup["surface"], "claude_desktop_cowork")
        self.assertEqual(setup["model"], "Claude Opus 5")
        self.assertEqual(
            setup["reasoning_or_parameter_profile"],
            "claude_desktop_cowork_opus5_task_time",
        )

    def test_cowork_model_profile_and_product_mismatches_fail_closed(self):
        with self.assertRaisesRegex(ReceiverSetupError, "catalog_identity"):
            build_receiver_setup(
                cowork_selection(model="Claude Opus 5 imaginary"),
                catalog=CATALOG,
                role_contract=ROLES,
            )
        with self.assertRaisesRegex(ReceiverSetupError, "profile_unsupported"):
            build_receiver_setup(
                cowork_selection(reasoning_or_parameter_profile="claude_code_account_current"),
                catalog=CATALOG,
                role_contract=ROLES,
            )
        setup = build_receiver_setup(cowork_selection(), catalog=CATALOG, role_contract=ROLES)
        setup["product"] = "Claude Cowork"
        with self.assertRaisesRegex(ReceiverSetupError, "product_surface_mismatch"):
            validate_receiver_setup(setup, catalog=CATALOG, role_contract=ROLES)

    def test_cowork_registration_separates_provider_surface_evidence_from_human_model_label(self):
        entry = next(
            item
            for item in CATALOG["entries"]
            if item.get("provider") == "Anthropic"
            and item.get("surface_id") == "claude_desktop_cowork"
            and item.get("model_label") == "Claude Opus 5"
        )
        self.assertTrue(entry["registered"])
        self.assertEqual(
            entry["evidence_binding"]["surface_and_product_identity"],
            "provider_first_party_documentation",
        )
        self.assertEqual(
            entry["evidence_binding"]["exact_model_label"],
            "Human_task_time_observation",
        )
        self.assertFalse(entry["evidence_binding"]["exact_model_label_provider_documentation_claimed"])
        source_refs = set(entry["source_refs"])
        self.assertIn("ANTH_COWORK_GET_STARTED", source_refs)
        self.assertIn("HUMAN_COWORK_OPUS5_20260815", source_refs)
        self.assertEqual(SOURCE_INDEX["sources"]["ANTH_COWORK_GET_STARTED"]["kind"], "provider_first_party")
        self.assertEqual(
            SOURCE_INDEX["sources"]["HUMAN_COWORK_OPUS5_20260815"]["kind"],
            "Human_task_time_observation",
        )
        rules = SOURCE_INDEX["resolution_contract"]["field_binding_rules"]
        self.assertTrue(rules["surface_and_product_identity"]["provider_first_party_source_required"])
        self.assertTrue(rules["exact_active_UI_model_label"]["Human_task_time_observation_allowed"])
        self.assertTrue(rules["exact_active_UI_model_label"]["requires_externally_bound_surface"])

    def test_github_only_receiver_cannot_assume_local_files(self):
        with self.assertRaisesRegex(ReceiverSetupError, "local_material_unpublished"):
            build_receiver_setup(
                selection(repository_access_mode="GitHub_only"),
                catalog=CATALOG,
                role_contract=ROLES,
            )
        setup = build_receiver_setup(
            selection(
                repository_access_mode="GitHub_only",
                github_publication_required_before_start=True,
                communication_carrier="GitHub",
            ),
            catalog=CATALOG,
            role_contract=ROLES,
        )
        self.assertTrue(setup["github_publication_required_before_start"])
        with self.assertRaisesRegex(ReceiverSetupError, "requires_GitHub_carrier"):
            build_receiver_setup(
                selection(
                    repository_access_mode="GitHub_only",
                    local_files_required=False,
                    github_publication_required_before_start=True,
                    communication_carrier="local",
                ),
                catalog=CATALOG,
                role_contract=ROLES,
            )

    def test_independent_review_requires_isolation_and_private_context_limit(self):
        with self.assertRaisesRegex(ReceiverSetupError, "isolation_invalid"):
            build_receiver_setup(
                selection(collaboration_role="independent_review", isolation_level="shared"),
                catalog=CATALOG,
                role_contract=ROLES,
            )
        with self.assertRaisesRegex(ReceiverSetupError, "private_context_limit"):
            build_receiver_setup(
                selection(collaboration_role="independent_review", isolation_level="isolated_project"),
                catalog=CATALOG,
                role_contract=ROLES,
            )


if __name__ == "__main__":
    unittest.main()
