"""
Unit tests for VAE E2–E4 scope coverage and negative failure paths.
"""

from src.vae.e2_e4_extensions import VAEE2E4ScopeGuard


def test_e2_coach_minutes_and_timeline():
    # Valid minutes (0..48)
    ok, msg = VAEE2E4ScopeGuard.validate_coach_minutes_request(player_id=101, minutes=32, roster_size=15)
    assert ok is True

    # Invalid minutes (>48)
    ok, msg = VAEE2E4ScopeGuard.validate_coach_minutes_request(player_id=101, minutes=50, roster_size=15)
    assert ok is False
    assert "MINUTES_OUT_OF_RANGE" in msg

    # Roster overflow (>15)
    ok, msg = VAEE2E4ScopeGuard.validate_coach_minutes_request(player_id=101, minutes=20, roster_size=16)
    assert ok is False
    assert "ROSTER_OVERFLOW" in msg

    # Rejection of external 48-minute timeline full override
    ok, msg = VAEE2E4ScopeGuard.reject_full_rotation_timeline_override()
    assert ok is False
    assert "UNSUPPORTED_TIMELINE_OVERRIDE" in msg


def test_e3_trade_boundaries():
    # 2-team trade is accepted
    ok, msg = VAEE2E4ScopeGuard.validate_trade_teams([1, 2])
    assert ok is True

    # 3-team trade is deterministically rejected (GAP-BP-01)
    ok, msg = VAEE2E4ScopeGuard.validate_trade_teams([1, 2, 3])
    assert ok is False
    assert "THREE_TEAM_TRADE_UNSUPPORTED" in msg

    # Roster counts: regular <= 15, active <= 13
    ok, _ = VAEE2E4ScopeGuard.validate_roster_counts_after_trade(regular_count=14, active_count=12)
    assert ok is True

    ok, msg = VAEE2E4ScopeGuard.validate_roster_counts_after_trade(regular_count=16, active_count=12)
    assert ok is False
    assert "REGULAR_ROSTER_EXCEEDED" in msg

    ok, msg = VAEE2E4ScopeGuard.validate_roster_counts_after_trade(regular_count=15, active_count=14)
    assert ok is False
    assert "ACTIVE_ROSTER_EXCEEDED" in msg


def test_e4_player_training_preset_guard():
    # Individual player training preset write must be rejected until real UI audit completes
    ok, msg = VAEE2E4ScopeGuard.reject_player_training_preset_write(position=0, player_type=1)
    assert ok is False
    assert "PLAYER_TRAINING_PRESET_SETTER_NOT_BOUND" in msg
