# NBA2K22 文档权威、证据位置与上下文恢复索引 V1

> **2026-10-28延伸索引入口**：此V1索引是历史权威与来源导航，最新跨模块总览请先读`../../PROJECT_INDEX.md`和`PROJECT_MODULE_REGISTRY_V2.json`。尤其游戏资料`docs/game_mechanics/`、未并入本分支的`world_data_prototype`独立世界数据库工程、已复制的REA交接和角色批量Native执行架构，请从新索引查准确分支/证据。旧能力快照不因新增文档自动升级为实机完成。


**2026-10-22；领域知识导航，不创造新的OS上下文机制或审批机构。** 本索引用来决定新开发/规划窗口应读哪一份文件，哪些结论已有证据、哪些只是历史或候选。项目状态会随GitHub分支和Player决定改变，以下固定SHA为**历史来源锚点**，绝不代替实时HEAD。

## 1. 权威来源分层

| 优先级/范围 | Canonical来源（相对领域根，OS路径从仓库根） | 解释规则 |
|---|---|---|
| OS全局机制与权限 | `AGENT_WORKING_DISCIPLINE.md`, 根`AGENTS.md`, `01_os/README.md`, `01_os/开发入口与单窗口任务规范_v1.md`, `08_Domain_Applications/AGENTS.md` | 当下`master`或Human指派的确切OS版本；不由领域docs重写 |
| 玩家产品目标和角色授权 | [项目宗旨](../PROJECT_INTENT_AND_MODEL_DEVELOPMENT_BOUNDARIES.md)、后续Human明确更新 | 六阶段参与顺序、自然成长、受控写入。业务文档不可将规划视作Human新的写游戏许可 |
| NBA2K22 项目级开发协作 | [跨模型开发规范V2](MULTI_MODEL_TASK_OWNERSHIP_AND_VERIFICATION_V2.md)，[旧V1](MULTI_MODEL_TASK_OWNERSHIP_AND_VERIFICATION_V1.md) | **V2进入master后为当前项目默认**：GPT负责规划/Human关键决策，Codex唯一工程Owner，Antigravity顺序有界探索；共用本地仓库不得并行。V1保留历史和不冲突的证据/子代理限制。此行不是OS全局机制更新 |
| 世界数据目标架构 | [平行世界V2](PARALLEL_BASKETBALL_WORLD_DATA_ARCHITECTURE_V2.md)及**未来通过审核的新ADR** | V2修订V1中“必须保留旧双库物理Schema”说法；**V2仍为目标设计而非通过的DDL** |
| 当前开发基线与成熟度 | [正式开发基线](NBA2K22_PROJECT_DEVELOPMENT_BASELINE_V1.md)、[能力总账](PROJECT_CAPABILITY_AND_DELIVERY_LEDGER_V1.json) | 只是来源和状态索引，关于某族成熟度优先回到FINAL-CODEX矩阵与新实际验证 |
| 历史代码/成果证据 | [历史任务索引](NBA2K22_HISTORICAL_TASK_REGISTER_V1.json)、`docs/development_reviews/`、`research/native_access/` | 历史审计判断仅针对固定commit和范围，之后AG research与生产状态不能借旧证据冒领 |
| 已完成R系列研究 | `docs/game_mechanics/PROGRESS.md`、`docs/development_reviews/DEV29_R07_TARGETED_INDEPENDENT_RECHECK_AND_DEV29_CLOSURE_20261021.md` | R01–R07研究结案；R07 694项是引用目录，不是694个真实原生字段 |
| 未来任务、依赖 | [OS下一阶段路线图](OS_GOVERNED_NEXT_STAGE_ROADMAP_20261022.md)、[机读Backlog](NBA2K22_OS_TASK_BACKLOG_V1.json) | 当前计划≠任务授权、开始或验收，状态始终从相应run和实际GitHub master核实 |
| 新窗口交接 | [任务窗口模板](NBA2K22_OS_TASK_WINDOW_HANDOFF_TEMPLATE_V1.md)、[规划模型入口](NBA2K22_PLANNING_MODEL_ENTRY_V1.md) | 只加载当次任务直接证据；OS context_management为生命周期权威 |
| 真实运行/验证收尾 | `01_os/07_content/_runs/<run-id>/`、`run.yml`与`completion_pointer` | domain-owned run traffic；证据不应复制全文进业务baseline或README |
| 旧网页GM运行记忆 | `docs/35_WEB_GPT_BASELINES_AND_MEMORY_PROTOCOL.md`、`web_gm/baselines/`、`web_gm/memory/` | 与开发知识索引职责不同，不删除/覆盖角色实际长期经营记忆 |

## 2. 当前重要工程证据锚点

| 文档或源码 | 精确证据与使用限制 |
|---|---|
| `docs/development_reviews/FINAL_CODEX_CAPABILITY_MATRIX_20261021_V1.json` | 40族/20缺口，审计提交`d1038811ecee3a6b35a5d9c4787c67bf65456438`；来源主线较早，不包含后续01D能力验收；矩阵轴独立 |
| `docs/development_reviews/FINAL_CODEX_NATIVE_IO_COVERAGE_AUDIT_20261021_V1.md` | 静态来源、历史批封存与查询证据；旧未脱敏批不得当现行GM生产输入 |
| `docs/development_reviews/FINAL_CODEX_DEV28_GAP_REGISTER_20261021_V1.md` | 20继承工程缺口及候选DEV28工作包，不能误判全已关闭 |
| `docs/development_reviews/FINAL_CODEX_MATCH_HISTORY_BRANCH_AUDIT_20261021_V1.md` | 旧match_history候选不建议直接集成；需要修事务、错误回退、边界和真实实机证明 |
| `research/native_access/AG_NATIVE_01*/` | 01至01D研究对象/Decoder/Fixtures来自`21d62ec9e04b86a1f737c1500ea2f41c34583215`；独立Codex原生验收尚待完成 |
| `src/gm_state_io/`、`src/gm_data_access/query.py`、`database/schema.sql` | 第一代采集/状态/查询的确实存在源码；V2允许全面重构物理结构，必须保留已证安全与数据语义 |
| `docs/34_BASELINE_CURRENT_STATE.md`、`docs/33_DEVELOPMENT_BASELINE_PROMPT.md` | 历史滚动状态/交接资料，可能含未更新的PR或旧架构措辞；若与新的玩家V2指示冲突，以最新明确指示为准并记录revision |

**历史分支参考**：旧仓库`chris2gao/nba2k22-gm-engine@eb275a46765c758fa5ce6aaf6ca8dae217baaf97`为业务正式main基线，原生研究`@21d62ec9...`，Final-Codex`@d1038811...`；新仓库实际业务刷新候选`task/nba2k22-source-refresh-20261022@8bdae170...`。不要用旧仓库作为今后任务默认写入目标。历史SHA能溯源，但不能自动代表新master已合并。

## 3. 一致性与版本规则

1. **每个长期设计决定一个canonical ADR/契约**：业务V2/新已审核ADR持有具体身份Schema；README、基线、任务回执仅链接并摘要，禁止平行定义不同的GameUID。
2. **状态总账不盖过原始验证**：状态`source_discovered/fixture_passed/independently_accepted/published/queryable/game_write_verified/save_reload_verified`是不同能力维度。以具体run、代码/数据库、真实来源时间判定，不以“目录存在”“历史报告已完成”替代。
3. **源内容和历史保留**：不要删除或默改旧R资料、旧DEV验收或AG01C早期误判；新文档说明版本覆盖关系（如Slot44从赛程改判交锋矩阵），保留最早出处。
4. **停用/替代文档**：保留旧文件，并在权威入口标`SUPERSEDED`及替代ref，不复制全部内容。具体文件的归档遵OS Context Working Set规则。
5. **未知事实显式返回**：没有实机观察填`NOT_OBSERVED`；原生布局不明用`UNKNOWN`；只有模拟测试则标`FIXTURE_ONLY`。未知不是零，也不是没实现的证明。
6. **每次任务合入后维护索引**：检查新/替代的规范、新产出的run pointer、能力总账与依赖表；仅更新实际涉及的行。归档与工作集的生命周期由`01_os/03_mechanisms/context_management/`的活动机制负责。

## 4. 按问题恢复上下文（最小读取集）

- **我是NBA2K22开发规划/执行模型**：在OS启动文件后读取领域`AGENTS.md`所指向的[当前项目级跨模型规范V2](MULTI_MODEL_TASK_OWNERSHIP_AND_VERIFICATION_V2.md)；旧规划中的Codex/Antigravity并行或先全研究再开发要求，以最新Human决定的顺序结对与原型驱动为准。
- **我是新开发执行模型**：读OS入口 + [开发基线](NBA2K22_PROJECT_DEVELOPMENT_BASELINE_V1.md) + 当前task packet + 前置完成指针；需要具体能力时定位[40族总账](PROJECT_CAPABILITY_AND_DELIVERY_LEDGER_V1.json)中的1项。
- **我是新规划模型**：读OS入口 + [规划入口](NBA2K22_PLANNING_MODEL_ENTRY_V1.md) + [路线图](OS_GOVERNED_NEXT_STAGE_ROADMAP_20261022.md)/backlog对应节点 + 直属上游设计裁决。
- **我想知道开发完成了什么**：能力总账→FINAL-CODEX机器矩阵→具体源码/验收报告和当前新run；不信“任务名称”或全局DONE。
- **我想继续GAME/Box研究**：AG-NATIVE-01C/01D原始记录、测试、`CODEX_HANDOFF`及新Codex验收run，不读全部R07分卷。
- **我想实现世界数据库**：平行世界V2→ARCH-01的获审身份ADR→Schema-01关系模型→Native-ACCEPT字段证据→变更/迁移任务包。
- **我需要访问本地**：先具体向玩家请求DCR授权，得到明确批准后才操作；本索引与任务计划不授予权限。

## 5. 迁移状态和本知识版本限制

此文档自身属于`task/nba2k22-project-memory-baseline-01`候选。该分支基于仍未集成master的源刷新候选`8bdae170...`，因此**应先处理源刷新，再按OS独立审核与Human决定是否集成本知识任务**。规划分支的三份路线图/任务模板被原样移入本候选，以减少重复与碎片化；仍须核验当前master及OS签入路径。

本索引本身无法证明当前本地SQLite/live游戏数据。当前任务未获得DCR授权，独立OS本地managed verify不在这里假装已经执行。
