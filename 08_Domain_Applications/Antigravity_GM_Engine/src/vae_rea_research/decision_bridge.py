from __future__ import annotations

import json
import math
import os
from typing import Any, Dict, List, Optional, Tuple

from src.vae_rea_research.role_governor import NativeTacticalRoleGovernor
from src.vae_rea_research.coach_pacing import NativeCoachPacingEngine


class ExperimentalTacticalDecisionBridge:
    """
    Experimental, non-native tactical simulation bridge.

    STATUS: EXPERIMENTAL_HEURISTIC_MODEL_NON_NATIVE
    NOTE: The mathematical formulas in this bridge represent experimental heuristics
    derived from reverse engineering research leads. They are NOT certified native game laws
    and must NOT be used as rigid deterministic production rules without empirical validation.

    Reverse Engineering Grounding & Epistemological Demarcation:
    1. Role Ceiling Governor (RVA 0x1226942..0x1226a8b):
       Static disassembly reveals 3 branches:
       - Branch A: Dual Tier 3 (Core) bypasses ceilings.
       - Branch B: Tier 3 Primary with Secondary != 3 clamped to (ceiling - 5).
       - Branch C: Tier < 3 clamped to table floor and ratings scaled by table multiplier.
    2. Coach Tempo Bounds (RVA 0x120ba72..0x120babb):
       Static disassembly proves that internal tempo modifiers are clamped strictly to [10, 70]
       via fixed-point formula: clamp(10, 70, (Tempo - 50) * 1.2 + 10).
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
        secondary_tier: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Evaluates the Role-Based Tactical Shot Ceiling Governor.
        Explicitly separates experimental heuristic results from static disassembly leads.
        """
        if secondary_tier is None:
            secondary_tier = role_tier

        # 1. Experimental Heuristic Track (user-supplied role_ceiling)
        is_franchise_core = (role_tier == 3)
        effective_ceiling = max(0.0, float(role_ceiling) - 5.0)

        if is_franchise_core:
            heuristic_effective_shot = float(shot_tendency)
            is_suppressed = False
            friction_score = 0.0
            clamp_status = "FRANCHISE_CORE_UNCONSTRAINED"
            recommendation = "Franchise core option (tier 3); shot tendency bypasses role ceiling."
        else:
            if shot_tendency > effective_ceiling:
                heuristic_effective_shot = effective_ceiling
                is_suppressed = True
                friction_score = shot_tendency - effective_ceiling
                clamp_status = "ROLE_CEILING_SUPPRESSED"
                recommendation = (
                    f"Non-core role player (tier {role_tier}) shot tendency ({shot_tendency:.1f}) "
                    f"exceeds discounted role ceiling ({effective_ceiling:.1f}). "
                    f"Experimental heuristic clamps effective shot attempts."
                )
            else:
                heuristic_effective_shot = float(shot_tendency)
                is_suppressed = False
                friction_score = 0.0
                clamp_status = "WITHIN_ROLE_CEILING"
                recommendation = "Shot tendency is within secondary role ceiling."

        # 2. Static Disassembly Lead Track (native table 0x2b59798)
        native_eval = NativeTacticalRoleGovernor.evaluate(
            role_tier=role_tier,
            secondary_tier=secondary_tier,
            raw_shot_tendency=int(round(shot_tendency)),
            raw_touches=int(round(touches)),
            strict=False,
        )

        native_effective_shot = float(native_eval.effective_shot_tendency)
        has_cross_model_divergence = (round(heuristic_effective_shot, 1) != round(native_effective_shot, 1))

        return {
            "model_status": "EXPERIMENTAL_HEURISTIC",
            "is_native_law": False,
            "role_tier": role_tier,
            "secondary_tier": secondary_tier,
            "raw_shot_tendency": shot_tendency,
            "touches": touches,
            # Heuristic output
            "effective_role_ceiling": effective_ceiling,
            "effective_shot_tendency": round(heuristic_effective_shot, 1),
            "is_suppressed": is_suppressed,
            "friction_score": round(friction_score, 2),
            "clamp_status": clamp_status,
            "recommendation": recommendation,
            # Static disassembly reference track
            "static_disassembly_reference": {
                "branch": native_eval.governor_branch,
                "table_val": native_eval.applied_ceiling_or_floor,
                "table_multiplier": native_eval.applied_multiplier,
                "native_effective_shot": native_effective_shot,
                "native_effective_touches": float(native_eval.effective_touches),
            },
            # Cross-track divergence disclosure (INT-P0-03)
            "has_cross_model_divergence": has_cross_model_divergence,
            "divergence_note": (
                f"Heuristic effective shot ({heuristic_effective_shot:.1f}) differs from native table "
                f"disassembly lead ({native_effective_shot:.1f}). Disassembly lead applies table floor/ceiling "
                f"from RVA 0x2b59798, while heuristic evaluates supplied ceiling ({role_ceiling:.1f})."
                if has_cross_model_divergence else "Heuristic and static disassembly leads align."
            ),
        }

    def calculate_effective_coach_tempo(self, raw_tempo: float) -> Dict[str, Any]:
        """
        Evaluates Coach Pacing Engine Bounds.
        Explicitly separates slider clamping from the internal x86 fixed-point assembly modifier.
        """
        raw_val = float(raw_tempo)
        effective_tempo = min(self.COACH_TEMPO_MAX_BOUND, max(self.COACH_TEMPO_MIN_BOUND, raw_val))
        is_saturated = raw_val > self.COACH_TEMPO_MAX_BOUND
        is_choked = raw_val < self.COACH_TEMPO_MIN_BOUND

        # Static disassembly fixed-point calculation
        pacing_res = NativeCoachPacingEngine.evaluate(tempo=raw_val)

        # Heuristic pace estimation for macro simulation
        estimated_pace = self.HEURISTIC_BASE_POSSESSIONS + (effective_tempo * self.HEURISTIC_TEMPO_SLOPE)
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
            # Static disassembly reference track
            "static_disassembly_lead": {
                "bounded_modifier": pacing_res.bounded_modifier,
                "unclamped_ecx": pacing_res.unclamped_register_ecx,
                "hypothesized_net_target": pacing_res.hypothesized_net_target,
                "formula": "clamp(10, 70, (Tempo - 50) * 1.2 + 10)",
            },
            "note": (
                "Heuristic slider model clamps effective slider to [10, 70]. "
                "Native assembly fixed-point engine computes modifier = clamp(10, 70, (Tempo - 50)*1.2 + 10), "
                f"yielding internal modifier {pacing_res.bounded_modifier} for tempo {raw_val:.1f}."
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
                "has_cross_model_divergence": gov["has_cross_model_divergence"],
                "recommendation": gov["recommendation"],
            })

        total_players = len(roster)
        synergy_index = round(max(0.0, 100.0 - (total_friction * 2.5)), 1) if total_players > 0 else 100.0

        return {
            "model_status": "EXPERIMENTAL_HEURISTIC",
            "is_native_law": False,
            "coach_tempo_analysis": tempo_eval,
            "coach_tempo_eval": tempo_eval,
            "roster_size": total_players,
            "aligned_players_count": aligned_players,
            "aligned_players": aligned_players,
            "total_friction_score": round(total_friction, 2),
            "team_tactical_synergy_score": synergy_index,
            "heuristic_synergy_index": synergy_index,
            "player_evaluations": player_evals,
        }
