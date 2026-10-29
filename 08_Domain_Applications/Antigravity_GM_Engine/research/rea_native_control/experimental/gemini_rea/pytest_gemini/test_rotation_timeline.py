import pytest
import sys
from pathlib import Path

exp_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(exp_dir))

from rotation_timeline_codec import (
    RotationTimelineCodec,
    TeamRotationPlan,
    PlayerMinuteAllocation,
    TOTAL_TEAM_MINUTES
)

def test_minutes_field_bitfield_exact():
    # Native function 0x11b2bb0:
    # and dword ptr [rdx + 0xf8], 0xfe03ffff
    # shl eax, 0x12
    # or dword ptr [rdx + 0xf8], eax
    original_dword = 0x12345678
    minutes = 36 # 36 minutes
    
    encoded = RotationTimelineCodec.encode_player_minutes_field(minutes, original_dword)
    decoded = RotationTimelineCodec.decode_player_minutes_field(encoded)
    
    assert decoded == 36
    # Check that bits outside 18..24 were preserved
    mask_outside = 0xfe03ffff
    assert (encoded & mask_outside) == (original_dword & mask_outside)

def test_team_rotation_validation():
    allocations = [
        PlayerMinuteAllocation(player_id=1, roster_index=0, minutes=36, role_id=0),
        PlayerMinuteAllocation(player_id=2, roster_index=1, minutes=34, role_id=0),
        PlayerMinuteAllocation(player_id=3, roster_index=2, minutes=32, role_id=0),
        PlayerMinuteAllocation(player_id=4, roster_index=3, minutes=30, role_id=0),
        PlayerMinuteAllocation(player_id=5, roster_index=4, minutes=28, role_id=0),
        PlayerMinuteAllocation(player_id=6, roster_index=5, minutes=24, role_id=1), # 6th man
        PlayerMinuteAllocation(player_id=7, roster_index=6, minutes=20, role_id=2),
        PlayerMinuteAllocation(player_id=8, roster_index=7, minutes=18, role_id=2),
        PlayerMinuteAllocation(player_id=9, roster_index=8, minutes=18, role_id=2),
        PlayerMinuteAllocation(player_id=10, roster_index=9, minutes=0, role_id=4),
    ]
    # Total = 36+34+32+30+28 + 24+20+18+18 = 240
    plan = TeamRotationPlan(team_id=10, allocations=allocations)
    valid, msg = plan.validate_minutes()
    assert valid is True
    assert msg == "Valid"

def test_timeline_roundtrip():
    # 48 slices, each slice has 5 player IDs
    dummy_timeline = [[(m * 5 + i) % 15 + 1 for i in range(5)] for m in range(48)]
    plan = TeamRotationPlan(team_id=5, allocations=[], timeline_active=True, timeline=dummy_timeline)
    
    buf = bytearray(880)
    RotationTimelineCodec.encode_timeline_into_gameplan(plan, buf)
    is_active, decoded_timeline = RotationTimelineCodec.decode_timeline_from_gameplan(buf)
    
    assert is_active is True
    assert len(decoded_timeline) == 48
    assert decoded_timeline == dummy_timeline
