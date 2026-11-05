# DEV-03 · 原生机制实验与验证基准 / Mechanism Experimentation

**任务 ID**：`NBA2K22-BIC-B1-DEV03-MECHANISM-EXPERIMENT-20261104`  
**领域**：NBA2K22 · Basketball Intelligence Core (BIC)  
**岗位**：`execution`；**建议执行模型**：Codex（离线实验引擎和验证），Gemini（机制假说与因素分组研究，可并行只读）；GPT-6 规划与系列审核。  
**发布状态**：`PUBLISHED_CONDITIONAL_NOT_IMPLEMENTATION_AUTHORIZED`，以同 Run `task_packet.json` 的阶段/权限门为准。发布本任务本身不允许模拟推进真实存档、接入游戏进程或更改原生设置。

## 1. 真正要交付的功能

交付可以复用已有 WorldData/Calendar/REA 的**受控篮球机制实验能力**：输入一个有依据的篮球机制假说及可检验因素，产生符合对照要求的实验设计、可复核的离线执行计划、结果分析和证据状态。它必须能够尽可能分离球员能力、徽章、倾向、教练/球队设置、阵容、战术/PlayTypes 的独立作用与相互作用，并明确无法识别的混杂。

本任务以建立**机制基准**为核心，竞技方案只是实验载体，不能仅用多场胜负证明单个字段具有因果作用。需求映射：`RES-01B-CONTROLLED-CAUSAL-INTERACTION`、`RES-01B-ONCOURT-EVIDENCE-CANDIDATE`、`RES-01B-EVIDENCE-QUALIFICATION`、`RES-01B-MECHANISM-KNOWLEDGE-CORRECTION`、`RES-01B-COMPETITION-KNOWLEDGE-LEDGER`，对应 A0 `SC-03/04/05/06/07`。

## 2. 已有系统必须优先复用

- WorldData v24 的真实只读原生采集与比赛、模式、球队/球员身份、来源单元和查询接口；`world_data_prototype/` 是首选。不得重建 Calendar 和统计采集。
- `01_os/07_content/_runs/run-20261101-nba2k22-vae-native-stats-worlddata-loop-001/07_测试执行/loop_verification_and_regression_report.json`：当时 307/307 测试与真实模式/统计读回证据；该记录不等于所有新实验效果已认证。
- `08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_control/bulk_executor.py` 与 `01_os/07_content/_runs/run-20261101-nba2k22-rea-deterministic-bulk-executor-001/06_执行/bulk_executor_design_and_validation.md`：受控 CAS、readback、chunk budget、journal 和 `UNKNOWN` 锁资源方案，历史状态是离线批量就绪/分级实机受限；本任务不重复造 Native Setter。
- 既有 VAE 的 204 字段/指标研究与单字段 Loop、教练设置/训练研究材料，均按固定版本及实际验证范围引用，不将“字段有定义”当成“实机效果已确证”。

## 3. 功能设计与开发顺序

**P0 · 实验能力盘点（只读；无需新游戏测试）**  
列出现有日历模拟接口、可恢复/克隆存档方式、比赛模式、采集时间与事件、原生随机性和控制因素的可用性。给每个想操作的参数标明 `READ_VERIFIED / WRITE_VERIFIED / LIVE_EFFECT_VERIFIED / UNKNOWN / FORBIDDEN`，实际可操作权与已认证状态分别校验。

**P1 · 离线实验规格与编排（工程执行门通过后）**  
建立最小确定性实验计划及报告入口（优先扩展已有任务与查询而非创建独立平台）。输入包括：`hypothesis_id`、球队/球员/存档/版本/模式、处理因素和数值、对照因素、证据层级、重复/分组方案、预期行为与统计指标、停止条件、变更授权、数据来源链接。输出包括：冻结的因素分组与计划摘要、可执行性状态、哪些需要游戏写入、哪些只是离线比较、方案哈希、预定判定标准。

**P2 · 因果解释与独立/交互识别**  
支持**至少一个可复核的 2×2 双因素离线实例**（可使用有明确“合成”标识的模拟夹具，不能冒充真实游戏实验）：检查因素 A、B 各自效应与 A×B 交互，并测试混杂、缺失值与零效应。再用一个真实 WorldData 只读批次演示分队、分场或分时期的**相关性/可比较性报告**；没有真实随机或控制分组时输出 `NOT_CAUSALLY_IDENTIFIED`，不宣布因果证明。

对于未来 30 支球队、400+ 球员、多轮赛季规模实验：以球队/同一存档/同一时间推进为聚类单元，预先隔离不同处理组与对照；**同一球队的多名球员、同一赛季多场比赛并非天然独立样本**。无法真正固定的球员自然成长、伤病、疲劳、对手/赛程、AI 覆盖、随机性须保留为混杂；不要“一轮全改全部倾向”后直接归因到每一项。可以提出分块、正交或分层设计候选，但最终设计需按真实可控因素和实际算力决定，不能制造确定的样本量/效应数值。

**P3 · 3D 战术行为补证协议**  
为关键战术设立观察条目：篮球意图 → 原生设置/调用证据 → 球员实际配合/跑位 → 是否创造优势 → 终结行为 → 竞技结果。区分用户亲自对战 AI、CPU 对 CPU 3D、Fast Sim；当没有录像/动作证据时只报告 `TACTICAL_EXECUTION_UNKNOWN`。不预设已有自动视觉识别或能直接从 Box Score 还原战术。

**P4 · 受控 Native 实验接口（仅专门实机授权之后）**  
设计接收 REA 批量计划及只读状态的适配**规范**，不自行启动 Frida、不调用 Setter、不进行真实日历推进。真正需要实验时由 Human 另行授予固定 `save_instance + team/players + field/bounds + game_build + before/after + rollback` 的权限；原版 getter/ CAS/readback/持久收据/异常阻断仍归 REA。只读实验结果与 Native 写入效果严格区分，不对数据进行不经授权的反复操作。

## 4. 必须通过的离线验收

1. 2×2 因素设计可正确标记独立作用、交互作用或不可识别原因；合成数据与真实 NBA2K22 数据有显著标记。
2. 重复样本/聚类、赛季进度、对手差异、球员成长与遗漏因素不能被自动当作独立证据；提供至少两类负例（混杂和不可比模式）。
3. 真实 WorldData 批次中可以形成 `SOURCES → DESIGN → OBSERVATIONS → FINDINGS/UNKNOWN` 的只读证据链；没有原始观察就拒绝生成精确结果。
4. 3D 与 Fast Sim 证据彼此不混合；战术设置变了但未观察到实际执行时不能声称战术成功。
5. 大规模计划编译、批次复用、错误阻断有性能测量；不得通过万次逐字段 Frida 启动实现万级测试。
6. 所有实验记录包含版本、对照条件、假设、原始数据引用、正反证据、局限、复验触发；无需开发大规模视频识别或新数据平台。
7. 游戏进程附加/存档推进/原生写入=0，直到收到独立 Human 实机授权。

## 5. 交付与回滚

交付：复用与可控矩阵、离线实验计划/对照方案格式、最小 2×2 演示与真实只读批次示例、3D 标注指南、结果和负例回执、性能/回归报告、开发 Loop 检查点与可复核的后续实机授权候选。所有实验若执行异常必须保留收据与 UNKNOWN 而非重试改写；任何被阻断的实验都不能标记为比赛结果。

**阶段退出门**：至少可离线运行一个受控实验计划并识别独立/交互及混杂限制；可引用 WorldData 已有证据；能准确指出哪些机制需要真实 NBA2K22 游戏操作及其授权边界。
