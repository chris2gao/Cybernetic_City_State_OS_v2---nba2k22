# NBA2K22 BIC Wave1/Wave2 · 独立离线子 Run 正式接续任务

## 一、身份、来源与现行授权

**任务 ID**：`NBA2K22-BIC-W1-W2-OFFLINE-SCOPED-OS-RUN-20261105-001`  
**领域**：NBA2K22 / Cybernetic City-State OS / Basketball Intelligence Core  
**执行角色/模型**：`execution / Codex`，负责离线阶段合同构建、真实 Core 检查、证据记录及检查点。  
**统筹和正式复审**：`decision_architecture / GPT-6`；依 Core 现行政策判定须由哪一合法 owner 或 Human 进行阶段接受；不得将执行者自身签名当作 Human 决定。  
**Human 最新批准**：明确批准 **建立 Wave1/Wave2 独立离线子范围 Run、原完整 BIC 父任务保持未完成**。只批准这一路线与准备工作；**不等于** Stage01–07 全部通过、23 项规范化映射的正式确认、Stage04 正式冻结、`master` 合并或真实游戏操作。

固定授权记录：本 Run `HUMAN_SCOPED_RUN_ROUTE_APPROVAL_20261105.json`。  
正式子范围候选定义：本 Run `W1_W2_SCOPED_RUN_CHARTER_CANDIDATE_v1.json`（7 项 `OFF-SC01` 至 `OFF-SC07`，未正式签收）。

**目标**：利用两批已审核工程和既有原始文件，建立**独立**、完整且证据边界明确的七阶段离线子 Run 候选；逐阶段取得**真实**核验与需要的 owner 处置，直到合法可执行的正式完成门或明确不可由执行岗位关闭的单一 owner 决策门。不要再把整个 BIC 的 8 项最终目标塞进本次子 Run，更不要改写原 A0/A v2。

## 二、固定对象与不重复工作

NBA 仓库：`chris2gao/Cybernetic_City_State_OS_v2---nba2k22`  
Core 仓库：`chris2gao/Cybernetic_City_State_OS_v2---core`

- 原 NBA master（2026-11-05 复核）：`66f8f73f1a91597f4562b834c2acad332ad9de5b`。
- 固定 Core master：`08d8e534a3438269aa7d7eb1b080ab11c172f462`。
- Wave1 已审核代码：`aec3dbaacd1d56b0c7cc1d40c2f70607493b9a4b`。
- Wave2 已审核代码：`cdcb293f8a690725cf9168225cc2046ab0574b2b`。
- 已验证集成候选：`4998a43a3f9f94d1013e574e99d29b4c3d666de4`。
- 正式工程与治理交接：`bb886c50028e8332849f5b03ad54711a16870cfa`。
- 独立双轨审查回执：`980ad8c713e06f118d645a6a0bb6dc114b8aacb1`。
- 原 A v2 Git blob：`e16fdf6c4ef69b0a90b8c4abd3856617030a7ae4`。
- 之前的正式 OS 运行器回执：`exit_code=33`、`identity:workflow_stage_01_requirement_modeling`；这个结论不可覆盖。

固定输入 Run：
`01_os/07_content/_runs/run-20261105-nba2k22-bic-os-integration-readiness-001/`

提议新子 Run：
`01_os/07_content/_runs/run-20261105-nba2k22-bic-wave1-wave2-offline-subscope-001/`

**必须先检查工作区、HEAD、远端和冲突**。优先在独立任务分支建立新 Run，不能直接操作 `master`，不能污染独立审核分支。若目标分支无法创建，只记录错误并保留可恢复的现有工作，不重做工程开发。

## 三、子 Run 的完整但有限成功标准

以 `W1_W2_SCOPED_RUN_CHARTER_CANDIDATE_v1.json` 为候选输入，将这七项逐项写入正式 Stage01 Requirement、Stage03 Result B、Stage04 Tests、Stage05 Steps、Stage06 Execution 与 Stage07 Verification 的交叉引用：

`OFF-SC01`：只读球员和球队基准、存档/赛季/截止时间/来源和身份隔离。

`OFF-SC02`：知识成熟度、数据覆盖、缺失/陈旧、徽章持有与资格未知，不乱猜原生机制。

`OFF-SC03`：球员/固定阵容诊断、角色候选与对比、Scope/来源一致性、PlayType 不完整负例。

`OFF-SC04`：Native/REA 候选计划仅只读映射；历史精确验证不过度继承，当前不宣称 Getter 认证，`execute=false`。

`OFF-SC05`：离线合成 2×2 主效应、交互、混杂负例；真实比赛因果保留 `NOT_CAUSALLY_IDENTIFIED`。

`OFF-SC06`：基准和诊断 CLI 的可复现离线调用、`query_at` 历史隔离、合成数据库不改变。

`OFF-SC07`：独立审核代码来源、技术测试哈希、回归和日志真实性、Git 恢复记录、无越权行为。

这些仅证明已完成的**离线能力**，不是父 BIC `SC-01..SC-08` 被满足。尤其完整 `SC-05` BIC-vs-BIC 自主竞争仍然 `NOT_DELIVERED`。旧研究/历史未绑定存档 `REAL_DATA_NOT_VERIFIED` 保留。

## 四、内部执行路线（七阶段保持原顺序）

**Stage01**：构建独立子 Run 的真正 A0/A 和确认绑定。原始父 A0/A v2 与两个 Human 原始确认仍保持精确 Git blob；不得简单套用父 A 来宣称子标准已获正式批准。对 23 项规范化变换逐项复用现有 `FIELD_EQUIVALENCE_MAP` 和校验收据；把子 Run 新增加的验收边界标注为**本次 Human 路线批准后的候选，待适用 owner 正式裁定**。严格区分旧 Human 的父语义确认、新 Human 的子 Run 路线批准、以及未来 owner 的子合同验收。

**Stage02**：复用已固定 12+8 来源、两批源码与回归和两份独立代码审核。分类 `STATIC_INSPECTED`、`RECORDED_TEST`、`INDEPENDENT_SOURCE_REVIEW`、`UNKNOWN_LIVE_EFFECT`。只读历史 SQLite 的 `UNBOUND` 和模式未知不得抬高来源成熟度。运行实际 Core `evidence_findings`，保存原始输出。

**Stage03**：就七项 `OFF-SC` 建立结果 B、输入/输出、可复现示例及与源码/测试关联，明确这是一份 Wave1/Wave2 子 Run 而非完整 BIC 完成结论。复用既有六项结果及 Wave2 扩展，不另建大型规则平台。

**Stage04**：冻结候选只能由适用 owner 正式批准。现有七测试文件的技术 SHA 固定为 `71d421a1a95263a5cb8ed0a6ab8144817f3d62103bf735ebc2275cb43d016906`，它**不是**正式冻结授权。准确确定新子 Run 应冻结哪些测试和必须覆盖的负例，给出正式阶段 owner 可签收的单一决策清单。必须在有效正式冻结后，再记录相应真实验证；不把以前的 `65 passed` 当成冻结后已经发生。

**Stage05**：最小改写已有七步计划，绑定离线子 Run 的责任、路径、检查点、失败与停止门；已审核业务实现属于历史已经完成的工程事实，不重构旧执行历史，不新开 parallel 数据库/REA/PRMS。

**Stage06**：工程执行证据引用既有 Wave1/Wave2 固定提交和审核凭证；必要的正式冻结后离线运行，在真实授权到达后按当前 Core 阶段流程完成。无授权时保留真实候选，不伪造 `attempts` 或提交过往代签回执。

**Stage07**：独立复核子 Run 的具体 `OFF-SC` 结果，保留与既有代码系列审核的区别；只有当前子 Run 有正式前序接受、冻结和实际独立验收，才允许声称完整 Run 通过。

实际 Core runner：
```powershell
python -B -X utf8 <CORE_ROOT>/01_os/06_execution/workflow/minimum_operational_loop/run_minimum_operational_loop.py static <CORE_ROOT> --json-output
python -B -X utf8 <CORE_ROOT>/01_os/06_execution/workflow/minimum_operational_loop/run_minimum_operational_loop.py validate <NBA_ROOT>/<NEW_SUBRUN_PATH> --repo-root <NBA_ROOT> --candidate <EXACT_40_HEX_COMMITTED_SHA> --json-output
```
对尚未获得 owner 决定的结构候选应运行适用子校验，不应因全量 Run 仍为 `candidate_pending_owner_acceptance` 反复调用 `validate`，浪费窗口。待产生真正可验证的阶段完整提交，再运行完整正式门。保持 Core 真实退出码和 findings。

## 五、权限与 Loop

本次 Human 批准**子 Run 路线及所需普通离线准备工作**。所有阶段 owner 接受、独立 review、正式冻结和正式验证仍须真实发生。Codex 可以一次性把所有可完成的候选产物整理好，**不必每完成一个格式字段就停止**；同一证明缺口重复出现时只记录一次明确 blocker，并继续其他不依赖它的安全工作。

如有超出批准范围的承重语义变化，需先提交 GPT/合法 owner 裁决；不允许擅自把离线方案变成实机 Native 调用，或者绕过完整七阶段发布/历史门。

**禁止**：修改父 A0/A v2；伪造阶段 `complete`、`Human_confirmation`、正式阶段控制签名或历史 owner 决议；业务代码重新开发或旧 P0 重跑；合并 master；连接 NBA2K22、推进游戏日历、Native/REA 写入、修改存档；上传大型 SQLite/备份。

## 六、最终交付与真正停点

交付一个已提交的 `SCOPED_RUN_HANDOFF.md`，附实际子 Run SHA、适用静态和 Stage01/02 校验回执、七项 OFF-SC 验收矩阵、测试包与真实重跑证据、Core 完成门真实状态、精确 owner 决策项目；Git/PRMS 恢复检查点。若 PRMS 仍不可用，写明 `NOT_SAVED`，不用重新造状态仓。

如果执行过程中由于 Core 的正式 owner 门仍无法进一步推进，**应当把准备好的候选和剩余 owner 决策集中为一次审查包，结束在明确的 `PENDING_OWNER_ACCEPTANCE`**；不要继续发布微型“恢复任务”或循环验证相同错误。

GPT-6 最终检查证据与合规性；Human/合法 owner 按适用 Core 授权要求作真实阶段决定。只有 Core 验证得出实际 PASS，才可称子 Run 正式完成。父 BIC 始终未完成，主线合并与任何真实游戏操作仍各自独立授权。

**现在按本合同开始子 Run 规范化和验证准备，不重复 Wave1/Wave2 工程开发。**
