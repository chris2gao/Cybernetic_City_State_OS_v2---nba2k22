# 孟菲斯灰熊 (MEM) 2022-2023 新赛季（Day 1）全维度战术与博弈调优报告

> **文档状态**: 2022-2023 赛季 Day 1 正式执行提案  
> **球队标识**: Memphis Grizzlies (MEM) | `team_id: 8` | 主教练: Lucas Lucas (`staff_slot: 1125`)  
> **底层数据源**: `C:\nba2k22\saves\MyLEAGUE0005\league_state.sqlite` (`snapshot_id = '2022-2023_M01_NOV'`)  
> **关联规范**: Doc 43 V2 (规则四) / Doc 49 (攻守并重) / Doc 85 (倾向校准) / Doc 86 (训练模板与负荷) / Doc 58 (MEM 上季基准)  
> **生成日期**: 2026-11-25

---

## 1. 新赛季完整阵容与休赛期变动审计

基于 `2022-2023_M01_NOV` 实机数据库切片，MEM 当前激活名册共 17 人。相比 2021-2022 赛季（Doc 58），休赛期发生了关键的射手与年轻资产轮换重塑：

- **核心新援补强**：
  - **Luke Kennard**（Slot 10, `face_id=7511`, 26 岁）：三分 `85`、中投 `84`、控球 `72` 的精英级无球射手，完美填补 Melton 与 Anderson 离队后的外线空间缺口。
  - **年轻储备与新秀**：Dion Oakley（Slot 8, `face_id=1`, 21 岁，三分 `80`/中投 `97`）、Michael Young（Slot 9, `face_id=1981`, 22 岁）、Murray Pittman（Slot 21, `face_id=1`, 21 岁）、Justin James（Slot 22, `face_id=7859`, 25 岁）。
- **离队人员**：De'Anthony Melton（已交易至 PHI）、Kyle Anderson、Juancho Hernangomez、Sam Merrill 离队。

### 实机诊断与关键失真点
1. **教练体系与节奏参数严重失真**：`COACHDATA` 中 `ActiveSystem = 7`（DEFENSE）、`RunPlayTendency = 99`（近乎 100% 死跑战术，完全锁死 Morant 的快攻与自由阅读比赛能力），且 `HelpDefense = 35`（严重偏低，浪费了 Jaren Jackson Jr. `BLK=91 / ID=81` 的历史级扫荡护框能力）。
2. **首发球权超载与出手极端化**：当前首发五人触球和为 `Morant(99) + Bane(91) + JJJ(79) + Brooks(52) + Adams(44) = 365`，超出 `[310, 330]` 黄金守恒区间 35 点；同时 `Morant` `shot_tendency=99 / play_discipline=99`，`Bane` `touches=91 / shot=92`，导致进攻分配僵化。
3. **战术类型与纪律错位**：
   - `Desmond Bane` 当前 `play_types = [13, 4, 14, 7]`，竟然包含 `7 (P&R Roll Man)` 而缺失首选 `12 (Handoff Receiver)`；
   - `Dillon Brooks`（`disc=35`）、`Steven Adams`（`disc=20`）、`Luke Kennard`（`disc=10`）、`Brandon Clarke`（`disc=35`）、`Xavier Tillman`（`disc=25`）战术纪律普遍崩塌。
4. **核心轮换犯规红线违规**：`Ziaire Williams`（`foul=90`）与 `Luke Kennard`（`foul=54`）突破了 Doc 85 `foul <= 50` 铁律，日历模拟极易提前犯满离场。

---

## 2. 先发五虎与 6~10 人第二阵容轮换（触球守恒）

### 2.1 先发五虎（触球总和 = **314** ∈ `[310, 330]`）
| 槽位 | 球员 | 位置 | 目标时间 | 触球 (原→新) | 出手 (原→新) | 分球 (原→新) | 发起 | PlayTypes | 战术定位 |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| 0 | Ja Morant | PG | 35.0 | 99 → **88** | 99 → **90** | 90 → **88** | 1 | `[4, 1, 2, 11]` | 绝对超巨引擎，挡拆突击、面框单挑与突分撕裂防线 |
| 4 | Desmond Bane | SG | 34.0 | 91 → **68** | 92 → **82** | 55 → **60** | 0 | `[14, 12, 4, 11]` | 二当家致命高炮台，挂掩护三分与手递手终结 |
| 1 | Dillon Brooks | SF | 30.0 | 52 → **48** | 60 → **58** | 40 → **45** | 0 | `[14, 3, 1, 11]` | 外线 POA 恶犬大锁 + 纪律化 3D 终结点 |
| 11 | Jaren Jackson Jr | PF | 32.0 | 79 → **64** | 87 → **78** | 35 → **45** | 0 | `[14, 7, 1, 11]` | DPOY 级弱侧扫荡神塔 + 空间外弹四/五号位 |
| 2 | Steven Adams | C | 25.0 | 44 → **46** | 38 | 65 | 0 | `[7, 13, 11, 0]` | 重型掩护巨盾、肘区 DHO 发牌手与前场篮板霸王 |

### 2.2 第二阵容 6~10 人（触球总和 = **256** ∈ `[250, 280]`）
| 槽位 | 球员 | 位置 | 目标时间 | 触球 (原→新) | 出手 (原→新) | 分球 (原→新) | 发起 | PlayTypes | 战术定位 |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| 12 | Tyus Jones | PG | 20.0 | 68 → **62** | 46 → **52** | 92 → **90** | 1 | `[4, 12, 14, 1]` | 二阵零失误控场大师，稳定梳理挡拆与转换 |
| 10 | Luke Kennard | SG | 20.0 | 45 → **56** | 70 → **76** | 35 → **45** | 0 | `[14, 12, 13, 11]` | 替补第一无球射手，牵制弱侧防守为 Morant/Clarke 拉开禁区 |
| 3 | Brandon Clarke | PF | 20.0 | 52 → **54** | 57 → **60** | 35 → **42** | 0 | `[11, 7, 13, 0]` | 机动空切飞人与决胜五小四号位 |
| 6 | Ziaire Williams | SF | 14.0 | 27 → **46** | 38 → **52** | 35 → **40** | 0 | `[11, 14, 12, 0]` | 运动型侧翼 3D，快攻跟进与底角三分 |
| 5 | Xavier Tillman | C | 10.0 | 37 → **38** | 39 → **44** | 45 → **48** | 0 | `[7, 11, 13, 0]` | 矮壮硬朗替补中锋，掩护顺下与卡位护筐 |

* **轮换时间总计**：`35 + 34 + 30 + 32 + 25 + 20 + 20 + 20 + 14 + 10 = 240.0` 分钟完美闭环。

---

## 3. 攻防博弈体系（Doc 49 攻守并重）

### 3.1 进攻体系：`PACE_AND_SPACE` (2) + 超音速转换冲击
- **重心重构**：将 `active_system` 由 `7`（DEFENSE）切换至 `2`（`PACE_AND_SPACE`），`run_play_tendency` 由 `99` 回调至 `72`，在保留战术呼出率的同时彻底释放 Morant 的高速推进与早期转换攻击。
- **引力闭环**：Morant（`touches=88, dish=88`）与 Adams（`ORB=92, DHO Passer`）发动高位挡拆逼迫对手收缩，Bane（`3PT=88`）、Kennard（`3PT=85`）与 JJJ（`3PT=77, roll_vs_pop=72`）在弧顶和底角形成三点高炮惩罚网。

### 3.2 防守博弈体系：Grit & Grind 2.0 内外立体封锁
- **资源支撑**：JJJ（`ID=81, BLK=91`）、Adams（`ID=77, DRB=74`）、Brooks（`PD=76, LQ=80`）、Clarke（`LQ=78, BLK=73`）与 Ziaire（`PD=77, LQ=80`）。
- **博弈策略**：
  - 将 `help_defense` 从 `35` 暴力拉升至 **`75`**，激活 JJJ 弱侧游弋封盖与提前轮转（`PreRotate`）；
  - 常规时段 Adams 沉退保护三秒区，决胜五小由 Clarke + JJJ 构成 1~5 号位无限机动换防；
  - `bench_depth` 设为 `10`，`bench_utilization` 调至 `65`，保证高强度全场撕咬的体能续航。

---

## 4. 模拟侧重（Scoring Options 1~3 & 6 大 POE）

- **Scoring Option 1**: `Ja Morant` (`face_id = 7821`)
- **Scoring Option 2**: `Desmond Bane` (`face_id = 8019`)
- **Scoring Option 3**: `Jaren Jackson Jr` (`face_id = 7703`)
- **6 大 POE**：
  - `poe_offense`: `1` (`GET_TO_BASKET`，由 `5` 调整，最大化 Morant 与 Clarke 禁区冲击)
  - `poe_offense_tempo`: `9` (`SHOOT_AT_WILL`，由 `8` 调整，7 秒转换快攻)
  - `poe_offense_rebound`: `10` (`CRASH_OFFENSIVE_BOARDS`，由 `12` 调整，释放 Adams + Clarke 前板碾压)
  - `poe_defense`: `13` (`PROTECT_PAINT`，由 `15` 调整，依托 JJJ + Adams 封锁油漆区)
  - `poe_defense_physicality`: `18` (`PLAY_PHYSICAL`，由 `17` 调整，拉满身体对抗)
  - `poe_defense_rebound`: `19` (`CRASH_DEFENSIVE_BOARDS`，维持 `19`，抓板即推反击)

---

## 5. 全维倾向安全线与训练负荷管理

- **犯规红线（Doc 85 铁律五）**：
  - `Ziaire Williams` `foul` 由 `90` 压降至 **`42`**；
  - `Luke Kennard` `foul` 由 `54` 压降至 **`36`**；
  - 全队 10 人核心轮换 `foul` 均 `<= 48`，`hard_foul <= 35`。
- **训练模板与防伤负荷（Doc 86）**：
  - **≤ 24 岁成长梯队（`intensity = 3` Medium）**：Ja Morant (23, PG, `OFFENSIVE=2`), Desmond Bane (24, SG, `OFFENSIVE=2`), Jaren Jackson Jr (23, PF, `TWO_WAY=1`), Ziaire Williams (21, SF, `TWO_WAY=1`), Xavier Tillman (23, C, `REBOUNDING=5`)。
  - **≥ 26 岁巅峰/定型梯队（`intensity = 2` Low）**：Dillon Brooks (26, SF, `TWO_WAY=1`), Steven Adams (29, C, `REBOUNDING=5`), Tyus Jones (26, PG, `PLAYMAKING=6`), Luke Kennard (26, SG, `OUTSIDE=7`), Brandon Clarke (26, PF, `ATHLETIC=4`)。
  - 所有 10 名核心轮换球员 `is_intensity_overriden = 1`。
