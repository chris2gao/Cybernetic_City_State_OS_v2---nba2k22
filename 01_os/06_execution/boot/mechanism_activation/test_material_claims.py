from pathlib import Path
from tempfile import TemporaryDirectory
import subprocess
import unittest

from activation import (
    ActivationError,
    MaterialObservationContext,
    evaluate_material_claim,
    observe_changed_path_claim,
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


def context_for(*claims, binding_overrides=None):
    context = MaterialObservationContext()
    binding_overrides = binding_overrides or {}
    for value in claims:
        override = binding_overrides.get(value["claim_id"], {})
        consumed = {value.get("exact_observation_ref", "")}
        for field in ("subject_principal_observation_ref", "freshness_observation_ref"):
            if value.get(field):
                consumed.add(value[field])
        context.bind(
            claim_id=value["claim_id"],
            expected_source_ref=override.get(
                "expected_source_ref", value.get("expected_claim_source_ref", "missing")
            ),
            expected_value=override.get(
                "expected_value", value.get("expected_value_or_predicate")
            ),
            expected_resolver_id="test_expected_source_fixture",
            observed_source_class=override.get(
                "observed_source_class", value.get("observed_authoritative_source_class", "missing")
            ),
            observed_value=override.get("observed_value", value.get("observed_value")),
            exact_observation_ref=override.get(
                "exact_observation_ref", value.get("exact_observation_ref", "missing")
            ),
            observation_adapter_id="test_physical_observation_fixture",
            consumed_observation_refs=override.get("consumed_observation_refs", consumed),
        )
    return context


def bound_result(value, *, binding_overrides=None):
    return evaluate_material_claim(
        value,
        context_for(value, binding_overrides=binding_overrides),
    )


class MaterialClaimTests(unittest.TestCase):
    def test_real_candidate_and_base_sha_swaps_are_mismatch(self):
        candidate = claim("exact_sha_role_equality", SHA_A, SHA_B)
        self.assertEqual(bound_result(candidate), "MISMATCH")
        base = claim(
            "exact_base_equality_plus_required_relation",
            {"sha": SHA_B, "required_relation": "ancestor_of_candidate"},
            {"sha": SHA_A, "relation_satisfied": True},
            claim_role="base_SHA",
        )
        self.assertEqual(bound_result(base), "MISMATCH")

    def test_authentic_stale_moving_ref_is_stale(self):
        value = claim(
            "named_ref_fresh_state_relation",
            {"sha": SHA_A},
            {"sha": SHA_A, "fresh": False},
            claim_role="moving_head_or_current_ref",
            observed_authoritative_source_class="fresh_remote_Git_ref_readback",
            freshness_requirement_when_applicable="immediately_before_action",
            freshness_observation_ref="git:ls-remote:old-boundary",
        )
        self.assertEqual(bound_result(value), "STALE")
        wrong_named_ref = claim(
            "named_ref_fresh_state_relation",
            {"named_ref": "refs/heads/master", "sha": SHA_A},
            {"named_ref": "refs/heads/task", "sha": SHA_A, "fresh": True},
            claim_role="moving_head_or_current_ref",
            observed_authoritative_source_class="fresh_remote_Git_ref_readback",
        )
        self.assertEqual(bound_result(wrong_named_ref), "MISMATCH")

    def test_integrity_without_semantic_binding_is_mismatch(self):
        value = claim(
            "byte_integrity_and_semantic_role_binding",
            {"sha256": "abc", "candidate_sha": SHA_A, "action_id": "action-001"},
            {"sha256": "abc", "candidate_sha": SHA_B, "action_id": "action-001"},
            claim_role="durable_evidence_artifact",
            observed_authoritative_source_class="Git_blob_at_exact_commit",
        )
        self.assertEqual(bound_result(value), "MISMATCH")

    def test_execution_from_wrong_package_or_candidate_is_mismatch(self):
        expected = {
            "candidate_sha": SHA_A,
            "entrypoint": "tests.py",
            "execution_root": ".",
            "test_package_ref": "frozen-v1",
        }
        observed = dict(expected, test_package_ref="other-real-package")
        value = claim(
            "execution_result_bound_to_expected_candidate_inputs_and_entrypoint",
            expected,
            observed,
            claim_role="execution_or_validation_result",
            observed_authoritative_source_class="trusted_execution_adapter",
        )
        self.assertEqual(bound_result(value), "MISMATCH")

    def test_partial_duplicate_and_noncanonical_path_sets_fail_closed(self):
        expected = {"allowed_patterns": ["allowed/**"]}
        partial = claim(
            "complete_path_set_within_authorized_boundary",
            expected,
            {"paths": ["allowed/a.txt"], "complete": False},
            claim_role="changed_path_and_diff_scope",
            observed_authoritative_source_class="complete_Git_compare",
        )
        self.assertEqual(bound_result(partial), "UNVERIFIABLE")
        duplicate = dict(partial, observed_value={"paths": ["allowed/a.txt", "allowed/a.txt"], "complete": True})
        self.assertEqual(bound_result(duplicate), "AMBIGUOUS")
        noncanonical = dict(partial, observed_value={"paths": ["allowed\\a.txt"], "complete": True})
        self.assertEqual(bound_result(noncanonical), "AMBIGUOUS")
        hidden_forbidden = dict(partial, observed_value={"paths": ["allowed/a.txt", "forbidden.txt"], "complete": True})
        self.assertEqual(bound_result(hidden_forbidden), "MISMATCH")
        loose_pattern = dict(
            partial,
            expected_value_or_predicate={"allowed_patterns": ["allowed/*"]},
            observed_value={"paths": ["allowed/a.txt"], "complete": True},
        )
        self.assertEqual(bound_result(loose_pattern), "AMBIGUOUS")

    def test_actual_authenticated_actor_must_match_authorized_principal(self):
        value = claim(
            "authenticated_actor_satisfies_authorized_principal_binding",
            {"allowed_principals": ["alice"], "task_id": "task-001", "action": "push"},
            {"authenticated_principal": "mallory", "task_id": "task-001", "action": "push"},
            claim_role="authority_and_actual_actor",
            observed_authoritative_source_class="local_authenticated_principal",
            subject_principal_observation_ref="host:principal-observation",
        )
        self.assertEqual(bound_result(value), "MISMATCH")
        endpoint_substitute = dict(value, observed_authoritative_source_class="endpoint_capability_claim")
        self.assertEqual(bound_result(endpoint_substitute), "UNVERIFIABLE")

    def test_observation_cannot_self_assign_role_and_comparator_is_mandatory(self):
        self_assigned = claim(
            "exact_sha_role_equality", SHA_A, SHA_A,
            expected_claim_source_ref="receipt:self-assigned-candidate",
        )
        self.assertEqual(evaluate_material_claim(self_assigned), "UNVERIFIABLE")
        no_comparator = claim("exact_sha_role_equality", SHA_A, SHA_A)
        no_comparator.pop("comparator_id")
        self.assertEqual(bound_result(no_comparator), "UNVERIFIABLE")
        wrong_role = claim(
            "exact_sha_role_equality", SHA_A, SHA_A, claim_role="base_SHA"
        )
        self.assertEqual(bound_result(wrong_role), "UNVERIFIABLE")

    def test_claim_values_cannot_verify_without_trusted_context(self):
        value = claim("exact_sha_role_equality", SHA_A, SHA_A)
        self.assertEqual(evaluate_material_claim(value), "UNVERIFIABLE")

    def test_nonresolving_expected_source_fails_closed(self):
        value = claim("exact_sha_role_equality", SHA_A, SHA_A)
        context = context_for(value, binding_overrides={
            value["claim_id"]: {"expected_source_ref": "different/source.yml#candidate"}
        })
        self.assertEqual(evaluate_material_claim(value, context), "UNVERIFIABLE")

    def test_asserted_complete_diff_requires_consumed_git_compare(self):
        value = claim(
            "complete_path_set_within_authorized_boundary",
            {"allowed_patterns": ["allowed/**"]},
            {"paths": ["allowed/a.txt"], "complete": True},
            claim_role="changed_path_and_diff_scope",
            observed_authoritative_source_class="complete_Git_compare",
            exact_observation_ref="receipt:asserted-complete",
        )
        self.assertEqual(evaluate_material_claim(value), "UNVERIFIABLE")

    def test_asserted_principal_requires_consumed_principal_observation(self):
        value = claim(
            "authenticated_actor_satisfies_authorized_principal_binding",
            {"allowed_principals": ["alice"], "action": "push"},
            {"authenticated_principal": "alice", "action": "push"},
            claim_role="authority_and_actual_actor",
            observed_authoritative_source_class="local_authenticated_principal",
            exact_observation_ref="host:push-principal",
            subject_principal_observation_ref="host:authenticated-principal",
        )
        context = context_for(value, binding_overrides={
            value["claim_id"]: {"consumed_observation_refs": {"host:push-principal"}}
        })
        self.assertEqual(evaluate_material_claim(value, context), "UNVERIFIABLE")

    def test_observation_ref_and_source_class_mismatch_fails_closed(self):
        value = claim("exact_sha_role_equality", SHA_A, SHA_A)
        context = context_for(value, binding_overrides={
            value["claim_id"]: {"observed_source_class": "Git_blob_at_exact_commit"}
        })
        self.assertEqual(evaluate_material_claim(value, context), "UNVERIFIABLE")

    def test_claim_observed_value_must_match_trusted_context(self):
        value = claim("exact_sha_role_equality", SHA_A, SHA_A)
        context = context_for(value, binding_overrides={
            value["claim_id"]: {"observed_value": SHA_B}
        })
        self.assertEqual(evaluate_material_claim(value, context), "MISMATCH")

    def test_receipt_only_correct_looking_observed_value_fails_closed(self):
        value = claim(
            "byte_integrity_and_semantic_role_binding",
            {"sha256": "abc", "role": "evidence"},
            {"sha256": "abc", "role": "evidence"},
            claim_role="durable_evidence_artifact",
            observed_authoritative_source_class="Git_blob_at_exact_commit",
            exact_observation_ref="receipt:prose-only",
        )
        self.assertEqual(evaluate_material_claim(value), "UNVERIFIABLE")

    def test_aggregate_cannot_claim_verified_over_nonverified_subclaim(self):
        first = claim("exact_sha_role_equality", SHA_A, SHA_A)
        first["verification_result"] = "VERIFIED"
        second = claim("exact_sha_role_equality", SHA_A, SHA_B, claim_id="claim-002")
        second["verification_result"] = "MISMATCH"
        with self.assertRaisesRegex(ActivationError, "AGGREGATE_MISMATCH"):
            validate_material_receipt({
                "material_claims": [first, second],
                "aggregate_result": "VERIFIED",
            }, context_for(first, second))

    def test_declared_claim_result_is_recomputed(self):
        value = claim("exact_sha_role_equality", SHA_A, SHA_B)
        value["verification_result"] = "VERIFIED"
        with self.assertRaisesRegex(ActivationError, "DECLARED_RESULT_MISMATCH"):
            validate_material_receipt(
                {"material_claims": [value], "aggregate_result": "VERIFIED"},
                context_for(value),
            )

    def test_duplicate_claim_ids_cannot_overwrite_blocking_result(self):
        first = claim("exact_sha_role_equality", SHA_A, SHA_B)
        first["verification_result"] = "MISMATCH"
        second = claim("exact_sha_role_equality", SHA_A, SHA_A)
        second["verification_result"] = "VERIFIED"
        with self.assertRaisesRegex(ActivationError, "ID_DUPLICATE"):
            validate_material_receipt({
                "material_claims": [first, second],
                "aggregate_result": "VERIFIED",
            }, context_for(first))

    def test_actual_git_observers_bind_commit_and_complete_paths(self):
        with TemporaryDirectory() as temp:
            repo = Path(temp)
            subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
            subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=repo, check=True)
            subprocess.run(["git", "config", "user.name", "test"], cwd=repo, check=True)
            (repo / "allowed").mkdir()
            (repo / "allowed/a.txt").write_text("a\n", encoding="utf-8")
            subprocess.run(["git", "add", "allowed/a.txt"], cwd=repo, check=True)
            subprocess.run(["git", "commit", "-qm", "base"], cwd=repo, check=True)
            base = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()
            (repo / "allowed/a.txt").write_text("b\n", encoding="utf-8")
            subprocess.run(["git", "commit", "-qam", "candidate"], cwd=repo, check=True)
            candidate = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()
            commit_claim = observe_git_commit_claim(
                repo,
                claim_id="candidate",
                claim_role="candidate_SHA",
                action_id_or_review_id="action",
                expected_source_ref="task.yml#candidate",
                expected_sha=candidate,
                observation_context=MaterialObservationContext(),
                expected_resolver_id="test_task_yaml_readback",
            )
            self.assertEqual(commit_claim["verification_result"], "VERIFIED")
            path_context = MaterialObservationContext()
            path_claim = observe_changed_path_claim(
                repo,
                claim_id="scope",
                action_id_or_review_id="action",
                expected_source_ref="task.yml#allowed",
                base_sha=base,
                candidate_sha=candidate,
                allowed_patterns=["allowed/**"],
                observation_context=path_context,
                expected_resolver_id="test_task_yaml_readback",
            )
            self.assertEqual(path_claim["verification_result"], "VERIFIED")
            self.assertEqual(path_claim["observed_value"]["paths"], ["allowed/a.txt"])

    def test_changed_path_observer_does_not_hide_rename_source(self):
        with TemporaryDirectory() as temp:
            repo = Path(temp)
            subprocess.run(["git", "init", "-q"], cwd=repo, check=True)
            subprocess.run(["git", "config", "user.email", "test@example.invalid"], cwd=repo, check=True)
            subprocess.run(["git", "config", "user.name", "test"], cwd=repo, check=True)
            (repo / "forbidden").mkdir()
            (repo / "forbidden/a.txt").write_text("same\n", encoding="utf-8")
            subprocess.run(["git", "add", "forbidden/a.txt"], cwd=repo, check=True)
            subprocess.run(["git", "commit", "-qm", "base"], cwd=repo, check=True)
            base = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()
            (repo / "allowed").mkdir()
            subprocess.run(["git", "mv", "forbidden/a.txt", "allowed/a.txt"], cwd=repo, check=True)
            subprocess.run(["git", "commit", "-qm", "candidate"], cwd=repo, check=True)
            candidate = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=repo, text=True).strip()
            path_claim = observe_changed_path_claim(
                repo,
                claim_id="scope",
                action_id_or_review_id="action",
                expected_source_ref="task.yml#allowed",
                base_sha=base,
                candidate_sha=candidate,
                allowed_patterns=["allowed/**"],
                observation_context=MaterialObservationContext(),
                expected_resolver_id="test_task_yaml_readback",
            )
            self.assertEqual(path_claim["verification_result"], "MISMATCH")
            self.assertEqual(
                path_claim["observed_value"]["paths"],
                ["allowed/a.txt", "forbidden/a.txt"],
            )


if __name__ == "__main__":
    unittest.main()
