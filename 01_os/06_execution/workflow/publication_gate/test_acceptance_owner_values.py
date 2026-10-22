"""Partial record/content probes, NOT scope acceptance, Git binding or Human identity."""
import copy
import importlib.util
from pathlib import Path
import unittest

import test_publication_gate as fixture

ROOT = Path(__file__).resolve().parents[4]
SPEC = importlib.util.spec_from_file_location(
    "acceptance_value_subject",
    ROOT / "01_os/03_mechanisms/stage_collaborative_deliberation/实现/verify_stage_collaborative_deliberation.py")
owner = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(owner)


def context():
    sid = fixture.STAGES[0]
    commit = "a" * 40
    ref = {"commit": commit, "path": "synthetic/model.yml", "blob_sha": "b" * 40}
    return {
        "phase": "plan", "task_id": fixture.TASK_ID, "stage_id": sid,
        "record": fixture.accepted(sid, fixture.PLAN_DECISION, exact_model_version=commit),
        "bound_model": copy.deepcopy(ref), "accepted_model": copy.deepcopy(ref),
        "model": fixture.current_model(sid, commit),
        "receipt": fixture.stage_receipt(sid, commit),
        "profile_set": copy.deepcopy(fixture.PROFILE_SET_DOC),
        "contract": copy.deepcopy(fixture.PROFILE_CONTRACT_DOC),
    }


INVALID_VALUES = (True, False, 0, 1, " \t", [], {}, None)
VALID_VALUES = ("none_material", "supported result", ["supported result"], {"result": "supported"})


def completion_context():
    data = context()
    sid = fixture.STAGES[0]
    output = {"commit": "c" * 40, "path": "synthetic/output.yml", "blob_sha": "d" * 40}
    verification = {"commit": "e" * 40, "path": "synthetic/verification.yml", "blob_sha": "f" * 40}
    data.update(phase="completion", accepted_output=output, accepted_verification=verification,
                verification=fixture.verification_doc(sid, output["commit"]))
    data["record"] = fixture.accepted(sid, fixture.COMPLETION_DECISION,
        bound_output_version=output["commit"], verification_result=copy.deepcopy(verification),
        actual_result="The synthetic output was produced and its verification recorded.",
        plan_vs_actual_delta="none_material", material_deviation="none_material",
        residual_risk="none_material", downstream_baseline=output["commit"])
    return data


class OwnerValueCases(unittest.TestCase):
    def test_receipt_versions_are_positive_integers(self):
        for field in ("mechanism_version", "active_contract_version", "boot_manifest_version",
                      "registry_version", "loader_version"):
            for value in (True, False, 0, -1, "1", 1.0, None):
                with self.subTest(field=field, value=value):
                    data = context()
                    data["receipt"][field] = value
                    self.assertEqual(owner._validate_stage_acceptance_records(data),
                                     (17, "receipt_version_invalid"))

    def test_receipt_list_fields_have_string_items(self):
        for field in ("loaded_paths", "open_detail_divergence_event_refs", "deferred_detail_record_refs"):
            for value in (False, "path", [False], [" "], ["same", "same"]):
                with self.subTest(field=field, value=value):
                    data = context()
                    data["receipt"][field] = value
                    self.assertEqual(owner._validate_stage_acceptance_records(data),
                                     (17, "receipt_list_required:" + field))

    def test_receipt_validator_mode_and_exit_types(self):
        for value in ({"mode": "instance", "exit_code": False},
                      {"mode": "instance", "exit_code": 0.0},
                      {"mode": "full", "exit_code": 0}):
            with self.subTest(value=value):
                data = context()
                data["receipt"]["validator_mode_and_exit_code"] = value
                self.assertEqual(owner._validate_stage_acceptance_records(data),
                                 (17, "receipt_validator_result_invalid"))

    def test_receipt_mechanism_is_a_nonempty_string_list(self):
        for value in ("mechanism", [], [False], [" "]):
            with self.subTest(value=value):
                data = context()
                data["receipt"]["main_mechanism_ref"] = value
                self.assertEqual(owner._validate_stage_acceptance_records(data),
                                 (17, "receipt_mechanism_required"))

    def test_public_entry_requires_repository_and_candidate(self):
        self.assertEqual(owner.validate_stage_acceptance_context(context()),
                         (11, "explicit_repository_and_candidate_required"))

    def test_positive_context(self):
        self.assertEqual(owner._validate_stage_acceptance_records(context()), (0, ""))

    def test_common_field_rejects_nonvalues(self):
        for field in ("proposed_method_or_solution", "downstream_impact"):
            for value in INVALID_VALUES:
                with self.subTest(field=field, value=value):
                    data = context()
                    data["model"][field] = value
                    self.assertEqual(owner._validate_stage_acceptance_records(data),
                                     (16, "current_model_completeness"))

    def test_common_field_accepts_explicit_values(self):
        for value in VALID_VALUES:
            with self.subTest(value=value):
                data = context()
                data["model"]["downstream_impact"] = value
                self.assertEqual(owner._validate_stage_acceptance_records(data), (0, ""))

    def test_represented_element_rejects_nonvalues(self):
        for value in INVALID_VALUES:
            with self.subTest(value=value):
                data = context()
                data["model"]["stage_specific_model_elements"][fixture.STAGE_FIELDS[fixture.STAGES[0]][0]]["value"] = value
                self.assertEqual(owner._validate_stage_acceptance_records(data),
                                 (16, "effective_stage_model"))

    def test_represented_element_accepts_explicit_values(self):
        for value in VALID_VALUES:
            with self.subTest(value=value):
                data = context()
                data["model"]["stage_specific_model_elements"][fixture.STAGE_FIELDS[fixture.STAGES[0]][0]]["value"] = value
                self.assertEqual(owner._validate_stage_acceptance_records(data), (0, ""))

    def test_irrelevance_requires_nonempty_text(self):
        for value in (True, 1, " \t", ["not text"], {"not": "text"}):
            with self.subTest(value=value):
                data = context()
                data["model"]["stage_specific_model_elements"][fixture.STAGE_FIELDS[fixture.STAGES[0]][0]] = {
                    "disposition": "explicitly_irrelevant_with_reason_and_scope", "reason_and_scope": value}
                self.assertEqual(owner._validate_stage_acceptance_records(data),
                                 (16, "effective_stage_model"))

    def test_irrelevance_with_reason_and_scope_is_accepted(self):
        data = context()
        data["model"]["stage_specific_model_elements"][fixture.STAGE_FIELDS[fixture.STAGES[0]][0]] = {
            "disposition": "explicitly_irrelevant_with_reason_and_scope",
            "reason_and_scope": "This fixture has no external consumer for this element."}
        self.assertEqual(owner._validate_stage_acceptance_records(data), (0, ""))

    def test_complete_completion_summary_passes(self):
        self.assertEqual(owner._validate_stage_acceptance_records(completion_context()), (0, ""))

    def test_completion_actual_result_is_required(self):
        data = completion_context()
        del data["record"]["actual_result"]
        self.assertEqual(owner._validate_stage_acceptance_records(data), (14, "actual_result_required"))

    def test_completion_actual_result_must_be_nonempty_text(self):
        for value in INVALID_VALUES:
            with self.subTest(value=value):
                data = completion_context()
                data["record"]["actual_result"] = value
                self.assertEqual(owner._validate_stage_acceptance_records(data), (14, "actual_result_required"))

    def test_completion_closure_cannot_be_empty_or_boolean(self):
        for field in ("plan_vs_actual_delta", "material_deviation", "residual_risk", "downstream_baseline"):
            for value in (False, " \t", [], {}):
                with self.subTest(field=field, value=value):
                    data = completion_context()
                    data["record"][field] = value
                    self.assertEqual(owner._validate_stage_acceptance_records(data),
                                     (14, f"closure_field_empty:{field}"))

    def test_completion_closure_accepts_explicit_values(self):
        for value in VALID_VALUES:
            with self.subTest(value=value):
                data = completion_context()
                data["record"]["residual_risk"] = value
                self.assertEqual(owner._validate_stage_acceptance_records(data), (0, ""))


if __name__ == "__main__":
    unittest.main()
