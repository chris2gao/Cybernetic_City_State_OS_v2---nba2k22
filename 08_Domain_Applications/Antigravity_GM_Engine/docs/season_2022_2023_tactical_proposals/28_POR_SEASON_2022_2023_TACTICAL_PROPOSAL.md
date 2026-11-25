# 波特兰开拓者 (POR) 2022-2023 新赛季（Day 1）全维度战术与博弈调优报告

> **文档状态**: 2022-2023 赛季 Day 1 正式执行提案  
> **球队标识**: Portland Trail Blazers (POR) | `team_id: 28` | 主教练: Chauncey Billups (昌西·比卢普斯)  
> **底层数据源**: `C:\nba2k22\saves\MyLEAGUE0005\league_state.sqlite` (`snapshot_id = '2022-2023_M01_NOV'`)  
> **关联规范**: Doc 43 V2 (规则四) / Doc 49 (攻守并重) / Doc 85 (倾向校准) / Doc 86 (训练模板与负荷)  
> **生成日期**: 2026-11-25

---

## 1. 新赛季完整阵容与休赛期变动审计

基于 `2022-2023_M01_NOV` 实机数据库切片，POR 当前激活名册共 17 人。相比 2021-2022 赛季（Doc 69），休赛期完成了关键的年轻化与侧翼防守升级：

- **核心回归与保留**：**Anfernee Simons**（Slot 7, `face_id=7723`, 23 岁，三分 89、扣篮 89、速度 88）回归波特兰，与 **Damian Lillard**（Slot 0, `face_id=2449`, 32 岁）、**Jerami Grant**（Slot 2, `face_id=4105`, 28 岁）、**Jusuf Nurkic**（Slot 8, `face_id=4111`, 28 岁）组成四核骨架。
- **侧翼防守重磅补强**：
  - **Matisse Thybulle**（Slot 6, `face_id=7839`, 25 岁）：外防 93、横移 95、抢断 98、盖帽 80、三分 72，彻底填补 Lillard 身侧的领防大锁空缺。
  - **Cameron Reddish**（Slot 4, `face_id=7829`, 23 岁）：提供二阵容侧翼尺寸、运动冲击（扣篮 80）与定点三分（71）。
- **1984 届传奇新秀加盟**：
  - **Sam Bowie**（Slot 10, `face_id=1970`, 23 岁）：内防 84、盖帽 88、前板 80、后板 85、中投 71，成为优质替补护筐与高位策应内线。
  - **Jerome Kersey**（Slot 11, `face_id=1749`, 20 岁）：突破扣篮 88、外防 78、抢断 80、前板 78、速度 84，极高上限的铁血锋线。
- **离队人员**：Josh Hart、Nassir Little、Eric Bledsoe、Nickeil Alexander-Walker 已离队。

### 实机诊断与关键失真点
1. **首发球权超标**：实测先发五人当前触球和为 `Lillard(95) + Simons(88) + Thybulle(40) + Grant(75) + Nurkic(54) = 352`，超出 `[310, 330]` 守恒区间，Lillard 与 Simons 双枪持球权重叠。
2. **教练体系与协防参数错配**：COACHDATA `active_system` 为 `7 (DEFENSE)` 而非 `2 (PACE_AND_SPACE)`；`help_defense` 仅 `37`，无法支撑 Nurkic 沉退护筐下的弱侧轮转。
3. **年轻内线与替补犯规/运球失真**：**Keon Johnson** `foul = 52`、**Drew Eubanks** `foul = 84`（均突破 Doc 85 `<= 50` 红线），且 Eubanks 竟有 `crossover = 100`、`roll_vs_pop = 85`（三分仅 28 却 85% 外弹）。
4. **战术纪律过低**：Thybulle (`15`)、Reddish (`35`)、Winslow (`40`)、Nurkic (`50`) 战术纪律过低，影响半场跑位连贯性。

---

## 2. 先发五虎与 6~11 人第二阵容轮换（触球守恒）

### 2.1 先发五虎（触球总和 = **324** ∈ `[310, 330]`）
| 槽位 | 球员 | 位置 | 目标时间 | 触球 (原→新) | 出手 (原→新) | 分球 (原→新) | 发起 | PlayTypes | 战术定位 |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| 0 | Damian Lillard | PG | 35.0 | 95 → **88** | 96 → **88** | 92 → **84** | 1 | `[4, 14, 1, 12]` | 第一进攻大核，Logo 超远三分与高位挡拆发起 |
| 7 | Anfernee Simons | SG | 34.0 | 88 → **68** | 88 → **80** | 55 → **68** | 1 | `[4, 14, 12, 1]` | 第二持球点与无球接球三分微波炉 |
| 6 | Matisse Thybulle | SF | 27.0 | 40 → **40** | 42 → **46** | 35 → **45** | 0 | `[14, 11, 0, 0]` | 顶级外线领防大锁 + 底角三分空切 3D |
| 2 | Jerami Grant | PF | 34.0 | 75 → **74** | 81 → **78** | 55 → **58** | 0 | `[1, 3, 14, 11]` | 侧翼错位单挑手与强侧终结副攻手 |
| 8 | Jusuf Nurkic | C | 28.0 | 54 → **54** | 60 → **58** | 68 → **70** | 0 | `[7, 8, 11, 0]` | 掩护巨墙、顺下吃饼（`Roll vs Pop = 25`）与高位策应 |

### 2.2 第二阵容轮换（第 6~10 人触球和 = **252**，含第 11 人 = **278** ∈ `[250, 280]`）
| 槽位 | 球员 | 位置 | 目标时间 | 触球 (原→新) | 出手 (原→新) | 分球 (原→新) | 发起 | PlayTypes | 战术定位 |
| :---: | :--- | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :--- |
| 4 | Cameron Reddish | SF | 22.0 | 49 → **54** | 68 → **66** | 30 → **45** | 0 | `[14, 11, 6, 0]` | 二阵容侧翼火力点，定点三分与快攻冲筐 |
| 3 | Justise Winslow | PF | 18.0 | 45 → **52** | 42 → **46** | 75 → **78** | 1 | `[11, 4, 13, 0]` | 二阵容组织前锋（Point Forward），推反击与空切 |
| 11 | Jerome Kersey | PF | 16.0 | 71 → **50** | 76 → **64** | 68 → **55** | 0 | `[11, 3, 7, 0]` | 1984 铁血锋线新秀，空切暴扣与前场篮板冲抢 |
| 10 | Sam Bowie | C | 16.0 | 73 → **52** | 78 → **62** | 75 → **70** | 0 | `[7, 8, 9, 11]` | 1984 护筐策应中锋（`Roll vs Pop = 40`） |
| 5 | Keon Johnson | SG | 10.0 | 22 → **44** | 51 → **56** | 45 → **50** | 1 | `[4, 11, 14, 0]` | 替补双能卫，转换冲击与外线施压 |
| 9 | Drew Eubanks | C | 6.0 | 20 → **26** | 48 → **46** | 35 → **38** | 0 | `[7, 11, 0, 0]` | 第 11 人纯吃饼护筐内线（`Roll vs Pop = 20`） |

---

## 3. 攻防博弈体系（Doc 49 攻守并重）

### 3.1 进攻体系：`PACE_AND_SPACE` (2) + 高位挡拆引力闭环
- **双枪超远射程拉开**：Lillard 与 Simons 在三分线外 28 英尺即具备牵制力，配合 Nurkic 的重型掩护顺下（`Roll vs Pop = 25`）与 Grant 的弱侧单打/空切，形成“挡拆牵制—顺下吸引协防—弱侧 Grant/Thybulle 惩罚”的清晰闭环。
- **教练滑块**：`active_system` 由 `7` 调整为 **`2` (`PACE_AND_SPACE`)**，`run_play_tendency = 76`，`bench_depth = 10`，`bench_utilization = 62`。

### 3.2 防守博弈体系：Thybulle/Grant 领防屏蔽 Lillard + Nurkic/Bowie 沉退护筐
- **对位隐藏与外线锁防**：Thybulle（PDef 93, LQ 95, Stl 98）主防对手第一外线持球核心，Grant 与 Kersey 轮番消耗顶级锋线；Lillard 对位隐藏在对手弱侧定点投手身上以保存体能。
- **双塔沉退护筐与弱侧 Tag**：Nurkic 与 Bowie 均执行禁区沉退（`PROTECT_PAINT`），`help_defense` 由 `37` 提升至 **`68`**，强化 Grant、Thybulle 与 Kersey 的弱侧轮转夹击与顺下人顶防。

---

## 4. 模拟侧重（Scoring Options 1~3 & 6 大 POE）

- **Scoring Option 1**: `Damian Lillard` (`face_id = 2449`)
- **Scoring Option 2**: `Jerami Grant` (`face_id = 4105`)
- **Scoring Option 3**: `Anfernee Simons` (`face_id = 7723`)
- **6 大 POE**：
  - `poe_offense`: `4` (`PICK_AND_ROLL_OFFENSE`)
  - `poe_offense_tempo`: `8` (`NEUTRAL_OFFENSE_TEMPO`)
  - `poe_offense_rebound`: `12` (`LIMIT_TRANSITION`)
  - `poe_defense`: `13` (`PROTECT_PAINT`)
  - `poe_defense_physicality`: `18` (`PLAY_PHYSICAL`)
  - `poe_defense_rebound`: `19` (`CRASH_DEFENSIVE_BOARDS`)

---

## 5. 全维倾向安全线与训练负荷管理

- **犯规红线**：修正 Keon Johnson (`52 → 42`) 与 Drew Eubanks (`84 → 44`)，全队核心轮换 `foul` (`0x4B9`) 均 `<= 45`，`hard_foul` (`0x4BA`) `<= 25`。
- **蓝领运球与顺下修正**：Drew Eubanks 控球仅 36，将其 `crossover` 由 `100` 压至 `2`，`no_move_dribble` 设为 `94`，`roll_vs_pop` 由 `85` 修正为 `20`。
- **训练模板与防伤负荷（Doc 86）**：
  - **≤ 24 岁成长梯队（`intensity = 3` Medium）**：Anfernee Simons (23, SG, `OFFENSIVE=2`), Cameron Reddish (23, SF, `TWO_WAY=1`), Jerome Kersey (20, PF, `ATHLETIC=4`), Sam Bowie (23, C, `INSIDE=8`), Keon Johnson (20, SG, `TWO_WAY=1`)。
  - **≥ 25/26 岁巅峰/老将梯队（`intensity = 2` Low）**：Damian Lillard (32, PG, `PLAYMAKING=6`), Jerami Grant (28, PF, `TWO_WAY=1`), Jusuf Nurkic (28, C, `INSIDE=8`), Matisse Thybulle (25, SF, `TWO_WAY=1`), Justise Winslow (26, PF, `TWO_WAY=1`), Drew Eubanks (25, C, `REBOUNDING=5`)。
  - 所有球员 `is_intensity_overriden = 1`。
