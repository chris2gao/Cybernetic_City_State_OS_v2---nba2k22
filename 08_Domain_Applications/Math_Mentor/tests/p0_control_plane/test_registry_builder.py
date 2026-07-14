from __future__ import annotations

import json
import subprocess
import sys
import unittest
import uuid
from pathlib import Path
from unittest import mock

from jsonschema import Draft202012Validator


REPO_ROOT = Path(__file__).resolve().parents[4]
MATH_MENTOR = Path(__file__).resolve().parents[2]
if str(MATH_MENTOR) not in sys.path:
    sys.path.insert(0, str(MATH_MENTOR))

from p0_control_plane import registry_builder as builder
from p0_control_plane.identity import canonical_json_bytes


SOURCE_HEAD = "764d03d7d0a9ad553f4f3868699b06d9de5553ea"
FORBIDDEN_AGGREGATE = (
    "08_Domain_Applications/Math_Mentor/学习期prompt/数学知识路线图_全部.yaml"
)
FULLWIDTH_PATHS = {
    "08_Domain_Applications/Math_Mentor/Pure_Math_Intuition_DB/ANALYTIC_NT-684.yaml",
    "08_Domain_Applications/Math_Mentor/Pure_Math_Intuition_DB/ANALYTIC_NT-687.yaml",
    "08_Domain_Applications/Math_Mentor/Pure_Math_Intuition_DB/ANALYTIC_NT-688.yaml",
    "08_Domain_Applications/Math_Mentor/Pure_Math_Intuition_DB/ANALYTIC_NT-692.yaml",
    "08_Domain_Applications/Math_Mentor/Pure_Math_Intuition_DB/DIFF_GEO-662.yaml",
    "08_Domain_Applications/Math_Mentor/Pure_Math_Intuition_DB/DIFF_GEO-663.yaml",
    "08_Domain_Applications/Math_Mentor/Pure_Math_Intuition_DB/DIFF_GEO-668.yaml",
}


class RegistryBuilderTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.outputs = builder.build_all(REPO_ROOT, SOURCE_HEAD)
        cls.root = cls.outputs["ROOT_CORPUS_REGISTRY.json"]
        cls.crosswalk = cls.outputs["CANONICAL_NODE_CROSSWALK.json"]
        cls.conflicts = cls.outputs["ALIAS_CONFLICT_REGISTRY.json"]

    def test_root_discovery_reproduces_frozen_source_snapshot(self) -> None:
        summary = self.root["summary"]
        self.assertEqual(SOURCE_HEAD, self.root["source_head"])
        self.assertEqual(1014, summary["tracked_scope_path_count"])
        self.assertEqual(912, summary["db_tracked_count"])
        self.assertEqual(683, summary["root_direct_count"])
        self.assertEqual(229, summary["nested_excluded_count"])
        self.assertEqual(667, summary["root_candidate_count"])
        self.assertEqual(667, summary["root_candidate_parse_pass_count"])
        self.assertEqual(245, summary["excluded_asset_count"])
        self.assertEqual({"missing": 1, "resolved": 666}, summary["strict_identity_counts"])
        self.assertEqual(
            {
                "E1_wrapper_or_alternate_identity": 143,
                "E2_flat_migration_legacy": 496,
                "E3_stage0_canonical_body": 8,
                "E4_post_stage0_repaired": 20,
            },
            summary["schema_era_counts"],
        )

    def test_candidate_discovery_excludes_staging_bridges_schema_and_script(self) -> None:
        node_paths = {node["path"] for node in self.root["nodes"]}
        self.assertEqual(667, len(node_paths))
        self.assertFalse(any("/staging/" in path for path in node_paths))
        self.assertFalse(any(Path(path).name.startswith("BRIDGE-") for path in node_paths))
        self.assertNotIn(
            "08_Domain_Applications/Math_Mentor/Pure_Math_Intuition_DB/schema.yaml",
            node_paths,
        )
        excluded = self.root["excluded_assets"]
        self.assertTrue(all(item["parsed_as_node"] is False for item in excluded))
        self.assertTrue(all(item["identity_resolution_allowed"] is False for item in excluded))

    def test_crosswalk_reproduces_frozen_ascii_claim_comparison(self) -> None:
        summary = self.crosswalk["summary"]
        self.assertEqual(667, summary["canonical_node_count"])
        self.assertEqual(770, summary["roadmap_entry_count"])
        self.assertEqual(473, summary["explicit_self_claim_file_count"])
        self.assertEqual(473, summary["distinct_explicit_roadmap_claim_count"])
        self.assertEqual(297, summary["roadmap_without_explicit_claim_count"])
        self.assertEqual(
            {
                "agree": 416,
                "disagree": 53,
                "explicit_only": 4,
                "neither": 28,
                "stage0_only": 166,
            },
            summary["alias_comparison_counts"],
        )
        self.assertEqual(
            {
                "conflict_open": 53,
                "declared_consistent_unapproved": 420,
                "quarantined": 2,
                "unclaimed": 192,
            },
            summary["binding_status_counts"],
        )
        self.assertEqual(420, summary["candidate_edge_count"])
        self.assertEqual(0, summary["human_approved_binding_count"])
        self.assertEqual(0, summary["consumer_allowed_count"])

    def test_fullwidth_claims_are_exact_diagnostics_and_never_edges(self) -> None:
        nodes_by_path = {
            next(alias["value"] for alias in node["aliases"] if alias["alias_type"] == "root_path"): node
            for node in self.crosswalk["nodes"]
        }
        diagnosed = {
            path
            for path, node in nodes_by_path.items()
            if node["alias_comparison"]["unparsed_fullwidth_roadmap_claims"]
        }
        self.assertEqual(FULLWIDTH_PATHS, diagnosed)
        for path in diagnosed:
            node = nodes_by_path[path]
            self.assertEqual("stage0_only", node["alias_comparison"]["status"])
            self.assertIsNone(node["candidate_edge_uuid"])
            self.assertFalse(node["consumer_allowed"])
            self.assertIn("unicode_fullwidth_roadmap_tag_unparsed", node["blockers"])

    def test_conflict_registry_reproduces_fail_closed_findings(self) -> None:
        summary = self.conflicts["summary"]
        self.assertEqual(286, summary["conflict_record_count"])
        self.assertEqual(
            {
                "explicit_vs_stage0_alias_disagreement": 53,
                "filename_domain_id_difference_diagnostic": 3,
                "forbidden_filename_suffix_collision_evidence": 33,
                "missing_explicit_roadmap_alias": 194,
                "source_quarantine_disposition": 2,
                "strict_domain_id_missing": 1,
            },
            summary["counts_by_type"],
        )
        self.assertEqual(153, summary["forbidden_filename_suffix_collision_member_count"])
        self.assertEqual(7, summary["unicode_fullwidth_roadmap_tag_unparsed_file_count"])
        self.assertEqual(0, summary["resolved_by_suffix_count"])
        self.assertEqual(0, summary["resolved_by_basename_count"])
        self.assertEqual(0, summary["resolved_by_fuzzy_match_count"])
        self.assertEqual(0, summary["resolved_from_staging_count"])

    def test_opaque_uuidv5_is_unique_and_only_materialized_node_primary(self) -> None:
        root_uuids = [node["canonical_uuid"] for node in self.root["nodes"]]
        crosswalk_uuids = [node["canonical_uuid"] for node in self.crosswalk["nodes"]]
        self.assertEqual(667, len(set(root_uuids)))
        self.assertEqual(set(root_uuids), set(crosswalk_uuids))
        self.assertTrue(all(uuid.UUID(value).version == 5 for value in root_uuids))
        model = self.crosswalk["identity_model"]
        self.assertEqual("canonical_uuid", model["sole_node_primary"])
        self.assertTrue(model["bootstrap_only"])
        self.assertFalse(model["prior_crosswalk_preservation_implemented"])
        self.assertFalse(model["human_resolution_trust_adapter_implemented"])

    def test_six_allowlisted_roadmaps_are_contiguous_and_aggregate_is_forbidden(self) -> None:
        entries = self.crosswalk["roadmap_entries"]
        self.assertEqual([f"n_{number}" for number in range(1, 771)], [e["roadmap_id_alias"] for e in entries])
        config = builder.load_config(REPO_ROOT)
        with self.assertRaises(builder.ForbiddenInputError):
            builder.ensure_allowed_roadmap_path(FORBIDDEN_AGGREGATE, config)
        input_paths = {item["path"] for item in self.crosswalk["inputs"]}
        self.assertNotIn(FORBIDDEN_AGGREGATE, input_paths)

    def test_nonempty_model_writable_resolution_overlay_is_rejected(self) -> None:
        forged = {
            "schema_version": "1.0.0",
            "namespace_uuid": self.crosswalk["namespace_uuid"],
            "resolutions": [
                {
                    "approved_by": "Human Speaker",
                    "decision": "bind",
                    "packet_ref": "model-writable-string-is-not-authentication",
                }
            ]
        }
        with self.assertRaisesRegex(builder.BuildError, "Human-authenticated"):
            builder.validate_and_apply_resolutions(
                forged,
                SOURCE_HEAD,
                {"namespace_uuid": self.crosswalk["namespace_uuid"]},
                {},
                "Human Speaker",
            )

    def test_outputs_validate_against_their_schemas(self) -> None:
        schema_dir = MATH_MENTOR / "p0_control_plane/schemas"
        for output_name, schema_name in (
            ("ROOT_CORPUS_REGISTRY.json", "root_corpus_registry.schema.json"),
            ("CANONICAL_NODE_CROSSWALK.json", "canonical_node_crosswalk.schema.json"),
            ("ALIAS_CONFLICT_REGISTRY.json", "alias_conflict_registry.schema.json"),
        ):
            schema = json.loads((schema_dir / schema_name).read_text(encoding="utf-8"))
            errors = sorted(
                Draft202012Validator(schema).iter_errors(self.outputs[output_name]),
                key=lambda item: list(item.path),
            )
            self.assertEqual([], [error.message for error in errors])

    def test_build_is_byte_deterministic(self) -> None:
        repeated = builder.build_all(REPO_ROOT, SOURCE_HEAD)
        for name in builder.OUTPUT_NAMES:
            self.assertEqual(
                canonical_json_bytes(self.outputs[name]),
                canonical_json_bytes(repeated[name]),
            )

    def test_descendant_development_head_does_not_change_source_snapshot(self) -> None:
        with mock.patch.object(builder, "current_head", return_value="f" * 40), mock.patch.object(
            builder, "is_ancestor", return_value=True
        ):
            repeated = builder.build_all(REPO_ROOT, SOURCE_HEAD)
        for name in builder.OUTPUT_NAMES:
            self.assertEqual(SOURCE_HEAD, repeated[name]["source_head"])
            self.assertEqual(
                canonical_json_bytes(self.outputs[name]),
                canonical_json_bytes(repeated[name]),
            )

    def test_nonbaseline_source_commit_is_rejected_before_corpus_read(self) -> None:
        parent_head = subprocess.check_output(
            ["git", "rev-parse", f"{SOURCE_HEAD}^"], cwd=REPO_ROOT, text=True
        ).strip()
        with self.assertRaisesRegex(builder.BuildError, "frozen baseline"):
            builder.build_all(REPO_ROOT, parent_head)


if __name__ == "__main__":
    unittest.main()
