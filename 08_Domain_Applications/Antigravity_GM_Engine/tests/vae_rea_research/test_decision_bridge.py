from __future__ import annotations

import os
import pytest

from src.vae_rea_research.decision_bridge import NativeTacticalDecisionBridge


@pytest.fixture
def bridge():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
    return NativeTacticalDecisionBridge(repo_root=repo_root)


def test_equilibrium_governor_within_margin(bridge):
    """
    Verifies that when |ShotTendency - Touches| <= 5, governor does not suppress shot attempts.
    """
    res = bridge.calculate_equilibrium_governor(shot_tendency=75.0, touch_tendency=78.0)
    assert res["is_in_equilibrium"] is True
    assert res["friction_score"] == 0.0
    assert res["effective_shot_tendency"] == 75.0
    assert res["clamp_status"] == "PERFECT_EQUILIBRIUM"


def test_equilibrium_governor_high_usage_suppression(bridge):
    """
    Verifies that when ShotTendency exceeds Touches by > 5, native AI governor
    clamps effective shot tendency to Touches + 5.
    Example: Tyrese Haliburton has live ShotTendency=96, if assigned Touches=60.
    """
    res = bridge.calculate_equilibrium_governor(shot_tendency=96.0, touch_tendency=60.0)
    assert res["is_in_equilibrium"] is False
    assert res["delta"] == 36.0
    assert res["friction_score"] == 31.0
    assert res["effective_shot_tendency"] == 65.0  # 60 + 5
    assert res["clamp_status"] == "NATIVE_SUPPRESSED_HIGH_USAGE_DISPARITY"
    assert "suppresses unassigned shots" in res["recommendation"]


def test_coach_tempo_clamping_saturation(bridge):
    """
    Verifies Coach Dynamic Pacing Engine clamps tempo influence to [10, 70].
    Doc Rivers has live Tempo=80 in COACHDATA; native engine clamps to 70.
    """
    res = bridge.calculate_effective_coach_tempo(raw_tempo=80.0)
    assert res["raw_tempo_slider"] == 80.0
    assert res["effective_tempo"] == 70.0
    assert res["is_saturated"] is True
    assert res["saturation_loss"] == 10.0
    assert res["estimated_pace_possessions"] == 88.0 + (70.0 * 0.28)
    assert "saturates any coach tempo above 70" in res["note"]


def test_coach_tempo_clamping_floor(bridge):
    """
    Verifies Coach Dynamic Pacing Engine clamps ultra-low tempo to 10.
    """
    res = bridge.calculate_effective_coach_tempo(raw_tempo=4.0)
    assert res["raw_tempo_slider"] == 4.0
    assert res["effective_tempo"] == 10.0
    assert res["is_choked"] is True
    assert res["estimated_pace_possessions"] == 88.0 + (10.0 * 0.28)


def test_possession_shot_probability_calculation(bridge):
    """
    Verifies combined calculation of shot probability incorporating governor and pacing scale.
    """
    res = bridge.calculate_shot_selection_probability(
        shot_tendency=80.0, touch_tendency=80.0, coach_tempo=50.0, slider_weight=1.0
    )
    # 50 tempo: multiplier = 0.65 + (50 / 70) * 0.45 = 0.65 + 0.321428 = 0.9714
    # P_shot = (80 / 100) * 0.9714 = 0.7771
    assert 0.75 <= res["possession_shot_probability"] <= 0.80
    assert res["player_effective_shot_tendency"] == 80.0


def test_roster_tactical_alignment_with_live_profile(bridge):
    """
    Simulates a 5-man starting lineup under Head Coach Doc Rivers (Tempo=80).
    Verifies lineup friction, synergy score, and GM recommendations.
    """
    roster = [
        {"name": "Tyrese Haliburton", "ShotTendency": 96, "TouchTendency": 95},  # In equilibrium (delta=1)
        {"name": "Buddy Hield", "ShotTendency": 85, "TouchTendency": 82},       # In equilibrium (delta=3)
        {"name": "Harrison Barnes", "ShotTendency": 65, "TouchTendency": 62},   # In equilibrium (delta=3)
        {"name": "Marvin Bagley", "ShotTendency": 70, "TouchTendency": 50},     # Clamped (delta=20 > 5)
        {"name": "Richaun Holmes", "ShotTendency": 45, "TouchTendency": 45},    # In equilibrium (delta=0)
    ]
    coach_gameplan = {
        "Tempo": 80,
        "PreferredSystem": 1,
        "ActiveSystem": 4,
    }

    eval_result = bridge.evaluate_roster_tactical_alignment(roster, coach_gameplan)

    assert eval_result["roster_size"] == 5
    assert eval_result["aligned_players_count"] == 4
    assert eval_result["equilibrium_ratio"] == 0.8
    assert eval_result["coach_tempo_analysis"]["effective_tempo"] == 70.0
    assert eval_result["team_tactical_synergy_score"] > 60.0

    # Marvin Bagley should be flagged
    bagley = next(p for p in eval_result["player_evaluations"] if p["name"] == "Marvin Bagley")
    assert bagley["clamp_status"] == "NATIVE_SUPPRESSED_HIGH_USAGE_DISPARITY"
    assert bagley["effective_shot"] == 55.0  # 50 + 5
