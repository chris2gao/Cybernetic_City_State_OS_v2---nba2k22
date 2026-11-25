# 克利夫兰骑士 (CLE) 2022-2023 新赛季（Day 1）全维度战术与博弈调优报告

> **文档状态**: 2022-2023 赛季 Day 1 正式执行提案  
> **球队标识**: Cleveland Cavaliers (CLE) | `team_id: 4` | 主教练: J.B. Bickerstaff (J.B. 比克斯塔夫)  
> **底层数据源**: `C:\nba2k22\saves\MyLEAGUE0005\league_state.sqlite` (`snapshot_id = '2022-2023_M01_NOV'`)  
> **关联规范**: Doc 43 V2 (规则四) / Doc 49 (攻守并重) / Doc 85 (倾向校准) / Doc 86 (训练模板与负荷)  
> **生成日期**: 2026-11-25

---

## 1. 新赛季完整阵容与休赛期变动审计

基于 `2022-2023_M01_NOV` 实机数据库切片，CLE 当前激活名册共 17 人。相比 2021-2022 赛季（Doc 66），球队保留了“米切尔 + 加兰 + 莫布利 + 阿伦”四大核心，并在休赛期引入老将拼图与 1984 届新秀：

- **1984 届新秀加盟**：
  - **Devin Durrant**（Slot 14, `face_id=1987`, 23 岁）：侧翼前锋（Mid 72, Lay 72, BH 68, PDef 68, IDef 65, DReb 68, Spd 75），补充第二阵容锋线冲击力与防守韧性。
- **休赛期新援与轮换调整**：
  - **Danny Green**（Slot 12, `face_id=1652`, 35 岁）：冠军经验 3D 侧翼（3PT 82, PDef 74）。
  - **Raul Neto**（Slot 11, `face_id=2733`, 30 岁）：替补双能控卫（3PT 80, BH 83, Spd 84）。
  - **Robin Lopez**（Slot 13, `face_id=1521`, 34 岁）：替补护筐中锋。
  - **Cedi Osman**（Slot 9, `face_id=4305`, 27 岁）：替补锋线火力点。
- **离队人员**：Kevin Love、Tristan Thompson、Mfiondu Kabengele、Tacko Fall、Denzel Valentine。

### 实机诊断与关键失真点
1. **首发球权严重超载**：数据库实测首发五虎当前触球和为 `Garland(99) + Mitchell(93) + Allen(70) + Mobley(66) + Okoro(33) = 361`，超出 `[310, 330]` 黄金守恒区间 31 点；其中 Garland (99) 与 Mitchell (93) 球权过满，Allen (70) 作为纯吃饼中锋占用了过多球权。
2. **全队战术纪律偏低**：Garland (40)、Okoro (35)、Allen (30)、Rubio (30)、Osman (30)、Wade (10) 战术纪律严重偏低，导致双塔与角色球员脱离既定挡拆战术。
3. **射手三分倾向偏低与老将犯规超标**：
   - Ricky Rubio `shot_three` 仅 `43`，Isaac Okoro 仅 `52`，需适度回调以维持空间威慑；
   - **Cedi Osman `foul = 56`**（突破 50 红线）、**Devin Durrant `hard_foul = 60`**（突破 35 红线），必须压降。
4. **协防滑块偏低**：`COACHDATA.help_defense` 仅 `40`，未能激活 Mobley + Allen 双塔禁飞区的弱侧协防统治力。

---

## 2. 先发五虎与 6~10 人第二阵容轮换（触球守恒）

### 2.1 先发五虎（触球总和 = **320** ∈ `[310, 330]`）
| 槽位 | 球员 | 位置 | 目标时间 | 触球 (原→新) | 出手 (原→新) | 纪律 (原→新) | 发起 | PlayTypes | 战术定位 |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| 0 | Darius Garland | PG | 35.0 | 99 → **82** | 93 → **82** | 40 → **85** | 1 | `[5, 4, 14, 12]` | 阵地战进攻总指挥，高位挡拆发牌与外线投射 |
| 8 | Donovan Mitchell | SG | 35.0 | 93 → **86** | 95 → **90** | 50 → **82** | 1 | `[4, 1, 14, 13]` | 绝对第一得分核心与关键球单挑硬解王 |
| 1 | Isaac Okoro | SF | 26.0 | 33 → **46** | 47 → **54** | 35 → **90** | 0 | `[14, 11, 4, 0]` | 首发 3D 外线大锁，底角三分与空切袭筐 |
| 3 | Evan Mobley | PF | 34.0 | 66 → **62** | 75 | 50 → **85** | 0 | `[7, 11, 9, 8]` | 短顺下策应轴心（`R/P=35`）与弱侧扫荡大闸 |
| 2 | Jarrett Allen | C | 31.0 | 70 → **44** | 74 → **62** | 30 → **95** | 0 | `[7, 11, 0, 0]` | 护筐吃饼中锋（`R/P=15`），专职顺下空接与前板 |

### 2.2 第二阵容轮换（第 6~10 人触球总和 = **254** ∈ `[250, 280]`）
| 槽位 | 球员 | 位置 | 目标时间 | 触球 (原→新) | 出手 (原→新) | 纪律 (原→新) | 发起 | PlayTypes | 战术定位 |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| 7 | Caris LeVert | SG/SF | 25.0 | 65 → **66** | 75 | 50 → **80** | 1 | `[4, 1, 14, 11]` | 最佳第六人，二阵第一持球单挑爆破手 |
| 10 | Ricky Rubio | PG | 16.0 | 67 → **50** | 43 | 30 → **88** | 1 | `[5, 4, 12, 0]` | 替补控场大师，高位喂饼梳理二阵 |
| 9 | Cedi Osman | SF | 15.0 | 20 → **48** | 58 | 30 → **88** | 0 | `[14, 11, 0, 0]` | 替补侧翼射手与转换空切点（`foul 56→42`） |
| 4 | Dean Wade | PF | 13.0 | 28 → **46** | 43 | 10 → **92** | 0 | `[14, 7, 11, 0]` | 空间型四号位（`R/P=75`, `3PT=78`） |
| 14 | Devin Durrant | SF/PF | 10.0 | 69 → **44** | 71 → **58** | 55 → **82** | 0 | `[11, 14, 4, 0]` | 1984 届新秀锋线，空切冲抢与侧翼换防（`hfoul 60→25`） |

---

## 3. 攻防博弈体系（Doc 49 攻守并重）

### 3.1 进攻体系：`DEFENSE` (7) 基底下的双卫挡拆 + 双塔高低位
- **双核引力闭环**：Garland 与 Mitchell 轮番发起高位挡拆（`4, 5`），Allen（`Roll vs Pop = 15`）深顺下吃饼牵制护筐者，Mobley（`Roll vs Pop = 35`）在罚球线短顺下接球完成二次分球或抛投终结；弱侧 Okoro、Wade、Osman 拉开底角空间。
- **教练滑块**：`active_system = 7` (Defense)，`run_play_tendency = 75`，`bench_depth` 由 `9` 提至 **`10`**，`bench_utilization = 60`。

### 3.2 防守博弈体系：双塔禁飞区深沉退 + 奥科罗外线锁喉
- **资源支撑**：Mobley（Blk 87, IDef 79, DReb 82）与 Allen（IDef 82, Blk 80, DReb 87）组成全联盟顶级内线双塔；Okoro（PDef 83, LQ 81）与 Mitchell（LQ 89, Spd 97）封锁外线持球点。
- **博弈策略**：将 `help_defense` 由 `40` 提升至 **`78`**，全面激活双塔弱侧协防补帽与护筐轮转；POE 防守端锁定 `PROTECT_PAINT (13)` + `PLAY_PHYSICAL (18)` + `CRASH_DEFENSIVE_BOARDS (19)`。

---

## 4. 模拟侧重（Scoring Options 1~3 & 6 大 POE）

- **Scoring Option 1**: `Donovan Mitchell` (`face_id = 7510`)
- **Scoring Option 2**: `Darius Garland` (`face_id = 7824`)
- **Scoring Option 3**: `Evan Mobley` (`face_id = 8052`)
- **6 大 POE**：
  - `poe_offense`: `4` (`PICK_AND_ROLL_OFFENSE`)
  - `poe_offense_tempo`: `7` (`PATIENT_OFFENSE`)
  - `poe_offense_rebound`: `10` (`CRASH_OFFENSIVE_BOARDS`)
  - `poe_defense`: `13` (`PROTECT_PAINT`)
  - `poe_defense_physicality`: `18` (`PLAY_PHYSICAL`)
  - `poe_defense_rebound`: `19` (`CRASH_DEFENSIVE_BOARDS`)

---

## 5. 全维倾向安全线与训练负荷管理

- **犯规红线（Doc 85 铁律 5）**：将超标的 Cedi Osman `foul` 由 `56` 压降至 **`42`**，Devin Durrant `hard_foul` 由 `60` 压降至 **`25`**，全队核心轮换 10 人 `foul <= 45`、`hard_foul <= 25`。
- **训练模板与防伤负荷（Doc 86）**：
  - **≤ 24 岁成长梯队（`intensity = 3` Medium）**：Isaac Okoro (21, SF, `TWO_WAY=1`), Evan Mobley (21, PF, `ALL_AROUND=0`), Darius Garland (22, PG, `PLAYMAKING=6`), Devin Durrant (23, SF, `ALL_AROUND=0`), Jarrett Allen (24, C, `INSIDE=8`)。
  - **≥ 26 岁巅峰/老将梯队（`intensity = 2` Low）**：Dean Wade (25/26, PF, `TWO_WAY=1`), Donovan Mitchell (26, SG, `OFFENSIVE=2`), Cedi Osman (27, SF, `OUTSIDE=7`), Caris LeVert (28, SG, `OFFENSIVE=2`), Ricky Rubio (32, PG, `PLAYMAKING=6`)。
  - 所有球员均置 `is_intensity_overriden = 1`。
