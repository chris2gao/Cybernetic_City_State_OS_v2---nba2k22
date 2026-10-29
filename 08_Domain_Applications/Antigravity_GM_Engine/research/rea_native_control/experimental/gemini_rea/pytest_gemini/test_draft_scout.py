import pytest
import sys
from pathlib import Path

exp_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(exp_dir))

from draft_scout_codec import (
    DraftScoutCodec,
    DraftPick,
    PickProtectionType
)

def test_pick_dword_1c_roundtrip():
    # Test encoding Round 1, Pick 14, Owning Team 7, Lottery Protected
    encoded = DraftScoutCodec.encode_pick_dword_1c(
        round_num=1,
        pick_index=14,
        owning_team_id=7,
        protection=int(PickProtectionType.LOTTERY_PROTECTED)
    )
    
    rnd, pick, team, prot = DraftScoutCodec.decode_pick_dword_1c(encoded)
    assert rnd == 1
    assert pick == 14
    assert team == 7
    assert prot == int(PickProtectionType.LOTTERY_PROTECTED)

def test_big_board_roundtrip():
    # 60 prospect IDs ranked 1..60
    board = [(i * 7 + 13) % 500 + 1 for i in range(60)]
    raw = DraftScoutCodec.encode_big_board(board)
    assert len(raw) == 120
    
    decoded = DraftScoutCodec.decode_big_board(raw)
    assert len(decoded) == 60
    assert decoded == board
