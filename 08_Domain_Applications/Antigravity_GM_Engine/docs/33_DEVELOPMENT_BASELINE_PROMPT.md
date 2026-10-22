# 迭代开发基线提示词

> [**开发规划窗口达到会话上限后的最新恢复快照**](development_snapshots/DEV_PLANNING_WINDOW_HANDOFF_20261021_V1.md)：开发规划/独立审核的新网页GPT窗口应首先读取此快照及当时的PROGRESS、共享状态。快照记录R07的最新独立复验门槛、PR12已合并、FINAL-CODEX/DEV28仍需玩家独立批准、六模型运行与人格开发边界；不要按本文其它旧阶段文字重启R研究。


> [**当前项目级开发意图优先于本文件旧交接**](PROJECT_INTENT_AND_MODEL_DEVELOPMENT_BOUNDARIES.md)：DEV29 R系列只研究NBA2K20–23游戏玩法/全部信息、可设置项和交互作用，DEV28只补可靠可读可查询且经批准可执行的游戏底层；未来独立Coach/Player人格、谈判/行为决策模型必须另立任务，**不得以固定阈值/权重决策程序冒充人格并顺带纳入R/DEV28**。六阶段采集→分析→教练→球员→GM→执行。下方PR #12“当前冲突”段落属于2026-10-20历史记录，PR #12已合并；最新状态见GitHub和文档34。

## 当前权威状态：PR #12 主线冲突整理

已将最新origin/main 5c032a0整合到原codex/bpti-package-c，保留主线官方/社区机制研究先行规范、DEV28和十二类战术/命名/DEV24来源资料，以及包C与F1–F4已完成记录。实际冲突只有AGENTS与本文件开头的新增说明；没有代码冲突或功能重写。F1–F4以2f659138已审查实现为准，旧阶段“待修/尚未开始”只作历史。证据见[验收及冲突交接](development_reviews/BPTI_PACKAGE_C_IMPLEMENTATION_AND_ACCEPTANCE.md)和[状态34](34_BASELINE_CURRENT_STATE.md)。PR #12保持Draft、未合并，DEV28仍须另行授权；本轮不重跑已通过的测试、不做无关游戏资料研究。


## 2026-10-20 游戏机制研究先行的持久开发规定

对游戏领域工作，在理解机制前不急于编码。永久规范：[GAME_MECHANICS_RESEARCH_FIRST_DEVELOPMENT_POLICY_V1](GAME_MECHANICS_RESEARCH_FIRST_DEVELOPMENT_POLICY_V1.md)。先复用项目文档→**优先搜索玩家社区（Operation Sports、Reddit、Coach2K）、游戏攻略与官方NBA2K22手册/开发者说明**→形成明确的游戏机制理解→核对真实PC本世代UI、原生枚举及内存来源→写代码与最小授权验证。**同年PS5/Xbox Series次世代MyNBA资料可作为篮球/经营机制的重要参考，不能因平台差异默认排除；只有具体菜单、地址及执行路径要按PC实机认证。**社区玩法与已证原生地址分级登记。战术分类、教练/训练/个体倾向、赛场AI和动态采集等都适用。玩家允许无法直接通过内存找到的战术分类用游戏截图核查（可几十张分批）；不要求Codex活跃等待。**Git冲突/纯代码任务不做无关网页检索**，原开发边界V2保持。

PR #12本轮F1–F4收尾：当前演化必须绑定当前蓝图/来源，旧历史保留但不能进入当前final/strategy；前态须沿同队/career/真实存档实例与连续历史线，缺证据HOLD。无原生可执行动作仅native_action_status=HOLD，市场继续原M3门槛；组合只选INTERNAL/VIABLE_CANDIDATE。结果见[包C验收](development_reviews/BPTI_PACKAGE_C_IMPLEMENTATION_AND_ACCEPTANCE.md)。后续[DEV28权威规划](https://github.com/chris2gao/nba2k22-gm-engine/blob/main/docs/development_tasks/DEV_20261020_28_GM_NATIVE_IO_TRANSPARENCY_AND_EXECUTION_COMPLETENESS_MASTER_PLAN_V1.md)另行启动，本轮不实施DEV24/DEV28、不合并PR、不启用V4。


2026-10-20 工作包C增量：PR #11经玩家批准合并main（04b194a），B4/B5/B6在独立codex/bpti-package-c接入现有M3候选流程。新增submit-blueprint/record-evolution、D1–D6与内部优先比较、同工作台版本历史；详见[B4/B5手册](BPTI_B4_B5_M3_REASONING_AND_EVOLUTION.md)、本轮验收与34。仅C-C1～C-C5合成验收；正式GM、DEV24、采集/游戏数据发布与写入未触发。文化慢变、技能按当前来源、未知方向HOLD，V3有效/V4未启用、实际30队UNASSESSED。下方包B“未合并/包C未开始”为历史阶段描述。

2026-10-20 工作包B增量：DEV27已按玩家新授权以80459b4快进合入远端及本地main。B2/B3已在独立codex/bpti-package-b交付知识映射/30队历史seed和四条早期机制；接口与限制见[B2/B3手册](BPTI_B2_B3_NATIVE_BINDINGS_AND_TEAM_IDENTITIES.md)、[四项验收](development_reviews/BPTI_PACKAGE_B_IMPLEMENTATION_AND_ACCEPTANCE.md)及34。仅四项授权检查首次通过；包B待Draft PR审阅，不自动合并或启动B4–B6。V4未启用，真实30队UNASSESSED；下面旧“未合main/未做B2”描述保留原阶段历史。


2026-10-20 DEV27局部修复：team_book()仅兼容独立末尾Playbook标签，保留原精确匹配、缺失/歧义报错及原生identity，不改游戏数据或其它功能。授权T1–T3静态检查一次通过（3 tests，0.005s）；按玩家最新“直接提交即可”本地提交867fe85，未创建Draft PR或合main，状态BPTI_DEV27_BUGFIX_COMPLETE_TASK_CLOSED。验收见development_reviews/BPTI_DEV27_TEAM_BOOK_SUFFIX_FIX_AND_ACCEPTANCE.md及34。下方DEV23“未修”保留历史调查含义。

2026-10-20接收决定：玩家接受DEV23研究，并明确同意[PR #10](https://github.com/chris2gao/nba2k22-gm-engine/pull/10)作为“战术知识基础设施”并入main，工程提交88a16ec。实际合并提交/状态以该PR与本地Git为准；下方原Draft/独立分支是交付历史。此次接收不认证未知类型/比赛效果、不修既有缺口、不授权后续B2–B6、测试、采集或游戏写入。

2026-10-20玩家追加开发：已实现[共享战术池/用途适配](GM_SHARED_PLAY_POOL_V1.md)，通过Knowledge.play_pool及现有gm_knowledge的play-*只读入口给GM使用。1392个归档共享标识、1345个静态名称、1335条名称推断用途；精确原生类型成员仍UNKNOWN、候选另列。玩家确认球员四PlayTypes和球队四Freelance均前槽更优先/更多执行；共享条目可被其它球队加入或替换进各自书，保留容量和原DEV14同批全局目录/本队目标/具体批准。此授权只新增知识结构与读取，不等于完成B2或新游戏执行能力；没有新测试/采集/写入。

2026-10-20玩家补充E09/E10：同一战术可跨类型分类，类型匹配后装载；球员四PlayType的1/2主用、3/4偶尔，效果与教练等会影响选择；人类按键指定、CPU自动调用，无固定位置限制。按PLAYER_REPORTED_UI使用，不深究精确频率/AI系数，不把固定受益人当类型匹配前置。操作问题已答完；[手册关联补录](development_research/BPTI_DEV23_MANUAL_AND_PLAYER_CALLING_RULES_ADDENDUM_V1.md)和34区分球员类型、球队Freelance、POE与ScoringOption。逐CRC类型仍缺证据；文档补录不启动B2或游戏操作。

BPTI知识层开发索引：[B0契约](BPTI_KNOWLEDGE_CONTRACT_V1.md)和[B1十卡与检索](BPTI_B1_SYSTEM_CARDS_AND_RETRIEVAL.md)已按玩家授权分别经PR #8/#9合入main。后续独立DEV23只读研究见[研究报告](development_research/BPTI_DEV23_CORE_PLAYBOOK_SEMANTICS_AND_ROLE_EVIDENCE_V1.md)及34：204槽中111槽/89个CRC有静态名称，逐战术类型/受益人仍UNKNOWN；实际同名书后缀匹配阻断已记录，未修复。研究部分交付后TASK_CLOSED，后续操作问题已由E10答复，不保持等待会话。复用M2/M3/DEV14，研究不成为GM源/执行许可，不启用V4。后续包B（B2→B3→四家族补证）、包C（B4→B5→B6）按DEV26分别由玩家新触发，DEV24后置。

DEV20/M4工程增量：独立M4分支已实现外挂工程问题池、追加事件、显式有界导入/分流/交接和带日期readiness，状态M4_ENGINEERING_MAIN_MERGED，PR #7经玩家批准小修正后合入main（c51fa36），正式本地工作区已同步。见[工作台手册](M4_SYSTEM_EVOLUTION_WORKBENCH.md)、[验收](development_reviews/M4_SYSTEM_EVOLUTION_IMPLEMENTATION_AND_ACCEPTANCE.md)、文档34及[开发问题索引](../web_gm/development_feedback/CURRENT.md)。它取代旧M4混合经营效果/比赛校准定义；不修Issue #6、不实施BPTI或校准器、不启用V4。新开发规划由玩家主动触发后读取索引，先提出范围/成本再待批准。

DEV14-H/DEV15工程已随PR#5合入main（570419a）：每save_id独立目录及三份数据库，复用schema，不再扩展隔离/防伪工程。按玩家2026-10-20决定，信任聊天具体批准的操作者引用，完整tuple/CAS/回读不变，review可选。另有自动Potential=1脱敏、Intangibles单字节例外、个人防守/本队同名书受限动作。M3-T已在原PR#4接入此底座并完成本轮8项最小验收，PR#4已由玩家批准合入main（504a4c0），正式本地工作区已同步；详见文档34、[M3-T交付](development_reviews/M3_T_IMPLEMENTATION_AND_ACCEPTANCE.md)、[DEV15手册](DEV15_ROTATION_AND_POTENTIAL_RUNBOOK.md)、[给M3交接](development_reviews/DEV14_TO_M3_HANDOFF.md)。基线加载不自动开发、测试或运行游戏，扩展遵守开发规范V2。

DEV14 V1.1工程增量：统一字段/控制库/采集/受控执行入口与多存档生命周期见 [DEV14手册](DEV14_STATE_IO_RUNBOOK.md) 和文档34。开发复用 `gm_state_io`、`save_context` 与原 codecs；不要另造字段偏移表、隐式legacy-shared或跨档审批。当前PR/部署、真实观测和限制以文档34/验收为准，不自动运行示例。

版本：v2，2026-10-17。用途：建立常驻开发基线；每次开发任务由玩家另开一次性窗口。读取本文件不代表启动待办开发。

## 玩家如何使用

建立基线时发送：

```text
请读取并遵守 E:\games\NBA 2K22\Antigravity_GM_Engine\docs\33_DEVELOPMENT_BASELINE_PROMPT.md，初始化开发基线。只建立项目上下文并报告就绪，等待我的任务，不运行采集、测试、发布或游戏写入。
```

以后从基线开新窗口，直接给开发任务。全新对话则在任务前加“先读取 docs/33_DEVELOPMENT_BASELINE_PROMPT.md”。不需要粘贴此前开发聊天记录。

---

## 以下是给模型的完整基线提示词

### 1. 身份与模式

你是 `E:\games\NBA 2K22\Antigravity_GM_Engine` 的迭代开发者。基于已有实现完成玩家本次明确指定的开发；保持数据真实性、数据库兼容、玩法边界和一次性任务交接。

- **初始化基线**：读取最小索引，报告就绪并等待。不得自动认领待办、改代码、连接游戏、运行测试、采集、发布或创建其他对话。
- **一次性开发任务**：核对当前代码与需求，完成实现、必要文档和按授权范围的验证。用户没有要求测试/验证时不自行加或运行测试。开发完成不进入正式 GM、采集或游戏执行。
- **刷新基线**：只重读当前规则、状态和相关增量，更新工作索引后等待。基线聊天不保存长日志，也不代替持久化文件。

### 2. 最小读取顺序

1. 根目录 `AGENTS.md` 和本文件。
2. `docs/34_BASELINE_CURRENT_STATE.md`：当前架构、已交付能力、明确缺口和待办。
3. `config/gameplay_policy.json`：玩家已确认规则；`config/gm_policy.json` 则仍是待确认经营配置。
4. 本次任务对应的规范和入口，小范围读取源码；不要一开始遍历所有历史文档或加载完整数据库/JSON。

开始任务先看 `git status -sb`、`git log --oneline -n 5` 和相关 diff 摘要，识别别人的改动。旧聊天、文件名、历史测试通过记录都不是当前能力证明。任务相关范围外的未提交内容保留，不重置、不顺带提交。

文档索引：数据真实性/批准 22；来源登记 24；数据窗口 27；执行窗口 28；同步 29；GM v1 架构与历史验收 30；字段扩充与最新选秀权 31。文档 30 的历史缺口和 40 项通过记录仅描述当时；新状态以当前源码、文档 31/34 和当前证据为准。

### 3. 不能破坏的系统分工

- 玩家分别触发数据采集、GM 决策、游戏执行，掌握游戏时间。不要加自动月历、自动 GM、自动模型派发或完成后自动写游戏。
- 采集由确定性脚本完成；模型不伪造数据、不手工修 JSON/数据库以通过检查。所有数值计算交给 Python/SQL。
- 网页 GPT 是 GM；`src/gm_core` 是离线数据消费、计算和提案协议。它不导入游戏内存/写入模块，不直接读 live SQLite，不获取执行权。
- 普通人物能力编辑禁止，自然成长交给游戏。历史重力与名单装载要有具体批准和已验收的独立实现；MC 成长故事仍停用。
- 历史新秀按 1984–2020 顺序轮回；选秀权年份是游戏日历年份。选秀权交易仅简单权属、无保护/交换、最多接下来三届。
- 合同数据范围已收窄为大名单球员薪资；不要重新扩展保障金额、死钱和完整现实 CBA 账本。年龄/OVR 可以保持已登记缺口，不能补默认值。
- 已有权限与授权在范围内持续有效；不用为普通可逆开发重复请示。游戏写入、正式球队档案和具体执行动作仍按玩家批准范围处理。

### 4. 当前代码地图

| 层 | 主要文件 | 开发约束 |
| --- | --- | --- |
| Windows 访问 | `src/memory.py`、`scripts/run_admin_data_capture.ps1` | 只读采集；HANDLE/指针 64 位；按实际采集子进程权限判断错误 5 |
| 地址校准 | `src/address_calibrator.py` | 当前 PID/模块/签名检查；失效重扫；同一目录派生来源，不能选中不同名单副本 |
| 字段解码 | `src/source_extensions.py`、`src/draft_assets.py`、`config/*field_profile.json`、`config/draft_asset_profile.json`、`src/config.py` | 明确原点、偏移、类型、位域、版本和证据，未知不猜 |
| 全局模型 | `src/dump_player_pool.py`、`src/historical_rookies.py` | 实时目录数量；暂存后原子切换；历史新秀掩码分类与排重 |
| 模板/隔离 | `src/save_context.py`、`database/schema.sql`、`database/templates/save_template.json` | 新局干净模板，旧局不清空；扩展表迁移和旧批 NULL/缺失语义兼容 |
| 采集/审计 | `src/auto_pipeline_ingest.py`、`src/run_monthly_cycle.py`、`src/audit_sampling.py`、`src/audit_source_extensions.py` | 脚本采集与内存复核；失败不发布；当前是全量 profile |
| 来源绑定 | `src/snapshot_integrity.py`、`src/data_context.py`、`src/data_sync_metadata.py` | 绑定源批次，不把新字段/新规则追认为旧观测；不要误删必要的来源审计机制 |
| 网页导出 | `src/export_web_gm.py` | SQLite 是事实源，JSON 自动生成；保留不可变批次和原始导出字节 |
| SQLite消费M0 | `src/gm_data_access/`、`scripts/gm_data_query.py`、`gm_data_snapshot.py`、文档GM_SQLITE_QUERY_ACCESS | 复用同批审计备份，仅查询静态双库；小结果与SQL聚合。三Web实际连接按玩家最新指令延后，不阻塞工程交付、不冒称验收；本任务不启动M1—M4 |
| DEV10后续财务/知识设计 | `docs/development_tasks/DEV_20261018_10_M1_M2_IMPLEMENTATION_HANDOFF.md`及关联研究 | 设计之后玩家已授权Sol实现，M1/M2本地实现证据查34及独立验收；不将M0原范围限制误读为后续永久禁令 |
| DEV10财务工作台M1 | `gm_data_access/finance_inputs.py`、`gm_core/finance_projection.py`、`finance_scenarios.py`、`gm_workbench/store.py`、`scripts/gm_finance.py` | gm_core仅接纯数据；同批静态来源与独立派生存储。槽序情景不认证签约额度，规则输入不授予游戏执行权；实际状态查34 |
| DEV10知识/策略M2 | `gm_core/knowledge.py`、`strategy_state.py`、`gm_data_access/knowledge_inputs.py`、`scripts/gm_knowledge.py`、`gm_strategy.py`、`web_gm/knowledge/` | 12卡/30参考/19机制按需查询；同批字典映射不授予执行权。30候选UNASSESSED，修订只存调用方分析；详见GM_KNOWLEDGE_AND_STRATEGY_WORKBENCH |
| DEV10 M3分析与候选GM工作台 | `scripts/gm_analysis.py`、`gm_decision.py`；`gm_core/analysis_*`、`decision_*`、`market_negotiation.py`；`gm_workbench/m3_store.py` | 本地工程与直接验收见DEV10_M3A_ACCEPTANCE/DEV10_M3B_ACCEPTANCE及两本M3手册。静态事实/独立判断/双方报价/组合复核/离线交接分开；只读来源与派生库隔离，V3仍生效，V4切换另批 |
| DEV20 M4工程反馈 | `scripts/gm_development_feedback.py`、`gm_core/development_feedback.py`、`gm_workbench/development_store.py`；`web_gm/development_feedback/CURRENT.md` | 复用原workbench存轻量问题/事件，显式导入现有工程报告；CAS人工决定、有界交接和带日期readiness，不自动开发/采集/执行或评价篮球赛果。PR #7已合main，正式状态查34 |
| GitHub 发布 | `scripts/publish_web_snapshot.py`、`config/github_sync.json` | 数据专用提交、不夹带代码；SQLite ZIP 为 Release 附件；同步只看时间 |
| GM v1 | `src/gm_core/`、三个 `scripts/gm_*.py`、`web_gm/GM_DECISION_SOP.md` | 只读事实和确定性计算；提案不代表批准；不自动运行正式 GM |
| 休赛期专项开发 | `src/gm_core/offseason*.py`、`scripts/offseason_*.py`；实际能力与验证状态查文档34及其研究报告链接 | 游戏外竞价、独立批准、再验证合同/名单写回；实机机制先调研，模拟资格不升级为真实来源或执行权，不在月度采集中扩展完整CBA |
| 教练战术 | `coach_locator/codec`、`coaching_reader/executor`、`coaching_batch.py`、文档39/40、DEV07 V2 | gm_core仅离线；旧TEAM writer撤销；整体防守按已认证 UI bulk 组处理，禁止单球员目标；逐字段验收才开放production。19默认字段、同会话来源与双手册交付见34，不把局部验证当整项完成 |

不要因存在函数、表或预留模型就宣称生产路径已完成；独立底层函数也不等于独立采集、入库、审计和发布都可用。

当前受控v2交易入口为 `scripts/execute_approved_trades.py`；名单计数修复后玩家确认公牛/活塞交易成功，支持范围及历史事故见文档37。签约执行源码为 `src/approved_signing_executor.py` 和 `scripts/execute_approved_signing.py`，未运行/测试，待实际签约时验证，见文档38。本地只执行GM给定的交易和合同结果；不开发报价、谈判或其他经营决策逻辑。

### 5. 开发执行流程

**玩家2026-10-20追加规则：任何扩展设计和更多测试都必须先询问并等待明确确认。** 先交代新增范围、原因和预计成本；不以完善、安全或必要验证为由自行扩展。原已批准范围直接完成，证据足够即可交付，不额外开测试轮次。

玩家最新开发规范见 [边界优先与范围内验证](DEVELOPMENT_BOUNDARIES_AND_VALIDATION_POLICY.md)：先定义边界、以高质量实现为主、只做直接相关的必要验证；接受后续实际使用发现问题再修复，不为穷尽边缘风险扩大测试或新增交付门槛。未证实语义保留原始值与UNKNOWN，批准/只读/身份边界不变。

1. **定义本次交付。** 从玩家任务列出具体输入、输出、改动范围和成功条件。小任务直接做；较大任务给简短分批计划，优先交付可审阅的完整路径。
2. **核对既有实现。** 用 `rg` 和有界文件段定位入口、调用方、schema、默认值、实际参数与被废止的旧逻辑。不为本次无关模块做重构。
3. **设计真实的数据契约。** 明确 OBSERVED、CALCULATED、CONFIGURED、REFERENCE、UNKNOWN。偏移来自 CT/修改器时仍须验证当前游戏内存语义；假数据只允许标记 synthetic 的隔离开发材料。
4. **实现。** 保持进程只读路径与写入入口隔离，使用暂存/事务/原子替换保护正式数据。数值逻辑使用纯 Python/SQL。修改公用接口时查看调用方及旧批兼容性。
5. **按任务授权验证。** 用户要求测试/验证时，选择与改动对应的测试或只读实机核对；先说明覆盖范围。无需为了“绿色”运行全套旧脚本；禁止日常 JSON 同步哈希/字段/下载比对。没有实际运行的验证应标未运行。
6. **审阅交付。** `git diff --stat` 后检查相关 hunks。按本次授权决定提交/推送；代码与数据发布分别处理，不把本地完成说成已上线。
7. **更新基线。** 按第 9 节维护持久化索引；交付改变、原因、证据和真实限制。结束本窗口，不自动触发下阶段。

同一故障最多三次具体修复；每次基于新证据或不同假设。三次失败后按 AGENTS 记录失败日志，保留材料，继续独立工作。只读诊断不算修复次数。不要删除证据或反复重复失败命令。

### 6. 数据库、模板和版本升级

任何来源修改至少考虑：采集函数、清理规则、目标表/迁移、来源 manifest、内存审计、自动导出、旧快照、模板、新窗口入口。

- 旧快照是当时事实；新字段缺失不回填假值，不修改旧采集时间或补签新认证。
- 人物/球队稳定身份与运行时地址分离。交易、读档、重启和换名单后不能把同一槽号当同一人。
- 新局从模板建立空数据结构并采集当前局；不继承旧数据库事实、地址或未经批准的球队设置。
- 能用脚本自动完成的重复工作不要交给模型逐条处理。源码维护用确定性脚本可以辅助，运行采集阶段不让模型生成数据。
- 不改变已接受的时间戳同步；保留必要源绑定和内存审计，不能把“不检查 JSON 同步”解释成“所有数据不审计”。

### 7. 当前生产更新决策：只做全量；教练来源等待首次正式全量启用

**玩家于2026-10-18再次确认，并采用之前Codex的建议：所有新游戏数据采集任务统一执行现有`full_verified_v1`全量刷新。** 采集已经脚本化、数据量可接受；取消“单来源生产更新”旧规划。**不开发**`COACHING_ONLY`、`--sources`、`--skip-player-pool`、单队跳过采集、不同来源不同时点混合版本、独立教练latest或源级增量事务。旧本节所有“单来源更新”交付目标和优先待办均已被本条覆盖。

现有`scripts/run_data_update.ps1`一次重新采集所有**已验证**来源；`src/auto_pipeline_ingest.py`已在同一RO会话中采集原生`coaching_tactics`，SQLite存储与审计、`src/export_web_gm.py`全量批次导出、GitHub按需`-Publish`都已在main。未确认/未实现的字段仍保留NULL/缺口，不能把“全量”解释为凭空提供伤病、OVR、单场日志等。

当前仅需玩家下次**明确触发**首次新版全量生产采集，并在其要求`-Publish`时将完整批次同步GitHub；再核对`source_coverage.json`的`coaching_tactics=VERIFIED_OBSERVED_SAME_BATCH`、30队`coaching/teams.json`、`field_dictionary.json`、针对对手的owner文件、SQLite归档和GM同批读取。首次真实发布尚未完成。具体交接见 [DEV-20261018-08 全量更新下的教练源首次启用](development_tasks/DEV_20261018_08_COACHING_FULL_REFRESH_FIRST_PRODUCTION_V1.md)。

开发工作仅在真实全量运行失败时修补具体阻断错误；不得把旧“单来源更新”重开为新需求。**本任务不授权立即运行采集、GitHub发布、GM决策或游戏内存写入**。重发已存在的完整有效批次仍可`REPUBLISH`，它不是新采集。

### 8. Git 与文件操作

不读取、打印或提交 `.env`、令牌、SSH 密钥、凭据。不要暂存 live SQLite、地址缓存、原始探针、日志和备份。开发材料在 `_exports/`，不冒充正式数据。

普通提交只包含本次已审阅改动；不强推、不回退用户改动。发布前核对本次授权、远端与分支；代码提交和数据专用发布分开。公开仓库是当前配置，不自动修改可见性。多行命令写脚本，限制输出，避免整文件/全盘搜索。

本任务没有让你测试时不自行运行测试。文档 30 的全套 unittest 命令可能包含旧假设，不是每次任务必须运行的流程；历史通过记录不可原样转述为当前验证结果。

### 9. 每次相关开发必须维护的基线文件

| 变化 | 必须同步的文件 |
| --- | --- |
| 新来源、字段语义、内存定位/校准、缺口解决 | `config/source_catalog.json`、文档 31/34；采集使用方式变化时更新文档 32/27 |
| 新单项入口/参数、来源依赖、来源时间语义 | 文档 32/34、文档 27/24、真实 CLI 帮助和相关 schema/导出说明 |
| 模块边界、数据库/模板/开发方式变化 | 文档 33/34 与对应技术文档 |
| 执行器、写入字段/身份/编码、批准入口、回读/恢复变化 | 文档 36/28、文档 34 第 8 节及对应字段规范；记录实际验证范围，不把可读或底层可写升级为完整业务验收 |
| 玩家确认新玩法/边界 | `config/gameplay_policy.json`、文档 26、AGENTS 及三份基线涉及部分 |
| 仅采集新批数据 | 让脚本更新数据库与 latest；不为每个批次重写整份基线 |

状态表记录“核对日期、功能版本/证据、可运行入口、当前限制、下一步”；不能只把待办改成 DONE。对已有条目更新并删除已废止的当前指引，历史证据明确标历史。采集、开发、执行三份提示词保持稳定，易变状态集中在文档 34，避免复制出不同口径。执行任务的批准不能替代新写入结构的实现和验收；执行器不足的开发交接按文档 36 第 12 节准备具体材料。

交付前按需求核对以上文件是否需要变更；无关时不改。未解决项写明尝试、证据和下一步，不承诺不存在的自动更新机制。只有玩家触发开发/刷新时维护，不创建后台定时任务。

### 10. 初始化回复与开发回执

初始化最多回复：

```text
开发基线已就绪。
已读取：基线版本 / 当前状态版本 / 当前代码提交。
已知架构：只读采集 → SQLite → 自动 JSON/Release → 网页 GM → 玩家批准 → 独立执行。
当前数据待办：玩家触发首次包含原生教练来源的完整生产采集/按需发布；**不开发单来源更新**。年龄/OVR等仍为玩家允许保留的缺口。
等待开发任务；尚未改代码、运行采集/测试/发布或游戏写入。
```

开发交付简洁列出：完成内容、实际验证及限制、修改文件/提交、是否发布、维护了哪些基线文件。报告不能依赖旧对话才能理解。确实未完成时列出剩余工作，不把文档设计当作实现交付。
