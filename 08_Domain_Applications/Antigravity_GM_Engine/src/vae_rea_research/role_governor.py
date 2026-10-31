from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class NativeRoleGovernorResult:
    """
    Result of evaluating the native NBA2K22 Tactical Role Hierarchy & Tendency Governor.
    Distinguishes strictly between proven native assembly arithmetic and hypothesized gameplay effects.
    """
    role_tier: int
    secondary_tier: int
    raw_shot_tendency: int
    raw_touches: int
    effective_shot_tendency: int
    effective_touches: int
    raw_ratings: List[int]
    scaled_ratings: List[int]
    governor_branch: str  # "BRANCH_A_FRANCHISE_CORE", "BRANCH_B_SECONDARY_CORE", "BRANCH_C_NON_CORE_SUPPORT"
    applied_ceiling_or_floor: int
    applied_multiplier: float
    epistemological_tier: str = "PROVEN_NATIVE_ASSEMBLY"
    gameplay_validation_status: str = "PENDING_GAMEPLAY_VALIDATION"


class NativeTacticalRoleGovernor:
    """
    In-Engine Tactical Role Hierarchy and Player Tendency Governor.

    Reverse Engineering Ground Truth:
    Target: NBA2K22.exe
    Call Site RVA: 0x1226942..0x1226a8b
    Table RVA: 0x2b59798 (Ceilings uint32[4]), 0x2b597a8 (Multipliers float[4])

    Control Flow Breakdown:
    - Primary Role Tier loaded from [rsp + 0x20]
    - Secondary Role Tier loaded from [rsp + 0x24]
    - Ground Truth Table at RVA 0x2b59798:
        Tier 0 (Deep Bench): Ceiling = 92, Multiplier = 0.9400
        Tier 1 (Rotation Support): Ceiling = 83, Multiplier = 0.9600
        Tier 2 (Secondary Core): Ceiling = 74, Multiplier = 0.9800
        Tier 3 (Franchise Core): Ceiling = 0 (Unconstrained), Multiplier = 1.0000

    Branch A (Dual Tier 3, RVA 0x1226963):
        Both [rsp + 0x20] == 3 and [rsp + 0x24] == 3.
        Raw Shot Tendency and Touches are directly passed to [rdi + 0x2dd] and [rdi + 0x2de].
        Bypasses table clamping and attribute scaling.

    Branch B (Secondary Core, RVA 0x1226981):
        [rsp + 0x20] == 3, but [rsp + 0x24] != 3.
        Upper Bound Clamping (Ceiling):
            effective_shot = min(raw_shot, table[rcx] - 5) via cmovl (0x1226998)
            effective_touches = min(raw_touches, table[rcx] - 5) via cmovl (0x12269c1)
        Prevents secondary core options from exceeding superstar shot volume.

    Branch C (Non-Core Support / Bench, RVA 0x12269cf):
        [rsp + 0x20] != 3.
        Lower Bound Clamping (Floor):
            effective_shot = max(raw_shot, table[rcx]) via cmovg (0x12269e8)
            effective_touches = max(raw_touches, table[rcx]) via cmovg (0x1226a0d)
        Attribute Scaling (RVA 0x1226a18..0x1226a8b):
            5 offensive ratings [rdi + 0x2d1..0x2d5] are multiplied by table_mult[rbx] (0.94..0.98).
    """

    # Ground truth values read from live process at RVA 0x2b59798 and 0x2b597a8
    NATIVE_ROLE_TABLE_CEILINGS: Tuple[int, int, int, int] = (92, 83, 74, 0)
    NATIVE_ROLE_TABLE_MULTIPLIERS: Tuple[float, float, float, float] = (0.94, 0.96, 0.98, 1.00)

    ROLE_NAMES = {
        0: "Deep Bench / Reserve",
        1: "Rotation Support / Role Player",
        2: "Secondary Core / Co-Star",
        3: "Franchise Core / Primary Superstar",
    }

    @classmethod
    def evaluate(
        cls,
        role_tier: int,
        secondary_tier: int,
        raw_shot_tendency: int,
        raw_touches: int,
        raw_ratings: Optional[List[int]] = None,
    ) -> NativeRoleGovernorResult:
        """
        Executes the exact native assembly logic of RVA 0x1226942..0x1226a8b.
        """
        if raw_ratings is None:
            raw_ratings = [75, 75, 75, 75, 75]

        # Clamp input role index to valid table range [0, 3]
        safe_primary = max(0, min(3, int(role_tier)))
        safe_secondary = max(0, min(3, int(secondary_tier)))

        shot = max(0, min(100, int(raw_shot_tendency)))
        touches = max(0, min(100, int(raw_touches)))

        # Branch A: Dual Tier 3 (Franchise Core Option)
        if safe_primary == 3 and safe_secondary == 3:
            return NativeRoleGovernorResult(
                role_tier=safe_primary,
                secondary_tier=safe_secondary,
                raw_shot_tendency=shot,
                raw_touches=touches,
                effective_shot_tendency=shot,
                effective_touches=touches,
                raw_ratings=list(raw_ratings),
                scaled_ratings=list(raw_ratings),
                governor_branch="BRANCH_A_FRANCHISE_CORE",
                applied_ceiling_or_floor=0,
                applied_multiplier=1.00,
                epistemological_tier="PROVEN_NATIVE_ASSEMBLY",
                gameplay_validation_status="PENDING_GAMEPLAY_VALIDATION",
            )

        # Branch B: Primary 3, Secondary != 3 (Secondary Core Option)
        if safe_primary == 3 and safe_secondary != 3:
            table_val = cls.NATIVE_ROLE_TABLE_CEILINGS[safe_secondary]
            discounted_ceiling = max(0, table_val - 5)
            # 0x1226992: cmp (table - 5), raw_shot; cmovl ecx, eax -> min(raw, ceiling - 5)
            effective_shot = min(shot, discounted_ceiling)
            # 0x12269ba: cmp (table - 5), raw_touches; cmovl edx, ecx -> min(raw, ceiling - 5)
            effective_touches = min(touches, discounted_ceiling)

            return NativeRoleGovernorResult(
                role_tier=safe_primary,
                secondary_tier=safe_secondary,
                raw_shot_tendency=shot,
                raw_touches=touches,
                effective_shot_tendency=effective_shot,
                effective_touches=effective_touches,
                raw_ratings=list(raw_ratings),
                scaled_ratings=list(raw_ratings),  # Branch B does not execute rating scaling
                governor_branch="BRANCH_B_SECONDARY_CORE",
                applied_ceiling_or_floor=discounted_ceiling,
                applied_multiplier=1.00,
                epistemological_tier="PROVEN_NATIVE_ASSEMBLY",
                gameplay_validation_status="PENDING_GAMEPLAY_VALIDATION",
            )

        # Branch C: Non-Core Support / Bench (Primary != 3)
        table_val = cls.NATIVE_ROLE_TABLE_CEILINGS[safe_primary]
        multiplier = cls.NATIVE_ROLE_TABLE_MULTIPLIERS[safe_primary]

        # 0x12269dd: cmp table, raw_shot; cmovg edx, eax -> max(raw, table)
        effective_shot = max(shot, table_val)
        # 0x12269fd: cmp table, raw_touches; cmovg r8d, ecx -> max(raw, table)
        effective_touches = max(touches, table_val)

        # 0x1226a18..0x1226a8b: 5 offensive rating channels scaled by multiplier
        scaled_ratings = []
        for r in raw_ratings[:5]:
            scaled = int(round(float(r) * multiplier))
            scaled_ratings.append(max(0, min(99, scaled)))

        return NativeRoleGovernorResult(
            role_tier=safe_primary,
            secondary_tier=safe_secondary,
            raw_shot_tendency=shot,
            raw_touches=touches,
            effective_shot_tendency=effective_shot,
            effective_touches=effective_touches,
            raw_ratings=list(raw_ratings),
            scaled_ratings=scaled_ratings,
            governor_branch="BRANCH_C_NON_CORE_SUPPORT",
            applied_ceiling_or_floor=table_val,
            applied_multiplier=multiplier,
            epistemological_tier="PROVEN_NATIVE_ASSEMBLY",
            gameplay_validation_status="PENDING_GAMEPLAY_VALIDATION",
        )

    @classmethod
    def create_telemetry_validation_spec(cls) -> Dict[str, Any]:
        """
        Defines the future telemetry logging and telemetry comparison contract
        for validating the real-world competitive effects of the Tactical Role Governor.
        """
        return {
            "mechanism_id": "TACTICAL_ROLE_HIERARCHY_GOVERNOR",
            "epistemological_status": "ASSEMBLY_PROVEN_GAMEPLAY_PENDING",
            "native_assembly_sites": ["0x1226942..0x1226a8b", "0x2b59798", "0x2b597a8"],
            "monitored_telemetry_metrics": [
                "gameplay.player_role_tier",
                "gameplay.actual_fga_per_36",
                "gameplay.actual_usage_pct",
                "gameplay.shot_selection_distribution",
                "gameplay.offensive_efficiency_per_possession",
            ],
            "validation_hypotheses": [
                {
                    "hypothesis_id": "H_ROLE_CEILING_SUPPRESSION",
                    "description": "Secondary core players with ShotTendency > (Ceiling - 5) exhibit clamped FGA in live/sim games.",
                    "comparison_condition": "Player FGA in Tier 2 vs Tier 3 with identical raw ShotTendency 99.",
                    "verification_gate": "PENDING_GAMEPLAY_VALIDATION",
                },
                {
                    "hypothesis_id": "H_ROLE_FLOOR_ACTIVITY",
                    "description": "Bench support players with ShotTendency < Table Floor maintain minimum shot attempts.",
                    "comparison_condition": "Player FGA in Tier 0 vs Tier 1 with raw ShotTendency 10.",
                    "verification_gate": "PENDING_GAMEPLAY_VALIDATION",
                },
                {
                    "hypothesis_id": "H_RATING_ATTENUATION",
                    "description": "Supporting role players shoot lower eFG% due to 0.94x-0.98x attribute multiplier scaling.",
                    "comparison_condition": "True shooting % across role tiers with normalized badges.",
                    "verification_gate": "PENDING_GAMEPLAY_VALIDATION",
                },
            ],
        }
