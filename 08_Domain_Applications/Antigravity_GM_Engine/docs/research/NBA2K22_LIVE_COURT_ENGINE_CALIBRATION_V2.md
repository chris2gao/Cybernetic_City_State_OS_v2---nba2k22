# NBA2K22 PC — 实时3D赛场引擎竞技打磨研究 V2（LIVE COURT ONLY）

> **2026-10-19 玩家再次确定最终技术边界**：本文件曾提出的ACE运行时内存控制、C2临场切换、C3外挂实时教练和ACE算法逆向**不再是项目任务**。用户实机确认原版ACE能叫暂停/动态调整，决定比赛时始终ACE ON、完全接受原版AI自主调整；GM只作赛前人员/战术/个人倾向。我们三方只研究Gameplay赛场环境滑块：Movement、Defense、Offense命中/传球、Attributes、Fouls、全局Tendencies、General/Controller。**现行权威文档：[LIVE_COURT_GAMEPLAY_PARAMETERS_V3](NBA2K22_LIVE_COURT_GAMEPLAY_PARAMETERS_V3.md)**。V2仅保留历史参考。

> 2026-10-19，Web Development。**玩家2026-10-19最新范围裁定**：本项目的竞技引擎调校**只研究实际进入比赛后的3D赛场引擎**，包括USER控制对CPU、CPU对CPU在场上实际比赛。**不研究、不调校MyLEAGUE日历快速模拟/Sim Engine/赛季结果数值引擎。** 旧[竞技调校路线V1](NBA2K22_COMPETITIVE_SIMULATION_CALIBRATION_ROADMAP_V1.md)中对Quick Sim的调校目标已废止；若未来要研究须由玩家另立任务。
>
> 任务优先级：**M3 GM V4先完成→这份真实赛场竞技研究的实际调校→球员/媒体世界**。Antigravity在另一条线上定位比赛设置/教练/训练等原生UI与内存，仅已证实的字段进入候选。这里是研究方案，**不批准游戏写入、不直接启动测试**。

## 一、准确目标：赛场上的篮球对抗与博弈

> 用NBA2K22 PC的实时游戏引擎，使进攻方通过正确跑位、组织、篮球意识及球员优势创造机会；防守方能够针对和反制；比赛由有差异的球员、教练策略与人机操作能力在规则下自然竞争，而不是通过放大CPU作弊加成或调整赛季Sim分数保证结果。

同时衡量三种结果：
- **场上行为自然**：空间、速度和变向、假动作、身体对抗、掩护/顺下、转移球、协防/换防/补防/内线外线弱点、体力、犯规、不同球员角色表现真实。
- **博弈反应有效**：策略A被针对后能调整为策略B，聪明的玩家和CPU会获得合理优势；重复突破、反复挡拆或固定回合套路不能永远奏效。战术不是装饰数值。
- **可玩的公平竞争**：明星有明显优势但不能永远得分，弱点真实存在，玩家不能轻松无伤横扫、AI也不能凭离谱命中/速度/抢断追分。胜负和手感合理、有随机波动，不能每场固定胜率。

**真实比分、统计数据只是赛场机制的副产物/辅助诊断**。不是用Sim Engine向现实赛季结果校准，也不为模拟出真实2022总冠军而改游戏引擎。

## 二、可调整的四个杠杆（玩家明确限定）

| 杠杆 | 具体例子 | 赛场决策意义 | 原生字段/权限状态 |
|---|---|---|---|
| **A. 全局Gameplay参数** | USER/CPU攻防成功率、投篮干扰、运动速度、持/无球加速度、对抗、犯规、耐力、AI侧全局Tendencies、意识/敏捷影响滑块 | 比赛物理/判定与整体AI行为的规则环境 | Antigravity需实机定位，旧`src/slider_manager.py`地址不认证 |
| **B. 单个球员Tendencies行为倾向** | 喜欢三分、突破、背打、传球/假动作、抢断、协防及个人Play Type（须看游戏真实字段） | 使球员按照各自真实技术倾向发挥，而不是让所有人做相同选择 | **研究对象**；按照现行项目规定，不直接授权普通经营性修改球员倾向等原始信息。若玩家明确采纳“仅竞技基线行为倾向修正”例外，需单独定规则/审批/保留原始快照；绝不顺带改OVR或单项能力 |
| **C. 原生教练体系和战术** | Playbook、POE、PreferredSystem/ActiveSystem、Freelance、RunPlayTendency、BenchDepth及可证Play Types | 为球员能力创造合理使用方式、减少战术僵化 | 项目原有教练19项默认+18项对手整体防守，写入范围遵循最新受控规程；个人分钟由AI管理 |
| **D. 实时攻防策略与调整水平** | 绕掩护、换防、协防、贴射手、封篮下、包夹、限制持球人、ACE与教练设置覆盖关系 | AI应依据球队战术/对手风格作出合理反制，能让优秀教练决策影响场上过程 | 已有指定对手整体18字段；比赛时ACE是否会覆盖预设、动态调整触发及范围必须实机观察，不能声称已有可随回合写入API |

**这些是游戏菜单/已有本局数据可以影响赛场的主要入口，不代表解锁引擎内部行为决策代码。** 未证实“单个球员的传球偏好”具体字段时不能从概念硬造偏移。训练、工资、选秀、日历模拟、调每个人数值、赛季自动结果**不属于此竞技项目的可调杠杆**。

注意“双重倾向”：`GAMEPLAY_GLOBAL_TENDENCY_SLIDER`（对USER/CPU全部阵营生效）和`PLAYER_NATIVE_TENDENCY`（某位球员原始行为偏好）必须分开，不是同一授权、同一地址或同一影响规模。球员倾向更偏“行为决策”，不是球员能力，但其长期写回仍是个体游戏数据修改，正式采用前需确认政策。

## 三、两种实际场上玩法，不研究第三种

### USER vs CPU（真人亲自打）
- 核心：玩家怎样拿到分？CPU如何调整来防守？玩家防守能否利用AI漏洞？难度等级是否产生可感知的不公平CPU加成？
- 观察用户操控/镜头/投篮方式/防守辅助如何改变实际难度；某个方案只对Broadcast镜头有效，应标注，而不能假装在2K镜头下仍公平。

### CPU vs CPU（3D场内两边均由AI操控）
- 核心：教练战术、球员倾向、攻防AI互动与真实篮球表现；观赛时能否看到双方以不同体系创造和反制优势。
- 需实机确认：这个模式的球队到底读USER或CPU一侧滑块、教练AI是否被ACE覆盖、换人和运行时策略的消费方式。

**明确排除**：`QUICK_SIM / CALENDAR_SIM / SIMULATED_GAME_STATS / SIM_ENGINE_SLIDERS`。我们已有的赛季累计统计可用于观察球员背景，但不能因为它们存在就把赛季模拟表现加入本调校验收；日历推进可能不使用3D Gameplay Sliders的实际执行路径。

## 四、来自NBA2K22玩家社区的可复用经验（非直接照抄数值）

优先2021–22 PS4/PC Current Gen，Next Gen仅供推测参考。当前资料：

1. [RES2 — All Star Current Gen Sliders，2022多轮迭代](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/nba-2k-basketball-sliders/917713-res2-2k22-all-star-current-gen-sliders/page6)：玩家围绕运动速率、侧向敏捷、防守恢复、身体接触、出手倾向和犯规持续修正；建议起点Pro/All-Star、Game Speed约60，但不同配置互相耦合，**不是本站确认“最佳全局值”**；关闭ACE/Play Physical用于保持某次教练配置的经验需要单独实机验证，可能不适合我们需要AI主动调整的博弈目标。
2. [RES2 2022-06补充](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/nba-2k-basketball-sliders/917713-res2-2k22-all-star-current-gen-sliders/page8)：注意其对速度、球员/CPU加成、投篮与防守状态不断试验，本版本不等于之前值；研究时记录帖发布日期及改动原因。
3. [Eccentric 2K22玩家讨论](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/nba-2k-basketball-sliders/917100-nba-2k22-the-eccentric-edition-realistic-ng-slider-set/page11?postcount=140)：玩家提出**先改AI投篮/进攻倾向，让出手选择自然，再改成功率**；也提教练设置与不同队表现。这是有价值的步骤经验，但主帖次世代方案、跨版本不自动成立。
4. [gu8lal8 Competitive Sliders](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/nba-2k-basketball-sliders/920479-gu8lal8-s-competitive-sliders)：作者侧重USER对CPU有可竞争性和积极针对，不以球队真实历史风格为唯一目标；提供不同难度与USER/CPU差额思路，但其偏好可能追求竞技难度而非真实NBA篮球，须分解采纳。

**重要矛盾**：一套社区滑块追求“更硬的CPU挑战”，另一套追求“接近NBA的投篮行为”，可能得到相反设置。我们的筛选原则是**先识别当下实机的具体失真及希望恢复的比赛动作，再选择机制证据、社区改法和少量候选值**。

不采用的研究目标：NBA2K22下一代Quick Sim专用参数、仅靠快速模拟得分数值、借改真实球员OVR/徽章来补救比赛AI、不经确认的一键全局“拟真包”。仓库旧`docs/10_GAME_SETTINGS_AND_SLIDERS.md`中的“权威推荐值”和旧`src/slider_manager.py`地址均应被视为**历史研究候选**。

## 五、你与模型的双向反馈：赛场观察驱动调参

**高价值反馈来自真人实际操作的可重复比赛过程。** 建议每次只记录一个明显问题，不需要录完整12分钟×整季。用户现场指出现象，比模型无感地套网络参数更可靠。典型反馈契约：

```yaml
case_id: COURT-0001
game_build: "NBA2K22_PC_CURRENT_GEN"
mode: "USER_VS_CPU"            # or CPU_VS_CPU_LIVE
game_date: "USER_OBSERVED"
teams_and_lineups: "observed"
quarter_length: "observed"
difficulty: "observed"
camera_and_control: "observed"
settings_profile_before: "PROFILE_SHA/ID"
symptom: "中锋一持球启动就像月球漫步；无球与别的动作正常"
when_and_how_to_reproduce: "actual sample and controls"
user_observation: "帧率正常；持球运球速度和加速度可能不足"
candidate_cause: "Movement ball min/max acceleration; unverified until applied"
source_basis: ["OS_CURRENT_GEN_THREADS"]
experiment: "change only the related movement family, no player OVR editing"
before_observation: "measurable movement or subjective A/B description"
after_observation: "measurable movement or subjective A/B description"
side_effects: ["guard/center gap", "contact animation", "sprint/transition"]
decision: "KEEP / REVERT / RESEARCH_MORE"
approval: "EXPLICIT_PLAYER_GATE_FOR_GAME_WRITES"
```

### 简短双向试验

1. **建立实机基线**：Antigravity读取当前UI真实值，确认地址/USER vs CPU，玩家记住当前比赛手感和主要漏洞，形成一个可撤回`COURT_PROFILE`；开始时不改变任何球员原始能力。
2. **选择一个典型对抗现象**：例如“外线掩护后CPU永远绕下让库里空位”；明确场上看到了什么、什么样才算改善。
3. **检索现有经验**：Operation Sports/PC22本世代为优先，记录他用的难度、镜头、真实/假想阵容和滑块；不要“作者说改75就全改75”。
4. **匹配多个可能根因并排序**：教练挡拆防守路线、球员出手偏好、AI协防、外围防守意识、速度/身体接触；如果原生教练字段能解决，优先不改全局。
5. **只试相关小组参数或一项策略**：两档Profile A/B，保存前后修改清单，玩家亲自打/观赛并指出行为差异；不要求无意义的几百场统计测试，避免用户为每个滑块跑完整赛事。
6. **双向反馈**：用户说“还是太慢/太容易突破/CPU不会包夹”；模型记录现象→更新假设/推荐小幅参数调整→下次再试。改善则保留，出现副作用则恢复，不把某一次失误/命中当稳定因果。
7. **阶段冻结和版本化**：保存`LIVE_COURT_PROFILE_Vx`及测试对象、效果、反例，全球Gameplay参数作为所有球队共同世界规则；GM只可改变球队合法教练/战术。避免为了打败一个对手而随时切全局难度。

### 主要问题—排查路径

| 实际场上现象 | 第一优先排查 | 第二优先排查 |
|---|---|---|
| 中锋持球启动像慢动作，帧数正常 | Ball speed/acceleration min与max、game speed及球员固有差距 | 身体对抗/控球触发动画、控球基础能力；**不改个体能力** |
| 挡拆一做就得分 | ScreenDefenseOnBall/Hedge/ICE/Switch、POE及ACE运行时覆盖 | HelpDefense/StayAttached、内线运动、防守干扰 |
| CPU见谁都往篮下冲 | AI全局Drive/Inside/Mid/3PT倾向、教练Playbook | 单人倾向原始分布、身体对抗/传球可行性 |
| CPU外线空位却不传球 | Playbook/战术调用、球员角色/Play Types | 传球/进攻意识环境、相应球员行为倾向 |
| 玩家三分异常无解 | Shot Coverage/Jump Shot Defense/距离&动作 | CPU投篮判定、协防/干扰位置、投篮方式 |
| 防守永远跟不上持球人 | 无球加速度、侧向敏捷、Body-Up与HelpDefense | 掩护后路线、单人速度差及换防设置 |
| 关键时刻AI无策略调整 | ACE是否开启/覆盖教练值，比赛AI轮换/POE是否变化 | 游戏原生是否存在可切换的策略/可用的已验证教练设置 |
| 球员体力没有实际价值 | Gameplay Fatigue Rate、实际上场/动作/体力反应 | 战术Tempo/Press等副作用、默认轮换深度 |
| 命中率合理但进攻像随机投篮 | 优先看Tendencies、Playbook与出手位置 | 成功率/防守判定不要先乱改 |

## 六、研发和权限安排

- **Antigravity**：收集比赛、球员倾向、教练、ACE的真实页面、字段范围、内存地址；确认写入后UI变化，不把UI缓冲当场上生效证据。
- **Web Development/研究**：检索玩家现象、平台适用性、给出一两个核心候选根因和反例、更新观察登记；避免无限深究一个小滑块。
- **人类玩家**：自己打一场/几个典型回合，反馈“看得见的篮球行为”，批准局部配置调整与是否保留。
- **Codex**：正式获批后将证实的菜单字段接入`LIVE_COURT_PROFILE`受控读写、恢复前值、生成before/after和版本回执；不代替GM自主决定球员能力和倾向。
- **GM V4**：在共同的Court Profile下，运用合法球队阵容、教练战术和指定对手整体防守参与竞争；不通过临时更改世界Gameplay来提高某队胜率。

## 七、范围和先决事实

1. 本竞技计划**只覆盖3D实时场上引擎**，用户与AI双方都不能轻易获胜；`Calendar Sim`、赛季整体模拟和虚拟统计分布不在本项目。
2. 玩家明确可研究四类赛场杠杆；但**“球员个人Tendency可调”尚不等于已经授权普通经营性写入所有球员原始信息**。若需合法化专项倾向调校，应由玩家单独批准明确的调整范围、批次版本、回滚与禁止能力修改条款。
3. 全局比赛参数必须双边统一、玩家批准，教练技战术要有球队差异和针对性，球员差异应保留。
4. 用户体验是主要质性信号；少量录像/赛场截图、有关回合及box score用于支持或否定某项假设；不要以“模拟一百场比赛结果”作为竞技调校的验收门槛。
5. 当前没有任何竞技配置得到本局正式校准验收，本文件不是已验证的全局参数最优方案，**不准把尚未认证的旧绝对地址直接应用于新存档**。

**下一次实施启动方式**：GM V4完成后，使用Antigravity给出的实机字段清单，先构建可撤回的真实比赛参数Profile，再以用户选出的具体赛场问题做首轮双向调试。**本研究不授权现在改变游戏或改变M3优先级。**
