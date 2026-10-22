# NBA2K22 GM Engine — 游戏机制研究先行的开发规范 V1

日期：2026-10-20，2026-10-20玩家修订：**游戏机制研究允许且鼓励参考次世代资料；开发时优先搜索社区、游戏攻略和官方游戏手册，理解机制之后再编码。** 研究是开发业务理解的前置步骤，不是对次世代信息的默认排斥。此规范与[开发边界和验证规则](DEVELOPMENT_BOUNDARIES_AND_VALIDATION_POLICY.md)并行：**游戏机制相关任务必须研究先行；纯代码/Git任务直接处理，不强行搜索；原有批准、适量验证与TASK_CLOSED规则不变。**

## 1. 触发规则：什么任务必须先了解游戏

**要求先研究**：涉及NBA2K22 MyLEAGUE（PC本世代）游戏功能语义、玩家菜单/枚举/原生战术及其名称、战术手册、PlayTypes、教练ACE与对位、Gameplay滑块、训练、疲劳与伤病、员工作用、经营财政、合同/选秀、赛场AI调用与数据采集字段等。特别是开发者要回答「某字段干什么」「有哪些真实可选项」「它为何影响场上行为」「这个按钮或操作如何生效」时，**禁止只凭内存字段名、编程常识或模型想象判断**。

**不要求额外外部搜索**：纯Git冲突解决、已有合同明确的机械代码修改、文件路径/拼写Bug、旧代码直接可判定的确定性逻辑问题。需要理解NBA2K行为的局部Bug仍应先查适量相关资料。**先判断是否存在游戏机制知识缺口；没有就直接编码**，避免形式主义的冗长检索。

### 每次触发的最短研究路径

1. **先读本仓库已有机制知识与先前证据**：`docs/`、`docs/development_research/`、`docs/research/`、DEV23/DEV24/DEV28、`web_gm/knowledge/`、`config/state_io_native/`、`config/source_catalog.json`；不要重复调研已有认证来源。
2. **先搜索社区和优秀玩家攻略**：Operation Sports NBA2K22/MyLEAGUE/slider/roster/tendency/playbook、Reddit r/NBA2k、Coach2K、玩家制作的战术/经营指南及有根据的NBA真实篮球战术研究。优先提炼玩家已经确认的功能逻辑、菜单使用流程、典型设置、相互作用和实战问题；有争议时比较不同来源及原帖修订，注明平台、版本和模式。不让玩家重新解释已有公开攻略的基础知识，也不把社区感受伪装成官方公式。
3. **并行查官方手册和开发者说明核对机制**：NBA2K22的2K官方手册、开发者Courtside Report、官方说明（例如 https://2k.com/game-manuals/ 和 https://support.2k.com/hc/en-us/articles/203972113-Digital-Copies-of-2K-Manuals ），用于确认游戏设计、菜单语义和明确的限制；查不到也不能阻止利用可验证的社区玩法知识。**官方、社区和攻略均是重要输入，不要求形式上的固定搜索次数或文献数量。**
4. **对照这台游戏及项目原生事实**：静态游戏文件/CRC、真实菜单/截图、Antigravity定向只读内存、对象身份/值域、原有M0同批SQLite与已认证enum；构造可被GM查询的选项、意义和真实业务动作。社区知识能提供用途推理，但**不自动证明某一CRC的native_category_id/内存地址、游戏写入或实际效果**。
5. **适量实现和直接相关检查**：把正确知识联到原有Registry/DTO/M0/DEV14/业务执行器，不能发明第二套架构；按本次用户授权的最小测试范围检查。产物中标明已验证与UNKNOWN；游戏写入需用户逐项批准。

**查不到官方手册并不妨碍继续**：记录官方来源缺失，使用社区有来源的资料与已读原生事实逐级建立理解，未认证的物理内存细节保持UNKNOWN；不要要求用户先逐一口述网上已有的信息。

## 2. 多世代机制资料可用：理解可迁移，技术接口按PC实机落地

- 最终运行环境仍是**NBA2K22 PC本世代 MyLEAGUE**，但**同年次世代PS5/Xbox Series的MyNBA资料是高价值机制参考，主动搜索并利用，而不是排除**。两代游戏在篮球战术、教练调度、球员决策、合同、球队经营等方面通常存在大量共通概念；次世代开发者说明甚至可能比PC社区更系统地解释设计目的。NBA2K20/21/23及MyTEAM/MyCAREER的同底层篮球玩法也可补充研究，适用性按具体问题判断。
- **两层证据分开**：①篮球/经营机制的概念、设计意图、战术原理和玩家使用经验可先跨平台学习并用于提出GM模型候选；②当前PC本世代真实**菜单是否存在、选项名称/数值、数据类型、CRC、偏移、原生对象、执行效果、生命周期**仍应核对项目字典/社区PC实例/Antigravity实机来源。不要将同年次世代独有的UI与具体二进制结构不加验证地复制为PC可执行接口。
- 具体示例：[2K官方2021 MyNBA MySTAFF/Prep Hub/Conditional Coaching说明](https://newsroom.2k.com/news/nbar-2k22-adds-new-features-to-mynba-for-playstation-5-and-xbox-series-xs-consoles)针对PS5/Xbox Series X|S；可以借其理解球队员工建设与比赛准备的机制思路，**但不能仅凭此确认PC版本也提供完全相同的岗位、菜单或内存实现**。差异仅影响相应功能的实机落地，不自动否定其篮球或经营价值。
- 游戏内显示值与最终执行机制分开：`NATIVE_UI_OBSERVED`、`RUNTIME_READ_VERIFIED`、`WRITE_READBACK_VERIFIED`、`SAVE_RELOAD_VERIFIED`、`LIVE_3D_EFFECT_OBSERVED`要分别登记；2D战术预览是计划描述，不等于3D比赛AI一定调用。

## 3. 战术与经营业务的具体研究范式

以玩家证实的`'95 FIST 15 SIDE`为例：
- 静态CRC、原生战术名字：共享池已有`0x79215B33`与`STATIC_LABEL_CRC_JOIN`；
- 球员实际说明：`'95`1995年代版本、`FIST`挡拆、`15`1号位持球/5号位掩护、`SIDE`侧翼，属于`PLAYER_REPORTED_UI`；
- 游戏战术目录中的12类（单打、挡拆、外弹中投、外弹三分、挡拆选项、低位背身、高位背身、后卫背身、中投、三分、手递手、切入）与球员4槽的16个PlayType枚举**是两套信息**，不预填未认证native ID；
- 从优秀社区资料可研究Play Discipline、Run Plays、Shot/Touches、PlayTypes、Playbook相互作用，如[OS NBA2K22 Useful Findings](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/917203-nba-2k22-useful-findings)，但无需编造游戏内部固定算法、绝对胜率或每次必定跑完战术；
- 若找不到游戏战术类型内存表，先让Antigravity从真实菜单/类型筛选和当前对象调查；确实需要时**可请求玩家提供截图**，即使需几十张也按类型有界批次征集。到需玩家介入处完成可交付部分并结束TASK_CLOSED，不保留Codex活跃等待会话。

其它业务按此模型：先解释球员/球队经营上为什么需要这项机制，再找其原生可读可写来源及受控业务执行路径；不以“找到了地址”冒充GM已能有效经营。

## 4. 证据结构与交付标准

机制性新增解释至少留简短可追溯记录（可放现有文档，避免无意义新文件）：

```yaml
topic: "NBA2K22 PC MyLEAGUE"
question: "在实际游戏中这一参数或操作解决什么篮球/经营问题"
official_sources:
  - url: "仅真实查到的官方相关网页/手册"
    platform_and_mode: "EXPLICIT; PC/NextGen/both; mechanism transferable vs implementation unverified"
community_sources:
  - url: "真实社区资料，含作者/日期/适用版本"
    finding: "精确记录支持的结论及限制"
repo_evidence:
  - path: "现有README/registry/源码/内存/SQLite中真实来源"
verified_game_fact: "只有实际证实的本机字段/枚举/菜单"
interpretation: "篮球作用与适用条件"
unresolved: ["UNKNOWN具体关系/效果"]
planned_use: "对GM可检索功能、对应来源/操作"
```

**关键区别**：`OFFICIAL_VERSION_SPECIFIC`、`COMMUNITY_REPORTED`、`PLAYER_REPORTED_UI`、`CROSS_GENERATION_MECHANICS_REFERENCE`、`PE_STATIC_MATCH`、`RUNTIME_NATIVE_VERIFIED`、`GM_MODEL_INFERENCE`、`UNKNOWN`；次世代资料可为机制设计提供重要依据，但不能凭概念参考直接认证PC内存地址/菜单。只引用真正相关且已查看的来源，不设刚性的资料篇数；纯代码修改不重新搜网。

**完成条件**：开发者能够说清（1）游戏中功能含义和限制，（2）当前PC22可用选项/来源及UNKNOWN，（3）GM能如何选择使用，（4）是否需要玩家审批和原生执行，（5）怎样读回。已知源有缺口应在当前授权内合理退化，不自动增加设计范围或大量验证。

## 5. 与既有开发政策的关系

- 开发期仍以实现优先；研究是**必要的业务理解动作**，不是额外实现功能、测试任务、全面逆向工程或自动外部联网许可。
- 玩家此前规定「新增设计/更多测试必须询问批准」。本规则**已正式授权开发任务中为相关游戏机制做适量资料检索并记录依据**，不需就每一次搜索重复申请；但后续实机游戏写入、数据发布、超范围设计/测试仍按原权限。
- 当前PR #12只需Git冲突解决，不以本规范扩展其代码范围；DEV28本来就是机制透明化计划，之后各独立工作包执行时必须遵循**先社区/攻略/官方资料理解机制，再核对项目技术事实，最后实现**的流程。
- 凡必须玩家提供UI截图、文字说明或审批：完成所有当前能完成的部分，报告精确阻断后`TASK_CLOSED`，下次用户新启动任务继续；绝不保留`PAUSED/WAITING`消耗额度。
