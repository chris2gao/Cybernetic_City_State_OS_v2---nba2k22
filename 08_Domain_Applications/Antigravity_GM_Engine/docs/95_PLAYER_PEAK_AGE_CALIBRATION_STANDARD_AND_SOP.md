# 95_球员巅峰年龄（Peak Start / Peak End）真实化校准专项标准与可复用 SOP

> **文档标识**: `STANDARD-PLAYER-PEAK-AGE-CALIBRATION-V1`  
> **生效时间**: 2026-11-25  
> **关联协议**:
> - [43_FULL_DIMENSIONAL_NATIVE_MOD_PROTOCOL_V2.md](file:///e:/workspace/Cybernetic_City_State_OS_v2%20-%20nba2k22/08_Domain_Applications/Antigravity_GM_Engine/docs/43_FULL_DIMENSIONAL_NATIVE_MOD_PROTOCOL_V2.md)（第 5 节纯差分与自解释规格书规范）
> - [26_GAMEPLAY_ROLES_AND_WORLDLINE_RULES.md](file:///e:/workspace/Cybernetic_City_State_OS_v2%20-%20nba2k22/08_Domain_Applications/Antigravity_GM_Engine/docs/26_GAMEPLAY_ROLES_AND_WORLDLINE_RULES.md)（纪元历史线 / 现代历史线双轨规则）
> - [94_2026_EVOLVING_STARS_REALISM_AND_GROWTH_CALIBRATION.md](file:///e:/workspace/Cybernetic_City_State_OS_v2%20-%20nba2k22/08_Domain_Applications/Antigravity_GM_Engine/docs/94_2026_EVOLVING_STARS_REALISM_AND_GROWTH_CALIBRATION.md)（2026 成长型球星潜力与打法共识）
> **适用范围**: 可按 **全联盟现役 (`ACTIVE_LEAGUE`)**、**指定单队 (`SINGLE_TEAM`)** 或 **指定年份选秀名单 (`DRAFT_CLASS`)** 一键复用的专项标准作业程序。

---

## 一、 引擎底层机制与物理位域字典

### 1.1 NBA 2K22 能力成长三阶段曲线机制
在 NBA 2K22 终极联盟（MyLEAGUE）引擎中，每位球员的年度能力值与徽章（达到解锁条件时）演化受 **巅峰开始年龄 (`PEAKSTART`)** 与 **巅峰结束年龄 (`PEAKEND`)** 严格支配，并与全局滑块（`offseason_progression_rate`、`regression_rate`、`training_effects`）联动：
1. **成长期（`age < PEAKSTART`）**：能力值与符合条件的技能徽章每年快速增长（受 `potential` 天花板与 `offseason_progression_rate` 调节）；
2. **巅峰期（`PEAKSTART <= age <= PEAKEND`）**：能力值维持在当前平台期，停止大幅上涨（偶有小幅微调或缓慢回落）；
3. **衰退期（`age > PEAKEND`）**：身体素质（速度/弹跳/加速/耐力）与综合能力开始大幅下滑，衰老速度受 `regression_rate` 控制。

> **核心实机痛点**：
> - 原生名册中 **1984 届历史新秀**（如奥拉朱旺 `23..26`、巴克利 `24..27`、乔丹 `25..31`、斯托克顿 `25..31`）的 `PEAKEND` 被严重截断，导致 27~32 岁本该夺冠/MVP 的时期提前衰退；
> - 现代线 **大器晚成/2022~2026 蜕变超巨**（如布伦森 26 岁但 `PEAKSTART=25`、马克卡宁、怀特、亚历山大等）因 `age >= PEAKSTART` 而被提前锁死成长，无法兑现真实历史涨幅；
> - **常青树超巨**（詹姆斯、库里、杜兰特等）的 `PEAKEND` 需延长至其真实高水平巅峰末期。

### 1.2 `PLAYER_STRUCT` 底层物理偏移与安全写入掩码
在 1,264 字节 `PLAYER_STRUCT` 结构体中，`PEAKSTART` 与 `PEAKEND` 连续打包存储于偏移 **`114 (0x72)`** 的 `uint16`（2 字节小端序）位域中：

| 字段名称 | 字节偏移 (Dec / Hex) | `uint16 @ 0x72` 起始位 | 位宽 (`length`) | 物理值域 | 安全写入掩码规范 |
| :--- | :---: | :---: | :---: | :---: | :--- |
| **保留低位标志** | `114 (0x72)` | `0..3` | `4 bits` | 原值保留 | **必须通过 `old_word & 0x000F` 完整保留，严禁覆盖** |
| **PEAKSTART** (巅峰开始) | `114 (0x72)` | `4` (`bits 4..9`) | `6 bits` | `18..40` | `(peak_start & 0x3F) << 4` |
| **PEAKEND** (巅峰结束) | `115 (0x73)` / `114` bit 10 | `2` of `0x73` (`bits 10..15` of `0x72`) | `6 bits` | `25..45` | `(peak_end & 0x3F) << 10` |

**原子写入公式（Read-Modify-Write）**：
```python
new_u16 = (old_u16 & 0x000F) | ((peak_start & 0x3F) << 4) | ((peak_end & 0x3F) << 10)
```
执行模型使用 REA 原生位域写入接口或带掩码 CAS 写入 `PLAYER_STRUCT + 114` (`uint16`) 后，必须立即回读验证 `(read_u16 >> 4) & 0x3F == peak_start` 与 `(read_u16 >> 10) & 0x3F == peak_end`。

---

## 二、 可复用范围选择器 (Reusable Scope Selector)

本专项任务每次触发时，只需声明 `scope_mode` 与参数即可标准复用：

| `scope_mode` | 适用场景 | 目标输入源 | 输出目录规范 |
| :--- | :--- | :--- | :--- |
| **`ACTIVE_LEAGUE`** | 全联盟 30 支球队现役球员整体校准 | `league_state.sqlite` 最新快照全部 30 队 | `C:\nba2k22\exports\YYYYMMDD_active_league_peak_age_execution\`（按队 30 份单队 JSON） |
| **`SINGLE_TEAM`** | 单支球队新援或局部阵容矫正 | `league_state.sqlite` 指定 `team_id` | `C:\nba2k22\exports\YYYYMMDD_<abbr>_peak_age_execution\`（单队 JSON） |
| **`DRAFT_CLASS`** | 休赛期历史选秀名单（1985~2021 届）生成前/后标定 | `player_pool.sqlite` 或选秀名单 JSON | `C:\nba2k22\exports\YYYYMMDD_<year>_draft_peak_age_execution\`（或直接合入选秀真实化执行包） |

---

## 三、 双轨真实历史标定法则 (Dual-Timeline Calibration Rules)

所有球员必须严格依据其所属时间线，按以下五级历史标定法则设置 `(PEAKSTART, PEAKEND)`，且强制满足 **`21 <= PEAKSTART < PEAKEND <= 42`** 与 **`PEAKEND - PEAKSTART >= 4`**：

### 法则 1：纪元历史线（Era Historical Timeline — 1984 届及后续历史选秀球员）
严格对标该历史球员在现实 NBA 生涯的真实崛起年份与高水准巅峰末期：
- **历史级常青超巨**：
  - Michael Jordan (`24..36`)、Hakeem Olajuwon (`24..34`)、John Stockton (`25..36`)、Charles Barkley (`24..33`)；
- **长青核心首发 / 最佳阵容级球星**：
  - Kevin Willis (`26..35`)、Otis Thorpe (`25..33`)、Sam Perkins (`25..34`)、Jerome Kersey (`24..31`)；
- **早熟或受重伤影响的历史球星**：
  - Alvin Robertson (`23..30`)、Sam Bowie (`23..29`)、Jay Humphries (`24..30`)、Tony Campbell (`25..30`)；
- **普通历史角色 / AI 补全自由新秀**：
  - 彻底修复 `PEAKEND <= 27` 的畸形截断，统一提升至 `24..30`（普通轮换）或 `25..31`（蓝领内线/射手）。

### 法则 2：现代历史线 — 2022~2026 晚熟蜕变超巨与全明星（Late-Bloomer & Evolving Stars）
对于 2021-22 赛季尚未达巅峰、在 2022~2026 年爆发至全明星/一阵级别的球员，**必须将 `PEAKSTART` 推迟至其真实爆发成熟年份之后**，确保其在游戏模拟中不会因过早进入平台期而停止成长：
- **MVP / 一阵级后期爆发核**：
  - **Jalen Brunson**（26 岁起飞至 97 档）：`29..34`
  - **Shai Gilgeous-Alexander**（24~26 岁冲 MVP）：`27..34`
  - **Lauri Markkanen**（25~26 岁全明星进步最快）：`28..33`
  - **Derrick White**（28~30 岁大器晚成二防核心）：`29..34`
- **2022~2026 成长型全明星与核心基石（对齐 Doc 94）**：
  - **Tyrese Maxey** (`26..32`)、**Alperen Şengün** (`26..33`)、**Franz Wagner** (`26..33`)、**Desmond Bane** (`26..32`)、**Jalen Green** (`26..32`)、**Jalen Johnson** (`26..32`)、**Austin Reaves** (`27..32`)、**Coby White** (`26..32`)、**Deni Avdija** (`26..32`)、**Trey Murphy III** (`26..32`)、**Anfernee Simons** (`26..32`)、**Immanuel Quickley** (`26..32`)、**Cameron Thomas** (`26..31`)、**Nicolas Claxton** (`26..32`)、**Jonathan Kuminga** (`26..32`)、**Jaren Jackson Jr.** (`26..33`)、**Mikal Bridges** (`27..33`)、**De'Aaron Fox** (`26..33`)、**Domantas Sabonis** (`26..33`)、**Tyrese Haliburton** (`26..33`)、**Anthony Edwards** (`25..33`)、**Ja Morant** (`25..32`)、**LaMelo Ball** (`25..32`)、**Cade Cunningham** (`26..33`)、**Scottie Barnes** (`26..33`)、**Evan Mobley** (`26..33`)、**Darius Garland** (`26..32`)。

### 法则 3：现代历史线 — 常青传奇与超级巨星（Longevity Legends & MVPs）
依据真实生涯至 2026 年的高水平续航能力延长 `PEAKEND`：
- **历史级超长待机**：LeBron James (`24..39`)、Stephen Curry (`25..37`)、Kevin Durant (`24..37`)、Chris Paul (`23..36`)、Al Horford (`25..36`)；
- **顶级巨星常规长巅峰**：Nikola Jokic (`25..35`)、Giannis Antetokounmpo (`24..34`)、Luka Doncic (`24..34`)、Jayson Tatum (`25..34`)、Jaylen Brown (`25..33`)、Jimmy Butler (`26..35`)、James Harden (`24..34`)、Damian Lillard (`25..34`)、Devin Booker (`25..34`)、Donovan Mitchell (`25..33`)、Joel Embiid (`25..32`)、Anthony Davis (`24..33`)、Kawhi Leonard (`24..33`)、Paul George (`24..34`)、Kyrie Irving (`24..34`)、Bam Adebayo (`25..33`)、Pascal Siakam (`26..33`)、Karl-Anthony Towns (`25..33`)、Rudy Gobert (`26..33`)。

### 法则 4：早衰 / 伤病受限 / 爆发力依赖型球员（Early-Decline / Injury-Impacted）
符合现实中因伤病或运动能力依赖导致 29~31 岁明显下滑的球员，严格如实下调 `PEAKEND`（如 Blake Griffin `23..29`、Kemba Walker `25..30`、Isaiah Thomas `26..30`、John Wall `24..29`、Derrick Rose `22..28`、Gordon Hayward `25..30`、Victor Oladipo `24..28`、Russell Westbrook `24..32`、Ben Simmons `23..27`）。

### 法则 5：普通现役轮换与边缘球员默认基准（Generic Calibration Floor）
- **常规现役首发/重要轮换**：`25..31`（射手型或地板流内线可放宽至 `25..32`）；
- **纯运动天赋型角色球员/替补**：`24..30`；
- **未进核心轮换的年轻新秀/双向球员**：至少保障 `24..30`，消除 `PEAKEND <= 27` 的畸形早衰。

---

## 四、 REA Native 纯差分执行规格书格式与闭环审计

1. **纯差分铁律**：仅当球员当前游戏内 `(PEAKSTART, PEAKEND)` 与历史目标值存在任意一项差异时，才写入对应球队 JSON；完全一致的球员**绝不写入**。
2. **单队文件结构（Doc 43 V2 规则四兼容）**：
   - 顶层：`protocol_version: "v2.0_full_dimensional_native_mod"`、`task_package_id`、`scope_mode`、`team_id`、`team_abbr`、`player_writes`。
   - 每个 `player_writes` 条目含：`player_name`、`roster_index`、`cyberface_id`、`timeline` (`ERA_1984` | `MODERN_2022_2026` | `AI_GENERIC`)、`birth_date`、`age_in_season`、`peak_start_target`、`peak_end_target`、`modifications`（包含 `offset: 114`, `type: "uint16_bitfield"`, `mask_preserve: "0x000F"`, `peak_start` & `peak_end` 各自当前值、目标值与 `decision_rationale`）。
3. **全量自动化审计必过门禁**：
   - `21 <= peak_start < peak_end <= 42` 且 `peak_end - peak_start >= 4`；
   - 零 `65535`/`null` 占位、无无效平写（至少 `peak_start` 或 `peak_end` 有变化）；
   - 关键哨兵通过（如 Jordan `24..36`、Olajuwon `24..34`、Brunson `29..34`、LeBron `24..39`、SGA `27..34`）。
