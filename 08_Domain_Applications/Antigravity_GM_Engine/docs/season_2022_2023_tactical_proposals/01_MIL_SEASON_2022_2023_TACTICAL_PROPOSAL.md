# 密尔沃基雄鹿 (MIL) 2022-2023 新赛季（Day 1）全维度战术与博弈调优报告

> **文档状态**: 2022-2023 赛季 Day 1 正式执行提案  
> **球队标识**: Milwaukee Bucks (MIL) | `team_id: 1` | 主教练: Mike Budenholzer (迈克·布登霍尔泽)  
> **底层数据源**: `C:\nba2k22\saves\MyLEAGUE0005\league_state.sqlite` (`snapshot_id = '2022-2023_M01_NOV'`)  
> **关联规范**: Doc 43 V2 (规则四) / Doc 49 (攻守并重) / Doc 85 (倾向校准) / Doc 86 (训练模板与负荷)  
> **生成日期**: 2026-11-25

---

## 1. 新赛季完整阵容与休赛期变动审计

基于 `2022-2023_M01_NOV` 实机数据库切片，MIL 当前激活名册共 16 人。相比 2021-2022 赛季（Doc 53），核心三巨头（Giannis Antetokounmpo、Khris Middleton、Jrue Holiday）与护筐双柱（Brook Lopez、Bobby Portis Jr.）完整保留，轮换拼图迎来老将化升级：

- **休赛期新援补强**：
  - **Jae Crowder**（Slot 8, `face_id=2477`, 32 岁）：硬汉 3D 锋线（3PT 79, PDef 74, IDef 74），强化侧翼换防与顶防硬度。
  - **Joe Ingles**（Slot 12, `face_id=2612`, 35 岁）：高球商组织前锋与定点射手（3PT 86, PDef 76），分担二阵挡拆发牌压力。
  - **Goran Dragic**（Slot 11, `face_id=1555`, 36 岁）：经验丰富的替补控卫（BH 82, 3PT 76, Mid 80），稳固第二阵容推进。
  - **Jevon Carter**（Slot 7, `face_id=7731`, 27 岁）：外线领防工兵与定点射手（3PT 78, BH 82, LQ 83）。
  - **Dwight Howard**（Slot 13, `face_id=1150`, 36 岁）：内线护筐与前场篮板老将（IDef 81, Blk 80, DReb 80）。
  - **Patrick Valentine**（Slot 6, `face_id=1`, 21 岁）：年轻外线防守后卫（PDef 85, LQ 88, Spd 91, Lay 89）。
- **离队人员**：Donte DiVincenzo、Rodney Hood、Semi Ojeleye、Jordan Nwora、P.J. Dozier、Tremont Waters、Justin Robinson。

### 实机诊断与关键失真点
1. **首发球权超载与发起权冗余**：数据库实测首发五虎当前触球和为 `Giannis(98) + Holiday(86) + Middleton(84) + Allen(48) + Lopez(43) = 359`，超出 `[310, 330]` 黄金守恒区间 29 点；且 Giannis、Middleton、Holiday 三人同时开启 `is_play_initiator = 1`，容易抢夺后场推进权。
2. **全队战术纪律（Play Discipline `0x497`）严重偏低**：Holiday (40)、Middleton (25)、Lopez (25)、Allen (20)、Portis (25)、Connaughton (15)、Crowder (10)、Ingles (20) 战术纪律极低，导致阵地战脱离战术乱打。
3. **协防滑块偏低**：`COACHDATA.help_defense` 仅 `42`，无法支撑布登霍尔泽招牌的“大洛深沉退 + 字母哥弱侧扫荡”禁区长城。
4. **部分射手三分倾向偏低**：Grayson Allen (72)、Pat Connaughton (65)、Jae Crowder (70)、Joe Ingles (70) 需提升至 `82 ~ 85` 以匹配一星四射五外空间定位。

---

## 2. 先发五虎与 6~10 人第二阵容轮换（触球守恒）

### 2.1 先发五虎（触球总和 = **320** ∈ `[310, 330]`）
| 槽位 | 球员 | 位置 | 目标时间 | 触球 (原→新) | 出手 (原→新) | 纪律 (原→新) | 发起 | PlayTypes | 战术定位 |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| 0 | Jrue Holiday | PG | 33.0 | 86 → **70** | 82 → **76** | 40 → **82** | 1 | `[4, 14, 1, 12]` | 唯一首发控场发起点 + 外线 DPOY 领防大闸 |
| 10 | Grayson Allen | SG | 27.0 | 48 → **44** | 66 | 20 → **90** | 0 | `[14, 12, 0, 0]` | 五外拉开纯定点射手（`3PT=85`） |
| 1 | Khris Middleton | SF | 33.0 | 84 → **78** | 88 → **84** | 25 → **78** | 0 | `[13, 4, 1, 14]` | 阵地战中距离挡拆解题大师与关键球单挑手 |
| 2 | Giannis Antetokoun | PF | 35.0 | 98 → **88** | 96 → **92** | 85 → **72** | 0 | `[1, 7, 8, 11]` | 禁区核爆第一核心、顺下空接与转换一条龙 |
| 3 | Brook Lopez | C | 28.0 | 43 → **40** | 56 | 25 → **92** | 0 | `[14, 13, 8, 0]` | 外拆五外高炮台（`Roll vs Pop = 80`）+ 沉退护筐柱 |

### 2.2 第二阵容轮换（第 6~10 人触球总和 = **256** ∈ `[250, 280]`）
| 槽位 | 球员 | 位置 | 目标时间 | 触球 (原→新) | 出手 (原→新) | 纪律 (原→新) | 发起 | PlayTypes | 战术定位 |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| 9 | Bobby Portis Jr. | PF/C | 25.0 | 68 | 79 | 25 → **80** | 0 | `[8, 14, 7, 13]` | 最佳第六人，二阵低位与外弹双威胁核（`R/P=65`） |
| 11 | Goran Dragic | PG | 16.0 | 55 → **54** | 60 | 40 → **82** | 1 | `[4, 14, 12, 1]` | 二阵主控发动机，挡拆梳理节奏 |
| 8 | Jae Crowder | PF/SF | 18.0 | 44 → **48** | 50 → **58** | 10 → **90** | 0 | `[14, 11, 0, 0]` | 强硬 3D 侧翼，底角三分与换防顶防 |
| 4 | Pat Connaughton | SG/SF | 15.0 | 46 → **44** | 60 | 15 → **92** | 0 | `[14, 11, 12, 0]` | 替补无球射手与反切突击点 |
| 12 | Joe Ingles | SF | 10.0 | 29 → **42** | 69 → **60** | 20 → **88** | 1 | `[14, 12, 4, 0]` | 侧翼副组织手递手与外线高炮台 |

---

## 3. 攻防博弈体系（Doc 49 攻守并重）

### 3.1 进攻体系：`DEFENSE_FIRST` (6) 带动转换 + 一星四射五外拉开
- **重力闭环**：Giannis 冲筐与低位单打（`1, 7, 8`）迫使对手收缩油漆区，Brook Lopez（`Roll vs Pop = 80`）、Allen、Middleton、Portis 在五外弧顶与底角形成惩罚网；Middleton 与 Holiday 在半场阵地通过高位挡拆与中距离干拔（`13, 4`）解决防线。
- **教练滑块**：`active_system = 6` (Defense First)，`run_play_tendency` 由 `70` 提至 **`75`**，`bench_depth` 由 `9` 提至 **`10`**，`bench_utilization = 60`。

### 3.2 防守博弈体系：大洛深沉退 + 霍勒迪抢过掩护 + 字母哥弱侧扫荡
- **资源支撑**：Lopez（IDef 84, Blk 75）坐镇篮下深沉退；Giannis（IDef 90, LQ 88, DReb 90, Blk 75）担任弱侧自由人补防；Holiday（PDef 89, LQ 80, Stl 76）与 Crowder（PDef 74, IDef 74）外线死缠抢过掩护。
- **博弈策略**：将 `help_defense` 由 `42` 大幅提升至 **`80`**，激活弱侧 Tag 与提前轮转保护油漆区；POE 防守端锁定 `PROTECT_PAINT (13)` + `PLAY_PHYSICAL (18)` + `CRASH_DEFENSIVE_BOARDS (19)`。

---

## 4. 模拟侧重（Scoring Options 1~3 & 6 大 POE）

- **Scoring Option 1**: `Giannis Antetokoun` (`face_id = 2701`)
- **Scoring Option 2**: `Khris Middleton` (`face_id = 2482`)
- **Scoring Option 3**: `Jrue Holiday` (`face_id = 1607`)
- **6 大 POE**：
  - `poe_offense`: `1` (`GET_TO_BASKET`，由 4 调至 1 强化冲击篮筐与造杀伤)
  - `poe_offense_tempo`: `8` (`NEUTRAL_OFFENSE_TEMPO`)
  - `poe_offense_rebound`: `12` (`LIMIT_TRANSITION`)
  - `poe_defense`: `13` (`PROTECT_PAINT`)
  - `poe_defense_physicality`: `18` (`PLAY_PHYSICAL`)
  - `poe_defense_rebound`: `19` (`CRASH_DEFENSIVE_BOARDS`)

---

## 5. 全维倾向安全线与训练负荷管理

- **犯规红线（Doc 85 铁律 5）**：全队核心轮换 10 人实机 `foul` (`0x4B9`) 均处于 `28 ~ 48`（全员 `<= 50`），`hard_foul` (`0x4BA`) 均处于 `5 ~ 25`（全员 `<= 35`），安全无超标。
- **训练模板与防伤负荷（Doc 86）**：
  - **≥ 26 岁巅峰/老将梯队（`intensity = 2` Low）**：核心轮换 10 人年龄均在 `27 ~ 36` 岁之间（Giannis 27, Portis 27, Allen 27, Connaughton 29, Middleton 31, Holiday 32, Crowder 32, Lopez 34, Ingles 35, Dragic 36），全员严格设定 `intensity = 2` (Low) 与 `is_intensity_overriden = 1`，严控长期疲劳与大伤风险。
