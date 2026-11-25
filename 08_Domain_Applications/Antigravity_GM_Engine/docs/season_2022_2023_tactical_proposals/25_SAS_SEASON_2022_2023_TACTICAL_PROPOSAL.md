# 圣安东尼奥马刺 (SAS) 2022-2023 新赛季（Day 1）全维度战术与博弈调优报告

> **文档状态**: 2022-2023 赛季 Day 1 正式执行提案  
> **球队标识**: San Antonio Spurs (SAS) | `team_id: 25` | 主教练: Gregg Popovich (格雷格·波波维奇)  
> **底层数据源**: `C:\nba2k22\saves\MyLEAGUE0005\league_state.sqlite` (`snapshot_id = '2022-2023_M01_NOV'`)  
> **关联规范**: Doc 43 V2 (规则四) / Doc 49 (攻守并重) / Doc 85 (倾向校准) / Doc 86 (训练模板与负荷)  
> **生成日期**: 2026-11-25

---

## 1. 新赛季完整阵容与休赛期变动审计

基于 `2022-2023_M01_NOV` 实机数据库切片，SAS 当前激活名册共 19 人。相比 2021-2022 赛季（Doc 74），马刺经历了彻底的阵容换血：

- **1984 届传奇新秀加盟**：
  - **Alvin Robertson**（Slot 13, `face_id=875`, 22 岁）：历史级外线死亡缠绕大锁与抢断王（外防 91、抢断 95、速度 87、控球 80、传球 78、上篮 81、力量 75），完美契合波波维奇外线高压体系。
  - **Jim Petersen**（Slot 23, `face_id=1958`, 21 岁）：全能防守型内线（内防 78、盖帽 80、力量 82、外防 68、速度 75）。
  - **Rok Pavic**（Slot 24, `face_id=1`, 20 岁）：外线防守新星（外防 87、抢断 80、速度 88、三分 79）。
- **核心新援补强**：
  - **Devonte Graham**（Slot 7, `face_id=7733`, 27 岁）：控球 86、传球 79、三分 79、速度 88，出任首发控球发起点。
  - **Doug McDermott**（Slot 6, `face_id=4096`, 30 岁）：纯无球跑动神射（三分 83、中投 77）。
  - **Zach Collins**（Slot 4, `face_id=7512`, 24 岁）：空间护筐五号位（三分 78、盖帽 75、内防 70）。
  - **Charles Bassey**（Slot 12, `face_id=9945`, 22 岁）、**Isaiah Roby**（Slot 8, `face_id=7864`, 24 岁）、**Khem Birch**（Slot 9）、**Gorgui Dieng**（Slot 11）、**Keita Bates-Diop**（Slot 10）。
- **离队人员**：Lonzo Ball、Jakob Poeltl、Thaddeus Young、Danilo Gallinari、Josh Richardson、Lonnie Walker IV、Bryn Forbes、Hamidou Diallo、Al-Farouq Aminu 已离队。

### 实机诊断与关键失真点
1. **外线核心战术纪律严重崩塌**：Devin Vassell `play_discipline = 25`、Devonte Graham `10`、Doug McDermott `30`、Joshua Primo `35`、Romeo Langford `25`，导致波波维奇“Good-to-Great”传切体系完全无法运转。
2. **犯规倾向严重越界**：Charles Bassey `foul = 99`、Luka Samanic `99`、Sekou Doumbouya `78`、Gorgui Dieng `74`、Joshua Primo `68`、Romeo Langford `62`，极易在模拟中 6 犯离场。
3. **教练替补使用率畸高**：`COACHDATA.bench_utilization` 高达 **`95`**，严重压缩首发决胜时间；`help_defense` 仅 `40`。
4. **Roll vs Pop 倒置**：Doug McDermott `roll_vs_pop = 10`（纯射手却设成顺下）、Charles Bassey `roll_vs_pop = 90`（吃饼中锋却设成外弹）。

---

## 2. 先发五虎与 6~11 人第二阵容轮换（触球守恒）

### 2.1 先发五虎（触球总和 = **324** ∈ `[310, 330]`）
| 槽位 | 球员 | 位置 | 目标时间 | 触球 (原→新) | 出手 (原→新) | 分球 (原→新) | 发起 | PlayTypes | 战术定位 |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| 7 | Devonte Graham | PG | 29.0 | 55 → **64** | 58 → **66** | 70 → **78** | 1 | `[4, 14, 12, 5]` | 首发控卫与外线发牌手，挡拆持球与三分牵制 |
| 13 | Alvin Robertson | SG | 33.0 | 74 → **72** | 76 → **74** | 75 → **78** | 1 | `[4, 1, 11, 12]` | 1984 攻防一体外线大闸，抢断反击与持球冲击 |
| 1 | Devin Vassell | SF | 33.0 | 64 → **66** | 78 → **80** | 45 → **52** | 0 | `[14, 12, 11, 4]` | 顶级 3D 侧翼二号火力点，无球绕掩护三分 |
| 0 | Keldon Johnson | PF | 33.0 | 80 → **76** | 87 → **84** | 50 → **54** | 0 | `[1, 11, 6, 14]` | 球队第一重装冲筐得分核心与错位强攻点 |
| 4 | Zach Collins | C | 27.0 | 42 → **46** | 52 → **56** | 45 → **52** | 0 | `[7, 14, 9, 0]` | 空间型五号位（`Roll vs Pop = 65`），高位策应与护筐 |

### 2.2 第二阵容轮换（第 6~10 人触球和 = **252**，含第 11 人 = **280** ∈ `[250, 280]`）
| 槽位 | 球员 | 位置 | 目标时间 | 触球 (原→新) | 出手 (原→新) | 分球 (原→新) | 发起 | PlayTypes | 战术定位 |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| 2 | Joshua Primo | PG/SG | 20.0 | 30 → **56** | 58 → **64** | 35 → **55** | 1 | `[4, 14, 12, 0]` | 二阵容双能卫主控新星 |
| 6 | Doug McDermott | SF | 18.0 | 38 → **52** | 66 → **68** | 30 → **38** | 0 | `[14, 12, 11, 0]` | 纯无球跑动神射（`Roll vs Pop = 80`） |
| 5 | Romeo Langford | SG | 16.0 | 41 → **48** | 51 → **52** | 25 → **40** | 0 | `[11, 4, 12, 0]` | 侧翼空切与防守轮换 |
| 23 | Jim Petersen | PF | 16.0 | 60 → **52** | 72 → **58** | 65 → **60** | 0 | `[8, 11, 7, 0]` | 替补防守内线与低位策应 |
| 12 | Charles Bassey | C | 15.0 | 17 → **44** | 47 → **50** | 15 → **32** | 0 | `[7, 11, 0, 0]` | 替补护筐吃饼中锋（`Roll vs Pop = 18`，犯规降至 45） |
| 8 | Isaiah Roby | PF | 8.0 | 42 → **28** | 55 → **50** | 40 → **42** | 0 | `[7, 11, 0, 0]` | 第 11 人机动前锋 |

---

## 3. 攻防博弈体系（Doc 49 攻守并重）

### 3.1 进攻体系：`PACE_AND_SPACE` (2) + 波波维奇动态传切
- **耐心传导与空间拉扯**：Keldon Johnson 突破/低位重力吸引收缩，Vassell 与 McDermott 两侧绕掩护拉满三分威胁，Graham 与 Robertson 双持球发起确保球权流畅运转。
- **教练滑块**：`active_system = 2` (Pace & Space)，`run_play_tendency = 85`，`bench_depth = 10`，`bench_utilization = 58`（自 95 压降）。

### 3.2 防守博弈体系：Alvin Robertson 死亡缠绕 + Collins/Petersen/Bassey 立体护筐
- **资源支撑**：Alvin Robertson（外防 91、抢断 95）领防对方箭头，Vassell（外防 85）封锁侧翼，Collins（盖帽 75）/ Petersen（盖帽 80）/ Bassey（盖帽 80）轮番镇守禁区。
- **博弈策略**：`help_defense` 自 `40` 提升至 **`78`**，执行波波维奇招牌团队协防；POE 防守锁定 `PROTECT_PAINT (13)` + `PLAY_PHYSICAL (18)` + `CRASH_DEFENSIVE_BOARDS (19)`。

---

## 4. 模拟侧重（Scoring Options 1~3 & 6 大 POE）

- **Scoring Option 1**: `Keldon Johnson` (`face_id = 7848`)
- **Scoring Option 2**: `Devin Vassell` (`face_id = 8003`)
- **Scoring Option 3**: `Alvin Robertson` (`face_id = 875`)
- **6 大 POE**：
  - `poe_offense`: `4` (`PICK_AND_ROLL_OFFENSE`)
  - `poe_offense_tempo`: `7` (`PATIENT_OFFENSE`)
  - `poe_offense_rebound`: `12` (`LIMIT_TRANSITION`)
  - `poe_defense`: `13` (`PROTECT_PAINT`)
  - `poe_defense_physicality`: `18` (`PLAY_PHYSICAL`)
  - `poe_defense_rebound`: `19` (`CRASH_DEFENSIVE_BOARDS`)

---

## 5. 全维倾向安全线与训练负荷管理

- **犯规红线**：全队核心轮换 `foul` (`0x4B9`) 均 ≤ 45（Charles Bassey 由 99 压降至 **45**；Joshua Primo 由 68 压降至 **38**；Romeo Langford 由 62 压降至 **40**）。
- **训练模板与防伤负荷（Doc 86）**：
  - **≤ 24 岁成长梯队（`intensity = 3` Medium）**：Joshua Primo (19, PG, `ALL_AROUND=0`), Jim Petersen (21, PF, `DEFENSIVE=3`), Alvin Robertson (22, SG, `TWO_WAY=1`), Devin Vassell (22, SF, `TWO_WAY=1`), Charles Bassey (22, C, `INSIDE=8`), Keldon Johnson (23, PF, `OFFENSIVE=2`), Romeo Langford (23, SG, `TWO_WAY=1`), Zach Collins (24, C, `OUTSIDE=7`), Isaiah Roby (24, PF, `TWO_WAY=1`)。
  - **≥ 26 岁巅峰/老将梯队（`intensity = 2` Low）**：Devonte Graham (27, PG, `PLAYMAKING=6`), Doug McDermott (30, SF, `OUTSIDE=7`)。
  - 所有球员 `is_intensity_overriden = 1`。
