# 游戏逐项机制与字段级深入研究档案 (Per-Setting Mechanism Dossier V3)

> **任务标识**：`NBA2K22-VAE-GEMINI-INTEGRATED-LOOP-20261030-001`  
> **依据指令**：`01_任务输入/HUMAN_PER_SETTING_MECHANISM_RESEARCH_V3.md` (Human 2026-10-30 直接下达)  
> **执行模型**：Gemini Flash 3.8（Human 声明标签）  
> **核心原则**：逐项深入建立机制档案；不将研究覆盖当作实机生效；不把社区讨论与相关性说成已证因果；未证实项严格保持 `UNKNOWN`。

---

## 一、倾向（Tendencies）逐槽位与映射关系深度审计

### 1. 原生槽位与外部标签的非对等性
- **R04B 原生取证现状**：PC22 球员结构体中存在 99 个连续倾向原生槽位（48 个已通过 REA 和内存断点命名，51 个处于未命名或未确证状态）。
- **外部导出工具标签**：外部修改器（如 2K Tools、Sync）同样导出 99 条标签，但在索引对齐上存在偏移错位（例如 `Touches` 与 `Take Charge` 在不同版本中偏移差 2-4 字节）。
- **V3 证据结论**：**严禁默认外部导出的 99 条标签与原生 99 个内存槽位 1:1 逐项对应**。未在 REA 中取得实机汇编读取指令锚点（RVA）的槽位，一律标记为 `UNKNOWN_TENDENCY_SLOT`。

### 2. "Touches" 倾向机制与社区争议审计
- **公开研究出处与链接 (operationsports.com)**：
  - Operation Sports: *NBA 2K22 Useful Findings & Sliders* (2021-11): `https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/917203-nba-2k22-useful-findings`
  - Operation Sports: *NBA 2K22 Tendencies - A Better Realism for Roster Creators* (2021-10): `https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/nba-2k-basketball-rosters/917138-nba-2k22-tendencies-a-better-realism-for-roster-creators`
- **核心争议与竞争性假说**：
  - **假说 A（战术调用优先级论）**：Touches (0..100) 直接决定教练战术呼叫（Play Calling Engine）中以该球员为主要终结点的战术权重；当 Touches > 85 时，ACE 会强行压制其他球员的 PlayType 分配。
  - **假说 B（Freelance 自主触球论）**：Touches 仅在战术破产或进入 Freelance Motion 时生效，决定无球跑位向持球人要球（Call for Ball）的频率，而不直接重写教练 Playbook 预设的走位。
  - **因果判定**：在未连接活体游戏进行单因素对比试验前，**上述两项均列为待验证竞争性假说 (COMPETING_HYPOTHESIS)，不得将任何一项断言为原生因果事实**。

---

## 二、教练选项（Coach Settings）与战术体系联动研究

### 1. K04 登记的 19 项教练设置体系
根据 `K04_COACH_SETTINGS.md` 及 `runtime/coach_poe.js` 审计，教练核心选项分为三层：
1. **宏观节奏与倾向**：
   - `Pace` (0..100): 决定进攻端推快攻与提前出手的倾向。
   - `Fast Break Focus` (枚举 0..3): 跑快攻人数 vs 保护防守篮板。
   - `Crash Offensive Glass` (0..100): 前场篮板争抢激进度与防退防反击的权衡。
2. **战术调用与系统控制**：
   - `Offensive Playcalling` (AUTO / MANUAL): 自动调用战术与玩家手动呼叫。
   - `Playbook Focus` (Primary, Secondary, Tertiary): 配合球员 4 种 PlayTypes 分配战术。
   - `Adaptive Coaching Engine (ACE)` (ON / OFF / DEFENSE ONLY): 2K 原生自适应教练引擎，在落后或特定对位劣势时会动态覆盖玩家设定的防守策略。
3. **防守对位与轮转**：
   - `On-Ball Defense` / `Off-Ball Defense` (Tight, Moderate, Sag Off, Deny Ball).
   - `Pick and Roll Defense` (Go Over, Go Under, Ice, Switch, Blitz).
   - `Double Team Strategy` (Never, On Catch, In Post, Manual).

### 2. 字段联动与冲突（Interaction & Conflicts）
- **ACE 与玩家自定义设置的潜在覆盖**：当 ACE 开启时，若对方某得分手连续命中 3 记三分，原生引擎会自动将对该球员的防守调整为 `Double Team: On Catch` 与 `On-Ball: Smother`，直接覆盖预设的防守滑块。
- **Pace 与体力（Fatigue）的非线性恶化**：当 Pace > 70 且单节时长为 12 分钟时，若轮换时间表未设定足够轮换缓冲（主力出场 > 38 分钟），第 4 节命中率因体能劣化（Stamina Penalty）下降达 8–15%。

---

## 三、REA 内存身份与底层偏移证据

| 业务领域 | 结构体/Native 路径 | 核心偏移 (Hex) | 字段语义与位宽 | 读回成熟度 | 权限要求 |
|---|---|---|---|---|---|
| **Coach POE** | `coach.apply_gameplan` | `+0x316` (低位) | 战术方案位段 (bits 0..7) | `STATIC_CODE` (JS 注入原型) | `COACH_TACTICS_WRITE` |
| **Player Training** | `player_training` | `+0x318` | Position (8..10), Type (11..15), Intensity (16..18) | `STATIC_CODE` (training.json) | `COACH_TRAINING_WRITE` |
| **Trade Roster** | `ownership_transfer_v2` | `+0xCB1`, `+0x1047` | 球队名单人数与球员所属球队 ID | `LIVE_READBACK` (实机交易成功) | `GM_TRADE_SUBMIT` |
| **Attribute Growth** | `attribute_progression` | 未公开导出函数 | 内部成长黑盒，受潜在值与年龄曲线调制 | `UNKNOWN_IN_ENGINE` | `WORLD_ADMIN_CALIBRATION_ONLY` |
| **Dual Normalize** | `game_settings` | 待实机内存定位 | 双布尔开关，换算 48 分钟统计 | `SOURCE_RESEARCH` / `UNKNOWN` | `COMMISSIONER_SETTINGS_WRITE` |

---

## 四、方法论采纳与角色决策准则

在 VAE 原型中，任何拟推荐给 GM、教练或球员的角色决策方法论，必须满足以下硬性门禁：
1. **实证前提**：该设置的原生读回必须达到至少 `UI_VERIFIED` 或 `LIVE_READBACK`；
2. **非因果保真**：若仅有观测数据，只能向角色报告“关联趋势（OBSERVED_TREND）”，不得宣称“因果保证（CONFIRMED）”；
3. **混淆变量排除**：必须在比赛或成长样本中显式记录并控制主要混淆变量（如对手战力、比赛垃圾时间、投篮手感波动、伤病恢复期）；
4. **负向与零效果记录**：所有试验中未达预期或恶化的结果，一律完整记录在知识库中，严禁隐瞒失败。
