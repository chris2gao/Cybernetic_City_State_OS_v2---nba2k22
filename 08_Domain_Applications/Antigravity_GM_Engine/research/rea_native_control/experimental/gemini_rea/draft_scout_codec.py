"""Draft, Draft Pick Rights, and Scouting Codec for NBA 2K22 (Wave-03 W03-09)
Encodes and decodes Draft Picks (Round, Pick Number, Owning Team, Protection),
Big Board Rankings (60 prospects), and Scouting Goal Assignments.

Binary Verified Anchors:
- 0x92a6a0: Draft_GetCurrentSelection(uint32 round, uint32 pick, uint32 year_offset)
  Reads pick structure at [rax + 0x1c], checking round and pick index.
- 0xec9610: Draft_SelectProspect(Prospect* rcx, DraftPick* rdx)
  Executes pick transaction and assigns prospect to owning team.
- 0x1261d40: Scout_ExecuteTrip(ScoutContext* rcx)
  Checks trip budget at [rcx + 0x1068] bits 15..18.
- 0x1244580: Scout_AppendGoalTarget(ScoutGoalContext* rcx, uint16 prospect_id)
"""
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple
from enum import IntEnum

class PickProtectionType(IntEnum):
    UNPROTECTED = 0
    TOP_3_PROTECTED = 1
    TOP_5_PROTECTED = 2
    TOP_10_PROTECTED = 3
    LOTTERY_PROTECTED = 4

@dataclass
class DraftPick:
    year: int
    round_num: int       # 1 or 2
    pick_index: int      # 1..30 (or overall 1..60)
    original_team_id: int
    owning_team_id: int
    protection: PickProtectionType = PickProtectionType.UNPROTECTED
    selected_player_id: Optional[int] = None

@dataclass
class ScoutAssignment:
    scout_id: int
    target_prospect_ids: List[int]
    scout_region: int = 0  # 0: National, 1: College East, 2: College West, 3: International
    trip_days: int = 14
    progress_pct: int = 0  # 0..100

class DraftScoutCodec:
    """Encodes and decodes Draft Pick structures and Scouting assignments."""

    @staticmethod
    def encode_pick_dword_1c(round_num: int, pick_index: int, owning_team_id: int, protection: int = 0) -> int:
        """Simulates native 0x92a6a0 bitfield at [DraftPick + 0x1c]:
        - bits 0..7: owning_team_id
        - bits 8..15: pick_index
        - bits 16..18: round_num
        - bits 19..22: protection
        """
        val = (owning_team_id & 0xff)
        val |= ((pick_index & 0xff) << 8)
        val |= ((round_num & 0x7) << 16)
        val |= ((protection & 0xf) << 19)
        return val

    @staticmethod
    def decode_pick_dword_1c(dword: int) -> Tuple[int, int, int, int]:
        """Reads (round_num, pick_index, owning_team_id, protection) from dword."""
        owning_team_id = dword & 0xff
        pick_index = (dword >> 8) & 0xff
        round_num = (dword >> 16) & 0x7
        protection = (dword >> 19) & 0xf
        return round_num, pick_index, owning_team_id, protection

    @staticmethod
    def encode_big_board(rankings: List[int]) -> bytearray:
        """Encodes up to 60 prospect IDs in ordered rank into 120-byte buffer (60 * 2 bytes)."""
        buf = bytearray(120)
        for i in range(min(60, len(rankings))):
            buf[i*2 : (i+1)*2] = (rankings[i] & 0xffff).to_bytes(2, "little")
        return buf

    @staticmethod
    def decode_big_board(buf: bytes) -> List[int]:
        """Decodes 120-byte buffer into list of ordered prospect IDs."""
        rankings = []
        for i in range(min(60, len(buf) // 2)):
            pid = int.from_bytes(buf[i*2 : (i+1)*2], "little")
            if pid != 0 and pid != 0xffff:
                rankings.append(pid)
        return rankings
