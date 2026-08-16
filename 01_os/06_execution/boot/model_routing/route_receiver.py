#!/usr/bin/env python3
"""Validate an evidence-backed route and emit the Human receiver setup."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import yaml


RECEIVER_SETUP_FIELDS = {
    "collaboration_role",
    "provider",
    "product",
    "surface",
    "model",
    "reasoning_or_parameter_profile",
    "session_mode",
    "isolation_level",
    "repository_access_mode",
    "repository_or_worktree_requirement",
    "required_branch_or_sha",
    "local_files_required",
    "github_publication_required_before_start",
    "communication_carrier",
    "routing_basis_ref",
    "availability_assumption_or_observation_ref",
    "limitations",
}
SURFACE_PRODUCTS = {
    "chatgpt_web": "ChatGPT",
    "codex_desktop": "Codex Desktop",
    "claude_code_desktop": "Claude Code Desktop",
    "claude_desktop_cowork": "Claude Desktop",
    "gemini_web": "Gemini",
    "antigravity": "Antigravity",
}


class ReceiverSetupError(ValueError):
    pass


def _load(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ReceiverSetupError("receiver_setup_source_must_be_mapping")
    return value


def _entry(catalog: dict[str, Any], provider: str, surface: str, model: str) -> dict[str, Any]:
    matches = [
        entry for entry in catalog.get("entries") or []
        if entry.get("provider") == provider
        and entry.get("surface_id") == surface
        and entry.get("model_label") == model
    ]
    if len(matches) != 1:
        raise ReceiverSetupError("selected_route_catalog_identity_invalid")
    if matches[0].get("registered") is not True:
        raise ReceiverSetupError("selected_route_not_registered")
    return matches[0]


def validate_receiver_setup(
    setup: dict[str, Any],
    *,
    catalog: dict[str, Any],
    role_contract: dict[str, Any],
) -> None:
    if not isinstance(setup, dict) or set(setup) != RECEIVER_SETUP_FIELDS:
        raise ReceiverSetupError("receiver_setup_field_set_invalid")
    roles = role_contract.get("collaboration_roles") or {}
    if setup.get("collaboration_role") not in roles:
        raise ReceiverSetupError("collaboration_role_invalid")
    if not isinstance(setup.get("local_files_required"), bool):
        raise ReceiverSetupError("local_files_required_must_be_boolean")
    if not isinstance(setup.get("github_publication_required_before_start"), bool):
        raise ReceiverSetupError("github_publication_required_must_be_boolean")
    if setup.get("communication_carrier") not in {"local", "GitHub"}:
        raise ReceiverSetupError("receiver_setup_carrier_invalid")
    for field in RECEIVER_SETUP_FIELDS - {
        "limitations", "local_files_required", "github_publication_required_before_start"
    }:
        if setup.get(field) in (None, ""):
            raise ReceiverSetupError(f"receiver_setup_field_empty:{field}")
    if not isinstance(setup.get("limitations"), list):
        raise ReceiverSetupError("receiver_setup_limitations_invalid")

    entry = _entry(catalog, setup["provider"], setup["surface"], setup["model"])
    if setup["product"] != SURFACE_PRODUCTS.get(setup["surface"]):
        raise ReceiverSetupError("receiver_setup_product_surface_mismatch")
    profile_id = setup["reasoning_or_parameter_profile"]
    profiles = entry.get("parameter_profiles") or []
    if profile_id not in {profile.get("profile_id") for profile in profiles}:
        raise ReceiverSetupError("receiver_setup_parameter_profile_unsupported")

    if setup["repository_access_mode"] == "GitHub_only":
        if setup["local_files_required"] and setup["github_publication_required_before_start"] is not True:
            raise ReceiverSetupError("github_only_local_material_unpublished")
        if setup["github_publication_required_before_start"] is not True:
            raise ReceiverSetupError("github_only_publication_precondition_missing")
        if setup["communication_carrier"] != "GitHub":
            raise ReceiverSetupError("github_only_receiver_requires_GitHub_carrier")
    if setup["collaboration_role"] == "independent_review":
        if setup["isolation_level"] not in {"fresh_session", "isolated_project", "isolated_worktree"}:
            raise ReceiverSetupError("independent_review_isolation_invalid")
        if "executor_private_context" not in setup["limitations"]:
            raise ReceiverSetupError("independent_review_private_context_limit_missing")


def build_receiver_setup(
    selection: dict[str, Any],
    *,
    catalog: dict[str, Any],
    role_contract: dict[str, Any],
) -> dict[str, Any]:
    required = RECEIVER_SETUP_FIELDS - {"product"}
    missing = sorted(field for field in required if field not in selection)
    if missing:
        raise ReceiverSetupError("receiver_selection_fields_missing:" + ",".join(missing))
    setup = {field: selection.get(field) for field in RECEIVER_SETUP_FIELDS}
    setup["product"] = SURFACE_PRODUCTS.get(str(selection.get("surface")))
    validate_receiver_setup(setup, catalog=catalog, role_contract=role_contract)
    return setup


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--selection", required=True, type=Path)
    parser.add_argument("--catalog", required=True, type=Path)
    parser.add_argument("--role-contract", required=True, type=Path)
    args = parser.parse_args()
    try:
        setup = build_receiver_setup(
            _load(args.selection), catalog=_load(args.catalog), role_contract=_load(args.role_contract)
        )
    except (OSError, yaml.YAMLError, ReceiverSetupError) as exc:
        print(f"receiver_setup_rejected:{exc}", file=sys.stderr)
        return 2
    print(json.dumps({"receiver_setup": setup, "authority": "routing_only"}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
