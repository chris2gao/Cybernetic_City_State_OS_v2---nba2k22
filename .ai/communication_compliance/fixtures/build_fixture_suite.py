"""Deterministically build release-bound Human-AI compliance fixtures."""

from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[3]
FIXTURES = Path(__file__).resolve().parent
ARTIFACTS = FIXTURES / "artifacts"
RAW = FIXTURES / "raw"
SUITE_PATH = FIXTURES / "fixture_suite.json"
INHERITED_COVERAGE_PATH = (
    ROOT / ".ai" / "communication_compliance" / "inherited_fixture_coverage_map.json"
)
POLICY_PATH = ROOT / ".ai" / "communication_compliance" / "material_event_policy.yml"
PARENT_CANDIDATE = "e6ca76bce8849f3a7a8bc498f66bfbd767aa4d0d"
LEGACY_SUITE_HEAD = "4530b4f684f64cc7928884cf96d9a221aa5a2b8a"
TASK_ID = "human-ai-communication-compliance-fixture"
TASK_REF = ".ai/CODEX_TASK_INPUT_CONTRACT.md"
PROTOCOL_REF = ".ai/PROTOCOL.md"

POLICY = yaml.safe_load(POLICY_PATH.read_text(encoding="utf-8"))
SOURCE_BASE = POLICY["source_mailbox_base_head"]
RELEASE = POLICY["protocol_release_head"]
if POLICY.get("release_binding_status") != "bound" or not isinstance(RELEASE, str):
    raise RuntimeError("protocol release head must be bound before fixture generation")

ROLE_MAP = {
    "ChatGPT": ("foreground_review_and_task_dispatch", "chatgpt_to_codex_v1"),
    "Claude": ("foreground_review_and_task_dispatch", "chatgpt_to_codex_v1"),
    "Codex": ("backend_execution_and_handoff", "codex_to_chatgpt_v1"),
    "Claude Code": ("backend_execution_and_handoff", "codex_to_chatgpt_v1"),
}
ALWAYS_LOADED_PATHS = POLICY["bootstrap_required_loaded_files"]
PREFLIGHT_FIELDS = [
    "factual_status_grounded",
    "required_refs_dereferenced",
    "canonical_pointer_present_when_applicable",
    "execution_recommendation_present_when_dispatching",
    "independent_expression_present_for_material_event",
    "independent_expression_separated_from_authority",
    "no_long_task_or_report_echo",
    "no_hidden_chain_of_thought_request_or_disclosure",
]
ONBOARDING_FIELDS = [
    "repository_and_source_state",
    "role_and_authority",
    "always_loaded_files",
    "inherited_on_demand_files",
    "workflow_state_and_signal",
    "non_null_refs",
    "human_gate",
    "next_action_and_response_shape",
    "communication_channels",
    "execution_recommendation",
    "independent_expression",
    "expression_preservation",
    "expression_authority_boundary",
    "drift_correction",
    "role_and_wire_schema",
    "mixed_recipient_resolution",
    "bootstrap_receipt_capability_boundary",
    "c2_external_authority_origin",
]


def gate_module() -> Any:
    path = ROOT / ".ai" / "communication_compliance" / "validate_communication.py"
    spec = importlib.util.spec_from_file_location("fixture_gate", path)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load communication validator")
    gate = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(gate)
    return gate


def git_show(path: str, head: str = RELEASE) -> bytes:
    completed = subprocess.run(
        ["git", "-C", str(ROOT), "show", f"{head}:{path}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(f"cannot resolve {head}:{path}")
    return completed.stdout


def sha256(content: bytes) -> str:
    return hashlib.sha256(content).hexdigest()


def git_ref(path: str, head: str = RELEASE) -> dict[str, Any]:
    return {
        "kind": "git_blob",
        "commit": head,
        "path": path,
        "content_sha256": sha256(git_show(path, head)),
    }


def fixture_ref(path: str) -> dict[str, Any]:
    return {
        "kind": "test_fixture_blob",
        "path": path,
        "content_sha256": sha256((ROOT / path).read_bytes()),
        "test_only": True,
    }


def write_json(path: Path, value: Any, *, sort_keys: bool = True) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=sort_keys) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def receipt(provider: str, head: str = RELEASE) -> dict[str, Any]:
    role, wire = ROLE_MAP[provider]
    role_paths = POLICY["bootstrap_on_demand_requirements"].get(role, [])
    loaded_paths = list(dict.fromkeys(ALWAYS_LOADED_PATHS + role_paths))
    return {
        "schema_version": "human_ai.communication_bootstrap_receipt.v1",
        "receipt_id": "fixture-receipt-" + provider.lower().replace(" ", "-"),
        "protocol_release_head": head,
        "provider": provider,
        "occupied_role": role,
        "wire_schema": wire,
        "loaded_files": [
            {"commit": head, "path": path, "content_sha256": sha256(git_show(path, head))}
            for path in loaded_paths
        ],
        "inherited_on_demand": [
            {"path": path, "trigger": "role/load-profile routing", "loaded": True}
            for path in role_paths
        ] + [
            {"path": ".ai/LONG_RUN_AUTONOMOUS_PROGRAM_PROTOCOL.md", "trigger": "separate long run", "loaded": False},
        ],
        "authority_boundary": {
            "receipt_is_authorization": False,
            "protected_actions_need_external_human": True,
        },
        "onboarding_answers": {field: True for field in ONBOARDING_FIELDS},
    }


def recommendation() -> dict[str, Any]:
    return {
        "recommended_model": "runtime_dependent",
        "recommended_thinking_level": "xhigh",
        "mode": "goal",
        "subagents": "not_applicable",
        "task_ref_or_plan_ref": TASK_REF,
        "short_complexity_rationale": "deterministic material-event fixture",
        "human_gate": "not_required",
    }


def human_content(*, dispatch: bool, text: str | None = None) -> dict[str, Any]:
    return {
        "factual_status": "The durable fixture binds physical evidence before a state transition.",
        "execution_recommendation": recommendation() if dispatch else None,
        "preflight": {field: True for field in PREFLIGHT_FIELDS},
        "independent_expression": {
            "heading": "Independent expression",
            "text": text or "Physical evidence makes omissions visible. It never grants protected authority.",
            "separated_from_authority": True,
        },
    }


def pointer(provider: str) -> dict[str, Any]:
    _role, wire = ROLE_MAP[provider]
    if wire == "chatgpt_to_codex_v1":
        data = {
            "signal_id": "fixture-signal",
            "decision": "start_task",
            "task_ref": TASK_REF,
            "packet_ref": None,
            "brief_ref": None,
            "source_head": SOURCE_BASE,
            "human_gate": "approved_to_start_implementation",
        }
    else:
        data = {
            "packet_id": "fixture-packet",
            "status": "awaiting_chatgpt_review",
            "report_ref": PROTOCOL_REF,
            "brief_ref": None,
            "source_head": SOURCE_BASE,
            "review_branch_head": RELEASE,
            "human_gate": "not_required",
        }
    return {"wire_schema": wire, "data": data, "extra_text": ""}


def event(
    provider: str,
    event_id: str,
    event_type: str,
    event_class: str,
    *,
    dispatch: bool,
    transition: dict[str, Any] | None = None,
    recipient_mode: str = "mixed_separable",
) -> dict[str, Any]:
    role, _wire = ROLE_MAP[provider]
    refs = [git_ref(PROTOCOL_REF)]
    if dispatch or provider in {"ChatGPT", "Claude"}:
        refs.append(git_ref(TASK_REF))
    return {
        "schema_version": "human_ai.communication_event.v1",
        "event_id": event_id,
        "task_id": TASK_ID,
        "event_type": event_type,
        "claimed_event_class": event_class,
        "provider": provider,
        "occupied_role": role,
        "bootstrap_receipt": receipt(provider),
        "pointer": None if recipient_mode == "human_only" else pointer(provider),
        "required_refs": refs,
        "communication": {
            "recipient_mode": recipient_mode,
            "channels_separated": recipient_mode == "mixed_separable",
            "human_pointer_only_waiver": False,
            "human_operational": human_content(dispatch=dispatch),
            "brief_artifact_ref": None,
        },
        "proposed_transition": transition,
        "descriptive_human_gate": "descriptive_only",
    }


def human_event(base: dict[str, Any], event_id: str, *, human_only: bool = False) -> dict[str, Any]:
    result = copy.deepcopy(base)
    result["event_id"] = event_id
    result["provider"] = "Human"
    result["occupied_role"] = "human_speaker"
    result["bootstrap_receipt"] = None
    if human_only:
        result["pointer"] = None
        result["communication"]["recipient_mode"] = "human_only"
        result["communication"]["channels_separated"] = False
    return result


def case(case_id: str, operation: str, *, payload: Any = None, result: str = "pass", codes: list[str] | None = None, **extra: Any) -> dict[str, Any]:
    item = {
        "id": case_id,
        "operation": operation,
        "expected_result": result,
        "expected_exit_code": 0 if result == "pass" else (3 if result == "error" else 1),
        "expected_violation_codes": codes or [],
    }
    if payload is not None:
        item["payload"] = payload
    item.update(extra)
    return item


def transition_bundle(case_id: str, payload: dict[str, Any], status: str, *, active_task: str | None = TASK_ID, validation: bool = False, pointer_override: Any = None) -> tuple[dict[str, Any], dict[str, Any]]:
    relative = f".ai/communication_compliance/fixtures/artifacts/proof/{case_id}"
    event_path = f"{relative}/event.json"
    state_path = f"{relative}/state.json"
    pointer_path = f"{relative}/pointer.json"
    validation_path = f"{relative}/validation.json"
    write_json(ROOT / event_path, payload, sort_keys=False)
    if status in {"idle", "neutral_baseline"} and active_task == TASK_ID:
        active_task = None
    state = {
        "protocol_version": "fixture-v2",
        "status": status,
        "active_task": active_task,
        "source_head": SOURCE_BASE,
        "review_branch": "ai/review/latest",
        "review_branch_head": "self",
        "next_expected_actor": "fixture",
    }
    write_json(ROOT / state_path, state, sort_keys=False)
    actual_pointer = payload.get("pointer") if pointer_override is None else pointer_override
    if actual_pointer is not None:
        write_json(ROOT / pointer_path, actual_pointer, sort_keys=False)
    request = {
        "schema_version": "human_ai.communication_transition_request.v2",
        "request_id": "fixture-request-" + case_id,
        "event_ref": fixture_ref(event_path),
        "state_ref": fixture_ref(state_path),
        "pointer_ref": fixture_ref(pointer_path) if actual_pointer is not None else None,
        "validation_artifact_ref": None,
    }
    if validation:
        gate = gate_module()
        policy, policy_sha = gate.load_policy(POLICY_PATH)
        fresh = gate.validate_event(payload, ROOT, policy, policy_sha, test_mode=True)
        write_json(ROOT / validation_path, fresh)
        request["validation_artifact_ref"] = fixture_ref(validation_path)
    context = {
        "schema_version": "human_ai.communication_active_state_context.v1",
        "context_id": "fixture-state-" + case_id,
        "injection_source": "deterministic_test_fixture",
        "test_only": True,
        "review_branch": "ai/review/latest",
        "observed_head": RELEASE,
        "state_path": state_path,
    }
    return request, context


def authority_context() -> dict[str, Any]:
    return {
        "schema_version": "human_ai.communication_authorization_context.v3",
        "context_id": "fixture-authority",
        "injection_source": "deterministic_test_fixture",
        "test_only": True,
        "issuer": "Human",
        "decision": "allow",
        "task_id": "AUTO_TASK_ID",
        "event_id": "AUTO_EVENT_ID",
        "transition_id": "AUTO_TRANSITION_ID",
        "action": "AUTO_ACTION",
        "target": "AUTO_TARGET",
        "protocol_release_head": "AUTO_PROTOCOL_RELEASE_HEAD",
        "event_input_sha256": "AUTO_EVENT_INPUT_SHA256",
        "actor_origin_context_id": "AUTO_ACTOR_ORIGIN_CONTEXT_ID",
        "actor_origin_context_sha256": "AUTO_ACTOR_ORIGIN_CONTEXT_SHA256",
        "revoked": False,
        "replay_protected": True,
    }


def actor_origin_context() -> dict[str, Any]:
    return {
        "schema_version": "human_ai.communication_actor_origin_context.v2",
        "context_id": "AUTO_ORIGIN_CONTEXT_ID",
        "injection_source": "deterministic_test_fixture",
        "test_only": True,
        "provider": "AUTO_PROVIDER",
        "occupied_role": "AUTO_OCCUPIED_ROLE",
        "event_id": "AUTO_EVENT_ID",
        "task_id": "AUTO_TASK_ID",
        "transition_id": "AUTO_TRANSITION_ID",
        "protocol_release_head": "AUTO_PROTOCOL_RELEASE_HEAD",
        "event_input_sha256": "AUTO_EVENT_INPUT_SHA256",
        "authenticated_channel": True,
        "replay_protected": True,
    }


def drift_record(record_id: str, violation_class: str, prior: list[dict[str, Any]], *, fixture: dict[str, Any] | None = None) -> dict[str, Any]:
    gate = gate_module()
    occurrence = sum(1 for item in prior if item["violation_class"] == violation_class) + 1
    record = {
        "schema_version": "human_ai.communication_drift_record.v2",
        "sequence": len(prior) + 1,
        "record_id": record_id,
        "previous_record_sha256": prior[-1]["record_sha256"] if prior else None,
        "record_sha256": "0" * 64,
        "violation_class": violation_class,
        "occurrence_count": occurrence,
        "detection": "deterministic fixture detection",
        "correction_status": "corrected",
        "repository_work_preserved": True,
        "root_cause": "fixture root cause",
        "preventive_action": "fixture preventive action",
        "regression_fixture_ref": fixture,
        "deterministic_fixture_impossible_reason": None,
        "foreground_review_required": False,
        "foreground_review_ref": None,
        "contains_private_reasoning": False,
        "contains_secret_content": False,
    }
    record["record_sha256"] = gate.digest_object(
        {key: value for key, value in record.items() if key != "record_sha256"},
        preserve_mapping_order=False,
    )
    return record


def immutable_parent_case(case_id: str) -> dict[str, Any]:
    gate = gate_module()
    suite_bytes = git_show(".ai/communication_compliance/fixtures/fixture_suite.json", PARENT_CANDIDATE)
    suite = json.loads(suite_bytes)
    matches = [item for item in suite["cases"] if item.get("id") == case_id]
    if len(matches) != 1:
        raise RuntimeError("parent case is not unique")
    return {
        "suite_ref": {
            "kind": "git_blob",
            "commit": PARENT_CANDIDATE,
            "path": ".ai/communication_compliance/fixtures/fixture_suite.json",
            "content_sha256": sha256(suite_bytes),
        },
        "case_id": case_id,
        "case_sha256": gate.digest_object(matches[0], preserve_mapping_order=False),
    }


def rehash(records: list[dict[str, Any]]) -> list[dict[str, Any]]:
    gate = gate_module()
    result: list[dict[str, Any]] = []
    counts: dict[str, int] = {}
    for index, original in enumerate(records, 1):
        item = copy.deepcopy(original)
        item["sequence"] = index
        item["previous_record_sha256"] = result[-1]["record_sha256"] if result else None
        counts[item["violation_class"]] = counts.get(item["violation_class"], 0) + 1
        item["occurrence_count"] = counts[item["violation_class"]]
        item["record_sha256"] = gate.digest_object(
            {key: value for key, value in item.items() if key != "record_sha256"},
            preserve_mapping_order=False,
        )
        result.append(item)
    return result


def add_transition(cases: list[dict[str, Any]], case_id: str, payload: dict[str, Any], status: str, *, result: str = "pass", codes: list[str] | None = None, active_task: str | None = TASK_ID, validation: bool = False, authority: dict[str, Any] | None = None, origin: dict[str, Any] | None = None, include_origin: bool = True, consumed_actor_origin_context_ids: list[str] | None = None, pointer_override: Any = None) -> tuple[dict[str, Any], dict[str, Any]]:
    request, context = transition_bundle(case_id, payload, status, active_task=active_task, validation=validation, pointer_override=pointer_override)
    if include_origin and origin is None:
        origin = actor_origin_context()
    cases.append(
        case(
            case_id,
            "transition",
            result=result,
            codes=codes,
            request=request,
            active_state_context=context,
            state_context_mode="test-fixture",
            authorization_context=authority,
            authority_mode="test-fixture" if authority else "none",
            actor_origin_context=origin,
            actor_origin_mode="test-fixture" if origin else "none",
            consumed_actor_origin_context_ids=consumed_actor_origin_context_ids or [],
        )
    )
    return request, context


def write_raw_parser_fixtures() -> None:
    RAW.mkdir(parents=True, exist_ok=True)
    (RAW / "pointer_duplicate_keys.yml").write_text("signal_id: one\nsignal_id: two\n", encoding="utf-8", newline="\n")
    (RAW / "pointer_multidoc.yml").write_text("---\nsignal_id: one\n---\nsignal_id: two\n", encoding="utf-8", newline="\n")
    (RAW / "pointer_anchor_alias.yml").write_text("signal_id: &x one\ndecision: *x\n", encoding="utf-8", newline="\n")


def migrate_inherited_cases(cases: list[dict[str, Any]]) -> list[dict[str, Any]]:
    coverage = json.loads(INHERITED_COVERAGE_PATH.read_text(encoding="utf-8"))
    by_id = {item["id"]: item for item in cases}
    if len(by_id) != len(cases):
        raise RuntimeError("base fixture case identifiers are not unique")
    migrated: list[dict[str, Any]] = []
    for mapping in coverage["mappings"]:
        template_id = mapping["template_case_id"]
        if template_id not in by_id:
            raise RuntimeError(f"coverage template is missing: {template_id}")
        item = copy.deepcopy(by_id[template_id])
        item["id"] = mapping["current_case_id"]
        migrated.append(item)
    if len({item["id"] for item in migrated}) != len(migrated):
        raise RuntimeError("migrated fixture case identifiers are not unique")
    return cases + migrated


def build_cases() -> list[dict[str, Any]]:
    cases: list[dict[str, Any]] = []
    cases.append(case("classify_c0_ordinary", "classify", event_type="ordinary_discussion"))
    cases.append(case("classify_unknown_fail_closed", "classify", result="fail", codes=["UNKNOWN_EVENT_TYPE"], event_type="future_unknown_transition"))
    for provider in ROLE_MAP:
        cases.append(case("bootstrap_" + provider.lower().replace(" ", "_") + "_pass", "validate_bootstrap", payload=receipt(provider)))
    cases.append(case("bootstrap_stale_release_head", "validate_bootstrap", payload=receipt("ChatGPT", SOURCE_BASE), result="fail", codes=["BOOTSTRAP_PROTOCOL_HEAD_STALE"]))
    wrong_wire = receipt("ChatGPT")
    wrong_wire["wire_schema"] = "codex_to_chatgpt_v1"
    cases.append(case("bootstrap_wrong_wire", "validate_bootstrap", payload=wrong_wire, result="fail", codes=["BOOTSTRAP_RECEIPT_SCHEMA_INVALID"]))
    loaded_digest = receipt("ChatGPT")
    loaded_digest["loaded_files"][0]["content_sha256"] = "0" * 64
    cases.append(case("bootstrap_loaded_file_digest_mismatch", "validate_bootstrap", payload=loaded_digest, result="fail", codes=["BOOTSTRAP_REFERENCE_DIGEST_MISMATCH"]))
    loaded_head = receipt("ChatGPT")
    protocol_loaded = next(item for item in loaded_head["loaded_files"] if item["path"] == PROTOCOL_REF)
    protocol_loaded["commit"] = SOURCE_BASE
    protocol_loaded["content_sha256"] = sha256(git_show(PROTOCOL_REF, SOURCE_BASE))
    cases.append(case("bootstrap_loaded_file_head_mismatch", "validate_bootstrap", payload=loaded_head, result="fail", codes=["BOOTSTRAP_LOADED_FILE_HEAD_MISMATCH"]))

    c0_project = {
        "schema_version": "human_ai.communication_event.v1",
        "event_id": "c0-project-mention",
        "task_id": TASK_ID,
        "event_type": "ordinary_discussion",
        "claimed_event_class": "C0",
        "provider": "Human",
    }
    cases.append(case("c0_project_mention_pass", "validate_event", payload=c0_project))
    c0_transition = copy.deepcopy(c0_project)
    c0_transition["event_id"] = "c0-transition-forbidden"
    c0_transition["proposed_transition"] = {"transition_id": "dispatch_to_backend"}
    cases.append(case("c0_transition_fail_closed", "validate_event", payload=c0_transition, result="fail", codes=["C0_TRANSITION_FORBIDDEN"]))

    dispatch_transition = {"transition_id": "dispatch_to_backend", "from_state": "idle", "to_state": "awaiting_codex"}
    completion_transition = {"transition_id": "backend_completion", "from_state": "awaiting_codex", "to_state": "awaiting_chatgpt_review"}
    revision_transition = {"transition_id": "foreground_revision_dispatch", "from_state": "awaiting_chatgpt_review", "to_state": "awaiting_codex"}
    acceptance_transition = {"transition_id": "foreground_acceptance", "from_state": "awaiting_chatgpt_review", "to_state": "completed"}
    candidate_transition = {"transition_id": "publication_candidate", "from_state": "awaiting_chatgpt_review", "to_state": "awaiting_human_gate"}
    protected_transition = {"transition_id": "protected_publication_entry", "from_state": "awaiting_human_gate", "to_state": "publication_authorized_in_progress"}

    dispatch = event("ChatGPT", "dispatch", "backend_dispatch", "C1", dispatch=True, transition=dispatch_transition)
    completion = event("Codex", "completion", "completion_handoff", "C1", dispatch=False, transition=completion_transition)
    revision = event("ChatGPT", "revision", "backend_dispatch", "C1", dispatch=True, transition=revision_transition)
    acceptance = event("ChatGPT", "acceptance", "significant_acceptance", "C1", dispatch=False, transition=acceptance_transition)
    candidate = event("ChatGPT", "candidate", "significant_acceptance", "C1", dispatch=False, transition=candidate_transition)
    protected = event("ChatGPT", "protected", "source_publication", "C2", dispatch=False, transition=protected_transition)
    for identifier, payload in (("event_dispatch_pass", dispatch), ("event_completion_pass", completion), ("event_revision_pass", revision), ("event_acceptance_pass", acceptance), ("event_candidate_pass", candidate), ("event_protected_pass", protected)):
        cases.append(case(identifier, "validate_event", payload=payload))
    claude_dispatch = event("Claude", "claude-dispatch", "backend_dispatch", "C1", dispatch=True, transition=dispatch_transition)
    claude_code_completion = event("Claude Code", "claude-code-completion", "completion_handoff", "C1", dispatch=False, transition=completion_transition)
    material_review = event("ChatGPT", "material-review", "material_review", "C1", dispatch=False)
    cases.append(case("event_claude_dispatch_pass", "validate_event", payload=claude_dispatch))
    cases.append(case("event_claude_code_completion_pass", "validate_event", payload=claude_code_completion))
    cases.append(case("event_material_review_no_dispatch_pass", "validate_event", payload=material_review))

    pointer_prose = copy.deepcopy(dispatch)
    pointer_prose["event_id"] = "pointer-prose"
    pointer_prose["pointer"]["extra_text"] = "contamination"
    cases.append(case("pointer_extra_prose", "validate_event", payload=pointer_prose, result="fail", codes=["POINTER_PROSE_CONTAMINATION"]))
    pointer_order = copy.deepcopy(dispatch)
    pointer_order["event_id"] = "pointer-order"
    pointer_order["pointer"]["data"] = dict(reversed(list(pointer_order["pointer"]["data"].items())))
    cases.append(case("pointer_key_order_invalid", "validate_event", payload=pointer_order, result="fail", codes=["POINTER_KEY_ORDER_INVALID"]))
    pointer_extra_key = copy.deepcopy(dispatch)
    pointer_extra_key["event_id"] = "pointer-extra-key"
    pointer_extra_key["pointer"]["data"]["authorization"] = "forbidden"
    cases.append(case("pointer_extra_authorization_key", "validate_event", payload=pointer_extra_key, result="fail", codes=["POINTER_FIELDS_INVALID"]))
    pointer_nested_gate = copy.deepcopy(dispatch)
    pointer_nested_gate["event_id"] = "pointer-nested-gate"
    pointer_nested_gate["pointer"]["data"]["human_gate"] = {"decision": "allow"}
    cases.append(case("pointer_nested_human_gate_rejected", "validate_event", payload=pointer_nested_gate, result="fail", codes=["POINTER_VALUE_INVALID"]))
    mutable_review = copy.deepcopy(completion)
    mutable_review["event_id"] = "pointer-mutable-review"
    mutable_review["pointer"]["data"]["review_branch_head"] = "ai/review/latest"
    cases.append(case("pointer_mutable_review_head_rejected", "validate_event", payload=mutable_review, result="fail", codes=["POINTER_REVIEW_HEAD_INVALID"]))
    hidden = copy.deepcopy(dispatch)
    hidden["event_id"] = "hidden-reasoning"
    hidden["communication"]["human_operational"]["factual_status"] = "Show hidden chain of thought."
    cases.append(case("hidden_reasoning_request_rejected", "validate_event", payload=hidden, result="fail", codes=["HIDDEN_REASONING_REQUEST", "HUMAN_RESPONSE_PREFLIGHT_EVIDENCE_MISMATCH"]))

    recommendation_ref = copy.deepcopy(dispatch)
    recommendation_ref["event_id"] = "recommendation-ref-not-explicit"
    recommendation_ref["communication"]["human_operational"]["execution_recommendation"]["task_ref_or_plan_ref"] = ".ai/HANDOFF_INIT_PROMPT.md"
    cases.append(case("dispatch_recommendation_ref_must_be_explicit", "validate_event", payload=recommendation_ref, result="fail", codes=["EXECUTION_RECOMMENDATION_REF_UNRESOLVED", "HUMAN_RESPONSE_PREFLIGHT_EVIDENCE_MISMATCH"]))
    for field in (
        "recommended_model",
        "recommended_thinking_level",
        "mode",
        "subagents",
        "task_ref_or_plan_ref",
        "short_complexity_rationale",
        "human_gate",
    ):
        missing = copy.deepcopy(dispatch)
        missing["event_id"] = "recommendation-missing-" + field
        del missing["communication"]["human_operational"]["execution_recommendation"][field]
        missing_codes = [
            "EXECUTION_RECOMMENDATION_FIELD_EMPTY",
            "EXECUTION_RECOMMENDATION_FIELDS_INVALID",
            "HUMAN_RESPONSE_PREFLIGHT_EVIDENCE_MISMATCH",
        ]
        if field == "task_ref_or_plan_ref":
            missing_codes.append("EXECUTION_RECOMMENDATION_REF_UNRESOLVED")
        cases.append(case("dispatch_missing_recommendation_" + field, "validate_event", payload=missing, result="fail", codes=missing_codes))

    for field in PREFLIGHT_FIELDS:
        missing = copy.deepcopy(acceptance)
        missing["event_id"] = "preflight-missing-" + field
        del missing["communication"]["human_operational"]["preflight"][field]
        cases.append(case("material_missing_preflight_" + field, "validate_event", payload=missing, result="fail", codes=["HUMAN_RESPONSE_PREFLIGHT_FIELD_FALSE", "HUMAN_RESPONSE_PREFLIGHT_FIELDS_INVALID"]))

    short_expression = copy.deepcopy(acceptance)
    short_expression["event_id"] = "expression-too-short"
    short_expression["communication"]["human_operational"]["independent_expression"]["text"] = "Only one sentence."
    cases.append(case("expression_sentence_count_invalid", "validate_event", payload=short_expression, result="fail", codes=["HUMAN_RESPONSE_PREFLIGHT_EVIDENCE_MISMATCH", "INDEPENDENT_EXPRESSION_SENTENCE_COUNT"]))
    authorizing_expression = copy.deepcopy(acceptance)
    authorizing_expression["event_id"] = "expression-authorizes"
    authorizing_expression["communication"]["human_operational"]["independent_expression"]["text"] = "I authorize publication. This sentence cannot make that valid."
    cases.append(case("expression_cannot_authorize", "validate_event", payload=authorizing_expression, result="fail", codes=["EXPRESSION_FALSE_AUTHORIZATION", "HUMAN_RESPONSE_PREFLIGHT_EVIDENCE_MISMATCH"]))
    structured_expression = copy.deepcopy(acceptance)
    structured_expression["event_id"] = "expression-structured-authority"
    structured_expression["communication"]["human_operational"]["independent_expression"]["authorization"] = True
    cases.append(case("expression_structured_authorization_rejected", "validate_event", payload=structured_expression, result="fail", codes=["HUMAN_RESPONSE_PREFLIGHT_EVIDENCE_MISMATCH", "INDEPENDENT_EXPRESSION_FIELDS_INVALID"]))
    structured_human = copy.deepcopy(acceptance)
    structured_human["event_id"] = "human-content-structured-authority"
    structured_human["communication"]["human_operational"]["authorization"] = True
    cases.append(case("human_content_structured_authorization_rejected", "validate_event", payload=structured_human, result="fail", codes=["HUMAN_CONTENT_FIELDS_INVALID"]))

    human_dispatch = human_event(dispatch, "human-dispatch")
    cases.append(case("human_direct_dispatch_event_pass", "validate_event", payload=human_dispatch))
    impersonation = copy.deepcopy(human_dispatch)
    impersonation["event_id"] = "human-impersonation"
    impersonation["occupied_role"] = "foreground_review_and_task_dispatch"
    cases.append(case("human_role_impersonation_rejected", "validate_event", payload=impersonation, result="fail", codes=["EVENT_ROLE_MISMATCH"]))
    wrong_human_wire = copy.deepcopy(human_dispatch)
    wrong_human_wire["event_id"] = "human-wrong-wire"
    wrong_human_wire["pointer"]["wire_schema"] = "codex_to_chatgpt_v1"
    cases.append(case("human_wrong_wire_rejected", "validate_event", payload=wrong_human_wire, result="fail", codes=["POINTER_WIRE_SCHEMA_MISMATCH"]))

    complete_dispatch_path = ".ai/communication_compliance/fixtures/artifacts/complete_dispatch_brief.md"
    incomplete_dispatch_path = ".ai/communication_compliance/fixtures/artifacts/incomplete_dispatch_brief.md"
    complete_dispatch_ref = git_ref(complete_dispatch_path)
    incomplete_dispatch_ref = git_ref(incomplete_dispatch_path)
    nonseparable = copy.deepcopy(dispatch)
    nonseparable["event_id"] = "mixed-nonseparable-complete"
    nonseparable["required_refs"].append(complete_dispatch_ref)
    nonseparable["communication"].update({
        "recipient_mode": "mixed_nonseparable",
        "channels_separated": False,
        "human_operational": None,
        "brief_artifact_ref": complete_dispatch_ref,
    })
    nonseparable["pointer"]["data"]["brief_ref"] = complete_dispatch_path
    cases.append(case("mixed_nonseparable_complete_brief_pass", "validate_event", payload=nonseparable))
    waiver_complete = copy.deepcopy(nonseparable)
    waiver_complete["event_id"] = "mixed-waiver-complete"
    waiver_complete["communication"]["recipient_mode"] = "mixed_separable"
    waiver_complete["communication"]["channels_separated"] = True
    waiver_complete["communication"]["human_pointer_only_waiver"] = True
    cases.append(case("mixed_pointer_only_waiver_complete_brief_pass", "validate_event", payload=waiver_complete))
    incomplete = copy.deepcopy(nonseparable)
    incomplete["event_id"] = "mixed-nonseparable-incomplete"
    incomplete["required_refs"][-1] = incomplete_dispatch_ref
    incomplete["communication"]["brief_artifact_ref"] = incomplete_dispatch_ref
    incomplete["pointer"]["data"]["brief_ref"] = incomplete_dispatch_path
    cases.append(case("mixed_nonseparable_incomplete_brief", "validate_event", payload=incomplete, result="fail", codes=["EXECUTION_RECOMMENDATION_REQUIRED", "HUMAN_RESPONSE_PREFLIGHT_EVIDENCE_MISMATCH", "INDEPENDENT_EXPRESSION_REQUIRED"]))
    missing_brief = copy.deepcopy(dispatch)
    missing_brief["event_id"] = "pointer-waiver-missing-brief"
    missing_brief["communication"]["human_pointer_only_waiver"] = True
    missing_brief["communication"]["human_operational"] = None
    missing_brief["communication"]["brief_artifact_ref"] = {
        "path": ".ai/communication_compliance/fixtures/artifacts/missing-brief.md"
    }
    missing_brief["pointer"]["data"]["brief_ref"] = None
    cases.append(case("pointer_only_waiver_missing_brief", "validate_event", payload=missing_brief, result="fail", codes=["DURABLE_BRIEF_FALLBACK_UNRESOLVED", "HUMAN_CONTENT_REQUIRED", "POINTER_BRIEF_REF_MISMATCH"]))

    dispatch_step = add_transition(cases, "transition_dispatch_pass", dispatch, "idle")
    accepted_dispatch = copy.deepcopy(dispatch)
    accepted_dispatch["proposed_transition"]["from_state"] = "accepted_closed"
    add_transition(cases, "transition_exact_validation_artifact_pass", accepted_dispatch, "accepted_closed", active_task=None, validation=True)
    completion_step = add_transition(cases, "transition_completion_pass", completion, "awaiting_codex")
    revision_step = add_transition(cases, "transition_revision_loop_pass", revision, "awaiting_chatgpt_review")
    completion_two = copy.deepcopy(completion)
    completion_two["event_id"] = "completion-two"
    completion_two_step = add_transition(cases, "transition_completion_two_pass", completion_two, "awaiting_codex")
    acceptance_step = add_transition(cases, "transition_acceptance_pass", acceptance, "awaiting_chatgpt_review")
    add_transition(cases, "transition_candidate_pass", candidate, "awaiting_chatgpt_review")
    add_transition(cases, "transition_c2_no_authority", protected, "awaiting_human_gate", result="fail", codes=["AUTHENTICATED_HUMAN_AUTHORITY_UNAVAILABLE"])
    accepted_protected = copy.deepcopy(protected)
    accepted_protected["proposed_transition"]["from_state"] = "accepted_awaiting_human_publication_gate"
    add_transition(cases, "transition_c2_authority_pass", accepted_protected, "accepted_awaiting_human_publication_gate", authority=authority_context())
    completed_human_dispatch = copy.deepcopy(human_dispatch)
    completed_human_dispatch["proposed_transition"]["from_state"] = "completed"
    add_transition(cases, "transition_human_dispatch_pass", completed_human_dispatch, "completed", active_task=None, origin=actor_origin_context())
    add_transition(cases, "transition_human_origin_missing", copy.deepcopy(human_dispatch), "idle", active_task=None, include_origin=False, result="fail", codes=["ACTOR_ORIGIN_ATTESTATION_REQUIRED", "ACTOR_ORIGIN_CONTEXT_SCHEMA_INVALID"])
    human_c2 = human_event(protected, "human-c2", human_only=True)
    add_transition(cases, "transition_human_c2_no_authority", human_c2, "awaiting_human_gate", origin=actor_origin_context(), result="fail", codes=["AUTHENTICATED_HUMAN_AUTHORITY_UNAVAILABLE"])

    human_acceptance = human_event(acceptance, "human-acceptance", human_only=True)
    add_transition(cases, "transition_human_acceptance_pass", human_acceptance, "awaiting_chatgpt_review")
    backend_acceptance = event("Codex", "backend-self-acceptance", "significant_acceptance", "C1", dispatch=False, transition=acceptance_transition)
    add_transition(cases, "transition_backend_self_acceptance_rejected", backend_acceptance, "awaiting_chatgpt_review", result="fail", codes=["TRANSITION_ACTOR_ROLE_FORBIDDEN"])
    backend_material_review = event("Codex", "backend-material-review-close", "material_review", "C1", dispatch=False, transition=acceptance_transition)
    add_transition(cases, "transition_backend_material_review_close_rejected", backend_material_review, "awaiting_chatgpt_review", result="fail", codes=["TRANSITION_ACTOR_ROLE_FORBIDDEN"])
    backend_candidate = event("Claude Code", "backend-publication-candidate", "material_review", "C1", dispatch=False, transition=candidate_transition)
    add_transition(cases, "transition_backend_publication_candidate_rejected", backend_candidate, "awaiting_chatgpt_review", result="fail", codes=["TRANSITION_ACTOR_ROLE_FORBIDDEN"])
    foreground_completion = event("ChatGPT", "foreground-self-completion", "completion_handoff", "C1", dispatch=False, transition=completion_transition)
    add_transition(cases, "transition_foreground_self_completion_rejected", foreground_completion, "awaiting_codex", result="fail", codes=["TRANSITION_ACTOR_ROLE_FORBIDDEN"])
    human_completion = human_event(foreground_completion, "human-self-completion", human_only=True)
    add_transition(cases, "transition_human_self_completion_rejected", human_completion, "awaiting_codex", result="fail", codes=["TRANSITION_ACTOR_ROLE_FORBIDDEN"])
    role_impersonation = copy.deepcopy(dispatch)
    role_impersonation["event_id"] = "transition-role-impersonation"
    role_impersonation["occupied_role"] = "backend_execution_and_handoff"
    add_transition(cases, "transition_provider_role_edge_mismatch_rejected", role_impersonation, "idle", result="fail", codes=["FRESH_EVENT_VALIDATION_FAILED", "TRANSITION_ACTOR_ROLE_FORBIDDEN"])

    add_transition(cases, "transition_model_origin_missing", copy.deepcopy(dispatch), "idle", include_origin=False, result="fail", codes=["ACTOR_ORIGIN_ATTESTATION_REQUIRED", "ACTOR_ORIGIN_CONTEXT_SCHEMA_INVALID"])
    wrong_origin_provider = actor_origin_context()
    wrong_origin_provider["provider"] = "Codex"
    add_transition(cases, "transition_actor_origin_wrong_provider", copy.deepcopy(dispatch), "idle", origin=wrong_origin_provider, result="fail", codes=["ACTOR_ORIGIN_BINDING_MISMATCH"])
    wrong_origin_role = actor_origin_context()
    wrong_origin_role["occupied_role"] = "backend_execution_and_handoff"
    add_transition(cases, "transition_actor_origin_wrong_role", copy.deepcopy(dispatch), "idle", origin=wrong_origin_role, result="fail", codes=["ACTOR_ORIGIN_BINDING_MISMATCH"])
    wrong_origin_transition = actor_origin_context()
    wrong_origin_transition["transition_id"] = "foreground_acceptance"
    add_transition(cases, "transition_actor_origin_wrong_transition", copy.deepcopy(dispatch), "idle", origin=wrong_origin_transition, result="fail", codes=["ACTOR_ORIGIN_BINDING_MISMATCH"])
    wrong_origin_digest = actor_origin_context()
    wrong_origin_digest["event_input_sha256"] = "0" * 64
    add_transition(cases, "transition_actor_origin_event_digest_transplant", copy.deepcopy(dispatch), "idle", origin=wrong_origin_digest, result="fail", codes=["ACTOR_ORIGIN_BINDING_MISMATCH"])
    cross_event_origin = actor_origin_context()
    cross_event_origin["event_id"] = "another-event"
    add_transition(cases, "transition_actor_origin_cross_event_transplant", copy.deepcopy(dispatch), "idle", origin=cross_event_origin, result="fail", codes=["ACTOR_ORIGIN_BINDING_MISMATCH"])
    replay_origin = actor_origin_context()
    add_transition(cases, "transition_actor_origin_replay", copy.deepcopy(dispatch), "idle", origin=replay_origin, consumed_actor_origin_context_ids=["fixture-actor-origin-dispatch"], result="fail", codes=["ACTOR_ORIGIN_CONTEXT_REPLAYED"])
    forged_origin = actor_origin_context()
    forged_origin["injection_source"] = "trusted_external_host"
    forged_origin["test_only"] = False
    origin_request, origin_state = transition_bundle("transition-actor-origin-forged-host", copy.deepcopy(dispatch), "idle")
    cases.append(case("transition_actor_origin_forged_trusted_context", "transition", result="fail", codes=["ACTOR_ORIGIN_ATTESTATION_REQUIRED"], request=origin_request, active_state_context=origin_state, state_context_mode="test-fixture", actor_origin_context=forged_origin, actor_origin_mode="trusted-host"))

    wrong_authority_digest = authority_context()
    wrong_authority_digest["event_input_sha256"] = "0" * 64
    add_transition(cases, "transition_c2_authority_event_digest_mismatch", copy.deepcopy(protected), "awaiting_human_gate", authority=wrong_authority_digest, result="fail", codes=["AUTHORITY_CONTEXT_BINDING_MISMATCH"])
    cross_actor_authority = authority_context()
    cross_actor_authority["actor_origin_context_id"] = "another-actor-origin"
    cross_actor_authority["actor_origin_context_sha256"] = "0" * 64
    add_transition(cases, "transition_c2_authority_cross_actor_transplant", copy.deepcopy(protected), "awaiting_human_gate", authority=cross_actor_authority, result="fail", codes=["AUTHORITY_CONTEXT_BINDING_MISMATCH"])

    wrong_task_request, wrong_task_context = transition_bundle("transition-state-task-mismatch", completion, "awaiting_codex", active_task="wrong-task")
    cases.append(case("transition_state_task_mismatch", "transition", result="fail", codes=["STATE_TASK_BINDING_MISMATCH"], request=wrong_task_request, active_state_context=wrong_task_context, state_context_mode="test-fixture", actor_origin_context=actor_origin_context(), actor_origin_mode="test-fixture"))
    unreachable_request, unreachable_context = transition_bundle("transition-unreachable", dispatch, "awaiting_codex")
    cases.append(case("transition_unreachable", "transition", result="fail", codes=["TRANSITION_FROM_STATE_EVIDENCE_MISMATCH", "TRANSITION_UNREACHABLE"], request=unreachable_request, active_state_context=unreachable_context, state_context_mode="test-fixture", actor_origin_context=actor_origin_context(), actor_origin_mode="test-fixture"))
    claim_request, claim_context = transition_bundle("transition-claim-forgery", dispatch, "idle")
    claim_request["claimed_event_id"] = "forged"
    cases.append(case("transition_claim_forgery", "transition", result="fail", codes=["TRANSITION_CLAIM_BINDING_MISMATCH"], request=claim_request, active_state_context=claim_context, state_context_mode="test-fixture", actor_origin_context=actor_origin_context(), actor_origin_mode="test-fixture"))
    bad_pointer = copy.deepcopy(dispatch["pointer"])
    bad_pointer["data"]["decision"] = "forged"
    pointer_request, pointer_context = transition_bundle("transition-pointer-binding", dispatch, "idle", pointer_override=bad_pointer)
    cases.append(case("transition_pointer_binding", "transition", result="fail", codes=["POINTER_ARTIFACT_BINDING_MISMATCH", "POINTER_ARTIFACT_BYTE_MISMATCH"], request=pointer_request, active_state_context=pointer_context, state_context_mode="test-fixture", actor_origin_context=actor_origin_context(), actor_origin_mode="test-fixture"))

    mutated_request, mutated_context = transition_bundle("transition-event-mutation", copy.deepcopy(dispatch), "idle", validation=True)
    event_path = ROOT / mutated_request["event_ref"]["path"]
    mutated = json.loads(event_path.read_text(encoding="utf-8"))
    mutated["descriptive_human_gate"] = "mutated-after-validation"
    write_json(event_path, mutated, sort_keys=False)
    mutated_request["event_ref"] = fixture_ref(mutated_request["event_ref"]["path"])
    cases.append(case("transition_event_mutation_after_result", "transition", result="fail", codes=["VALIDATION_ARTIFACT_BYTE_MISMATCH", "VALIDATION_ARTIFACT_SEMANTIC_MISMATCH"], request=mutated_request, active_state_context=mutated_context, state_context_mode="test-fixture", actor_origin_context=actor_origin_context(), actor_origin_mode="test-fixture"))
    forged_event = copy.deepcopy(dispatch)
    forged_event["event_id"] = "forged-resolved-status-event"
    forged_event["required_refs"][0] = {
        "kind": "test_fixture_blob",
        "path": ".ai/communication_compliance/fixtures/artifacts/physically-missing-required-ref.md",
        "content_sha256": "0" * 64,
        "test_only": True,
    }
    fabricated_request, fabricated_context = transition_bundle("transition-fabricated-result", forged_event, "idle")
    fabricated_path = ".ai/communication_compliance/fixtures/artifacts/proof/transition-fabricated-result/validation.json"
    fixture_gate = gate_module()
    fixture_policy, fixture_policy_sha = fixture_gate.load_policy(POLICY_PATH)
    fabricated_pass = fixture_gate.validate_event(dispatch, ROOT, fixture_policy, fixture_policy_sha, test_mode=True)
    if fabricated_pass["result"] != "pass":
        raise RuntimeError("handcrafted-pass source event must validate")
    write_json(ROOT / fabricated_path, fabricated_pass)
    fabricated_request["validation_artifact_ref"] = fixture_ref(fabricated_path)
    fabricated_request["claimed_validation_artifact_sha256"] = fabricated_request["validation_artifact_ref"]["content_sha256"]
    cases.append(case("transition_fabricated_pass_result", "transition", result="fail", codes=["FRESH_EVENT_VALIDATION_FAILED", "VALIDATION_ARTIFACT_BYTE_MISMATCH", "VALIDATION_ARTIFACT_SEMANTIC_MISMATCH"], request=fabricated_request, active_state_context=fabricated_context, state_context_mode="test-fixture", actor_origin_context=actor_origin_context(), actor_origin_mode="test-fixture"))
    cases.append(case("transition_fabricated_resolved_status_rejected", "transition", result="fail", codes=["FRESH_EVENT_VALIDATION_FAILED", "VALIDATION_ARTIFACT_BYTE_MISMATCH", "VALIDATION_ARTIFACT_SEMANTIC_MISMATCH"], request=copy.deepcopy(fabricated_request), active_state_context=fabricated_context, state_context_mode="test-fixture", actor_origin_context=actor_origin_context(), actor_origin_mode="test-fixture"))

    other_event = copy.deepcopy(dispatch)
    other_event["event_id"] = "other-event"
    other_event["task_id"] = "other-task"
    other_request, other_context = transition_bundle("transition-validation-from-other-event", other_event, "idle", active_task=None)
    other_validation_path = ".ai/communication_compliance/fixtures/artifacts/proof/transition-validation-from-other-event/validation.json"
    write_json(ROOT / other_validation_path, fabricated_pass)
    other_request["validation_artifact_ref"] = fixture_ref(other_validation_path)
    cases.append(case("transition_validation_from_other_event_task", "transition", result="fail", codes=["VALIDATION_ARTIFACT_BYTE_MISMATCH", "VALIDATION_ARTIFACT_SEMANTIC_MISMATCH"], request=other_request, active_state_context=other_context, state_context_mode="test-fixture", actor_origin_context=actor_origin_context(), actor_origin_mode="test-fixture"))

    claimed_from_event = copy.deepcopy(dispatch)
    claimed_from_event["event_id"] = "claimed-from-state-mismatch"
    claimed_from_event["proposed_transition"]["from_state"] = "completed"
    claimed_from_request, claimed_from_context = transition_bundle("transition-claimed-from-mismatch", claimed_from_event, "idle")
    cases.append(case("transition_claimed_from_state_mismatch", "transition", result="fail", codes=["TRANSITION_FROM_STATE_EVIDENCE_MISMATCH"], request=claimed_from_request, active_state_context=claimed_from_context, state_context_mode="test-fixture", actor_origin_context=actor_origin_context(), actor_origin_mode="test-fixture"))

    wrong_authority = authority_context()
    wrong_authority["task_id"] = "wrong-task"
    add_transition(cases, "transition_c2_authority_wrong_task", copy.deepcopy(protected), "awaiting_human_gate", authority=wrong_authority, result="fail", codes=["AUTHORITY_CONTEXT_BINDING_MISMATCH"])
    replay_authority = authority_context()
    replay_request, replay_context = transition_bundle("transition-c2-replay", copy.deepcopy(protected), "awaiting_human_gate")
    cases.append(case("transition_c2_authority_replay", "transition", result="fail", codes=["AUTHORITY_CONTEXT_REPLAYED"], request=replay_request, active_state_context=replay_context, state_context_mode="test-fixture", authorization_context=replay_authority, authority_mode="test-fixture", actor_origin_context=actor_origin_context(), actor_origin_mode="test-fixture", consumed_context_ids=[replay_authority["context_id"]]))
    forged_trusted = authority_context()
    forged_trusted["injection_source"] = "trusted_external_host"
    forged_trusted["test_only"] = False
    trusted_request, trusted_context = transition_bundle("transition-c2-forged-trusted", copy.deepcopy(protected), "awaiting_human_gate")
    cases.append(case("transition_c2_forged_trusted_context", "transition", result="fail", codes=["AUTHORITY_CONTEXT_TRUST_BOUNDARY_INVALID"], request=trusted_request, active_state_context=trusted_context, state_context_mode="test-fixture", authorization_context=forged_trusted, authority_mode="trusted-host", actor_origin_context=actor_origin_context(), actor_origin_mode="test-fixture"))
    trusted_origin = actor_origin_context()
    trusted_origin["injection_source"] = "trusted_external_host"
    trusted_origin["test_only"] = False
    trusted_authority = authority_context()
    trusted_authority["injection_source"] = "trusted_external_host"
    trusted_authority["test_only"] = False
    trusted_pass_request, trusted_pass_state = transition_bundle("transition-c2-trusted-host-pass", copy.deepcopy(protected), "awaiting_human_gate")
    cases.append(case("transition_c2_trusted_host_verifiers_pass", "transition", request=trusted_pass_request, active_state_context=trusted_pass_state, state_context_mode="test-fixture", authorization_context=trusted_authority, authority_mode="trusted-host", actor_origin_context=trusted_origin, actor_origin_mode="trusted-host", trusted_host_verifier_result=True, trusted_actor_origin_verifier_result=True))

    malformed_request, malformed_context = transition_bundle("transition-validation-malformed", copy.deepcopy(dispatch), "idle")
    malformed_path = ".ai/communication_compliance/fixtures/artifacts/proof/transition-validation-malformed/validation.json"
    write_json(ROOT / malformed_path, {"schema_version": "malformed"})
    malformed_request["validation_artifact_ref"] = fixture_ref(malformed_path)
    cases.append(case("transition_validation_artifact_malformed", "transition", result="fail", codes=["VALIDATION_ARTIFACT_BYTE_MISMATCH", "VALIDATION_ARTIFACT_SCHEMA_INVALID", "VALIDATION_ARTIFACT_SEMANTIC_MISMATCH"], request=malformed_request, active_state_context=malformed_context, state_context_mode="test-fixture", actor_origin_context=actor_origin_context(), actor_origin_mode="test-fixture"))
    missing_request, missing_context = transition_bundle("transition-missing-event", dispatch, "idle")
    missing_request["event_ref"] = {"kind": "test_fixture_blob", "path": ".ai/communication_compliance/fixtures/artifacts/missing-event.json", "content_sha256": "0" * 64, "test_only": True}
    cases.append(case("transition_missing_event_ref", "transition", result="fail", codes=["EVENT_REFERENCE_UNRESOLVED", "FRESH_EVENT_VALIDATION_FAILED", "TRANSITION_ID_UNKNOWN"], request=missing_request, active_state_context=missing_context, state_context_mode="test-fixture"))
    cases.append(case("transition_full_real_workflow", "workflow_sequence", steps=[{"request": request, "active_state_context": context, "actor_origin_context": actor_origin_context(), "actor_origin_mode": "test-fixture"} for request, context in (dispatch_step, completion_step, revision_step, completion_two_step, acceptance_step)]))

    tree_head = subprocess.run(
        ["git", "-C", str(ROOT), "rev-parse", RELEASE + "^{tree}"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
        text=True,
    ).stdout.strip()
    valid_digest = sha256(git_show(PROTOCOL_REF, RELEASE))
    for label in ("EVENT", "STATE", "POINTER", "VALIDATION_ARTIFACT"):
        prefix = label.lower()
        cases.append(case(prefix + "_ref_mutable_rejected", "reference_attack", result="fail", codes=[label + "_REFERENCE_COMMIT_INVALID", label + "_REFERENCE_UNRESOLVED"], label=label, attack="mutable", reference={"kind": "git_blob", "commit": "master", "path": PROTOCOL_REF, "content_sha256": valid_digest}))
        cases.append(case(prefix + "_ref_missing_rejected", "reference_attack", result="fail", codes=[label + "_REFERENCE_UNRESOLVED"], label=label, attack="missing", reference={"kind": "git_blob", "commit": RELEASE, "path": ".ai/communication_compliance/fixtures/no-such-artifact.json", "content_sha256": "0" * 64}))
        cases.append(case(prefix + "_ref_tree_rejected", "reference_attack", result="fail", codes=[label + "_REFERENCE_UNRESOLVED"], label=label, attack="tree", reference={"kind": "git_blob", "commit": tree_head, "path": PROTOCOL_REF, "content_sha256": valid_digest}))
        cases.append(case(prefix + "_ref_digest_mismatch_rejected", "reference_attack", result="fail", codes=[label + "_REFERENCE_DIGEST_MISMATCH"], label=label, attack="digest", reference={"kind": "git_blob", "commit": RELEASE, "path": PROTOCOL_REF, "content_sha256": "0" * 64}))
        cases.append(case(prefix + "_ref_symlink_rejected", "reference_attack", result="fail", codes=[label + "_REFERENCE_UNRESOLVED"], label=label, attack="symlink", reference={}))
        cases.append(case(prefix + "_ref_submodule_rejected", "reference_attack", result="fail", codes=[label + "_REFERENCE_UNRESOLVED"], label=label, attack="submodule", reference={}))

    first = drift_record("fixture-drift-first", "POINTER_PROSE_CONTAMINATION", [])
    recurring = drift_record("fixture-drift-recurring", "POINTER_PROSE_CONTAMINATION", [first], fixture=immutable_parent_case("pointer_extra_prose"))
    cases.append(case("drift_first_occurrence_pass", "validate_drift", payload=first))
    cases.append(case("drift_recurring_immutable_fixture_pass", "validate_drift", payload=recurring, prior_records=[first]))
    mutable = copy.deepcopy(recurring)
    mutable["regression_fixture_ref"] = ".ai/communication_compliance/fixtures/fixture_suite.json#pointer_extra_prose"
    mutable["record_sha256"] = "0" * 64
    cases.append(case("drift_mutable_fixture_rejected", "validate_drift", payload=mutable, prior_records=[first], result="fail", codes=["DRIFT_RECORD_HASH_MISMATCH", "DRIFT_RECORD_SCHEMA_INVALID", "DRIFT_RECURRENCE_FIXTURE_REQUIRED"]))
    reviewed_exception = drift_record("fixture-drift-reviewed-exception", "NON_DETERMINISTIC_EXTERNAL_CHANNEL", [drift_record("fixture-drift-reviewed-first", "NON_DETERMINISTIC_EXTERNAL_CHANNEL", [])])
    reviewed_exception["deterministic_fixture_impossible_reason"] = "The external authenticated channel cannot be replayed inside the repository validator."
    reviewed_exception["foreground_review_required"] = True
    review_path = ".ai/HUMAN_BRIEFS/human-ai-communication-compliance-gate-exact-head-review-0002.md"
    reviewed_exception["foreground_review_ref"] = git_ref(review_path)
    reviewed_exception["record_sha256"] = gate_module().digest_object({key: value for key, value in reviewed_exception.items() if key != "record_sha256"}, preserve_mapping_order=False)
    cases.append(case("drift_deterministic_exception_with_review_pass", "validate_drift", payload=reviewed_exception, prior_records=[drift_record("fixture-drift-reviewed-first", "NON_DETERMINISTIC_EXTERNAL_CHANNEL", [])]))

    ledger_bytes = git_show(".ai/COMMUNICATION_DRIFT_LEDGER.yml", RELEASE)
    ledger = yaml.safe_load(ledger_bytes)
    ledger_ref = {"kind": "git_blob", "commit": RELEASE, "path": ".ai/COMMUNICATION_DRIFT_LEDGER.yml", "content_sha256": sha256(ledger_bytes)}
    cases.append(case("drift_ledger_release_pass", "validate_ledger", payload=ledger, expected_base_head=RELEASE))
    appended = copy.deepcopy(ledger)
    appended["ledger_revision"] += 1
    appended["previous_ledger_ref"] = ledger_ref
    new_record = drift_record("fixture-ledger-append", "FIXTURE_LEDGER_APPEND", ledger["records"])
    appended["records"] = ledger["records"] + [new_record]
    cases.append(case("drift_ledger_append_pass", "validate_ledger", payload=appended, expected_base_head=RELEASE))
    deleted = copy.deepcopy(appended)
    deleted["records"] = ledger["records"][:-1]
    cases.append(case("drift_ledger_delete_rejected", "validate_ledger", payload=deleted, expected_base_head=RELEASE, result="fail", codes=["DRIFT_LEDGER_PRIOR_RECORD_DELETED"]))
    changed = copy.deepcopy(appended)
    changed_records = copy.deepcopy(ledger["records"])
    changed_records[0]["root_cause"] = "rewritten history"
    changed["records"] = rehash(changed_records)
    cases.append(case("drift_ledger_mutation_rejected", "validate_ledger", payload=changed, expected_base_head=RELEASE, result="fail", codes=["DRIFT_LEDGER_PRIOR_RECORD_MUTATED"]))
    reordered = copy.deepcopy(appended)
    reordered_records = copy.deepcopy(ledger["records"])
    reordered_records[0], reordered_records[1] = reordered_records[1], reordered_records[0]
    reordered["records"] = rehash(reordered_records)
    cases.append(case("drift_ledger_reorder_rejected", "validate_ledger", payload=reordered, expected_base_head=RELEASE, result="fail", codes=["DRIFT_LEDGER_PRIOR_RECORD_REORDERED"]))
    rollback = copy.deepcopy(appended)
    rollback["ledger_revision"] = ledger["ledger_revision"]
    cases.append(case("drift_ledger_sequence_rollback", "validate_ledger", payload=rollback, expected_base_head=RELEASE, result="fail", codes=["DRIFT_LEDGER_SEQUENCE_ROLLBACK"]))

    for name in ("pointer_duplicate_keys.yml", "pointer_multidoc.yml", "pointer_anchor_alias.yml"):
        cases.append(case("strict_parse_" + name.removesuffix(".yml"), "parse_document", result="error", codes=["INPUT_DOCUMENT_REJECTED"], input_ref=f".ai/communication_compliance/fixtures/raw/{name}"))
    return migrate_inherited_cases(cases)


def main() -> int:
    write_raw_parser_fixtures()
    prior_suite_bytes = git_show(
        ".ai/communication_compliance/fixtures/fixture_suite.json",
        LEGACY_SUITE_HEAD,
    )
    prior_suite = json.loads(prior_suite_bytes)
    suite = {
        "schema_version": "human_ai.communication_fixture_suite.v2",
        "source_mailbox_base_head": SOURCE_BASE,
        "protocol_release_head": RELEASE,
        "prior_suite_ref": {
            "kind": "git_blob",
            "commit": LEGACY_SUITE_HEAD,
            "path": ".ai/communication_compliance/fixtures/fixture_suite.json",
            "content_sha256": sha256(prior_suite_bytes),
        },
        "prior_case_ids": [item["id"] for item in prior_suite["cases"]],
        "inherited_coverage_map_ref": git_ref(
            ".ai/communication_compliance/inherited_fixture_coverage_map.json"
        ),
        "cases": build_cases(),
    }
    write_json(SUITE_PATH, suite, sort_keys=False)
    print(f"fixture_cases={len(suite['cases'])}")
    print(f"suite={SUITE_PATH.relative_to(ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
