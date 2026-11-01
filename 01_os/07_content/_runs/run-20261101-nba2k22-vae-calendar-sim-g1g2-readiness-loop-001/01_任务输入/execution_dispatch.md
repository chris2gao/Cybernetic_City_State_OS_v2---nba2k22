# VAE Calendar Sim · G1自动采集与G2设置效果验证链路开发合同

## 岗位与固定输入

任务ID：`NBA2K22-VAE-CALENDAR-SIM-G1G2-READINESS-20261101-001`；`execution`；执行模型建议 Gemini，真实运行型号在回执中登记。

NBA仓库：`chris2gao/Cybernetic_City_State_OS_v2---nba2k22`。

工作分支：`task/nba2k22-vae-calendar-sim-g1g2-readiness-loop-20261101`。

**精确父SHA**：`75e17813af64f0046a0393071a2115c44835092d`，继承已提交的Gemini H1-H5 数据加固候选；**不是master**。

真正的任务包、边界、验证在本Run：
`01_os/07_content/_runs/run-20261101-nba2k22-vae-calendar-sim-g1g2-readiness-loop-001/`
分别读 `run.yml`、`01_任务输入/task_packet.json`、`01_任务输入/verification_plan.json`。

其他资料固定源：Stage02 38指标 `c812042e087f4c7000d27ac42d3839741039c188`；独立审查需求基线 `8ed0baff7fd7cf6439c0a49e158dea5b1838d1e3`；WorldData v24 `17ec1cea88c2bb6c36264792f70c94bef9a8bdb4`。

## 背景：别把S0查询PASS当成真正G1完备

上一轮Gemini报告 307 unittest通过、恢复38个ID、修复DNP/重复记录、区分GameScore/Touche等指标；保留成果，不重复整轮独立审核。

但它同时自报“Pilot 1/2 G1=READY”，而现存 `refresh-world auto` 只是命令调用后自动识别进程/来源，**不是用户推进日历后自动监听/触发采集**。上一轮也没有固定当前新增Calendar Sim完赛比赛→完整Reader→新DB capture unit→SQL同比赛独立读回的真实验收收据。

因此这轮集中让两个条件真正具备，而不是继续逆向204字段：

- **G1 数据门**：Human推进日历后，可以由明确启用的触发机制发现**新增已完赛**Calendar Sim比赛、复用既有WorldData采集并保存、通过SQL复核真正新增球员与球队数据。
- **G2 验证门**：有设置前后快照/REA读回、实验ID、比赛样本、准确的对照条件、指标来源/日期/查询回执和可修正的机制假设。

Human已经确定：**先只用Calendar Sim作设置影响的标准；3D真实比赛暂不混入评价，旧历史比赛只用于诊断和建立前测，不当作新设置的因果证据。**

## 工作包与开发Loop

**A0 · 梳理现有代码与缺口。** 对比现有CLI、`refresh.py`、`process_session.py`、Game Mode/score读取、Oracle保存绑定、采集输出、查询接口。检查旧M3 38身份与上一报告“31项S0_READY”的实际证据层。先建立发现清单。

**A1 · 实现受控的采集触发。** 优先用现有`refresh-world`和 Reader，不建平行采集器。设计小型**非驻留、明确opt-in**的单次/受控监听入口：通过已完赛比赛集合、season、save、mode、game date等判断是否有真正新比赛；只看到日期变化不得造新Game；只在状态稳定且检查成功时启动采集。重复观察相同状态不重复计算比赛。可以实现可选有界监听设计与测试，但**本任务不实际安装或启动常驻监控/后台任务、不得在未获额外批准时开启对用户进程的持续轮询**。

**A2 · 统一采集→SQL闭环。** 复用`refresh-world`+原有SQLite，确保新游戏ID、同赛季、球队与球员、完整与未完赛、来源批次、模式及新鲜度。只读Staging DB运行重复/中断/无新增/缓存与重启异常测试。所有`SQL result`必须能追溯到同一Native source unit（否则返回UNKNOWN/NOT_READY），不能拿旧fixture充当新赛果。刷新失败要有可恢复状态，不默默标PASS。

**A3 · G2机制效果实验合同。** 先完成**不动设置**的数据结构与可执行验证样例：
`ExperimentID → Save/season/engine/settings-version → exact setting field_id + old_value + proposed_value + future REA readback → S0 calendar sim block → S1/S2 new game block → matched controls/opponents/roster/injury/coach/ACE/Normalize/quart-length → native metric query → uncertainty/alternative explanations → supported/refuted/inconclusive`。
不是自动优化器，也不是RE A Setter。不得把相关性当作因果性。未知的设置效果应形成可证伪、可追加的假设。

**A4 · 强化测试和判断门槛。** 实际运行成功、重复事件、日期推进却无新比赛、跨赛季、重复unit、多进程、PID重启、游戏模拟中途数据部分缺失、历史存档不匹配、DNP/NULL、Calendar Sim/3D混入、None/派生项和数据库失败等定向负例，并运行现有回归。每轮要保存真实exit code、Git SHA和问题修复回执。

所有阶段采用**有证据的内部Loop**，没有固定迭代轮次。不因一次代码提交就宣告整件工作完成；但缺实际可访问游戏时先完成逻辑和fixture验证后停在明确的`LIVE_VALIDATION_PENDING`，不为了形式上绿灯擅自访问或推进游戏。

## 必须遵守的行动边界

- **本任务绝对不得修改球员倾向、教练设置、游戏内存、原始存档或推进比赛日历。** VAE S1需要Human后续单独批准。
- 新采集触发程序只有获得Human明确授权才能在用户游戏机器上启动（尤其是常驻轮询）。源码实现、静态验证、合成/既有fixture重放本任务可做。
- 不调用外部RDC用于普通仓库/SQL/文档查询；Gemini在自己的已授权环境运行其测试并将证据上传GitHub。RDC若由GPT复核，只允许极少数关键、与NBA2K22进程直接相关、读写边界清楚的本机验证脚本。
- 只可修改`08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype/**`及本Run；其他Core、NBA master、旧Run都只读。
- 不新增数据库替身、不开发新的VAE自动调参、不重新定义38项指标、不默认开启后台代理，不与正式OS七阶段Workflow混淆。
- 旧测307 passed只证明代码/fixture覆盖，**不证明自动新赛果采集已启动或G2修改生效**。

## 验收等级（逐Pilot、逐门填写）

各门分开填写：
- `CODE_READY`：实现与合成/回放负例正确；
- `LIVE_NATIVE_READY`：真实当前进程绑定与新增Calendar Sim终场数据确实可读；
- `SQL_INGEST_READY`：新比赛入库，按同一Game ID与source unit查询结果核对；
- `TRIGGER_READY`：实际受控启用后无需手动分别调用各Reader，确实发现新Game，失败不重计；
- `SETTING_EFFECT_PROTOCOL_READY`：前值、后值、REA读回、S0/S1比较合同真实可执行；
- `SETTING_EFFECT_LIVE_VERIFIED`：必须待以后Human授权修改设置、推进新Calendar Sim并采样后才能证明，**本任务不可能直接宣称该状态已通过**。

若无真实游戏/授权：只可报告前述非实机门满足，其他标`NOT_RUN / PARTIAL`；不得“全门READY”。

## 交付与完成门

按包内列出的：
`g1g2_requirement_to_evidence_matrix.json`、
`auto_capture_orchestrator_design_and_entrypoint.md`、
`experiment_settings_metrics_contract.json`、
`calendar_sim_pilot_gates.json`、
`loop_iteration_log.md`、
`g1g2_replay_negative_verification.json`、
`completion_pointer.md`，同时提交真正代码和测试。

独立审核延迟至VAE系列集中审核，但在后续使用此接口发起自动设置修改前，须按已批准的风险门做关键子集确认并获得Human授权。

请先读取当前分支实际HEAD和原任务包，从A0开始执行内部Loop。
