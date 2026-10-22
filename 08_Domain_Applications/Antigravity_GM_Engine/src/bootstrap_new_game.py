# -*- coding: utf-8 -*-
"""Initialize or resume an isolated save and capture its M00 baseline.

Game settings and 30-team ticket values are only written when the player
explicitly supplies --approve-game-writes. Data capture remains read-only.
Legacy TEAM POE templates are revoked and never applied, including with approval.
"""
import os
import sys
import math
import sqlite3
import argparse

sys.path.append(os.path.dirname(__file__))
from memory import GameMemory
from scanner import LeagueScanner
from strategy_manager import StrategyManager
from slider_manager import GlobalSettingsManager
from init_database import init_or_migrate
from address_calibrator import AddressCalibrator
from save_context import create_or_open_save
from season_rules import load_configured_season_rules
import config

# 历史模板：仅最后三项票价仍使用；前六项旧战术数值已撤销，严禁应用或映射。
TEAM_BOOTSTRAP_CONFIGS = {
    # 缩写: (六个已撤销历史值..., COURTSIDE, LOWER, UPPER)
    "PHI": (4, 3, 3, 5, 5, 1, 210.0, 87.6, 39.9),
    "MIL": (4, 4, 2, 5, 5, 1, 173.0, 93.6, 43.0),
    "WAS": (3, 3, 2, 4, 3, 1, 140.0, 65.0, 28.0),
    "CHI": (3, 3, 2, 4, 3, 1, 190.0, 85.0, 38.0),
    "CLE": (3, 3, 4, 5, 4, 3, 145.0, 68.0, 29.0),
    "BOS": (4, 3, 2, 5, 5, 6, 260.0, 105.0, 48.0),
    "LAC": (3, 3, 2, 4, 4, 6, 230.0, 95.0, 42.0),
    "MEM": (5, 5, 5, 4, 5, 1, 135.0, 62.0, 27.0),
    "ATL": (5, 4, 2, 4, 3, 1, 150.0, 72.0, 32.0),
    "MIA": (3, 3, 2, 5, 5, 1, 240.0, 98.0, 45.0),
    "CHA": (5, 5, 3, 3, 3, 1, 130.0, 58.0, 25.0),
    "UTA": (3, 3, 2, 5, 3, 1, 145.0, 66.0, 30.0),
    "SAC": (5, 5, 2, 4, 3, 1, 140.0, 64.0, 28.0),
    "NYK": (3, 2, 5, 5, 4, 1, 350.0, 120.0, 55.0),
    "LAL": (4, 4, 2, 4, 3, 1, 500.0, 150.0, 65.0),
    "ORL": (4, 4, 3, 4, 3, 1, 110.0, 50.0, 22.0),
    "DAL": (3, 3, 2, 4, 3, 1, 220.0, 92.0, 40.0),
    "BKN": (4, 3, 2, 4, 3, 6, 420.0, 135.0, 58.0),
    "DEN": (4, 3, 3, 5, 3, 1, 180.0, 80.0, 36.0),
    "IND": (5, 5, 2, 4, 4, 1, 135.0, 60.0, 26.0),
    "NOP": (4, 3, 4, 5, 3, 1, 125.0, 55.0, 24.0),
    "DET": (4, 4, 3, 4, 3, 1, 115.0, 52.0, 23.0),
    "TOR": (4, 4, 4, 4, 5, 6, 185.0, 82.0, 37.0),
    "HOU": (5, 5, 3, 3, 2, 1, 120.0, 54.0, 24.0),
    "SAS": (4, 3, 2, 4, 4, 1, 145.0, 65.0, 28.0),
    "PHX": (4, 3, 2, 5, 4, 1, 210.0, 88.0, 39.0),
    "OKC": (4, 4, 3, 4, 4, 6, 115.0, 50.0, 22.0),
    "MIN": (5, 5, 4, 4, 3, 1, 140.0, 62.0, 27.0),
    "POR": (4, 3, 2, 4, 2, 1, 160.0, 75.0, 33.0),
    "GSW": (5, 5, 2, 4, 5, 6, 480.0, 145.0, 62.0),
}

def _normalize_abbr(abbr: str) -> str:
    return {"GS": "GSW", "NY": "NYK", "NO": "NOP", "SA": "SAS"}.get(abbr, abbr)


def apply_approved_ticket_templates(teams, manager):
    """Preserve pricing; deliberately ignore the six revoked tactical values."""
    for team_id, team in teams.items():
        courtside, lower, upper = TEAM_BOOTSTRAP_CONFIGS[_normalize_abbr(team["abbreviation"])][-3:]
        if not manager.set_ticket_pricing(team_id, courtside=courtside, lower=lower, upper=upper):
            raise RuntimeError("Approved ticket template failed")
    return len(teams)


def bootstrap_new_game(
    season_year: int = 2022,
    save_id: str = "main",
    approve_game_writes: bool = False,
):
    season_rules = load_configured_season_rules(season_year)
    context = create_or_open_save(save_id)
    print("=" * 70)
    print(f"  NBA 2K22 Antigravity 新局初始化 | 存档: {context['save_id']}")
    print("=" * 70)

    # 1. 数据库升级与结构校验
    print("\n[阶段 1/6] 正在校验并准备标准化数据库...")
    init_or_migrate(context["db_path"])

    # 2. 挂接内存引擎
    print("\n[阶段 2/6] 正在挂接 NBA2K22.exe 进程...")
    mem = GameMemory(read_only=not approve_game_writes)
    print(f"[+] 挂接成功！PID: {mem.pid}, 基址: 0x{mem.base_address:X}")

    calibrator = AddressCalibrator(mem)
    calibration = calibrator.run_full_calibration()
    if calibration["status"] != "HEALTHY":
        raise RuntimeError("球队、活跃球员、球员池或制服组锚点校准未全部通过；没有对游戏内存写入初始化设置。")
    teams = calibrator._extract_teams_from_pacers(int(calibration["teams"]["pacers_base"], 16))
    if set(teams) != config.CORE_TEAM_IDS:
        raise RuntimeError("球队阵列 ID 与模板不一致；没有对游戏内存写入初始化设置。")
    missing_configs = sorted(
        _normalize_abbr(team["abbreviation"])
        for team in teams.values()
        if _normalize_abbr(team["abbreviation"]) not in TEAM_BOOTSTRAP_CONFIGS
    )
    if missing_configs:
        raise RuntimeError(f"球队配置模板未覆盖当前阵列: {', '.join(missing_configs)}")

    scanner = LeagueScanner(mem)
    strat = StrategyManager(mem)
    sliders = GlobalSettingsManager(mem)
    if set(strat.teams) != config.CORE_TEAM_IDS:
        raise RuntimeError("StrategyManager 读取到的球队集合与校准结果不一致；停止初始化。")

    # 3. 检查队列并写入经校准的静态队伍身份/赛季规则
    print("\n[阶段 3/6] 正在绑定 30 支核心球队与赛季模板...")
    scanner_teams = scanner.find_active_teams()
    if set(scanner_teams) != config.CORE_TEAM_IDS:
        raise RuntimeError("LeagueScanner 队伍 ID 与已校准阵列不一致；停止新局初始化。")
    injected_count = 0

    with sqlite3.connect(context["db_path"]) as conn:
        conn.execute("PRAGMA foreign_keys = ON")
        cursor = conn.cursor()
        for tid, tinfo in teams.items():
            addr = tinfo["address"]
            abbr = _normalize_abbr(tinfo["abbreviation"])
            total_salary = mem.require_uint32(addr + config.TEAM_OFFSETS["TOTAL_SALARY"])
            payroll = mem.require_uint32(addr + config.TEAM_OFFSETS["PAYROLL"])
            budget = mem.require_uint32(addr + config.TEAM_OFFSETS["BUDGET"])
            chemistry = mem.require_float(addr + config.TEAM_OFFSETS["CHEMISTRY"])
            fan_interest = mem.require_float(addr + config.TEAM_OFFSETS["FAN_INTEREST"])
            if not math.isfinite(chemistry) or not math.isfinite(fan_interest):
                raise RuntimeError(f"{abbr} chemistry/fan_interest 不是有限值，未写入模板数据库。")
            chemistry = round(chemistry, 2)
            fan_interest = round(fan_interest, 2)
            cursor.execute("""
                INSERT INTO teams (team_id, abbreviation, city, name, memory_address,
                                   total_salary, payroll, budget, chemistry, fan_interest)
                VALUES (?, ?, ?, ?, 'RUNTIME_ONLY', ?, ?, ?, ?, ?)
                ON CONFLICT(team_id) DO UPDATE SET
                    abbreviation=excluded.abbreviation, city=excluded.city, name=excluded.name,
                    memory_address='RUNTIME_ONLY', total_salary=excluded.total_salary,
                    payroll=excluded.payroll, budget=excluded.budget,
                    chemistry=excluded.chemistry, fan_interest=excluded.fan_interest
            """, (tid, abbr, tinfo["city"], tinfo["name"], total_salary, payroll, budget, chemistry, fan_interest))

        cursor.execute("""
            INSERT INTO seasons (season_year, season_code, salary_cap, luxury_tax_threshold,
                                 first_apron, historical_draft_class_year, season_status)
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

    # 4. Game-memory writes require an explicit player approval flag.
    if approve_game_writes:
        print("\n[阶段 4/6] 正在应用已获批准的全局规则与门票模板...")
        print("[BLOCKED] LEGACY_TEAM_POE_OFFSETS_REVOKED；旧战术模板跳过，教练策略须另行提案批准。")
        if not sliders.lock_realistic_sliders(quarter_min=12, is_hof=True):
            raise RuntimeError("全局比赛设置写入或回读校验失败；停止初始化。")
        print("[+] 全局比赛设置已写入并回读核验。")

        injected_count = apply_approved_ticket_templates(teams, strat)

        if injected_count != config.TEAM_MAX_COUNT:
            raise RuntimeError(f"仅为 {injected_count}/30 支球队应用了门票模板，初始化失败。")
        print(f"[+] 门票设置已写入并回读核验 ({injected_count}/30)；教练战术未设置。")
    else:
        print("\n[阶段 4/6] 未提供 --approve-game-writes；跳过所有游戏内存写入。")

    # 5. 校验当前焦点/活跃球员 (支持任意自建或现役球星)
    print("\n[阶段 5/6] 动态检测当前存档中的活跃焦点球员...")
    act = scanner.get_active_player()
    if act:
        print(f"[+] 成功捕获活跃球员: {act['first_name']} {act['last_name']}")
        print(f"    - 所属球队 ID: {act['team_id']}")
        print(f"    - 三分能力: {act['three_point_rating']} | 传球准确度: {act['pass_accuracy_rating']}")
        print(f"    - 保护原则：玩家所操控的焦点球员享有绝对主体性，豁免一切自动化强制交易！")
    else:
        print("[!] 提示：未检测到当前焦点球员指针，进入球员名单或比赛后系统将自动吸附。")

    mem.close()

    baseline_id = f"{season_year-1}-{season_year}_M00_BASELINE"
    with sqlite3.connect(context["db_path"]) as conn:
        baseline_exists = conn.execute(
            "SELECT 1 FROM monthly_snapshots WHERE snapshot_id=?", (baseline_id,)
        ).fetchone() is not None
    baseline_ready = baseline_exists and all(
        os.path.isfile(os.path.join(context["snapshots_dir"], f"{prefix}_{baseline_id}.json"))
        for prefix in ("ingest_manifest", "ai_sampling_audit")
    )
    if baseline_ready:
        try:
            from gm_engine import GMEngine
            GMEngine(
                context["db_path"], context["snapshots_dir"], context["player_pool_db_path"]
            ).verify_snapshot_gate(baseline_id)
        except Exception:
            baseline_ready = False
    if not baseline_ready:
        print("\n[阶段 6/6] 正在首次抓取初始化后的全量数据并运行基线审计……")
        from run_monthly_cycle import run_cycle
        run_cycle(
            season_year=season_year,
            month_idx=0,
            month_name="BASELINE",
            notes="新局初始化基线：无比赛数据时保持赛况字段为 NULL",
            save_id=context["save_id"],
        )

    print("\n" + "=" * 70)
    if approve_game_writes:
        print("  [SUCCESS] 新局数据初始化、基线采集与已批准的游戏设置写入完成。")
    else:
        print("  [SUCCESS] 新局数据库与基线采集完成；游戏设置保持未修改。")
    print(f"  存档数据库: {context['db_path']}")
    print(f"  后续月度流程请继续使用 --save-id {context['save_id']}")
    print("=" * 70)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="从干净模板创建或复用一个隔离的新局数据库")
    parser.add_argument("--save-id", default="main", help="此游戏存档的唯一 ID；不同游戏必须使用不同 ID")
    parser.add_argument("--season", type=int, default=2022)
    parser.add_argument(
        "--approve-game-writes",
        action="store_true",
        help="显式批准本次初始全局设置和门票模板；不包含已撤销的 POE 模板",
    )
    args = parser.parse_args()
    bootstrap_new_game(
        season_year=args.season,
        save_id=args.save_id,
        approve_game_writes=args.approve_game_writes,
    )
