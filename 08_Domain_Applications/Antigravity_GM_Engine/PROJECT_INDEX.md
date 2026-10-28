# NBA2K22 外挂系统 · 全项目总索引（所有新任务先读）

**索引版本**：v2.0 / 2026-10-28 · **状态**：项目领域级导航，随 Draft PR #18 提交；不代表已合并 master。  
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
| **P06 Coach角色与战术** | Coach参数、对手防守、12战术类别、68槽Book、4Freelance的研究/部分工程；独立Coach人格仍是待开发能力 | `docs/game_mechanics/guides/K04_COACH_AND_PLAYS.md`、`docs/39_COACHING_TACTICS.md` | `web_gm/manuals/`、`config/state_io_native/settings.json`、REA能力目录 |
| **P07 Player角色与成长** | Player档案、能力/倾向/徽章、合同、训练/生命线/个人请求的研究；独立Player人格未验收 | `docs/game_mechanics/guides/K03_K12_PLAYER_PROFILE_AGENCY.md`、`docs/game_mechanics/catalogs/PLAYER_FIELD_AND_RIGHTS_MATRIX.json` | `config/state_io_native/player.json`、`web_gm/knowledge/` |
| **P08 交易/签约/选秀/球探/训练** | GM/Coach跨域业务机制与执行材料；交易特定实例和球探已有Goal实机验证，签约与Draft待补 | `docs/game_mechanics/guides/K07_K08_K09_FRANCHISE_OPERATIONS.md`、`docs/game_mechanics/guides/K06_TRAINING_HEALTH_GROWTH.md` | `research/rea_native_control/`、`src/gm_state_io/` |
| **P09 REA原生执行（**必读**）** | 交易原生Process、Coach Apply、球探Goal的具体实机效果，62动作的静态/部分调用登记；**不是62个实机验收** | `research/rea_native_control/REA_WINDOW_CONTEXT_HANDOFF_20261028.md`、`research/rea_native_control/ROLE_MODEL_MECHANISM_GUIDE.md`、`research/rea_native_control/VALIDATION_RESULTS.md` | `research/rea_native_control/data/action_registry.json`、`data/native_bindings.json`、`facade.py`、`runtime/` |
| **P10 角色能力与批量执行规划** | 183个初版原子需求/14组、现有REA 62动作映射50、40资料组对照12 Reader；**正在Human共识阶段，不等于实现** | `docs/development/ROLE_BATCH_NATIVE_EXECUTION_ARCHITECTURE_V2.md`、本PR #18 的Run | `01_os/07_content/_runs/run-20261028-nba2k22-role-native-execution-model-001/` |
| **P11 知识/战术/历史数据支撑** | 球队画像、历史选秀轮回、战术池、比赛规则辅助知识，按来源成熟度读取 | `docs/development_research/`、`docs/game_mechanics/SOURCES.md`、`web_gm/knowledge/` | `docs/06_HISTORICAL_DRAFT_SYSTEM.md`、`web_gm/knowledge/plays/` |
| **P12 治理与历史证据归档** | 2026-10-22原始能力总账、任务和来源历史；使用时查更新版本，不作为当前执行成功数 | `docs/development/PROJECT_CAPABILITY_AND_DELIVERY_LEDGER_V1.json`、`docs/development/NBA2K22_HISTORICAL_TASK_REGISTER_V1.json`、`docs/development/NBA2K22_DOCUMENT_AUTHORITY_INDEX_V1.md` | Draft PR #10、#12、#14、#16→集成PR #17→规划PR #18 |

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

- PR #17：从 #10、#12、#14、#16整合研发成果，未进入master。
- PR #18：角色执行能力全量需求盘点，新增本索引、REA交接原文和最新批量原生执行链；目前Draft，尚需Human逐项审议。
- REA交接源 `b7e0f51e8e00be4c3233af2c73c26c73b4958e80` 的原始blob `4cc0b2c487315cc26bd6f25419e0afea63f94ddc` 已按原文纳入。
- 角色能力初稿的183条包括游戏动作、外部人格请求及世界控制，不应直接视作183项Native函数开发计划。

**唯一后续默认**：有能力索引可读，就先读；有关模块变更了，就更新；证据等级没提升，就不夸大。