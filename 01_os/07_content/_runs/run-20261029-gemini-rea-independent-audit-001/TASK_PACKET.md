# NBA2K22 Gemini REA Wave-01/02/03 → Codex 独立审核与条件性工程接收任务

任务ID：`NBA2K22-GEMINI-REA-INDEPENDENT-AUDIT-01`  
任务角色：`independent_review_and_selected_repair`，**Codex 是唯一正式工程Owner**。  
执行工作分支：`task/nba2k22-gemini-native-audit-20261029`（基于冻结工程基线直接创建）。  
固定 Codex 工程基线：`baseline/nba2k22-native-execution-checkpoint-014-20261029@6151ef5d484914edcec2fbcfcf3bcce83a848907`。  
固定 Gemini 候选研究：`gemini_rea@6cad7c7454798dbe18e7bd800d85e2a9d1c7119c`。  
Gemini 最早分叉的工程提交：`39086984adfa554d36315382d41bc2e5d2e54c39`。  
项目 PR：规划PR18；Codex冻结PR19（OPEN Draft、仍不合并master）。  

## 1. 任务定义与严禁的捷径

Human已指示由Gemini集中探索，Codex负责最终**整理、独立复核、必要的修复和有条件的选择性集成**。本任务不是重新启动已结项的原`NBA2K22-ROLE-NATIVE-EXECUTION-SYSTEM-01`，也不是证明原184项已实现。当前研究输入含GREA-01、Wave-02及Wave-03全部材料。Gemini自称“163项闭环+21项不在第一版范围”；这只能解释为**研究处置覆盖**，不代表Native动作可调用、游戏生效或持久保存。

**当前默认权限：只读既有目标EXE的有界静态证据、研究源文件、离线校验和本分支工程修复。禁止启动/附加游戏或Frida在线执行，禁止更改存档、日期、真实联盟状态、系统安全设置或测试任何未获Human批准的游戏Native写入。** 如需实机，只产出最小可授权验证用例，不执行。严禁修改Gemini分支、冻结基线、PR19旧工程工作区或master。不能直接整体merge/rebase实验分支；只逐文件对照、选择性移植经复核的代码。

### OS启动顺序

根`AGENTS.md`、领域`AGENTS.md`、`PROJECT_INDEX.md`、`docs/development/PROJECT_MODULE_REGISTRY_V2.json`、`docs/development/PROJECT_INDEX_SYNC_CONTRACT_V1.md`；REA`REA_WINDOW_CONTEXT_HANDOFF_20261028.md`、`VALIDATION_RESULTS.md`、`ROLE_EXECUTION_PROGRESS.md`及任务相关Native绑定/运行时。机制参照`docs/game_mechanics/guides/K04_COACH_AND_PLAYS.md`、`K06_TRAINING_HEALTH_GROWTH.md`、`K07_K08_K09_FRANCHISE_OPERATIONS.md`；不需要全文加载全部历史文档。应先记录所读来源SHA，避免不同分支文件混用。

### 不可跳过的权威来源

正式工程冻结版本：
- `08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_control/TASK_CLOSURE_20261029.md`
- `.../research/rea_native_control/data/NATIVE_EXECUTION_BASELINE_MANIFEST_20261029.json`
- `.../research/rea_native_control/data/DEFERRED_NATIVE_CAPABILITIES_20261029.json`
- `.../research/rea_native_control/GEMINI_NATIVE_INTEGRATION_HANDOFF_20261029.md`
- `.../research/rea_native_control/FA_OFFER_NATIVE_CONTRACT.md`
- `.../research/rea_native_control/OFFER_WITHDRAWAL_NATIVE_CONTRACT.md`
- `01_os/07_content/_runs/run-20261028-role-native-execution-system-001/coverage_current.json`

Gemini读取为**冻结提交的外部分支素材**，不要覆盖工程树：
- `01_os/07_content/_runs/run-20261028-gemini-rea-001/GREA_01/`
- `.../W02_A/`, `.../W02_B/`, `.../W02_C/`
- `.../W02_CONSOLIDATED_CODEX_HANDOFF.md`
- `.../W03_00/`, `.../W03_04/` 至 `.../W03_12/`
- `.../W03_MASTER_GAP_MATRIX.json`、`.../W03_CONSOLIDATED_CODEX_HANDOFF.md`
- `08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_control/experimental/gemini_rea/` 下的隔离候选代码与21项离线测试。

## 2. 按“逐claim”审核，而不是把测试通过当语义证据

为每条有价值的claim建立审查清单：
`claim_id`, `requirement_id`, `candidate_rva`, `gemini_claim`, `original_assembly_replay_ref`, `independent_caller_or_consumer_ref`, `comparison_with_codex_baseline`, `ABI_this_context`, `side_effects`, `native_readback`, `status`, `reject_reason`, `migration_decision`。

对固定EXE SHA256 `1727ad72085fba39e789ee574fc15aab623ad1651cf6879e95e8cd53b6ffbbf5`执行**独立**PE字节与Capstone重演：命令/输出须记录原始字节、反汇编、函数边界、调用者与精确SHA。Gemini引用的路径、算法和自身生成的EVIDENCE_LEDGER不是二进制事实的替代。没拿到同SHA PE时，不能把无法重演的宣称晋升为已证。

验证阶段分为：
1. `TRACE_REPLAYED`：原始字节/窗口确实复现；
2. `SEMANTICS_CORROBORATED`：独立上下游证据证明声明的对象和业务含义；
3. `ABI_SAFE_STATIC_CANDIDATE`：ABI/this/线程/阶段/对象归属/副作用有可信静态合同；
4. `OFFLINE_INTEGRATED`：只是离线运行真实工程处理器和Reader/Batch契约；
5. `LIVE_APPROVED_VERIFIED`：**本轮不允许授予**，必须以后获Human授权才会有；
6. `PERSISTENCE_VERIFIED`：**本轮不允许授予**。

当前未验证的结论标`UNKNOWN`或`STATIC_CANDIDATE`，不能因为模拟测试PASS而升级。

## 3. 第一轮必须优先排除的高风险冲突

先读同目录`HIGH_RISK_CONFLICTS.md`，逐项完成：
- **GM合同**：Gemini把`0x12bf5a0`标成phase22选项执行器，而冻结Codex合同资料说明该函数扫描/选择报价且在phase22存在断言条件；另Gemini48字节/5薪资的`ContractOfferContext`与Codex原生44字节报价记录/6薪资必须区分对象、真实生命周期，不能直接换正式编码。
- **GM报价撤回**：Gemini标`0x12b3840`为撤回，而Codex具有完整独立`0x12b4040`撤回服务与单项调用合同；先证明是同一种对象/作用还是仅内部辅助函数。
- **GM交易**：Gemini候选中的`validate_salary_matching`使用硬编码CBA规则，且宣称可进行三方/多资产原子事务；**执行器不得自行替原版决定业务合法性，更不能变更双方GM的意图**。排除自行算薪或评分的生产集成，复核多方原生调用链及范围。
- **教练Gameplan**：IsInUse/UI Dirty ≠ 对手独立提交/存档持久性/下一场生效；默认Gameplan刷新函数不可冒充全29对手提交。
- **防守18项**：两次8+4字节存储≠单指令原子事务；默认位掩码≠全部字段枚举语义。核验邻域保持和实际消费点。
- **Playbook**：一处`cmp eax,0x44`≠自动证明360字节结构、68个CRC槽和四分区；从原版读写/消费者/真实Team Book归属分别证明。
- **轮换**：7位分钟存储/位置标记不能替代原版完整排兵布阵与时间线提交；48×10字节时间线只可确认尺寸，不可擅自假设逐分钟选手顺序。
- **训练/员工/选秀/Getter**：原生函数名、指针偏移和值域按各自现存证据回查；Getter目录条目不等于可用的当前存档对象解析与结果语义。
- **21项测试**：检查是否只是自建codec对象roundtrip；没有独立黄金样本时不能做生产级Native证明。

## 4. 运行计划（审核与条件性集成分离）

**阶段A：归档接收和反证（必须先完成）**
1. 固定源码commit/manifest/分支差异，建立`CLAIM_AUDIT_MATRIX.json`及`EVIDENCE_REPLAY_LOG.md`。
2. 优先审高风险（先合同/交易、后Coach Gameplan/防守/Playbook、再轮换/训练/员工选秀/Getter），每项状态：`KEEP_STATIC`, `REWORK`, `DUPLICATE`, `REJECT`, `UNVERIFIABLE`。
3. 与冻结已有72 action、65绑定、15读取逐项去重。**不以实现163项新业务为验收目标**。
4. 输出`STAGE_A_AUDIT_GATE.md`：Codex已复现的原始窗口、明确冲突、真实可复用子集、不可调用清单。

**阶段B：仅对通过阶段A的项目做条件性修复/集成（自动继续，但严格受证据门控）**
1. 优先采纳能独立证明、不会引入业务决策的纯Codec、字段目录、只读Getter候选；必要时局部修正函数语义。禁止整体复制Gemini模块/测试。
2. 只对ABI/对象/阶段/副作用被独立证明的Native候选编写正式调用合同、离线Runtime模拟及错误隔离；证据不足的函数不能接入有写权限的Facade或ActionRegistry。
3. 优先保留Codex当前的交易Process、报价提交/撤回和执行编排，不用Gemini候选替换已有严格协议；优先修复生产合同或校验，而不是创造未经确认的业务规则。
4. 真实生产改动须遵守OS: 同任务索引/Registry同步、动作和读取覆盖数准确更新、`full_goal_complete`不受本次审核篡改。
5. 离线执行真实工程单测+新增反例；成功与失败均记录工具命令和实际输出。任何未触及游戏都只能称静态/离线合格。
6. 建议将正式集成分成`COACH_CORE`、`GM_CORE`、`GETTERS`三个明确子提交，便于撤销。若阶段A无可信项，阶段B无代码提交也属于合法结果。

## 5. 提交与验收

本次任务至少交付：
- `CLAIM_AUDIT_MATRIX.json`：逐claim精确结论与证据。
- `EVIDENCE_REPLAY_LOG.md`：真实离线复核命令+SHA+输出与失败记录。
- `CONFLICT_RESOLUTION.md`：原始差异、为何接受/驳回/不确定。
- `STAGE_A_AUDIT_GATE.md`：哪个候选可进入后续集成，附明确信息缺口。
- `SELECTED_INTEGRATION_MANIFEST.json`：经审的特定来源/变动/测试/成熟度，或空清单及原因。
- `CODEX_FINAL_HANDOFF.md`：与冻结基线逐需求比较，已接收、需Gemini返工、需要实机授权、对第一版GM+Coach阻断点影响。
- `run.yml`：OS任务过程、前后HEAD、module scope、验证与交付状态；不要改写历史GREA和旧M0–M5 Run。

每个独立工作包记录checkpoint，更新索引后推送**只到本审核分支**。可新建Draft PR以`baseline/nba2k22-native-execution-checkpoint-014-20261029`为base，但不要自动合并；最终申请Human验收。不操作Gemini工作区、PR19、master。找不到可信同SHA二进制/REA工具或存在重大ABI不确定时直接`RESEARCH_ONLY`/停止相关集成，提交完整冲突报告比制造可调用函数更有价值。
