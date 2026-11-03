# Human 补充裁决 · WorldData 第一阶段架构继承与人工一键全量采集

**适用任务**：`NBA2K22-VAE-CALENDAR-SIM-G1G2-READINESS-20261101-001`；这是一份对现有 A0–A4 任务的**范围澄清**，不是新任务、不是新采集系统，也不改变其它禁止的游戏写入边界。

## 1. Human 要求的“自动化”含义

Human 不希望游戏在后台被持续监控，也不希望每次采集都占用 Gemini 额度、让模型逐字段搬数据。

**目标是**：由 Human 主动触发一次 → **本地既有程序**自动识别当前游戏进程/既定存档 → 调用已有 WorldData 20 族 Reader 完成当次全量（按已注册来源和年频策略）采集 → 校验/留存到本机单存档 SQLite → 自动执行版本化 SQL/查询模板 → 输出 VAE 所需规范化数据和带来源清单 → Gemini/其它模型仅分析现成的规范化数据。

这里的 `automatic` 是**一次人工触发后的完全自动化流水线**，不是后台常驻监听、自动推进日历或为每一场比赛重新调用模型。

## 2. 必须继承的第一阶段实际架构（准事实来源）

开发前阅读：
- `08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype/BASELINE_HANDOFF.md`
- 同目录 `README.md`、`refresh.py`、`cli.py`、`schema_model.py`、`schema.sql`、`field_dictionary.json`、`engine.py`、`query.py`、`fact_queries.py`、`observation_scope.py`、`tests/`
- `01_os/07_content/_runs/run-20261024-nba2k22-world-data-implementation-002/06_执行/increment37/` 的 `source-coverage.json`、`field-maturity.json`、`query-api-catalog.json`、`verification-report.json`。

冻结参考：`17ec1cea88c2bb6c36264792f70c94bef9a8bdb4` 的 WorldData v24（**100张 STRICT SQLite 表、1,775列、20族 Reader**），其本身是常规赛工程候选，非已完成全部生命周期的正式认证。

必须保留/复用：

1. **单档单库**：Human 绑定的 `save.json`、独立 `world-v24.sqlite`、`save_id`，严禁MC与MyLEAGUE存档混库或以PID/同名球员自动判定存档身份。
2. **Reader/SOURCES 注册表**：`refresh.py:SOURCES` 中20族确定性顺序，schedule 建立身份；16个普通来源随调用按策略重采，4个 annual 来源（records、honors、league-history、staff-history）保持每独立存档/游戏赛季年一次策略。新字段只能扩展合法既有 Reader/Codec/事实表与字段字典，必要新增来源应先证明旧族不足且完整注册，不得平行造另一套脚本或数据库。
3. **来源账本与事务**：`capture_runs` / `capture_units` / `source_artifacts` 的不可变来源批次、原始摘要、来源等级、completeness、单族原子提交、失败部分保留/恢复；`refresh-world` 对每个来源验证 `COMMITTED_SUCCESS_VERIFIED` 回执。不得凭成功打印或UI显示宣称完整。
4. **历史/时效**：append-only，不覆盖旧值；`observed_at`/ `--as-of` 是**采集时间**而非游戏日期；区分原生赛季/阶段/日历日期，最新值按允许的成功单元与source解释，不混跨批次、不隐式拼凑同一时刻快照。年度来源策略、`--data-updated`、`--resume-report`、全新输出目录保持原语义。
5. **既有Query/Export**：先用 `fact-fields`、`query-facts`、`export-filtered`、卡片/历史页/leaderboard和现有typed SQL API；允许增加**固定、版本化、参数化**的 VAE 查询/导出配置，但不要再造查询层。Owner-only原始证据和隐藏Potential不进入模型公开数据包。
6. **兼容、回归与迁移**：不能重写旧 v24库、历史数据或既有键；确需新表/DDL时备份后copy-upgrade、保留旧事实、跑SQLite integrity/FK、来源和基线回归。不要将已注册的20族和100表误称为“所有游戏原生统计全部可采”。

## 3. 现有任务 A1/A2 的调整方向

A1 优先实现**单次显式触发命令/包装脚本**（命名由实际现有CLI设计决定），在本地可离线无模型参与地执行，输入仅需已绑定存档/已加载游戏文件名和必要的输出或配置。

在内部调用现有 `refresh-world auto SAVE_DIRECTORY LOADED_FILENAME NEW_OUTPUT_DIRECTORY`（全族默认），适用时按已有来源节奏处理 `--data-updated`、`--resume-report`。脚本自动执行绑定/进程/版本/新完赛识别、已注册20族采集及原始来源校验；不要求Human或模型分别操作20个Reader。重复触发可追加真实观察，但对`新比赛数量`、VAE指标和导出必须去重并区分新旧/相同源，不能重复计一次比赛。

A2 增加**固定规范数据提取流水线**：从本地单档SQLite生成至少三个可复用、版本化的VAE数据集：

- `calendar_sim_completed_game_player_team_metrics`：逐场比赛/球队/球员基础观察，含游戏身份、final、Calendar Sim模式、场次、日期、对手、来源批次/时效、指标完整性；
- `vae_setting_context_snapshot`：当前倾向、球员能力/健康、教练/战术/阵容和关键世界设置的可获取只读值，按来源成熟度/时间分离；尚未可采的字段为UNKNOWN而非补零；
- `vae_experiment_evidence_input`：S0/S1/S2比较所需版本化manifest，包含实验ID、设置候选与将来REA读回占位、前后观察、混杂变量、口径/指标来源；本任务绝不实际改设置。

所有导出要有固定SQL或配置版本、指标字典版本、schema版本、save_id、game-mode、source_units、采集时间界限、数据哈希/行数、缺口、`READY/PARTIAL` 和失败状态。允许本地生成 JSON/JSONL/CSV（以既有 `export-filtered` 为优先），但**数据主账本只在WorldData SQLite**；导出是可重建产物而非第二套事实库。仅当一个完整的受控批次和必要门通过才发布 `READY` manifest，否则失败关闭；独立来源原子性不等于真实单时点全局快照。

## 4. G1/G2与真正采集触发的边界

- **G1 软件就绪**：一键命令从配置到本地Reader→SQLite→固定数据包，完成可重放fixture/SQL测试；不代表新日历比赛已实机采集。
- **G1 实际就绪**：Human以后明确触发本地采集，当前真实NBA2K22进程与已绑定存档读取成功，新增Calendar Sim完赛场次和同源SQL回读经对账，全部必要数据包正确生成。不需要让模型亲自执行每项采集。
- **G2 软件就绪**：设置前值、候选调整、未来REA读回/时间戳、新比赛块与指标差异拥有可查询的完整契约，未知项可成为可证伪假设。
- **G2 效果已验证**：Human授权设置修改、游戏原生读回，随后Human推进日历，产生新样本并被上述一键采集接纳，才可声称某次设置影响得到支持/反驳。

Human未触发时，**不得启动后台监听、持续轮询游戏、自动修改设置或推进赛季**。可在开发环境下反复测试固定脚本、fixture及只读staging，不使用RDC执行普通Git/SQL任务。

## 5. 对任务完成与整改的约束

继续现有 A0–A4 的开发Loop；每次修复、测试和来源检查留SHA、日志和实际对照。**不要启动一个新架构设计任务或超出此合同去补全204字段。**

所有测试等级、S0 Pilot G1/G2报告、完成指针必须区分：`CLI_ORCHESTRATION_CODE`、`FIXTURE_SQL_REPLAY`、`CURRENT_NATIVE_READ`、`FULL_REGISTERED_FAMILIES_COMMITTED`、`STANDARD_DATASET_EXPORTED`、`POST_CALENDAR_NEW_GAME_VERIFIED`。任何未测阶段不能用其他PASS替代。

**本次Human补充只是使既有任务从“新建触发监听”回到“继承WorldData、用户一键触发、脚本自动全量与数据提取”的原本目标。**
