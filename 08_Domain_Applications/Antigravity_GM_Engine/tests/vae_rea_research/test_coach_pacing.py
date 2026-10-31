from __future__ import annotations

import pytest
from src.vae_rea_research.coach_pacing import NativeCoachPacingEngine, NativeCoachPacingResult


def test_tempo_midpoint_calculation():
    """At Tempo 50, offset is 0 and modifier is baseline 10."""
    result = NativeCoachPacingEngine.evaluate(tempo=50.0, base_possession_target=100, secondary_factor=10)
    assert result.integer_tempo == 50
    assert result.tempo_offset_from_50 == 0
    assert result.bounded_modifier == 10
    assert result.hypothesized_net_target == 90  # 100 - 10
    assert result.possession_score_5x_2x == 5 * 90 + 2 * 10  # 470
    assert result.epistemological_tier == "STATIC_DISASSEMBLY_LEAD"
    assert result.gameplay_validation_status == "PENDING_GAMEPLAY_VALIDATION"


def test_tempo_native_fixed_point_scaling_oracle():
    """
    Verifies the exact x86 assembly fixed-point multiply sequence:
    ecx = (tempo - 50) * 60; edx = (ecx * 0x51eb851f) >> 36; ecx = edx + sign + 10; clamp [10, 70].
    Verified against independent mathematical oracle.
    """
    # Independent Oracle Table (verified by independent audit)
    oracle_table = {
        0: 10,    # unclamped = -50 -> clamped to floor 10
        10: 10,   # unclamped = -38 -> clamped to floor 10
        40: 10,   # unclamped = -2  -> clamped to floor 10
        50: 10,   # unclamped = 10  -> 10
        51: 11,   # unclamped = 11  -> 11
        52: 12,   # unclamped = 12  -> 12
        60: 22,   # unclamped = 22  -> 22
        70: 34,   # unclamped = 34  -> 34
        80: 46,   # unclamped = 46  -> 46
        90: 58,   # unclamped = 58  -> 58
        100: 70,  # unclamped = 70  -> 70 (ceiling saturation)
    }

    for tempo, expected_bounded in oracle_table.items():
        _, _, bounded = NativeCoachPacingEngine.calculate_tempo_modifier(float(tempo))
        assert bounded == expected_bounded, f"Failed at Tempo {tempo}: got {bounded}, expected {expected_bounded}"


def test_tempo_lower_bound_floor_saturation():
    """At low tempos (0 to 40), modifier saturates at minimum floor 10."""
    res_0 = NativeCoachPacingEngine.evaluate(tempo=0.0)
    assert res_0.bounded_modifier == 10

    res_20 = NativeCoachPacingEngine.evaluate(tempo=20.0)
    assert res_20.bounded_modifier == 10

    res_40 = NativeCoachPacingEngine.evaluate(tempo=40.0)
    assert res_40.bounded_modifier == 10


def test_tempo_upper_bound_saturation():
    """At extreme tempos above 100, modifier clamps strictly at 70."""
    res_100 = NativeCoachPacingEngine.evaluate(tempo=100.0)
    assert res_100.bounded_modifier == 70
    assert res_100.hypothesized_net_target == 30  # 100 - 70

    res_150 = NativeCoachPacingEngine.evaluate(tempo=150.0)
    assert res_150.bounded_modifier == 70
    assert res_150.hypothesized_net_target == 30


def test_possession_score_5x_2x_formula():
    """Verifies RVA 0x120bafe..0x120bb07: edx = 5*rax; eax = edx + 2*rcx."""
    res = NativeCoachPacingEngine.evaluate(tempo=70.0, base_possession_target=100, secondary_factor=20)
    # At Tempo 70, bounded_modifier is 34
    assert res.bounded_modifier == 34
    assert res.hypothesized_net_target == 66  # 100 - 34
    assert res.possession_score_5x_2x == 5 * 66 + 2 * 20  # 330 + 40 = 370


def test_coach_pacing_telemetry_spec():
    """Verifies telemetry contract schema conforms to semantic requirements without physical schemas."""
    spec = NativeCoachPacingEngine.create_telemetry_validation_spec()
    assert spec["target_mechanism"] == "COACH_DYNAMIC_PACING_ENGINE"
    assert spec["epistemological_status"] == "STATIC_DISASSEMBLY_LEAD"
    assert len(spec["required_metrics"]) >= 3
    # Verify no physical schema leak
    for m in spec["required_metrics"]:
        assert "sql_type" not in m
        assert "table_name" not in m
