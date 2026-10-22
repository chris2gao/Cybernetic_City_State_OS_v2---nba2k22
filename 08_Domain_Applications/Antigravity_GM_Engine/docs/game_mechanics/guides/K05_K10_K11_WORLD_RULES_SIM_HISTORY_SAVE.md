# K05 / K10 / K11 — NBA2K22 全局规则、3D比赛、日历模拟、历史与存档机制

> DEV29 V3，2026-10-21，**R06-A首批正式研究**。R06-A研究K05原生世界设置、3D比赛与Calendar Sim；R06-B另研究K10历史纪元/奖项/媒体，R06-C另研究K11时间推进/存档，R06-D整合。目标NBA2K22 PC本世代离线MyLEAGUE，PS4旧世代与PS5/XSX次世代内容保留出处和区别。**只提供游戏资料和设置机制，不制定Agent/GM/Coach/Player/Media行为，不修改游戏。**

**研究伴随目录**：[R06-A世界设置与双引擎机读原料](../catalogs/R06A_WORLD_GAMEPLAY_SIMULATION_SETTINGS_V1.json)：项目settings与world合计**86个注册候选**（可能同址重叠，不是86个验证按钮）、玩家资料中**118类菜单/参数候选**（Setup 13，Simulation 32，3D Gameplay 73）。来源SRC-0163..0173见[SOURCES](../SOURCES.md)，VIS证据见[外部视觉索引](../visuals/EXTERNAL_VISUALS.md)。

## 0. 区分4种运行过程

| 流程 | 数据产生方式 | 主要可观察控制 | 风险 |
|---|---|---|---|
| LIVE_3D_USER_CPU | 真人操控和原生AI在真实3D里逐回合比赛 | Quarter Length、Game Speed、Gameplay USER/CPU攻防判定、ACE、手柄配置 | 真人输入与球队经营控制权不是同一变量 |
| LIVE_3D_CPU_CPU | 3D AI打完整场，人观看 | 真实投篮、身体碰撞、CPU攻防、ACE及全场回放/Box | **不是日历快模拟**；CPU与USER侧各字段真实消费者需确认 |
| CALENDAR_SIM | 日历由Sim Engine快速产生比赛结果和Box | Sim Quarter Length、节奏、出手结构、命中、事件、伤病、Stat Distribution | 无法保证拥有3D逐球/动作/站位细节 |
| SIMCAST_JUMP_IN | 在SimCast状态和真实3D之间转换 | Simulation与Gameplay设置、标准化可能同时参与 | 玩家确实报告比分/赛后统计不一致，不能把日历数字等同场上原始事实 |

**同版强证据**：2021-11 PC22玩家cdcool明确写控制30队、却看每场CPU-vs-CPU的3D比赛、从不Quick Sim（SRC-0163）；2022-01 PC默认阵容玩家res2明确列出Quarter Length=12、Sim Quarter Length=11和整组Simulation参数（SRC-0164）；2021-09 PS4旧世代MyLEAGUE玩家DarthRambo用同组Sim菜单及独立Gameplay设置（SRC-0165）。这些**取值是作者自定义实验，不是官方默认、也不是本项目当前存档的读取值**。

## 1. 联盟Setup与标准化：最容易污染统计的开关

| 候选设置 | 实际语义 | 未知边界 |
|---|---|---|
| Season Length / Playoff Length | 控制常规赛与系列赛赛程长度候选 | 具体PC22原版列表和赛季中可否修改待证；R06-B/C继续 |
| Quarter Length | 3D真实单节分钟数 | 单节12不代表日历模拟也为12 |
| Simulated Quarter Length | 日历Quick Sim计算单节时长 | 不保证SimCast跳入模式完整沿用同一缩放处理 |
| Normalize Played to Sim Minutes | 对真人比赛统计MIN进行显示/赛季累计等口径转换的候选 | 不是真实多打了分钟；其实际作用与存储映射待实测 |
| Normalize Played to Sim Stats | 对短单节真实比赛的得分、篮板、助攻等作模拟时长口径转换 | 可能赛后分数变化，不可当球员当场真实完成事件 |
| Autosave | 自动存盘及历史覆盖设置 | 开启≠已保存当前内存改值，也不保证外部数据源跟进；R06-C单列 |
| Game Speed、Difficulty、Foul Out | 3D速度、难度及规则；同版PC玩家有这些项 | 改HoF自定义滑块后不必与官方HoF预设同值 |
| Fatigue/Injuries | 游戏体能与伤病开关/频率范围 | 单场体能、日历恢复、身体Durability是不同对象 |

**具体同版异常**：2022-06 MyLEAGUE用户报告实场比分约126:116，退出游戏后赛程变成300分量级，单人35分变98分，回复指向Normalize开关，作者确认曾开启（SRC-0170）。这是**单用户问题线索，不是可推导的固定乘法规则**。2021-04更早的MyLEAGUE玩家则报告统计被规格化但分钟没有同比改变（SRC-0171），只是前代警示。2K22的MyGM玩家有找不到Normalize菜单的讨论（SRC-0172），不能借此断言PC22 MyLEAGUE没有该功能。

研究读取同一场Game应分开记录：Game ID、save/batch/game_date、真实Played和Simulated Quarter、Play/CPU-CPU/QuickSim/SimCast/Jump-In、两个Normalize开关、场内结束比分、日历页保存比分、赛后Box、季节累计以及球员MIN。**若不一致标SCORE_CONFLICT或NORMALIZATION_UNKNOWN，不得用其中某一个统计强行替换另一项“真实发生”。**

## 2. 日历Simulation Engine至少5组，和真实3D不是同一张表

2021-09 PS4同版+2022-01 PC同版玩家反复列出菜单族（SRC-0164/0165）：

| 类别 | 玩家报告的英文子项 | 研究语义和边界 |
|---|---|---|
| Fatigue / Recovery | Player Fatigue Rate、Player Recovery Rate（其它来源） | 赛程体力消耗和恢复趋势；并非单个球员16部位身体耐久度值 |
| Team Style Factors | Team Pace、Team Fastbreak | 模拟的球队风格与回合节奏倾向；不是篮球统计的实测Pace |
| Possession Results | Possessions Per Game、Shots、Assists、Steals、Blocks、Turnovers、Fouls、Injuries | 模拟生成事件的设置；值100不等于这队已经打出100回合 |
| Shot Types | Dunks、Layups、Shot Close、Shot Medium、Shot Three | 模拟出手类别分布候选；不是球员个人Tendency或球队Playbook |
| Shot Percentages | Dunk、Layup、Close Range、Medium Range、Three Point、Free Throw | 模拟命中率环境权重；不等于LIVE_3D中3PT Success |
| Stat Distribution | Shot、OReb、DReb、TReb、Assist、Steal、Block、Foul、Turnovers | 球员间统计事件分配的候选机制；不是GM锁定球员出手次数 |

**反例说明**：DarthRambo和res2有Team Pace=100、Possessions=100、Fouls=0的例子，而同版RealSport攻略建议Pace=49、Possessions=49（SRC-0167）。这只能证明社区存在不同调校方案，并且部分玩家**同时修改了球员个人倾向**；不能把这种组合实验当单一滑块的因果公式，绝不能不经批准给全队球员修改能力/倾向以“还原”他人的Sim结果。

## 3. 真实3D Gameplay七大参数家族

| 族 | 代表菜单/值 | 影响目标（定性） | 明确不可混同 |
|---|---|---|---|
| Offense | Inside/Close/Mid/3PT Shot Success、Layup、Shot Coverage Impact、Shot Timing Impact、Pass Accuracy、Ball Security、Contact Shot | 实场投篮、传球、身体终结、对抗判定环境 | 个人Skill/Badge、日历Shot Percentages |
| Defense | Driving/Inside Contact Shot Frequency、Layup Defense Strength Takeoff/Release、Jump Shot Defense Gather/Release、Help Defense Strength、Steal Success | 碰撞、干扰和防守动作执行效果 | 不能自动修复挡拆协防“第三人不补位”的ACE战术算法 |
| Attributes | Acceleration/Speed/Strength、Stamina、Durability、Hands、Ball Handling、On-ball Defense、Off/Def Awareness、Lateral Quickness | 原生能力在实场动作/判定中的**全局倍率或影响环境** | 不等于给任何球员原生Ability、潜力、徽章直接加点 |
| Tendencies | Take 3PT Shots、Attack Basket、Post Shots、Contest Shots、Backdoor Cuts、Steals | 3D全局USER/CPU的偏好概率环境 | 不是原生球员99 Tendency字节 |
| Fouls | Charging、Blocking、Shooting、Loose Ball、Reaching、Illegal Screen、Over Back | 实时3D犯规判定发生倾向 | 日历SIM Possession Results/Fouls |
| Movement | With/Without Ball的Speed和Acceleration各Min/Max，共8项 | 持球/无球速度及高低评分差异 | Game Speed、帧率和个体球员速度Rating |
| General/Controller | Game Speed、Difficulty、Shot Timing / Real Player %、Controller Side | 游戏手柄输入、难度、观看AI对AI的状态 | 30队“User经营”不等于球场10人自动使用USER滑块 |

**2K22 PC来源**：cdcool在PC CPU-vs-CPU展示完整实场滑块（SRC-0163）；RES2在2022年回答PC默认Roster并附本世代Gameplay配置（SRC-0164）；Shady Mike的2021-10方案描述PC Movement表现不确定并给完整With/Without Ball候选（SRC-0166）。PS5 HOF的J-Kits提供同版新世代比较而不能直接充当PC22本机游戏引擎证明（SRC-0173）。

**USER/CPU重要未知**：球队经营权、比赛手柄所属和具体场上10名球员消费哪一侧的Gameplay slider应分别核查。本项目此前记录30队全部User-controlled的意图，但没有一条PC22实证证明“所有AI球员只消费USER栏”。2017论坛观点（SRC-0169）认为电脑队友也读CPU，属于旧版本社区经验，不能推广为当前游戏的绝对执行逻辑。

**用户已经真实观察（非本轮模拟实验）**：你的HoF原版ACE能临场应变，某些挡拆中第三人没有补位，普通球员篮下接触终结困难、个别中锋带球像慢动作，但你明确排除一般帧率问题，认为更多涉及运球速度/加速度。它们可作为参数作用研究的**观察目标**，不能断言Help Defense=100、Speed With Ball=某个数就必然修好，也不能因此直接改某位中锋的个人技能。

## 4. 原生技术注册表：有字段不等于现场可以安全读写

| 已有本仓库文件 | 实际存在的结构 | 尚未被R06实机验证的部分 |
|---|---|---|
| config/state_io_native/settings.json | 七组共**49个静态字段候选**：Game 6、Simulation 2、Trade 10、Contracts 8、Injuries/Morale 11、Progression 3、Gameplay 9；含RVA/offset/type/min/max/default | 某些固定地址与默认值来自老CT推断，不能认定当前PC22游戏build及存盘后均正确 |
| config/state_io_native/world.json | 五组共**37个静态候选**：Trade/Draft 9、Contracts/Finance 8、Progression 3、Injury/Morale 12、Gameplay/Calendar 5 | 和settings可能重叠，相同slot+offset不能当两个独立游戏按钮 |
| config/state_io_native/court.json | 已配置四个Gameplay modified_sliders及其Float/镜像布局 | 仅表示项目存在这四项受限技术定义，不代表原版所有滑块均已写入验证 |
| src/slider_manager.py | 旧读取函数和一键“拟真滑块锁定”设置函数，带静态基址与默认候选 | 旧一键设置函数会**实际修改游戏**，本轮既不调用也不据此认全部原生值已认证 |
| src/gm_state_io/registry.py | 把world/settings导入世界设置Registry，供以后观察/计划的技术路径 | 软件Registry显示writable不等于本游戏同版本已验效果、当前存档真实值或用户批准写入 |

**一个明确技术差距**：settings.json目前只有simulation.normalize_stats及simulation.sim_quarter_length，而玩家资料清楚区分Normalize Played to Sim **Minutes和Stats两个开关**。注册表的单字段不证明另一个已经覆盖；其名字和旧slider_manager中的中文解释也存在口径混淆。**不得以normalize_stats=1断定“两个都开”，也不该从一个模糊地址写两处数据**。

R06-A没有使用PC进程、运行任何CPU游戏、试验写入/重启，也没有取得原版PC MyLEAGUE全套滑块的可核实逐像素截图。绝大多数字段的实际值域、更新机制、原生内存效应/长期存档状态仍需要以后独立取证，不能依赖历史文档标题写“权威/科学最优”就自动升级为游戏事实。

## 5. 模式联动与真实比赛反馈

研究可稳定区分的对象：

- 全球Gameplay倍率/控制设置与每队Coach ACE/POE/Playbook、个人Player Rating/Badge/Tendency，**可能同时影响同一场比赛**；真实引擎具体运算顺序仍未知。
- 日历模拟设置可影响比赛结果分布，**实场3D改变**不必然能让日历Quick Sim各队产生同样的打法。
- 已进行比赛后的Box、球队赛季平均、真实赛程比分和历史保存的记录存在**不同生成/归一化时点**；全部跟Game ID/Source Batch/真实游戏日期关联，不能因数值不合真实NBA平均便直接改游戏属性。
- 2K22 PS5/XSX MyNBA的同版数据可以作为“可能有何机制”的游戏玩法类参考，但不能从新世代引擎参数推断PC完全一致的地址、CPU侧消费行为或ACE物理计算。
- **游戏运行结果归原生引擎裁决**。DEV29不为任何独立GM/Coach/Player设计强制最优滑块，也不提前推进日历或写历史冠军。

## 6. R06-A研究结论及下一断点

**目前可靠**：PC22本世代MyLEAGUE确有被玩家独立使用的3D CPUvsCPU环境与日历Sim滑块分类；真实Gameplay七家族、Sim五组与Setup参数可以分辨；已有86个静态Registry候选和部分代码读写入口；Normalization异常有2K22同版报告。

**目前未知**：在本项目当前build下86项位置是否都成立、每个参数精确UI合法值、当前存档真实启用状态、两个Normalize独立原生映射、USER/CPU各AI消费模式、SimCast跨引擎切换、真实比赛统计完整读回与保存持久性、误差/效果系数。

**R06-A状态：R06_A_RESEARCH_PUBLISHED_WITH_PC22_RUNTIME_VERIFICATION_GAPS**。R06-B将集中研究K10历史时期、联盟规则变化、奖项/纪录、媒体数据，不设计媒体Agent。R06-C研究K11游戏日历、阶段推进、Autosave/Manual Save、存档覆盖与恢复；R06-D再研究整合。以上阶段尚未启动。R05正式保持用户已批准状态R05_RESEARCH_CLOSED_WITH_PC22_NATIVE_CAPABILITY_GAPS，选秀权代码同步归独立Codex维护。**没有修改球员能力、比赛设置或真实游戏数据。**
