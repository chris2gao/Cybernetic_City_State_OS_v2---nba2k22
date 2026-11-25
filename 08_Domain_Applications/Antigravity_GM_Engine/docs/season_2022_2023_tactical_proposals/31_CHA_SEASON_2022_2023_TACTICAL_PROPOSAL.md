# 夏洛特黄蜂 (CHA) 2022-2023 赛季全维度战术体系与攻防博弈执行提案

> **文件标识**: `31_CHA_SEASON_2022_2023_TACTICAL_PROPOSAL.md`  
> **基准快照**: `2022-2023_M01_NOV` (`file:C:/nba2k22/saves/MyLEAGUE0005/league_state.sqlite`)  
> **球队标识**: `Team ID: 31 | Team Abbr: CHA | Charlotte Hornets`  
> **执教主帅**: 欧文·泰勒 (Owen Taylor, `staff_slot: 1148`)  
> **关联规范**: Doc 43 V2 (`v2.0_full_dimensional_native_mod`)、Doc 49（攻守并重）、Doc 85（全维倾向校准）、Doc 86（训练模板与负荷管理）

---

## 1. 新赛季完整阵容与休赛期变动审计

对比 `2021-2022_M01_NOV` 与 `2022-2023_M01_NOV` 实机存档，黄蜂队在新赛季共注册 **16 名球员**，主教练由詹姆斯·博雷戈变更为 **欧文·泰勒 (Owen Taylor)**。

### 1.1 休赛期阵容变动
* **离队球员 (4 人)**：Will Barton (`2483`)、Jalen McDaniels (`7871`)、Wesley Iwundu (`7553`)、Vlatko Cancar (`7892`)。
* **新援与补充 (5 人)**：Dennis Smith Jr. (`7507`, 25岁控卫)、Theo Maledon (`9833`, 21岁双能卫)、Melvin Turpin (`2039`, 22岁内线)、Benjamin Cannon (`1`, 23岁内线)、Josh Hall (`9876`, 22岁锋线)。
* **保留核心骨架**：LaMelo Ball (`7953`, 21岁)、Terry Rozier III (`4460`, 28岁)、Miles Bridges (`7711`, 24岁)、Gordon Hayward (`1809`, 32岁)、P.J. Washington (`7831`, 24岁)、Kelly Oubre Jr. (`4449`, 26岁)、James Bouknight (`8068`, 22岁)、Cody Martin (`7855`, 27岁)、Kai Jones (`8069`, 21岁)。

### 1.2 实机底层痛点诊断
1. **拉梅洛·鲍尔球权过载与纪律偏低**：`touches=99`、`shot=94` 接近满格，但 `play_discipline=45`、`hard_foul=48`（高于 Doc 85 安全上限 35）。
2. **锋线与内线犯规倾向严重超标**：P.J. Washington (`foul=75, hard_foul=38`)、Miles Bridges (`foul=80`)、Kelly Oubre Jr. (`foul=70`)、Kai Jones (`foul=85, hard_foul=44`)、Dennis Smith Jr. (`foul=85`)，在日历模拟中极易提前陷入犯规危机导致核心时间失真。
3. **主教练控制块防守真空与节奏偏慢**：Owen Taylor 当前 `ActiveSystem=0 (Balanced)`、`HelpDefense=35`（全联盟垫底级别协防漏洞）、`Tempo=40`（严重压制黄蜂快攻天赋）、`RunPlayTendency=90`（过于死板），且 `GAMEPLAN` 模拟侧重（376~387）处于未标定状态。

---

## 2. 先发五虎与 6~10 人第二阵容轮换架构

| 轮换层级 | 槽位 | 球员姓名 | Face ID | 年龄 | 位置 | 目标时间 | 战术定位与核心职责 |
| :---: | :---: | :--- | :---: | :---: | :---: | :---: | :--- |
| **首发 1** | 0 | **LaMelo Ball** | 7953 | 21 | PG | 35.0 | 绝对第一持球大核与转换推进引擎（3PT 88, BH 94, STL 82） |
| **首发 2** | 1 | **Terry Rozier III** | 4460 | 28 | SG | 33.0 | 无球/持球双威胁冷箭手与关键球单挑手（3PT 84, MID 83） |
| **首发 3** | 13 | **Miles Bridges** | 7711 | 24 | SF | 34.0 | 暴力空切暴扣箭头与空间终结点（DDK 91, 3PT 84） |
| **首发 4** | 2 | **Gordon Hayward** | 1809 | 32 | PF | 28.0 | 半场阵地第二发牌点与错位策应锋线（3PT 82, MID 79） |
| **首发 5** | 3 | **P.J. Washington** | 7831 | 24 | C | 30.0 | 五外高炮台空间五号位与弱侧护筐者（3PT 84, BLK 81） |
| **替补 6** | 4 | **Kelly Oubre Jr.** | 4449 | 26 | SF | 24.0 | 第六人活力突击手与反击终结锋线（LAY 85, DDK 84） |
| **替补 7** | 12 | **Dennis Smith Jr.** | 7507 | 25 | PG | 18.0 | 二阵控球推进器与外线撕咬领防尖兵（SPD 87, BH 86, STL 75） |
| **替补 8** | 5 | **James Bouknight** | 8068 | 22 | SG | 14.0 | 替补外线微波炉得分手（SPD 89, LAY 84, 3PT 80） |
| **替补 9** | 11 | **Cody Martin** | 7855 | 27 | SG | 12.0 | 侧翼 3&D 铁血防守大锁与无球空切点 |
| **替补 10** | 6 | **Kai Jones** | 8069 | 21 | C | 12.0 | 弹簧护筐吃饼中锋（IDEF 83, BLK 80, DDK 83） |

* **时间守恒**：先发 `160.0` 分钟 + 替补 `80.0` 分钟 = `240.0` 分钟。
* **储备待命**：Vernon Carey Jr. (`7`)、J.T. Thor (`8`)、Theo Maledon (`10`)、Benjamin Cannon (`9`)、Melvin Turpin (`14`)、Josh Hall (`21`)。

---

## 3. 攻防博弈体系与模拟侧重（Doc 49 攻守并重）

### 3.1 进攻体系：`PACE_AND_SPACE (2)` + 五外空接快打
1. **三球引力驱动**：LaMelo Ball 作为唯一先发战术发起人（`is_play_initiator=1`），搭配 `play_types=[4, 14, 5, 12]` 与 `dish_to_open_man=90`，利用高位挡拆与超远三分引力撕裂防线，喂饼 Bridges (`[11, 7, 14, 10]`) 或外传 Rozier (`[14, 4, 1, 12]`) 与 Washington (`[14, 7, 11, 0]`, `Roll vs Pop=70`)。
2. **替补正交分流**：由 Dennis Smith Jr.（`is_play_initiator=1`, `[4, 1, 12, 0]`）主导二阵推进，Oubre 与 Bouknight 分别承担无球空切与定点/单打终结，Kai Jones 专注顺下吃饼（`Roll vs Pop=20`），避免与先发核心混编时抢球。

### 3.2 防守博弈体系：护筐补位 + 外线长臂截断反击
1. **修补协防真空**：`COACHDATA` `help_defense` 从 `35` 拉升至 `75`，彻底解决内线频繁漏人被暴扣的失真问题。
2. **禁区保护 + 身体对抗**：依托 P.J. Washington (`BLK 81`) 与 Kai Jones (`BLK 80, IDEF 83`)，确立 `PROTECT_PAINT (13)` + `PLAY_PHYSICAL (18)` + `CRASH_DEFENSIVE_BOARDS (19)`，抢下后场篮板后立刻由三球与 Smith Jr. 发动高速转换反击。

### 3.3 教练控制块与模拟侧重（`COACHDATA` & `GAMEPLAN`）
* **COACHDATA**：`active_system=2 (PACE_AND_SPACE)`、`run_play_tendency=75`、`help_defense=75`、`bench_depth=10`、`bench_utilization=55`。
* **GAMEPLAN Scoring Options**：
  * Option 1: **LaMelo Ball** (`7953`)
  * Option 2: **Terry Rozier III** (`4460`)
  * Option 3: **Miles Bridges** (`7711`)
* **GAMEPLAN 6 大 POE**：
  * `poe_offense=1 (GET_TO_BASKET)` | `poe_offense_tempo=9 (SHOOT_AT_WILL)` | `poe_offense_rebound=12 (LIMIT_TRANSITION)`
  * `poe_defense=13 (PROTECT_PAINT)` | `poe_defense_physicality=18 (PLAY_PHYSICAL)` | `poe_defense_rebound=19 (CRASH_DEFENSIVE_BOARDS)`

---

## 4. 核心轮换全维倾向校准与防伤训练模板

| 球员姓名 | 年龄 | Touches (0x499) | Shot (0x458) | Dish (0x498) | Disc (0x497) | Roll/Pop (0x49B) | Foul (0x4B8) | HardFoul (0x4B9) | 训练模板 (Pos / Type / Int) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| **LaMelo Ball** | 21 | 86 | 86 | 90 | 82 | 20 | 35 | 15 | PG (0) / PLAYMAKING (6) / **3** |
| **Terry Rozier III** | 28 | 76 | 82 | 55 | 85 | 25 | 30 | 12 | SG (1) / OFFENSIVE (2) / **2** |
| **Miles Bridges** | 24 | 66 | 80 | 40 | 88 | 20 | **42** | 15 | SF (2) / ATHLETIC (4) / **3** |
| **Gordon Hayward** | 32 | 54 | 68 | 75 | 88 | 40 | 30 | 12 | PF (3) / ALL_AROUND (0) / **2** |
| **P.J. Washington** | 24 | 38 | 65 | 40 | 92 | 70 | **44** | **15** | C (4) / OUTSIDE (7) / **3** |
| **Kelly Oubre Jr.** | 26 | 58 | 74 | 35 | 85 | 20 | **42** | 15 | SF (2) / OFFENSIVE (2) / **2** |
| **Dennis Smith Jr.** | 25 | 54 | 60 | 75 | 85 | 20 | **42** | 15 | PG (0) / TWO_WAY (1) / **2** |
| **James Bouknight** | 22 | 52 | 72 | 40 | 82 | 20 | 25 | 12 | SG (1) / OFFENSIVE (2) / **3** |
| **Cody Martin** | 27 | 48 | 48 | 48 | 92 | 20 | 40 | **15** | SG (1) / DEFENSIVE (3) / **2** |
| **Kai Jones** | 21 | 40 | 48 | 20 | 90 | 20 | **44** | **15** | C (4) / ATHLETIC (4) / **3** |

* **触球和守恒校验**：
  * 先发 5 人触球和：$86 + 76 + 66 + 54 + 38 = \mathbf{320} \in [310, 330]$。
  * 替补 5 人触球和：$58 + 54 + 52 + 48 + 40 = \mathbf{252} \in [250, 280]$。
* **安全红线校验**：全员 `foul <= 44`（硬性红线 `<= 50`），`hard_foul <= 15`；Kai Jones (`BH=37 < 60`) 保持 `no_move_dribble=95` 与花式运球 `0` 锁死非受迫失误。
* **训练负荷校验**：24 岁及以下（LaMelo、Bridges、Washington、Bouknight、Kai Jones）统一 `intensity=3 (Medium)`；26 岁及以上（Rozier、Hayward、Oubre、Martin）及 25 岁防守工兵 Dennis Smith Jr. 统一 `intensity=2 (Low)`，全员 `is_intensity_overriden=1`。
