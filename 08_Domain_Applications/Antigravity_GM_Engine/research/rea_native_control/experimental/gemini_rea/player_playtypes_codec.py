"""Player PlayTypes, Tendencies, and Attributes Codec for NBA 2K22 (Wave-03 W03-11)
Encodes and decodes the 4 PlayTypes packed into a 16-bit nibble field at [Player + 0x168],
Player Tendencies/Attributes (0x990a10 jump table of 155 indices), and Badge levels.

Binary Verified Anchors:
- 0xf1e370: Player_SetPlayType1(Player* rcx, uint32 type_id) -> writes bits 0..3 of [rcx + 0x168]
- 0xf1e390: Player_SetPlayType2(Player* rcx, uint32 type_id) -> writes bits 4..7 of [rcx + 0x168]
- 0xf1e3b0: Player_SetPlayType3(Player* rcx, uint32 type_id) -> writes bits 8..11 of [rcx + 0x168]
- 0xf1e3d0: Player_SetPlayType4(Player* rcx, uint32 type_id) -> writes bits 12..15 of [rcx + 0x168]
- 0x990a10: Player_SetStatUI(Player* rcx, uint32 stat_index, uint32 value) -> 155 indices (cmp ebp, 0x9b)
- 0x992d40: Player_SetBadge(Player* rcx, uint32 badge_id, uint8 level) -> levels 0..4 (0=None, 1=Bronze, 2=Silver, 3=Gold, 4=HoF)
"""
from dataclasses import dataclass
from typing import List, Tuple
from enum import IntEnum

class PlayType(IntEnum):
    NONE = 0
    ISOLATION = 1
    PNR_BALL_HANDLER = 2
    PNR_ROLL_MAN = 3
    POST_UP_LOW = 4
    POST_UP_HIGH = 5
    GUARD_POST_UP = 6
    CUTTER = 7
    HANDOFF = 8
    MID_RANGE = 9
    THREE_POINT = 10
    ISO_3PT = 11
    CATCH_AND_SHOOT = 12

class BadgeLevel(IntEnum):
    NONE = 0
    BRONZE = 1
    SILVER = 2
    GOLD = 3
    HALL_OF_FAME = 4

@dataclass
class PlayerTacticalProfile:
    player_id: int
    playtype_1: PlayType = PlayType.NONE
    playtype_2: PlayType = PlayType.NONE
    playtype_3: PlayType = PlayType.NONE
    playtype_4: PlayType = PlayType.NONE
    is_play_initiator: bool = False

class PlayerPlayTypesCodec:
    """Encodes/Decodes 4-PlayType packed nibbles at offset 0x168."""

    @staticmethod
    def encode_playtypes_word(pt1: int, pt2: int, pt3: int, pt4: int, existing_dword: int = 0) -> int:
        """Simulates native functions 0xf1e370, 0xf1e390, 0xf1e3b0, 0xf1e3d0:
        Pack 4 4-bit nibbles into bits 0..15 of dword.
        """
        cleared = existing_dword & 0xffff0000
        packed = (
            (pt1 & 0xf) |
            ((pt2 & 0xf) << 4) |
            ((pt3 & 0xf) << 8) |
            ((pt4 & 0xf) << 12)
        )
        return cleared | packed

    @staticmethod
    def decode_playtypes_word(dword: int) -> Tuple[PlayType, PlayType, PlayType, PlayType]:
        """Reads 4 PlayTypes from bits 0..15."""
        p1 = PlayType(dword & 0xf) if (dword & 0xf) <= 12 else PlayType.NONE
        p2 = PlayType((dword >> 4) & 0xf) if ((dword >> 4) & 0xf) <= 12 else PlayType.NONE
        p3 = PlayType((dword >> 8) & 0xf) if ((dword >> 8) & 0xf) <= 12 else PlayType.NONE
        p4 = PlayType((dword >> 12) & 0xf) if ((dword >> 12) & 0xf) <= 12 else PlayType.NONE
        return p1, p2, p3, p4

    @staticmethod
    def validate_stat_index(index: int) -> bool:
        """Simulates native 0x990a10: checks index <= 0x9b (155 decimal)."""
        return 0 <= index <= 0x9b
