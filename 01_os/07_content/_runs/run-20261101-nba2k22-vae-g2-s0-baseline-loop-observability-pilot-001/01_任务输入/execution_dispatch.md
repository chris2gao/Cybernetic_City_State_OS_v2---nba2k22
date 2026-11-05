# VAE G2-S0 · 单Pilot证据基线与 OS Loop 可观测性首个实测样本

Task: `NBA2K22-VAE-G2-S0-BASELINE-LOOP-OBSERVABILITY-20261101-001`
Role: `execution`; Executor: Gemini（实际型号及验证环境据实记录）。
Branch: `task/nba2k22-vae-g2-s0-baseline-loop-observability-pilot-20261101`
Base: `63f86a26e8cee99f40eedc1312f045b5f60d0c37`（上轮 G1 真实全量采集候选，不是master）。
Packet: `01_任务输入/task_packet.json`。

## 0. 已确认范围 / Human 裁决

Human 已批准 Core OS **开发 Loop 可观测模型 v0.1 的3–5任务先行试用**。Core试用方案分支：
`task/core-development-loop-observability-model-20261101`，批准记录commit：`f3ae6b83897c04f6ee7758a9b32fc8ea2d06cea5`，模板位于该Core Run `06_执行/loop_observability_contract_candidate_v0.1.json`。

本轮为该模型**首个新任务实证样本**。它不修改Core canonical规范，不改变七阶段Workflow、Human双检查点、真实停止条件、研发权限或系列审核排期。

当前 G1 Full 首轮运行已经上传可信候选证据：批次 `3a75c0e19302`；16族新来源入库、4年度安全跳过、42→58 Capture Units；238个现有Calendar Sim完赛比赛、476队Box、6133球员Box；含36个FULL_NATIVE_BOX、202个 REUSED_FROZEN_BOX。具体`live_full_capture_sql_reconciliation.json`反映：
- 222/238 场 Player points vs Period points **精确一致**；
- 228/238 场进入“±3分”分类（包含上述222场）；
- **10场超出3分**。16场差异的真实机制尚无独立证据，不得写“全部都是2K技术犯规/自投”。
- 各新unit `completeness=PARTIAL`，意味着已注册Reader成功提交，不等于NBA2K22所有原生字段全覆盖。

同时，238是**联盟总场数**，并非任何具体目标球员/球队的S0有效场数；不能用整体238直接判三组Pilot全部高置信度通过。上轮G1的真实“全量采集→SQLite→导出”成功可以接受；G2设置实际修改与日历模拟赛后效果验证尚未开始。

## 1. 下一目标：从G1成果形成一个可执行的 G2 单Pilot真实S0

**优先从原M5三组Pilot选择一个**目前现有数据能可靠支持的，理由是原生来源、每目标可比有效场数、数值/字段稳定性与REA readback候选。可优先考虑`TENDENCY_NATIVE_001` Shot 对 FGA/Shot-share 的Calendar Sim分析，但如果现场证据显示另一个Pilot显著更可执行，说明后选择；**不要把 `MET_TOUCHES_NATIVE`或假定USG%原生已采作为必要完成条件，也不能说 ePOSS 是实际Touches**。

先读取旧M3 38 ID / M5 Pilot 实验合同与现有VAE导出，**从本地已采集的同一 Human 绑定存档 SQLite**筛选：
- `save_id`/loaded_filename/game_mode/season_id/start-end native game date/observed_at；
- 真实对象（player_id/team_id/coach），准确的Reader映射和字段ID；
- 该对象在S0设定稳定窗口内的**有效Calendar Sim比赛数**（目标10场，只按该对象计，不按联盟总238）；
- 对手、主客、阵容、伤病、轮换、世界Sliders/normalize、教练设置及历史来源更新的可观测控制；不可观测的列UNKNOWN；
- 每场原生Box `selected_unit_id`、冻结复用及时间；某场或单字段来源缺失时返回PARTIAL并从相关指标验证中剔除，保留原因；
- 分离赛季总计与单场，真正日历Sim与3D来源不得合并；不得推断未干预历史没有设置变化；
- 先建立至少1个合理的前测对照/可证伪实验假设，**不要随机宣布效果显著**。

## 2. 分数差异与来源指标不能装作已闭环

利用只读SQL，输出16个原生比分/活跃球员得分不一致的比赛ID和两侧差异：其中6个差异<=3，10个差异>3。逐场对齐原生Header、状态、比赛Box和来源unit，判断是评分归属、DNP、参与者完整性、旧冻结等哪类可证明问题。若证据不足，标`CAUSE_UNKNOWN`，这些比赛可保留供历史分析，但有关分数守恒/球员效率的Pilot统计需显式质量标记或排除。不要为了“一切绿”任意设容差或自动修正原始数据。

`manifest.json` 的`READY`需要按具体数据产品和**本次选中source units**区分实际来源；现有代码基于整个`capture_runs`的等级和空值硬编码，应至少在新Pilot证据包中真实标明被采用unit的grade、completeness和样本；仅在它导致具体错误时做最小代码修复，不重新设计WorldData。

## 3. G2 Ready 是设置读取和验证路径，不是已经修改

通过既有REA文档/授权范围内代码，只读核对将来一项设置的：
- exact canonical `setting_field_id`、存档/实体/旧值；
- Getter或原生读回证据级、Setter现有实现成熟度、操作边界、原生状态回读和可能由游戏覆盖的风险；
- 提议调整值作为`proposed_value`，但**不得在游戏里执行Setter、改内存、改存档、推进日历、运行模拟**；
- 正式G2实验三块：S0当前未干预已有数据，S1未来Human批准的单变量调整后游戏事件，S2后续持续Calendar Sim观测。输出最小SQL/证据连接规则、缺样本时暂停条件。
- 置信度来自样本与对照质量，不能拿任意 +15 倾向点与 +5% usage百分点算出“成功”；
- 不擅自要求每个篮球机制先研究完；仅在该Pilot关键数据足够时才提请Human授权下一步。

## 4. OS Loop 可观测性 v0.1 首个采样要求（必交）

本任务默认循环：**诊断选择增量 → 开发或研究 → 执行验证 → 对比分类 → 修复继续或正确停止**。

从本任务的第一轮真正工作起，在 `06_执行/loop_iterations.jsonl` append-only记录每轮，必须有：`iteration_id`、`trigger_type`、`trigger_ref`、`bounded_objective`、`actions`、`sha_before/after`、`test_receipts`及真实exit code、`outcome`、`decision`、`next_trigger_or_stop_ref`。

可用触发类别：`PLANNED_INCREMENT`、`TEST_FAILURE`、`REGRESSION`、`NEW_PRIMARY_EVIDENCE`、`HUMAN_FEEDBACK`、`REVIEW_FINDING`、`HYPOTHESIS_REFUTED`、`SOURCE_OR_ENV_CHANGE`、`DEPENDENCY_UNBLOCKED`、`OTHER_EVIDENCED`。

每个`test_receipt`保留命令/退出码/日志；测试前后Failure Set、目标覆盖及新UNKNOWN据实记录。没有实际遥测时耗时/Token/成本为null。

**注意计数**：
- 有界目标 + 实际行动 + 验证 + 决策组成一轮；多次命令/测试/提交不自动算多轮；
- 无新证据的原样重跑只作为重复尝试事件，不计有效Loop轮次；
- `internal_development_iteration_count`与`post_first_delivery_remediation_round_count`分开；后者遵循现行Core §11交付后整改预算；
- task收尾必须产生 `08_结论/loop_summary.json`：总数、触发类型分布、有效结果、回归/无效重复、真实Stop Class及其原因/来源证据、剩余未知与何时可重启；不将模型自检冒充独立审核。
- 本轮不要把历史G1任务A0–A8标题事后强行算成9个Loop；从这次正式采用的新任务开始统计。

## 5. 测试、边界与完成

只允许写 `08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype/**` 及本Run。既有SQLite是单存档历史事实库，只读查询（需样本可在临时副本测试）、不可上传私有数据库、游戏Save或原始protected内存。不能修改Core、NBA master、旧Run；必要研究资料只读。

Gemini通过本地GitHub已有来源+当前本地数据库进行普通查询与执行；**禁止普通查询使用GPT的RDC**。当前不得在游戏进程操作、更改任何设置、推进比赛、启动后台服务、部署自动调参。

交付 `s0_selected_pilot_baseline_and_sources.json`、`one_pilot_g2_rea_preflight.json`、`score_discrepancy_scope.json`、`loop_iterations.jsonl`、`loop_summary.json`、`s0_pilot_reconciliation_tests.json`和`completion_pointer.md`，再提交到本工作分支、远端回读精确SHA。

**终止时请独立报告两件事**：
(1) G2-S0 single-Pilot `READY / PARTIAL / NOT_READY`及为什么；
(2) Loop观测试点真实迭代次数、类型和停止证据。

无需为普通局部失败开启独立审核。涉及设置写入成为承重真实决策、正式集成或Human授权边界，遵循 Core 现有§9/§11，进入下一门前另外处置。
