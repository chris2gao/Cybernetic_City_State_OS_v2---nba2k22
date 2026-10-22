# -*- coding: utf-8 -*-
"""
NBA 2K22 内存全局设置与拟真滑块控制器 (Slider & Global Settings Manager)
基于 k.CT (KappaLambda 原版逆向工程) 与内存控制台基址实现：
1. 控制全局交易与联盟规则 (Trade Controller @ 0x0632FAE8)
2. 控制比赛单节时间与伤病开关 (Settings Controller @ 0x06332630)
3. 控制名人堂难度与拟真对抗滑块 (Sliders Controller @ 0x063319F8)
"""
import sys
import os
import argparse
from typing import Dict, Any, Optional

# 添加根目录路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from memory import GameMemory
import config

class GlobalSettingsManager:
    # 静态控制台基址偏移
    ADDR_TRADE = 0x0632FAE8       # Trade & League Controller
    ADDR_SETTINGS = 0x06332630    # Gameplay Settings
    ADDR_SLIDERS = 0x063319F8     # Sliders (User & CPU)
    ADDR_TIMERS = 0x040A5508      # Game Clock / Timers

    # 关键偏移映射 (来源: k.CT)
    OFFSETS_TRADE = {
        "SIM_QUARTER_LENGTH": 0xB4,           # 模拟单节时长 (4 Bytes, 推荐 12)
        "RECENTLY_SIGNED": 0x154,             # 刚签约不可交易规则 (4 Bytes)
        "RECENTLY_TRADED": 0x158,             # 刚交易不可交易规则 (4 Bytes)
        "FINANCIAL_RULES": 0x160,             # 工资帽硬规则校验 (4 Bytes)
        "TRADE_OVERRIDE": 0x168,              # 强制交易开关 (4 Bytes, 1=开启, 0=关闭)
        "TRADE_DEADLINE": 0x16C,              # 交易截止日开关 (4 Bytes)
        "CPU_CPU_TRADE": 0x170,               # 电脑间自动交易 (4 Bytes, 0=彻底关闭)
        "TRADE_DIFFICULTY": 0x174,            # 交易难度 (4 Bytes, 0~100)
        "CONTRACT_DIFFICULTY": 0x210,         # 续约谈判难度 (4 Bytes, 0~100)
        "CPU_RESIGN_AGGRESSIVE": 0x234,       # 电脑续约积极性 (4 Bytes)
        "MORALE_DIFFICULTY": 0x238,           # 士气难度 (4 Bytes)
        "MORALE_EFFECTS": 0x23C,              # 士气影响程度 (4 Bytes)
        "CHEMISTRY_DIFFICULTY": 0x240,        # 化学反应难度 (4 Bytes)
        "CHEMISTRY_EFFECTS": 0x244,           # 化学反应影响程度 (4 Bytes)
        "USER_INJURY_FREQ": 0x24C,            # 玩家球队伤病频率 (4 Bytes, 推荐 65~75)
        "CPU_INJURY_FREQ": 0x250,             # 电脑球队伤病频率 (4 Bytes, 推荐 65~75)
        "USER_INJURY_EFFECTS": 0x254,         # 玩家伤病严重程度 (4 Bytes, 推荐 25~35)
        "CPU_INJURY_EFFECTS": 0x258,          # 电脑伤病严重程度 (4 Bytes, 推荐 25~35)
        "NORMALIZE_STATS": 0x600,             # 将出场时间规格化至模拟数据 (4 Bytes, 1=开启)
    }

    OFFSETS_SETTINGS = {
        "GAME_SPEED": 0x00,                   # 比赛速度 (Float, 0.0~1.0, 默认 0.50)
        "QUARTER_LENGTH": 0x14,               # 比赛单节时间 (4 Bytes, 用户打 12 分钟)
        "FREE_THROW_DIFFICULTY": 0x60,        # 罚球难度 (Float, 0.0~1.0, 默认 0.50)
        "FOUL_OUT": 0xA0,                     # 犯规离场次数 (4 Bytes, 默认 6)
        "INJURIES_ENABLED": 0xF0,             # 伤病总开关 (4 Bytes, 1=开启, 0=关闭)
    }

    OFFSETS_SLIDERS = {
        "GAME_DIFFICULTY": 0x00,              # 游戏难度 (4 Bytes: 0=职业, 1=全明星, 2=超级巨星, 3=名人堂)
        "USER_INSIDE_SHOT": 0xC8,             # 用户内线投篮 (Float)
        "USER_MID_RANGE": 0xD8,               # 用户中距离 (Float)
        "USER_3PT_SUCCESS": 0xE0,             # 用户三分命中率 (Float)
        "CPU_INSIDE_SHOT": 0xC8 + 4,          # 电脑内线投篮 (Float)
        "CPU_MID_RANGE": 0xD8 + 4,            # 电脑中距离 (Float)
        "CPU_3PT_SUCCESS": 0xE0 + 4,          # 电脑三分命中率 (Float)
        "HELP_DEFENSE_STRENGTH": 0x324,       # 协防强度 (Float)
        "BODY_UP_SENSITIVITY": 0x134,         # 身体对抗敏感度 (Float)
    }

    def __init__(self, mem: GameMemory):
        self.mem = mem

    def inspect_current_state(self) -> Dict[str, Any]:
        """读取当前内存中所有核心全局开关的状态"""
        base = self.mem.base_address
        trade_base = base + self.ADDR_TRADE
        settings_base = base + self.ADDR_SETTINGS

        status = {
            "CPU_CPU_TRADE": self.mem.require_uint32(trade_base + self.OFFSETS_TRADE["CPU_CPU_TRADE"]),
            "TRADE_OVERRIDE": self.mem.require_uint32(trade_base + self.OFFSETS_TRADE["TRADE_OVERRIDE"]),
            "SIM_QUARTER_LENGTH": self.mem.require_uint32(trade_base + self.OFFSETS_TRADE["SIM_QUARTER_LENGTH"]),
            "NORMALIZE_STATS": self.mem.require_uint32(trade_base + self.OFFSETS_TRADE["NORMALIZE_STATS"]),
            "USER_INJURY_FREQ": self.mem.require_uint32(trade_base + self.OFFSETS_TRADE["USER_INJURY_FREQ"]),
            "CPU_INJURY_FREQ": self.mem.require_uint32(trade_base + self.OFFSETS_TRADE["CPU_INJURY_FREQ"]),
            "USER_INJURY_EFFECTS": self.mem.require_uint32(trade_base + self.OFFSETS_TRADE["USER_INJURY_EFFECTS"]),
            "CPU_INJURY_EFFECTS": self.mem.require_uint32(trade_base + self.OFFSETS_TRADE["CPU_INJURY_EFFECTS"]),
            "QUARTER_LENGTH": self.mem.require_uint32(settings_base + self.OFFSETS_SETTINGS["QUARTER_LENGTH"]),
            "INJURIES_ENABLED": self.mem.require_uint32(settings_base + self.OFFSETS_SETTINGS["INJURIES_ENABLED"]),
            "GAME_DIFFICULTY": self.mem.require_uint32(
                base + self.ADDR_SLIDERS + self.OFFSETS_SLIDERS["GAME_DIFFICULTY"]
            ),
        }
        return status

    def lock_realistic_sliders(self, quarter_min: int = 12, is_hof: bool = True) -> bool:
        """
        一键锁定为用户最爱的【12分钟名人堂拟真生态】：
        1. 锁死关闭电脑间乱交易 (CPU_CPU_TRADE = 0)
        2. 开启比赛数据规格化 (NORMALIZE_STATS = 1)
        3. 调整伤病为“高频轻伤、低大伤” (频率 70, 严重度 30)
        4. 确保单节时长设定
        """
        base = self.mem.base_address
        trade_base = base + self.ADDR_TRADE
        settings_base = base + self.ADDR_SETTINGS
        sliders_base = base + self.ADDR_SLIDERS

        try:
            if not 1 <= int(quarter_min) <= 12:
                raise ValueError("quarter_min 必须在 1 到 12 之间")
            # 1. 交易与规则锁定
            expected = {
                "CPU_CPU_TRADE": 0,
                "TRADE_OVERRIDE": 1,
                "SIM_QUARTER_LENGTH": 12,
                "NORMALIZE_STATS": 1,
                "USER_INJURY_FREQ": 70,
                "CPU_INJURY_FREQ": 70,
                "USER_INJURY_EFFECTS": 30,
                "CPU_INJURY_EFFECTS": 30,
                "QUARTER_LENGTH": int(quarter_min),
                "INJURIES_ENABLED": 1,
            }
            if is_hof:
                expected["GAME_DIFFICULTY"] = 3
            addresses = {
                "CPU_CPU_TRADE": trade_base + self.OFFSETS_TRADE["CPU_CPU_TRADE"],
                "TRADE_OVERRIDE": trade_base + self.OFFSETS_TRADE["TRADE_OVERRIDE"],
                "SIM_QUARTER_LENGTH": trade_base + self.OFFSETS_TRADE["SIM_QUARTER_LENGTH"],
                "NORMALIZE_STATS": trade_base + self.OFFSETS_TRADE["NORMALIZE_STATS"],
                "USER_INJURY_FREQ": trade_base + self.OFFSETS_TRADE["USER_INJURY_FREQ"],
                "CPU_INJURY_FREQ": trade_base + self.OFFSETS_TRADE["CPU_INJURY_FREQ"],
                "USER_INJURY_EFFECTS": trade_base + self.OFFSETS_TRADE["USER_INJURY_EFFECTS"],
                "CPU_INJURY_EFFECTS": trade_base + self.OFFSETS_TRADE["CPU_INJURY_EFFECTS"],
                "QUARTER_LENGTH": settings_base + self.OFFSETS_SETTINGS["QUARTER_LENGTH"],
                "INJURIES_ENABLED": settings_base + self.OFFSETS_SETTINGS["INJURIES_ENABLED"],
                "GAME_DIFFICULTY": sliders_base + self.OFFSETS_SLIDERS["GAME_DIFFICULTY"],
            }
            for key, value in expected.items():
                if not self.mem.write_uint32(addresses[key], value):
                    raise OSError(f"写入全局设置 {key} 失败")

            actual = self.inspect_current_state()
            mismatches = {
                key: {"expected": value, "actual": actual.get(key)}
                for key, value in expected.items()
                if actual.get(key) != value
            }
            if mismatches:
                raise OSError(f"全局设置写入后回读不匹配: {mismatches}")
            return True
        except Exception as e:
            print(f"[SliderManager] 写入异常: {e}")
            return False

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="读取或经批准后修改 NBA 2K22 全局设置")
    parser.add_argument(
        "--approve-game-writes",
        action="store_true",
        help="显式批准将拟真设置写入游戏内存",
    )
    args = parser.parse_args()
    mem = GameMemory(read_only=not args.approve_game_writes)

    mgr = GlobalSettingsManager(mem)
    print("=== 读取当前 2K22 内存控制台全局状态 ===")
    state = mgr.inspect_current_state()
    for k, v in state.items():
        print(f"  {k:24}: {v}")

    if not args.approve_game_writes:
        print("\n只读检查完成。未提供 --approve-game-writes，本次未修改游戏设置。")
        sys.exit(0)

    print("\n>>> 正在应用已批准的【单节 12 分钟 + 名人堂 + 关闭电脑交易 + 拟真伤病】方案...")
    if mgr.lock_realistic_sliders(quarter_min=12, is_hof=True):
        print(">>> 锁定成功！底层内存全局设置已与外部 GM 引擎完美对齐！")
    else:
        print(">>> 锁定失败，请检查游戏权限！")
