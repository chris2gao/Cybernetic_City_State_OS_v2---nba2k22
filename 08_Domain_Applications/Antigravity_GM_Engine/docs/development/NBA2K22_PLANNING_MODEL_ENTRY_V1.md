# NBA2K22 开发规划模型专用入口 V1

**面向**开发规划GPT、架构设计与派单窗口；不授予编程、合并master、进入游戏、跨模型自动调度或DCR访问权限。2026-10-22。

## 1. 不读全仓的入场协议

读取新仓库最新`master`精确SHA，并按活动OS版本读根`AGENT_WORKING_DISCIPLINE.md`、`AGENTS.md`、`01_os/README.md`、`01_os/开发入口与单窗口任务规范_v1.md`、领域`AGENTS.md`/`domain.yml`。随后只读：

1. [正式开发基线](NBA2K22_PROJECT_DEVELOPMENT_BASELINE_V1.md)：产品意图与已有资产。
2. [项目宗旨](../PROJECT_INTENT_AND_MODEL_DEVELOPMENT_BOUNDARIES.md)：六阶段独立模型、游戏权威与权限。
3. [平行世界架构V2](PARALLEL_BASKETBALL_WORLD_DATA_ARCHITECTURE_V2.md)：旧数据库可以完全重构，重大身份/Schema尚需裁决。
4. [OS路线图](OS_GOVERNED_NEXT_STAGE_ROADMAP_20261022.md)和[机读Backlog](NBA2K22_OS_TASK_BACKLOG_V1.json)：当前计划与依赖。
5. [文档权威索引](NBA2K22_DOCUMENT_AUTHORITY_INDEX_V1.md)：按需追踪历史证据与更早版本。
6. 当前具体任务的前置`completion_pointer`、关键ADR/被引用的字段字典；**不整套读取694条R研究和全部run历史**。

**迁移状态**：业务刷新分支`task/nba2k22-source-refresh-20261022@8bdae1700ecd3ed47d2ad197cca86ace388083bb`、原路线图分支`task/nba2k22-os-onboarding-roadmap-20261022@309161201627dc517ad65450eb34d053ac7ab7b4`在此文档建立时均未集成master；本知识基线分支叠在刷新候选之上。模型每次接手应通过远端读回重新辨别谁已经合并，**不得把三个分支当前候选状态直接变成生产master事实**。

## 2. 判断是否应该派发某项任务

先判断属于：**原生逆向研究 / 工程结构验收 / 数据世界架构 / 数据采集发布 / GM经营决策 / Coach人格 / Player人格 / 游戏修改执行 / OS本身机制**哪一层。不同任务不顺手跨层。

每个业务任务的有效性按以下顺序考虑：

1. **它解决什么玩家目标？** 应当服务完整篮球世界，而非仅给旧GM页面添加列。
2. **当前源码和历史研究是否已具备足够支持？** 查询[40族能力总账](PROJECT_CAPABILITY_AND_DELIVERY_LEDGER_V1.json)及具体原始Audit/Fixes；每个状态分研究、静态、实机、封存、查询、动作和持久性。不要重跑已经结案的R01–R07研究，也不要把R研究当Native验收。
3. **是否是未获批准的重要产品选择？** 例如world/player stable ID、物理数据库切分、真实写入动作或直接修改player growth，都应在Human要求的边界停下。
4. **最小可验证增量是什么？** 尽可能做贯通一个真实Game/Player/Season的纵向闭环；不能为了显得全面一次性建大量无证空表。
5. **能否复用现有工程事实/安全机制？** 可以全面重构旧双库，但必须迁移已证历史、DEV14存档与发布安全、M0查询脱敏和审批回读。
6. **并行是否会产生交叉写冲突？** `WORLD-DATA-ARCH-01`与`NATIVE-ACCEPT-01`可并行，通过身份/字段证据文档沟通；两者分别在独立任务分支，之后Schema建模消费获审结论。

## 3. 最新任务路线（查JSON得准确依赖）

| 顺序 | 任务 | 当前需要的成果 |
|---|---|---|
| 0 | `OS-BASELINE-01` | 业务刷新、能力/知识规划入正式主线前的必要OS审核与Human决定 |
| 1a | `WORLD-DATA-ARCH-01` | World、Season、Save、Generation、Game、PlayerIncarnation、DraftTemplate等概念关系/有效时间 |
| 1b | `NATIVE-ACCEPT-01` | 独立验证AG-NATIVE-01D Game/Box/StatBank/Slot24、生涯索引、Slot44交锋与原生布局 |
| 2 | `WORLD-DATA-SCHEMA-01` | 关系模型、候选SQLite DDL、查询/索引/容量、旧库迁移映射及对比ADR |
| 3 | `WORLD-DATA-PROTOTYPE-01` | 用真实安全Fixtures装载离线纵向原型并验证ID冲突 |
| 4 | `WORLD-DATA-INGEST-01` → `PUBLISH-01` → `QUERY-01` | 源解码、世界身份、验证发布、长期历史、角色权限与GM脱敏 |
| 5 | `WORLD-DATA-MIGRATION-01` → `E2E-01` | 旧库Shadow对账、回滚、跨档/实机合法场景与独立验收 |
| 6 | `WORLD-ACTION-ADAPTER-01`与`WORLD-ACTOR-DATA-01` | 受限执行器身份适配；GM/Coach/Player数据契约 |
| 后续 | Coach / Player / 下一代GM系统 | 真正独立人格和复杂经营产品，各自重新立项 |

这只是规划，**不代表已经派单、验证或赋予模型新增执行权限**。

## 4. 窗口拆分、预算与长期任务

OS的默认是`long_horizon_big_task`：一个连贯、已授权目标下的需求、证据、方案、测试、步骤、执行、修复、提交、证据收尾，可留在一个窗口直到真正停止条件发生。不要每个python文件或一次验证都开启新窗口。

**必须分开**：不同产品目标、重大新的语义裁决、独立审核与执行、Human批准的生产数据库切换/游戏写入。派单、执行与最终独立审核不能由同会话一把包办。Gemini可承担快速探索，Codex承担复杂工程，审核优先独立模型族；具体选型遵守当次OS模型路由，不为降低额度把关键风险审查直接豁免。

**DCR额度约束不可忘**：所有本地Desktop Commander读取或运行都要提前说明所需路径/命令并向玩家重新获得明确授权。计划与资料盘点优先GitHub源证据，不默许本地访问。

## 5. 标准任务包应写什么

一个完整可执行的工作包至少包括：`task_id`、单一明确目标、**当前远端master与任务基准精确SHA**、来源路径及证据、允许变更路径、非目标/禁止动作、验证计划、成功标准、失败/停工条件、独立审核会话、Human受保护动作边界、OS领域run路径和完成指针。

在提交前声明角色分工、Native研究成熟度与Schema已批准程度；使用OS自己的Task Packet/MWU/Model Routing/Workflow机制，不建立一套业务项目自己的第二OS流程。标准交接模板见[任务窗口模板](NBA2K22_OS_TASK_WINDOW_HANDOFF_TEMPLATE_V1.md)。

### ARCH-01应首先讨论的关键设计选择

- 游戏存档复制、回滚、平行世界分叉时如何定义`world_id`和`generation_id`？
- 原生PlayerID、GameID、Slot是否跨赛季唯一？未知时什么情况下拒绝自动归并？
- 一场比赛后统计可能被修订，如何保留先前观察和后续更正，而不无声篡改历史？
- 再次采集同一比赛如何幂等；真实赛季累计与Box互相矛盾如何处理？
- 真实NBA选秀模板与实际世界线中的球员实例怎样关联？
- SQLite单库事务与多文件发布之间的安全边界？哪种物理拆分最可证明？
- Coach/Player/GM何时有权看到哪些观察字段，隐藏Potential如何从源头隔离？

这些决定不要靠历史记录“有个数据库表”就立即冻结，需用反例/实际字段/被审核的身份合同支撑。

## 6. 如何把本窗口的成果留给下一窗口

- 已获认可的稳定设计结论/ADR进入领域`docs/development/`，明确被替代版本；
- 任务实际证据、验证日志、失败与completion pointer进入OS`01_os/07_content/_runs/<run-id>/`；
- 更新能力总账对应条目、历史任务索引（若新增归档）和Backlog任务依赖，保留证据SHA；
- 将新增/弃用文档登记到[文档权威索引](NBA2K22_DOCUMENT_AUTHORITY_INDEX_V1.md)；
- 完成后停止，不自动进入下一产品任务或执行实际游戏操作。

**规划模型最终交付的是高质量可验证的任务上下文，而不是独立替另一模型完成实现或自我验收。**
