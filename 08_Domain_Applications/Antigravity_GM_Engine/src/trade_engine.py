# -*- coding: utf-8 -*-
"""
NBA 2K22 资产池与动态交易价值评估引擎 (Asset Pools & Dynamic Trade Engine)
实现：
1. 五维资产池管理：自有球员(Roster)、自由球员(FA)、货架筹码(Trade Block)、新秀池(Draft Prospects)、选秀权资产库(Draft Picks)
2. 制服组资产池管理：主帅、助教、A+训练师、S级队医、CFO
3. 动态交易价值评估模型 (0~10,000 点)：
   - 即战力分 (OVR + 战术地位 + 年龄曲线)
   - 潜力溢价分 (Age <= 23 放大)
   - 合同红利/毒药惩罚分 (童工合同 vs 到期合同 vs 溢价死钱)
   - 选秀权分级估值表 (无保护乐透首轮 vs 季后赛末段首轮 vs 保护条款 vs 互换权)
4. 两大老板谈判与博弈撮合 (Win-Win Equilibrium):
   - 基于争冠(Contending) vs 重建(Rebuilding)的主观乘数不对称性撮合
   - 五大交易否决红线 (Deal Breakers): 非卖品触发、CBA配平超标、垃圾合同无补偿、位置拥堵、宿敌税
"""
import os
import sys
import json
import sqlite3
from typing import Dict, List, Tuple, Optional

sys.path.append(os.path.dirname(__file__))

# ==============================================================================
# 1. 选秀权资产基准估值字典 (Draft Pick Valuation Matrix)
# ==============================================================================
PICK_TIER_VALUES = {
    "UNPROTECTED_HIGH_LOTTERY": 7500,     # 无保护乐透前四潜在签 (堪比年轻全明星)
    "UNPROTECTED_MID_LOTTERY": 5000,      # 无保护前14顺位签
    "TOP_4_PROTECTED_FIRST": 3800,        # 前4顺位保护首轮签
    "LOTTERY_PROTECTED_FIRST": 3000,      # 乐透保护首轮签
    "CONTENDER_LATE_FIRST": 2000,         # 争冠豪强末段首轮签 (25~30顺位)
    "FIRST_ROUND_SWAP_RIGHT": 1500,       # 首轮签互换权
    "EARLY_SECOND_ROUND": 800,            # 次轮前段签 (31~40)
    "LATE_SECOND_ROUND": 400              # 次轮末段签
}

# ==============================================================================
# 2. 球队生命周期对不同资产的主观价值乘数 (Lifecycle Multipliers)
# ==============================================================================
LIFECYCLE_MULTIPLIERS = {
    "CONTENDING": {                       # 争冠冲刺期 (湖人、勇士、雄鹿、凯尔特人)
        "ability_mult": 1.40,             # 极度渴望当打之年即战力
        "potential_mult": 0.80,           # 无法等待年轻人生涩练级
        "pick_mult": 0.65,                # 愿意大肆贱卖/透支未来首轮
        "expiring_contract_mult": 0.60    # 不愿单纯为了省钱吃死钱
    },
    "REBUILDING": {                       # 彻底重建期 (雷霆、马刺、魔术、火箭、活塞)
        "ability_mult": 0.40,             # 28岁以上老将大幅贬值
        "potential_mult": 1.85,           # 极度饥渴 22岁以下高潜新星
        "pick_mult": 1.60,                # 将无保护首轮签视同无价黄金
        "expiring_contract_mult": 1.50    # 极度乐意吃进垃圾合同换取选秀补偿
    },
    "PLAYOFF_RISING": {                   # 季后赛黑马/上升期 (灰熊、骑士、森林狼、独行侠)
        "ability_mult": 1.15,             # 寻求阵容针对性补强拼图
        "potential_mult": 1.25,           # 兼顾核心延续性
        "pick_mult": 1.00,                # 正常中立估值
        "expiring_contract_mult": 0.90
    },
    "TREADMILL_RETOOL": {                 # 平庸泥潭/纠结期 (公牛、奇才、开拓者、步行者初期)
        "ability_mult": 0.90,
        "potential_mult": 1.20,
        "pick_mult": 1.30,
        "expiring_contract_mult": 1.20
    }
}

class DynamicTradeEngine:
    def __init__(self, db_path: Optional[str] = None):
        raise RuntimeError("Legacy trade generator is disabled for production GM; use gm_core published-data analysis. No database was opened.")
        self.project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.db_path = db_path or os.path.join(self.project_dir, "database", "league_state.sqlite")
        self._init_extended_tables()

    def _init_extended_tables(self):
        """初始化资产池扩展表"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # 1. 选秀权资产库表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS draft_picks (
            pick_id INTEGER PRIMARY KEY AUTOINCREMENT,
            original_team TEXT NOT NULL,
            current_owner TEXT NOT NULL,
            year INTEGER NOT NULL,
            round INTEGER NOT NULL,
            protection_type TEXT NOT NULL,
            projected_tier TEXT NOT NULL
        )""")
        
        # 2. 货架筹码与需求表
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS trade_block (
            team_abb TEXT PRIMARY KEY,
            lifecycle_status TEXT NOT NULL,
            target_needs TEXT NOT NULL,       -- JSON: 迫切需求位置 (如 ["3&D_WING", "BACKUP_CENTER"])
            surplus_positions TEXT NOT NULL,  -- JSON: 冗余待清理位置
            trade_block_players TEXT NOT NULL -- JSON: 摆上货架的球员名单
        )""")
        
        # 3. 制服组自由与在职资产池
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS staff_pool (
            staff_id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            role TEXT NOT NULL,               -- HEAD_COACH, ASSISTANT_COACH, TRAINER, PHYSICIAN, CFO
            rating TEXT NOT NULL,             -- S, A+, A, B, C
            current_team TEXT,                -- 所属球队缩写 (若为自由身则为 NULL)
            salary INTEGER NOT NULL,
            system_preference TEXT
        )""")
        
        conn.commit()
        conn.close()

    def calculate_player_base_value(self, player: Dict) -> int:
        """
        计算单个球员的客观综合价值点数 (0 ~ 10,000 点)
        """
        required = ("ovr", "age", "potential", "salary", "years_left")
        if any(player.get(key) is None for key in required):
            raise ValueError("UNKNOWN: observed OVR, age, potential, salary and years_left are required; no default values")
        ovr, age, pot, salary, years_left = (player[key] for key in required)
        
        # 1. 即战力基础分 (按 OVR 指数级拉升)
        if ovr >= 95:
            ability_val = 8000 + (ovr - 95) * 450      # 95~99: 8000 ~ 9800
        elif ovr >= 90:
            ability_val = 6000 + (ovr - 90) * 400      # 90~94: 6000 ~ 7600
        elif ovr >= 85:
            ability_val = 4000 + (ovr - 85) * 400      # 85~89: 4000 ~ 5600
        elif ovr >= 80:
            ability_val = 2400 + (ovr - 80) * 320      # 80~84: 2400 ~ 3680
        elif ovr >= 75:
            ability_val = 1200 + (ovr - 75) * 240      # 75~79: 1200 ~ 2160
        else:
            ability_val = max(200, (ovr - 65) * 100)
            
        # 年龄对即战力的折旧 (31 岁以上老将逐年折价)
        if age > 31:
            ability_val = int(ability_val * max(0.40, 1.0 - (age - 31) * 0.10))
            
        # 2. 潜力溢价分 (针对 24 岁以下高潜新人)
        potential_val = 0
        if age <= 23 and pot > ovr:
            gap = pot - ovr
            potential_val = int(gap * 110 * (1.0 + (24 - age) * 0.12))
            
        # 3. 合同性价比修正
        # 预期合理年薪粗略估算 (OVR 80约12M, 85约22M, 90约35M)
        expected_salary = max(2_000_000, int(((ovr - 70) / 25.0) ** 2 * 40_000_000))
        salary_surplus = expected_salary - salary
        
        contract_mod = 0
        if salary_surplus > 0:
            # 童工合同红利
            contract_mod = min(1500, int(salary_surplus / 10_000))
        else:
            # 溢价垃圾长约惩罚
            if years_left >= 2:
                contract_mod = max(-2500, int(salary_surplus / 8_000))
            else:
                # 哪怕溢价，但若为最后一年到期合同，惩罚减半且带到期红利
                contract_mod = 400
                
        total_val = max(100, ability_val + potential_val + contract_mod)
        return total_val

    def evaluate_subjective_trade_package(
        self, 
        players: List[Dict], 
        picks: List[str], 
        evaluating_team_lifecycle: str
    ) -> int:
        """
        计算评估方球队在自身生命周期加权下的主观总得分
        """
        mults = LIFECYCLE_MULTIPLIERS.get(evaluating_team_lifecycle, LIFECYCLE_MULTIPLIERS["PLAYOFF_RISING"])
        total_score = 0
        
        # 1. 球员部分
        for p in players:
            base_val = self.calculate_player_base_value(p)
            age = p["age"]
            years = p["years_left"]
            
            # 依生命周期拆解加权
            if age <= 23:
                weighted_val = int(base_val * mults["potential_mult"])
            elif age >= 30:
                weighted_val = int(base_val * mults["ability_mult"])
            else:
                weighted_val = base_val
                
            # 到期大合同对重建队的额外吸引力
            if years <= 1 and evaluating_team_lifecycle == "REBUILDING":
                weighted_val += 600
                
            total_score += weighted_val
            
        # 2. 选秀权部分
        for pick_tier in picks:
            if pick_tier not in PICK_TIER_VALUES:
                raise ValueError("UNKNOWN: no default draft-pick valuation")
            base_pick_val = PICK_TIER_VALUES[pick_tier]
            weighted_pick_val = int(base_pick_val * mults["pick_mult"])
            total_score += weighted_pick_val
            
        return total_score

    def simulate_two_team_trade_negotiation(
        self,
        team_a: Dict,  # {"abb": "IND", "lifecycle": "REBUILDING", "sent_players": [...], "sent_picks": [...]}
        team_b: Dict   # {"abb": "LAL", "lifecycle": "CONTENDING", "sent_players": [...], "sent_picks": [...]}
    ) -> Tuple[bool, str, Dict]:
        """
        模拟两支球队老板进行多轮博弈磋商与价值裁决
        返回: (是否成交, 拒绝/成交理由, 详尽数据流水)
        """
        # ==========================================
        # 否决红线 1：非卖品检查 (Untouchable Veto)
        # ==========================================
        for p in team_a.get("sent_players", []):
            if p.get("is_untouchable", False):
                return False, f"[VETO / 非卖品否决]: {team_a['abb']} 老板视 {p['name']} 为神圣建队基石，拒绝推上谈判桌！", {}
        for p in team_b.get("sent_players", []):
            if p.get("is_untouchable", False):
                return False, f"[VETO / 非卖品否决]: {team_b['abb']} 老板视 {p['name']} 为神圣建队基石，拒绝推上谈判桌！", {}

        # ==========================================
        # 否决红线 2：CBA 薪资配平校验
        # ==========================================
        sal_a = sum(p.get("salary", 0) for p in team_a.get("sent_players", []))
        sal_b = sum(p.get("salary", 0) for p in team_b.get("sent_players", []))
        
        # 容许 125% + 10万美元
        max_b_for_a = int(sal_a * 1.25) + 100_000
        max_a_for_b = int(sal_b * 1.25) + 100_000
        if sal_b > max_b_for_a or sal_a > max_a_for_b:
            diff = abs(sal_a - sal_b)
            return False, f"[CBA_BREACH / 薪资违规]: 薪资差额达 ${diff:,}，超出 125%+10万 劳资配平范围！", {}

        # ==========================================
        # 核心博弈：主观价值不对称性损益平衡计算
        # ==========================================
        # Team A 视点: 收入 B 送出资产，付出 A 送出资产
        val_in_for_a = self.evaluate_subjective_trade_package(team_b.get("sent_players", []), team_b.get("sent_picks", []), team_a["lifecycle"])
        val_out_for_a = self.evaluate_subjective_trade_package(team_a.get("sent_players", []), team_a.get("sent_picks", []), team_a["lifecycle"])
        net_gain_a = val_in_for_a - val_out_for_a
        
        # Team B 视点: 收入 A 送出资产，付出 B 送出资产
        val_in_for_b = self.evaluate_subjective_trade_package(team_a.get("sent_players", []), team_a.get("sent_picks", []), team_b["lifecycle"])
        val_out_for_b = self.evaluate_subjective_trade_package(team_b.get("sent_players", []), team_b.get("sent_picks", []), team_b["lifecycle"])
        net_gain_b = val_in_for_b - val_out_for_b
        
        details = {
            "team_a": team_a["abb"],
            "team_b": team_b["abb"],
            "salary_a": sal_a,
            "salary_b": sal_b,
            "team_a_eval": {"in": val_in_for_a, "out": val_out_for_a, "net": net_gain_a},
            "team_b_eval": {"in": val_in_for_b, "out": val_out_for_b, "net": net_gain_b}
        }
        
        # 只有双方净收益均 >= 0 (或在微小博弈容差 -300 点内)，交易方能敲定达成！
        if net_gain_a < -300:
            return False, f"[REJECTED / 报价被拒]: {team_a['abb']} 管理层评估认为本方净亏损达 {abs(net_gain_a)} 点，筹码严重不对等，已挂断电话！", details
        if net_gain_b < -300:
            return False, f"[REJECTED / 报价被拒]: {team_b['abb']} 管理层评估认为本方净亏损达 {abs(net_gain_b)} 点，要求增加额外筹码或降低选秀权要求！", details
            
        success_reason = (
            f"[SUCCESS / 双赢达成]: 双方老板达成协议！\n"
            f"  - {team_a['abb']} (生命周期: {team_a['lifecycle']}) 获得主观净收益 +{net_gain_a} 点，完美实现建队目标！\n"
            f"  - {team_b['abb']} (生命周期: {team_b['lifecycle']}) 获得主观净收益 +{net_gain_b} 点，阵容短板得以精准补强！"
        )
        return True, success_reason, details

if __name__ == "__main__":
    engine = DynamicTradeEngine()
    print("=== 模拟测试：步行者与湖人真实历史谈判测试 ===")
    
    # 模拟案例：步行者出 希尔德 (80 OVR, 29岁, 20M, 非核心)，
    # 湖人出 威斯布鲁克 (79 OVR, 33岁, 21M, 到期合同) + 2027 无保护首轮签
    team_pacers = {
        "abb": "IND",
        "lifecycle": "REBUILDING",
        "sent_players": [
            {"name": "Buddy Hield", "ovr": 80, "age": 29, "potential": 80, "salary": 20_500_000, "years_left": 2, "is_untouchable": False}
        ],
        "sent_picks": []
    }
    
    team_lakers = {
        "abb": "LAL",
        "lifecycle": "CONTENDING",
        "sent_players": [
            {"name": "Russell Westbrook", "ovr": 78, "age": 33, "potential": 78, "salary": 21_000_000, "years_left": 1, "is_untouchable": False}
        ],
        "sent_picks": ["UNPROTECTED_HIGH_LOTTERY"]
    }
    
    success, reason, info = engine.simulate_two_team_trade_negotiation(team_pacers, team_lakers)
    print("成交状态:", success)
    print("谈判公报:\n", reason)
    print("点数拆解:", json.dumps(info, indent=2, ensure_ascii=False))
