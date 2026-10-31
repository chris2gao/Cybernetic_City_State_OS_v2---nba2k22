from __future__ import annotations

import pytest
from src.vae_rea_research.coach_pacing import NativeCoachPacingEngine, NativeCoachPacingResult


def test_tempo_midpoint_calculation():
    """At Tempo 50, offset is 0 and modifier is baseline 10."""
    result = NativeCoachPacingEngine.evaluate(tempo=50.0, base_possession_target=100, secondary_factor=10)
    assert result.integer_tempo == 50
    assert result.tempo_offset_from_50 == 0
    assert result.bounded_modifier == 10
    assert result.net_possession_target == 90  # 100 - 10
    assert result.possession_score_5x_2x == 5 * 90 + 2 * 10  # 470
    assert result.epistemological_tier == "PROVEN_NATIVE_ASSEMBLY"
    assert result.gameplay_validation_status == "PENDING_GAMEPLAY_VALIDATION"


def test_tempo_lower_bound_floor_saturation():
    """At low tempos (e.g. 0 to 40), modifier saturates at minimum floor 10."""
    res_0 = NativeCoachPacingEngine.evaluate(tempo=0.0)
    assert res_0.bounded_modifier == 10

    res_20 = NativeCoachPacingEngine.evaluate(tempo=20.0)
    assert res_20.bounded_modifier == 10

    res_40 = NativeCoachPacingEngine.evaluate(tempo=40.0)
    # (40 - 50) * 0.6 + 10 = -6 + 10 = 4 -> clamped to 10
    assert res_40.bounded_modifier == 10


def test_tempo_scaling_and_upper_bound_saturation():
    """At higher tempos, modifier scales up to 40 at tempo 100, and clamps to 70 if extended."""
    res_100 = NativeCoachPacingEngine.evaluate(tempo=100.0)
    # (100 - 50) * 0.6 + 10 = 30 + 10 = 40
    assert res_100.bounded_modifier == 40
    assert res_100.net_possession_target == 100 - 40  # 60

    # Over-range extreme test verifying eax=0x46 clamping
    res_extreme = NativeCoachPacingEngine.evaluate(tempo=200.0)
    # (200 - 50) * 0.6 + 10 = 90 + 10 = 100 -> clamped strictly to 70!
    assert res_extreme.bounded_modifier == 70
    assert res_extreme.net_possession_target == 100 - 70  # 30


def test_possession_score_5x_2x_formula():
    """Verifies RVA 0x120bafe..0x120bb07: edx = 5*rax; eax = edx + 2*rcx."""
    res = NativeCoachPacingEngine.evaluate(tempo=70.0, base_possession_target=100, secondary_factor=20)
    # (70 - 50) * 0.6 + 10 = 12 + 10 = 22
    assert res.bounded_modifier == 22
    assert res.net_possession_target == 78  # 100 - 22
    assert res.possession_score_5x_2x == 5 * 78 + 2 * 20  # 390 + 40 = 430


def test_coach_pacing_telemetry_spec():
    """Verifies telemetry contract schema conforms to future in-game validation principles."""
    spec = NativeCoachPacingEngine.create_telemetry_validation_spec()
    assert spec["mechanism_id"] == "COACH_DYNAMIC_PACING_ENGINE"
    assert spec["epistemological_status"] == "ASSEMBLY_PROVEN_GAMEPLAY_PENDING"
    assert len(spec["validation_hypotheses"]) >= 3
    for hyp in spec["validation_hypotheses"]:
        assert hyp["verification_gate"] == "PENDING_GAMEPLAY_VALIDATION"
