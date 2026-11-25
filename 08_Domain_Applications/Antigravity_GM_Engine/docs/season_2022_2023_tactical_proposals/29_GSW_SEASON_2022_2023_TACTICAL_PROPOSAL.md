# 金州勇士 (GSW) 2022-2023 新赛季（Day 1）全维度战术与博弈调优报告

> **文档状态**: 2022-2023 赛季 Day 1 正式执行提案  
> **球队标识**: Golden State Warriors (GSW) | `team_id: 29` | 主教练: Steve Kerr (史蒂夫·科尔)  
> **底层数据源**: `C:\nba2k22\saves\MyLEAGUE0005\league_state.sqlite` (`snapshot_id = '2022-2023_M01_NOV'`)  
> **关联规范**: Doc 43 V2 (规则四) / Doc 49 (攻守并重) / Doc 85 (倾向校准) / Doc 86 (训练模板与负荷)  
> **生成日期**: 2026-11-25

---

## 1. 新赛季完整阵容与休赛期变动审计

基于 `2022-2023_M01_NOV` 实机数据库切片，GSW 当前激活名册共 17 人。相比 2021-2022 冠军赛季（Doc 50），休赛期完成了卫冕后的阵容微调：

- **冠军首发五虎完整保留**：**Stephen Curry**（Slot 0, `face_id=1612`, 34 岁）、**Klay Thompson**（Slot 1, `face_id=2137`, 32 岁）、**Andrew Wiggins**（Slot 2, `face_id=4091`, 27 岁）、**Draymond Green**（Slot 3, `face_id=2478`, 32 岁）、**Kevon Looney**（Slot 9, `face_id=4431`, 26 岁）。
- **核心新援补强**：
  - **Donte DiVincenzo**（Slot 11, `face_id=7716`, 25 岁）：外防 82、横移 85、抢断 76、三分 82，完美填补小佩顿与波特离队后的外线领防与副攻空缺。
  - **JaMychal Green**（Slot 6, `face_id=4252`, 32 岁）：空间型四五号位（三分 79、前板 83）。
  - **Jalen Smith**（Slot 14, `face_id=8005`, 22 岁）：年轻运动型内线储备（内防 75、后板 72、突破扣篮 83）。
  - **Ty Jerome**（Slot 8, `face_id=7843`, 25 岁）：稳健控卫储备（控球 87、三分 82）。
- **回流与成长**：**Gary Payton II**（Slot 10, `face_id=7412`, 29 岁）在阵；**Jordan Poole**（Slot 4, 23 岁）、**Jonathan Kuminga**（Slot 5, 20 岁）、**Moses Moody**（Slot 7, 20 岁）进入新赛季核心轮换。
- **离队人员**：Anfernee Simons（回归 POR）、Otto Porter Jr.、Nemanja Bjelica、James Wiseman、Cody Zeller。

### 实机诊断与关键失真点
1. **首发球权超标**：实测先发五人当前触球和为 `Curry(98) + Thompson(77) + Wiggins(65) + Green(81) + Looney(32) = 353`，超出 `[310, 330]` 守恒区间；而二阵 **Poole(88) + Kuminga(87)** 触球严重虚高。
2. **哨兵球员 Klay Thompson 纪律与角色锁**：Thompson 当前 `play_discipline = 25`、`dish = 25`、`touches = 77`，必须收束其 `touches` 至 **60**、保持 `is_play_initiator = 0` 与纯无球终结战术 `[14, 12, 11, 13]`，同时拉高 `play_discipline` 至 **90**，严防其沦为低效持球单打手。
3. **全队战术纪律普遍偏低**：Curry (`50`)、Green (`25`)、Looney (`15`)、Poole (`35`)、DiVincenzo (`30`)、JaMychal Green (`20`) 战术纪律均过低，无法有效执行科尔 `PACE_AND_SPACE` 与 `WARRIORS` 无球传切。
4. **协防滑块与犯规红线**：COACHDATA `help_defense` 仅 `40`（压制追梦扫荡威力）；替补 **Moses Moody** `foul = 58`、**Ty Jerome** `foul = 56`、**Jalen Smith** `foul = 74` 均超出 `<= 50` 安全红线。

---

## 2. 先发五虎与 6~11 人第二阵容轮换（触球守恒）

### 2.1 先发五虎（触球总和 = **324** ∈ `[310, 330]`）
| 槽位 | 球员 | 位置 | 目标时间 | 触球 (原→新) | 出手 (原→新) | 分球 (原→新) | 发起 | PlayTypes | 战术定位 |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| 0 | Stephen Curry | PG | 34.0 | 98 → **88** | 96 → **88** | 92 → **90** | 1 | `[4, 14, 12, 1]` | 绝对第一引力大核，超远三分与高位挡拆发起 |
| 1 | Klay Thompson | SG | 32.0 | 77 → **60** | 92 → **84** | 25 → **28** | 0 | `[14, 12, 11, 13]` | **【哨兵】无球纯终结神射**，零控球发起权，绕掩护接球即投 |
| 2 | Andrew Wiggins | SF | 32.0 | 65 → **62** | 71 → **72** | 50 → **50** | 0 | `[11, 3, 14, 8]` | 攻防一体侧翼大锁，弱侧反切与错位攻坚 |
| 3 | Draymond Green | PF | 31.0 | 81 → **78** | 52 → **35** | 96 → **96** | 1 | `[7, 9, 13, 11]` | 短顺下 4v3 策应枢纽与防守司令官 |
| 9 | Kevon Looney | C | 24.0 | 32 → **36** | 36 → **38** | 45 → **48** | 0 | `[7, 11, 10, 0]` | 纯吃饼掩护中锋（`Roll vs Pop = 15`）与前板苦力 |

### 2.2 第二阵容轮换（第 6~10 人触球和 = **250**，含第 11 人 = **280** ∈ `[250, 280]`）
| 槽位 | 球员 | 位置 | 目标时间 | 触球 (原→新) | 出手 (原→新) | 分球 (原→新) | 发起 | PlayTypes | 战术定位 |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| 4 | Jordan Poole | PG | 28.0 | 88 → **72** | 88 → **80** | 65 → **72** | 1 | `[4, 1, 14, 12]` | 二阵容主控发动机与挡拆持球突击手 |
| 11 | Donte DiVincenzo | SG | 22.0 | 52 → **50** | 61 → **60** | 65 → **68** | 1 | `[14, 12, 4, 11]` | 替补 3&D 副攻手，抢断推反击与定点三分 |
| 10 | Gary Payton II | SG | 16.0 | 62 → **38** | 52 → **50** | 35 → **42** | 0 | `[11, 7, 14, 0]` | 94 英尺领防撕咬与底线幽灵空切扣将 |
| 5 | Jonathan Kuminga | PF | 18.0 | 87 → **48** | 90 → **64** | 35 → **42** | 0 | `[11, 3, 7, 8]` | 运动怪兽空切冲筐与转换终结（`Roll vs Pop = 25`） |
| 7 | Moses Moody | SF | 14.0 | 44 → **42** | 54 → **58** | 40 → **45** | 0 | `[14, 11, 12, 0]` | 年轻 3&D 侧翼，定点三分与无球跑位 |
| 6 | JaMychal Green | C | 10.0 | 35 → **30** | 43 → **46** | 30 → **38** | 0 | `[14, 7, 11, 0]` | 空间型替补五号位（`Roll vs Pop = 75`） |

---

## 3. 攻防博弈体系（Doc 49 攻守并重）

### 3.1 进攻体系：`PACE_AND_SPACE` (2) + 库里引力 4v3 传切闭环
- **引力与无球纯终结**：Curry 持球挡拆与无球绕掩护吸引包夹（`dish = 90`），出球给罚球线短顺下的 Draymond Green（`dish = 96`）形成 4 打 3；Klay Thompson 严格保持 `is_play_initiator = 0`，专注 `[14, 12, 11, 13]` 无球跑位接球即投。
- **教练滑块**：`active_system = 2` (`PACE_AND_SPACE`)，`run_play_tendency = 65`（兼顾自由传切与战术呼叫），`bench_depth = 11`，`bench_utilization = 65`。

### 3.2 防守博弈体系：追梦自由人扫荡 + 维金斯/迪文琴佐/小佩顿外线铁闸
- **外线三层锁防**：Wiggins 主防对手核心锋线，DiVincenzo 与 Payton II 轮番领防对手顶级后卫并执行全场撕咬。
- **内线扫荡与协防拉满**：`help_defense` 由 `40` 大幅提升至 **`80`**，最大化 Draymond Green 的自由人预轮转（Pre-Rotate）与弱侧刷卡破坏力，配合 Looney 沉退卡位保护后场篮板后第一时间推转换反击。

---

## 4. 模拟侧重（Scoring Options 1~3 & 6 大 POE）

- **Scoring Option 1**: `Stephen Curry` (`face_id = 1612`)
- **Scoring Option 2**: `Klay Thompson` (`face_id = 2137`)
- **Scoring Option 3**: `Jordan Poole` (`face_id = 7847`)
- **6 大 POE**：
  - `poe_offense`: `2` (`GET_SHOOTERS_OPEN`)
  - `poe_offense_tempo`: `9` (`SHOOT_AT_WILL`)
  - `poe_offense_rebound`: `12` (`LIMIT_TRANSITION`)
  - `poe_defense`: `15` (`LIMIT_PERIMETER_SHOTS`)
  - `poe_defense_physicality`: `18` (`PLAY_PHYSICAL`)
  - `poe_defense_rebound`: `21` (`RUN_TRANSITION`)

---

## 5. 全维倾向安全线与训练负荷管理

- **犯规红线**：修正 Moses Moody (`58 → 42`)，全队核心轮换 `foul` (`0x4B9`) 均 `<= 48`（Draymond Green 48, Looney 44, Payton II 44），`hard_foul` (`0x4BA`) `<= 32`。
- **蓝领运球保护**：Gary Payton II 限制花式运球（`crossover: 35 → 5`），杜绝非受迫性失误。
- **训练模板与防伤负荷（Doc 86）**：
  - **≤ 24 岁成长梯队（`intensity = 3` Medium）**：Jordan Poole (23, PG, `OFFENSIVE=2`), Jonathan Kuminga (20, PF, `ATHLETIC=4`), Moses Moody (20, SF, `TWO_WAY=1`)。
  - **≥ 25/26 岁巅峰/老将梯队（`intensity = 2` Low）**：Stephen Curry (34, PG, `OFFENSIVE=2`), Klay Thompson (32, SG, `OUTSIDE=7`), Andrew Wiggins (27, SF, `TWO_WAY=1`), Draymond Green (32, PF, `DEFENSIVE=3`), Kevon Looney (26, C, `REBOUNDING=5`), Donte DiVincenzo (25, SG, `TWO_WAY=1`), Gary Payton II (29, SG, `DEFENSIVE=3`), JaMychal Green (32, C, `OUTSIDE=7`)。
  - 所有球员 `is_intensity_overriden = 1`。
