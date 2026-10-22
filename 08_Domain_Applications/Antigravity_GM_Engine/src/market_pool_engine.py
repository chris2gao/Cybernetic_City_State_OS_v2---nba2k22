# -*- coding: utf-8 -*-
"""
NBA 2K22 全市场化动态交易池与竞价撮合引擎 (Market Pool & Dynamic Trading Engine)
彻底实现“数据驱动与市场池驱动”的双轨机制：
1. 球队每月赛场表现与胜率 ──► 驱动卖家主动向 market_trade_block 挂牌真实球员
2. 买家根据识别出的攻防短板 ──► 实时扫描市场池 (Scan Market Pool)
3. 双方发起商业谈判、资产打包、主观得益测算与 CBA 125% 配平
4. 撮合成交后，自动从池中下架、流转归属权并在内存中热写入执行！
历史版市场池已停用：其球员资产、球队挂牌理由和成交样例含硬编码内容，不能作为实测数据。
当前只使用审计通过快照产生的待复核 GM 候选。
"""
import os
import sys
import json
import sqlite3
from datetime import datetime
from typing import Dict, List, Tuple, Optional

sys.path.append(os.path.dirname(__file__))

# 联盟真实资产候选底库 (在赛季进行中根据各队真实表现被推上货架)
REAL_LEAGUE_TRADE_ASSETS = [
    # (所属队, 球员姓名, 位置, 年龄, 能力值, 薪水, 剩余年限, 技能标签, 要价层级, 基础点数, 挂牌动机)
    ("IND", "Domantas Sabonis", "PF/C", 25, 86, 18500000, 3, "INSIDE_ALLSTAR_ANCHOR", "HIGH_LOTTERY_OR_STAR", 6200, "双塔内线拥挤，彻底拆队套现建队大核"),
    ("IND", "Caris LeVert", "SG/SF", 27, 81, 17500000, 2, "SHOT_CREATOR", "FIRST_ROUND_PICK", 3800, "阵地突破效率下滑，腾出后场球权"),
    ("IND", "Justin Holiday", "SF/SG", 32, 75, 6000000, 1, "3&D_WING", "SECOND_ROUND_AND_RELIEF", 1800, "老将到期合同，换取选秀次轮资产"),
    ("SAC", "Buddy Hield", "SG", 28, 80, 23076923, 3, "ELITE_3PT_SHOOTER", "FIRST_ROUND_OR_STARTER", 3600, "后场三后卫拥堵，急需优化薪资结构"),
    ("SAC", "Harrison Barnes", "SF/PF", 29, 81, 20284091, 2, "3&D_WING", "FIRST_ROUND_PICK", 4000, "当打之年锋线拼图，变现潜力资产"),
    ("SAC", "Tristan Thompson", "C", 30, 76, 9720900, 1, "REBOUND_DEF_BIG", "SECOND_ROUND_AND_RELIEF", 1500, "到期合同内线肉盾，降薪避税"),
    ("POR", "CJ McCollum", "SG/PG", 30, 85, 30864198, 3, "ELITE_SHOT_CREATOR", "HIGH_FIRST_AND_YOUNG", 5800, "双枪时代终结，彻底拆解后场薪资空间"),
    ("POR", "Robert Covington", "SF/PF", 31, 77, 12975494, 1, "3&D_WING", "FIRST_ROUND_PICK", 2600, "到期合同优质防守侧翼，季后赛抢手拼图"),
    ("POR", "Norman Powell", "SG/SF", 28, 81, 15517241, 4, "3&D_SCORER", "FIRST_ROUND_PICK", 3900, "长约优质侧翼，清理全队奢侈税压力"),
    ("PHI", "Ben Simmons", "PG/PF", 25, 84, 33003936, 4, "ELITE_PLAYMAKER_DEFENDER", "SUPERSTAR_EXCHANGE", 6500, "心理问题拒绝出战，非全明星后卫绝不贱卖"),
    ("BKN", "James Harden", "SG/PG", 32, 90, 44310840, 1, "MVP_LEVEL_PLAYMAKER", "SUPERSTAR_EXCHANGE", 8200, "更衣室矛盾激化，合同即将到期存在离队风险"),
    ("HOU", "Eric Gordon", "SG", 33, 78, 18218818, 2, "EXPIRING_SHOOTER", "FIRST_ROUND_PICK", 2400, "老将功臣换取未来选秀权，让位年轻人"),
    ("HOU", "Christian Wood", "C/PF", 26, 83, 13666667, 2, "STRETCH_BIG_SCORER", "FIRST_ROUND_AND_YOUNG", 4400, "高位空间内线，合同超值但防守与团队纪律存疑"),
    ("ORL", "Terrence Ross", "SG/SF", 30, 76, 12500000, 2, "BENCH_SPARK_PLUG", "SECOND_ROUND_AND_RELIEF", 1900, "板凳匪徒射手，全面转正年轻新秀出场时间"),
    ("DET", "Jerami Grant", "PF/SF", 27, 82, 20000000, 2, "TWO_WAY_SCORING_WING", "MULTIPLE_FIRSTS", 4800, "当红锋线大鱼，争冠球队争夺焦点"),
    ("WAS", "Spencer Dinwiddie", "PG/SG", 28, 80, 17142857, 3, "P&R_BALL_HANDLER", "ROTATION_PLAYER_SWAP", 3100, "与比尔后场球权不兼容，寻求外线射手互换"),
    ("UTA", "Joe Ingles", "SF/PF", 34, 76, 13000000, 1, "VETERAN_PLAYMAKER_3PT", "SECOND_ROUND_AND_RELIEF", 1800, "受重伤报销但拥有千万到期合同，具备极高避税配平价值")
]

class MarketPoolEngine:
    def __init__(self, db_path: Optional[str] = None):
        self.project_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.db_path = db_path or os.path.join(self.project_dir, "database", "league_state.sqlite")

    def get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    # =========================================================================
    # 1. 卖家根据最新赛程战绩将球员挂牌入池 (Listing into Pool)
    # =========================================================================
    def refresh_trade_block_pool(self, snapshot_id: str) -> List[Dict]:
        """
        基于本月各队生命周期与战绩，动态将符合条件的球员推上公共交易货架池。
        """
        raise RuntimeError(
            "旧版市场挂牌器使用硬编码球员/战绩假设，已停用；"
            "当前快照不具备足够数据确认真实挂牌。"
        )
        conn = self.get_conn()
        cursor = conn.cursor()

        # 清除快照历史挂牌，确保幂等性
        cursor.execute("DELETE FROM market_trade_block WHERE snapshot_id = ?", (snapshot_id,))
        cursor.execute("DELETE FROM market_trade_offers WHERE snapshot_id = ?", (snapshot_id,))

        # 读取处于 SELLER 或 REBUILDING 状态的球队，以及产生位置冗余的球队
        sellers = cursor.execute("""
            SELECT team_abbr, current_lifecycle_state, win_pct 
            FROM team_monthly_stats 
            WHERE snapshot_id = ? AND (current_lifecycle_state IN ('SELLER', 'REBUILDING') OR team_abbr IN ('PHI', 'BKN', 'SAC', 'POR', 'IND'))
        """, (snapshot_id,)).fetchall()

        seller_abbrs = {row["team_abbr"] for row in sellers}
        today_str = datetime.now().strftime("%Y-%m-%d")

        listed_players = []
        for asset in REAL_LEAGUE_TRADE_ASSETS:
            team_abb, p_name, pos, age, ovr, sal, years, tag, tier, val, reason = asset
            # 如果母队处于卖家/重组/挂牌名单中
            if team_abb in seller_abbrs:
                cursor.execute("""
                    INSERT OR REPLACE INTO market_trade_block (
                        snapshot_id, team_abb, player_name, position, age, overall_rating,
                        salary, contract_years_left, skill_archetype, asking_price_tier,
                        base_trade_value, listing_reason, listed_date, status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, 'AVAILABLE')
                """, (
                    snapshot_id, team_abb, p_name, pos, age, ovr,
                    sal, years, tag, tier, val, reason, today_str
                ))
                listed_players.append({
                    "name": p_name, "team": team_abb, "pos": pos, "ovr": ovr,
                    "salary": f"${sal:,}", "tag": tag, "reason": reason
                })

        conn.commit()
        conn.close()
        print(f"[+] 市场交易货架池已刷新！本月全联盟共有 {len(listed_players)} 名真实球员在售挂牌。")
        return listed_players

    # =========================================================================
    # 2. 买家扫描市场池、供需匹配与 CBA 撮合交易 (Market Scan & Bidding)
    # =========================================================================
    def match_market_trades(self, snapshot_id: str) -> List[Dict]:
        """
        买家根据自身技战术短板 (Weaknesses / Target Needs)，实时扫描市场池并撮合交易。
        """
        raise RuntimeError(
            "旧版市场撮合器含硬编码交易与不完整 CBA 结论，已停用；"
            "请使用 GM 生成的待复核候选。"
        )
        conn = self.get_conn()
        cursor = conn.cursor()

        # 1. 查询当前在售公共货架池
        available_assets = cursor.execute("""
            SELECT * FROM market_trade_block 
            WHERE snapshot_id = ? AND status = 'AVAILABLE'
        """, (snapshot_id,)).fetchall()

        # 2. 查询买家需求
        buyers = cursor.execute("""
            SELECT e.team_abbr AS team_abbr, s.current_lifecycle_state AS current_lifecycle_state, e.primary_reinforcement_need AS primary_reinforcement_need
            FROM team_monthly_evaluations e
            JOIN team_monthly_stats s ON e.snapshot_id = s.snapshot_id AND e.team_id = s.team_id
            WHERE e.snapshot_id = ? AND s.current_lifecycle_state IN ('CONTENDING', 'BUYER')
        """, (snapshot_id,)).fetchall()

        executed_deals = []

        # -------------------------------------------------------------
        # 现实大交易场景 1: 新奥尔良鹈鹕求购 CJ·麦科勒姆
        # -------------------------------------------------------------
        cj = next((a for a in available_assets if a["player_name"] == "CJ McCollum"), None)
        buyer_abbrs = {b["team_abbr"] for b in buyers}
        if cj and "NOP" in buyer_abbrs:
            # 鹈鹕送出：约什·哈特 ($12M) + 萨托兰斯基 ($10M到期) + 亚历山大·沃克 ($3.2M) + 2025首轮签
            sent_sal = 12000000 + 10000000 + 3261556
            cj_sal = cj["salary"]
            # CBA 校验: $25.2M * 1.25 + 100k = $31.6M >= $30.8M (合法!)
            cba_pass = (sent_sal * 1.25 + 100000) >= cj_sal

            deal = {
                "trade_name": "波特兰开拓者 与 新奥尔良鹈鹕：CJ·麦科勒姆重磅交易",
                "buyer": "NOP",
                "seller": "POR",
                "target_player": "CJ McCollum",
                "buyer_sent": ["Josh Hart ($12.0M)", "Tomas Satoransky ($10.0M到期)", "Nickeil Alexander-Walker ($3.2M)", "2025年前四保护首轮签"],
                "seller_sent": ["CJ McCollum ($30.8M)", "Larry Nance Jr. ($10.6M)"],
                "buyer_gain": +850,
                "seller_gain": +920,
                "salary_diff": cj_sal - sent_sal,
                "cba_legal": cba_pass,
                "verdict": "ACCEPTED_AND_EXECUTED",
                "reasoning": "鹈鹕从市场池精准寻获 CJ，搭档锡安与英格拉姆组建三叉戟；开拓者获得 $1000万到期合同避税，并斩获首轮签与年轻后卫，双赢达成！"
            }
            executed_deals.append(deal)

            # 更新市场池状态为 TRADED
            cursor.execute("UPDATE market_trade_block SET status = 'TRADED' WHERE item_id = ?", (cj["item_id"],))

            # 写入交易大账本
            cursor.execute("""
                INSERT INTO market_trade_offers (
                    snapshot_id, buyer_team, seller_team, target_player_name, buyer_offered_assets,
                    seller_sent_assets, buyer_net_gain, seller_net_gain, salary_diff, cba_legal,
                    trade_verdict, verdict_reason
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                snapshot_id, deal["buyer"], deal["seller"], deal["target_player"],
                json.dumps(deal["buyer_sent"], ensure_ascii=False), json.dumps(deal["seller_sent"], ensure_ascii=False),
                deal["buyer_gain"], deal["seller_gain"], deal["salary_diff"], deal["cba_legal"],
                deal["verdict"], deal["reasoning"]
            ))

        # -------------------------------------------------------------
        # 现实大交易场景 2: 费城 76 人 与 布鲁克林篮网：哈登互换西蒙斯世纪大交易
        # -------------------------------------------------------------
        harden = next((a for a in available_assets if a["player_name"] == "James Harden"), None)
        simmons = next((a for a in available_assets if a["player_name"] == "Ben Simmons"), None)
        if harden and simmons:
            # 76人送出：西蒙斯 ($33M) + 塞斯·库里 ($8.2M) + 德拉蒙德 ($2.4M) + 2个首轮签
            # 篮网送出：哈登 ($44.3M) + 米尔萨普 ($2.6M)
            deal_harden = {
                "trade_name": "费城 76人 与 布鲁克林篮网：哈登互换西蒙斯与两枚首轮签世纪重磅大交易",
                "buyer": "PHI",
                "seller": "BKN",
                "target_player": "James Harden",
                "buyer_sent": ["Ben Simmons ($33.0M)", "Seth Curry ($8.2M神射)", "Andre Drummond ($2.4M替补中锋)", "2022年首轮无保护", "2027年首轮受保护"],
                "seller_sent": ["James Harden ($44.3M)", "Paul Millsap ($2.6M)"],
                "buyer_gain": +1400,
                "seller_gain": +1350,
                "salary_diff": 44310840 - 43600000,
                "cba_legal": True,
                "verdict": "ACCEPTED_AND_EXECUTED",
                "reasoning": "费城莫雷如愿为恩比德寻得 MVP 级挡拆持球大核哈登；篮网摆脱欧文缺阵带来的更衣室阴霾，收获 DPOY 级防守核心西蒙斯、神射库里与 2 枚宝贵首轮签！"
            }
            executed_deals.append(deal_harden)
            cursor.execute("UPDATE market_trade_block SET status = 'TRADED' WHERE item_id = ?", (harden["item_id"],))
            cursor.execute("UPDATE market_trade_block SET status = 'TRADED' WHERE item_id = ?", (simmons["item_id"],))

            cursor.execute("""
                INSERT INTO market_trade_offers (
                    snapshot_id, buyer_team, seller_team, target_player_name, buyer_offered_assets,
                    seller_sent_assets, buyer_net_gain, seller_net_gain, salary_diff, cba_legal,
                    trade_verdict, verdict_reason
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                snapshot_id, deal_harden["buyer"], deal_harden["seller"], deal_harden["target_player"],
                json.dumps(deal_harden["buyer_sent"], ensure_ascii=False), json.dumps(deal_harden["seller_sent"], ensure_ascii=False),
                deal_harden["buyer_gain"], deal_harden["seller_gain"], deal_harden["salary_diff"], deal_harden["cba_legal"],
                deal_harden["verdict"], deal_harden["reasoning"]
            ))

        conn.commit()
        conn.close()

        print(f"[+] 市场看池与博弈匹配完毕：成功从公共货架池撮合达成 {len(executed_deals)} 笔双赢大交易！")
        return executed_deals

    # =========================================================================
    # 3. 获取当前池子实时摘要 (供 GM 狼人杀发言与公报引用)
    # =========================================================================
    def get_market_summary(self, snapshot_id: str) -> Dict[str, Any]:
        raise RuntimeError(
            "旧版市场池数据未经新批次审计，不能作为当前决策来源。"
        )
        conn = self.get_conn()
        cursor = conn.cursor()

        available = cursor.execute("""
            SELECT player_name, team_abb, position, overall_rating, salary, skill_archetype, listing_reason
            FROM market_trade_block
            WHERE snapshot_id = ? AND status = 'AVAILABLE'
            ORDER BY overall_rating DESC
        """, (snapshot_id,)).fetchall()

        traded = cursor.execute("""
            SELECT * FROM market_trade_offers WHERE snapshot_id = ?
        """, (snapshot_id,)).fetchall()

        conn.close()
        return {
            "available_count": len(available),
            "available_players": [dict(row) for row in available],
            "traded_deals": [dict(row) for row in traded]
        }

if __name__ == "__main__":
    raise SystemExit(
        "此旧版市场池脚本已停用；当前交易输出只能来自通过审计的快照，"
        "且必须标记为待人工与 CBA 复核候选。"
    )
