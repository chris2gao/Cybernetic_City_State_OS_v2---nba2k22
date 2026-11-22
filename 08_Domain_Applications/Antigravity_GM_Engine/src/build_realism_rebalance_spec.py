# -*- coding: utf-8 -*-
"""
NBA 2K22 30 支球队核心五虎现实化与标志性 DNA 重构规格书构建器 (v2.0 全维通用规范)
(Build 30-Team Top 5 Realism & Signature DNA Rebalance Spec v2.0)

目标：
1. 覆盖 30 支球队每队最好的 5 名核心球员 (共 150 名球员)；
2. 深度融入 14 位现实爆发巨星 (布伦森、SGA、爱德华兹、哈利伯顿、马克西、申京、马尔卡宁、小瓦格纳等)；
3. 彻底修复原生 2K 对历史巨星的陈旧偏见 (如 2022 FMVP 库里力量仅 54、纯持球挡拆打法缺失无球跑位体系等)；
4. 严格执行“球权双核铁律”：触球倾向 (touches at 1177) 与出手倾向 (shot at 1112) 双驱绑定；
5. 严格遵循《NBA 2K22 全维度战术、教练与球员资产 REA Native 批量注入标准接口协议 (v2.0)》；
6. 输出至 C:\\nba2k22\\exports\\cycle_02_30_teams_realism_execution_ready.json 及仓内归档目录。
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
        # GSW: 传切空间流
        29: {
            "active_system": 0, # Pace & Space
            "bench_depth": 10,
            "bench_utilization": 54,
            "run_play": 85,
            "poe_offense": 2, # 为射手跑位
            "poe_tempo": 9,   # 尽早反击出手
            "poe_defense": 15 # 贴防外线三分
        },
        # DEN: 约基奇高低位传控流
        19: {
            "active_system": 4, # Post Centric
            "bench_depth": 9,
            "bench_utilization": 50,
            "run_play": 82,
            "poe_offense": 3, # 打低位内线
            "poe_tempo": 7,   # 耐心阵地战
            "poe_defense": 13 # 保护禁区
        },
        # PHI: 恩比德低位压迫
        0: {
            "active_system": 4, # Post Centric
            "bench_depth": 9,
            "bench_utilization": 50,
            "run_play": 80,
            "poe_offense": 3,
            "poe_tempo": 7,
            "poe_defense": 13
        },
        # MIL: 字母哥冲击禁区
        1: {
            "active_system": 0, # Pace & Space
            "bench_depth": 9,
            "bench_utilization": 50,
            "run_play": 78,
            "poe_offense": 1, # 冲击篮筐
            "poe_tempo": 9,
            "poe_defense": 13 # 保护禁区
        },
        # PHX: 保罗布克中距离挡拆
        26: {
            "active_system": 2, # Perimeter Centric
            "bench_depth": 9,
            "bench_utilization": 50,
            "run_play": 85,
            "poe_offense": 4, # 挡拆进攻
            "poe_tempo": 7,
            "poe_defense": 15
        },
        # DAL: 东契奇持球大核
        17: {
            "active_system": 0, # Pace & Space
            "bench_depth": 9,
            "bench_utilization": 52,
            "run_play": 80,
            "poe_offense": 4, # 挡拆进攻
            "poe_tempo": 7,
            "poe_defense": 13
        },
        # BOS: 双探花侧翼单打与五外
        5: {
            "active_system": 0, # Pace & Space
            "bench_depth": 9,
            "bench_utilization": 50,
            "run_play": 82,
            "poe_offense": 4,
            "poe_tempo": 8,
            "poe_defense": 15
        },
        # MIA: 强硬防守与强侧挡拆手递手
        10: {
            "active_system": 5, # Grit and Grind
            "bench_depth": 9,
            "bench_utilization": 52,
            "run_play": 85,
            "poe_offense": 4,
            "poe_tempo": 7,
            "poe_defense": 18 # 强硬身体对抗
        }
    }
    # 默认标准配置
    default_cfg = {
        "active_system": 6, # Balanced
        "bench_depth": 9,
        "bench_utilization": 50,
        "run_play": 80,
        "poe_offense": 4, # 挡拆进攻
        "poe_tempo": 8,
        "poe_defense": 13 # 保护禁区
    }
    return profiles.get(team_id, default_cfg)

def build_all_teams_spec() -> Dict[str, Any]:
    db_path = r"C:\nba2k22\saves\MyLEAGUE0005\league_state.sqlite"
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"未找到数据库: {db_path}")

    con = sqlite3.connect(db_path)
    cur = con.cursor()

    # 获取球队基础信息
    teams_meta = {}
    for tid, abbr, name, city in cur.execute("SELECT team_id, abbreviation, name, city FROM teams").fetchall():
        teams_meta[tid] = {"abbr": abbr, "name": f"{city} {name}", "city": city}

    # 获取每队球员名单
    team_players = {}
    for tid in teams_meta.keys():
        rows = cur.execute(
            "SELECT roster_slot, player_name, face_id FROM player_source_details WHERE team_id = ? ORDER BY roster_slot",
            (tid,)
        ).fetchall()
        team_players[tid] = {r[0]: (r[1], r[2]) for r in rows}

    batches_list = []
    total_players_count = 0

    # 逐赛区构建
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
                    { "field_name": "bench_depth", "target_block": "COACHDATA", "offset": 268, "val_raw": t_tactics["bench_depth"], "description": f"轮换人数: {t_tactics['bench_depth']}人" },
                    { "field_name": "bench_utilization", "target_block": "COACHDATA", "offset": 269, "val_raw": t_tactics["bench_utilization"], "description": f"替补使用率: {t_tactics['bench_utilization']}" },
                    { "field_name": "run_play_tendency", "target_block": "COACHDATA", "offset": 224, "val_raw": t_tactics["run_play"], "description": f"战术执行倾向: {t_tactics['run_play']}%" },
                    { "field_name": "poe_offense", "target_block": "COACHDATA", "offset": 382, "val_raw": t_tactics["poe_offense"], "description": f"进攻重点: {t_tactics['poe_offense']}" },
                    { "field_name": "poe_defense", "target_block": "COACHDATA", "offset": 385, "val_raw": t_tactics["poe_defense"], "description": f"防守重点: {t_tactics['poe_defense']}" }
                ],
                "player_writes": []
            }

            # 针对每支球队定制其核心五虎名单及精细化设定
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
        "total_teams": len(teams_meta),
        "total_players": total_players_count,
        "batches": batches_list
    }
    return spec

def make_player_entry(name: str, slot: int, face: int, initiator: int, play_types: List[int],
                      intangibles: int, touches: int, shot: int,
                      extra_attrs: Dict[str, int] = None,
                      extra_tends: Dict[str, int] = None,
                      badges: Dict[str, int] = None) -> Dict[str, Any]:
    """标准化生成单一球员 v2.0 规格项"""
    # 属性偏移字典
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
        "stamina": 1084,
        "hustle": 1085
    }
    # 倾向偏移字典
    tend_offsets = {
        "touches": 1177,
        "shot": 1112,
        "drive": 1155,
        "dish_to_open_man": 1176,
        "shot_three": 1138,
        "spot_up_three": 1139,
        "post_up": 1178,
        "contest_shot": 1207,
        "block_shot": 1208,
        "on_ball_steal": 1206
    }

    mods = []
    # 无形资产 (Intangibles)
    mods.append({
        "field": "intangibles",
        "offset": 1088,
        "val_raw": rating_to_raw(intangibles),
        "human_val": intangibles,
        "type": "uint8",
        "description": f"无形资产设定: {intangibles} (控制轮换地位与AI上场时间)"
    })
    # 球权双核：触球倾向
    mods.append({
        "field": "touches",
        "offset": 1177,
        "val_raw": touches,
        "type": "uint8",
        "description": f"触球呼叫倾向: {touches} (决定战术发起比率)"
    })
    # 球权双核：出手倾向
    mods.append({
        "field": "shot",
        "offset": 1112,
        "val_raw": shot,
        "type": "uint8",
        "description": f"持球终结出手倾向: {shot} (决定真实持球得分侵略性)"
    })

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
    """根据真实联盟战力和赋能目标构建每支球队核心五虎"""
    writes = []

    # 1. 勇士 Golden State Warriors (Team 29)
    if team_id == 29:
        # 库里 FMVP 强化 + 修复无球跑位缺陷
        writes.append(make_player_entry(
            name=roster[0][0], slot=0, face=roster[0][1], initiator=1,
            play_types=[11, 12, 15, 4], # Cutter, Handoff, 3PT, PnR Handler
            intangibles=99, touches=95, shot=95,
            extra_attrs={"strength": 75, "perimeter_def": 80, "interior_def": 60, "stamina": 99, "three_point": 99},
            extra_tends={"spot_up_three": 99, "dish_to_open_man": 88, "contest_shot": 75},
            badges={"Chef": 4, "CircusThrees": 4, "CatchAndShoot": 4, "Deadeye": 4, "LimitlessSpotUp": 4, "Sniper": 4, "SlipperyOffball": 4, "HandlesForDays": 4, "ClutchesShooter": 4}
        ))
        # 汤普森
        writes.append(make_player_entry(
            name=roster[1][0], slot=1, face=roster[1][1], initiator=0,
            play_types=[15, 11, 14, 12], # 3PT, Cutter, Mid-Range, Handoff
            intangibles=90, touches=80, shot=86,
            extra_attrs={"three_point": 92, "perimeter_def": 82},
            badges={"CatchAndShoot": 4, "CornerSpecialist": 4, "Deadeye": 3, "Sniper": 3}
        ))
        # 追梦格林
        writes.append(make_player_entry(
            name=roster[3][0], slot=3, face=roster[3][1], initiator=1,
            play_types=[13, 7, 0, 0], # Handoff Passer, PnR Roll
            intangibles=88, touches=78, shot=50,
            extra_attrs={"pass_accuracy": 92, "pass_vision": 90, "interior_def": 92, "perimeter_def": 86, "strength": 88},
            extra_tends={"dish_to_open_man": 95, "block_shot": 80, "contest_shot": 95},
            badges={"Dimer": 4, "FloorGeneral": 4, "BrickWall": 4, "DefensiveLeader": 4, "Clamps": 3, "Intimidator": 4}
        ))
        # 维金斯
        writes.append(make_player_entry(
            name=roster[2][0], slot=2, face=roster[2][1], initiator=0,
            play_types=[15, 11, 1, 4], # 3PT, Cutter, Iso, PnR Handler
            intangibles=88, touches=80, shot=82,
            extra_attrs={"perimeter_def": 88, "lateral_quick": 86, "driving_layup": 85},
            badges={"Clamps": 3, "Intimidator": 3, "CatchAndShoot": 3}
        ))
        # 普尔 Jordan Poole (Slot 8, Face 7847)
        p_slot = 8 if 8 in roster else 5
        writes.append(make_player_entry(
            name=roster[p_slot][0], slot=p_slot, face=roster[p_slot][1], initiator=1,
            play_types=[4, 1, 15, 12], # PnR, Iso, 3PT, Handoff
            intangibles=90, touches=84, shot=88,
            extra_attrs={"three_point": 86, "ball_control": 86, "driving_layup": 86},
            badges={"Chef": 2, "QuickFirstStep": 3, "DifficultShots": 2}
        ))

    # 2. 独行侠 Dallas Mavericks (Team 17) - 核心布伦森爆发赋能
    elif team_id == 17:
        # 东契奇
        writes.append(make_player_entry(
            name=roster[0][0], slot=0, face=roster[0][1], initiator=1,
            play_types=[4, 1, 9, 8], # PnR, Iso, Post High, Post Low
            intangibles=99, touches=98, shot=95,
            extra_attrs={"pass_accuracy": 98, "pass_vision": 98, "ball_control": 98, "strength": 88},
            badges={"Dimer": 4, "FloorGeneral": 4, "QuickFirstStep": 4, "Unpluckable": 4, "Deadeye": 3}
        ))
        # 布伦森 Jalen Brunson (Slot 8, Face 7732) - 爆发为 2026 纽约大头超巨模板！
        b_slot = 8 if 8 in roster else 1
        writes.append(make_player_entry(
            name=roster[b_slot][0], slot=b_slot, face=roster[b_slot][1], initiator=1,
            play_types=[4, 1, 8, 14], # PnR Handler, Iso, Post Low (标志性背身脚步), Mid-Range
            intangibles=97, touches=94, shot=94,
            extra_attrs={"ball_control": 94, "mid_range": 95, "three_point": 88, "driving_layup": 95, "pass_accuracy": 90, "strength": 78},
            extra_tends={"drive": 95, "post_up": 85, "dish_to_open_man": 88},
            badges={"DifficultShots": 4, "FearlessFinisher": 4, "TearDropper": 4, "AnkleBreaker": 3, "HandlesForDays": 4, "ClutchShooter": 4, "QuickFirstStep": 4}
        ))
        # 波尔津吉斯
        writes.append(make_player_entry(
            name=roster[3][0], slot=3, face=roster[3][1], initiator=0,
            play_types=[15, 8, 7, 14], # 3PT, Post Low, PnR Roll, Mid-Range
            intangibles=88, touches=84, shot=86,
            extra_attrs={"three_point": 86, "block": 88, "interior_def": 82},
            badges={"CatchAndShoot": 3, "RimProtector": 3}
        ))
        # 哈达威
        writes.append(make_player_entry(
            name=roster[1][0], slot=1, face=roster[1][1], initiator=0,
            play_types=[15, 12, 1, 0],
            intangibles=82, touches=78, shot=84,
            badges={"CatchAndShoot": 3, "CornerSpecialist": 3}
        ))
        # 芬尼-史密斯
        writes.append(make_player_entry(
            name=roster[2][0], slot=2, face=roster[2][1], initiator=0,
            play_types=[15, 11, 0, 0],
            intangibles=80, touches=65, shot=65,
            extra_attrs={"perimeter_def": 85, "three_point": 82},
            badges={"CornerSpecialist": 3, "Clamps": 3}
        ))

    # 3. 雷霆 Oklahoma City Thunder (Team 24) - SGA 爆发赋能
    elif team_id == 24:
        # SGA Shai Gilgeous-Alexander (Slot 0, Face 7710) - 2026 MVP 级强化
        writes.append(make_player_entry(
            name=roster[0][0], slot=0, face=roster[0][1], initiator=1,
            play_types=[1, 4, 14, 8], # Iso, PnR Handler, Mid-Range, Post Low
            intangibles=98, touches=96, shot=95,
            extra_attrs={"ball_control": 96, "driving_layup": 96, "mid_range": 94, "perimeter_def": 88, "steal": 92, "lateral_quick": 90},
            extra_tends={"drive": 98, "dish_to_open_man": 88, "on_ball_steal": 85},
            badges={"DifficultShots": 4, "QuickFirstStep": 4, "HandlesForDays": 4, "Clamps": 3, "Interceptor": 4, "FearlessFinisher": 4}
        ))
        # 多特 Luguentz Dort (Slot 1, Face 7910)
        writes.append(make_player_entry(
            name=roster[1][0], slot=1, face=roster[1][1], initiator=0,
            play_types=[15, 11, 1, 0],
            intangibles=85, touches=74, shot=75,
            extra_attrs={"perimeter_def": 95, "strength": 88, "lateral_quick": 92},
            badges={"Clamps": 4, "Menace": 4, "CornerSpecialist": 3}
        ))
        # 吉迪 Josh Giddey (Slot 6, Face 8064)
        g_slot = 6 if 6 in roster else 2
        writes.append(make_player_entry(
            name=roster[g_slot][0], slot=g_slot, face=roster[g_slot][1], initiator=1,
            play_types=[4, 9, 11, 1],
            intangibles=88, touches=84, shot=75,
            extra_attrs={"pass_accuracy": 92, "pass_vision": 92, "ball_control": 86},
            badges={"Dimer": 3, "NeedleThreader": 3}
        ))
        # 波库舍夫斯基
        writes.append(make_player_entry(
            name=roster[2][0], slot=2, face=roster[2][1], initiator=0,
            play_types=[15, 11, 7, 0],
            intangibles=80, touches=72, shot=74
        ))
        # 贝兹利
        writes.append(make_player_entry(
            name=roster[3][0], slot=3, face=roster[3][1], initiator=0,
            play_types=[11, 7, 15, 0],
            intangibles=78, touches=70, shot=70
        ))

    # 4. 森林狼 Minnesota Timberwolves (Team 27) - 爱德华兹爆发赋能
    elif team_id == 27:
        # 爱德华兹 Anthony Edwards (Slot 2, Face 7954) - 2026 门面球星模板
        writes.append(make_player_entry(
            name=roster[2][0], slot=2, face=roster[2][1], initiator=1,
            play_types=[1, 4, 15, 11], # Iso, PnR, 3PT, Cutter
            intangibles=98, touches=95, shot=95,
            extra_attrs={"driving_layup": 95, "three_point": 88, "perimeter_def": 88, "strength": 85, "speed": 94, "vertical": 96},
            extra_tends={"drive": 96, "spot_up_three": 88, "contest_shot": 85},
            badges={"Posterizer": 4, "QuickFirstStep": 4, "FearlessFinisher": 4, "LimitlessTakeoff": 4, "Clamps": 3}
        ))
        # 唐斯 Karl-Anthony Towns (Slot 4, Face 4472)
        writes.append(make_player_entry(
            name=roster[4][0], slot=4, face=roster[4][1], initiator=0,
            play_types=[15, 8, 7, 14],
            intangibles=92, touches=88, shot=88,
            extra_attrs={"three_point": 90, "mid_range": 88, "interior_def": 78},
            badges={"CatchAndShoot": 4, "Sniper": 3}
        ))
        # 麦克丹尼尔斯 Jaden McDaniels (Slot 3, Face 8017)
        writes.append(make_player_entry(
            name=roster[3][0], slot=3, face=roster[3][1], initiator=0,
            play_types=[15, 11, 0, 0],
            intangibles=88, touches=72, shot=72,
            extra_attrs={"perimeter_def": 94, "lateral_quick": 92, "block": 84},
            badges={"Clamps": 4, "Interceptor": 3, "CornerSpecialist": 3}
        ))
        # 拉塞尔
        writes.append(make_player_entry(
            name=roster[0][0], slot=0, face=roster[0][1], initiator=1,
            play_types=[4, 14, 15, 1],
            intangibles=85, touches=84, shot=82,
            extra_attrs={"pass_accuracy": 88, "three_point": 85}
        ))
        # 比斯利
        writes.append(make_player_entry(
            name=roster[1][0], slot=1, face=roster[1][1], initiator=0,
            play_types=[15, 12, 0, 0],
            intangibles=80, touches=75, shot=82
        ))

    # 5. 步行者 Indiana Pacers (Team 20) - 哈利伯顿 & 马尔卡宁爆发赋能
    elif team_id == 20:
        # 哈利伯顿 Tyrese Haliburton (Slot 2, Face 8001) - 历史级传控与投射大核
        writes.append(make_player_entry(
            name=roster[2][0], slot=2, face=roster[2][1], initiator=1,
            play_types=[4, 15, 1, 12],
            intangibles=97, touches=96, shot=82,
            extra_attrs={"pass_accuracy": 98, "pass_vision": 98, "pass_iq": 98, "three_point": 93, "ball_control": 92},
            extra_tends={"dish_to_open_man": 98, "spot_up_three": 90},
            badges={"Dimer": 4, "FloorGeneral": 4, "BulletPasser": 4, "NeedleThreader": 4, "Sniper": 4, "QuickFirstStep": 3}
        ))
        # 马尔卡宁 Lauri Markkanen (Slot 4, Face 7508) - 最快进步球员 / 全明星高炮台
        writes.append(make_player_entry(
            name=roster[4][0], slot=4, face=roster[4][1], initiator=0,
            play_types=[15, 11, 7, 8],
            intangibles=94, touches=88, shot=88,
            extra_attrs={"three_point": 90, "mid_range": 86, "driving_layup": 84, "strength": 82},
            badges={"CatchAndShoot": 4, "CornerSpecialist": 4, "Sniper": 3}
        ))
        # 西亚卡姆 Pascal Siakam (Slot 3, Face 7236)
        writes.append(make_player_entry(
            name=roster[3][0], slot=3, face=roster[3][1], initiator=1,
            play_types=[1, 8, 4, 11],
            intangibles=94, touches=90, shot=90,
            extra_attrs={"mid_range": 85, "driving_layup": 88, "interior_def": 82},
            badges={"DifficultShots": 3, "FearlessFinisher": 3}
        ))
        # 特纳 Myles Turner (Slot 0, Face 4474)
        writes.append(make_player_entry(
            name=roster[0][0], slot=0, face=roster[0][1], initiator=0,
            play_types=[15, 7, 0, 0],
            intangibles=86, touches=72, shot=72,
            extra_attrs={"block": 94, "interior_def": 86, "three_point": 80},
            badges={"RimProtector": 4, "Intimidator": 3}
        ))
        # 哈特 Josh Hart (Slot 7, Face 7528)
        h_slot = 7 if 7 in roster else 5
        writes.append(make_player_entry(
            name=roster[h_slot][0], slot=h_slot, face=roster[h_slot][1], initiator=0,
            play_types=[11, 15, 0, 0],
            intangibles=84, touches=70, shot=68,
            extra_attrs={"hustle": 98, "perimeter_def": 85},
            badges={"Hustler": 4, "Clamps": 3}
        ))

    # 6. 76人 Philadelphia 76ers (Team 0) - 马克西爆发赋能
    elif team_id == 0:
        # 恩比德 Joel Embiid (Slot 4, Face 4090)
        writes.append(make_player_entry(
            name=roster[4][0], slot=4, face=roster[4][1], initiator=1,
            play_types=[8, 1, 7, 4], # Post Low, Iso, PnR Roll, PnR Handler
            intangibles=99, touches=96, shot=96,
            extra_attrs={"interior_def": 94, "block": 92, "mid_range": 90, "strength": 96},
            badges={"BackdownPunisher": 4, "Dropstepper": 4, "RimProtector": 4, "Intimidator": 4}
        ))
        # 马克西 Tyrese Maxey (Slot 8, Face 8011) - 极速爆发超巨
        m_slot = 8 if 8 in roster else 1
        writes.append(make_player_entry(
            name=roster[m_slot][0], slot=m_slot, face=roster[m_slot][1], initiator=1,
            play_types=[4, 1, 15, 11],
            intangibles=95, touches=90, shot=90,
            extra_attrs={"speed": 98, "acceleration": 98, "three_point": 91, "driving_layup": 92, "ball_control": 90},
            extra_tends={"drive": 95, "spot_up_three": 90},
            badges={"QuickFirstStep": 4, "Downhill": 4, "Sniper": 4, "Chef": 3, "FearlessFinisher": 3}
        ))
        # 托比亚斯·哈里斯
        writes.append(make_player_entry(
            name=roster[3][0], slot=3, face=roster[3][1], initiator=0,
            play_types=[14, 15, 8, 0],
            intangibles=84, touches=78, shot=78
        ))
        # 赛斯·库里
        writes.append(make_player_entry(
            name=roster[1][0], slot=1, face=roster[1][1], initiator=0,
            play_types=[15, 12, 14, 0],
            intangibles=82, touches=72, shot=75,
            extra_attrs={"three_point": 93},
            badges={"CatchAndShoot": 4, "CornerSpecialist": 4}
        ))
        # 丹尼·格林 / 塞布尔
        d_slot = 2 if 2 in roster else 6
        writes.append(make_player_entry(
            name=roster[d_slot][0], slot=d_slot, face=roster[d_slot][1], initiator=0,
            play_types=[15, 0, 0, 0],
            intangibles=80, touches=65, shot=65,
            extra_attrs={"perimeter_def": 88},
            badges={"CornerSpecialist": 3, "Clamps": 3}
        ))

    # 7. 火箭 Houston Rockets (Team 23) - 申京爆发赋能
    elif team_id == 23:
        # 申京 Alperen Sengun (Slot 6, Face 9908) - 小约基奇体系中枢
        s_slot = 6 if 6 in roster else 3
        writes.append(make_player_entry(
            name=roster[s_slot][0], slot=s_slot, face=roster[s_slot][1], initiator=1,
            play_types=[8, 9, 7, 13], # Post Low, Post High, PnR Roll, Handoff Passer
            intangibles=95, touches=92, shot=86,
            extra_attrs={"pass_accuracy": 90, "pass_vision": 92, "interior_def": 82, "strength": 85},
            extra_tends={"dish_to_open_man": 94, "post_up": 90},
            badges={"PostPlaymaker": 4, "Dimer": 3, "DreamShake": 3, "Dropstepper": 3}
        ))
        # 杰伦·格林 Jalen Green (Slot 1, Face 8053)
        writes.append(make_player_entry(
            name=roster[1][0], slot=1, face=roster[1][1], initiator=1,
            play_types=[1, 4, 15, 11],
            intangibles=90, touches=88, shot=90,
            extra_attrs={"speed": 95, "driving_layup": 90, "three_point": 85},
            badges={"QuickFirstStep": 3, "Posterizer": 3}
        ))
        # 小凯文·波特
        writes.append(make_player_entry(
            name=roster[4][0], slot=4, face=roster[4][1], initiator=1,
            play_types=[4, 1, 15, 0],
            intangibles=84, touches=82, shot=84
        ))
        # 泰特
        writes.append(make_player_entry(
            name=roster[2][0], slot=2, face=roster[2][1], initiator=0,
            play_types=[11, 8, 0, 0],
            intangibles=80, touches=70, shot=70
        ))
        # 肯扬·马丁
        m_slot = 5 if 5 in roster else 0
        writes.append(make_player_entry(
            name=roster[m_slot][0], slot=m_slot, face=roster[m_slot][1], initiator=0,
            play_types=[11, 15, 0, 0],
            intangibles=80, touches=70, shot=72
        ))

    # 8. 掘金 Denver Nuggets (Team 19)
    elif team_id == 19:
        # 约基奇 Nikola Jokic (Slot 3, Face 4170)
        writes.append(make_player_entry(
            name=roster[3][0], slot=3, face=roster[3][1], initiator=1,
            play_types=[8, 9, 7, 13], # Post Low, Post High, PnR Roll, Handoff Passer
            intangibles=99, touches=98, shot=80,
            extra_attrs={"pass_accuracy": 99, "pass_vision": 99, "pass_iq": 99, "mid_range": 94, "strength": 92},
            extra_tends={"dish_to_open_man": 99, "post_up": 92},
            badges={"Dimer": 4, "FloorGeneral": 4, "PostPlaymaker": 4, "BreakStarter": 4, "BulletPasser": 4, "Dropstepper": 4}
        ))
        # 穆雷 Jamal Murray (Slot 0, Face 7202)
        writes.append(make_player_entry(
            name=roster[0][0], slot=0, face=roster[0][1], initiator=1,
            play_types=[4, 12, 1, 14],
            intangibles=94, touches=88, shot=90,
            extra_attrs={"mid_range": 90, "three_point": 88, "driving_layup": 90},
            badges={"DifficultShots": 3, "Deadeye": 3, "QuickFirstStep": 3}
        ))
        # 小波特 Michael Porter Jr. (Slot 1, Face 7713)
        writes.append(make_player_entry(
            name=roster[1][0], slot=1, face=roster[1][1], initiator=0,
            play_types=[15, 11, 14, 0],
            intangibles=88, touches=80, shot=86,
            extra_attrs={"three_point": 91, "mid_range": 88},
            badges={"CatchAndShoot": 4, "Sniper": 3}
        ))
        # 戈登 Aaron Gordon (Slot 2, Face 4095)
        writes.append(make_player_entry(
            name=roster[2][0], slot=2, face=roster[2][1], initiator=0,
            play_types=[11, 7, 1, 8],
            intangibles=88, touches=76, shot=75,
            extra_attrs={"perimeter_def": 86, "interior_def": 85, "strength": 88},
            badges={"Posterizer": 3, "Clamps": 3, "Intimidator": 3}
        ))
        # 蒙特·莫里斯
        writes.append(make_player_entry(
            name=roster[4][0], slot=4, face=roster[4][1], initiator=1,
            play_types=[4, 14, 15, 0],
            intangibles=82, touches=78, shot=72
        ))

    # 9. 雄鹿 Milwaukee Bucks (Team 1)
    elif team_id == 1:
        # 字母哥
        writes.append(make_player_entry(
            name=roster[3][0], slot=3, face=roster[3][1], initiator=1,
            play_types=[1, 7, 8, 4],
            intangibles=99, touches=98, shot=96,
            extra_attrs={"driving_layup": 96, "interior_def": 95, "perimeter_def": 88, "block": 92, "strength": 96},
            badges={"Posterizer": 4, "Intimidator": 4, "RimProtector": 4, "Clamps": 4, "ChasedownArtist": 4}
        ))
        # 米德尔顿
        writes.append(make_player_entry(
            name=roster[2][0], slot=2, face=roster[2][1], initiator=1,
            play_types=[1, 4, 14, 15],
            intangibles=92, touches=86, shot=88,
            extra_attrs={"mid_range": 92, "three_point": 88},
            badges={"DifficultShots": 3, "Deadeye": 3}
        ))
        # 霍勒迪
        writes.append(make_player_entry(
            name=roster[0][0], slot=0, face=roster[0][1], initiator=1,
            play_types=[4, 8, 1, 14],
            intangibles=92, touches=84, shot=82,
            extra_attrs={"perimeter_def": 96, "steal": 92, "lateral_quick": 94},
            badges={"Clamps": 4, "Menace": 4, "PickPocket": 4}
        ))
        # 大洛佩兹
        writes.append(make_player_entry(
            name=roster[4][0], slot=4, face=roster[4][1], initiator=0,
            play_types=[15, 7, 0, 0],
            intangibles=86, touches=70, shot=72,
            extra_attrs={"block": 94, "interior_def": 90, "three_point": 80},
            badges={"RimProtector": 4, "Intimidator": 3}
        ))
        # 波蒂斯 Bobby Portis Jr. (Slot 6, Face 4454)
        p_slot = 6 if 6 in roster else 1
        writes.append(make_player_entry(
            name=roster[p_slot][0], slot=p_slot, face=roster[p_slot][1], initiator=0,
            play_types=[15, 8, 7, 0],
            intangibles=84, touches=76, shot=80
        ))

    # 10. 凯尔特人 Boston Celtics (Team 5)
    elif team_id == 5:
        # 塔图姆
        writes.append(make_player_entry(
            name=roster[3][0], slot=3, face=roster[3][1], initiator=1,
            play_types=[1, 4, 15, 14],
            intangibles=99, touches=96, shot=96,
            extra_attrs={"three_point": 90, "mid_range": 90, "perimeter_def": 88},
            badges={"Deadeye": 4, "Sniper": 4, "DifficultShots": 3}
        ))
        # 布朗
        writes.append(make_player_entry(
            name=roster[2][0], slot=2, face=roster[2][1], initiator=1,
            play_types=[1, 4, 11, 15],
            intangibles=96, touches=90, shot=92,
            extra_attrs={"driving_layup": 92, "three_point": 86, "perimeter_def": 88},
            badges={"Posterizer": 3, "Clamps": 3}
        ))
        # 斯玛特
        writes.append(make_player_entry(
            name=roster[1][0], slot=1, face=roster[1][1], initiator=1,
            play_types=[4, 12, 15, 0],
            intangibles=88, touches=76, shot=70,
            extra_attrs={"perimeter_def": 96, "steal": 92, "lateral_quick": 94},
            badges={"Clamps": 4, "Menace": 4, "DefensiveLeader": 4}
        ))
        # 罗伯特·威廉姆斯
        r_slot = 5 if 5 in roster else 4
        writes.append(make_player_entry(
            name=roster[r_slot][0], slot=r_slot, face=roster[r_slot][1], initiator=0,
            play_types=[7, 11, 0, 0],
            intangibles=86, touches=60, shot=55,
            extra_attrs={"block": 95, "interior_def": 88},
            badges={"RimProtector": 4, "Intimidator": 4}
        ))
        # 霍福德
        writes.append(make_player_entry(
            name=roster[4][0], slot=4, face=roster[4][1], initiator=0,
            play_types=[15, 8, 13, 0],
            intangibles=85, touches=70, shot=68,
            extra_attrs={"three_point": 82, "pass_accuracy": 82}
        ))

    # 11. 篮网 Brooklyn Nets (Team 18) - 托马斯爆发赋能
    elif team_id == 18:
        # 杜兰特
        writes.append(make_player_entry(
            name=roster[3][0], slot=3, face=roster[3][1], initiator=1,
            play_types=[1, 14, 15, 4],
            intangibles=99, touches=96, shot=96,
            extra_attrs={"mid_range": 98, "three_point": 92, "block": 85},
            badges={"Deadeye": 4, "DifficultShots": 4, "Sniper": 4}
        ))
        # 哈登
        writes.append(make_player_entry(
            name=roster[0][0], slot=0, face=roster[0][1], initiator=1,
            play_types=[4, 1, 15, 0],
            intangibles=96, touches=95, shot=88,
            extra_attrs={"pass_accuracy": 96, "pass_vision": 96, "ball_control": 95},
            badges={"Dimer": 4, "FloorGeneral": 4, "HandlesForDays": 4}
        ))
        # 欧文
        writes.append(make_player_entry(
            name=roster[1][0], slot=1, face=roster[1][1], initiator=1,
            play_types=[1, 4, 14, 15],
            intangibles=95, touches=90, shot=92,
            extra_attrs={"ball_control": 99, "driving_layup": 98, "mid_range": 94},
            badges={"AnkleBreaker": 4, "HandlesForDays": 4, "DifficultShots": 4}
        ))
        # 卡梅隆·托马斯 Cameron Thomas (Slot 12, Face 8066) - 爆发单打得分手
        c_slot = 12 if 12 in roster else 4
        writes.append(make_player_entry(
            name=roster[c_slot][0], slot=c_slot, face=roster[c_slot][1], initiator=1,
            play_types=[1, 4, 14, 15],
            intangibles=90, touches=86, shot=90,
            extra_attrs={"mid_range": 90, "three_point": 86, "driving_layup": 88},
            badges={"DifficultShots": 3, "VolumeShooter": 4}
        ))
        # 乔·哈里斯
        writes.append(make_player_entry(
            name=roster[2][0], slot=2, face=roster[2][1], initiator=0,
            play_types=[15, 11, 12, 0],
            intangibles=82, touches=72, shot=75,
            extra_attrs={"three_point": 92},
            badges={"CatchAndShoot": 4, "CornerSpecialist": 4}
        ))

    # 12. 湖人 Los Angeles Lakers (Team 15) - 里夫斯爆发赋能
    elif team_id == 15:
        # 詹姆斯
        writes.append(make_player_entry(
            name=roster[2][0], slot=2, face=roster[2][1], initiator=1,
            play_types=[4, 1, 9, 8],
            intangibles=99, touches=96, shot=94,
            extra_attrs={"pass_accuracy": 96, "pass_vision": 96, "strength": 92, "driving_layup": 95},
            badges={"Dimer": 4, "FloorGeneral": 4, "ChasedownArtist": 4}
        ))
        # 浓眉
        writes.append(make_player_entry(
            name=roster[3][0], slot=3, face=roster[3][1], initiator=1,
            play_types=[8, 7, 14, 1],
            intangibles=98, touches=92, shot=92,
            extra_attrs={"interior_def": 95, "block": 95, "rebound": 94},
            badges={"RimProtector": 4, "Intimidator": 4, "ReboundChaser": 4}
        ))
        # 威少
        writes.append(make_player_entry(
            name=roster[0][0], slot=0, face=roster[0][1], initiator=1,
            play_types=[4, 1, 11, 0],
            intangibles=88, touches=88, shot=86,
            extra_attrs={"speed": 92, "driving_layup": 88}
        ))
        # 里夫斯 Austin Reaves (Slot 12, Face 7720) - 湖人关键大心脏
        r_slot = 12 if 12 in roster else 1
        writes.append(make_player_entry(
            name=roster[r_slot][0], slot=r_slot, face=roster[r_slot][1], initiator=1,
            play_types=[4, 1, 15, 14],
            intangibles=92, touches=84, shot=82,
            extra_attrs={"pass_accuracy": 88, "three_point": 86, "driving_layup": 88},
            badges={"QuickFirstStep": 3, "DifficultShots": 2, "ClutchShooter": 3}
        ))
        # 蒙克
        writes.append(make_player_entry(
            name=roster[1][0], slot=1, face=roster[1][1], initiator=0,
            play_types=[15, 11, 4, 0],
            intangibles=84, touches=80, shot=84
        ))

    # 13. 公牛 Chicago Bulls (Team 3) - 科比·怀特爆发赋能
    elif team_id == 3:
        # 德罗赞
        writes.append(make_player_entry(
            name=roster[1][0], slot=1, face=roster[1][1], initiator=1,
            play_types=[1, 4, 14, 8],
            intangibles=94, touches=92, shot=92,
            extra_attrs={"mid_range": 96, "driving_layup": 92},
            badges={"DifficultShots": 4}
        ))
        # 拉文
        writes.append(make_player_entry(
            name=roster[0][0], slot=0, face=roster[0][1], initiator=1,
            play_types=[4, 1, 15, 11],
            intangibles=92, touches=90, shot=90,
            extra_attrs={"three_point": 90, "driving_dunk": 92}
        ))
        # 武切维奇
        writes.append(make_player_entry(
            name=roster[3][0], slot=3, face=roster[3][1], initiator=0,
            play_types=[8, 15, 7, 0],
            intangibles=86, touches=82, shot=80
        ))
        # 科比·怀特 Coby White (Slot 4, Face 7826) - 爆发先发控卫
        writes.append(make_player_entry(
            name=roster[4][0], slot=4, face=roster[4][1], initiator=1,
            play_types=[4, 15, 1, 14],
            intangibles=92, touches=86, shot=88,
            extra_attrs={"three_point": 88, "speed": 90, "driving_layup": 88},
            badges={"Sniper": 3, "QuickFirstStep": 3}
        ))
        # 帕特里克·威廉姆斯
        writes.append(make_player_entry(
            name=roster[2][0], slot=2, face=roster[2][1], initiator=0,
            play_types=[15, 11, 0, 0],
            intangibles=80, touches=70, shot=70
        ))

    # 14. 灰熊 Memphis Grizzlies (Team 8) - 贝恩爆发赋能
    elif team_id == 8:
        # 莫兰特
        writes.append(make_player_entry(
            name=roster[0][0], slot=0, face=roster[0][1], initiator=1,
            play_types=[4, 1, 11, 0],
            intangibles=98, touches=96, shot=95,
            extra_attrs={"speed": 98, "acceleration": 98, "driving_layup": 96},
            badges={"Posterizer": 4, "QuickFirstStep": 4}
        ))
        # 贾伦·杰克逊
        writes.append(make_player_entry(
            name=roster[3][0], slot=3, face=roster[3][1], initiator=0,
            play_types=[15, 7, 8, 0],
            intangibles=94, touches=84, shot=85,
            extra_attrs={"block": 98, "interior_def": 92, "three_point": 82},
            badges={"RimProtector": 4, "Intimidator": 4}
        ))
        # 贝恩 Desmond Bane (Slot 6, Face 8019) - 爆发神射副攻手
        b_slot = 6 if 6 in roster else 1
        writes.append(make_player_entry(
            name=roster[b_slot][0], slot=b_slot, face=roster[b_slot][1], initiator=1,
            play_types=[15, 4, 1, 12],
            intangibles=94, touches=88, shot=90,
            extra_attrs={"three_point": 92, "strength": 82, "driving_layup": 88},
            badges={"CatchAndShoot": 4, "CornerSpecialist": 4, "Sniper": 4}
        ))
        # 狄龙·布鲁克斯
        writes.append(make_player_entry(
            name=roster[1][0], slot=1, face=roster[1][1], initiator=0,
            play_types=[1, 15, 0, 0],
            intangibles=84, touches=78, shot=82,
            extra_attrs={"perimeter_def": 90},
            badges={"Clamps": 3, "Menace": 3}
        ))
        # 亚当斯
        writes.append(make_player_entry(
            name=roster[4][0], slot=4, face=roster[4][1], initiator=0,
            play_types=[7, 0, 0, 0],
            intangibles=84, touches=65, shot=55,
            extra_attrs={"strength": 98, "hustle": 95},
            badges={"BrickWall": 4, "Box": 4}
        ))

    # 15. 魔术 Orlando Magic (Team 16) - 小瓦格纳爆发赋能
    elif team_id == 16:
        # 小瓦格纳 Franz Wagner (Slot 9, Face 8062) - 全能高大组织前锋
        w_slot = 9 if 9 in roster else 0
        writes.append(make_player_entry(
            name=roster[w_slot][0], slot=w_slot, face=roster[w_slot][1], initiator=1,
            play_types=[4, 11, 15, 1],
            intangibles=94, touches=88, shot=86,
            extra_attrs={"driving_layup": 90, "three_point": 85, "pass_accuracy": 86},
            badges={"FearlessFinisher": 3, "Sniper": 3}
        ))
        # 温德尔·卡特
        writes.append(make_player_entry(
            name=roster[4][0], slot=4, face=roster[4][1], initiator=0,
            play_types=[15, 7, 8, 13],
            intangibles=86, touches=78, shot=75,
            extra_attrs={"three_point": 80, "interior_def": 85}
        ))
        # 科尔·安东尼 Cole Anthony (Slot 7, Face 7951)
        c_slot = 7 if 7 in roster else 0
        writes.append(make_player_entry(
            name=roster[c_slot][0], slot=c_slot, face=roster[c_slot][1], initiator=1,
            play_types=[4, 1, 15, 0],
            intangibles=86, touches=84, shot=85
        ))
        # 萨格斯 Jalen Suggs (Slot 0, Face 8051)
        writes.append(make_player_entry(
            name=roster[0][0], slot=0, face=roster[0][1], initiator=1,
            play_types=[4, 11, 0, 0],
            intangibles=85, touches=78, shot=75,
            extra_attrs={"perimeter_def": 92},
            badges={"Clamps": 3}
        ))
        # 富尔茨 / 艾萨克
        writes.append(make_player_entry(
            name=roster[1][0], slot=1, face=roster[1][1], initiator=1,
            play_types=[4, 14, 0, 0],
            intangibles=82, touches=76, shot=74
        ))

    # 其余 15 支球队的标准五虎配置 (自然排前 5 核心)
    else:
        # 取 roster 中前 5 个槽位
        slots = sorted(list(roster.keys()))[:5]
        for s_idx, slot_num in enumerate(slots):
            p_name, p_face = roster[slot_num]
            # 第 1 核心（如果是槽位 0 或 1）：
            if s_idx == 0:
                writes.append(make_player_entry(
                    name=p_name, slot=slot_num, face=p_face, initiator=1,
                    play_types=[4, 1, 15, 14],
                    intangibles=95, touches=92, shot=92
                ))
            elif s_idx == 1:
                writes.append(make_player_entry(
                    name=p_name, slot=slot_num, face=p_face, initiator=1,
                    play_types=[4, 1, 14, 15],
                    intangibles=90, touches=86, shot=86
                ))
            elif s_idx == 2:
                writes.append(make_player_entry(
                    name=p_name, slot=slot_num, face=p_face, initiator=0,
                    play_types=[15, 11, 1, 0],
                    intangibles=85, touches=78, shot=78
                ))
            elif s_idx == 3:
                writes.append(make_player_entry(
                    name=p_name, slot=slot_num, face=p_face, initiator=0,
                    play_types=[15, 8, 7, 0],
                    intangibles=84, touches=75, shot=75
                ))
            else:
                writes.append(make_player_entry(
                    name=p_name, slot=slot_num, face=p_face, initiator=0,
                    play_types=[7, 11, 0, 0],
                    intangibles=82, touches=70, shot=68
                ))

    return writes

def main():
    print("=" * 80)
    print("正在构建 NBA 2K22 30 队五虎现实化重构规格书 (v2.0 全维通用规范)...")
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
    print(f"  - 覆盖球员数: {spec['total_players']} 名核心五虎")
    print("=" * 80)

if __name__ == "__main__":
    main()
