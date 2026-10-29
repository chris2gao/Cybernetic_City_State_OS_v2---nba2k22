# GREA Wave-03｜GM + Coach 全剩余 Native 能力连续研究计划

状态：`AUTHORIZED_HUMAN_CONTINUOUS_RESEARCH / NO_LIVE_GAME_ACCESS`  
日期：2026-10-29；Owner：正式工程仍由Codex负责，Gemini为隔离实验研究者。  
实验入口：`gemini_rea`，本Wave开始前基线`a72ad80eff5769085d12997bf55bdf4059590705`。  
正式接收基线：`baseline/nba2k22-native-execution-checkpoint-014-20261029@6151ef5d484914edcec2fbcfcf3bcce83a848907`。Gemini历史来源`39086984adfa554d36315382d41bc2e5d2e54c39`。  
**不合并两分支，不更改Codex冻结提交或master，不宣称原始184需求/完整M0–M5已完成。**

## 0. Human授权与这一轮相对Wave-02的改变

Human明确要求：Gemini额度较充足，**将剩余REA原生研究集中授权，连续推进约两个小时量级的高强度探索/自纠，而不是每十分钟交一小包并停机**；Codex最后集中独立验证、整理、修复和集成。这个“约两小时”是工作预算/目标深度，不是强制等待、空跑、耗满时间或保证会话不停机。遇到模型额度、上下文或工具会话上限，应以真实checkpoint结束/由新会话依据本文件续接；不能假装仍在后台运行。

本Wave覆盖**GM和Coach第一版玩法所需的全部剩余原生机制研究、与其直接相关的Getter和执行读回**。不做LLM人格、媒体、D1–D5完整数据库/自动化开发、世界线推进、游戏模拟、玩家自然成长篡改。非第一版的Player人格和WorldAdmin属于保留总账，不允许悄然变成第一版工作；可登记相关Native线索但不执行大规模新功能开发。

## 1. 真实权威来源与启动加载

1. OS启动规范：根AGENTS、AGENT_WORKING_DISCIPLINE、领域AGENTS；`PROJECT_INDEX.md`、`PROJECT_MODULE_REGISTRY_V2.json`、`PROJECT_INDEX_SYNC_CONTRACT_V1.md`。
2. REA交接：`research/rea_native_control/REA_WINDOW_CONTEXT_HANDOFF_20261028.md`、`ROLE_EXECUTION_PROGRESS.md`、`DISCOVERY_NOTES.md`、`CONTROL_CALLBACK_DISCOVERY.md`、`VALIDATION_RESULTS.md`；已有Frida/REA安装与局部PE/Capstone工具，**不重新安装或重复全游戏Ghidra导入**。
3. 教练/GM机制：`docs/game_mechanics/guides/K04_COACH_AND_PLAYS.md`、`K06_TRAINING_HEALTH_GROWTH.md`、`K07_K08_K09_FRANCHISE_OPERATIONS.md`及领域相关R05 catalogs。
4. Codex正式冻结基线：`TASK_CLOSURE_20261029.md`、`data/NATIVE_EXECUTION_BASELINE_MANIFEST_20261029.json`、`data/DEFERRED_NATIVE_CAPABILITIES_20261029.json`、`GEMINI_NATIVE_INTEGRATION_HANDOFF_20261029.md`；优先以固定SHA的远端文档只读获取，不把它们合并或复制覆盖实验源码。
5. 当前`gemini_rea`本Run：`GREA_01/`、`W02_A/B/C/`、`W02_CONSOLIDATED_CODEX_HANDOFF.md`及隔离候选；保证工作树与版本隔离。

**立即从Codex冻结总账建立`W03_MASTER_GAP_MATRIX.json`**：每行 requirement_id、existing_action、Native成熟度、现有原始证据、缺少的函数/对象/ABI/提交/观察、研究优先级、Gemini已证内容、最终Codex验收要求。原184项逐项保留原状态；非Native类消息/人格请求不得伪装成未破解函数。优先研究当前第一版缺口，不得把已经由Codex修复且有证据的函数重新发明。

## 2. 完整研究队列：不再每包等待Human/Codex批准

**按顺序或在明确依赖被阻断时切换，全部属于本Wave已授权范围。**

| ID | 工作包 | 研究目标/关键停止依据 |
|---|---|---|
| **W03-00** | **Wave-02证据可信度回查** | 对18项位段及Playbook四分区查独立字段语义/数值/调用者；仅`mov 0x280000`或`and 0xfffff800`只能证明默认/位范围，不证明每个字段名称与枚举；`cmp eax,0x44`只证明某处与68比较，不独自证明对象起址/CRC/分区；8+4字节两条复制不是硬件单条原子事务；持久化/比赛效果均未验证。列实证与推断差异，修正过高成熟度，寻找真正Gameplan和Playbook提交/刷新链。 |
| **W03-04** | Coach全局设置和四Freelance | 已恢复10项Coach默认设置之外的剩余字段、四个有序Freelance槽、Preferred/ActiveSystem、ACE/体系/HelpDefense等；找实际Native对象、原生枚举来源、应用、读取和刷新。 |
| **W03-05** | Coach首发/轮换/分钟 | 在现有逐人分钟调用基础上找首发五人、第二阵容、位置、轮换顺序、时间线、分钟约束和原生整套提交；区分UI editor/career clamp/真实MyLEAGUE。 |
| **W03-06** | Coach球队与个人训练 | 复用现有日期训练Patch；研究个人训练、师徒/导师、团队重点、强度、背靠背休息、疲劳/健康字段的原生设置、日程和状态读取；训练设置不等于直接提升技能。 |
| **W03-07** | GM合同全链 | 在原生FA报价/撤回基础上追踪原版接受/拒绝、最终签约、续约、合同选项、年限/薪资/状态变更和读回。不要把`OFFERED`或函数Return1当`SIGNED`，不自动设计价格或接受概率。 |
| **W03-08** | GM员工及名单管理 | 原版员工雇佣/解雇/合同/球探/训练师岗位、球队名单迁移/裁员/名额规则/伤病名单；不能把内层TeamID写入或菜单确认当完整业务。 |
| **W03-09** | GM选秀、球探、签权 | 选秀大会指定新秀、选秀权归属/保护/交易、新秀考察、球探雇佣/任务/进度/报告及读取；旧Goal实机实例不重复提交。 |
| **W03-10** | GM剩余交易业务 | 多人/选秀权/三方交易与交易区操作；现有DirectProcess不重复研究；按真实对象/单次原生事务证明，不能代GM配平薪资或自主换目标。 |
| **W03-11** | 与教练直接相关的Player原生接口与读回 | 仅第一版Coach可授权的倾向、四个战术类型、训练关联及只读档案；复用已有Setter，专查不完整值域、参数、权限、后效和读取路径；不启用独立球员人格/任意能力或徽章修改。 |
| **W03-12** | 与本轮动作直接相关的Native Getter缺口 | 仅为执行前决策输入和执行后校验追踪合同/员工/对手Gameplan/Playbook/训练/名单/球探/选秀/比赛统计Getters，并与现有Memory Reader和15类读取目录对照；不做另一个全量世界数据库。 |

**W03-00是必做首轮**，其余不需要每个目标被完全破解才能继续下一个。首选回收“证据充足且Codex可快速复核”的真实Native调用链；不强制每项都生成代码。每个包结束应明确未证功能与剩余证据成本。

## 3. 深度研究循环，不设置“做完两三函数立即停止”

按`DISCOVER → CROSSCHECK → FALSIFY → IMPLEMENT_ISOLATED → OFFLINE_REPLAY → EVIDENCE_QA → NEXT_GAP`执行。对每个关键函数或对象保持下列条件：

- **两条独立支持链**：至少一份与固定EXE哈希匹配的原始PE字节/准确反汇编，加至少一条不同来源的调用者、字段消费者、已保存游戏证据或相关原版流程交叉证据。两个自己写的JSON不算独立来源。
- **三级具体区分**：识别函数/布局；证明Native可调用的ABI、this、线程、阶段、对象生命周期与前后效果；证明持续保存/下一场生效。离线研究最多可到前两者的静态候选，不得宣称第三者通过。
- **反例尝试**：对象错队、过期身份、空指针、未知阶段、非法枚举、跨对手覆盖、未知结果不重放、非目标位/非目标槽保存；由静态证据不能确定时标`UNKNOWN`，不“修复测试”使猜测通过。
- **结构性反证**：位段默认初始化只证明默认值/掩码不证明字段语义；某处比较68不证明具体分区或CRC布局；12字节两次store不等于原子更新；setter位置存在不等于持久业务commit。
- **停止单一方向的条件**：同一个假设经过至少两种不同方法仍没有新增证据、或连续两轮无信息增益、或缺少目标PE/REA或必须实机权限，则记载阻碍，转向下一个待办。**不因为一个函数无解而停掉全Wave**。
- 目标为**连续深入推进整个任务队列**，不按全Wave固定4轮/12轮提前退出。保持合理上下文与工具成本：只做有界PE和xref扩展，低价值重复搜索立即切换；禁止整包解编译、重复安装REA、制造自我证明的测试套件。
- 若运行环境支持，可把`约120分钟`当作本轮研究预算目标；**无证据可继续时必须提前停，不空跑；会话/额度中断时保存可接续状态，不承诺自动后台运行**。当全部授权包均完成或者有明确无可进一步静态获取的证据时，按完成/部分完成结束，不以消耗完时间为标准。

## 4. Gemini隔离代码与证据接口

仅在以下范围写入：
- `01_os/07_content/_runs/run-20261028-gemini-rea-001/W03_*/`、`W03_MASTER_GAP_MATRIX.json`、`W03_MASTER_RESEARCH_LOG.jsonl`、`W03_CONSOLIDATED_CODEX_HANDOFF.md`和本Run的run/README增量；
- `08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_control/experimental/gemini_rea/W03_*/`。

禁止修改PR19正式`data/action_registry.json`、`data/native_bindings.json`、`facade.py`、`role_batches.py`、`runtime/`、全局OS Core、正式`PROJECT_INDEX.md`、模块Registry，禁止动数据库/存档/游戏exe/本地Codex工作区。若某项准备好正式集成，以**独立补丁建议**和Precise API Contract交Codex，不自行冒充生产接口。

每个W03包必须交付：
1. `HANDOFF.md`：涉及需求、已证和未证、反例、方法、达到的成熟度；
2. `EVIDENCE_LEDGER.json`：逐claim真实来源、二进制SHA、工具调用、原始输出索引、函数/偏移/ABI、反证；
3. `REPRODUCTION.md`：Codex可执行的实际离线重放命令，区分`ACTUAL`与`EXPECTED`；
4. `ITERATIONS.jsonl`：逐次有效研究循环和Git checkpoint；
5. `CODEX_REVIEW.md`：最关键独立审查点，可能的实机最小验证情景（仅提出，不运行）；
6. 若候选确需实现：隔离代码+测试。无足够证据时**不要制造一个“成功”的仿真执行器**。

每个小包独立Git提交并保存源SHA；全Wave每结束两个工作包更新`W03_MASTER_GAP_MATRIX.json`与主进度文件，方便模型会话中断恢复。完成后必须给Codex一张逐需求对照表：`KEEP_CANDIDATE`、`RECHECK_RAW_BYTES`、`RESEARCH_ONLY`、`REJECTED_OR_RETRACTED`；但这些只是Gemini建议，不是Codex接受决定。

## 5. 当前实机边界和权限

**本Wave只授权静态源码/PE/REA只读静态工具与离线程序。** 不附加用户NBA2K22进程、不Frida运行时注入、不启动游戏、不修改真实游戏内存、存档、日期/比赛，不更改安全软件或系统权限。涉及真实游戏才能确认的选项写为`NEEDS_HUMAN_APPROVED_LIVE_TEST`并提供最小场景；不调用后继续宣称已验证。

不能把`静态候选`、`纯Python往返测试通过`、`真实游戏状态变化`、`保存重开后仍有效`视为同一成熟度。

## 6. Wave最终提交与停止条件

- 全部已授权领域（W03-00、04…12）均有`HANDOFF`或明确`BLOCKED/NOT_FOUND`结果；
- 累积研究日志可续接；版本、构建SHA、旧分支SHA、每项成熟度与Codex接收差异可查；
- 交付`W03_CONSOLIDATED_CODEX_HANDOFF.md`，同时列出原始184项仍未解决需求与第一版GM/Coach关键阻断点；
- 只推送`gemini_rea`，清洁工作区、回读HEAD；不得合并进正式工程、PR19、master；
- 完成后停止，等待Human启动**新的Codex集中审核与接收任务**；不将Gemini证据自行升级正式成功。
