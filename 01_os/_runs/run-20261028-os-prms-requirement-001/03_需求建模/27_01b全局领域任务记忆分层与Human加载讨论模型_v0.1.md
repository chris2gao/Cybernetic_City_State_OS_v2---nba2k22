# OS-PRMS 01b · OS全局/领域生态/任务系列记忆分类与Human选择加载模型 v0.1

- 任务：os-prms-global-persistent-role-memory-20261028-001
- 本文性质：**新Human目标的需求模型候选和讨论追问实例（DRAFT_IN_DISCUSSION）**；不是改写Q1–Q51，不是已获正式Human批准的完整A，也不是运行时实现。
- 讨论机制来源：01_os/03_mechanisms/stage_collaborative_deliberation/方法论_v1.md、阶段profiles_v1.yml、激活状态_v1.yml（active_dormant）。
- 触发：Human在01b明确要求细化“上下文记忆都记录什么”，特别提出OS全局机制、08领域全局机制、活动任务链/已完成任务、经验提炼升级、按角色询问Human加载并验证恢复。命中stage01「Human_requests_collaborative_requirement_modeling」「load_bearing_requirement_gap_exists」。
- 讨论路由：full（新增承重分类与加载审批语义）；讨论实例仅保存于本Run，不修改canonical机制状态。
- 现行基线：OS-PRMS-A0-v1-RC01已Human批准；01b Q20–Q51单项已裁决；OS-PRMS-A-v1-RC01为CANDIDATE_PENDING_HUMAN；RES-001..020为候选。基础文档25/26为独立审查增量。
- 主要原件：AGENTS.md、01_os/README.md、01_os/开发入口与单窗口任务规范_v1.md、08_Domain_Applications/AGENTS.md、08_Domain_Applications/domain.yml、01_os/03_mechanisms/context_management/方法论_v1.md、工作集与归档契约_v1.yml、01_os/05_registry/README.md、RES-017..020与RC01入口。
- 新Human原始需求：本轮对话用户文字，为Human新目标信源；不存在单独签名URI。本次仅做需求讨论并在已批准规划Run中归档，不授予工程/主干变更。

## 1. 核心问题与成功义务

每个OS仓库有通用OS机制及各自领域生态。长期记忆要保存哪些对象、让新窗口在最小可验证启动后发现哪些机制、按什么触发加载活动任务、何时将已完成任务归档、怎样把经验以正式升级门提升为全局知识，并可由Human决定本窗口具体恢复内容。

**成功判据**：
1. 新窗口能完整发现G1 OS机制与本仓G2领域全局机制，报告版本、范围、缺口，未加载正文不得说“已完整理解”。
2. 任务T1只在当前任务链连续性或Human明确点名时参与上下文；系列任务真正终止后不再默认装配。
3. T2完整归档并可检索，经验提炼保留证据、适用范围、反证；经正式发布才进入G1或G2。
4. Human看到角色相关、可解释的加载选择，决定本会话的合法范围；恢复可验证版本、已加载清单、遗漏、预算、stale与任务授权。
5. 固定OS安全启动不被“拒绝加载可选长期记忆”绕过；全域读权限Q22=C与本次选择注入的范围不同，不能虚构访问隔离。
6. 同一结构适用于NBA2K22及数学、英语、日常管理、人际关系等其他领域OS仓库；各仓的领域权威归属及具体内容独立。

## 2. 两轴分类，不得混淆

**内容轴/权限轴（本轮候选）**
- B0: 强制OS启动与安全/权威约束。对当前工作有效的最小正式规范、权限、Human任务输入、source SHA、Boot/Registry；不是可任意关闭的“历史记忆包”。
- G1: OS全局机制生态。Workflow、上下文管理、模型路由、通信、任务编排、协同讨论、验证/发布门、全局技能/工具以及正式已提升经验。要有统一可验证catalog，具体全局加载**深度**待Human Q52。
- G2: 本仓特色内容全局机制生态。例如本仓08_Domain_Applications/领域规则、篮球世界数据、Native/Reader、REA、游戏知识资料库、OS管理下的外挂开发机制；**只是目录类别候选，不表示这些内容已全部审核发布或自动激活**。其他仓按domain.yml与正式注册源解析，不假定目录皆命名08，也不硬编码某游戏术语。
- T1: 当前正在执行或尚未关闭的任务、系列任务链。包含任务/series ID、目标、阶段、依赖、Human版本、已完成节点、未决、checkpoint、证据与下一步。非当前任务或未点名时不默认加载；关联系列在尚未完结时对同系列接任保持可发现。
- T2: 已完成/终止任务与历史，保存于权威GitHub并可索引/加宽/检索。默认不进入新任务上下文；被Human指定、证据核验或回顾时可按需加载。
- K1: 从T1/T2提炼的候选经验卡，保留source/evidence/适用范围/置信及反证；独立于原事件。
- K2: 正式提升的跨任务OS知识/领域知识/机制。必须有目标owner、review、发布与版本回执；不能因提炼质量高自动取得master或canonical变更授权。

**读取深度轴（继承已建模的RES-017）**
- L0=强制Boot/角色与任务入口；L1=精简有效CURRENT；L2=目录/主题概要；L3=精确事件/证据；L4=完整历史/审计。
- 例：G2领域机制在某会话可L2浏览，再L3读原始机制规范；T1可L1复原当前状态，必要时L3展开Human裁决。保存全面≠默认注入全面；全量复制Q42=A不允许只复制概要。

## 3. 逻辑记录对象（新增候选视图，暂不改变20个RES计数）

| 类型 | 最小逻辑字段或约束 | 来源/关联 |
|---|---|---|
| ContextDomainDescriptor | domain_id、repo_ref、domain_registry_refs、authority_version、scope、global_mechanism_catalog_ref、status | 本仓domain.yml及每仓独立领域目录 |
| GlobalMechanismCatalog | catalog_id、layer(G1/G2)、repository、scope、catalog_version、built_from_commit、coverage、count、missing_count、items | 不能将扫描到的任意08文件自动定义为全局机制 |
| GlobalMechanismEntry | mechanism_id、category、title、purpose、canonical_refs、trigger、required_by_roles、priority、source_version、validity、loading_levels、conflicts/dependencies | 是否正式全局/应加载取决于规则/注册与人类确认 |
| TaskSeriesCurrent | series_id、members(task_id)、owner_role、scope、goal、open/terminal状态、milestone_refs、dependency_refs、confirmed_decision_refs、blocking_refs、checkpoint、source_sha | 系列未关闭时提供可选恢复入口；具体状态需继承OS现有合法lifecycle，而非臆造生命周期 |
| TaskMemoryManifest | task_id、series_ref?、stage、effective_current、result_refs、evidence_refs、experience_refs、archive_state、source_commit | 不等同任务所有内容默认加载 |
| ExperiencePromotionCandidate | experience_id、origin_task_refs、source_evidence、applicability、proposed_target(G1/G2)、diff/proposal、review_state、risk、authority | 仅候选；正式升级遵守OS protected publishing规范 |
| LoadSelectionProposal | session_ref、role_id、current_task、G1/G2/T1/T2可选项、mandatory_B0、recommended_scope、source_versions、estimated_cost、reason、available_tools | 新窗口可向Human说明“加载什么与为什么”；Human未选不可自行伪称批准 |
| HumanLoadDecision | decision_id、scope、selected_layers_and_entries、actor、context_version、decision_time、valid_for_session、exceptions | Human同意的是**加载范围**而非执行权限/技术可达性；可能允许复用当前明确任务授权，具体决策见Q53 |
| ContextRecoveryReceipt | request/decision refs、effective_role/task、loaded_entry_refs和SHA、omitted/excluded、stale/partial、mandatory_present、budget、evidence_verification、owner_state、status | 回执区别“已发现”“已选择”“已读取”“已验证”“已恢复” |

物理目录、字段编码、检索算法与缓存留02/03；与RoleMemoryRoot、IndexManifest、SummaryCard、ContextAssemblyReceipt尽可能组合，避免第二套真相来源与冗余实体数。

## 4. 初步提议的生命周期与触发模型（待讨论，非最终决定）

**保存：** 所有长期事实/记录按Q14=A持续留GitHub权威原件。任务完成并不删历史；closed task从默认上下文退场，仍可准确查询。经验候选与原始记录分开，源变更传播stale。

**G1/G2：** 每仓需要全局机制权威目录及可验证覆盖；“全局加载”精确定义是本次Human讨论的优先决策Q52，禁止预先替Human解释为“全仓全文注入”或“仅发现索引”之一。自动发现目录不代表自动信任新文件、自动激活机制或自动发布核心规则。

**T1：** 当前Human任务、同系列尚未完成工作中与角色职责相关的必要依赖提供可发现性。活动任务链是否默认装配/每窗口提示需后续Q53裁决，不能把所有未完成run都加载。Human点名的历史任务/系列触发按需装配；关闭的任务T2默认退出，相关经验通过K1/K2流入G层。

**新窗口：** 先执行现有OS强制最小启动与安全门，再根据role、repo/domain、task及未结束series列出可加载层及具体版本；向Human提出有理由的选择；获准后装配G1/G2及指定T1、其他历史按需；输出恢复回执。不能因为未选择长期记忆包，违反AGENTS.md现行always-on启动规范。具体“每个窗口都问一次”还是可复用任务/角色级批准，留Q53。

**正式升级：** 任务完成后提炼经验/工具改良建议，分别判断适合G1/G2、不适合或尚需证据；先新版本候选与影响分析，再按既有OS Human/评审/发布门实施，不能绕过master保护、权限和测试。REA可作为潜在G1升级案例，但不声称已完成升级。

## 5. 可观察接口与异常（需求目标）

- discover_context_layers(role, repository, task): B0+G1/G2/T1可选候选、版本/覆盖、缺口与理由。
- propose_load_selection(role, task, budget): mandatory B0、建议G1/G2、关联活动series与摘要、成本/工具可达性。
- record_human_load_choice(decision, expected_catalog_version): 记录Human本次选择、有效范围与版本；来源变化或无法验证不静默重用旧许可。
- assemble_approved_context(selection): 按L0–L4读取真实版本与任务必要内容；budget不足不能删除强制安全条件。
- verify_context_recovery(receipt): 检查role/task/OS规范/领域机制/series进度、证据、缺失项、stale、实际加载清单和预算，输出READY / PARTIAL / BLOCKED等。
- close_task_series(series): 只有现有OS真实closeout门成功且Human/任务作用域有效，才退出默认活动集合；不能因最后一个聊天窗口关闭便认定任务完结。
- promote_experience(candidate): 先候选再评审/批准/发布；实施具体Git操作需另有授权。本轮不运行。

**故障不变量**：
- GitHub不可用/来源缺失：不得冒称已加载最新全局机制；可提供Human上传已确认恢复包但标注可核实范围。
- 目录partial/过滤：不得声称“没有相关机制”；提供excluded/missing与加宽路径。
- Human拒绝某可选记忆但当前任务真正需要它：报告依赖缺口、提示选择变更或限制任务，不能偷偷注入。
- 正式权限和任务授权不随上下文复制或Human“同意加载”扩大；独立审核默认不灌开发者意见，Q22=C技术读取开放的残余风险仍显示。
- G1/G2机制的“加载”与“激活/执行”和“升级/发布”为不同状态。

## 6. 本轮full讨论的承重缺口与排序

| inquiry | schema/缺口类型 | 为什么承重 | 处置/下一步 |
|---|---|---|---|
| Q52 (本轮首先询问) | G1/G2 global load语义；terminology_ambiguity + goal-success scope | 决定默认token预算、是否能保证全局正文可用、验收与权限 | Human选A/B/C并描述保留意见；未答前本部分为proposed |
| Q53 (后续) | 新窗口选择批准粒度；authority_and_confirmation_requirements | 每会话交互与可复用批准涉及易用性/过期风险 | 等Q52后针对实际模型提问，不机械凑轮次 |
| Q54 (按需) | 活动任务系列自动推荐与完结判断；unknown semantic | 影响跨窗口连续性与历史退场 | 先继承既有OS closeout，必要时请Human |
| Q55 (按需) | 已完成任务经验提炼和升级门；potential policy conflict | Human希望“直接升级”，现有master门禁不能省 | 先复用现有受保护发布；若Human想自动越权升级需单独决定 |

其余字段粒度/接口命名/存储路径是ordinary local choice或02/03证据，不给Human制造微审批。

### Q52 候选选项（尚未确认）

**问题：您说“OS机制和领域机制都是全局加载”，对于每个新窗口，这一词应被定义成哪一种可验收的加载量？**

- **A · 所有机制原文全量默认注入**：经Human选择启用G1/G2后，将各层正式全局机制文件正文一次性全部送入模型上下文；不足预算则阻断。优点是文本全在当次上下文，成本高且容易被历史噪声影响。
- **B · 全局完整发现 + 分层精确加载（规划模型建议）**：G1/G2每个机制的身份、版本、适用性、内容索引和高密度概要先全部可见；本次角色/任务要求的强制机制正文完整加载，其他机制的正文按需展开。必须报告哪些只是目录/概要、哪些已读原文，并支持Human明确要求全部展开。
- **C · 仅先发现目录，所有机制正文由Human逐个选择**：除B0强制启动外，G1/G2仅加载机制清单，正文均通过新窗口二次选择再读。交互更多，最小启动更轻，但可能缺少足够上下文以主动判断需要哪些机制。

上述三方案均保留旧OS始终适用的强制启动与正式授权（B0），不会擅自把Q22=C开放读取改成技术隔离，Q42=A全量持久复制不受单次上下文加载影响。

## 7. 拟验收场景（全部NOT_RUN）

SC-GL-01：在NBA2K22新GPT窗口，发现OS核心G1及NBA2K22领域G2并按Human选择恢复，准确指出哪些已读原件/哪些仅有摘要；载入证据及SHA可核对。
SC-GL-02：数学教学OS仓库同样发现OS G1和数学领域G2，而不是加载2K资料；全部物理路径由该仓实际注册/领域描述决定。
SC-GL-03：活动系列任务经多个窗口继续，恢复已完成里程碑、未决和有效Human约束；不自动载入不相关未完成run。
SC-GL-04：任务系列正式完成后退场，历史按需可查；经验经候选审核才出现在G1/G2，不能由任务结束直接自动改核心。
SC-GL-05：用户拒绝可选层，但该层对当前任务为必要依赖；不得偷偷加载或假装有足够上下文，回执BLOCKED/PARTIAL。
SC-GL-06：GitHub目录或source变更，旧概要标stale，必要时重新核验；局部检索无命中不得宣称全仓不存在。
SC-GL-07：独立审核默认输入避免预灌执行者推断，仍披露同仓库Q22=C自律访问的不可技术保证边界。
SC-GL-08：跨岗位完整复制仍逐项复制源长期内容；上下文只选择性读取，不得以摘要替代副本原始内容。

## 8. 阶段与版本门

本文件不预先新增/批准任何Q52+ Human裁决，不替换RC01，也不据此把RES数从20改为21。discussion full的实际完成条件是Human明确global load语义、其他承重缺口有可追踪处置，之后形成精确A候选修订并请求Human确认。禁止阶段02、开发、master/核心迁移、REA/PR#18任务改变及游戏操作。
