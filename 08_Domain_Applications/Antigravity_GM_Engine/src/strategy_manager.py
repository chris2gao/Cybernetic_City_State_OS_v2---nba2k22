# -*- coding: utf-8 -*-
"""
NBA 2K22 历史 TEAM 字节只读兼容及球票管理器。
旧 TEAM POE 语义与 setter 已撤销；教练战术使用 coaching_reader/executor。
"""
import os
import sys
import math
from typing import Dict, Optional

sys.path.append(os.path.dirname(__file__))
from memory import GameMemory
from scanner import LeagueScanner
import config

# ==========================================
# 历史名称仅供旧字段兼容；以下字节为 LEGACY_UNVERIFIED，禁止按名称推断语义。
# ==========================================
LEGACY_TEAM_RAW_OFFSETS = {
    "OFF_PACE": 0xEB2,
    "FASTBREAK_FOCUS": 0xEB3,
    "OFF_REBOUND": 0xEB4,
    "DEF_REBOUND": 0xEB5,
    "ON_BALL_PRESSURE": 0xEB7,
    "OFF_BALL_PRESSURE": 0xEB8,
    "PICK_AND_ROLL_DEF": 0xEB9,
    "HELP_DEFENSE_LEVEL": 0xEBC,
}

# ==========================================
# 场馆商业与物价偏移字典 (基于 Team 结构体)
# ==========================================
BUSINESS_OFFSETS = {
    "TICKET_LOWER_BOWL": 0xF8C,     # 下层看台票价 (float)
    "TICKET_UPPER_BOWL": 0xF90,     # 上层看台平民票价 (float)
    "TICKET_CLUB_LEVEL": 0xF94,     # 贵宾俱乐部票价 (float)
    "TICKET_COURTSIDE": 0xF98,      # 场边VIP/平均指导票价 (float)
    "PARKING_FEE": 0xF9C,           # 停车费 (float)
    "CONCESSION_BEER": 0xFA0,       # 啤酒饮料售价 (float)
    "CONCESSION_HOTDOG": 0xFA4,     # 热狗食品售价 (float)
    "CONCESSION_SODA": 0xFA8,       # 碳酸汽水售价 (float)
    "MERCH_HAT": 0xFB0,             # 球队主题球帽售价 (float)
    "MERCH_TSHIRT": 0xFB8,          # 球队官方T恤售价 (float)
    "MERCH_JERSEY": 0xFC0,          # 官方复刻比赛球衣售价 (float)
    "FAN_INTEREST": 0xF7C,          # 球迷热度 (float, 0.0 ~ 1.0)
    "GATE_REVENUE": 0xFD8,          # 门票总收入 (uint32)
    "MERCH_REVENUE": 0xFDC,         # 周边商品总收入 (uint32)
}

class StrategyManager:
    def __init__(self, mem: Optional[GameMemory] = None):
        self.mem = mem or GameMemory()
        self.scanner = LeagueScanner(self.mem)
        self.teams = self.scanner.find_active_teams()

    def get_team_strategy(self, team_id: int) -> Optional[Dict]:
        """Compatibility observations only: these bytes are NOT coach tactics."""
        if team_id not in self.teams:
            return None
        base = self.teams[team_id]["address"]
        STRATEGY_OFFSETS = LEGACY_TEAM_RAW_OFFSETS
        return {
            "observation_status": "LEGACY_UNVERIFIED",
            "tactical_semantics": "REVOKED_USE_COACHING_READER",
            "team_name": self.teams[team_id]["name"],
            "off_pace": self.mem.require_uint8(base + STRATEGY_OFFSETS["OFF_PACE"]),
            "fastbreak_focus": self.mem.require_uint8(base + STRATEGY_OFFSETS["FASTBREAK_FOCUS"]),
            "off_rebound": self.mem.require_uint8(base + STRATEGY_OFFSETS["OFF_REBOUND"]),
            "def_rebound": self.mem.require_uint8(base + STRATEGY_OFFSETS["DEF_REBOUND"]),
            "on_ball_pressure": self.mem.require_uint8(base + STRATEGY_OFFSETS["ON_BALL_PRESSURE"]),
            "off_ball_pressure": self.mem.require_uint8(base + STRATEGY_OFFSETS["OFF_BALL_PRESSURE"]),
            "pnr_def": self.mem.require_uint8(base + STRATEGY_OFFSETS["PICK_AND_ROLL_DEF"]),
            "help_def": self.mem.require_uint8(base + STRATEGY_OFFSETS["HELP_DEFENSE_LEVEL"]),
        }

    def set_team_strategy(self, team_id: int, **kwargs) -> bool:
        """Revoked before any target lookup, memory read or write."""
        raise RuntimeError("LEGACY_TEAM_POE_OFFSETS_REVOKED: use an explicitly approved native coaching plan")

    def get_team_business(self, team_id: int) -> Optional[Dict]:
        """读取指定球队商业与票价参数"""
        if team_id not in self.teams:
            return None
        base = self.teams[team_id]["address"]
        return {
            "team_name": self.teams[team_id]["name"],
            "ticket_lower": round(self.mem.require_float(base + BUSINESS_OFFSETS["TICKET_LOWER_BOWL"]), 2),
            "ticket_upper": round(self.mem.require_float(base + BUSINESS_OFFSETS["TICKET_UPPER_BOWL"]), 2),
            "ticket_courtside": round(self.mem.require_float(base + BUSINESS_OFFSETS["TICKET_COURTSIDE"]), 2),
            "beer_price": round(self.mem.require_float(base + BUSINESS_OFFSETS["CONCESSION_BEER"]), 2),
            "hotdog_price": round(self.mem.require_float(base + BUSINESS_OFFSETS["CONCESSION_HOTDOG"]), 2),
            "jersey_price": round(self.mem.require_float(base + BUSINESS_OFFSETS["MERCH_JERSEY"]), 2),
            "fan_interest": round(self.mem.require_float(base + BUSINESS_OFFSETS["FAN_INTEREST"]), 2),
            "gate_revenue": self.mem.require_uint32(base + BUSINESS_OFFSETS["GATE_REVENUE"]),
        }

    def set_ticket_pricing(self, team_id: int, courtside: float, lower: float, upper: float) -> bool:
        """分级设置球票价格"""
        if team_id not in self.teams:
            return False
        base = self.teams[team_id]["address"]
        values = {
            "ticket_courtside": (BUSINESS_OFFSETS["TICKET_COURTSIDE"], float(courtside)),
            "ticket_lower": (BUSINESS_OFFSETS["TICKET_LOWER_BOWL"], float(lower)),
            "ticket_upper": (BUSINESS_OFFSETS["TICKET_UPPER_BOWL"], float(upper)),
        }
        for name, (_, value) in values.items():
            if not math.isfinite(value) or value < 0:
                raise ValueError(f"{name} 必须是有限的非负价格")
        for name, (offset, value) in values.items():
            if not self.mem.write_float(base + offset, value):
                raise OSError(f"写入球队 {team_id} {name} 失败")
        for name, (offset, expected) in values.items():
            actual = self.mem.require_float(base + offset)
            if not math.isfinite(actual) or not math.isclose(actual, expected, rel_tol=1e-6, abs_tol=0.02):
                raise OSError(f"球队 {team_id} {name} 回读不符: 期望 {expected}, 实际 {actual}")
        return True

if __name__ == "__main__":
    mgr = StrategyManager()
    print("=== 全联盟代表性球队攻防策略与门票经济抽检 ===")
    for tid in [20, 29, 10, 8]:  # IND, GSW, MIA, MEM
        strat = mgr.get_team_strategy(tid)
        biz = mgr.get_team_business(tid)
        print(f"\n[{strat['team_name']}]")
        print(f"  - 攻防策略: 进攻节奏={strat['off_pace']}, 快攻={strat['fastbreak_focus']}, 对球施压={strat['on_ball_pressure']}, 挡拆防守={strat['pnr_def']}")
        print(f"  - 主场经济: 场边票=${biz['ticket_courtside']:.2f}, 下层票=${biz['ticket_lower']:.2f}, 上层票=${biz['ticket_upper']:.2f}, 球衣=${biz['jersey_price']:.2f}, 球迷热度={biz['fan_interest']}")
