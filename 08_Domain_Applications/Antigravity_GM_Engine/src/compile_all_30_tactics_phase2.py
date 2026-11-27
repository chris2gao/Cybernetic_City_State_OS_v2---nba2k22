# -*- coding: utf-8 -*-
"""
NBA 2K22 全联盟 30 支球队战术设计 Phase 2 确定性编译器
读取：
1. 29 支球队 Phase 1 报告 (docs/tactical_designs_2022_2023/<TEAM>_2022_2023_TACTICAL_DESIGN_REPORT.md)
   + IND 试点已验证规格 (C:/nba2k22/exports/20261126_ind_tactical_design_phase2/ind_tactical_execution_spec.json)
2. scratch/swarm_inputs/<TEAM>_m02_dec.json
3. web_gm/knowledge/plays/native_plays_complete_catalog_v1.json
4. config/coach_tactics_profile.json

输出：
C:/nba2k22/exports/20261126_all30_tactical_design_phase2/<TEAM>_spec.json
以及 manifest.json (30 队汇总与唯一 PlaybookID 校验结果)
"""
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPO_ROOT = ROOT.parents[1]
CATALOG_PATH = ROOT / "web_gm" / "knowledge" / "plays" / "native_plays_complete_catalog_v1.json"
PROFILE_PATH = ROOT / "config" / "coach_tactics_profile.json"
REPORTS_DIR = ROOT / "docs" / "tactical_designs_2022_2023"
M02_DIR = REPO_ROOT / "scratch" / "swarm_inputs"
IND_SPEC_PATH = Path(r"C:\nba2k22\exports\20261126_ind_tactical_design_phase2\ind_tactical_execution_spec.json")
OUT_DIR = Path(r"C:\nba2k22\exports\20261126_all30_tactical_design_phase2")

# 30 队严格 1-to-1 独占 Playbook enum_id 映射 (修复 CHA/MEM/ORL/WAS 原版共用 Standard=30 与 MIN/MEM 错位)
EXCLUSIVE_PLAYBOOK_ENUM = {
    "PHI": 0,   # 76ers Playbook
    "MIL": 1,   # Bucks Playbook
    "CHI": 2,   # Bulls Playbook
    "CLE": 3,   # Cavaliers Playbook
    "BOS": 4,   # Celtics Playbook
    "LAC": 5,   # Clippers Playbook
    "MEM": 6,   # Grizzlies Playbook (was 30)
    "ATL": 7,   # Hawks Playbook
    "MIA": 8,   # Heat Playbook
    "CHA": 9,   # Hornets Playbook (was 30)
    "UTA": 10,  # Jazz Playbook
    "SAC": 11,  # Kings Playbook
    "NYK": 12,  # Knicks Playbook
    "LAL": 13,  # Lakers Playbook
    "ORL": 14,  # Magic Playbook (was 30)
    "DAL": 15,  # Mavericks Playbook
    "BKN": 16,  # Nets Playbook
    "DEN": 17,  # Nuggets Playbook
    "IND": 18,  # Pacers Playbook
    "NOP": 19,  # Pelicans Playbook
    "DET": 20,  # Pistons Playbook
    "TOR": 21,  # Raptors Playbook
    "HOU": 22,  # Rockets Playbook
    "SAS": 23,  # Spurs Playbook
    "PHX": 24,  # Suns Playbook
    "OKC": 25,  # Thunder Playbook
    "MIN": 26,  # Timberwolves Playbook (was 6)
    "POR": 27,  # Trail Blazers Playbook
    "GSW": 28,  # Warriors Playbook
    "WAS": 29,  # Wizards Playbook (was 30)
}


def parse_range_or_int(s: str):
    m = re.search(r"(\d+)\s*[–\-~]\s*(\d+)", s)
    if m:
        return (int(m.group(1)) + int(m.group(2))) // 2
    m2 = re.search(r"(\d+)", s)
    return int(m2.group(1)) if m2 else None


def parse_report_to_spec(team: str, report_path: Path, m02_path: Path, by_name: dict, valid_poe: set) -> dict:
    doc = report_path.read_text(encoding="utf-8")
    m02 = json.loads(m02_path.read_text(encoding="utf-8"))
    team_id = m02["team"]["team_id"]
    coach_vals = m02.get("coach_values", {})

    # 1. 解析 68 槽 Playbook (0..59 来自表格, 60..67 来自表格或 4.4 编号列表)
    slots_map = {}
    for line in doc.splitlines():
        if "|" not in line:
            continue
        m = re.match(r"^\|\s*(\d{1,2})\s*\|", line.strip())
        if m:
            s = int(m.group(1))
            cols = [c.strip() for c in line.strip().strip("|").split("|")]
            for c in cols[1:]:
                bt = re.search(r"`([^`]+)`", c)
                cand = bt.group(1) if bt else c
                if cand in by_name:
                    slots_map[s] = cand
                    break

    # 若 60..67 未在表格中，从 ### 4.4 解析编号列表 1..8
    fav_count = sum(1 for s in range(60, 68) if s in slots_map)
    if fav_count < 8:
        sec44 = ""
        m44 = re.search(r"###\s*4\.4[^\n]*\n(.*?)(?=\n##\s|\Z)", doc, re.S)
        if m44:
            sec44 = m44.group(1)
        fav_list = []
        for line in sec44.splitlines():
            for bt in re.findall(r"`([^`]+)`", line):
                if bt in by_name and bt not in fav_list:
                    fav_list.append(bt)
        if len(fav_list) >= 8:
            for i in range(8):
                slots_map[60 + i] = fav_list[i]

    rb_slots = [s for s in range(0, 50) if s in slots_map]
    end_slots = [s for s in range(50, 60) if s in slots_map]
    fav_slots = [s for s in range(60, 68) if s in slots_map]
    assert 36 <= len(rb_slots) <= 42, f"{team}: expected 36..42 Regular+Bench plays, got {len(rb_slots)}"
    assert len(set(slots_map[s] for s in rb_slots)) == len(rb_slots), f"{team}: duplicate Regular+Bench plays"
    assert 4 <= len(end_slots) <= 6, f"{team}: expected 4..6 Endgame plays, got {len(end_slots)}"
    assert len(fav_slots) == 8, f"{team}: expected 8 Favorite plays, got {len(fav_slots)}"

    ordered_slots = []
    for s in range(68):
        if s in slots_map:
            name = slots_map[s]
            p = by_name[name]
            ordered_slots.append({
                "slot": s,
                "name": name,
                "native_crc": p["native_crc"],
                "crc_hex": p["crc_hex"],
                "cat_id": p["native_category_id"],
            })
        else:
            ordered_slots.append({
                "slot": s,
                "name": None,
                "native_crc": 0,
                "crc_hex": "0x00000000",
                "cat_id": 0,
            })

    # 2. 解析 Section 5 球员 PlayType 1-4 与 Initiator
    sec5 = doc.split("## 5.")[-1].split("## 6.")[0] if "## 5." in doc else ""
    player_playtypes = []
    for line in sec5.splitlines():
        if "|" not in line:
            continue
        cols = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cols) >= 7 and not cols[0].startswith("---") and not cols[0].startswith(":---") and "球员" not in cols[0]:
            pname = re.sub(r"\*+", "", cols[0]).strip()
            pts = []
            for c in cols[2:6]:
                mm = re.search(r"(\d+)", c)
                pts.append(int(mm.group(1)) if mm else 0)
            assert all(0 <= x <= 14 for x in pts), f"{team} {pname}: invalid PlayType {pts} (15 forbidden!)"
            init = "true" in cols[6].lower()
            player_playtypes.append({
                "name": pname,
                "slot_values": {"1": pts[0], "2": pts[1], "3": pts[2], "4": pts[3]},
                "initiator": init,
            })
    assert len(player_playtypes) >= 8, f"{team}: too few players parsed ({len(player_playtypes)})"

    # 3. 教练设置与 POE (以 M02_DEC 为基线，叠加报告中明确给出的 HelpDefense / ZoneUsage / 防守 POE 1-3，并强制独占 PlaybookID)
    settings = {
        "PlaybookID": EXCLUSIVE_PLAYBOOK_ENUM[team],
        "PreferredSystem": coach_vals.get("PreferredSystem", 0),
        "ActiveSystem": coach_vals.get("ActiveSystem", 0),
        "FreelanceType": coach_vals.get("FreelanceType", 0),
        "FreelanceType2": coach_vals.get("FreelanceType2", 0),
        "FreelanceType3": coach_vals.get("FreelanceType3", 0),
        "FreelanceType4": coach_vals.get("FreelanceType4", 0),
        "RunPlayTendency": coach_vals.get("RunPlayTendency", 65),
        "HelpDefense": coach_vals.get("HelpDefense", 50),
        "ZoneUsage": coach_vals.get("ZoneUsage", 10),
        "Tempo": coach_vals.get("Tempo", 55),
    }
    poe = {
        "POEOffense": coach_vals.get("POEOffense", 0),
        "POEOffense2": coach_vals.get("POEOffense2", 0),
        "POEOffense3": coach_vals.get("POEOffense3", 0),
        "POEOffense4": coach_vals.get("POEOffense4", 0),
        "POEDefense": coach_vals.get("POEDefense", 0),
        "POEDefense2": coach_vals.get("POEDefense2", 0),
        "POEDefense3": coach_vals.get("POEDefense3", 0),
        "POEDefense4": coach_vals.get("POEDefense4", 0),
    }

    # 从报告 3.2 提取 HelpDefense / ZoneUsage / 防守 POE 1-3
    sec32 = ""
    m32 = re.search(r"###\s*3\.2[^\n]*\n(.*?)(?=\n##\s|\Z)", doc, re.S)
    if m32:
        sec32 = m32.group(1)

    for line in sec32.splitlines():
        if "HelpDefense" in line:
            v = parse_range_or_int(line.split("HelpDefense")[-1])
            if v is not None and 0 <= v <= 100:
                settings["HelpDefense"] = v
        if "ZoneUsage" in line:
            v = parse_range_or_int(line.split("ZoneUsage")[-1])
            if v is not None and 0 <= v <= 100:
                settings["ZoneUsage"] = v

    # 提取防守 POE 枚举 (11..21)
    def_poes = []
    for m_poe in re.finditer(r"`(\d{2})\s*\([^`)]+\)`", sec32):
        val = int(m_poe.group(1))
        if val in valid_poe and val >= 11 and val not in def_poes:
            def_poes.append(val)
    if len(def_poes) >= 1:
        poe["POEDefense"] = def_poes[0]
    if len(def_poes) >= 2:
        poe["POEDefense2"] = def_poes[1]
    if len(def_poes) >= 3:
        poe["POEDefense3"] = def_poes[2]

    return {
        "team_id": team_id,
        "abbreviation": team,
        "playbook_enum_id": EXCLUSIVE_PLAYBOOK_ENUM[team],
        "playbook_slots_ordered": ordered_slots,
        "player_playtypes": player_playtypes,
        "coach_targets": {
            "team_id": team_id,
            "abbreviation": team,
            "playbook_enum_id": EXCLUSIVE_PLAYBOOK_ENUM[team],
            "settings": settings,
            "poe": poe,
        },
        "stats": {
            "reg_bench_count": len(rb_slots),
            "endgame_count": len(end_slots),
            "favorite_count": len(fav_slots),
            "player_count": len(player_playtypes),
        },
    }


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    catalog = json.loads(CATALOG_PATH.read_text(encoding="utf-8"))
    by_name = {p["name"]: p for p in catalog["plays"]}
    prof = json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
    valid_poe = {int(k) for k in prof.get("poe_enum", {}).keys()}

    manifest = []
    for team in sorted(EXCLUSIVE_PLAYBOOK_ENUM.keys()):
        if team == "IND":
            ind_spec = json.loads(IND_SPEC_PATH.read_text(encoding="utf-8"))
            ind_spec["abbreviation"] = "IND"
            ind_spec["team_id"] = 20
            ind_spec["playbook_enum_id"] = 18
            ind_spec["coach_targets"]["settings"]["PlaybookID"] = 18
            # 确保 IND 无 PlayType 15 (已于先前修复为 14)
            for pl in ind_spec["player_playtypes"]:
                for k, v in pl["slot_values"].items():
                    if v == 15:
                        pl["slot_values"][k] = 14
            spec = ind_spec
            spec["stats"] = {
                "reg_bench_count": sum(1 for x in spec["playbook_slots_ordered"][:50] if x["native_crc"] != 0),
                "endgame_count": sum(1 for x in spec["playbook_slots_ordered"][50:60] if x["native_crc"] != 0),
                "favorite_count": sum(1 for x in spec["playbook_slots_ordered"][60:68] if x["native_crc"] != 0),
                "player_count": len(spec["player_playtypes"]),
            }
        else:
            report_path = REPORTS_DIR / f"{team}_2022_2023_TACTICAL_DESIGN_REPORT.md"
            m02_path = M02_DIR / f"{team}_m02_dec.json"
            spec = parse_report_to_spec(team, report_path, m02_path, by_name, valid_poe)

        out_path = OUT_DIR / f"{team}_spec.json"
        out_path.write_text(json.dumps(spec, ensure_ascii=False, indent=2), encoding="utf-8")
        manifest.append({
            "team": team,
            "team_id": spec["team_id"],
            "playbook_enum_id": spec["playbook_enum_id"],
            **spec["stats"],
            "spec_path": str(out_path),
        })

    (OUT_DIR / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Compiled {len(manifest)}/30 team specs to {OUT_DIR}")
    for m in manifest:
        print(f"  {m['team']:3s} tid={m['team_id']:2d} pb={m['playbook_enum_id']:2d} RB={m['reg_bench_count']:2d} End={m['endgame_count']} Fav={m['favorite_count']} Players={m['player_count']:2d}")


if __name__ == "__main__":
    main()
