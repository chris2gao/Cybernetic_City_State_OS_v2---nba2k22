"""
VAE Basketball Diagnosis Engine (R02).
Analyzes observed symptoms against basketball common sense and known 2K mechanics.
"""

from typing import List, Dict, Any, Optional
import uuid
from .contracts import IssueDiagnosis, DiagnosisStatus


class VAEDiagnosisEngine:
    """
    Evaluates reported symptoms, checks for plausible causes and confounders,
    and supports NO_CHANGE decisions when changes would violate basketball reality.
    """

    def diagnose_issue(
        self,
        game_ref: str,
        observed_symptom: str,
        domain: str = "E1",  # "E1" | "E2" | "E3" | "E4"
    ) -> IssueDiagnosis:
        issue_id = f"issue-{uuid.uuid4().hex[:8]}"

        # E1: Gameplay slider symptom
        if domain == "E1":
            if "three_point_percentage_too_high" in observed_symptom.lower():
                return IssueDiagnosis(
                    issue_id=issue_id,
                    game_ref=game_ref,
                    observed_symptom=observed_symptom,
                    basketball_source_ref="NBA_LEAGUE_AVG_3PT_35_PCT",
                    plausible_causes=[
                        "slider_user_3pt_success_too_high",
                        "slider_cpu_defensive_pressure_too_low",
                        "hall_of_fame_difficulty_override",
                    ],
                    confounders=[
                        "small_sample_under_10_games",
                        "played_normalize_active_with_short_quarters",
                        "star_shooter_usage_skew",
                    ],
                    no_change_decision=False,
                    status=DiagnosisStatus.DIAGNOSED,
                )
            elif "fatigue_too_rapid" in observed_symptom.lower():
                return IssueDiagnosis(
                    issue_id=issue_id,
                    game_ref=game_ref,
                    observed_symptom=observed_symptom,
                    basketball_source_ref="NBA_LOAD_MANAGEMENT_GUIDE",
                    plausible_causes=["fatigue_rate_slider_too_high", "coach_high_tempo"],
                    confounders=["back_to_back_schedule", "short_bench_depth"],
                    no_change_decision=False,
                    status=DiagnosisStatus.DIAGNOSED,
                )

        # Baseline fallback
        return IssueDiagnosis(
            issue_id=issue_id,
            game_ref=game_ref,
            observed_symptom=observed_symptom,
            basketball_source_ref="GENERAL_BASKETBALL_THEORY",
            plausible_causes=["unspecified_gameplay_variance"],
            confounders=["small_sample_size", "difficulty_slider_mix"],
            no_change_decision=True,  # Default to conservative NO_CHANGE when root cause is uncertain
            status=DiagnosisStatus.NO_CHANGE,
        )
