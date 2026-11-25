# 亚特兰大老鹰 (ATL) 2022-2023 新赛季 (Day 1) 全维度战术与博弈研究报告

> **球队标识**: `team_id = 9` | `ATL` | `Atlanta Hawks`  
> **数据快照**: `2022-2023_M01_NOV` (`league_state.sqlite` 实机只读萃取)  
> **执教主帅**: 内特·麦克米兰 (Nate McMillan, `staff_slot = 7`)  
> **关联标准**: [43_FULL_DIMENSIONAL_NATIVE_MOD_PROTOCOL_V2.md](file:///e:/workspace/Cybernetic_City_State_OS_v2%20-%20nba2k22/08_Domain_Applications/Antigravity_GM_Engine/docs/43_FULL_DIMENSIONAL_NATIVE_MOD_PROTOCOL_V2.md) | [49_NBA2K22_TACTICAL_SYSTEM_AND_GAME_THEORETIC_TUNING_STANDARD.md](file:///e:/workspace/Cybernetic_City_State_OS_v2%20-%20nba2k22/08_Domain_Applications/Antigravity_GM_Engine/docs/49_NBA2K22_TACTICAL_SYSTEM_AND_GAME_THEORETIC_TUNING_STANDARD.md) | [85_PLAYER_TENDENCIES_FULL_DIMENSIONAL_CALIBRATION_STANDARD.md](file:///e:/workspace/Cybernetic_City_State_OS_v2%20-%20nba2k22/08_Domain_Applications/Antigravity_GM_Engine/docs/85_PLAYER_TENDENCIES_FULL_DIMENSIONAL_CALIBRATION_STANDARD.md) | [86_PLAYER_TRAINING_TEMPLATES_AND_LOAD_MANAGEMENT_STANDARD.md](file:///e:/workspace/Cybernetic_City_State_OS_v2%20-%20nba2k22/08_Domain_Applications/Antigravity_GM_Engine/docs/86_PLAYER_TRAINING_TEMPLATES_AND_LOAD_MANAGEMENT_STANDARD.md)  
> **执行规格书**: [09_ATL_season2_tactical_mod.json](file:///C:/nba2k22/exports/20261125_season2_day1_tactical_execution/09_ATL_season2_tactical_mod.json)

---

## 一、 新赛季完整阵容审计与休赛期变动

经 `2022-2023_M01_NOV` 快照实机读取，亚特兰大老鹰当前 17 人名册（含 2 名双向球员）完成重大结构性重组：

### 1.1 休赛期核心变动
* **新援入驻**：
  * **萨迪克·贝 (Saddiq Bey, slot=8, cf=8010, 23岁)**：强力空间侧翼，3PT 86、定点三分倾向 90、三分总倾向 84，完美补强锋线外线火力。
  * **阿隆·霍勒迪 (Aaron Holiday, slot=9, cf=7722, 26岁)**：替补稳健控卫，控球 88、速度 87、三分 80。
  * **1984 届历史新秀补强**：**凯文·威利斯 (Kevin Willis, slot=10, cf=318)**（内防 84、盖帽 75）与 **查理·西顿 (Charlie Sitton, slot=11, cf=1972)** 进入深度轮换储备。
* **离队球员**：德隆·赖特、卡梅隆·雷迪什、戈尔吉·吉昂、路·威廉姆斯、所罗门·希尔、小托马斯、达拉诺·班顿已离队。
* **核心班底保留**：特雷·杨 (slot=0)、德章泰·穆雷 (slot=7)、德安德烈·亨特 (slot=2)、约翰·科林斯 (slot=3)、克林特·卡佩拉 (slot=4)、博格丹·博格达诺维奇 (slot=1)、奥涅卡·奥孔武 (slot=5)、杰伦·约翰逊 (slot=6)。

### 1.2 实机数据异常诊断 (Real-Save Anomalies)
1. **后场双核触球严重撞车**：特雷·杨 `touches = 99` 且 `play_discipline = 5`；德章泰·穆雷 `touches = 99` 且 `spot_up_three = 30`；首发五人触球和高达 `99 + 99 + 54 + 69 + 58 = 379`（远超 `310~330` 守恒区间）。
2. **杰伦·约翰逊球权畸高**：替补前锋 `touches = 88`、`shot = 86`、`dish = 78`，会在混编时段严重抢占博格丹与特雷·杨球权。
3. **阿隆·霍勒迪犯规红线越界**：`foul = 58`（超过 Doc 85 铁律 5 的 `<= 50` 硬性上限），`drive = 99` 过于极端。
4. **凯文·威利斯运球门槛违规**：控球 `BH = 48 < 60`，但 `crossover = 79`、`no_move = 0`，违反 Doc 85 铁律 2，易导致内线运球失误。
5. **教练体系与协防失真**：`ActiveSystem = 7 (DEFENSE)` 与“杨+穆雷+卡佩拉+射手群”的快节奏空间挡拆阵容严重错配；`HelpDefense = 39` 过低，未激活卡佩拉/奥孔武护筐协防网；`GAMEPLAN` 的 POE 仍为全中立默认值 (`5, 8, 11, 14, 17, 20`)。

---

## 二、 10 人核心轮换与先发/替补架构 (240 人·分闭环)

### 2.1 先发五虎 (Starters - 158 分钟)
| 槽位 | 球员 | 位置 | 年龄 | 目标时间 | 战术定位与核心职责 |
| :---: | :--- | :---: | :---: | :---: | :--- |
| **0** | **Trae Young** | PG | 24 | 35.0 | 绝对进攻大脑，高位挡拆发起核心、超远三分引力与抛投/空接喂饼 |
| **7** | **Dejounte Murray** | SG | 26 | 35.0 | 攻防副核与外线第一领防大锁（外防89/抢断84），转换推进与中距离惩罚 |
| **2** | **De'Andre Hunter** | SF | 24 | 30.0 | 首发 3&D 锋线铁锁（外防80），承担对方头号侧翼主攻手对位 |
| **3** | **John Collins** | PF | 25 | 30.0 | 飞天空间大前锋（中投93/三分78/扣篮81），45%外弹+55%顺下空接 |
| **4** | **Clint Capela** | C | 28 | 28.0 | 禁区护筐屏障（内防84/盖帽87）与吃饼中锋，深沉退护筐+冲抢前板 |

### 2.2 第二阵容 (Bench 6~10 - 82 分钟，凯文·威利斯第 11 人机动储备)
| 槽位 | 球员 | 位置 | 年龄 | 目标时间 | 战术定位与核心职责 |
| :---: | :--- | :---: | :---: | :---: | :--- |
| **1** | **Bogdan Bogdanovic** | SG/SF | 30 | 26.0 | 最佳第六人与决胜射手（三分92/中投88），第二阵容第一进攻火力点 |
| **5** | **Onyeka Okongwu** | C | 21 | 20.0 | 高机动护筐中锋（盖帽80/上篮92），小阵容换防五号位与顺下吃饼 |
| **8** | **Saddiq Bey** | SF/PF | 23 | 16.0 | 替补空间炮台（三分86），底角/侧翼定点三分轰炸 |
| **6** | **Jalen Johnson** | PF | 20 | 12.0 | 运动型锋线（速度82/上篮87），转换快攻空切与活力拼抢 |
| **9** | **Aaron Holiday** | PG | 26 | 8.0 | 替补稳健控卫（控球88/三分80），衔接段控场与外线施压 |
| **10** | **Kevin Willis** | C/PF | 60 | 0.0 (机动) | 11人名单深度内线，常规赛待命、犯规危机/伤病顶替内线肉搏 |

---

## 三、 攻防博弈体系 (Doc 49 攻守并重)

### 3.1 进攻博弈体系：`PACE_AND_SPACE` (ID: 2)
* **核心引力模型**：特雷·杨高位挡拆 + 卡佩拉/科林斯双威胁顺下，迫使对手防线在“包夹/延误特雷·杨（漏空接与底角博格丹/贝/亨特）”与“中锋沉退（特雷·杨超远三分与抛投惩罚）”之间陷入两难。
* **双控错峰与纪律**：将特雷·杨 `touches` 从 99 降至 `86`、`play_discipline` 从 5 升至 `78`；穆雷 `touches` 从 99 降至 `78`、`spot_up_three` 从 30 升至 `60`，确保无球侧翼衔接顺畅而不踩踏。

### 3.2 防守博弈体系：外线双锁领防 + 内线深沉退/机动换防
* **外线藏匿与锁死**：穆雷（外防 89、抢断 84）与亨特（外防 80）对位对手后场/侧翼双核心，掩护特雷·杨（外防 53）；`POEDefense2 = PLAY_PHYSICAL (18)` 提升外线身体对抗。
* **内线分层防御**：卡佩拉在场主打 `PROTECT_PAINT (13)` 深沉退护筐；奥孔武在场提升机动换防覆盖；`HelpDefense` 由 `39` 大幅提升至 `75`，激活弱侧刷卡协防与 `CRASH_DEFENSIVE_BOARDS (19)` 保护后板推反击。

---

## 四、 模拟侧重 (GAMEPLAN Scoring Options & 6 大 POE)

* **Scoring Option 1 (`offset 376`)**：`Trae Young` (`cyberface_id = 7706`)
* **Scoring Option 2 (`offset 378`)**：`Dejounte Murray` (`cyberface_id = 7222`)
* **Scoring Option 3 (`offset 380`)**：`John Collins` (`cyberface_id = 7513`)
* **6 大 POE**：
  * `poe_offense (382)` = `4` (`PICK_AND_ROLL_OFFENSE`：挡拆起手)
  * `poe_offense_tempo (383)` = `9` (`SHOOT_AT_WILL`：抓转换早攻与射手空位)
  * `poe_offense_rebound (384)` = `12` (`LIMIT_TRANSITION`：优先退防限制对手反击)
  * `poe_defense (385)` = `13` (`PROTECT_PAINT`：卡佩拉/奥孔武护筐保禁区)
  * `poe_defense_physicality (386)` = `18` (`PLAY_PHYSICAL`：高强度身体对抗)
  * `poe_defense_rebound (387)` = `19` (`CRASH_DEFENSIVE_BOARDS`：全员保护防守篮板)

---

## 五、 核心轮换全维倾向校准与球权守恒

> **球权守恒核验**：
> * **先发 5 人触球和**：`86 (Trae) + 78 (Murray) + 52 (Hunter) + 62 (Collins) + 42 (Capela) = 320` $\in [310, 330]$
> * **第二阵容 5 人触球和**：`66 (Bogdan) + 46 (Okongwu) + 56 (Bey) + 54 (J. Johnson) + 44 (A. Holiday) = 266` $\in [250, 280]$
> * **犯规红线核验**：全员 `foul <= 50`（重点将 Aaron Holiday 从 `58` 压降至 `42`）。
> * **非极端与门槛核验**：Jalen Johnson `roll_vs_pop` 从 `5` 调至 `30`；Kevin Willis (`BH=48`) 花式运球 `crossover` 从 `79` 压至 `5`、`no_move` 设为 `92`。

---

## 六、 训练模板与防伤负荷管理 (Doc 86)

| 球员 | 年龄 | 训练位置 (`position`) | 训练模板 (`player_type`) | 强度 (`intensity`) | 负荷管理理由 |
| :--- | :---: | :---: | :---: | :---: | :--- |
| Trae Young | 24 | 0 (PG) | 6 (PLAYMAKING) | **3 (Medium)** | ≤24岁成长红利，强化传控与组织 |
| Dejounte Murray | 26 | 1 (SG) | 1 (TWO_WAY) | **2 (Low)** | ≥26岁防伤负荷管理，保持攻防一体 |
| De'Andre Hunter | 24 | 2 (SF) | 1 (TWO_WAY) | **3 (Medium)** | ≤24岁，强化3D侧翼单防与定点三分 |
| John Collins | 25 | 3 (PF) | 4 (ATHLETIC) | **3 (Medium)** | 25岁黄金期，保持空中终结与对抗 |
| Clint Capela | 28 | 4 (C) | 5 (REBOUNDING) | **2 (Low)** | ≥26岁防伤保护，巩固护筐与篮板 |
| Bogdan Bogdanovic | 30 | 1 (SG) | 7 (OUTSIDE) | **2 (Low)** | 30岁老将养生护航，维持外线投射 |
| Onyeka Okongwu | 21 | 4 (C) | 3 (DEFENSIVE) | **3 (Medium)** | 21岁内线新星，强化护筐与换防 |
| Saddiq Bey | 23 | 2 (SF) | 7 (OUTSIDE) | **3 (Medium)** | 23岁射手，强化外线三分稳定性 |
| Jalen Johnson | 20 | 3 (PF) | 0 (ALL_AROUND) | **3 (Medium)** | 20岁高潜新星，全能型模板全面发育 |
| Aaron Holiday | 26 | 0 (PG) | 1 (TWO_WAY) | **2 (Low)** | ≥26岁防伤控制，稳固替补3D控卫定位 |
| Kevin Willis | 60 | 4 (C) | 5 (REBOUNDING) | **2 (Low)** | 高龄内线低负荷保护，维持篮板卡位 |
