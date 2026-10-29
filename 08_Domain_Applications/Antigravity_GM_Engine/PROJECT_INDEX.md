# NBA2K22 外挂系统 · 全项目总索引（所有新任务先读）

**索引版本**：v2.2 / 2026-10-29 · **状态**：Native Checkpoint014当前工程范围已正式结项，CLOSED_WITH_DEFERRED_SCOPE；full_goal_complete=false。PR19保留打开Draft，未合并master。
**项目位置**：`08_Domain_Applications/Antigravity_GM_Engine/`（下文默认此路径为 D）。  
**适用**：GPT 规划、Codex 工程、Antigravity、GM/Coach/Player 人格开发、数据采集与分析、独立审核。

> **最重要的默认动作**：进入NBA2K22任务时，先读本文件；再读实际相关的模块文档；开发任务完成时，必须更新本索引、[机器注册表](docs/development/PROJECT_MODULE_REGISTRY_V2.json)中的受影响模块及其当前状态/交付引用，才可以称为“交接完成”。无需全文加载所有旧Run或694研究项。

## 0. 现阶段的产品全貌

NBA2K22 PC离线MyLEAGUE是真实比赛、赛季变化、自然成长与原生状态权威。外挂要给**全部球队的GM、独立教练和球员人格**提供完整的游戏数据以及他们可执行的身份能力，而不是让工程执行器替他们决定交易、签约、战术或选秀。

**最新 Human 执行链（2026-10-28；覆盖旧执行方式的描述，但数据方案暂不改变）**：

```text
[NBA2K22 Game 真实数据/原生读取]
       ↓ 既有数据采集、身份/时间/批次、SQLite/查询、数据分析（暂不改）
[角色可见的数据源 + 预先加载的 GM/Coach/Player 身份能力目录]
       ↓
[各身份人格自主决策、谈判、同意 → 输出精确的批量 ActionIntent]
       ↓
[统一汇总器：归集、按已达成的业务共识构建批次、处理执行顺序/冲突反馈]
       ↓
[REA Native 执行机制：严格对象/ABI/上下文绑定 → 原生函数批量按序调用]
       ↓
[游戏原生状态结果 → 定向读回 → 数据源下一采集批次]
```

- **游戏角色决定 WHAT/WHO/VALUE；执行层只负责 HOW**。交易不由Codex配薪、找替代球员、评估公平；球探不由Codex挑新秀；Coach由模型先选择设置值。原生接口的真实对象/参数/资源检查仍需保留。
- **批量≠底层一次原子事务**：单条Native函数失败或状态未知时按具体回执暂停/隔离，不能重放未知交易；不私自改角色决定。
- **角色知道自己能做什么**：通过 `list_actions(role, phase)`、`describe_action(id)`、`allowed_values(id, context)`和`read_current_state`加载字段含义、枚举与可调用成熟度，输出精确执行指令。
- **数据层暂不重做**；已批准的数据逻辑/世界身份/来源规则继续沿用，旧双SQLite是现有实现，不是未来不可变物理Schema。
- 现有原生实机实例仅有特定Coach设置、特定交易、已有球探Goal设置；不要把研究目录的全部能力宣称正式可用。后续开发以前先基于角色实际需要的全量动作列表确定范围。

[完整新执行架构与批量动作合同](docs/development/ROLE_BATCH_NATIVE_EXECUTION_ARCHITECTURE_V2.md) · [现有能力需求初稿](../../01_os/07_content/_runs/run-20261028-nba2k22-role-native-execution-model-001/02_角色执行能力建模/GM教练球员_可执行能力盘点_A_v1.md)（此相对链接从领域根返回仓库根，应以根绝对路径为准）。

## 1. 逐模块导航：先理解“已有什么、还缺什么”

| ID / 模块 | 当前可证明的内容/角色 | 优先阅读的权威入口 | 主要源码/记录 |
|---|---|---|---|
| **P00 OS与任务治理** | 七阶段工作流、Run/审批/版本/证据管理；不替领域开发做业务决定 | 根`AGENTS.md`、`01_os/README.md`、`01_os/开发入口与单窗口任务规范_v1.md`、D/`AGENTS.md` | `01_os/07_content/_runs/` |
| **P01 平行世界数据架构** | 已有逻辑目标：世界/存档/赛季/人物身份、状态/事件/历史、来源与多角色视图；**V2目标不等于DDL已正式发布** | `docs/development/PARALLEL_BASKETBALL_WORLD_DATA_ARCHITECTURE_V2.md`、`docs/development/NBA2K22_TASK1_REQUIREMENT_RESULT_MODEL_V0_1.md` | `docs/development/NATIVE_GAME_DATA_SYSTEM_RECONSTRUCTION_AND_IO_BLUEPRINT_V2.md` |
| **P02 第一代数据库与事实发布** | 现有SQLite Schema、采集/审计/查询/批次批准与发布组件；范围有历史证据，不等于字段完整 | `database/schema.sql`、`docs/29_SIMPLE_DATABASE_SYNC.md`、`docs/34_BASELINE_CURRENT_STATE.md` | `src/auto_pipeline_ingest.py`、`src/gm_state_io/`、`src/gm_data_access/`、`published/index.json` |
| **P03 游戏原生数据/Decoder** | 本机字段profile、各类对象登记、局部Reader与未闭合覆盖 | `config/source_catalog.json`、`config/memory_field_profile.json`、`docs/development/NATIVE_GAME_DATA_SYSTEM_RECONSTRUCTION_AND_IO_BLUEPRINT_V2.md` | `config/state_io_native/`、`research/` |
| **P04 游戏机制资料库（**必读**）** | DEV29 R01–R07：攻略、功能、19项Coach、18项对手防守、Playbook、训练、选秀、财务、历史；40组/694异构参考项，**不是当前Native执行全集** | **`docs/game_mechanics/README.md`**、`docs/game_mechanics/PROGRESS.md`、`docs/game_mechanics/SOURCES.md` | `docs/game_mechanics/guides/`、`docs/game_mechanics/catalogs/` |
| **P05 GM决策系统** | 现有GM决策/数据输入/多队经营代码与部分人格参考；不能将全部球队完整自动GM视为已通过 | `docs/04_GM_DECISION_ENGINE.md`、`docs/35_WEB_GPT_BASELINES_AND_MEMORY_PROTOCOL.md`、`web_gm/START_HERE.md` | `src/gm_core/`、`web_gm/`、`src/gm_data_access/` |
| **P06 Coach角色与战术** | Coach参数、对手防守、12战术类别、68槽Book、4Freelance的研究/部分工程；新增明确分钟Native调用实现，静态恢复且未实测；独立Coach人格仍待开发 | `docs/game_mechanics/guides/K04_COACH_AND_PLAYS.md`、`research/rea_native_control/ROTATION_MINUTES_CONTRACT.md` | `web_gm/manuals/`、`config/state_io_native/settings.json`、REA能力目录 |
| **P07 Player角色与成长** | Player档案、能力/倾向/徽章、合同、训练/生命线/个人请求的研究；四槽PlayType、54能力/耐久、99倾向及98非哨兵徽章已有原生实现、未实测；独立Player人格未验收 | `docs/game_mechanics/guides/K03_K12_PLAYER_PROFILE_AGENCY.md`、`research/rea_native_control/PLAYER_PLAYTYPE_NATIVE_CONTRACT.md`、`PLAYER_STAT_NATIVE_CONTRACT.md` | `config/state_io_native/player.json`、`research/rea_native_control/runtime/player_playtypes.js`、`web_gm/knowledge/` |
| **P08 交易/签约/选秀/球探/训练** | GM/Coach跨域业务机制与执行材料；交易特定实例和球探已有Goal实机验证，签约与Draft待补 | `docs/game_mechanics/guides/K07_K08_K09_FRANCHISE_OPERATIONS.md`、`docs/game_mechanics/guides/K06_TRAINING_HEALTH_GROWTH.md` | `research/rea_native_control/`、`src/gm_state_io/` |
| **P09 REA原生执行（**必读**）** | 交易原生Process、Coach Apply、球探Goal的具体历史实机效果；当前72动作、65绑定/布局含分钟链、PlayType与索引Stat Setter；**登记与静态实现不等于实机验收** | `research/rea_native_control/REA_WINDOW_CONTEXT_HANDOFF_20261028.md`、`research/rea_native_control/ROLE_EXECUTION_PROGRESS.md`、`research/rea_native_control/VALIDATION_RESULTS.md` | `research/rea_native_control/data/action_registry.json`、`data/native_bindings.json`、`facade.py`、`runtime/` |
| **P10 角色能力与批量执行** | 保留183个初版需求/14组，另有1项发现补充（当前184项）；来源50映射，当前61有效映射；角色服务/汇总/去重已有离线工程，**完整M0–M5仍在施工** | `docs/development/ROLE_BATCH_NATIVE_EXECUTION_ARCHITECTURE_V2.md`、`research/rea_native_control/ROLE_BATCH_EXECUTION.md` | `research/rea_native_control/role_capabilities.py`、`role_batches.py`、工程PR #19及其Run |
| **P11 知识/战术/历史数据支撑** | 球队画像、历史选秀轮回、战术池、比赛规则辅助知识，按来源成熟度读取 | `docs/development_research/`、`docs/game_mechanics/SOURCES.md`、`web_gm/knowledge/` | `docs/06_HISTORICAL_DRAFT_SYSTEM.md`、`web_gm/knowledge/plays/` |
| **P12 治理与历史证据归档** | 2026-10-22原始能力总账、任务和来源历史；使用时查更新版本，不作为当前执行成功数 | `docs/development/PROJECT_CAPABILITY_AND_DELIVERY_LEDGER_V1.json`、`docs/development/NBA2K22_HISTORICAL_TASK_REGISTER_V1.json`、`docs/development/NBA2K22_DOCUMENT_AUTHORITY_INDEX_V1.md` | Draft PR #10、#12、#14、#16→集成PR #17→规划PR #18 |

### 1.1 不能遗漏的“第一大任务”世界数据库工程分支（不在当前PR #17/#18文件树内）

**这属于现成的独立开发成果，不能因为在当前分支找不到`world_data_prototype/`就重新造一套数据库。**

| 状态/来源 | 固定版本与实际可复用内容 |
|---|---|
| **世界数据工程基线** | `task/nba2k22-world-data-full-implementation-20261024@17ec1cea88c2bb6c36264792f70c94bef9a8bdb4`；[源码/README](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/blob/17ec1cea88c2bb6c36264792f70c94bef9a8bdb4/08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype/README.md)，[BASELINE_HANDOFF](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/blob/17ec1cea88c2bb6c36264792f70c94bef9a8bdb4/08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype/BASELINE_HANDOFF.md)。原常规赛工程基线v24：100张STRICT表/1775列、20个Reader源族、42个成功采集单元、受控的事实库/查询/备份与回执；**不是全生命周期正式验收**。 |
| **定点审核修复分支** | `task/nba2k22-world-data-review-fixes-20261026@a3927fb150a213201e404cca043ced4f57409bd1`；[修复说明](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/blob/a3927fb150a213201e404cca043ced4f57409bd1/08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype/REVIEW_FIXES_F01_F02_F03.md)。候选v25：101张表/1789列；F-01年度有证据的追加、F-02赛程/Box一致性、F-03有效receipt的冲突隔离；**仍需独立审核/集成裁决**。 |
| **后续使用原则** | 数据底座开发任务应先fetch上述分支的`world_data_prototype/`及`01_os/07_content/_runs/run-20261024-nba2k22-world-data-implementation-002/`、`run-20261026-nba2k22-world-data-review-fixes-001/`证据；明确是否在目标分支拥有相关代码，再决定继承、Cherry-pick、整合或另建模块。未经Human批准不得合并数据分支或修改当前正式数据库。 |

> **同时存在两套不同成熟度的数据资产**：当前集成树的第一代`database/schema.sql`及`src/gm_state_io/`是现有业务实现；上述独立的`world_data_prototype/`是更完整的世界数据工程候选。**本次只建立可发现的索引，不修改数据实现、SQLite，也不合并这两套结构。**新执行架构继续沿用获准的数据来源，后续再决定实际采集服务与世界库怎么接入。

> **版本提示**：当前规划PR #18的base是集成PR #17，**master还没有纳入新REA或新索引**。新任务先读取fresh master和实际目标分支；找不到成果时先查正确分支，不能因此判断文件不存在。

## 2. 新窗口/新开发任务最小加载协议

1. 按现有OS规定先读fresh master SHA、根`AGENT_WORKING_DISCIPLINE.md`、根`AGENTS.md`、`01_os/README.md`、`01_os/开发入口与单窗口任务规范_v1.md`与任务包。
2. **读本项目 `D/PROJECT_INDEX.md` + `D/docs/development/PROJECT_MODULE_REGISTRY_V2.json`**，检查其`last_update`和PR分支；如果当前工作在D目录，先按D/`AGENTS.md`路由。
3. 按模块ID从表中挑选**最少必读的2–5份**具体资料；涉及游戏原生行为则加载P04游戏机制库、P09 REA经验与当前Native Registry。涉及数据库就加载P01–P03；涉及人格就加载身份能力/游戏机制资料。
4. 查询现有文件、分支、任务成果和真实实现状态再设计，禁止从零重写已完成能力。长文、694条R07分片仅在明确涉及其内容时读取。
5. 开发**前**在任务包写`affected_module_ids`、`loaded_source_refs`、`baseline_commit`；开发**后**更新受影响模块索引、最新实际PR/commit和状态，列出未解决缺口。详见[索引维护契约](docs/development/PROJECT_INDEX_SYNC_CONTRACT_V1.md)。
6. 保留OS原来的Human授权、审批及master发布门，不因自动读取索引而自动获得游戏附加/写入许可。

**文件不存在或分支不含文件**：先检查PR #18分支和集成基线，不许静默略过；无法访问时在交接报告标出`INDEX_NOT_LOADED`而不是假称完成索引阅读。

## 3. 任务完成→索引同步的最低要求

任务报告必须含：`task_id`、`affected_module_ids`、`files_changed`、`new_verified_evidence`、`new_or_changed_capabilities`、`remaining_gaps`、`pr/head_sha`、`index_sync_commit`。如果只做研究，就标研究；如果没有真实游戏实验，不得将能力标`LIVE_VERIFIED`。一项任务可以更新多个模块，但不能漏掉入口链接。

本索引是**入口/汇总层**，不取代某模块自己的权威源码、README、R07证据矩阵或OS task run。机器版注册见 `docs/development/PROJECT_MODULE_REGISTRY_V2.json`；索引更新可以在同一个开发PR提交，不需重开独立“补索引”任务。

## 4. 当前任务与证据路径

- 当前工程窗口（已正式结项，缺口保留）：[Draft PR #19](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/pull/19)，独立于来源PR #18；已验证代码候选`acfc12250f01becbd13c7061cb7513cea028ac08`（124项离线检查及Managed Run/Inspect；含既有原生工程、静态信息整理、辅助提交拒绝边界与来源/索引核对），完整M0–M5仍在施工。准确进度指针：`01_os/07_content/_runs/run-20261028-role-native-execution-system-001/PROGRESS_POINTER.json`，不是全任务完成指针。

- **已结项/保留未完成范围：`NBA2K22-ROLE-NATIVE-EXECUTION-SYSTEM-01`**，工程基准PR18 `094f1aa641f93dec2277707ad9dbf5bdb0341247`。新增[M0角色能力服务](research/rea_native_control/role_capabilities.py)、[M1批次/持久去重与恢复](research/rea_native_control/ROLE_BATCH_EXECUTION.md)、[日期训练局部Apply](research/rea_native_control/TRAINING_PATCH_CONTRACT.md)、[明确球员分钟Native链](research/rea_native_control/ROTATION_MINUTES_CONTRACT.md)及[准确进度/未完成项](research/rea_native_control/ROLE_EXECUTION_PROGRESS.md)。保留原183项需求并补充撤回报价1项；原有50映射保留为历史来源，当前61项有效映射含4项POE、2项训练局部操作、1项分钟操作、2项属性/倾向批量操作、1项明确合同报价提交及1项补充撤回操作，交易变体统一直接Process。P04/P06机制资料与P09/P10源码同步；离线协议/字节验证不等于新实机证据，**完整M0–M5尚未完成**。P01–P03数据链不变。运行证据：`01_os/07_content/_runs/run-20261028-role-native-execution-system-001/`。

- PR #17：从 #10、#12、#14、#16整合研发成果，未进入master。
- 当前Player增量：[四槽PlayType原生调用合同](research/rea_native_control/PLAYER_PLAYTYPE_NATIVE_CONTRACT.md)将已有4项需求从不可调用候选提升为静态调用实现，这一增量本身未增加映射总数。逐槽权限、Player自身UID与批次资源检查已接入；后续[属性/倾向合同](research/rea_native_control/PLAYER_STAT_NATIVE_CONTRACT.md)单独恢复索引Setter及角色字段权限；Potential和完整父对象复制体仍不可调用；徽章已按独立[明确联动合同](research/rea_native_control/BADGE_NATIVE_CONTRACT.md)接入，仍未实机验收。当前机读覆盖对未绑定或不可调用的修改明确给出`role_endpoint:null`，不再误指向读取接口。
- PR #18：角色执行能力全量需求盘点，新增本索引、REA交接原文和最新批量原生执行链；目前Draft，尚需Human逐项审议。
- REA交接源 `b7e0f51e8e00be4c3233af2c73c26c73b4958e80` 的原始blob `4cc0b2c487315cc26bd6f25419e0afea63f94ddc` 已按原文纳入。
- 角色能力初稿的183条包括游戏动作、外部人格请求及世界控制，不应直接视作183项Native函数开发计划。

**唯一后续默认**：有能力索引可读，就先读；有关模块变更了，就更新；证据等级没提升，就不夸大。

- Badge静态后续：[完整字段/内部名称/有效修正与互斥恢复](research/rea_native_control/BADGE_NATIVE_RECOVERY.md)。99项Native内部枚举已定位，包括NONE哨兵；80项上限4、19项上限1。有效等级还有链式修正，后续[明确联动接口](research/rea_native_control/BADGE_NATIVE_CONTRACT.md)通过有界当前快照及原版Getter交叉核对接入。仅限明确世界编辑，NONE不可用；界面/模式含义和实际效果仍待验证。

- 当前读取增量：[显式Player字段读取及角色快照合同](research/rea_native_control/PLAYER_EDITOR_READ_CONTRACT.md)。新增`player.editor_state`补齐编辑前值来源，可选择54属性/耐久、99倾向、98非NONE徽章及4槽位；原身份/合同Reader保留原范围。原版Getter153条路径与Setter字段一致，属性编辑前后值也改用原版Getter。角色投影不触发采集，保存/阶段标签仍为host attestation，非Native存档认证。68动作、55绑定/布局、13读取数据集均非实机验收。

- 当前签约增量：[显式合同编码、原生枚举与球队报价读取](research/rea_native_control/SIGNING_NATIVE_CONTRACT.md)。恢复25字段/27枚举，新增`signing.team_offers`只读查询和M0参数卡；ACCEPTED6与SIGNED8分开。原版生成器会改价格/年限，acquire/reset可改球员薪资，保留不可调用。当前72动作/65绑定/15读取数据集；通用完成签约仍未实现；明确报价提交见下方checkpoint012，生产采集/SQLite/历史链不变。

- 当前合同读回增量：[原版合同Getter与5位基础年限修正](research/rea_native_control/PLAYER_CONTRACT_READ_CONTRACT.md)。`player.contract_state`提供六个原版薪资Getter、含/不含选项的剩余年限及17个RAW合同字段，最多10次直接只读调用；原版总和>6时跳过断言路径并保留RAW。技术Reader宽度4→5，生产字段表和采集链不变；完成签约/合同选项写入仍不可调用。

- 当前报价提交增量：[原生FA_SIGNING阶段的明确合同报价](research/rea_native_control/FA_OFFER_NATIVE_CONTRACT.md)接入`GM.CONTRACT.CONTRACT_OFFER`。仅明确GM权限、宿主报价子场景及原生阶段22下，按指定Player/Team和NORMAL/HARDSHIP、CUSTOM六薪资/年限/选项调用原版OfferContract一次，最多7次直接Native调用；不替角色报价、不宣称完成签约。原生可用球员池及合同/报价/根上下文复核已接入离线处理器。全任务仍进行中，新的实机/独立审核/Save证据未运行。

- 当前撤回报价增量：[撤回指定待处理自由球员报价](research/rea_native_control/OFFER_WITHDRAWAL_NATIVE_CONTRACT.md)要求完整25字段预期、唯一当前记录及明确GM权限/场景，通过原版服务清状态，最多3次直接Native调用。只清所选记录状态，其他字节/报价/Player必须一致；未知结果不重试。原183需求不改，发现补充另存`supplemental_requirements.json`，当前合计184项；接受/拒绝及最终签约仍不可调用。自动选最高分报价、整池新秀和竞争报价处理器保留明确排除证据。

- **Human要求本阶段暂停**：合同与决策信息均停止新增探索。[当前信息获取发现](research/rea_native_control/DECISION_INFORMATION_DISCOVERY_20261028.md)整理已有世界数据与新增投篮分区静态证据；[Gemini辅助包](research/rea_native_control/auxiliary/gemini_information_20261028/README.md)提供独立目录、学习资料、三个有界小包、原始输出规范及Owner筛选流程。完整M0–M5仍未完成；Draft PR19不合并，辅助结构自检不等于事实验收。固定输入/验证证据见checkpoint014及其阶段交接指针。

## 2026-10-29 当前Native工程结项与固定继承入口

本轮当前工程范围状态为 **CLOSED_WITH_DEFERRED_SCOPE**，OS Run保持合法终态`deferred`，完整M0–M5未完成且本任务不再继续。旧段落的“进行中/暂停/继续施工”是历史checkpoint语境，由此结项入口取代。

- [正式结项报告](research/rea_native_control/TASK_CLOSURE_20261029.md)；[固定能力总账](research/rea_native_control/data/NATIVE_EXECUTION_BASELINE_MANIFEST_20261029.json)；[剩余能力清单](research/rea_native_control/data/DEFERRED_NATIVE_CAPABILITIES_20261029.json)；[未来Gemini选择性接收说明](research/rea_native_control/GEMINI_NATIVE_INTEGRATION_HANDOFF_20261029.md)。
- 固定工程源码`bc11fa7926a7eaf390b668515e03dc8507ecb656`；最终包含结项文件的冻结ref：`baseline/nba2k22-native-execution-checkpoint-014-20261029`。冻结ref须等于最终工程HEAD，准确SHA见发布后回执/Human最终交付；不得拿源码快照SHA代替最终冻结SHA。
- 实际72动作/65绑定布局/15部分数据集/184需求（183+1），61映射、42需求有调用逻辑。15数据集完整覆盖均false；124项Managed离线测试是既有候选证据，不是新实机或全目标验收。
- Gemini从`39086984…`较早版本分叉，在`gemini_rea`独立研发，当前不自动继承最新Codex结项。GREA-01/Wave-02仅实验候选；未来Codex从冻结SHA新建接收分支逐项审核，不直接合并整个实验分支。
- 结项/停止决策已由Human明确给出；本次交付最终Human阅读验收、独立审核、游戏实验和master集成分别保持适用门，不伪写通过。
