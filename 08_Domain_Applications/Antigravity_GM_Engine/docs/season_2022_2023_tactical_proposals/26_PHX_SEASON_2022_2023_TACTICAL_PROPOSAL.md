# ☀️ 菲尼克斯太阳 (PHX) 2022-2023 赛季 Day 1 全维度战术体系与攻防博弈方案
# (Phoenix Suns Season 2022-2023 Day 1 Tactical & Game-Theoretic Proposal)

> **文档标识**: `26_PHX_SEASON_2022_2023_TACTICAL_PROPOSAL.md`  
> **继承基线**: [`54_PHX_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md`](file:///e:/workspace/Cybernetic_City_State_OS_v2%20-%20nba2k22/08_Domain_Applications/Antigravity_GM_Engine/docs/54_PHX_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md)  
> **关联标准**: `43_FULL_DIMENSIONAL_NATIVE_MOD_PROTOCOL_V2.md` | `49_NBA2K22_TACTICAL_SYSTEM_AND_GAME_THEORETIC_TUNING_STANDARD.md` | `85_PLAYER_TENDENCIES_FULL_DIMENSIONAL_CALIBRATION_STANDARD.md` | `86_PLAYER_TRAINING_TEMPLATES_AND_LOAD_MANAGEMENT_STANDARD.md`  
> **目标快照**: `C:\nba2k22\saves\MyLEAGUE0005\league_state.sqlite` (`snapshot_id = '2022-2023_M01_NOV'`)  
> **球队标识**: `Team ID: 26 | Team Abbr: PHX | 球队名称: Phoenix Suns`  
> **主教练**: 蒙蒂·威廉姆斯 (Monty Williams) | **执行规格书**: `C:\nba2k22\exports\20261125_season2_day1_tactical_execution\26_PHX_season2_tactical_mod.json`

---

## 1. 2022-2023 新赛季阵容审计与休赛期变动 (Roster & Offseason Changes)

基于 `league_state.sqlite` 快照 `2022-2023_M01_NOV` 对菲尼克斯太阳队（Team ID: 26）16 人激活与储备名单进行全量核验，新赛季球队发生了震动联盟的超级重磅重构：

### 1.1 核心休赛期变动与新援落位
* **超级巨星空降**：**凯文·杜兰特 (Kevin Durant, Slot 4, CF=1411, 34岁)** 正式加盟太阳，与德文·布克、克里斯·保罗、德安德烈·艾顿组成全联盟最具中距离与空间毁灭力的四巨头！
* **离队人员**：米卡尔·布里奇斯 (Mikal Bridges)、卡梅隆·约翰逊 (Cameron Johnson)、贾·克劳德 (Jae Crowder)、贾维尔·麦基 (JaVale McGee)、达里奥·萨里奇 (Dario Saric) 等上赛季核心轮换与拼图离队。
* **新援与年轻拼图**：
  * **特伦斯·罗斯 (Terrence Ross, Slot 8, CF=2451, 31岁)**：二阵容微波炉外线得分手；
  * **达里厄斯·贝兹利 (Darius Bazley, Slot 7, CF=7842, 22岁)**：运动型锋线内线轮换；
  * **乔什·奥科吉 (Josh Okogie, Slot 11, CF=7719, 24岁)**：外线领防撕咬尖兵（外防 82）；
  * **达米恩·李 (Damion Lee, Slot 12, CF=7652, 30岁)**、**萨本·李 (Saben Lee, Slot 5, CF=9836, 23岁)**；
  * **1984 历史新秀落位**：**杰·汉弗莱斯 (Jay Humphries, Slot 13, CF=1756, 22岁)** 入驻太阳储备后场；另有 **Brendan Aldridge (Slot 3, CF=1, 22岁)**、**Jared Harper (Slot 21, CF=7908)**、**Wilson Price (Slot 22, CF=1)**。
* **保留班底**：克里斯·保罗 (Slot 0, 37岁)、德文·布克 (Slot 1, 26岁)、德安德烈·艾顿 (Slot 9, 24岁)、托里·克雷格 (Slot 6, 31岁)、卡梅隆·佩恩 (Slot 2, 28岁)、兰德里·沙梅特 (Slot 10, 25岁)。

### 1.2 数据库实测四大失真痛点
1. **三核球权严重超载踩踏**：杜兰特 (`touches=98, shot=98`)、保罗 (`touches=95, disc=20`)、布克 (`touches=86, disc=40`) 加上艾顿 (`touches=63`) 与克雷格 (`touches=34`)，先发五虎触球和高达 **376**（远超 `[310, 330]` 黄金守恒区间），且保罗/克雷格/艾顿战术纪律低至 `20~30`，极易出现乱投与持球停滞。
2. **教练宏观体系与协防参数失真**：`ActiveSystem` 为 `7 (DEFENSE)` 而非 `2 (PACE_AND_SPACE)`；`HelpDefense` 跌至 **37**（协防形同虚设），`BenchUtilization` 高达 **76**（过度消耗替补挤压四核时间）。
3. **艾顿与杜兰特挡拆倾向错位**：艾顿 `roll_vs_pop = 35`（需压低至 `18` 强化 82% 顺下空接），杜兰特 `roll_vs_pop = 15`（需纠偏至 `75` 发挥外弹三分/中投高炮台威力）。
4. **3D 侧翼外线果断性不足**：托里·克雷格 `shot_three = 48`、奥科吉 `shot_three = 32` 且 `roll_vs_pop = 80`，急需纠偏以防底角拒投。

---

## 2. 10 人核心轮换架构与球权守恒 (10-Man Rotation & Touches Conservation)

> **轮换时间闭环**：先发 5 人 `160.0` 分钟 + 替补 5 人 `80.0` 分钟 = **`240.0` 人·分**。  
> **触球和校验**：先发五虎 `70 + 84 + 36 + 86 + 52 = 328` ($\in [310, 330]$)；第二阵容 `62 + 60 + 48 + 40 + 50 = 260` ($\in [250, 280]$)。

| 梯队 | 槽位 | 球员姓名 | 位置 | 年龄 | 出场时间 | 发起 (`Init`) | 触球 (`Tch`) | 出手 (`Shot`) | 纪律 (`Disc`) | 外弹 (`R/P`) | 战术类型 (`PlayTypes`) |
| :---: | :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **先发** | 0 | **Chris Paul** | PG | 37 | 32.0 | 1 | **70** (95) | **72** (78) | **88** (20) | 0 | `[4, 13, 1, 12]` |
| **先发** | 1 | **Devin Booker** | SG | 26 | 36.0 | 1 | **84** (86) | **88** (94) | **78** (40) | 20 | `[4, 1, 13, 15]` |
| **先发** | 6 | **Torrey Craig** | SF | 31 | 24.0 | 0 | **36** (34) | **48** (41) | **90** (20) | **65** (20) | `[15, 11, 0, 0]` |
| **先发** | 4 | **Kevin Durant** | PF | 34 | 36.0 | 1 | **86** (98) | **90** (98) | **75** (50) | **75** (15) | `[1, 14, 15, 9]` |
| **先发** | 9 | **Deandre Ayton** | C | 24 | 32.0 | 0 | **52** (63) | **65** (78) | **85** (30) | **18** (35) | `[7, 8, 11, 14]` |
| **替补** | 2 | **Cameron Payne** | PG | 28 | 20.0 | 1 | **62** (55) | **68** (66) | **75** (52) | 0 | `[4, 1, 15, 0]` |
| **替补** | 8 | **Terrence Ross** | SG | 31 | 18.0 | 0 | **60** (53) | **76** (73) | **80** (55) | 0 | `[15, 12, 1, 0]` |
| **替补** | 10 | **Landry Shamet** | SG | 25 | 16.0 | 0 | **48** (42) | **66** (60) | **88** (15) | 10 | `[15, 12, 4, 0]` |
| **替补** | 11 | **Josh Okogie** | SF | 24 | 14.0 | 0 | **40** (32) | **46** (39) | **88** (60) | **30** (80) | `[11, 15, 0, 0]` |
| **替补** | 7 | **Darius Bazley** | PF | 22 | 12.0 | 0 | **50** (56) | **55** (58) | **82** (15) | 35 | `[11, 7, 15, 0]` |

*(注：储备阵容包含 1984 新秀 Jay Humphries (Slot 13, 22岁)、Damion Lee (Slot 12)、Saben Lee (Slot 5) 等作为伤病与垃圾时间深度替补。)*

---

## 3. 攻防博弈体系与模拟侧重 (Doc 49 攻守并重架构)

### 3.1 进攻博弈：三核中距离引力 + 艾顿顺下 + 双外线空间
* **核心机制**：保罗 (`Touches=70, Dish=94`) 负责高位挡拆发牌，杜兰特 (`Scoring Option 1, Mid 99, 3PT 91`) 与布克 (`Scoring Option 2, Mid 95`) 构成历史级无解中远投双核；艾顿 (`Scoring Option 3, RollPop=18`) 专职顺下吃饼。任何对 KD 或布克的夹击都将立刻惩罚弱侧底角克雷格/沙梅特/罗斯的三分火力。

### 3.2 防守博弈：克雷格/奥科吉外线抢过 + 艾顿沉退 + 高位协防网
* **人员支撑与反制策略**：失去大桥与克劳德后，太阳外线领防由 **Torrey Craig (外防 77, 内防 71)** 与替补 **Josh Okogie (外防 82)** 承担抢过掩护任务，**Kevin Durant (内防 69, 盖帽 74, 外防 79)** 提供锋线扫荡护筐协防，**Deandre Ayton (内防 76, 盖帽 76)** 沉退守护油漆区。
* **教练与 POE 关键修正**：
  * `active_system`: `7 -> 2` (`PACE_AND_SPACE`)；`help_defense`: `37 -> 78`；`bench_depth`: `9 -> 10`；`bench_utilization`: `76 -> 58`；`run_play_tendency`: `85 -> 75`。
  * `GAMEPLAN` 模拟侧重：`scoring_option_1 = 1411 (Durant)`、`scoring_option_2 = 4387 (Booker)`、`scoring_option_3 = 7700 (Ayton)`。
  * **6 大 POE**：`poe_offense = 4 (PICK_AND_ROLL_OFFENSE)`、`poe_offense_tempo = 8 (NEUTRAL)`、`poe_offense_rebound = 12 (LIMIT_TRANSITION)`、`poe_defense = 15 (LIMIT_PERIMETER_SHOTS)`、`poe_defense_physicality = 18 (PLAY_PHYSICAL)`、`poe_defense_rebound = 19 (CRASH_DEFENSIVE_BOARDS)`。

---

## 4. 个人训练模板与防伤负荷管理 (Doc 86 标准)

严格遵循 **“≤24 岁 `intensity=3`，≥25/26 岁 `intensity=2`，全员 `is_intensity_overriden=1`”**：
* **成长梯队 (`intensity = 3`)**：Deandre Ayton (24岁, `C + INSIDE=8`)、Josh Okogie (24岁, `SF + DEFENSIVE=3`)、Darius Bazley (22岁, `PF + ATHLETIC=4`)。
* **巅峰/老将负荷梯队 (`intensity = 2`)**：Chris Paul (37岁, `PG + PLAYMAKING=6`)、Kevin Durant (34岁, `PF + OFFENSIVE=2`)、Devin Booker (26岁, `SG + OFFENSIVE=2`)、Torrey Craig (31岁, `SF + TWO_WAY=1`)、Cameron Payne (28岁, `PG + PLAYMAKING=6`)、Terrence Ross (31岁, `SG + OFFENSIVE=2`)、Landry Shamet (25岁, `SG + OUTSIDE=7`)。
* **犯规红线核验**：全队 10 人原生 `foul` (`0x4B9`) 均处于 `28 ~ 44` 区间，100% 满足 `foul <= 50` 安全红线。
