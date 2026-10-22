# DEV12 — 战术手册、球员四槽、个人倾向及逐人防守的Codex交接 V1

> **2026-10-19 玩家最新决定，本V1执行分工已废止**：原A/B/C/D四期**全部由Antigravity负责开发**，而非Codex。技术背景与篮球问题可继续参考，但不要把本文件直接发给Codex执行，不要开发第二套教练读写系统。请使用唯一现行实施任务：[DEV12 V2 — ANTIGRAVITY_TACTICAL_ECOSYSTEM_AND_GM_REASONING](DEV_20261019_12_V2_ANTIGRAVITY_TACTICAL_ECOSYSTEM_AND_GM_REASONING.md)。核心验收是**战术机制关联、球员行为解释与GM如何判断内部改善/交易**，不只是可写内存地址。仍需玩家审批正式游戏写入，普通能力值不可修改。

2026-10-19，Web Development；详细机制依据：[NBA2K22战术生态与球员行为研究V1](../research/NBA2K22_TACTICAL_ECOSYSTEM_AND_PLAYER_BEHAVIOR_RESEARCH_V1.md)。**这是Codex后续的工程准备文档，不是已经实现或授权在游戏写入。** M系列实际完成并得到玩家安排之后再开始。Antigravity负责另外的原生训练/恢复/疲劳发现，等待其后续报告。

## 0. 项目不能改变的原则

- 网页GM负责30队分析：教练属性/球队采用体系/战术本/进攻4槽/个体Tendencies/个人防守及人员能力共同决定篮球表现，缺口才驱动交易；Codex负责读取、确定性校验、批准后内存执行。
- **用户新增许可：球员原生Tendencies可以作为赛前战术适应设置被GM提出修改**，由玩家逐项批准再实际执行。个人战术Play Types可作为战术角色设置另立动作。**仍禁止普通经营性直接增加球员原始能力/潜力/徽章/身高/身体速度、改历史表现。** 历史重力例外单独审批。
- ACE 真实比赛一直ON。不要开发外部实时比赛AI、不要锁个人分钟、不要改CalendarSim内置引擎滑块。研究赛前配置对两种比赛路径的影响时，必须区分已证/未知。
- 不重复现有COACH_DEFAULT 19项、VS_OPPONENT_DEFENSE OVERALL 18项写入器；保留已有playbook整本选择、四Freelance、原生枚举、球队/球员身份与CAS条件恢复。

## A. 首先补齐只读来源（先有数据，后有策略）

| 模块 | 必须的原生观测 | 预期最小GM输出 | 未经观测时 |
|---|---|---|---|
| A1 PLAYER_PLAY_TYPES | 个人4个按序槽位、各自真实type枚举、可空条件；Play Initiator（若存在） | 谁以何种方式被叫战术 | UNKNOWN，不以0填满 |
| A2 PLAYER_NATIVE_TENDENCIES | Touches、Shot、Drive、Iso、PlayDiscipline、Close Shot、Inside/Mid/3PT、Post/无球等已找到的原生字段与当前raw | 战术执行者的行为偏向，和55属性明确分开 | UNKNOWN，不臆测地址 |
| A3 PLAYBOOK_CONTENTS | 当前加载PlaybookID下全部具体原生PlayID、所属PlayType、顺序、已知发起/受益者及空间角色（若可定位） | 核对每名球员4槽的实际候选战术 | 只有PlaybookID则标COVERAGE_UNKNOWN |
| A4 MATCHUP_PERSONAL | 现有owner对opponent的整体18字段对应真实有效matchup记录，关联指定opponent_player_id及defender_id，逐人各字段raw与个人/整体继承关系 | 区分守库里/汤普森/非射手的不同防守 | 目前只能OVERALL，个人暂UNKNOWN |
| A5 COACH_ATTRIBUTES | 本机PC版教练原始攻防/发展/体系熟练度若存在、在队员工关系、合同，适配评级真实观测 | 了解教练选择及体系匹配的来源 | 不把PS5-only 17人MySTAFF/PrepHub冒充PC |
| A6 TEAM_RESULTS | 同批已证球员/球队出手结构、效率、对位/位置和球队赛季累计数据 | 对经营效果的事后证据 | 无原生逐回合源时不虚构 |

来源验证：同一career/save、snapshot、batch、player_id/team_id、当前教练指针、原生enum/dictionary；沿已建立的full_verified_v1整批发布流程纳入新来源。**不为这些项分别制造半套生产采集。** 可以在Codex隔离环境做字段观察，不在正式局未经批准修改。

## B. GM离线战术兼容性诊断器（确定性判断，不编赢球权重）

每个队和每人给出的只读结果：
1. 体系（Preferred/Active，玩家真正采用的阵容与教练适配）+ 赛前POE+Freelance+RunPlayTendency；
2. 每名球员4个Play Types次序，逐槽与当前战术手册的真实同type PlayID匹配；
3. 如果槽非空且Playbook无该Type，则STATIC_PLAY_TYPE_UNSERVED；如果type匹配但内生接球位置/谁执行未知，则TYPE_MATCHED_ONLY；若已证发起/目标角色不符合则ROLE_OR_TARGET_MISMATCH；Book内部读取不完整则COVERAGE_UNKNOWN；
4. Touch/Shot/Iso/Close/Drive/PlayDiscipline等倾向，以及现有55项只读能力是否可以执行此角色。例如三分投得准≠会跑动战术、不会处理球≈不能担任频繁被夹的发起者；
5. 针对不同对手单独的外线射手限制、换防与挡拆、弱侧补防、低位/中锋对位、协防牺牲项；个体设置缺时不能从OVERALL伪造；
6. 给出HOLD、内部改Playbook、调整4槽、调整Tendency、改逐人防守、换教练、交易/签约的可比较备选，明确改善什么、牺牲什么、为何“现有阵容还不能完成”；
7. 所有来源与判断分为PROJECT_VERIFIED、2K22_COMMUNITY、NBA_REAL、INFERRED、UNKNOWN；**不能为GM给假“战术适配总评分”或从社区50值推算必然战术频率**。

工程上建议一个可复用的TACTICAL_FIT_REPORT，通过gm_data_query或现有只读Workbench按队查询。首批可只做一队GSW与一队play type未匹配队的字段，逐项扩到30队，避免重复跑已有19/18教练原生测试。

## C. 玩家批准后才可执行的写入接口

| 操作类别 | 输入和合法性 | 不得做 |
|---|---|---|
| PLAYER_PLAY_TYPE_CHANGE | 真实player身份与球队+4槽原值和目标type枚举+新手册支持检查；保持顺序；重复Type是否合法以PC原生行为判断 | 把4槽当4套独立固定战术或猜出场概率 |
| PLAYER_TENDENCY_CHANGE | 单人单个或同一组真正可证Tendency字段，前后raw、合法enum/范围、篮球理由、具体玩家审批 | 改能力值、潜力、徽章、伤病、动画或编辑不在清单的裸字节 |
| PLAYBOOK_CONTENT_CHANGE | 当前本BookPlayID真实清单、增删顺序、原生类型和内部约束，支持玩家批准的整体战术配置 | 只会换PlaybookID就谎称能精确增删本内战术 |
| INDIVIDUAL_MATCHUP_DEFENSE_CHANGE | owner_team_id + opponent_team_id + opponent_player_id + assigned_defender_id + 原生字段/enum；读取本人条目的前值 | 用18字段OVERALL批次冒充逐人防守；把其他对位记录一起覆盖 |

**重要冲突**：当前OVERALL执行器会对特定owner/opponent全部有效Matchup条目应用同值。在支持个人覆盖后，必须明确OVERALL先应用、再合并个人例外，或同一事务以明确优先级一次性提交；不允许后一笔普通整体变更无声清除已批准的个别防守。UI原生“整体与个人”继承关系要实机研究，不能擅自发明协议。

所有执行沿已有审批协议：完整career+batch+decision+version+action IDs+digest、身份/CAS前值保护、读回、只在本执行器刚写值仍相同时条件回滚、禁止跨存档套地址。球员转会/换帅/换战术书后，原倾向和PlayType与新球队体系的匹配结论自动失效，需要重新分析和审批；不自动将旧队专用倾向永久解释为球员天性。

## D. GM篮球知识与交易触发策略

输入卡片维度：
- OffensiveIdentity：Motion/Split Cut、Spread PnR、Horns/High Post、DHO、Low Post、Transition、Five Out等；
- RoleProfile：primary creator、offball shooter、secondary attacker、roller/popper、short-roll passer、defensive stopper、rim protector、help/tag、rebounder；
- Counterplay：Drop时的pull-up与射手远投；Blitz时的short-roll与弱侧处理；Switch时的错位攻击但不能全员站着看；TopLock时的backdoor。**这是篮球合理候选，不保证游戏内某PlayID一定实现**；
- DefenseProfile：根据特定对手球员的投射、突破、掩护和接球威胁选择Pressure/Screen/Hedge/Tag，注明自己牺牲的角落空间；
- MarketNeed：角色缺口→当前球员属性读数/战术兼容证据→内部调整失败或机会成本太高→寻找市场候选→M1资金/合同→双边议价（M3）；
- TacticalCase：2022勇士Curry/Thompson/Green/Looney/Wiggins联合攻防，不要把Wiggins Game5爆发误写成Curry整个系列被锁死，NBA官方G5 Curry16pts、Wiggins26pts13reb、Wiggins该场季后赛最高用球率26.4%，现实真正需要的是多点回应和针对防守薄弱处。

GM输出至少明确：赢球哲学和球员构成、赛前战术/个人设置、对手可怎样限制本队、备选回应、阵容中谁能够执行/谁不能、是否真的要交易，以及执行能力是否具备。不生成只会自证已有阵容合理的形容词。

## E. 分期与完成标准

**A（信息）**：先有个人4槽+原生Playbook具体PlayID/Type目录+少量重要Tendency+个人防守快照，能读到真实队员/原生值，未找到的明确UNKNOWN。

**B（GM诊断）**：从事实发现某个球员play type没被本书覆盖或角色受益者错位，给出内部改善对照，不凭空设数值。不同于篮球教科书讨论，要具体到当前游戏已有实际战术。

**C（写入）**：上述获批的动作按原生身份和CAS可执行、读回、条件回滚，不能触碰能力值；与已有19+18接口不冲突；不存在原生支持的具体项目时保留BLOCKED。

**D（训练联动）**：只有Antigravity之后给出真实训练/恢复/疲劳/导师字段及行为后，才把这些角色所需训练方向纳入GM；无需为了本阶段重写训练系统。

禁止为开发阶段增加大量无关游戏测试。当前M3/M4任务和生产数据保持原状态；本Dev只代表下一阶段的可实施交接。
