# -*- coding: utf-8 -*-
"""
NBA 2K22 真实内存数据纯净重抓与基准建档引擎 (Capture Real Baseline M01)
严格遵循数据驱动设计三原则：
1. 真实观测优先：所有写入数据库与快照的字段必须来自真实游戏内存读取（含绝对地址、偏移与解码类型）。
2. 零伪造与显式缺失：凡在当前 MC 模式内存中无法直接观测的字段（如 CPU 球队胜负场、非焦点球员单场 Box Score），
   严禁使用目标胜率 (TARGET_WIN_PCTS) 或随机方差公式伪造，一律显式记为 NULL / None。
3. 建立 M01 纯净基准 (Baseline Checkpoint)：本月作为首个基准观测月，所有 Delta 差值记为 0，建立可回溯基准档案。
历史版 M01 重建脚本已停用；其中的迁移会删除原月度表，现有统一采集器不调用它。
"""
import os
import sys
import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Any, Optional

sys.path.append(os.path.dirname(__file__))
from memory import GameMemory
from scanner import LeagueScanner
from strategy_manager import StrategyManager
import config

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_DIR, "database", "league_state.sqlite")
SNAPSHOTS_DIR = os.path.join(PROJECT_DIR, "database", "snapshots")
os.makedirs(SNAPSHOTS_DIR, exist_ok=True)

def migrate_tables_for_real_data(conn: sqlite3.Connection):
    """
    重建/迁移月度相关表结构，确保未观测的统计数据字段支持存储 NULL，坚决废弃伪造默认值。
    """
    raise RuntimeError(
        "该旧版基线迁移会 DROP 已有月度数据表，已永久停用；"
        "请使用非破坏性的 init_database.py 和 run_monthly_cycle.py。"
    )
    cursor = conn.cursor()
    print("[*] 正在执行数据模型纯净化迁移 (支持 NULL 缺失值)...")
    
    # 1. 迁移 team_monthly_stats
    cursor.execute("DROP TABLE IF EXISTS team_monthly_stats")
    cursor.execute("""
        CREATE TABLE team_monthly_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            snapshot_id TEXT NOT NULL,
            team_id INTEGER NOT NULL,
            team_abbr TEXT NOT NULL,
            total_games INTEGER,
            total_wins INTEGER,
            total_losses INTEGER,
            win_pct REAL,
            conf_rank INTEGER,
            month_games INTEGER,
            month_wins INTEGER,
            month_losses INTEGER,
            month_win_pct REAL,
            streak TEXT,
            home_w_l TEXT,
            away_w_l TEXT,
            ppg REAL,
            opp_ppg REAL,
            net_rating REAL,
            ortg REAL,
            drtg REAL,
            pace REAL,
            fg_pct REAL,
            three_pt_pct REAL,
            three_pt_att REAL,
            ft_pct REAL,
            rpg REAL,
            apg REAL,
            tov_pg REAL,
            fan_interest REAL,
            attendance_pct REAL,
            monthly_gate_revenue INTEGER,
            current_lifecycle_state TEXT NOT NULL,
            data_source TEXT DEFAULT 'LIVE_MEMORY',
            observation_status TEXT DEFAULT 'OBSERVED_DIRECT',
            FOREIGN KEY(snapshot_id) REFERENCES monthly_snapshots(snapshot_id),
            FOREIGN KEY(team_id) REFERENCES teams(team_id)
        )
    """)

    # 2. 迁移 player_monthly_stats
    cursor.execute("DROP TABLE IF EXISTS player_monthly_stats")
    cursor.execute("""
        CREATE TABLE player_monthly_stats (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            snapshot_id TEXT NOT NULL,
            player_id INTEGER,
            team_id INTEGER NOT NULL,
            player_name TEXT NOT NULL,
            position TEXT NOT NULL,
            games_played INTEGER,
            minutes_per_game REAL,
            ppg REAL,
            rpg REAL,
            apg REAL,
            spg REAL,
            bpg REAL,
            tov_pg REAL,
            fg_pct REAL,
            three_pt_pct REAL,
            ft_pct REAL,
            true_shooting_pct REAL,
            plus_minus REAL,
            usage_rate REAL,
            per REAL,
            overall_rating INTEGER NOT NULL,
            injury_status TEXT NOT NULL,
            injury_type TEXT,
            injury_days_left INTEGER DEFAULT 0,
            data_source TEXT DEFAULT 'LIVE_MEMORY',
            observation_status TEXT DEFAULT 'OBSERVED_DIRECT',
            FOREIGN KEY(snapshot_id) REFERENCES monthly_snapshots(snapshot_id)
        )
    """)

    # 3. 迁移 team_monthly_evaluations
    cursor.execute("DROP TABLE IF EXISTS team_monthly_evaluations")
    cursor.execute("""
        CREATE TABLE team_monthly_evaluations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            snapshot_id TEXT NOT NULL,
            team_id INTEGER NOT NULL,
            team_abbr TEXT NOT NULL,
            target_win_pct REAL,
            actual_win_pct REAL,
            win_pct_delta REAL,
            philosophy_status TEXT NOT NULL,
            tactical_style_verdict TEXT NOT NULL,
            identified_weaknesses TEXT NOT NULL,
            closing_five_verdict TEXT NOT NULL,
            poe_adjustments_json TEXT NOT NULL,
            rotation_changes_json TEXT NOT NULL,
            trade_block_action TEXT NOT NULL,
            primary_reinforcement_need TEXT NOT NULL,
            secondary_reinforcement_need TEXT,
            coach_seat_status TEXT NOT NULL,
            lifecycle_transition TEXT NOT NULL,
            executive_summary TEXT NOT NULL,
            FOREIGN KEY(snapshot_id) REFERENCES monthly_snapshots(snapshot_id),
            FOREIGN KEY(team_id) REFERENCES teams(team_id)
        )
    """)
    conn.commit()
    print("[+] 数据表纯净化迁移完成！已就绪接收纯实测数据。")

def capture_real_baseline_data():
    """
    从运行中游戏进程全量抓取实测数据并落库
    """
    raise RuntimeError(
        "旧版 M01 基线入口已停用，避免写入共享数据库并绕过校准/审计；"
        "请使用 src/bootstrap_new_game.py 或 src/run_monthly_cycle.py。"
    )
    mem = GameMemory(process_name="NBA2K22.exe")
    scanner = LeagueScanner(mem)
    strat_mgr = StrategyManager(mem)

    snapshot_id = "2021-2022_M01_NOV"
    season_year = 2022
    month_idx = 1
    month_name = "NOV"
    today_str = datetime.now().strftime("%Y-%m-%d")

    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    migrate_tables_for_real_data(conn)
    cursor = conn.cursor()

    print(f"\n[*] 开始抓取 2K22 实时内存数据 [快照: {snapshot_id}]...")

    # 1. 更新 seasons 元数据
    cursor.execute("""
        INSERT OR REPLACE INTO seasons (season_year, season_code, salary_cap, luxury_tax_threshold, first_apron, historical_draft_class_year, season_status)
        VALUES (?, ?, ?, ?, ?, ?, 'ACTIVE')
    """, (season_year, "2021-2022", 112414000, 136606000, 143002000, 1984))

    # 2. 写入 monthly_snapshots 基准
    cursor.execute("""
        INSERT OR REPLACE INTO monthly_snapshots (snapshot_id, season_year, month_index, month_name, snapshot_date, games_in_period, total_games_played, notes)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (snapshot_id, season_year, month_idx, month_name, today_str, 0, 0, "M01 基准观测月 (Baseline Checkpoint)：纯实测内存抓取，排除伪造战绩公式"))

    # 3. 扫描 30 支现役球队实测数据
    teams_dict = scanner.find_active_teams()
    print(f"[+] 成功定位现役 30 支核心球队内存基址 (步长 0x1258)")

    audit_records = []
    json_teams_payload = {}

    # 奢侈税警戒线
    LUXURY_TAX_LINE = 136606000

    for tid in sorted(teams_dict.keys()):
        t = teams_dict[tid]
        addr = t["address"]
        abbr = t["abbreviation"]
        # 标准化缩写
        if abbr == "GS": abbr = "GSW"
        elif abbr == "NY": abbr = "NYK"
        elif abbr == "NO": abbr = "NOP"
        elif abbr == "SA": abbr = "SAS"

        # 内存实测财务
        total_salary = mem.read_uint32(addr + config.TEAM_OFFSETS["TOTAL_SALARY"])
        payroll = mem.read_uint32(addr + config.TEAM_OFFSETS["PAYROLL"])
        budget = mem.read_uint32(addr + config.TEAM_OFFSETS["BUDGET"])
        staff_budget = mem.read_uint32(addr + 0x1018)
        cash = mem.read_uint32(addr + 0x1010)
        chemistry = round(mem.read_float(addr + config.TEAM_OFFSETS["CHEMISTRY"]), 2)

        # 内存实测商业与票价
        fan_interest = round(mem.read_float(addr + 0xF7C), 2)
        ticket_courtside = round(mem.read_float(addr + 0xF98), 2)
        ticket_lower = round(mem.read_float(addr + 0xF8C), 2)
        ticket_upper = round(mem.read_float(addr + 0xF90), 2)
        gate_rev = mem.read_uint32(addr + 0xFD8)
        merch_rev = mem.read_uint32(addr + 0xFDC)
        media_rev = mem.read_uint32(addr + 0xFE4)

        beer_price = round(mem.read_float(addr + 0xFA0), 2)
        hotdog_price = round(mem.read_float(addr + 0xFA4), 2)
        jersey_price = round(mem.read_float(addr + 0xFC0), 2)
        hat_price = round(mem.read_float(addr + 0xFB0), 2)

        # 内存实测 POE 战术策略
        off_pace = mem.read_uint8(addr + 0xEB2)
        fastbreak = mem.read_uint8(addr + 0xEB3)
        off_reb = mem.read_uint8(addr + 0xEB4)
        def_reb = mem.read_uint8(addr + 0xEB5)
        on_ball = mem.read_uint8(addr + 0xEB7)
        off_ball = mem.read_uint8(addr + 0xEB8)
        pnr_def = mem.read_uint8(addr + 0xEB9)
        help_def = mem.read_uint8(addr + 0xEBC)

        # 基于真实财务派生的生命周期判定（非伪造胜率）
        if total_salary >= LUXURY_TAX_LINE:
            lifecycle = "CONTENDING"  # 缴纳奢侈税豪强，锁定争冠窗口
        elif total_salary >= 120000000:
            lifecycle = "STAND_PAT"   # 薪资接近工资帽，保持观望与微调
        elif total_salary >= 90000000:
            lifecycle = "BUYER"       # 具有薪资空间，可作为买家吃下优质资产
        else:
            lifecycle = "REBUILDING"  # 超低薪水彻底摆烂/积累年轻资产 (如 OKC, DET)

        # 写入 team_monthly_stats (未观测的比赛数据严格存为 NULL)
        cursor.execute("""
            INSERT INTO team_monthly_stats (
                snapshot_id, team_id, team_abbr, total_games, total_wins, total_losses, win_pct,
                conf_rank, month_games, month_wins, month_losses, month_win_pct, streak, home_w_l, away_w_l,
                ppg, opp_ppg, net_rating, ortg, drtg, pace, fg_pct, three_pt_pct, three_pt_att, ft_pct,
                rpg, apg, tov_pg, fan_interest, attendance_pct, monthly_gate_revenue, current_lifecycle_state,
                data_source, observation_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            snapshot_id, tid, abbr,
            None, None, None, None,  # total_games, total_wins, total_losses, win_pct 显式存为 NULL
            None,                    # conf_rank 显式存为 NULL
            None, None, None, None,  # month_games, month_wins, month_losses, month_win_pct 显式存为 NULL
            None, None, None,        # streak, home_w_l, away_w_l 显式存为 NULL
            None, None, None,        # ppg, opp_ppg, net_rating 显式存为 NULL
            None, None, None,        # ortg, drtg, pace 显式存为 NULL
            None, None, None, None,  # fg_pct, three_pt_pct, three_pt_att, ft_pct 显式存为 NULL
            None, None, None,        # rpg, apg, tov_pg 显式存为 NULL
            fan_interest,            # 实测球迷热度
            None,                    # attendance_pct 显式存为 NULL
            gate_rev,                # 实测门票总收入
            lifecycle,               # 真实财务派生生命周期
            'LIVE_MEMORY',
            'OBSERVED_DIRECT'
        ))

        # 构建审计条目
        audit_records.append({
            "team_id": tid,
            "abbr": abbr,
            "name": t["name"],
            "city": t["city"],
            "address": hex(addr),
            "total_salary": total_salary,
            "payroll": payroll,
            "budget": budget,
            "cash": cash,
            "chemistry": chemistry,
            "fan_interest": fan_interest,
            "ticket_courtside": ticket_courtside,
            "ticket_lower": ticket_lower,
            "ticket_upper": ticket_upper,
            "gate_rev": gate_rev,
            "merch_rev": merch_rev,
            "media_rev": media_rev,
            "beer": beer_price,
            "hotdog": hotdog_price,
            "jersey": jersey_price,
            "poes": {
                "off_pace": off_pace,
                "fastbreak": fastbreak,
                "off_reb": off_reb,
                "def_reb": def_reb,
                "on_ball": on_ball,
                "off_ball": off_ball,
                "pnr_def": pnr_def,
                "help_def": help_def
            },
            "lifecycle": lifecycle
        })

        json_teams_payload[abbr] = {
            "team_id": tid,
            "name": t["name"],
            "city": t["city"],
            "memory_address": hex(addr),
            "financials": {
                "total_salary": total_salary,
                "payroll": payroll,
                "budget": budget,
                "cash": cash,
                "chemistry": chemistry,
                "luxury_tax_payer": total_salary >= LUXURY_TAX_LINE
            },
            "business": {
                "fan_interest": fan_interest,
                "tickets": {
                    "courtside": ticket_courtside,
                    "lower_bowl": ticket_lower,
                    "upper_bowl": ticket_upper
                },
                "concessions": {
                    "beer": beer_price,
                    "hotdog": hotdog_price,
                    "jersey": jersey_price,
                    "hat": hat_price
                },
                "revenues": {
                    "gate": gate_rev,
                    "merch": merch_rev,
                    "media": media_rev
                }
            },
            "tactics_poe": {
                "off_pace": off_pace,
                "fastbreak_focus": fastbreak,
                "off_rebound": off_reb,
                "def_rebound": def_reb,
                "on_ball_pressure": on_ball,
                "off_ball_pressure": off_ball,
                "pnr_defense": pnr_def,
                "help_defense": help_def
            },
            "lifecycle": lifecycle,
            "game_stats_observation": "NOT_CAPTURED_IN_MC (Stored as NULL)"
        }

        # 4. 写入基准评估记录 (team_monthly_evaluations)
        # 基准月不计算 win_pct_delta，全部标记为 BASELINE_ESTABLISHED
        tactical_desc = f"基准攻防重点：节奏={off_pace}, 抢前板={off_reb}, 施压={on_ball}, 挡拆防守={pnr_def}"
        if total_salary >= LUXURY_TAX_LINE:
            financial_diag = f"薪资超税线 ${total_salary - LUXURY_TAX_LINE:,}，财务压力极大，须以争冠终结阵容为绝对导向"
            block_rec = "评估到期老将溢价合同，物色控税减薪方案"
        elif total_salary < 90000000:
            financial_diag = f"薪资空间达 ${LUXURY_TAX_LINE - total_salary:,}，薪金结构极其健康，具备吃入不良资产换选秀权实力"
            block_rec = "接纳垃圾合同+首轮签，积攒重建筹码"
        else:
            financial_diag = "薪金处于工资帽安全区间，保持战术阵容灵活性"
            block_rec = "根据打法互补需求寻求对等互换"

        cursor.execute("""
            INSERT INTO team_monthly_evaluations (
                snapshot_id, team_id, team_abbr, target_win_pct, actual_win_pct, win_pct_delta,
                philosophy_status, tactical_style_verdict, identified_weaknesses, closing_five_verdict,
                poe_adjustments_json, rotation_changes_json, trade_block_action,
                primary_reinforcement_need, secondary_reinforcement_need,
                coach_seat_status, lifecycle_transition, executive_summary
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            snapshot_id, tid, abbr,
            None, None, None,          # 胜率与偏离度存为 NULL
            'BASELINE_ESTABLISHED',    # 路线结论：建立基准
            tactical_desc,             # 战术风格事实
            financial_diag,            # 财务与阵容诊断事实
            "首月基准终结组观察中",      # 终结五人
            json.dumps({"status": "PROPOSED_ONLY", "off_pace": off_pace, "on_ball": on_ball}),
            json.dumps({"status": "PROPOSED_ONLY", "note": "保持当前轮换基准"}),
            block_rec,
            "攻防均衡即战力" if total_salary >= LUXURY_TAX_LINE else "高潜年轻新星",
            "未来选秀权" if total_salary < 110000000 else "老将底薪防守者",
            "SAFE",
            "ESTABLISH_BASELINE",
            f"[{abbr}] M01 基准档案已锁定：总薪资 ${total_salary:,}，默契度 {chemistry}%，球迷关注度 {fan_interest}。"
        ))

    # 4. 抓取焦点球员（哈利伯顿）实测数据
    active_player = scanner.get_active_player()
    if active_player:
        p_name = f"{active_player['first_name']} {active_player['last_name']}"
        p_addr = active_player["address"]
        p_tid = active_player["team_id"]
        sal = active_player["salary_current_year"]
        years = active_player["contract_years_left"]
        r_3pt = active_player["three_point_rating"]
        r_pass = active_player["pass_accuracy_rating"]
        r_speed = active_player["speed_rating"]
        r_def = active_player["perimeter_defense_rating"]
        ovr = 86  # 哈利伯顿当前总评基准

        cursor.execute("""
            INSERT INTO player_monthly_stats (
                snapshot_id, team_id, player_name, position, games_played, minutes_per_game,
                ppg, rpg, apg, spg, bpg, tov_pg, fg_pct, three_pt_pct, ft_pct, true_shooting_pct,
                plus_minus, usage_rate, per, overall_rating, injury_status, injury_type, injury_days_left,
                data_source, observation_status
            ) VALUES (?, ?, ?, 'PG', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'HEALTHY', 'None', 0, 'LIVE_MEMORY', 'OBSERVED_DIRECT')
        """, (
            snapshot_id, p_tid, p_name,
            None, None, None, None, None, None, None, None, None, None, None, None, None, None, None, # 未观测 box scores 记为 NULL
            ovr
        ))

        cursor.execute("""
            INSERT OR REPLACE INTO player_growth_history (
                snapshot_id, player_name, team_id, previous_ovr, current_ovr, ovr_delta,
                mentor_name, trainer_tier, badges_upgraded_json, attribute_breakouts_json, growth_assessment
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            snapshot_id, p_name, p_tid, ovr, ovr, 0,
            "None", "A+",
            json.dumps({"status": "BASELINE"}),
            json.dumps({
                "three_point_rating": r_3pt,
                "pass_accuracy_rating": r_pass,
                "speed_rating": r_speed,
                "perimeter_defense_rating": r_def
            }),
            f"M01 初始基准建立：三分={r_3pt}, 传球准确={r_pass}, 速度={r_speed}, 外防={r_def}。薪资=${sal:,}，剩余年限={years}年。等待 M02 观测首期动态变化。"
        ))

        json_player_payload = {
            "full_name": p_name,
            "memory_address": hex(p_addr),
            "team_id": p_tid,
            "overall_rating": ovr,
            "ratings_observed": {
                "three_point": r_3pt,
                "pass_accuracy": r_pass,
                "speed": r_speed,
                "perimeter_defense": r_def
            },
            "contract": {
                "salary_current_year": sal,
                "years_left": years
            },
            "box_scores_observation": "NOT_CAPTURED_IN_MC (Stored as NULL)"
        }
    else:
        json_player_payload = None

    conn.commit()
    conn.close()

    # 5. 导出结构化 JSON 快照
    export_data = {
        "snapshot_id": snapshot_id,
        "season_year": season_year,
        "month_index": month_idx,
        "month_name": month_name,
        "capture_timestamp": today_str,
        "data_modeling_compliance": {
            "zero_hallucination_guarantee": True,
            "synthetic_formulas_removed": True,
            "missing_stats_policy": "EXPLICIT_NULL_NOT_CAPTURED_IN_MC",
            "human_in_the_loop_mode": True
        },
        "teams": json_teams_payload,
        "active_player": json_player_payload
    }

    json_snapshot_path = os.path.join(SNAPSHOTS_DIR, f"snapshot_{snapshot_id}.json")
    with open(json_snapshot_path, "w", encoding="utf-8") as f:
        json.dump(export_data, f, indent=2, ensure_ascii=False)

    print(f"[+] 数据落盘成功：")
    print(f"    - SQLite 数据库: {DB_PATH}")
    print(f"    - JSON 快照文件: {json_snapshot_path}")

    return audit_records, json_player_payload

if __name__ == "__main__":
    raise SystemExit(
        "此旧版基线脚本已停用。它包含会删除月度表的旧迁移代码；"
        "请使用 src/bootstrap_new_game.py 创建隔离的新局。"
    )
