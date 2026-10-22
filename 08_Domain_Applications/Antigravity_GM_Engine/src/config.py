# -*- coding: utf-8 -*-
"""
NBA 2K22 Antigravity 外部 GM 引擎配置与全局字典映射规范
提取并对齐自官方工具数据规范：PLAYER.json / TEAM.json / STAFF.json
"""

# ==========================================
# 1. 2K 游戏静态全局指针 (基于 NBA2K22.exe)
# ==========================================
# 全局控制台基址 (Trade & League Controller)
BASE_TRADE_CONTROLLER_OFFSET = 0x0632FAE8

# 全局控制台下关键偏移
TRADE_OFFSETS = {
    "TRADE_OVERRIDE": 0x168,       # 强制交易开关 (1: 开启, 0: 关闭)
    "CPU_CPU_TRADE": 0x170,        # CPU 与 CPU 间原生交易开关 (建议置 0 关闭)
    "FINANCIAL_RULES": 0x160,      # 工资帽硬规则校验开关
    "TRADE_DEADLINE": 0x16C,       # 交易截止日开关
    "TRADE_DIFFICULTY": 0x174,     # 交易难度
}

# 当前活跃/选中球员静态指针 (Active Player Pointer)
ACTIVE_PLAYER_STATIC_PTR_1 = 0x0632B410
ACTIVE_PLAYER_STATIC_PTR_2 = 0x0634B2F8

# ==========================================
# 2. 球队结构体规范 (TEAM.json)
# ==========================================
TEAM_STRUCT_STRIDE = 0x1258         # 球队数组步长: 精确 4,696 字节
TEAM_MAX_COUNT = 30                 # 现役核心球队总数
# 2K 内部 ID 7/30 保留给全明星槽位，夏洛特黄蜂使用 31。
# 以实际 30 支 NBA 球队 ID 集合作为校准标准，避免把全明星队或旧缓存算入。
CORE_TEAM_IDS = set(range(0, 7)) | set(range(8, 30)) | {31}

TEAM_OFFSETS = {
    "TEAM_NAME": 0x2B4,             # 队名 (UTF-16LE, 40字节, 如 Pacers)
    "CITY": 0x2E6,                  # 城市 (UTF-16LE, 40字节, 如 Indiana)
    "ABB": 0x30A,                   # 缩写 (UTF-16LE, 10字节, 如 IND)
    "UNIQUE_ID": 0xCA8,             # 球队唯一 ID (uint16; 核心现役 ID 集合见 CORE_TEAM_IDS)
    "TEAM_TYPE": 0xEEB,             # 球队类型 (5 bits): 0=现役(NORMAL), 1=经典(HISTORIC), 4/5=全明星
    "TOTAL_SALARY": 0xCBC,          # 球队总薪资 (uint32, 美元)
    "PAYROLL": 0xFF4,               # 发放薪资 (uint32)
    "BUDGET": 0x1014,               # 运营预算 (uint32)
    "CHEMISTRY": 0xEC4,             # 球队默契度 (float, 0.0 ~ 100.0)
    "FAN_INTEREST": 0xF7C,          # 球迷热度 (float)
}

# ==========================================
# 3. 主教练结构体规范 (STAFF.json)
# ==========================================
STAFF_OFFSETS = {
    "TEAM_ID": 0x60,                # 归属球队 ID (uint8)
    "OFFENSE": 0x100,               # 进攻战术等级
    "DEFENSE": 0x100,               # 防守战术等级
    "PREFERRED_SYSTEM": 0x10A,      # 首选战术体系 (3 bits)
    "ACTIVE_SYSTEM": 0x10B,         # 当前战术体系 (3 bits)
    "STYLE_1": 0x114,               # 建队风格 1
    "STYLE_2": 0x115,               # 建队风格 2
    "STYLE_3": 0x116,               # 建队风格 3
    "OFF_VS_DEF": 0x140,            # 攻守平衡偏好
    "PACE_SPACE_PROFICIENCY": 0xEE, # 跑轰空间体系熟练度 (0~100)
    "DEFENSE_PROFICIENCY": 0xF3,    # 防守战术体系熟练度 (0~100)
}

SYSTEM_OPTIONS = {
    0: "BALANCED",                  # 攻守均衡体系
    1: "GRIT_&_GRIND",              # 铁血防守阵地绞杀
    2: "PACE_&_SPACE",              # 跑轰空间与外线投射 (现代小球/步行者/勇士)
    3: "PERIMETER_CENTRIC",         # 外线持球突分主导
    4: "POST_CENTRIC",              # 低位大中锋阵地单打
    5: "TRIANGLE",                  # 三角进攻体系
    6: "SEVEN_SECONDS",             # 七秒极限跑轰
    7: "DEFENSE"                    # 全场施压强硬防守
}

STYLE_OPTIONS = {
    0: "NONE",
    1: "ATHLETICISM",               # 偏爱运动能力与爆发力
    2: "HIGH_IQ",                   # 偏爱高球商与视野
    3: "INTANGIBLES",               # 偏爱隐形贡献
    7: "SHOOTING_THREE",            # 偏爱三分投射
    8: "SHOT_CREATION",             # 偏爱自主进攻得分手
    9: "SIZE",                      # 偏爱体型高大化与臂展
    10: "SKILLS",                   # 偏爱全能基本功
    11: "TOUGHNESS",                # 偏爱坚韧硬汉
    12: "TRANSITION"                # 偏爱攻防转换推快攻
}

# ==========================================
# 4. 球员结构体规范 (PLAYER.json)
# ==========================================
PLAYER_STRUCT_STRIDE = 0xDF0        # 球员步长: 3,568 字节

PLAYER_OFFSETS = {
    # 基础信息
    "LAST_NAME": 0x0,               # 姓 (UTF-16LE, 40字节)
    "FIRST_NAME": 0x28,             # 名 (UTF-16LE, 40字节)
    "FACE_ID": 0x6C,                # 面补 ID (Cyberface ID, uint16)
    "CURRENT_TEAM": 0x60,           # uint64 pointer to current team; resolve using this capture's team map
    "CONTRACT_TEAM": 0xA8,          # uint64 pointer to contract team, not a byte ID
    "POSITION": 0xF9,               # 位置 (3 bits: 0=PG, 1=SG, 2=SF, 3=PF, 4=C)
    "SIGNATURE_ID": 0xE8,           # 赛场被动专属动画包 ID (uint32)
    "AUDIO_SIG_ID": 0xEC,           # 专属音效 ID (uint32)
    
    # 战术角色分配 (PlayType)
    "PLAY_TYPE_1": (0x168, 0, 4),   # 战术类型 1 (offset, startbit, size)
    "PLAY_TYPE_2": (0x168, 4, 4),   # 战术类型 2
    "PLAY_TYPE_3": (0x169, 0, 4),   # 战术类型 3
    "PLAY_TYPE_4": (0x169, 4, 4),   # 战术类型 4
    "PLAY_INITIATOR": 0x16A,        # 战术组织核心/持球发起人 (1 bit)
    
    # 合同信息
    "SALARY_YEAR_1": 0x1A4,         # 本年薪水 (uint32)
    "SALARY_YEAR_2": 0x1A8,
    "CONTRACT_YEARS_LEFT": 0x32E,   # 剩余年限原始字节 (需经 (raw >> 2) & 0x0F 提取)
    
    # 核心能力属性 (0~255 原生值, 公式: 25 + 原生值 / 3)
    "ATTR_DRIVING_LAYUP": 0x41F,    # 切入上篮
    "ATTR_SHOT_CLOSE": 0x424,       # 近距离投篮
    "ATTR_MID_RANGE": 0x425,        # 中距离投篮
    "ATTR_THREE_POINT": 0x426,      # 三分球 (3PT)
    "ATTR_FREE_THROW": 0x427,       # 罚球
    "ATTR_BALL_CONTROL": 0x428,     # 控球
    "ATTR_PASS_IQ": 0x429,          # 传球球商
    "ATTR_PASS_ACCURACY": 0x42A,    # 传球准确度
    "ATTR_OFF_REBOUND": 0x42B,      # 进攻篮板
    "ATTR_DEF_REBOUND": 0x42C,      # 防守篮板
    "ATTR_INTERIOR_DEF": 0x42D,     # 内线防守
    "ATTR_PERIMETER_DEF": 0x42E,    # 外线防守
    "ATTR_LATERAL_QUICK": 0x42F,    # 横向敏捷
    "ATTR_BLOCK": 0x431,            # 盖帽
    "ATTR_STEAL": 0x432,            # 抢断
    "ATTR_SPEED": 0x437,            # 速度
    "ATTR_SPEED_WITH_BALL": 0x438,  # 持球速度
    "ATTR_ACCELERATION": 0x439,     # 加速度
    "ATTR_VERTICAL": 0x43A,         # 弹跳
    "ATTR_STRENGTH": 0x43B,         # 力量
    "ATTR_STAMINA": 0x43C,          # 体力
    "ATTR_PASS_VISION": 0x453,      # 传球视野
    
    # 核心实战倾向 (0~100)
    "TEND_SHOT": 0x458,                         # 全场出手总倾向 (FGA/36 映射)
    "TEND_DRIVING_LAYUP": 0x459,                # 突破上篮
    "TEND_STANDING_DUNK": 0x45A,                # 原地扣篮
    "TEND_DRIVING_DUNK": 0x45B,                 # 突破扣篮
    "TEND_ALLEY_OOP": 0x45D,                    # 空接暴扣
    "TEND_PUTBACK": 0x45E,                      # 二次补篮
    "TEND_FLOATER": 0x463,                      # 禁区抛投
    "TEND_SHOT_CLOSE": 0x466,                   # 近距离投篮
    "TEND_SHOT_MID": 0x46A,                     # 中距离跳投基准
    "TEND_SHOT_THREE": 0x472,                   # 三分球跳投基准 (3PAr 映射)
    "TEND_SPOT_UP_THREE": 0x473,                # 定点三分
    "TEND_OFF_SCREEN_THREE": 0x474,             # 借掩护三分
    "TEND_STEPBACK_THREE": 0x47C,               # 后撤步三分
    "TEND_TRANSITION_PULLUP_THREE": 0x47F,      # 快攻追身三分
    "TEND_DRIVE_PULLUP_MID": 0x481,             # 突破急停中投
    "TEND_DRIVE": 0x483,                        # 持球突破意愿 (Drive Per Game 映射)
    "TEND_ATTACK_ON_DRIVE": 0x497,              # 强攻造杀伤
    "TEND_DISH_TO_OPEN_MAN": 0x498,             # 突破突分给空位
    "TEND_PASS_OPEN": 0x498,                    # 突分给空位别名
    "TEND_TOUCHES": 0x499,                      # 触球分配权重
    "TEND_POST_UP": 0x49A,                      # 低位背身
    "TEND_ROLL_VS_POP": 0x49B,                  # 挡拆顺下(0) vs 外拆(100)
    "TEND_PLAY_DISCIPLINE": 0x4A1,              # 战术纪律性
    "TEND_FLASHY_PASS": 0x4B2,                  # 花式传球
    "TEND_PASS_INTERCEPT": 0x4B4,               # 传球路线抢断
    "TEND_TAKE_CHARGE": 0x4B5,                  # 制造进攻犯规
    "TEND_ON_BALL_STEAL": 0x4B6,                # 持球逼抢断球
    "TEND_CONTEST_SHOT": 0x4B7,                 # 贴防干扰投篮 (垂直起跳)
    "TEND_BLOCK_SHOT": 0x4B8,                   # 起跳封盖
    "TEND_FOUL": 0x4B9,                         # 常规犯规
    "TEND_HARD_FOUL": 0x4BA                     # 凶狠犯规
}

PLAY_TYPES = {
    0: "NONE",
    1: "ISOLATION",
    4: "P&R_BALL_HANDLER",          # 挡拆持球发起人
    7: "P&R_ROLL_MAN",              # 挡拆顺下暴扣人
    8: "POST_UP_LOW",               # 低位背身
    11: "CUTTER",                   # 空切终结者
    12: "HAND_OFF",                 # 手递手策应
    13: "SPOT_UP"                   # 定点三分射手
}

# 能力值与游戏内 Rating 换算公式
def raw_to_rating(raw_val: int) -> int:
    """将内存原生 0~255 值换算为 2K 游戏内 25~99 评分"""
    return min(99, max(25, 25 + int(raw_val // 3)))

def rating_to_raw(rating: int) -> int:
    """将游戏内 25~99 评分换算为内存原生 0~255 值"""
    return min(255, max(0, int((rating - 25) * 3)))

def extract_contract_years(raw_byte: int) -> int:
    """从 0x32E 字节中提取 4-bit 剩余合同年限 (startbit: 2, size: 4)"""
    return (raw_byte >> 2) & 0x0F
