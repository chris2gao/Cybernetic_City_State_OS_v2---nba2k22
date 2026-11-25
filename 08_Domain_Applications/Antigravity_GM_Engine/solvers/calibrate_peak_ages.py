"""Reusable Peak Age (PEAKSTART / PEAKEND) Calibration Engine (Doc 95).

Supports scope modes:
  - ACTIVE_LEAGUE: All 30 teams active rosters in league_state.sqlite
  - SINGLE_TEAM:   Specific team_id in league_state.sqlite
  - DRAFT_CLASS:   Specific draft class / player list (extensible)

Physical Layout (NBA 2K22 PLAYER_STRUCT):
  - uint16 at offset 114 (0x72):
      bits 0..3   : reserved flags (preserve via & 0x000F)
      bits 4..9   : PEAKSTART (6 bits)
      bits 10..15 : PEAKEND (6 bits, equivalent to byte 115 bits 2..7)
"""

import argparse
import json
import os
import sqlite3
from datetime import datetime

DB_URI = "file:C:/nba2k22/saves/MyLEAGUE0005/league_state.sqlite?mode=ro"

# Exact Historical & Evolving Calibration Table: player_name -> (peak_start, peak_end, timeline, rationale)
CALIBRATION_TABLE = {
    # === ERA 1984 HISTORICAL TIMELINE ===
    "Michael Jordan": (24, 36, "ERA_1984", "纪元历史线：24岁起飞，33~35岁仍包揽MVP与三连冠FMVP，巅峰延续至36岁"),
    "Hakeem Olajuwon": (24, 34, "ERA_1984", "纪元历史线：修复原23..26严重截断，31~32岁夺双冠FMVP，巅峰延续至34岁"),
    "John Stockton": (25, 36, "ERA_1984", "纪元历史线：修复原25..31截断，助攻王与全明星水准一直延续至36岁"),
    "Charles Barkley": (24, 33, "ERA_1984", "纪元历史线：修复原24..27截断，29岁夺MVP并保持统治力至33岁"),
    "Kevin Willis": (26, 35, "ERA_1984", "纪元历史线：常青铁血内线，29岁入选最佳阵容，高水准延续至35岁"),
    "Otis Thorpe": (25, 33, "ERA_1984", "纪元历史线：休斯顿夺冠核心大前锋，巅峰期覆盖25~33岁"),
    "Sam Perkins": (25, 34, "ERA_1984", "纪元历史线：空间大前锋常青树，30~34岁仍为总决赛主力"),
    "Jerome Kersey": (24, 31, "ERA_1984", "纪元历史线：修复原23..26截断，开拓者两进总决赛主力侧翼至31岁"),
    "Alvin Robertson": (23, 30, "ERA_1984", "纪元历史线：DPOY级外线铁闸，巅峰期23~30岁"),
    "Sam Bowie": (23, 29, "ERA_1984", "纪元历史线：受困伤病早熟中锋，巅峰期23~29岁"),
    "Jay Humphries": (24, 30, "ERA_1984", "纪元历史线：主力控卫巅峰24~30岁"),
    "Tony Campbell": (25, 30, "ERA_1984", "纪元历史线：修复原24..27截断，森林狼核心得分手至30岁"),
    "Ron Anderson": (25, 31, "ERA_1984", "纪元历史线：修复原23..26截断，76人时期主力第六人至31岁"),
    "Steve Burtt": (24, 30, "ERA_1984", "纪元历史线：修复原24..27截断"),
    "Tim McCormick": (24, 30, "ERA_1984", "纪元历史线：修复原24..27截断"),
    "Victor Fleming": (24, 31, "ERA_1984", "纪元历史线：修复原24..27截断，步行者主力后卫至31岁"),
    "Jim Petersen": (24, 30, "ERA_1984", "纪元历史线：修复原22..23极度异常截断"),
    "Bernard Thompson": (24, 30, "ERA_1984", "纪元历史线：修复原24..25极度异常截断"),

    # === MODERN TIMELINE: 2022-2026 LATE BLOOMERS & EVOLVING STARS ===
    "Jalen Brunson": (29, 34, "MODERN_2022_2026", "现代线晚熟超巨：26~28岁在NYK爆发至97档MVP候选，推迟peak_start至29防止提前锁死"),
    "Shai Gilgeous-Alexander": (27, 34, "MODERN_2022_2026", "现代线MVP级蜕变：24~26岁连续一阵并冲刺MVP，推迟peak_start至27"),
    "Lauri Markkanen": (28, 33, "MODERN_2022_2026", "现代线大器晚成：25~27岁在爵士蜕变为全明星核心，推迟peak_start至28"),
    "Derrick White": (29, 34, "MODERN_2022_2026", "现代线大器晚成：28~30岁在凯尔特人成为二防冠军拼图，推迟peak_start至29"),
    "Tyrese Maxey": (26, 32, "MODERN_2022_2026", "现代线成长全明星：23~25岁拿下MIP与全明星首发，设26..32保障持续进化"),
    "Alperen Sengun": (26, 33, "MODERN_2022_2026", "现代线小约基奇：21~25岁高速成长为全明星中轴，设26..33"),
    "Franz Wagner": (26, 33, "MODERN_2022_2026", "现代线控球前锋：21~25岁成长为顶薪全明星，设26..33"),
    "Desmond Bane": (26, 32, "MODERN_2022_2026", "现代线重炮分卫：持续成长至24+分准全明星，设26..32"),
    "Jalen Green": (26, 32, "MODERN_2022_2026", "现代线爆炸得分手：20~25岁兑现运动天赋，设26..32"),
    "Austin Reaves": (27, 32, "MODERN_2022_2026", "现代线落选秀逆袭：24~26岁成长为湖人决胜核心，推迟peak_start至27"),
    "Coby White": (26, 32, "MODERN_2022_2026", "现代线MIP级飞跃：23~25岁成长为公牛外线引擎，设26..32"),
    "Deni Avdija": (26, 32, "MODERN_2022_2026", "现代线全能控锋：22~25岁全面兑现组织与防守，设26..32"),
    "Trey Murphy": (26, 32, "MODERN_2022_2026", "现代线核武3D：22~25岁成长为20分空间侧翼，设26..32"),
    "Jalen Johnson": (26, 32, "MODERN_2022_2026", "现代线三双控锋：21~25岁爆发为老鹰锋线核心，设26..32"),
    "Jonathan Kuminga": (26, 32, "MODERN_2022_2026", "现代线攻筐野兽：20~25岁持续兑现天赋，设26..32"),
    "Immanuel Quickley": (26, 32, "MODERN_2022_2026", "现代线亿元主控：23~25岁晋升主力控卫，设26..32"),
    "Anfernee Simons": (26, 32, "MODERN_2022_2026", "现代线微波炉射手：23~25岁稳定22+分输出，设26..32"),
    "Cameron Thomas": (26, 31, "MODERN_2022_2026", "现代线单打得分机器：21~25岁爆发得分能力，设26..31"),
    "Nicolas Claxton": (26, 32, "MODERN_2022_2026", "现代线换防护筐中锋：23~25岁成长为DPOY候选，设26..32"),
    "Mikal Bridges": (27, 33, "MODERN_2022_2026", "现代线铁人侧翼：26岁转型持球核心，设27..33"),
    "Jaren Jackson Jr.": (26, 33, "MODERN_2022_2026", "现代线DPOY内线：23~25岁攻防同步进化，设26..33"),
    "Tyrese Haliburton": (26, 33, "MODERN_2022_2026", "现代线控卫之神：22~25岁迈入一阵级传控核，设26..33"),
    "De'Aaron Fox": (26, 33, "MODERN_2022_2026", "现代线关键先生：25岁入选三阵并持续巅峰至33"),
    "Domantas Sabonis": (26, 33, "MODERN_2022_2026", "现代线策应轴心：26~28岁连续三双王与三阵，设26..33"),
    "Anthony Edwards": (25, 33, "MODERN_2022_2026", "现代线门面级超巨：21~24岁火速跨入一阵行列，设25..33"),
    "Ja Morant": (25, 32, "MODERN_2022_2026", "现代线爆发力后卫：巅峰25~32岁"),
    "LaMelo Ball": (25, 32, "MODERN_2022_2026", "现代线传控核心：巅峰25~32岁"),
    "Cade Cunningham": (26, 33, "MODERN_2022_2026", "现代线状元持球大核：21~25岁成长为全明星，设26..33"),
    "Scottie Barnes": (26, 33, "MODERN_2022_2026", "现代线全能前锋：21~25岁成长为全明星，设26..33"),
    "Evan Mobley": (26, 33, "MODERN_2022_2026", "现代线DPOY级内线：21~25岁攻防进化，设26..33"),
    "Darius Garland": (26, 32, "MODERN_2022_2026", "现代线全明星控卫：巅峰26~32岁"),
    "Zion Williamson": (25, 32, "MODERN_2022_2026", "现代线禁区怪兽：巅峰25~32岁"),
    "Jarred Vanderbilt": (25, 31, "MODERN_2022_2026", "现代线防守蓝领：23~25岁打磨防守价值，设25..31"),
    "Josh Giddey": (26, 32, "MODERN_2022_2026", "现代线高大控卫：设26..32"),

    # === MODERN TIMELINE: LONGEVITY LEGENDS & PRIME SUPERSTARS ===
    "LeBron James": (24, 39, "MODERN_LONGEVITY", "现代线历史常青树：38~40岁仍保持最佳阵容级统治力，peak_end延长至39"),
    "Stephen Curry": (25, 37, "MODERN_LONGEVITY", "现代线历史射手：34岁FMVP，36~37岁仍具顶级引力，设25..37"),
    "Kevin Durant": (24, 37, "MODERN_LONGEVITY", "现代线死神得分手：35~37岁仍维持50/40/90级别高效输出，设24..37"),
    "Chris Paul": (23, 36, "MODERN_LONGEVITY", "现代线控卫之神：35~36岁仍带队打入总决赛并入选二阵，设23..36"),
    "Al Horford": (25, 36, "MODERN_LONGEVITY", "现代线常青内线：35~36岁仍为总冠军级别首发空间护筐手，设25..36"),
    "Nikola Jokic": (25, 35, "MODERN_LONGEVITY", "现代线历史中锋：26~29岁三夺MVP，技术流高球商巅峰延至35岁"),
    "Giannis Antetokounmpo": (24, 34, "MODERN_LONGEVITY", "现代线希腊怪兽：统治力巅峰24~34岁"),
    "Luka Doncic": (24, 34, "MODERN_LONGEVITY", "现代线持球大核：20岁即一阵，巅峰24~34岁"),
    "Jayson Tatum": (25, 34, "MODERN_LONGEVITY", "现代线一阵锋线：巅峰25~34岁"),
    "Jaylen Brown": (25, 33, "MODERN_LONGEVITY", "现代线FMVP级侧翼：巅峰25~33岁"),
    "Jimmy Butler": (26, 35, "MODERN_LONGEVITY", "现代线硬汉领袖：33~34岁仍带队进总决赛，设26..35"),
    "James Harden": (24, 34, "MODERN_LONGEVITY", "现代线持球组织大师：巅峰与转型延至34岁"),
    "Damian Lillard": (25, 34, "MODERN_LONGEVITY", "现代线超远核心：巅峰延至34岁"),
    "Devin Booker": (25, 34, "MODERN_LONGEVITY", "现代线全能得分手：巅峰25~34岁"),
    "Donovan Mitchell": (25, 33, "MODERN_LONGEVITY", "现代线一阵分卫：巅峰25~33岁"),
    "Joel Embiid": (25, 32, "MODERN_LONGEVITY", "现代线MVP中锋：修复原25..29过早衰退，29~30岁正值MVP巅峰，延至32岁"),
    "Anthony Davis": (24, 33, "MODERN_LONGEVITY", "现代线攻防一体内线：30~31岁仍入选一防二阵，延至33岁"),
    "Kawhi Leonard": (24, 33, "MODERN_LONGEVITY", "现代线攻防机器：巅峰延至33岁"),
    "Paul George": (24, 34, "MODERN_LONGEVITY", "现代线双能侧翼：33~34岁仍维持全明星效率，设24..34"),
    "Kyrie Irving": (24, 34, "MODERN_LONGEVITY", "现代线人球合一大师：31~32岁总决赛主力，设24..34"),
    "Bam Adebayo": (25, 33, "MODERN_LONGEVITY", "现代线换防轴心：巅峰25~33岁"),
    "Pascal Siakam": (26, 33, "MODERN_LONGEVITY", "现代线全能锋线：巅峰26~33岁"),
    "Karl-Anthony Towns": (25, 33, "MODERN_LONGEVITY", "现代线空间中锋：巅峰25~33岁"),
    "Karl-Anthony To": (25, 33, "MODERN_LONGEVITY", "现代线空间中锋：巅峰25~33岁"),
    "Giannis Antetokoun": (24, 34, "MODERN_LONGEVITY", "现代线希腊怪兽：统治力巅峰24~34岁"),
    "Jaren Jackson Jr": (26, 33, "MODERN_2022_2026", "现代线DPOY内线：23~25岁攻防同步进化，设26..33"),
    "Shai Gilgeous-A": (27, 34, "MODERN_2022_2026", "现代线MVP级蜕变：24~26岁连续一阵并冲刺MVP，推迟peak_start至27"),
    "Rudy Gobert": (26, 33, "MODERN_LONGEVITY", "现代线4届DPOY：31岁再夺DPOY，设26..33"),
    "Jrue Holiday": (25, 34, "MODERN_LONGEVITY", "现代线冠军领防大闸：33~34岁仍入选一防二防，设25..34"),
    "Brook Lopez": (25, 35, "MODERN_LONGEVITY", "现代线空间护筐大闸：34~35岁仍为一防与DPOY亚军，设25..35"),
    "Draymond Green": (25, 34, "MODERN_LONGEVITY", "现代线防守司令官：33~34岁仍具顶级防守智商，设25..34"),
    "Klay Thompson": (25, 32, "MODERN_LONGEVITY", "现代线历史射手：大伤后巅峰截至32岁"),
    "Khris Middleton": (26, 32, "MODERN_LONGEVITY", "现代线关键中投手：巅峰26~32岁"),
    "Kyle Lowry": (26, 34, "MODERN_LONGEVITY", "现代线地板流大脑：巅峰延至34岁"),
    "DeMar DeRozan": (25, 34, "MODERN_LONGEVITY", "现代线中投活化石：32~34岁仍保持24+分高效，设25..34"),
    "Nikola Vucevic": (25, 33, "MODERN_LONGEVITY", "现代线技术型内线：巅峰25~33岁"),
    "Trae Young": (24, 32, "MODERN_LONGEVITY", "现代线挡拆引擎：巅峰24~32岁"),
    "Brandon Ingram": (25, 32, "MODERN_LONGEVITY", "现代线长臂中投侧翼：巅峰25~32岁"),
    "Fred VanVleet": (26, 32, "MODERN_LONGEVITY", "现代线稳健控卫：巅峰26~32岁"),

    # === EARLY DECLINE / INJURY IMPACTED ===
    "Blake Griffin": (23, 29, "MODERN_EARLY_DECLINE", "伤病/爆发力衰退型：30岁后运动能力大幅下滑，设23..29"),
    "Kemba Walker": (25, 30, "MODERN_EARLY_DECLINE", "伤病受限型：膝伤导致30岁后快速衰退，设25..30"),
    "John Wall": (24, 29, "MODERN_EARLY_DECLINE", "大伤受限型：跟腱伤后30岁起明显下滑，设24..29"),
    "Derrick Rose": (22, 28, "MODERN_EARLY_DECLINE", "早熟大伤型：22岁MVP后受多次大伤，巅峰22..28"),
    "Gordon Hayward": (25, 30, "MODERN_EARLY_DECLINE", "伤病受限型：设25..30"),
    "Victor Oladipo": (24, 28, "MODERN_EARLY_DECLINE", "大伤受限型：24~26岁巅峰，肌腱大伤后28岁显著下滑，设24..28"),
    "Russell Westbrook": (24, 32, "MODERN_EARLY_DECLINE", "爆发力依赖型：32岁后投射短板放大、运动能力回落，设24..32"),
    "Ben Simmons": (23, 27, "MODERN_EARLY_DECLINE", "背伤心理型：25岁后能力快速下滑，设23..27"),
    "Lonzo Ball": (24, 28, "MODERN_EARLY_DECLINE", "膝伤受限型：设24..28"),
    "Jonathan Isaac": (24, 28, "MODERN_EARLY_DECLINE", "重伤玻璃人型：设24..28"),
    "Markelle Fultz": (25, 29, "MODERN_EARLY_DECLINE", "肩伤受限型：设25..29"),
}


def read_bits(buf: bytes, byte_offset: int, start_bit: int, length: int) -> int:
    val = int.from_bytes(buf[byte_offset : byte_offset + 2], "little")
    return (val >> start_bit) & ((1 << length) - 1)


def compute_age(birth_date: str, season_year: int = 2022) -> int:
    if not birth_date or len(birth_date) < 4:
        return 22
    by = int(birth_date[:4])
    return max(18, season_year - by)


def decide_target_peak(name: str, birth_date: str, cur_ps: int, cur_pe: int):
    if name in CALIBRATION_TABLE:
        ps, pe, timeline, reason = CALIBRATION_TABLE[name]
        return ps, pe, timeline, reason

    # Check if 1984 / AI rookie truncated (birth_date >= 2000 or 1960s with short peak_end <= 27)
    is_1960s = bool(birth_date and birth_date.startswith("196"))
    is_2000s_short = bool(birth_date and birth_date.startswith("200") and cur_pe <= 27)
    if is_1960s or is_2000s_short:
        ps = max(24, min(26, cur_ps if cur_ps >= 24 else 24))
        pe = max(30, cur_pe)
        if pe <= ps + 4:
            pe = ps + 6
        return ps, pe, "ERA_1984_GENERIC", f"纪元/新秀早衰截断修复：修正原 {cur_ps}..{cur_pe} 畸形截断至标准成长曲线 {ps}..{pe}"

    # Generic Modern NBA floor: ensure no modern active player has peak_end < 30 or peak_start < 24
    ps = max(24, cur_ps)
    pe = max(30, cur_pe)
    if pe - ps < 4:
        pe = ps + 5
    if ps != cur_ps or pe != cur_pe:
        return ps, pe, "MODERN_GENERIC_FLOOR", f"现代线通用下限修复：修正原 {cur_ps}..{cur_pe} 至稳健区间 {ps}..{pe}"

    return cur_ps, cur_pe, "UNCHANGED", ""


def run_calibration(scope_mode: str, team_id: int | None, out_dir: str):
    os.makedirs(out_dir, exist_ok=True)
    conn = sqlite3.connect(DB_URI, uri=True)
    cur = conn.cursor()

    sql = """
    SELECT d.team_id, t.abbreviation, t.name, d.roster_slot, d.player_name, d.face_id, d.birth_date, d.raw_struct
    FROM player_source_details d
    LEFT JOIN teams t ON d.team_id = t.team_id
    WHERE d.snapshot_id = '2022-2023_M01_NOV'
    """
    params = []
    if scope_mode == "SINGLE_TEAM":
        if team_id is None:
            raise ValueError("--team-id is required for SINGLE_TEAM scope")
        sql += " AND d.team_id = ?"
        params.append(team_id)
    sql += " ORDER BY d.team_id, d.roster_slot"

    cur.execute(sql, params)
    rows = cur.fetchall()

    teams_data = {}
    total_scanned = 0
    total_modified = 0

    for tid, abbr, tname, slot, pname, face_id, dob, raw in rows:
        total_scanned += 1
        if not raw or len(raw) < 120:
            continue
        cur_u16 = int.from_bytes(raw[114:116], "little")
        cur_ps = (cur_u16 >> 4) & 0x3F
        cur_pe = (cur_u16 >> 10) & 0x3F

        tgt_ps, tgt_pe, timeline, reason = decide_target_peak(pname, dob, cur_ps, cur_pe)
        if tgt_ps == cur_ps and tgt_pe == cur_pe:
            continue  # Pure delta: skip unchanged players

        assert 21 <= tgt_ps < tgt_pe <= 42 and (tgt_pe - tgt_ps) >= 4, f"Invalid peak range for {pname}: {tgt_ps}..{tgt_pe}"

        new_u16 = (cur_u16 & 0x000F) | ((tgt_ps & 0x3F) << 4) | ((tgt_pe & 0x3F) << 10)
        total_modified += 1

        if tid not in teams_data:
            teams_data[tid] = {
                "protocol_version": "v2.0_full_dimensional_native_mod",
                "task_package_id": "20261125_ACTIVE_LEAGUE_PEAK_AGE_CALIBRATION",
                "scope_mode": scope_mode,
                "standard_doc": "95_PLAYER_PEAK_AGE_CALIBRATION_STANDARD_AND_SOP.md",
                "team_id": tid,
                "team_abbr": abbr,
                "team_name": tname,
                "player_writes": [],
            }

        mods = []
        if tgt_ps != cur_ps:
            mods.append({
                "field": "peak_start",
                "target_block": "PLAYER_STRUCT",
                "offset": 114,
                "bit_start": 4,
                "bit_length": 6,
                "mask_preserve": "0x000F",
                "type": "uint16_bitfield",
                "val_raw": tgt_ps,
                "current_in_game_val": cur_ps,
                "category": "GROWTH_CURVE",
                "decision_rationale": reason,
            })
        if tgt_pe != cur_pe:
            mods.append({
                "field": "peak_end",
                "target_block": "PLAYER_STRUCT",
                "offset": 115,
                "bit_start": 2,
                "bit_length": 6,
                "mask_preserve": "0x000F_AT_0x72",
                "type": "uint16_bitfield",
                "val_raw": tgt_pe,
                "current_in_game_val": cur_pe,
                "category": "GROWTH_CURVE",
                "decision_rationale": reason,
            })

        teams_data[tid]["player_writes"].append({
            "player_name": pname,
            "roster_index": slot,
            "cyberface_id": face_id,
            "birth_date": dob,
            "age_in_season": compute_age(dob, 2022),
            "timeline": timeline,
            "atomic_u16_0x72": {
                "offset": 114,
                "type": "uint16",
                "mask_preserve": "0x000F",
                "current_u16": cur_u16,
                "target_u16": new_u16,
                "peak_start": tgt_ps,
                "peak_end": tgt_pe,
            },
            "modifications": mods,
        })

    written_files = []
    for tid, payload in sorted(teams_data.items()):
        abbr = payload["team_abbr"]
        fn = f"{tid:02d}_{abbr}_peak_age_mod.json"
        fp = os.path.join(out_dir, fn)
        with open(fp, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        written_files.append((tid, abbr, fn, len(payload["player_writes"])))

    print(f"Scope={scope_mode} | Scanned={total_scanned} | Calibrated={total_modified} | Team Files={len(written_files)}")
    for tid, abbr, fn, cnt in written_files:
        print(f"  {fn:<32} -> {cnt} players")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Doc 95 Reusable Peak Age Calibration Engine")
    parser.add_argument("--scope", default="ACTIVE_LEAGUE", choices=["ACTIVE_LEAGUE", "SINGLE_TEAM"])
    parser.add_argument("--team-id", type=int, default=None)
    parser.add_argument("--out-dir", default=r"C:\nba2k22\exports\20261125_active_league_peak_age_execution")
    args = parser.parse_args()
    run_calibration(args.scope, args.team_id, args.out_dir)
