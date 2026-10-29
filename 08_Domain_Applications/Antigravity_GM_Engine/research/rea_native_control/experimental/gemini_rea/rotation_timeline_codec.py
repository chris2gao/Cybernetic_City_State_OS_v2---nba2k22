"""Rotation and Minutes Timeline Codec for NBA 2K22 (Wave-03 W03-05)
Encodes and decodes Starting Five, Bench Depth, 240-minute allocations,
and 48-minute rotation timeline (48 x 10 bytes = 480 bytes) at GAMEPLAN 0x18e..0x36e.

Binary Verified Anchors:
- 0x11b2bb0: Player_SetMinutes(PlayerRosterSlot* rdx, uint32 minutes)
  Writes 7-bit minutes value into [rdx + 0xf8] bits 18..24.
- 0xedf000: Player_GetRosterPosition(PlayerRosterSlot* rcx)
  Extracts 4-bit slot from [rcx + 0xf78] bits 22..25.
- GAMEPLAN+0x18c: has_rotation_timeline (uint8 / bool)
- GAMEPLAN+0x18e..0x36e: 48-minute timeline (480 bytes, 48 slices of 5 x uint16 player IDs)
"""
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional

TOTAL_TEAM_MINUTES = 240
MAX_PLAYER_MINUTES = 48
TIMELINE_SLICES = 48
PLAYERS_ON_COURT = 5

@dataclass
class PlayerMinuteAllocation:
    player_id: int
    roster_index: int  # 0..14 (0..4 = Starter, 5..9 = Second Unit, 10..14 = Reserves)
    minutes: int       # 0..48
    role_id: int = 0   # 0: Starter, 1: Sixth Man, 2: Role Player, 3: Prospect, 4: Bench

@dataclass
class TeamRotationPlan:
    team_id: int
    allocations: List[PlayerMinuteAllocation]
    timeline_active: bool = False
    # 48 minutes, each minute is a list of 5 player IDs
    timeline: Optional[List[List[int]]] = None

    def validate_minutes(self) -> Tuple[bool, str]:
        total = sum(p.minutes for p in self.allocations)
        if total != TOTAL_TEAM_MINUTES:
            return False, f"Total minutes {total} != {TOTAL_TEAM_MINUTES}"
        for p in self.allocations:
            if not (0 <= p.minutes <= MAX_PLAYER_MINUTES):
                return False, f"Player {p.player_id} minutes {p.minutes} out of range [0, 48]"
        return True, "Valid"


class RotationTimelineCodec:
    """Encodes/Decodes Rotation Timeline and Minutes into GAMEPLAN 0x18c..0x36e"""

    @staticmethod
    def encode_player_minutes_field(minutes: int, existing_dword_f8: int = 0) -> int:
        """Simulates native function 0x11b2bb0: writes 7-bit minutes into bits 18..24."""
        clamped = min(127, max(0, minutes)) & 0x7f
        cleared = existing_dword_f8 & 0xfe03ffff
        return cleared | (clamped << 18)

    @staticmethod
    def decode_player_minutes_field(dword_f8: int) -> int:
        """Reads 7-bit minutes from dword at offset 0xf8."""
        return (dword_f8 >> 18) & 0x7f

    @staticmethod
    def encode_timeline_into_gameplan(plan: TeamRotationPlan, buffer: bytearray) -> None:
        """Writes timeline flag (0x18c) and 48-minute timeline (0x18e..0x36e) into buffer."""
        if len(buffer) < 0x370:
            buffer.extend(b"\x00" * (0x370 - len(buffer)))

        buffer[0x18c] = 1 if plan.timeline_active else 0

        if not plan.timeline_active or not plan.timeline:
            # Clear timeline area
            buffer[0x18e:0x36e] = b"\x00" * 480
            return

        offset = 0x18e
        for minute in range(TIMELINE_SLICES):
            minute_lineup = plan.timeline[minute] if minute < len(plan.timeline) else [0, 0, 0, 0, 0]
            for slot in range(PLAYERS_ON_COURT):
                pid = minute_lineup[slot] if slot < len(minute_lineup) else 0
                buffer[offset : offset + 2] = (pid & 0xffff).to_bytes(2, "little")
                offset += 2

    @staticmethod
    def decode_timeline_from_gameplan(buffer: bytes) -> Tuple[bool, List[List[int]]]:
        """Reads timeline flag and 48-minute timeline from GAMEPLAN buffer."""
        if len(buffer) < 0x36e:
            raise ValueError(f"Buffer too short: {len(buffer)} < 0x36e")

        is_active = bool(buffer[0x18c])
        timeline = []
        offset = 0x18e
        for _ in range(TIMELINE_SLICES):
            minute_lineup = []
            for _ in range(PLAYERS_ON_COURT):
                pid = int.from_bytes(buffer[offset : offset + 2], "little")
                minute_lineup.append(pid)
                offset += 2
            timeline.append(minute_lineup)

        return is_active, timeline
