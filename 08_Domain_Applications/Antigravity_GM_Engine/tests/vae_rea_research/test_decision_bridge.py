from __future__ import annotations

import os
import pytest

from src.vae_rea_research.decision_bridge import ExperimentalTacticalDecisionBridge


@pytest.fixture
def bridge():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
    return ExperimentalTacticalDecisionBridge(repo_root=repo_root)


def test_decision_bridge_experimental_status(bridge):
    """
    Verifies that ExperimentalTacticalDecisionBridge explicitly declares
    itself as an experimental heuristic rather than a verified native law.
    """
    assert bridge.MODEL_TIER == "EXPERIMENTAL_HEURISTIC"
    assert bridge.IS_NATIVE_LAW is False


def test_role_ceiling_governor_franchise_core(bridge):
    """
    Verifies that primary franchise core players (role_tier == 3) bypass
    role ceiling clamping as proven in native assembly (cmp ecx, 3).
    """
    res = bridge.calculate_role_ceiling_governor(
        shot_tendency=96.0, touches=90.0, role_tier=3, role_ceiling=80.0
    )
    assert res["is_suppressed"] is False
    assert res["friction_score"] == 0.0
    assert res["effective_shot_tendency"] == 96.0
    assert res["clamp_status"] == "FRANCHISE_CORE_UNCONSTRAINED"
    assert res["is_native_law"] is False


def test_role_ceiling_governor_secondary_suppression(bridge):
    """
    Verifies that secondary players (role_tier != 3) exceeding their
    discounted role ceiling (ceiling - 5) are clamped by the governor.
    """
    # role_ceiling = 80.0 -> effective_ceiling = 75.0 (sub edx, 5)
    # shot_tendency = 88.0 > 75.0 -> clamped to 75.0
    res = bridge.calculate_role_ceiling_governor(
        shot_tendency=88.0, touches=65.0, role_tier=2, role_ceiling=80.0
    )
    assert res["is_suppressed"] is True
    assert res["friction_score"] == 13.0
    assert res["effective_shot_tendency"] == 75.0
    assert res["clamp_status"] == "ROLE_CEILING_SUPPRESSED"


def test_coach_tempo_bounds_saturation_and_floor(bridge):
    """
    Verifies Coach Tempo Bounds Engine:
    - High value (80) saturates at 70 (eax=0x46 in native code).
    - Low value (4) saturates at 10 (eax=0x0a in native code).
    - Middle value (50) scales within bounds.
    """
    res_high = bridge.calculate_effective_coach_tempo(raw_tempo=80.0)
    assert res_high["effective_tempo"] == 70.0
    assert res_high["is_saturated"] is True
    assert res_high["saturation_loss"] == 10.0

    res_low = bridge.calculate_effective_coach_tempo(raw_tempo=4.0)
    assert res_low["effective_tempo"] == 10.0
    assert res_low["is_choked"] is True

    res_mid = bridge.calculate_effective_coach_tempo(raw_tempo=50.0)
    assert res_mid["effective_tempo"] == 50.0
    assert not res_mid["is_saturated"]
    assert not res_mid["is_choked"]
    # Check self-consistent arithmetic at 50 tempo:
    # 0.65 + (50/70)*0.45 = 0.65 + 0.321428 = 0.9714
    assert 0.97 <= res_mid["pace_multiplier_scale"] <= 0.98


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
