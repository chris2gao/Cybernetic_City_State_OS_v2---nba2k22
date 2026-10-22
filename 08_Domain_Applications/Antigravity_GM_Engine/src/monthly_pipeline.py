# -*- coding: utf-8 -*-
"""
NBA 2K22 全联盟 30 支球队月度多维决策与执行流水线 (Monthly Multi-Dimensional Decision Pipeline)
每月末（或交易截止日前夕）运行一次，全自动化驱动 30 支球队依次通过六大决策维度：
  维度 1: 胜率与目标偏差研判 ──► 动态生命周期流转 (争冠 / 重建 / 黑马 / 危机)
  维度 2: 主帅绩效与帅位考核 ──► 帅位热度评分与换帅触发 (Hot Seat >= 85 下课)
  维度 3: 赛场攻防策略自适应重构 ──► POEs 针对性修正并热写入内存 (Pace, P&R Def, On-Ball)
  维度 4: 阵容资产审计与货架更新 ──► 刷新 Trade Block 与求购清单
  维度 5: 主场票房与分级票价调控 ──► 动态调价收割红利或保障上座率
  维度 6: 多边交易博弈与撮合执行 ──► 双赢等式撮合并通过内存热写入转会
历史版脚本已停用：此前含静态战绩/交易假设并会直接写入游戏内存。
当前请使用 run_monthly_cycle.py 的校准、采集、审计与数据库建议闭环。
"""
import os
import sys
import json
import sqlite3
from typing import Dict, List, Tuple, Optional
from datetime import datetime

sys.path.append(os.path.dirname(__file__))
from memory import GameMemory
from scanner import LeagueScanner
from strategy_manager import StrategyManager
from trade_engine import DynamicTradeEngine
import config

class MonthlyDecisionPipeline:
    def __init__(self, db_path: Optional[str] = None):
        raise RuntimeError(
            "旧版 MonthlyDecisionPipeline 已停用：它使用硬编码战绩/交易假设并会直接写游戏内存。"
            "请运行 src/run_monthly_cycle.py 获取审计通过的数据和待人工确认的建议。"
        )
        self.project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.db_path = db_path or os.path.join(self.project_dir, "database", "league_state.sqlite")
        self.mem = GameMemory()
        self.scanner = LeagueScanner(self.mem)
        self.strat_mgr = StrategyManager(self.mem)
        self.trade_engine = DynamicTradeEngine(self.db_path)
        self.teams = self.scanner.find_active_teams()

    def run_monthly_pipeline(self, month_title: str = "2022年2月全明星交易截止日") -> Dict:
        """
        全联盟 30 队自动化逐一执行六维决策流水线
        """
        raise RuntimeError(
            "旧版内存写入决策流水线已停用；请使用 run_monthly_cycle.py，"
            "并通过通过审计的数据库快照生成只读建议。"
        )
        print("=" * 65)
        print(f"  NBA 2K22 Antigravity 全联盟月度多维决策流水线: {month_title}")
        print("=" * 65)
        
        decisions_summary = []
        coaching_changes = []
        tactical_updates = []
        trade_blocks_updated = []
        ticket_adjustments = []
        
        # 30 支球队预设赛季胜率基准目标 (Target Win%)
        team_targets = {
            "GSW": 0.65, "PHX": 0.68, "MIL": 0.65, "BOS": 0.62, "MIA": 0.63,
            "MEM": 0.60, "PHI": 0.60, "UTA": 0.58, "DAL": 0.58, "DEN": 0.58,
            "CHI": 0.55, "CLE": 0.52, "TOR": 0.52, "BKN": 0.55, "MIN": 0.52,
            "LAC": 0.52, "ATL": 0.50, "CHA": 0.48, "NY": 0.45, "LAL": 0.55,
            "NOP": 0.45, "WAS": 0.42, "SAC": 0.40, "POR": 0.40, "IND": 0.35,
            "SA": 0.35,  "OKC": 0.28, "DET": 0.25, "HOU": 0.25, "ORL": 0.25
        }

        for tid in sorted(self.teams.keys()):
            t = self.teams[tid]
            abb = t["abbreviation"]
            name = t["name"]
            chem = t["chemistry"]
            addr = t["address"]
            
            # 维度 1: 动态胜率研判与生命周期判定
            target_pct = team_targets.get(abb, 0.50)
            # 示例按现实节点映射或胜率差判定
            if target_pct >= 0.60:
                lifecycle = "CONTENDING"
            elif target_pct <= 0.35:
                lifecycle = "REBUILDING"
            elif abb in ["MEM", "CLE", "MIN", "DAL"]:
                lifecycle = "PLAYOFF_RISING"
            else:
                lifecycle = "TREADMILL_RETOOL"
                
            # 维度 2: 主帅绩效与帅位考核 (Hot Seat)
            # 若化学反应低或战绩滑坡，热度上升
            hot_seat = int((100.0 - chem) * 0.8)
            fired = False
            replacement_coach = None
            if abb == "LAL" and chem <= 60.0:  # 湖人动荡案例
                hot_seat = 88
                fired = True
                replacement_coach = "达文·哈姆 (Darvin Ham)"
                coaching_changes.append(f"湖人主帅沃格尔帅位热度达 {hot_seat} 触发下课，聘请 {replacement_coach} 接掌教鞭！")
            elif abb == "SAC":  # 国王换帅迈克·布朗案例
                hot_seat = 90
                fired = True
                replacement_coach = "迈克·布朗 (Mike Brown)"
                coaching_changes.append(f"国王解雇沃顿，聘请勇士首席助教 {replacement_coach}，注入铁血防守与手递手动态进攻！")

            # 维度 3: 赛场攻防策略针对性自适应调优 (POEs)
            tactical_updates.append(f"{abb}: LEGACY_TEAM_POE_OFFSETS_REVOKED；新版战术须独立提案及玩家批准")

            # 维度 4: 阵容资产审计与货架清单更新 (Trade Block)
            # 写入本地 trade_block 表
            target_needs = []
            surplus = []
            block_players = []
            if lifecycle == "CONTENDING":
                target_needs = ["3&D_WING", "BACKUP_RIM_PROTECTOR"]
                surplus = ["FUTURE_LATE_PICKS", "END_OF_BENCH_YOUTH"]
            elif lifecycle == "REBUILDING":
                target_needs = ["HIGH_POTENTIAL_YOUTH", "FUTURE_FIRST_PICKS"]
                surplus = ["EXPIRING_VETERANS", "MIDRANGE_SCORERS"]
                if abb == "IND":
                    block_players = ["Caris LeVert", "Domantas Sabonis", "Justin Holiday"]
                elif abb == "POR":
                    block_players = ["CJ McCollum", "Norman Powell", "Robert Covington"]
                    
            trade_blocks_updated.append({
                "abb": abb,
                "lifecycle": lifecycle,
                "needs": target_needs,
                "surplus": surplus,
                "block": block_players
            })

            # 维度 5: 主场票房与分级门票调控 (Ticket Pricing)
            biz = self.strat_mgr.get_team_business(tid)
            if biz:
                cur_court = biz["ticket_courtside"]
                cur_lower = biz["ticket_lower"]
                cur_upper = biz["ticket_upper"]
                fan = biz["fan_interest"]
                
                # 豪门高热度适度调价，弱队维持亲民
                if fan >= 0.85 and cur_court < 400.0 and lifecycle == "CONTENDING":
                    new_court = cur_court + 15.0
                    self.strat_mgr.set_ticket_pricing(tid, new_court, cur_lower, cur_upper)
                    ticket_adjustments.append(f"{abb}: 球迷热度高达 {fan:.2f}，场边VIP票上调至 ${new_court:.2f} 收割票房红利")
                elif fan <= 0.45 and cur_upper > 28.0:
                    new_upper = 25.0
                    self.strat_mgr.set_ticket_pricing(tid, cur_court, cur_lower, new_upper)
                    ticket_adjustments.append(f"{abb}: 球迷热度较低({fan:.2f})，上层看台票压低至 ${new_upper:.2f} 保障上座率")

        # 维度 6: 执行月度核心交易撮合 (如步行者与国王哈利伯顿/小萨博尼斯大交易)
        trade_events = []
        # 案例：步行者送出小萨博尼斯，国王送出哈利伯顿 (双赢达成)
        print("\n[*] 正在执行月度多边交易撮合与劳资协议审计...")
        trade_ind_sac = {
            "trade_name": "步行者与国王：哈利伯顿互换小萨博尼斯世纪大交易",
            "team_a": "IND (印第安纳步行者)",
            "team_a_sent": ["Domantas Sabonis (25岁全明星中锋)", "Justin Holiday", "Jeremy Lamb"],
            "team_b": "SAC (萨克拉门托国王)",
            "team_b_sent": ["Tyrese Haliburton (21岁传控之神)", "Buddy Hield", "Tristan Thompson"],
            "cba_verified": "CBA 125% 配平通过",
            "status": "APPROVED_AND_EXECUTED",
            "reasoning": "国王获得小萨打破16年季后赛荒；步行者获得哈利伯顿确立未来十年大核，双赢达成！"
        }
        trade_events.append(trade_ind_sac)

        # 整理输出公报
        print("\n" + "=" * 65)
        print("  【月度全联盟多维决策执行报告】")
        print("=" * 65)
        print(f"[1] 动态换帅动态 ({len(coaching_changes)} 起):")
        for c in coaching_changes:
            print(f"    - {c}")
        print(f"\n[2] 战术攻防策略针对性更新 ({len(tactical_updates)} 队生效):")
        for u in tactical_updates[:6]:
            print(f"    - {u}")
        print(f"    ... 以及其余 {len(tactical_updates)-6} 支球队攻防策略微调")
        print(f"\n[3] 主场门票与票房动态微调 ({len(ticket_adjustments)} 队生效):")
        for t in ticket_adjustments[:4]:
            print(f"    - {t}")
        print(f"\n[4] 月度多边交易撮合与执行 ({len(trade_events)} 笔达成):")
        for tr in trade_events:
            print(f"    - {tr['trade_name']} ({tr['status']})")
            print(f"      {tr['reasoning']}")
        print("=" * 65)
        print("[√] 全联盟 30 支球队月度决策流水线全部执行完毕！内存与数据库同步更新！\n")

        return {
            "month": month_title,
            "coaching_changes": coaching_changes,
            "tactical_updates": tactical_updates,
            "ticket_adjustments": ticket_adjustments,
            "trades": trade_events
        }

if __name__ == "__main__":
    raise SystemExit(
        "此旧版直接写内存流水线已停用。请改用："
        "python src/run_monthly_cycle.py --save-id <id> --season 2022 --month <n> --name <name>"
    )
