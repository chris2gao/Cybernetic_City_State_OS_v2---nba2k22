from __future__ import annotations

import decimal
import math
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


@dataclass
class NativeRoleGovernorResult:
    """
    Result of evaluating the static disassembly model of the NBA2K22 Tactical Role Hierarchy & Governor.
    Strictly distinguishes proven register assembly arithmetic from hypothesized gameplay effects.
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
    domain_clamped: bool = False
    epistemological_tier: str = "STATIC_DISASSEMBLY_LEAD"
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
        Tier 0 (Deep Bench): Floor/Ceiling = 92, Multiplier = 0.9400
        Tier 1 (Rotation Support): Floor/Ceiling = 83, Multiplier = 0.9600
        Tier 2 (Secondary Core): Floor/Ceiling = 74, Multiplier = 0.9800
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
        Activity Floor Clamping (0x12269dd..0x12269e8):
            cmp ecx, r8d; cmovg edx, eax -> effective_shot = max(raw_shot, table[rcx])
            cmp edx, eax; cmovg r8d, ecx -> effective_touches = max(raw_touches, table[rcx])
        Attribute Scaling (RVA 0x1226a18..0x1226a8b):
            5 offensive ratings [rdi + 0x2d1..0x2d5] are multiplied by table_mult[rbx] (0.94..0.98)
            converted via cvtss2si using banker's rounding (round half to even).
    """

    # Values extracted from live process at RVA 0x2b59798 and 0x2b597a8
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
        strict: bool = False,
    ) -> NativeRoleGovernorResult:
        """
        Executes the exact assembly logic of RVA 0x1226942..0x1226a8b.
        """
        if raw_ratings is None:
            raw_ratings = [75, 75, 75, 75, 75]

        # Domain check for role_tier
        domain_clamped = False
        if role_tier < 0 or role_tier > 3 or secondary_tier < 0 or secondary_tier > 3:
            if strict:
                raise ValueError(f"Role tiers must be in [0, 3], got primary={role_tier}, secondary={secondary_tier}")
            domain_clamped = True

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
                domain_clamped=domain_clamped,
                epistemological_tier="STATIC_DISASSEMBLY_LEAD",
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
                domain_clamped=domain_clamped,
                epistemological_tier="STATIC_DISASSEMBLY_LEAD",
                gameplay_validation_status="PENDING_GAMEPLAY_VALIDATION",
            )

        # Branch C: Non-Core Support / Bench (Primary != 3)
        table_val = cls.NATIVE_ROLE_TABLE_CEILINGS[safe_primary]
        multiplier = cls.NATIVE_ROLE_TABLE_MULTIPLIERS[safe_primary]

        # 0x12269dd: cmp table, raw_shot; cmovg edx, eax -> max(raw, table)
        effective_shot = max(shot, table_val)
        # 0x12269fd: cmp table, raw_touches; cmovg r8d, ecx -> max(raw, table)
        effective_touches = max(touches, table_val)

        # 0x1226a18..0x1226a8b: 5 offensive rating channels scaled by multiplier via cvtss2si (banker's rounding)
        scaled_ratings = []
        for r in raw_ratings[:5]:
            prod = decimal.Decimal(str(float(r))) * decimal.Decimal(str(multiplier))
            scaled = int(prod.quantize(decimal.Decimal('1'), rounding=decimal.ROUND_HALF_EVEN))
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
            domain_clamped=domain_clamped,
            epistemological_tier="STATIC_DISASSEMBLY_LEAD",
            gameplay_validation_status="PENDING_GAMEPLAY_VALIDATION",
        )

    @classmethod
    def create_telemetry_validation_spec(cls) -> Dict[str, Any]:
        """
        Defines the future telemetry logging semantic requirements for Tactical Role Governor.
        Does NOT prescribe physical database tables, SQL types, or log file formats.
        """
        return {
            "hypothesis_id": "VAL_CONTRACT_FGA_SUPPRESSION",
            "target_mechanism": "TACTICAL_ROLE_HIERARCHY_GOVERNOR",
            "epistemological_status": "STATIC_DISASSEMBLY_LEAD",
            "disassembly_call_sites": ["0x1226942..0x1226a8b", "0x2b59798", "0x2b597a8"],
            "required_metrics": [
                {
                    "metric_name": "player_role_tier",
                    "semantic_role": "independent_variable",
                    "observation_type": "DIRECT_ROSTER_READ",
                },
                {
                    "metric_name": "actual_fga_per_36",
                    "semantic_role": "primary_outcome",
                    "observation_type": "DERIVED_FROM_BOXSCORE",
                },
                {
                    "metric_name": "actual_usage_pct",
                    "semantic_role": "secondary_outcome",
                    "observation_type": "DERIVED_FROM_PLAY_BY_PLAY",
                },
                {
                    "metric_name": "normalize_stats_rule",
                    "semantic_role": "confounder_control",
                    "observation_type": "DIRECT_SETTING_READ",
                },
            ],
            "comparison_conditions": [
                {
                    "condition_name": "SECONDARY_CORE_CEILING_SUPPRESSION",
                    "group_a": "Players with RoleTier=2 and raw ShotTendency > 85",
                    "group_b": "Players with RoleTier=3 and raw ShotTendency > 85",
                    "expected_trend": "Group A exhibits suppressed FGA/36 relative to unconstrained Group B.",
                },
                {
                    "condition_name": "BENCH_FLOOR_ACTIVITY_CHECK",
                    "group_a": "Players with RoleTier=0 and raw ShotTendency < 30",
                    "group_b": "Players with RoleTier=1 and raw ShotTendency < 30",
                    "expected_trend": "Group A and B maintain baseline shot attempts conforming to role floor activity.",
                },
            ],
            "fallback_if_unrecorded": "FLAG_AS_UNKNOWN",
        }
