# -*- coding: utf-8 -*-
"""
Generate 15_LAL_stars_realism_mod.json and 06_LAC_stars_realism_mod.json
Worker: worker_08_lal_lac
"""
import json
import os

OUT_DIR = r"e:\workspace\Cybernetic_City_State_OS_v2 - nba2k22\08_Domain_Applications\Antigravity_GM_Engine\database\tactics\20261124_stars_realism_execution"

lal_spec = {
  "protocol_version": "v2.0_full_dimensional_native_mod",
  "task_package_id": "20261124_STARS_REALISM_REBALANCE",
  "team_id": 15,
  "team_abbr": "LAL",
  "team_name": "Los Angeles Lakers",
  "source_research_docs": [
    "62_LAL_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md",
    "88_2022_STARS_CONSENSUS_TIER1_SUPERSTARS.md",
    "91_2022_STARS_CONSENSUS_TIER3_ALLSTARS.md"
  ],
  "coaching_writes": [
    {
      "field_name": "active_system",
      "target_block": "COACHDATA",
      "offset": 267,
      "type": "uint8",
      "val_raw": 2,
      "current_in_game_val": 2,
      "desc": "Pace & Space / High-Low Motion",
      "decision_rationale": "维持以空间拉开、詹姆斯反击推土机与浓眉内线攻防为核心的体系配置"
    },
    {
      "field_name": "run_play_tendency",
      "target_block": "COACHDATA",
      "offset": 224,
      "type": "uint8",
      "val_raw": 75,
      "current_in_game_val": 75,
      "desc": "run_play_tendency: 75",
      "decision_rationale": "维持75战术执行力，保障高位挡拆与低位错位惩罚战术高频运转"
    },
    {
      "field_name": "help_defense",
      "target_block": "COACHDATA",
      "offset": 330,
      "type": "uint8",
      "val_raw": 80,
      "current_in_game_val": 4,
      "desc": "help_defense: 80",
      "decision_rationale": "【核心修复】原版仅4为严重失真漏洞，修正至80，全面释放浓眉与外线锋卫群禁区收缩协防威力"
    },
    {
      "field_name": "bench_depth",
      "target_block": "COACHDATA",
      "offset": 222,
      "type": "uint8",
      "val_raw": 9,
      "current_in_game_val": 9,
      "desc": "bench_depth: 9",
      "decision_rationale": "维持9人核心轮换结构"
    },
    {
      "field_name": "bench_utilization",
      "target_block": "COACHDATA",
      "offset": 312,
      "type": "uint8",
      "val_raw": 65,
      "current_in_game_val": 65,
      "desc": "bench_utilization: 65",
      "decision_rationale": "维持替补使用率配置"
    },
    {
      "field_name": "poe_defense",
      "target_block": "GAMEPLAN",
      "offset": 385,
      "type": "uint8",
      "val_raw": 13,
      "current_in_game_val": 13,
      "desc": "PROTECT_PAINT",
      "decision_rationale": "防守侧重收缩禁区，依托浓眉统治级禁区护筐阻击对手冲击篮筐"
    },
    {
      "field_name": "poe_offense",
      "target_block": "GAMEPLAN",
      "offset": 382,
      "type": "uint8",
      "val_raw": 2,
      "current_in_game_val": 2,
      "desc": "PUSH_THE_PACE",
      "decision_rationale": "进攻侧重快速推进反击，充分发挥詹姆斯坦克式转换快攻第一得分杀伤"
    }
  ],
  "player_writes": [
    {
      "player_name": "LeBron James",
      "roster_index": 2,
      "cyberface_id": 1013,
      "position": "SF/C",
      "tactical_playbook": {
        "is_play_initiator": 1,
        "play_types": [1, 4, 9, 11]
      },
      "modifications": [
        {
          "field": "touches",
          "target_block": "PLAYER_STRUCT",
          "offset": 1177,
          "type": "uint8",
          "val_raw": 98,
          "current_in_game_val": 86,
          "category": "TENDENCY",
          "decision_rationale": "【绝对第一球权】2022赛季场均30.3分8.2板6.2助攻，由86大幅提至98，确立全队绝对指挥官与战术发起者地位"
        },
        {
          "field": "shot_tendency",
          "target_block": "PLAYER_STRUCT",
          "offset": 1112,
          "type": "uint8",
          "val_raw": 95,
          "current_in_game_val": 92,
          "category": "TENDENCY",
          "decision_rationale": "【超级得分王欲望】由92微调至95，还原其关键时刻强突硬解与全天候反击得分爆发力"
        },
        {
          "field": "dish_to_open_man",
          "target_block": "PLAYER_STRUCT",
          "offset": 1176,
          "type": "uint8",
          "val_raw": 95,
          "current_in_game_val": 85,
          "category": "TENDENCY",
          "decision_rationale": "【历史级空位发牌】由85提至95，高位背身与突分时极强分球意愿，精确输送弱侧底角射手"
        },
        {
          "field": "drive_tendency",
          "target_block": "PLAYER_STRUCT",
          "offset": 1155,
          "type": "uint8",
          "val_raw": 96,
          "current_in_game_val": 95,
          "category": "TENDENCY",
          "decision_rationale": "【坦克强攻突破】阵地战半场大幅起步撕裂防线，直接冲击篮筐不惧对抗"
        },
        {
          "field": "roll_vs_pop",
          "target_block": "PLAYER_STRUCT",
          "offset": 1184,
          "type": "uint8",
          "val_raw": 40,
          "current_in_game_val": 65,
          "category": "TENDENCY",
          "decision_rationale": "【小球中锋顺下】客串中锋时挡拆偏向内切顺下攻筐（40），修正原版过度外弹（65）"
        },
        {
          "field": "shot_three",
          "target_block": "PLAYER_STRUCT",
          "offset": 1182,
          "type": "uint8",
          "val_raw": 85,
          "current_in_game_val": 85,
          "category": "TENDENCY",
          "decision_rationale": "【追分超远干拔】维持85三分投射倾向，2022赛季场均出手8.0记三分"
        },
        {
          "field": "block_shot",
          "target_block": "PLAYER_STRUCT",
          "offset": 1208,
          "type": "uint8",
          "val_raw": 92,
          "current_in_game_val": 78,
          "category": "TENDENCY",
          "decision_rationale": "【招牌追身钉板帽】由78提至92，只要对手反击单刀必定全力回追送出震撼排球封盖"
        },
        {
          "field": "contest_shot",
          "target_block": "PLAYER_STRUCT",
          "offset": 1207,
          "type": "uint8",
          "val_raw": 88,
          "current_in_game_val": 82,
          "category": "TENDENCY",
          "decision_rationale": "【防守威慑】由82提至88，扬手干扰投篮态度积极"
        },
        {
          "field": "foul_tendency",
          "target_block": "PLAYER_STRUCT",
          "offset": 1209,
          "type": "uint8",
          "val_raw": 42,
          "current_in_game_val": 58,
          "category": "TENDENCY",
          "decision_rationale": "【防守犯规安全锁】由58下调至42安全阈值，防守干净杜绝模拟中频繁犯规下场"
        },
        {
          "field": "strength",
          "target_block": "PLAYER_STRUCT",
          "offset": 1083,
          "type": "uint8",
          "val_raw": 201,
          "current_in_game_val": 180,
          "category": "ATTRIBUTE",
          "decision_rationale": "【不老重型坦克力道】力量评级从85提至92 (Raw: 201)，突破抗撞生吃各路侧翼"
        },
        {
          "field": "stamina",
          "target_block": "PLAYER_STRUCT",
          "offset": 1082,
          "type": "uint8",
          "val_raw": 213,
          "current_in_game_val": 200,
          "category": "ATTRIBUTE",
          "decision_rationale": "【季后赛体能耐力】耐力评级锁定96 (Raw: 213)，场均出战37.2分钟历史级消耗支撑"
        }
      ]
    },
    {
      "player_name": "Anthony Davis",
      "roster_index": 3,
      "cyberface_id": 2444,
      "position": "PF/C",
      "tactical_playbook": {
        "is_play_initiator": 0,
        "play_types": [8, 7, 14, 11]
      },
      "modifications": [
        {
          "field": "touches",
          "target_block": "PLAYER_STRUCT",
          "offset": 1177,
          "type": "uint8",
          "val_raw": 90,
          "current_in_game_val": 82,
          "category": "TENDENCY",
          "decision_rationale": "【前场第一终结】由82提至90，确立湖人内线首要攻筐与低位强打顺位"
        },
        {
          "field": "shot_tendency",
          "target_block": "PLAYER_STRUCT",
          "offset": 1112,
          "type": "uint8",
          "val_raw": 92,
          "current_in_game_val": 92,
          "category": "TENDENCY",
          "decision_rationale": "【高效终结欲望】维持92主力内线终结火力，场均贡献23.2分"
        },
        {
          "field": "roll_vs_pop",
          "target_block": "PLAYER_STRUCT",
          "offset": 1184,
          "type": "uint8",
          "val_raw": 35,
          "current_in_game_val": 25,
          "category": "TENDENCY",
          "decision_rationale": "【顺下攻筐偏向】锁定35，挡拆后极度偏向内切顺下空接与短顺下抛投，极少拉出外弹"
        },
        {
          "field": "shot_three",
          "target_block": "PLAYER_STRUCT",
          "offset": 1182,
          "type": "uint8",
          "val_raw": 30,
          "current_in_game_val": 70,
          "category": "TENDENCY",
          "decision_rationale": "【三分克制纠偏】2022赛季三分命中率仅18.6%，由70大幅压制至30，杜绝盲目漂移外线三分"
        },
        {
          "field": "block_shot",
          "target_block": "PLAYER_STRUCT",
          "offset": 1208,
          "type": "uint8",
          "val_raw": 96,
          "current_in_game_val": 92,
          "category": "TENDENCY",
          "decision_rationale": "【全天候禁飞区】场均2.3盖帽，由92提升至96，防守端绝对擎天柱火锅威慑"
        },
        {
          "field": "contest_shot",
          "target_block": "PLAYER_STRUCT",
          "offset": 1207,
          "type": "uint8",
          "val_raw": 96,
          "current_in_game_val": 98,
          "category": "TENDENCY",
          "decision_rationale": "【禁区干扰】维持96极高内线投篮干扰意愿"
        },
        {
          "field": "foul_tendency",
          "target_block": "PLAYER_STRUCT",
          "offset": 1209,
          "type": "uint8",
          "val_raw": 42,
          "current_in_game_val": 62,
          "category": "TENDENCY",
          "decision_rationale": "【防守犯规安全锁】由62严格压制至42安全阈值，防守起跳干净，杜绝模拟中频繁犯规毕业"
        },
        {
          "field": "strength",
          "target_block": "PLAYER_STRUCT",
          "offset": 1083,
          "type": "uint8",
          "val_raw": 189,
          "current_in_game_val": 170,
          "category": "ATTRIBUTE",
          "decision_rationale": "【内线对抗力量】力量评级从82提升至88 (Raw: 189)，顶防传统重型内线不吃亏"
        },
        {
          "field": "interior_def",
          "target_block": "PLAYER_STRUCT",
          "offset": 1069,
          "type": "uint8",
          "val_raw": 210,
          "current_in_game_val": 195,
          "category": "ATTRIBUTE",
          "decision_rationale": "【禁飞区护筐屏障】内线防守评级提升至95 (Raw: 210)，撑起湖人防守体系"
        }
      ]
    }
  ]
}

lac_spec = {
  "protocol_version": "v2.0_full_dimensional_native_mod",
  "task_package_id": "20261124_STARS_REALISM_REBALANCE",
  "team_id": 6,
  "team_abbr": "LAC",
  "team_name": "LA Clippers",
  "source_research_docs": [
    "61_LAC_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md",
    "90_2022_STARS_CONSENSUS_TIER2_WINGS_BIGS.md"
  ],
  "coaching_writes": [
    {
      "field_name": "active_system",
      "target_block": "COACHDATA",
      "offset": 267,
      "type": "uint8",
      "val_raw": 2,
      "current_in_game_val": 2,
      "desc": "Pace & Space / Dual Wings ISO",
      "decision_rationale": "维持以空间拉开、双向侧翼单打与中距离硬解为核心的战术体系"
    },
    {
      "field_name": "run_play_tendency",
      "target_block": "COACHDATA",
      "offset": 224,
      "type": "uint8",
      "val_raw": 75,
      "current_in_game_val": 75,
      "desc": "run_play_tendency: 75",
      "decision_rationale": "维持75半场战术调用频率，保障伦纳德与乔治高位掩护中投战术执行"
    },
    {
      "field_name": "help_defense",
      "target_block": "COACHDATA",
      "offset": 330,
      "type": "uint8",
      "val_raw": 80,
      "current_in_game_val": 75,
      "desc": "help_defense: 80",
      "decision_rationale": "【协防提升】由75微调至80，最大化发挥全锋线五小阵容换防扫荡与死亡缠绕协防截断"
    },
    {
      "field_name": "bench_depth",
      "target_block": "COACHDATA",
      "offset": 222,
      "type": "uint8",
      "val_raw": 9,
      "current_in_game_val": 9,
      "desc": "bench_depth: 9",
      "decision_rationale": "维持9人核心轮换结构"
    },
    {
      "field_name": "bench_utilization",
      "target_block": "COACHDATA",
      "offset": 312,
      "type": "uint8",
      "val_raw": 65,
      "current_in_game_val": 65,
      "desc": "bench_utilization: 65",
      "decision_rationale": "维持替补使用率配置"
    },
    {
      "field_name": "poe_defense",
      "target_block": "GAMEPLAN",
      "offset": 385,
      "type": "uint8",
      "val_raw": 14,
      "current_in_game_val": 14,
      "desc": "PHYSICAL_DEFENSE",
      "decision_rationale": "防守侧重身体强硬对抗，利用顶级侧翼尺寸与力量进行高压逼抢"
    },
    {
      "field_name": "poe_offense",
      "target_block": "GAMEPLAN",
      "offset": 382,
      "type": "uint8",
      "val_raw": 1,
      "current_in_game_val": 1,
      "desc": "PATIENT_OFFENSE",
      "decision_rationale": "进攻侧重耐心寻觅错位，主打伦纳德与乔治的中距离干拔单挑硬解"
    }
  ],
  "player_writes": [
    {
      "player_name": "Kawhi Leonard",
      "roster_index": 2,
      "cyberface_id": 2143,
      "position": "SF",
      "tactical_playbook": {
        "is_play_initiator": 1,
        "play_types": [1, 14, 8, 4]
      },
      "modifications": [
        {
          "field": "touches",
          "target_block": "PLAYER_STRUCT",
          "offset": 1177,
          "type": "uint8",
          "val_raw": 92,
          "current_in_game_val": 86,
          "category": "TENDENCY",
          "decision_rationale": "【终极硬解球权】由86提升至92，确立快船阵地战第一错位单挑核心顺位"
        },
        {
          "field": "shot_tendency",
          "target_block": "PLAYER_STRUCT",
          "offset": 1112,
          "type": "uint8",
          "val_raw": 94,
          "current_in_game_val": 95,
          "category": "TENDENCY",
          "decision_rationale": "【效率机器欲望】维持94，极高投篮把握度，中距离后仰与低位硬解无解终结"
        },
        {
          "field": "dish_to_open_man",
          "target_block": "PLAYER_STRUCT",
          "offset": 1176,
          "type": "uint8",
          "val_raw": 75,
          "current_in_game_val": 70,
          "category": "TENDENCY",
          "decision_rationale": "【包夹分球提升】由70微调至75，面对侧翼重重包夹沉着分球给外线空位投手"
        },
        {
          "field": "roll_vs_pop",
          "target_block": "PLAYER_STRUCT",
          "offset": 1184,
          "type": "uint8",
          "val_raw": 0,
          "current_in_game_val": 0,
          "category": "TENDENCY",
          "decision_rationale": "【持球大核锋线】顺下外弹倾向锁定为0"
        },
        {
          "field": "shot_three",
          "target_block": "PLAYER_STRUCT",
          "offset": 1182,
          "type": "uint8",
          "val_raw": 82,
          "current_in_game_val": 85,
          "category": "TENDENCY",
          "decision_rationale": "【三分投射克制】由85微调至82，以中距离干拔与低位背身单打为主打武器"
        },
        {
          "field": "on_ball_steal",
          "target_block": "PLAYER_STRUCT",
          "offset": 1206,
          "type": "uint8",
          "val_raw": 95,
          "current_in_game_val": 95,
          "category": "TENDENCY",
          "decision_rationale": "【招牌死亡缠绕】巨掌精准掏球，对持球人构成顶级抢断威胁"
        },
        {
          "field": "contest_shot",
          "target_block": "PLAYER_STRUCT",
          "offset": 1207,
          "type": "uint8",
          "val_raw": 96,
          "current_in_game_val": 98,
          "category": "TENDENCY",
          "decision_rationale": "【顶级外防干扰】维持96超强投篮干扰态度"
        },
        {
          "field": "foul_tendency",
          "target_block": "PLAYER_STRUCT",
          "offset": 1209,
          "type": "uint8",
          "val_raw": 40,
          "current_in_game_val": 55,
          "category": "TENDENCY",
          "decision_rationale": "【历史级防守纪律】由55压制至40安全阈值，抢断极其干净绝不盲目下手，防模拟犯规"
        },
        {
          "field": "strength",
          "target_block": "PLAYER_STRUCT",
          "offset": 1083,
          "type": "uint8",
          "val_raw": 189,
          "current_in_game_val": 175,
          "category": "ATTRIBUTE",
          "decision_rationale": "【重型装甲车对抗】力量评级从83提至88 (Raw: 189)，下盘扎实抗撞顶级"
        },
        {
          "field": "perimeter_def",
          "target_block": "PLAYER_STRUCT",
          "offset": 1070,
          "type": "uint8",
          "val_raw": 213,
          "current_in_game_val": 200,
          "category": "ATTRIBUTE",
          "decision_rationale": "【外线死亡死锁】外线单防评级提升至96 (Raw: 213)，历史最强单防侧翼模板"
        }
      ]
    },
    {
      "player_name": "Paul George",
      "roster_index": 1,
      "cyberface_id": 1810,
      "position": "SF/SG",
      "tactical_playbook": {
        "is_play_initiator": 1,
        "play_types": [1, 4, 15, 14]
      },
      "modifications": [
        {
          "field": "touches",
          "target_block": "PLAYER_STRUCT",
          "offset": 1177,
          "type": "uint8",
          "val_raw": 90,
          "current_in_game_val": 84,
          "category": "TENDENCY",
          "decision_rationale": "【持球双核掌控】由84提升至90，兼具高位挡拆持球发起与全场推转换重任"
        },
        {
          "field": "shot_tendency",
          "target_block": "PLAYER_STRUCT",
          "offset": 1112,
          "type": "uint8",
          "val_raw": 92,
          "current_in_game_val": 92,
          "category": "TENDENCY",
          "decision_rationale": "【得分主力顺位】维持92主力分卫终结火力"
        },
        {
          "field": "dish_to_open_man",
          "target_block": "PLAYER_STRUCT",
          "offset": 1176,
          "type": "uint8",
          "val_raw": 78,
          "current_in_game_val": 70,
          "category": "TENDENCY",
          "decision_rationale": "【突分组织提升】由70提升至78，挡拆突刺后分球外线射手"
        },
        {
          "field": "roll_vs_pop",
          "target_block": "PLAYER_STRUCT",
          "offset": 1184,
          "type": "uint8",
          "val_raw": 0,
          "current_in_game_val": 0,
          "category": "TENDENCY",
          "decision_rationale": "【持球外线】顺下外弹倾向锁定为0"
        },
        {
          "field": "shot_three",
          "target_block": "PLAYER_STRUCT",
          "offset": 1182,
          "type": "uint8",
          "val_raw": 92,
          "current_in_game_val": 92,
          "category": "TENDENCY",
          "decision_rationale": "【丝滑干拔三分】维持92三分高频出手，招牌急停干拔与底角跑动三分"
        },
        {
          "field": "pass_interception",
          "target_block": "PLAYER_STRUCT",
          "offset": 1205,
          "type": "uint8",
          "val_raw": 90,
          "current_in_game_val": 82,
          "category": "TENDENCY",
          "decision_rationale": "【传球路线截断】由82提升至90，长臂幽灵预判截断快攻反击"
        },
        {
          "field": "on_ball_steal",
          "target_block": "PLAYER_STRUCT",
          "offset": 1206,
          "type": "uint8",
          "val_raw": 88,
          "current_in_game_val": 92,
          "category": "TENDENCY",
          "decision_rationale": "【贴防掏球】维持88高压领防掏球"
        },
        {
          "field": "contest_shot",
          "target_block": "PLAYER_STRUCT",
          "offset": 1207,
          "type": "uint8",
          "val_raw": 90,
          "current_in_game_val": 86,
          "category": "TENDENCY",
          "decision_rationale": "【外线防守干扰】由86提升至90，侧翼防守扬手干扰积极性"
        },
        {
          "field": "foul_tendency",
          "target_block": "PLAYER_STRUCT",
          "offset": 1209,
          "type": "uint8",
          "val_raw": 44,
          "current_in_game_val": 60,
          "category": "TENDENCY",
          "decision_rationale": "【防守犯规安全锁】由60下调至44安全阈值，避免外线手部微小犯规累积"
        },
        {
          "field": "strength",
          "target_block": "PLAYER_STRUCT",
          "offset": 1083,
          "type": "uint8",
          "val_raw": 165,
          "current_in_game_val": 150,
          "category": "ATTRIBUTE",
          "decision_rationale": "【侧翼对抗力量】力量评级提升至80 (Raw: 165)，保证突破撞击后稳定性"
        }
      ]
    }
  ]
}

os.makedirs(OUT_DIR, exist_ok=True)

lal_path = os.path.join(OUT_DIR, "15_LAL_stars_realism_mod.json")
with open(lal_path, "w", encoding="utf-8") as f:
    json.dump(lal_spec, f, indent=2, ensure_ascii=False)
print(f"Generated {lal_path} ({os.path.getsize(lal_path)} bytes)")

lac_path = os.path.join(OUT_DIR, "06_LAC_stars_realism_mod.json")
with open(lac_path, "w", encoding="utf-8") as f:
    json.dump(lac_spec, f, indent=2, ensure_ascii=False)
print(f"Generated {lac_path} ({os.path.getsize(lac_path)} bytes)")
