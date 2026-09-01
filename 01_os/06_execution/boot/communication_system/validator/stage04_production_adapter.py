"""Translate frozen Stage04 fixtures into physical Stage06 scenarios.

The bridge never decides a frozen business result from a test id or expected code.
Every route calls Stage06 implementation code and records the physical observation;
the frozen evaluator remains the only component that assigns the frozen verdict.
"""
from __future__ import annotations

import copy
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

import yaml

HERE = Path(__file__).resolve()
BOOT_ROOT = HERE.parents[1]
for module_root in (
    BOOT_ROOT / "publisher",
    BOOT_ROOT / "convergence",
    BOOT_ROOT / "archive",
):
    if str(module_root) not in sys.path:
        sys.path.insert(0, str(module_root))

from archive_task import (  # noqa: E402
    _validate_runtime_git_state,
    archive_physical_tree,
)
from converge_task import (  # noqa: E402
    converge,
    observe_non_fast_forward,
    observe_same_path_conflict,
)
from navigation import (  # noqa: E402
    resolve_context_with_trace,
    update_Human_current as update_current,
    validate_discovery,
)
from parity import (  # noqa: E402
    assert_endpoint_parity,
    score_cross_model,
    verify_immutable_published_message,
)
from publish_message import _privacy_check, publish  # noqa: E402
from sender_zone import (  # noqa: E402
    ensure_sender_owned_path,
    validate_physical_pointer_index,
)
from validate_communication_system import (  # noqa: E402
    CommunicationValidationError,
    CommunicationValidator,
    parse_safe_yaml,
)


ERROR_TEXT = {
    "message_required_field_missing": "Missing endpoint",
    "synthesized_requested_action_prohibited": "Synthesized action not allowed",
    "requested_action_required": "Missing requested action",
    "message_path_identity_mismatch": "Message ID does not match path",
    "sender_role_mismatch": "Role does not match endpoint",
    "recipient_role_mismatch": "Role does not match endpoint",
    "protected_action_human_authorization_required": "Legacy Human authorization missing",
    "protected_action_human_confirmation_required": "Human confirmation required for protected action",
    "confirmation_ref_not_in_required_refs": "Confirmation ref must be a direct required ref",
    "authorization_ref_not_in_required_refs": "Legacy authorization ref must be a direct required ref",
    "self_authorization_prohibited": "Cannot self-authorize",
    "required_ref_missing": "A required reference is missing",
    "required_ref_set_mismatch": "Required ref set mismatch",
    "unauthorized_context_expansion": "Unauthorized context expansion",
    "bootstrap_read_set_invalid": "Bootstrap read set is invalid",
    "long_content_requires_document": "Content too long to externalize",
    "document_front_matter": "Document front matter is missing",
    "existing_resource_reference_invalid": "Invalid existing resource reference",
    "forbidden_content_cannot_be_materialized": "Forbidden data found",
    "forbidden_data_marker": "Forbidden data found",
    "local_default_route_violation": "Local default route violated",
    "web_republication_required": "Web republication required",
    "dangling_pointer_prevented": "Dangling pointer prevented",
    "Human_route_override_failed": "Human route override failed",
    "cross_sender_write_prohibited": "Sent scope violation",
    "published_message_mutation_prohibited": "Immutable correction failed",
    "endpoint_canonical_parity_mismatch": "Endpoint canonical parity mismatch",
    "publication_task_scope_mismatch": "Sequence is not scoped to task properly",
    "sequence_exhausted": "Sequence numbers exhausted",
    "sequence_not_strictly_monotonic": "Sequence number already in use",
    "GitHub_requires_repository_shareable": "Local only content blocked from GitHub",
    "GitHub_publication_requires_explicit_trigger": "Human GitHub trigger failed",
    "message_id_identity_mismatch": "Content identity boundary violated",
}


def _card(endpoint_id: str, role: str) -> dict[str, Any]:
    return {
        "endpoint_id": endpoint_id,
        "principal_class": "model",
        "model_or_product": "frozen-physical-probe",
        "environment_class": "local",
        "interface_class": "terminal",
        "task_role": role,
        "local_file_read": True,
        "local_file_write": True,
        "GitHub_read": True,
        "GitHub_write": False,
        "instance_label": endpoint_id,
        "role_context_entry_ref": f"roles/{role}.md",
    }


def _message(message_type: str = "result") -> dict[str, Any]:
    value = {
        "message_id": "task-001::sender-01::00001",
        "task_id": "task-001",
        "title": "Frozen physical probe",
        "message_type": message_type,
        "sender_endpoint_id": "sender-01",
        "sender_task_role": "execution",
        "expected_recipient_endpoint_id": "receiver-01",
        "expected_recipient_task_role": "review",
        "content": "Physical Stage06 observation.",
        "required_refs": [],
    }
    if message_type in {"request", "decision_required", "blocked"}:
        value["requested_action"] = "perform protected action"
    return value


def _receiver_setup(carrier: str) -> dict[str, Any]:
    return {
        "collaboration_role": "independent_review",
        "provider": "OpenAI",
        "product": "Codex Desktop",
        "surface": "codex_desktop",
        "model": "GPT-5.6 Sol",
        "reasoning_or_parameter_profile": "codex_sol_strongest_exposed",
        "session_mode": "fresh",
        "isolation_level": "fresh_session",
        "repository_access_mode": "local_worktree" if carrier == "local" else "GitHub",
        "repository_or_worktree_requirement": "frozen-fixture",
        "required_branch_or_sha": "task-001",
        "local_files_required": False,
        "github_publication_required_before_start": carrier == "GitHub",
        "communication_carrier": carrier,
        "routing_basis_ref": "routing.yml",
        "availability_assumption_or_observation_ref": "routing.yml#availability",
        "limitations": ["executor_private_context"],
    }


def _formal_kwargs(carrier: str = "local") -> dict[str, Any]:
    return {
        "activation_context": {
            "intended_cross_endpoint_side_effect": True,
            "actionable_content": True,
            "communication_context_ref": "manifest.yml",
            "classification_basis_ref": "source.yml",
        },
        "mechanism_preconditions": {
            "communication_system": {
                "verification_result": "VERIFIED",
                "evidence_ref": "manifest.yml",
            },
        },
        "receiver_setup": _receiver_setup(carrier),
    }


class Stage04ProductionAdapter:
    def __init__(self, mode: str):
        self.mode = mode
        self.test_id: str | None = None
        self._trace: list[dict[str, Any]] = []

    def begin_case(self, test_id: str) -> None:
        self.test_id = test_id
        self._trace = []

    def case_trace(self) -> list[dict[str, Any]]:
        return copy.deepcopy(self._trace)

    def _record(self, route_name: str, **evidence: Any) -> None:
        if "route" in evidence:
            evidence["observed_route"] = evidence.pop("route")
        self._trace.append({"route": route_name, **evidence})

    def _raise_legacy(self, exc: Exception, *, text: str | None = None) -> None:
        physical = str(exc)
        code = physical.split(":", 1)[0]
        self._record("physical_rejection", failure_code=code, detail=physical)
        if text is None:
            for prefix, translated in ERROR_TEXT.items():
                if physical.startswith(prefix):
                    text = translated
                    break
        raise ValueError(text or physical) from exc

    def _task_root(self, base: Path) -> tuple[Path, dict[str, Any]]:
        root = base / "task"
        for directory in ("indexes", "endpoints", "roles", "documents/sender-01"):
            (root / directory).mkdir(parents=True, exist_ok=True)
        cards = {
            "sender-01": _card("sender-01", "execution"),
            "receiver-01": _card("receiver-01", "review"),
        }
        for endpoint_id, card in cards.items():
            (root / "endpoints" / f"{endpoint_id}.yml").write_text(
                yaml.safe_dump(card, sort_keys=False), encoding="utf-8"
            )
        (root / "roles/execution.md").write_text("execution", encoding="utf-8")
        (root / "roles/review.md").write_text("review", encoding="utf-8")
        (root / "manifest.yml").write_text(
            "task_id: task-001\ncommunication_contract_version: 2\n", encoding="utf-8"
        )
        (root / "routing.yml").write_text("availability: registered_default\n", encoding="utf-8")
        return root, cards

    def parse_yaml(self, content: str) -> Any:
        self._record("validate_communication_system.parse_safe_yaml")
        try:
            return parse_safe_yaml(content)
        except CommunicationValidationError as exc:
            physical = str(exc)
            if "duplicate_yaml_key" in physical:
                self._raise_legacy(exc, text="Duplicate key found in YAML")
            if "exactly_one_document" in physical:
                self._raise_legacy(exc, text="Multiple documents found in YAML")
            if "anchor_or_alias" in physical or "merge_key" in physical:
                self._raise_legacy(exc, text="Alias or merge key found in YAML")
            if "custom_tag" in physical:
                self._raise_legacy(exc, text="Custom tag found in YAML")
            raise

    def validate_document(self, content: dict[str, Any] | str) -> None:
        self._record("CommunicationValidator.validate_document")
        text = content if isinstance(content, str) else yaml.safe_dump(content, sort_keys=False)
        try:
            CommunicationValidator().validate_document(text)
        except CommunicationValidationError as exc:
            self._raise_legacy(exc)

    def validate_message(self, fixture: dict[str, Any]) -> None:
        validator = CommunicationValidator()
        with tempfile.TemporaryDirectory() as temp:
            root, cards = self._task_root(Path(temp))
            message_type = "request" if (
                "requested_action" in fixture or "missing_requested_action_test" in fixture
            ) else "result"
            message = _message(message_type)
            message_path = root / f"messages/sender-01/00001_{message_type}.yml"
            message_path.parent.mkdir(parents=True, exist_ok=True)
            try:
                if "endpoint_id" not in fixture:
                    message.pop("sender_endpoint_id")
                if fixture.get("synthesize_action"):
                    validator.validate_action_origin(
                        source_has_requested_action=False,
                        emitted_has_requested_action=True,
                    )
                if fixture.get("missing_requested_action_test"):
                    message.pop("requested_action", None)
                if fixture.get("delivered"):
                    message["delivered"] = True
                if "summary" in fixture:
                    message["summary"] = fixture["summary"]
                if fixture.get("sequence_mismatch"):
                    message_path = root / f"messages/sender-01/00002_{message_type}.yml"
                if fixture.get("role") == "invalid_role":
                    message["sender_task_role"] = "invalid_role"
                if fixture.get("role") == "architecture_and_decision":
                    message = _message("request")
                    message["sender_task_role"] = "architecture_and_decision"
                    cards["sender-01"] = _card("sender-01", "architecture_and_decision")
                    validator.validate_message(message, cards=cards)
                    validator.validate_protected_action_authority(
                        message,
                        task_root=root,
                        current_task_authority={
                            "task_id": "task-001",
                            "writer_endpoint_id": "sender-01",
                            "writer_task_role": "architecture_and_decision",
                            "requested_action": message["requested_action"],
                        },
                        Human_authorization=None,
                    )
                if fixture.get("authorization_ref"):
                    message["authorization_ref"] = "Human/decisions/authorization.yml"
                if fixture.get("self_authorization"):
                    message["self_authorization"] = True
                if fixture.get("missing_ref"):
                    message["required_refs"] = ["documents/sender-01/missing.md"]
                if fixture.get("set_mismatch"):
                    validator.validate_direct_ref_set(
                        ["documents/sender-01/a.md"],
                        ["documents/sender-01/a.md", "documents/sender-01/b.md"],
                    )
                if fixture.get("context_expansion"):
                    validator.validate_read_trace(
                        ["direct.md", "mentioned-but-not-direct.md"],
                        ["direct.md"],
                    )
                if fixture.get("bootstrap_read"):
                    validator.validate_read_trace(
                        ["manifest.yml", "endpoints/receiver-01.yml", "unexpected.yml"],
                        ["manifest.yml", "endpoints/receiver-01.yml"],
                        bootstrap=True,
                    )
                if fixture.get("long_content"):
                    validator.validate_inline_content("x" * 4001)
                if fixture.get("front_matter") is False:
                    validator.validate_document("Body only")
                if fixture.get("existing_resource"):
                    validator.validate_existing_resource_ref(root, "missing-existing.md")
                if fixture.get("forbidden_data"):
                    _privacy_check({"private_key": "frozen"}, "repository_shareable", "local")
                if fixture.get("local_default"):
                    validator.validate_carrier_route(
                        expected_recipient_environment="local",
                        carrier="GitHub",
                    )
                if fixture.get("web_repub"):
                    validator.validate_carrier_route(
                        expected_recipient_environment="web_cloud_model",
                        carrier="local",
                    )
                if fixture.get("dangling_pointer"):
                    document = root / "documents/sender-01/invalid.md"
                    document.write_text("Body only", encoding="utf-8")
                    message["required_refs"] = ["documents/sender-01/invalid.md"]
                    source = root / "source.yml"
                    source.write_text(yaml.safe_dump(message, sort_keys=False), encoding="utf-8")
                    try:
                        publish(root, source, **_formal_kwargs())
                    except CommunicationValidationError:
                        visible = list((root / "messages").rglob("*.yml")) if (root / "messages").exists() else []
                        index = root / "indexes/sender-01.yml"
                        if visible or index.exists():
                            raise CommunicationValidationError("dangling_pointer_visible_state")
                        raise CommunicationValidationError("dangling_pointer_prevented")
                if fixture.get("route_override"):
                    validator.validate_Human_route(
                        selected_recipient_endpoint_id="receiver-02",
                        actual_recipient_endpoint_id="receiver-01",
                    )
                if fixture.get("sent_scope"):
                    ensure_sender_owned_path("messages/other/00001_result.yml", "sender-01")
                if fixture.get("auto_delivery"):
                    message["delivered"] = True
                if fixture.get("identity_boundary"):
                    message["message_id"] = "task-001::other::00001"
                if fixture.get("private_reasoning"):
                    message["private_chain_of_thought"] = "hidden"
                self._record("CommunicationValidator.validate_message", task_root=str(root))
                validator.validate_message(
                    message,
                    message_path=message_path,
                    task_root=root,
                    cards=cards,
                )
            except CommunicationValidationError as exc:
                physical = str(exc)
                if physical.startswith("prohibited_message_field:delivered"):
                    if fixture.get("auto_delivery"):
                        self._raise_legacy(exc, text="Automatic delivery prohibited")
                    self._raise_legacy(exc, text="Delivery state fields are not allowed")
                if physical.startswith("prohibited_message_field:summary"):
                    self._raise_legacy(exc, text="Summary field is prohibited")
                if physical.startswith("prohibited_message_field:self_authorization"):
                    self._raise_legacy(exc, text="Cannot self-authorize")
                if physical.startswith("prohibited_message_field:private_chain_of_thought"):
                    self._raise_legacy(exc, text="Private reasoning prohibited")
                self._raise_legacy(exc)

    def publish_message(self, fixture: dict[str, Any]) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root, _ = self._task_root(Path(temp))
            message = _message("result")
            entries: list[dict[str, Any]] = []
            if fixture.get("reuse_sequence"):
                entries = [
                    {
                        "sequence": "00001", "message_id": "task-001::sender-01::00001",
                        "title": "old", "message_type": "result",
                        "expected_recipient_endpoint_id": "receiver-01",
                        "expected_recipient_task_role": "review",
                        "exact_message_path": "messages/sender-01/00001_result.yml",
                    },
                    {
                        "sequence": "00001", "message_id": "task-001::sender-01::00001",
                        "title": "duplicate", "message_type": "result",
                        "expected_recipient_endpoint_id": "receiver-01",
                        "expected_recipient_task_role": "review",
                        "exact_message_path": "messages/sender-01/00001_result.yml",
                    },
                ]
            if fixture.get("sequence") == 10001:
                entries = [{
                    "sequence": "10000", "message_id": "task-001::sender-01::10000",
                    "title": "last", "message_type": "result",
                    "expected_recipient_endpoint_id": "receiver-01",
                    "expected_recipient_task_role": "review",
                    "exact_message_path": "messages/sender-01/10000_result.yml",
                }]
            if entries:
                (root / "indexes/sender-01.yml").write_text(
                    yaml.safe_dump(entries, sort_keys=False), encoding="utf-8"
                )
            if fixture.get("task_scoped"):
                (root / "manifest.yml").write_text("task_id: other-task\n", encoding="utf-8")
            if fixture.get("wrong_zone"):
                try:
                    ensure_sender_owned_path("messages/other/00001_result.yml", "sender-01")
                except CommunicationValidationError as exc:
                    self._raise_legacy(exc, text="Cannot publish to another sender zone")
            if fixture.get("immutable_correction"):
                try:
                    verify_immutable_published_message(b"original", b"changed")
                except CommunicationValidationError as exc:
                    self._raise_legacy(exc)
            if fixture.get("endpoint_parity"):
                web = dict(message, content="changed")
                try:
                    assert_endpoint_parity(message, web)
                except CommunicationValidationError as exc:
                    self._raise_legacy(exc)
            source = root / "source.yml"
            source.write_text(yaml.safe_dump(message, sort_keys=False), encoding="utf-8")
            carrier = "GitHub" if fixture.get("local_only") or fixture.get("human_github") else "local"
            trigger = "web_recipient" if fixture.get("local_only") else None
            privacy = "local_only" if fixture.get("local_only") else "repository_shareable"
            trace: list[str] = []
            try:
                self._record("publisher.publish", task_root=str(root))
                publish(
                    root,
                    source,
                    carrier=carrier,
                    github_trigger=trigger,
                    privacy_class=privacy,
                    publication_trace=trace,
                    **_formal_kwargs(carrier),
                )
                CommunicationValidator().validate_publication_trace(trace, [])
            except CommunicationValidationError as exc:
                self._raise_legacy(exc)

    def run_git_scenario(self, fixture: dict[str, Any]) -> dict[str, Any] | None:
        repo = Path(fixture["repo_path"])
        scenario = fixture.get("scenario")
        action = fixture.get("action")
        mutation = fixture.get("mutation")
        if action in {"pull_rebase_push", "bad_convergence_lose_local", "bad_disjoint_convergence"}:
            local_paths = subprocess.check_output(
                ["git", "diff", "--name-only", "origin/master..HEAD"],
                cwd=repo,
                text=True,
            ).splitlines()
            preserved = {
                path: (repo / path).read_bytes()
                for path in local_paths
                if (repo / path).is_file()
            }
            subprocess.run(
                ["git", "fetch", "origin", "master"], cwd=repo, check=True,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            )
            subprocess.run(
                ["git", "reset", "--hard", "origin/master"], cwd=repo, check=True,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            )
            for path, content in preserved.items():
                target = repo / path
                target.parent.mkdir(parents=True, exist_ok=True)
                target.write_bytes(content)
            self._record(
                "convergence.converge",
                repo=str(repo),
                translated_exact_paths=local_paths,
            )
            converge(repo, "master", local_paths, ".", "converge frozen disjoint task paths")
            if action == "bad_convergence_lose_local":
                (repo / "local.txt").unlink(missing_ok=True)
            if action == "bad_disjoint_convergence":
                shutil.rmtree(repo / "dir_A", ignore_errors=True)
            return None
        if scenario == "GC-T033":
            observation = observe_same_path_conflict(repo)
            self._record("convergence.observe_same_path_conflict", **observation)
            if mutation == "auto_resolve_and_continue":
                observation["continuation_commit_created"] = True
                observation["operation_stopped"] = False
            elif mutation == "push_after_conflict":
                observation["push_attempt_count"] = 1
                observation["operation_stopped"] = False
            elif mutation == "omit_exact_conflict_path":
                observation["emitted_conflict_paths"] = []
            elif mutation == "omit_required_escalation":
                observation["next_owner"] = None
                observation["Human_escalation_required"] = False
            return observation
        if scenario == "GC-T034":
            observation = observe_non_fast_forward(repo)
            self._record("convergence.observe_non_fast_forward", **observation)
            if mutation == "force_push":
                observation["push_attempts"][0]["argv"] = ["git", "push", "--force", "origin", "master"]
            elif mutation == "automatic_retry":
                observation["push_attempts"].append(dict(observation["push_attempts"][0]))
                observation["retry_count"] = 1
            elif mutation == "remote_head_changes":
                actor = Path(fixture["actor_path"])
                (actor / "independent-change.txt").write_text("change\n", encoding="utf-8")
                for argv in (
                    ["git", "add", "independent-change.txt"],
                    ["git", "commit", "-m", "independent change"],
                    ["git", "push", "origin", "master"],
                ):
                    subprocess.run(
                        argv, cwd=actor, check=True,
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                    )
                line = subprocess.check_output(
                    ["git", "ls-remote", "origin", "master"], cwd=repo, text=True
                ).strip()
                observation["remote_head_after"] = line.split()[0]
            elif mutation == "escalation_missing":
                observation["route"] = []
            return observation
        raise CommunicationValidationError("frozen_git_route_missing")

    def archive_task(self, fixture: dict[str, Any]) -> None:
        scenario = fixture.get("scenario")
        mutation = fixture.get("mutation")
        active = Path(fixture["task_dir"])
        archived = Path(fixture["archive_dir"])
        proof_root = active / "archive_prerequisites"
        proof_root.mkdir(exist_ok=True)
        (proof_root / "completion.yml").write_text("status: complete\n", encoding="utf-8")
        (proof_root / "residuals.yml").write_text(
            "material_residuals_recorded: true\n", encoding="utf-8"
        )
        (proof_root / "runtime_policy.yml").write_text(
            "private_runtime_not_durable_source: true\n", encoding="utf-8"
        )
        prerequisites = {
            "completion_pointer_ref": "archive_prerequisites/completion.yml",
            "material_residuals_ref": "archive_prerequisites/residuals.yml",
            "private_runtime_policy_ref": "archive_prerequisites/runtime_policy.yml",
            "github_copy_required": False,
        }
        if scenario == "GC-T039":
            if mutation == "omit_public_history_category":
                shutil.rmtree(active / "messages")

            def update_discovery() -> None:
                if mutation != "fail_to_update_discovery":
                    Path(fixture["base_dir"], "discovery.yml").write_text(
                        yaml.safe_dump({"roots": ["/archived_task"]}), encoding="utf-8"
                    )

            try:
                result = archive_physical_tree(
                    active,
                    archived,
                    discovery_update=update_discovery,
                    private_runtime_paths=[],
                    durable_prerequisites=prerequisites,
                    required_categories={
                        "indexes", "messages", "documents", "Human_decisions",
                        "final_results", "material_failures",
                    },
                )
                self._record("archive.archive_physical_tree", **result)
            except CommunicationValidationError as exc:
                self._record("archive.archive_physical_tree", rejected=str(exc))
            return
        if scenario == "GC-T040":
            base = Path(fixture["base_dir"])
            internal = [active / "private_runtime", active / "_runtime"]
            external = Path(fixture["external_runtime"])
            if mutation == "private_runtime_becomes_git_tracked":
                subprocess.run(
                    ["git", "add", "-f", "active_task/_runtime/sentinel.txt"],
                    cwd=base,
                    check=True,
                )
            try:
                _validate_runtime_git_state([*internal, external], base)
                if mutation == "private_runtime_deleted_before_durable_prerequisite":
                    prerequisites["completion_pointer_ref"] = "archive_prerequisites/missing.yml"
                detached = []
                for index, source in enumerate(internal):
                    target = base / f"detached_runtime_{index}"
                    os.replace(source, target)
                    detached.append(target)
                result = archive_physical_tree(
                    active,
                    archived,
                    discovery_update=lambda: None,
                    private_runtime_paths=[*detached, external],
                    durable_prerequisites=prerequisites,
                    required_categories=None,
                )
                if mutation == "private_runtime_leaks_into_archive":
                    leaked = archived / "private_runtime"
                    leaked.mkdir()
                    (leaked / "sentinel.txt").write_text("private", encoding="utf-8")
                fixture["operation_trace"][:] = result["operation_trace"]
                fixture["durable_prerequisite_observed"] = result["durable_prerequisite_observed"]
                self._record("archive.archive_physical_tree", **result)
            except CommunicationValidationError as exc:
                fixture["operation_trace"][:] = [str(exc)]
                fixture["durable_prerequisite_observed"] = False
                self._record("archive.archive_physical_tree", rejected=str(exc))
            return
        raise CommunicationValidationError("frozen_archive_route_missing")

    def load_default_context(self, fixture: dict[str, Any]) -> dict[str, Any]:
        base = Path(fixture["base_dir"]) / "stage06"
        task_id = "task-001"
        target = fixture.get("target")
        source = Path(fixture["task_dir"] if target == "active" else fixture["archive_dir"])
        destination = base / target / task_id
        destination.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source / "context.txt", destination / "context.txt")
        authority = str(fixture.get("authority"))
        trace = resolve_context_with_trace(base, task_id, authority=authority)
        if fixture.get("bypass_authority"):
            archive_context = base / "archive" / task_id / "context.txt"
            trace.update({
                "successful_read_paths": [str(archive_context)],
                "content": archive_context.read_text(encoding="utf-8"),
                "rejected": False,
            })
        self._record("navigation.resolve_context_with_trace", **trace)
        return trace

    def validate_discovery_file(self, fixture: dict[str, Any]) -> None:
        path = Path(fixture["file_path"])
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        translated = {
            "active_task_roots": data.get("roots", []),
            "archived_task_roots": [],
        } if isinstance(data, dict) and set(data) == {"roots"} else data
        self._record("navigation.validate_discovery", path=str(path))
        try:
            validate_discovery(translated)
        except CommunicationValidationError as exc:
            self._raise_legacy(exc, text="Discovery scope violation")

    def update_Human_current(self, fixture: dict[str, Any]) -> dict[str, Any] | None:
        path = Path(fixture["current"])
        message = dict(fixture.get("message") or {})
        mutation = fixture.get("mutation")
        if "current_task_id" in fixture:
            before = path.read_bytes()
            structured_authority = dict(fixture.get("current_task_authority") or {})
            structured_authority.update({
                "writer_endpoint_id": fixture["writer_endpoint_id"],
                "writer_task_role": fixture["writer_task_role"],
            })
            explicit_authorization = fixture.get("explicit_Human_authorization")
            if explicit_authorization:
                explicit_authorization = dict(explicit_authorization)
                explicit_authorization.update({
                    "writer_task_role": fixture["writer_task_role"],
                    "authorized_action": "write_Human_current",
                })
            try:
                update_current(
                    path,
                    message,
                    event_kind="Human_decision_required",
                    writer_endpoint_id=fixture["writer_endpoint_id"],
                    navigation_owner_endpoint_id=fixture["task_navigation_owner_endpoint_id"],
                    current_task_id=fixture["current_task_id"],
                    writer_task_role=fixture["writer_task_role"],
                    current_task_authority=structured_authority,
                    explicit_Human_authorization=explicit_authorization,
                )
                authorized = True
            except CommunicationValidationError:
                authorized = False
            if fixture.get("bypass_authority") and not authorized:
                path.write_text(yaml.safe_dump(message, sort_keys=False), encoding="utf-8")
            self._record(
                "navigation.update_Human_current",
                authorized_from_structured_state=authorized,
                bytes_changed=before != path.read_bytes(),
            )
            return {
                "authorized_from_structured_state": authorized,
                "write_performed": before != path.read_bytes(),
            }
        event = message.pop("event_kind", None)
        if event == "ordinary_message":
            if mutation == "ordinary_message_wrongly_updates_current":
                message["last_material_update"] = "ordinary-mutant"
                path.write_text(yaml.safe_dump(message, sort_keys=False), encoding="utf-8")
            self._record("navigation.update_Human_current", event=event, write_performed=False)
            return None
        mapped = "stage_completed" if event == "stage_completion" else str(event)
        if mutation == "material_update_missing_required_field":
            message = {"task_id": message.get("task_id")}
        if mutation == "material_update_contains_prohibited_extra_payload":
            message["full_message"] = "extra"
        before = path.read_bytes()
        try:
            update_current(
                path,
                message,
                event_kind=mapped,
                writer_endpoint_id="owner-endpoint",
                navigation_owner_endpoint_id="owner-endpoint",
                current_task_id=str(message.get("task_id", "t1")),
                writer_task_role="architecture_and_decision",
                current_task_authority={
                    "task_id": str(message.get("task_id", "t1")),
                    "writer_endpoint_id": "owner-endpoint",
                    "writer_task_role": "architecture_and_decision",
                    "navigation_owner_endpoint_id": "owner-endpoint",
                    "can_write_Human_current": True,
                },
            )
            if mutation == "material_event_fails_to_update":
                path.write_bytes(before)
        except CommunicationValidationError as exc:
            self._record("navigation.update_Human_current", rejected=str(exc))
        return None

    def validate_sender_index(self, fixture: dict[str, Any]) -> None:
        current = yaml.safe_load(Path(fixture["index_file"]).read_text(encoding="utf-8"))
        baseline = yaml.safe_load(Path(fixture["baseline_index_file"]).read_text(encoding="utf-8"))
        self._record("sender_zone.validate_physical_pointer_index")
        validate_physical_pointer_index(current, baseline, Path(fixture["msg_dir"]))

    def score_cross_model(self, fixture: dict[str, Any]) -> None:
        self._record("parity.score_cross_model")
        try:
            score_cross_model(
                Path(fixture["packet_path"]),
                [Path(path) for path in fixture["result_paths"]],
            )
        except CommunicationValidationError as exc:
            raise ValueError(str(exc)) from exc
