# 萨克拉门托国王 (SAC) 2022-2023 新赛季（Day 1）全维度战术与博弈调优报告

> **文档状态**: 2022-2023 赛季 Day 1 正式执行提案  
> **球队标识**: Sacramento Kings (SAC) | `team_id: 13` | 主教练: Luke Walton (卢克·沃顿)  
> **底层数据源**: `C:\nba2k22\saves\MyLEAGUE0005\league_state.sqlite` (`snapshot_id = '2022-2023_M01_NOV'`)  
> **关联规范**: Doc 43 V2 (规则四) / Doc 49 (攻守并重) / Doc 85 (倾向校准) / Doc 86 (训练模板与负荷)  
> **生成日期**: 2026-11-25

---

## 1. 新赛季完整阵容与休赛期变动审计

基于 `2022-2023_M01_NOV` 实机数据库切片，SAC 当前激活名册共 17 人。相比 2021-2022 赛季（Doc 73），国王保留了 Fox + Sabonis + Huerter + Barnes + Holmes + Davion Mitchell 核心骨架，并精准补强了替补火力与内线篮板深度：

- **核心新援与 1984 届新秀加盟**：
  - **Malik Monk**（Slot 10, `face_id=7506`, 24 岁）：三分 82、突破上篮 81、速度 86，与 Fox 重逢组成联盟最具爆发力的替补微波炉双枪。
  - **1984 届传奇新秀 Otis Thorpe**（Slot 13, `face_id=2019`, 1984 新秀）：前板 87、后板 89、内防 83、盖帽 72，极大补强国王四五号位肉搏与前场篮板统治力。
  - **Trey Lyles**（Slot 9, `face_id=4433`, 26 岁）：三分 80、后板 83，提供替补空间四号位投射。
  - **深度替补补充**：Steven Buford（Slot 21）、Greg Whittington（Slot 22）。
- **离队人员**：Marvin Bagley III、Damian Jones、Jeremy Lamb、Justin Holiday。

### 实机诊断与关键失真点
1. **替补使用率畸高**：`COACHDATA.bench_utilization` 高达 **`85`**，严重压缩 Fox 与 Sabonis 出场时间，需回调至 **`55`**；`help_defense` 仅 **`37`**，无法支撑 Sabonis/Huerter 的防守轮转，需提升至 **`65`**。
2. **Otis Thorpe 运球倾向异常（Doc 85 铁律二违规）**：Otis Thorpe 控球能力仅 `52`（`< 60`），但底层 `crossover` 竟高达 **`82`**、`no_move` 为 **`0`**，会导致内线强行外线运球失误，必须压低至 `crossover = 5`、`no_move = 90`。
3. **射手 `roll_vs_pop` 归零与全队 `play_discipline` 崩溃**：
   - `Kevin Huerter`（`disc = 15, rp = 0`）、`Malik Monk`（`disc = 35, rp = 0`）、`Trey Lyles`（`disc = 45, rp = 0, 3ptT = 40`）、`Domantas Sabonis`（`disc = 30`）、`Terence Davis`（`disc = 25, rp = 0`）战术纪律极低，导致 DHO 手递手体系无法正常跑出掩护。
4. **球权结构微调**：Fox (`95`) 与 Sabonis (`88`) 触球和偏高，需收敛至 `Fox 84 + Sabonis 80 + Huerter 56 + Barnes 54 + Holmes 42 = 316`。

---

## 2. 先发五虎与 6~10 人第二阵容轮换（触球守恒）

### 2.1 先发五虎（触球总和 = **316** ∈ `[310, 330]`）
| 槽位 | 球员 | 位置 | 目标时间 | 触球 (原→新) | 出手 (原→新) | 分球 (原→新) | 发起 | PlayTypes | 战术定位 |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| 0 | De'Aaron Fox | PG | 35.0 | 95 → **84** | 92 → **86** | 85 → **82** | 1 | `[4, 2, 1, 12]` | 97 速度闪电推进核心，高位挡拆与急停中投 |
| 11 | Kevin Huerter | SG | 30.0 | 58 → **56** | 73 → **74** | 45 → **52** | 0 | `[14, 12, 4, 11]` | 手递手（DHO）无球狙击手与绕掩护三分 |
| 1 | Harrison Barnes | SF | 29.0 | 54 → **54** | 66 → **64** | 40 → **48** | 0 | `[14, 11, 6, 0]` | 稳健 3&D 空间侧翼、底角三分与空切 |
| 8 | Domantas Sabonis | PF/C | 35.0 | 88 → **80** | 77 → **78** | 92 → **90** | 1 | `[9, 12, 8, 7]` | 高位肘区策应轴心、手递手发牌与低位硬解 |
| 2 | Richaun Holmes | C | 24.0 | 38 → **42** | 53 → **56** | 25 → **32** | 0 | `[7, 11, 10, 0]` | 挡拆顺下吃饼、禁区抛投终结与护筐 |

### 2.2 第二阵容轮换（第 6~10 人触球总和 = **252** ∈ `[250, 280]`）
| 槽位 | 球员 | 位置 | 目标时间 | 触球 (原→新) | 出手 (原→新) | 分球 (原→新) | 发起 | PlayTypes | 战术定位 |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| 3 | Davion Mitchell | PG | 22.0 | 60 → **58** | 65 → **62** | 78 → **76** | 1 | `[4, 1, 14, 12]` | 二阵容主控兼外线“Off-Night”领防大锁 |
| 10 | Malik Monk | SG | 23.0 | 55 → **56** | 72 → **76** | 45 → **54** | 0 | `[14, 12, 4, 1]` | 第六人微波炉得分手，手递手三分与冲筐 |
| 13 | Otis Thorpe | PF | 16.0 | 68 → **48** | 80 → **66** | 39 → **42** | 0 | `[7, 8, 11, 0]` | 1984 超级新秀，禁区肉搏卡位、顺下与前板 |
| 9 | Trey Lyles | PF | 14.0 | 45 → **46** | 38 → **56** | 45 → **45** | 0 | `[14, 7, 11, 0]` | 替补空间型四号位高炮台（`Roll vs Pop = 75`） |
| 5 | Terence Davis | SG | 12.0 | 50 → **44** | 73 → **66** | 35 → **42** | 0 | `[14, 4, 1, 0]` | 替补外线抢分与转换三分火力 |

---

## 3. 攻防博弈体系（Doc 49 攻守并重）

### 3.1 进攻体系：`PACE_AND_SPACE` (2) + Sabonis DHO 轴心转换风暴
- **双核驱动**：Sabonis 驻守肘区/弧顶充当手递手（DHO）与高位策应发牌官（`is_play_initiator = 1`, `dish = 90`），为 Huerter、Monk、Barnes 挂出高质量掩护三分；Fox 利用 97 速度在反击与高位挡拆（`poe_offense = 4`）中撕裂禁区。
- **教练滑块**：`active_system = 2`，`run_play_tendency = 75`，`bench_depth = 10`，`bench_utilization = 55`。

### 3.2 防守博弈体系：Davion Mitchell 领防锁喉 + Holmes/Thorpe 护筐收板
- **资源支撑**：Davion Mitchell（外防 83、横移 86、抢断 79）担任第一道外线大锁，专门对位对方核心后卫；Holmes（盖帽 81、内防 74）与 Otis Thorpe（内防 83、后板 89、盖帽 72）筑起禁区护筐与后场篮板防线。
- **博弈策略**：`help_defense` 由 `37` 提升至 **`65`**，通过 `PROTECT_PAINT (13)` + `PLAY_PHYSICAL (18)` + `CRASH_DEFENSIVE_BOARDS (19)` 弥补 Sabonis 单防横移短板，收下后板后立即交 Fox/Monk 发动闪电快攻（`poe_offense_tempo = 9`）。

---

## 4. 模拟侧重（Scoring Options 1~3 & 6 大 POE）

- **Scoring Option 1**: `De'Aaron Fox` (`face_id = 7503`)
- **Scoring Option 2**: `Domantas Sabonis` (`face_id = 7212`)
- **Scoring Option 3**: `Kevin Huerter` (`face_id = 7718`)
- **6 大 POE**：
  - `poe_offense`: `4` (`PICK_AND_ROLL_OFFENSE`)
  - `poe_offense_tempo`: `9` (`SHOOT_AT_WILL`)
  - `poe_offense_rebound`: `12` (`LIMIT_TRANSITION`)
  - `poe_defense`: `13` (`PROTECT_PAINT`)
  - `poe_defense_physicality`: `18` (`PLAY_PHYSICAL`)
  - `poe_defense_rebound`: `19` (`CRASH_DEFENSIVE_BOARDS`)

---

## 5. 全维倾向安全线与训练负荷管理

- **犯规红线**：核心 10 人轮换 `foul` (`0x4B9`) 实机值均 ≤ 42（Fox/Sabonis/Holmes/Thorpe 42，Mitchell 35，Monk/Davis 30，Huerter/Barnes 28，Lyles 26），全部满足 `foul <= 50` 硬性安全线。
- **训练模板与防伤负荷（Doc 86）**：
  - **≤ 24 岁及新秀成长梯队（`intensity = 3` Medium）**：De'Aaron Fox (24, PG, `ALL_AROUND=0`)、Kevin Huerter (24, SG, `OUTSIDE=7`)、Davion Mitchell (24, PG, `TWO_WAY=1`)、Malik Monk (24, SG, `OFFENSIVE=2`)、Otis Thorpe (1984 新秀, PF, `REBOUNDING=5`)。
  - **≥ 25/26 岁巅峰/老将梯队（`intensity = 2` Low）**：Domantas Sabonis (26, C, `PLAYMAKING=6`)、Harrison Barnes (30, SF, `TWO_WAY=1`)、Richaun Holmes (29, C, `INSIDE=8`)、Trey Lyles (26, PF, `OUTSIDE=7`)、Terence Davis (25, SG, `OFFENSIVE=2`)。
  - 所有球员 `is_intensity_overriden = 1`。
