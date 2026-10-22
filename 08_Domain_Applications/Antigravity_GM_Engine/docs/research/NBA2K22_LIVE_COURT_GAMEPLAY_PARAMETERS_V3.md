# NBA2K22 PC 本世代 — 实时赛场 Gameplay 调校范围 V3（ACE原版全程开启）

> **2026-10-19 最新用户研究方法修正**：以名人堂原版设定为唯一基线（用户所有实战均是HoF），**不要求用户替模型试错数值、不让模型凭经验随口猜改动幅度**。前文“你打几个回合+模型再给小数值反复A/B”的通用方案不再执行；以有版本/平台/难度/完整参数/实际反馈的已发表成功经验为证据，优先综合查找HoF本世代。**现行权威研究：[NBA2K22_HOF_CURRENT_GEN_PROVEN_SLIDER_RESEARCH_20261019_V1](NBA2K22_HOF_CURRENT_GEN_PROVEN_SLIDER_RESEARCH_20261019_V1.md)**。防守PnR第三人不tag与篮下打铁的现有来源证据分级已整理，P&R原生算法缺陷目前没有可信的“Help Defense=100必修复”结论。

> **2026-10-19 玩家真实名人堂比赛观察，优先级更新**：[场上实战诊断/首轮A-B方案](NBA2K22_LIVE_COURT_USER_EYE_TEST_20261019_V1.md)。玩家已打几十场，实测普遍犯规、疲劳、篮板、CPU抢断/反应、3D速度基本合理；未发现名人堂CPU普遍作弊。**第一问题是挡拆时双人围持球者、顺下者无人防守；第二是普通球员在篮下有接触时几乎无法完成终结；第三是小后卫面对大中锋仍强攻与球队战术调用分化**（勇士传切很出彩）。因此本文件原“第一轮先调Movement8项”仅为无实战症状时的候选，**实际首轮改为挡拆防守Gameplan核查→篮下终结/接触滑块核查→球员投篮选择和Playbook**。中锋持球慢动作保留单独问题，不因范围广而排队抢先。ACE持续ON，正常的防守/体能/篮板/犯规HOLD。注意区分玩家真实观察与模型因果假设。

> 日期：2026-10-19；Web Development研究定稿。本文件**覆盖**[Live Court V2](NBA2K22_LIVE_COURT_ENGINE_CALIBRATION_V2.md)中探索ACE动态覆盖/外挂临场控制的实施方向，以及[DEV11 ACE探索V1](../development_tasks/DEV_20261019_11_LIVE_COURT_AI_AND_ACE_DISCOVERY_V1.md)中的C2/C3运行时控制计划。**不再开展C2比赛时内存改战术、C3外挂实时教练、不查ACE引擎内部算法**。用户已在实机确认原版ACE有暂停、教练防守调整等基本应变；以后比赛期间完全交给原生AI、ACE必须开。
>
> 唯一调校对象：**已进入NBA2K22真实3D比赛后持续生效的Gameplay参数/控制设置**。USER vs CPU与CPU vs CPU实场均在范围；日历快速模拟/Simulation Engine、赛季统计引擎不属于本项目。**GM V4、球员战术体系和赛前倾向设定是已有/另由Codex负责的经营层，不重复开发。**
>
> 玩家报告Antigravity已经找到此前全部全局设置的内存修改方法，研究下一步是**把这些实际可控的设定变成可验证、有问题导向的比赛环境Profile**，不重新搜索旧全局偏移。Game build、USER/CPU槽作用、设置真正进3D引擎消费的效果仍可按需实机确认。

## 1. 固定技术边界

```text
GM V4 赛前：球队人员、真实战术手册、教练体系、整体防守、球员进攻行为/倾向
      ↓ （受用户审批，由Codex受控落地）
游戏3D比赛：原版 ACE = ON；原版CPU与玩家正常进行临场攻防调整
      ↓
Gameplay全局环境：速度/对抗/传控/出手/犯规/体力/防守反应
      ↓
玩家或CPU真实场上竞争；事后用户反馈 + 本局已获得的统计 / 录像
      ↓
模型提出有证据的少量Gameplay差分，用户批准再应用新世界Profile
```

**GM赛前个体Tendency**与**Gameplay全球Tendencies**两者不同。用户已提出将球员行为倾向与球队战术匹配为赛前经营控制项；具体是否修改原始持久球员Tendency须受控定义为玩家明确批准的专题范围，不允许顺便直接修改球员能力/潜力/徽章。赛场专项仅研究**全局**Tendencies何时需要校正整体CPU行为；默认先HOLD并优先让GM战术与原生ACE决定选择。

## 2. 赛场剩余可调参数全集：以NBA2K22本世代玩家菜单与社区方案为依据

用户之前整理的六大类Gameplay：Offense、Defense、Attributes、Tendencies、Fouls、Movement，实际上再加Game General及Controller控制模式，共**八个参数域**。均是**本世代候选UI标签**；由于不同Menu/存档场景呈现可能不同，最终以Antigravity已实机确认的字段字典及USER/CPU通道为准，切勿从社区文稿反推绝对内存地址。

### A Movement：运动、空间与速度差异 — 第一优先级

1. `Speed with Ball (Max rating)` / `Speed with Ball (Min rating)`；
2. `Acceleration with Ball (Max/Min rating)`；
3. `Speed without Ball (Max/Min rating)`；
4. `Acceleration without Ball (Max/Min rating)`。

**这是8个独立滑块，不是两个速度总开关。** 用来研究带球启动、空切、回防、补位、追掩护、快攻和速度等级差。特别针对用户长期观察“中锋持球月球漫步，帧率正常”的现象，优先看with-ball的`Min/Max`与控球动画，而不是给单个中锋强行加能力。改变最高最低值可能会压缩或扩大球星/中锋差距，需要同时观察球员差异与后卫突破/篮下护框副作用。社区RES2与DiamondLobby的方案值有明显差异，**不能选择看起来最真实的某个数字当固定权威**。

### B Defense：防守干扰与接触 — 第一优先级

- `Driving Contact Shot Frequency`、`Inside Contact Shot Frequency`：接触发生环境；与实际犯规有区别。
- `Layup Defense Strength (Takeoff/Release)`：上篮起跳与出手两个阶段的干扰判定。
- `Jump Shot Defense Strength (Gather/Release)`：跳投准备与出手两个阶段的干扰判定。
- `Help Defense Strength`：原生协防力度/效果滑块；**不是新增更聪明的临场包夹算法**。
- `Steal Success`：已产生合理抢断机会时能否成功，不等同于球员做出抢断决策的概率。
- 跨组关键耦合：`Body-Up Sensitivity`（Offense组）、`On-Ball Defense`、`Lateral Quickness`、`Defensive Awareness`、`Defensive Consistency`（Attributes组）。

**观察目标**：后卫挡拆后的回追、合理距离下贴防是否瞬移、协防是否过快/过慢、合理防守是否被判成无效。若原版AI策略选择错误，不能假装滑块能提升其智慧；但滑块可以改善执行动作的真实对抗强度。

### C Offense：投篮终结与判定 — 第二优先级

- `Inside Shot Success`, `Close Shot Success`, `Mid-Range Success`, `3PT Success`, `Layup Success`
- `Shot Coverage Impact`：防守覆盖对结果的影响；社区对高低方向和CPU作用有争论，**需本局少量A/B验证**。
- `Shot Timing Impact`：投篮时机对命中影响；与用户使用`Real Player %`或`Shot Timing`方式有关。社区有人称CPU也受到该值影响，但属于玩家实验，不等于官方公式。
- `Dunk in Traffic Frequency`、`Dunk in Traffic Success`、`Contact Shot Success`、`Alley-Oop Success`。
- `Free Throw Difficulty`可在比赛/控制区显示，是否USER/CPU分别可设按实际当前页面。

**重点**：先确认有高质量出手机会、协防与干扰过程，再调整命中。不能为了得到“标准45% FG”让无解的强投也频频命中。

### D Offense：传球、运球与身体控制 — 第二优先级

- `Pass Accuracy`, `Pass Speed`；
- `Ball Security`, `Body-Up Sensitivity`；
- `Alley-Oop Success`、`Hands`、`Ball Handling`（Attributes）；
- `Hustle`、`Strength`与`Offensive Awareness`等仅在赛场行动表现存在问题时检查。

观察慢传球被断、传球穿模、后卫对抗大个子是否合理、突破中过度弹回/身体吸附、接球/抢球动作。注意**传球速度不足有时会被误判为球员“没意识”**，属于动作执行问题。

### E Attributes：全局能力作用倍率 — 第三优先级（谨慎）

社区2K22对应参数：
`Acceleration, Vertical, Strength, Stamina, Speed, Durability, Hustle, Ball Handling, Hands, Dunking Ability, On-Ball Defense, Stealing, Blocking, Offensive Awareness, Defensive Awareness, Offensive Rebounding, Defensive Rebounding, Offensive Consistency, Defensive Consistency, Fatigue Rate, Lateral Quickness`。

这类**全局属性滑块是赛场能力作用环境**，不等于改游戏存档中的个人原始属性值；但因为牵涉全员实际强弱差，它比命中/运动调节更敏感。尤其`Offensive Awareness`、`Defensive Awareness`可能影响已有原生决策/站位的表现，**但不能据此说原版AI智商已经变高**；具体机制仍需赛场行为证据。

`Stamina`、`Fatigue Rate`、`Durability`应与球员体力/训练/伤病状态统筹，避免为了某一场打得刺激无意破坏一个赛季的伤病生态。强烈建议默认先不动全局属性倍数，等可复现明确缺陷再分模块处理。

### F Fouls：对抗成本与比赛规则实际执行 — 第三优先级

`Over the Back Foul Frequency`、`Charging Foul Frequency`、`Blocking Foul Frequency`、`Reaching Foul Frequency`、`Shooting Foul Frequency`、`Loose Ball Foul Frequency`、`Illegal Screen Frequency`。

另有`Driving/Inside Contact Shot Frequency`属于Defense接触滑块，不能将“高接触频率”和“高哨子频率”混为一谈。保证合理对抗、抢断与掩护违规代价，改善双方战术选择的后果；太高会造成罚球大战、主力早早犯满，太低则导致无成本的非法身体接触。

### G 全局Gameplay Tendencies：全联盟通用选择偏置 — 研究层，通常HOLD

候选：`Take Inside/Close/Mid-Range/3PT Shots, Post Shots, Attack the Basket, Look for Post Players, Throw Alley-Oops, Attempt Dunks/Putbacks, Play Passing Lanes, Go for On-Ball Steals, Contest Shots, Backdoor Cuts`。

与GM赛前为球队个别球员匹配战术的个人Tendency不同，**这个滑块改变两侧（或USER/CPU所属）的整体概率环境**。若所有球队都不投中距离/不传低位，应先查此组，但若只是一个阵容战术调用错误，优先交GM的Playbook/球员角色，不得全联盟修改。

### H General + Controller：玩家体验/判定模式 — 单独配置，不等于AI提升

`Game Difficulty`、`Game Speed`、`Quarter Length`、`Fatigue/Injuries On/Off`、`Shot Timing/Real Player %`、`Free Throw Timing/Real Player %`、`Defensive Assist with Intense-D`、`Box Assist Strength`、`Shot Meter/Feedback`、Camera（对操作难度有影响，但本身不是篮球引擎规则），可能属于General、Controller、显示配置不同页面。

**别把给USER降低投篮操作门槛当成CPU篮球AI更智能**。尤其`Shot Timing Impact`与`Real Player %`的耦合要标注，社区描述CPU路径不完全一致。

### 参数清单支撑来源

1. [Operation Sports RES2 2K22 All Star Current Gen（2021–2022长期多版）](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/nba-2k-basketball-sliders/917713-res2-2k22-all-star-current-gen-sliders)：包含Offense/Defense/Attributes/Tendencies/Fouls/Movement完整公开示例；其部分方案依赖**全员修改球员徽章和属性**，违反我们的项目限制，**只提炼Gameplay滑块和A/B方法**。大量极端参数是作者的体验结果，不代表普遍正确。
2. [DiamondLobby NBA2K22完整Gameplay Sliders（2022-04-30）](https://diamondlobby.com/nba-2k22/realistic-game-sliders-nba-2k22/)：六类滑块和8项Movement表。
3. [Operation Sports gu8lal8 2K22 Competitive Sliders](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/nba-2k-basketball-sliders/920479-gu8lal8-s-competitive-sliders)：各难度之间的USER/CPU参数对比；方案包含额外人物属性/徽章编辑，不纳入我们的合法操作。
4. [Operation Sports 关于Shot Coverage Impact方向争议（2021）](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/nba-2k-basketball-sliders/917076-real-player-vs-shot-timing-can-guys-go-off)。
5. [Operation Sports Shot Timing Impact + CPU/Real Player%研究（2022）](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/nba-2k-basketball-sliders/919716-shot-timing-impact-sliders)。

## 3. 我们三方需要解决的顺序

**不再将ACE/场上战术实时控制纳入待查**；只做已经可访问的Gameplay环境调校。推荐第一轮：
1. **Movement 8项 + Game Speed：运动真实与速度差**（尤其用户中锋持球“月球漫步”）；单组小改，看后卫+内线+护框的副作用。
2. **Defense接触/防守干扰 + Lateral Quickness/Body-Up**：解决“切入无解”“一碰就被锁”“协防瞬移”等正常回合问题。
3. **Pass Accuracy/Speed/Ball Security/Hands**：球运行和持球接球是否自然。
4. **Shot Coverage/Timing Impact + 距离命中/终结**：当接球与防守动作正确后，再调成功率。
5. **Fouls + Fatigue**：规则成本与完整比赛的强度/消耗是否合理。
6. **全局Tendencies、Attributes**：默认保留，只有全联盟共同存在特定问题且非GM战略缺陷时才启用相关设置。

注意先后可随用户实战观察调整，没有明显症状的分类不用强迫去改。

## 4. A/B 调校契约：一次只问场上发生什么

每项`COURT_CANDIDATE`记录：
`game_build`, `save_id`, `match_mode(USER_CPU|CPU_CPU_LIVE)`, `court_profile_before`, `specific_problem`, `human_observation`, `candidate_parameters`, `USER_CPU_channels`, `old_values`, `new_values`, `approval`, `after_replay_observation`, `unintended_side_effects`, `KEEP/REVERT`。

- 玩家先正常打比赛，讲清当下问题。模型结合已证机制和社区实验选择最少相关的设置；Antigravity/已有接口提供真实当前字段，Codex按具体批准差分落地，玩家继续实际比赛反馈。
- **ACE始终ON**，没有“关ACE以保留静态设置”的研究路线；GM教练配置受原生AI动态调整是项目接受的基本事实。
- 玩家说“改善球场运动/身体对抗/选投处理”，不要转移成日历Sim统计拟合、教练外挂实时控制器或非授权人物能力编辑。
- USER和CPU侧是否作用于CPUvsCPU两支球队应通过实际行为/当前场景辨认，而不是预先假设固定。一种模式调好了不能自动宣称另一模式也调好。
- 优先尊重个体差异，慎调Attributes倍数。不给原版AI凭空加“智商”，只能改善已存在机制被调用时的环境效果。
- 允许一个问题用少量反复体验逐步解决，不要求做一百场比赛或全参数网格搜索。当前没有经玩家确认的最终官方`LIVE_COURT_PROFILE`数值。

## 5. 工作职责

- **GM V4 / Codex**：赛前阵容、球员战术角色和个人Tendency（须遵守具体审批范围）、19默认+18对手的教练战略及Playbook完整执行。
- **原版NBA2K22**：比赛中ACE永远启用，比赛决策与即时调整，以及实际3D动画、判定、胜负。
- **用户**：决定真实3D比赛的主要玩法与发现的问题，批准竞技环境的参数差分，打球反馈。
- **Web Development**：据玩家反馈选出对应Gameplay参数组、研读本世代滑块案例、排查改动对其它位置的副作用，形成最少必要候选。
- **Antigravity**：提供已经找到的全局设置字段当前值、两个通道/值域、是否持续有效及读回；不再研究ACE运行时AI实时控制接口。
- **Codex**：在玩家批准之后接现有全局设置执行机制，记录before/after与回滚；不要求新一轮全局地址扫描。
- **M3仍为开发首要任务**。本文件只是后续竞技打磨的最新研究边界与参数分类，不授予立即游戏写入权。
