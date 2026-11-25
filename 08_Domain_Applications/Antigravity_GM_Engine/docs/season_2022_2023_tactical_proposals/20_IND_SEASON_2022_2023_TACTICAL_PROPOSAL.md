# 印第安纳步行者 (IND) 2022-2023 新赛季（Day 1）全维度战术与博弈调优报告

> **文档状态**: 2022-2023 赛季 Day 1 正式执行提案  
> **球队标识**: Indiana Pacers (IND) | `team_id: 20` | 主教练: Rick Carlisle (里克·卡莱尔)  
> **底层数据源**: `C:\nba2k22\saves\MyLEAGUE0005\league_state.sqlite` (`snapshot_id = '2022-2023_M01_NOV'`)  
> **关联规范**: Doc 43 V2 (规则四) / Doc 49 (攻守并重) / Doc 85 (倾向校准与哨兵基线) / Doc 86 (训练模板与负荷)  
> **生成日期**: 2026-11-25

---

## 1. 新赛季完整阵容与休赛期变动审计

基于 `2022-2023_M01_NOV` 实机数据库切片，IND 当前激活名册共 15 人。相比 2021-2022 赛季（Doc 70），休赛期阵容发生以下重要变化：

- **新援与 1984 届新秀补强**：
  - **Ron Anderson**（Slot 6, `face_id=1960`, 22 岁）：全能侧翼新秀（中投 82、近投 79、突破上篮 78、外防 70、速度 78），补充第二阵容持球与中距离火力；
  - **Michael Cage**（Slot 11, `face_id=1974`, 23 岁）：强硬篮板内线（前板 87、防板 87、内防 80、力量 84）；
  - **Maxi Kleber**（Slot 13, `face_id=4979`, 30 岁）：空间型四号位（三分 83、外防 67、内防 67），完美适配五外拉开；
  - **George Hill**（Slot 8, `face_id=1531`, 36 岁）与 **DeMarcus Cousins**（Slot 14, `face_id=1805`, 32 岁）、**Kent Bazemore**（Slot 12, `face_id=2517`, 33 岁）提供老将深度。
- **核心骨架稳固**：Tyrese Haliburton（Slot 2, 22 岁）、Myles Turner（Slot 0, 26 岁）、Buddy Hield（Slot 4, 29 岁）、Chris Duarte（Slot 9, 25 岁）、Aaron Nesmith（Slot 3, 23 岁）、Isaiah Jackson（Slot 1, 20 岁）、Daniel Theis（Slot 5, 30 岁）、T.J. McConnell（Slot 7, 30 岁，回归步行者）、Oshae Brissett（Slot 10, 24 岁）在列；Pascal Siakam、Alex Caruso 已离队。

### 实机诊断与关键失真点
1. **哨兵球员 Tyrese Haliburton（Doc 85 哨兵 1）需精准校准**：当前 `touches = 98`, `dish_to_open_man = 98`, `shot_tendency = 80`, `foul = 82`, `play_discipline = 40`。依据 Doc 85 哨兵基线，需维持**高触球（`>= 90`）+ 高分球（`>= 92`）+ 出手克制（`70~76`）**，并将 `foul` 从 `82` 压至 `35`。
2. **战术纪律（Play Discipline `0x497`）全面崩塌**：Kleber (5)、Nesmith (15)、Turner (20)、Theis (20)、Brissett (30)、Jackson (30)、Duarte (35)、McConnell (35)、Haliburton (40) 均严重偏低，导致五外跑位停滞。
3. **犯规倾向严重超标**：Turner (`96`)、Theis (`99`)、Jackson (`90`)、Brissett (`90`)、Kleber (`85`)、Haliburton (`82`) 均远超 `<= 50` 安全红线，实机模拟极易犯满离场。
4. **协防滑块过低**：COACHDATA `help_defense` 仅 `37`，无法支撑 Turner（盖帽 96）+ Jackson（盖帽 84）的禁区护筐漏斗。

---

## 2. 先发五虎与 6~11 人第二阵容轮换（触球守恒）

### 2.1 先发五虎（触球总和 = **316** ∈ `[310, 330]`）
| 槽位 | 球员 | 位置 | 目标时间 | 触球 (原→新) | 出手 (原→新) | 分球 (原→新) | 发起 | PlayTypes | 战术定位 |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| 2 | Tyrese Haliburton | PG | 35.0 | 98 → **92** | 80 → **74** | 98 → **95** | 1 | `[4, 14, 2, 11]` | **绝对发牌大核（哨兵）**：高触球、顶级分球、出手克制 |
| 4 | Buddy Hield | SG | 31.0 | 58 → **56** | 82 → **80** | 45 → **48** | 0 | `[14, 12, 4, 0]` | 无球神射终结者，绕掩护与手递手三分重炮 |
| 9 | Chris Duarte | SF | 28.0 | 57 → **58** | 73 → **72** | 40 → **50** | 0 | `[14, 12, 4, 1]` | 侧翼副攻手与接球三分点（三分 87） |
| 13 | Maxi Kleber | PF | 26.0 | 35 → **46** | 48 → **56** | 35 → **48** | 0 | `[14, 7, 11, 0]` | 空间型四号位，外弹三分拉开与协防换防 |
| 0 | Myles Turner | C | 32.0 | 68 → **64** | 72 → **74** | 45 → **50** | 0 | `[7, 14, 8, 0]` | 空间护筐五号位（`Roll vs Pop = 75`）+ 盖帽王 |

### 2.2 第二阵容轮换（第 6~10 人触球和 = **258** ∈ `[250, 280]`，含第 11 人）
| 槽位 | 球员 | 位置 | 目标时间 | 触球 (原→新) | 出手 (原→新) | 分球 (原→新) | 发起 | PlayTypes | 战术定位 |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| 6 | Ron Anderson | SF | 22.0 | 70 → **62** | 80 → **76** | 62 | 0 | `[3, 1, 14, 11]` | 第二阵容主攻侧翼，中距离与面框单挑得分手 |
| 7 | T.J. McConnell | PG | 20.0 | 71 → **56** | 43 → **52** | 92 | 1 | `[5, 4, 11, 0]` | 替补控卫指挥官与外线抢断恶犬（抢断 95） |
| 3 | Aaron Nesmith | SG | 18.0 | 40 → **50** | 58 → **62** | 40 → **48** | 0 | `[14, 11, 0, 0]` | 活力 3&D 锋线，定点三分与快攻空切 |
| 1 | Isaiah Jackson | C | 14.0 | 34 → **46** | 53 → **58** | 35 → **38** | 0 | `[7, 11, 0, 0]` | 机动护筐与吃饼中锋（`Roll vs Pop = 18`） |
| 5 | Daniel Theis | C | 10.0 | 35 → **44** | 43 → **52** | 45 → **48** | 0 | `[7, 8, 11, 0]` | 稳健替补内线，高位策应与掩护顺下 |
| 10 | Oshae Brissett | PF | 4.0 | 44 → **38** | 43 → **48** | 35 → **42** | 0 | `[14, 11, 0, 0]` | 第 11 人机动锋线与底角三分储备 |

---

## 3. 攻防博弈体系（Doc 49 攻守并重）

### 3.1 进攻体系：`PACE_AND_SPACE` (2) + 哈利伯顿五外挡拆引擎
- **哈利伯顿发牌 + 双高炮台拉空**：Haliburton（`touches=92`, `dish=95`, `shot=74`）主导高位挡拆，Turner（`Roll vs Pop = 75`）与 Kleber（`Roll vs Pop = 80`）双双外弹至三分线外，迫使对手护筐中锋远离三秒区，为 Haliburton 突分 Hield（90 三分倾向）、Duarte（三分 87）创造绝对空位。
- **教练滑块**：`active_system = 2` (Pace and Space)，`run_play_tendency` 由 `70` 调至 `75`，`bench_depth` 由 `9` 调至 `10`，`bench_utilization` 由 `55` 调至 `58`。

### 3.2 防守博弈体系：外线抢断压迫 + 特纳/杰克逊禁区封盖漏斗
- **资源支撑**：先发依靠 Myles Turner（盖帽 96、内防 87）与 Maxi Kleber（内防 67、外防 67）筑起禁飞区；替补依靠 T.J. McConnell（抢断 95、外防 80）全场撕咬持球人，配合 Isaiah Jackson（盖帽 84、内防 74）守护二阵容禁区。
- **博弈策略**：`help_defense` 由 `37` 强力拉升至 **`72`**，最大化弱侧对顺下人的 Tag 与护筐补帽；POE 防守端锁定 `PROTECT_PAINT (13)` + `PLAY_PHYSICAL (18)` + `CRASH_DEFENSIVE_BOARDS (19)`。

---

## 4. 模拟侧重（Scoring Options 1~3 & 6 大 POE）

- **Scoring Option 1**: `Tyrese Haliburton` (`face_id = 8001`)
- **Scoring Option 2**: `Buddy Hield` (`face_id = 7204`)
- **Scoring Option 3**: `Myles Turner` (`face_id = 4474`)
- **6 大 POE**：
  - `poe_offense`: `4` (`PICK_AND_ROLL_OFFENSE`)
  - `poe_offense_tempo`: `8` (`NEUTRAL_OFFENSE_TEMPO`)
  - `poe_offense_rebound`: `12` (`LIMIT_TRANSITION`)
  - `poe_defense`: `13` (`PROTECT_PAINT`)
  - `poe_defense_physicality`: `18` (`PLAY_PHYSICAL`)
  - `poe_defense_rebound`: `19` (`CRASH_DEFENSIVE_BOARDS`)

---

## 5. 全维倾向安全线与训练负荷管理

- **犯规红线（Doc 85 铁律 5）**：全队核心轮换 `foul` (`0x4B8`) 全部压制在 `<= 46`（Turner `96->46`, Theis `99->46`, Jackson `90->46`, Brissett `90->44`, Kleber `85->44`, Haliburton `82->35`）；`hard_foul` (`0x4B9`) 统一压制在 `<= 35`（常规球员 `18~28`，内线蓝领/恶汉 `30~35`）。
- **训练模板与防伤负荷（Doc 86）**：
  - **≤ 25 岁成长梯队（`intensity = 3` Medium）**：Tyrese Haliburton (22, PG, `PLAYMAKING=6`)、Isaiah Jackson (20, C, `DEFENSIVE=3`)、Ron Anderson (22, SF, `OFFENSIVE=2`)、Aaron Nesmith (23, SG, `TWO_WAY=1`)、Oshae Brissett (24, PF, `TWO_WAY=1`)、Chris Duarte (25, SF, `TWO_WAY=1`)。
  - **≥ 26 岁巅峰/老将梯队（`intensity = 2` Low）**：Myles Turner (26, C, `OUTSIDE=7`)、Buddy Hield (29, SG, `OUTSIDE=7`)、Maxi Kleber (30, PF, `OUTSIDE=7`)、T.J. McConnell (30, PG, `PLAYMAKING=6`)、Daniel Theis (30, C, `INSIDE=8`)。
  - 所有球员 `is_intensity_overriden = 1`。
