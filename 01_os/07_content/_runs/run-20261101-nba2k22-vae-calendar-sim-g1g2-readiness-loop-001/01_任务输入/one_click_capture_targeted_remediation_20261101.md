# Human 澄清后的定向整改 · 采集全量 / 采集新增的全量数据

任务：`NBA2K22-VAE-CALENDAR-SIM-G1G2-READINESS-20261101-001`

审阅对象：`d1a34ddbb7b1578a20ce773b0496a33cf71b1f33`。状态：**源码静态检查发现影响实际数据正确性的缺口；上轮已报313单测PASS不可替代本清单的新负例与真实采集回读**。当前由开发期内部 Loop 定点整改，不新增独立审核任务，不改原Run的历史交付报告。

## 1. Human 指令的严格语义（必须优先于新命令的旧游戏门槛）

- Human对Gemini说 **“采集全量数据”**：按第一阶段标准初始化/核对当前已声明绑定的存档；执行现有`refresh-world auto`注册的全部20族来源，遵循16普通+4年度频率、append-only、失败恢复、来源回执。不得以“当前没有未入库完赛比赛”为由跳过玩家倾向/能力、教练、名单、设置、伤病、财务、交易、赛程和历史等来源。
- Human说 **“采集新增的全量数据”**：针对**同一存档**的已注册来源执行一次受控增量全族刷新，复用`--data-updated`、年度跳过策略和`--resume-report`；以源单元/时间、存档、赛季及字段变化判定新观察。即使没有新比赛，设置、轮换、交易、球队等也可能变化。新增比赛的检测仅用于报告赛果及VAE增量提取，不得成为整个采集的启动条件。
- 采集自动化等于 **Human一次口头指令→Gemini按配置启动现有本地脚本一次→20族Reader→单库SQLite→固定SQL导出→回执**。后续重复执行本地脚本本身零LLM调用/零额外模型Token；对话触发Gemini仍属于模型调用，不能宣称对话本身零Token。没有后台常驻服务。
- `calendar-sim-trigger` 可以做便利入口，必须与第一阶段默认全族采集一致；不需要用户改用另一个复杂新工作流。可以保留`calendar-sim-inspect`和`vae-export-datasets`作诊断/重导出，但不得替代旧`refresh-world`协议。

## 2. 代码级阻断项（GitHub源码可直接复核，不需要RDC）

**R1 / P0 采集触发语义错位**：`calendar_sim_orchestrator.py:trigger_capture_if_new_game` 在无 `new_final_game_detected` 时直接 `SKIPPED`，无法完成Human初始/新增全族采集，甚至同一天新伤病/新名单/新设置全会被漏掉；`force=True`允许绕过`INCOMPLETE_GAME_IN_PROGRESS`，不能用强制覆盖替代安全前提。修正：全族采集不以游戏完成状态为唯一开关，模式区分FULL / INCREMENTAL；运行中的比赛只影响赛果候选资格，不可让强制选项绕开关键数据一致性验证。

**R2 / P0 SQL核验失败仍宣告成功**：`trigger_capture_if_new_game`忽略`verify_game_sql_integrity`的 `verified_in_db` / `is_final` / `was_simulated` / `score_conservation`结果，始终可返回`SUCCESS_INGESTED`并发布导出；`verify_game_sql_integrity`只要game和state两行存在就设`verified_in_db=True`，缺一方球队Box或节分可回退0且标守恒；未限定**本轮新成功source unit**及完整两队一致性。修正：核验失败禁止发布READY Manifest，所有必需球员/球队/比分/Final/Sim/Source Unit一致性须实际满足，旧观察不可代替新回执。

**R3 / P0 标准数据包重复/拼接多采集**：`export_vae_standard_datasets`直接从`game_state_observations`和两个Box表按game_id全历史读出，未选最新有效同源Unit；多次刷新同一比赛会让`games_count`、Box条数翻倍，且不同时间的单场状态和球队/球员Box可以混配。修正：按save+season+game+mode+status+source合格性选唯一有效观察，依照WorldData原有观察范围、同源单位和时点规则（并明确历史点读）；对重复采集、部分单元、跨赛季模拟/3D混合构建负例。

**R4 / P0 实验字段身份错误**：`vae_experiment_evidence_input`硬编码`TENDENCY_SHOT_066`（源注册表Shot是`TENDENCY_NATIVE_001`，066才是Touches）及`COACH_DEFAULT_002_HELP_DEFENSE`（应先用权威COACH来源确认HelpDefense身份，旧候选为`COACH_DEFAULT_015`，002属于进攻POE）；输出必须引用审核M1/M3字段registry的**精确canonical ID**，不能发明临时字段名或默认实验效果阈值证明。不要把`same seed`对照当作用户真实日历SIM必可用。

**R5 / P1 Manifest误晋级**：`export_vae_standard_datasets`不看数据是否为空、是否只含`RESEARCH_FIXTURE`、是否已完成新游戏真实入库、是否已有合法setting readback，仍硬编码三个`datasets.status=READY`、`CURRENT_NATIVE_READ=VERIFIED`、`G1_READY`、`game_mode=MyLEAGUE`。用户目前有MC档与MyLEAGUE档，不能强制混用。修正：保存模式/Build来自真实来源，仅符合各门必要证据时才升级，只有Fixture时`CODE_READY / SQL_REPLAY_READY`，其它`LIVE_VALIDATION_PENDING / NO_DATA / PARTIAL`；即便独立导出旧库，也不能宣称已自动捕获新日历比赛。

**R6 / P1 设置快照非确定性**：采用 `WHERE unit_id IN (SELECT MAX(unit_id) ... GROUP BY team_id/player_id/staff_id)`，不是逐实体/字段按`observed_at`的合法最新成功单位选择，多个实体共享同unit时可能出现重复行、旧字段混入；应复用WorldData原有`--as-of`/来源scope和公共查询权限过滤。Owner材料、隐藏Potential及不可公开元数据不进入VAE数据包。

**R7 / P1 可执行验证不足**：8个新测试验证了一些mock/SQLite样例，但并没有证明真实`refresh_world`全20族采集、同源新赛果闭环、完整fail-closed与状态机多场/离线复用。须新增全族 mock 测试、无新比赛但有其它变化、重复同场多单元、不同比赛先后顺序、SQL不守恒、空库、不同存档/模式、部分来源失败恢复、指标未知、当前真实新比赛不可用等负例。

## 3. 目标达成方式与验收

- **保持原有单库/20 Reader/atomic unit/append-only/年度策略**，不新开数据库/新采集体系。
- 给Gemini提供两个稳定人类指令对应的**一键模式**，从本地配置中选存档/实际游戏文件名，完整输出采集回执与三份固定VAE数据产品；API可以保持旧命令形式（或极薄包装）；不要求Human逐Reader操作。
- `FULL`、`INCREMENTAL`、`EXPORT_ONLY`清晰分离，任何实现不能让新完赛比赛成为全量采集的必要条件。
- G1分级：代码/Fixture PASS、实机Native读回、全20来源落库、VAE数据包真实同源查询、新完赛实测，**分开评级**。G2仅验证合同就绪，真实REA写入/比赛效果仍须未来Human授权。
- 按已批准开发Loop实施定点修复和测试。当前不执行NBA2K22游戏、存档或后台操作；无需使用GPT RDC完成常规源码/DB测试。全部修复提交本任务分支，保留原历史结果，写变更和负例回执。
