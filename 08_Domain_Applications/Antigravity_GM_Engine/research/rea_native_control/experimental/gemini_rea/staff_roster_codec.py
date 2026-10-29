"""GM Staff and Roster Management Codec for NBA 2K22 (Wave-03 W03-08)
Encodes and decodes Roster Movement, Active/Inactive Status, Waiving,
and Staff Role Assignments (Roles 8..20: Head Coach, Assistant, Scouts, Trainers).

Binary Verified Anchors:
- 0x12d0340: Team_ReleasePlayerInternal(TeamFranchise* rcx, uint32 slot_index)
  Updates roster count at [rcx + 0xee8] and unbinds player.
- 0x1327590: Staff_ValidateRoleAndDispatch(uint32 role_id)
  Enforces role_id - 8 <= 0xc (Roles 8 to 20 valid: Head Coach to Staff roles).
- 0xedf000: Player_GetRosterSlot(PlayerRosterSlot* rcx)
  Bits 22..25 of [rcx + 0xf78] represent 4-bit depth chart slot (0..14).
"""
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from enum import IntEnum

class StaffRole(IntEnum):
    HEAD_COACH = 8
    ASSISTANT_COACH = 9
    LEAD_SCOUT = 10
    SCOUT = 11
    HEAD_TRAINER = 12
    TRAINER = 13
    CFO = 14
    GM_ASSISTANT = 15

MIN_ACTIVE_ROSTER = 13
MAX_ACTIVE_ROSTER = 15
MAX_TWO_WAY_ROSTER = 2
MAX_TOTAL_ROSTER = 17

@dataclass
class RosterPlayerState:
    player_id: int
    slot_index: int       # 0..14 (0..4 = Starting 5)
    is_active: bool = True
    is_two_way: bool = False
    is_g_league: bool = False

@dataclass
class StaffMember:
    staff_id: int
    role: StaffRole
    contract_years: int
    annual_salary: int
    offense_rating: int = 75
    defense_rating: int = 75
    potential_rating: int = 75

class StaffRosterCodec:
    """Manages Roster Legality and Staff Structure representations."""

    @staticmethod
    def validate_roster_legality(players: List[RosterPlayerState]) -> Tuple[bool, str]:
        """Validates NBA roster composition rules."""
        active_count = sum(1 for p in players if p.is_active and not p.is_two_way and not p.is_g_league)
        two_way_count = sum(1 for p in players if p.is_two_way)
        total_count = len(players)

        if total_count > MAX_TOTAL_ROSTER:
            return False, f"Total roster size {total_count} exceeds maximum {MAX_TOTAL_ROSTER}"
        if two_way_count > MAX_TWO_WAY_ROSTER:
            return False, f"Two-way players {two_way_count} exceed maximum {MAX_TWO_WAY_ROSTER}"
        if active_count > MAX_ACTIVE_ROSTER:
            return False, f"Active players {active_count} exceed maximum {MAX_ACTIVE_ROSTER}"
        if active_count < MIN_ACTIVE_ROSTER:
            return False, f"Active players {active_count} below minimum {MIN_ACTIVE_ROSTER}"

        return True, "Valid"

    @staticmethod
    def validate_staff_role(role_id: int) -> bool:
        """Simulates native 0x1327590: checks if role_id - 8 <= 0xc."""
        normalized = role_id - 8
        return 0 <= normalized <= 0xc

    @staticmethod
    def simulate_waive_player(roster: List[RosterPlayerState], player_id: int) -> List[RosterPlayerState]:
        """Simulates native 0x12d0340: removes player from team roster and shifts remaining slots."""
        new_roster = [p for p in roster if p.player_id != player_id]
        for idx, p in enumerate(new_roster):
            p.slot_index = idx
        return new_roster
