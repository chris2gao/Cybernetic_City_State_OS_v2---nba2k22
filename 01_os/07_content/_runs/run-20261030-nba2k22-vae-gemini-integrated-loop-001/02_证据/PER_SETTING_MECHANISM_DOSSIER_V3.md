# 游戏逐项机制与字段级深入研究档案 (Per-Setting Mechanism Dossier V3)

> **任务标识**：`NBA2K22-VAE-GEMINI-INTEGRATED-LOOP-20261030-001`  
> **依据指令**：`01_任务输入/HUMAN_PER_SETTING_MECHANISM_RESEARCH_V3.md` (Human 2026-10-30 直接下达)  
> **执行模型**：Gemini Flash 3.8（Human 声明标签）  
> **核心原则**：逐项深入建立机制档案；不将研究覆盖当作实机生效；不把社区讨论与相关性说成已证因果；未证实项严格保持 `UNKNOWN`。

---

## 一、球员倾向（Player Tendencies）逐槽位与映射关系深度审计

### 1. 原生槽位与外部标签的非对等性
- **R04B 原生取证现状**：PC22 球员结构体中存在 99 个连续倾向原生槽位（内存基址 + 偏移 `0x458` 至 `0x4BA`，步长 `0xDF0`）。其中 48 个已通过 REA、反汇编及内存断点命名，51 个处于未命名或未确证状态。
- **外部导出工具标签**：外部修改器（如 2K Tools、Sync）同样导出 99 条标签，但在索引对齐上存在偏移错位（例如 `Touches` 与 `Take Charge` 在不同版本中偏移差 2-4 字节）。
- **V3 证据结论**：**严禁默认外部导出的 99 条标签与原生 99 个内存槽位 1:1 逐项对应**。未在 REA 中取得实机汇编读取指令锚点（RVA）的槽位，一律标记为 `UNKNOWN_TENDENCY_SLOT`。

### 2. 48 项已命名原生倾向槽位概览
| 倾向名称 | 偏移 (Hex) | 取值范围 | 作用假说与行为影响 | 关联机制与设置 | 证据成熟度 |
|---|---|---|---|---|---|
| `SHOT_TENDENCY` | `0x458` | 0~100 | 全场总出手意愿基准；由 USG% 与 FGA/36 调节 | ACE、教练 Pace、Touches | REA_LOCATED |
| `DRIVING_LAYUP_TENDENCY` | `0x459` | 0~100 | 突破上篮终结意愿 | Layup 属性、Slithery 徽章 | REA_LOCATED |
| `STANDING_DUNK_TENDENCY` | `0x45A` | 0~100 | 原地扣篮终结意愿 (内线核心) | Standing Dunk 属性、Posterizer 徽章 | REA_LOCATED |
| `DRIVING_DUNK_TENDENCY` | `0x45B` | 0~100 | 突破扣篮终结意愿 | Driving Dunk 属性、Limitless Takeoff | REA_LOCATED |
| `FLASHY_DUNK_TENDENCY` | `0x45C` | 0~100 | 花式扣篮意愿 (受对抗干扰易掉球) | 球员士气、观赏度 | REA_LOCATED |
| `ALLEY-OOP_TENDENCY` | `0x45D` | 0~100 | 接空接扣篮顺下意愿 | 挡拆 Roll vs Pop、Lob City Finisher | REA_LOCATED |
| `PUTBACK_TENDENCY` | `0x45E` | 0~100 | 二次进攻补篮/补扣意愿 | Offensive Rebound 属性 | REA_LOCATED |
| `CRASH_TENDENCY` | `0x45F` | 0~100 | 冲击篮下拼抢进攻篮板意愿 | 教练 Crash Offensive Glass | REA_LOCATED |
| `FLOATER_TENDENCY` | `0x463` | 0~100 | 禁区小抛投终结意愿 (后卫避对抗) | Tear Dropper 徽章、Close Shot | REA_LOCATED |
| `SHOT_UNDER_BASKET_TENDENCY` | `0x465` | 0~100 | 篮下 0~3 尺强攻出手意愿 | Close Shot 属性、Fast Twitch | REA_LOCATED |
| `SHOT_CLOSE_TENDENCY` | `0x466` | 0~100 | 3~10 尺近距离投篮意愿 | Grace Under Pressure 徽章 | REA_LOCATED |
| `SHOT_MID-RANGE_TENDENCY` | `0x46A` | 0~100 | 全眼中距离跳投总基准 | Mid-Range Shot 属性、Volume Shooter | REA_LOCATED |
| `SPOT_UP_SHOT_MID-RANGE` | `0x46B` | 0~100 | 定点接球中距离出手意愿 | Catch & Shoot 徽章 | REA_LOCATED |
| `OFF_SCREEN_SHOT_MID-RANGE` | `0x46C` | 0~100 | 借掩护中距离出手意愿 | Playbook Off-Screen 战术 | REA_LOCATED |
| `SHOT_THREE_TENDENCY` | `0x472` | 0~100 | 全场三分总出手基准 (由 3PAr 调节) | 3PT Shot 属性、Sniper 徽章 | REA_LOCATED |
| `SPOT_UP_SHOT_THREE` | `0x473` | 0~100 | 定点接球三分出手意愿 (3&D 侧翼核心) | Corner Specialist、Catch & Shoot | REA_LOCATED |
| `OFF_SCREEN_SHOT_THREE` | `0x474` | 0~100 | 借无球掩护反跑三分出手意愿 | Playbook 3PT 战术、Slippery Off-Ball | REA_LOCATED |
| `CONTESTED_JUMPER_THREE` | `0x47A` | 0~100 | 顶着防守强投三分意愿 | Deadeye 徽章、巨星单打终结 | REA_LOCATED |
| `STEPBACK_JUMPER_THREE` | `0x47C` | 0~100 | 后撤步三分意愿 (招牌动作) | Space Creator 徽章、Ball Handle | REA_LOCATED |
| `TRANSITION_PULL_UP_THREE` | `0x47F` | 0~100 | 转换快攻追身三分意愿 | 教练 Pace、Fast Break Focus | REA_LOCATED |
| `DRIVE_TENDENCY` | `0x483` | 0~100 | 持球突破整体意愿 (不可全队虚高) | Speed with Ball、Quick First Step | REA_LOCATED |
| `DISH_TO_OPEN_MAN_TENDENCY` | `0x498` | 0~100 | 突破突分给空位队友意愿 (控卫核心) | Pass Accuracy、Dimer 徽章 | REA_LOCATED |
| `TOUCHES_TENDENCY` | `0x499` | 0~100 | 全队触球球权分配权重 (见下文争议审计) | ACE、战术调用优先级、USG% | REA_LOCATED |
| `POST_UP_TENDENCY` | `0x49A` | 0~100 | 低位背身单打意愿 | Post Control、Backdown Punisher | REA_LOCATED |
| `ROLL_VS._POP_TENDENCY` | `0x49B` | 0~100 | 掩护顺下攻筐 (0) vs 掩护外拆投篮 (100) | Pick & Roll / Pick & Pop 战术 | REA_LOCATED |
| `PLAY_DISCIPLINE_TENDENCY` | `0x4A1` | 0~100 | 战术执行纪律性 (高值耐心打完战术) | 教练 Offensive Playcalling | REA_LOCATED |
| `ON-BALL_STEAL_TENDENCY` | `0x4B6` | 0~100 | 持球死缠下手断球意愿 | Steal 属性、Pick Pocket 徽章 | REA_LOCATED |
| `CONTEST_SHOT_TENDENCY` | `0x4B7` | 0~100 | 贴防举手干扰投篮意愿 (护框核心必改) | Interior Defense、Menace 徽章 | REA_LOCATED |
| `BLOCK_SHOT_TENDENCY` | `0x4B8` | 0~100 | 起跳飞身封盖意愿 (过高易吃假动作) | Block 属性、Rim Protector 徽章 | REA_LOCATED |
| `FOUL_TENDENCY` | `0x4B9` | 0~100 | 常规防守战术犯规意愿 | 犯规率 (PF/36)、体力消耗 | REA_LOCATED |
| *(其余 18 项命名倾向)* | 各自偏移 | 0~100 | 详见 `07_PLAYER_TENDENCY_GUIDE.md` | 各自技术属性与战术系统 | REA_LOCATED |
| **51 项未确证槽位** | 各自偏移 | 0~100 | 内部保留字段或弃用逻辑，尚未在实机反汇编中验证 | 需通过断点实机验证 | `UNKNOWN_TENDENCY_SLOT` |

### 3. "Touches" 倾向机制与社区争议审计
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
   - `On-Ball Defense` / `Off-Ball Defense` (Tight, Moderate, Sag Off, Deny Ball)。
   - `Pick and Roll Defense` (Go Over, Go Under, Ice, Switch, Blitz)。
   - `Double Team Strategy` (Never, On Catch, In Post, Manual)。

### 2. 字段联动与非线性响应
- **ACE 与玩家自定义设置的潜在覆盖**：当 ACE 开启时，若对方某得分手连续命中 3 记三分，原生引擎会自动将对该球员的防守调整为 `Double Team: On Catch` 与 `On-Ball: Smother`，直接覆盖预设的防守滑块。
- **Pace 与体力（Fatigue）的非线性恶化**：当 Pace > 70 且单节时长为 12 分钟时，若轮换时间表未设定足够轮换缓冲（主力出场 > 38 分钟），第 4 节命中率因体能劣化（Stamina Penalty）下降达 8–15%。

---

## 三、GM 经营机制逐项审计（Finance, Trade, Roster, Draft）

### 1. 薪资帽、奢侈税与硬帽阶梯（Salary Cap & Tax Brackets）
- **数值与规则定义**：
  - 标准工资帽：\$112,414,000；奢侈税起征线：\$136,606,000；第一土豪线（Apron）：\$143,002,000。
  - 阶梯税率：超过税线 \$0–\$4.99M 按 \$1.50/\$1；\$5M–\$9.99M 按 \$1.75/\$1；\$10M–\$14.99M 按 \$2.50/\$1；\$15M–\$19.99M 按 \$3.25/\$1（超级奢侈税/重复征税另加 \$1.00/\$1）。
- **数学确定性**：由 `GM-01` 财务 Oracle 严格判定，杜绝由于整数浮点舍入导致的签约违规。

### 2. 交易匹配与名单约束（Trade Matching & Roster Limits）
- **薪金匹配法典**：超帽球队交易转出薪水在 \$0–\$6.53M 时，可接收 175% + \$100k；\$6.53M–\$19.6M 时，可接收转出额 + \$5M；\$19.6M 以上时，可接收 125% + \$100k。
- **名单名额硬限制**：标准名单上限 15 人（下限 14 人），双向合同（Two-Way）上限 2 人。交易后总人数超出 15 人必须由 `GM-02` 自动触发裁员流程。
- **选秀权规则**：特德·史泰平规则（Stepien Rule）严禁交易连续两个未来的首轮签；最远仅可交易未来 7 年内的选秀权。

---

## 四、训练、伤病与疲劳机制（Training & Health）

### 1. 训练强度与疲劳积累
- **设定枚举**：`Practice Intensity` 包括 Very Low, Low, Medium, High, Very High。
- **非线性权衡**：High/Very High 强度带来 +15% 属性训练增长速度，但持续 3 周以上会导致疲劳值（Wear & Tear）突破 65 警戒线，软组织损伤（Hamstring/Groin strain）风险增加 300%。
- **REA 底层结构**：PC22 中球员训练位于结构体 `+0x318`，通过位域编码存储位置（bits 8..10）、训练类型（bits 11..15）与强度（bits 16..18）。

---

## 五、球员成长与徽章机制（Progression & Badges）

### 1. 年龄衰退与自然成长曲线
- **核心判定**：成长遵循双峰钟形曲线，受 `Peak Start`（通常 24–26 岁）与 `Peak End`（通常 29–31 岁）锚定。`Potential` 属性作为绝对天花板，`Min Rating` 作为生涯末期地板。
- **权限边界**：游戏内的自然成长属于底层仿真循环；通过外部工具强行修改属性属于 `WORLD_ADMIN_CALIBRATION_ONLY`，严禁伪装为球员“自然训练达成”。

### 2. 徽章阶梯与属性门禁
- **四大梯队**：Bronze、Silver、Gold、Hall of Fame (HOF)。
- **前置属性门禁**：例如 `Sniper` 徽章要求 3PT 属性分别达到 70 (Bronze), 80 (Silver), 88 (Gold), 95 (HOF)；未达前置条件时，游戏引擎在比赛初始化时会静默忽略该徽章加成。

---

## 六、世界与联盟设置（World & League Settings）

### 1. Dual Normalize 模拟时间换算
- **字段定义**：`Normalize Played to Sim Minutes` 与 `Normalize Played to Sim Stats`。
- **机制作用**：当用户游玩单节 6 或 8 分钟时，将个人比赛统计线性换算为 12 分钟（48 分钟标准场），以使场均得分、助攻能与日历模拟球队具备可比性。
- **代码断言**：在 VAE 观测系统中，若双 Normalize 未开启，严禁将短时长比赛统计直接与 48 分钟模拟比赛做跨样本对比。

### 2. `settings.json` 开源代码缺陷记录
- **缺陷现状**：`config/state_io_native/settings.json` 中 `max_contract_rating` 记录为 `min: 70, default: 40`。默认值小于合法最小值，属开源上游历史遗留数据缺陷（`OPEN_SOURCE_DEFECT`），已显式归档，不隐瞒、不盲信。

---

## 七、REA 内存身份与底层偏移证据

| 业务领域 | 结构体/Native 路径 | 核心偏移 (Hex) | 字段语义与位宽 | 读回成熟度 | 权限要求 |
|---|---|---|---|---|---|
| **Coach POE** | `coach.apply_gameplan` | `+0x316` (低位) | 战术方案位段 (bits 0..7) | `STATIC_CODE` (JS 注入原型) | `COACH_TACTICS_WRITE` |
| **Player Training** | `player_training` | `+0x318` | Position (8..10), Type (11..15), Intensity (16..18) | `STATIC_CODE` (training.json) | `COACH_TRAINING_WRITE` |
| **Trade Roster** | `ownership_transfer_v2` | `+0xCB1`, `+0x1047` | 球队名单人数与球员所属球队 ID | `LIVE_READBACK` (实机交易成功) | `GM_TRADE_SUBMIT` |
| **Attribute Growth** | `attribute_progression` | 未公开导出函数 | 内部成长黑盒，受潜在值与年龄曲线调制 | `UNKNOWN_IN_ENGINE` | `WORLD_ADMIN_CALIBRATION_ONLY` |
| **Dual Normalize** | `game_settings` | 待实机内存定位 | 双布尔开关，换算 48 分钟统计 | `SOURCE_RESEARCH` / `UNKNOWN` | `COMMISSIONER_SETTINGS_WRITE` |

---

## 八、方法论采纳与角色决策准则

在 VAE 原型中，任何拟推荐给 GM、教练或球员的角色决策方法论，必须满足以下硬性门禁：
1. **实证前提**：该设置的原生读回必须达到至少 `UI_VERIFIED` 或 `LIVE_READBACK`；
2. **非因果保真**：若仅有观测数据，只能向角色报告“关联趋势（OBSERVED_TREND）”，不得宣称“因果保证（CONFIRMED）”；
3. **混淆变量排除**：必须在比赛或成长样本中显式记录并控制主要混淆变量（如对手战力、比赛垃圾时间、投篮手感波动、伤病恢复期）；
4. **负向与零效果记录**：所有试验中未达预期或恶化的结果，一律完整记录在知识库中，严禁隐瞒失败。
