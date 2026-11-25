# 丹佛掘金 (DEN) 2022-2023 新赛季（Day 1）全维度战术与博弈调优报告

> **文档状态**: 2022-2023 赛季 Day 1 正式执行提案  
> **球队标识**: Denver Nuggets (DEN) | `team_id: 19` | 主教练: Mike Malone (迈克尔·马龙)  
> **底层数据源**: `C:\nba2k22\saves\MyLEAGUE0005\league_state.sqlite` (`snapshot_id = '2022-2023_M01_NOV'`)  
> **关联规范**: Doc 43 V2 (规则四) / Doc 49 (攻守并重) / Doc 85 (倾向校准) / Doc 86 (训练模板与负荷)  
> **生成日期**: 2026-11-25

---

## 1. 新赛季完整阵容与休赛期变动审计

基于 `2022-2023_M01_NOV` 实机数据库切片，DEN 当前激活名册共 17 人。相比 2021-2022 赛季（Doc 57），休赛期围绕“约基奇 + 穆雷 + 波特”健康合体完成了极具针对性的 3D 与替补深度升级：

- **核心新援补强**：
  - **Kentavious Caldwell-Pope**（Slot 7, `face_id=2694`, 29 岁）：三分 81、外防 78、横移 84，完美担任首发 3D 领防大闸与无球空间射手。
  - **Bruce Brown**（Slot 8, `face_id=7741`, 26 岁）：外防 71、抢断 71、前板 79、控球 74，全能型第六人万金油，兼具短顺下抛投与外线撕咬。
  - **Reggie Jackson**（Slot 6, `face_id=2156`, 32 岁）：三分 81、控球 79，担任第二阵容挡拆发动机与外线火力点。
  - **Thomas Bryant**（Slot 9, `face_id=7541`, 25 岁）：三分 79、原地扣篮 75、前板 78，空间型替补中锋。
  - **DeAndre Jordan**（Slot 11, `face_id=1538`, 34 岁）、**Ish Smith**（Slot 10, `face_id=1900`, 34 岁）、**Vlatko Cancar**（Slot 12, `face_id=7892`, 25 岁）提供深度储备。
- **离队人员**：Monte Morris、Bones Hyland、JaMychal Green、Austin Rivers、Facundo Campazzo 等部分旧轮换已调整或退居边缘。

### 实机诊断与关键失真点
1. **约基奇触球与出手微超载**：数据库实测 Nikola Jokic 当前 `touches = 99`, `shot = 92`, `play_discipline = 50`，而首发其余四人触球相对健康（Murray 78, MPJ 64, Gordon 48, KCP 48，总和 `337` 略超 `[310, 330]` 上限）。同时**哨兵校验**：Jokic 当前 `roll_vs_pop = 50`，完美符合 Doc 85 双能内线中间值准则，需严格维持 `50`。
2. **战术纪律（Play Discipline `0x497`）全员偏低**：Murray (30)、MPJ (30)、KCP (20)、Brown (35)、Jeff Green (30)、Bryant (30)、Nnaji (15) 均处于低纪律状态，导致进攻端极易脱离马龙的高位手递手与肘区策应体系。
3. **单打分层曲线（ISO vs Defenders）倒挂**：MPJ (`[88, 95, 25, 0]`)、Gordon (`[92, 15, 25, 10]`)、KCP (`[92, 85, 10, 10]`) 出现“面对精英防守者单打欲望极高、面对漏勺反而为 0~10”的严重逆向 BUG，必须按 Doc 85 铁律 3 重建阶梯。
4. **KCP 扑防倾向过低 & Brown 顺弹错配**：外线头号领防人 KCP `contest_shot` 仅 `35`；Bruce Brown `roll_vs_pop` 高达 `90`（误判为纯外弹射手）。
5. **协防滑块偏低**：`COACHDATA.help_defense` 仅 `37`，不足以支撑约基奇平视延误后的弱侧 `TagOnRoll` 补位。

---

## 2. 先发五虎与 6~10 人第二阵容轮换（触球守恒）

### 2.1 先发五虎（触球总和 = **322** ∈ `[310, 330]`）
| 槽位 | 球员 | 位置 | 目标时间 | 触球 (原→新) | 出手 (原→新) | 分球 (原→新) | 发起 | PlayTypes | 战术定位 |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| 3 | Nikola Jokic | C | 36.0 | 99 → **88** | 92 → **82** | 99 | 1 | `[9, 8, 13, 7]` | 历史级肘区策应大脑，手递手与高低位发牌（`roll_vs_pop = 50`） |
| 0 | Jamal Murray | PG | 34.0 | 78 → **76** | 82 → **84** | 72 → **78** | 1 | `[4, 1, 12, 14]` | 挡拆核心与决胜单打手，与约基奇二人转 |
| 1 | Michael Porter Jr. | SF | 32.0 | 64 → **60** | 84 | 25 → **38** | 0 | `[14, 11, 12, 3]` | 6'10" 无球高炮台，弱侧接球三分与反跑空切 |
| 2 | Aaron Gordon | PF | 32.0 | 48 → **50** | 57 → **62** | 40 → **52** | 0 | `[11, 7, 8, 14]` | 底线幽灵空切暴扣（`roll_vs_pop = 20`）+ 侧翼大闸 |
| 7 | Kentavious Caldwell-Pope | SG | 31.0 | 48 | 58 → **62** | 35 → **45** | 0 | `[14, 12, 11, 0]` | 首发 3D 领防尖兵与底角定点射手 |

### 2.2 第二阵容轮换（第 6~10 人触球和 = **256** ∈ `[250, 280]`）
| 槽位 | 球员 | 位置 | 目标时间 | 触球 (原→新) | 出手 (原→新) | 分球 (原→新) | 发起 | PlayTypes | 战术定位 |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| 8 | Bruce Brown | SG/PG | 25.0 | 48 → **56** | 50 → **58** | 50 → **62** | 1 | `[11, 4, 14, 1]` | 第六人万金油，空切+短顺下+外线撕咬（`roll_vs_pop = 30`） |
| 6 | Reggie Jackson | PG | 18.0 | 65 → **64** | 70 → **68** | 82 | 1 | `[4, 14, 12, 1]` | 二阵容主控，挡拆突分与外线投射 |
| 4 | Jeff Green | PF | 14.0 | 38 → **44** | 48 → **52** | 40 → **45** | 0 | `[11, 14, 7, 8]` | 老将锋线空切与空间接应 |
| 9 | Thomas Bryant | C | 11.0 | 48 → **50** | 57 | 30 → **35** | 0 | `[7, 14, 8, 11]` | 空间型替补中锋（`roll_vs_pop = 55`） |
| 5 | Zeke Nnaji | PF/C | 7.0 | 40 → **42** | 54 | 25 → **35** | 0 | `[14, 7, 11, 0]` | 机动换防内线与底角三分点 |

---

## 3. 攻防博弈体系（Doc 49 攻守并重）

### 3.1 进攻体系：`PACE_AND_SPACE` (2) + 约基奇肘区轴心
- **双核空间闭环**：约基奇（`touches=88`, `dish=99`, `roll_vs_pop=50`）在肘区与高位发起手递手（`13`）和策应（`9`），穆雷（`4, 12`）通过二人转攻筐或拔干，MPJ（`14`）与 KCP（`14`）在两翼拉满重力，Gordon（`11`）沿底线伺机空切。
- **教练滑块**：`active_system = 2` (Pace & Space)，`run_play_tendency = 75`，`bench_depth = 10`，`bench_utilization = 60`。

### 3.2 防守博弈体系：约基奇平视延误 + KCP 挤过掩护 + Gordon 弱侧扫荡
- **资源支撑**：KCP（外防 78、横移 84）与 Brown（外防 71、抢断 71）负责外线 POA 挤过掩护（`GO_OVER`）；Gordon（内/外防 69、弹跳扣篮级身体素质）锁死敌方锋线王牌并执行弱侧 `TagOnRoll`；约基奇（抢断 72、防守篮板 87）采用平视延误（Soft Hedge）阻断持球人第一时间干拔，守住后场篮板后一传发动快攻。
- **博弈策略**：`help_defense` 由 `37` 提升至 **`65`**，确保弱侧轮转闭合；POE 防守端锁定 `PROTECT_PAINT (13)` + `PLAY_PHYSICAL (18)` + `CRASH_DEFENSIVE_BOARDS (19)`。

---

## 4. 模拟侧重（Scoring Options 1~3 & 6 大 POE）

- **Scoring Option 1**: `Nikola Jokic` (`face_id = 4170`)
- **Scoring Option 2**: `Jamal Murray` (`face_id = 7202`)
- **Scoring Option 3**: `Michael Porter Jr.` (`face_id = 7713`)
- **6 大 POE**：
  - `poe_offense`: `3` (`FEED_THE_POST`)
  - `poe_offense_tempo`: `8` (`NEUTRAL_OFFENSE_TEMPO`)
  - `poe_offense_rebound`: `10` (`CRASH_OFFENSIVE_BOARDS`)
  - `poe_defense`: `13` (`PROTECT_PAINT`)
  - `poe_defense_physicality`: `18` (`PLAY_PHYSICAL`)
  - `poe_defense_rebound`: `19` (`CRASH_DEFENSIVE_BOARDS`)

---

## 5. 全维倾向安全线与训练负荷管理

- **哨兵与犯规红线**：
  - 约基奇 `roll_vs_pop` 锁定 **`50`**；全队 10 人轮换 `foul` (`0x4B9`) 均 `≤ 45`（Jokic 45, Bryant 42, Gordon/Brown/Nnaji 38, Murray/KCP/Jackson/Green 32, MPJ 30），`hard_foul` 均 `≤ 18`。
- **训练模板与防伤负荷（Doc 86）**：
  - **≤ 25 岁成长梯队（`intensity = 3` Medium）**：Zeke Nnaji (21, PF, `TWO_WAY=1`), Michael Porter Jr. (24, SF, `OUTSIDE=7`), Jamal Murray (25, PG, `OFFENSIVE=2`), Thomas Bryant (25, C, `OUTSIDE=7`)。
  - **≥ 26 岁巅峰/老将梯队（`intensity = 2` Low）**：Bruce Brown (26, SG, `TWO_WAY=1`), Nikola Jokic (27, C, `PLAYMAKING=6`), Aaron Gordon (27, PF, `TWO_WAY=1`), Kentavious Caldwell-Pope (29, SG, `TWO_WAY=1`), Reggie Jackson (32, PG, `PLAYMAKING=6`), Jeff Green (36, PF, `TWO_WAY=1`)。
  - 所有球员 `is_intensity_overriden = 1`。
