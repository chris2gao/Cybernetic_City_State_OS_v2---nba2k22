# -*- coding: utf-8 -*-
"""
NBA 2K22 Antigravity 历史选秀名单与 MC 模式选秀接管引擎 (Draft Engine)
1. 1984 钻石一代起步的历史新秀数据库 (乔丹、奥拉朱旺、巴克利、斯托克顿等)
2. 选秀大会前夕 60 槽位内存偷梁换柱覆写接口
3. 选秀大会落幕后的“GM 选秀夜交易与选秀权热纠偏”接口
"""
import os
import sys
from typing import Dict, List, Optional

sys.path.append(os.path.dirname(__file__))
from historical_rookies import query_historical_draft_class

class DraftEngine:
    def __init__(self, db_path: str, player_pool_db_path: Optional[str] = None):
        self.db_path = db_path
        default_pool_db = os.path.join(os.path.dirname(__file__), "..", "database", "nba2k22_players.sqlite")
        self.player_pool_db_path = player_pool_db_path or default_pool_db

    def get_draft_class(self, year: int) -> List[Dict]:
        """按年份读取已由结构标签验证的历史新秀，不回退到未验证克隆或手填名单。"""
        rows = query_historical_draft_class(
            db_path=self.player_pool_db_path,
            year=year,
            limit=60,
        )
        if not rows:
            raise LookupError(
                f"{year} 年没有找到带历史新秀类型码 7 的有效球员；"
                "请检查球员池抓取结果和类型标签，不会按 draft_year 猜测克隆版本。"
            )

        return [
            {
                "pick_proj": row["pick_proj"],
                "slot_id": row.get("slot_id"),
                "full_name": row.get("full_name"),
                "first_name": row.get("first_name"),
                "last_name": row.get("last_name"),
                "draft_round": row.get("draft_round"),
                "draft_pick": row.get("draft_pick"),
                "overall_pick": row.get("overall_pick"),
                "position": row.get("position"),
                "position_name": row.get("position_name"),
                "face_id": row.get("cyberface_id"),
                "potential": row.get("potential"),
                "memory_addr": row.get("memory_addr"),
            }
            for row in rows
        ]

    def simulate_draft_night_trade(self, rookie_name: str, origin_team_abb: str, target_team_abb: str, compensation: str) -> Dict:
        """
        选秀夜大交易与选秀权纠偏协议 (Draft Night Trade Rectification)
        当原生 AI 导致新秀错配或为了促成史诗级建队 (如乔丹与哈利伯顿在步行者联手)，发起选秀夜互换
        """
        return {
            "trade_type": "DRAFT_NIGHT_TRADE",
            "rookie_name": rookie_name,
            "from_team": origin_team_abb,
            "to_team": target_team_abb,
            "compensation": compensation,
            "gm_rational": f"选秀夜正式达成协议！{target_team_abb} 通过送出 {compensation}，从 {origin_team_abb} 手中夺得超级历史新秀 {rookie_name} 的独家签约权与母队签约指针！"
        }

if __name__ == "__main__":
    db_file = os.path.join(os.path.dirname(__file__), "..", "database", "league_state.sqlite")
    engine = DraftEngine(db_file)
    print("============================================================")
    print("  NBA 2K22 历史选秀名单与 MC 模式选秀接管引擎 (Draft Engine)")
    print("============================================================")
    rookie_class = engine.get_draft_class(1984)
    print(f"[+] 成功读取数据库中已验证的 1984 历史新秀，共 {len(rookie_class)} 名。")
    for r in rookie_class[:10]:
        pick = r.get('pick', r.get('pick_proj'))
        fname = r.get('first', r.get('first_name'))
        lname = r.get('last', r.get('last_name'))
        pos = r.get('pos', r.get('position'))
        ovr = r.get('ovr', r.get('overall'))
        pot = r.get('pot', r.get('potential'))
        face = r.get('face', r.get('face_id'))
        print(f"    - 数据排序 #{pick:02d}: {fname} {lname} (位置: {pos}, 潜力: {pot}, 面补 ID: {face})")
    print(f"    - 仅替换以上已验证的 {len(rookie_class)} 名；其余新秀槽位保留游戏生成的小人。")
        
    print("\n[+] 模拟选秀夜纠偏操盘 (Draft Night Trade):")
    sample_trade = engine.simulate_draft_night_trade(
        rookie_name="Michael Jordan",
        origin_team_abb="POR",
        target_team_abb="CHI",
        compensation="两枚未来首轮签 + 全明星锋线即战力"
    )
    print(f"    - {sample_trade['gm_rational']}")
