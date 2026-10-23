# NBA2K22 平行篮球世界 — OS治理下的下一阶段开发总规划 V1

> **性质**：领域业务开发规划 / 待独立审阅的任务候选。**不授权源码实现、游戏读写、生产数据迁移、OS核心机制修改或合并master**。执行必须使用各自当前OS任务包与本仓最新master SHA。本规划是之后新窗口的总入口，不以聊天上下文作为事实来源。
>
> 新仓库：`chris2gao/Cybernetic_City_State_OS_v2---nba2k22`；领域根：`08_Domain_Applications/Antigravity_GM_Engine/`；工作证据：`01_os/07_content/_runs/<run-id>/`。
>
> **注意分支状态**：最新完整业务候选目前是`task/nba2k22-source-refresh-20261022@8bdae1700ecd3ed47d2ad197cca86ace388083bb`，不是`master`；必须经过OS独立审阅和玩家合并决定后，后续工程才从实际新master建立新分支。此状态必须在未来每次派单时重新核验。

> 2026-10-22 ARCH-01 实际更新：本任务启动时远端 master 已为 407e2134bd2f595477099b2c6e3484c818059fd9，包含上述知识资产；旧“未入主线”段落是生成时状态，不能代替当前 Git 事实。Human 已派发 WORLD-DATA-ARCH-01，候选状态与完成指针见 Backlog；此任务不替 G0 补做独立验收。产品规则固定为每存档独立连续世界，无存档分叉、合并或跨档历史/记忆继承。设计入口：[领域模型](WORLD_DATA_DOMAIN_MODEL_V1.md)、[身份 ADR](WORLD_DATA_IDENTITY_AND_TIME_ADR_V1.md)，均待独立审核。

## 1. 不可妥协的最终产品定义

目标不是“较好用的旧GM数据库”，而是**以NBA2K22本体作为比赛与自然成长权威的平行篮球世界**：

`NBA2K22实际存档/模拟 → 带版本的Native只读观测 → 身份/语义验收 → 世界事实与跨季历史 → 安全角色查询与自主决策 → 玩家批准的有限游戏回写 → 实机回读与审计`。

长期包含30队经营、球员与教练真实原生状态、完整比赛与赛季统计、选秀轮回与多世代生涯、交易合同及财务、球队战术与比赛效果、球员人格和教练人格等。五层技术架构与**采集→数据分析→教练→球员→GM→汇总执行**六阶段逻辑流程并存；后两类独立人格尚未开发，不使用阈值规则冒充自主性。

现有双SQLite、月度表、采集代码、查询接口可以整体重构；保留的是已认证游戏事实、来源可信、跨存档隔离、脱敏规则、审批边界、回读与崩溃安全，不保留旧物理DDL为永久标准。以[平行世界数据架构V2](PARALLEL_BASKETBALL_WORLD_DATA_ARCHITECTURE_V2.md)作为目标设计输入（在源刷新候选合入后才会出现在正式master）。

## 2. 每个任务与窗口的原则

**不是每写一个文件就新开窗口，也不是一个窗口跑完整项目。** OS默认一个窗口只对应**一个目标和一个有界任务包**；一个连贯的系列目标，内部分析、设计、实现、修错、定点测试和提交可以在同一长任务/窗口完成，只要路径边界与委托语义不变、验证证据继续收敛。只有发生**不同目标、独立审阅、权限边界、需要Human做新的负载关键选择、上下文无法恢复**时，才建立新的任务或新窗口。

- **规划/派单窗口（本角色）**：读取项目宗旨、最新架构/任务登记和已结束任务completion pointer；将目标、约束、证据、依赖、交付物和Human边界写入任务包。只协调，不替代执行模型本地大量机械工作。
- **Gemini Flash逆向突击窗口**：只读内存/汇编/fixtures探索、UNKNOWN字段、最小Decoder、UI原生关系与可重放样本；一个实质性对象群可为单次长任务；不能宣布生产验收。
- **Codex工程/架构窗口**：概念和逻辑模型、DDL候选、迁移风险、生产实现、复杂疑难验证；架构设计可委托T2语义选择，但Human保留未委托的重要产品裁决。
- **独立审核窗口**：与执行者/派单者独立的另一会话，优先跨模型族；复读源证据、运行可运行的独立核查、给出PASS/FIX_REQUIRED/REJECT与剩余风险；不能以执行者的“41 passed”取代复验。
- **玩家**：选择世界架构中新的重大战略分歧；确认受保护的master集成、实机修改或其它OS保护动作；触发原生采集、游戏进程及赛季推进。**DCR无论哪个任务都要事前单独明确获准，且说明所需路径、命令、收益**。GitHub读取不构成DCR授权。

每个material任务启动前按当前OS root规范重读`AGENT_WORKING_DISCIPLINE.md`、`AGENTS.md`、`01_os/README.md`、`01_os/开发入口与单窗口任务规范_v1.md`；按需读取Model Routing boot、Minimum Work Unit契约、相应Registry/Validator，不修改core-owned路径。Risk tier、执行模型与参数是**任务时点的路由结论**，下文的模型只是建议。

## 3. 分阶段任务与明确依赖

机器可读记录见[任务清单JSON](NBA2K22_OS_TASK_BACKLOG_V1.json)；这里的任务ID与JSON必须一致。**状态均为PLANNED/WAITING_GATE，不代表已派发、已验收或已获执行授权**。

| 优先级 | 任务ID | 目标与最低可验收交付 | 前置条件 | 建议执行/独立评审 |
|---|---|---|---|---|
| G0 | `OS-BASELINE-01` | 接收当前业务刷新任务候选及OS门禁/玩家合并决定；确保V2、AG01D、FINAL-CODEX证据在新master且有来源 | 独立迁移候选已存在；不预设审核结论 | Gemini小修（若需要）/新审核窗口/Human集成 |
| P0 | `WORLD-DATA-ARCH-01` | 独立存档连续世界的领域ER、业务身份与DEV14技术绑定、事件/状态/累计双时间、来源/敏感性及六反例；禁止存档分叉合并继承 | G0；本轮Human已明确派发，候选见Backlog | Codex T2设计/不同会话独立审阅/Human裁决争议 |
| P0 | `NATIVE-ACCEPT-01` | AG01B–01D（尤其SEASON/StatBank/Slot24、Box和生涯索引）独立验证、候选字段字典、未知与失败矩阵；绝不直接合并旧match-history | G0；可与ARCH-01并行 | Codex工程验证；Gemini提供fixtures不自验收 |
| P0 | `WORLD-DATA-SCHEMA-01` | 在已验身份合同上给出逻辑关系模型、约束、索引、物理SQLite分库方案A/B权衡、候选DDL、真实fixtures的查询样例与旧库迁移映射 | ARCH-01；NATIVE-ACCEPT的已确认部分可分批消化 | Codex主设计/独立ER与SQL审阅/Human决定重大存储拓扑 |
| P0 | `WORLD-DATA-PROTOTYPE-01` | **离线独立实验平台**：最小世界线+player/team+GAME+Box+SeasonTotals+来源/批次结构，真实样本加载/身份冲突与幂等测试；不触及生产库 | SCHEMA-01已评审 | Codex实现/独立验收 |
| P0 | `WORLD-DATA-INGEST-01` | 新原生采集→带版本Decoder→身份归并→字段验证→有界暂存/质量清单；错误批次fail closed | NATIVE-ACCEPT-01 + PROTOTYPE-01 | Codex主工程/Gemini仅支持逆向缺口 |
| P0 | `WORLD-DATA-PUBLISH-01` | 批次发布、崩溃恢复、历史不可覆盖、世代/跨档隔离、来源哈希及跨文件一致性、重复发布不重复写 | INGEST-01 | Codex/独立故障注入审核 |
| P1 | `WORLD-DATA-QUERY-01` | 提供版本化M0风格只读API/SQL视图：球队/球员/单场/赛季/生涯/窗口聚合，GM_SANITIZED及角色可见性，禁止隐性Potential泄漏 | PUBLISH-01 | Codex + 独立权限负例 |
| P1 | `WORLD-DATA-MIGRATION-01` | 原`league_state`/`player_pool`/月度快照与历史记录映射；shadow read双轨对账→可回滚试运行→另批生产切换 | QUERY-01 + Human确认需要影响生产的数据操作 | Codex/审计与Human切换决定 |
| P1 | `WORLD-DATA-COVERAGE-01` | 以游戏UI完整页面和R07 40族为检查范围做逐字段来源矩阵，补赛季高阶、教练、合同财务、士气/伤病、G联赛、新秀报告的证据与优先级 | NATIVE-ACCEPT-01；可与INGEST并行 | Gemini探索/ Codex验证复杂字段 |
| P1 | `WORLD-DATA-E2E-01` | 相同世界线的完整演示：原生只读→真实Box与赛季守恒→封存发布→查询→长期历史、跨档冲突拒绝；实机只读验证需玩家独立授权 | PUBLISH-01 + QUERY-01 + MIGRATION-01 | Codex/独立审核/Human放行 |
| P2 | `WORLD-ACTION-ADAPTER-01` | 将现有限定交易、教练、合同等合法行为对接新对象身份和审批回执，保留游戏读回、Save/Reload未证HOLD；不扩大允许写入范围 | E2E-01；每种真实写入另需Human批准 | Codex/安全审核 |
| P2 | `WORLD-ACTOR-DATA-01` | 分别形成GM/Coach/Player可访问事实、来源、时间口径、数据质量与许可矩阵；先订契约，不把人格算法偷塞数据层 | E2E-01 + COVERAGE-01 | 网页GPT架构/Codex DTO/独立审核 |
| 后续独立产品线 | `COACH-AGENT-01`、`PLAYER-AGENT-01`、`GM-OPERATIONS-VNEXT` | 自主角色架构、职业目标/记忆、互动/拒绝与赛场反馈；分别定产品要求与玩家授权 | ACTOR-DATA-01与对应领域来源达标 | 独立设计及工程窗口，后续另批 |

**依赖的含义**：允许不破坏上游合同的**并行候选设计**；不允许靠未认证候选数据跳过生产发布门。若原生字段仍UNKNOWN，模型可先含待验证扩展位，但不能伪造可查询事实。已验证部分可以分阶段生产上线，不必等所有R07字段完成。

### 第一轮最有价值的闭环（明确范围）

从单个确认为当前存档的GAME开始，贯通：
`World/Season/Game/PlayerIdentity → Game+TeamScore+PlayerBox → SeasonTotals原生对账 → 数据来源/批次 → SQLite只读查询`。

在正式上线前要求：游戏结果及姓名/号码/索引关联一致、相关StatBank有效性与界限合法、单场与赛季对账的适用范围已确认、不可观测事件显式标记而非填零、生成数据带时间与世界线标签；隐藏Potential被隔离。**离线41项测试与Curry16场样本并不能证明全联盟238场已验收。**

## 4. 验收策略：四类门禁，彼此不可替代

1. **Research gate**：来源SHA、原始bytes（受控脱敏）、Getter/布局版本、实际游戏UI交叉证据；把观察、推断、UNKNOWN分开。
2. **Schema gate**：ER基数、主键、外键、游戏时间/观察时间、历史追加与更正、玩家模板/游戏实例区分；DDL能回答核心查询。
3. **Engineering gate**：Python/SQLite测试、负例、故障注入、跨档拒绝、发布回滚、同档Game→Season统计守恒、权限边界；真实测试退出码和完整日志。
4. **Product gate**：GM、Coach、Player需要的信息与角色允许看到的信息已按证据满足；Human再决定是否进入真实环境与master；不能以Schema PASS冒充人格或赛场表现通过。

`DEV29研究完成`、`FINAL-CODEX覆盖对账通过`、`Gemini逆向研究交付`、`游戏实机确认`、`数据库生产发布`应保留独立状态，不能互相升级。

## 5. 跨窗口长期上下文与任务关闭

**单一权威原则**：OS机制规则来自当前`master`上的`01_os/**`，业务产品边界来自`docs/PROJECT_INTENT_AND_MODEL_DEVELOPMENT_BOUNDARIES.md`，数据架构来自V2与后续获批ADR，项目计划与任务依赖来自此文件和JSON，具体任务运行事实来自`01_os/07_content/_runs/<run-id>/`。旧聊天仅为参考，不能覆盖Git证据。

每个新窗口只接收最小上下文：
- 当前远端master SHA + OS四份必读入口；
- 本路线图 + machine backlog对应本任务一项；
- 直属前置任务的completion pointer与被引用的关键ADR/字段字典；
- 不多读整个R01–R07或整个`_runs`。
派单应提供`task_id`、精确基准、工作分支、allowed paths、具体目标、不做事项、OS模型路由/风险、验证计划与应通过的测试、独立评审、结束形态；不得预填未知实际测试数量、输出哈希或文件数。

每次任务的持久记忆至少包括：
- `run.yml`中的合法七值`lifecycle`及closure pointer；
- 机器可读任务包与实际变更/测试/来源；
- 核心设计决定（ADR/字段判准/主键规则）、证据与反例；
- 未解决事项与下一任务依赖及真实Git SHA；
- 通过的结论写入对应领域规范/ADR；**不能只留在completion pointer或聊天里**。

参照[窗口交接模板](NBA2K22_OS_TASK_WINDOW_HANDOFF_TEMPLATE_V1.md)。复核任务必须是**不同会话**，T2/高风险尤其不允许派单窗口兼做最终独立审核。对来源过时、上游冲突或任务范围外新需求，停止本任务并记录后继，不顺手扩散。

### 可以共用一个窗口的系列

- **ARCH-01**可以在一个长窗口内完成问题梳理、概念建模、身份对比、反例设计、候选图和对应修订，最后交独立审核窗口。
- **SCHEMA-01**可以连续完成关系设计、DDL候选、SQL样例和可逆本地fixture验证，统一交独立审核。
- **INGEST-01**可在一个有界任务中完成Source适配、解码、错误阻断、相关测试和提交，前提是依赖合同已确定。
- **审核**永远开独立窗口；**正式生产切换**和**人格产品设计**属于不同目标，不与原任务混用。

## 6. 现在应该触发什么？

**第一步**：等玩家决定是否把`task/nba2k22-source-refresh-20261022`的业务迁移候选纳入正式master；若存在小修，在迁移候选分支上局部闭环，不重做全目录拷贝。计划本身只登记，不视为已合并。

**第二步**：启动`WORLD-DATA-ARCH-01`的独立架构设计窗口。Codex做可复查的概念模型、身份与历史规则，网页GPT作为需求/边界裁决与之后的另一独立审阅会话。明确设计权限不等于批准实施。

**并行**：`NATIVE-ACCEPT-01`可由另一个Codex工作窗口验收AG01C/01D；两边只通过字段/身份证据包交流，不互改任务分支。

**第三步**：上面合同达成后才`WORLD-DATA-SCHEMA-01`，然后最小真实数据纵向切片原型。绝不先批量重写旧库再找证据补位。

> 计划更新时间：2026-10-22。当前用户明确要求安排后续任务与长期记忆；此记录**不是对刷新分支的独立验收**，也不宣称后续任务已经运行。
