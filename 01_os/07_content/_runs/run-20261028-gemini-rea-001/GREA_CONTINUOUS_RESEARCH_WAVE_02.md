# GREA Wave-02 · Gemini连续有界逆向研究 → Codex阶段性审核

**日期**：2026-10-29。**授权来源**：Human明确提出“先让Gemini继续跑，额度较充足；最后由Codex整理”。**分支**：`gemini_rea`，基于PR19旧工程快照 `39086984adfa554d36315382d41bc2e5d2e54c39`，原GREA-01成果 `1818fc7274c94fb6bd4e265273e217ba75ade1e7`。Codex PR19在本轮计划时已推进至 `bc11fa7926a7eaf390b668515e03dc8507ecb656`，不自动merge/rebase/cherry-pick；Codex审核时需独立比较。

## 目的

利用Gemini更多的研究额度连续消除游戏Coach第一版核心缺口，在**一次阶段**内做多个严格独立的小任务，让Codex最后集中对照、选择性修复与接收。不再每个任务都必须Codex批准才开始；但不能无限扩展任务，也不能把离线模拟测试计为原生实证。

### 当前授权范围：同一Wave，最多三个工作包

1. **W02-A / GREA-01-EVIDENCE-REPAIR（必须先做）**：独立复审已提交的对手Gameplan证据；抽原始字节、复核ABI/函数身份/对象布局/保存副作用；纠正无证的“已完整逆向、已提交生效”说法；更新不确定性和失败反例。特别检查：GREA-01称`GAMEPLAN+0x2`是uint16 owner_team_id，却声称`0x146ec50: mov rcx,[rcx+2]`是取Coach指针。这至少是需原始指令核对的类型矛盾。另证`0x131f110`是否确为commit，`0x7a7aab`是否位于相同原版UI调用链，及35槽/880字节是否有真实PE字节证据。**这是静态证据复核，不是重新运行旧模拟测试。**
2. **W02-B / GREA-02-MATCHUP-DEFENSE**：在已确认的Gameplan/Matchup结构范围内，逐项寻找18项个人防守设置的真实位置、取值域与Setter或原版业务修改来源。按字段分表：`CONFIRMED_FROM_BYTES`、`CANDIDATE`、`UNKNOWN`。必须给出字段移位/掩码证据、相邻位不变反例；**若GREA-01对象或生命周期未闭合，只能做独立静态表/译码候选，不能声称原生Gameplan提交已恢复**。
3. **W02-C / GREA-03-PLAYBOOK-68-SLOTS**：调查球队Playbook四个分区（Regular 30、Bench 20、Endgame 10、Favorite 8）真实对象、槽位结构、play CRC→类别/来源、增删换/提交刷新流程。特别区分共享战术定义与球队持有战术书、`find`与`ensure`和持久`apply`；证据不足不能宣称已支持68槽操作。作为独立研究链，可以不依赖GREA-02的结果。

**明确不授权**：GREA-04至09；球员人格/GM正式合同修改；数据辅助包`A01_SHOT_ENUMS/A02_SHOT_ARRAYS/B01_PLAYER_CHART_GETTER`是Codex另行冻结输入的独立辅助任务，不能混入本Wave，也不能更改其inputs/tools；如你正在跑该辅助包，先按其原任务完成并停止，之后再切到本Wave。任何实机attach、Native写、游戏UI、进度/日期、存档或测试游戏状态变更均不在本轮授权内。

## 必须继承的上下文（按需而非全仓重复扫描）

先遵守仓库/领域AGENTS和OS；读取`PROJECT_INDEX.md`、模块登记与同步契约、REA `REA_WINDOW_CONTEXT_HANDOFF_20261028.md`、`DISCOVERY_NOTES.md`、`VALIDATION_RESULTS.md`、`ROLE_EXECUTION_PROGRESS.md`、`K04_COACH_AND_PLAYS.md`、`data/action_registry.json`、`data/native_bindings.json`；读取此Run原`README.md`、`GREA_01_OPPONENT_GAMEPLAN.md`和全部已有GREA-01候选与交接。原始被引用的本机PE只在已获项目授权、按固定SHA且工作区隔离情况下**只读**分析；无工具/权限/二进制时如实`BLOCKED_ENVIRONMENT`，不得引用自己生成的反汇编文字冒充已读PE。

## 每个工作包的内部Research Loop（自动继续，最多4轮）

每轮必须产生完整记录：

`iteration_id`, `fixed_git_head`, `target_exe_sha256_checked`, `specific_claim_under_test`, `primary_raw_byte_or_tool_output_ref`, `independent_countercheck`, `negative_evidence`, `claims_downgraded`, `code_or_doc_delta`, `offline_tests`, `next_question`。

- 一轮限定一个核心原生假设及其直接依赖；优先原始字节/反汇编及有界xref，而不是写更长的自然语言描述。
- 每次尝试最多只研究小范围函数/调用者，不反复整游戏Ghidra；同样失败连续两轮或无新证据连续两轮时，当前包以`STILL_PARTIAL`/`BLOCKED`停止，**继续下一包可独立研究的部分**。
- 每包最多4轮，全部Wave最多12轮；不得通过持续细分任务自行扩大预算、对象范围或创建W02-D。
- 每轮Git checkpoint，结果目录以`W02_A/`、`W02_B/`、`W02_C/`区分，严禁覆盖GREA-01原始证据。每包在结束时用`STATUS=STATIC_CANDIDATE|STILL_PARTIAL|NOT_FOUND_IN_BOUNDED_SCOPE|BLOCKED_ENVIRONMENT`准确归档。
- **真实性门槛**：`OFFLINE_TESTED`只证明Python模块的编解码逻辑；源码注释、模拟Harness的SUCCESS、报告中的手写伪反汇编不是证明真实Native Commit调用的证据。单元测试不得自我验证完全源自同一未经确认的布局常量。
- 不能用直接写游戏业务内存冒充真正Native机制；只做隔离候选/证据。必须保证没有从实验候选向正式Facade/Registry/Runtime/索引升级成熟度的操作。

## 交付文件（每包都必须）

在`01_os/07_content/_runs/run-20261028-gemini-rea-001/W02_A/`等目录提交：

- `HANDOFF.md`：目标、真实结果、已证/未证和停止条件（包含已撤回的过度结论）。
- `EVIDENCE_LEDGER.json`：每条claim的原始来源文件、精确文件版本、PE SHA、RVA、函数范围、调用者、ABI、证据成熟度、反例、UNKNOWN。
- `REPRODUCTION.md`：真实离线复验命令、实际输出/退出码、工具不可用时的确切限制；不只写预期输出。
- `ITERATIONS.jsonl`：每一轮的可重放原始证据索引、新发现与自纠。
- `CODEX_REVIEW.md`：最多10个高优先级独立审核点，以及Codex需自行证实哪些。
- 若有候选代码，只允许写在`08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_control/experimental/gemini_rea/W02_*/`。无新Native证据时不要求凑代码。

完成全部授权包后，再提交`W02_CONSOLIDATED_CODEX_HANDOFF.md`，包含三包状态、可复用候选、重复或相互矛盾证据、固定Git SHA（最后提交后必须输出准确SHA）、改变文件范围、Copilot/Codex逐项审查建议。保留历史GREA-01；不整体标记为已实机可用，不自动将分支合并到正式PR19/master。

**最终停机条件**：三个包全部完成或各自达到封闭限制后即停止，等待Codex集中审核和Human下一轮授权。任何新的Gemini研究只在另一个明确的Wave开始。
