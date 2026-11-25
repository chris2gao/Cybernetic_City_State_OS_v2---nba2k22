# 迈阿密热火 (MIA) 2022-2023 新赛季全维度战术体系与攻防博弈提案

> **文档标识**: `10_MIA_SEASON_2022_2023_TACTICAL_PROPOSAL`  
> **基准规范**: [43_FULL_DIMENSIONAL_NATIVE_MOD_PROTOCOL_V2.md](file:///e:/workspace/Cybernetic_City_State_OS_v2%20-%20nba2k22/08_Domain_Applications/Antigravity_GM_Engine/docs/43_FULL_DIMENSIONAL_NATIVE_MOD_PROTOCOL_V2.md) | [49_NBA2K22_TACTICAL_SYSTEM_AND_GAME_THEORETIC_TUNING_STANDARD.md](file:///e:/workspace/Cybernetic_City_State_OS_v2%20-%20nba2k22/08_Domain_Applications/Antigravity_GM_Engine/docs/49_NBA2K22_TACTICAL_SYSTEM_AND_GAME_THEORETIC_TUNING_STANDARD.md) | [85_PLAYER_TENDENCIES_FULL_DIMENSIONAL_CALIBRATION_STANDARD.md](file:///e:/workspace/Cybernetic_City_State_OS_v2%20-%20nba2k22/08_Domain_Applications/Antigravity_GM_Engine/docs/85_PLAYER_TENDENCIES_FULL_DIMENSIONAL_CALIBRATION_STANDARD.md) | [86_PLAYER_TRAINING_TEMPLATES_AND_LOAD_MANAGEMENT_STANDARD.md](file:///e:/workspace/Cybernetic_City_State_OS_v2%20-%20nba2k22/08_Domain_Applications/Antigravity_GM_Engine/docs/86_PLAYER_TRAINING_TEMPLATES_AND_LOAD_MANAGEMENT_STANDARD.md)  
> **数据快照**: `league_state.sqlite` (`snapshot_id = '2022-2023_M01_NOV'`)  
> **球队标识**: `team_id: 10 | MIA | Miami Heat` | **主教练**: Erik Spoelstra (`staff_slot: 8`)

---

## 1. 新赛季完整阵容审计与休赛期变动

对比 2021-2022 赛季（[Doc 52](file:///e:/workspace/Cybernetic_City_State_OS_v2%20-%20nba2k22/08_Domain_Applications/Antigravity_GM_Engine/docs/52_MIA_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md)），2022-2023 Day 1 实机存档呈现如下阵容演变：

- **离队球员**：P.J. Tucker、Eric Gordon、Markieff Morris、Dewayne Dedmon。
- **新援补强**：
  - **Kevin Love (Slot 7, `face_id: 1511`, 34岁)**：接替四号位空缺，提供顶级防守篮板（`91`）与外线空间（3PT `80`）。
  - **Cody Zeller (Slot 12, `face_id: 2690`, 30岁)**：替补吃饼护筐中锋（Layup `84`、Reb `81`），但实机存在 `roll_vs_pop = 80`（3PT仅39却外弹！）与 `foul = 86` 严重 Bug，必须纠偏。
  - **Serge Ibaka (Slot 14, `face_id: 1698`, 33岁)**：老将内线深度补充（Mid `82`、Blk `71`）。
  - **Casey Waters (Slot 6, `face_id: 1`, 20岁)**：新秀内线储备（Dunk `83`、Mid `79`）。
- **核心架构与实机异常诊断**：
  - **Tyler Herro (Slot 3, 22岁)** 正式进入先发分卫与外线第一火力点，与 Butler、Adebayo 构成三核。
  - **首发触球拥堵**：Butler (`91`) + Bam (`90`) + Herro (`80`) + Lowry (`76`) + Love (`55`) 合计 `392`，远超 `[310, 330]` 守恒区间。
  - **Bam Adebayo 缺失手递手战术资格**：当前 `play_types = [13, 7, 8, 11]`，缺少 `12`（Hand-off），需重构为 `[12, 7, 11, 8]`。
  - **犯规红线超标**：Duncan Robinson (`foul=58`)、Cody Zeller (`foul=86`)、Omer Yurtseven (`foul=99, hard_foul=60`) 均严重超标，必须在本次差分包中压降至 `<= 50`。
  - **教练体系偏软**：`ActiveSystem = 2 (PACE_AND_SPACE)`、`HelpDefense = 44`，未体现斯波铁血防守与 `ZoneUsage = 30` 联防体系。

---

## 2. 轮换架构（先发 5 人 + 6~10 人第二阵容）

### 2.1 先发五虎（Starters — 触球和 = 326 ∈ [310, 330]）
| 位置 | 槽位 | 球员 | 年龄 | 定位与职责 | 目标时间 | 触球 (Tch) |
| :--- | :---: | :--- | :---: | :--- | :---: | :---: |
| PG | 0 | **Kyle Lowry** (`1357`) | 36 | 首发控场指挥官 / 节奏分配与定点三分 | 31.0 | **62** |
| SG | 3 | **Tyler Herro** (`7832`) | 22 | 外线第一火力点 / 挡拆持球与 DHO 借掩护 | 34.0 | **74** |
| SF | 1 | **Jimmy Butler** (`2165`) | 33 | 绝对第一攻坚核心 / 造犯规与错位单打 | 36.0 | **84** |
| PF | 7 | **Kevin Love** (`1511`) | 34 | 空间四号位 / 长传反击与后场篮板保护 | 26.0 | **36** |
| C | 2 | **Bam Adebayo** (`7519`) | 25 | 高位 DHO 策应轴心 / 1~5 号位扫荡换防 | 35.0 | **70** |

### 2.2 第二阵容（6~10 人 — 触球和 = 254 ∈ [250, 280]）+ 11 人安全修正
| 顺位 | 槽位 | 球员 | 年龄 | 定位与职责 | 目标时间 | 触球 (Tch) |
| :---: | :---: | :--- | :---: | :--- | :---: | :---: |
| 6 | 4 | **Max Strus** (`7920`) | 26 | 替补无球神射 / 卷切三分火力 | 24.0 | **52** |
| 7 | 9 | **Victor Oladipo** (`2688`) | 30 | 二阵领防尖兵与副持球突击手 (`is_initiator=1`) | 22.0 | **62** |
| 8 | 10 | **Gabe Vincent** (`7928`) | 26 | 斗犬型替补控卫 / 全场紧逼领防 | 20.0 | **58** |
| 9 | 8 | **Duncan Robinson** (`7768`) | 28 | 纯无球手递手射手 / 犯规修正 (`58→36`) | 16.0 | **48** |
| 10 | 12 | **Cody Zeller** (`2690`) | 30 | 替补吃饼护筐中锋 / 外弹与犯规纠偏 (`80→18`, `86→42`) | 14.0 | **34** |
| 11 | 5 | **Omer Yurtseven** (`8079`) | 24 | 内线储备 / 犯规安全锁修正 (`foul 99→44, hard_foul 60→15`) | 6.0 | **24** |

---

## 3. 攻防博弈体系（Doc 49 攻守并重）

### 3.1 进攻体系：`DEFENSE` (7) + 高位 DHO 流动传切
- **手递手闭环**：Bam Adebayo 注入 `12 (HANDOFF_RECEIVER/HUB)` 与 `is_play_initiator=1`，串联 Herro、Strus、Robinson 的无球卷切三分；关键回合由 Butler（`84` 触球、`91` 出手）低位或侧翼硬解造杀伤。
- **空间与吃饼解耦**：Kevin Love（`roll_vs_pop=82`）严格外弹拉开空间，Cody Zeller（`roll_vs_pop=18`）纯顺下吃饼，彻底避免禁区拥堵。

### 3.2 防守体系：1~4 号位换防 + 斯波 2-3 变奏联防（`ZoneUsage=30`）
- **铁血协防网**：将 `HelpDefense` 从 `44` 提升至 `80`，配合 `ZoneUsage=30` 与 `POEDefense=13 (PROTECT_PAINT)`、`POEDefense2=18 (PLAY_PHYSICAL)`，以 Butler（PDef `89`）、Oladipo（PDef `80`）外线施压，Bam（IDef `79`, Reb `84`）扫荡禁区，Love 与 Bam 卡位锁死防守篮板（`POEDefense3=19`）并极速退防限制对手转换（`POEOffense3=12`）。

---

## 4. 教练设置与模拟侧重（COACHDATA & GAMEPLAN）

| 模块 | 字段 | 偏移 | 类型 | 原值 | 设定值 | 决策依据 |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| `COACHDATA` | `active_system` | 267 | `uint8` | 2 | **7** | 切换为 `DEFENSE` 铁血防守带动半场体系 |
| `COACHDATA` | `run_play_tendency` | 224 | `uint8` | 80 | **78** | 维持高纪律战术呼叫率，高频触发 DHO |
| `COACHDATA` | `help_defense` | 330 | `uint8` | 44 | **80** | 大幅提升弱侧协防与强侧合围积极性 |
| `COACHDATA` | `bench_depth` | 222 | `uint8` | 9 | **10** | 常规赛 10 人轮换 |
| `COACHDATA` | `bench_utilization` | 312 | `uint8` | 55 | **55** | 保持主力高出场时间与稳定终结权 |
| `GAMEPLAN` | `scoring_option_1` | 376 | `uint16` | - | **2165** | Jimmy Butler 第一终结核心 |
| `GAMEPLAN` | `scoring_option_2` | 378 | `uint16` | - | **7832** | Tyler Herro 第二终结核心 |
| `GAMEPLAN` | `scoring_option_3` | 380 | `uint16` | - | **7519** | Bam Adebayo 第三终结核心 |
| `GAMEPLAN` | `poe_offense` | 382 | `uint8` | 4 | **4** | `PICK_AND_ROLL_OFFENSE` 挡拆与 DHO 起手 |
| `GAMEPLAN` | `poe_offense_tempo` | 383 | `uint8` | 8 | **7** | `PATIENT_OFFENSE` 耐心落半场传导 |
| `GAMEPLAN` | `poe_offense_rebound` | 384 | `uint8` | 12 | **12** | `LIMIT_TRANSITION` 极速退防限制对手反击 |
| `GAMEPLAN` | `poe_defense` | 385 | `uint8` | 13 | **13** | `PROTECT_PAINT` 死守油漆区 |
| `GAMEPLAN` | `poe_defense_physicality` | 386 | `uint8` | 18 | **18** | `PLAY_PHYSICAL` 全场身体对抗 |
| `GAMEPLAN` | `poe_defense_rebound` | 387 | `uint8` | 19 | **19** | `CRASH_DEFENSIVE_BOARDS` 全员卡位保后板 |

---

## 5. 核心轮换全维倾向校准与训练负荷模板（Doc 85 & Doc 86）

- **犯规红线**：全队核心轮换 `foul <= 50`（修正 Robinson `58→36`、Zeller `86→42`、Yurtseven `99→44` 且 `hard_foul 60→15`）。
- **蓝领运球门槛**：Love (`bc=52`)、Zeller (`bc=40`) 锁定 `crossover=0, no_move_dribble=95`。
- **训练负荷铁律**：
  - `<= 24岁`（Herro 22、Yurtseven 24）：`intensity = 3 (Medium)` 保障成长；
  - `>= 26岁`（Lowry 36、Butler 33、Love 34、Strus 26、Oladipo 30、Vincent 26、Robinson 28、Zeller 30）及高负荷 25 岁核心（Adebayo 25）：`intensity = 2 (Low)` 防疲劳防大伤；全员 `is_intensity_overriden = 1`。
