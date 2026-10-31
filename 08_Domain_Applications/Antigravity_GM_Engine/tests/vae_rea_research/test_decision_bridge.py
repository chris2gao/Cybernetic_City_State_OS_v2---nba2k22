from __future__ import annotations

import pytest
from src.vae_rea_research.decision_bridge import ExperimentalTacticalDecisionBridge


@pytest.fixture
def bridge():
    return ExperimentalTacticalDecisionBridge()


def test_decision_bridge_experimental_status(bridge):
    """Verifies that the decision bridge is strictly marked as an experimental heuristic."""
    assert bridge.MODEL_TIER == "EXPERIMENTAL_HEURISTIC"
    assert bridge.IS_NATIVE_LAW is False


def test_role_ceiling_governor_franchise_core(bridge):
    """Branch A: Primary Core (role_tier == 3) bypasses role ceilings."""
    res = bridge.calculate_role_ceiling_governor(
        shot_tendency=96.0, touches=90.0, role_tier=3, role_ceiling=80.0
    )
    assert res["is_suppressed"] is False
    assert res["friction_score"] == 0.0
    assert res["effective_shot_tendency"] == 96.0
    assert res["clamp_status"] == "FRANCHISE_CORE_UNCONSTRAINED"
    assert res["is_native_law"] is False
    assert res["has_cross_model_divergence"] is False


def test_role_ceiling_governor_secondary_suppression_and_divergence(bridge):
    """
    Verifies that secondary players (role_tier != 3) exceeding their
    discounted role ceiling (ceiling - 5) are clamped by the heuristic,
    and cross-model divergence is transparently reported (INT-P0-03).
    """
    # role_ceiling = 80.0 -> effective_ceiling = 75.0 (sub edx, 5)
    # shot_tendency = 88.0 > 75.0 -> heuristic clamps to 75.0
    res = bridge.calculate_role_ceiling_governor(
        shot_tendency=88.0, touches=65.0, role_tier=2, role_ceiling=80.0
    )
    assert res["is_suppressed"] is True
    assert res["friction_score"] == 13.0
    assert res["effective_shot_tendency"] == 75.0
    assert res["clamp_status"] == "ROLE_CEILING_SUPPRESSED"

    # Static disassembly reference track check
    assert "static_disassembly_reference" in res
    assert res["static_disassembly_reference"]["branch"] == "BRANCH_C_NON_CORE_SUPPORT"
    # Transparent disclosure of divergence between user ceiling and table floor
    assert res["has_cross_model_divergence"] is True
    assert "differs from native table" in res["divergence_note"]


def test_coach_tempo_bounds_saturation_and_floor(bridge):
    """
    Verifies Coach Tempo Bounds Engine:
    - High value (80) saturates slider at 70, while static assembly calculates modifier 46.
    - Low value (4) saturates slider at 10.
    - Static assembly fixed-point modifier is distinctly separated.
    """
    res_high = bridge.calculate_effective_coach_tempo(raw_tempo=80.0)
    assert res_high["effective_tempo"] == 70.0
    assert res_high["is_saturated"] is True
    assert res_high["saturation_loss"] == 10.0
    # Fixed-point assembly modifier: (80 - 50)*1.2 + 10 = 46
    assert res_high["static_disassembly_lead"]["bounded_modifier"] == 46

    res_low = bridge.calculate_effective_coach_tempo(raw_tempo=4.0)
    assert res_low["effective_tempo"] == 10.0
    assert res_low["is_choked"] is True
    assert res_low["static_disassembly_lead"]["bounded_modifier"] == 10


def test_roster_tactical_alignment_experimental(bridge):
    """
    Simulates a 5-man starting lineup under Head Coach Doc Rivers (Tempo=80).
    Verifies experimental lineup friction and tactical synergy scoring.
    """
    roster = [
        {"name": "Tyrese Haliburton", "ShotTendency": 96, "TouchTendency": 95, "RoleTier": 3, "RoleCeiling": 95},  # Core
        {"name": "Buddy Hield", "ShotTendency": 85, "TouchTendency": 82, "RoleTier": 2, "RoleCeiling": 90},       # Ceil=85, Shot=85 (within)
        {"name": "Harrison Barnes", "ShotTendency": 65, "TouchTendency": 62, "RoleTier": 1, "RoleCeiling": 75},   # Ceil=70, Shot=65 (within)
        {"name": "Marvin Bagley", "ShotTendency": 75, "TouchTendency": 50, "RoleTier": 1, "RoleCeiling": 70},     # Ceil=65, Shot=75 (suppressed by 10)
        {"name": "Richaun Holmes", "ShotTendency": 45, "TouchTendency": 45, "RoleTier": 1, "RoleCeiling": 60},   # Ceil=55, Shot=45 (within)
    ]
    coach_gameplan = {
        "Tempo": 80,
        "PreferredSystem": 1,
    }

    eval_result = bridge.evaluate_roster_tactical_alignment(roster, coach_gameplan)

    assert eval_result["model_status"] == "EXPERIMENTAL_HEURISTIC"
    assert eval_result["roster_size"] == 5
    assert eval_result["aligned_players_count"] == 4
    assert eval_result["coach_tempo_analysis"]["effective_tempo"] == 70.0
    assert eval_result["team_tactical_synergy_score"] > 60.0

    # Marvin Bagley should be flagged
    bagley = next(p for p in eval_result["player_evaluations"] if p["name"] == "Marvin Bagley")
    assert bagley["is_suppressed"] is True
    assert bagley["clamp_status"] == "ROLE_CEILING_SUPPRESSED"
    assert bagley["effective_shot"] == 65.0  # 70 - 5
