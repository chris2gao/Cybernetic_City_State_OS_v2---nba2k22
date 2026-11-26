# -*- coding: utf-8 -*-
"""
NBA 2K22 球队年度战术设计 Phase 2 确定性编译器 (IND 试点)
读取 Phase 1 报告与 native_plays_complete_catalog_v1.json，零幻觉生成：
1. 68 槽 Playbook CRC 序列
2. 12 名核心轮换球员 PlayType 1-4 与 Initiator 参数
3. 教练体系、Freelance 1-4、攻防 POE 与协防/联防滑块目标
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG_PATH = ROOT / "web_gm" / "knowledge" / "plays" / "native_plays_complete_catalog_v1.json"
REPORT_PATH = ROOT / "docs" / "98_PILOT_IND_2022_2023_TACTICAL_DESIGN_REPORT.md"
OUT_DIR = Path(r"C:\nba2k22\exports\20261126_ind_tactical_design_phase2")


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    by_name = {p["name"]: p for p in catalog["plays"]}

    doc = REPORT_PATH.read_text(encoding="utf-8")

    # 1. 解析 0-59 槽 (Regular 0-29, Bench 30-49, Endgame 50-59)
    slot_rows = re.findall(r"^\|\s*(\d+)\s*\|\s*`([^`]+)`\s*\|", doc, re.M)
    playbook_slots = {}
    for slot_str, name in slot_rows:
        slot = int(slot_str)
        if name not in by_name:
            raise ValueError(f"Unknown play name in slot {slot}: {name}")
        playbook_slots[slot] = {
            "slot": slot,
            "name": name,
            "native_crc": by_name[name]["native_crc"],
            "crc_hex": by_name[name]["crc_hex"],
            "cat_id": by_name[name]["native_category_id"],
        }

    # 2. Favorite 60-67 (精选 8 条高频战术)
    fav_names = [
        "5OUT BIG TOP FIST 1",
        "FIST 15 POP",
        "FIST 14 POP CNR",
        "FIST 5 SHORT 4 CNR",
        "FLOPPY",
        "QUICK 12 HAMMER",
        "GIVE 42 HORNS FIST",
        "5OUT BIG TOP ISO 4",
    ]
    for i, name in enumerate(fav_names):
        slot = 60 + i
        if name not in by_name:
            raise ValueError(f"Unknown favorite play: {name}")
        playbook_slots[slot] = {
            "slot": slot,
            "name": name,
            "native_crc": by_name[name]["native_crc"],
            "crc_hex": by_name[name]["crc_hex"],
            "cat_id": by_name[name]["native_category_id"],
        }

    assert len(playbook_slots) == 68, f"Expected 68 slots, got {len(playbook_slots)}"

    # 3. 12 名球员 PlayType 1-4 与 Initiator 目标 (依据报告第 5 章)
    player_playtypes = [
        {"name": "Tyrese Haliburton", "slot_values": {"1": 4, "2": 5, "3": 15, "4": 1}, "initiator": True},
        {"name": "Pascal Siakam",     "slot_values": {"1": 1, "2": 10, "3": 8, "4": 9}, "initiator": True},
        {"name": "Buddy Hield",       "slot_values": {"1": 15, "2": 12, "3": 6, "4": 11}, "initiator": False},
        {"name": "Aaron Nesmith",     "slot_values": {"1": 15, "2": 11, "3": 12, "4": 0}, "initiator": False},
        {"name": "Myles Turner",      "slot_values": {"1": 7, "2": 15, "3": 14, "4": 13}, "initiator": False},
        {"name": "T.J. McConnell",    "slot_values": {"1": 5, "2": 4, "3": 14, "4": 11}, "initiator": True},
        {"name": "Dillon Brooks",     "slot_values": {"1": 10, "2": 14, "3": 15, "4": 6}, "initiator": False},
        {"name": "DeMarcus Cousins",  "slot_values": {"1": 8, "2": 9, "3": 13, "4": 7}, "initiator": False},
        {"name": "Daniel Theis",      "slot_values": {"1": 7, "2": 14, "3": 11, "4": 13}, "initiator": False},
        {"name": "Maxi Kleber",       "slot_values": {"1": 15, "2": 7, "3": 11, "4": 0}, "initiator": False},
        {"name": "Kent Bazemore",     "slot_values": {"1": 15, "2": 11, "3": 12, "4": 0}, "initiator": False},
        {"name": "Oshae Brissett",    "slot_values": {"1": 15, "2": 11, "3": 0, "4": 0}, "initiator": False},
    ]

    # 4. 教练宏观设置目标
    coach_targets = {
        "team_id": 20,
        "abbreviation": "IND",
        "playbook_enum_id": 18,
        "settings": {
            "PreferredSystem": 2,
            "ActiveSystem": 2,
            "FreelanceType": 5,
            "FreelanceType2": 16,
            "FreelanceType3": 13,
            "FreelanceType4": 24,
            "RunPlayTendency": 75,
            "HelpDefense": 48,
            "ZoneUsage": 18,
            "Tempo": 65,
        },
        "poe": {
            "POEOffense": 4,    # PICK_AND_ROLL_OFFENSE
            "POEOffense2": 9,   # SHOOT_AT_WILL
            "POEOffense3": 12,  # LIMIT_TRANSITION
            "POEDefense": 13,   # PROTECT_PAINT
            "POEDefense2": 15,  # LIMIT_PERIMETER_SHOTS
            "POEDefense3": 21,  # RUN_IN_TRANSITION
        },
    }

    spec = {
        "spec_id": "SPEC-IND-2022-2023-TACTICAL-PHASE2",
        "team_id": 20,
        "abbreviation": "IND",
        "playbook_slots_ordered": [playbook_slots[i] for i in range(68)],
        "player_playtypes": player_playtypes,
        "coach_targets": coach_targets,
    }

    out_file = OUT_DIR / "ind_tactical_execution_spec.json"
    out_file.write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[OK] Compiled Phase 2 spec -> {out_file}")
    print(f"     Playbook slots: {len(spec['playbook_slots_ordered'])}/68")
    print(f"     Player PlayTypes: {len(spec['player_playtypes'])} players")


if __name__ == "__main__":
    main()
