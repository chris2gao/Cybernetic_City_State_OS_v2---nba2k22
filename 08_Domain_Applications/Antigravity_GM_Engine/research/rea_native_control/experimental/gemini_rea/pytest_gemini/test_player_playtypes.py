import pytest
import sys
from pathlib import Path

exp_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(exp_dir))

from player_playtypes_codec import (
    PlayerPlayTypesCodec,
    PlayType,
    BadgeLevel
)

def test_playtypes_nibble_packing_exact():
    # Native 0xf1e370..0xf1e3d0:
    # 4 nibbles at bits 0..15 of [rcx + 0x168]
    pt1 = PlayType.PNR_BALL_HANDLER # 2
    pt2 = PlayType.ISOLATION        # 1
    pt3 = PlayType.THREE_POINT      # 10
    pt4 = PlayType.HANDOFF          # 8
    
    orig = 0xabcd0000 # existing upper 16 bits
    packed = PlayerPlayTypesCodec.encode_playtypes_word(pt1, pt2, pt3, pt4, orig)
    
    expected_low16 = 2 | (1 << 4) | (10 << 8) | (8 << 12)
    assert (packed & 0xffff) == expected_low16
    assert (packed & 0xffff0000) == 0xabcd0000
    
    d1, d2, d3, d4 = PlayerPlayTypesCodec.decode_playtypes_word(packed)
    assert d1 == PlayType.PNR_BALL_HANDLER
    assert d2 == PlayType.ISOLATION
    assert d3 == PlayType.THREE_POINT
    assert d4 == PlayType.HANDOFF

def test_stat_index_range():
    # Native 0x990a10: cmp ebp, 0x9b (155)
    assert PlayerPlayTypesCodec.validate_stat_index(0) is True
    assert PlayerPlayTypesCodec.validate_stat_index(0x9b) is True
    assert PlayerPlayTypesCodec.validate_stat_index(0x9c) is False
