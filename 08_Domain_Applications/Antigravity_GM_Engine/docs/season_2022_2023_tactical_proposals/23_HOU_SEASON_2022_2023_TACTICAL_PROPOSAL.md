# 休斯顿火箭 (HOU) 2022-2023 新赛季（Day 1）全维度战术与博弈调优报告

> **文档状态**: 2022-2023 赛季 Day 1 正式执行提案  
> **球队标识**: Houston Rockets (HOU) | `team_id: 23` | 主教练: Stephen Silas (斯蒂芬·塞拉斯)  
> **底层数据源**: `C:\nba2k22\saves\MyLEAGUE0005\league_state.sqlite` (`snapshot_id = '2022-2023_M01_NOV'`)  
> **关联规范**: Doc 43 V2 (规则四) / Doc 49 (攻守并重) / Doc 85 (倾向校准) / Doc 86 (训练模板与负荷)  
> **生成日期**: 2026-11-25

---

## 1. 新赛季完整阵容与休赛期变动审计

基于 `2022-2023_M01_NOV` 实机数据库切片，HOU 当前激活名册共 17 人。相比 2021-2022 赛季（Doc 79），休赛期迎来了建队基石级的重磅升级：

- **1984 届传奇状元加盟**：**Hakeem Olajuwon**（Slot 13, `face_id=952`, 22 岁）空降休斯顿！带来历史级的禁区统治力（内防 95、盖帽 95、力量 88、抢断 70、速度 73、中投 77、背身强攻与低位终结），瞬间将火箭的护筐天花板从联盟垫底拉升至争冠级。
- **新秀与深度补强**：
  - **Leo Roberts**（Slot 10, `face_id=1`, 19 岁）：极具爆发力的外线双能侧翼（三分 86、中投 89、上篮 90、外防 92、速度 99），是第二阵容最锋利的攻防尖刀。
  - **Bruno Fernando**（Slot 12, `face_id=7853`, 24 岁）：内线吃饼与篮板替补（上篮 81、力量 78）。
  - **Cameron Oliver**（Slot 21, `face_id=9892`, 26 岁）与 **Derrick Doyle**（Slot 22, `face_id=1`, 23 岁）：深度储备。
- **离队人员**：Danuel House、D.J. Augustin、Dante Exum、Anthony Lamb、Tyler Bey 已离队。

### 实机诊断与关键失真点
1. **首发球权严重拥堵**：实测首发五虎当前触球和为 `Jalen Green(94) + Hakeem Olajuwon(92) + Alperen Sengun(92) + Kevin Porter Jr.(69) + Jae'Sean Tate(48) = 395`，远超 `[310, 330]` 守恒区间，导致外线双枪与内线双塔互相抢球。
2. **中锋推进权限异常**：Alperen Sengun（速度 55、控球 58）底层 `is_play_initiator = 1`，会与 KPJ、Green 争抢后场推进权，必须置 `0`；同时 Leo Roberts 在替补席应专注无球终结与反击（置 `0`）。
3. **奥拉朱旺分球偏低与角色球员战术纪律崩塌**：Olajuwon `dish_to_open_man` 仅 `34`，面对低位包夹难以第一时间外传射手；Tate (`40`)、KPJ (`45`)、KJ Martin (`40`)、Garuba (`45`)、Christophe (`45`)、Fernando (`25`) 战术纪律过低，脱离体系乱打。
4. **犯规天花板越界**：Bruno Fernando `foul = 74`（越界 50 红线）。
5. **教练协防滑块严重过低**：`COACHDATA.help_defense` 仅 `22`，无法支撑 Olajuwon 坐镇禁区后的弱侧轮转；`active_system = 6`（Seven Seconds）与内线双核不匹配。

---

## 2. 先发五虎与 6~11 人第二阵容轮换（触球守恒）

### 2.1 先发五虎（触球总和 = **324** ∈ `[310, 330]`）
| 槽位 | 球员 | 位置 | 目标时间 | 触球 (原→新) | 出手 (原→新) | 分球 (原→新) | 发起 | PlayTypes | 战术定位 |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| 3 | Kevin Porter Jr. | PG | 31.0 | 69 → **64** | 79 → **74** | 65 → **72** | 1 | `[4, 1, 14, 12]` | 首发控卫，挡拆持球发起与定点三分 |
| 1 | Jalen Green | SG | 35.0 | 94 → **82** | 97 → **88** | 65 → **62** | 1 | `[4, 1, 14, 12]` | 外线第一进攻大核，转换闪电突击与三分 |
| 2 | Jae'Sean Tate | SF | 26.0 | 48 → **42** | 43 → **46** | 40 → **45** | 0 | `[11, 6, 14, 0]` | 强硬侧翼粘合剂，空切袭筐与错位强吃 |
| 5 | Alperen Sengun | PF | 32.0 | 92 → **62** | 85 → **74** | 88 → **82** | 0 | `[9, 8, 7, 12]` | 高位策应“小约基奇”轴心，高低位喂球奥拉朱旺 |
| 13 | Hakeem Olajuwon | C | 35.0 | 92 → **74** | 89 → **86** | 34 → **58** | 0 | `[8, 9, 7, 13]` | 内线绝对统治核心，低位梦幻脚步单打与护筐大闸 |

### 2.2 第二阵容轮换（第 6~10 人触球和 = **250**，含第 11 人 = **274** ∈ `[250, 280]`）
| 槽位 | 球员 | 位置 | 目标时间 | 触球 (原→新) | 出手 (原→新) | 分球 (原→新) | 发起 | PlayTypes | 战术定位 |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| 10 | Leo Roberts | SG/SF | 24.0 | 59 → **56** | 46 → **68** | 54 → **58** | 0 | `[14, 11, 4, 12]` | 二阵容外线爆破点与外防大锁（外防 92、速度 99） |
| 0 | John Wall | PG | 20.0 | 49 → **54** | 54 → **56** | 75 → **78** | 1 | `[4, 1, 12, 0]` | 替补指挥官，推反击与喂饼 |
| 8 | Josh Christophe | SG | 16.0 | 59 → **52** | 74 → **68** | 45 → **50** | 1 | `[1, 4, 12, 14]` | 板凳微波炉突击手 |
| 4 | Kenyon Martin Jr. | PF | 16.0 | 44 → **46** | 53 → **56** | 30 → **35** | 0 | `[7, 11, 14, 0]` | 高空空接轰炸机（`Roll vs Pop = 18`） |
| 7 | Usman Garuba | C | 15.0 | 45 → **42** | 35 → **42** | 35 → **42** | 0 | `[7, 11, 8, 0]` | 替补防守扫荡绞肉机（内防 75、外防 75、盖帽 77） |
| 12 | Bruno Fernando | C | 6.0 | 20 → **24** | 43 → **46** | 30 → **32** | 0 | `[7, 11, 0, 0]` | 第 11 人吃饼内线，犯规压降至 45 |

---

## 3. 攻防博弈体系（Doc 49 攻守并重）

### 3.1 进攻体系：`PACE_AND_SPACE` (2) + 高低位双核引力
- **内外双核引力闭环**：Olajuwon 低位背身（`8, 9`）与 Sengun 高位策应（`9, 8`）形成罕见的高低位传切双塔；一旦对手包夹内线，Olajuwon（分球提升至 58）与 Sengun（分球 82）立即外传 Green、KPJ 与 Leo Roberts。
- **教练滑块**：`active_system = 2` (Pace & Space)，`run_play_tendency = 75`，`bench_depth = 10`，`bench_utilization = 55`。

### 3.2 防守博弈体系：奥拉朱旺禁飞区 + 外线闪电追击
- **资源支撑**：Olajuwon（内防 95、盖帽 95、抢断 70）坐镇禁区，Garuba（内防 75/外防 75/盖帽 77）与 Leo Roberts（外防 92、速度 99）提供顶级换防与外线压迫。
- **博弈策略**：`help_defense` 自 `22` 大幅提升至 **`68`**，确保弱侧轮转及时到位；POE 防守锁定 `PROTECT_PAINT (13)` + `PLAY_PHYSICAL (18)` + `CRASH_DEFENSIVE_BOARDS (19)`。

---

## 4. 模拟侧重（Scoring Options 1~3 & 6 大 POE）

- **Scoring Option 1**: `Jalen Green` (`face_id = 8053`)
- **Scoring Option 2**: `Hakeem Olajuwon` (`face_id = 952`)
- **Scoring Option 3**: `Kevin Porter Jr.` (`face_id = 7849`)
- **6 大 POE**：
  - `poe_offense`: `4` (`PICK_AND_ROLL_OFFENSE`)
  - `poe_offense_tempo`: `9` (`SHOOT_AT_WILL`)
  - `poe_offense_rebound`: `12` (`LIMIT_TRANSITION`)
  - `poe_defense`: `13` (`PROTECT_PAINT`)
  - `poe_defense_physicality`: `18` (`PLAY_PHYSICAL`)
  - `poe_defense_rebound`: `19` (`CRASH_DEFENSIVE_BOARDS`)

---

## 5. 全维倾向安全线与训练负荷管理

- **犯规红线**：全队核心轮换 `foul` (`0x4B9`) 均 ≤ 45（Bruno Fernando 由 74 压降至 **45**；Olajuwon/Roberts 维持 45；Tate/Garuba 维持 42）。
- **训练模板与防伤负荷（Doc 86）**：
  - **≤ 24 岁成长梯队（`intensity = 3` Medium）**：Leo Roberts (19, SG, `TWO_WAY=1`), Jalen Green (20, SG, `OFFENSIVE=2`), Alperen Sengun (20, PF, `PLAYMAKING=6`), Usman Garuba (20, C, `DEFENSIVE=3`), Josh Christophe (20, SG, `OFFENSIVE=2`), Kenyon Martin Jr. (21, PF, `ATHLETIC=4`), Kevin Porter Jr. (22, PG, `PLAYMAKING=6`), Hakeem Olajuwon (22, C, `INSIDE=8`), Bruno Fernando (24, C, `INSIDE=8`)。
  - **≥ 26 岁巅峰/老将梯队（`intensity = 2` Low）**：Jae'Sean Tate (27, SF, `TWO_WAY=1`), John Wall (32, PG, `PLAYMAKING=6`)。
  - 所有球员 `is_intensity_overriden = 1`。
