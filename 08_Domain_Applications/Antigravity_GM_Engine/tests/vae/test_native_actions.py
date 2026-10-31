"""
Tests for VAE Pillar 1: Native Capabilities and Actions (GM-01~05, COACH-01~03, PLAYER-01~04).
Verifies:
- All 12 actions are registered and have explicit preconditions/readbacks.
- Role permissions are validated (e.g. Player cannot execute GM actions).
- World-admin only actions (PLAYER-01, PLAYER-03) are blocked for non-admin roles.
- Parameter boundary rules (e.g. 240 rotation minutes, 2-team trades) are enforced.
- Numerical math oracle for GM-01 payroll/cap/tax calculations works deterministically.
"""

import pytest
from src.vae.contracts import RoleType, EvidenceTier
from src.vae.native_actions import VAENativeActionRegistry


@pytest.fixture
def registry():
    return VAENativeActionRegistry()


def test_native_action_inventory(registry):
    """Verifies that all 12 requested actions across GM, Coach, and Player are fully specified."""
    expected_actions = [
        "GM-01", "GM-02", "GM-03", "GM-04", "GM-05",
        "COACH-01", "COACH-02", "COACH-03",
        "PLAYER-01", "PLAYER-02", "PLAYER-03", "PLAYER-04"
    ]
    for action_id in expected_actions:
        spec = registry.get_action(action_id)
        assert spec is not None, f"Action {action_id} must be registered"
        assert spec.native_entry_path != ""
        assert len(spec.readback_layers) > 0
        assert spec.rollback_strategy != ""


def test_role_permission_enforcement(registry):
    """Verifies that roles cannot execute other roles' actions."""
    # Player cannot execute GM trade
    valid, msg = registry.validate_action_call("GM-03", RoleType.PLAYER, {})
    assert valid is False
    assert "ROLE_MISMATCH" in msg

    # Coach cannot execute GM salary cap calculations
    valid2, msg2 = registry.validate_action_call("GM-01", RoleType.COACH, {})
    assert valid2 is False
    assert "ROLE_MISMATCH" in msg2


def test_world_admin_boundary(registry):
    """Verifies that direct attribute or badge editing requires WORLD_ADMIN authority."""
    # Player role attempting direct attribute growth edit
    valid, msg = registry.validate_action_call("PLAYER-01", RoleType.PLAYER, {}, has_world_admin=False)
    assert valid is False
    assert "PERMISSION_DENIED" in msg
    assert "world-maintenance only" in msg

    # World admin authority grants validation
    valid_admin, _ = registry.validate_action_call("PLAYER-01", RoleType.WORLD_ADMIN, {}, has_world_admin=True)
    assert valid_admin is True


def test_coach_rotation_240_minute_rule(registry):
    """Verifies that rotation minutes must sum to exactly 240."""
    valid_rotation = {"minutes_sum": 240}
    invalid_rotation = {"minutes_sum": 230}

    ok, _ = registry.validate_action_call("COACH-02", RoleType.COACH, valid_rotation)
    assert ok is True

    bad, msg = registry.validate_action_call("COACH-02", RoleType.COACH, invalid_rotation)
    assert bad is False
    assert "240" in msg


def test_gm_trade_dual_team_rule(registry):
    """Verifies that trade action strictly enforces 2-team limit for current tooling."""
    ok, _ = registry.validate_action_call("GM-03", RoleType.GM, {"teams_count": 2})
    assert ok is True

    bad, msg = registry.validate_action_call("GM-03", RoleType.GM, {"teams_count": 3})
    assert bad is False
    assert "Only 2-team trades are supported" in msg


def test_gm_01_deterministic_financial_oracle(registry):
    """Verifies GM-01 numerical payroll, cap space, and luxury tax calculations."""
    salaries = [30_000_000, 25_000_000, 20_000_000, 15_000_000, 10_000_000]  # Total: 100M
    result = registry.execute_dryrun("GM-01", RoleType.GM, {"salaries": salaries})

    assert result.status == "BLOCKED_AWAITING_GAME_AUTH"
    assert result.evidence_tier == EvidenceTier.OFFLINE_FIXTURE
    out = result.output_data
    assert out["payroll_total"] == 100_000_000
    assert out["salary_cap"] == 112_414_000
    assert out["cap_space"] == 12_414_000
    assert out["luxury_tax_projected"] == 0
