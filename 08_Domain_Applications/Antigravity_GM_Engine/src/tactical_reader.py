"""Full tactical and player behavior reader for NBA2K22.

Extracts:
1. Playbook contents (68 play slots categorized into Regular, Bench B1-B5, Endgame, Favorite).
2. Player 4 ordered Play Types, Play Initiator flag, and unique player IDs.
3. Player 99 Tendencies grouped by tactical dimensions with strict Ability separation.
4. Head Coach attributes, 8 system proficiencies, and staff ratings.
5. Individual matchup defensive settings and opponent-player binding.
"""

from typing import Dict, List, Any, Optional
import struct
import zlib
from coach_locator import CoachLocator, read_exact, u64
from coaching_reader import defensive_catalog, DEFENSE_NAMES

# 16 standard Play Type enums in NBA 2K22
PLAY_TYPE_NAMES = {
    0: "None",
    1: "Isolation",
    2: "Isolation Point",
    3: "Isolation Wing",
    4: "P&R Ball Handler",
    5: "P&R Point",
    6: "P&R Wing",
    7: "P&R Roll Man",
    8: "Post Up Low",
    9: "Post Up High",
    10: "Guard Post Up",
    11: "Cutter",
    12: "Handoff Receiver",
    13: "Handoff Passer",
    14: "Mid Range",
    15: "3 PT"
}

# 8 System Proficiency names in NBA 2K22
SYSTEM_PROFICIENCY_NAMES = [
    "Balanced",
    "Grit & Grind",
    "Pace & Space",
    "Perimeter Centric",
    "Post Centric",
    "Triangle",
    "Seven Seconds",
    "Defense First"
]

# Key tendency offset mapping (relative to player struct base, stride 0x4F0)
# Verified offsets from docs/07_PLAYER_TENDENCY_GUIDE.md and live memory
TENDENCY_OFFSETS = {
    # Core Shot & Touches
    "SHOT_TENDENCY": 0x458,
    "DRIVING_LAYUP_TENDENCY": 0x459,
    "STANDING_DUNK_TENDENCY": 0x45A,
    "DRIVING_DUNK_TENDENCY": 0x45B,
    "FLASHY_DUNK_TENDENCY": 0x45C,
    "ALLEY_OOP_TENDENCY": 0x45D,
    "PUTBACK_TENDENCY": 0x45E,
    "CRASH_TENDENCY": 0x45F,
    "SPIN_LAYUP_TENDENCY": 0x460,
    "HOP_STEP_LAYUP_TENDENCY": 0x461,
    "EURO_STEP_LAYUP_TENDENCY": 0x462,
    "FLOATER_TENDENCY": 0x463,
    "STEP_THROUGH_SHOT_TENDENCY": 0x464,
    "SHOT_UNDER_BASKET_TENDENCY": 0x465,
    "SHOT_CLOSE_TENDENCY": 0x466,
    "SHOT_MID_RANGE_TENDENCY": 0x46A,
    "SPOT_UP_SHOT_MID_RANGE": 0x46B,
    "OFF_SCREEN_SHOT_MID_RANGE": 0x46C,
    "SHOT_THREE_TENDENCY": 0x472,
    "SPOT_UP_SHOT_THREE": 0x473,
    "OFF_SCREEN_SHOT_THREE": 0x474,
    "CONTESTED_JUMPER_THREE": 0x47A,
    "CONTESTED_JUMPER_MID_RANGE": 0x47B,
    "STEPBACK_JUMPER_THREE": 0x47C,
    "STEPBACK_JUMPER_MID_RANGE": 0x47D,
    "SPIN_JUMPER_TENDENCY": 0x47E,
    "TRANSITION_PULL_UP_THREE": 0x47F,
    "DRIVE_PULL_UP_THREE": 0x480,
    "DRIVE_PULL_UP_MID_RANGE": 0x481,
    "DRIVE_TENDENCY": 0x483,
    "SPOT_UP_DRIVE_TENDENCY": 0x484,
    "OFF_SCREEN_DRIVE_TENDENCY": 0x485,
    "ATTACK_STRONG_ON_DRIVE": 0x497,
    "DISH_TO_OPEN_MAN_TENDENCY": 0x498,
    "TOUCHES_TENDENCY": 0x499,
    "POST_UP_TENDENCY": 0x49A,
    "ROLL_VS_POP_TENDENCY": 0x49B,
    "TRANSITION_SPOT_UP": 0x49C,
    "PLAY_DISCIPLINE_TENDENCY": 0x4A1,
    "FLASHY_PASS_TENDENCY": 0x4B2,
    "ALLEY_OOP_PASS_TENDENCY": 0x4B3,
    "PASS_INTERCEPTION_TENDENCY": 0x4B4,
    "TAKE_CHARGE_TENDENCY": 0x4B5,
    "ON_BALL_STEAL_TENDENCY": 0x4B6,
    "CONTEST_SHOT_TENDENCY": 0x4B7,
    "BLOCK_SHOT_TENDENCY": 0x4B8,
    "FOUL_TENDENCY": 0x4B9,
    "HARD_FOUL_TENDENCY": 0x4BA
}


def read_player_tactical_data(mem, player_addr: int) -> Dict[str, Any]:
    """Read a single player's PlayTypes, Initiator flag, Tendencies, and Identity."""
    raw = read_exact(mem, player_addr, 0x4F0)
    name = raw[:0x30].decode("utf-16le", errors="ignore").split("\0")[0]
    player_id = int.from_bytes(raw[0x2F8:0x2FA], "little")

    # PlayTypes at 0x168 (PT1: bits 0-3, PT2: bits 4-7) and 0x169 (PT3: bits 0-3, PT4: bits 4-7)
    pt1 = raw[0x168] & 0x0F
    pt2 = (raw[0x168] >> 4) & 0x0F
    pt3 = raw[0x169] & 0x0F
    pt4 = (raw[0x169] >> 4) & 0x0F
    is_initiator = bool((raw[0x16A] >> 2) & 0x01)

    play_types = [
        {"slot": 1, "raw": pt1, "name": PLAY_TYPE_NAMES.get(pt1, "Unknown")},
        {"slot": 2, "raw": pt2, "name": PLAY_TYPE_NAMES.get(pt2, "Unknown")},
        {"slot": 3, "raw": pt3, "name": PLAY_TYPE_NAMES.get(pt3, "Unknown")},
        {"slot": 4, "raw": pt4, "name": PLAY_TYPE_NAMES.get(pt4, "Unknown")}
    ]

    # Read all verified tendencies (Offsets 0x458 to 0x4BA)
    tendencies = {}
    for t_name, offset in TENDENCY_OFFSETS.items():
        tendencies[t_name] = raw[offset]

    # Group tendencies for easy tactical analysis
    tactical_groups = {
        "creation": {
            "touches": tendencies.get("TOUCHES_TENDENCY", 50),
            "shot": tendencies.get("SHOT_TENDENCY", 50),
            "drive": tendencies.get("DRIVE_TENDENCY", 50),
            "dish_to_open_man": tendencies.get("DISH_TO_OPEN_MAN_TENDENCY", 50),
            "play_discipline": tendencies.get("PLAY_DISCIPLINE_TENDENCY", 50),
            "post_up": tendencies.get("POST_UP_TENDENCY", 50),
            "roll_vs_pop": tendencies.get("ROLL_VS_POP_TENDENCY", 50)
        },
        "shooting": {
            "shot_close": tendencies.get("SHOT_CLOSE_TENDENCY", 50),
            "shot_mid": tendencies.get("SHOT_MID_RANGE_TENDENCY", 50),
            "shot_three": tendencies.get("SHOT_THREE_TENDENCY", 50),
            "spot_up_three": tendencies.get("SPOT_UP_SHOT_THREE", 50),
            "off_screen_three": tendencies.get("OFF_SCREEN_SHOT_THREE", 50),
            "transition_three": tendencies.get("TRANSITION_PULL_UP_THREE", 50)
        },
        "defense": {
            "contest_shot": tendencies.get("CONTEST_SHOT_TENDENCY", 50),
            "block_shot": tendencies.get("BLOCK_SHOT_TENDENCY", 50),
            "on_ball_steal": tendencies.get("ON_BALL_STEAL_TENDENCY", 50),
            "pass_interception": tendencies.get("PASS_INTERCEPTION_TENDENCY", 50),
            "foul": tendencies.get("FOUL_TENDENCY", 50),
            "take_charge": tendencies.get("TAKE_CHARGE_TENDENCY", 50)
        }
    }

    return {
        "player_id": player_id,
        "name": name,
        "address": hex(player_addr),
        "is_play_initiator": is_initiator,
        "play_types": play_types,
        "active_play_types": [pt["name"] for pt in play_types if pt["raw"] != 0],
        "tendencies": tendencies,
        "tactical_profile": tactical_groups
    }


def read_team_playbook(mem, playbook_data_addr: int) -> Dict[str, Any]:
    """Read a 360-byte PLAYBOOKDATA structure and parse all 68 play slots."""
    raw = read_exact(mem, playbook_data_addr, 0x168)
    name = raw[:0x38].decode("utf-16le", errors="ignore").split("\0")[0]
    unique_id = int.from_bytes(raw[0x3E:0x40], "little")
    enum_id = raw[0x54] & 127

    slots = list(struct.unpack_from("<68I", raw, 0x58))
    regular_slots = slots[:30]
    bench_slots = slots[30:50]
    endgame_slots = slots[50:60]
    favorite_slots = slots[60:68]

    def decode_active(subslots):
        return [hex(c) for c in subslots if c != 0]

    return {
        "playbook_name": name,
        "unique_id": unique_id,
        "enum_id": enum_id,
        "address": hex(playbook_data_addr),
        "slot_counts": {
            "total_active": sum(1 for c in slots if c != 0),
            "regular_active": sum(1 for c in regular_slots if c != 0),
            "bench_active": sum(1 for c in bench_slots if c != 0),
            "endgame_active": sum(1 for c in endgame_slots if c != 0),
            "favorite_active": sum(1 for c in favorite_slots if c != 0)
        },
        "plays": {
            "regular_plays": decode_active(regular_slots),
            "bench_formation_plays": decode_active(bench_slots),
            "endgame_plays": decode_active(endgame_slots),
            "favorite_plays": decode_active(favorite_slots)
        },
        "all_active_crcs": decode_active(slots)
    }


def read_coach_attributes(mem, coach_addr: int) -> Dict[str, Any]:
    """Read coach attributes, system proficiencies, and staff ratings."""
    raw = read_exact(mem, coach_addr, 0x160)
    first_name = raw[0x30:0x58].decode("utf-16le", errors="ignore").split("\0")[0]
    last_name = raw[0x58:0x80].decode("utf-16le", errors="ignore").split("\0")[0]

    # System proficiencies at 0xEC - 0xF3
    system_proficiencies = {}
    for idx, sys_name in enumerate(SYSTEM_PROFICIENCY_NAMES):
        system_proficiencies[sys_name] = raw[0xEC + idx]

    # Staff Ratings at 0x100 (4 bits each)
    val_100 = struct.unpack_from("<I", raw, 0x100)[0]
    val_104 = struct.unpack_from("<I", raw, 0x104)[0]

    grade_keys = [
        "coach_offense", "coach_defense", "training", "scouting",
        "contract_negotiation", "trade_negotiation", "business_savvy", "emotional_iq"
    ]
    ratings = {}
    max_ratings = {}
    for idx, key in enumerate(grade_keys):
        shift = idx * 4
        ratings[key] = (val_100 >> shift) & 0x0F
        max_ratings[key] = (val_104 >> shift) & 0x0F

    # Lynchpin info at 0x114
    lynchpin_pos = (struct.unpack_from("<I", raw, 0x114)[0]) & 0x07

    return {
        "coach_name": f"{first_name} {last_name}",
        "address": hex(coach_addr),
        "system_proficiencies": system_proficiencies,
        "highest_proficiency_system": max(system_proficiencies, key=system_proficiencies.get),
        "staff_ratings": ratings,
        "max_staff_ratings": max_ratings,
        "lynchpin_position_code": lynchpin_pos
    }


def read_team_tactical_snapshot(locator: CoachLocator, team_id: int) -> Dict[str, Any]:
    """Read complete tactical state for a given team in the live session."""
    mem = locator.mem
    team = locator.teams.get(team_id)
    if not team:
        raise ValueError(f"Team ID {team_id} not found in locator.")

    # 1. Roster & Players
    p_table = locator.directory["players"]
    players = []
    for off in range(0, 0xC8, 8):
        ptr = u64(mem, team["address"] + off)
        if ptr:
            p_data = read_player_tactical_data(mem, ptr)
            players.append(p_data)

    # 2. Coach
    coach_info = locator.coaches[team_id]
    coach_attrs = read_coach_attributes(mem, coach_info["address"])

    # 3. Playbook
    # Find team's assigned PlaybookID from coach data
    from coach_codec import decode
    fields = locator.profile["fields"]
    coach_raw = read_exact(mem, coach_info["address"], 0x160)
    pb_id = decode(coach_raw, fields["PlaybookID"])
    active_system = decode(coach_raw, fields["ActiveSystem"])
    preferred_system = decode(coach_raw, fields["PreferredSystem"])

    # Locate loaded playbook
    n = locator.profile["native"]
    pb_base = u64(mem, locator.roster + n["playbook_pointer_offset"])
    pb_entry = next((p for p in locator.playbooks if p["enum_id"] == pb_id), None)
    playbook_data = None
    if pb_entry:
        pb_addr = pb_base + pb_entry["index"] * n["playbook_stride"]
        playbook_data = read_team_playbook(mem, pb_addr)

    # 4. Matchup Defenses for this team
    def_catalog = defensive_catalog(locator)
    gameplan_mgr = locator.managers[team_id]
    matchup_defenses = {}
    for idx in range(n["gameplan_capacity"]):
        gp_addr = gameplan_mgr + n["gameplan_start"] + idx * n["gameplan_stride"]
        gp_raw = read_exact(mem, gp_addr, n["gameplan_stride"])
        owner = int.from_bytes(gp_raw[2:4], "little")
        opp = int.from_bytes(gp_raw[4:6], "little")
        if owner != team_id or opp not in locator.teams:
            continue
        opp_abbr = locator.teams[opp]["abbreviation"]
        
        # Read matchups in this gameplan
        matchups = []
        for j in range((0x178 - 0x64) // 12):
            start = 0x64 + j * 12
            m_id = int.from_bytes(gp_raw[start:start+2], "little")
            d_id = int.from_bytes(gp_raw[start+2:start+4], "little")
            if m_id != 65535:
                # Decode 8-byte settings
                data = gp_raw[start+4:start+12]
                settings = {}
                for name, field in def_catalog.items():
                    shift = field["offset"] * 8 + field["start_bit"]
                    val = (int.from_bytes(data, "little") >> shift) & ((1 << field["width"]) - 1)
                    settings[name] = val
                matchups.append({
                    "opponent_player_id": m_id,
                    "assigned_defender_id": d_id if d_id != 65535 else None,
                    "settings": settings
                })
        matchup_defenses[opp_abbr] = {
            "opponent_team_id": opp,
            "matchup_count": len(matchups),
            "matchups": matchups
        }

    return {
        "team_id": team_id,
        "team_name": team["name"],
        "abbreviation": team["abbreviation"],
        "active_system_id": active_system,
        "preferred_system_id": preferred_system,
        "coach": coach_attrs,
        "playbook": playbook_data,
        "players": players,
        "opponent_matchup_defenses": matchup_defenses
    }
