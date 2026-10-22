# DEV11 — NBA2K22 PC 实时赛场球员决策与 ACE 临场教练控制调研 V1

> **2026-10-19 用户最新裁定覆盖本任务范围**：不再查ACE运行时对象/动态修改控制接口，不做C2/C3外挂临场教练、不改ACE内部算法。ACE比赛期间始终ON，已观察到原版教练会正常叫暂停和调整。GM赛前教练策略与球员倾向由其他模块负责，Antigravity也不需要重复这些。剩余三方竞技调校仅限游戏Gameplay全局设置与用户真实打球反馈。**现行权威文档：[LIVE_COURT_GAMEPLAY_PARAMETERS_V3](../research/NBA2K22_LIVE_COURT_GAMEPLAY_PARAMETERS_V3.md)**。DEV11保留作为废止的研究提案，不再执行。

> 2026-10-19；Web Development；供 Antigravity 与开发规划后续配合。
> **仅实时3D比赛（USER vs CPU、CPU vs CPU）；不调日历快速模拟/Sim Engine。** 本轮为内存取证/少量玩家实战观察任务，不授权游戏写入，不增加M3 GM V4交付范围。
> 玩家已确认此前全部全局比赛设置均可修改；不要重做全局滑块内存扫描。
> 教练19项默认+18项指定对手整体防守已有生产读写。完整Playbook/阵容/角色由Codex另一机制负责；本项目研究**赛场中的实际执行和动态覆盖**而不是重复开发静态教练接口。

## 研究结论先行

**应该先检查AI的进攻选择（战术选择/出手结构/传球/无球动作）是否合理，再看防守临场反制/ACE，最后改物理、命中率和对抗参数。** 因为AI即使投篮成功率正常，也可能选了错误的出手。先确认“决策不对”还是“决策正确但动作或判定错误”，否则调整成功率会掩盖真正问题。

**ACE存在配置入口，但不等于存在可调的Coach IQ系数。** ACE的模式/权限、runtime适应对象、CPU球队是否消费相同值、与Gameplan字段覆盖关系，都未由本局定位报告确认。不能宣称改变模式=重写AI，也不能先假设所有球队都能独立修改ACE。

## 公开资料（证据等级）

1. [2K官方 NBA2K22 Gameplay报告（2021-09）](https://newsroom-anz.2k.com/news/nbar-2k22-unveils-new-gameplay-innovations)：宣布Shot IQ偏重好出手与投篮质量；详细说明新一代防守AI的Hedge、协防轮转、弱侧第二次轮转和掩护追逐，但文件中明确提及new-gen AI重点，**不能把PS5/XBS重写全部按PC本世代已实施处理**。本世代有共享的运动等升级；具体ACE须实机核对。
2. [Operation Sports 2K22 Current Gen（RES2，2022-05/06）](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/nba-2k-basketball-sliders/917713-res2-2k22-all-star-current-gen-sliders/page6)：作者为维持`Play Physical`，建议ACE Off，并认为ACE可能更改教练计划；**玩家经验，不是已证明覆盖地址**。
3. [Operation Sports ACE讨论（2022-03）](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/921133-adaptive-coaching-engine)：有玩家称“ACE only affects the user”，并强调ACE On+Auto playcalling可产生不透明变更；与CPU侧作用范围存在不确定性，必须真实检查。
4. [Operation Sports 2K22 挡拆防守深度评估](https://www.operationsports.com/nba-2k22-gameplay-pick-and-roll-defense-must-improve-this-year/)：提出ACE/CPU策略反制不足、包夹方案常不合理等行为问题；没有验证内存调节能解决。
5. [2K23中ACE模式解释](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/nba-2k-basketball-sliders/927085-schnaidt1-s-nba-2k23-sliders-and-settings/page5)：Off / Offense Only / Defense Only / Offense & Defense，**本局NBA2K22 PC原生枚举须核实，不要从2K23拷原始数值**。
6. [NBA2K22 MyLeague指定对手Gameplan影响旧阵容（玩家经验）](https://www.reddit.com/r/NBA2k/comments/vhpyvz)：用户遭遇轮换被针对对手的旧Gameplan覆盖；不同层级/持续性的确值得检查，但不是当前赛场覆盖字段的直接证据。

## 优先顺序

### P0A: AI进攻行为诊断（先观察、不改命中率）

观察4种典型球权：
- 外线优秀射手获得空位时，CPU选择三分，还是无理由运球/中投/把球传走？
- 切入/挡拆后，防守内缩而外线空位，CPU是否愿意完成合理inside-out传球？弱侧会不会主动创造接球点？
- 低位强点面对明显错位，球队会不会安排低位/高低位，或一直用无效的控球人单打？
- 战术是否真的由Playbook和`RunPlayTendency`调用；四套Freelance是否被切换；是否反复只用少数战术？

把可能根因分三类：`PLAY_SELECTION`（战术/角色调用）、`DECISION_TENDENCY`（全局/个体行为选择）、`EXECUTION_PHYSICS`（跑动、传球动画、干扰判定）。不从单次出手证明规律。已有的`RunPlayTendency`、`PlaybookID`、`FreelanceType*`和原生全局`Take Inside/Mid/3PT`等先用于判断，**不要因缺理想效果直接修改球员真实个人倾向**。

### P0B: ACE控制作用域与runtime覆盖实机取证（Antigravity最重要）

1. 查当前PC终极联盟`Adaptive Coaching Engine`所在菜单、所有合法中文/英文选项、原始enum，设置实际生效对象`USER_CONTROLLER/CPU_CONTROLLER/TEAM/COACH/RUNTIME`。请区分玩家侧的“自动进攻/防守战术调用”和CPU球队比赛AI天然自主决策；**不能直接把一个玩家设置开关认定CPU教练AI总开关**。
2. 静态原生教练默认`COACHDATA`、指定对手`GAMEPLAN`已有读取路径；新重点是比赛开始后的实际live coach/gameplan状态指针，最好定位何时由静态预设拷贝进入实况状态；每个状态须按球队ID/对手ID/当前执教方身份校验，不把TEAM数组槽和team_id混用。
3. 选定玩家控制队与AI控制队，分别记录比赛前、开场、第一节中、暂停后、节间、第三节及比赛后ACE状态、战术调用/防守指令变化。**只需典型时点抓取，非逐帧监控**，不能为了这个强制在正式存档推进日期。
4. 对比`ACE ON/OFF`在隔离测试场景下的行为变化，关注三种现象：① static CoachData未变，但临场覆盖了live字段；② gameplan默认或特定对手设置被覆盖；③页面变了但AI执行行为未变。对应分类`STATIC_OVERRIDE`、`LIVE_OVERRIDE`、`UI_ONLY`、`UNKNOWN`。
5. 允许查看当前有无“自动进攻叫战术/自动防守调整/ACE四模式”的独立开关。关键问题：**能否只关进攻、保留防守的自动反制**；是否只影响用户队、对手CPU、双方CPUvsCPU，以及是否需要每场重新设置。
6. 对同一支球队、同一场景保留可复验的原值快照；避免停留在Coach Gameplan编辑页面直接写入，因为该UI缓冲已证实可能覆盖外挂写入。不要假设旧`IsInUse=0`就是禁用。

### P1: 赛场攻防“可提高智商”的可操作层级

| 技术层级 | 定义 | 当前判断 |
|---|---|---|
| **C1现有控制** | 固定比赛Gameplay全局参数、19项教练默认、18项对手防守、Playbook/FreeLance/POE，ACE菜单模式 | 静态教练原生接口已开发；全局用户称可写，ACE模式存储尚未证明 |
| **C2运行时状态选择** | 比赛中动态切换某套已合法存在的攻防指令/覆盖当前战术计划；保持对手身份 | 可行性未知，需查live gameplan对象/哪些变更会被AI接受/多久覆盖一次 |
| **C3外部临场规则控制器** | 不调用GM网页模型每球决策；由GM赛前批准的条件规则，根据真实可读比赛状态在暂停/节间有条件应用已认证C2指令 | 仅当实时可读/可写、稳定更新且能撤回才有意义；**未来专项，不是当前已实现能力** |
| **C4真正ACE内部算法重编程** | 修改内置对策效用函数/模式识别/内部状态机、提升决策搜索质量 | **目前无验证证据，成本高且风险大，不能承诺可以仅靠原生滑块做到** |

理想长期方向是**保留合理的原生AI反制、修复不合适的策略选择**，而非粗暴全关ACE。若ACE导致错误自动覆盖，可先比较`DEFENSE_ONLY`/ACE OFF，只作为待验假设；CPU侧有效性无法证实时，不将其直接作为CPU智商改善措施。

### P2: 最后校准动作、成功判定与运动

待跑位、传球和对策基本合理后，再分模块调`Shot Coverage`/投篮成功、Body-Up、Help Defense、运动速度/持球最低值、犯规、体力等。否则不合理出手也能进球，会掩盖AI决策问题。不得用无依据的CPU超能力加成模拟高智商。

## 与M3/既有项目的关系

- Codex负责完整Playbook/球员角色/阵容及已有教练执行器扩展；Antigravity负责**ACE实时状态观察和内存定位**，不重复做第二套静态教练计划写入；两者要共享同一`COACHING_RUNTIME`对象身份。
- GM V4完成后，针对真实赛场一组用户观测现象→研究模型解释问题及候选参数→玩家批准→Codex受控执行→用户再玩后反馈。玩家暂未授权本轮改变现实赛场参数。
- 个人球员`Tendency`属于原始球员数据修改，与既定普通经营禁止改倾向冲突；如果未来只为世界级竞技基线校准个体AI行为，先由玩家独立批准范围，保留原值与版本，仍禁止任意提高球员能力、潜力和徽章。
- CPU vs CPU现场比赛和USER vs CPU是本项目场景；日历sim、虚拟季末结果不是调校对象。
- 有关比赛片段可由玩家口述、截图或少量录屏反馈；未知事件数据不使用虚构的逐回合日志。

## 建议Antigravity交付最小文档

```yaml
game: NBA2K22_PC_CURRENT_GEN
save_id: ACTUAL_TEST_SAVE
test_case: ACE_SCOPE_001
ui_path: OBSERVED
ace_enum: OBSERVED_OR_UNKNOWN
owner_control_mode: USER_OR_CPU
opponent_control_mode: USER_OR_CPU
static_coach_pointer: VERIFIED_DYNAMIC_LOCATOR
matchup_plan_pointer: VERIFIED_DYNAMIC_LOCATOR
live_plan_pointer: UNKNOWN_UNTIL_FOUND
ace_runtime_pointer: UNKNOWN_UNTIL_FOUND
timeline:
  pregame: STATIC_STATE_SNAPSHOT
  Q1_start: RUNTIME_STATE_SNAPSHOT_OR_MISSING
  timeout: RUNTIME_STATE_SNAPSHOT_OR_MISSING
  Q3_start: RUNTIME_STATE_SNAPSHOT_OR_MISSING
differential_observation: ON_OFF_COMPARISON_IF_PERMITTED
writes: READ_ONLY_RESEARCH
effective_on_cpu: UNKNOWN
effective_on_user: UNKNOWN
coach_setting_override: OBSERVED_OR_UNKNOWN
battle_effect: USER_OBSERVED_OR_UNKNOWN
recovery: NOT_APPLICABLE_READ_ONLY
```

核心交付问题：**ACE控制了哪个对象、谁在比赛中修改战术、改完能否保持、CPU是否真的受它影响；若不能确认，给出未知而不是臆造AI智商旋钮**。不必为了完成报告反编译整个AI、也不必进行大样本比赛。
