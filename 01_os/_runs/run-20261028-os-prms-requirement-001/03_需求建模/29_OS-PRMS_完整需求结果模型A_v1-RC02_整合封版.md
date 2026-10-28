# OS-PRMS 完整需求结果模型 A-v1-RC02 · 需求整合与Human批准绑定版

## 0. 版本、依据、批准范围

- **文档身份**：`OS-PRMS-A-v1-RC02`，在已向Human披露的RC01与25–28增量成果上规范化整合，不进行未经Human覆盖的新产品语义选择。
- **项目与适用对象**：OS系统及各领域OS下的架构、规划、研发、资料整理、独立审核等**持续工作岗位角色**；游戏世界内部GM/Coach/Player人格不是本A的对象。
- **Human直接原文**：`01_任务输入/15_Human批准Q52_B及完整A意图_精确范围记录_v1.md`：“我也同意后者，请继续，批准完整a”。该消息确认**Q52=B**及**完整A批准意图**，不意味着Human提前逐字确认本文件编写后的任何新增实质规则。
- **Human作出决定时已公开的内容快照**：NBA2K22规划分支 `35a791cf95d5c5fa7f58b8a56f44d229392488a0`；该SHA包含已正式确认的A0/Q1–Q51、RC01、25/26一致性审查增量、27/28专题内容与Human追加输入13/14。本文件是该已讨论内容 + 已明确的Q52=B的**无语义扩张的精确组合**。
- **版本绑定规则**：Human说的是“批准完整A”，不是逐字报出`RC02`；`RC02`是本次后续归档时规划模型赋予完整组合的精确标签。此Human批准只适用于下列不可拆分、在Human指令时已存在的组成来源与Q52=B，不覆盖今后对本RC02的实质扩充；新的承重语义应依01b机制另行确认。
- **既有决定**：A0 `OS-PRMS-A0-v1-RC01` Q1–Q19有效；01b Q20–Q51原件有效，不擅改选项；Q52=B在本轮直接确认。
- **结果数量**：稳定RES-001..020（20项）。G1/G2/TaskSeries/Promotion并入17–20、009、013、014的明确子项；不因新增候选DTO/聚合视图虚增物理文件/数据库数量。
- **文档责任**：本文件封装可观察需求、契约一致性与验收义务；Core中真正的代码、GitHub发布、合并/分发、09目录创建、跨模型UI、性能阈值及其他工程事实尚未实现或实测。后续02实证、03方案B、04–07执行验证保持分离。

## 1. 核心成品与20项RES不可拆分总览

| ID | 应实际交付的系统产品结果 | 基础详细规格 |
|---|---|---|
| RES-001 | RoleDefinition的注册、身份、模板版本与兼容升级 | 09、10、11 |
| RES-002 | RoleInstance独立工作岗位稳定ID和生命周期 | 09、10、11 |
| RES-003 | RoleAssignment任务/权限与岗位身份分离 | 09、10–12 |
| RES-004 | 单活动RoleSession及自动GitHub核证接管 | 09、12、26 |
| RES-005 | GitHub Markdown/JSON唯一耐久权威，候选→核实→正式发布 | 09–12、26 |
| RES-006 | 人类决定、事实事件、历史更正和来源审计追加保存 | 09–12、26 |
| RES-007 | 可恢复RoleCurrent、Checkpoint与已发布有效指针 | 09–12、26 |
| RES-008 | 经验提炼、来源/反证/适用范围、stale与后继 | 09–12、16、26、27 |
| RES-009 | 共享知识、正式发布/独立审核及全仓开放读边界 | 09、12、27、28 |
| RES-010 | 动态上下文、检索和预算与证据引用 | 09–12、18、21–22、25–28 |
| RES-011 | GPT/Codex/Human工作台适配、Boot与恢复包 | 09、12、18、22、27 |
| RES-012 | 自动维护、冲突/失败、观测和安全重试 | 09、12、22、26 |
| RES-013 | 经03 Human确认设计B后直接升级主OS核心规划机制 | 09、28 |
| RES-014 | OS工作岗位端到端测试和反例矩阵 | 09、14、19、26–28 |
| RES-015 | 跨岗位源内容**全量实体**复制、快照与血缘 | 09、12、26 |
| RES-016 | 新会话自动接管、GitHub有效所有权读回和旧会话失效 | 09、12、26 |
| RES-017 | 长期OS/领域/任务事实分层，G1/G2/TaskSeries内容分区 | 16、21、25、27–28 |
| RES-018 | SummaryCard及任务/主题/岗位/交接概要、增量失效 | 16、21、25–28 |
| RES-019 | 多维索引、来源范围、分域目录与任务索引和更新 | 17、21–22、25、27–28 |
| RES-020 | L0–L4分层装配、Human选择、来源验证、上下文恢复回执 | 18、21–22、25–28 |

以上表中的数字均指本Run `03_需求建模/` 对应编号前缀，**不是文件必填物理路径**。详细正文为本表引用的原件组合；冲突时以Human原始决定与本版本明确核销的不变量为准。未明示覆盖的旧值不能凭后写的概要自动废止。

## 2. 记忆记录对象分类（内容轴）与读取深度（深度轴）

### 2.1 两轴不混淆

| 内容类别 | 记录什么 | 何时发现和注入 |
|---|---|---|
| B0 · 固定OS Boot与生效安全限制 | 新鲜master SHA、根级协作规范、最小Boot、岗位/任务/当前Human权限、禁止事项与验证状态 | 原现行OS始终适用；不能由Human“不加载历史记忆”绕过 |
| G1 · OS全局机制生态 | 七阶段Workflow、上下文/通信/讨论/模型路由/任务编排、正式工具/机制、适用角色、依赖、版本、升级依据、证据及目录 | 每OS仓库完整发现其适用正式目录与概要；需要遵守的规范全文按职责/触发加载 |
| G2 · 当前特色领域全局机制 | 本领域的整体规则、知识入口、体系结构、正式领域机制、引用的08源、领域工具、适用范围/版本 | 当前仓库单独的领域目录；不把NBA2K22机制塞到数学或英语 |
| T1 · 当前任务/仍活动系列任务 | task/series ID、成员和完成里程碑、当前阶段、Human约束、已完成信息、未决、依赖、下步/checkpoint、证据版本 | 当前任务需要的入口必读；同系列连续工作或Human选择时加载相关上下文，不把所有活动run全文预读 |
| T2 · 历史完成/终止任务 | 全部任务原件、原始事件、最终结果、失败/测试、审核、出处与归档状态 | 正式终态后从默认活动装配退出；指定/核证/追溯时可查询和扩大范围 |
| K1 · 待提升经验 | ExperienceCard、来源任务/证据、适用条件、反例、置信、建议修正或新机制 | 不因任务结束自动取得正式G1/G2身份 |
| K2 · 已正式发布的共享知识/机制 | 目标归属(G1 Core或G2 Domain)、已批准版本、正式审核/发布回执、依赖及来源 | 发布后作为其归属G1/G2的一部分可发现和加载 |

L0 = 最小强制入口、L1 = CURRENT、L2 = 目录/概要、L3 = 原始精准证据、L4 = 全史与审计。两轴正交：记录全部事实不代表全部原文默认进入prompt；Q42=A复制全部原始内容不允许被L2摘要替代。

### 2.2 Q52=B全局加载的正式语义

1. G1/G2正式机制**全部可发现**，具备目录身份、版本、适用性、摘要与原件位置；无法核实覆盖时显示partial/unknown，不虚报已看完。
2. 每个工作窗口必须先执行现有仓库固定Boot；随后以当前role/task与Human选择确定G1/G2范围；需要遵守的机制规范正文按职责和实际触发完整读取，不能只依赖未经核实的模型摘要。
3. 其它非相关机制可先加载**经过验证的高密度概要**或目录索引，在任务触发、Human指定、证据核验时精确展开L3/L4。任何时候都必须区别“发现/选择/加载概要/阅读全文/验证”。
4. 对需要的强制核心若因预算缺失而未能装载，应返回CONTEXT_BUDGET_INSUFFICIENT并限制相关操作，不得以压缩掉授权或安全规范作为成功。
5. Human允许全部展开时仍需遵守可用预算、来源真实性与工具能力，不保证单一窗口能容纳无限全文。

## 3. 同级领域目录和Core权威继承

- **领域目录产品目标**：每个domain OS仓库设置与`08_Domain_Applications/`同级的`09_Domain_Global_Mechanisms/`（目录名为本次确定的目标形态，在02/03验证路径兼容；本次未创建），容纳领域全局机制权威目录、知识目录与领域正式机制/原件指针。
- **唯一权威分工**：通用PRMS、加载协议、Boot、通用Registry/validator属于`chris2gao/Cybernetic_City_State_OS_v2---core`的core-owned机制。09目录为**domain-owned**；08源码、业务资料、原始领域数据仍由该领域持有；09可以引用08，不默认把08每个源码文件升级为全局机制。
- **未来结构接入义务**：Core的`CORE_MANIFEST.yml`应新增09 domain-owned归属，Core的生成脚本、通用Boot/Registry/loader需识别领域根/目录状态与兼容；每个领域`domain.yml`或等效入口有领域ID、目录精确引用与Core版本关系。
- **主库关系已核对**：主Core`---core`与本NBA2K22、数学`---maths2.0`共享已验证的Git历史祖先`3ae48d2183a6e77d63a43783c7e1999edc01711e`；各领域有core远端来源与独立origin。它们不是GitHub平台fork，Core/Domain单独有master。
- **发布/分发**：按Q35=C/Q36=B在03设计B经Human确认后直接更新**主Core规划规范**；运行时须经历后续工程和验证。主Core接受通用PRMS内容后，经每领域自身Human请求与三方合并、兼容性/冲突/09完整性检查才能分发。不自动merge所有领域master，不将NBA特定08或09正文上传主Core。
- **经验升级链**：任务经验→来源可核证候选→评估通用性和已有机制→G1 Core或G2 Domain目标→必要评审、Human确认及目标仓库保护发布→正式全球目录可见。例REA属于潜在通用能力，**不因本A批准就声称它已升级Core或已成为所有领域可用工具**。

## 4. 活动系列任务与Human新窗口记忆恢复

1. 任务不是全局加载材料；其原件长期保存，但`_runs/**`从不作为全仓默认全文注入。当前角色/任务启动必要的任务包和工作状态遵循既有Boot。
2. 多窗口完成同一task或series时，提供TaskSeriesCurrent、TaskMemoryManifest、已完成阶段/决定、Checkpoint、下一步与证据；未完成且与本岗位相关的系列在新窗口中可发现并由Human具体选择继续加载。
3. 当series经既有OS合法closeout进入终态，其默认活动加载资格退出，但历史仍可检索。仅关闭聊天窗口不等于系列完成；不清除source或虚构完成。
4. 新窗口按角色、仓库及待续工作提出候选加载清单，Human批准**本次**具体可选记忆范围；该批准不是长期仓库读取ACL，也不是写权限。已有明确Human同窗口指令可作为有效选择，不必制造形式性重复许可。跨新窗口不得擅用旧窗口选择宣称已获Human批准；日后如要设计自动跨窗口复用策略需另有明确授权/有效性规则。
5. 固定Boot、安全、当前任务生效授权不得被可选记忆选择关闭。若Human不批准某可选机制但任务的合法安全执行必需它，应说明缺口、限制动作或请求调整选择；不得暗读后声称“没加载”。
6. 完成装配后必须输出ContextRecoveryReceipt，至少含Human选择、角色/任务/领域、Core与领域版本、实际原件/概要、source SHA、coverage、excluded、missing、stale、预算和READY/PARTIAL/BLOCKED，不把模型自己说“懂了”当证据。

## 5. 逻辑对象、字段继承及版本对账

沿用v0.9的19种基础逻辑记录，而非将它误称为19张SQL表；在此上新增或细化以下角色：
- RoleMemoryRoot = RoleInstance/RoleCurrent/Checkpoint/MemoryIndex逻辑聚合入口（不产生第二RoleInstance身份）。
- SummaryCard = 有独立来源/状态的派生摘要记录；需source_ref+精确commit、kind、scope、role/task/topic refs、facts与Human decisions/模型推断类型、open_items及阻塞/下步类型、watermark、覆盖与遗漏、generator/version、stale/supersedes、字节与估算tokens、创建/刷新时间。
- MemoryIndexManifest = 既有MemoryIndex的可核验目录/代际表现；IndexEntry = 可定位到原始item/source与commit的明细。schema_version、generator_version、index_version应语义可区分；scope、indexed/filtered/unindexed/missing分开统计，不能用excluded=0推出全仓完整。
- ContextAssemblyReceipt（或既有SearchHit/RecoveryPackage的组合回执）= 本次选择/校验/装配结果；能证明实际装载版本、预算、有效授权及未载入项，不能与单条SearchHit混同。
- DomainGlobalCatalog/DomainGlobalMechanismEntry = 领域G2权威目录/条目；Role和TaskSeries实体关系及Core兼容、治理状态、激活状态、已审核可见性、来源版本可核验。
- TaskSeriesCurrent/TaskMemoryManifest、ExperiencePromotionCandidate、LoadSelectionProposal、HumanLoadDecision = 当前任务与series、经验提升、人类装载选择的规范逻辑对象；可由现有RoleAssignment/Checkpoint/MemoryIndex/Publication及操作回执组合实现，不先验要求物理独立表。
- `09_Domain_Global_Mechanisms/` 的`README.md`、`domain_mechanisms.yml`、`knowledge_catalog.yml`等为02/03待实证的**候选物理形状**，不宣称文件已存在。

遵守25号《对象字段谱系与覆盖口径》：v0.10→v0.11重命名不得丢失purpose、source range、事实/观点、completeness/gaps、版本/预算度量；scope完整仅说明本已核验scope，空检索不能作为“全仓不存在”。

## 6. 操作、状态、不变量与失败回执

最低可消费功能接口包括：`register_role`、`claim_new_session`、`verify_owner`、`record_durable_event`、`publish_current`、`copy_all_memory`、`search_memory`、`expand_memory`、`refresh_summaries`、`update_memory_index`、`build_context`、`create_recovery_package`、`discover_context_layers`、`propose_load_selection`、`record_human_load_choice`、`assemble_approved_context`、`verify_context_recovery`、`promote_experience`。这里列的是**期望行为的逻辑接口**，不是固定物理API/函数名。

状态至少区分：
- event已耐久保存 vs 外部动作真实成功/失败/未知；
- summary候选/核源/发布 vs 当前有效/stale/contested；
- index可验证覆盖scope/partial/unverified vs 是否已发布；
- checkpoint/CURRENT staged/verified/published；
- session owner pending/verified/stale/conflict；
- Human加载选择 vs 已实际加载/可用/已验证；
- 机制正式发布 vs 已加载上下文 vs 激活与可执行；
- 经验候选 vs 正式Core/Domain全球知识发布。

失败至少涵盖REJECTED、STALE_OWNER、VERSION_CONFLICT、PARTIAL_STAGED、PUBLISH_NOT_CONFIRMED、SOURCE_MISSING、AUTHORITY_UNVERIFIED、INDEX_PARTIAL、SUMMARY_STALE、CONTEXT_BUDGET_INSUFFICIENT、EXTERNAL_EFFECT_UNKNOWN及覆盖范围限定的NO_MATCH；每项保留输入条件、source、预期版本、是否幂等、可否安全重试及回执。

**强制不变量**：只有候选完整校验并正式读回后才可提升CURRENT；部分写入不污染上次有效状态。旧窗口无法被物理关停、Github权限与受控写入绕过技术实证保留EVQ；Q22=C开放读与独立审核污染风险必须公开。全量复制源内容而非摘要，副本产生目标独立CURRENT并保留风险来源；旧Human执行权限不随复制继承。来源变化只按受影响依赖传播stale，不能全仓无差别失效，也不能丢弃旧source。

## 7. 追踪、反例与验收义务

- Q1–Q51逐项Human裁决继续使用`13_Av0.9_裁决需求证据验收追踪矩阵.md`及`23_Av0.11_二十项交付与五十一项裁决追踪增量.md`，**Q52=B**新绑定RES-017/018/019/020、27/28专题模型与SC-GL-01/02、SC-DGM-01/02/08、SC-020；该增量不代替原51决策原件。
- RES-001..020仍以EVQ-001..020和SC-001..020为主追踪；26号补充CL-SAVE/CL-SUM/CL-IDX/CL-CTX/CL-ROLE/CL-COPY/CL-AUDIT/CL-CORE反例（共17个），27号SC-GL-01..08，28号SC-DGM-01..08是**补充子验收场景**，不得误当原SC已全部测试。
- 增加Core/Domain差异、09目录、Core兼容、上游更新对多领域仓库影响和保留domain-owned内容测试义务；Core发布前的所有权/文件对账与跨领域负例必须实测，不能以manifest自述等于测试通过。
- 02负责GitHub跨文件/owner/CAS/复制与跨仓库实际能力、各OS领域目录真实规模和Repo成本、示范长期历史/多模型上下文预算、Domain原有loader/registry事实；03据此定物理结构、算法、完整字段编码及Human指标阈值。
- 保存、索引、概要、恢复、owner、domain-propagation每类均含失败案例。当前所有新SC状态均`NOT_RUN`，EVQ仍待证。没有因批准A而自动获得任何独立工程验收。

## 8. 受控风险、非目标、阶段边界

| 风险 | 保留状态/后续证明 |
|---|---|
| RISK-01开放读与独立审核 | Q22=C同仓库可读；默认避免审计预灌不是强制访问控制 |
| RISK-02自动接管与不合作旧客户端 | GitHub正确记录owner与物理阻断晚到直接写入不可混同，02/03实证 |
| RISK-03删除活动入口与Git历史 | Q17=B不声称历史安全擦除 |
| RISK-04全量复制与新岗位有效状态 | 源快照/哈希、目标独立CURRENT、独立演化及stale报告 |
| RISK-05Core规划升级与实际运行分离 | 03 Human批准B后仅升级Core规划，不直接写master或声称软件完成 |
| RISK-06 G1/G2目录覆盖与加载权威 | 全目录完整性、Human选择/预算、OS固定Boot与新领域09正反证据 |
| RISK-07 Core/Domain分发及资产所有权 | 09域所有、Core兼容/三方合并、人类按仓更新，禁止自动跨仓发布 |

非目标：游戏内人格规则、实际游戏操作、现阶段工程实现、自动后台调度、绕过Human确认的master发布、全部任务历史每次全文注入、强制假装角色读权限被隔离。

## 9. 不可拆分来源清单与精确边界

**冻结来源快照**（此节列出的来源在Human批准前均存在于`35a791cf95d5c5fa7f58b8a56f44d229392488a0`；新Human原句独立为15号文件）：

- 已批准共识及原始选择：`03_需求建模/01_A0需求共识_Human确认_v1.md`，`01_任务输入/01_...10_`，修正`01_任务输入/04_Human范围澄清_OS工作角色优先_v1.md`。
- RC01原本完整产品结果：`03_需求建模/09_需求结果模型A_v0.8_含前七轮裁决.md`、`10_Av0.9_逻辑字段清单.md`、`11_Av0.9_实体关系和主要值域.md`、`12_Av0.9_操作接口和失败回执.md`、`13_Av0.9_裁决需求证据验收追踪矩阵.md`、`14_Av0.9_证据缺口和验收矩阵.md`、`16_Av0.10_持久记忆分层与概要生成合同.md`、`17_Av0.10_多维索引与增量维护合同.md`、`18_Av0.10_按需加载与上下文预算恢复合同.md`、`19_Av0.10_索引概要检索验收与证据计划.md`、`21_Av0.11_记忆概要索引与上下文装配字段级收口.md`、`22_Av0.11_索引概要按需检索输入输出及状态转换.md`、`23_Av0.11_二十项交付与五十一项裁决追踪增量.md`、`24_OS-PRMS_完整需求结果模型A_v1-RC01_待Human确认.md`。
- 01b新审查内容：`03_需求建模/25_Av1_RC01终审增量_对象字段谱系与覆盖口径_v1.md`、`26_Av1_RC01终审增量_状态失败与记忆恢复验收_v1.md`。
- Human新专题及已展示的候选：`01_任务输入/13_Human记忆内容分类及新窗口批准加载要求_v1.md`、`14_Human领域全局机制同级目录与核心仓库继承要求_v1.md`、`03_需求建模/27_01b全局领域任务记忆分层与Human加载讨论模型_v0.1.md`、`28_01b领域全局机制目录与Core向领域分发结果模型_v0.1.md`。
- 本轮Q52=B和“批准完整A”原始记录：`01_任务输入/15_Human批准Q52_B及完整A意图_精确范围记录_v1.md`。它发生于上述快照之后；本文件是后继**精确封装**，不得反写成Q52此前已选择。

**精确版本确认解释**：`A-v1-RC02`不是Human逐字报出的版本字符串。Human已明确批准在先前对话中展示的完整A范围，本版本将其绑定到可回读的固定来源组；它只包括此前已呈现的产品语义和Q52 B。本次撰写中为填空所列的接口名称、逻辑记录名、物理目录内文件名及附加RISK/SC分类，仅在与现有已讨论目标同义时作为规范性实例/核销方式；若后续发现实质新增需求，回01b并需Human再确认，不能借本批准扩权。

**阶段门**：记录Human确认完整A语义后，01b可视为需求目标通过Human确认；02只有在现有任务的阶段转换与权限边界满足后才开展事实收集。不得把本次A批准当作开始工程、真实Core升级、09物理创建或master合并授权。
