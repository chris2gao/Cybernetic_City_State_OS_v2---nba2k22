#!/usr/bin/env python3
"""Tests for big-task closure preflight and pause classification."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import pytest
import yaml

sys.path.insert(0, str(Path(__file__).resolve().parent))

import closure_preflight  # noqa: E402
from closure_preflight import INTERNAL, STOP, UNRECOGNIZED  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[4]


def _packet(**overrides) -> dict:
    base = {
        "objective": "close one coherent objective",
        "allowed_changed_paths": ["01_os/03_mechanisms/example/**"],
        "required_tests": ["python -m pytest 01_os/06_execution -q"],
        "prohibitions": ["force_push", "rebase"],
        "required_completion_pointer": "section 10 shape",
        "terminal_lifecycle_state": "integrated_and_verified_on_demand",
        "publisher": {
            "principal_binding": "connector_authenticated",
            "publication_transport": "github_api_connector",
            "source_branch_publication": "task_scope_default",
            "master_integration_confirmation": "not_requested",
            "confirmation_ref": None,
            "expected_remote_head": "0" * 40,
        },
        "big_task_confirmation_closure": {
            "enabled": True,
            "known_confirmation_required_actions": [],
            "preconfirmed_actions": [],
            "confirmation_ref": None,
            "uncovered_actions": [],
        },
        "verification_profile": {
            "independent_reviewer": "fresh isolated window",
            "executor_self_acceptance": "prohibited",
        },
    }
    base.update(overrides)
    return base


# --------------------------------------------------------------------------
# pause classification
# --------------------------------------------------------------------------


@pytest.mark.parametrize("reason", sorted(closure_preflight.INTERNAL_CONTINUATION))
def test_internal_continuation_reasons_do_not_stop(reason):
    assert closure_preflight.classify_pause(reason) == INTERNAL


@pytest.mark.parametrize("reason", sorted(closure_preflight.GENUINE_STOP))
def test_genuine_stop_reasons_stop(reason):
    assert closure_preflight.classify_pause(reason) == STOP


def test_task_branch_push_is_internal_not_a_human_gate():
    """The single distinction this contract exists to fix."""
    assert closure_preflight.classify_pause("task_branch_push") == INTERNAL
    assert closure_preflight.classify_pause("task_branch_commit") == INTERNAL
    assert closure_preflight.classify_pause("completion_pointer_closure") == INTERNAL


@pytest.mark.parametrize(
    "reason",
    ["", "   ", "feels_risky", "master_write", "TASK_BRANCH_PUSH", "asking_to_be_safe"],
)
def test_unrecognized_reasons_fail_closed(reason):
    verdict = closure_preflight.classify_pause(reason)
    assert verdict == UNRECOGNIZED
    assert verdict != INTERNAL


def test_continuation_and_stop_sets_are_disjoint():
    assert not (
        closure_preflight.INTERNAL_CONTINUATION & closure_preflight.GENUINE_STOP
    )


# --------------------------------------------------------------------------
# packet closure
# --------------------------------------------------------------------------


def test_complete_packet_is_closable():
    assert closure_preflight.validate_packet(_packet()) == []


def test_empty_protected_action_set_is_valid():
    """Large does not mean dangerous: size creates no authorization need."""
    closure = closure_preflight.derive_closure(_packet())
    assert closure["known_protected_actions"] == []
    assert closure_preflight.validate_packet(_packet()) == []


def test_current_schema_master_integration_is_surfaced_as_a_protected_action():
    packet = _packet(
        publisher={
            "principal_binding": "connector_authenticated",
            "publication_transport": "github_api_connector",
            "source_branch_publication": "task_scope_default",
            "master_integration_confirmation": "current_Human_confirmed",
            "confirmation_ref": None,
            "expected_remote_head": "0" * 40,
        },
        big_task_confirmation_closure={
            "enabled": True,
            "known_confirmation_required_actions": ["master_integration"],
            "preconfirmed_actions": ["master_integration"],
            "confirmation_ref": None,
            "uncovered_actions": [],
        },
    )
    closure = closure_preflight.derive_closure(packet)
    assert closure["known_protected_actions"] == ["master_integration"]
    assert closure_preflight.validate_packet(packet) == []


def test_current_schema_master_integration_p5_false_negative_is_closed():
    """Regression for P5: current section-7 fields must not derive []."""
    packet = _packet()
    packet["publisher"]["master_integration_confirmation"] = "current_Human_confirmed"
    packet["big_task_confirmation_closure"].update(
        known_confirmation_required_actions=["master_integration"],
        preconfirmed_actions=["master_integration"],
        uncovered_actions=[],
    )
    closure = closure_preflight.derive_closure(packet)
    assert "master_integration" in closure["known_protected_actions"]
    assert closure_preflight.validate_packet(packet) == []


def test_uncovered_confirmation_required_action_is_a_finding():
    packet = _packet(
        big_task_confirmation_closure={
            "enabled": True,
            "known_confirmation_required_actions": ["master_integration"],
            "preconfirmed_actions": [],
            "confirmation_ref": None,
            "uncovered_actions": ["master_integration"],
        }
    )
    assert (
        "confirmation_required_action_uncovered:master_integration"
        in closure_preflight.validate_packet(packet)
    )


def test_current_human_confirmation_does_not_require_legacy_authorization_ref():
    packet = _packet()
    packet["publisher"]["master_integration_confirmation"] = "current_Human_confirmed"
    packet["big_task_confirmation_closure"].update(
        known_confirmation_required_actions=["master_integration"],
        preconfirmed_actions=["master_integration"],
    )
    assert closure_preflight.validate_packet(packet) == []


def test_preconfirmed_master_action_requires_matching_publisher_state():
    packet = _packet()
    packet["big_task_confirmation_closure"].update(
        known_confirmation_required_actions=["master_integration"],
        preconfirmed_actions=["master_integration"],
    )
    assert (
        "master_integration_preconfirmed_but_publisher_not_confirmed"
        in closure_preflight.validate_packet(packet)
    )


@pytest.mark.parametrize(
    "field",
    ["objective", "allowed_changed_paths", "required_tests", "prohibitions",
     "required_completion_pointer", "terminal_lifecycle_state"],
)
def test_each_missing_closure_field_is_reported(field):
    packet = _packet()
    packet.pop(field)
    findings = closure_preflight.validate_packet(packet)
    assert findings, f"removing {field} should not leave the packet closable"


def test_empty_list_field_counts_as_missing():
    packet = _packet(allowed_changed_paths=[])
    assert "closure_field_missing:allowed_changed_paths" in closure_preflight.validate_packet(packet)


def test_freeform_terminal_state_is_rejected():
    packet = _packet(terminal_lifecycle_state="COMPLETE_MASTER_PUBLISHED")
    findings = closure_preflight.validate_packet(packet)
    assert any(f.startswith("terminal_lifecycle_state_not_in_enum") for f in findings)


@pytest.mark.parametrize("state", sorted(closure_preflight.OPEN_LIFECYCLE_STATES))
def test_a_task_may_declare_it_ends_on_an_open_state(state):
    """A review-ready candidate ends open. Demanding a closing value here would
    force every implementation task to either lie or self-accept."""
    assert closure_preflight.validate_packet(
        _packet(terminal_lifecycle_state=state)
    ) == []


def test_missing_reviewer_boundary_is_reported():
    packet = _packet(verification_profile={"executor_self_acceptance": "prohibited"})
    assert "closure_field_missing:final_reviewer_boundary" in closure_preflight.validate_packet(packet)


def test_self_acceptance_must_be_prohibited():
    packet = _packet(
        verification_profile={
            "independent_reviewer": "self",
            "executor_self_acceptance": "allowed",
        }
    )
    assert "executor_self_acceptance_must_be_prohibited" in closure_preflight.validate_packet(packet)


def test_explicit_closure_block_wins_over_derivation():
    packet = _packet(big_task_closure={"known_protected_actions": ["runtime_activation"]})
    closure = closure_preflight.derive_closure(packet)
    assert closure["known_protected_actions"] == ["runtime_activation"]


def test_legacy_explicit_closure_cannot_mask_current_master_integration():
    packet = _packet(big_task_closure={"known_protected_actions": []})
    packet["publisher"]["master_integration_confirmation"] = "current_Human_confirmed"
    packet["big_task_confirmation_closure"].update(
        known_confirmation_required_actions=["master_integration"],
        preconfirmed_actions=["master_integration"],
    )
    closure = closure_preflight.derive_closure(packet)
    assert closure["known_protected_actions"] == ["master_integration"]
    assert closure_preflight.validate_packet(packet) == []


def test_malformed_confirmation_action_item_fails_closed_without_crashing():
    packet = _packet(
        big_task_confirmation_closure={
            "enabled": True,
            "known_confirmation_required_actions": [{"bad": "mapping"}],
            "preconfirmed_actions": [],
            "confirmation_ref": None,
            "uncovered_actions": [],
        }
    )
    findings = closure_preflight.validate_packet(packet)
    assert (
        "confirmation_closure_known_confirmation_required_actions_items_must_be_nonempty_strings"
        in findings
    )


# --------------------------------------------------------------------------
# this task's own packet must pass its own gate
# --------------------------------------------------------------------------


def test_this_tasks_packet_is_closable():
    packet_path = (
        REPO_ROOT
        / "01_os/_runs/run-20260828-t3-archive-and-big-task-workflow-001"
        / "01_任务输入/任务包_v1.yml"
    )
    if not packet_path.is_file():
        pytest.skip("run packet not present in this checkout")
    packet = closure_preflight.load_packet(packet_path)
    assert closure_preflight.validate_packet(packet) == []


# --------------------------------------------------------------------------
# CLI
# --------------------------------------------------------------------------


def test_cli_classify_exit_codes(tmp_path):
    script = Path(closure_preflight.__file__)
    ok = subprocess.run(
        [sys.executable, "-B", str(script), "--classify", "task_branch_push"],
        capture_output=True, text=True, encoding="utf-8",
    )
    assert ok.returncode == 0
    stop = subprocess.run(
        [sys.executable, "-B", str(script), "--classify", "runtime_or_scheduler_activation"],
        capture_output=True, text=True, encoding="utf-8",
    )
    assert stop.returncode == 1


def test_cli_rejects_unreadable_packet(tmp_path):
    bad = tmp_path / "bad.yml"
    bad.write_text("- not: a mapping\n", encoding="utf-8")
    script = Path(closure_preflight.__file__)
    proc = subprocess.run(
        [sys.executable, "-B", str(script), "--packet", str(bad)],
        capture_output=True, text=True, encoding="utf-8",
    )
    assert proc.returncode == 3


def test_contract_lists_match_the_code():
    """Drift guard between the canonical contract and this module."""
    contract = REPO_ROOT / "01_os/03_mechanisms/task_orchestration/大任务与长时执行契约_v1.yml"
    data = yaml.safe_load(contract.read_text(encoding="utf-8"))
    assert set(data["internal_continuation"]["actions"]) == set(
        closure_preflight.INTERNAL_CONTINUATION
    )
    assert set(data["genuine_stop"]["conditions"]) == set(closure_preflight.GENUINE_STOP)
    assert data["not_a_stop_condition"]["ordinary_task_branch_publication"] is True
    assert (
        data["closure_preflight"]["authorization_artifact_required_merely_because_task_is_large"]
        is False
    )
