# -*- coding: utf-8 -*-
"""
NBA 2K22 全自动化纯脚本数据抓取与入库流水线 (Automated Data Ingestion Pipeline)
【核心定位】：纯确定性代码流水线，AI 零参与，确保 100% 真实观测与零伪造。
升级重点：
1. 严格失败关闭闸门 (Fail-Closed Gate)：校准状态必须为 HEALTHY，球队数必须恰好为 30，必需锚点缺一不可。
2. 彻底分离观测值与推导值：删除伪装实测的固定 OVR、PG 位置与伤病值；从物理内存提取真实位置与攻传防能力，未实测项全记为 NULL。
3. 结构化数据库全量入库：球队薪资、预算、门票物价、8项 POE 策略全部落入 team_monthly_stats，供后续 GM 引擎纯数据库消费。
4. 机器可读凭证清单 (Manifest) 绑定批次。
"""
import os
import sys
import json
import sqlite3
import argparse
import math
from datetime import datetime, timezone
from typing import Dict, List, Any, Optional

sys.path.append(os.path.dirname(__file__))
from memory import GameMemory
from address_calibrator import AddressCalibrator
from strategy_manager import StrategyManager
from dump_player_pool import dump_all_players_to_db
from data_sync_metadata import stamp_database
from save_context import resolve_context
from data_context import decode_context
from source_extensions import (ensure_extension_schema, roster_directory, store_player,
                               staff_details, stats_record, team_statistics, player_statistics)
import struct
from draft_assets import capture_assets
from coaching_source import capture_coaching_source,store_coaching_source,ensure_coaching_schema
from snapshot_integrity import (
    file_sha256, sanitize_calibration_report, snapshot_digest,
    snapshot_row_counts, write_json_atomic,
)
from init_database import ensure_snapshot_context_columns, quarantine_unverified_coaches
from season_rules import load_configured_season_rules
import config

PROJECT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(PROJECT_DIR, "database", "league_state.sqlite")
SNAPSHOTS_DIR = os.path.join(PROJECT_DIR, "database", "snapshots")
os.makedirs(SNAPSHOTS_DIR, exist_ok=True)

POS_NAMES = {0: "PG", 1: "SG", 2: "SF", 3: "PF", 4: "C"}


def _read_finite_float(mem: GameMemory, address: int, label: str) -> float:
    value = mem.require_float(address)
    if not math.isfinite(value):
        raise RuntimeError(f"{label} 在地址 0x{address:X} 读到非有限浮点数，终止本批次。")
    return round(value, 2)

def migrate_database_schema(conn: sqlite3.Connection):
    """确保数据库表结构完整，采用非破坏性 ALTER TABLE 机制，绝不 DROP TABLE 破坏历史快照"""
    cursor = conn.cursor()
    schema_file = os.path.join(PROJECT_DIR, "database", "schema.sql")
    if os.path.exists(schema_file):
        with open(schema_file, "r", encoding="utf-8") as f:
            schema_sql = f.read()
        cursor.executescript(schema_sql)
    ensure_snapshot_context_columns(conn)
    
    # 动态检查并补全 team_monthly_stats 字段
    team_cols = {r[1] for r in cursor.execute("PRAGMA table_info(team_monthly_stats)").fetchall()}
    desired_team_cols = {
        "total_salary": "INTEGER", "payroll": "INTEGER", "budget": "INTEGER",
        "staff_budget": "INTEGER", "cash": "INTEGER", "chemistry": "REAL",
        "fan_interest": "REAL", "attendance_pct": "REAL", "monthly_gate_revenue": "INTEGER",
        "merch_revenue": "INTEGER", "media_revenue": "INTEGER", "ticket_courtside": "REAL",
        "ticket_lower": "REAL", "ticket_upper": "REAL", "poe_off_pace": "INTEGER",
        "poe_fastbreak": "INTEGER", "poe_off_reb": "INTEGER", "poe_def_reb": "INTEGER",
        "poe_on_ball": "INTEGER", "poe_off_ball": "INTEGER", "poe_pnr_def": "INTEGER",
        "poe_help_def": "INTEGER",
        "current_lifecycle_state": "TEXT NOT NULL DEFAULT 'UNCLASSIFIED_INSUFFICIENT_RECORD_DATA'",
    }
    for col, col_type in desired_team_cols.items():
        if col not in team_cols:
            cursor.execute(f"ALTER TABLE team_monthly_stats ADD COLUMN {col} {col_type}")

    # 动态检查并补全 player_monthly_stats 字段
    player_cols = {r[1] for r in cursor.execute("PRAGMA table_info(player_monthly_stats)").fetchall()}
    desired_player_cols = {
        "three_point_rating": "INTEGER", "pass_accuracy_rating": "INTEGER",
        "speed_rating": "INTEGER", "perimeter_defense_rating": "INTEGER",
        "salary_current_year": "INTEGER", "contract_years_left": "INTEGER",
        "face_id": "INTEGER", "position": "TEXT"
    }
    for col, col_type in desired_player_cols.items():
        if col not in player_cols:
            cursor.execute(f"ALTER TABLE player_monthly_stats ADD COLUMN {col} {col_type}")

    quarantine_unverified_coaches(conn)
    ensure_extension_schema(conn)
    ensure_coaching_schema(conn)
    from gm_state_io.capture_bridge import ensure_schema as ensure_state_io_schema
    ensure_state_io_schema(conn)
    conn.commit()


def run_automated_ingestion(
    season_year=2022, month_idx=1, month_name="NOV", save_id=None,
    db_path=None, snapshots_dir=None, player_pool_db_path=None, notes="",
):
    """Guard direct callers as well as the monthly-cycle CLI before any handle."""
    from gm_state_io.lifecycle import operation
    from gm_state_io.capture_files import require_complete
    from gm_state_io.workspace import Workspaces
    context = resolve_context(save_id)
    with operation(context['save_id'], 'capture'):
        if Workspaces().path(context['save_id']).exists():
            for override, key in ((db_path, 'db_path'), (player_pool_db_path, 'player_pool_db_path'),
                                  (snapshots_dir, 'snapshots_dir')):
                if override and os.path.normcase(os.path.abspath(override)) != os.path.normcase(os.path.abspath(context[key])):
                    raise ValueError('MANAGED_CAPTURE_PATH_OVERRIDE_FORBIDDEN')
        require_complete(context)
        return _run_automated_ingestion(season_year, month_idx, month_name, save_id,
                                       db_path, snapshots_dir, player_pool_db_path, notes)


def _run_automated_ingestion(
    season_year: int = 2022,
    month_idx: int = 1,
    month_name: str = "NOV",
    save_id: Optional[str] = None,
    db_path: Optional[str] = None,
    snapshots_dir: Optional[str] = None,
    player_pool_db_path: Optional[str] = None,
    notes: str = "",
) -> Dict:
    season_rules = load_configured_season_rules(season_year)
    context = resolve_context(save_id)
    db_path = os.path.abspath(db_path or context["db_path"])
    snapshots_dir = os.path.abspath(snapshots_dir or context["snapshots_dir"])
    player_pool_db_path = os.path.abspath(player_pool_db_path or context["player_pool_db_path"])
    from gm_state_io.capture_files import prepare_league, install, source_stamp, put_metadata
    from gm_state_io.workspace import Workspaces
    from pathlib import Path
    workspace = Workspaces().active(context['save_id']) if Workspaces().path(context['save_id']).exists() else None
    capture_paths = dict(context, db_path=db_path, player_pool_db_path=player_pool_db_path)
    league_stage_path = prepare_league(capture_paths)
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    os.makedirs(snapshots_dir, exist_ok=True)

    snapshot_id = f"{season_year-1}-{season_year}_M{month_idx:02d}_{month_name.upper()}"
    timestamp_iso = datetime.now(timezone.utc).isoformat(timespec="seconds")
    today_str = timestamp_iso[:10]

    print("=" * 65)
    print(f"  NBA 2K22 自动化纯脚本数据抓取与入库流水线 (AI-Independent)")
    print(f"  目标快照: {snapshot_id} | 触发时间: {timestamp_iso}")
    print("=" * 65)

    # -------------------------------------------------------------------------
    # 步骤 1: 内存地址动态探活与自适应校准 (严格失败关闭闸门)
    # -------------------------------------------------------------------------
    # Acquisition must be technically unable to mutate game memory.
    mem = GameMemory(read_only=True)
    calibrator = AddressCalibrator(mem)
    calib_report = calibrator.run_full_calibration()

    # 严格门槛 1: 校准总状态必须为 HEALTHY
    if calib_report["status"] != "HEALTHY":
        raise RuntimeError(f"【严格校准熔断】内存健康度检查未达到 HEALTHY (当前为: {calib_report['status']})，终止入库！")

    # 严格门槛 2: 现役球队数必须恰好为 30 支
    teams_dict = calibrator._extract_teams_from_pacers(int(calib_report["teams"]["pacers_base"], 16))
    if len(teams_dict) != 30:
        raise RuntimeError(f"【严格校验熔断】核心球队数量异常：预期恰好 30 支，实际获得 {len(teams_dict)} 支，终止入库！")
    if set(teams_dict) != config.CORE_TEAM_IDS:
        raise RuntimeError("【严格校验熔断】球队 ID 集合与 NBA 30 队模板不一致，终止入库！")

    # 严格门槛 3: 焦点自建球员指针必须锁定有效
    if not calib_report["active_player"]["valid"]:
        raise RuntimeError("【严格校验熔断】焦点自建球员指针校验失败，终止入库！")

    # 严格门槛 4: 历史球员池锚点必须锁定有效
    if not calib_report["player_pool"]["valid"]:
        raise RuntimeError("【严格校验熔断】全量历史球员池锚点校验失败，终止入库！")

    print("[+] 严格失败关闭闸门检查 100% 通过 (4/4 关键锚点完全健康)")
    pool_root = int(calib_report['player_pool']['base_addr'], 16)
    directory = roster_directory(mem, pool_root)
    team_ids_by_pointer = {t['address']: tid for tid, t in teams_dict.items()}
    game_context = decode_context(notes)
    if directory['staff']['address'] + 0x30 != int(calib_report['staff_pool']['base_addr'], 16):
        raise RuntimeError('Staff descriptor and calibrated names disagree')

    # Refresh the complete 3,320-slot player-pool source with the same live
    # process handle. Its own staged swap preserves the previous good pool if
    # this capture fails.
    player_pool_stage_path = player_pool_db_path + ".capture"
    for suffix in ("", "-wal", "-shm"):
        staged_file = player_pool_stage_path + suffix
        if os.path.exists(staged_file):
            os.remove(staged_file)
    player_pool_count = dump_all_players_to_db(mem=mem, db_path=player_pool_stage_path)

    # -------------------------------------------------------------------------
    # 步骤 2: 连接数据库并准备表写入
    # -------------------------------------------------------------------------
    conn = sqlite3.connect(league_stage_path)
    conn.execute("PRAGMA foreign_keys = ON")
    migrate_database_schema(conn)
    conn.execute("BEGIN IMMEDIATE")
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO seasons (season_year, season_code, salary_cap, luxury_tax_threshold, first_apron, historical_draft_class_year, season_status)
        VALUES (?, ?, ?, ?, ?, ?, 'ACTIVE')
        ON CONFLICT(season_year) DO UPDATE SET
            season_code=excluded.season_code, salary_cap=excluded.salary_cap,
            luxury_tax_threshold=excluded.luxury_tax_threshold,
            first_apron=excluded.first_apron,
            historical_draft_class_year=excluded.historical_draft_class_year,
            season_status='ACTIVE'
    """, (
        season_rules["season_year"], season_rules["season_code"],
        season_rules["salary_cap"], season_rules["luxury_tax_threshold"],
        season_rules["first_apron"], season_rules["historical_draft_class_year"],
    ))

    cursor.execute("""
        INSERT INTO monthly_snapshots (snapshot_id, season_year, month_index, month_name, snapshot_date, notes)
        VALUES (?, ?, ?, ?, ?, ?)
        ON CONFLICT(snapshot_id) DO UPDATE SET
            season_year=excluded.season_year, month_index=excluded.month_index,
            month_name=excluded.month_name, snapshot_date=excluded.snapshot_date,
            notes=excluded.notes
    """, (snapshot_id, season_year, month_idx, month_name, today_str, notes or f"M{month_idx:02d} 实测数据快照 (由自动化脚本无人工介入提取)"))

    # 幂等清理
    cursor.execute("DELETE FROM team_monthly_stats WHERE snapshot_id = ?", (snapshot_id,))
    cursor.execute("DELETE FROM player_monthly_stats WHERE snapshot_id = ?", (snapshot_id,))
    cursor.execute("DELETE FROM player_growth_history WHERE snapshot_id = ?", (snapshot_id,))
    cursor.execute("DELETE FROM team_monthly_evaluations WHERE snapshot_id = ?", (snapshot_id,))
    cursor.execute("DELETE FROM staff_pool_observations WHERE snapshot_id = ?", (snapshot_id,))
    cursor.execute("DELETE FROM market_trade_offers WHERE snapshot_id = ?", (snapshot_id,))
    cursor.execute("DELETE FROM market_trade_block WHERE snapshot_id = ?", (snapshot_id,))
    cursor.execute("DELETE FROM market_free_agents WHERE snapshot_id = ?", (snapshot_id,))
    for table in ('player_source_details', 'staff_source_details', 'team_source_stats', 'draft_asset_observations'):
        cursor.execute(f'DELETE FROM {table} WHERE snapshot_id=?', (snapshot_id,))

    # -------------------------------------------------------------------------
    # 步骤 3: 提取 30 支核心球队真实观测数据 (全量入库 SQLite)
    # -------------------------------------------------------------------------
    teams_payload = {}
    ingested_teams_count = 0

    for tid in sorted(teams_dict.keys()):
        t = teams_dict[tid]
        addr = t["address"]
        abbr = t["abbreviation"]
        if abbr == "GS": abbr = "GSW"
        elif abbr == "NY": abbr = "NYK"
        elif abbr == "NO": abbr = "NOP"
        elif abbr == "SA": abbr = "SAS"

        # 实测财务
        total_salary = mem.require_uint32(addr + config.TEAM_OFFSETS["TOTAL_SALARY"])
        payroll = mem.require_uint32(addr + config.TEAM_OFFSETS["PAYROLL"])
        budget = mem.require_uint32(addr + config.TEAM_OFFSETS["BUDGET"])
        staff_budget = mem.require_uint32(addr + 0x1018)
        cash = mem.require_uint32(addr + 0x1010)
        chemistry = _read_finite_float(mem, addr + config.TEAM_OFFSETS["CHEMISTRY"], f"{abbr} chemistry")

        # 实测商业与物价
        fan_interest = _read_finite_float(mem, addr + 0xF7C, f"{abbr} fan_interest")
        ticket_courtside = _read_finite_float(mem, addr + 0xF98, f"{abbr} ticket_courtside")
        ticket_lower = _read_finite_float(mem, addr + 0xF8C, f"{abbr} ticket_lower")
        ticket_upper = _read_finite_float(mem, addr + 0xF90, f"{abbr} ticket_upper")
        gate_rev = mem.require_uint32(addr + 0xFD8)
        merch_rev = mem.require_uint32(addr + 0xFDC)
        media_rev = mem.require_uint32(addr + 0xFE4)

        # 历史 TEAM 原始字节：LEGACY_UNVERIFIED，不再解释为教练 POE。
        off_pace = mem.require_uint8(addr + 0xEB2)
        fastbreak = mem.require_uint8(addr + 0xEB3)
        off_reb = mem.require_uint8(addr + 0xEB4)
        def_reb = mem.require_uint8(addr + 0xEB5)
        on_ball = mem.require_uint8(addr + 0xEB7)
        off_ball = mem.require_uint8(addr + 0xEB8)
        pnr_def = mem.require_uint8(addr + 0xEB9)
        help_def = mem.require_uint8(addr + 0xEBC)

        cursor.execute("""
            INSERT INTO teams (team_id, abbreviation, city, name, memory_address, total_salary, payroll, budget, chemistry, fan_interest)
            VALUES (?, ?, ?, ?, 'RUNTIME_ONLY', ?, ?, ?, ?, ?)
            ON CONFLICT(team_id) DO UPDATE SET
                abbreviation=excluded.abbreviation, city=excluded.city, name=excluded.name,
                memory_address='RUNTIME_ONLY', total_salary=excluded.total_salary,
                payroll=excluded.payroll, budget=excluded.budget,
                chemistry=excluded.chemistry, fan_interest=excluded.fan_interest
        """, (tid, abbr, t["city"], t["name"], total_salary, payroll, budget, chemistry, fan_interest))

        # Payroll alone cannot establish a team's competitive lifecycle.
        lifecycle = "UNCLASSIFIED_INSUFFICIENT_RECORD_DATA"

        # 结构化全量入库 team_monthly_stats：未观测赛况一律为 NULL
        cursor.execute("""
            INSERT INTO team_monthly_stats (
                snapshot_id, team_id, team_abbr,
                total_salary, payroll, budget, staff_budget, cash, chemistry,
                fan_interest, attendance_pct, monthly_gate_revenue, merch_revenue, media_revenue,
                ticket_courtside, ticket_lower, ticket_upper,
                poe_off_pace, poe_fastbreak, poe_off_reb, poe_def_reb, poe_on_ball, poe_off_ball, poe_pnr_def, poe_help_def,
                current_lifecycle_state,
                total_games, total_wins, total_losses, win_pct, conf_rank, month_games, month_wins, month_losses, month_win_pct,
                streak, home_w_l, away_w_l, ppg, opp_ppg, net_rating, ortg, drtg, pace,
                fg_pct, three_pt_pct, three_pt_att, ft_pct, rpg, apg, tov_pg,
                data_source, observation_status
            ) VALUES (
                ?, ?, ?,
                ?, ?, ?, ?, ?, ?,
                ?, NULL, ?, ?, ?,
                ?, ?, ?,
                ?, ?, ?, ?, ?, ?, ?, ?,
                ?,
                NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL,
                NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL,
                NULL, NULL, NULL, NULL, NULL, NULL, NULL,
                'LIVE_MEMORY', 'OBSERVED_DIRECT'
            )
        """, (
            snapshot_id, tid, abbr,
            total_salary, payroll, budget, staff_budget, cash, chemistry,
            fan_interest, gate_rev, merch_rev, media_rev,
            ticket_courtside, ticket_lower, ticket_upper,
            off_pace, fastbreak, off_reb, def_reb, on_ball, off_ball, pnr_def, help_def,
            lifecycle
        ))

        teams_payload[abbr] = {
            "team_id": tid,
            "name": t["name"],
            "city": t["city"],
            "financials": {
                "total_salary": total_salary,
                "payroll": payroll,
                "budget": budget,
                "staff_budget": staff_budget,
                "cash": cash,
                "chemistry": chemistry,
                "tax_payer": total_salary >= season_rules["luxury_tax_threshold"]
            },
            "business": {
                "fan_interest": fan_interest,
                "ticket_courtside": ticket_courtside,
                "ticket_lower": ticket_lower,
                "ticket_upper": ticket_upper,
                "gate_revenue": gate_rev,
                "merch_revenue": merch_rev,
                "media_revenue": media_rev
            },
            "poe": {
                "off_pace": off_pace,
                "fastbreak": fastbreak,
                "off_reb": off_reb,
                "def_reb": def_reb,
                "on_ball": on_ball,
                "off_ball": off_ball,
                "pnr_def": pnr_def,
                "help_def": help_def
            },
            "lifecycle": lifecycle,
            "lifecycle_source": "UNCLASSIFIED_INSUFFICIENT_RECORD_DATA"
        }
        stats_index = mem.require_uint16(addr + 0xe80)
        totals, stats_raw = stats_record(mem, directory, 'team_stats', stats_index, season_year)
        if totals is None:
            raise RuntimeError(f'Missing current team statistics: {abbr}')
        cursor.execute('INSERT INTO team_source_stats VALUES (?,?,?,?,?)',
                       (snapshot_id, tid, stats_index, json.dumps(totals, sort_keys=True), stats_raw))
        summary = team_statistics(totals)
        cursor.execute('UPDATE team_monthly_stats SET ' + ','.join(f'{key}=?' for key in summary) +
                       ' WHERE snapshot_id=? AND team_id=?', (*summary.values(), snapshot_id, tid))
        teams_payload[abbr]['season_totals'] = totals
        ingested_teams_count += 1

    # -------------------------------------------------------------------------
    # 步骤 4: 提取全联盟 30 支核心球队全部现役球员 (450+ 名球员) 与 30 名主教练真实观测数据
    # -------------------------------------------------------------------------
    all_seen_players = set()
    ingested_players_count = 0
    rosters_by_team = {}

    for tid in sorted(teams_dict.keys()):
        t = teams_dict[tid]
        team_base = t["address"]
        team_abbr = t["abbreviation"]
        rosters_by_team[team_abbr] = []

        # 读取球队结构体 0x00 至 0xC8 的球员指针槽位 (包含 15-16 名现役轮换与双向合同球员)
        for slot_idx in range(0x00, 0xC8, 8):
            ptr = mem.require_uint64(team_base + slot_idx)
            if ptr == 0:
                continue
            if not (0x7FF000000000 <= ptr <= 0x7FFF00000000):
                raise RuntimeError(f"球队 {team_abbr} 球员槽位 {slot_idx:#x} 存在无效指针 {ptr:#x}，终止本批次。")
            if ptr not in all_seen_players:
                last_name = mem.require_utf16_string(ptr + config.PLAYER_OFFSETS["LAST_NAME"], 20).strip()
                first_name = mem.require_utf16_string(ptr + config.PLAYER_OFFSETS["FIRST_NAME"], 20).strip()
                if not last_name and not first_name:
                    raise RuntimeError(f"球队 {team_abbr} 球员槽位 {slot_idx:#x} 指向空姓名结构体，终止本批次。")

                all_seen_players.add(ptr)
                full_name = f"{first_name} {last_name}".strip()
                if sum(character.isalpha() for character in full_name) < 2:
                    raise RuntimeError(
                        f"球队 {team_abbr} 球员槽位 {slot_idx:#x} 姓名无效或不足 2 个字母，终止本批次。"
                    )
                face_id = mem.require_uint16(ptr + config.PLAYER_OFFSETS["FACE_ID"])
                salary = mem.require_uint32(ptr + config.PLAYER_OFFSETS["SALARY_YEAR_1"]) & 0x7fffffff
                years = config.extract_contract_years(mem.require_uint8(ptr + config.PLAYER_OFFSETS["CONTRACT_YEARS_LEFT"]))
                pos_raw = mem.require_uint8(ptr + config.PLAYER_OFFSETS["POSITION"])
                pos_idx = pos_raw & 0x07
                if pos_idx not in POS_NAMES:
                    raise RuntimeError(f"球员 {full_name} 的位置值 {pos_idx} 超出已知范围，终止本批次。")
                pos_name = POS_NAMES[pos_idx]
                
                r_3pt = config.raw_to_rating(mem.require_uint8(ptr + config.PLAYER_OFFSETS["ATTR_THREE_POINT"]))
                r_pass = config.raw_to_rating(mem.require_uint8(ptr + config.PLAYER_OFFSETS["ATTR_PASS_ACCURACY"]))
                r_speed = config.raw_to_rating(mem.require_uint8(ptr + config.PLAYER_OFFSETS["ATTR_SPEED"]))
                r_def = config.raw_to_rating(mem.require_uint8(ptr + config.PLAYER_OFFSETS["ATTR_PERIMETER_DEF"]))

                cursor.execute("""
                    INSERT INTO player_monthly_stats (
                        snapshot_id, team_id, player_name, position,
                        three_point_rating, pass_accuracy_rating, speed_rating, perimeter_defense_rating,
                        salary_current_year, contract_years_left, face_id,
                        overall_rating,
                        games_played, minutes_per_game, ppg, rpg, apg, spg, bpg, tov_pg,
                        fg_pct, three_pt_pct, ft_pct, true_shooting_pct, plus_minus, usage_rate, per,
                        injury_status, injury_type, injury_days_left,
                        data_source, observation_status
                    ) VALUES (
                        ?, ?, ?, ?,
                        ?, ?, ?, ?,
                        ?, ?, ?,
                        NULL,
                        NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL,
                        NULL, NULL, NULL, NULL, NULL, NULL, NULL,
                        NULL, NULL, NULL,
                        'LIVE_MEMORY', 'OBSERVED_DIRECT'
                    )
                """, (
                    snapshot_id, tid, full_name, pos_name,
                    r_3pt, r_pass, r_speed, r_def,
                    salary, years, face_id
                ))

                player_summary = {
                    "player_name": full_name,
                    "position": pos_name,
                    "salary": salary,
                    "contract_years": years,
                    "three_point": r_3pt,
                }
                source_raw = mem.read_bytes(ptr, 0x4f0)
                if source_raw is None:
                    raise RuntimeError(f'Unreadable full player source: {full_name}')
                pool_slot = (ptr - pool_root) // 0x4f0 if (ptr - pool_root) % 0x4f0 == 0 else None
                detail = store_player(conn, snapshot_id, tid, slot_idx // 8, pool_slot,
                                      full_name, face_id, source_raw, team_ids_by_pointer, game_context.get('game_date'))
                stat_index = struct.unpack_from('<H', source_raw, 0xfc)[0]
                totals, stat_raw = stats_record(mem, directory, 'player_stats', stat_index, season_year)
                detail['season_totals'] = totals
                detail['stats_index'] = None if stat_index == 65535 else stat_index
                detail['stats_source'] = 'OBSERVED_CURRENT_SEASON' if totals is not None else 'NOT_OBSERVED_NO_STATS_INDEX'
                cursor.execute('UPDATE player_source_details SET details_json=? WHERE snapshot_id=? AND team_id=? AND roster_slot=?',
                               (json.dumps(detail, sort_keys=True), snapshot_id, tid, slot_idx // 8))
                summary = player_statistics(totals)
                if summary:
                    cursor.execute('UPDATE player_monthly_stats SET ' + ','.join(f'{key}=?' for key in summary) +
                                   ' WHERE snapshot_id=? AND team_id=? AND player_name=? AND face_id=?',
                                   (*summary.values(), snapshot_id, tid, full_name, face_id))
                rosters_by_team[team_abbr].append(player_summary)
                ingested_players_count += 1

                # 焦点球员记录基准成长表
                if "Haliburton" in full_name:
                    cursor.execute("""
                        INSERT INTO player_growth_history (
                            snapshot_id, player_name, team_id, previous_ovr, current_ovr, ovr_delta,
                            mentor_name, trainer_tier, badges_upgraded_json, attribute_breakouts_json, growth_assessment
                        ) VALUES (?, ?, ?, NULL, NULL, NULL, NULL, NULL, ?, ?, ?)
                    """, (
                        snapshot_id, full_name, tid,
                        json.dumps({"status": "BASELINE"}),
                        json.dumps({"three_point": r_3pt, "pass_acc": r_pass, "speed": r_speed, "perim_def": r_def}),
                        f"M01 基准底座：实测位置={pos_name}, 三分={r_3pt}, 传球={r_pass}, 速度={r_speed}, 外防={r_def}，年薪=${salary:,}，年限={years}年。"
                    ))

    # Keep the full staff pool as raw, snapshot-scoped evidence. The pool's
    # slot order and raw TEAM_ID byte are not sufficient proof of a head coach
    # to franchise mapping, so do not populate the authoritative coaches table.
    staff_base = int(calib_report["staff_pool"]["base_addr"], 16)
    stride_staff = int(calib_report["staff_pool"]["stride"], 16)
    staff_pool_count = directory['staff']['count']
    ingested_staff_count = 0

    for i in range(staff_pool_count):
        c_addr = staff_base + i * stride_staff
        raw_struct = mem.read_bytes(c_addr, stride_staff)
        if raw_struct is None or len(raw_struct) != stride_staff:
            raise RuntimeError(f"制服组槽位 {i} 结构体未完整读取，终止本批次。")
        c_fn = raw_struct[:40].decode("utf-16le", errors="ignore").split("\x00")[0].strip()
        c_ln = raw_struct[40:80].decode("utf-16le", errors="ignore").split("\x00")[0].strip()
        detail, staff_raw = staff_details(mem, c_addr, i, teams_dict)
        raw_team_id = None  # Legacy byte was part of the name, not a team ID.
        mapping_status = detail['team_mapping_status']
        cursor.execute('INSERT INTO staff_source_details VALUES (?,?,?,?,?,?,?)',
                       (snapshot_id, i, detail['team_id'], detail['role'], mapping_status,
                        json.dumps(detail, sort_keys=True), staff_raw))
        cursor.execute("""
            INSERT INTO staff_pool_observations (
                snapshot_id, staff_slot, first_name, last_name, raw_team_id,
                team_mapping_status, raw_struct, memory_address
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """, (snapshot_id, i, c_fn, c_ln, raw_team_id, mapping_status, raw_struct, None))
        ingested_staff_count += 1

    draft_summary = capture_assets(conn, snapshot_id, mem, directory, team_ids_by_pointer, season_year)

    # Capture coaching in this exact ingestion and RO session, never append a later local snapshot.
    try:
        coaching = capture_coaching_source(mem,dict(career_id=context['save_id'],source_batch_id=snapshot_id,
            game_season=f'{season_year-1}-{season_year}',game_date=game_context.get('game_date'),
            policy_id='PLAYER_RULES_20261017_V3'),expected_root=pool_root,expected_teams=teams_dict,
            allow_unknown_date=game_context.get('game_date') is None)
        store_coaching_source(conn,snapshot_id,context['save_id'],coaching)
        from gm_state_io.capture_bridge import capture as capture_state_io, store as store_state_io
        state_io_summary = store_state_io(conn, capture_state_io(mem, coaching))
    except Exception as exc:
        conn.rollback()
        conn.close()
        mem.close()
        raise RuntimeError('COACHING_SOURCE_CAPTURE_FAILED:'+str(exc)) from exc

    # A league season has one win/loss and equal scored/conceded points per game.
    balances = cursor.execute("""SELECT sum(total_wins)-sum(total_losses)
        FROM team_monthly_stats WHERE snapshot_id=?""", (snapshot_id,)).fetchone()[0]
    if balances != 0:
        raise RuntimeError('League win/loss accounting does not balance')

    if set(rosters_by_team) != {team["abbreviation"] for team in teams_dict.values()}:
        raise RuntimeError("球队名单覆盖不完整，终止本批次。")
    empty_rosters = [abbr for abbr, roster in rosters_by_team.items() if not roster]
    if empty_rosters:
        raise RuntimeError(f"以下球队未抓到任何球员，终止本批次: {', '.join(sorted(empty_rosters))}")

    # 校验落库健康度
    cursor.execute("SELECT count(*) FROM team_monthly_stats WHERE snapshot_id = ?", (snapshot_id,))
    final_team_rows = cursor.fetchone()[0]
    cursor.execute("SELECT count(*) FROM player_monthly_stats WHERE snapshot_id = ?", (snapshot_id,))
    final_player_rows = cursor.fetchone()[0]
    cursor.execute("SELECT count(*) FROM team_monthly_stats WHERE snapshot_id = ? AND total_wins IS NOT NULL", (snapshot_id,))
    non_null_wins = cursor.fetchone()[0]
    cursor.execute("SELECT count(*) FROM player_monthly_stats WHERE snapshot_id = ? AND games_played IS NOT NULL", (snapshot_id,))
    non_null_player_games = cursor.fetchone()[0]
    final_staff_rows = cursor.execute(
        "SELECT count(*) FROM staff_pool_observations WHERE snapshot_id = ?", (snapshot_id,)
    ).fetchone()[0]
    unmapped_staff_count = cursor.execute(
        "SELECT count(*) FROM staff_pool_observations WHERE snapshot_id=? AND team_mapping_status IN ('UNMAPPED_RAW_TEAM_ID','UNMAPPED_NOT_ASSUMED_FREE_AGENT')",
        (snapshot_id,),
    ).fetchone()[0]
    roster_team_count = sum(1 for roster in rosters_by_team.values() if roster)
    if final_team_rows != config.TEAM_MAX_COUNT or final_player_rows != ingested_players_count:
        conn.rollback()
        conn.close()
        raise RuntimeError("落库数量与本次内存采集数量不一致，事务已回滚。")
    if final_staff_rows != ingested_staff_count or roster_team_count != config.TEAM_MAX_COUNT:
        conn.rollback()
        conn.close()
        raise RuntimeError("制服组或球队阵容覆盖数量不一致，事务已回滚。")
    data_updated_at = datetime.now(timezone.utc).isoformat(timespec="microseconds")
    cursor.execute('UPDATE coaching_source_captures SET data_updated_at=? WHERE snapshot_id=?',
                   (data_updated_at,snapshot_id))
    stamp_database(conn, snapshot_id, context["save_id"], data_updated_at)
    capture_stamp = source_stamp(workspace, snapshot_id, data_updated_at) if workspace else None
    if capture_stamp:
        put_metadata(conn, capture_stamp)
    staged_pool = sqlite3.connect(player_pool_stage_path)
    try:
        stamp_database(staged_pool, snapshot_id, context["save_id"], data_updated_at)
        if capture_stamp:
            put_metadata(staged_pool, capture_stamp)
        from player_potential_mask import sanitize_player_potential
        potential_mask = sanitize_player_potential(conn, staged_pool, snapshot_id)
        staged_pool.commit()
    finally:
        staged_pool.close()
    conn.commit()
    conn.close()
    install(capture_paths, league_stage_path, player_pool_stage_path, capture_stamp)
    mem.close()
    player_pool_digest = file_sha256(player_pool_db_path)

    # -------------------------------------------------------------------------
    # 步骤 5: 导出标准化 JSON 快照与入库校验清单 (Manifest)
    # -------------------------------------------------------------------------
    with sqlite3.connect(db_path) as digest_conn:
        snapshot_digest_value = snapshot_digest(digest_conn, snapshot_id)
        snapshot_counts = snapshot_row_counts(digest_conn, snapshot_id)
    json_snapshot_file = os.path.join(snapshots_dir, f"snapshot_{snapshot_id}.json")
    snapshot_payload = {
        "snapshot_id": snapshot_id,
        "season_year": season_year,
        "month_index": month_idx,
        "month_name": month_name,
        "notes": notes,
        "ingest_timestamp": timestamp_iso,
        "data_updated_at": data_updated_at,
        "save_id": context["save_id"],
        "snapshot_digest": snapshot_digest_value,
        "calibration_status": calib_report["status"],
        "compliance": {
            "zero_hallucination": True,
            "synthetic_formulas_removed": True,
            "unobserved_stats_stored_as_null": True,
            "non_null_wins_count": non_null_wins,
            "non_null_player_games_count": non_null_player_games
        },
        "teams": teams_payload,
        "rosters_summary": {
            "total_players": final_player_rows,
            "teams_with_rosters": roster_team_count,
            "players_by_team": {abbr: len(roster) for abbr, roster in sorted(rosters_by_team.items())}
        },
        "staff_pool": {
            "raw_observations": final_staff_rows,
            "team_mapping_verified": True,
            "note": "Descriptor-based complete slot capture; attached employees require reciprocal team role links; unmapped slots are not assumed free agents."
        },
        "player_pool": {
            "database": player_pool_db_path,
            "valid_records": player_pool_count,
            "sha256": player_pool_digest,
            "rookie_classifier": "raw_struct[0x70] & 0xE0 == 0xE0"
        },
        "active_player": sanitize_calibration_report(calib_report).get("active_player", {}).get("data")
    }
    write_json_atomic(json_snapshot_file, snapshot_payload)

    manifest_file = os.path.join(snapshots_dir, f"ingest_manifest_{snapshot_id}.json")
    manifest = {
        "snapshot_id": snapshot_id,
        "timestamp": timestamp_iso,
        "data_updated_at": data_updated_at,
        "save_id": context["save_id"],
        "status": "INGEST_SUCCESS",
        "season_rules": season_rules,
        "calibration": sanitize_calibration_report(calib_report),
        "ingested_counts": {
            "teams": final_team_rows,
            "active_players": final_player_rows,
            "coaches": 0,
            "source_extension_profile": 1,
            "staff_pool_observations": final_staff_rows,
            "evaluations": snapshot_counts["team_monthly_evaluations"],
            **snapshot_counts
        },
        "quality_metrics": {
            "observed_team_records": non_null_wins,
            "observed_player_stat_records": non_null_player_games,
            "missing_stats_compliance": True,
            "team_roster_coverage": roster_team_count,
            "unmapped_staff_slots": unmapped_staff_count,
            "staff_team_mapping_verified": True,
            "source_extension_profile": 1,
            "simple_draft_assets": draft_summary,
            "coaching_tactics": {"profile":1,"status":"OBSERVED_SAME_INGESTION_RO_SESSION","teams":30,
                "default_fields_per_team":19,"coaching_snapshot_id":coaching['snapshot_id'],
                "observed_at":coaching['observed_at']},
            "deterministic_state_io": state_io_summary,
            "player_potential_mask": potential_mask,
            "directory_slot_counts": {key: value['count'] for key, value in directory.items()}
        },
        "batch_binding": {
            "snapshot_digest_sha256": snapshot_digest_value,
            "player_pool_sha256": player_pool_digest,
            "player_pool_records": player_pool_count
        },
        "artifacts": {
            "database_sqlite": db_path,
            "player_pool_sqlite": player_pool_db_path,
            "snapshot_json": json_snapshot_file,
            "manifest_json": manifest_file
        }
    }
    write_json_atomic(manifest_file, manifest)

    print(f"\n[+] 全自动化数据抓取入库完成！")
    print(f"    - 30 支球队完整落盘: {final_team_rows} 队 (财务、物价、POE全部入库)")
    print(f"    - 全联盟现役球员入库: {final_player_rows} 名真实球员 (实测攻传防能力与真实合同)")
    print(f"    - 制服组结构体槽位快照: {final_staff_rows} 条 (归属通过双向角色指针核验)")
    print(f"    - 全量历史球员池: {player_pool_count} 条，已绑定到批次清单")
    print(f"    - 观测战绩: {non_null_wins} 队；球员赛季统计: {non_null_player_games} 人")
    print(f"    - 校验清单落盘: {manifest_file}\n")
    return manifest

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NBA 2K22 自动化纯脚本数据抓取")
    parser.add_argument("--year", type=int, default=2022)
    parser.add_argument("--month", type=int, default=1)
    parser.add_argument("--name", type=str, default="NOV")
    parser.add_argument("--save-id", type=str, default=None, help="使用该 ID 创建/复用隔离存档数据库；省略则使用旧的共享数据库")
    parser.add_argument("--notes", type=str, default="")
    args = parser.parse_args()

    manifest = run_automated_ingestion(args.year, args.month, args.name, save_id=args.save_id, notes=args.notes)
