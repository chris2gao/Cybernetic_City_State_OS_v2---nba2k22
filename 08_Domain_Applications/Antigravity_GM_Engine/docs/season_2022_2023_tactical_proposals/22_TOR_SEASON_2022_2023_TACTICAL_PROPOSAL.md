# 多伦多猛龙 (TOR) 2022-2023 新赛季全维度战术体系与攻防博弈提案

> **文档标识**: `22_TOR_SEASON_2022_2023_TACTICAL_PROPOSAL`  
> **基准规范**: [43_FULL_DIMENSIONAL_NATIVE_MOD_PROTOCOL_V2.md](file:///e:/workspace/Cybernetic_City_State_OS_v2%20-%20nba2k22/08_Domain_Applications/Antigravity_GM_Engine/docs/43_FULL_DIMENSIONAL_NATIVE_MOD_PROTOCOL_V2.md) | [49_NBA2K22_TACTICAL_SYSTEM_AND_GAME_THEORETIC_TUNING_STANDARD.md](file:///e:/workspace/Cybernetic_City_State_OS_v2%20-%20nba2k22/08_Domain_Applications/Antigravity_GM_Engine/docs/49_NBA2K22_TACTICAL_SYSTEM_AND_GAME_THEORETIC_TUNING_STANDARD.md) | [85_PLAYER_TENDENCIES_FULL_DIMENSIONAL_CALIBRATION_STANDARD.md](file:///e:/workspace/Cybernetic_City_State_OS_v2%20-%20nba2k22/08_Domain_Applications/Antigravity_GM_Engine/docs/85_PLAYER_TENDENCIES_FULL_DIMENSIONAL_CALIBRATION_STANDARD.md) | [86_PLAYER_TRAINING_TEMPLATES_AND_LOAD_MANAGEMENT_STANDARD.md](file:///e:/workspace/Cybernetic_City_State_OS_v2%20-%20nba2k22/08_Domain_Applications/Antigravity_GM_Engine/docs/86_PLAYER_TRAINING_TEMPLATES_AND_LOAD_MANAGEMENT_STANDARD.md)  
> **数据快照**: `league_state.sqlite` (`snapshot_id = '2022-2023_M01_NOV'`)  
> **球队标识**: `team_id: 22 | TOR | Toronto Raptors` | **主教练**: Nick Nurse (`staff_slot: 21`)

---

## 1. 新赛季完整阵容审计与休赛期变动

对比 2021-2022 赛季（[Doc 64](file:///e:/workspace/Cybernetic_City_State_OS_v2%20-%20nba2k22/08_Domain_Applications/Antigravity_GM_Engine/docs/64_TOR_FULL_DIMENSIONAL_TACTICAL_AND_GAME_THEORETIC_PROPOSAL.md)），2022-2023 Day 1 实机存档发生重大阵容升级：

- **核心回归与重磅补强**：
  - **Pascal Siakam (Slot 9, `face_id: 7236`, 28岁)** 回归猛龙并出任绝对第一进攻核心（3PT `76`、Mid `80`、Layup `83`、Dunk `80`、BC `79`、PDef `79`、IDef `87`）。
  - **Jakob Poeltl (Slot 10, `face_id: 7207`, 27岁)** 加盟坐镇首发五号位（IDef `81`、Blk `86`、Reb `74`），补齐护筐与扎实掩护短板。
  - **Otto Porter Jr. (Slot 13, `face_id: 2689`, 29岁)**、**Will Barton (Slot 8, `face_id: 2483`, 31岁)**、**Thaddeus Young (Slot 12, `face_id: 1421`, 34岁)** 充实侧翼投射与老将经验。
  - **Pat Carson (Slot 7, `face_id: 1`, 23岁)** 新晋高炮台后卫（3PT `97`、Mid `92`、BC `84`），但实机 `foul = 59` 超出安全线，需压降至 `40`。
- **离队球员**：Goran Dragic、Khem Birch、Maurice Harkless、Yuta Watanabe、Drew Eubanks、Isaac Bonga。
- **教练与球权现状诊断**：
  - `BenchUtilization` 高达 `90`，严重压缩首发核心（Siakam/VanVleet/Barnes）出场时间；`HelpDefense` 仅 `45`，远低于纳斯侵略性协防标准。
  - 首发球权局部拥堵（VanVleet `tch=92`、Barnes `tch=89`、Siakam `tch=81`、OG `tch=78`），且 Siakam `is_play_initiator = 0` 未激活组织前锋推进权。
  - 角色球员 `play_discipline` 普遍偏低（Trent `20`、Boucher `35`、Barton `35`、Porter `40`），易导致半场无序单打。

---

## 2. 轮换架构（先发 5 人 + 6~10 人第二阵容）

### 2.1 先发五虎（Starters — 触球和 = 320 ∈ [310, 330]）
| 位置 | 槽位 | 球员 | 年龄 | 定位与职责 | 目标时间 | 触球 (Tch) |
| :--- | :---: | :--- | :---: | :--- | :---: | :---: |
| PG | 0 | **Fred VanVleet** (`7288`) | 28 | 战术主脑 / 高位挡拆发起与超远三分牵制 | 35.0 | **82** |
| SG | 3 | **Gary Trent Jr.** (`7736`) | 23 | 无球绕掩护射手 / 强侧外线火力 | 31.0 | **56** |
| SF | 1 | **OG Anunoby** (`7515`) | 25 | 顶级 3&D 侧翼大闸 / 领防对方头号外线 | 34.0 | **58** |
| PF | 9 | **Pascal Siakam** (`7236`) | 28 | 绝对第一进攻大核 / 错位背身与面框突分 | 36.0 | **86** |
| C | 10 | **Jakob Poeltl** (`7207`) | 27 | 护筐与掩护顺下中锋 / 禁区卡位屏障 | 28.0 | **38** |

### 2.2 第二阵容（6~10 人 — 触球和 = 256 ∈ [250, 280]）+ 11 人安全修正
| 顺位 | 槽位 | 球员 | 年龄 | 定位与职责 | 目标时间 | 触球 (Tch) |
| :---: | :---: | :--- | :---: | :--- | :---: | :---: |
| 6 | 2 | **Scottie Barnes** (`8060`) | 21 | 超级第六人 & 终结五虎成员 / 组织前锋二阵发动机 | 32.0 | **76** |
| 7 | 11 | **Chris Boucher** (`7590`) | 29 | 空间型护筐四/五号位 / 弱侧协防大帽 | 20.0 | **48** |
| 8 | 8 | **Will Barton** (`2483`) | 31 | 替补持球双能卫 / 转换推进与急停跳投 | 16.0 | **46** |
| 9 | 4 | **Precious Achiuwa** (`8004`) | 23 | 机动吃饼内线 / 无限换防小球五号位 | 18.0 | **44** |
| 10 | 13 | **Otto Porter Jr.** (`2689`) | 29 | 空间 3&D 锋线 / 稳定底角接球投射 | 14.0 | **42** |
| 11 | 7 | **Pat Carson** (`1`) | 23 | 深度神射储备 / 犯规倾向安全锁修正 (`59→40`) | 8.0 | **38** |

---

## 3. 攻防博弈体系（Doc 49 攻守并重）

### 3.1 进攻体系：`PACE_AND_SPACE` (2) + 全能锋线错位驱动
- **双核双轴驱动**：Siakam（`86` 触球 + `is_initiator=1`）与 VanVleet（`82` 触球 + `85` 分球）构成半场高低位与挡拆双发起轴，Barnes 在替补衔接段接管球权（`76` 触球 + `85` 分球）并在决胜时刻替代 Poeltl 组成“死亡五长”。
- **空间与顺下分工**：Poeltl（`roll_vs_pop=15`）与 Achiuwa（`roll_vs_pop=15`）专注高质量掩护顺下吃饼，Boucher（`roll_vs_pop=70`）与 Porter（`roll_vs_pop=78`）拉开五外空间。

### 3.2 防守体系：纳斯流“长臂天网”与极速转换反击
- **协防与换防**：将 `HelpDefense` 从 `45` 拉升至 `85`，依托 OG（PDef `88`）、Barnes（PDef `79`/IDef `82`）、Siakam（IDef `87`）的长臂换防群，结合 Poeltl（Blk `86`）沉退护筐，形成“外线强硬对抗 + 禁区合围封盖”立体防线。
- **攻防转换闭环**：抢下后场篮板或造失误后全员推进反击，最大化锋线运动天赋。

---

## 4. 教练设置与模拟侧重（COACHDATA & GAMEPLAN）

| 模块 | 字段 | 偏移 | 类型 | 原值 | 设定值 | 决策依据 |
| :--- | :--- | :---: | :---: | :---: | :---: | :--- |
| `COACHDATA` | `active_system` | 267 | `uint8` | 2 | **2** | 锁定 `PACE_AND_SPACE` 现代空间与节奏体系 |
| `COACHDATA` | `run_play_tendency` | 224 | `uint8` | 70 | **75** | 适度提高半场战术呼叫率，减少无序单打 |
| `COACHDATA` | `help_defense` | 330 | `uint8` | 45 | **85** | 激活纳斯标志性高压刷卡协防体系 |
| `COACHDATA` | `bench_depth` | 222 | `uint8` | 9 | **10** | 常规赛 10 人精细化轮换 |
| `COACHDATA` | `bench_utilization` | 312 | `uint8` | 90 | **58** | 从 90 回调至 58，保障核心主力 34~36 分钟时间 |
| `GAMEPLAN` | `scoring_option_1` | 376 | `uint16` | - | **7236** | Pascal Siakam 第一终结核心 |
| `GAMEPLAN` | `scoring_option_2` | 378 | `uint16` | - | **7288** | Fred VanVleet 第二终结核心 |
| `GAMEPLAN` | `scoring_option_3` | 380 | `uint16` | - | **8060** | Scottie Barnes 第三终结核心 |
| `GAMEPLAN` | `poe_offense` | 382 | `uint8` | 4 | **4** | `PICK_AND_ROLL_OFFENSE` 挡拆起手 |
| `GAMEPLAN` | `poe_offense_tempo` | 383 | `uint8` | 9 | **9** | `SHOOT_AT_WILL` 抓住机会果断推早攻 |
| `GAMEPLAN` | `poe_offense_rebound` | 384 | `uint8` | 10 | **10** | `CRASH_OFFENSIVE_BOARDS` 发挥锋线冲抢优势 |
| `GAMEPLAN` | `poe_defense` | 385 | `uint8` | 15 | **13** | `PROTECT_PAINT` 依托 Poeltl 与长臂群优先护筐 |
| `GAMEPLAN` | `poe_defense_physicality` | 386 | `uint8` | 18 | **18** | `PLAY_PHYSICAL` 全场高强度身体对抗 |
| `GAMEPLAN` | `poe_defense_rebound` | 387 | `uint8` | 21 | **21** | `RUN_IN_TRANSITION` 收板即刻推转换 |

---

## 5. 核心轮换全维倾向校准与训练负荷模板（Doc 85 & Doc 86）

- **犯规红线**：全队核心轮换 `foul <= 50`（重点将 Pat Carson 从 `59` 压降至 `40`）。
- **蓝领运球门槛**：Poeltl (`bc=37`) `crossover=0, no_move_dribble=95`，杜绝传统中锋外线运球失误。
- **训练负荷铁律**：
  - `<= 24岁`（Barnes 21、Trent 23、Achiuwa 23、Carson 23）：`intensity = 3 (Medium)` 保障成长；
  - `>= 26岁`（VanVleet 28、Siakam 28、Poeltl 27、Boucher 29、Barton 31、Porter 29）及高负荷 25 岁核心（Anunoby 25）：`intensity = 2 (Low)` 防疲劳防大伤；全员 `is_intensity_overriden = 1`。
