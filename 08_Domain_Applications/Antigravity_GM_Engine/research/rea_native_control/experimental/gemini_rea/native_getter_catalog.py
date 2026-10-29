"""Native Getter and Readback Catalog for NBA 2K22 (Wave-03 W03-12)
Provides structured, typed readback helpers and address catalogs for Coach,
Roster, Contracts, Draft, Scouting, and Player statistics.

Binary Verified Anchors:
- Player Entity: 0xf3fa80 (Player_FindById)
- Player Stats: 0x978360 (Player_GetStatUI)
- Player Badges: 0x97b870 (Player_GetBadgeEffectiveLevel)
- Player Salary: 0x9888b0 (Player_GetSalary)
- Player Remaining Years: 0x9886c0 (Player_GetRemainingContractYears)
- Playbook Play Count: 0x149ae80 (Playbook_GetAssignedCount, [PlaybookManager+0x7fc])
- Season Phase: 0x140edf010 (Franchise_GetSeasonPhase)
- FA Pool Count: 0x9b5bf0 (FA_GetAvailableCount)
- Draft Pick Read: 0x92a6a0 (Draft_GetCurrentSelection)
"""
from dataclasses import dataclass
from typing import Dict, Any, List, Optional

@dataclass
class NativeGetterDefinition:
    getter_id: str
    category: str
    rva: Optional[str]
    target_struct: str
    field_offset: Optional[str]
    return_type: str
    description: str

GETTER_CATALOG: Dict[str, NativeGetterDefinition] = {
    # 1. Player Getters
    "player.by_id": NativeGetterDefinition(
        "player.by_id", "PLAYER", "0xf3fa80", "PlayerRegistry", "None", "Player*", "Resolves 64-bit Player pointer by uint16 ID"
    ),
    "player.get_stat": NativeGetterDefinition(
        "player.get_stat", "PLAYER", "0x978360", "Player", "JumpTable(0x9b)", "uint32", "Reads attribute or tendency value (0..99)"
    ),
    "player.get_badge_level": NativeGetterDefinition(
        "player.get_badge_level", "PLAYER", "0x97b870", "Player", "BadgeContext", "uint8", "Returns badge effective tier (0..4)"
    ),
    "player.get_salary": NativeGetterDefinition(
        "player.get_salary", "PLAYER", "0x9888b0", "PlayerContract", "+0x8", "uint32", "Returns current season salary in USD"
    ),
    "player.get_contract_years": NativeGetterDefinition(
        "player.get_contract_years", "PLAYER", "0x9886c0", "PlayerContract", "+0x4", "uint16", "Returns remaining contract years"
    ),
    "player.get_roster_slot": NativeGetterDefinition(
        "player.get_roster_slot", "PLAYER", "0xedf000", "Player", "+0xf78 bits 22..25", "uint8", "Returns depth chart slot (0..14)"
    ),
    "player.get_minutes": NativeGetterDefinition(
        "player.get_minutes", "PLAYER", "0x11b2bb0", "PlayerRosterSlot", "+0xf8 bits 18..24", "uint8", "Returns assigned minutes (0..48)"
    ),
    "player.get_playtypes": NativeGetterDefinition(
        "player.get_playtypes", "PLAYER", "0xf1e370", "Player", "+0x168 bits 0..15", "uint16", "Returns 4x 4-bit packed playtypes"
    ),

    # 2. Coach & Gameplan Getters
    "coach.get_coachdata": NativeGetterDefinition(
        "coach.get_coachdata", "COACH", "0x1409cd2a0", "Team", "+0xce8", "COACHDATA*", "Resolves Coach runtime execution context"
    ),
    "coach.get_default_gameplan": NativeGetterDefinition(
        "coach.get_default_gameplan", "COACH", "0x1258b59", "TeamFranchise", "+0x7854", "GAMEPLAN*", "Returns 880-byte default gameplan"
    ),
    "coach.get_dirty_flags": NativeGetterDefinition(
        "coach.get_dirty_flags", "COACH", "0x131f11a", "TeamFranchise", "+0x7bc4", "uint32", "Bit 0: gameplan dirty, Bit 1: coach settings dirty"
    ),
    "coach.get_poe_settings": NativeGetterDefinition(
        "coach.get_poe_settings", "COACH", "0x146ebfa", "COACHDATA", "+0x13c", "uint32", "Packs 6x 5-bit POE settings"
    ),
    "coach.get_tactical_system": NativeGetterDefinition(
        "coach.get_tactical_system", "COACH", "0x146eaf6", "COACHDATA", "+0x148 bits 17..24", "uint8", "Returns active tactical system enum"
    ),

    # 3. Playbook Getters
    "playbook.get_count": NativeGetterDefinition(
        "playbook.get_count", "PLAYBOOK", "0x149ae80", "PlaybookManager", "+0x7fc", "uint32", "Returns assigned play count (max 68)"
    ),

    # 4. Roster & Staff Getters
    "team.get_roster_count": NativeGetterDefinition(
        "team.get_roster_count", "ROSTER", "0x12d039b", "TeamFranchise", "+0xee8", "uint32", "Returns active roster player count"
    ),

    # 5. Contract & Free Agency Getters
    "sign.get_fa_count": NativeGetterDefinition(
        "sign.get_fa_count", "CONTRACT", "0x9b5bf0", "FreeAgencyManager", "+0x0", "uint32", "Returns total available free agents"
    ),
    "franchise.get_season_phase": NativeGetterDefinition(
        "franchise.get_season_phase", "FRANCHISE", "0x140edf010", "FranchiseContext", "Global", "uint32", "Returns season phase (e.g. 0x16 = Options)"
    ),

    # 6. Draft & Scouting Getters
    "draft.get_current_pick": NativeGetterDefinition(
        "draft.get_current_pick", "DRAFT", "0x92a6a0", "DraftManager", "+0xbc, +0xc0", "DraftPick*", "Returns active draft pick pointer"
    ),
    "scout.get_trip_budget": NativeGetterDefinition(
        "scout.get_trip_budget", "SCOUT", "0x1261d4a", "ScoutContext", "+0x1068 bits 15..18", "uint8", "Returns remaining scout trip budget"
    ),
}

class NativeGetterCatalog:
    """Catalog lookup service for Native Getters."""

    @staticmethod
    def get(getter_id: str) -> Optional[NativeGetterDefinition]:
        return GETTER_CATALOG.get(getter_id)

    @staticmethod
    def list_by_category(category: str) -> List[NativeGetterDefinition]:
        return [g for g in GETTER_CATALOG.values() if g.category == category]

    @staticmethod
    def get_summary_dict() -> Dict[str, Any]:
        return {
            gid: {
                "category": g.category,
                "rva": g.rva,
                "target_struct": g.target_struct,
                "offset": g.field_offset,
                "return_type": g.return_type,
                "description": g.description
            }
            for gid, g in GETTER_CATALOG.items()
        }
