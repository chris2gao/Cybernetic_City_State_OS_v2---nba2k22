# 芝加哥公牛 (CHI) 2022-2023 新赛季（Day 1）全维度战术与博弈调优报告

> **文档状态**: 2022-2023 赛季 Day 1 正式执行提案  
> **球队标识**: Chicago Bulls (CHI) | `team_id: 3` | 主教练: Billy Donovan (比利·多诺万)  
> **底层数据源**: `C:\nba2k22\saves\MyLEAGUE0005\league_state.sqlite` (`snapshot_id = '2022-2023_M01_NOV'`)  
> **关联规范**: Doc 43 V2 (规则四) / Doc 49 (攻守并重) / Doc 85 (倾向校准) / Doc 86 (训练模板与负荷)  
> **生成日期**: 2026-11-25

---

## 1. 新赛季完整阵容与休赛期变动审计

基于 `2022-2023_M01_NOV` 实机数据库切片，CHI 当前激活名册共 17 人。相比 2021-2022 赛季（Doc 63），休赛期发生了重大结构性重塑：

- **1984 届传奇巨星加盟**：**Michael Jordan**（Slot 14, `face_id=1759`）重披公牛战袍，带来历史级攻防统治力（中投 94、近投 91、突破上篮 96、突破扣篮 95、控球 90、外防 91、抢断 90、速度 94）。
- **核心后场双铁闸回归与补强**：
  - **Lonzo Ball**（Slot 9, `face_id=7501`, 25 岁）回归控卫线，三分 84、抢断 83、外防 75、速度 87，提供顶级推进与空间串联；
  - **Alex Caruso**（Slot 8, `face_id=7570`, 28 岁）回归担任外线领防大闸（外防 79、抢断 79、三分 78）；
  - **Patrick Beverley**（Slot 12, `face_id=1650`, 34 岁）加盟提供外防 90、横移 88 的撕咬防守；
  - **Andre Drummond**（Slot 11, `face_id=2452`, 29 岁）加盟补强替补护筐与篮板（防板 97、前板 92、盖帽 75）；
  - **Derrick Jones Jr.**（Slot 13, `face_id=7293`, 25 岁）提供侧翼运动能力（突破扣篮 93、盖帽 75）。
- **休赛期新星与留队核心**：Zach LaVine（Slot 10, 27 岁）、DeMar DeRozan（Slot 0, 33 岁）、Nikola Vucevic（Slot 2, 32 岁）、Patrick Williams（Slot 1, 21 岁）、Coby White（Slot 3, 22 岁）、Ayo Dosunmu（Slot 6, 22 岁）、Fred Reynolds（Slot 7, 22 岁）在列；T.J. McConnell、T.J. Warren、Doug McDermott、Tony Bradley 等已离队。

### 实机诊断与关键失真点
1. **首发球权严重拥堵**：数据库实测先发五人当前触球和为 `Jordan(99) + LaVine(86) + DeRozan(86) + Ball(99) + Vucevic(65) = 435`，远超 `[310, 330]` 守恒区间，导致球权严重踩踏。
2. **战术纪律（Play Discipline `0x497`）两极撕裂**：Vucevic (15)、Patrick Williams (30)、DeRozan (35)、Caruso (25)、Dosunmu (40)、Beverley (15) 战术纪律过低，脱离战术体系乱打；同时 DeRozan `is_play_initiator = 1` 与 Ball/Jordan/LaVine 抢夺后场推进权。
3. **犯规倾向超标隐患**：Vucevic (`foul=80`)、Patrick Williams (`70`)、Lonzo Ball (`60`)、Michael Jordan (`72`)、Andre Drummond (`63`)、Patrick Beverley (`95`) 均突破 Doc 85 安全红线（`<= 50`），`hard_foul` 普遍在 `38~45` 区间，易导致日历模拟过早犯满离场。
4. **协防滑块偏低**：COACHDATA `help_defense` 仅 `40`，未能激活 Jordan + Ball + Caruso + Williams 的外线协防网。

---

## 2. 先发五虎与 6~11 人第二阵容轮换（触球守恒）

### 2.1 先发五虎（触球总和 = **324** ∈ `[310, 330]`）
| 槽位 | 球员 | 位置 | 目标时间 | 触球 (原→新) | 出手 (原→新) | 分球 (原→新) | 发起 | PlayTypes | 战术定位 |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| 9 | Lonzo Ball | PG | 33.0 | 99 → **60** | 77 → **66** | 95 → **92** | 1 | `[4, 14, 2, 12]` | 推进发牌大脑、转换一传与外线 3&D |
| 10 | Zach LaVine | SG | 34.0 | 86 → **68** | 92 → **84** | 65 → **68** | 1 | `[4, 14, 1, 11]` | 无球绕掩护三分与快攻暴力终结副核 |
| 14 | Michael Jordan | SF | 36.0 | 99 → **82** | 99 → **92** | 70 → **75** | 1 | `[1, 3, 4, 14]` | 球队绝对第一攻防核心，单挑突分与关键收割 |
| 0 | DeMar DeRozan | PF | 32.0 | 86 → **64** | 94 → **80** | 78 → **75** | 0 | `[14, 8, 1, 13]` | 阵地战中距离大师与错位单打第三火力 |
| 2 | Nikola Vucevic | C | 30.0 | 65 → **50** | 71 → **66** | 72 → **74** | 0 | `[14, 7, 8, 9]` | 高位空间策应中锋（`Roll vs Pop = 75`） |

### 2.2 第二阵容轮换（第 6~10 人触球和 = **252** ∈ `[250, 280]`，含第 11 人）
| 槽位 | 球员 | 位置 | 目标时间 | 触球 (原→新) | 出手 (原→新) | 分球 (原→新) | 发起 | PlayTypes | 战术定位 |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| 3 | Coby White | PG | 22.0 | 91 → **64** | 92 → **76** | 75 → **72** | 1 | `[4, 13, 14, 1]` | 第二阵容主控与微波炉双能卫得分手 |
| 8 | Alex Caruso | SG | 22.0 | 67 → **48** | 55 → **54** | 78 → **76** | 1 | `[14, 11, 4, 0]` | 外线第一领防大闸、空切与二次组织 |
| 1 | Patrick Williams | PF | 20.0 | 42 → **50** | 59 → **64** | 50 → **55** | 0 | `[14, 11, 6, 0]` | 年轻 3&D 锋线，底角三分与协防换防 |
| 6 | Ayo Dosunmu | PG | 14.0 | 46 → **48** | 53 → **58** | 75 → **72** | 1 | `[4, 11, 12, 0]` | 替补推进尖兵与外线轮转防守拼图 |
| 11 | Andre Drummond | C | 14.0 | 42 → **42** | 48 → **48** | 45 → **45** | 0 | `[7, 11, 0, 0]` | 替补吃饼与前场篮板统治者（`Roll vs Pop = 18`） |
| 12 | Patrick Beverley | PG | 8.0 | 40 → **36** | 39 → **40** | 45 → **52** | 0 | `[14, 11, 0, 0]` | 第 11 人外线撕咬恶犬与定点三分 |

---

## 3. 攻防博弈体系（Doc 49 攻守并重）

### 3.1 进攻体系：`PACE_AND_SPACE` (2) + 高位外弹拉开
- **双枪+飞人空间闭环**：Vucevic 保持 `Roll vs Pop = 75`（75% 挡拆外弹至三分线与肘区），彻底拉空禁区，为 Michael Jordan（突破扣篮 95、中投 94）与 Zach LaVine（突破扣篮 94、三分 91）提供一马平川的突破走廊；Lonzo Ball 负责推进一传与底角接应。
- **教练滑块**：`active_system = 2` (Pace and Space)，`run_play_tendency = 75`，`bench_depth = 10`，`bench_utilization = 60`。

### 3.2 防守博弈体系：外线双锁高压撕咬 + 禁区篮板反击闭环
- **资源支撑**：Michael Jordan（外防 91、抢断 90）与 Lonzo Ball（外防 75、抢断 83）在先发端锁死对手后场双核，替补席更有 Alex Caruso（外防 79、抢断 79）与 Patrick Beverley（外防 90、横移 88）无缝衔接；内线依托 Vucevic（防板 89）与 Drummond（防板 97、盖帽 75）守住后场篮板。
- **博弈策略**：`help_defense` 由 `40` 提升至 **`68`**，强化弱侧抢断轮转与对顺下内线的提前收缩；POE 防守端锁定 `LIMIT_PERIMETER_SHOTS (15)` + `PLAY_PHYSICAL (18)` + `CRASH_DEFENSIVE_BOARDS (19)`，收板后立即交 Ball / Jordan / LaVine 推快攻。

---

## 4. 模拟侧重（Scoring Options 1~3 & 6 大 POE）

- **Scoring Option 1**: `Michael Jordan` (`face_id = 1759`)
- **Scoring Option 2**: `Zach LaVine` (`face_id = 4101`)
- **Scoring Option 3**: `DeMar DeRozan` (`face_id = 1605`)
- **6 大 POE**：
  - `poe_offense`: `4` (`PICK_AND_ROLL_OFFENSE`)
  - `poe_offense_tempo`: `8` (`NEUTRAL_OFFENSE_TEMPO`)
  - `poe_offense_rebound`: `12` (`LIMIT_TRANSITION`)
  - `poe_defense`: `15` (`LIMIT_PERIMETER_SHOTS`)
  - `poe_defense_physicality`: `18` (`PLAY_PHYSICAL`)
  - `poe_defense_rebound`: `19` (`CRASH_DEFENSIVE_BOARDS`)

---

## 5. 全维倾向安全线与训练负荷管理

- **犯规红线（Doc 85 铁律 5）**：全队核心轮换 `foul` (`0x4B8`) 全部压制在 `<= 48`（Jordan `72->42`, Ball `60->40`, Vucevic `80->44`, Williams `70->42`, Drummond `63->46`, Beverley `95->48`）；`hard_foul` (`0x4B9`) 统一压制在 `<= 35`（常规球员 `15~28`，Drummond/Beverley `32`）。
- **训练模板与防伤负荷（Doc 86）**：
  - **≤ 25 岁成长梯队（`intensity = 3` Medium）**：Patrick Williams (21, PF, `TWO_WAY=1`)、Coby White (22, PG, `OFFENSIVE=2`)、Ayo Dosunmu (22, PG, `TWO_WAY=1`)、Lonzo Ball (25, PG, `PLAYMAKING=6`)。
  - **≥ 26 岁巅峰/老将梯队（`intensity = 2` Low）**：Michael Jordan (59, SF, `ALL_AROUND=0`)、Zach LaVine (27, SG, `OFFENSIVE=2`)、DeMar DeRozan (33, PF, `OFFENSIVE=2`)、Nikola Vucevic (32, C, `OUTSIDE=7`)、Alex Caruso (28, SG, `DEFENSIVE=3`)、Andre Drummond (29, C, `REBOUNDING=5`)、Patrick Beverley (34, PG, `DEFENSIVE=3`)。
  - 所有球员 `is_intensity_overriden = 1`。
