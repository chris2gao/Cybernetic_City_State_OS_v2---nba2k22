# 底特律活塞 (DET) 2022-2023 新赛季（Day 1）全维度战术与博弈调优报告

> **文档状态**: 2022-2023 赛季 Day 1 正式执行提案  
> **球队标识**: Detroit Pistons (DET) | `team_id: 21` | 主教练: Dwane Casey (德韦恩·凯西)  
> **底层数据源**: `C:\nba2k22\saves\MyLEAGUE0005\league_state.sqlite` (`snapshot_id = '2022-2023_M01_NOV'`)  
> **关联规范**: Doc 43 V2 (规则四) / Doc 49 (攻守并重) / Doc 85 (倾向校准) / Doc 86 (训练模板与负荷)  
> **生成日期**: 2026-11-25

---

## 1. 新赛季完整阵容与休赛期变动审计

基于 `2022-2023_M01_NOV` 实机数据库切片，DET 当前激活名册共 17 人。相比 2021-2022 赛季（Doc 77），休赛期阵容发生大幅重塑：

- **1984 届新秀加盟**：**Tony Campbell**（Slot 14, `face_id=1997`, 21 岁）加盟活塞，具备出色的运动能力与突破终结（Spd 84, Lay 80, DDk 80, Mid 78, PDef 72），充实锋线冲击力。
- **核心新援补强**：
  - **Bojan Bogdanovic**（Slot 10, `face_id=2560`, 33 岁）：老将空间炮台（Spot3 90, 3pT 85, 3PT 79, Mid 77），为 Cade Cunningham 拉开宝贵进攻空间。
  - **Alec Burks**（Slot 8, `face_id=2138`, 31 岁）：外线双能卫与优质射手（3PT 86, Spot3 85, BH 79, Spd 82）。
  - **James Wiseman**（Slot 7, `face_id=7950`, 21 岁）：高顺位年轻中锋（Lay 91, DDk 78, Blk 78, DReb 80, IDef 74），与 Isaiah Stewart 组成年轻内线双塔。
  - **Marvin Bagley III**（Slot 11, `face_id=7701`, 23 岁）：替补席运动型前场（DDk 84, DReb 83, IDef 73）。
  - **Cory Joseph**（Slot 6, `face_id=2164`, 31 岁）、**R.J. Hampton**（Slot 9, `face_id=7955`, 21 岁）、**Hamidou Diallo**（Slot 12, `face_id=7744`, 24 岁, DDk 93）、**Kelan Martin**（Slot 5, `face_id=7911`, 27 岁）。
- **离队人员**：Saddiq Bey、Kelly Olynyk、Chris Duarte、Moses Moody、Josh Jackson、Saben Lee、Trey Lyles、Edmond Sumner 已离队。

### 实机诊断与关键失真点
1. **犯规倾向严重爆表（铁律 5 违例）**：James Wiseman `foul = 99`、Hamidou Diallo `78`、Kelan Martin `78`、Cory Joseph `70`、Marvin Bagley III `64`，在日历模拟中极易迅速 6 犯离场。
2. **内线花式运球越界（铁律 2 违例）**：James Wiseman（`BH = 55 < 60`）原始 `crossover = 99, no_move = 0`，极易导致中锋外线强行变向失误，必须压低至 `crossover <= 5, no_move >= 90`。
3. **战术纪律与球权分配失衡**：Cade Cunningham（`touches = 99, play_discipline = 35`）、Bojan（`35`）、Burks（`25`）、Livers（`25`）战术纪律偏低；而 Wiseman（`touches = 23`）作为首发内线触球严重不足。
4. **协防滑块偏低**：`COACHDATA.help_defense` 仅 `39`，无法支撑活塞年轻内线群的弱侧护筐协防。

---

## 2. 先发五虎与 6~11 人第二阵容轮换（触球守恒）

### 2.1 先发五虎（触球总和 = **320** ∈ `[310, 330]`）
| 槽位 | 球员 | 位置 | 目标时间 | 触球 (原→新) | 出手 (原→新) | 分球 (原→新) | 发起 | PlayTypes | 战术定位 |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| 0 | Cade Cunningham | PG | 35.0 | 99 → **88** | 95 → **88** | 92 | 1 | `[4, 1, 14, 2]` | 203cm 绝对持球大核，高位挡拆发牌与单挑解题 |
| 8 | Alec Burks | SG | 28.0 | 55 → **60** | 67 → **72** | 55 → **58** | 0 | `[14, 12, 4, 11]` | 外线双能卫，定点三分与手递手副攻点 |
| 10 | Bojan Bogdanovic | SF | 31.0 | 60 → **66** | 70 → **78** | 45 → **48** | 0 | `[14, 8, 3, 12]` | 老将空间射手与侧翼错位单打终结点 |
| 3 | Isaiah Stewart | PF | 30.0 | 43 → **52** | 59 → **58** | 30 → **40** | 0 | `[7, 11, 14, 8]` | 铁血护筐大闸与空间顺下/外弹四号位 (`Roll/Pop=45`) |
| 7 | James Wiseman | C | 28.0 | 23 → **54** | 62 → **68** | 25 → **35** | 0 | `[7, 11, 8, 0]` | 高顺位护筐吃饼中锋 (`Roll/Pop=28`) |

### 2.2 第二阵容轮换（第 6~10 人触球和 = **260**，含第 11 人 = **280** ∈ `[250, 280]`）
| 槽位 | 球员 | 位置 | 目标时间 | 触球 (原→新) | 出手 (原→新) | 分球 (原→新) | 发起 | PlayTypes | 战术定位 |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| 1 | Killian Hayes | PG | 22.0 | 70 → **60** | 49 → **52** | 85 → **86** | 1 | `[4, 1, 12, 14]` | 二阵容主控大脑与外线领防后卫 |
| 11 | Marvin Bagley III | PF | 22.0 | 50 → **56** | 75 → **68** | 35 → **38** | 0 | `[7, 11, 8, 0]` | 替补吃饼内线与前场篮板冲击手 (`Roll/Pop=25`) |
| 14 | Tony Campbell | SF | 18.0 | 68 → **54** | 78 → **68** | 64 → **60** | 0 | `[11, 3, 14, 12]` | 1984 新秀侧翼突击手与空切终结者 |
| 4 | Isaiah Livers | SF | 16.0 | 32 → **46** | 48 → **58** | 35 → **45** | 0 | `[14, 12, 11, 0]` | 替补定点三分高炮台 (`Roll/Pop=80`) |
| 12 | Hamidou Diallo | SG | 14.0 | 20 → **44** | 53 → **60** | 40 → **42** | 0 | `[11, 3, 1, 0]` | 暴力冲筐转换先锋与空切袭筐点 (`Roll/Pop=25`) |
| 6 | Cory Joseph | PG | 6.0 | 18 → **20** | 38 → **40** | 55 → **58** | 0 | `[4, 14, 0, 0]` | 第 11 人老将稳控储备 |

---

## 3. 攻防博弈体系（Doc 49 攻守并重）

### 3.1 进攻体系：`PACE_AND_SPACE` (2) + 高位挡拆双塔纵深
- **大核引力闭环**：Cade Cunningham（`touches=88, dish=92`）主导高位挡拆（`4`），利用 Bojan 与 Burks 的外线牵制力撕裂防线；Wiseman 与 Stewart 形成“一顺下吃饼、一外弹拉开”的立体内线组合，避免禁区拥堵。
- **教练滑块**：`active_system = 2` (Pace & Space)，`run_play_tendency = 75`，`bench_depth = 10`，`bench_utilization = 58`。

### 3.2 防守博弈体系：Stewart + Wiseman 双塔护筐 + 强硬身体对抗
- **资源支撑**：Stewart（Blk 86, IDef 73, DReb 84）与 Wiseman（Blk 78, IDef 74, DReb 80）构筑禁区双闸，Cade（203cm, PDef 80）与 Hayes（PDef 73, Stl 62）外线换防施压。
- **博弈策略**：`help_defense` 由 `39` 大幅提升至 **`72`**，强化弱侧对顺下人的 Tag 与提前轮转；POE 防守端锁定 `PROTECT_PAINT (13)` + `PLAY_PHYSICAL (18)` + `CRASH_DEFENSIVE_BOARDS (19)`，重现底特律铁血防守底色。

---

## 4. 模拟侧重（Scoring Options 1~3 & 6 大 POE）

- **Scoring Option 1**: `Cade Cunningham` (`face_id = 8050`)
- **Scoring Option 2**: `Bojan Bogdanovic` (`face_id = 2560`)
- **Scoring Option 3**: `James Wiseman` (`face_id = 7950`)
- **6 大 POE**：
  - `poe_offense`: `4` (`PICK_AND_ROLL_OFFENSE`)
  - `poe_offense_tempo`: `8` (`NEUTRAL_OFFENSE_TEMPO`)
  - `poe_offense_rebound`: `10` (`CRASH_OFFENSIVE_BOARDS`)
  - `poe_defense`: `13` (`PROTECT_PAINT`)
  - `poe_defense_physicality`: `18` (`PLAY_PHYSICAL`)
  - `poe_defense_rebound`: `19` (`CRASH_DEFENSIVE_BOARDS`)

---

## 5. 全维倾向安全线与训练负荷管理

- **犯规红线**：全队核心轮换 `foul` (`0x4B9`) 均 ≤ 45（Wiseman 99→**45**、Diallo 78→**44**、Joseph 70→**40**、Bagley 64→**44**、Cade 45、Stewart 45），`hard_foul` (`0x4BA`) ≤ 30。
- **运球门槛**：Wiseman（BH 55 < 60）`crossover` 99→**5**、`no_move` 0→**92**。
- **训练模板与防伤负荷（Doc 86）**：
  - **≤ 24 岁成长梯队（`intensity = 3` Medium）**：Cade Cunningham (21, PG, `ALL_AROUND=0`)、Isaiah Stewart (21, PF, `TWO_WAY=1`)、James Wiseman (21, C, `INSIDE=8`)、Killian Hayes (21, PG, `PLAYMAKING=6`)、Marvin Bagley III (23, PF, `INSIDE=8`)、Tony Campbell (21, SF, `ALL_AROUND=0`)、Isaiah Livers (24, SF, `TWO_WAY=1`)、Hamidou Diallo (24, SG, `ATHLETIC=4`)。
  - **≥ 26 岁巅峰/老将梯队（`intensity = 2` Low）**：Alec Burks (31, SG, `OFFENSIVE=2`)、Bojan Bogdanovic (33, SF, `OUTSIDE=7`)、Cory Joseph (31, PG, `PLAYMAKING=6`)。
  - 所有球员 `is_intensity_overriden = 1`。
