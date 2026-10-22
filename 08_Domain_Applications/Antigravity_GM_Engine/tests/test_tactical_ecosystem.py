import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import pytest
import struct
from unittest.mock import MagicMock

from tactical_reader import (
    PLAY_TYPE_NAMES, SYSTEM_PROFICIENCY_NAMES, TENDENCY_OFFSETS,
    read_player_tactical_data, read_team_playbook, read_coach_attributes
)
from player_tactics_adapter import (
    PlayerTacticsAdapter, assert_safe_target_offset, FORBIDDEN_PLAYER_RANGES
)
from matchup_defense_adapter import MatchupDefenseAdapter
from tactical_fit_analyzer import TacticalFitAnalyzer


def create_mock_player_raw():
    """Create a 0x4F0 byte mock player record."""
    buf = bytearray(0x4F0)
    # Name: "Test Player" in utf-16le
    name_bytes = "Test Player\0".encode("utf-16le")
    buf[:len(name_bytes)] = name_bytes

    # PlayType1=4 (P&R Ball Handler), PlayType2=1 (Isolation) at 0x168
    buf[0x168] = (1 << 4) | 4
    # PlayType3=15 (3 PT), PlayType4=0 (None) at 0x169
    buf[0x169] = (0 << 4) | 15
    # PlayInitiator at 0x16A (bit 2 = 1)
    buf[0x16A] = 1 << 2

    # Player ID at 0x2F8
    buf[0x2F8:0x2FA] = struct.pack("<H", 7777)

    # Tendencies
    buf[0x458] = 85  # SHOT_TENDENCY
    buf[0x472] = 80  # SHOT_THREE_TENDENCY
    buf[0x483] = 90  # DRIVE_TENDENCY
    buf[0x498] = 75  # DISH_TO_OPEN_MAN_TENDENCY
    buf[0x499] = 88  # TOUCHES_TENDENCY
    buf[0x4A1] = 95  # PLAY_DISCIPLINE_TENDENCY
    return bytes(buf)


def create_mock_playbook_raw():
    """Create a 0x168 byte mock playbook record."""
    buf = bytearray(0x168)
    name_bytes = "Mock Playbook\0".encode("utf-16le")
    buf[:len(name_bytes)] = name_bytes
    buf[0x3E:0x40] = struct.pack("<H", 123)
    buf[0x54] = 18  # Enum ID

    # 68 play slots at 0x58: populate 10 regular plays, 2 bench plays, 8 endgame, 8 favorite
    slots = [0] * 68
    for i in range(10):
        slots[i] = 0xAA000000 + i
    slots[30] = 0xBB000001
    slots[31] = 0xBB000002
    for i in range(8):
        slots[50 + i] = 0xCC000000 + i
        slots[60 + i] = 0xDD000000 + i
    buf[0x58:0x58 + 68 * 4] = struct.pack("<68I", *slots)
    return bytes(buf)


def create_mock_coach_raw():
    """Create a 0x160 byte mock coach record."""
    buf = bytearray(0x160)
    first = "Head\0".encode("utf-16le")
    last = "Coach\0".encode("utf-16le")
    buf[0x30:0x30 + len(first)] = first
    buf[0x58:0x58 + len(last)] = last

    # System proficiencies at 0xEC - 0xF3
    proficiencies = [70, 75, 80, 85, 60, 50, 65, 75]
    for idx, p in enumerate(proficiencies):
        buf[0xEC + idx] = p

    # Staff Ratings at 0x100: 4 bits each
    # CoachOffense=9, CoachDefense=8, Training=7, Scouting=6, etc.
    val_100 = 0x12345689
    buf[0x100:0x104] = struct.pack("<I", val_100)
    buf[0x104:0x108] = struct.pack("<I", val_100)
    return bytes(buf)


def test_tactical_reader_player():
    raw = create_mock_player_raw()
    mock_mem = MagicMock()
    mock_mem.read_bytes.return_value = raw

    data = read_player_tactical_data(mock_mem, 0x1000)
    assert data["name"] == "Test Player"
    assert data["player_id"] == 7777
    assert data["is_play_initiator"] is True
    assert data["active_play_types"] == ["P&R Ball Handler", "Isolation", "3 PT"]
    assert data["tendencies"]["SHOT_TENDENCY"] == 85
    assert data["tendencies"]["TOUCHES_TENDENCY"] == 88
    assert data["tactical_profile"]["creation"]["dish_to_open_man"] == 75


def test_tactical_reader_playbook():
    raw = create_mock_playbook_raw()
    mock_mem = MagicMock()
    mock_mem.read_bytes.return_value = raw

    pb = read_team_playbook(mock_mem, 0x2000)
    assert pb["playbook_name"] == "Mock Playbook"
    assert pb["enum_id"] == 18
    assert pb["slot_counts"]["total_active"] == 10 + 2 + 8 + 8
    assert pb["slot_counts"]["regular_active"] == 10
    assert pb["slot_counts"]["bench_active"] == 2
    assert pb["slot_counts"]["endgame_active"] == 8
    assert pb["slot_counts"]["favorite_active"] == 8


def test_tactical_reader_coach():
    raw = create_mock_coach_raw()
    mock_mem = MagicMock()
    mock_mem.read_bytes.return_value = raw

    coach = read_coach_attributes(mock_mem, 0x3000)
    assert coach["coach_name"] == "Head Coach"
    assert coach["system_proficiencies"]["Perimeter Centric"] == 85
    assert coach["highest_proficiency_system"] == "Perimeter Centric"
    assert coach["staff_ratings"]["coach_offense"] == 9
    assert coach["staff_ratings"]["coach_defense"] == 8


def test_player_tactics_adapter_safety_guards():
    # 1. Writing to Ability range must raise PermissionError
    with pytest.raises(PermissionError) as exc:
        assert_safe_target_offset(0x420, 1)
    assert "CRITICAL_SAFETY_VIOLATION" in str(exc.value)

    # 2. Writing to Contract range must raise PermissionError
    with pytest.raises(PermissionError) as exc:
        assert_safe_target_offset(0x070, 1)
    assert "CRITICAL_SAFETY_VIOLATION" in str(exc.value)

    # 3. Writing to UniqueId must raise PermissionError
    with pytest.raises(PermissionError) as exc:
        assert_safe_target_offset(0x2F8, 2)
    assert "CRITICAL_SAFETY_VIOLATION" in str(exc.value)

    # 4. Writing to authorized PlayType offsets must succeed
    assert_safe_target_offset(0x168, 1)
    assert_safe_target_offset(0x169, 1)
    assert_safe_target_offset(0x16A, 1)

    # 5. Writing to authorized Tendency offsets must succeed
    assert_safe_target_offset(0x458, 1)
    assert_safe_target_offset(0x472, 1)
    assert_safe_target_offset(0x4BA, 1)


def test_tactical_fit_analyzer():
    analyzer = TacticalFitAnalyzer()
    mock_snapshot = {
        "team_id": 20,
        "team_name": "Pacers",
        "abbreviation": "IND",
        "active_system_id": 3,  # Perimeter Centric
        "preferred_system_id": 3,
        "coach": {
            "coach_name": "Rick Carlisle",
            "system_proficiencies": {
                "Balanced": 70, "Grit & Grind": 75, "Pace & Space": 80,
                "Perimeter Centric": 85, "Post Centric": 75, "Triangle": 20,
                "Seven Seconds": 50, "Defense First": 75
            },
            "highest_proficiency_system": "Perimeter Centric"
        },
        "playbook": {
            "playbook_name": "Pacers Playbook",
            "slot_counts": {"total_active": 50}
        },
        "players": [
            {
                "name": "Primary Guy",
                "player_id": 101,
                "is_play_initiator": True,
                "play_types": [{"slot": 1, "raw": 4, "name": "P&R Ball Handler"}],
                "active_play_types": ["P&R Ball Handler"],
                "tactical_profile": {
                    "creation": {"touches": 92, "shot": 88, "drive": 90, "dish_to_open_man": 85, "post_up": 10},
                    "shooting": {"shot_three": 85, "shot_close": 50, "shot_mid": 50, "spot_up_three": 85, "off_screen_three": 80, "transition_three": 80},
                    "defense": {}
                }
            },
            {
                "name": "Shooter Guy",
                "player_id": 102,
                "is_play_initiator": False,
                "play_types": [{"slot": 1, "raw": 15, "name": "3 PT"}],
                "active_play_types": ["3 PT"],
                "tactical_profile": {
                    "creation": {"touches": 55, "shot": 60, "drive": 20, "dish_to_open_man": 45, "post_up": 0},
                    "shooting": {"shot_three": 90, "shot_close": 50, "shot_mid": 50, "spot_up_three": 95, "off_screen_three": 90, "transition_three": 70},
                    "defense": {}
                }
            }
        ]
    }

    report = analyzer.analyze_team(mock_snapshot)
    assert report["team_name"] == "Pacers"
    assert report["coach_overview"]["alignment_verdict"] == "OPTIMAL_ALIGNMENT"
    assert "Primary Guy" in report["tactical_hierarchy"]["primary_creators"]
    assert "Shooter Guy" in report["tactical_hierarchy"]["floor_spacers"]
    assert report["roster_diagnostics"][0]["recommended_training_archetype"] == "0 (进攻创造者)"
    assert report["roster_diagnostics"][1]["recommended_training_archetype"] == "2 (空间射手)"
