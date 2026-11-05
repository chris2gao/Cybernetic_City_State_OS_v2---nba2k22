# DEV-01 · 篮球数据基准 / Data Baseline

**任务 ID**：`NBA2K22-BIC-B1-DEV01-BASELINE-DATA-20261104`  
**领域**：NBA2K22 · Basketball Intelligence Core (BIC)  
**岗位**：`execution`；**建议执行模型**：Codex；**发布/验收归属**：GPT-6 · `decision_architecture`  
**状态**：`PUBLISHED_CONDITIONAL_NOT_IMPLEMENTATION_AUTHORIZED`  
**先决条件**：见同目录 `task_packet.json`；不得以任务发布代替 OS 正式 Stage01 完成门、Stage02 证据、Stage03 结果模型、冻结测试及独立 Human 执行授权。

## 1. 业务目标（不是新建数据库）

在已存在的 NBA2K22 世界数据系统上，交付**可调用、可追溯、可诊断的篮球数据基准接口**。调用方能准确知道：当前球员和球队是什么状态、哪些原生数据实际读到、来自哪份存档/采集批次、属于哪种比赛模式、何时生效，以及哪些字段是未知/过期/仅研究目录，而不是用猜测补齐。

优先服务篮球基准，而非自动出战术；首版固定球员成员构成。**不可另起一套 WorldData、球员数据汇总库或累计统计计算引擎。**

需求映射：`RES-01B-NATIVE-BASELINE-COVERAGE`、`RES-01B-BASELINE-FOUNDATION`、`RES-01B-KNOWLEDGE-ADMISSION`；A0 `SC-01,SC-02,SC-07,SC-08`。

## 2. 已有资产与复用检查（先核查现状，不把旧文档当现行实测）

- `08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype/`：现有 WorldData v24、schema、读数与查询/卡片能力；README 记录 20 Reader families、100 STRICT 表及后续扩展，**需核查当前 master 真实代码与能力，不将 README 声明自动升格为全域实机通过**。
- `08_Domain_Applications/Antigravity_GM_Engine/research/history_source_resolution/worlddata_reference/`：比赛与统计事实引用。
- `01_os/07_content/_runs/run-20261101-nba2k22-vae-native-stats-worlddata-loop-001/07_测试执行/loop_verification_and_regression_report.json`：已有 307/307 测试报告，是当时固定测试证据，不是现行全部字段的普遍认证。
- `08_Domain_Applications/Antigravity_GM_Engine/docs/development_reviews/FINAL_CODEX_NATIVE_IO_COVERAGE_AUDIT_20261021_V1.md`：历史输入源、查询/原生能力、限制与证据等级。
- `08_Domain_Applications/Antigravity_GM_Engine/config/state_io_native/` 与 `src/gm_state_io/`：原生字段/读写模型与来源，必须区分结构存在、历史读回和当前游戏可读。

所有来源列出固定 commit、文件路径与证据等级。若 master 与任务分支成果不一致，建立差异/归属记录，**不擅自 cherry-pick、合并或重写既有功能**。

## 3. 阶段化工作

**P0 · 只读盘点与差异分析（发布后可由任务接收方审阅；不做源代码实现）**  
扫描现有查询入口、球员卡字段、球队/教练/轮换/徽章/倾向/PlayTypes/战术/训练/比赛及历史事实；形成逐领域 `REUSE | EXTEND | MISSING | UNVERIFIED | OUT_OF_SCOPE` 对账。逐个记录“来源真实值是否存在、是否含准确身份/时间/模式/权限信息”；辨别 Research Catalog 与可查询 Native fact。提供可复核的源路径/符号/固定 SHA。

**P1 · 功能增量（仅 OS 与 Human 工程准入后）**  
以现有 WorldData 查询能力为底座提供最小、稳定的 BIC 读取与事实解释入口。逻辑接口（可实现为当前体系的 CLI/API，不强制另建服务）：
- `player_baseline(player_id, save, as_of)`：可得的真实能力、身体条件、倾向、徽章、关键比赛数据及每项来源/等级/未知。
- `team_baseline(team_id, save, as_of)`：阵容与人员归属、教练/战术/轮换设置和球员角色依据。
- `knowledge_status(field_or_mechanism, mode, version)`：来源、字段语义、原生只读实测/研究假设、缺失与限制。
- `coverage_report(save, batch)`：逐领域覆盖、缺口、禁用/受限项、数据新鲜度；**不能以字段存在代替实际读数**。

数据契约必须保留：save_instance/批次/原生身份/赛季或游戏日期/采集时间、观察模式（`Fast Sim` 与 `3D` 分离）、来源路径、数据版本/新鲜度/可见范围/知识状态。不同记录混接时明确 `UNKNOWN`，不把游戏计算值和自造公式混称；不计算原版无法直接读取的累积统计。

**P2 · 可用原型演示**  
使用现成真实只读快照生成**至少两名风格差异明显球员（优先西亚卡姆、约基奇，如当前快照无真实记录则明确不存在并替换为可核实玩家）**及其球队基准卡。卡片包含字段引用、时间、当前徽章、基础能力、未知与支持/阻断推断；展示一次 `field unknown`、一次过期批次和一次身份错误的拒绝。**不能造 NBA2K22 真实球员当前属性数值**。

## 4. 验收与测试（必须产出可复核证据）

1. **对照复用**：新入口确实复用现有 WorldData、Query/Reader 和统一身份；无平行数据库或重复统计引擎。
2. **真实输入可查**：至少一个真实带源批次可端到端读出球员卡与球队上下文；读出来源、模式、时间、知识状态可定位到原始采集单位。
3. **负例 fail-closed**：缺失字段、陈旧快照、混合存档身份、模式未知、隐藏/受限数据分别拒绝或明确降级，不静默填充/泄露。
4. **性能和回归**：重用已有全量采集与批次查询；以实际测量记录查询耗时、重复读取与热点，不为了功能增加重启 Frida、逐字段反复附加、重做百表采集；现有相关回归继续通过。
5. **可诊断能力**：产出可供 DEV-02/03 消费的稳定事实接口及样例 JSON（或既有格式），含 `value + provenance + status + applicability`。

提交：代码增量（若已授权）、领域覆盖矩阵、真实只读样例/脱敏夹具、验证命令和原始退出码、性能/回归报告、限制和未认证字段列表、PRMS checkpoint。不能以文档充分或静态代码扫描单独标记实机验证完成。

## 5. 严格边界

不得直接修改游戏、存档、球员属性/潜力/徽章、交易/合同、正式数据库历史事实；不得跨正式 BIC 竞技信息隔离查询隐藏对手数据；不得在 GitHub 提交大体积 SQLite/备份/压缩分片；暂不重构 SQL 架构，不引入新的数据平台或网络服务。OS 阶段和 Human 授权门分别处理。

**完成门**：交付可直接调用的篮球事实基准 + 精确来源 + 原生事实/未知区分 + 真实读数示例 + 负例与回归，不等于完成整个 BIC。
