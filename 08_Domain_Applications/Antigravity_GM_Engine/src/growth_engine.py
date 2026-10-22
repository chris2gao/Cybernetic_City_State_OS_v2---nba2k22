# -*- coding: utf-8 -*-
"""
NBA 2K22 Antigravity 球员动态战术成长与制服组签约引擎 (Player Growth & Staff Engine)
1. 制服组签约与薪资预算模型 (主教练、助理教练、首席训练师/神医、球探主管)
2. 球员“战术环境熏陶”动态成长模型 (如乔丹打跑轰空间体系进化出三分球与追身远投)
3. 比赛表现走势激励 (Hot/Cold Slump)
4. 生成内存写回指令并记录成长审计日志
"""
import os
import sys
import json
import sqlite3
from typing import Dict, List, Tuple, Optional
from datetime import datetime

# 体系熏陶影响字典：不同体系对各属性与战术倾向的月度滋养加成
TACTICAL_IMPRINTING_RULES = {
    "PACE_&_SPACE": {
        "description": "现代跑轰与极致空间体系",
        "boost_attributes": {
            "ATTR_THREE_POINT": 2,          # 三分属性 +2
            "ATTR_PASS_ACCURACY": 1,        # 传球准度 +1
            "ATTR_SPEED_WITH_BALL": 1       # 持球推进速度 +1
        },
        "boost_tendencies": {
            "TEND_PASS_OPEN": 5             # 突分空位分球倾向 +5
        },
        "growth_narrative": "在高频挡拆与五外拉开的现代跑轰体系浸泡下，外线射程大幅外扩，持球推反击节奏全面提速！"
    },
    "SEVEN_SECONDS": {
        "description": "七秒极限快攻风暴",
        "boost_attributes": {
            "ATTR_SPEED": 2,
            "ATTR_DRIVING_LAYUP": 2,
            "ATTR_PASS_VISION": 2
        },
        "boost_tendencies": {
            "TEND_PASS_OPEN": 8
        },
        "growth_narrative": "极限转换快攻驱动下，奔跑速度与快攻视野被完全激发，终结效率暴涨！"
    },
    "DEFENSE": {
        "description": "全场施压强硬防守体系",
        "boost_attributes": {
            "ATTR_PERIMETER_DEF": 2,
            "ATTR_INTERIOR_DEF": 2,
            "ATTR_LATERAL_QUICK": 1,
            "ATTR_STEAL": 2
        },
        "boost_tendencies": {
            "TEND_ON_BALL_STEAL": 5,
            "TEND_CONTEST_SHOT": 6
        },
        "growth_narrative": "在铁血防守教鞭的严酷打磨下，横移防守脚步、扑防压迫感与下手抢断习惯显著进化！"
    },
    "TRIANGLE": {
        "description": "经典三角进攻单打与轴心体系",
        "boost_attributes": {
            "ATTR_MID_RANGE": 2,
            "ATTR_PASS_IQ": 2,
            "ATTR_SHOT_CLOSE": 1
        },
        "boost_tendencies": {
            "TEND_SHOT": 4
        },
        "growth_narrative": "侧翼中距离单挑脚步臻于化境，高位阅读防守与策应球商大幅飞跃！"
    }
}

class GrowthEngine:
    def __init__(self, db_path: str):
        raise PermissionError(
            "Legacy automatic growth and fictional staff market are disabled by "
            "the current player policy. Natural development belongs to the game; "
            "historical-gravity edits need a separately implemented, specifically approved executor."
        )
        self.db_path = db_path
        self._ensure_tables()

    def _ensure_tables(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS player_growth_logs (
            log_id INTEGER PRIMARY KEY AUTOINCREMENT,
            player_name TEXT NOT NULL,
            team_abb TEXT NOT NULL,
            tactical_system TEXT NOT NULL,
            attribute_changed TEXT NOT NULL,
            old_value INTEGER NOT NULL,
            new_value INTEGER NOT NULL,
            growth_reason TEXT NOT NULL,
            logged_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        """)
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS staff_contracts (
            staff_id INTEGER PRIMARY KEY AUTOINCREMENT,
            team_id INTEGER NOT NULL,
            team_abb TEXT NOT NULL,
            role TEXT NOT NULL,
            name TEXT NOT NULL,
            annual_salary INTEGER NOT NULL,
            years_left INTEGER NOT NULL,
            offense_grade INTEGER,
            defense_grade INTEGER,
            specialty TEXT NOT NULL
        )
        """)
        conn.commit()
        conn.close()

    def simulate_monthly_player_growth(self, active_players: List[Dict], team_systems: Dict[str, str]) -> List[Dict]:
        """
        计算球员受所在球队战术体系熏陶的月度属性进化与异变
        """
        raise PermissionError("Automatic player attribute growth is disabled; see docs/26.")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        growth_events = []

        for p in active_players:
            p_name = p.get("name", "")
            team_abb = p.get("team_abb", "IND")
            system = team_systems.get(team_abb, "PACE_&_SPACE")
            
            rule = TACTICAL_IMPRINTING_RULES.get(system)
            if not rule:
                continue

            # 核心案例 1: 乔丹在跑轰体系下进化出三分
            if "Jordan" in p_name and system in ["PACE_&_SPACE", "SEVEN_SECONDS"]:
                old_3pt = p.get("three_point", 78)
                new_3pt = min(99, old_3pt + 4)
                narrative = f"迈克尔·乔丹在现代空间跑轰体系熏陶下，三分投射从复古中距离异变为致命远程冷箭！三分能力值由 {old_3pt} 暴涨至 {new_3pt}！"
                growth_events.append({
                    "player_name": p_name,
                    "team_abb": team_abb,
                    "system": system,
                    "attribute": "ATTR_THREE_POINT",
                    "old_val": old_3pt,
                    "new_val": new_3pt,
                    "narrative": narrative
                })
                cursor.execute("""
                INSERT INTO player_growth_logs (player_name, team_abb, tactical_system, attribute_changed, old_value, new_value, growth_reason)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (p_name, team_abb, system, "ATTR_THREE_POINT", old_3pt, new_3pt, narrative))

            # 核心案例 2: 哈利伯顿在卡莱尔体系下传控与三分再登巅峰
            elif "Haliburton" in p_name and system == "PACE_&_SPACE":
                old_3pt = p.get("three_point", 97)
                new_3pt = min(99, old_3pt + 1)
                old_pass = p.get("pass_accuracy", 94)
                new_pass = min(99, old_pass + 2)
                narrative = f"泰雷斯·哈利伯顿作为全联盟唯一主控大脑，跑轰节奏如臂使指，传球准确度由 {old_pass} 进化至 {new_pass}，三分稳定性升至 {new_3pt}！"
                growth_events.append({
                    "player_name": p_name,
                    "team_abb": team_abb,
                    "system": system,
                    "attribute": "ATTR_PASS_ACCURACY",
                    "old_val": old_pass,
                    "new_val": new_pass,
                    "narrative": narrative
                })
                cursor.execute("""
                INSERT INTO player_growth_logs (player_name, team_abb, tactical_system, attribute_changed, old_value, new_value, growth_reason)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (p_name, team_abb, system, "ATTR_PASS_ACCURACY", old_pass, new_pass, narrative))

            # 常规球员通用加成
            else:
                for attr, delta in rule["boost_attributes"].items():
                    old_v = p.get("three_point", 75) if attr == "ATTR_THREE_POINT" else 75
                    new_v = min(99, old_v + delta)
                    narrative = rule["growth_narrative"]
                    growth_events.append({
                        "player_name": p_name,
                        "team_abb": team_abb,
                        "system": system,
                        "attribute": attr,
                        "old_val": old_v,
                        "new_val": new_v,
                        "narrative": narrative
                    })
                    cursor.execute("""
                    INSERT INTO player_growth_logs (player_name, team_abb, tactical_system, attribute_changed, old_value, new_value, growth_reason)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                    """, (p_name, team_abb, system, attr, old_v, new_v, narrative))
                    break # 每次取主属性

        conn.commit()
        conn.close()
        return growth_events

    def evaluate_staff_market(self, teams_financials: List[Dict]) -> List[Dict]:
        """
        根据各队财务实力与赚钱能力，模拟制服组与教练签约升级
        """
        staff_transactions = []
        for t in teams_financials:
            abb = t.get("abbreviation", "")
            budget = t.get("budget", 10_000_000)
            
            # 豪门大球市：高薪聘请 S 级神医与助理教练
            if budget >= 15_000_000:
                staff_transactions.append({
                    "team_abb": abb,
                    "role": "首席训练师 (Head Trainer)",
                    "name": "亚历克斯·麦克肯尼 (S级冠军队医)",
                    "salary": 3_500_000,
                    "effect": "伤病发生概率降低 35%，背靠背赛后体力恢复速度提升 40%！为当家超巨保驾护航！"
                })
            # 青年军球队：聘请顶级球员发展助教
            elif abb in ["IND", "OKC", "SAS"]:
                staff_transactions.append({
                    "team_abb": abb,
                    "role": "进攻战术助教 (Offensive Coordinator)",
                    "name": "奇普·英格兰德 (全联盟投篮教父)",
                    "salary": 2_800_000,
                    "effect": "全队年轻球员底角三分与罚球训练效率提升 25%，直接加速外线投射蜕变！"
                })
        return staff_transactions

if __name__ == "__main__":
    db_file = os.path.join(os.path.dirname(__file__), "..", "database", "league_state.sqlite")
    engine = GrowthEngine(db_file)
    print("============================================================")
    print("  NBA 2K22 球员动态战术成长与制服组签约引擎")
    print("============================================================")
    sample_players = [
        {"name": "Tyrese Haliburton", "team_abb": "IND", "three_point": 97, "pass_accuracy": 94},
        {"name": "Michael Jordan", "team_abb": "IND", "three_point": 78, "pass_accuracy": 82}
    ]
    systems = {"IND": "PACE_&_SPACE"}
    growths = engine.simulate_monthly_player_growth(sample_players, systems)
    for g in growths:
        print(f"[+] 动态成长: {g['player_name']} -> {g['attribute']}: {g['old_val']} -> {g['new_val']}")
        print(f"    论述: {g['narrative']}")
    
    staff = engine.evaluate_staff_market([{"abbreviation": "IND", "budget": 12_000_000}, {"abbreviation": "LAL", "budget": 18_000_000}])
    print(f"\n[+] 制服组签约建议: {len(staff)} 笔")
    for s in staff:
        print(f"    - {s['team_abb']} 签约 {s['role']}: {s['name']} (年薪: ${s['salary']:,}) -> {s['effect']}")
