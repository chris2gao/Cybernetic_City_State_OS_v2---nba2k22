import pytest
import sys
from pathlib import Path

exp_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(exp_dir))

from staff_roster_codec import (
    StaffRosterCodec,
    RosterPlayerState,
    StaffMember,
    StaffRole
)

def test_roster_legality_validation():
    # 14 active players + 1 two-way = 15 total (Legal)
    legal_roster = [RosterPlayerState(player_id=i, slot_index=i, is_active=True) for i in range(14)]
    legal_roster.append(RosterPlayerState(player_id=99, slot_index=14, is_active=True, is_two_way=True))
    
    valid, msg = StaffRosterCodec.validate_roster_legality(legal_roster)
    assert valid is True
    assert msg == "Valid"
    
    # 16 active players (Illegal: exceeds 15)
    illegal_roster = [RosterPlayerState(player_id=i, slot_index=i, is_active=True) for i in range(16)]
    valid, msg = StaffRosterCodec.validate_roster_legality(illegal_roster)
    assert valid is False
    assert "exceed maximum 15" in msg

def test_staff_role_validation():
    # Native 0x1327590 checks role_id - 8 <= 0xc (Roles 8..20)
    assert StaffRosterCodec.validate_staff_role(8) is True  # HEAD_COACH
    assert StaffRosterCodec.validate_staff_role(10) is True # LEAD_SCOUT
    assert StaffRosterCodec.validate_staff_role(20) is True # Upper bound
    assert StaffRosterCodec.validate_staff_role(7) is False # Underflow
    assert StaffRosterCodec.validate_staff_role(21) is False # Overflow

def test_waive_player_shifts_slots():
    roster = [
        RosterPlayerState(player_id=1, slot_index=0),
        RosterPlayerState(player_id=2, slot_index=1),
        RosterPlayerState(player_id=3, slot_index=2),
    ]
    waived = StaffRosterCodec.simulate_waive_player(roster, player_id=2)
    assert len(waived) == 2
    assert waived[0].player_id == 1 and waived[0].slot_index == 0
    assert waived[1].player_id == 3 and waived[1].slot_index == 1
