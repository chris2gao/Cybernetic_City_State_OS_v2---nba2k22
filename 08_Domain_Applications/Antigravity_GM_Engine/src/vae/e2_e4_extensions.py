"""
VAE E2–E4 Domain Scope Extensions & Bounded Safety Guardrails.
Provides boundary contracts and deterministic rejection paths for E2, E3, and E4.
Note (P2-11): These components represent bounded contract guardrails and rejection gates,
not fully operational native execution slices.
Note (P2-12): Distinguishes current adapter capability limitations from engine impossibility.
"""

from typing import Dict, Any, Tuple, List, Optional
from .contracts import TrialPreflight, PreflightStatus, EvidenceTier


class VAEE2E4ScopeGuard:
    """
    Enforces scope boundaries and negative failure paths across E2, E3, and E4 domains.
    Serves as safety gates preventing out-of-scope operations.
    """

    # ---------------------------------------------------------------------
    # E2: Coach / Rotation / Strategy Guardrails
    # ---------------------------------------------------------------------
    @staticmethod
    def validate_coach_minutes_request(
        player_id: int,
        minutes: int,
        roster_size: int,
    ) -> Tuple[bool, str]:
        """
        Validates single player minutes against physical bounds (0..48) and roster limit (15).
        """
        if not (0 <= minutes <= 48):
            return False, f"MINUTES_OUT_OF_RANGE: {minutes} not in 0..48"
        if roster_size > 15:
            return False, f"ROSTER_OVERFLOW: roster size {roster_size} exceeds 15"
        return True, "Valid single-player minutes request"

    @staticmethod
    def reject_full_rotation_timeline_override() -> Tuple[bool, str]:
        """
        Rejects external 48-minute rotation timeline full override (GAP-RT-02).
        """
        return False, "UNSUPPORTED_TIMELINE_OVERRIDE: 48-minute rotation timeline commit has no native ABI bound"

    # ---------------------------------------------------------------------
    # E3: Franchise / Trade / Roster Guardrails
    # ---------------------------------------------------------------------
    @staticmethod
    def validate_trade_teams(team_ids: List[int]) -> Tuple[bool, str]:
        """
        Enforces dual-team trade boundary for current adapter (P2-12).
        Rejects 3-team trades as unsupported by current tooling (engine status remains UNKNOWN).
        """
        if len(team_ids) == 2:
            return True, "Valid dual-team trade structure"
        if len(team_ids) == 3:
            return False, "THREE_TEAM_TRADE_UNSUPPORTED_BY_CURRENT_TOOLS: Proposal buffer adapter currently supports 2 teams only; native 3-team engine support is unverified / UNKNOWN"
        return False, f"INVALID_TEAM_COUNT: Expected 2 teams, got {len(team_ids)}"

    @staticmethod
    def validate_roster_counts_after_trade(
        regular_count: int,
        active_count: int,
    ) -> Tuple[bool, str]:
        """
        Enforces 15 regular and 13 active player constraints.
        """
        if regular_count > 15:
            return False, f"REGULAR_ROSTER_EXCEEDED: {regular_count} > 15"
        if active_count > 13:
            return False, f"ACTIVE_ROSTER_EXCEEDED: {active_count} > 13"
        return True, "Roster counts within safe limits"

    # ---------------------------------------------------------------------
    # E4: Player Attributes / Training Presets Guardrails
    # ---------------------------------------------------------------------
    @staticmethod
    def reject_player_training_preset_write(
        position: int,
        player_type: int,
    ) -> Tuple[bool, str]:
        """
        Rejects player training preset write attempts until real UI audit completes (GAP-ST-01 / GAP-RT-01).
        """
        return (
            False,
            "PLAYER_TRAINING_PRESET_SETTER_NOT_BOUND: UI menu options for position "
            f"{position} and player_type {player_type} remain UNKNOWN pending live UI audit",
        )
