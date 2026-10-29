import pytest
import sys
from pathlib import Path

# Add experimental directory to path
exp_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(exp_dir))

from coach_settings_codec import CoachSettings, CoachSettingsCodec

def test_coach_settings_roundtrip():
    original = CoachSettings(
        poe_offense_1=14,
        poe_offense_2=3,
        poe_offense_3=21,
        poe_defense_1=13,
        poe_defense_2=0,
        poe_defense_3=28,
        run_play_tendency=65,
        zone_usage=15,
        bench_depth=9,
        bench_utilization=70,
        sub_method=1,
        ace_mode=1,
        automation_flags=0b101101,
        tactical_system=4,
        freelance_slots=[101, 202, 303, 0xffff]
    )
    
    buf = bytearray(880)
    CoachSettingsCodec.encode_gameplan_tail(original, buf)
    decoded = CoachSettingsCodec.decode_gameplan_tail(buf)
    
    assert decoded.poe_offense_1 == 14
    assert decoded.poe_offense_2 == 3
    assert decoded.poe_offense_3 == 21
    assert decoded.poe_defense_1 == 13
    assert decoded.poe_defense_2 == 0
    assert decoded.poe_defense_3 == 28
    assert decoded.run_play_tendency == 65
    assert decoded.zone_usage == 15
    assert decoded.bench_depth == 9
    assert decoded.bench_utilization == 70
    assert decoded.tactical_system == 4
    assert decoded.freelance_slots[:3] == [101, 202, 303]

def test_coachdata_packing_matches_native_binary():
    # Verify bit shifts from RVA 0x146eaa0:
    # 0x13c packs:
    #   bits 0..4: [rcx+0x181] (poe_o1)
    #   bits 5..9: [rcx+0x182] << 5 (poe_o2)
    #   bits 10..14: [rcx+0x183] << 10 (poe_o3)
    #   bits 15..19: [rcx+0x17e] << 15 (poe_d1)
    #   bits 20..24: [rcx+0x17f] << 20 (poe_d2)
    #   bits 25..29: [rcx+0x180] << 25 (poe_d3)
    settings = CoachSettings(
        poe_offense_1=1,
        poe_offense_2=2,
        poe_offense_3=4,
        poe_defense_1=8,
        poe_defense_2=16,
        poe_defense_3=31,
        tactical_system=5,
        automation_flags=0x2a
    )
    
    sim = CoachSettingsCodec.simulate_apply_to_coachdata(settings)
    
    expected_13c = 1 | (2 << 5) | (4 << 10) | (8 << 15) | (16 << 20) | (31 << 25)
    assert sim["coachdata_0x13c_poe_packed"] == expected_13c
    
    expected_148 = 5 << 17
    assert sim["coachdata_0x148_system"] == expected_148
    
    expected_fc = 0x2a << 25
    assert sim["coachdata_0xfc_automation"] == expected_fc
