# 达拉斯独行侠 (DAL) 2022-2023 新赛季（Day 1）全维度战术与博弈调优报告

> **文档状态**: 2022-2023 赛季 Day 1 正式执行提案  
> **球队标识**: Dallas Mavericks (DAL) | `team_id: 17` | 主教练: Jason Kidd (贾森·基德)  
> **底层数据源**: `C:\nba2k22\saves\MyLEAGUE0005\league_state.sqlite` (`snapshot_id = '2022-2023_M01_NOV'`)  
> **关联规范**: Doc 43 V2 (规则四) / Doc 49 (攻守并重) / Doc 85 (倾向校准) / Doc 86 (训练模板与负荷)  
> **生成日期**: 2026-11-25

---

## 1. 新赛季完整阵容与休赛期变动审计

基于 `2022-2023_M01_NOV` 实机数据库切片，DAL 当前激活名册共 17 人。相比 2021-2022 赛季（Doc 55），休赛期阵容迎来超级双核重构：

- **1984 届传奇新秀加盟**：**Sam Perkins**（Slot 13, `face_id=1747`, 1984 届高炮台内线）加盟独行侠，兼具内线护筐与外线投射（Mid 86, IDef 80, Blk 75, DReb 84, 3PT 72），完美填补 5-Out 空间四号位空缺。
- **重磅交易与新援补强**：
  - **Kyrie Irving**（Slot 10, `face_id=2122`, 30 岁）：顶级单挑与控运大师（Mid 97, Lay 90, 3PT 87, BH 99, Stl 75, Spd 89），与 Luka Doncic 组成历史级双核后场。
  - **T.J. Warren**（Slot 14, `face_id=4103`, 29 岁）：侧翼中距离与终结火力（Lay 88, Mid 80, 3PT 76）。
  - **JaVale McGee**（Slot 12, `face_id=1524`, 34 岁）：替补护筐与吃饼中锋（Blk 85, DDk 80）。
  - **Markieff Morris**（Slot 11, `face_id=2140`, 33 岁）、**Tyler Dorsey**（Slot 21, `face_id=7540`, 26 岁）、**Clifton Copeland**（Slot 22, `face_id=1`）。
- **离队人员**：Spencer Dinwiddie、Dorian Finney-Smith、Maxi Kleber、Duncan Robinson、Willie Cauley-Stein 已离队。

### 实机诊断与关键失真点
1. **双核球权与替补使用率过高**：Luka Doncic（`touches = 99, shot = 99`）与 Kyrie Irving（`touches = 94, shot = 94`）同时在场会导致首发触球和严重超标；同时 `COACHDATA.bench_utilization = 90` 过高，会压低双核出场时间。
2. **全队战术纪律集体崩溃**：Reggie Bullock (`10`)、Davis Bertans (`5`)、Tim Hardaway Jr. (`30`)、Josh Green (`30`)、T.J. Warren (`30`)、Sam Perkins (`38`) 战术纪律极低，导致角色球员脱离双核体系乱打。
3. **Sam Perkins 犯规与运球红线违例**：1984 新秀 Sam Perkins 原档 `hard_foul = 51`（远超 35 红线！），且 `BH = 56 < 60` 却拥有 `crossover = 82`（违背铁律 2）。
4. **协防滑块偏低**：`COACHDATA.help_defense` 仅 `37`，无法复现基德时代的高位延误与弱侧提前轮转防守体系。

---

## 2. 先发五虎与 6~11 人第二阵容轮换（触球守恒）

### 2.1 先发五虎（触球总和 = **326** ∈ `[310, 330]`）
| 槽位 | 球员 | 位置 | 目标时间 | 触球 (原→新) | 出手 (原→新) | 分球 (原→新) | 发起 | PlayTypes | 战术定位 |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| 0 | Luka Doncic | PG | 36.0 | 99 → **90** | 99 → **90** | 98 → **92** | 1 | `[4, 1, 10, 14]` | 绝对持球大核，高位挡拆发牌与低位背打小个 |
| 10 | Kyrie Irving | SG | 35.0 | 94 → **82** | 94 → **86** | 75 → **76** | 1 | `[2, 1, 4, 14]` | 顶级单挑副核，关键球攻坚与无球接应三分 |
| 3 | Reggie Bullock | SF | 29.0 | 38 → **42** | 53 → **56** | 35 → **40** | 0 | `[14, 12, 11, 0]` | 首发 3D 领防铁闸与底角定点三分 (`PlayDisc=92`) |
| 13 | Sam Perkins | PF | 28.0 | 71 → **56** | 78 → **72** | 32 → **48** | 0 | `[14, 7, 8, 9]` | 1984 空间高炮台四号位，外拆拉开 (`Roll/Pop=72`) |
| 8 | Christian Wood | C | 28.0 | 62 → **56** | 77 → **74** | 45 → **48** | 0 | `[7, 14, 8, 11]` | 机动挡拆内线，顺下吃饼与外拆三分 (`Roll/Pop=55`) |

### 2.2 第二阵容轮换（第 6~10 人触球和 = **252**，含第 11 人 = **280** ∈ `[250, 280]`）
| 槽位 | 球员 | 位置 | 目标时间 | 触球 (原→新) | 出手 (原→新) | 分球 (原→新) | 发起 | PlayTypes | 战术定位 |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| 1 | Tim Hardaway Jr. | SG | 24.0 | 55 → **64** | 77 → **78** | 35 → **42** | 0 | `[14, 12, 13, 4]` | 二阵容外线主攻炮台与绕掩护三分 |
| 14 | T.J. Warren | SF | 20.0 | 50 → **58** | 69 → **70** | 35 → **40** | 0 | `[1, 11, 13, 14]` | 替补席中距离单打与空切得分手 |
| 5 | Josh Green | SG | 18.0 | 44 → **48** | 55 → **56** | 25 → **45** | 0 | `[11, 14, 12, 0]` | 高能量外线领防尖兵与快攻空切手 |
| 7 | Davis Bertans | PF | 12.0 | 38 → **42** | 64 → **68** | 25 → **35** | 0 | `[14, 12, 0, 0]` | 纯空间外弹高炮台 (`Roll/Pop=85`) |
| 2 | Dwight Powell | C | 14.0 | 34 → **40** | 43 → **46** | 45 → **48** | 0 | `[7, 11, 0, 0]` | 替补掩护墙与顺下吃饼中锋 (`Roll/Pop=18`) |
| 12 | JaVale McGee | C | 6.0 | 33 → **28** | 49 → **46** | 20 → **28** | 0 | `[7, 11, 0, 0]` | 第 11 人护筐肉盾与吃饼替补 |

---

## 3. 攻防博弈体系（Doc 49 攻守并重）

### 3.1 进攻体系：`PACE_AND_SPACE` (2) + 东欧双核 5-Out 错位点名
- **双核引力闭环**：Doncic（`touches=90, dish=92`）与 Irving（`touches=82, shot=86`）错开持球节奏，通过 `run_play_tendency = 85` 与 `PATIENT_OFFENSE (7)` 磨阵地找错位；Perkins 与 Wood 双空间内线拉开三秒区，最大化双核突破与低位背打走廊。
- **教练滑块**：`active_system = 2` (Pace & Space)，`bench_depth = 10`，`bench_utilization = 62`（由 90 下调以保障双核 35+ 分钟）。

### 3.2 防守博弈体系：Perkins/Wood 护筐 + Bullock/Green 外线撕咬 + 提前轮转
- **资源支撑**：Sam Perkins（IDef 80, Blk 75, DReb 84）与 Christian Wood（IDef 74, Blk 72, DReb 88）稳固禁区与后板，Reggie Bullock（PDef 77, Stl 63）与 Josh Green（PDef 75, Spd 87）承担外线领防任务。
- **博弈策略**：`help_defense` 由 `37` 提升至 **`68`**，配合 `PROTECT_PAINT (13)` + `PLAY_PHYSICAL (18)` + `CRASH_DEFENSIVE_BOARDS (19)` + `LIMIT_TRANSITION (12)`，限制对手转换快攻并严防油漆区。

---

## 4. 模拟侧重（Scoring Options 1~3 & 6 大 POE）

- **Scoring Option 1**: `Luka Doncic` (`face_id = 7702`)
- **Scoring Option 2**: `Kyrie Irving` (`face_id = 2122`)
- **Scoring Option 3**: `Christian Wood` (`face_id = 4485`)
- **6 大 POE**：
  - `poe_offense`: `4` (`PICK_AND_ROLL_OFFENSE`)
  - `poe_offense_tempo`: `7` (`PATIENT_OFFENSE`)
  - `poe_offense_rebound`: `12` (`LIMIT_TRANSITION`)
  - `poe_defense`: `13` (`PROTECT_PAINT`)
  - `poe_defense_physicality`: `18` (`PLAY_PHYSICAL`)
  - `poe_defense_rebound`: `19` (`CRASH_DEFENSIVE_BOARDS`)

---

## 5. 全维倾向安全线与训练负荷管理

- **犯规红线**：全队核心轮换 `foul` (`0x4B9`) 均 ≤ 45（Doncic 45, McGee 45, Perkins 42, Powell 42, Wood 40, Irving 40），`hard_foul` (`0x4BA`) ≤ 35（Sam Perkins 51→**20**）。
- **运球门槛**：Sam Perkins（BH 56 < 60）`crossover` 82→**5**、`no_move` 0→**90**；Christian Wood（BH 59 < 60）`spin` 10→**5**、`no_move` 0→**90**。
- **训练模板与防伤负荷（Doc 86）**：
  - **≤ 24 岁成长梯队（`intensity = 3` Medium）**：Luka Doncic (23, PG, `ALL_AROUND=0`)、Josh Green (21, SG, `TWO_WAY=1`)、Sam Perkins (1984 届新秀, PF, `OUTSIDE=7`)。
  - **≥ 26 岁巅峰/老将梯队（`intensity = 2` Low）**：Kyrie Irving (30, SG, `OFFENSIVE=2`)、Reggie Bullock (31, SF, `TWO_WAY=1`)、Christian Wood (27, C, `OUTSIDE=7`)、Tim Hardaway Jr. (30, SG, `OFFENSIVE=2`)、T.J. Warren (29, SF, `OFFENSIVE=2`)、Davis Bertans (29, PF, `OUTSIDE=7`)、Dwight Powell (31, C, `INSIDE=8`)、JaVale McGee (34, C, `INSIDE=8`)。
  - 所有球员 `is_intensity_overriden = 1`。
