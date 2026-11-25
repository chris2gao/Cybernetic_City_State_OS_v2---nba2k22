# 新奥尔良鹈鹕 (NOP) 2022-2023 新赛季（Day 1）全维度战术与博弈调优报告

> **文档状态**: 2022-2023 赛季 Day 1 正式执行提案  
> **球队标识**: New Orleans Pelicans (NOP) | `team_id: 11` | 主教练: Willie Green (`staff_slot: 19`)  
> **底层数据源**: `C:\nba2k22\saves\MyLEAGUE0005\league_state.sqlite` (`snapshot_id = '2022-2023_M01_NOV'`)  
> **关联规范**: Doc 43 V2 (规则四) / Doc 49 (攻守并重) / Doc 85 (倾向校准) / Doc 86 (训练模板与负荷) / Doc 68 (NOP 上季基准)  
> **生成日期**: 2026-11-25

---

## 1. 新赛季完整阵容与休赛期变动审计

基于 `2022-2023_M01_NOV` 实机数据库切片，NOP 当前激活名册共 16 人。相比 2021-2022 赛季（Doc 68），核心三巨头（Zion、Ingram、CJ）与双防守骨干（Herbert Jones、Larry Nance Jr.）完整保留，替补席进行了关键升级：

- **核心新援补强**：
  - **Josh Richardson**（Slot 12, `face_id=4459`, 29 岁）：中投 `85`、控球 `78`、外防 `71`、抢断 `72` 的双能型 3D 老将，填补 Devonte' Graham 离队后的二阵持球与外线防守空缺。
  - **Tim Hall**（Slot 10, `face_id=1`, 20 岁）：外防 `91`、横移 `99`、速度 `99`、抢断 `84`、三分 `75` 的顶级防守型年轻控卫，为二阵提供窒息级 POA 领防与推进速度。
  - **深度储备**：Ricky Ross（Slot 14, 21 岁）、Vincent Poirier（Slot 21, 29 岁）。
- **离队人员**：Devonte' Graham、Tony Snell、Bruno Fernando 已离队。

### 实机诊断与关键失真点
1. **首发球权严重超载与推进权冲突**：
   - 首发五人当前触球和为 `Zion(98) + Ingram(93) + CJ(77) + Herbert Jones(66) + Valanciunas(45) = 379`，超出 `[310, 330]` 黄金守恒区间 49 点；
   - `Zion Williamson` `is_play_initiator = 1`，与 `Ingram (1)`、`CJ (1)` 形成三重推进冲突。
2. **核心球员战术逻辑严重反转**：
   - **Zion Williamson** `roll_vs_pop` 高达 **`85`**（3PT 仅 66、扣篮 98！），导致挡拆后疯狂外弹三分而非顺下爆扣；
   - **Herbert Jones** `play_discipline` 仅 **`5`**、`touches` 高达 `66`、`roll_vs_pop` 高达 `70`，完全脱离 3D 空切纪律；
   - **Brandon Ingram**（`disc=30`）、**C.J. McCollum**（`disc=25`）、**Valanciunas**（`disc=25`）、**Larry Nance Jr.**（`disc=20`）、**Josh Richardson**（`disc=20`）战术纪律全线崩塌；
   - **Trey Murphy III** `touches=84` 严重挤压替补球权。
3. **主教练协防与轮换参数失衡**：`HelpDefense` 仅 **`39`**，无法支撑双模态防守轮转；`BenchUtilization` 高达 **`80`**，过度消耗三巨头出场时间。

---

## 2. 先发五虎与 6~10 人第二阵容轮换（触球守恒）

### 2.1 先发五虎（触球总和 = **322** ∈ `[310, 330]`）
| 槽位 | 球员 | 位置 | 目标时间 | 触球 (原→新) | 出手 (原→新) | 分球 (原→新) | 发起 | PlayTypes | 战术定位 |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| 8 | C.J. McCollum | PG | 33.0 | 77 → **76** | 80 | 80 | 1 | `[4, 14, 1, 12]` | 外线挡拆发动机与无球/持球三分狙击手 |
| 7 | Herbert Jones | SG | 28.0 | 66 → **36** | 65 → **52** | 40 → **45** | 0 | `[11, 14, 12, 0]` | 死亡缠绕外线大锁 + 底角空切幽灵 |
| 0 | Brandon Ingram | SF | 34.0 | 93 → **80** | 98 → **86** | 88 → **78** | 1 | `[4, 1, 14, 12]` | 阵地战中距离死神与组织锋线 |
| 1 | Zion Williamson | PF | 34.0 | 98 → **84** | 99 → **90** | 55 → **60** | 0 | `[1, 8, 11, 7]` | 禁区核动力第一终结核心（取消推进权，主攻面框/低位/顺下） |
| 11 | Jonas Valanciunas | C | 26.0 | 45 → **46** | 54 | 45 | 0 | `[8, 7, 14, 11]` | 重型掩护墙、前板霸王与空间中远投 |

### 2.2 第二阵容 6~10 人（触球总和 = **252** ∈ `[250, 280]`）
| 槽位 | 球员 | 位置 | 目标时间 | 触球 (原→新) | 出手 (原→新) | 分球 (原→新) | 发起 | PlayTypes | 战术定位 |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| 6 | Trey Murphy | SF | 23.0 | 84 → **58** | 88 → **78** | 30 → **40** | 0 | `[14, 12, 11, 7]` | 206cm 空间高炮台，外弹三分与底角拉开 |
| 12 | Josh Richardson | SG | 18.0 | 46 → **56** | 53 → **60** | 50 → **62** | 1 | `[4, 14, 12, 11]` | 二阵次级持球组织者 + 外线 3D |
| 10 | Tim Hall | PG | 12.0 | 50 | 48 → **50** | 59 → **68** | 1 | `[4, 11, 14, 0]` | 替补 POA 防守尖兵与转换推进器 |
| 9 | Larry Nance Jr. | PF | 22.0 | 38 → **48** | 34 → **46** | 55 | 0 | `[7, 11, 14, 0]` | 决胜五小无限换防中枢 + 顺下吃饼 |
| 2 | Jaxson Hayes | C | 10.0 | 35 → **40** | 46 → **48** | 20 → **30** | 0 | `[7, 11, 0, 0]` | 垂直空接吃饼与护筐能量点 |

* **轮换时间总计**：`33 + 28 + 34 + 34 + 26 + 23 + 18 + 12 + 22 + 10 = 240.0` 分钟完美闭环。

---

## 3. 攻防博弈体系（Doc 49 攻守并重）

### 3.1 进攻体系：`PACE_AND_SPACE` (2) 三核立体分流
- **错位闭环**：Zion（`touches=84`）主导禁区强攻与顺下（`roll_vs_pop=22`），Ingram（`touches=80`）主导高位挡拆与中距离单挑，CJ（`touches=76`）负责外线挡拆与三分牵制；Murphy（`3PT=85`）与 Valanciunas（`MID=88 / ORB=94`）提供空间与二次进攻保障。
- **教练滑块**：维持 `active_system = 2`（`PACE_AND_SPACE`），`run_play_tendency = 72`，`bench_depth = 10`，`bench_utilization` 从 `80` 下调至 **`58`** 以确保三巨头核心时间。

### 3.2 防守博弈体系：Herbert Jones/Tim Hall 锁防 + 双模态内线切换
- **资源支撑**：Herbert Jones（`PD=79, LQ=83, BLK=73`）、Tim Hall（`PD=91, LQ=99, STL=84`）、Larry Nance Jr.（`ID=72, PD=72, STL=79`）与 Valanciunas（`ID=74, DRB=90`）。
- **博弈策略**：
  - **常规模态**：Valanciunas 沉退护筐，Jones/Hall 外线死缠对方持球核心，隐藏 CJ；
  - **决胜五小模态**：Nance 顶到五号位执行 1~5 号位全换防；
  - 将 `help_defense` 从 `39` 拉升至 **`70`**，全面激活弱侧轮转补位网络。

---

## 4. 模拟侧重（Scoring Options 1~3 & 6 大 POE）

- **Scoring Option 1**: `Zion Williamson` (`face_id = 7820`)
- **Scoring Option 2**: `Brandon Ingram` (`face_id = 7201`)
- **Scoring Option 3**: `C.J. McCollum` (`face_id = 2696`)
- **6 大 POE**：
  - `poe_offense`: `1` (`GET_TO_BASKET`，由 `4` 调整，最大化 Zion 历史级禁区终结效率)
  - `poe_offense_tempo`: `8` (`NEUTRAL_OFFENSE_TEMPO`，维持 `8`，兼顾三核阵地落位与转换)
  - `poe_offense_rebound`: `10` (`CRASH_OFFENSIVE_BOARDS`，维持 `10`，释放 Valanciunas + Zion 前板统治力)
  - `poe_defense`: `13` (`PROTECT_PAINT`，维持 `13`，保护禁区)
  - `poe_defense_physicality`: `18` (`PLAY_PHYSICAL`，维持 `18`，对抗拉满)
  - `poe_defense_rebound`: `19` (`CRASH_DEFENSIVE_BOARDS`，维持 `19`，锁死后场篮板)

---

## 5. 全维倾向安全线与训练负荷管理

- **犯规红线（Doc 85 铁律五）**：
  - 核心 10 人轮换全部满足 `foul <= 44`（最高为 Herbert Jones `44`），`hard_foul <= 18`，无需额外压降即可安全通过模拟红线。
- **训练模板与防伤负荷（Doc 86）**：
  - **≤ 25 岁成长梯队（`intensity = 3` Medium）**：Zion Williamson (22, PF, `ATHLETIC=4`), Brandon Ingram (25, SF, `OFFENSIVE=2`), Herbert Jones (24, SG, `TWO_WAY=1`), Trey Murphy (22, SF, `OUTSIDE=7`), Tim Hall (20, PG, `DEFENSIVE=3`), Jaxson Hayes (22, C, `ATHLETIC=4`)。
  - **≥ 26 岁巅峰/老将梯队（`intensity = 2` Low）**：C.J. McCollum (31, PG, `OFFENSIVE=2`), Jonas Valanciunas (30, C, `INSIDE=8`), Larry Nance Jr. (29, PF, `TWO_WAY=1`), Josh Richardson (29, SG, `TWO_WAY=1`)。
  - 所有 10 名核心轮换球员 `is_intensity_overriden = 1`。
