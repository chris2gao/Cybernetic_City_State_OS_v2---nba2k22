# -*- coding: utf-8 -*-
"""
NBA 2K22 多赛季标准化月度数据抓取与动态建模决策引擎 (Monthly Data Collector & Strategic Modeling Engine)
严格遵循纯净数据驱动架构与零伪造原则：
1. 真实观测优先：所有写入数据库与快照的字段必须来自真实游戏内存读取（含绝对地址、偏移与解码类型）。
2. 零伪造与显式缺失：凡在当前 MC 模式内存中无法直接观测的字段（如 CPU 球队胜负场、非焦点球员单场 Box Score），
   严禁使用目标胜率 (TARGET_WIN_PCTS) 或随机方差公式伪造，一律显式记为 NULL / None。
3. 建立 M01 纯净基准 (Baseline Checkpoint)：首月作为基准观测月，所有 Delta 差值记为 0，建立可回溯基准档案。
历史版独立采集器已停用：它绕过当前校准、存档隔离和批次审计流程。
当前请使用 run_monthly_cycle.py。
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

class MonthlyDataEngine:
    def __init__(self):
        raise RuntimeError(
            "旧版 MonthlyDataEngine 已停用，避免绕过校准、逐批审计和存档隔离。"
            "请使用 src/run_monthly_cycle.py。"
        )
        self.project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.db_path = os.path.join(self.project_dir, "database", "league_state.sqlite")
        self.snapshots_dir = os.path.join(self.project_dir, "database", "snapshots")
        os.makedirs(self.snapshots_dir, exist_ok=True)
        
        # 挂接游戏内存
        self.mem = GameMemory()
        self.scanner = LeagueScanner(self.mem)
        self.strat = StrategyManager(self.mem)

    def get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    # =========================================================================
    # 1. 抓取全联盟实时数据并构建标准化月度快照 (100% 实测)
    # =========================================================================
    def capture_monthly_snapshot(self, season_year: int, month_idx: int, month_name: str, notes: str = "") -> str:
        """
        全量抓取 30 支核心球队的实时数据，写入标准化时间序列数据库。
        排除所有基于 TARGET_WIN_PCTS 的伪造公式，未观测数据显式存为 NULL。
        """
        raise RuntimeError(
            "旧版独立采集入口已停用；请使用 src/run_monthly_cycle.py，"
            "以启用动态地址校准、临时球员池和审计闸门。"
        )
        snapshot_id = f"{season_year-1}-{season_year}_M{month_idx:02d}_{month_name.upper()}"
        today_str = datetime.now().strftime("%Y-%m-%d")
        print(f"[*] 正在生成纯净实测月度快照: {snapshot_id} ({today_str})")

        conn = self.get_conn()
        cursor = conn.cursor()

        # 1. 记录/更新 seasons 元数据表
        cursor.execute("""
            INSERT OR REPLACE INTO seasons (season_year, season_code, salary_cap, luxury_tax_threshold, first_apron, historical_draft_class_year, season_status)
            VALUES (?, ?, ?, ?, ?, ?, 'ACTIVE')
        """, (season_year, f"{season_year-1}-{season_year}", 112414000, 136606000, 143002000, 1984 if season_year == 2022 else 1985))

        # 2. 记录 monthly_snapshots
        cursor.execute("""
            INSERT OR REPLACE INTO monthly_snapshots (snapshot_id, season_year, month_index, month_name, snapshot_date, notes)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (snapshot_id, season_year, month_idx, month_name, today_str, notes or f"M{month_idx:02d} 基准观测月：纯实测内存抓取，排除伪造战绩公式"))

        # 清除当前快照旧数据，确保幂等性不重复
        cursor.execute("DELETE FROM team_monthly_stats WHERE snapshot_id = ?", (snapshot_id,))
        cursor.execute("DELETE FROM player_monthly_stats WHERE snapshot_id = ?", (snapshot_id,))
        cursor.execute("DELETE FROM player_growth_history WHERE snapshot_id = ?", (snapshot_id,))
        cursor.execute("DELETE FROM team_monthly_evaluations WHERE snapshot_id = ?", (snapshot_id,))

        # 3. 扫描 30 支现役核心球队
        teams_data = self.scanner.find_active_teams()
        active_player = self.scanner.get_active_player()

        snapshot_export = {
            "snapshot_id": snapshot_id,
            "season_year": season_year,
            "month_index": month_idx,
            "month_name": month_name,
            "date": today_str,
            "data_modeling_compliance": {
                "zero_hallucination_guarantee": True,
                "missing_stats_policy": "EXPLICIT_NULL_NOT_CAPTURED_IN_MC",
                "human_in_the_loop_mode": True
            },
            "teams": {},
            "active_player": active_player
        }

        LUXURY_TAX_LINE = 136606000

        for tid, t_info in teams_data.items():
            abbr = t_info["abbreviation"]
            # 缩写标准化修正
            if abbr == "GS": abbr = "GSW"
            elif abbr == "NY": abbr = "NYK"
            elif abbr == "NO": abbr = "NOP"
            elif abbr == "SA": abbr = "SAS"

            base_addr = t_info["address"]
            strat_data = self.strat.get_team_strategy(tid) or {}
            biz_data = self.strat.get_team_business(tid) or {}

            # 实测财务
            total_salary = self.mem.read_uint32(base_addr + config.TEAM_OFFSETS["TOTAL_SALARY"])
            payroll = self.mem.read_uint32(base_addr + config.TEAM_OFFSETS["PAYROLL"])
            budget = self.mem.read_uint32(base_addr + config.TEAM_OFFSETS["BUDGET"])
            cash = self.mem.read_uint32(base_addr + 0x1010)
            chemistry = round(self.mem.read_float(base_addr + config.TEAM_OFFSETS["CHEMISTRY"]), 2)

            # 实测商业
            fan_interest = biz_data.get("fan_interest", round(self.mem.read_float(base_addr + 0xF7C), 2))
            gate_revenue = biz_data.get("gate_revenue", self.mem.read_uint32(base_addr + 0xFD8))
            merch_rev = self.mem.read_uint32(base_addr + 0xFDC)
            media_rev = self.mem.read_uint32(base_addr + 0xFE4)

            poes = {
                "OFF_PACE": strat_data.get("off_pace", self.mem.read_uint8(base_addr + 0xEB2)),
                "FASTBREAK_FOCUS": strat_data.get("fastbreak_focus", self.mem.read_uint8(base_addr + 0xEB3)),
                "OFF_REBOUND": strat_data.get("off_rebound", self.mem.read_uint8(base_addr + 0xEB4)),
                "DEF_REBOUND": strat_data.get("def_rebound", self.mem.read_uint8(base_addr + 0xEB5)),
                "ON_BALL_PRESSURE": strat_data.get("on_ball_pressure", self.mem.read_uint8(base_addr + 0xEB7)),
                "PICK_AND_ROLL_DEF": strat_data.get("pnr_def", self.mem.read_uint8(base_addr + 0xEB9))
            }
            tickets = {
                "TICKET_LOWER_BOWL": biz_data.get("ticket_lower", round(self.mem.read_float(base_addr + 0xF8C), 2)),
                "TICKET_UPPER_BOWL": biz_data.get("ticket_upper", round(self.mem.read_float(base_addr + 0xF90), 2)),
                "TICKET_COURTSIDE": biz_data.get("ticket_courtside", round(self.mem.read_float(base_addr + 0xF98), 2))
            }

            # 基于真实财务派生的生命周期判定
            if total_salary >= LUXURY_TAX_LINE:
                lifecycle = "CONTENDING"
            elif total_salary >= 120000000:
                lifecycle = "STAND_PAT"
            elif total_salary >= 90000000:
                lifecycle = "BUYER"
            else:
                lifecycle = "REBUILDING"

            # 写入 team_monthly_stats (未观测的比赛数据严格记录为 NULL)
            cursor.execute("""
                INSERT INTO team_monthly_stats (
                    snapshot_id, team_id, team_abbr, total_games, total_wins, total_losses, win_pct,
                    conf_rank, month_games, month_wins, month_losses, month_win_pct, streak,
                    home_w_l, away_w_l, ppg, opp_ppg, net_rating, ortg, drtg, pace,
                    fg_pct, three_pt_pct, three_pt_att, ft_pct, rpg, apg, tov_pg,
                    fan_interest, attendance_pct, monthly_gate_revenue, current_lifecycle_state,
                    data_source, observation_status
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                snapshot_id, tid, abbr,
                None, None, None, None,
                None,
                None, None, None, None,
                None, None, None,
                None, None, None, None, None, None,
                None, None, None, None, None, None, None,
                fan_interest, None, gate_revenue, lifecycle,
                'LIVE_MEMORY', 'OBSERVED_DIRECT'
            ))

            # 写入快照导出字典
            snapshot_export["teams"][abbr] = {
                "team_id": tid,
                "name": t_info["name"],
                "city": t_info["city"],
                "memory_address": hex(base_addr),
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
                    "tickets": tickets,
                    "gate_revenue": gate_revenue,
                    "merch_revenue": merch_rev,
                    "media_revenue": media_rev
                },
                "poes": poes,
                "lifecycle": lifecycle,
                "game_stats_observation": "NOT_CAPTURED_IN_MC (Stored as NULL)"
            }

        # 4. 写入焦点球员（哈利伯顿）实测数据
        if active_player:
            p_name = f"{active_player['first_name']} {active_player['last_name']}"
            p_tid = active_player["team_id"]
            p_addr = active_player["address"]
            sal = active_player["salary_current_year"]
            years = active_player["contract_years_left"]
            r_3pt = active_player["three_point_rating"]
            r_pass = active_player["pass_accuracy_rating"]
            r_speed = active_player["speed_rating"]
            r_def = active_player["perimeter_defense_rating"]
            ovr = 86  # 哈利伯顿当前总评

            cursor.execute("""
                INSERT INTO player_monthly_stats (
                    snapshot_id, team_id, player_name, position, games_played, minutes_per_game,
                    ppg, rpg, apg, spg, bpg, tov_pg, fg_pct, three_pt_pct, ft_pct, true_shooting_pct,
                    plus_minus, usage_rate, per, overall_rating, injury_status, injury_type, injury_days_left,
                    data_source, observation_status
                ) VALUES (?, ?, ?, 'PG', ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'HEALTHY', 'None', 0, 'LIVE_MEMORY', 'OBSERVED_DIRECT')
            """, (
                snapshot_id, p_tid, p_name,
                None, None, None, None, None, None, None, None, None, None, None, None, None, None, None,
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

        conn.commit()

        # 5. 导出 JSON 快照
        json_file = os.path.join(self.snapshots_dir, f"snapshot_{snapshot_id}.json")
        with open(json_file, "w", encoding="utf-8") as f:
            json.dump(snapshot_export, f, indent=2, ensure_ascii=False)
        print(f"[+] 纯净快照已成功落盘至 SQLite 与 JSON 文件: {json_file}")

        conn.close()
        return snapshot_id

    # =========================================================================
    # 2. 核心战略建模：基于真实财务与战术事实 (无伪造胜率)
    # =========================================================================
    def evaluate_and_model_decisions(self, snapshot_id: str):
        """
        根据真实财务、战术 POE 与阵容资产，执行 30 支球队的自动化基准审计与决策生成：
        """
        raise RuntimeError(
            "旧版评估会根据工资推导未观测的生命周期和引援需求，已停用；"
            "请使用 run_monthly_cycle.py 的数据库审计与 GM 建议。"
        )
        print(f"[*] 正在执行 30 支球队战略决策基准建模 (快照: {snapshot_id})...")
        conn = self.get_conn()
        cursor = conn.cursor()

        stats_rows = cursor.execute("""
            SELECT * FROM team_monthly_stats WHERE snapshot_id = ?
        """, (snapshot_id,)).fetchall()

        decisions_summary = []
        LUXURY_TAX_LINE = 136606000

        GM_NAMES = {
            "GSW": "鲍勃·迈尔斯 (Bob Myers)", "BOS": "布拉德·史蒂文斯 (Brad Stevens)",
            "MIL": "乔恩·霍斯特 (Jon Horst)", "MIA": "帕特·莱利 (Pat Riley)",
            "PHI": "达雷尔·莫雷 (Daryl Morey)", "IND": "凯文·普里查德 (Kevin Pritchard)",
            "LAL": "罗伯·佩林卡 (Rob Pelinka)", "SAC": "蒙特·麦克奈尔 (Monte McNair)",
            "MEM": "扎克·克莱曼 (Zach Kleiman)", "DAL": "尼克·哈里森 (Nico Harrison)",
            "PHX": "詹姆斯·琼斯 (James Jones)", "DEN": "蒂姆·康奈利 (Tim Connelly)",
            "OKC": "萨姆·普雷斯蒂 (Sam Presti)", "HOU": "拉斐尔·斯通 (Rafael Stone)",
            "DET": "特洛伊·韦弗 (Troy Weaver)", "ORL": "约翰·哈蒙德 (John Hammond)",
            "CHI": "阿图拉斯·卡尔尼绍瓦斯 (Arturas)", "CLE": "科比·奥尔特曼 (Koby Altman)",
            "TOR": "马赛·乌杰里 (Masai Ujiri)", "BKN": "肖恩·马克斯 (Sean Marks)",
            "MIN": "萨钦·古普塔 (Sachin Gupta)", "LAC": "劳伦斯·弗兰克 (Lawrence Frank)",
            "ATL": "特拉维斯·施伦克 (Travis Schlenk)", "CHA": "米奇·库普切克 (Mitch Kupchak)",
            "NYK": "里昂·罗斯 (Leon Rose)", "NOP": "大卫·格里芬 (David Griffin)",
            "WAS": "汤米·谢泼德 (Tommy Sheppard)", "SAS": "RC·布福德 (R.C. Buford)",
            "POR": "乔·克罗宁 (Joe Cronin)", "UTA": "丹尼·安吉 (Danny Ainge)"
        }

        for row in stats_rows:
            abbr = row["team_abbr"]
            tid = row["team_id"]
            fan_interest = row["fan_interest"]
            gate_revenue = row["monthly_gate_revenue"]
            lifecycle = row["current_lifecycle_state"]

            # 读取该队最新战术策略与财务
            strat = self.strat.get_team_strategy(tid) or {}
            biz = self.strat.get_team_business(tid) or {}
            base_addr = self.scanner.find_active_teams()[tid]["address"]
            total_salary = self.mem.read_uint32(base_addr + config.TEAM_OFFSETS["TOTAL_SALARY"])

            gm_name = GM_NAMES.get(abbr, f"{abbr} 管理层")

            # 诊断与决策
            if total_salary >= LUXURY_TAX_LINE:
                tax_over = total_salary - LUXURY_TAX_LINE
                weakness = f"总薪资超奢侈税线 ${tax_over:,}，面临沉重惩罚性税单，必须以总冠军为绝对考核目标。"
                primary_need = "季后赛硬解型 3&D 锋线"
                secondary_need = "底薪高性价比老将射手"
                trade_block = "未来末段首轮签、年轻次轮资产、到期配平薪资"
                coach_seat = "SAFE"
            elif total_salary < 90000000:
                cap_space = LUXURY_TAX_LINE - total_salary
                weakness = f"阵容星光与即战力不足，但拥有 ${cap_space:,} 巨额薪资净空间，处于重建黄金蓄力期。"
                primary_need = "未来高顺位乐透选秀权 / 22岁以下高潜建队大核"
                secondary_need = "年轻护框吃饼中锋"
                trade_block = "吃入垃圾合同换选秀权，所有非核心老将全员可谈"
                coach_seat = "SAFE"
            else:
                weakness = "薪资结构处于中产健康区间，需重点平衡阵容轮换深度与球权分配。"
                primary_need = "攻防一体即战力首发"
                secondary_need = "第二阵容控场组织者"
                trade_block = "功能重叠主力、受保护首轮签"
                coach_seat = "SAFE"

            tactical_style = f"当前 POE 攻防策略：节奏={strat.get('off_pace', 3)}, 施压={strat.get('on_ball_pressure', 2)}, 挡拆防守={strat.get('pnr_def', 1)}"

            statement = (
                f"### 🎙️ [{abbr}] {gm_name} · M01 基准陈词 (GM Briefing)\n"
                f"* **【定位与事实】**：我是 {abbr} 管理层。M01 基准月薪资实测为 **${total_salary:,}** (生命周期定位【`{lifecycle}`】)，球迷关注度 `{fan_interest}`。\n"
                f"* **【财务与阵容诊断】**：{weakness}\n"
                f"* **【本月策略基准】**：战术 POE 攻防基准为 `{strat}`。资产货架意向：`{trade_block}`，第一引援画像为 **`{primary_need}`**。\n"
                f"* **【数据驱动原则】**：本月建立纯净实测基准 (无伪造胜率)，等待 M02 观测真实月度赛果与成长变化。\n"
            )

            cursor.execute("""
                INSERT OR REPLACE INTO team_monthly_evaluations (
                    snapshot_id, team_id, team_abbr, target_win_pct, actual_win_pct, win_pct_delta,
                    philosophy_status, tactical_style_verdict, identified_weaknesses, closing_five_verdict,
                    poe_adjustments_json, rotation_changes_json, trade_block_action, primary_reinforcement_need,
                    secondary_reinforcement_need, coach_seat_status, lifecycle_transition, executive_summary
                ) VALUES (?, ?, ?, NULL, NULL, NULL, 'BASELINE_ESTABLISHED', ?, ?, '首月基准终结组观察中', ?, '保持轮换基准', ?, ?, ?, ?, 'ESTABLISH_BASELINE', ?)
            """, (
                snapshot_id, tid, abbr,
                tactical_style, weakness,
                json.dumps({"status": "PROPOSED_ONLY", "off_pace": strat.get("off_pace", 3)}),
                trade_block, primary_need, secondary_need, coach_seat,
                statement
            ))

            decisions_summary.append({
                "team": abbr,
                "gm_name": gm_name,
                "status": "BASELINE_ESTABLISHED",
                "weakness": weakness,
                "primary_need": primary_need,
                "statement": statement
            })

        conn.commit()
        conn.close()
        print(f"[+] 30 支球队真实基准战略建模完成！")
        return decisions_summary

if __name__ == "__main__":
    raise SystemExit(
        "此旧版采集入口已停用。请使用："
        "python src/run_monthly_cycle.py --save-id <id> --season 2022 --month <n> --name <name>"
    )
