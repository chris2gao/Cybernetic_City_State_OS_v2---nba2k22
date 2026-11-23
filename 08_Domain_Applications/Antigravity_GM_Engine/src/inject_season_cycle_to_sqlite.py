# -*- coding: utf-8 -*-
"""
NBA 2K22 Antigravity 赛季周期 30 队战术与攻防博弈 SQLite 底层离线批量注入引擎 (v2.0)
(Universal Full-Dimensional Season Cycle Tactical & Assets SQLite Batch Injector v2.0)

标准作业触发命令 (SOP Trigger):
  python 08_Domain_Applications/Antigravity_GM_Engine/src/inject_season_cycle_to_sqlite.py --spec-path "C:\\nba2k22\\exports\\cycle_02_30_teams_realism_execution_ready.json" --commit

功能：
1. 自动创建数据库快照备份；
2. 直接向 C:\\nba2k22\\saves\\MyLEAGUE0005\\league_state.sqlite 执行 30 队全量批量修改；
3. 更新 player_source_details.raw_struct 二进制结构体（touches, dish, play_discipline, shot_three, roll_vs_pop, is_play_initiator, play_types）；
4. 更新 coaching_team_observations.observation_json 教练控制块；
5. 输出标准化全量回执。
"""

import os
import sys
import json
import sqlite3
import shutil
import argparse
from datetime import datetime
from typing import Dict, List, Any


def run_sqlite_injection(db_path: str, spec_path: str, commit: bool = False) -> Dict[str, Any]:
    print("=" * 90)
    print("NBA 2K22 FULL-DIMENSIONAL TACTICAL BATCH INJECTOR FOR SQLITE DATABASE (v2.0)")
    print("=" * 90)
    print(f"[*] 执行模式: {'【正式写入 COMMIT】' if commit else '【预览模式 DRY-RUN】'}")
    print(f"[*] 目标数据库: {db_path}")
    print(f"[*] 规格书路径: {spec_path}")

    if not os.path.exists(db_path):
        raise FileNotFoundError(f"未找到目标数据库: {db_path}")
    if not os.path.exists(spec_path):
        raise FileNotFoundError(f"未找到规格书: {spec_path}")

    # 1. 安全前置备份
    if commit:
        backup_dir = os.path.dirname(db_path)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(backup_dir, f"league_state_pre_cycle02_{timestamp}.sqlite")
        shutil.copyfile(db_path, backup_path)
        print(f"[+] 安全前置快照已创建: {backup_path}")

    if os.path.isdir(spec_path):
        single_files = sorted([os.path.join(spec_path, f) for f in os.listdir(spec_path) if f.endswith("_native_mod.json")])
        teams_list = []
        for sf in single_files:
            with open(sf, "r", encoding="utf-8") as f:
                teams_list.append(json.load(f))
        batches = [{"batch_id": "ALL_30_SINGLE_TEAMS", "division": "Full League Single Teams", "teams": teams_list}]
        task_id = "CYCLE_02_30_TEAMS_SINGLE_EXECUTION"
    else:
        with open(spec_path, "r", encoding="utf-8") as f:
            spec = json.load(f)

        task_id = spec.get("task_package_id", f"SINGLE_TEAM_{spec.get('team_abbr', 'CUSTOM')}_NATIVE_REBALANCE")
        batches = spec.get("batches", [])
        if not batches and "team_id" in spec:
            batches = [{"batch_id": f"TEAM_{spec.get('team_abbr', spec['team_id'])}", "division": spec.get("team_name", "Single Team"), "teams": [spec]}]

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    total_players_patched = 0
    total_coaching_patched = 0
    mismatches = []
    batch_summaries = []

    try:
        for b_idx, b in enumerate(batches, 1):
            bid = b.get("batch_id")
            bname = b.get("division")
            b_teams = b.get("teams", [])
            print(f"\n>>> 正在处理第 {b_idx}/6 批次: 【{bid}】({bname} 赛区, 共 {len(b_teams)} 队)")

            b_players = 0
            b_coaches = 0

            for t in b_teams:
                tid = t.get("team_id")
                tabbr = t.get("team_abbr")
                tname = t.get("team_name")

                # --- 1. 更新球员维度 ---
                player_writes = t.get("player_writes", [])
                for p in player_writes:
                    pname = p.get("player_name")
                    ridx = p.get("roster_index")
                    playbook = p.get("tactical_playbook", {})
                    mods = p.get("modifications", [])

                    cursor.execute(
                        "SELECT raw_struct, details_json FROM player_source_details WHERE team_id=? AND roster_slot=?",
                        (tid, ridx)
                    )
                    row = cursor.fetchone()
                    if not row or not row[0]:
                        mismatches.append(f"Team {tabbr} 球员 {pname} (Slot {ridx}): 未在数据库中找到记录")
                        continue

                    raw_bytes = bytearray(row[0])
                    if len(raw_bytes) != 1264:
                        mismatches.append(f"Team {tabbr} 球员 {pname} (Slot {ridx}): 原始结构体长度异常 ({len(raw_bytes)} != 1264)")
                        continue

                    # 应用属性与倾向
                    for mod in mods:
                        field = mod.get("field")
                        off = mod.get("offset")
                        val = mod.get("val_raw")
                        if 0 <= off < 1264:
                            raw_bytes[off] = int(val) & 0xFF

                    # 应用战术发起人 (0x16A bit 2)
                    if "is_play_initiator" in playbook:
                        init_val = 1 if playbook["is_play_initiator"] else 0
                        raw_bytes[0x16A] = (raw_bytes[0x16A] & ~(1 << 2)) | ((init_val & 1) << 2)

                    # 应用战术类型 (0x168 & 0x169)
                    if "play_types" in playbook and len(playbook["play_types"]) >= 4:
                        pts = playbook["play_types"]
                        raw_bytes[0x168] = (int(pts[0]) & 0x0F) | ((int(pts[1]) & 0x0F) << 4)
                        raw_bytes[0x169] = (int(pts[2]) & 0x0F) | ((int(pts[3]) & 0x0F) << 4)

                    # 更新 details_json
                    details_dict = {}
                    if row[1]:
                        try:
                            details_dict = json.loads(row[1])
                        except Exception:
                            details_dict = {}

                    details_dict["touches"] = raw_bytes[1177]
                    details_dict["dish_to_open_man"] = raw_bytes[1176]
                    details_dict["play_discipline"] = raw_bytes[1181]
                    details_dict["shot_three"] = raw_bytes[1182]
                    details_dict["roll_vs_pop"] = raw_bytes[1184]
                    details_dict["is_play_initiator"] = (raw_bytes[0x16A] >> 2) & 1
                    details_dict["play_types"] = [
                        raw_bytes[0x168] & 0x0F,
                        (raw_bytes[0x168] >> 4) & 0x0F,
                        raw_bytes[0x169] & 0x0F,
                        (raw_bytes[0x169] >> 4) & 0x0F
                    ]

                    if commit:
                        cursor.execute(
                            "UPDATE player_source_details SET raw_struct=?, details_json=? WHERE team_id=? AND roster_slot=?",
                            (bytes(raw_bytes), json.dumps(details_dict, ensure_ascii=False), tid, ridx)
                        )
                    b_players += 1
                    total_players_patched += 1

                # --- 2. 更新教练观察维度 ---
                c_writes = t.get("coaching_writes", [])
                c_mods = t.get("coaching_modifications", {})
                if c_writes or c_mods:
                    cursor.execute(
                        "SELECT observation_json FROM coaching_team_observations WHERE team_id=?",
                        (tid,)
                    )
                    c_row = cursor.fetchone()
                    obs_dict = {}
                    if c_row and c_row[0]:
                        try:
                            obs_dict = json.loads(c_row[0])
                        except Exception:
                            obs_dict = {}

                    # 从 coaching_writes 解析
                    for cw in c_writes:
                        fname = cw.get("field_name")
                        val = cw.get("val_raw")
                        if fname == "active_system":
                            obs_dict["ActiveSystem"] = val
                        elif fname == "preferred_system":
                            obs_dict["PreferredSystem"] = val
                        elif fname == "bench_depth":
                            obs_dict["BenchDepth"] = val
                        elif fname == "bench_utilization":
                            obs_dict["BenchUtilization"] = val
                        elif fname == "run_play_tendency":
                            obs_dict["RunPlayTendency"] = val
                        elif fname == "help_defense":
                            obs_dict["HelpDefense"] = val
                        elif fname == "zone_usage":
                            obs_dict["ZoneUsage"] = val

                    # 补充高阶 POE 设置
                    if "poe_offense" in c_mods:
                        obs_dict["POEOffense"] = c_mods["poe_offense"]
                    if "poe_defense" in c_mods:
                        obs_dict["POEDefense"] = c_mods["poe_defense"]
                    if "poe_defense_physicality" in c_mods:
                        obs_dict["POEDefensePhysicality"] = c_mods["poe_defense_physicality"]
                    if "poe_defense_rebound" in c_mods:
                        obs_dict["POEDefenseRebound"] = c_mods["poe_defense_rebound"]
                    if "tempo" in c_mods:
                        obs_dict["Tempo"] = c_mods["tempo"]

                    if commit:
                        cursor.execute(
                            "UPDATE coaching_team_observations SET observation_json=? WHERE team_id=?",
                            (json.dumps(obs_dict, ensure_ascii=False), tid)
                        )
                    b_coaches += 1
                    total_coaching_patched += 1

            batch_summaries.append({
                "batch_id": bid,
                "division": bname,
                "teams_count": len(b_teams),
                "players_patched": b_players,
                "coaching_patched": b_coaches
            })
            print(f"    - 完成 {bname} 赛区: 注入球员 {b_players} 人，更新教练控制块 {b_coaches} 支")

        if commit:
            conn.commit()
            print("\n[+] SQLite 事务成功提交 (COMMIT SUCCESSFUL)！")
        else:
            conn.rollback()
            print("\n[*] DRY-RUN 预览模式结束，未修改数据库内容。")

    finally:
        conn.close()

    receipt = {
        "task_id": task_id,
        "execution_time": datetime.now().isoformat(),
        "commit_mode": commit,
        "database_target": db_path,
        "total_players_patched": total_players_patched,
        "total_coaching_patched": total_coaching_patched,
        "batches": batch_summaries,
        "mismatches": mismatches
    }

    receipt_path = os.path.join(r"C:\nba2k22\exports", "cycle_02_sqlite_injection_receipt.json")
    with open(receipt_path, "w", encoding="utf-8") as f:
        json.dump(receipt, f, indent=2, ensure_ascii=False)
    print(f"[+] 注入回执已生成: {receipt_path}")

    return receipt


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NBA 2K22 Cycle 02 SQLite Batch Injector")
    parser.add_argument("--db-path", default=r"C:\nba2k22\saves\MyLEAGUE0005\league_state.sqlite", help="Path to league_state.sqlite")
    parser.add_argument("--spec-path", default=r"C:\nba2k22\exports\cycle_02_30_teams_realism_execution_ready.json", help="Path to cycle_02 spec JSON")
    parser.add_argument("--commit", action="store_true", help="Execute write to SQLite (otherwise dry-run)")
    args = parser.parse_args()

    run_sqlite_injection(args.db_path, args.spec_path, args.commit)
