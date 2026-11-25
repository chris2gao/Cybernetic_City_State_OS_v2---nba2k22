# 华盛顿奇才 (WAS) 2022-2023 赛季全维度战术体系与攻防博弈执行提案

> **文件标识**: `02_WAS_SEASON_2022_2023_TACTICAL_PROPOSAL.md`  
> **基准快照**: `2022-2023_M01_NOV` (`file:C:/nba2k22/saves/MyLEAGUE0005/league_state.sqlite`)  
> **球队标识**: `Team ID: 2 | Team Abbr: WAS | Washington Wizards`  
> **执教主帅**: 德昂·布朗特 (Deon Blount, `staff_slot: 1139`)  
> **关联规范**: Doc 43 V2 (`v2.0_full_dimensional_native_mod`)、Doc 49（攻守并重）、Doc 85（全维倾向校准）、Doc 86（训练模板与负荷管理）

---

## 1. 新赛季完整阵容与休赛期变动审计

对比 `2021-2022_M01_NOV` 与 `2022-2023_M01_NOV` 实机存档，奇才队在新赛季共注册 **17 名球员**，主教练由小昂塞尔德变更为 **德昂·布朗特 (Deon Blount)**。

### 1.1 休赛期阵容变动
* **离队球员 (8 人)**：Kentavious Caldwell-Pope (`2694`)、Rui Hachimura (`7828`)、Montrezl Harrell (`4409`)、Thomas Bryant (`7541`)、Raul Neto (`2733`)、Aaron Holiday (`7722`)、Anthony Gill (`9879`)、Udonis Haslem (`1118`)。
* **新援与补充 (9 人)**：Monte Morris (`7545`, 27岁控卫)、Delon Wright (`4486`, 30岁防守双能卫)、Kendrick Nunn (`7818`, 27岁得分后卫)、Isaiah Todd (`9923`, 21岁空间前锋)、Jordan Mickey (`4438`, 28岁内线)，以及新秀/补充球员 Steve Burtt (`1769`)、Leon Wood (`1990`)、Anthony Teachey (`2080`)、Deion Dudley (`1`)。
* **保留核心骨架**：Bradley Beal (`2446`, 29岁)、Kristaps Porzingis (`4455`, 27岁)、Kyle Kuzma (`7535`, 27岁)、Deni Avdija (`7998`, 21岁)、Daniel Gafford (`7857`, 24岁)、Corey Kispert (`8057`, 23岁)、Taj Gibson (`1638`, 37岁)、Cassius Winston (`9848`, 24岁)。

### 1.2 实机底层痛点诊断
1. **Deni Avdija 球权严重越位**：新赛季存档中 Avdija 原始 `touches=84`、`shot=84`、`is_play_initiator=1`，几乎与 Beal (`touches=86`) 平起平坐，严重挤压了 Beal 与 Porzingis 的核心回合。
2. **内线犯规天花板失控**：Daniel Gafford (`foul=90, hard_foul=44`)、Kristaps Porzingis (`foul=88, hard_foul=42`)、Taj Gibson (`foul=99, hard_foul=76`)、Kyle Kuzma (`foul=60`)，若不压低至 `<= 50`，模拟引擎极易出现双塔集体六犯毕业的灾难。
3. **主教练协防崩塌与替补过度消耗**：Deon Blount 当前 `ActiveSystem=0 (Balanced)`、`HelpDefense=35`、`BenchUtilization=80`（替补占用过高，削减主力时间），且 `GAMEPLAN` 模拟侧重（376~387）处于未标定状态。

---

## 2. 先发五虎与 6~10 人第二阵容轮换架构

| 轮换层级 | 槽位 | 球员姓名 | Face ID | 年龄 | 位置 | 目标时间 | 战术定位与核心职责 |
| :---: | :---: | :--- | :---: | :---: | :---: | :---: | :--- |
| **首发 1** | 7 | **Monte Morris** | 7545 | 27 | PG | 30.0 | 稳健零失误控场大脑与外线传导手（BH 86, 3PT 78, SPD 87） |
| **首发 2** | 9 | **Bradley Beal** | 2446 | 29 | SG | 36.0 | 球队第一得分大核与中距离硬解王（MID 92, LAY 91, BH 89） |
| **首发 3** | 0 | **Deni Avdija** | 7998 | 21 | SF | 30.0 | 锋线防守大闸、空切与二次策应连接器（LAY 87, PDEF 70） |
| **首发 4** | 1 | **Kyle Kuzma** | 7535 | 27 | PF | 34.0 | 锋线错位单挑与转换突击手（LAY 87, 3PT 80, SPD 81） |
| **首发 5** | 4 | **Kristaps Porzingis** | 4455 | 27 | C | 32.0 | 五外独角兽高炮台与禁区护筐巨塔（3PT 81, LAY 90, BLK 75） |
| **替补 6** | 2 | **Daniel Gafford** | 7857 | 24 | C | 22.0 | 禁区禁飞区护筐神兽与顺下吃饼怪兽（BLK 90, SDK 85） |
| **替补 7** | 11 | **Delon Wright** | 4486 | 30 | PG | 18.0 | 替补外线锁防大闸与抢断发动机（STL 82, PDEF 70） |
| **替补 8** | 12 | **Kendrick Nunn** | 7818 | 27 | SG | 16.0 | 第二阵容微波炉得分手与持球急停箭（MID 90, 3PT 83, SPD 91） |
| **替补 9** | 3 | **Corey Kispert** | 8057 | 23 | SF | 14.0 | 纯无球绕掩护定点神射手（3PT 83, Spot3PT 90） |
| **替补 10** | 10 | **Taj Gibson** | 1638 | 37 | PF | 8.0 | 老将肉搏内线卡位与短时轮换护筐蓝领 |

* **时间守恒**：先发 `162.0` 分钟 + 替补 `78.0` 分钟 = `240.0` 分钟。
* **储备待命**：Isaiah Todd (`8`)、Cassius Winston (`13`)、Leon Wood (`6`)、Steve Burtt (`5`)、Anthony Teachey (`14`)、Jordan Mickey (`21`)、Deion Dudley (`22`)。

---

## 3. 攻防博弈体系与模拟侧重（Doc 49 攻守并重）

### 3.1 进攻体系：`PACE_AND_SPACE (2)` + 比尔挡拆外弹五外空间
1. **双核挡拆空间拉扯**：Bradley Beal（`play_types=[4, 1, 5, 12]`, `Roll vs Pop=20`）与 Monte Morris（`[4, 14, 12, 0]`）作为先发双发起点，搭配 Porzingis（`Roll vs Pop=75`, `[14, 7, 8, 9]`）外弹拉开五外空间，彻底清空禁区供 Beal 突破与 Kuzma（`[1, 11, 14, 6]`）空切。
2. **Avdija 角色收拢**：将 Avdija 转为无球连接器与 3&D 终结者（`is_play_initiator=0`, `touches=48`, `[12, 11, 14, 4]`），根除首发球权踩踏。
3. **替补正交**：Delon Wright 主导防守与组织（`dish=82`），Kendrick Nunn 负责火力输出（`touches=60, shot=72`），Kispert 专注无球三分（`[14, 12, 0, 0]`），Gafford 专注顺下吃饼（`Roll vs Pop=20`）。

### 3.2 防守博弈体系：双塔禁飞区 + 外线轮换锁防
1. **强力修复协防**：`COACHDATA` `help_defense` 从 `35` 提升至 `78`，释放 Gafford (`BLK 90`) 与 Porzingis (`221cm, BLK 75`) 的禁区统治力。
2. **护筐 + 身体对抗 + 后板保护**：确立 `PROTECT_PAINT (13)` + `PLAY_PHYSICAL (18)` + `CRASH_DEFENSIVE_BOARDS (19)`，搭配 Delon Wright (`STL 82`) 与 Avdija 的外线领防压迫，守转攻效率最大化。

### 3.3 教练控制块与模拟侧重（`COACHDATA` & `GAMEPLAN`）
* **COACHDATA**：`active_system=2 (PACE_AND_SPACE)`、`run_play_tendency=75`、`help_defense=78`、`bench_depth=10`、`bench_utilization=55`。
* **GAMEPLAN Scoring Options**：
  * Option 1: **Bradley Beal** (`2446`)
  * Option 2: **Kristaps Porzingis** (`4455`)
  * Option 3: **Kyle Kuzma** (`7535`)
* **GAMEPLAN 6 大 POE**：
  * `poe_offense=4 (PICK_AND_ROLL_OFFENSE)` | `poe_offense_tempo=9 (SHOOT_AT_WILL)` | `poe_offense_rebound=12 (LIMIT_TRANSITION)`
  * `poe_defense=13 (PROTECT_PAINT)` | `poe_defense_physicality=18 (PLAY_PHYSICAL)` | `poe_defense_rebound=19 (CRASH_DEFENSIVE_BOARDS)`

---

## 4. 核心轮换全维倾向校准与防伤训练模板

| 球员姓名 | 年龄 | Touches (0x499) | Shot (0x458) | Dish (0x498) | Disc (0x497) | Roll/Pop (0x49B) | Foul (0x4B8) | HardFoul (0x4B9) | 训练模板 (Pos / Type / Int) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **Monte Morris** | 27 | 54 | 58 | 88 | 90 | 25 | 35 | 12 | PG (0) / PLAYMAKING (6) / **2** |
| **Bradley Beal** | 29 | 86 | 90 | 75 | 90 | 20 | 35 | 12 | SG (1) / OFFENSIVE (2) / **2** |
| **Deni Avdija** | 21 | **48** | **62** | 78 | 88 | 25 | 42 | 15 | SF (2) / TWO_WAY (1) / **3** |
| **Kyle Kuzma** | 27 | 62 | 75 | 52 | 86 | 30 | **42** | 15 | PF (3) / ALL_AROUND (0) / **2** |
| **Kristaps Porzingis** | 27 | 74 | 82 | 55 | 88 | 75 | **42** | **12** | C (4) / OUTSIDE (7) / **2** |
| **Daniel Gafford** | 24 | 44 | 48 | 25 | 95 | 20 | **45** | **15** | C (4) / INSIDE (8) / **3** |
| **Delon Wright** | 30 | 56 | 52 | 82 | 90 | 20 | 42 | 15 | PG (0) / DEFENSIVE (3) / **2** |
| **Kendrick Nunn** | 27 | 60 | 72 | 55 | 85 | 20 | 35 | 12 | SG (1) / OFFENSIVE (2) / **2** |
| **Corey Kispert** | 23 | 50 | 72 | 35 | 95 | 20 | 20 | 10 | SF (2) / OUTSIDE (7) / **3** |
| **Taj Gibson** | 37 | 42 | 46 | 40 | 92 | 35 | **45** | **15** | PF (3) / REBOUNDING (5) / **2** |

* **触球和守恒校验**：
  * 先发 5 人触球和：$54 + 86 + 48 + 62 + 74 = \mathbf{324} \in [310, 330]$。
  * 替补 5 人触球和：$44 + 56 + 60 + 50 + 42 = \mathbf{252} \in [250, 280]$。
* **安全红线校验**：全员 `foul <= 45`（硬性红线 `<= 50`），`hard_foul <= 15`；Gafford (`BH=44`) 与 Gibson (`BH=38`) 保持花式运球 `0`、`no_move_dribble=95`。
* **训练负荷校验**：24 岁及以下（Avdija、Gafford、Kispert）统一 `intensity=3 (Medium)`；26 岁及以上（Morris、Beal、Kuzma、Porzingis、Wright、Nunn、Gibson）统一 `intensity=2 (Low)`，全员 `is_intensity_overriden=1`。
