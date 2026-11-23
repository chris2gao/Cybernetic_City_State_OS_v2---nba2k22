# -*- coding: utf-8 -*-
"""
NBA 2K22 30 支球队核心五虎现实化与标志性 DNA 重构规格书构建器 (v2.0 全维通用规范 - 2022~2026 核心巨星深度现实化校准版)
(Build 30-Team Top 5 Realism & Signature DNA Rebalance Spec v2.0 - 2022-2026 Core Calibration Edition)

目标：
1. 聚焦 30 支球队绝对核心（如勇士库里、掘金约基奇、独行侠东契奇、雄鹿字母哥、凯尔特人塔图姆、76人恩比德等），深度注入 2022 夺冠/巅峰打法与 2026 成长轨迹；
2. 彻底重构库里 FMVP 标志性特征：增肌至力量 75、体能 99、无球掩护反跑 (Cutter 11) + 追梦手递手 (Handoff 12) + 跑位三分 (3PT 15) + 决胜挡拆 (PnR 4)；
3. 严格执行“球权双核铁律”：触球倾向 (touches at 1177) 与出手倾向 (shot at 1112) 双驱绑定；
4. 修正并扩充 29 项攻防属性、29 项战术倾向与 80 项技能等级徽章（100% 匹配底层二进制字典与位域）；
5. 输出至 C:\\nba2k22\\exports\\cycle_02_30_teams_realism_execution_ready.json 及仓内归档目录。
"""

import os
import sys
import json
import sqlite3
from typing import Dict, List, Any

# 换算公式：Raw = min(255, max(0, int((Rating - 25) * 3)))
def rating_to_raw(rating: int) -> int:
    return min(255, max(0, int((rating - 25) * 3)))

# 30 支核心球队六大赛区映射
DIVISIONS = {
    "BATCH_01_ATLANTIC": {
        "division": "Atlantic",
        "team_ids": [0, 5, 14, 18, 22]  # PHI, BOS, NYK, BKN, TOR
    },
    "BATCH_02_CENTRAL": {
        "division": "Central",
        "team_ids": [1, 3, 4, 20, 21]   # MIL, CHI, CLE, IND, DET
    },
    "BATCH_03_SOUTHEAST": {
        "division": "Southeast",
        "team_ids": [2, 9, 10, 16, 31]  # WAS, ATL, MIA, ORL, CHA
    },
    "BATCH_04_NORTHWEST": {
        "division": "Northwest",
        "team_ids": [12, 19, 24, 27, 28] # UTA, DEN, OKC, MIN, POR
    },
    "BATCH_05_PACIFIC": {
        "division": "Pacific",
        "team_ids": [6, 13, 15, 26, 29]  # LAC, SAC, LAL, PHX, GSW
    },
    "BATCH_06_SOUTHWEST": {
        "division": "Southwest",
        "team_ids": [8, 11, 17, 23, 25]  # MEM, NOP, DAL, HOU, SAS
    }
}

# 战术类型定义
# 0: NONE, 1: ISOLATION, 4: PR_BALL_HANDLER, 7: PR_ROLL_MAN, 8: POST_UP_LOW, 9: POST_UP_HIGH, 
# 11: CUTTER, 12: HANDOFF_RECEIVER, 13: HANDOFF_PASSER, 14: MID_RANGE, 15: THREE_POINT

def get_team_tactical_profile(team_id: int) -> Dict[str, Any]:
    """返回球队默认战术系统、轮换与攻防重点"""
    profiles = {
        0: {"active_system": 4, "bench_depth": 9, "bench_utilization": 50, "run_play": 82, "poe_offense": 3, "poe_tempo": 7, "poe_defense": 13},
        1: {"active_system": 0, "bench_depth": 9, "bench_utilization": 50, "run_play": 80, "poe_offense": 1, "poe_tempo": 9, "poe_defense": 13},
        2: {"active_system": 2, "bench_depth": 9, "bench_utilization": 50, "run_play": 80, "poe_offense": 4, "poe_tempo": 8, "poe_defense": 13},
        3: {"active_system": 2, "bench_depth": 9, "bench_utilization": 50, "run_play": 80, "poe_offense": 4, "poe_tempo": 8, "poe_defense": 13},
        4: {"active_system": 2, "bench_depth": 9, "bench_utilization": 50, "run_play": 84, "poe_offense": 4, "poe_tempo": 8, "poe_defense": 13},
        5: {"active_system": 0, "bench_depth": 10, "bench_utilization": 52, "run_play": 85, "poe_offense": 4, "poe_tempo": 8, "poe_defense": 15},
        6: {"active_system": 2, "bench_depth": 10, "bench_utilization": 52, "run_play": 82, "poe_offense": 4, "poe_tempo": 7, "poe_defense": 15},
        8: {"active_system": 2, "bench_depth": 10, "bench_utilization": 52, "run_play": 80, "poe_offense": 1, "poe_tempo": 9, "poe_defense": 13},
        9: {"active_system": 2, "bench_depth": 9, "bench_utilization": 50, "run_play": 82, "poe_offense": 4, "poe_tempo": 8, "poe_defense": 13},
        10: {"active_system": 5, "bench_depth": 9, "bench_utilization": 52, "run_play": 85, "poe_offense": 4, "poe_tempo": 7, "poe_defense": 18},
        11: {"active_system": 2, "bench_depth": 9, "bench_utilization": 50, "run_play": 82, "poe_offense": 1, "poe_tempo": 8, "poe_defense": 13},
        12: {"active_system": 0, "bench_depth": 9, "bench_utilization": 50, "run_play": 80, "poe_offense": 2, "poe_tempo": 8, "poe_defense": 13},
        13: {"active_system": 0, "bench_depth": 9, "bench_utilization": 50, "run_play": 85, "poe_offense": 2, "poe_tempo": 9, "poe_defense": 13},
        14: {"active_system": 2, "bench_depth": 9, "bench_utilization": 48, "run_play": 85, "poe_offense": 4, "poe_tempo": 7, "poe_defense": 13},
        15: {"active_system": 2, "bench_depth": 9, "bench_utilization": 50, "run_play": 82, "poe_offense": 1, "poe_tempo": 8, "poe_defense": 13},
        16: {"active_system": 2, "bench_depth": 9, "bench_utilization": 50, "run_play": 80, "poe_offense": 4, "poe_tempo": 8, "poe_defense": 13},
        17: {"active_system": 0, "bench_depth": 9, "bench_utilization": 50, "run_play": 82, "poe_offense": 4, "poe_tempo": 7, "poe_defense": 13},
        18: {"active_system": 2, "bench_depth": 9, "bench_utilization": 50, "run_play": 80, "poe_offense": 4, "poe_tempo": 8, "poe_defense": 15},
        19: {"active_system": 4, "bench_depth": 9, "bench_utilization": 50, "run_play": 85, "poe_offense": 3, "poe_tempo": 7, "poe_defense": 13},
        20: {"active_system": 0, "bench_depth": 10, "bench_utilization": 54, "run_play": 86, "poe_offense": 2, "poe_tempo": 9, "poe_defense": 15},
        21: {"active_system": 2, "bench_depth": 9, "bench_utilization": 50, "run_play": 80, "poe_offense": 4, "poe_tempo": 8, "poe_defense": 13},
        22: {"active_system": 0, "bench_depth": 9, "bench_utilization": 50, "run_play": 80, "poe_offense": 4, "poe_tempo": 8, "poe_defense": 15},
        23: {"active_system": 4, "bench_depth": 9, "bench_utilization": 50, "run_play": 80, "poe_offense": 3, "poe_tempo": 8, "poe_defense": 13},
        24: {"active_system": 0, "bench_depth": 10, "bench_utilization": 52, "run_play": 82, "poe_offense": 4, "poe_tempo": 8, "poe_defense": 15},
        25: {"active_system": 2, "bench_depth": 9, "bench_utilization": 50, "run_play": 80, "poe_offense": 4, "poe_tempo": 8, "poe_defense": 13},
        26: {"active_system": 2, "bench_depth": 9, "bench_utilization": 50, "run_play": 85, "poe_offense": 4, "poe_tempo": 7, "poe_defense": 15},
        27: {"active_system": 4, "bench_depth": 9, "bench_utilization": 50, "run_play": 82, "poe_offense": 1, "poe_tempo": 8, "poe_defense": 13},
        28: {"active_system": 0, "bench_depth": 9, "bench_utilization": 50, "run_play": 82, "poe_offense": 4, "poe_tempo": 8, "poe_defense": 13},
        29: {"active_system": 0, "bench_depth": 10, "bench_utilization": 54, "run_play": 88, "poe_offense": 2, "poe_tempo": 9, "poe_defense": 15},
        31: {"active_system": 0, "bench_depth": 9, "bench_utilization": 52, "run_play": 80, "poe_offense": 2, "poe_tempo": 9, "poe_defense": 13}
    }
    default_cfg = {"active_system": 6, "bench_depth": 9, "bench_utilization": 50, "run_play": 80, "poe_offense": 4, "poe_tempo": 8, "poe_defense": 13}
    return profiles.get(team_id, default_cfg)

def remap_play_types(pts: List[int]) -> List[int]:
    """
    修正 2K22 原生战术枚举：
    原脚本误将 13 视为 Handoff Passer，导致 14(Mid Range) 与 15(3PT) 整体右移越界。
    2K22 原生有效枚举严格为 0..14 (play_type_enum):
    13: SCREEN_MID (中距离战术)
    14: SCREEN_3PT (三分球战术)
    任何 >= 15 的数值均属越界，必须纠正回原生合法值。
    """
    remapped = []
    for x in pts:
        if x == 15:
            val = 14  # 原意为三分战术，映射为原生 14
        elif x == 14:
            val = 13  # 原意为中距离战术，映射为原生 13
        else:
            val = x
        if val in [13, 14] and val in remapped:
            val = 13 if val == 14 and 13 not in remapped else 0
        remapped.append(min(14, max(0, val)))
    return remapped

def make_player_entry(name: str, slot: int, face: int, initiator: int, play_types: List[int],
                      intangibles: int, touches: int, shot: int,
                      extra_attrs: Dict[str, int] = None,
                      extra_tends: Dict[str, int] = None,
                      badges: Dict[str, int] = None) -> Dict[str, Any]:
    """标准化生成单一球员 v2.0 规格项 (扩展全量物理字典)"""
    play_types = remap_play_types(play_types)
    attr_offsets = {
        "intangibles": 1088,
        "three_point": 1062,
        "mid_range": 1061,
        "shot_close": 1060,
        "driving_layup": 1055,
        "ball_control": 1064,
        "pass_accuracy": 1066,
        "pass_iq": 1065,
        "pass_vision": 1107,
        "perimeter_def": 1070,
        "interior_def": 1069,
        "lateral_quick": 1071,
        "steal": 1074,
        "block": 1073,
        "strength": 1083,
        "speed": 1079,
        "acceleration": 1081,
        "vertical": 1082,
        "stamina": 1084,
        "hustle": 1085,
        "driving_dunk": 1078,
        "standing_dunk": 1077,
        "post_hook": 1057,
        "post_fadeaway": 1056,
        "post_moves": 1058,
        "def_rebound": 1068,
        "off_rebound": 1067
    }
    tend_offsets = {
        "touches": 1177,
        "shot": 1112,
        "drive": 1155,
        "dish_to_open_man": 1176,
        "shot_three": 1138,
        "spot_up_three": 1139,
        "shot_mid_range": 1130,
        "shot_close": 1126,
        "post_up": 1178,
        "contest_shot": 1207,
        "block_shot": 1208,
        "on_ball_steal": 1206,
        "pass_interception": 1204,
        "attack_strong_on_drive": 1175
    }

    mods = [
        {
            "field": "intangibles",
            "offset": 1088,
            "val_raw": rating_to_raw(intangibles),
            "human_val": intangibles,
            "type": "uint8",
            "description": f"无形资产设定: {intangibles} (控制轮换地位与AI上场时间)"
        },
        {
            "field": "touches",
            "offset": 1177,
            "val_raw": touches,
            "type": "uint8",
            "description": f"触球呼叫倾向: {touches} (决定战术发起比率)"
        },
        {
            "field": "shot",
            "offset": 1112,
            "val_raw": shot,
            "type": "uint8",
            "description": f"持球终结出手倾向: {shot} (决定真实持球得分侵略性)"
        }
    ]

    if extra_attrs:
        for attr_k, attr_v in extra_attrs.items():
            if attr_k in attr_offsets:
                mods.append({
                    "field": attr_k,
                    "offset": attr_offsets[attr_k],
                    "val_raw": rating_to_raw(attr_v),
                    "human_val": attr_v,
                    "type": "uint8",
                    "description": f"关键攻防属性 {attr_k}: {attr_v}"
                })

    if extra_tends:
        for tend_k, tend_v in extra_tends.items():
            if tend_k in tend_offsets:
                mods.append({
                    "field": tend_k,
                    "offset": tend_offsets[tend_k],
                    "val_raw": tend_v,
                    "type": "uint8",
                    "description": f"战术特征倾向 {tend_k}: {tend_v}"
                })

    return {
        "player_name": name,
        "roster_index": slot,
        "cyberface_id": face,
        "tactical_playbook": {
            "is_play_initiator": initiator,
            "play_types": play_types
        },
        "modifications": mods,
        "badges": badges or {}
    }

def build_team_top5_players(team_id: int, roster: Dict[int, tuple]) -> List[Dict[str, Any]]:
    """根据真实联盟战力和赋能目标构建每支球队核心五虎 (全联盟 30 队核心深度现实化校准)"""
    writes = []

    # ==================== BATCH 01: ATLANTIC ====================
    # 0: PHI (Philadelphia 76ers)
    if team_id == 0:
        # 乔尔·恩比德 Joel Embiid (Slot 2, Face 4090) - 2022 得分王中锋 (30.6 PPG)
        writes.append(make_player_entry(
            name=roster[2][0], slot=2, face=roster[2][1], initiator=1,
            play_types=[8, 1, 7, 4], # Post Low, Iso, PnR Roll, PnR Handler
            intangibles=99, touches=96, shot=96,
            extra_attrs={"interior_def": 95, "block": 94, "mid_range": 94, "strength": 98, "post_moves": 96, "post_fadeaway": 95, "def_rebound": 95},
            extra_tends={"post_up": 96, "shot_mid_range": 92, "contest_shot": 95, "block_shot": 92},
            badges={"BackdownPunisher": 4, "PostDropStepper": 4, "RimProtector": 4, "Intimidator": 4, "DifficultShots": 4, "Deadeye": 4, "DreamShake": 4, "HookSpecialist": 4}
        ))
        # 詹姆斯·哈登 James Harden (Slot 12, Face 1603)
        writes.append(make_player_entry(
            name=roster[12][0], slot=12, face=roster[12][1], initiator=1,
            play_types=[4, 1, 15, 0],
            intangibles=96, touches=92, shot=88,
            extra_attrs={"pass_accuracy": 96, "pass_vision": 96, "ball_control": 95, "three_point": 88},
            extra_tends={"dish_to_open_man": 96, "drive": 90, "shot_three": 90},
            badges={"Dimer": 4, "FloorGeneral": 4, "HandlesForDays": 4, "Deadeye": 3, "SpaceCreator": 4, "StopAndPop": 4}
        ))
        # 泰雷斯·马克西 Tyrese Maxey (Slot 5, Face 8011) - 极速爆发超巨
        writes.append(make_player_entry(
            name=roster[5][0], slot=5, face=roster[5][1], initiator=1,
            play_types=[4, 1, 15, 11],
            intangibles=95, touches=90, shot=90,
            extra_attrs={"speed": 98, "acceleration": 98, "three_point": 92, "driving_layup": 94, "ball_control": 90},
            extra_tends={"drive": 95, "spot_up_three": 90},
            badges={"QuickFirstStep": 4, "Downhill": 4, "Sniper": 4, "Chef": 3, "FearlessFinisher": 4}
        ))
        # 托比亚斯·哈里斯 (Slot 1, Face 2149)
        writes.append(make_player_entry(
            name=roster[1][0], slot=1, face=roster[1][1], initiator=0,
            play_types=[14, 15, 8, 0],
            intangibles=85, touches=78, shot=80,
            extra_attrs={"mid_range": 86, "three_point": 82}
        ))
        # 马蒂斯·塞布尔 Matisse Thybulle (Slot 3, Face 7839)
        writes.append(make_player_entry(
            name=roster[3][0], slot=3, face=roster[3][1], initiator=0,
            play_types=[11, 15, 0, 0],
            intangibles=84, touches=60, shot=60,
            extra_attrs={"perimeter_def": 95, "steal": 95, "lateral_quick": 94},
            extra_tends={"on_ball_steal": 95, "contest_shot": 90},
            badges={"Clamps": 4, "Interceptor": 4, "PickPocket": 4}
        ))

    # 5: BOS (Boston Celtics)
    elif team_id == 5:
        # 杰森·塔图姆 Jayson Tatum (Slot 3, Face 7504) - 2022 总决赛领袖 / 最佳一阵
        writes.append(make_player_entry(
            name=roster[3][0], slot=3, face=roster[3][1], initiator=1,
            play_types=[1, 4, 15, 14],
            intangibles=99, touches=96, shot=96,
            extra_attrs={"three_point": 92, "mid_range": 92, "driving_layup": 92, "perimeter_def": 92, "lateral_quick": 90, "ball_control": 90},
            extra_tends={"shot_three": 92, "spot_up_three": 92, "drive": 92, "contest_shot": 88},
            badges={"Deadeye": 4, "Sniper": 4, "DifficultShots": 4, "Clamps": 4, "Blinders": 4, "CatchAndShoot": 4, "HandlesForDays": 3}
        ))
        # 杰伦·布朗 Jaylen Brown (Slot 2, Face 7206)
        writes.append(make_player_entry(
            name=roster[2][0], slot=2, face=roster[2][1], initiator=1,
            play_types=[1, 4, 11, 15],
            intangibles=96, touches=92, shot=94,
            extra_attrs={"driving_dunk": 95, "driving_layup": 94, "three_point": 86, "perimeter_def": 90},
            badges={"Posterizer": 4, "Clamps": 4, "FearlessFinisher": 4, "FastTwitch": 4}
        ))
        # 马库斯·斯玛特 Marcus Smart (Slot 1, Face 4092) - 2022 DPOY 最佳防守球员
        writes.append(make_player_entry(
            name=roster[1][0], slot=1, face=roster[1][1], initiator=1,
            play_types=[4, 12, 15, 0],
            intangibles=92, touches=80, shot=75,
            extra_attrs={"perimeter_def": 96, "steal": 94, "lateral_quick": 94},
            badges={"Clamps": 4, "Menace": 4, "DefensiveLeader": 4, "PickPocket": 4}
        ))
        # 德里克·怀特 Derrick White (Slot 11, Face 7536)
        writes.append(make_player_entry(
            name=roster[11][0], slot=11, face=roster[11][1], initiator=1,
            play_types=[4, 15, 11, 12],
            intangibles=92, touches=82, shot=82,
            extra_attrs={"three_point": 88, "perimeter_def": 92, "pass_accuracy": 88},
            badges={"Clamps": 4, "CatchAndShoot": 4, "Sniper": 3}
        ))
        # 马尔科姆·布罗格登 Malcolm Brogdon (Slot 12, Face 7239)
        writes.append(make_player_entry(
            name=roster[12][0], slot=12, face=roster[12][1], initiator=1,
            play_types=[4, 15, 1, 14],
            intangibles=88, touches=82, shot=84,
            extra_attrs={"three_point": 90, "driving_layup": 88, "mid_range": 88},
            badges={"CatchAndShoot": 4, "Deadeye": 3, "Sniper": 3}
        ))

    # 14: NYK (New York Knicks)
    elif team_id == 14:
        # 加伦·布伦森 Jalen Brunson (Slot 14, Face 7732) - 2026 纽约大头最佳阵容一阵超巨！
        writes.append(make_player_entry(
            name=roster[14][0], slot=14, face=roster[14][1], initiator=1,
            play_types=[4, 1, 8, 14], # PnR, Iso, Post Low, Mid-Range
            intangibles=98, touches=96, shot=95,
            extra_attrs={"ball_control": 95, "mid_range": 96, "three_point": 90, "driving_layup": 96, "pass_accuracy": 92, "strength": 78, "post_moves": 92},
            extra_tends={"drive": 96, "post_up": 90, "shot_mid_range": 95, "dish_to_open_man": 88},
            badges={"DifficultShots": 4, "FearlessFinisher": 4, "TearDropper": 4, "HandlesForDays": 4, "ClutchShooter": 4, "QuickFirstStep": 4}
        ))
        # 朱利叶斯·兰德尔 Julius Randle (Slot 3, Face 4094)
        writes.append(make_player_entry(
            name=roster[3][0], slot=3, face=roster[3][1], initiator=1,
            play_types=[8, 1, 4, 15],
            intangibles=92, touches=90, shot=90,
            extra_attrs={"strength": 92, "driving_layup": 88, "mid_range": 86, "three_point": 82},
            badges={"BackdownPunisher": 3, "PostDropStepper": 3}
        ))
        # R.J. 巴雷特 R.J. Barrett (Slot 2, Face 7822)
        writes.append(make_player_entry(
            name=roster[2][0], slot=2, face=roster[2][1], initiator=0,
            play_types=[11, 4, 15, 1],
            intangibles=86, touches=82, shot=84,
            extra_attrs={"driving_layup": 88, "speed": 88}
        ))
        # 米切尔·罗宾逊 Mitchell Robinson (Slot 4, Face 7735)
        writes.append(make_player_entry(
            name=roster[4][0], slot=4, face=roster[4][1], initiator=0,
            play_types=[7, 11, 0, 0],
            intangibles=88, touches=65, shot=65,
            extra_attrs={"interior_def": 90, "block": 94},
            badges={"RimProtector": 4, "Intimidator": 4}
        ))
        # 伊曼纽尔·奎克利 Immanuel Quickley (Slot 7, Face 8014)
        writes.append(make_player_entry(
            name=roster[7][0], slot=7, face=roster[7][1], initiator=1,
            play_types=[4, 15, 1, 14],
            intangibles=88, touches=82, shot=84,
            extra_attrs={"three_point": 88, "speed": 92, "driving_layup": 88},
            badges={"TearDropper": 4, "Sniper": 3}
        ))

    # 18: BKN (Brooklyn Nets)
    elif team_id == 18:
        # 凯文·杜兰特 Kevin Durant (Slot 2, Face 1411) - 2022 极度高效无解死神 (29.9 PPG)
        writes.append(make_player_entry(
            name=roster[2][0], slot=2, face=roster[2][1], initiator=1,
            play_types=[1, 14, 15, 4],
            intangibles=99, touches=98, shot=98,
            extra_attrs={"mid_range": 99, "three_point": 94, "driving_layup": 92, "block": 86},
            extra_tends={"shot_mid_range": 99, "shot_three": 94, "drive": 90},
            badges={"Deadeye": 4, "DifficultShots": 4, "Sniper": 4, "Blinders": 4, "CatchAndShoot": 4, "VolumeShooter": 4}
        ))
        # 凯里·欧文 Kyrie Irving (Slot 0, Face 2122)
        writes.append(make_player_entry(
            name=roster[0][0], slot=0, face=roster[0][1], initiator=1,
            play_types=[1, 4, 14, 15],
            intangibles=97, touches=95, shot=95,
            extra_attrs={"ball_control": 99, "driving_layup": 99, "mid_range": 95, "three_point": 92},
            badges={"AnkleBreaker": 4, "HandlesForDays": 4, "DifficultShots": 4, "TearDropper": 4, "CircusThrees": 4}
        ))
        # 本·西蒙斯 Ben Simmons (Slot 10, Face 7200)
        writes.append(make_player_entry(
            name=roster[10][0], slot=10, face=roster[10][1], initiator=1,
            play_types=[4, 11, 7, 13],
            intangibles=88, touches=82, shot=55,
            extra_attrs={"perimeter_def": 96, "interior_def": 88, "pass_vision": 92, "speed": 90},
            extra_tends={"dish_to_open_man": 95},
            badges={"Clamps": 4, "Dimer": 4, "BreakStarter": 4}
        ))
        # 赛斯·库里 Seth Curry (Slot 11, Face 2860)
        writes.append(make_player_entry(
            name=roster[11][0], slot=11, face=roster[11][1], initiator=0,
            play_types=[15, 12, 14, 0],
            intangibles=86, touches=78, shot=84,
            extra_attrs={"three_point": 94},
            badges={"CatchAndShoot": 4, "CornerSpecialist": 4, "Sniper": 4}
        ))
        # 尼古拉斯·克拉克斯顿 Nicolas Claxton (Slot 7, Face 7850)
        writes.append(make_player_entry(
            name=roster[7][0], slot=7, face=roster[7][1], initiator=0,
            play_types=[7, 11, 0, 0],
            intangibles=88, touches=68, shot=68,
            extra_attrs={"block": 94, "interior_def": 88, "lateral_quick": 84},
            badges={"RimProtector": 4, "Intimidator": 4}
        ))

    # 22: TOR (Toronto Raptors)
    elif team_id == 22:
        # 斯科蒂·巴恩斯 Scottie Barnes (Slot 3, Face 8060) - 2022 ROY 年度最佳新秀 -> 2026 全能前锋
        writes.append(make_player_entry(
            name=roster[3][0], slot=3, face=roster[3][1], initiator=1,
            play_types=[4, 1, 8, 11],
            intangibles=95, touches=92, shot=88,
            extra_attrs={"pass_vision": 92, "strength": 90, "perimeter_def": 90, "driving_layup": 90},
            extra_tends={"drive": 92, "dish_to_open_man": 90},
            badges={"Dimer": 4, "Clamps": 4, "BackdownPunisher": 3, "FearlessFinisher": 3}
        ))
        # 弗雷德·范弗利特 Fred VanVleet (Slot 1, Face 7288)
        writes.append(make_player_entry(
            name=roster[1][0], slot=1, face=roster[1][1], initiator=1,
            play_types=[4, 15, 1, 14],
            intangibles=92, touches=90, shot=88,
            extra_attrs={"three_point": 90, "steal": 92, "pass_accuracy": 90},
            badges={"CatchAndShoot": 4, "Sniper": 3, "PickPocket": 3}
        ))
        # OG·阿奴诺比 OG Anunoby (Slot 2, Face 7515)
        writes.append(make_player_entry(
            name=roster[2][0], slot=2, face=roster[2][1], initiator=0,
            play_types=[15, 11, 1, 0],
            intangibles=90, touches=82, shot=84,
            extra_attrs={"perimeter_def": 95, "steal": 92, "three_point": 86},
            badges={"Clamps": 4, "CornerSpecialist": 4}
        ))
        # 加里·特伦特 Gary Trent Jr. (Slot 5, Face 7736)
        writes.append(make_player_entry(
            name=roster[5][0], slot=5, face=roster[5][1], initiator=0,
            play_types=[15, 14, 12, 1],
            intangibles=86, touches=80, shot=85,
            extra_attrs={"three_point": 88, "mid_range": 85}
        ))
        # 克里斯·布歇 Chris Boucher (Slot 4, Face 7590)
        writes.append(make_player_entry(
            name=roster[4][0], slot=4, face=roster[4][1], initiator=0,
            play_types=[15, 7, 0, 0],
            intangibles=84, touches=72, shot=74,
            extra_attrs={"block": 90, "three_point": 80}
        ))

    # ==================== BATCH 02: CENTRAL ====================
    # 1: MIL (Milwaukee Bucks)
    elif team_id == 1:
        # 扬尼斯·阿德托昆博 Giannis Antetokounmpo (Slot 3, Face 2701) - 巅峰希腊怪兽统治力
        writes.append(make_player_entry(
            name=roster[3][0], slot=3, face=roster[3][1], initiator=1,
            play_types=[1, 7, 8, 4],
            intangibles=99, touches=98, shot=96,
            extra_attrs={"driving_layup": 98, "driving_dunk": 98, "standing_dunk": 95, "interior_def": 96, "block": 94, "perimeter_def": 88, "strength": 98, "speed": 88},
            extra_tends={"drive": 99, "attack_strong_on_drive": 99, "post_up": 90, "block_shot": 92, "contest_shot": 95},
            badges={"Posterizer": 4, "LimitlessTakeoff": 4, "FastTwitch": 4, "FearlessFinisher": 4, "Intimidator": 4, "RimProtector": 4, "Clamps": 4, "ChasedownArtist": 4, "BackdownPunisher": 4, "PostDropStepper": 4, "Downhill": 4}
        ))
        # 克里斯·米德尔顿 Khris Middleton (Slot 2, Face 2482)
        writes.append(make_player_entry(
            name=roster[2][0], slot=2, face=roster[2][1], initiator=1,
            play_types=[1, 4, 14, 15],
            intangibles=94, touches=88, shot=90,
            extra_attrs={"mid_range": 94, "three_point": 90},
            badges={"DifficultShots": 4, "Deadeye": 4, "Sniper": 4}
        ))
        # 朱·霍勒迪 Jrue Holiday (Slot 0, Face 1607)
        writes.append(make_player_entry(
            name=roster[0][0], slot=0, face=roster[0][1], initiator=1,
            play_types=[4, 8, 1, 14],
            intangibles=94, touches=86, shot=84,
            extra_attrs={"perimeter_def": 98, "steal": 95, "lateral_quick": 96},
            badges={"Clamps": 4, "Menace": 4, "PickPocket": 4, "Interceptor": 4}
        ))
        # 布鲁克·洛佩兹 Brook Lopez (Slot 4, Face 1516)
        writes.append(make_player_entry(
            name=roster[4][0], slot=4, face=roster[4][1], initiator=0,
            play_types=[15, 7, 0, 0],
            intangibles=90, touches=75, shot=78,
            extra_attrs={"block": 94, "interior_def": 92, "three_point": 82},
            badges={"RimProtector": 4, "Intimidator": 4}
        ))
        # 鲍比·波蒂斯 Bobby Portis Jr. (Slot 6, Face 4454)
        writes.append(make_player_entry(
            name=roster[6][0], slot=6, face=roster[6][1], initiator=0,
            play_types=[15, 8, 7, 0],
            intangibles=86, touches=80, shot=82,
            extra_attrs={"three_point": 84, "mid_range": 84}
        ))

    # 3: CHI (Chicago Bulls)
    elif team_id == 3:
        # 德马尔·德罗赞 DeMar DeRozan (Slot 1, Face 1605) - 2022 MVP 候选 / 绝杀之王 (中投之神)
        writes.append(make_player_entry(
            name=roster[1][0], slot=1, face=roster[1][1], initiator=1,
            play_types=[1, 4, 14, 8],
            intangibles=96, touches=95, shot=95,
            extra_attrs={"mid_range": 98, "post_fadeaway": 95, "driving_layup": 94},
            extra_tends={"shot_mid_range": 99, "drive": 94, "post_up": 90},
            badges={"DifficultShots": 4, "Deadeye": 4, "ClutchShooter": 4, "SpaceCreator": 4, "StopAndPop": 4}
        ))
        # 扎克·拉文 Zach LaVine (Slot 0, Face 4101)
        writes.append(make_player_entry(
            name=roster[0][0], slot=0, face=roster[0][1], initiator=1,
            play_types=[4, 1, 15, 11],
            intangibles=94, touches=92, shot=92,
            extra_attrs={"three_point": 92, "speed": 96, "driving_dunk": 96},
            extra_tends={"shot_three": 92, "drive": 94},
            badges={"Posterizer": 4, "LimitlessTakeoff": 4, "Sniper": 4, "QuickFirstStep": 4}
        ))
        # 尼古拉·武切维奇 Nikola Vucevic (Slot 3, Face 2144)
        writes.append(make_player_entry(
            name=roster[3][0], slot=3, face=roster[3][1], initiator=0,
            play_types=[8, 15, 7, 0],
            intangibles=88, touches=84, shot=85,
            extra_attrs={"mid_range": 88, "three_point": 82}
        ))
        # 科比·怀特 Coby White (Slot 4, Face 7826)
        writes.append(make_player_entry(
            name=roster[4][0], slot=4, face=roster[4][1], initiator=1,
            play_types=[4, 15, 1, 14],
            intangibles=90, touches=84, shot=86,
            extra_attrs={"three_point": 88, "speed": 90, "driving_layup": 88},
            badges={"Sniper": 3, "QuickFirstStep": 3}
        ))
        # 帕特里克·威廉姆斯 Patrick Williams (Slot 2, Face 7996)
        writes.append(make_player_entry(
            name=roster[2][0], slot=2, face=roster[2][1], initiator=0,
            play_types=[15, 11, 0, 0],
            intangibles=84, touches=72, shot=72,
            extra_attrs={"perimeter_def": 86, "three_point": 82}
        ))

    # 4: CLE (Cleveland Cavaliers)
    elif team_id == 4:
        # 多诺万·米切尔 Donovan Mitchell (Slot 13, Face 7510) - 71 分爆炸得分手
        writes.append(make_player_entry(
            name=roster[13][0], slot=13, face=roster[13][1], initiator=1,
            play_types=[4, 1, 15, 11],
            intangibles=98, touches=96, shot=96,
            extra_attrs={"three_point": 94, "driving_layup": 96, "speed": 95, "ball_control": 94},
            extra_tends={"shot_three": 95, "drive": 95},
            badges={"Chef": 4, "Sniper": 4, "DifficultShots": 4, "QuickFirstStep": 4, "FearlessFinisher": 4, "CircusThrees": 4}
        ))
        # 达里厄斯·加兰 Darius Garland (Slot 0, Face 7824)
        writes.append(make_player_entry(
            name=roster[0][0], slot=0, face=roster[0][1], initiator=1,
            play_types=[4, 15, 1, 14],
            intangibles=94, touches=92, shot=88,
            extra_attrs={"pass_accuracy": 94, "pass_vision": 94, "three_point": 90},
            badges={"Dimer": 4, "Sniper": 3, "TearDropper": 4}
        ))
        # 埃文·莫布利 Evan Mobley (Slot 3, Face 8052)
        writes.append(make_player_entry(
            name=roster[3][0], slot=3, face=roster[3][1], initiator=1,
            play_types=[7, 9, 8, 11],
            intangibles=94, touches=84, shot=82,
            extra_attrs={"interior_def": 95, "perimeter_def": 90, "block": 94, "lateral_quick": 86},
            badges={"RimProtector": 4, "Intimidator": 4, "Clamps": 4, "ChasedownArtist": 4}
        ))
        # 贾勒特·阿伦 Jarrett Allen (Slot 2, Face 7517)
        writes.append(make_player_entry(
            name=roster[2][0], slot=2, face=roster[2][1], initiator=0,
            play_types=[7, 11, 0, 0],
            intangibles=90, touches=78, shot=76,
            extra_attrs={"interior_def": 92, "block": 90, "strength": 90},
            badges={"RimProtector": 4, "Intimidator": 4}
        ))
        # 卡里斯·勒韦尔 Caris LeVert (Slot 12, Face 7233)
        writes.append(make_player_entry(
            name=roster[12][0], slot=12, face=roster[12][1], initiator=1,
            play_types=[4, 1, 14, 15],
            intangibles=86, touches=80, shot=82,
            extra_attrs={"driving_layup": 88, "mid_range": 85}
        ))

    # 20: IND (Indiana Pacers)
    elif team_id == 20:
        # 泰雷斯·哈利伯顿 Tyrese Haliburton (Slot 2, Face 8001) - 2026 控球之神！
        writes.append(make_player_entry(
            name=roster[2][0], slot=2, face=roster[2][1], initiator=1,
            play_types=[4, 15, 1, 12],
            intangibles=98, touches=96, shot=85,
            extra_attrs={"pass_accuracy": 99, "pass_vision": 99, "pass_iq": 99, "three_point": 94, "ball_control": 94},
            extra_tends={"dish_to_open_man": 99, "spot_up_three": 95, "shot_three": 92},
            badges={"Dimer": 4, "FloorGeneral": 4, "NeedleThreader": 4, "BulletPasser": 4, "Sniper": 4, "BailOut": 4, "QuickFirstStep": 4, "SpecialDelivery": 4}
        ))
        # 帕斯卡尔·西亚卡姆 Pascal Siakam (Slot 3, Face 7236)
        writes.append(make_player_entry(
            name=roster[3][0], slot=3, face=roster[3][1], initiator=1,
            play_types=[1, 8, 4, 11],
            intangibles=96, touches=92, shot=92,
            extra_attrs={"mid_range": 88, "driving_layup": 90, "interior_def": 85, "strength": 86},
            badges={"DifficultShots": 3, "FearlessFinisher": 4, "FastTwitch": 4}
        ))
        # 迈尔斯·特纳 Myles Turner (Slot 0, Face 4474)
        writes.append(make_player_entry(
            name=roster[0][0], slot=0, face=roster[0][1], initiator=0,
            play_types=[15, 7, 0, 0],
            intangibles=90, touches=80, shot=80,
            extra_attrs={"block": 96, "interior_def": 88, "three_point": 82},
            badges={"RimProtector": 4, "Intimidator": 4}
        ))
        # 巴迪·希尔德 Buddy Hield (Slot 9, Face 7204)
        writes.append(make_player_entry(
            name=roster[9][0], slot=9, face=roster[9][1], initiator=0,
            play_types=[15, 12, 14, 0],
            intangibles=88, touches=82, shot=86,
            extra_attrs={"three_point": 91},
            extra_tends={"spot_up_three": 95},
            badges={"CatchAndShoot": 4, "CornerSpecialist": 4, "Sniper": 4}
        ))
        # 亚历克斯·卡鲁索 Alex Caruso (Slot 5, Face 7570)
        writes.append(make_player_entry(
            name=roster[5][0], slot=5, face=roster[5][1], initiator=1,
            play_types=[4, 11, 15, 0],
            intangibles=90, touches=75, shot=70,
            extra_attrs={"perimeter_def": 96, "steal": 95, "lateral_quick": 94},
            badges={"Clamps": 4, "Menace": 4, "PickPocket": 4}
        ))

    # 21: DET (Detroit Pistons)
    elif team_id == 21:
        # 凯德·坎宁安 Cade Cunningham (Slot 0, Face 8050)
        writes.append(make_player_entry(
            name=roster[0][0], slot=0, face=roster[0][1], initiator=1,
            play_types=[4, 1, 14, 15],
            intangibles=96, touches=95, shot=92,
            extra_attrs={"ball_control": 94, "pass_accuracy": 94, "mid_range": 90, "driving_layup": 90},
            extra_tends={"drive": 92, "dish_to_open_man": 92},
            badges={"Dimer": 4, "HandlesForDays": 4, "QuickFirstStep": 4, "DifficultShots": 3}
        ))
        # 萨迪克·贝 Saddiq Bey (Slot 2, Face 8010)
        writes.append(make_player_entry(
            name=roster[2][0], slot=2, face=roster[2][1], initiator=0,
            play_types=[15, 11, 1, 0],
            intangibles=86, touches=82, shot=85,
            extra_attrs={"three_point": 86, "strength": 84}
        ))
        # 以赛亚·斯图尔特 Isaiah Stewart (Slot 6, Face 8008)
        writes.append(make_player_entry(
            name=roster[6][0], slot=6, face=roster[6][1], initiator=0,
            play_types=[7, 15, 8, 0],
            intangibles=86, touches=76, shot=76,
            extra_attrs={"interior_def": 88, "strength": 92, "three_point": 78}
        ))
        # 克里斯·杜阿尔特 Chris Duarte (Slot 12, Face 9905)
        writes.append(make_player_entry(
            name=roster[12][0], slot=12, face=roster[12][1], initiator=0,
            play_types=[15, 14, 4, 12],
            intangibles=85, touches=80, shot=82,
            extra_attrs={"three_point": 85, "mid_range": 85}
        ))
        # 凯利·奥利尼克 Kelly Olynyk (Slot 3, Face 2699)
        writes.append(make_player_entry(
            name=roster[3][0], slot=3, face=roster[3][1], initiator=0,
            play_types=[15, 7, 13, 8],
            intangibles=84, touches=76, shot=78,
            extra_attrs={"three_point": 82, "pass_accuracy": 82}
        ))

    # ==================== BATCH 03: SOUTHEAST ====================
    # 2: WAS (Washington Wizards)
    elif team_id == 2:
        # 布拉德利·比尔 Bradley Beal (Slot 0, Face 2446) - 30 分得分机器
        writes.append(make_player_entry(
            name=roster[0][0], slot=0, face=roster[0][1], initiator=1,
            play_types=[4, 1, 14, 15],
            intangibles=96, touches=94, shot=94,
            extra_attrs={"mid_range": 94, "three_point": 90, "driving_layup": 92},
            extra_tends={"shot_mid_range": 92, "drive": 92},
            badges={"DifficultShots": 4, "Sniper": 4, "QuickFirstStep": 4, "Deadeye": 3}
        ))
        # 克里斯塔普斯·波尔津吉斯 Kristaps Porzingis (Slot 13, Face 4455)
        writes.append(make_player_entry(
            name=roster[13][0], slot=13, face=roster[13][1], initiator=0,
            play_types=[15, 8, 7, 14],
            intangibles=94, touches=90, shot=90,
            extra_attrs={"three_point": 88, "block": 92, "interior_def": 88},
            badges={"RimProtector": 4, "CatchAndShoot": 4, "Intimidator": 3}
        ))
        # 凯尔·库兹马 Kyle Kuzma (Slot 6, Face 7535)
        writes.append(make_player_entry(
            name=roster[6][0], slot=6, face=roster[6][1], initiator=1,
            play_types=[1, 4, 15, 11],
            intangibles=90, touches=86, shot=88,
            extra_attrs={"three_point": 84, "mid_range": 86, "driving_layup": 86}
        ))
        # 波普 Kentavious Caldwell-Pope (Slot 5, Face 2694)
        writes.append(make_player_entry(
            name=roster[5][0], slot=5, face=roster[5][1], initiator=0,
            play_types=[15, 11, 0, 0],
            intangibles=88, touches=76, shot=78,
            extra_attrs={"three_point": 86, "perimeter_def": 88},
            badges={"Clamps": 3, "CornerSpecialist": 3}
        ))
        # 德尼·阿夫迪亚 Deni Avdija (Slot 1, Face 7998)
        writes.append(make_player_entry(
            name=roster[1][0], slot=1, face=roster[1][1], initiator=1,
            play_types=[4, 11, 15, 0],
            intangibles=88, touches=78, shot=76,
            extra_attrs={"perimeter_def": 88, "pass_vision": 85, "speed": 85}
        ))

    # 9: ATL (Atlanta Hawks)
    elif team_id == 9:
        # 特雷·杨 Trae Young (Slot 0, Face 7706) - 2022 得分总榜+助攻总榜双冠王
        writes.append(make_player_entry(
            name=roster[0][0], slot=0, face=roster[0][1], initiator=1,
            play_types=[4, 1, 15, 0],
            intangibles=96, touches=96, shot=94,
            extra_attrs={"three_point": 94, "pass_accuracy": 98, "pass_vision": 98, "ball_control": 96},
            extra_tends={"dish_to_open_man": 98, "shot_three": 96},
            badges={"Dimer": 4, "Sniper": 4, "Chef": 4, "TearDropper": 4, "FloorGeneral": 4, "NeedleThreader": 4}
        ))
        # 德章泰·穆雷 Dejounte Murray (Slot 13, Face 7222)
        writes.append(make_player_entry(
            name=roster[13][0], slot=13, face=roster[13][1], initiator=1,
            play_types=[4, 1, 14, 15],
            intangibles=94, touches=92, shot=90,
            extra_attrs={"mid_range": 90, "steal": 95, "perimeter_def": 92},
            badges={"PickPocket": 4, "Clamps": 3, "DifficultShots": 3}
        ))
        # 克林特·卡佩拉 Clint Capela (Slot 4, Face 4115)
        writes.append(make_player_entry(
            name=roster[4][0], slot=4, face=roster[4][1], initiator=0,
            play_types=[7, 11, 0, 0],
            intangibles=88, touches=72, shot=70,
            extra_attrs={"interior_def": 90, "block": 92},
            badges={"RimProtector": 4, "Intimidator": 4}
        ))
        # 博格丹·博格达诺维奇 Bogdan Bogdanovic (Slot 1, Face 4043)
        writes.append(make_player_entry(
            name=roster[1][0], slot=1, face=roster[1][1], initiator=1,
            play_types=[15, 4, 12, 14],
            intangibles=88, touches=82, shot=85,
            extra_attrs={"three_point": 90, "mid_range": 88},
            badges={"CatchAndShoot": 4, "Sniper": 3}
        ))
        # 约翰·科林斯 John Collins (Slot 3, Face 7513)
        writes.append(make_player_entry(
            name=roster[3][0], slot=3, face=roster[3][1], initiator=0,
            play_types=[7, 11, 15, 8],
            intangibles=86, touches=78, shot=80,
            extra_attrs={"three_point": 80, "interior_def": 82}
        ))

    # 10: MIA (Miami Heat)
    elif team_id == 10:
        # 吉米·巴特勒 Jimmy Butler (Slot 1, Face 2165) - 2022 东决天神下凡 (47分超巨)
        writes.append(make_player_entry(
            name=roster[1][0], slot=1, face=roster[1][1], initiator=1,
            play_types=[1, 4, 8, 14],
            intangibles=99, touches=95, shot=92,
            extra_attrs={"mid_range": 94, "perimeter_def": 97, "steal": 95, "strength": 88, "stamina": 99, "hustle": 99},
            extra_tends={"on_ball_steal": 95, "contest_shot": 96, "drive": 95, "post_up": 88},
            badges={"Clamps": 4, "Menace": 4, "PickPocket": 4, "FearlessFinisher": 4, "ClutchShooter": 4, "DifficultShots": 4}
        ))
        # 巴姆·阿德巴约 Bam Adebayo (Slot 3, Face 7519)
        writes.append(make_player_entry(
            name=roster[3][0], slot=3, face=roster[3][1], initiator=1,
            play_types=[13, 7, 8, 14],
            intangibles=96, touches=88, shot=84,
            extra_attrs={"interior_def": 96, "perimeter_def": 90, "lateral_quick": 88, "pass_accuracy": 88},
            badges={"RimProtector": 4, "Intimidator": 4, "Clamps": 4, "Dimer": 3}
        ))
        # 泰勒·希罗 Tyler Herro (Slot 4, Face 7832)
        writes.append(make_player_entry(
            name=roster[4][0], slot=4, face=roster[4][1], initiator=1,
            play_types=[15, 4, 12, 14],
            intangibles=92, touches=88, shot=92,
            extra_attrs={"three_point": 90, "mid_range": 90, "driving_layup": 88},
            badges={"CatchAndShoot": 4, "Sniper": 4, "DifficultShots": 3}
        ))
        # 凯尔·洛瑞 Kyle Lowry (Slot 0, Face 1357)
        writes.append(make_player_entry(
            name=roster[0][0], slot=0, face=roster[0][1], initiator=1,
            play_types=[4, 15, 12, 0],
            intangibles=90, touches=80, shot=76,
            extra_attrs={"pass_accuracy": 90, "three_point": 84}
        ))
        # 马克斯·斯特鲁斯 Max Strus (Slot 7, Face 7920)
        writes.append(make_player_entry(
            name=roster[7][0], slot=7, face=roster[7][1], initiator=0,
            play_types=[15, 12, 11, 0],
            intangibles=86, touches=76, shot=82,
            extra_attrs={"three_point": 88},
            badges={"CatchAndShoot": 4, "CornerSpecialist": 3}
        ))

    # 16: ORL (Orlando Magic)
    elif team_id == 16:
        # 弗朗茨·瓦格纳 Franz Wagner (Slot 9, Face 8062) - 2026 世界杯冠军核心 / 全明星前锋
        writes.append(make_player_entry(
            name=roster[9][0], slot=9, face=roster[9][1], initiator=1,
            play_types=[4, 11, 15, 1],
            intangibles=96, touches=92, shot=90,
            extra_attrs={"driving_layup": 94, "three_point": 88, "pass_accuracy": 90},
            extra_tends={"drive": 94, "dish_to_open_man": 90},
            badges={"FearlessFinisher": 4, "Sniper": 4, "Dimer": 3}
        ))
        # 杰伦·萨格斯 Jalen Suggs (Slot 0, Face 8051)
        writes.append(make_player_entry(
            name=roster[0][0], slot=0, face=roster[0][1], initiator=1,
            play_types=[4, 11, 15, 0],
            intangibles=92, touches=82, shot=80,
            extra_attrs={"perimeter_def": 94, "lateral_quick": 92, "steal": 90},
            badges={"Clamps": 4, "Menace": 4}
        ))
        # 温德尔·卡特 Wendell Carter Jr. (Slot 4, Face 7704)
        writes.append(make_player_entry(
            name=roster[4][0], slot=4, face=roster[4][1], initiator=0,
            play_types=[15, 7, 8, 13],
            intangibles=88, touches=80, shot=80,
            extra_attrs={"three_point": 82, "interior_def": 86}
        ))
        # 科尔·安东尼 Cole Anthony (Slot 7, Face 7951)
        writes.append(make_player_entry(
            name=roster[7][0], slot=7, face=roster[7][1], initiator=1,
            play_types=[4, 1, 15, 0],
            intangibles=88, touches=84, shot=86,
            extra_attrs={"three_point": 86, "driving_layup": 86}
        ))
        # 马克尔·富尔茨 Markelle Fultz (Slot 1, Face 7500)
        writes.append(make_player_entry(
            name=roster[1][0], slot=1, face=roster[1][1], initiator=1,
            play_types=[4, 14, 0, 0],
            intangibles=86, touches=80, shot=76,
            extra_attrs={"mid_range": 85, "pass_accuracy": 86}
        ))

    # 31: CHA (Charlotte Hornets)
    elif team_id == 31:
        # 拉梅洛·鲍尔 LaMelo Ball (Slot 0, Face 7953) - 20 岁全明星天才指挥官
        writes.append(make_player_entry(
            name=roster[0][0], slot=0, face=roster[0][1], initiator=1,
            play_types=[4, 15, 1, 11],
            intangibles=96, touches=96, shot=90,
            extra_attrs={"pass_accuracy": 98, "pass_vision": 98, "three_point": 92, "ball_control": 94},
            extra_tends={"dish_to_open_man": 98, "shot_three": 94},
            badges={"Dimer": 4, "FloorGeneral": 4, "SpecialDelivery": 4, "BulletPasser": 4, "Sniper": 4}
        ))
        # 迈尔斯·布里奇斯 Miles Bridges (Slot 4, Face 7711)
        writes.append(make_player_entry(
            name=roster[4][0], slot=4, face=roster[4][1], initiator=1,
            play_types=[11, 1, 15, 7],
            intangibles=92, touches=88, shot=90,
            extra_attrs={"driving_layup": 92, "three_point": 85, "speed": 88},
            badges={"Posterizer": 4}
        ))
        # 特里·罗齐尔 Terry Rozier III (Slot 1, Face 4460)
        writes.append(make_player_entry(
            name=roster[1][0], slot=1, face=roster[1][1], initiator=1,
            play_types=[4, 15, 1, 14],
            intangibles=90, touches=88, shot=90,
            extra_attrs={"three_point": 88, "mid_range": 86}
        ))
        # 戈登·海沃德 Gordon Hayward (Slot 2, Face 1809)
        writes.append(make_player_entry(
            name=roster[2][0], slot=2, face=roster[2][1], initiator=0,
            play_types=[14, 15, 4, 12],
            intangibles=88, touches=80, shot=82,
            extra_attrs={"mid_range": 88, "three_point": 84}
        ))
        # P.J. 华盛顿 P.J. Washington (Slot 3, Face 7831)
        writes.append(make_player_entry(
            name=roster[3][0], slot=3, face=roster[3][1], initiator=0,
            play_types=[15, 11, 7, 0],
            intangibles=86, touches=78, shot=80,
            extra_attrs={"three_point": 84, "interior_def": 82}
        ))

    # ==================== BATCH 04: NORTHWEST ====================
    # 12: UTA (Utah Jazz)
    elif team_id == 12:
        # 劳里·马尔卡宁 Lauri Markkanen (Slot 12, Face 7508) - 2023 MIP & 2024 全明星 7 尺高炮台！
        writes.append(make_player_entry(
            name=roster[12][0], slot=12, face=roster[12][1], initiator=0,
            play_types=[15, 11, 7, 8],
            intangibles=96, touches=94, shot=94,
            extra_attrs={"three_point": 92, "mid_range": 88, "driving_layup": 88, "strength": 84},
            extra_tends={"spot_up_three": 96, "shot_three": 94},
            badges={"CatchAndShoot": 4, "CornerSpecialist": 4, "Sniper": 4, "Deadeye": 3}
        ))
        # 科林·塞克斯顿 Collin Sexton (Slot 8, Face 7707)
        writes.append(make_player_entry(
            name=roster[8][0], slot=8, face=roster[8][1], initiator=1,
            play_types=[4, 1, 11, 14],
            intangibles=90, touches=88, shot=90,
            extra_attrs={"speed": 94, "driving_layup": 90, "three_point": 84},
            badges={"Downhill": 4, "FearlessFinisher": 3}
        ))
        # 乔丹·克拉克森 Jordan Clarkson (Slot 2, Face 4175)
        writes.append(make_player_entry(
            name=roster[2][0], slot=2, face=roster[2][1], initiator=1,
            play_types=[1, 4, 15, 14],
            intangibles=90, touches=88, shot=92,
            extra_attrs={"three_point": 86, "driving_layup": 88, "mid_range": 88},
            badges={"DifficultShots": 3, "Sniper": 3}
        ))
        # 迈克·康利 Mike Conley (Slot 0, Face 1413)
        writes.append(make_player_entry(
            name=roster[0][0], slot=0, face=roster[0][1], initiator=1,
            play_types=[4, 15, 14, 0],
            intangibles=90, touches=80, shot=76,
            extra_attrs={"pass_accuracy": 92, "pass_vision": 90, "three_point": 86},
            badges={"Dimer": 3, "FloorGeneral": 3}
        ))
        # 贾里德·范德比尔特 Jarred Vanderbilt (Slot 13, Face 7740)
        writes.append(make_player_entry(
            name=roster[13][0], slot=13, face=roster[13][1], initiator=0,
            play_types=[7, 11, 0, 0],
            intangibles=86, touches=65, shot=60,
            extra_attrs={"perimeter_def": 88, "interior_def": 86, "hustle": 96},
            badges={"Clamps": 3, "Hustler": 4}
        ))

    # 19: DEN (Denver Nuggets)
    elif team_id == 19:
        # 尼古拉·约基奇 Nikola Jokic (Slot 3, Face 4170) - 2022 连庄常规赛 MVP / 历史级组织中锋
        writes.append(make_player_entry(
            name=roster[3][0], slot=3, face=roster[3][1], initiator=1,
            play_types=[8, 9, 7, 13], # Post Low, Post High, PnR Roll, Handoff Passer
            intangibles=99, touches=98, shot=92,
            extra_attrs={"pass_accuracy": 99, "pass_vision": 99, "pass_iq": 99, "mid_range": 96, "shot_close": 98, "post_hook": 96, "post_fadeaway": 95, "post_moves": 98, "strength": 94},
            extra_tends={"dish_to_open_man": 99, "post_up": 95},
            badges={"Dimer": 4, "FloorGeneral": 4, "PostPlaymaker": 4, "BreakStarter": 4, "BulletPasser": 4, "NeedleThreader": 4, "PostDropStepper": 4, "BackdownPunisher": 4, "DreamShake": 4, "HookSpecialist": 4, "Unpluckable": 4, "DifficultShots": 4, "ProTouch": 4}
        ))
        # 贾马尔·穆雷 Jamal Murray (Slot 0, Face 7202)
        writes.append(make_player_entry(
            name=roster[0][0], slot=0, face=roster[0][1], initiator=1,
            play_types=[4, 12, 1, 14],
            intangibles=96, touches=92, shot=94,
            extra_attrs={"mid_range": 94, "three_point": 90, "driving_layup": 92},
            badges={"DifficultShots": 4, "Deadeye": 4, "Sniper": 4, "ClutchShooter": 4}
        ))
        # 小迈克尔·波特 Michael Porter Jr. (Slot 1, Face 7713)
        writes.append(make_player_entry(
            name=roster[1][0], slot=1, face=roster[1][1], initiator=0,
            play_types=[15, 11, 14, 0],
            intangibles=90, touches=84, shot=90,
            extra_attrs={"three_point": 92, "mid_range": 88},
            badges={"CatchAndShoot": 4, "Sniper": 4}
        ))
        # 阿隆·戈登 Aaron Gordon (Slot 2, Face 4095)
        writes.append(make_player_entry(
            name=roster[2][0], slot=2, face=roster[2][1], initiator=0,
            play_types=[11, 7, 1, 8],
            intangibles=92, touches=80, shot=80,
            extra_attrs={"perimeter_def": 88, "interior_def": 86, "strength": 90},
            badges={"Posterizer": 4, "Clamps": 3, "Intimidator": 3}
        ))
        # 蒙特·莫里斯 Monte Morris (Slot 4, Face 7545)
        writes.append(make_player_entry(
            name=roster[4][0], slot=4, face=roster[4][1], initiator=1,
            play_types=[4, 14, 15, 0],
            intangibles=86, touches=78, shot=76,
            extra_attrs={"pass_accuracy": 88, "pass_iq": 94}
        ))

    # 24: OKC (Oklahoma City Thunder)
    elif team_id == 24:
        # 谢伊·吉尔杰斯-亚历山大 Shai Gilgeous-Alexander (Slot 0, Face 7710) - 2024-2026 MVP 级大核！
        writes.append(make_player_entry(
            name=roster[0][0], slot=0, face=roster[0][1], initiator=1,
            play_types=[1, 4, 14, 8],
            intangibles=99, touches=98, shot=96,
            extra_attrs={"ball_control": 96, "driving_layup": 98, "mid_range": 96, "perimeter_def": 90, "steal": 94, "lateral_quick": 92},
            extra_tends={"drive": 99, "dish_to_open_man": 90, "on_ball_steal": 92},
            badges={"DifficultShots": 4, "QuickFirstStep": 4, "HandlesForDays": 4, "Clamps": 4, "Interceptor": 4, "FearlessFinisher": 4, "Unpluckable": 4}
        ))
        # 约什·吉迪 Josh Giddey (Slot 6, Face 8064)
        writes.append(make_player_entry(
            name=roster[6][0], slot=6, face=roster[6][1], initiator=1,
            play_types=[4, 9, 11, 1],
            intangibles=90, touches=85, shot=75,
            extra_attrs={"pass_accuracy": 94, "pass_vision": 94, "ball_control": 88},
            badges={"Dimer": 4, "NeedleThreader": 3}
        ))
        # 卢冈茨·多特 Luguentz Dort (Slot 1, Face 7910)
        writes.append(make_player_entry(
            name=roster[1][0], slot=1, face=roster[1][1], initiator=0,
            play_types=[15, 11, 1, 0],
            intangibles=90, touches=76, shot=78,
            extra_attrs={"perimeter_def": 96, "strength": 88, "lateral_quick": 94},
            badges={"Clamps": 4, "Menace": 4, "CornerSpecialist": 3}
        ))
        # 特雷·曼 Tre Mann (Slot 9, Face 8059)
        writes.append(make_player_entry(
            name=roster[9][0], slot=9, face=roster[9][1], initiator=1,
            play_types=[4, 15, 1, 0],
            intangibles=85, touches=80, shot=82,
            extra_attrs={"three_point": 86, "speed": 90}
        ))
        # 达柳斯·贝兹利 Darius Bazley (Slot 3, Face 7842)
        writes.append(make_player_entry(
            name=roster[3][0], slot=3, face=roster[3][1], initiator=0,
            play_types=[11, 7, 15, 0],
            intangibles=84, touches=74, shot=74,
            extra_attrs={"block": 86, "interior_def": 84}
        ))

    # 27: MIN (Minnesota Timberwolves)
    elif team_id == 27:
        # 安东尼·爱德华兹 Anthony Edwards (Slot 1, Face 7954) - 2026 联盟门面球星模板！
        writes.append(make_player_entry(
            name=roster[1][0], slot=1, face=roster[1][1], initiator=1,
            play_types=[1, 4, 15, 11],
            intangibles=98, touches=96, shot=96,
            extra_attrs={"driving_dunk": 98, "vertical": 98, "three_point": 90, "perimeter_def": 92, "strength": 88, "speed": 96, "acceleration": 96},
            extra_tends={"drive": 98, "shot_three": 92, "contest_shot": 90},
            badges={"Posterizer": 4, "LimitlessTakeoff": 4, "QuickFirstStep": 4, "FearlessFinisher": 4, "Clamps": 4, "Sniper": 3}
        ))
        # 卡尔-安东尼·唐斯 Karl-Anthony Towns (Slot 3, Face 4472)
        writes.append(make_player_entry(
            name=roster[3][0], slot=3, face=roster[3][1], initiator=0,
            play_types=[15, 8, 7, 14],
            intangibles=95, touches=90, shot=92,
            extra_attrs={"three_point": 92, "mid_range": 90, "post_moves": 90},
            badges={"CatchAndShoot": 4, "Sniper": 4, "Deadeye": 4}
        ))
        # 鲁迪·戈贝尔 Rudy Gobert (Slot 12, Face 2713) - 4届 DPOY 护筐霸主
        writes.append(make_player_entry(
            name=roster[12][0], slot=12, face=roster[12][1], initiator=0,
            play_types=[7, 11, 0, 0],
            intangibles=95, touches=70, shot=68,
            extra_attrs={"interior_def": 98, "block": 98, "strength": 98, "def_rebound": 96},
            badges={"RimProtector": 4, "Intimidator": 4, "BrickWall": 4, "ReboundChaser": 4}
        ))
        # 迪安吉洛·拉塞尔 D'Angelo Russell (Slot 0, Face 4461)
        writes.append(make_player_entry(
            name=roster[0][0], slot=0, face=roster[0][1], initiator=1,
            play_types=[4, 14, 15, 1],
            intangibles=90, touches=85, shot=85,
            extra_attrs={"pass_accuracy": 90, "three_point": 86}
        ))
        # 杰登·麦克丹尼尔斯 Jaden McDaniels (Slot 2, Face 8017)
        writes.append(make_player_entry(
            name=roster[2][0], slot=2, face=roster[2][1], initiator=0,
            play_types=[15, 11, 0, 0],
            intangibles=92, touches=74, shot=76,
            extra_attrs={"perimeter_def": 95, "lateral_quick": 94, "block": 86},
            badges={"Clamps": 4, "CornerSpecialist": 3}
        ))

    # 28: POR (Portland Trail Blazers)
    elif team_id == 28:
        # 达米安·利拉德 Damian Lillard (Slot 0, Face 2449) - 表时刻历史级超远三分
        writes.append(make_player_entry(
            name=roster[0][0], slot=0, face=roster[0][1], initiator=1,
            play_types=[4, 15, 1, 11],
            intangibles=99, touches=98, shot=98,
            extra_attrs={"three_point": 97, "driving_layup": 94, "pass_accuracy": 92},
            extra_tends={"shot_three": 98, "spot_up_three": 96, "drive": 92},
            badges={"Chef": 4, "LimitlessSpotUp": 4, "ClutchShooter": 4, "Sniper": 4, "StopAndPop": 4, "Deadeye": 4}
        ))
        # 杰拉米·格兰特 Jerami Grant (Slot 12, Face 4105)
        writes.append(make_player_entry(
            name=roster[12][0], slot=12, face=roster[12][1], initiator=1,
            play_types=[1, 15, 4, 11],
            intangibles=92, touches=88, shot=90,
            extra_attrs={"three_point": 88, "perimeter_def": 86, "driving_layup": 88},
            badges={"CornerSpecialist": 3, "DifficultShots": 3}
        ))
        # 优素福·努尔基奇 Jusuf Nurkic (Slot 1, Face 4111)
        writes.append(make_player_entry(
            name=roster[1][0], slot=1, face=roster[1][1], initiator=0,
            play_types=[7, 8, 13, 0],
            intangibles=88, touches=78, shot=78,
            extra_attrs={"strength": 92, "interior_def": 86}
        ))
        # 约什·哈特 Josh Hart (Slot 11, Face 7528)
        writes.append(make_player_entry(
            name=roster[11][0], slot=11, face=roster[11][1], initiator=0,
            play_types=[11, 15, 0, 0],
            intangibles=88, touches=78, shot=78,
            extra_attrs={"hustle": 98, "perimeter_def": 86},
            badges={"Hustler": 4, "Clamps": 3}
        ))
        # 纳西尔·利特尔 Nassir Little (Slot 2, Face 7844)
        writes.append(make_player_entry(
            name=roster[2][0], slot=2, face=roster[2][1], initiator=0,
            play_types=[15, 11, 0, 0],
            intangibles=82, touches=72, shot=74,
            extra_attrs={"perimeter_def": 84, "three_point": 80}
        ))

    # ==================== BATCH 05: PACIFIC ====================
    # 6: LAC (Los Angeles Clippers)
    elif team_id == 6:
        # 科怀·伦纳德 Kawhi Leonard (Slot 2, Face 2143) - 中距离机器人 / 死亡缠绕巨掌
        writes.append(make_player_entry(
            name=roster[2][0], slot=2, face=roster[2][1], initiator=1,
            play_types=[1, 4, 8, 14],
            intangibles=99, touches=96, shot=95,
            extra_attrs={"mid_range": 97, "perimeter_def": 98, "steal": 95, "strength": 92},
            extra_tends={"shot_mid_range": 96, "on_ball_steal": 95, "contest_shot": 96, "post_up": 90},
            badges={"Clamps": 4, "DifficultShots": 4, "Deadeye": 4, "PickPocket": 4, "Intimidator": 4, "Menace": 4}
        ))
        # 保罗·乔治 Paul George (Slot 1, Face 1810)
        writes.append(make_player_entry(
            name=roster[1][0], slot=1, face=roster[1][1], initiator=1,
            play_types=[1, 4, 15, 14],
            intangibles=96, touches=94, shot=94,
            extra_attrs={"three_point": 92, "mid_range": 92, "perimeter_def": 94},
            badges={"Sniper": 4, "Clamps": 4, "DifficultShots": 3, "Deadeye": 3}
        ))
        # 诺曼·鲍威尔 Norman Powell (Slot 13, Face 4456)
        writes.append(make_player_entry(
            name=roster[13][0], slot=13, face=roster[13][1], initiator=1,
            play_types=[4, 15, 1, 11],
            intangibles=90, touches=86, shot=90,
            extra_attrs={"three_point": 88, "driving_layup": 90, "speed": 90},
            badges={"Sniper": 3, "FearlessFinisher": 3}
        ))
        # 雷吉·杰克逊 Reggie Jackson (Slot 0, Face 2156)
        writes.append(make_player_entry(
            name=roster[0][0], slot=0, face=roster[0][1], initiator=1,
            play_types=[4, 1, 15, 14],
            intangibles=88, touches=84, shot=85,
            extra_attrs={"three_point": 85, "mid_range": 86}
        ))
        # 伊维察·祖巴茨 Ivica Zubac (Slot 4, Face 7237)
        writes.append(make_player_entry(
            name=roster[4][0], slot=4, face=roster[4][1], initiator=0,
            play_types=[7, 8, 0, 0],
            intangibles=88, touches=75, shot=75,
            extra_attrs={"interior_def": 90, "block": 88, "strength": 90}
        ))

    # 13: SAC (Sacramento Kings)
    elif team_id == 13:
        # 达龙·福克斯 De'Aaron Fox (Slot 0, Face 7503) - 2023 年度关键球员 (极速中投之王)
        writes.append(make_player_entry(
            name=roster[0][0], slot=0, face=roster[0][1], initiator=1,
            play_types=[4, 1, 14, 11],
            intangibles=98, touches=96, shot=95,
            extra_attrs={"speed": 99, "acceleration": 99, "mid_range": 94, "driving_layup": 96},
            extra_tends={"drive": 98, "shot_mid_range": 92},
            badges={"Downhill": 4, "QuickFirstStep": 4, "ClutchShooter": 4, "TearDropper": 4, "FearlessFinisher": 4}
        ))
        # 多曼塔斯·萨博尼斯 Domantas Sabonis (Slot 11, Face 7212) - 普林斯顿三双轴心
        writes.append(make_player_entry(
            name=roster[11][0], slot=11, face=roster[11][1], initiator=1,
            play_types=[13, 8, 7, 9],
            intangibles=96, touches=94, shot=86,
            extra_attrs={"pass_accuracy": 95, "pass_vision": 95, "interior_def": 86, "strength": 95, "def_rebound": 96},
            extra_tends={"dish_to_open_man": 96, "post_up": 90},
            badges={"PostPlaymaker": 4, "Dimer": 4, "BreakStarter": 4, "ReboundChaser": 4, "BrickWall": 4}
        ))
        # 哈里森·巴恩斯 Harrison Barnes (Slot 1, Face 2450)
        writes.append(make_player_entry(
            name=roster[1][0], slot=1, face=roster[1][1], initiator=0,
            play_types=[15, 8, 14, 0],
            intangibles=88, touches=80, shot=82,
            extra_attrs={"three_point": 86, "mid_range": 85}
        ))
        # 凯文·许尔特 Kevin Huerter (Slot 13, Face 7718)
        writes.append(make_player_entry(
            name=roster[13][0], slot=13, face=roster[13][1], initiator=0,
            play_types=[15, 12, 14, 0],
            intangibles=88, touches=80, shot=86,
            extra_attrs={"three_point": 89},
            badges={"CatchAndShoot": 4, "Sniper": 3}
        ))
        # 戴维恩·米切尔 Davion Mitchell (Slot 4, Face 8056)
        writes.append(make_player_entry(
            name=roster[4][0], slot=4, face=roster[4][1], initiator=1,
            play_types=[4, 1, 0, 0],
            intangibles=86, touches=76, shot=74,
            extra_attrs={"perimeter_def": 94, "lateral_quick": 94},
            badges={"Clamps": 4, "Menace": 4}
        ))

    # 15: LAL (Los Angeles Lakers)
    elif team_id == 15:
        # 勒布朗·詹姆斯 LeBron James (Slot 2, Face 1013) - 2022 30.3分历史级常青得分手 / 全能控场
        writes.append(make_player_entry(
            name=roster[2][0], slot=2, face=roster[2][1], initiator=1,
            play_types=[4, 1, 9, 8],
            intangibles=99, touches=98, shot=96,
            extra_attrs={"pass_accuracy": 98, "pass_vision": 98, "pass_iq": 99, "strength": 94, "driving_layup": 96, "three_point": 86},
            extra_tends={"dish_to_open_man": 98, "drive": 95, "post_up": 90},
            badges={"Dimer": 4, "FloorGeneral": 4, "ChasedownArtist": 4, "BulletPasser": 4, "HandlesForDays": 4, "FearlessFinisher": 4, "QuickFirstStep": 4, "Unpluckable": 4}
        ))
        # 安东尼·戴维斯 Anthony Davis (Slot 3, Face 2444)
        writes.append(make_player_entry(
            name=roster[3][0], slot=3, face=roster[3][1], initiator=1,
            play_types=[8, 7, 14, 1],
            intangibles=98, touches=95, shot=92,
            extra_attrs={"interior_def": 96, "block": 96, "mid_range": 88, "def_rebound": 95},
            badges={"RimProtector": 4, "Intimidator": 4, "ReboundChaser": 4, "FastTwitch": 4}
        ))
        # 拉塞尔·威斯布鲁克 Russell Westbrook (Slot 0, Face 1510)
        writes.append(make_player_entry(
            name=roster[0][0], slot=0, face=roster[0][1], initiator=1,
            play_types=[4, 1, 11, 0],
            intangibles=90, touches=88, shot=84,
            extra_attrs={"speed": 92, "driving_layup": 88}
        ))
        # 奥斯汀·里夫斯 Austin Reaves (Slot 12, Face 7720)
        writes.append(make_player_entry(
            name=roster[12][0], slot=12, face=roster[12][1], initiator=1,
            play_types=[4, 1, 15, 14],
            intangibles=92, touches=82, shot=82,
            extra_attrs={"pass_accuracy": 88, "three_point": 86, "driving_layup": 88},
            badges={"QuickFirstStep": 3, "DifficultShots": 2, "ClutchShooter": 3}
        ))
        # 马利克·蒙克 Malik Monk (Slot 1, Face 7506)
        writes.append(make_player_entry(
            name=roster[1][0], slot=1, face=roster[1][1], initiator=0,
            play_types=[15, 11, 4, 0],
            intangibles=88, touches=82, shot=86,
            extra_attrs={"three_point": 88, "speed": 90}
        ))

    # 26: PHX (Phoenix Suns)
    elif team_id == 26:
        # 德文·布克 Devin Booker (Slot 1, Face 4387) - 2022 64胜太阳得分领袖 / 中距离刺客
        writes.append(make_player_entry(
            name=roster[1][0], slot=1, face=roster[1][1], initiator=1,
            play_types=[1, 4, 14, 15],
            intangibles=98, touches=96, shot=96,
            extra_attrs={"mid_range": 97, "three_point": 90, "driving_layup": 92, "ball_control": 92},
            extra_tends={"shot_mid_range": 96, "shot_three": 90, "drive": 92},
            badges={"DifficultShots": 4, "Sniper": 4, "Deadeye": 4, "StopAndPop": 4, "Blinders": 4, "ClutchShooter": 4}
        ))
        # 克里斯·保罗 Chris Paul (Slot 0, Face 1259) - 控卫之神
        writes.append(make_player_entry(
            name=roster[0][0], slot=0, face=roster[0][1], initiator=1,
            play_types=[4, 14, 1, 15],
            intangibles=98, touches=90, shot=80,
            extra_attrs={"pass_accuracy": 99, "pass_vision": 99, "mid_range": 96, "ball_control": 96},
            badges={"Dimer": 4, "FloorGeneral": 4, "NeedleThreader": 4, "PickPocket": 4}
        ))
        # 德安德烈·艾顿 Deandre Ayton (Slot 4, Face 7700)
        writes.append(make_player_entry(
            name=roster[4][0], slot=4, face=roster[4][1], initiator=0,
            play_types=[7, 8, 14, 0],
            intangibles=90, touches=84, shot=84,
            extra_attrs={"mid_range": 88, "interior_def": 88}
        ))
        # 米卡尔·布里奇斯 Mikal Bridges (Slot 2, Face 7709)
        writes.append(make_player_entry(
            name=roster[2][0], slot=2, face=roster[2][1], initiator=0,
            play_types=[15, 11, 14, 1],
            intangibles=92, touches=82, shot=84,
            extra_attrs={"perimeter_def": 95, "three_point": 86},
            badges={"Clamps": 4, "CornerSpecialist": 4}
        ))
        # 卡梅隆·约翰逊 Cameron Johnson (Slot 5, Face 7830)
        writes.append(make_player_entry(
            name=roster[5][0], slot=5, face=roster[5][1], initiator=0,
            play_types=[15, 12, 0, 0],
            intangibles=88, touches=78, shot=85,
            extra_attrs={"three_point": 90},
            badges={"CatchAndShoot": 4, "Sniper": 3}
        ))

    # 29: GSW (Golden State Warriors)
    elif team_id == 29:
        # 斯蒂芬·库里 Stephen Curry (Slot 0, Face 1612) - 2022 FMVP 增肌与跑位终极重塑！
        writes.append(make_player_entry(
            name=roster[0][0], slot=0, face=roster[0][1], initiator=1,
            play_types=[11, 12, 15, 4], # Cutter, Handoff, 3PT, PnR Handler
            intangibles=99, touches=98, shot=98,
            extra_attrs={
                "strength": 75,           # 彻底推翻 2K 默认力量 54 的荒谬偏见，还原 2022 核心增肌
                "stamina": 99,            # 历史最强心肺耐力
                "three_point": 99,        # 历史第一射手
                "mid_range": 94,          # 高效干拔中投
                "driving_layup": 94,      # 顶级篮下终结
                "ball_control": 97,       # 顶尖运球变向
                "pass_accuracy": 92,
                "pass_vision": 92,
                "perimeter_def": 80,      # 总决赛主防外线后卫表现
                "steal": 88,
                "lateral_quick": 82,
                "hustle": 96
            },
            extra_tends={
                "spot_up_three": 99,
                "shot_three": 99,
                "dish_to_open_man": 90,   # 引发 35 尺包夹后迅速分球短顺下
                "drive": 88,
                "contest_shot": 80,
                "on_ball_steal": 85
            },
            badges={
                "Chef": 4, "CircusThrees": 4, "CatchAndShoot": 4, "Deadeye": 4,
                "LimitlessSpotUp": 4, "Sniper": 4, "StopAndPop": 4, "Blinders": 4,
                "GreenMachine": 4, "ClutchShooter": 4, "SlipperyOffball": 4,
                "HandlesForDays": 4, "QuickFirstStep": 4, "Unpluckable": 4,
                "TearDropper": 4, "FearlessFinisher": 4, "Dimer": 3, "Clamps": 3, "PickPocket": 3
            }
        ))
        # 克莱·汤普森 Klay Thompson (Slot 1, Face 2137)
        writes.append(make_player_entry(
            name=roster[1][0], slot=1, face=roster[1][1], initiator=0,
            play_types=[15, 11, 14, 12],
            intangibles=92, touches=85, shot=90,
            extra_attrs={"three_point": 92, "perimeter_def": 82},
            badges={"CatchAndShoot": 4, "CornerSpecialist": 4, "Sniper": 3}
        ))
        # 德雷蒙德·格林 Draymond Green (Slot 3, Face 2478) - 勇士传切策应与防守核心
        writes.append(make_player_entry(
            name=roster[3][0], slot=3, face=roster[3][1], initiator=1,
            play_types=[13, 7, 0, 0],
            intangibles=95, touches=80, shot=50,
            extra_attrs={"pass_accuracy": 94, "pass_vision": 92, "interior_def": 94, "perimeter_def": 88, "strength": 90},
            extra_tends={"dish_to_open_man": 96, "block_shot": 80, "contest_shot": 95},
            badges={"Dimer": 4, "FloorGeneral": 4, "BrickWall": 4, "DefensiveLeader": 4, "Intimidator": 4}
        ))
        # 安德鲁·维金斯 Andrew Wiggins (Slot 2, Face 4091)
        writes.append(make_player_entry(
            name=roster[2][0], slot=2, face=roster[2][1], initiator=0,
            play_types=[15, 11, 1, 4],
            intangibles=90, touches=82, shot=84,
            extra_attrs={"perimeter_def": 90, "lateral_quick": 88, "driving_layup": 86},
            badges={"Clamps": 4, "Intimidator": 3, "CatchAndShoot": 3}
        ))
        # 乔丹·普尔 Jordan Poole (Slot 8, Face 7847)
        writes.append(make_player_entry(
            name=roster[8][0], slot=8, face=roster[8][1], initiator=1,
            play_types=[4, 1, 15, 12],
            intangibles=90, touches=86, shot=90,
            extra_attrs={"three_point": 88, "ball_control": 88, "driving_layup": 88},
            badges={"Chef": 2, "QuickFirstStep": 3, "DifficultShots": 3}
        ))

    # ==================== BATCH 06: SOUTHWEST ====================
    # 8: MEM (Memphis Grizzlies)
    elif team_id == 8:
        # 贾·莫兰特 Ja Morant (Slot 0, Face 7821) - 2022 MIP / 最佳二阵 (暴力美学突破之神)
        writes.append(make_player_entry(
            name=roster[0][0], slot=0, face=roster[0][1], initiator=1,
            play_types=[4, 1, 11, 0],
            intangibles=98, touches=98, shot=96,
            extra_attrs={"speed": 99, "acceleration": 99, "vertical": 99, "driving_layup": 98, "driving_dunk": 96},
            extra_tends={"drive": 99, "attack_strong_on_drive": 99, "dish_to_open_man": 90},
            badges={"Posterizer": 4, "LimitlessTakeoff": 4, "QuickFirstStep": 4, "Downhill": 4, "TearDropper": 4, "FearlessFinisher": 4, "FastTwitch": 4}
        ))
        # 小贾伦·杰克逊 Jaren Jackson Jr (Slot 3, Face 7703) - DPOY 盖帽王
        writes.append(make_player_entry(
            name=roster[3][0], slot=3, face=roster[3][1], initiator=0,
            play_types=[15, 7, 8, 0],
            intangibles=95, touches=86, shot=86,
            extra_attrs={"block": 99, "interior_def": 95, "three_point": 84},
            extra_tends={"block_shot": 99, "contest_shot": 96},
            badges={"RimProtector": 4, "Intimidator": 4, "ChasedownArtist": 4, "Clamps": 3}
        ))
        # 戴斯蒙德·贝恩 Desmond Bane (Slot 6, Face 8019)
        writes.append(make_player_entry(
            name=roster[6][0], slot=6, face=roster[6][1], initiator=1,
            play_types=[15, 4, 1, 12],
            intangibles=94, touches=88, shot=92,
            extra_attrs={"three_point": 92, "strength": 82, "driving_layup": 88},
            badges={"CatchAndShoot": 4, "CornerSpecialist": 4, "Sniper": 4}
        ))
        # 狄龙·布鲁克斯 Dillon Brooks (Slot 1, Face 7542)
        writes.append(make_player_entry(
            name=roster[1][0], slot=1, face=roster[1][1], initiator=0,
            play_types=[1, 15, 0, 0],
            intangibles=88, touches=80, shot=82,
            extra_attrs={"perimeter_def": 92},
            badges={"Clamps": 4, "Menace": 4}
        ))
        # 史蒂文·亚当斯 Steven Adams (Slot 4, Face 2698)
        writes.append(make_player_entry(
            name=roster[4][0], slot=4, face=roster[4][1], initiator=0,
            play_types=[7, 0, 0, 0],
            intangibles=90, touches=68, shot=55,
            extra_attrs={"strength": 99, "hustle": 96},
            badges={"BrickWall": 4}
        ))

    # 11: NOP (New Orleans Pelicans)
    elif team_id == 11:
        # 锡安·威廉姆森 Zion Williamson (Slot 2, Face 7820) - 禁区 60%+ 命中率不可阻挡霸主
        writes.append(make_player_entry(
            name=roster[2][0], slot=2, face=roster[2][1], initiator=1,
            play_types=[1, 4, 8, 11],
            intangibles=98, touches=96, shot=96,
            extra_attrs={"driving_layup": 99, "strength": 99, "vertical": 96, "speed": 88},
            extra_tends={"drive": 99, "post_up": 90, "attack_strong_on_drive": 99},
            badges={"BackdownPunisher": 4, "Posterizer": 4, "FearlessFinisher": 4, "FastTwitch": 4, "Downhill": 4}
        ))
        # 布兰登·英格拉姆 Brandon Ingram (Slot 1, Face 7201)
        writes.append(make_player_entry(
            name=roster[1][0], slot=1, face=roster[1][1], initiator=1,
            play_types=[1, 4, 14, 15],
            intangibles=96, touches=94, shot=94,
            extra_attrs={"mid_range": 96, "driving_layup": 92, "pass_accuracy": 90},
            badges={"DifficultShots": 4, "Deadeye": 4, "Sniper": 4}
        ))
        # C.J. 麦科勒姆 C.J. McCollum (Slot 12, Face 2696)
        writes.append(make_player_entry(
            name=roster[12][0], slot=12, face=roster[12][1], initiator=1,
            play_types=[4, 1, 15, 14],
            intangibles=94, touches=90, shot=92,
            extra_attrs={"three_point": 90, "mid_range": 90, "ball_control": 90},
            badges={"Sniper": 4, "DifficultShots": 3}
        ))
        # 约纳斯·瓦兰丘纳斯 Jonas Valanciunas (Slot 3, Face 2128)
        writes.append(make_player_entry(
            name=roster[3][0], slot=3, face=roster[3][1], initiator=0,
            play_types=[8, 7, 15, 0],
            intangibles=88, touches=82, shot=82,
            extra_attrs={"strength": 94, "interior_def": 86}
        ))
        # 赫伯特·琼斯 Herbert Jones (Slot 10, Face 9927)
        writes.append(make_player_entry(
            name=roster[10][0], slot=10, face=roster[10][1], initiator=0,
            play_types=[11, 15, 0, 0],
            intangibles=90, touches=72, shot=72,
            extra_attrs={"perimeter_def": 96, "steal": 92, "block": 86},
            badges={"Clamps": 4, "Interceptor": 4}
        ))

    # 17: DAL (Dallas Mavericks)
    elif team_id == 17:
        # 卢卡·东契奇 Luka Doncic (Slot 0, Face 7702) - 2022 西决宇宙级持球大核！
        writes.append(make_player_entry(
            name=roster[0][0], slot=0, face=roster[0][1], initiator=1,
            play_types=[4, 1, 9, 8],
            intangibles=99, touches=99, shot=98,
            extra_attrs={"ball_control": 98, "pass_accuracy": 99, "pass_vision": 99, "pass_iq": 99, "three_point": 90, "mid_range": 92, "driving_layup": 94, "strength": 90, "post_moves": 92},
            extra_tends={"drive": 96, "post_up": 90, "shot_three": 96, "dish_to_open_man": 99},
            badges={"Dimer": 4, "FloorGeneral": 4, "HandlesForDays": 4, "SpaceCreator": 4, "Deadeye": 4, "DifficultShots": 4, "Sniper": 4, "NeedleThreader": 4, "BulletPasser": 4, "Unpluckable": 4, "ClutchShooter": 4, "BailOut": 4}
        ))
        # 斯宾塞·丁威迪 Spencer Dinwiddie (Slot 10, Face 4168)
        writes.append(make_player_entry(
            name=roster[10][0], slot=10, face=roster[10][1], initiator=1,
            play_types=[4, 1, 15, 14],
            intangibles=90, touches=88, shot=88,
            extra_attrs={"three_point": 86, "driving_layup": 88, "ball_control": 88},
            badges={"QuickFirstStep": 3, "ClutchShooter": 3}
        ))
        # 克里斯蒂安·伍德 Christian Wood (Slot 12, Face 4485)
        writes.append(make_player_entry(
            name=roster[12][0], slot=12, face=roster[12][1], initiator=0,
            play_types=[15, 7, 8, 1],
            intangibles=88, touches=85, shot=88,
            extra_attrs={"three_point": 86, "driving_layup": 86},
            badges={"CatchAndShoot": 3}
        ))
        # 小蒂姆·哈达威 Tim Hardaway Jr (Slot 1, Face 2710)
        writes.append(make_player_entry(
            name=roster[1][0], slot=1, face=roster[1][1], initiator=0,
            play_types=[15, 12, 1, 0],
            intangibles=86, touches=82, shot=86,
            extra_attrs={"three_point": 88},
            badges={"CatchAndShoot": 4}
        ))
        # 多里安·芬尼-史密斯 Dorian Finney-Smith (Slot 2, Face 7286)
        writes.append(make_player_entry(
            name=roster[2][0], slot=2, face=roster[2][1], initiator=0,
            play_types=[15, 11, 0, 0],
            intangibles=88, touches=74, shot=74,
            extra_attrs={"perimeter_def": 88, "three_point": 86},
            badges={"CornerSpecialist": 4, "Clamps": 3}
        ))

    # 23: HOU (Houston Rockets)
    elif team_id == 23:
        # 阿尔佩伦·申京 Alperen Sengun (Slot 5, Face 9908) - 小约基奇内线战术母体！
        writes.append(make_player_entry(
            name=roster[5][0], slot=5, face=roster[5][1], initiator=1,
            play_types=[8, 9, 7, 13],
            intangibles=96, touches=92, shot=88,
            extra_attrs={"pass_accuracy": 94, "pass_vision": 95, "post_moves": 94, "interior_def": 86, "strength": 88},
            extra_tends={"dish_to_open_man": 96, "post_up": 92},
            badges={"PostPlaymaker": 4, "Dimer": 4, "DreamShake": 4, "PostDropStepper": 4, "BreakStarter": 3}
        ))
        # 杰伦·格林 Jalen Green (Slot 1, Face 8053)
        writes.append(make_player_entry(
            name=roster[1][0], slot=1, face=roster[1][1], initiator=1,
            play_types=[1, 4, 15, 11],
            intangibles=94, touches=94, shot=95,
            extra_attrs={"speed": 98, "acceleration": 98, "driving_dunk": 94, "three_point": 88},
            badges={"Posterizer": 4, "QuickFirstStep": 4, "Downhill": 4, "LimitlessTakeoff": 4}
        ))
        # 小凯文·波特 Kevin Porter Jr. (Slot 3, Face 7849)
        writes.append(make_player_entry(
            name=roster[3][0], slot=3, face=roster[3][1], initiator=1,
            play_types=[4, 1, 15, 0],
            intangibles=88, touches=88, shot=88,
            extra_attrs={"ball_control": 88, "three_point": 86}
        ))
        # 杰肖恩·泰特 Jae'Sean Tate (Slot 2, Face 8020)
        writes.append(make_player_entry(
            name=roster[2][0], slot=2, face=roster[2][1], initiator=0,
            play_types=[11, 8, 0, 0],
            intangibles=86, touches=76, shot=76,
            extra_attrs={"strength": 88, "perimeter_def": 85}
        ))
        # 约翰·沃尔 John Wall (Slot 0, Face 1801)
        writes.append(make_player_entry(
            name=roster[0][0], slot=0, face=roster[0][1], initiator=1,
            play_types=[4, 1, 14, 0],
            intangibles=86, touches=82, shot=80,
            extra_attrs={"speed": 92, "pass_accuracy": 88}
        ))

    # 25: SAS (San Antonio Spurs)
    elif team_id == 25:
        # 德文·瓦塞尔 Devin Vassell (Slot 5, Face 8003) - 纯粹跳投得分手
        writes.append(make_player_entry(
            name=roster[5][0], slot=5, face=roster[5][1], initiator=1,
            play_types=[4, 14, 15, 1],
            intangibles=92, touches=90, shot=92,
            extra_attrs={"mid_range": 94, "three_point": 90, "driving_layup": 88},
            extra_tends={"shot_mid_range": 92, "shot_three": 90},
            badges={"DifficultShots": 4, "Sniper": 4, "Deadeye": 3}
        ))
        # 凯尔登·约翰逊 Keldon Johnson (Slot 0, Face 7848)
        writes.append(make_player_entry(
            name=roster[0][0], slot=0, face=roster[0][1], initiator=1,
            play_types=[1, 4, 15, 11],
            intangibles=92, touches=92, shot=92,
            extra_attrs={"driving_layup": 92, "three_point": 86, "strength": 88},
            badges={"FearlessFinisher": 3}
        ))
        # 雅各布·珀尔特尔 Jakob Poeltl (Slot 2, Face 7207)
        writes.append(make_player_entry(
            name=roster[2][0], slot=2, face=roster[2][1], initiator=0,
            play_types=[7, 8, 13, 0],
            intangibles=88, touches=76, shot=74,
            extra_attrs={"interior_def": 90, "block": 90}
        ))
        # 朗尼·沃克 Lonnie Walker IV (Slot 4, Face 7717)
        writes.append(make_player_entry(
            name=roster[4][0], slot=4, face=roster[4][1], initiator=0,
            play_types=[15, 11, 4, 0],
            intangibles=86, touches=82, shot=84,
            extra_attrs={"speed": 94, "driving_layup": 86}
        ))
        # 约什·理查德森 Josh Richardson (Slot 12, Face 4459)
        writes.append(make_player_entry(
            name=roster[12][0], slot=12, face=roster[12][1], initiator=0,
            play_types=[15, 11, 4, 0],
            intangibles=86, touches=78, shot=80,
            extra_attrs={"perimeter_def": 85, "three_point": 84}
        ))

    return writes

def build_all_teams_spec() -> Dict[str, Any]:
    db_path = r"C:\nba2k22\saves\MyLEAGUE0005\league_state.sqlite"
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"未找到数据库: {db_path}")

    con = sqlite3.connect(db_path)
    cur = con.cursor()

    teams_meta = {}
    for tid, abbr, name, city in cur.execute("SELECT team_id, abbreviation, name, city FROM teams").fetchall():
        teams_meta[tid] = {"abbr": abbr, "name": f"{city} {name}", "city": city}

    team_players = {}
    for tid in teams_meta.keys():
        rows = cur.execute(
            "SELECT roster_slot, player_name, face_id FROM player_source_details WHERE team_id = ? ORDER BY roster_slot",
            (tid,)
        ).fetchall()
        team_players[tid] = {r[0]: (r[1], r[2]) for r in rows}

    batches_list = []
    total_players_count = 0

    for b_key, b_info in DIVISIONS.items():
        batch_obj = {
            "batch_id": b_key,
            "division": b_info["division"],
            "teams": []
        }

        for tid in b_info["team_ids"]:
            t_meta = teams_meta.get(tid, {"abbr": f"T{tid}", "name": f"Team {tid}"})
            t_tactics = get_team_tactical_profile(tid)

            team_obj = {
                "team_id": tid,
                "team_abbr": t_meta["abbr"],
                "team_name": t_meta["name"],
                "team_settings": {
                    "team_chemistry": 85,
                    "fan_interest": 92
                },
                "coaching_writes": [
                    { "field_name": "active_system", "target_block": "COACHDATA", "offset": 267, "val_raw": t_tactics["active_system"], "description": f"战术系统: {t_tactics['active_system']}" },
                    { "field_name": "bench_depth", "target_block": "COACHDATA", "offset": 222, "val_raw": t_tactics["bench_depth"], "description": f"轮换人数: {t_tactics['bench_depth']}人" },
                    { "field_name": "bench_utilization", "target_block": "COACHDATA", "offset": 312, "val_raw": t_tactics["bench_utilization"], "description": f"替补使用率: {t_tactics['bench_utilization']}" },
                    { "field_name": "run_play_tendency", "target_block": "COACHDATA", "offset": 224, "val_raw": t_tactics["run_play"], "description": f"战术执行倾向: {t_tactics['run_play']}%" }
                ],
                "player_writes": []
            }

            p_writes = build_team_top5_players(tid, team_players.get(tid, {}))
            team_obj["player_writes"] = p_writes
            total_players_count += len(p_writes)
            batch_obj["teams"].append(team_obj)

        batches_list.append(batch_obj)

    spec = {
        "protocol_version": "v2.0_full_dimensional_native_mod",
        "task_package_id": "CYCLE_02_30_TEAMS_REALISM_AND_SIGNATURE_REBALANCE",
        "season_id": "2021-2022",
        "target_career": "MyLEAGUE0005",
        "target_process": "NBA2K22.exe",
        "total_teams": 30,
        "total_players": total_players_count,
        "batches": batches_list
    }
    return spec

def main():
    print("=" * 80)
    print("正在构建 NBA 2K22 30 队五虎现实化重构规格书 (v2.0 - 2022~2026 核心巨星深度现实化校准版)...")
    print("=" * 80)

    spec = build_all_teams_spec()

    # 落盘外部免污染路径
    ext_dir = r"C:\nba2k22\exports"
    os.makedirs(ext_dir, exist_ok=True)
    ext_path = os.path.join(ext_dir, "cycle_02_30_teams_realism_execution_ready.json")
    with open(ext_path, "w", encoding="utf-8") as f:
        json.dump(spec, f, indent=2, ensure_ascii=False)
    print(f"[+] 外部执行规格书已输出至: {ext_path}")

    # 仓内备份归档
    repo_dir = os.path.join(os.path.dirname(__file__), "..", "database", "tactics")
    os.makedirs(repo_dir, exist_ok=True)
    repo_path = os.path.join(repo_dir, "cycle_02_30_teams_realism_execution_ready.json")
    with open(repo_path, "w", encoding="utf-8") as f:
        json.dump(spec, f, indent=2, ensure_ascii=False)
    print(f"[+] 仓内永久归档已同步至: {repo_path}")

    print("\n" + "=" * 80)
    print("规格书生成完毕统计：")
    print(f"  - 覆盖赛区数: {len(spec['batches'])} (六大赛区)")
    print(f"  - 覆盖球队数: {spec['total_teams']} 支")
    print(f"  - 覆盖球员数: {spec['total_players']} 名核心五虎 (100% 深度现实化定制)")
    print("=" * 80)

if __name__ == "__main__":
    main()
