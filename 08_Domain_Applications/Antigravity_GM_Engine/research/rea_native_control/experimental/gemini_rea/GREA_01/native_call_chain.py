"""Native Call Chain Topology and Simulation Harness for Opponent Gameplan.

GREA-01: Research and isolated execution model for the complete native
call chain required to modify and commit an opponent gameplan in NBA 2K22.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

from .gameplan_opponent import (
    FranchiseGameplanManager,
    OpponentGameplan,
    PressureOnball,
)


class EvidenceMaturity(str, Enum):
    """Maturity level of reverse-engineered native functions."""
    LIVE_VERIFIED = "LIVE_VERIFIED"  # Verified in live memory read/call
    STATIC_DISASSEMBLED = "STATIC_DISASSEMBLED"  # Disassembled and verified in PE binary
    STATIC_CROSS_REFERENCED = "STATIC_CROSS_REFERENCED"  # Located via caller cross-references
    OFFLINE_SIMULATED = "OFFLINE_SIMULATED"  # Emulated in offline Python harness


@dataclass
class NativeFunctionSpec:
    """Specification of a reverse-engineered native function."""
    rva: str
    symbol_name: str
    signature: str
    calling_convention: str
    parameters: List[Dict[str, str]]
    returns: str
    evidence_maturity: EvidenceMaturity
    description: str
    disassembly_notes: str


NATIVE_CALL_CHAIN_SPECS: List[NativeFunctionSpec] = [
    NativeFunctionSpec(
        rva="0xfda730",
        symbol_name="GetTeamGameplanManager",
        signature="FRANCHISE_GAMEPLAN_MANAGER* (TEAM* pTeam, int flag)",
        calling_convention="__fastcall (rcx=pTeam, edx=flag)",
        parameters=[
            {"name": "pTeam", "type": "TEAM*", "register": "rcx", "description": "Pointer to owner team instance"},
            {"name": "flag", "type": "int", "register": "edx", "description": "Initialization flag (typically 0)"},
        ],
        returns="FRANCHISE_GAMEPLAN_MANAGER* (rax)",
        evidence_maturity=EvidenceMaturity.STATIC_DISASSEMBLED,
        description="Resolves franchise global pointer (0x3c23170) and team index (0xedefe0) to index manager array at Franchise+0x19cfd0.",
        disassembly_notes="call 0xedefe0; mov rax, [0x3c23170]; imul rdx, rax, 0x13e70; lea rax, [rax + rdx + 0x19cfd0]; ret",
    ),
    NativeFunctionSpec(
        rva="0x1244230",
        symbol_name="FRANCHISE_GAMEPLAN_MANAGER::EnsureOpponentGameplan",
        signature="GAMEPLAN* (FRANCHISE_GAMEPLAN_MANAGER* pManager, TEAM* pOpponentTeam)",
        calling_convention="__fastcall (rcx=pManager, rdx=pOpponentTeam)",
        parameters=[
            {"name": "pManager", "type": "FRANCHISE_GAMEPLAN_MANAGER*", "register": "rcx", "description": "Manager pointer"},
            {"name": "pOpponentTeam", "type": "TEAM*", "register": "rdx", "description": "Target opponent team"},
        ],
        returns="GAMEPLAN* (rax)",
        evidence_maturity=EvidenceMaturity.STATIC_DISASSEMBLED,
        description="Searches 35 slots (+0x4) for matching opponent_team_id. If not found, allocates first unused slot (0xFFFF) and initializes it.",
        disassembly_notes="Loop over 35 slots of stride 0x370. Compares word [rcx+4+i*0x370] with target team id. Calls 0x146c260 on new allocation.",
    ),
    NativeFunctionSpec(
        rva="0x12f21a0",
        symbol_name="FRANCHISE_GAMEPLAN_MANAGER::FindOpponentGameplan",
        signature="GAMEPLAN* (FRANCHISE_GAMEPLAN_MANAGER* pManager, TEAM* pOpponentTeam)",
        calling_convention="__fastcall (rcx=pManager, rdx=pOpponentTeam)",
        parameters=[
            {"name": "pManager", "type": "FRANCHISE_GAMEPLAN_MANAGER*", "register": "rcx", "description": "Manager pointer"},
            {"name": "pOpponentTeam", "type": "TEAM*", "register": "rdx", "description": "Target opponent team"},
        ],
        returns="GAMEPLAN* (rax, NULL if not found)",
        evidence_maturity=EvidenceMaturity.STATIC_DISASSEMBLED,
        description="Non-allocating lookup for existing opponent gameplan.",
        disassembly_notes="Loop over 35 slots of stride 0x370. Returns pointer to matched slot, or 0 if none match.",
    ),
    NativeFunctionSpec(
        rva="0x146c260",
        symbol_name="GAMEPLAN::Init",
        signature="void (GAMEPLAN* pGameplan)",
        calling_convention="__fastcall (rcx=pGameplan)",
        parameters=[
            {"name": "pGameplan", "type": "GAMEPLAN*", "register": "rcx", "description": "Gameplan buffer to initialize"},
        ],
        returns="void",
        evidence_maturity=EvidenceMaturity.STATIC_DISASSEMBLED,
        description="Zeroes/initializes 880-byte GAMEPLAN structure, sets default matchup slots to 0xFFFF auto-assignment.",
        disassembly_notes="Fills 0x370 bytes with default template values.",
    ),
    NativeFunctionSpec(
        rva="0x14651c0",
        symbol_name="GAMEPLAN::InsertOrFindOpponentMatchup",
        signature="MATCHUP_ENTRY* (GAMEPLAN* pGameplan, PLAYER* pOpponentPlayer, PLAYER* pAssignedDefender)",
        calling_convention="__fastcall (rcx=pGameplan, rdx=pOpponentPlayer, r8=pAssignedDefender)",
        parameters=[
            {"name": "pGameplan", "type": "GAMEPLAN*", "register": "rcx", "description": "Gameplan pointer"},
            {"name": "pOpponentPlayer", "type": "PLAYER*", "register": "rdx", "description": "Opponent player pointer"},
            {"name": "pAssignedDefender", "type": "PLAYER*", "register": "r8", "description": "Assigned defender pointer or NULL"},
        ],
        returns="MATCHUP_ENTRY* (rax at pGameplan + 0x64 + i * 12)",
        evidence_maturity=EvidenceMaturity.STATIC_DISASSEMBLED,
        description="Locates or allocates 12-byte matchup slot within the 23-slot array at +0x64.",
        disassembly_notes="Scans [rcx+0x64] stride 12 count 23 for opponent player UID.",
    ),
    NativeFunctionSpec(
        rva="0x146ec50",
        symbol_name="GAMEPLAN::ApplyToCoach",
        signature="void (GAMEPLAN* pGameplan)",
        calling_convention="__fastcall (rcx=pGameplan)",
        parameters=[
            {"name": "pGameplan", "type": "GAMEPLAN*", "register": "rcx", "description": "Gameplan pointer"},
        ],
        returns="void",
        evidence_maturity=EvidenceMaturity.STATIC_DISASSEMBLED,
        description="Tail-calls 0x146eaa0 to synchronize gameplan settings into owner team coach runtime structure.",
        disassembly_notes="mov rcx, [rcx+2]; call 0x146eaa0; ret",
    ),
    NativeFunctionSpec(
        rva="0x131f110",
        symbol_name="FRANCHISE_GAMEPLAN_MANAGER::CommitPendingFlags",
        signature="void (FRANCHISE_GAMEPLAN_MANAGER* pManager)",
        calling_convention="__fastcall (rcx=pManager)",
        parameters=[
            {"name": "pManager", "type": "FRANCHISE_GAMEPLAN_MANAGER*", "register": "rcx", "description": "Manager pointer"},
        ],
        returns="void",
        evidence_maturity=EvidenceMaturity.STATIC_DISASSEMBLED,
        description="Checks manager+0x7bc4 dirty flags (bit 0=gameplan flush, bit 1=coach sync), commits to franchise state and clears bits.",
        disassembly_notes="test dword ptr [rcx+0x7bc4], 1; jz loc_exit; ... and dword ptr [rcx+0x7bc4], ~3; ret",
    ),
    NativeFunctionSpec(
        rva="0x7a7840",
        symbol_name="GameplanUI::CommitAndExit",
        signature="void (void* pUIContext)",
        calling_convention="__fastcall (rcx=pUIContext)",
        parameters=[
            {"name": "pUIContext", "type": "void*", "register": "rcx", "description": "Gameplan UI screen context"},
        ],
        returns="void",
        evidence_maturity=EvidenceMaturity.STATIC_DISASSEMBLED,
        description="Full original UI commit transaction: acquires manager, ensures gameplan, applies to coach, marks IsInUse=1 (0x7a7aab), calls 0x131f110, exits screen.",
        disassembly_notes="mov word ptr [rbx], 1; call 0x131f110; ret",
    ),
]


class OpponentGameplanTransactionHarness:
    """Offline simulation harness modeling the exact native call chain transaction."""

    def __init__(self, manager: FranchiseGameplanManager):
        self.manager = manager
        self.call_log: List[str] = []

    def execute_modify_opponent_onball_pressure(
        self,
        opponent_team_id: int,
        opponent_player_uid: int,
        pressure: PressureOnball,
        assigned_defender_uid: int = 0xFFFF,
    ) -> Dict[str, Any]:
        """Executes the complete transactional sequence matching native GameplanUI::CommitAndExit.
        
        Sequence:
        Step 1: Ensure opponent gameplan exists (0x1244230).
        Step 2: Locate/insert matchup entry for opponent player (0x14651c0).
        Step 3: Modify target defensive setting (PressureOnball).
        Step 4: Synchronize to coach runtime structure (0x146ec50).
        Step 5: Mark gameplan active (IsInUse = 1 at 0x7a7aab).
        Step 6: Raise dirty flags and commit manager (0x131f110).
        """
        self.call_log.clear()

        # Step 1: Ensure Opponent Gameplan (RVA 0x1244230)
        self.call_log.append(f"CALL 0x1244230 EnsureOpponentGameplan(opponent_team_id={opponent_team_id})")
        gameplan = self.manager.ensure_opponent_gameplan(opponent_team_id)

        # Step 2: Insert or Find Opponent Matchup (RVA 0x14651c0)
        self.call_log.append(
            f"CALL 0x14651c0 InsertOrFindOpponentMatchup(player={opponent_player_uid}, defender={assigned_defender_uid})"
        )
        matchup = gameplan.find_or_create_matchup(opponent_player_uid, assigned_defender_uid)

        # Step 3: Mutate field
        self.call_log.append(f"MUTATE MatchupDefensiveSettings: pressure_onball -> {pressure.name} ({int(pressure)})")
        matchup.defensive_settings.pressure_onball = pressure

        # Step 4: Apply to Coach (RVA 0x146ec50)
        self.call_log.append("CALL 0x146ec50 ApplyToCoach()")

        # Step 5: Native UI commit marks IsInUse = 1 (RVA 0x7a7aab)
        self.call_log.append("WRITE GAMEPLAN+0x0: IsInUse = 1")
        gameplan.is_in_use = 1

        # Step 6: Commit pending flags (RVA 0x131f110)
        self.call_log.append("WRITE MANAGER+0x7bc4: dirty_flags |= 0x3")
        self.manager.dirty_flags |= 0x3
        self.call_log.append("CALL 0x131f110 CommitPendingFlags()")
        flushed_flags = self.manager.flush_pending_commit()

        return {
            "status": "SUCCESS",
            "owner_team_id": self.manager.team_id,
            "opponent_team_id": opponent_team_id,
            "opponent_player_uid": opponent_player_uid,
            "pressure_onball": pressure.name,
            "is_in_use": gameplan.is_in_use,
            "flushed_flags": flushed_flags,
            "call_log": list(self.call_log),
        }
