# 犹他爵士 (UTA) 2022-2023 新赛季（Day 1）全维度战术与博弈调优报告

> **文档状态**: 2022-2023 赛季 Day 1 正式执行提案  
> **球队标识**: Utah Jazz (UTA) | `team_id: 12` | 主教练: Quin Snyder (`staff_slot: 10`)  
> **底层数据源**: `C:\nba2k22\saves\MyLEAGUE0005\league_state.sqlite` (`snapshot_id = '2022-2023_M01_NOV'`)  
> **关联规范**: Doc 43 V2 (规则四) / Doc 49 (攻守并重) / Doc 85 (倾向校准) / Doc 86 (训练模板与负荷) / Doc 60 (UTA 上季基准)  
> **生成日期**: 2026-11-25

---

## 1. 新赛季完整阵容与休赛期变动审计

基于 `2022-2023_M01_NOV` 实机数据库切片，UTA 当前激活名册共 17 人。相比 2021-2022 赛季（Doc 60），球队在休赛期完成了彻底的阵容重建与控卫线历史级补强：

- **核心新援补强**：
  - **John Stockton**（Slot 11, `face_id=163`, 传球准确度 `95` / 传球智商 `96` / 控球 `91` / 抢断 `88` / 外防 `87` / 三分 `78` / 中投 `85`）：历史级传统控场大师空降盐湖城，彻底接管首发一号位指挥棒。
  - **Kelly Olynyk**（Slot 4, `face_id=2699`, 31 岁）：空间型五号位与肘区发牌手（三分 `76` / 近投 `89` / 防板 `80` / 拼抢 `85`）。
  - **Talen Horton-Tucker**（Slot 6, `face_id=7865`, 21 岁）：高大强壮双能锋卫（上篮 `89` / 横移 `77` / 抢断 `75` / 速度 `80`）。
  - **Kris Dunn**（Slot 8, `face_id=7205`, 28 岁）：替补外线防守铁闸（外防 `85` / 抢断 `93` / 横移 `84`）。
  - **Udoka Azubuike**（Slot 5, `face_id=8016`, 23 岁）与 **Juan Toscano-Anderson**（Slot 9, `face_id=7937`, 29 岁）：分别提供替补禁区吃饼护筐（站扣 `86` / 盖帽 `72` / 前板 `80`）与侧翼万金油 3D 拼抢（三分 `79` / 拼抢 `95`）。
  - **其他新援与储备**：Damian Jones（Slot 10）、Ron Cavenall（Slot 12）、Terence Stansbury（Slot 13）、Kenny Green（Slot 14）、Qi Zhou（Slot 21）、Donta Hall（Slot 22）。
- **离队人员（共 11 人）**：Mike Conley、Bojan Bogdanovic、Joe Ingles、Hassan Whiteside、Eric Paschall、Elijah Hughes、Malik Beasley、Patrick Beverley、Jarred Vanderbilt、Cameron Thomas、Trent Forrest。
- **留队核心（共 5 人）**：Lauri Markkanen（Slot 3）、Collin Sexton（Slot 7）、Jordan Clarkson（Slot 0）、Rudy Gay（Slot 1）、Leandro Bolmaro（Slot 2）。

### 实机诊断与关键失真点
1. **教练体系与协防参数失真**：`COACHDATA` 中 `ActiveSystem = 7`（DEFENSE），与爵士当前五外空间投射阵容严重背离（`PreferredSystem` 已为 `2` PACE_AND_SPACE）；`HelpDefense = 42` 偏低，在失去戈贝尔后无法支撑弱侧轮转协防。
2. **核心球权分配与战术纪律失真**：
   - `John Stockton` 触球高达 `90`，且 `roll_vs_pop = 95`、`play_discipline = 30`，导致后场大脑反而过度粘球且纪律涣散；
   - `Talen Horton-Tucker`（`touches=22`）、`Kris Dunn`（`touches=20`）、`Udoka Azubuike`（`touches=20`）与 `Juan Toscano`（`touches=15`）球权被过度压榨，二阵无人敢接球运转；
   - `Lauri Markkanen`（`disc=30`）、`Jordan Clarkson`（`disc=25`）、`Rudy Gay`（`disc=15`）、`Azubuike`（`disc=5`）战术纪律普遍崩塌。
3. **非投篮型中锋外弹错位与犯规红线违规**：
   - `Udoka Azubuike` 三分能力仅 `26`，但 `roll_vs_pop` 竟高达 **`99`**（纯外弹），必须强制回调至 `18`（主顺下）；
   - `Talen Horton-Tucker`（`foul=55`）、`Juan Toscano`（`foul=72`）、`Kris Dunn`（`foul=99`）、`Udoka Azubuike`（`foul=99`）严重突破 Doc 85 `foul <= 50` 红线！

---

## 2. 先发五虎与 6~10 人第二阵容轮换（触球守恒）

### 2.1 先发五虎（触球总和 = **326** ∈ `[310, 330]`）
| 槽位 | 球员 | 位置 | 目标时间 | 触球 (原→新) | 出手 (原→新) | 分球 (原→新) | 发起 | PlayTypes | 战术定位 |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| 11 | John Stockton | PG | 30.0 | 90 → **64** | 67 → **64** | 94 | 1 | `[4, 14, 12, 13]` | 历史级控场大师，挡拆发牌与底角冷箭三分 |
| 7 | Collin Sexton | SG | 34.0 | 82 → **78** | 87 → **84** | 68 | 1 | `[4, 1, 12, 11]` | 首发外线第一突击刺客，挡拆强突造杀伤 |
| 6 | Talen Horton-Tuc | SF | 27.0 | 22 → **54** | 64 → **62** | 35 → **52** | 0 | `[11, 4, 14, 3]` | 强壮侧翼终结者，无球空切与反击推进 |
| 3 | Lauri Markkanen | PF | 35.0 | 82 | 84 → **86** | 60 | 0 | `[14, 7, 1, 11]` | 7 尺第一得分基石，绕掩护三分与错位单挑 |
| 4 | Kelly Olynyk | C | 26.0 | 57 → **48** | 63 → **58** | 55 → **68** | 0 | `[14, 7, 13, 12]` | 空间型五号位高炮台，外弹三分与肘区 DHO 策应 |

### 2.2 第二阵容 6~10 人（触球总和 = **252** ∈ `[250, 280]`）
| 槽位 | 球员 | 位置 | 目标时间 | 触球 (原→新) | 出手 (原→新) | 分球 (原→新) | 发起 | PlayTypes | 战术定位 |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| 0 | Jordan Clarkson | SG | 27.0 | 71 → **74** | 81 → **80** | 40 → **48** | 1 | `[1, 4, 14, 12]` | 最佳第六人，二阵绝对单挑与挡拆持球爆破点 |
| 1 | Rudy Gay | PF | 16.0 | 42 → **44** | 53 → **55** | 45 → **48** | 0 | `[14, 1, 7, 0]` | 老将空间四号位，定点三分与低位错位单打 |
| 8 | Kris Dunn | PG | 16.0 | 20 → **48** | 47 → **46** | 50 → **72** | 1 | `[4, 11, 0, 0]` | 替补控场与外线死亡缠绕大锁，梳理二阵转换 |
| 5 | Udoka Azubuike | C | 15.0 | 20 → **42** | 32 → **45** | 20 → **25** | 0 | `[7, 11, 0, 0]` | 替补吃饼巨兽与禁区护筐墙，顺下空接终结 |
| 9 | Juan Toscano | SF | 14.0 | 15 → **44** | 43 → **48** | 45 → **62** | 0 | `[11, 14, 0, 0]` | 拼抢型 3D 侧翼连接器，空切与底角三分 |

* **轮换时间总计**：`30 + 34 + 27 + 35 + 26 + 27 + 16 + 16 + 15 + 14 = 240.0` 分钟完美闭环。

---

## 3. 攻防博弈体系（Doc 49 攻守并重）

### 3.1 进攻体系：`PACE_AND_SPACE` (2) + 五外空间双核驱动
- **重心重构**：将 `active_system` 由 `7`（DEFENSE）切换至 `2`（`PACE_AND_SPACE`），`run_play_tendency` 由 `80` 微调至 `74`，在发挥斯托克顿精密挡拆战术执行力的同时，为塞克斯顿、克拉克森留足早期转换与五外空间自由阅读空间。
- **引力闭环**：斯托克顿（`PA=95, PIQ=96, dish=94`）与马尔卡宁（`3PT=81, DF=80`）、奥利尼克（`3PT=76, DHO Passer`）组成五外高位挡拆网。一旦对手护筐中锋沉退，马尔卡宁与奥利尼克外弹三分惩罚；一旦对手换防或夹击，塞克斯顿（`LAY=89, DF=96`）与 THT（`LAY=89`）强突禁区制造罚球杀伤。

### 3.2 防守博弈体系：外线领防施压 + 弱侧提前轮转护筐
- **资源支撑**：Stockton（`PD=87, STL=88, LQ=84`）、Kris Dunn（`PD=85, STL=93, LQ=84`）、THT（`PD=71, LQ=77, STL=75`）、Juan Toscano（`HUS=95, LQ=74`）、Azubuike（`ID=73, BLK=72`）。
- **博弈策略**：
  - 将 `help_defense` 自 `42` 提升至 **`68`**，弥补首发前场（Markkanen/Olynyk）护筐爆发力不足的短板，激活弱侧提前轮转与卡位顺下（Tag-on-roll）；
  - 外线由 Stockton（首发）与 Dunn（替补）轮番领防敌方持球核心，施加高强度身体对抗（`PLAY_PHYSICAL 18`）并切断传球路线；
  - `bench_depth` 设为 `10`，保证十人高机动轮换的防守续航。

---

## 4. 模拟侧重（Scoring Options 1~3 & 6 大 POE）

- **Scoring Option 1**: `Lauri Markkanen` (`face_id = 7508`)
- **Scoring Option 2**: `Collin Sexton` (`face_id = 7707`)
- **Scoring Option 3**: `Jordan Clarkson` (`face_id = 4175`)
- **6 大 POE**：
  - `poe_offense`: `2` (`GET_SHOOTERS_OPEN`，由 `5` 调整，最大化五外空间群射效率)
  - `poe_offense_tempo`: `9` (`SHOOT_AT_WILL`，由 `8` 调整，提速打早期转换三分)
  - `poe_offense_rebound`: `12` (`LIMIT_TRANSITION`，由 `11` 调整，五外投射后优先退防防止对手快攻)
  - `poe_defense`: `13` (`PROTECT_PAINT`，由 `14` 调整，收缩保护油漆区)
  - `poe_defense_physicality`: `18` (`PLAY_PHYSICAL`，由 `17` 调整，拉满外线身体对抗)
  - `poe_defense_rebound`: `19` (`CRASH_DEFENSIVE_BOARDS`，由 `20` 调整，全员保护后板后由 Stockton/Sexton 推进)

---

## 5. 全维倾向安全线与训练负荷管理

- **犯规红线（Doc 85 铁律五）**：
  - `Kris Dunn` `foul` 由 `99` 压降至 **`45`**；
  - `Udoka Azubuike` `foul` 由 `99` 压降至 **`44`**；
  - `Juan Toscano-Anderson` `foul` 由 `72` 压降至 **`40`**；
  - `Talen Horton-Tucker` `foul` 由 `55` 压降至 **`42`**；
  - 全队 10 人核心轮换 `foul` 均 `<= 45`。
- **训练模板与防伤负荷（Doc 86）**：
  - **≤ 24 岁成长梯队（`intensity = 3` Medium）**：Collin Sexton (23, SG, `OFFENSIVE=2`), Talen Horton-Tucker (21, SF, `TWO_WAY=1`), Udoka Azubuike (23, C, `INSIDE=8`)；另 Lauri Markkanen (25, PF, `OUTSIDE=7`) 处于当打上升期核心，同步设定 `intensity = 3` 保障全明星级成长。
  - **≥ 26 岁巅峰/老将梯队（`intensity = 2` Low）**：John Stockton (PG, `PLAYMAKING=6`), Kelly Olynyk (31, C, `OUTSIDE=7`), Jordan Clarkson (30, SG, `OFFENSIVE=2`), Rudy Gay (36, PF, `OUTSIDE=7`), Kris Dunn (28, PG, `DEFENSIVE=3`), Juan Toscano-Anderson (29, SF, `TWO_WAY=1`)。
  - 所有 10 名核心轮换球员 `is_intensity_overriden = 1`。
