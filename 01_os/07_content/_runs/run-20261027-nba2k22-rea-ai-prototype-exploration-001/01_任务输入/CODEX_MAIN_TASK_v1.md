# CODEX 主开发任务｜NBA2K22 REA · AI 机制知识与双执行后端探索原型

**任务ID：** `NBA2K22-REA-AI-PROTOTYPE-EXPLORATION-01`  
**任务性质：** `EXPLORATORY_ENGINEERING_PROTOTYPE / HUMAN_GO`（探索性工程实现，不是已验收生产模块）  
**工程唯一Owner：** Codex；可以自行探索、设计、实现、复核与持续迭代。  
**目标工作分支：** `task/nba2k22-rea-ai-mechanism-prototype-exploration-20261027`，基线从规划Run `@66d80a156711a04ef6bfcc4c81bb59eb9e25de6c` 派生。**禁止合并 master**。  
**日期：** 2026-10-27。

## 0. 先读这段——为何不是重复做规划

Human认为既有结果模型已经**足够进入探索性工程开发**；之前独立审核报告的状态为 **NOT PASSED（Human转述）**，但Human决定承担这个阶段的语义风险并**接受当前B作为初始工程原型**，不是伪称独立审核已PASS。具体记录见规划Run `03_Human审核裁决与探索原型开发例外_20261027.md`。  
本轮不要重新启动无限的需求问卷、GMA表格竞赛或七阶段形式化回填。**必须写出能运行、能展示行为合同与负例的真实工程原型，并在实际探索中修正原型。** 对影响用户核心业务意义的偏差，附证据向Human说明并提出改法。

Human给予Codex比以往**更大研究自由度**：可以自己选择研究代表参数、最有信息增益的原生符号与局部函数、探索小型补充AI机制、自己提出比B更好的领域接口或实现方案。唯一限制是要与**AI自主/AI↔AI机制、游戏原理知识或正确行为执行**直接相关，保留可复核证据与操作许可；不得扩大成全游戏扫描、玩家UI自动化、无批准Live游戏改写或生产集成。

## 1. 最终要达到的用户玩法（产品语义）

未来外部AI模型扮演 **GM、Coach、Player**，需要像熟悉NBA2K22机制的职业角色那样进行决策，并让决定落实到PC NBA2K22离线MyLEAGUE里。  
REA研究的两个同等重要结果：
1. **机制知识轨（Knowledge）**：知道游戏真正怎么处理AI角色的能力/徽章成长、教练战术、生效时机、交易评估/合法性/提交；每个字段的游戏意义、来源、限制、为何选某种行动，能够被AI角色引用/理解，而不只是输出地址与反编译。
2. **行为执行轨（Execution）**：AI发出类型化意图；对**已实证安全且具游戏AI调用路径**的业务函数，原生调用优先；没有合格原生函数时，只有证明其真实字段语义、值域、依赖、缓存、关联副作用与读回后才允许沿用实时内存写入；两条都不能成立返回`NO_SAFE_PATH`。同一动作无论走哪条路径都必须符合**同一业务后置条件**。

**只研究 AI 的自动行为和 AI 对 AI 的交互**，不研究/实现人类玩家专属徽章升级、人工教练UI作为执行主链、AI与玩家交易弹窗/编辑/确认逻辑。UI可以仅作观察证据；底层函数若同时服务Human与AI，须证明存在**游戏AI的真实调用点**及可复用上下文。

### 注意两个容易造成长期错误的控制概念
- 游戏实体名 `PLAYER` ≠ 人类控制者 `HumanController`；AI球员是研究对象。
- 外挂AI担任用户球队GM ≠ NBA2K22引擎自动将球队`HUMAN_CONTROLLED`切成`AI_CONTROLLED`；未实证前必须把`controller flag`与`AI callsite`单独标记，**不得自行改档或绕过玩家确认**。

## 2. 不可丢失的固定来源（按这个顺序获取，不要无界加载全仓库）

1. **本轮Human裁决与精确B**：规划Run `01_os/07_content/_runs/run-20261027-nba2k22-rea-native-mechanism-consensus-001/`：
   - `03_Human审核裁决与探索原型开发例外_20261027.md`
   - `03_Human机制主体边界裁决_AI与AI优先_20261027.md`
   - `03_Human最终目标补充_机制知识与双执行路径_20261027.md`
   - `NBA2K22_REA_03_完整结果模型_B_v1_RC01_待Human确认.yml`，**exact Git Blob `f711261d00b0df202906992597fdae7b895fcfb0`**；Human批准只是初始原型，不代表Native事实全对。
   - `02_evidence/证据索引_v3_原子归一化.yml`，Blob `d16ab7c91d2124d943866e3f070ab304a3963884`；五项`GAP-REA02-01..05`尚未实证闭环。
2. **Codex先前暂停的真实探索（不得改写其历史事实）**：`task/rea-development-exploration-01@b16e69727987f29bff5e2ee31ce82891102ab2d9`，`08_结论/PLANNING_HANDOFF.md`→`docs/development/REA_DEVELOPMENT_PLAYBOOK_V1.md`→`research/rea_development/README.md`→按需`SOURCE_MANIFEST.json`/raw Evidence。该代码/脚本在**旧探索分支**，可能不在本新研发分支，复用须选择性导入及说明来源，不得假定已合并。
3. **项目级协作**：`08_Domain_Applications/Antigravity_GM_Engine/docs/development/MULTI_MODEL_TASK_OWNERSHIP_AND_VERIFICATION_V2.md`（master固定基线）；Codex唯一主Owner，Antigravity只有同本地工作区**顺序交接**的有界辅助角色。
4. REA官方`morluto/rea@570abe95f2a35b5c580a5ec2fca90c33d4114bdc`及游戏构建/REA runtime版本必须在实验报告固定；先查当前可用后端，工具目录229项**不等于229项均可在Windows执行**。
5. 本仓库已有DEV07 Coach内存Reader/Writer、R04A Badge资料、R05B交易目录和相关项目规则，仅作为候选来源；不要自动把跨游戏模式攻略说成当前PC22 Native常量。

## 3. 必须形成的“能看到原型在运行”的成果

请避免只提交几十份Markdown：**必须产出一条从知识 → AI决策意图 → 后端选择 → 可验证结果的可运行演示路径**。

### D1 · 实际运行的最小垂直原型（最高优先级）
在领域目录下选用与现有代码相容的Python或TypeScript，建立一套紧凑原型：

```
MechanismKnowledgeCard/FieldSemantics
  → AI角色查询 + 适用性/证据等级过滤
  → DomainActionIntent（类型化对象，不给语言模型裸指针/地址）
  → Actor+Build+Preconditions+Authority checks
  → BackendCapability(native, memory, neither)
  → Router(native-first / validated-memory / NO_SAFE_PATH)
  → Fixture or authorized live readback → ActionReceipt
```

**最少能演示**：
- **知识可用但不能执行**：机制卡有证据/UNKNOWN，AI能合理解释，路由`NO_SAFE_PATH`，无写入。
- **Native候选已找到但上下文/许可不全**：不可越级为可调用，路由按有证Memory或阻断。
- **经验证内存后端**：仅在**自建Fixture模拟器**演示完整先决/影响对象/新读回，明确`game_target=false`；真实游戏写入必须另外获得安全实证和Human授权。
- **两个后端业务副作用不一致**：拒绝可互换宣称；保存负例回执。
- **Human玩家交易分支进入**：拒绝当成AI↔AI事务执行。
- 控制台CLI及machine-readable样例输入输出、局部测试可一条命令运行；环境不可用时至少确保纯离线Fixture运行成功。

### D2 · 三类代表机制研究成果（可以诚实地不完整）
M1 **AI球员自然徽章成长**：选1枚真实可研究候选深挖，第二枚轻对照；区分MyLEAGUE AI升级 vs Human MyCAREER积分、比赛徽章效果；写原生字段候选、真实条件是否已证、时间/导师关系、来源链和反例。  
M2 **AI教练攻防设置**：选1项真实攻防参数深挖、另一侧轻对照；拆分`AI设置决策/Native存值/消费函数/比赛实效`，旧人工Writer只作参考；若研究到安全真实AI调用路径，优先提`coach-first PoC`申请。  
M3 **AI GM↔AI GM交易**：研究AI自动评估、validator与commit，关联球员、合同、薪资、选秀权、球队记录/事件；**玩家交易对话不是目标**；结论可`FEASIBLE/INFEASIBLE/BOUNDED_UNKNOWN`但要有精确证据和下一步。  
三个档案的事实成熟度分开：指南假说L0、布局L1、静态函数L2、同模式游戏行为L3、已单独批准的真实Native调用L4。未到L3/L4绝不写“原版交易函数可用”。

### D3 · 机制知识交付（直接服务以后GM/Coach/Player）
至少为研究进度最高的一项AI机制生成**可被角色阅读的中文机制说明**（必要处英文Native字段保留），并提供机器可读卡。必须回答：机制是什么、AI什么时候会用、每个已知字段代表什么、为什么如此设置/决策、什么条件无效、真实效果是否可观察、哪些是推断/UNKNOWN、角色可读范围。其它两个代表允许有边界的部分卡，不需要杜撰缺失值。

### D4 · 工程架构可替换性
`NativeBackend`、`ValidatedMemoryBackend`及`NoSafePathBackend`为**接口/能力探针**，真正Native业务操作仅在完整实证及行动授权时可装入；**不能因为接口存在就将其标为qualified**。旧系统的交易、签约、选秀默认外部模拟路线不自动被覆盖。应留有独立回退和统一`ResultReceipt`，不以`return true`充游戏成功。

### D5 · 真实开发成果与总结
提交源代码、示例数据、CLI/demo说明、局部测试、Evidence Manifest、三机制研究记录、发生的原型修改及其理由、已知无法验证之处、下一轮建议。请提供**具体可运行命令和真实测试输出**，标记每项`REAL_GAME/STATIC_BINARY/OWNED_FIXTURE/PROJECT_GUIDE/INFERENCE`来源等级。禁止把旧52份哈希清单、原游戏EXE、模组资产或读取的用户秘密重新提交到Git。

## 4. Codex 探索自由度：充分而真实

你可以**自主**：
- 在三个核心机制中调整先后：**默认从M2教练垂直原型入手**（现有DEV07读写参考较多），但若M1或M3新证据更高信息增益，可调换，并记录理由。
- 从REA Native元数据、静态PE局部字符串/xref、Capstone/`.pdata`、开发者已有脚本、候选callsite入手；试用更高效的方法、替换现有小工具，**不要求大EXE完整Ghidra反编译**。
- 提出新机制或跨机制有价值的发现（例如AI与Human分发条件、共享业务核心、AI设置刷新/缓存、交易前后关系、AI自然成长触发周期），写入**机会发现登记**；可做有界额外概念验证，但不静默升级为新生产需求。
- 修改原型对象形态、补充新的字段关系、裁减无效设计，使AI知识真能被理解、Game action真能被核查。**须保留已批准关键语义和理由**；不必因命名/文件布局/局部小函数向Human逐一申请。
- 在首次可运行纵切完成后，自定每轮研究的`max_time/probes/bytes/failures`、按真实信息增益重排实验；终止时记录证据，不为达成“看似完整”编造数字或函数。
- 可依项目V2以**串行交接**方式让Antigravity辅助做狭小的资料/Native布局/机械提取，不能与Codex同时操作本地仓库或同一游戏进程。

**建议但不强制**：探索额外发现最多占当轮有效研究预算约20%–30%，防止任务漂移；如果确有改变产品路线的高价值发现，报告Human，由Human决定扩大范围。

## 5. 执行环境与动作权限：这次授权什么，不授权什么

**现在明确允许**：在独立研发分支进行真实代码开发、离线EXE/已存在资料静态解析、复用先前源码、Fixture测试、编译/CLI验证、文档与局部自动测试、创建草稿PR、向Human报告真实结果。  
**不要假定允许**：当前PC22真实进程Frida attach（即便脚本“只读”仍可能注入）、未知原生函数Hook或执行、实时游戏内存写入、强制变更球队控制权、推进赛季/提交交易、修改用户正式存档/游戏安装目录、关闭系统安全软件、修改master。  
需要真实游戏现场时，以一个**有界试验准入单**向Human汇报：模式/存档隔离、EXE SHA及PID重新获取、具体对象、读取/Hook/调用/写入动作、注入脚本SHA、时间/事件/字节预算、预计副作用、失败/清理与读回。Human可以一次批准整个同类场景包，避免逐字段微审批。**未经对应批准不执行**；不应把未获权限视作“必须等待就无法继续”的理由，离线可运行原型仍应交付。

**绝对不可声称**：Owned Fixture 4096写入或16 Hook事件证明游戏实际可安全执行；一字段写入证明完整交易；AI模型称自己是GM就自动具备引擎AI分发；存在CRC/RVA就已找到业务签名；对未知游戏副作用承诺自动恢复。  
**Windows环境风险**：NBA2K22可能管理员运行而Codex普通权限；不得通过不明提权或关闭防护绕过，必须在当前批准范围内核查权限与脚本。绝不记录或上传密码、令牌、私人数据。

## 6. 阶段性真实交付门（不是固定开发天数）

**M0 初始核对**：记录实际Git HEAD/worktree清洁度、游戏build/平台事实、REA工具版本、旧研究路径差异、可离线复用的组件、快速执行的最小测试。**工程可运行入口优先于拉长规划阶段**。

**M1 知识→意图→路由→回执纵切**：提供一个端到端**可运行的Fixture demo**及正负例、README命令和终端结果；要确实运行过，而不是伪造样例输出。最低展示`NO_SAFE_PATH`和一个受限、明确`fixture`的安全执行后端。

**M2 三代表专项深化**：至少给出三个源绑定研究档案，其中一个机制应具真实可查的深度研究推进；如因权限未得无法获取L3，请把有证据的L1/L2边界与下一场景实验单写明，而不是谎称完成。每个研究必须有`Human/AI`路径筛选结果和未证项。

**M3 结论与下一轮**：分别回答“AI知识现在能解释什么”“原生函数现在能执行什么”“经证实时内存现在能执行什么”“哪些被`NO_SAFE_PATH`阻断”“有哪些有价值的额外发现”，给出可回放的证据索引及建议。如果发现B原型要改，提交`B_DELTA`保留原因与Human承重裁决项。附干净提交记录/草稿PR供审核，**不发起master合并**。

**失败也是交付**：无安全游戏进程准入、某函数只属玩家UI、位宽/消费时机无法确定、交易commit可能不原子、PoC`NOT_EXECUTED`都可形成真实成果；但必须有**运行的离线原型和可复核探索档案**，不能只返回“尚需更多研究”。

## 7. Git/工作区边界和交付给谁

- **写入主线**：只在 `task/nba2k22-rea-ai-mechanism-prototype-exploration-20261027` 或它派生的开发子分支提交；不直接写`master`、原世界数据分支、原暂停Codex历史研究分支或旧REAP0冻结模型。
- **建议新增开发目录**：`08_Domain_Applications/Antigravity_GM_Engine/research/rea_ai_prototype/`（具体文件可由Codex调整），以及`docs/development/REA_AI_MECHANISM_KNOWLEDGE_*`与本Run下的Evidence/报告。若复用旧工程Reader/Writer，保持原合法接口、避免破坏旧功能，改动必须有专门原因和局部回归。
- **提交形式**：原型代码、机读合同、至少一个中文知识卡、真实离线Fixture测试回执、研究证据和总结。可提交**草稿PR**但只限review，**不可合并master**。
- **接口边界**：第二大任务统一读写层及第三大任务GM/Coach/Player完整人格不在本轮一并开发。只搭最小适配合同供后续任务对接。
- **Human回复/验收**：优先反馈“实际源是什么、运行了什么、游戏真实发生了什么、哪些未知、额外发现值不值得扩大”；不要只报文件数量/静态schema全部通过。

## 8. Codex可先用的真实事实基线

旧Codex REA部分探索归档：`13`个元数据结构/部分当前游戏字节片段、`9`个growth结构候选、`4096`条自建数据写入/恢复、`16`个自建ABI Trace事件。以上只证明相应范围的工具能力。旧流程四次大EXE Ghidra超时；不应无新定位仅增加timeout。

本任务允许尝试新路线、从中发现有价值的新机制；但每个游戏机制结论都要有来源范围（PC22 offline MyLEAGUE AI执行链）、证据成熟度、能推理/不能执行的状态。**没有真实游戏验证时可以明确说UNKNOWN。**

---

**正式派单指令**：Codex，作为唯一主工程Owner，从这个新探索分支开始真实工程开发。**先完成可运行原型和真实证据整理，再深挖最有信息增益的AI机制**。准许合理创新和有证据的B_DELTA；禁止无许可真实进程注入、游戏修改、原生函数调用或master合并。不要将独立审核“未通过”改写成“通过”：Human当前是以“探索原型的工程例外”明确授权你启动。