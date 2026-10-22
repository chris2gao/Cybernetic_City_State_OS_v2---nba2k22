# K06 — NBA2K22终极联盟训练、疲劳、伤病与自然成长：面向GM/教练/球员/媒体的机制与选择手册

> **DEV29 V3 / R03-A（2026-10-21）**。目标版本：NBA2K22 **PC本世代原版、离线MyLEAGUE**。2K22 PS4/Xbox One、2K22 PS5/Xbox Series MyNBA、2K20–21/23旧新系列单独标平台，不偷换为PC22菜单。玩家能够设置训练，不意味着本项目已采到疲劳、不意味着比赛引擎会按预期加能力；读到内存布局也不等于当前存档已发布可信值。
>
> 研究任务是**提供自由行动原料**，不制定训练处方、不开发Agent、不改球员属性、不运行游戏。事实与能力核查以[DEV14交接](../../development_reviews/DEV14_TO_M3_HANDOFF.md)、[原生训练目录](../../../config/state_io_native/training.json)、[Registry](../../../src/gm_state_io/registry.py)、[GM训练能力审计](../../research/NBA2K22_MYLEAGUE_GM_CAPABILITY_GAP_AND_MONTHLY_TRAINING_V1.md)和[DEV16](../../development_tasks/DEV_20261019_16_M3_NATIVE_COVERAGE_AND_GM_TRAINING_PLAYBOOK_INTEGRATION_V1.md)为准。外部来源SRC-0049..0059见[证据库](../SOURCES.md)。

## 0. 本领域最容易犯的五个混淆

1. **训练模板（player_type）不是球员比赛PlayTypes**。前者是培养方向的9类通用原生编码，后者是K04的4个有序比赛战术角色槽（0..15）；同叫“类型”，不同原生对象。
2. **训练强度≠总身体负荷**。比赛分钟、背靠背、休息日、训练安排可能共同影响负担。2K14/15开发人员曾给出计算解释[ SRC-0052 ]，不能无认证地说PC22仍用完全相同“两周公式”。
3. **记录了progressive_fatigue_history布局≠已经知道实时疲劳百分比**。当前注册/通用采集主要覆盖11个训练设置，历史区的编码、单位、窗口和游戏UI映射仍未验证。
4. **训练方向≠直接提升球员某个能力数值**。成长由2K引擎自然发生，且发展/衰退、潜力和模拟设置会影响观测；普通经营禁止直接改Ability/Potential/Badge。
5. **2K22次世代Prep Hub与PS5 MySTAFF不属于本项目PC MyLEAGUE已认证功能**。即便同属“2K22”，训练页的内容、教练自动规划和球员“自己决定降强度”等不能直接搬来作为PC22原生控制。

## 1. 本项目真正拥有什么：11个训练设置字段及其等级

**项目工程事实**：⟦src/gm_state_io/registry.py⟧已登记6个TEAM_TRAINING和5个PLAYER_TRAINING，⟦config/state_io_native/training.json⟧含原生位域布局和值域。DEV14已建立通用捕获/稀疏变更/回读机制，状态以具体执行版本和当前真实发布批次为准。**未在本轮执行采集/写入/实机持久性测试**；不能把Registry的⟦writable=true⟧说成所有球队本档当前已读到并获批准。

| 真实原生字段 | 已登记值域/表示 | 可供角色考虑的行为及边界 |
|---|---|---|
| ⟦training.team.home_intensity⟧ | ⟦0..5⟧原生强度：Rest/Very Low/Low/Medium/High/Very High | 主场训练力度候选；比赛主场前后如何应用未量化 |
| ⟦training.team.away_intensity⟧ | ⟦0..5⟧同上 | 客场训练力度；为何区分home/away尚未证明的引擎效果保持UNKNOWN |
| ⟦training.team.automate_intensity⟧ | 布尔0/1 | 是否让引擎自动管理强度；不能证明它会理解角色私人目标或总能防伤 |
| ⟦training.team.rest_before_b2b⟧ | 布尔0/1 | 背靠背之前休息候选；触发时点/例外待PC22 UI |
| ⟦training.team.rest_after_b2b⟧ | 布尔0/1 | 背靠背之后休息候选；不等同每天休息 |
| ⟦training.team.injury_recovery⟧ | 布尔0/1 | 球队恢复相关原生设置；不能用字段名推算加速康复天数 |
| ⟦training.player.position⟧ | 0 PG /1 SG/2 SF/3 PF/4 C/5 None | 属于训练位置模板身份，不是本球员实际上场位，也不是可任意更换位置的证明 |
| ⟦training.player.player_type⟧ | 0..8，9项训练原型，见§2 | 训练方向，不是比赛中的P&R/3PT PlayTypes |
| ⟦training.player.intensity⟧ | 0..5 | 个人力度；可与团队自动/override产生关系，覆盖优先级未知 |
| ⟦training.player.injury_recovery⟧ | 布尔0/1 | 个人康复侧设置，原生实际效果/伤员资格待证 |
| ⟦training.player.is_intensity_overriden⟧ | 布尔0/1 | 个人强度覆盖标记；不能直接从1推出所有比赛会按指定强度训练 |

⟦team_training.percentage_per_focus/profile_per_focus/points_per_subfocus/intensity_history⟧及球员⟦points/overall_history/attribute_value_history/progressive_fatigue_history/intensity_history⟧在原生目录中**有布局候选**；但这批字节的⟦source_status/current_value/单位/自然时间窗口⟧没有被本次认证为角色可读数据。导师⟦mentorship_manager⟧布局含导师/被指导者ID、持续时间、兼容性、徽章槽与进度；Registry仅登记⟦mentor.relationship⟧为⟦DISCOVERED⟧不可常规执行，不能借目录里出现⟦badges_array⟧就说我们已获得“导师自然传徽章”的当前进度。

**本项目过去的历史报告曾称训练尚未有执行接口**，那是旧时点；现行DEV14交接/Registry已经含11字段。反过来，**真实当前月/当前人物的实时疲劳/伤病并未因有11字段而自动被采集**。数据消费者要以实际⟦source_coverage⟧和batch确认。

## 2. 九个原生通用培养原型（TRAINING player_type）

| Raw | 英文原文 / 中文 | “期望方向”的篮球语言（目录说明，非具体属性增益证明） |
|---:|---|---|
| 0 | All-Around / 全能 | 不刻意只追一个得分技能，寻整体成长 |
| 1 | Two-Way / 攻防兼备 | 攻防两端的均衡职能 |
| 2 | Offensive / 进攻 | 得分、终结与进攻工具 |
| 3 | Defensive / 防守 | 单防、防守阅读、护筐等方向 |
| 4 | Athletic / 运动 | 速度、弹跳、力量等身体工具方向 |
| 5 | Rebounding / 篮板 | 篮板争抢与相关定位 |
| 6 | Playmaking / 组织 | 运控、传球、组织选择 |
| 7 | Outside / 外线 | 外线出手、中投等投射方向 |
| 8 | Inside / 内线 | 低位、近框终结、篮下对抗 |

**最重要的未证缺口**：玩家实际PC训练UI据此前项目记录存在“分位置的多套模板”，而目前Registry仅有**9种通用原型**和独立⟦position⟧。无法断定⟦PG/SG/SF/PF/C⟧每个UI模板如何与⟦(position,player_type)⟧配对，也不能声称所有位置都显示9项或10项。以后只读菜单/原生列表证实前，应将⟦EXACT_POSITION_TEMPLATE_MAPPING=UNKNOWN⟧标给角色。

一个希望改打射手的年轻中锋可能**请求**Outside训练，教练可能认为他优先发展护筐，GM可能希望培养有交易价值的投射能力。三种偏好允许冲突；**选Outside不保证一年后增加固定三分数值，更不代表可直接写三分Ability**。训练计划所代表的是拟投入方向，而不是兑现成功的承诺。

## 3. 团队训练、个人训练、比赛负荷：如何理解相互作用

### 3.1 机制关系与不确定性

从玩家选择自由看，至少有如下潜在相互作用：

- **球队训练强度/主客场与背靠背休息**：团队级负荷基线；为何home/away分别存两段是当前原生布局事实，具体每周时序并无PC22逐日UI已证。
- **个人训练原型/强度/覆盖标记**：个体培养方向与负担的候选；受比赛出场、年龄、训练后恢复以及伤病可用性影响。影响比例未认证。
- **自然比赛投入**：比赛由2K运行并产生真实赛程、分钟及健康事件；不是模型事先“选择训练会赢球”就保证出现。
- **训练和体能的关系**：身体疲劳可能影响之后比赛可用性与受伤风险；精确⟦dose→fatigue→injury⟧函数、随机参数、跨快速模拟与观战的差别均UNKNOWN。
- **教练和训练师**：PC本世代玩家已确认球队有训练师等可聘员工，员工能力对伤病预防/恢复/发展作用须独立认证；不把PS5新增“Sport Science/Medical MySTAFF”职位搬到PC22。

NBA2K14/15时期Visual Concepts AI工程师Leftos公开解释[ SRC-0052 ]：旧版训练⟦Overall Workload⟧不仅由Intensity确定，还考虑比赛日、练习日、休息日、上场分钟与Work Ethic；该帖描述投诉/承诺的滚动2周窗口，以及比赛日按“High”计负担。这是**开发人员的历史原始解释**，具有机制研究价值，但**并未证明同样窗口/换算在PC22存留**，也不自动赋予MyLEAGUE球员游戏内“训练协议拒绝”按钮。

### 3.2 年份/平台差异的关键事实

2K22 **PS5/Xbox Series MyNBA**官方新闻[ SRC-0049 ]确认⟦Prep Hub⟧、新版MySTAFF、团队和个体训练。2021年开发者Courtside文章在官方内容转载[ SRC-0050 ]描述：
- Prep Hub聚合下场对手、团队体系熟练度、训练与疲劳；
- Team Training可见未来3周安排、练习种类/强度/疲劳/受伤风险与当前伤员及Load Management情况；
- 教练会按自身风格自动生成团队计划；球员的负荷管理可让其在不利条件下自主选择低压力训练；高负荷会降低Game Fitness，作者称与比赛时精力/属性有关；
- Individual Training允许围绕目标原型发展，并显示疲劳、受伤风险和负荷管理。

这份文献极其适合V3将来“教练、球员拥有独立判断权”的世界设计，**但明确是次世代MyNBA！** 在本项目PC22默认只记录⟦NEXT_GEN_ANALOGUE_AGENT_BEHAVIOR⟧，不得写成PC原生已有⟦Prep Hub⟧或球员会自动拒绝练习。

2021-09 OS**2K22次世代MyNBA**玩家[ SRC-0051 ]报告三周训练日程在推进日期后出现错乱；作者提供两段视频URL，并表示每天只推进一天/每天纠正时暂能绕开。我们只核实**作者的文字说明和视频链接存在**，**没有审查视频具体帧/时间戳**；对PC本世代不构成BUG定论。2023-04另一玩家回顾2K22次世代的训练表错乱，称2K23已改善[ SRC-0057 ]，说明该历史问题有明确版本边界。

### 3.3 PC本世代/同代实际参考，而非偷用PS5菜单

本项目玩家此前直接确认：PC22 MyLEAGUE训练含**团队、个人、导师**概念，界面类似2K20；这项⟦PLAYER_CONFIRMED_OPERATIONAL_CONTEXT⟧比次世代MySTAFF更贴近目标，但不是每个枚举的完整图证。

2022-02 OS同年**PS4 MyLEAGUE**玩家[ SRC-0053 ]自述：给所有年轻人分配个人训练方向，许多人High/Very High，整个赛季以模拟方式推进，发展并没有达到他预期。其存档同时用了社区ATD roster和改变过的成长/衰退滑块，因此**不能单变量断言“Very High没有效果”**；但足以反驳“把强度拉满自然必成长”的错误规则。PS4属于本世代类比，不能认证PC确切值域。

旧版2K15论坛玩家[ SRC-0054/0055 ]清楚描述球队训练、按原型训练、个人Intensity、球员疲劳条和按技能单独训练的取舍。有玩家发现专练投篮会增加专长却使其它能力下滑，影响OVR；另有人用不同训练模板发展边缘球员。这是**旧版具体经验**，不等于PC22旧版的每项训练入口仍存在。2021年2K22次世代玩家甚至抱怨“以前逐项训练属性，2K22仅能选择presets”[ SRC-0056 ]，再次提醒项目不能未经核对地开放“逐属性训练百分比”。

## 4. 自然成长与统计反馈：真实需要怎样判断？

**把输入和结果分开**：

| 类型 | 事实字段或候选来源 | 有什么用 | 现阶段的真实限制 |
|---|---|---|---|
| 训练输入 | 当前⟦training.team.* / training.player.*⟧源真实已观察值与其生效日 | 教练/球员能知道自己已选择的训练计划 | 注册字段不代表本期Snapshot已有值；若missing要继续UNKNOWN |
| 比赛暴露 | 每场game_id、实际出场分钟、背靠背日期/主客、比赛类型 | 区分练太多和打太多的暴露量 | R01记录PC22逐场日志/赛程原生查询有缺口 |
| 生理状态 | 当前疲劳、Game Fitness、伤病部位/类型、预计恢复、健康上下限 | 球员是否希望保护身体与赛季竞技能力 | 历史Fatigue原生字节布局≠已解读有效**实时**疲劳；伤病目前可用发布来源不足 |
| 变化 | 赛前/赛后/下月真实属性、徽章、伤病、上场、复发事件 | 判断成长与损失，允许模型修正预期 | 必须来源相同的真实游戏存档，不能用潜力泄露、不可随意写能力作为实验 |
| 世界环境 | progression/regression sliders、injury sliders、simulation vs 3D | 解释同方案不同世界线为什么不同 | 与训练师、潜力、年龄、不同进度均混杂；不能直接归因 |
| 人格/谈判 | 球员私有训练目标、伤病风险承受、教练要求、GM资源边界、媒体公开争议 | 为未来多Agent提供意见冲突/自由决策空间 | 外部SQLite概念，**不是已读取的原生NPC思想或拒绝API** |

**数据比较质量要求**：必须至少存`save_id / source_batch_id / game_date / player_native_id / team_id / injury_status_source / training_source_status / actual_minutes_window / ability_snapshot_ids`；如果比赛不同赛程/不同难度/不同伤病随机性，不得从一次成长差值计算训练增益系数。OVR受位置/角色权重影响，**不能仅凭OVR升降断言所有底层属性都同步改变**；R04再研究全部属性和徽章明细。

本轮不是执行实验，因此**不存在真实某队本季训练成功率、康复提速天数和永久损伤概率**。

## 5. V3角色可见、可选、可拒绝、承担代价：给自主涌现而非最优控制

| 游戏原料 | GM能选择/担负什么 | Coach能选择/担负什么 | Player可提出/拒绝什么 | Media何时能报道 | 原生效果与外部状态分界 |
|---|---|---|---|---|---|
| 团队强度、背靠背休息 | 讨论球队赛季目标、风险与球队资源，不必亲自安排每个动作 | 可能主张训练文化、高强度或恢复优先；与GM争论 | 对个人承担过载或休息不足表示不满，要求改变 | 报道真正公开的训练和伤病信息，不能偷窥私有诉求 | 真实6个team字段是原生设置；教练坚持什么、球员是否不满要在外部世界建模 |
| 个人模板、Intensity与override | 提供培养资源和薪资/球队职责的交换条件 | 依据打法希望球员往指定角色发展，也可愿意放手 | 争取投射/组织/低位模板，选择争取上场或保护职业生涯、甚至拒绝球队方案 | 只有球员或队伍公开训练分歧才可写新闻 | 真实5个player字段可成受控操作；人格拒绝不是游戏字段 |
| 身体风险、伤病与恢复 | 重排阵容或签人、容忍比赛短期损失，也可提出交易 | 可能减少使用、改变战术负担，或坚持要赢关键战 | 可拒绝过度训练/要求休息，面对长期事业选择 | 可报道真实已知伤停，不把“怀疑带伤”冒充医疗诊断 | 伤病真实记录必须从游戏取；自述痛感/未来担忧属于外部角色内心 |
| 成长/退化与导师 | 是否长期培养、买入即战力、能否负担老将导师成本 | 可能愿意给年轻人机会，也可能保守弃用 | 追求某种打法、跟某位老将学习，也可拒绝导师安排 | 报道真实成长趋势、天赋评价要按可公开资料 | 徽章增长只能记录游戏自然事实；不能直接编辑徽章以制造“导师成效” |
| 不确定性与失败 | 一支球队可以为了当季总冠军忽视年轻球员成长 | 教练可以坚持低效练法、在赛季中反思或拒绝变化 | 球员可冒伤病风险赌地位，也可提前休息选择长期职业寿命 | 对失败作主观评价但必须承认资料缺口 | 不设全联盟一套强度最优表、不用固定阈值压制不同价值取向 |

未来的`CHOICE`、`COUNTER`、`REJECT`、`HOLD`仅是**外部角色行为的研究描述**，**不是立即能调用的游戏原生命令**。让球员具备个人训练自主权是系统愿景；是否允许某类计划真正改写原生训练字段，需满足**原生映射已认证、同批身份、人物/角色模拟同意和真人玩家批准**。一旦Coach、Player、GM利益冲突，不能在研究阶段替任何角色强制裁决。

### 5.1 一场自由的谈判可以怎样发生（不是必选剧情）

一名健康但出场少的新秀想多练三分；教练认为球队更需要防守；GM认为自己可能很快交易他。三人分别看到**同一人物当前真实训练类型/强度、比赛出场和公开伤病**，但对未来与风险有不同信念。球员要求Outside、教练反报价Two-Way、GM可提不同职责。任一方可拒绝；未来比赛或成长若被真正观测，各自仍可重新评价。**不能为了完成故事自动把球员三分能力调高**。

另一名带伤老将可以要求休息，即使教练想冲击季后赛。失去的比赛胜率机会和长期健康目标同时存在；在没有真实疲劳/伤病来源时，不能根据年龄制造一条“已发生伤病”新闻。

## 6. 本轮已证/未证/下一轮R03-B

| 目标 | 已有真实基础 | 当前缺口 | 下一轮最值钱的资料 |
|---|---|---|---|
| 11训练设置 | 真实Repo Registry的6team+5player，Native packed布局 | PC22具体中文UI、各强度/覆盖优先级、正式本批对象读数 | 本世代训练页截图、模板/强度的完整选项，按实际身份关联 |
| 通用9个Player训练原型 | training.json已命名0..8 | 各位置UI更细模板的精确映射与能力方向；分配后的UI持久性 | 位置分类与实际原生编码配对，不以“9=全部UI模板”推断 |
| 团队Training强度 | home/away/autointensity/b2b休息/injury_recovery在Registry | 总负荷时间窗口、强度对比赛/体力的量化效果 | PC同代真实菜单及已观测状态 |
| 个人健康/疲劳 | progressive_fatigue_history布局候选 | 当前疲劳值解码与单位、伤病及可用性未发布 | 只读原生验证/玩家已有UI，区分HISTORY_ONLY与CURRENT_VALUE |
| 导师与徽章 | native mentorship_manager布局候选，Mentor在Registry为DISCOVERED | 关系有效期、兼容性与徽章自然变化、是否可执行关系设置 | 真实2K22 PC导师菜单/徽章变化；不改原始Badge |
| 2K22次世代高级训练 | 官方明确有Prep Hub、3周计划、Load Management/球员降强度 | PC本世代是否存在及操作/智能安排**UNKNOWN** | 不外推；仅供未来教练/球员自主决策原料启发 |
| 生涯自然成长 | 游戏引擎负责，OS多时代玩家有不确定且冲突经验 | 真实变化窗口、比赛/训练/员工/潜力独立因果未证 | R03-B继续研究伤病模型、康复与不同模式、成长差分，R04负责全属性/徽章/耐久字段 |

**历史研究记录（R03-A当时的下一步，现已执行完毕）**：R03-A首先发表，随后R03-B补健康/导师、R03-C审核结案；**当前最终状态以§§13–15及[R03审核报告](../reviews/R03_COMPLETENESS_AUDIT_V1.md)为准**。下批按PROGRESS恢复，不重复本轮已研究的2K22官方次世代Prep Hub全文。R04仍是完整球员本人属性/全部耐久和Play for Win/Financial Security/Loyalty等合同人格专项；本章不取代它。

**执行边界**：只读GitHub和公开资料、出版研究。没有打开游戏、训练写入、伤病编辑、潜力泄漏、创建Agent或启动DEV28/Codex。凡未知仍明确UNKNOWN。

## 7. R03-A新增官方可读图证：2K22次世代不是PC22

**VIS-0009：官方Individual Training Focus截图**，见[官方新闻原图](https://cdn.prgloo.com/media/2858117e546348dbb3c016b7282e72c3.png?height=663&width=442)。本轮已经实际看过图中像素：上方`SKILL TRAINING FOCUS`，中间`POINT GUARD/SHOOTING GUARD/SMALL FORWARD/POWER FORWARD/CENTER`位置选择、`PLAYER TYPE`和`TRAINING COMPATIBILITY`两列，右侧有球员OVR。可见PG类型组列出了ALL-AROUND、TWO-WAY、OFFENSIVE、DEFENSIVE、ATHLETIC、REBOUNDING、PLAYMAKING、OUTSIDE SCORING、INSIDE SCORING等。**这是一张2K22官方明确属PS5/Xbox Series MyNBA的截图，不是PC22原版字段画面**。图中组合对我们定义`(position, visible_player_type, compatibility)`关系有实际参考价值，但不证明其UI顺序直接对应本机raw 0..8或训练成功率。

**VIS-0010：官方Training Schedule截图**，见[官方新闻原图](https://cdn.prgloo.com/media/eedbfc01c17a465eb26f5093c697ee8b.png?height=663&width=442)，本轮也实际查看像素：顶部`TRAINING SCHEDULE`与跨日期的多格日历，底部有`TEAM SYSTEM`、`TRAINING GOALS`、`TEAM OVERVIEW`三个信息区域，显示练习日与队伍状态的同屏联系。**这不意味着PC本世代有同样逐日练习排班UI**；具体截图像素较小，未逐项认证每个单格训练名/数值/动画，绝不复制为PC菜单完整值域。新闻页还有`MyNBA Prep Hub`图片链接，但本轮该媒体原图链接无法稳定加载，不把它升级为已检视像素的VIS。

两张官方原图具有实质视觉证据、也拥有严格平台边界。本研究仓库只保存链接和逐项核查文字，**没有上传或复制官方受版权保护的截图**。后续若得到PC22真正对应的训练页面，再按实际列与原生`training.json`对照，不强求版本看起来完全一样。

## 8. 用户校正：次世代终极联盟资料的可复用性（2026-10-21）

玩家明确指出：**次世代与PC本世代最明显的差异主要在3D物理/比赛引擎；终极联盟的大多数经营机制、信息和选择项实际上高度相通，可广泛复用**。研究方法因此作如下校正：

- **机制级默认可借鉴**：即使资料来自2K22 PS5/Xbox Series MyNBA，也积极用于解释训练强度、团队/个人训练、身体负荷、伤病风险、训练师、角色选择与动态反馈。不能因为资料标记NEXT_GEN就从能力知识库删除其训练行为或经营价值。
- **“概念适用”不等于“原生控件同一”**：官方Prep Hub的三周日程及Conditional Coaching是次世代明确宣传的入口/整合呈现。我们可复用其训练—体能—成长的**设计逻辑和模型可考虑的行动**，但不能未经查验宣称PC22有完全同名UI、相同每个子项、对应内存偏移或NPC自动拒绝训练。
- **UI/内存/实战算法单独核实**：PC22本地Registry的11个训练字段和9种通用训练原型仍是当前真实技术基线；次世代截图若出现额外Game Fitness或Load Management面板，可以列为`CROSS_GEN_MECHANISM_REUSABLE / PC22_UI_NATIVE_UNKNOWN`，不可虚构本机已经捕获的健康数值。
- **优先比较相同的业务操作，不强求界面像素一模一样**：如同样的强度切换、个人培养方向、伤病康复、教练自动安排，即使界面布局不同也可能使用共同规则。应尽量寻找具体差异证据，避免只因“次世代”标签就判定PC不可用。
- **研究人格涌现的价值优先**：让未来教练、球员和GM知道可以围绕负荷/发展做怎样的选择、各方利益为何冲突、失败会产生何种事实反馈；新旧平台差异仅决定游戏原生执行和字段验证程度，不限制角色学习通用篮球机制。

证据栏采用双轴而非排他判断：`MECHANISM_TRANSFERABILITY=HIGH_BY_PLAYER_EXPERIENCE`，`PC22_NATIVE_UI_OR_IMPLEMENTATION=NEEDS_INDEPENDENT_VERIFICATION`。后续R03-B/R04–R07按此执行；若找到某项确实只在次世代存在，将它标记为**具体例外**而不是整代资料不可复用。

---

# R03-B — 身体风险、伤病事件、康复和导师的动态机制（2026-10-21）

> **本轮研究范围**：完整补足“谁感知身体状况、哪些训练/医疗决定可选、什么真实事件会改变职业生涯”的知识，而非开工编码。证据详见SOURCES中SRC-0060..0069。用户明确指出次世代终极联盟机制高度可复用，因此本章承认其训练/医疗**机制层价值**；只对具体PC22字段、UI路径与可执行对象保持独立认证。

## 9. 伤病不是一个按钮：发生、严重程度、部位、持续时间与比赛模式是不同事件

一个球员至少可以经历**健康可用 → 训练/比赛暴露 → 伤病事件 → 诊断/预计缺席 → 康复过程 → 恢复比赛资格 → 再受伤/长期状态变化**。游戏可能在其中给出伤病类型、预计天数、可否带伤比赛、身体耐久，以及玩家/团队的不同来源记录；哪些字段可见、当前实现是否已采、实际写入权必须各自标记。**R03只研究病程和角色选择共性，R04再调查全部球员身体部位耐久字段、逐项特性和值域。**

### 9.1 同版一手资料暴露了“比赛参与方式”的混杂

- 2021-11 Operation Sports“**MyLeague Injury Sliders**”[SRC-0060]：作者称其模拟比赛中有伤病，但手打100+场未见伤员；回复的次世代MyNBA玩家说调高sliders后快速模拟出现较多伤病、手打很少，另有玩家报告**某场手打Luka真实受伤动画**。这并不证明手打“永不受伤”，恰恰证明“手打/看CPU三维/快Sim”的`game_execution_mode`必须单独标记。
- 2022-03 OS“**MyLeague Why are there no injuries**”[SRC-0061]提供同版相反个案：有人长期无现场伤病，也有人遇到鼻骨受伤；有人说降低Durability后立即出现受伤，另一玩家降低Durability并把伤病滑块开满却仍未出现。**这些都是未控制样本的玩家报告**，不能把“Durability=20必受伤”写作规则或操作建议。
- 2022-09 OS 2K23 MyNBA讨论[SRC-0063]中有玩家**回顾2K22**也出现“预计4–6周，但提前恢复”的状况；讨论触及是否在MyNBA开档时设置Duration、不同赛季长度，以及同一伤病时长字段的不同含义。回忆+另一版本问答不等于PC22具体康复算法，但足以提醒：**事件初始预估、剩余天数、正式恢复日期和复赛日期不是一个字段**。

**最小完整伤病事件模型**（未来研究建议的标记，不是新原生DB schema）：`native_player_id / team_id / game_id_or_practice_event / source_time / game_execution_mode / body_part_if_native / diagnosis_if_native / severity_if_native / initial_estimated_absence / observed_remaining_days / expected_return / actual_return / reliability`。没有明确游戏来源的字段必须`NULL/UNKNOWN`，不准媒体创造“膝盖已经重伤”或假恢复时间。

### 9.2 三层伤病设置与两个不允许的错误推断

| 层 | 研究对象 | 可选空间与反馈 | 不可做的推断 |
|---|---|---|---|
| 球队训练/个人训练 | 已认证11个可注册字段里的Intensity、Recovery、B2B休息与球员Override | Coach与Player可以争论训练负担；批准后观察真实恢复/缺赛 | “injury_recovery=1一定缩短7天” |
| 世界/比赛模拟环境 | Injuries On/Off，2K22系列教程列出的User/CPU Injury Frequency、Injury Severity等候选，以及模拟Fatigue/Recovery等滑块[SRC-0062] | 世界设定与玩法差别影响联盟遭遇风险；此为**世界权力**，不是30队GM可私自改全局 | “把所有设置调100就能使3D现场伤病正常” |
| 球员个体/医疗/运动医疗员工 | 身体部位Durability（R04详查），自然负荷、球队Trainer；2K22次世代独立Sports Scientist/Physio/Sleep Doctor等职责[SRC-0064] | 俱乐部围绕风险与康复资源讨价还价；球员可以追求更快复出或保守职业寿命 | “PC22已经有7个可聘Sports Medicine岗位/能读到该岗位数值” |

对当前项目，`training.json`中有`injury_recovery`标记和`progressive_fatigue_history`布局；**并没有经本轮证实的真实当前伤病明细/预计复赛事件表**。已知`config/source_catalog.json`中的`injuries_availability_rotations`来源此前为`NOT_OBSERVED`；历史SQLite伤病字段可能为占位NULL，不能因表有列推定事实已入库。未来实际采集覆盖状况每个batch另审，不用旧状态永久宣告不可获取。

### 9.3 “恢复/缺席时间”为什么不能直接写成统一规则

合理的因果分离是：`初始伤情严重度 → （原生医疗/康复/比赛时钟的未知规则）→ 当前伤停估计 → 真实复赛`。官方2K22次世代MySTAFF将**Sports Scientist**关联伤病预防/身体部位Durability，**Physio**关联伤后康复，**Sleep Doctor**关联累积疲劳管理[SRC-0064]，是很有用的医学职能知识。但是本世代当前已确认主要招聘Trainer，不能用一个Trainer评分代替次世代全部岗位，也不能伪造“Staff A缩短康复15%”。球员身体损伤是否会造成永久潜力/属性变化、伤后状态是否重新影响比赛，当前缺PC22实验，属于`EFFECT_UNKNOWN`而不是“没有损伤”。

## 10. 疲劳：瞬时场上体力、跨日负荷和历史进展不能混成同一个数

| 项 | 球员/教练能否据此做判断 | 当前取证和含义 |
|---|---|---|
| **3D比赛内体力Stamina** | 若当场界面显示，教练可决定让某人休息或冒险继续打 | 游戏比赛机制概念；外挂当前控制没有实时单场体力采集合同 |
| **跨日累积疲劳Progressive Fatigue** | 若当前真实值可查询，球员可比较负荷与健康目标 | `player_training.progressive_fatigue_history @0x2F5`及点数位域已登记**静态结构**；不知道采样间隔/取值单位/哪个历史点是当前点 |
| **训练强度历史Intensity History** | 对了解过去团队计划可能有用 | team/player均有历史数组布局；未证明现实已保存或被R03本轮读取成随时间变化的列表 |
| **伤病剩余时长** | 有真实观察时决定复出意愿/训练例外 | 需要独立伤病来源；不能从疲劳历史反推出病因和具体剩余时间 |
| **比赛曝光负荷** | 即使没有生理指标，实际分钟与赛程可以给角色提供**有限可见事实** | 依赖R01的GameID、真实比赛模式及可查询分钟；累计赛季MIN不能替代最近7天实际负担 |
| **游戏内Load Management/Game Fitness** | 2K22次世代MyNBA官方明确展示并赋予选择与代价 | 机制可高价值复用；PC22原生同名菜单/数值采集未认证 |

**取证分级不可压缩**：
`NATIVE_LAYOUT_KNOWN` ≠ `HISTORY_DECODED` ≠ `CURRENT_FATIGUE_VERIFIED` ≠ `GM_QUERYABLE_FOR_BATCH`。若状态没到当前可查询，Coach/Player可以提出`REQUEST_DATA`或依据真实公开出勤作主观判断，**不能以虚构精确疲劳百分比强化人物设定**。

真实NBA医学文章[SRC-0069]支持篮球负荷与伤病的复杂关系，但真实科学研究**不是**2K引擎的参数表，更不提供PC22必然阈值。不同角色可以持有不同关于风险的信念，这与游戏未证数学式同时成立。

## 11. Mentorship是“提出师徒关系”，不是“允许直接赋予徽章”

| 环节 | 可用机制信息 | 当前项目对应证据 | 角色可采取的自由选择 |
|---|---|---|---|
| 选择导师与学员 | 2021年离线MyLEAGUE玩家说明`Training→Mentor`页面可查看徽章进度[SRC-0065]，2K21本世代玩家报告过导师成功传授徽章[SRC-0066] | `mentorship_manager`有`mentee_id/mentor_id/duration_days/compatibility/num_badges/badges_array`结构；仍DISCOVERED、**不具备通用执行** | 教练可推荐导师；老将可以拒绝承担指导职责；新人可以要求特定对象 |
| 指定想学习的徽章 | 2021-12**2K22时期**玩家针对恩比德→斯图尔特Post Lockdown作出是否消耗导师徽章的询问，回复认为不会[SRC-0067] | `badge_slot`有`type_id/level/is_active/progression/date_last_checked`布局，但目前未认证自然转移数学条件 | 学员可在外部愿望中表达徽章偏好；不代表当前有`badge.transfer`安全写入 |
| 按季度/赛季查看结果 | 2K21玩家说导师页会看到徽章的渐进变化，也可以比较赛季前后player card[SRC-0065] | 需要真实Badge前/后快照，不能把`progression` raw值当作已经授予徽章 | Coach/Player可满意、失望、重选或坚持 |
| 出现BUG/不确定 | 2022-01至04**2K22 MyLEAGUE**有人报告设定某些导师会崩溃[SRC-0068]；其它系列版本有人说导师效果微弱甚至看不到 | **没有当前PC官方bug ID或复现条件**，不声明本机一定崩溃 | 角色可请求技术核验；真实外挂不得以修改徽章来掩盖异常 |

**尤其重要**：2K22在线MyLEAGUE 2021–22讨论[SRC-0070]中，一位用户先认为在线联盟没有Mentorship，2022-02另一位称在Overview里滚动可找到“Change Mentor”。这说明**同一功能是否存在和藏在何处**都可能受模式/入口影响，不能把线上菜单经验直接搬到离线PC，并由此断定导师“不存在”。

**GM玩法承载约束**：即便未来玩家/教练双方同意某导师关系，现行DEV14仍标`mentor.relationship=DISCOVERED, writable=false`；R03不授权直接操纵导师结构或Badge等级。未来只有专门取得本机身份、合法字段与可靠readback、真实玩家批准才可执行师徒操作。球员正常徽章自然变化仍由2K游戏负责。

## 12. 训练师（Trainer）与自然成长/衰退：职业资源不是决定论

- **员工职能**：PC用户确认本世代可聘Training/Trainer岗位；项目源里的STAFF8类技术位与可任命6岗位不同，不应把Trainer和Assistant Coach或次世代Sports Medicine七岗同一化。
- **同年官方2K22 MyNBA**明确区分Stamina Trainer、Strength Trainer、Sports Psych、Sports Scientist、Physio、Sleep Doctor及Team Doctor、各自影响健康、体能或球队心理[SRC-0064]，可为**角色谈判与医疗风险知情**提供机制原料，不表示PC本世代有全部职位和原生控制。
- **2K旧版玩家经验**对Trainer影响伤病避免、恢复、体力及休赛期Training Camps名额看法不一致（R03-A SRC-0058）；不能根据Hire Trainer A级给出“自然能力每月+2”公式。
- **进步与退步**：2020年玩家[ SRC-0071 ]报告以Very High全季训练却发生OVR下降；环境包括球队阵容、Trainer评分、潜力/年龄和自然进程，**单一训练强度的实际增长函数不可辨识**。身体状态、能力变化、导师徽章也不应合成“训练收益总分”强迫所有角色接受同一计划。
- **外部角色可以有错判**：GM坚持“年轻人应高负荷”，教练更重视争冠，球员担心短期伤痛与长期寿命，训练师提供专业意见，媒体根据公开受伤情况评论；**模型各自可以拒绝**，但真实医学职能与游戏原生信息须有不同可见权限。

### 12.1 按角色组织健康事件的“可观察世界”

1. 球员收到可见的个人训练计划与有来源的伤病结果，自己可能珍惜合同窗口、渴望上场、承担伤愈后再次受伤风险。
2. 教练看到球队训练政策、可用阵容、已公开的健康/可用性数据；可能要求老将上场或允许自主恢复，并需要对比赛结果负责。
3. GM看合同、可用名单、训练师资源与球员要求；可商议续约/交易/轮换或拒绝额外医疗资源，不因少一项数据就强迫“保险最优”。
4. 媒体只能依据游戏公开的球队公告、真实名单状态和可发表声明报道；不得把私人伤病报告、隐藏疲劳数值或球员私有信念直接当公开新闻。

状态语义用`GAME_NATIVE_FACT / GAME_NATIVE_CONTROL / SERIES_MECHANISM_REFERENCE / EXTERNAL_ROLE_GOAL / EXTERNAL_ROLE_CONSENT / PLAYER_REAL_APPROVAL / UNVERIFIED`分别记录。只在事实真的被观察后更新历史事件，不通过自行修改伤病/能力模拟“成长故事”。

# R03-C — 机制范围覆盖、停止规则与正式审核（2026-10-21）

## 13. 全机制家族和证据达标矩阵

| 家族 | 可解释机制和可选行为 | 目标PC原生观察/控制覆盖 | 当前研究结论 |
|---|---|---|---|
| Team Training：6项 | 主客场强度、自动化、背靠背前后休息、康复方向 | 静态Registry与通用状态I/O已存在；当前batch值未在本轮查询 | **RESEARCH_DONE / RUNTIME_NOT_TESTED** |
| Player Training：5项 | 位置与通用培养原型、个人强度/恢复/Override | 原生枚举0..8；各位置菜单与训练效率映射未知 | **RESEARCH_DONE / EXACT_TEMPLATE_MAPPING_UNKNOWN** |
| 训练日程和Load Management | 日程强度、Game Fitness、练习风险/自主放低强度 | 官方次世代可解释；PC22完整UI和当前体力值未证 | **CROSS_GEN_MECHANISM / PC_EXECUTION_UNKNOWN** |
| 疲劳/历史 | 比赛暴露、累计Fatigue历史、3D当场体力 | 历史布局存在；无可信当前值/单位/衰减公式 | **NATIVE_LAYOUT_KNOWN / CURRENT_DATA_GAP** |
| 伤病与康复 | 类型/部位/严重度/预计康复/实际复出 | 同年不同比赛模式玩家相反案例；当前伤病数据来源未认证 | **COMMUNITY_ENGINE_BEHAVIOR / LIVE_DATA_GAP** |
| 耐久/年龄与自然变化 | 身体风险决定、自然Ability/Badge成长/退化 | 不以一次OVR变化计算效应；R04调查完整body part字段 | **RESEARCH_DONE / FULL_FIELD_LIST_DEFER_R04** |
| 员工Trainer与次世代医疗 | PC本世代Trainer、次世代七类医疗分工 | STAFF槽非可任命岗位；每个职能效果PC待证 | **CROSS_GEN_REFERENCE / PC_EXACT_EFFECT_UNKNOWN** |
| 导师/徽章进度 | 选择导师、学员与目标徽章、长期有条件反馈 | native关系结构DISCOVERED，不支持通用更改；社区有成功/崩溃分歧 | **RESEARCH_DONE / CAPTURE_EXECUTION_GAP** |
| 比赛模式与世界滑块 | 手打/3D CPU/快Sim伤病不一致；频率/严重度环境 | 相同参数不同模式未受控，世界设定不属于30队GM自行权限 | **RESEARCH_DONE / ENGINE_FORMULA_UNKNOWN** |
| 四角色的健康人格选择 | 同意、争论、拒绝、风险/合同/公众形象 | 外部角色隐私与原生客观事实分层；不开发Agent | **RESEARCH_DONE / FUTURE_AGENCY_IMPLEMENTATION** |

## 14. 有界结案：哪些UNKNOWN不应该拖住R04

**R03公开文献研究达成“可列出机制、明确自由选择、知道必须观察哪些动态事实、允许事后反馈”的目标；但没有实现PC22健康数据实时闭环**。下列内容**不能称已实现**：

- `progressive_fatigue_history`动态解析的单位/采样顺序，当前可供GM查询的精确累积疲劳和比赛体力；
- 当前伤病、部位/预计剩余天数、旧伤/可出场资格的稳定本地查询与历史事件账本；
- TRAINER员工属性对防伤、康复和职业发展准确加成公式；
- Mentorship的具体原生UI/徽章传递条件/关系写入readback；
- 全部位置特定个人训练模板的PC22原生精确映射；
- 快速模拟 vs 手动玩 vs CPU观战的伤病概率差异的可重复量化；
- 官方次世代新增MySTAFF/Prep Hub界面的PC本世代同名存在与完整控制。

这些是**后续可以定向原生取证的已知缺口**，而不是可任意填默认值的“暂无数据”。K06不延伸为R04的全部身体Durability和人格徽章字段字典，不覆盖R04专项。为避免无限反复搜索PC画面，保留最小可核对清单并封存当前文献研究；日后经批准收到本机资料时**增量修订**，不推翻既有证据。

## 15. 交给审核人员的诚实判断标准

- **知识覆盖**：训练、负荷、健康、伤病、耐久、康复、导师、Trainer/医疗、自然成长、现实伤病模式差别、世界规则与四角色自主选择都被研究或明确保留给R04。
- **操作透明**：明确哪些是真实项目6+5已注册字段，哪些是跨代机制来源，哪些只是原生历史结构，哪些是目前没有实时观测的健康状态。
- **非干预**：不通过设置全联盟统一“高强度最优训练”、改Ability/Potential/Badge/伤病天数来替角色塑造故事；不把原生自动Load Management当已实现的外部自主Agent。
- **出路明确**：玩家可在R04之后要求DEV28针对以上缺口只读调查，或使用真实游戏截图补证；R03的文献研究已经有明确停止条件。
- **质量闸门**：如果要求的是“让未来角色今天就根据实时健康数据自主运营”，R03仍**不能通过执行就绪验收**；如果要求的是“为未来角色提供机制选择、可获取信息目录、约束和反馈”，则**文献研究可通过、原生读取与执行欠账列入阻断项**。

**建议审核结论**：`R03_RESEARCH_COMPLETE_WITH_NATIVE_DATA_GAPS`，与`AGENT_OPERATIONAL_READINESS=NOT_READY`并存。是否接受此边界并推进R04，由玩家决定。本轮不启动R04、不生成角色Agent、不修改游戏。
