# OS-PRMS 设计 B · G1/G2 机制全集、分类与按需加载细化附录（Human审阅版）

> **版本**：`B-v1-RC01-ADDENDUM-CATALOG-01`（后继细化，不覆盖既有B原文）；**状态**：Human 已同意完整设计B，但明确要求先展示清单、分类和按需加载机制。这是规划者负责完成的详细建模成果；不是Codex已实现的目录或测试。  
> **范围**：2026-10-28；Core `446ca66ad48831f5fcdb1af18f37d07619e048c4`；NBA2K22 **Draft PR #18** `094f1aa641f93dec2277707ad9dbf5bdb0341247`；其它领域 `master` 目录/`domain.yml` 当前读回。版本快照冻结后发生变更，应重新生成/比较，不得据旧快照声称新版本完整。

## 1. 首先明确「全局加载」和「全文加载」不是一回事

Q52=B，按两个完全独立的维度分级：

- **B0 强制 Boot**：当前OS生效安全/任务授权、根规范、角色/仓库/分支、已有Boot必要合同——按既有OS清单实际执行，不能由Human可选记忆选择绕过。
- **G1 Core通用机制**：所有适用于本次仓库/角色的正式G1条目，**目录+经过来源验证的概要全面发现**；按职责/工作流阶段/实际正式动作触发，读取相关canonical正文。不能声称「注册了7份README，就自动全文读了7套实现及来源历史」。
- **G2 领域机制**：只从当前`domain_id`所属仓库的正式`09_Domain_Global_Mechanisms/`发现所有已发布条目，并显示目录/概要；领域具体任务再展开相关机制全文与08资料。若09尚未建成，返回`DOMAIN_CATALOG_UNINITIALIZED`、列出08候选，并允许按任务读取合法现有领域源；不得声称有正式G2。
- **T1/T2/K1/K2**：当前任务/活动系列的有效状态优先；历史任务与候选经验有索引不全文灌入；K2仅经正式发布后获得G1/G2地位。

**Core版本不等于领域已安装版本**：主Core的当前`master`与各领域工作树的Core-owned文件版本应分别记录。若领域尚未合并Core更新，PRMS不能把主Core最新规则当作当前领域已实际安装；必须以目标仓当前树核对实际文件blob和兼容性，返回`CORE_VERSION_DIVERGED`/`CORE_COMPATIBILITY_UNVERIFIED`等可见缺口，不能隐式实施Core合并。

**重要区别**：`discovered`（目录可见）、`cataloged`（纳入索引）、`formally_published`（所有权及审核后正式版）、`body_loaded`（原文真的读取）、`mechanism_effective`（执行门控状态）、`action_authorized`（操作授权），是六个互不替代的状态。

## 2. 主 Core G1：已发现的七个全局机制（精确列表）

仓库：[`chris2gao/Cybernetic_City_State_OS_v2---core`](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---core)，snapshot SHA `446ca66a…`。以下七项确有 `01_os/03_mechanisms/<name>/README.md`；**指示加载条件是本次设计，不等于目前已经存在自动按需加载器**。

| ID | 机制与实际职责 | 候选加载条件 | 现行生效盘点 |
| G1-M01 | [communication_system](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---core/blob/446ca66ad48831f5fcdb1af18f37d07619e048c4/01_os/03_mechanisms/communication_system/README.md)：全局通信：端点、消息、Human中转、回执 | 跨端消息/正式handoff/发布通讯时 | L3_EXECUTION_GATED |
| G1-M02 | [context_management](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---core/blob/446ca66ad48831f5fcdb1af18f37d07619e048c4/01_os/03_mechanisms/context_management/README.md)：上下文管理：固定入口、文件隔离、工作集、归档/恢复 | 所有新窗口完成最小Boot；进行工作集/恢复/归档时读取相关正文 | L1_BOOT_VISIBLE |
| G1-M03 | [mechanism_activation](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---core/blob/446ca66ad48831f5fcdb1af18f37d07619e048c4/01_os/03_mechanisms/mechanism_activation/README.md)：形式化动作宪法、触发解析、执行前门禁、事实证据 | 发起formal action时强制应用，不得由可选记忆加载关闭 | L3_EXECUTION_GATED |
| G1-M04 | [minimum_work_unit_output](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---core/blob/446ca66ad48831f5fcdb1af18f37d07619e048c4/01_os/03_mechanisms/minimum_work_unit_output/README.md)：正式工作单元的四项输出与审查理由合同 | 正式方案/派单、执行结果或独立审核完成输出时 | NOT_LISTED_IN_CURRENT_EFFECTIVENESS_INVENTORY |
| G1-M05 | [model_routing](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---core/blob/446ca66ad48831f5fcdb1af18f37d07619e048c4/01_os/03_mechanisms/model_routing/README.md)：按模型、产品界面、任务能力和来源证据路由 | 需要选择模型或指派接收窗口时 | L3_EXECUTION_GATED |
| G1-M06 | [stage_collaborative_deliberation](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---core/blob/446ca66ad48831f5fcdb1af18f37d07619e048c4/01_os/03_mechanisms/stage_collaborative_deliberation/README.md)：跨阶段协同推演、共识/证据不足时增量再确认 | 承重歧义或当前阶段profile触发时；默认dormant | L1_BOOT_VISIBLE |
| G1-M07 | [task_orchestration](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---core/blob/446ca66ad48831f5fcdb1af18f37d07619e048c4/01_os/03_mechanisms/task_orchestration/README.md)：大任务粒度、内部继续与真实停止条件 | 大任务dispatch/收尾/暂停分类时 | NOT_LISTED_IN_CURRENT_EFFECTIVENESS_INVENTORY |

注：`L0_DEFINED/L1_BOOT_VISIBLE/L2_TRIGGER_BOUND/L3_EXECUTION_GATED/L4_E2E_ADVERSARIALLY_VERIFIED`是Core现存的**机制生效状态等级**，不等于PRMS的记忆上下文L0–L4加载深度。此处`L3`也不代表独立L4审核已通过；未列入Core当前生效盘点的机制仍能在目录中找到。

## 3. G1还必须收录的工作流、Boot、Registry与可选工具

### 七个工作流阶段（正式入口，按当前阶段展开）

| 阶段 | 路径与作用 |
| 01_需求建模 | `01_os/01_workflow/01_需求建模/`，需求建模A（当前Core方法论v0.2） |
| 02_信息收集与提炼 | `01_os/01_workflow/02_信息收集与提炼/`，信息与证据取得 |
| 03_结果建模 | `01_os/01_workflow/03_结果建模/`，设计结果B |
| 04_测试生成 | `01_os/01_workflow/04_测试生成/`，测试用例生成 |
| 05_步骤拆分 | `01_os/01_workflow/05_步骤拆分/`，实施计划分解 |
| 06_执行 | `01_os/01_workflow/06_执行/`，方案实施 |
| 07_测试执行 | `01_os/01_workflow/07_测试执行/`，执行验证 |

### 七份现有Boot manifest（不是7套无条件全文）

| 编号 | 已有路径 |
| 1 | `01_os/02_boot/communication_system/启动清单_v1.yml` |
| 2 | `01_os/02_boot/context_management/启动清单_v1.yml` |
| 3 | `01_os/02_boot/mechanism_activation/启动清单_v1.yml` |
| 4 | `01_os/02_boot/minimum_work_unit_output/启动清单_v1.yml` |
| 5 | `01_os/02_boot/model_routing/启动清单_v1.yml` |
| 6 | `01_os/02_boot/stage_collaborative_deliberation/启动清单_v1.yml` |
| 7 | `01_os/02_boot/workflow_minimum_operational_loop/启动清单_v1.yml` |

### 十三份现有 Registry（保证目录发现不漏项）

| 编号 | 文件 |
| 1 | `01_os/05_registry/communication_system_v1.yml` |
| 2 | `01_os/05_registry/context_management_v1.yml` |
| 3 | `01_os/05_registry/mechanism_activation_v1.yml` |
| 4 | `01_os/05_registry/minimum_work_unit_output_v1.yml` |
| 5 | `01_os/05_registry/model_routing_v1.yml` |
| 6 | `01_os/05_registry/repository_guards_v1.yml` |
| 7 | `01_os/05_registry/repository_publisher_authority_v1.yml` |
| 8 | `01_os/05_registry/skills_and_tools_v1.yml` |
| 9 | `01_os/05_registry/stage_collaborative_deliberation_v1.yml` |
| 10 | `01_os/05_registry/task_discipline_v1.yml` |
| 11 | `01_os/05_registry/task_orchestration_v1.yml` |
| 12 | `01_os/05_registry/workflow_minimum_operational_loop_v1.yml` |
| 13 | `01_os/05_registry/workflow_publication_gate_v1.yml` |

**Core已验证的可选工具**：`check-jsonschema`、`mutmut`、`cosmic-ray`，由 `01_os/04_skills_and_tools/README.md`和工具注册表发现，默认不装载运行；REA仍是另一个后续工具候选，不在本 PRMS 项目中安装/激活。

**完整性边界**：7机制+7工作流+7 Boot+13 Registry是**已枚举的分组/文件计数**，不是「OS 只有7项规则」或把这些文件全部加载的token承诺。根`AGENTS.md`、`AGENT_WORKING_DISCIPLINE.md`、`CORE_MANIFEST.yml`、`01_os/开发入口与单窗口任务规范_v1.md`、权限和发布合同属于B0/共享治理入口，不应被七机制统计吞掉。

## 4. 六个领域的真实身份与09目录状态

| 领域 | 仓库 | `domain_id` | 已发现09正式目录 | 业务内容状态 |
| NBA 2K22 | [nba2k22](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22) | `nba2k22` | 未建立/未找到 | 已导入 |
| 数学 2.0 | [maths2.0](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---maths2.0) | `maths2.0` | 未建立/未找到 | domain.yml声明未导入 |
| 英语 2.0 | [english2.0](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---english2.0) | `english2.0` | 未建立/未找到 | domain.yml声明未导入 |
| 人际关系 2.0 | [relationships2.0](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---relationships2.0) | `relationships2.0` | 未建立/未找到 | domain.yml声明未导入 |
| 生活作息 2.0 | [daily-routine2.0](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---daily-routine2.0) | `daily-routine2.0` | 未建立/未找到 | domain.yml声明未导入 |
| 公司与组织 2.0 | [company2.0](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---company2.0) | `company2.0` | 未建立/未找到 | domain.yml声明未导入 |

上述六个仓库均有独立`domain.yml`，声明相同Core祖先和按Human请求三方合并、自动更新关闭。所查`master`均没有正式`09_Domain_Global_Mechanisms/`，**因此当前不能填写任何已正式发布G2机制**。尤其其它五域尚无获证G2，不应从名字脑补「数学全局公式规范」「英语全局词表规范」等现存内容。未来每一域在Human允许并实际创建后独立初始化其G2目录。

## 5. NBA2K22 的 P00–P12 项目模块——逐项分类，不漏掉一个

来源：[NBA2K22 `PROJECT_MODULE_REGISTRY_V2.json` （Draft PR #18）](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/blob/094f1aa641f93dec2277707ad9dbf5bdb0341247/08_Domain_Applications/Antigravity_GM_Engine/docs/development/PROJECT_MODULE_REGISTRY_V2.json)，共13条；P00–P12是**项目模块**，绝非13个已正式G2。

| 模块 | 真实模块与来源 | PRMS分类 | 可升级或保留边界 |
| P00 | [OS bootstrap/governance](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/blob/094f1aa641f93dec2277707ad9dbf5bdb0341247/08_Domain_Applications/Antigravity_GM_Engine/AGENTS.md) | `G1_REFERENCE_NOT_G2` | 根OS规则与权限；不要复制OS到G2 |
| P01 | [Parallel world data architecture](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/blob/094f1aa641f93dec2277707ad9dbf5bdb0341247/08_Domain_Applications/Antigravity_GM_Engine/docs/development/PARALLEL_BASKETBALL_WORLD_DATA_ARCHITECTURE_V2.md) | `G2_ARCHITECTURE_CANDIDATE` | 跨NBA任务可复用架构目标，但方案不是已通过的DDL |
| P02 | [Existing SQLite ingestion/query/publishing](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/blob/094f1aa641f93dec2277707ad9dbf5bdb0341247/08_Domain_Applications/Antigravity_GM_Engine/database/schema.sql) | `SOURCE_CODE_ONLY` | 实际业务数据库和源代码；可被G2索引引用，不全量提升为机制 |
| P03 | [Native game data source and decoding](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/blob/094f1aa641f93dec2277707ad9dbf5bdb0341247/08_Domain_Applications/Antigravity_GM_Engine/config/source_catalog.json) | `SOURCE_TECHNICAL_EVIDENCE` | 原生字段与Decoder研究；状态未覆盖全部游戏数据 |
| P04 | [Gameplay mechanisms knowledge base](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/blob/094f1aa641f93dec2277707ad9dbf5bdb0341247/08_Domain_Applications/Antigravity_GM_Engine/docs/game_mechanics/README.md) | `G2_KNOWLEDGE_CATALOG_CANDIDATE` | 篮球知识和机制资料作为领域知识目录，不等于其每条资料都是已认证的原生机制 |
| P05 | [GM decision agents](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/blob/094f1aa641f93dec2277707ad9dbf5bdb0341247/08_Domain_Applications/Antigravity_GM_Engine/docs/04_GM_DECISION_ENGINE.md) | `G2_SUBSYSTEM_REFERENCE_CANDIDATE` | GM部分工程与方法；不是全部30队系统已完成 |
| P06 | [Coach tactics and Coach persona](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/blob/094f1aa641f93dec2277707ad9dbf5bdb0341247/08_Domain_Applications/Antigravity_GM_Engine/docs/game_mechanics/guides/K04_COACH_AND_PLAYS.md) | `G2_SUBSYSTEM_REFERENCE_CANDIDATE` | 教练参数与战术资料；独立Coach人格仍未验收 |
| P07 | [Player profile/persona](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/blob/094f1aa641f93dec2277707ad9dbf5bdb0341247/08_Domain_Applications/Antigravity_GM_Engine/docs/game_mechanics/guides/K03_K12_PLAYER_PROFILE_AGENCY.md) | `G2_SUBSYSTEM_REFERENCE_CANDIDATE` | 球员资料和人格研究；不是已正式执行的人格系统 |
| P08 | [Trades/contracts/draft/scouting/training](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/blob/094f1aa641f93dec2277707ad9dbf5bdb0341247/08_Domain_Applications/Antigravity_GM_Engine/docs/game_mechanics/guides/K07_K08_K09_FRANCHISE_OPERATIONS.md) | `G2_KNOWLEDGE_REFERENCE_CANDIDATE` | 不同操作的实机证据成熟度不同；只可引用已核实原件 |
| P09 | [REA native-action controller](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/blob/094f1aa641f93dec2277707ad9dbf5bdb0341247/08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_control/REA_WINDOW_CONTEXT_HANDOFF_20261028.md) | `G2_NATIVE_TOOL_PROFILE_CANDIDATE` | REA通用方法未来可进Core可选工具；游戏绑定在NBA，不是62项全部实测 |
| P10 | [Role action inventory/batched native execution](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/blob/094f1aa641f93dec2277707ad9dbf5bdb0341247/08_Domain_Applications/Antigravity_GM_Engine/docs/development/ROLE_BATCH_NATIVE_EXECUTION_ARCHITECTURE_V2.md) | `DRAFT_UNPUBLISHED_REQUIREMENTS` | 183个动作是初步需求目录，批执行器不是已实现的当前能力 |
| P11 | [Basketball/plays/era knowledge](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/blob/094f1aa641f93dec2277707ad9dbf5bdb0341247/08_Domain_Applications/Antigravity_GM_Engine/docs/development_research/) | `G2_KNOWLEDGE_CATALOG_CANDIDATE` | 篮球与历史知识参考，未声明已具备完整人格运行 |
| P12 | [Historical records and source authority](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/blob/094f1aa641f93dec2277707ad9dbf5bdb0341247/08_Domain_Applications/Antigravity_GM_Engine/docs/development/NBA2K22_DOCUMENT_AUTHORITY_INDEX_V1.md) | `SOURCE_PROVENANCE_INDEX` | 历史任务/交付/证据可定位，不可自动作为当前正式成功证明 |

## 6. 未来建议的G2目录长什么样（尚未在任何领域部署）

```text
09_Domain_Global_Mechanisms/
├── README.md                 # 人类审阅入口、当前批准/拒绝/缺失
├── domain_mechanisms.yml     # 唯一正式G2条目及生效状态/owner
├── knowledge_catalog.yml    # 项目知识导航；可以含候选但不能冒充正式机制
└── <mechanism_id>/           # 仅放正式提升的领域级机制
    ├── README.md
    ├── contract.yml
    └── sources.yml           # 指向08权威源/证据/精确版本
```

每个G2条目至少需要：`domain_id, repo, source_commit, content_path, object_kind, mechanism_id, title, summary, version, owner, publication_status, effectiveness_level, applicability, required_by_trigger, dependencies, evidence_refs, canonical_blob, last_verified, supersedes`。其中 `source_ref` 必须是仓库+ref+精确SHA，不能靠路径名字断言对象是同一个。`object_kind`区别`FORMAL_MECHANISM`/`DOMAIN_KNOWLEDGE`/`MODULE_INDEX`/`DRAFT_CANDIDATE`/`RAW_SOURCE`。

**领域判定优先级**：显式当前任务domain_id → 与domain.yml内仓库身份匹配 → exact commit/ref → 已发布 G2 owner资格 → entry applicability → Human本窗口选择；任何一项失配，禁止退回“在别的领域搜个相似机制”作为已加载。

## 7. Q52=B 的实际装配算法：目录全量、正文按需

```text
① 固定执行 B0：Root安全/任务规则、有效authority、Core当前Boot manifest
② 固定repo SHA：resolve 主Core权威版本 / 当前Domain实际继承Core版本 / task，并核对兼容（分支不等于master）
③ 枚举 Core G1正式机制、Workflow、Registry、可选工具目录
④ 枚举 当前domain G2的09目录及08候选来源；核算完整性和unknown
⑤ 读取所有适用正式机制的经过验证的标题/概要/依赖/状态（不是所有正文）
⑥ 按任务role/stage/action识别必须读的机制正文，确定真实mandatory集合
⑦ 生成 Human本窗口可选额外加载清单（选项、token估算、来源SHA、缺口）
⑧ Human确认可选范围；已有本窗口有效指令不重复追问；B0和必需安全机制不可跳过
⑨ 精确读取正文/任务证据：source SHA/bytes/blobs/版本、预算、stale检查
⑩ 输出 ContextRecoveryReceipt：真的读了什么、摘要还是全文、排除/缺失/未知/阻断
```

**实施时不能信任只写在文档里的加载规则**：Codex应提供`CatalogResolver/LoadPlanner/ContextAssembler/ReceiptValidator`四个独立可测的接口组件（物理组织可合并），强制这些结果的前置条件。需要的正文若因预算未装载，返回`REQUIRED_SOURCE_NOT_LOADED`，不可宣称READY。用户选了一个额外的源，只代表允许本窗口把该内容放进上下文，不提升它的发表状态或程序执行权限。

### 示例1：NBA2K22 原生工程任务

- B0必须读取；当前工作流阶段和对应Core机制按实际触发加载。
- 全部七个Core机制与七个工作流的**目录/概要可发现**，不要求打开其它六阶段所有方法论全文。
- G2当前未正式初始化，必须标`DOMAIN_CATALOG_UNINITIALIZED`；仍可基于Human当前任务指定的合法PR #18读取P04机制资料库和P09 REA经验原件，**只把它们标成已读领域来源/未发布候选**。
- 与游戏Native无关的纯Git任务不因为有P09就默认加载REA脚本；任何本机游戏操作依OS和Human单独授权。

### 示例2：数学领域规划新窗口

- 使用相同Core G1目录和适用Boot/Workflow正文。
- 读取`maths2.0`的domain.yml，09缺失则显示`DOMAIN_CATALOG_UNINITIALIZED`与覆盖缺口；**不装入NBA P04/P09**。
- 若数学领域当前没有其它正式业务资产，则如实报告，不能生成假想数学机制；该窗口可继续合法规划，但不能宣称数学G2已完整恢复。

## 8. 完整性检查：Human有权检查「到底收录了哪些」

未来应有两种不同的检查：**目录完整性**与**实际加载完整性**。目录不遗漏≠正文已载入，正文已读≠对事实和执行权限的验证通过。

目录报告至少包含：`source_tree_sha`、`scan_roots`、`registered_entries`、`unregistered_candidate_paths`、`missing_references`、`duplicate_ids`、`cross_domain_references`、`invalid_owner`、`stale_summaries`、`draft_entries`、`unknown_coverage`。单次筛选检索必须报excluded数量，不能把`no match`当成全仓没有。完整性含「路径、来源、条目身份、互链、状态」，不以模型自信代替仓库穷举。

装配报告至少包含：`mandatory_ids`、`selected_optional_ids`、`summary_loaded_ids`、`full_body_loaded_ids`、`actually_verified_source_blobs`、`not_loaded`、`stale`、`source_missing`、`budget_used`、`current_session_human_choice`、`ready/partial/blocked`；正式执行时必须保证mandatory全部以正确版本加载，不能只读取一个模型摘要就执行受约束动作。

### 20项反例与验收（**全部NOT_RUN**）

| 场景 | 必须通过的断言 |
| INV-01 | Core seven mechanism definitions all discovered, names and sources match Core frozen tree |
| INV-02 | Core seven workflow stage roots included as G1 stage references, no false duplicate mechanism |
| INV-03 | Core seven Boot manifests and 13 registries counted; binding failures surface separately |
| INV-04 | Mandatory B0 boot cannot be suppressed by optional Human memory selection |
| INV-05 | Q52=B all applicable G1/G2 directories and summaries discovered, not all bodies preloaded |
| INV-06 | Task/role triggers cause exact relevant mechanism body and valid SHA load, not unrelated mechanisms |
| INV-07 | G2 uses exact domain_id AND repository identity AND target ref AND ownership, rejects cross-domain references |
| INV-08 | All six 09 paths not found is reported as UNINITIALIZED, never silently treated as a fully registered catalog |
| INV-09 | NBA P00-P12 all 13 are classified; DRAFT_PR18 does not get promoted to formal G2 |
| INV-10 | NBA game mechanics P04 loaded on task relevance; REA P09 on Native scope only and no game execution grant |
| INV-11 | Non-NBA new window never receives NBA documents by default |
| INV-12 | Any unregistered source is reported as CANDIDATE_UNREGISTERED, not omitted or silently made active |
| INV-13 | Catalog source commit changed marks summaries stale and blocks required body until reread |
| INV-14 | Visible filtered listing reports complete scan scope, excluded count and unknown, not exhaustive from a filtered subset |
| INV-15 | Human current-window optional selections and consent receipt; B0 rules retained; no implicit new session reuse |
| INV-16 | Context receipt distinguishes discovered/summary/full/verified/selected/excluded/missing and authority |
| INV-17 | Old session cannot update authoritative state via unaudited direct write, or report FENCING_NOT_ENFORCEABLE |
| INV-18 | Core upgrade does not distribute mutable RoleCurrent or leaked domain secrets to domains |
| INV-19 | Task terminal vs unknown lifecycle conforms to current Core working-set contract |
| INV-20 | Core change/Domain merge only after explicit protected publication/individual domain upgrade approval |

## 9. 谁来完成，何时交给Codex

- **由我负责、当前已形成**：对现有Core 7机制、7工作流、7 Boot、13 Registry、NBA P00–P12、六个领域09现状进行清单核查；建立B的明确默认加载算法、分类和负例；本文件与机器清单可供Human逐项审阅。
- **Codex接下来负责实现及测试**：可枚举同一commit树的目录遍历、source/version/owner/schema校验、完整性报告、缓存/摘要增量失效、Human装配选择及真实新窗口加载receipt。Codex不应自行决定「哪条NBA原始游戏内容升级正式G2」；正式提升仍需独立评审/保护发布权。
- **现状不变**：本文件未在Core或任何领域创建09，也未创建真实G2/PRMS引擎；Human对设计B已批准，但新增细化需要作为B的可审计补充纳入正式规划交接，再进入工程开发；不得把本附录本身写成已测试/已发布。
- **历史状态差异**：NBA规划run.yml仍记录A RC01 candidate/confirmed:false，而Human A RC02批准的原件真实存在。提交正式设计时应一并把“Human决定证据”和“机读指针状态”分列并在授权路径完成修复，不因旧YAML错误否定已发Human指令。

## 10. 原始证据及读回边界

- [Core七个机制及通用入口](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---core/blob/446ca66ad48831f5fcdb1af18f37d07619e048c4/01_os/03_mechanisms/README.md)；[七阶段](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---core/blob/446ca66ad48831f5fcdb1af18f37d07619e048c4/01_os/01_workflow/README.md)；[Boot入口](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---core/blob/446ca66ad48831f5fcdb1af18f37d07619e048c4/01_os/02_boot/README.md)；[机制生效盘点](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---core/blob/446ca66ad48831f5fcdb1af18f37d07619e048c4/01_os/03_mechanisms/mechanism_activation/机制生效等级与盘点_v1.yml)。
- [NBA2K22总索引](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/blob/094f1aa641f93dec2277707ad9dbf5bdb0341247/08_Domain_Applications/Antigravity_GM_Engine/PROJECT_INDEX.md)；[13模块机器注册表](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/blob/094f1aa641f93dec2277707ad9dbf5bdb0341247/08_Domain_Applications/Antigravity_GM_Engine/docs/development/PROJECT_MODULE_REGISTRY_V2.json)；[索引同步合同](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/blob/094f1aa641f93dec2277707ad9dbf5bdb0341247/08_Domain_Applications/Antigravity_GM_Engine/docs/development/PROJECT_INDEX_SYNC_CONTRACT_V1.md)；[REA经验原件](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/blob/094f1aa641f93dec2277707ad9dbf5bdb0341247/08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_control/REA_WINDOW_CONTEXT_HANDOFF_20261028.md)。
- 六个域的`08_Domain_Applications/domain.yml`均通过GitHub获取，09均未发现；这些是**特定时间/branch/ref的静态证据**，不是未来环境持续完整性担保。

**本附录是需求/设计可审阅基线，非物理实现或运行验收。**