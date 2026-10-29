"""Opponent Gameplan Native Structure Codec and Manipulation Engine.

GREA-01: Research and isolated implementation for NBA 2K22 opponent gameplan
native memory layout, field codec (PressureOnball), multi-opponent isolation,
and transaction commit dirty flags.

This module is strictly isolated under experimental/gemini_rea/GREA_01.
It contains NO direct live process memory write side effects.
"""

from __future__ import annotations

import struct
from dataclasses import dataclass, field
from enum import IntEnum
from typing import List, Optional


class PressureOnball(IntEnum):
    """Pressure On-Ball setting for opponent matchup defensive strategy."""
    AUTO = 0
    GAP = 1
    MODERATE = 2
    TIGHT = 3
    SMOTHER = 4


class PressureOffball(IntEnum):
    """Pressure Off-Ball setting for opponent matchup defensive strategy."""
    AUTO = 0
    MODERATE = 1
    TIGHT = 2
    DENY = 3


class ForceDirection(IntEnum):
    """Force Direction setting."""
    AUTO = 0
    NO_PREFERENCE = 1
    BASELINE = 2
    MIDDLE = 3


class ScreenDefenseOnBall(IntEnum):
    """On-ball screen defense setting."""
    AUTO = 0
    GO_OVER = 1
    GO_UNDER = 2
    SWITCH = 3


class ScreenDefenseHedge(IntEnum):
    """Hedge setting on ball screens."""
    AUTO = 0
    NO_HEDGE = 1
    SOFT_HEDGE = 2
    HARD_HEDGE = 3
    CATCH = 4


# Constants for binary structures
GAMEPLAN_SIZE = 880  # 0x370 bytes
OFFSET_IS_IN_USE = 0x0
OFFSET_OWNER_TEAM_ID = 0x2
OFFSET_OPPONENT_TEAM_ID = 0x4
OFFSET_ROSTER_SLOTS = 0x6
ROSTER_SLOT_COUNT = 23
ROSTER_SLOT_STRIDE = 4  # uint16 uid, uint16 default_minutes (0x00FF)
ROSTER_REGION_SIZE = 0x64 - 0x6  # 94 bytes (92 bytes roster + 2 bytes alignment padding)

OFFSET_MATCHUPS = 0x64  # 100 decimal
MATCHUP_COUNT = 23
MATCHUP_STRIDE = 12

OFFSET_TAIL_AFTER_MATCHUPS = 0x178  # 0x64 + 23 * 12 = 0x178
TAIL_SIZE = GAMEPLAN_SIZE - OFFSET_TAIL_AFTER_MATCHUPS  # 880 - 376 = 504 bytes

# Franchise Gameplan Manager offsets
MANAGER_SIZE = 0x13E70  # 81,520 bytes
OFFSET_MANAGER_TEAM_RECORD_INDEX = 0x0
OFFSET_MANAGER_TEAM_ID = 0x2
OFFSET_MANAGER_SLOTS = 0x4
MANAGER_OPPONENT_SLOTS_COUNT = 35
OFFSET_MANAGER_DEFAULT_GAMEPLAN = 0x7854  # 0x4 + 35 * 880
OFFSET_MANAGER_DIRTY_FLAGS = 0x7BC4  # 0x7854 + 880
MANAGER_DIRTY_FLAG_GAMEPLAN = 0x00000001
MANAGER_DIRTY_FLAG_COACH_SYNC = 0x00000002

AUTO_UID = 0xFFFF


@dataclass
class MatchupDefensiveSettings:
    """Decoded 8-byte defensive settings from Matchup entry word1 and word2."""
    pressure_onball: PressureOnball = PressureOnball.AUTO
    pressure_offball: PressureOffball = PressureOffball.AUTO
    force_direction: ForceDirection = ForceDirection.AUTO
    screen_defense_onball: ScreenDefenseOnBall = ScreenDefenseOnBall.AUTO
    screen_defense_hedge: ScreenDefenseHedge = ScreenDefenseHedge.AUTO
    offball_screen_defense: int = 0
    post_defense: int = 0
    double_team_perimeter: int = 0
    double_team_post: int = 0
    screen_defense_onball5: int = 0
    screen_defense_hedge5: int = 0
    switch_rule: int = 0

    # Word 2 fields
    onball_help: int = 0
    screen_help: int = 0
    extend_pressure: int = 0
    tag_on_roll: int = 0
    stay_attached: int = 0
    pre_rotate: int = 0

    def pack_word1(self) -> int:
        w = 0
        w |= (int(self.pressure_onball) & 0x7)
        w |= ((int(self.pressure_offball) & 0x7) << 3)
        w |= ((int(self.force_direction) & 0x3) << 6)
        w |= ((int(self.screen_defense_onball) & 0x7) << 8)
        w |= ((int(self.screen_defense_hedge) & 0x7) << 11)
        w |= ((self.offball_screen_defense & 0x3) << 14)
        w |= ((self.post_defense & 0x7) << 16)
        w |= ((self.double_team_perimeter & 0x3) << 19)
        w |= ((self.double_team_post & 0x7) << 21)
        w |= ((self.screen_defense_onball5 & 0x7) << 24)
        w |= ((self.screen_defense_hedge5 & 0x7) << 27)
        w |= ((self.switch_rule & 0x3) << 30)
        return w

    @classmethod
    def unpack_word1(cls, w: int, settings: MatchupDefensiveSettings) -> None:
        settings.pressure_onball = PressureOnball(w & 0x7)
        settings.pressure_offball = PressureOffball((w >> 3) & 0x7)
        settings.force_direction = ForceDirection((w >> 6) & 0x3)
        settings.screen_defense_onball = ScreenDefenseOnBall((w >> 8) & 0x7)
        settings.screen_defense_hedge = ScreenDefenseHedge((w >> 11) & 0x7)
        settings.offball_screen_defense = (w >> 14) & 0x3
        settings.post_defense = (w >> 16) & 0x7
        settings.double_team_perimeter = (w >> 19) & 0x3
        settings.double_team_post = (w >> 21) & 0x7
        settings.screen_defense_onball5 = (w >> 24) & 0x7
        settings.screen_defense_hedge5 = (w >> 27) & 0x7
        settings.switch_rule = (w >> 30) & 0x3

    def pack_word2(self) -> int:
        w = 0
        w |= (self.onball_help & 0x3)
        w |= ((self.screen_help & 0x3) << 2)
        w |= ((self.extend_pressure & 0x3) << 4)
        w |= ((self.tag_on_roll & 0x3) << 6)
        w |= ((self.stay_attached & 0x3) << 8)
        w |= ((self.pre_rotate & 0x1) << 10)
        return w

    @classmethod
    def unpack_word2(cls, w: int, settings: MatchupDefensiveSettings) -> None:
        settings.onball_help = w & 0x3
        settings.screen_help = (w >> 2) & 0x3
        settings.extend_pressure = (w >> 4) & 0x3
        settings.tag_on_roll = (w >> 6) & 0x3
        settings.stay_attached = (w >> 8) & 0x3
        settings.pre_rotate = (w >> 10) & 0x1


@dataclass
class OpponentMatchupEntry:
    """A single 12-byte opponent matchup entry inside GAMEPLAN."""
    opponent_player_uid: int = AUTO_UID  # uint16 (+0)
    assigned_defender_uid: int = AUTO_UID  # uint16 (+2)
    defensive_settings: MatchupDefensiveSettings = field(default_factory=MatchupDefensiveSettings)

    def pack(self) -> bytes:
        word1 = self.defensive_settings.pack_word1()
        word2 = self.defensive_settings.pack_word2()
        return struct.pack("<HHI I", self.opponent_player_uid, self.assigned_defender_uid, word1, word2)

    @classmethod
    def unpack(cls, data: bytes, offset: int = 0) -> OpponentMatchupEntry:
        opp_uid, def_uid, word1, word2 = struct.unpack_from("<HHI I", data, offset)
        settings = MatchupDefensiveSettings()
        MatchupDefensiveSettings.unpack_word1(word1, settings)
        MatchupDefensiveSettings.unpack_word2(word2, settings)
        return cls(
            opponent_player_uid=opp_uid,
            assigned_defender_uid=def_uid,
            defensive_settings=settings,
        )


@dataclass
class OpponentGameplan:
    """Full 880 (0x370) byte Native GAMEPLAN layout."""
    is_in_use: int = 0  # uint16 (+0x0): 0=default/unused, 1=active custom gameplan
    owner_team_id: int = 0  # uint16 (+0x2)
    opponent_team_id: int = AUTO_UID  # uint16 (+0x4): 0xFFFF for default gameplan
    roster_slots_raw: bytes = field(default_factory=lambda: b"\x00" * ROSTER_REGION_SIZE)
    matchups: List[OpponentMatchupEntry] = field(default_factory=list)
    tail_raw: bytes = field(default_factory=lambda: b"\x00" * TAIL_SIZE)

    def __post_init__(self):
        if not self.matchups:
            self.matchups = [OpponentMatchupEntry() for _ in range(MATCHUP_COUNT)]
        if len(self.matchups) != MATCHUP_COUNT:
            raise ValueError(f"Matchup count must be exactly {MATCHUP_COUNT}, got {len(self.matchups)}")

    def pack(self) -> bytes:
        header = struct.pack("<HHH", self.is_in_use, self.owner_team_id, self.opponent_team_id)
        if len(self.roster_slots_raw) != ROSTER_REGION_SIZE:
            roster_bytes = self.roster_slots_raw.ljust(ROSTER_REGION_SIZE, b"\x00")[:ROSTER_REGION_SIZE]
        else:
            roster_bytes = self.roster_slots_raw
        
        matchup_bytes = bytearray()
        for m in self.matchups:
            matchup_bytes.extend(m.pack())
        
        if len(self.tail_raw) != TAIL_SIZE:
            tail_bytes = self.tail_raw.ljust(TAIL_SIZE, b"\x00")[:TAIL_SIZE]
        else:
            tail_bytes = self.tail_raw
            
        result = header + roster_bytes + bytes(matchup_bytes) + tail_bytes
        if len(result) != GAMEPLAN_SIZE:
            raise ValueError(f"Packed GAMEPLAN size {len(result)} does not match {GAMEPLAN_SIZE}")
        return result

    @classmethod
    def unpack(cls, data: bytes, offset: int = 0) -> OpponentGameplan:
        if len(data) < offset + GAMEPLAN_SIZE:
            raise ValueError(f"Insufficient data for GAMEPLAN: need {offset + GAMEPLAN_SIZE}, got {len(data)}")
        slice_data = data[offset:offset + GAMEPLAN_SIZE]
        is_in_use, owner_team, opp_team = struct.unpack_from("<HHH", slice_data, 0)
        roster_bytes = slice_data[OFFSET_ROSTER_SLOTS:OFFSET_MATCHUPS]
        
        matchups: List[OpponentMatchupEntry] = []
        for i in range(MATCHUP_COUNT):
            m_offset = OFFSET_MATCHUPS + i * MATCHUP_STRIDE
            matchups.append(OpponentMatchupEntry.unpack(slice_data, m_offset))
            
        tail_bytes = slice_data[OFFSET_TAIL_AFTER_MATCHUPS:]
        return cls(
            is_in_use=is_in_use,
            owner_team_id=owner_team,
            opponent_team_id=opp_team,
            roster_slots_raw=roster_bytes,
            matchups=matchups,
            tail_raw=tail_bytes,
        )

    def find_or_create_matchup(self, opponent_player_uid: int, assigned_defender_uid: int = AUTO_UID) -> OpponentMatchupEntry:
        """Emulates native 0x14651c0 GAMEPLAN::InsertOrFindOpponentMatchup."""
        # 1. Search existing
        for m in self.matchups:
            if m.opponent_player_uid == opponent_player_uid:
                if assigned_defender_uid != AUTO_UID:
                    m.assigned_defender_uid = assigned_defender_uid
                return m
        # 2. Find empty slot (0xFFFF)
        for m in self.matchups:
            if m.opponent_player_uid == AUTO_UID:
                m.opponent_player_uid = opponent_player_uid
                m.assigned_defender_uid = assigned_defender_uid
                return m
        # 3. If full, return first slot as fallback
        m = self.matchups[0]
        m.opponent_player_uid = opponent_player_uid
        m.assigned_defender_uid = assigned_defender_uid
        return m

    def set_onball_pressure(self, opponent_player_uid: int, pressure: PressureOnball, assigned_defender_uid: int = AUTO_UID) -> None:
        """Sets PressureOnball for target opponent player."""
        m = self.find_or_create_matchup(opponent_player_uid, assigned_defender_uid)
        m.defensive_settings.pressure_onball = pressure


class FranchiseGameplanManager:
    """Codec and state machine for FRANCHISE_GAMEPLAN_MANAGER (size 0x13E70)."""

    def __init__(self, team_record_index: int = 0, team_id: int = 0):
        self.team_record_index = team_record_index
        self.team_id = team_id
        # 35 opponent gameplan slots
        self.slots: List[OpponentGameplan] = [
            OpponentGameplan(owner_team_id=team_id, opponent_team_id=AUTO_UID)
            for _ in range(MANAGER_OPPONENT_SLOTS_COUNT)
        ]
        # Slot 35: Default gameplan against all opponents
        self.default_gameplan = OpponentGameplan(owner_team_id=team_id, opponent_team_id=AUTO_UID)
        self.dirty_flags = 0
        self.raw_extra_buffer = bytearray(MANAGER_SIZE - (OFFSET_MANAGER_DIRTY_FLAGS + 4))

    def ensure_opponent_gameplan(self, opponent_team_id: int) -> OpponentGameplan:
        """Emulates native 0x1244230 FRANCHISE_GAMEPLAN_MANAGER::EnsureOpponentGameplan."""
        # 1. Search existing
        for slot in self.slots:
            if slot.opponent_team_id == opponent_team_id:
                return slot
        # 2. Allocate an empty slot
        for slot in self.slots:
            if slot.opponent_team_id == AUTO_UID:
                slot.opponent_team_id = opponent_team_id
                slot.owner_team_id = self.team_id
                slot.is_in_use = 0  # reset until explicit commit
                return slot
        raise RuntimeError("No free opponent gameplan slot available in manager (limit 35)")

    def find_opponent_gameplan(self, opponent_team_id: int) -> Optional[OpponentGameplan]:
        """Emulates native 0x12f21a0 FRANCHISE_GAMEPLAN_MANAGER::FindOpponentGameplan."""
        for slot in self.slots:
            if slot.opponent_team_id == opponent_team_id:
                return slot
        return None

    def commit_gameplan(self, opponent_team_id: int) -> None:
        """Emulates native 0x7a7840 commit transaction sequence.
        
        1. Marks the targeted opponent gameplan as in-use (IsInUse = 1, offset +0x0).
        2. Raises dirty flags in manager: bit 0 (0x1) for pending flush, bit 1 (0x2) for coach sync.
        3. Clears dirty bits upon commit completion (simulating 0x131f110).
        """
        gp = self.find_opponent_gameplan(opponent_team_id)
        if gp is None:
            raise KeyError(f"No gameplan found for opponent team ID {opponent_team_id}")
        
        # Native 0x7a7aab: mov word ptr [rbx], 1
        gp.is_in_use = 1
        
        # Raise dirty flag
        self.dirty_flags |= (MANAGER_DIRTY_FLAG_GAMEPLAN | MANAGER_DIRTY_FLAG_COACH_SYNC)

    def flush_pending_commit(self) -> int:
        """Emulates native 0x131f110 FRANCHISE_GAMEPLAN_MANAGER::CommitPendingFlags."""
        flushed_flags = self.dirty_flags
        # Flush action executes...
        self.dirty_flags = 0
        return flushed_flags

    def pack(self) -> bytes:
        buf = bytearray(MANAGER_SIZE)
        struct.pack_into("<HH", buf, OFFSET_MANAGER_TEAM_RECORD_INDEX, self.team_record_index, self.team_id)
        
        for i, slot in enumerate(self.slots):
            offset = OFFSET_MANAGER_SLOTS + i * GAMEPLAN_SIZE
            buf[offset:offset + GAMEPLAN_SIZE] = slot.pack()
            
        # Default gameplan
        buf[OFFSET_MANAGER_DEFAULT_GAMEPLAN:OFFSET_MANAGER_DEFAULT_GAMEPLAN + GAMEPLAN_SIZE] = self.default_gameplan.pack()
        
        # Dirty flags
        struct.pack_into("<I", buf, OFFSET_MANAGER_DIRTY_FLAGS, self.dirty_flags)
        
        # Extra buffer
        extra_offset = OFFSET_MANAGER_DIRTY_FLAGS + 4
        buf[extra_offset:extra_offset + len(self.raw_extra_buffer)] = self.raw_extra_buffer
        return bytes(buf)

    @classmethod
    def unpack(cls, data: bytes) -> FranchiseGameplanManager:
        if len(data) < MANAGER_SIZE:
            raise ValueError(f"Data length {len(data)} is less than MANAGER_SIZE {MANAGER_SIZE}")
        
        team_rec, team_id = struct.unpack_from("<HH", data, OFFSET_MANAGER_TEAM_RECORD_INDEX)
        mgr = cls(team_record_index=team_rec, team_id=team_id)
        
        mgr.slots = []
        for i in range(MANAGER_OPPONENT_SLOTS_COUNT):
            offset = OFFSET_MANAGER_SLOTS + i * GAMEPLAN_SIZE
            mgr.slots.append(OpponentGameplan.unpack(data, offset))
            
        mgr.default_gameplan = OpponentGameplan.unpack(data, OFFSET_MANAGER_DEFAULT_GAMEPLAN)
        mgr.dirty_flags = struct.unpack_from("<I", data, OFFSET_MANAGER_DIRTY_FLAGS)[0]
        
        extra_offset = OFFSET_MANAGER_DIRTY_FLAGS + 4
        mgr.raw_extra_buffer = bytearray(data[extra_offset:MANAGER_SIZE])
        return mgr
