from __future__ import annotations

import json
import math
import os
from typing import Any, Dict, List, Optional, Tuple


class ExperimentalTacticalDecisionBridge:
    """
    Experimental, non-native tactical simulation bridge.

    STATUS: EXPERIMENTAL_HEURISTIC_MODEL_NON_NATIVE
    NOTE: The mathematical formulas in this bridge represent experimental heuristics
    derived from reverse engineering research leads. They are NOT certified native game laws
    and must NOT be used as rigid deterministic production rules without empirical validation.

    Reverse Engineering Grounding:
    1. Role Ceiling Governor (RVA 0x1226942..0x12269a6):
       Native assembly verifies that players with core role tier (rcx=3) bypass ceilings,
       whereas secondary players (rcx!=3) are clamped to (role_ceiling - 5) if raw tendency exceeds it.
    2. Coach Tempo Bounds (RVA 0x120ba72..0x120babb):
       Native assembly proves that tempo modifiers are clamped strictly to [10, 70].
    """

    MODEL_TIER = "EXPERIMENTAL_HEURISTIC"
    IS_NATIVE_LAW = False

    # Heuristic constants for macro estimation (clearly labeled as experimental)
    HEURISTIC_BASE_POSSESSIONS = 88.0
    HEURISTIC_TEMPO_SLOPE = 0.28
    COACH_TEMPO_MIN_BOUND = 10.0
    COACH_TEMPO_MAX_BOUND = 70.0

    def __init__(self, repo_root: Optional[str] = None) -> None:
        if repo_root is None:
            cur = os.path.abspath(__file__)
            repo_root = os.path.abspath(os.path.join(cur, "..", "..", "..", "..", ".."))
        self.repo_root = repo_root
        self.run_dir = os.path.join(
            self.repo_root, "01_os", "07_content", "_runs",
            "run-20261030-nba2k22-vae-rea-single-field-loop-001"
        )
        self.records_dir = os.path.join(self.run_dir, "06_执行", "field_records")

    def calculate_role_ceiling_governor(
        self,
        shot_tendency: float,
        touches: float,
        role_tier: int = 3,
        role_ceiling: float = 85.0,
    ) -> Dict[str, Any]:
        """
        Evaluates the Role-Based Tactical Shot Ceiling Governor (RVA 0x1226942..0x12269a6).

        Native Assembly Behavior:
        - Checks role at [rsp + 0x20] / [rsp + 0x24] against 3 (Primary Core option).
        - If role == 3: Raw shot tendency is stored unconstrained into [rdi + 0x2dd].
        - If role != 3: Role ceiling is loaded from [rsi + rcx*4 + 0x2b59798],
          discounted by 5 (sub edx, 5), and if (ceiling - 5) < shot_tendency,
          effective shot tendency is clamped to (ceiling - 5).
        """
        is_franchise_core = (role_tier == 3)
        effective_ceiling = max(0.0, role_ceiling - 5.0)

        if is_franchise_core:
            effective_shot = shot_tendency
            is_suppressed = False
            friction_score = 0.0
            clamp_status = "FRANCHISE_CORE_UNCONSTRAINED"
            recommendation = "Franchise core option (tier 3); shot tendency bypasses role ceiling."
        else:
            if shot_tendency > effective_ceiling:
                effective_shot = effective_ceiling
                is_suppressed = True
                friction_score = shot_tendency - effective_ceiling
                clamp_status = "ROLE_CEILING_SUPPRESSED"
                recommendation = (
                    f"Non-core role player (tier {role_tier}) shot tendency ({shot_tendency:.1f}) "
                    f"exceeds discounted role ceiling ({effective_ceiling:.1f}). "
                    f"In-engine AI governor clamps effective shot attempts."
                )
            else:
                effective_shot = shot_tendency
                is_suppressed = False
                friction_score = 0.0
                clamp_status = "WITHIN_ROLE_CEILING"
                recommendation = "Shot tendency is within secondary role ceiling."

        return {
            "model_status": "EXPERIMENTAL_HEURISTIC",
            "is_native_law": False,
            "role_tier": role_tier,
            "raw_shot_tendency": shot_tendency,
            "touches": touches,
            "effective_role_ceiling": effective_ceiling,
            "effective_shot_tendency": round(effective_shot, 1),
            "is_suppressed": is_suppressed,
            "friction_score": round(friction_score, 2),
            "clamp_status": clamp_status,
            "recommendation": recommendation,
        }

    def calculate_effective_coach_tempo(self, raw_tempo: float) -> Dict[str, Any]:
        """
        Evaluates Coach Pacing Engine Bounds (RVA 0x120ba72..0x120babb).

        Native Assembly Behavior:
        - eax = Tempo - 50; ecx = eax * 60; edx = ecx / 100; ecx = edx + 10;
        - cmp ecx, 70; cmovg ecx, 70; cmp ecx, 10; cmovl ecx, 10.
        - Clamping bounds [10, 70] are proven by native constants 0x46 and 0x0a.
        """
        raw_val = float(raw_tempo)
        effective_tempo = min(self.COACH_TEMPO_MAX_BOUND, max(self.COACH_TEMPO_MIN_BOUND, raw_val))
        is_saturated = raw_val > self.COACH_TEMPO_MAX_BOUND
        is_choked = raw_val < self.COACH_TEMPO_MIN_BOUND

        # Heuristic pace estimation for macro simulation
        estimated_pace = self.HEURISTIC_BASE_POSSESSIONS + (effective_tempo * self.HEURISTIC_TEMPO_SLOPE)

        # Linear pace scale factor: 10 tempo -> 0.714; 50 tempo -> 0.971; 70 tempo -> 1.100
        pace_multiplier = 0.65 + (effective_tempo / 70.0) * 0.45

        return {
            "model_status": "EXPERIMENTAL_HEURISTIC",
            "is_native_law": False,
            "raw_tempo_slider": raw_val,
            "effective_tempo": effective_tempo,
            "is_saturated": is_saturated,
            "is_choked": is_choked,
            "estimated_pace_possessions": round(estimated_pace, 2),
            "pace_multiplier_scale": round(pace_multiplier, 4),
            "saturation_loss": round(raw_val - effective_tempo, 1) if is_saturated else 0.0,
            "note": (
                "Native assembly clamps tempo modifier strictly to [10, 70]. "
                "Values above 70 are saturated by native instructions."
                if is_saturated else "Within native linear bounds [10, 70]."
            ),
        }

    def evaluate_roster_tactical_alignment(
        self,
        roster: List[Dict[str, Any]],
        coach_gameplan: Dict[str, Any],
    ) -> Dict[str, Any]:
        """
        Evaluates full team roster alignment against coach gameplan using experimental heuristics.
        """
        coach_tempo = float(coach_gameplan.get("Tempo", 50))
        tempo_eval = self.calculate_effective_coach_tempo(coach_tempo)

        total_friction = 0.0
        aligned_players = 0
        player_evals = []

        for p in roster:
            name = p.get("name", "Unknown Player")
            st = float(p.get("ShotTendency", 50))
            tt = float(p.get("TouchTendency", 50))
            role_tier = int(p.get("RoleTier", 3))
            role_ceil = float(p.get("RoleCeiling", 85.0))

            gov = self.calculate_role_ceiling_governor(
                shot_tendency=st, touches=tt, role_tier=role_tier, role_ceiling=role_ceil
            )
            total_friction += gov["friction_score"]
            if not gov["is_suppressed"]:
                aligned_players += 1

            player_evals.append({
                "name": name,
                "role_tier": role_tier,
                "raw_shot": st,
                "touches": tt,
                "effective_shot": gov["effective_shot_tendency"],
                "is_suppressed": gov["is_suppressed"],
                "friction_score": gov["friction_score"],
                "clamp_status": gov["clamp_status"],
                "recommendation": gov["recommendation"],
            })

        avg_friction = total_friction / len(roster) if roster else 0.0
        equilibrium_ratio = aligned_players / len(roster) if roster else 1.0
        synergy_score = max(0.0, round(100.0 - (avg_friction * 8.0), 1))

        return {
            "model_status": "EXPERIMENTAL_HEURISTIC",
            "is_native_law": False,
            "roster_size": len(roster),
            "aligned_players_count": aligned_players,
            "equilibrium_ratio": round(equilibrium_ratio, 3),
            "team_average_friction": round(avg_friction, 2),
            "team_tactical_synergy_score": synergy_score,
            "coach_tempo_analysis": tempo_eval,
            "player_evaluations": player_evals,
            "executive_recommendation": (
                "Roster usage distribution aligns well with tactical role ceilings."
                if synergy_score >= 80.0 else
                f"Roster has {len(roster) - aligned_players} players exceeding their secondary role ceilings. "
                "Adjust player roles or lower secondary shot tendencies to avoid native clamping."
            ),
        }
