# 俄克拉荷马雷霆 (OKC) 2022-2023 新赛季（Day 1）全维度战术与博弈调优报告

> **文档状态**: 2022-2023 赛季 Day 1 正式执行提案  
> **球队标识**: Oklahoma City Thunder (OKC) | `team_id: 24` | 主教练: Mark Daigneault (`staff_slot: 25`)  
> **底层数据源**: `C:\nba2k22\saves\MyLEAGUE0005\league_state.sqlite` (`snapshot_id = '2022-2023_M01_NOV'`)  
> **关联规范**: Doc 43 V2 (规则四) / Doc 49 (攻守并重) / Doc 85 (倾向校准) / Doc 86 (训练模板与负荷) / Doc 72 (OKC 上季基准)  
> **生成日期**: 2026-11-25

---

## 1. 新赛季完整阵容与休赛期变动审计

基于 `2022-2023_M01_NOV` 实机数据库切片，OKC 当前激活名册共 17 人。相比 2021-2022 赛季（Doc 72），青年军核心骨架完整保留，并在侧翼投射与空间内线位置完成精准换血：

- **核心新援补强**：
  - **Isaiah Joe**（Slot 10, `face_id=9845`, 23 岁）：精英级无球三分射手（三分 `83` / 横移 `80` / 控球 `77`），完美填补外线纯射空缺。
  - **Dario Saric**（Slot 11, `face_id=4304`, 28 岁）：空间型策应内线（三分 `75` / 上篮 `81` / 拼抢 `84` / 内防 `70`），接替 Muscala 成为五号位高炮台。
  - **Jordan Nwora**（Slot 13, `face_id=9842`, 24 岁）：高产侧翼得分手（三分 `85` / 中投 `80` / 抢断 `72`）。
  - **其他新援与储备**：Tim McCormick（Slot 12, 20 岁）、Victor Fleming（Slot 14, 21 岁）、Eric Cummings（Slot 22, 21 岁）。
- **离队人员（共 8 人）**：Darius Bazley、Isaiah Roby、Theo Maledon、Kenrich Williams、Ty Jerome、Mike Muscala、Mamadi Diakite、Paul Watson。
- **留队核心（共 11 人）**：Shai Gilgeous-Alexander（Slot 0）、Josh Giddey（Slot 4）、Luguentz Dort（Slot 1）、Aleksej Pokusevski（Slot 2）、Derrick Favors（Slot 3）、Tre Mann（Slot 5）、Gabriel Deck（Slot 6）、Jeremiah Robinson-Earl（Slot 7）、Cody Willis（Slot 8）、Cliff Lucas（Slot 9）、Lonnie Whitney（Slot 21）。

### 实机诊断与关键失真点
1. **协防智商偏低**：`COACHDATA` 中 `HelpDefense = 37`（严重低于现代长臂扫荡体系所需的 `75+`），且 `BenchDepth = 9` 无法覆盖新赛季 10 人轮换。
2. **SGA 球权过度膨胀与吉迪三分倾向归零**：
   - `Shai Gilgeous-Alexander` 当前 `touches = 99`、`shot_tendency = 98`、`play_discipline = 35`，且 `spot_up_three = 11`（三分能力 `86` 却极少接球投三分）；
   - `Josh Giddey` 三分能力已升至 `78`，但 `shot_three` 倾向竟然为 **`0`**！且 `play_discipline = 35`，导致其完全放弃外线空位三分。
3. **全队战术纪律坍塌与替补席失衡**：
   - `Luguentz Dort`（`disc=15`）、`Derrick Favors`（`disc=20`）、`Jeremiah Robinson-Earl`（`disc=15`）、`Dario Saric`（`disc=25`）、`Isaiah Joe`（`disc=5`）战术纪律全线崩盘，尤其是 `Isaiah Joe`（`disc=5`）极易脱离无球跑位体系；
   - `Isaiah Joe` `foul = 64` 突破 Doc 85 `foul <= 50` 红线。

---

## 2. 先发五虎与 6~10 人第二阵容轮换（触球守恒）

### 2.1 先发五虎（触球总和 = **312** ∈ `[310, 330]`）
| 槽位 | 球员 | 位置 | 目标时间 | 触球 (原→新) | 出手 (原→新) | 分球 (原→新) | 发起 | PlayTypes | 战术定位 |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| 0 | Shai Gilgeous-A | PG | 36.0 | 99 → **88** | 98 → **88** | 92 → **84** | 1 | `[1, 4, 2, 14]` | 绝对超巨引擎，单打硬解、挡拆突分与造犯规 |
| 4 | Josh Giddey | SG | 32.0 | 79 → **74** | 66 → **68** | 92 → **90** | 1 | `[4, 11, 9, 14]` | 203cm 高大组织大脑，挡拆发牌、空切与补强三分 |
| 1 | Luguentz Dort | SF | 31.0 | 58 → **56** | 66 → **64** | 40 → **48** | 0 | `[14, 11, 4, 0]` | 联盟顶级 POA 外线大锁 + 纪律化 3&D 终结点 |
| 2 | Aleksej Pokusevski | PF | 26.0 | 52 | 61 → **58** | 65 → **62** | 0 | `[9, 14, 11, 7]` | 213cm 独角兽前锋，高位策应、弱侧护筐与外弹三分 |
| 3 | Derrick Favors | C | 23.0 | 43 → **42** | 40 → **44** | 30 → **35** | 0 | `[7, 11, 0, 0]` | 蓝领肉盾中锋，高质量掩护顺下吃饼与前板拼抢 |

### 2.2 第二阵容 6~10 人（触球总和 = **257** ∈ `[250, 280]`）
| 槽位 | 球员 | 位置 | 目标时间 | 触球 (原→新) | 出手 (原→新) | 分球 (原→新) | 发起 | PlayTypes | 战术定位 |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| 5 | Tre Mann | PG | 24.0 | 58 → **68** | 76 | 50 → **60** | 1 | `[1, 4, 12, 14]` | 超级微波炉第六人，二阵持球急停干拔与单打核心 |
| 10 | Isaiah Joe | SG | 20.0 | 31 → **52** | 53 → **74** | 40 → **45** | 0 | `[14, 12, 11, 0]` | 替补第一无球神射手，绕掩护与手递手三分重炮 |
| 13 | Jordan Nwora | SF | 18.0 | 54 → **52** | 73 → **70** | 25 → **40** | 0 | `[14, 11, 3, 0]` | 侧翼高产得分手，定点三分与错位空切终结 |
| 11 | Dario Saric | C | 16.0 | 45 | 46 → **54** | 65 → **68** | 0 | `[14, 7, 11, 8]` | 五号位空间高炮台，外弹三分与高位策应发牌 |
| 7 | Jeremiah Robinson-E | PF | 14.0 | 36 → **40** | 49 → **48** | 45 → **50** | 0 | `[7, 14, 11, 0]` | 机动型小球五/四号位，拼抢篮板与底角空间 |

* **轮换时间总计**：`36 + 32 + 31 + 26 + 23 + 24 + 20 + 18 + 16 + 14 = 240.0` 分钟完美闭环。

---

## 3. 攻防博弈体系（Doc 49 攻守并重）

### 3.1 进攻体系：`PACE_AND_SPACE` (2) + 双引擎挡拆突分空间网
- **重心微调**：保持 `active_system = 2`（`PACE_AND_SPACE`），将 `run_play_tendency` 由 `65` 提升至 `72`，确保教练为 `Isaiah Joe`、`Dario Saric` 与 `Luguentz Dort` 稳定呼叫无球与外弹战术，同时保留 SGA 与 Giddey 的自由突破空间。
- **引力闭环**：SGA（`LAY=94, CLOSE=97, DF=91, touches=88`）与 Giddey（`PA=89, PIQ=89, dish=90`）双核驱动高位挡拆；一旦对手收缩禁区，外线 `Isaiah Joe (83 3PT)`、`Jordan Nwora (85 3PT)`、`Tre Mann (85 3PT)` 与 `Dario Saric (75 3PT, roll_vs_pop=76)` 形成全空间火力网。

### 3.2 防守博弈体系：多尔特单兵灭火 + 长臂合围扫荡保护禁区
- **资源支撑**：Luguentz Dort（`PD=84, LQ=85, HUS=94, STR=70`）、SGA（`LQ=81, HUS=90`）、Josh Giddey（`PD=75, DRB=79`）、Pokusevski（`BLK=74`）、Derrick Favors（`ID=74, BLK=84, DRB=82`）。
- **博弈策略**：
  - 将 `help_defense` 自 `37` 大幅拉升至 **`78`**，激活全员长臂锋线群（Giddey/SGA/Poku/JRE）在罚球线附近的“掏球协防与传球路线截断”；
  - 外线由 Dort 死锁对手第一持球大核（抢过掩护 + 强硬对抗），内线由 Favors + Poku 协同保护油漆区与后场篮板；
  - `bench_depth` 设为 `10`，`bench_utilization` 设为 `58`，保证高强度防守轮转体能。

---

## 4. 模拟侧重（Scoring Options 1~3 & 6 大 POE）

- **Scoring Option 1**: `Shai Gilgeous-Alexander` (`face_id = 7710`)
- **Scoring Option 2**: `Josh Giddey` (`face_id = 8064`)
- **Scoring Option 3**: `Luguentz Dort` (`face_id = 7910`)
- **6 大 POE**：
  - `poe_offense`: `4` (`PICK_AND_ROLL_OFFENSE`，由 `5` 调整，围绕 SGA 与 Giddey 高位挡拆起手)
  - `poe_offense_tempo`: `9` (`SHOOT_AT_WILL`，由 `8` 调整，释放青年军快攻转换速度)
  - `poe_offense_rebound`: `12` (`LIMIT_TRANSITION`，由 `11` 调整，优先退防落位建立长臂防线)
  - `poe_defense`: `13` (`PROTECT_PAINT`，由 `14` 调整，全员收缩保护三秒区)
  - `poe_defense_physicality`: `18` (`PLAY_PHYSICAL`，由 `17` 调整，依托 Dort 与 Favors 强硬对抗)
  - `poe_defense_rebound`: `19` (`CRASH_DEFENSIVE_BOARDS`，由 `20` 调整，五人合围保护后板后即推反击)

---

## 5. 全维倾向安全线与训练负荷管理

- **犯规红线（Doc 85 铁律五）**：
  - `Isaiah Joe` `foul` 由 `64` 压降至 **`38`**；
  - 全队 10 人核心轮换 `foul` 均 `<= 45`，`hard_foul <= 25`。
- **训练模板与防伤负荷（Doc 86）**：
  - **≤ 24 岁成长梯队（`intensity = 3` Medium）**：Shai Gilgeous-Alexander (24, PG, `ALL_AROUND=0`), Josh Giddey (20, PG, `PLAYMAKING=6`), Luguentz Dort (23, SG, `TWO_WAY=1`), Aleksej Pokusevski (20, PF, `TWO_WAY=1`), Tre Mann (21, PG, `OFFENSIVE=2`), Isaiah Joe (23, SG, `OUTSIDE=7`), Jordan Nwora (24, SF, `OFFENSIVE=2`), Jeremiah Robinson-Earl (21, PF, `TWO_WAY=1`)。
  - **≥ 26 岁老将梯队（`intensity = 2` Low）**：Derrick Favors (31, C, `REBOUNDING=5`), Dario Saric (28, C, `OUTSIDE=7`)。
  - 所有 10 名核心轮换球员 `is_intensity_overriden = 1`。
