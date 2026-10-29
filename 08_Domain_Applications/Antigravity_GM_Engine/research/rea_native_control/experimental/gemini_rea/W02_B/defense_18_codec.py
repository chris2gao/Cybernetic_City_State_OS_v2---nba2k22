"""W02-B: Complete 18 Individual Defensive Matchup Settings Codec.

Encodes and decodes the exact 8-byte defensive setting block (Word 1: 32 bits,
Word 2: low 11 bits) within the 12-byte Matchup structure of NBA 2K22.
"""

from __future__ import annotations

import struct
from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any, Dict, List, Optional, Tuple


class PressureOnball(IntEnum):
    AUTO = 0
    GAP = 1
    MODERATE = 2
    TIGHT = 3
    SMOTHER = 4


class PressureOffball(IntEnum):
    AUTO = 0
    GAP = 1
    LEAVE = 2
    MODERATE = 3
    TIGHT = 4
    DENY_BALL = 5


class ForceDirection(IntEnum):
    AUTO = 0
    MIDDLE = 1
    BASELINE = 2


class ScreenDefenseOnBall(IntEnum):
    AUTO = 0
    GO_OVER = 1
    GO_UNDER = 2
    SWITCH = 3
    ICE = 4


class ScreenDefenseHedge(IntEnum):
    AUTO = 0
    NO_HEDGE = 1
    SOFT_HEDGE = 2
    HARD_HEDGE = 3
    DOUBLE = 4
    CATCH_HEDGE = 5


class OffballScreenDefense(IntEnum):
    AUTO = 0
    GO_OVER = 1
    GO_UNDER = 2
    SWITCH = 3


class PostDefense(IntEnum):
    AUTO = 0
    FRONT = 1
    BEHIND = 2
    THREE_QUARTERS_TOP = 3
    THREE_QUARTERS_BOTTOM = 4


class DoubleTeamPerimeter(IntEnum):
    AUTO = 0
    MANUAL = 1
    ON_CATCH = 2
    ON_DRIVE = 3


class DoubleTeamPost(IntEnum):
    AUTO = 0
    MANUAL = 1
    DIG = 2
    ON_CATCH = 3
    ON_DRIBBLE = 4


class ScreenDefenseOnBall5(IntEnum):
    AUTO = 0
    GO_OVER = 1
    GO_UNDER = 2
    SWITCH = 3
    ICE = 4


class ScreenDefenseHedge5(IntEnum):
    AUTO = 0
    NO_HEDGE = 1
    SOFT_HEDGE = 2
    HARD_HEDGE = 3
    DOUBLE = 4
    CATCH_HEDGE = 5


class SwitchRule(IntEnum):
    SWITCH_AUTO = 0
    SWITCH_ALL = 1
    SWITCH_BIGS = 2
    SWITCH_GUARDS = 3


class HelpSetting(IntEnum):
    AUTO = 0
    HELP = 1
    NO_HELP = 2


class YesNoSetting(IntEnum):
    AUTO = 0
    YES = 1
    NO = 2


@dataclass(frozen=True)
class DefensiveFieldSpec:
    name: str
    word_index: int  # 0 for word1, 1 for word2
    start_bit: int
    width: int
    mask: int
    enum_cls: Any
    default_value: int


DEFENSIVE_18_SPECS: List[DefensiveFieldSpec] = [
    # Word 1 (32 bits, default = 0x00280000)
    DefensiveFieldSpec("PressureOnball", 0, 0, 3, 0x00000007, PressureOnball, 0),
    DefensiveFieldSpec("PressureOffball", 0, 3, 3, 0x00000038, PressureOffball, 0),
    DefensiveFieldSpec("ForceDirection", 0, 6, 2, 0x000000C0, ForceDirection, 0),
    DefensiveFieldSpec("ScreenDefenseOnBall", 0, 8, 3, 0x00000700, ScreenDefenseOnBall, 0),
    DefensiveFieldSpec("ScreenDefenseHedge", 0, 11, 3, 0x00003800, ScreenDefenseHedge, 0),
    DefensiveFieldSpec("OffballScreenDefense", 0, 14, 2, 0x0000C000, OffballScreenDefense, 0),
    DefensiveFieldSpec("PostDefense", 0, 16, 3, 0x00070000, PostDefense, 0),
    DefensiveFieldSpec("DoubleTeamPerimeter", 0, 19, 2, 0x00180000, DoubleTeamPerimeter, 1),  # Default = 1 (MANUAL)
    DefensiveFieldSpec("DoubleTeamPost", 0, 21, 3, 0x00E00000, DoubleTeamPost, 1),            # Default = 1 (MANUAL)
    DefensiveFieldSpec("ScreenDefenseOnBall5", 0, 24, 3, 0x07000000, ScreenDefenseOnBall5, 0),
    DefensiveFieldSpec("ScreenDefenseHedge5", 0, 27, 3, 0x38000000, ScreenDefenseHedge5, 0),
    DefensiveFieldSpec("SwitchRule", 0, 30, 2, 0xC0000000, SwitchRule, 0),

    # Word 2 (low 11 bits, default = 0x00000000)
    DefensiveFieldSpec("OnballHelp", 1, 0, 2, 0x00000003, HelpSetting, 0),
    DefensiveFieldSpec("ScreenHelp", 1, 2, 2, 0x0000000C, HelpSetting, 0),
    DefensiveFieldSpec("ExtendPressure", 1, 4, 2, 0x00000030, YesNoSetting, 0),
    DefensiveFieldSpec("TagOnRoll", 1, 6, 2, 0x000000C0, YesNoSetting, 0),
    DefensiveFieldSpec("StayAttached", 1, 8, 2, 0x00000300, YesNoSetting, 0),
    DefensiveFieldSpec("PreRotate", 1, 10, 1, 0x00000400, bool, 0),
]

DEFENSIVE_SPECS_MAP: Dict[str, DefensiveFieldSpec] = {spec.name: spec for spec in DEFENSIVE_18_SPECS}

DEFAULT_WORD1 = 0x00280000  # DoubleTeamPerimeter=1 (bit 19), DoubleTeamPost=1 (bit 21)
DEFAULT_WORD2_LOW11 = 0x00000000


@dataclass
class Matchup18DefenseSettings:
    """Represents the complete 18 individual defense settings for one matchup."""
    values: Dict[str, int] = field(default_factory=dict)

    def __post_init__(self):
        for spec in DEFENSIVE_18_SPECS:
            if spec.name not in self.values:
                self.values[spec.name] = spec.default_value

    def get(self, name: str) -> Any:
        spec = DEFENSIVE_SPECS_MAP[name]
        raw_val = self.values.get(name, spec.default_value)
        if spec.enum_cls is bool:
            return bool(raw_val)
        try:
            return spec.enum_cls(raw_val)
        except (ValueError, TypeError):
            return raw_val

    def set(self, name: str, val: Any) -> None:
        spec = DEFENSIVE_SPECS_MAP[name]
        int_val = int(val)
        max_val = (1 << spec.width) - 1
        if not (0 <= int_val <= max_val):
            raise ValueError(f"Value {int_val} out of bounds for {name} (0..{max_val})")
        self.values[name] = int_val

    def pack(self) -> Tuple[int, int]:
        """Packs into (word1, word2_low11)."""
        w1 = 0
        w2 = 0
        for spec in DEFENSIVE_18_SPECS:
            val = self.values.get(spec.name, spec.default_value)
            masked_val = (val & ((1 << spec.width) - 1)) << spec.start_bit
            if spec.word_index == 0:
                w1 |= masked_val
            else:
                w2 |= masked_val
        return w1, w2

    @classmethod
    def unpack(cls, w1: int, w2: int) -> Matchup18DefenseSettings:
        res = cls()
        for spec in DEFENSIVE_18_SPECS:
            raw_w = w1 if spec.word_index == 0 else w2
            val = (raw_w >> spec.start_bit) & ((1 << spec.width) - 1)
            res.values[spec.name] = val
        return res

    def pack_bytes(self) -> bytes:
        w1, w2 = self.pack()
        return struct.pack("<II", w1, w2)

    @classmethod
    def unpack_bytes(cls, b: bytes) -> Matchup18DefenseSettings:
        if len(b) != 8:
            raise ValueError(f"Expected 8 bytes for defensive settings, got {len(b)}")
        w1, w2 = struct.unpack("<II", b)
        return cls.unpack(w1, w2)
