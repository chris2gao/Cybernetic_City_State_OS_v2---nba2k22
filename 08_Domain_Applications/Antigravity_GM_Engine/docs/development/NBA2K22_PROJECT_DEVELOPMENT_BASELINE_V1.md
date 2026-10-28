# NBA2K22 项目正式开发基线 V1 — 开发模型必读

> **2026-10-28当前项目总览入口**：[PROJECT_INDEX.md](../../PROJECT_INDEX.md)和[PROJECT_MODULE_REGISTRY_V2.json](PROJECT_MODULE_REGISTRY_V2.json)。此V1为2026-10-22的事实/任务快照，不能取代PR #17集成的REA原生调用、独立世界数据工程分支和PR #18的身份能力→批量指令→Native执行新架构。旧数据库物理Schema和“手动热写”不是当前最终目标；**本次改变执行规划，不变更数据采集链**。


**性质**：NBA2K22领域长期工程知识入口；对当前新OS仓库中的候选业务源码做证据索引，**不构成独立源码验收、生产架构迁移或游戏写入许可**。更新日：2026-10-22。

> **仓库与源版本**：正式开发仓库`chris2gao/Cybernetic_City_State_OS_v2---nba2k22`；领域根`08_Domain_Applications/Antigravity_GM_Engine/`；本索引构建在迁移候选`task/nba2k22-source-refresh-20261022@8bdae1700ecd3ed47d2ad197cca86ace388083bb`之上。**截至此基线生成时该候选与规划分支未并入master**；日后新任务必须实时重新读取`master`及各证据分支，不准把当前时间的候选状态写成未来永久事实。此文档所在分支也未自动获得master权威性。

## 1. 我们真正建设的产品

目标不是仅给玩家推荐交易的GM助手，而是**以PC NBA2K22离线MyLEAGUE为比赛、游戏状态和自然成长权威的“平行篮球世界”**。实际赛果由游戏产生，外挂用带证据的原生读取收集真正发生的事实，在独立世界线身份下保存跨季历史，提供GM/Coach/Player等自主模型的角色可见信息，最后仅将玩家批准的合法动作写回游戏并确认实际读回。AI的推论不能伪造游戏事实。

系统五层：**原生游戏权威 → Native只读来源/Decoder → 世界数据平台（原生证据、事件、状态、累计、历史）→ AI独立参与者/扩展规则 → 授权执行器/回读**。

业务执行有另一套六阶段目标（与五层技术架构不可混淆）：**采集 → 数据分析 → Coach → Player → GM → 汇总/审批执行**。Coach和Player**独立人格尚未完成**；教练参数能读写不等于独立教练模型已经可以自主决策。历史1984–2020选秀轮回是真实游戏中球员模板来源，模板ID不能混作游戏内新生涯的PlayerIncarnationID。

权威意图：[项目宗旨与角色边界](../PROJECT_INTENT_AND_MODEL_DEVELOPMENT_BOUNDARIES.md)；新目标架构：[平行篮球世界完整数据架构V2](PARALLEL_BASKETBALL_WORLD_DATA_ARCHITECTURE_V2.md)。**旧双库及采集容器可重构**；保护的是游戏事实、存档/代际隔离、来源和时间、封存一致性、Potential脱敏、Human批准、Readback和故障恢复能力，而不是旧表名、文件数量及接口。

## 2. OS控制面与领域业务面

- OS机制入口：仓库根`AGENT_WORKING_DISCIPLINE.md`、`AGENTS.md`、`01_os/README.md`、`01_os/开发入口与单窗口任务规范_v1.md`；领域规则`08_Domain_Applications/AGENTS.md`及`domain.yml`。
- **01_os/**提供Workflow、机制、上下文、路由、任务编排、验证和发布纪律；不得把通用机制复制到`08`，也不得擅改core-owned内容。
- **08_Domain_Applications/Antigravity_GM_Engine/**负责业务代码、研究、项目事实、角色规范与已获采纳的设计决定；正式任务运行证据保存在`01_os/07_content/_runs/<run-id>/`。
- 完整的项目任务图：[OS开发路线图](OS_GOVERNED_NEXT_STAGE_ROADMAP_20261022.md)与[机读任务清单](NBA2K22_OS_TASK_BACKLOG_V1.json)；[新窗口交接](NBA2K22_OS_TASK_WINDOW_HANDOFF_TEMPLATE_V1.md)。任务运行生命周期必须遵守OS七值enum；不要借用业务能力成熟度标签当OS任务状态。
- 默认**一个连贯可授权目标一个任务包/窗口**，窗口内可以完成多步骤和确定性修复。**最终独立审核与执行/派单必须隔离会话**。Human保留产品关键语义裁决、master合并和未预批准的保护动作。
- 当前窗口不应通过DCR读取本地仓库或运行命令；每次使用DCR**必须事前另行向玩家请求具体授权**，说明路径和命令；仅通过GitHub远端可以解决的任务不消耗DCR额度。

## 3. 已有资产与真实成熟度（摘要）

完整40族**唯一机器来源**：[FINAL-CODEX矩阵](../development_reviews/FINAL_CODEX_CAPABILITY_MATRIX_20261021_V1.json)，本项目建立的[能力与交付总账](PROJECT_CAPABILITY_AND_DELIVERY_LEDGER_V1.json)只是带来源索引，**不重新判断40族已经DONE**。历史[任务文档索引](NBA2K22_HISTORICAL_TASK_REGISTER_V1.json)不凭文件名断言完成。

| 领域资产 | 已有证据或代码 | 不得越界的结论 |
|---|---|---|
| 世界采集/存档/批次 | `src/gm_state_io/`的Registry/Codec、save/generation控制、DEV14双库暂存/安装；`src/auto_pipeline_ingest.py`，旧`database/schema.sql` | 第一代工程可迁移，不代表所有对象已采集或新V2物理架构已实现 |
| 已有封存SQLite与M0查询 | `src/gm_data_access/query.py`和历史Oct18封存只读证据 | 所选封存批没有GM_SANITIZED Potential标识，旧批**不可作为新GM正式查询入口**；未观察的比赛表不能由累计补造 |
| 球队/球员/教练/资产部分字段 | `config/memory_field_profile.json`、`src/source_extensions.py`、`src/gm_core/`及教练、合同/财务源码 | 逻辑字段数≠原生对象数；教练19默认/训练与设置≠实时教练战术效果或独立人格 |
| GM基础经营与已有有限执行 | 部分名单/财务/选秀权/球队信息、DEV10 M系列、BPTI、`src/gm_state_io/executor.py`等 | 历史v1/v2不同回执不可互相替代；普通球员能力/Potential/Badge不得任意改写；签约Gate仍关闭 |
| R01–R07游戏机制研究 | `docs/game_mechanics/PROGRESS.md`、R07分卷和正式独立研究结案 | 694是研究引用、40是能力族、20是继承缺口；研究完成≠游戏原生读取和写入完成 |
| AG-NATIVE-01–01D原生深挖 | `research/native_access/` 的Getter/Slot、纪录簿、交锋矩阵、SEASON、24B Box/48B Stats、球员生涯fixture | 研究样本有很高价值；Curry16场与累计18项一致并非全部238场验收，赛程GameID/StatBank边界、原生当前验证与生产库集成待Codex |
| FINAL-CODEX审核 | `docs/development_reviews/FINAL_CODEX_*.md/json` | 40族历史工程审计：16历史部分、7已实现未发布、3未合并候选、1签约阻断、13参考/未知；审计基准早于AG01D，不能外推成熟度 |
| 多角色系统 | `docs/35_WEB_GPT_BASELINES_AND_MEMORY_PROTOCOL.md`、`web_gm/`、`src/gm_core/` | GM已有部分决策辅助；独立Coach、Player和更大规模角色生态属于**未来独立立项** |

对可查询数据必须逐维标出：**原生来源是否发现、是否真实采集、字段是否解码、身份是否验证、是否进入发布批次、是否通过脱敏/权限、是否有实机UI交叉证据、是否可执行、是否Save/Reload实证**。不能用单一DONE代替这些轴。

## 4. 本阶段为什么先建数据世界

Player、Team、Season、Game、StatBank、历史选秀池及不同游戏阶段拥有不同身份和生命周期；旧库将能力、合同、伤病、赛季统计揉进月度表、只用赛季年份标示Season及某些名字关联，无法成为长期平行世界终局Schema。

V2需要：`world_id/save_instance_id/generation_id/season_id/game_uid/player_incarnation_id/draft_template_id/team_identity_id`、游戏内有效时间与实际采集时间、真实比赛事件（可订正，不随快照覆盖）、球员/教练/合同状态观察、原生赛季累计、原始证据、派生统计、AI决策与动作回执各层分离。SQLite仍优先，但允许重新评估世界库/原生证据库/控制库文件分割和事务发布。

**不能先把研究Decoder塞入第一代双库**。正确顺序为：领域模型与原生独立验收并行 → 关系Schema/身份合同 → 离线垂直原型 → 统一采集/校验 → 发布/查询 → 旧库安全迁移 → E2E与角色接口。新V2概念模型和正式生产DDL**还没有验收**。

## 5. 开发模型的权限与事实纪律

- Gemini Flash优先快速实机只读逆向、Getter与数组调查、可追溯fixture及小Decoder；Codex优先架构、复杂验证、独立工程质量和生产集成。规划GPT定义产品约束、任务拆分、证据门槛；模型选择仍由**当前OS模型路由**确认而非硬编码绑定。
- 一条原生记录至少区分`NATIVE_VERIFIED`、`UI_CROSS_CHECKED`、`DERIVED_WITH_FORMULA`、`STATIC_CANDIDATE`、`UNKNOWN`；不可把UI页面名称推断为物理SQL表。
- 不把当前本机进程绝对地址当永久身份，不把PlayerID、Slot、姓名或年份当然当跨档主键；不把模拟联赛总计倒推不存在的具体单场事件。
- 不因`pytest passed`宣称已在当前游戏实机完成采集，不因API存在宣称有真实游戏可执行回读；事件未观察要返回NOT_OBSERVED，语义不明要UNKNOWN。
- 真人玩家具体批准前不触碰游戏内存写入、模拟推进、签约/交易等状态改变，也不修改生产SQLite或Save/Reload。研究样本不能泄露真实Potential。
- 旧仓库`chris2gao/nba2k22-gm-engine`只作精确历史证据来源；新工作、任务和权威业务路径在OS仓库。

## 6. 新窗口启动和任务收尾的最小契约

**新开发窗口**：实时读取master SHA、OS四份启动规范、领域AGENTS/domain.yml、本文件、任务清单中指定的一项及前置任务completion pointer/ADR；只在需要时读40族矩阵特定元素或原生Fixture。先按OS建立任务包、风险、allowlist、验证计划、停止条件和独立审核角色，再执行已获授权的目标。

**规划窗口**：读[开发规划专用入口](NBA2K22_PLANNING_MODEL_ENTRY_V1.md)、此基线与[文档权威索引](NBA2K22_DOCUMENT_AUTHORITY_INDEX_V1.md)，只组织任务，不越权代替另一个窗口验收或写游戏。

**任务完成**：业务决定写进对应长期ADR/Schema/Capability ledger；真实运行、测试、源SHA、风险、completion pointer进入OS run；任务依赖和成熟度再更新。只有**业务长期共识**进领域docs，机器运行流量不重复造在业务docs。根据OS独立审阅及Human集成结果更新状态，不能直接把候选文档标为master权威。

> 下次维护触发：V2架构/AG原生验证获得新结论、业务正式Schema和入口上线、GM/Coach/Player新增真实权限或OS新版机制改变。每次仅修改受影响记录及入口指针，不全文复制和重复审计。
