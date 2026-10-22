# NBA 2K22 核心数据结构与字节偏移全景规范 (Data Structure Specification)

本文档详尽定义了 NBA 2K22 在运行内存中的核心数据结构、内存对齐步长、绝对/相对偏移量（Offset）、数据类型（Data Types）及换算逻辑。本规范与官方导出数据标准 `PLAYER.json`、`TEAM.json`、`STAFF.json` 完全对齐，是任何存档读取、状态推演和修改注入的底层字典。

---

## 一、内存编码与字节对齐原则

1. **字节序（Endianness）：**
   * 采用标准 x86-64 小端序（Little Endian）。
2. **文本编码：**
   * 球员姓名、球队名、城市名均采用 **UTF-16LE**（双字节 Unicode）编码，字符串以 `\x00\x00` 结尾，通常预留 40~60 字节。
3. **结构体步长（Stride）：**
   * **球队结构体步长（Team Struct Stride）：** 精确为 `0x1258` 字节（十进制 4,696 字节）；
   * **球员结构体步长（Player Struct Stride）：** 精确为 `0xDF0` 字节（十进制 3,568 字节）。
4. **现役核心与历史/复古/全明星隔离准则：**
   * 2K22 存档中常驻数百支历史经典球队与全明星队，提取时必须严格过滤：
     * 校验 `TEAM_TYPE`（偏移 `0xEEB`）的低 5 位必须为 `0`（`NORMAL` 现役球队）；
     * 校验 `UNIQUE_ID`（偏移 `0xCA8`）必须在 `0 <= ID < 30` 范围内；
     * 提取球员时校验所属球队 `CURRENT_TEAM`（偏移 `0x60`）必须归属于现役 30 支核心球队，避免历史复古球员（如 84版乔丹、01版科比、12版詹姆斯）干扰决策引擎。

---

## 二、球队结构体全景规范 (Team Struct)

* **步长：** `0x1258` (4,696 字节)
* **现役数量：** 30 支核心 NBA 球队 (Team ID: 0 ~ 29)

| 偏移 (Offset) | 字段名 | 数据类型 | 长度/位数 | 取值范围与说明 |
| :--- | :--- | :--- | :--- | :--- |
| `0x2B4` | `TEAM_NAME` | UTF-16LE | 40 字节 | 队名（如 "Pacers", "Lakers", "Warriors"） |
| `0x2E6` | `CITY` | UTF-16LE | 40 字节 | 城市名（如 "Indiana", "Los Angeles"） |
| `0x30A` | `ABB` | UTF-16LE | 10 字节 | 球队缩写（3字符，如 "IND", "LAL", "GSW"） |
| `0xCA8` | `UNIQUE_ID` | uint16 | 2 字节 | 球队唯一逻辑 ID（0~29 对应现役 30 队） |
| `0xEEB` | `TEAM_TYPE` | uint8 (Bitfield) | 5 bits | **0: NORMAL(现役核心)**<br>1: HISTORIC(经典历史队)<br>4/5: ALLSTARS(全明星队) |
| `0xCBC` | `TOTAL_SALARY` | uint32 | 4 字节 | 球队全额保障总薪资（单位：美元） |
| `0xFF4` | `PAYROLL` | uint32 | 4 字节 | 球员实际发放薪资总和 |
| `0x1014` | `BUDGET` | uint32 | 4 字节 | 老板运营与引援总预算 |
| `0xEC4` | `CHEMISTRY` | float | 4 字节 | 球队更衣室默契度 / 化学反应 (0.00 ~ 100.00) |
| `0xF7C` | `FAN_INTEREST` | float | 4 字节 | 球迷支持度与球市热度 (0.00 ~ 100.00) |
| `0x10A8` | `ROSTER_COUNT` | uint8 | 1 字节 | 当前大名单活跃球员人数（通常 14~15 人） |

---

## 三、主教练与战术体系结构体 (Coach & Staff Struct)

主教练决定了球队的攻防基调、出手偏好、比赛节奏（Pace）以及新援契合度。

| 偏移 (Offset) | 字段名 | 数据类型 | 说明 |
| :--- | :--- | :--- | :--- |
| `0x60` | `TEAM_ID` | uint8 | 归属现役球队 ID (0~29) |
| `0x100` | `OFFENSE_RATING` | uint8 | 进攻战术等级与教鞭熟练度 (0~99) |
| `0x101` | `DEFENSE_RATING` | uint8 | 防守战术等级与教鞭熟练度 (0~99) |
| `0x10A` | `PREFERRED_SYSTEM` | uint8 (3 bits) | **主教练首选战术哲学** (枚举见下表) |
| `0x10B` | `ACTIVE_SYSTEM` | uint8 (3 bits) | **当前赛季正在执行的战术体系** |
| `0x114` | `STYLE_PREF_1` | uint8 | 建队风格偏好 1 (如 SHOOTING_THREE) |
| `0x115` | `STYLE_PREF_2` | uint8 | 建队风格偏好 2 (如 TRANSITION) |
| `0x116` | `STYLE_PREF_3` | uint8 | 建队风格偏好 3 (如 SIZE) |
| `0x140` | `OFF_VS_DEF` | uint8 | 攻防倾向：0=极端防守, 50=均衡, 100=跑轰极速 |
| `0xEE` | `PACE_SPACE_PROF` | uint8 | 空间与跑轰体系熟练度 (0~100) |
| `0xF3` | `DEFENSE_PROF` | uint8 | 防守绞杀体系熟练度 (0~100) |

### 战术体系枚举字典 (SYSTEM_OPTIONS)
* `0`: **BALANCED**（攻守均衡体系）
* `1`: **GRIT_&_GRIND**（铁血阵地绞杀，强调内线肉搏、防守与降速）
* `2`: **PACE_&_SPACE**（空间与现代小球，强调高频三分射手群与快速挡拆推进，步行者/勇士体系）
* `3`: **PERIMETER_CENTRIC**（外线核心突分主导）
* `4`: **POST_CENTRIC**（传统低位大中锋轴心打法）
* `5`: **TRIANGLE**（经典三角进攻体系）
* `6`: **SEVEN_SECONDS**（7秒极限跑轰纳什日式跑轰）
* `7`: **DEFENSE**（高压逼抢全场领防）

### 建队风格偏好枚举 (STYLE_OPTIONS)
* `1`: `ATHLETICISM`（极致爆发力与运动天赋）
* `2`: `HIGH_IQ`（高球商、传球视野与战术执行力）
* `7`: `SHOOTING_THREE`（三分投射与外线空间能力）
* `8`: `SHOT_CREATION`（硬解单打得分手）
* `9`: `SIZE`（体型高大化、臂展长、篮板保护）
* `11`: `TOUGHNESS`（铁血作风与领头羊硬汉气质）
* `12`: `TRANSITION`（防守反击与推快攻转换）

---

## 四、球员结构体全景规范 (Player Struct)

* **步长：** `0xDF0` (3,568 字节)
* **能力值换算公式：**
  $$\text{游戏内评分 (25~99)} = 25 + \left\lfloor \frac{\text{内存原生值 (0~255)}}{3} \right\rfloor$$
  $$\text{内存原生值 (0~255)} = \min\Big(255, \max\big(0, (\text{评分} - 25) \times 3\big)\Big)$$

### 1. 基础身份与外观
| 偏移 (Offset) | 字段名 | 类型 | 说明 |
| :--- | :--- | :--- | :--- |
| `0x0` | `LAST_NAME` | UTF-16LE (40B) | 姓氏（如 "Haliburton", "James"） |
| `0x28` | `FIRST_NAME` | UTF-16LE (40B) | 名字（如 "Tyrese", "LeBron"） |
| `0x60` | `CURRENT_TEAM` | uint8 | 当前所在球队 ID（0~29 现役，255 为自由球员） |
| `0xA8` | `CONTRACT_TEAM` | uint8 | 合同所属球队 ID |
| `0x6C` | `FACE_ID` | uint16 | 3D 面部面补 ID (Cyberface ID) |
| `0xF9` | `POSITION` | uint8 (3 bits) | 0: PG, 1: SG, 2: SF, 3: PF, 4: C |
| `0xFA` | `SEC_POSITION` | uint8 (3 bits) | 次要位置 (0~4) |
| `0xE8` | `SIGNATURE_ID` | uint32 | **球星赛场专属被动互动动画包 ID** |
| `0xEC` | `AUDIO_SIG_ID` | uint32 | **球星赛场专属音效/语音/裁判抱怨 ID** |

### 2. 战术角色分配 (PlayType & Initiator)
| 偏移 (Offset) | 字段名 | 位宽 | 描述 |
| :--- | :--- | :--- | :--- |
| `0x168 (Bit 0~3)` | `PLAY_TYPE_1` | 4 bits | 战术槽位 1（4: 挡拆持球人, 7: 挡拆顺下, 13: 定点射手） |
| `0x168 (Bit 4~7)` | `PLAY_TYPE_2` | 4 bits | 战术槽位 2 |
| `0x169 (Bit 0~3)` | `PLAY_TYPE_3` | 4 bits | 战术槽位 3 |
| `0x169 (Bit 4~7)` | `PLAY_TYPE_4` | 4 bits | 战术槽位 4 |
| `0x16A` | `PLAY_INITIATOR` | 1 bit | **全队战术发起人 / 主控核心** (1: 开启, 0: 关闭) |

### 3. 合同与年限
| 偏移 (Offset) | 字段名 | 类型 | 描述 |
| :--- | :--- | :--- | :--- |
| `0x1A4` | `SALARY_YEAR_1` | uint32 | 本赛季薪水（美元，如 $5,808,435） |
| `0x1A8` | `SALARY_YEAR_2` | uint32 | 第 2 年薪水 |
| `0x1AC` | `SALARY_YEAR_3` | uint32 | 第 3 年薪水 |
| `0x32E` | `CONTRACT_YEARS_LEFT` | uint8 | 合同剩余年限（1~5） |
| `0x32F` | `CONTRACT_OPTION` | uint8 | 0: 无选项, 1: 球队选项(Team), 2: 球员选项(Player) |

### 4. 攻防能力属性表 (0~255 原生值)
| 偏移 (Offset) | 属性代码 | 对应能力 | 典型值换算参考 |
| :--- | :--- | :--- | :--- |
| `0x41F` | `ATTR_DRIVING_LAYUP` | 切入上篮 | 原生 225 $\rightarrow$ 100 (99) |
| `0x424` | `ATTR_SHOT_CLOSE` | 近距离投篮 | 原生 210 $\rightarrow$ 95 |
| `0x425` | `ATTR_MID_RANGE` | 中距离投篮 | 原生 195 $\rightarrow$ 90 |
| `0x426` | `ATTR_THREE_POINT` | **三分球 (3PT)** | 原生 216 $\rightarrow$ 97, 原生 0 $\rightarrow$ 25 |
| `0x427` | `ATTR_FREE_THROW` | 罚球 | 原生 180 $\rightarrow$ 85 |
| `0x428` | `ATTR_BALL_CONTROL` | 控球手感 | 原生 213 $\rightarrow$ 96 |
| `0x429` | `ATTR_PASS_IQ` | 传球球商 | 原生 222 $\rightarrow$ 99 |
| `0x42A` | `ATTR_PASS_ACCURACY` | 传球准确度 | 原生 216 $\rightarrow$ 97 |
| `0x42D` | `ATTR_INTERIOR_DEF` | 内线防守 | 原生 90 $\rightarrow$ 55 |
| `0x42E` | `ATTR_PERIMETER_DEF` | 外线防守 | 原生 180 $\rightarrow$ 85 |
| `0x431` | `ATTR_BLOCK` | 盖帽 | 原生 75 $\rightarrow$ 50 |
| `0x432` | `ATTR_STEAL` | 抢断 | 原生 195 $\rightarrow$ 90 |
| `0x437` | `ATTR_SPEED` | 移动速度 | 原生 195 $\rightarrow$ 90 |
| `0x438` | `ATTR_SPEED_WITH_BALL`| 持球移动速度 | 原生 195 $\rightarrow$ 90 |
| `0x439` | `ATTR_ACCELERATION` | 加速度 | 原生 195 $\rightarrow$ 90 |
| `0x43A` | `ATTR_VERTICAL` | 弹跳高度 | 原生 150 $\rightarrow$ 75 |
| `0x43B` | `ATTR_STRENGTH` | 核心力量对抗 | 原生 120 $\rightarrow$ 65 |
| `0x43C` | `ATTR_STAMINA` | 耐力与体力池 | 原生 222 $\rightarrow$ 99 |
| `0x453` | `ATTR_PASS_VISION` | 传球视野 | 原生 225 $\rightarrow$ 100 (99) |

### 5. 核心实战倾向表 (0~100)
| 偏移 (Offset) | 倾向代码 | 描述 |
| :--- | :--- | :--- |
| `0x458` | `TEND_SHOT` | 整体投篮出手倾向 (0~100) |
| `0x498` | `TEND_PASS_OPEN` | 突分分球给空位队友倾向 (99=顶级传球大师) |
| `0x4B6` | `TEND_ON_BALL_STEAL` | 贴身逼抢下手断球倾向 |
| `0x4B7` | `TEND_CONTEST_SHOT` | 扑防投篮干扰倾向 |

### 6. 性格特征与关键先生位域 (0x4BB ~ 0x4C4)
| 偏移 (Offset) | Bit 掩码 | 性格名称 | 游戏内效果 |
| :--- | :--- | :--- | :--- |
| `0x4BB` | `Bit 1 (0x02)` | `ALPHA_DOG` | 领头羊：第四节落后时全能力暴增，主导进攻 |
| `0x4BC` | `Bit 1 (0x02)` | `RESERVED` | 内敛（开启后几乎不会有任何庆祝，需清除） |
| `0x4BD` | `Bit 1 (0x02)` | `FRIENDLY` | 友善：大幅增加更衣室默契度加成 |
| `0x4C0` | `Bit 0 (0x01)` | `PAT_MY_BACK` | 渴望认可与互动 |
| `0x4C0` | `Bit 1 (0x02)` | `EXPRESSIVE` | **极具表现力：高频触发抖肩、指表、挑衅与死球互动** |
| `0x4C1` | `Bit 1 (0x02)` | `LAID_BACK` | 悠闲（消极互动，需清除） |
| `0x4C4` | `Bit 2 (0x04)` | `CLUTCH_PERFORMER` | **关键先生：第四节或最后 2 分钟命中率提升** |

---

## 五、全局控制台结构体规范 (League Controller)

* **静态基址指针：** `NBA2K22.exe + 0x0632FAE8`

| 偏移 (Offset) | 控制项代码 | 类型 | 推荐配置与说明 |
| :--- | :--- | :--- | :--- |
| `0x168` | `TRADE_OVERRIDE` | uint32 | **强制交易开关**（1: 开启, 0: 关闭）。用于执行外部通过的合法交易方案。 |
| `0x170` | `CPU_CPU_TRADE` | uint32 | **CPU 原生交易开关**（推荐置 0 关闭，彻底杜绝 2K 原生弱智交易）。 |
| `0x160` | `FINANCIAL_RULES` | uint32 | 工资帽硬规则校验（1: 启用, 0: 忽略）。 |
| `0x16C` | `TRADE_DEADLINE` | uint32 | 交易截止日强制开关（1: 开启, 0: 关闭）。 |
| `0x174` | `TRADE_DIFFICULTY`| uint32 | 原生交易难度等级 (0~100)。 |

---

## 六、新秀名单与历史选秀池结构体 (Draft Class Struct)

在辉煌生涯（MC）或终极联盟（MyLEAGUE）的选秀阶段，系统在堆内存中维护一个固定的 **60 槽位新秀池数组**：
* **单体步长：** 同样复用 `0xDF0` 球员结构体；
* **顺位映射：** 槽位 `0 ~ 59` 对应首轮第 1 顺位至次轮第 30 顺位；
* **偷梁换柱注入点：** 在进入选秀前夕，将提前制作好的历史/真实新秀（如 2023 文班亚马、2022 班凯罗/切特、2025 弗拉格）数据，按顺位批量覆盖这 60 个槽位，即可在锁死的 MC 模式中实现加载真实历史/未来选秀名单。
