from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import unittest

import yaml
import activation

from activation import (
    ActivationError,
    MaterialObservationContext,
    _compare_claim,
    evaluate_material_claim,
    observe_changed_path_claim,
    observe_git_base_relation_claim,
    observe_git_commit_claim,
    validate_material_receipt,
)


SHA_A = "a" * 40
SHA_B = "b" * 40


def claim(comparator, expected, observed, **overrides):
    value = {
        "claim_id": "claim-001",
        "claim_role": "candidate_SHA",
        "action_id_or_review_id": "action-001",
        "expected_claim_source_ref": "task_packet.yml#candidate",
        "expected_value_or_predicate": expected,
        "observed_authoritative_source_class": "actual_Git_object_database",
        "observed_value": observed,
        "exact_observation_ref": "git:physical-observation",
        "comparator_id": comparator,
        "relationship_or_equality_check": "executed",
        "verification_result": "UNVERIFIABLE",
    }
    value.update(overrides)
    return value


class MaterialClaimComparatorTests(unittest.TestCase):
    def test_candidate_and_base_sha_swaps_are_mismatch(self):
        self.assertEqual(_compare_claim(claim("exact_sha_role_equality", SHA_A, SHA_B)), "MISMATCH")
        base = claim(
            "exact_base_equality_plus_required_relation",
            {"sha": SHA_B, "required_relation": "ancestor_of_candidate"},
            {"sha": SHA_A, "relation_satisfied": True},
            claim_role="base_SHA",
        )
        self.assertEqual(_compare_claim(base), "MISMATCH")

    def test_stale_named_ref_and_wrong_ref_fail(self):
        stale = claim(
            "named_ref_fresh_state_relation",
            {"sha": SHA_A}, {"sha": SHA_A, "fresh": False},
            claim_role="moving_head_or_current_ref",
            observed_authoritative_source_class="fresh_remote_Git_ref_readback",
        )
        self.assertEqual(_compare_claim(stale), "STALE")
        wrong = dict(stale,
            expected_value_or_predicate={"named_ref": "refs/heads/master", "sha": SHA_A},
            observed_value={"named_ref": "refs/heads/task", "sha": SHA_A, "fresh": True})
        self.assertEqual(_compare_claim(wrong), "MISMATCH")

    def test_integrity_execution_and_actor_semantic_mismatches(self):
        integrity = claim(
            "byte_integrity_and_semantic_role_binding",
            {"sha256": "abc", "candidate_sha": SHA_A},
            {"sha256": "abc", "candidate_sha": SHA_B},
            claim_role="durable_evidence_artifact",
            observed_authoritative_source_class="Git_blob_at_exact_commit",
        )
        self.assertEqual(_compare_claim(integrity), "MISMATCH")
        execution = claim(
            "execution_result_bound_to_expected_candidate_inputs_and_entrypoint",
            {"candidate_sha": SHA_A, "test_package_ref": "frozen-v1"},
            {"candidate_sha": SHA_A, "test_package_ref": "other"},
            claim_role="execution_or_validation_result",
            observed_authoritative_source_class="trusted_execution_adapter",
        )
        self.assertEqual(_compare_claim(execution), "MISMATCH")
        actor = claim(
            "authenticated_actor_satisfies_authorized_principal_binding",
            {"allowed_principals": ["alice"], "action": "push"},
            {"authenticated_principal": "mallory", "action": "push"},
            claim_role="authority_and_actual_actor",
            observed_authoritative_source_class="local_authenticated_principal",
            subject_principal_observation_ref="host:principal",
        )
        self.assertEqual(_compare_claim(actor), "MISMATCH")

    def test_path_set_fail_closed_cases(self):
        base = claim(
            "complete_path_set_within_authorized_boundary",
            {"allowed_patterns": ["allowed/**"]},
            {"paths": ["allowed/a.txt"], "complete": False},
            claim_role="changed_path_and_diff_scope",
            observed_authoritative_source_class="complete_Git_compare",
        )
        self.assertEqual(_compare_claim(base), "UNVERIFIABLE")
        self.assertEqual(_compare_claim(dict(base, observed_value={"paths": ["allowed/a.txt"] * 2, "complete": True})), "AMBIGUOUS")
        self.assertEqual(_compare_claim(dict(base, observed_value={"paths": ["allowed\\a.txt"], "complete": True})), "AMBIGUOUS")
        self.assertEqual(_compare_claim(dict(base, observed_value={"paths": ["allowed/a.txt", "forbidden.txt"], "complete": True})), "MISMATCH")


class ProvenanceBoundaryTests(unittest.TestCase):
    def test_public_context_has_no_caller_binding_api(self):
        self.assertFalse(hasattr(MaterialObservationContext(), "bind"))

    def test_self_consistent_claim_without_expected_resolver_is_nonpass(self):
        value = claim("exact_sha_role_equality", SHA_A, SHA_A)
        self.assertEqual(evaluate_material_claim(value, MaterialObservationContext()), "UNVERIFIABLE")

    def test_comparator_role_mismatch_is_nonpass(self):
        value = claim("exact_sha_role_equality", SHA_A, SHA_A, claim_role="base_SHA")
        self.assertEqual(evaluate_material_claim(value), "UNVERIFIABLE")

    def test_unregistered_observation_source_is_nonpass(self):
        value = claim(
            "exact_sha_role_equality", SHA_A, SHA_A,
            observed_authoritative_source_class="caller_declared_source",
        )
        self.assertEqual(evaluate_material_claim(value), "UNVERIFIABLE")

    def test_freshness_requirement_without_observation_ref_is_stale(self):
        value = claim(
            "named_ref_fresh_state_relation", {"sha": SHA_A}, {"sha": SHA_A, "fresh": True},
            claim_role="moving_head_or_current_ref",
            observed_authoritative_source_class="fresh_remote_Git_ref_readback",
            freshness_requirement_when_applicable="immediately_before_action",
        )
        self.assertEqual(evaluate_material_claim(value), "STALE")

    def test_no_generic_issuance_or_attachment_surface_exists(self):
        for name in (
            "_issue_expected", "_issue_observed", "attach_material_evidence",
            "_ResolvedExpectedSource", "_ConsumedObservation", "resolve_expected_yaml",
        ):
            self.assertFalse(hasattr(activation, name), name)

    def test_direct_semantic_equivalent_cannot_register_caller_facts(self):
        lookalike_expected = {
            "claim_id": "claim-001", "source_ref": "task.yml#candidate", "value": SHA_A
        }
        lookalike_observed = {
            "claim_id": "claim-001", "source_class": "actual_Git_object_database",
            "value": SHA_A, "exact_ref": "git:physical-observation",
        }
        context = MaterialObservationContext()
        for candidate in vars(activation).values():
            self.assertFalse(
                callable(candidate) and getattr(candidate, "__name__", "") in {
                    "_issue_expected", "_issue_observed", "attach_material_evidence"
                }
            )
        self.assertEqual(lookalike_expected["value"], lookalike_observed["value"])
        self.assertEqual(
            evaluate_material_claim(claim("exact_sha_role_equality", SHA_A, SHA_A), context),
            "UNVERIFIABLE",
        )

    def test_expected_ref_fragment_cannot_select_a_different_fact(self):
        with TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "task.yml").write_text("candidate: " + SHA_A + "\nbase: " + SHA_B + "\n", encoding="utf-8")
            with self.assertRaisesRegex(ActivationError, "SELECTOR_REF_MISMATCH"):
                observe_git_commit_claim(
                    root,
                    claim_id="claim-001",
                    claim_role="candidate_SHA",
                    action_id_or_review_id="action",
                    expected_root=root,
                    expected_source_ref="task.yml#candidate",
                    expected_value_path=("base",),
                    observation_context=MaterialObservationContext(),
                )

    def test_fabricated_complete_git_compare_is_nonpass(self):
        value = claim(
            "complete_path_set_within_authorized_boundary",
            {"allowed_patterns": ["allowed/**"]},
            {"base_sha": SHA_A, "candidate_sha": SHA_B, "paths": ["allowed/a"], "complete": True},
            claim_role="changed_path_and_diff_scope",
            observed_authoritative_source_class="complete_Git_compare",
        )
        self.assertEqual(evaluate_material_claim(value), "UNVERIFIABLE")

    def test_fabricated_authenticated_principal_is_nonpass(self):
        value = claim(
            "authenticated_actor_satisfies_authorized_principal_binding",
            {"allowed_principals": ["alice"]}, {"authenticated_principal": "alice"},
            claim_role="authority_and_actual_actor",
            observed_authoritative_source_class="local_authenticated_principal",
            subject_principal_observation_ref="caller:asserted-principal",
        )
        self.assertEqual(evaluate_material_claim(value), "UNVERIFIABLE")

    def test_fabricated_conditional_ref_consumption_is_nonpass(self):
        value = claim(
            "named_ref_fresh_state_relation", {"sha": SHA_A}, {"sha": SHA_A, "fresh": True},
            claim_role="moving_head_or_current_ref",
            observed_authoritative_source_class="fresh_remote_Git_ref_readback",
            freshness_requirement_when_applicable="immediately_before_action",
            freshness_observation_ref="caller:asserted-freshness",
        )
        self.assertEqual(evaluate_material_claim(value), "UNVERIFIABLE")

    def test_receipt_cannot_declare_verified_without_executed_context(self):
        value = claim("exact_sha_role_equality", SHA_A, SHA_A)
        value["verification_result"] = "VERIFIED"
        with self.assertRaisesRegex(ActivationError, "DECLARED_RESULT_MISMATCH"):
            validate_material_receipt({"material_claims": [value], "aggregate_result": "VERIFIED"})

    def test_aggregate_cannot_pass_nonverified_claim(self):
        value = claim("exact_sha_role_equality", SHA_A, SHA_A)
        value["verification_result"] = "UNVERIFIABLE"
        with self.assertRaisesRegex(ActivationError, "AGGREGATE_MISMATCH"):
            validate_material_receipt({"material_claims": [value], "aggregate_result": "VERIFIED"})

    def test_duplicate_claim_ids_fail_before_result_overwrite(self):
        first = claim("exact_sha_role_equality", SHA_A, SHA_A)
        second = dict(first)
        with self.assertRaisesRegex(ActivationError, "ID_DUPLICATE"):
            validate_material_receipt({"material_claims": [first, second], "aggregate_result": "BLOCKED"})


class ControlledGitAdapterTests(unittest.TestCase):
    def _repo(self, root: Path, *, rename=False):
        subprocess.run(["git", "init", "-q"], cwd=root, check=True)
        subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=root, check=True)
        subprocess.run(["git", "config", "user.name", "test"], cwd=root, check=True)
        start = root / ("forbidden/a.txt" if rename else "allowed/a.txt")
        start.parent.mkdir()
        start.write_text("a\n", encoding="utf-8")
        subprocess.run(["git", "add", "."], cwd=root, check=True)
        subprocess.run(["git", "commit", "-qm", "base"], cwd=root, check=True)
        base = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
        if rename:
            (root / "allowed").mkdir()
            subprocess.run(["git", "mv", "forbidden/a.txt", "allowed/a.txt"], cwd=root, check=True)
        else:
            start.write_text("b\n", encoding="utf-8")
        subprocess.run(["git", "commit", "-qam", "candidate"], cwd=root, check=True)
        candidate = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
        return base, candidate

    def test_physical_yaml_resolver_and_git_adapters_verify(self):
        with TemporaryDirectory() as temp:
            repo = Path(temp)
            base, candidate = self._repo(repo)
            spec = {
                "candidate": candidate,
                "base_expectation": {"sha": base, "required_relation": "ancestor_of_candidate"},
                "scope": {"allowed_patterns": ["allowed/**"]},
            }
            (repo / "task.yml").write_text(yaml.safe_dump(spec), encoding="utf-8")
            commit_context = MaterialObservationContext()
            commit_claim = observe_git_commit_claim(
                repo, claim_id="candidate", claim_role="candidate_SHA",
                action_id_or_review_id="action", expected_root=repo,
                expected_source_ref="task.yml#candidate",
                expected_value_path=("candidate",), observation_context=commit_context,
            )
            self.assertEqual(commit_claim["verification_result"], "VERIFIED")
            path_context = MaterialObservationContext()
            path_claim = observe_changed_path_claim(
                repo, claim_id="scope", action_id_or_review_id="action",
                expected_root=repo, expected_source_ref="task.yml#scope",
                expected_value_path=("scope",), base_sha=base, candidate_sha=candidate,
                observation_context=path_context,
            )
            self.assertEqual(path_claim["verification_result"], "VERIFIED")
            self.assertEqual(path_claim["observed_value"]["paths"], ["allowed/a.txt"])
            base_claim = observe_git_base_relation_claim(
                repo, claim_id="base", action_id_or_review_id="action",
                expected_root=repo, expected_source_ref="task.yml#base_expectation",
                expected_value_path=("base_expectation",), base_sha=base,
                candidate_sha=candidate, observation_context=MaterialObservationContext(),
            )
            self.assertEqual(base_claim["verification_result"], "VERIFIED")

            with self.assertRaisesRegex(ActivationError, "BINDING_DUPLICATE"):
                observe_git_commit_claim(
                    repo, claim_id="candidate", claim_role="candidate_SHA",
                    action_id_or_review_id="action", expected_root=repo,
                    expected_source_ref="task.yml#candidate",
                    expected_value_path=("candidate",), observation_context=commit_context,
                )

    def test_complete_compare_does_not_hide_rename_source(self):
        with TemporaryDirectory() as temp:
            repo = Path(temp)
            base, candidate = self._repo(repo, rename=True)
            (repo / "task.yml").write_text("scope:\n  allowed_patterns:\n    - allowed/**\n", encoding="utf-8")
            result = observe_changed_path_claim(
                repo, claim_id="scope", action_id_or_review_id="action",
                expected_root=repo, expected_source_ref="task.yml#scope",
                expected_value_path=("scope",), base_sha=base, candidate_sha=candidate,
                observation_context=MaterialObservationContext(),
            )
            self.assertEqual(result["verification_result"], "MISMATCH")
            self.assertEqual(result["observed_value"]["paths"], ["allowed/a.txt", "forbidden/a.txt"])


if __name__ == "__main__":
    unittest.main()
