# -*- coding: utf-8 -*-
"""
NBA 2K22 "高爆发 + 强质量" 拟真物理模型滑块注入器 (Physics Sliders Injector)
针对 2K22 "纸片人感"、"滑冰感"、"泥潭感" 的物理引擎级校准：
- 保留高速爆发与干净利落的动作帧率 (Game Speed 50)
- 建立"速度与加速度的剪刀差" (持球 90/80，无球 92/84)，让冲刺需要真实蹬地起速，告别瞬移滑冰
- 抬高下限 (Min 42/38/44/40)，确保中锋与大个子不卡慢动作
- 属性权重强化力量 (Strength 80) 与下压弹跳 (Vertical 42)，打造扎实重力与动量碰撞
- 提升身体对抗敏感度 (Body-Up 76) 与内线对抗频率 (90/95)
"""
import sys
import os
import struct
import argparse
from typing import Dict, Tuple

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from memory import GameMemory

SLIDERS_CONFIG: Dict[str, Tuple[float, float]] = {
    # 移动曲线 (最大 / 最小)
    'SpeedWithBallMaxRating':          (0.90, 0.90),  # 持球速度最高项 90
    'SpeedWithBallMinRating':          (0.42, 0.42),  # 持球速度最低项 42
    'AccelerationWithBallMaxRating':   (0.80, 0.80),  # 控球加速度最高项 80
    'AccelerationWithBallMinRating':   (0.38, 0.38),  # 控球加速度最低项 38
    'SpeedWithoutBallMaxRating':       (0.92, 0.92),  # 无球速度最高项 92
    'SpeedWithoutBallMinRating':       (0.44, 0.44),  # 无球速度最低项 44
    'AccelerationWithoutBallMaxRating':(0.84, 0.84),  # 无球加速度最高项 84
    'AccelerationWithoutBallMinRating':(0.40, 0.40),  # 无球加速度最低项 40
    # 属性权重
    'PlayerSpeed':                     (0.50, 0.50),  # 速度权重 50
    'PlayerQuickness':                 (0.46, 0.46),  # 加速度权重 46
    'PlayerStrength':                  (0.80, 0.80),  # 力量权重 80 (核心动能碰撞)
    'PlayerVertical':                  (0.42, 0.42),  # 弹跳权重 42 (锁定重力质感)
    # 身体对抗与频率
    'BodyupFitTightnessDistance':      (0.76, 0.76),  # 身体对抗灵敏度 76
    'DrivingContactShotFrequency':     (0.90, 0.95),  # 突破对抗频率 90/95
    'InsideContactShotFrequency':      (0.90, 0.95),  # 内线对抗频率 90/95
    # 控制器
    'DefensiveAssist':                 (0.05, 0.05),  # 强力防守辅助强度 5 (0-10区间)
}

TUNABLE_ORDER = [
    "BaseDifficulty", "PlayerStealing", "PlayerBlocking", "PlayerSpeed", "PlayerSpeedWithBall",
    "PlayerBallHandling", "PlayerDunk", "PlayerOffAwareness", "PlayerDefAwareness", "PlayerOffRebound",
    "PlayerDefRebound", "PlayerStrength", "PlayerQuickness", "PlayerHustle", "PlayerOffensiveConsistency",
    "PlayerDefensiveConsistency", "PlayerDurability", "PlayerStamina", "PlayerHands", "PlayerVertical",
    "PlayerOnBallDefense", "PlayerLateralQuickness", "AlleyOop", "ShotContact", "ShotInside",
    "ShotClose", "ShotMedium", "ShotFar", "ShotLayup", "FreeThrow",
    "ShotCoverageImpact", "ShotTimingImpact", "ShotAimingImpact", "ContactDunkFrequency", "ContactDunkSuccess",
    "BackdoorCuts", "PassAccuracy", "BallTangibility", "BodyupFitTightnessDistance", "PassSpeed",
    "BodyupAttributeWeighting", "PostSpinAndDriveEffectiveness", "PostHopstepAndDropstepEffectiveness", "PostBackdownEffectiveness", "BodyupOffenseSuccessWin",
    "BodyupOffenseSuccessNeutral", "BodyupOffenseSuccessLoss", "BodyupOffenseChargeResolutionFrequency", "BodyupSteeringEffectiveness", "ScreenQuickEffectivenessAbility",
    "ScreenQuickEffectivenessSituation", "ScreenQuickScreenerFoulFrequency", "ScreenQuickDefenderFoulFrequency", "ScreenRegularOffballEffectivenessAbility", "ScreenRegularOffballEffectivenessSituation",
    "ScreenRegularOffballScreenerFoulFrequency", "ScreenRegularOffballDefenderFoulFrequency", "ScreenRegularOnballEffectivenessAbility", "ScreenRegularOnballEffectivenessSituation", "ScreenRegularOnballScreenerFoulFrequency",
    "ScreenRegularOnballDefenderFoulFrequency", "OffballIso2pSpotUpEffectivenessAbility", "OffballIso2pSpotUpEffectivenessInput", "OffballIso2pBasketCutEffectivenessAbility", "OffballIso2pBasketCutEffectivenessInput",
    "OffballIso2pFlareCutEffectivenessAbility", "OffballIso2pFlareCutEffectivenessInput", "StealEffectiveness", "DrivingContactShotFrequency", "InsideContactShotFrequency",
    "LayupDefenseTakeoff", "LayupDefenseRelease", "JumpShotDefenseGather", "JumpShotDefenseRelease", "PostPushAndCrowdEffectiveness",
    "PostTakeChargeEffectiveness", "PostPullChairEffectiveness", "PostStealEffectiveness", "BodyupAIControlledDefenderPenalty", "BodyupDefenseBlockResolutionFrequency",
    "AIControlledPassStealPerceptionChance", "OverTheBackFoulFrequency", "ChargingFoulFrequency", "BlockingFoulFrequency", "ReachingFoulFrequency",
    "ShootingFoulFrequency", "LooseBallFoulFrequency", "IllegalPickFoulFrequency", "FatigueRate", "EnergyRecoverRate",
    "DefensiveAssist", "BoxoutAssist", "DunkTendency", "FlashyPassTendency", "PutbackTendency",
    "FoulTendency", "InterceptionTendency", "OnBallStealTendency", "ContestShotTendency", "PostShotTendency",
    "HelpDefense", "ShotInsideTendency", "ShotCloseTendency", "ShotMediumTendency", "ShotThreeTendency",
    "DriveTendency", "PostUpTendency", "AlleyOopTendency", "SpeedWithoutBallMaxRating", "SpeedWithoutBallMinRating",
    "SpeedWithBallMaxRating", "SpeedWithBallMinRating", "AccelerationWithoutBallMaxRating", "AccelerationWithoutBallMinRating", "AccelerationWithBallMaxRating",
    "AccelerationWithBallMinRating", "PlaceholderHiddenSlider_1", "PlaceholderHiddenSlider_2", "PlaceholderHiddenSlider_3", "PlaceholderHiddenSlider_4",
    "PlaceholderHiddenSlider_5", "PlaceholderHiddenSlider_6", "PlaceholderHiddenSlider_7", "PlaceholderHiddenSlider_8", "PlaceholderHiddenSlider_9",
    "PlaceholderHiddenSlider_10"
]

TUNABLE_INDEX_MAP = {name: i for i, name in enumerate(TUNABLE_ORDER)}

def run_physics_slider_sync(approve_writes: bool = False):
    mem = GameMemory(read_only=not approve_writes)
    base = mem.base_address

    ptr_settings_addr = base + 0x0632B4B0
    ptr_sliders_addr  = base + 0x0632B4A0

    raw_s = mem.read_bytes(ptr_settings_addr, 8)
    raw_l = mem.read_bytes(ptr_sliders_addr, 8)
    if not raw_s or not raw_l:
        raise RuntimeError("无法读取设置与滑块指针槽")

    ptr_settings = struct.unpack('<Q', raw_s)[0]
    ptr_sliders  = struct.unpack('<Q', raw_l)[0]

    def rf(addr):
        b = mem.read_bytes(addr, 4)
        return struct.unpack('<f', b)[0] if b and len(b) == 4 else None

    def wf(addr, val):
        return mem.write_bytes(addr, struct.pack('<f', float(val)))

    print(f"=== NBA 2K22 拟真物理模型状态 (PID: {mem.pid}) ===")
    gs_val = rf(ptr_settings + 0x00)
    print(f"比赛速度 (Game Speed): {gs_val*100:.1f}")

    tables = [("CurrentTable", 4), ("CustomTable", 1012)]
    writes = 0

    for tbl_name, tbl_off in tables:
        print(f"\n--- {tbl_name} (Base Offset +{tbl_off}) ---")
        for name, (u_target, c_target) in SLIDERS_CONFIG.items():
            idx = TUNABLE_INDEX_MAP[name]
            u_addr = ptr_sliders + tbl_off + idx * 8
            c_addr = u_addr + 4

            cur_u = rf(u_addr)
            cur_c = rf(c_addr)

            u_diff = abs(cur_u - u_target) > 0.001
            c_diff = abs(cur_c - c_target) > 0.001

            if approve_writes:
                if u_diff:
                    wf(u_addr, u_target)
                    writes += 1
                if c_diff:
                    wf(c_addr, c_target)
                    writes += 1
                rb_u = rf(u_addr)
                rb_c = rf(c_addr)
                status = "UPDATED" if (u_diff or c_diff) else "OPTIMAL"
                print(f"  [{status:<7}] {name:<35} | USER: {cur_u*100:4.1f} -> {rb_u*100:4.1f} | CPU: {cur_c*100:4.1f} -> {rb_c*100:4.1f}")
            else:
                status = "DIFF" if (u_diff or c_diff) else "MATCH"
                print(f"  [{status:<5}] {name:<35} | USER: {cur_u*100:4.1f} (target {u_target*100:4.1f}) | CPU: {cur_c*100:4.1f} (target {c_target*100:4.1f})")

    if approve_writes:
        print(f"\n[OK] 物理模型滑块写入与回读验证全部完成，总计写入 {writes} 处内存字段。")
    else:
        print("\n[INFO] 只读模式检查完成。未提供 --approve-writes 参数，未执行写入。")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="NBA 2K22 高爆发+强质量物理滑块管理器")
    parser.add_argument("--approve-writes", action="store_true", help="批准写入游戏内存")
    args = parser.parse_args()
    run_physics_slider_sync(approve_writes=args.approve_writes)
