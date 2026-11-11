# Durable tasks, disposable windows

Default work is sequential. Human explicitly requests saving A before switching
to B. Save first, confirm the durable commit, then switch. PRMS does not initiate
a switch, background capture or another model. Returning to A reads its own saved
context; B's current assignment does not hide A.

## Durable record

`SAVE_TASK_CONTEXT` is a task-scoped existing WriterGate operation. One Git tree
publishes the immutable context, per-task CURRENT, checkpoint and role CURRENT.
Each task has its own `roles/<role>/tasks/<task>/CURRENT.json`. Revisions preserve
previous plans and events. The window and temporary session capability are not
the memory store.

Input has `task_id`, `task_plan`, `load_spec`. The plan contains `objective` and
explicit lists `plan`, `progress`, `open_items`, `next_steps`, `human_decision_refs`.
Record actual Human wording as HUMAN_DECISION events with original sources;
plan references and model summaries cannot fabricate new approvals.

The load specification contains `core_repository`, exact `core_commit`,
`role_type`, ongoing Human `memory_choice_ref`, optional `stage`, `actions`,
`required_paths`, `optional_paths`, `selected_paths`, `history_depth` and
`selected_event_ids`. Resume rebinds this retained context-only selection to the
new session. An ongoing Human instruction survives a window switch; it grants
no additional execution or copy authority.

## Foreground commands

An isolated state store must already exist outside Core/domain code. Save uses
its current owner session. These commands do not create repositories, credentials
or services. Deployed hosts instead call the same operation through their ingress.

```text
python -B 01_os/06_execution/boot/context_management/prms/task_cli.py save --state-root <existing-isolated-state> --role <role-id> --session <current-owner> --payload <task-plan.json> --operation-id <unique-save-id> --isolated-test-only --output <new-save-receipt.json>
python -B 01_os/06_execution/boot/context_management/prms/task_cli.py list --state-root <existing-state> --role <role-id> --output <new-task-list.json>
python -B 01_os/06_execution/boot/context_management/prms/task_cli.py resume --state-root <existing-state> --role <role-id> --task <task-id> --session <new-window-id> --core-root <Core-checkout> --output <new-workbench-directory>
```

Resume gets Core version and loading instructions from durable state, without the
old chat, old session capability or old temporary plan files. It reads all latest
durable events for the selected task, including facts newer than its checkpoint;
lag and missing history are explicit. It does not change the current role/task
assignment or state. Updating frozen source versions remains an explicit action.

The new workbench contains readable `CONTEXT.md` with saved plan/progress/next
work, typed facts and decisions, gaps and actual selected Core bodies. It also
contains recovery JSON, plan, choice, history choice, exact-byte bundle and a
separately retained receiver request. Human opens/pastes the context into the new
window. No automatic app injection or model comprehension is claimed.

## Receiver file contract

`handoff_cli.py export`, `receive`, `verify-ack` use explicit Core/state,
plan/choice/history files. Export takes package and handoff ID; receive takes the
separately retained request and current receiver session. `--help` lists arguments.
Verification rereads exact source bytes/current state and binds role, task,
session and choices. Changed/missing objects, stale state and insufficient budget
are rejected. Outputs cannot silently overwrite. PARTIAL context retains gaps;
BLOCKED context cannot be exported as usable context. Context and transport byte
budgets are measured separately.

An ack proves receiver-tool file validation, not model identity, comprehension,
owner takeover, delivery or execution authorization. These artifacts are context
files; formal OS task messages retain communication_system's Human-relay contract.

## Dormant trusted-host port

`ingress.TrustedIngress(store, authority, enabled=False)` is callable but dormant.
HostAuthority authenticates opaque transport contexts and returns immutable
HostSession role/task/operation scopes and exact four-part CopyGrants. Mutation
and copy reauthenticate before publication. Expired/revoked/substituted/out-of-
scope calls are rejected. Host control may revoke sessions; recover is scoped.
Missing copy grants deny copy in every mode.

The host must keep this object, authority and transport outside model control.
It is an integration port, not a new identity provider or network service.
Fake-transport tests establish IMPLEMENTED_UNVERIFIED_PLATFORM only.
`require_enforced()` still refuses unproved fencing. Real GitHub/host/window
experiments remain NOT_RUN; deployment is outside this task's completion scope.

## 逻辑岗位连续性与工作窗口轮换（Human 原则：2026-10-29）

**逻辑岗位可以持续，模型会话不必永续。** `decision_architecture` 是现有
Model Routing 正式协作角色；`OS_PUBLIC_DEVELOPMENT_PLANNER` 等
`role_instance_id` 只是可复用的岗位实例标识，既不新增角色类型，也不赋予新权限。
模型提供商、OS 协作角色、岗位实例与领域业务人格不能混同。

一个实际工作窗口仍遵守“一个窗口一个任务”；同一逻辑岗位可以先后接任不同
`task_id`，但每个任务保留独立的 task packet、Human 决策来源、Run、证据与恢复记录。
不同岗位窗口不得把另一个任务的候选方案或私人工作叙事当作当前任务事实。

推荐主动轮换工作台，而不是等上下文耗尽：从干净、经核实的公共基线建立新窗口，
查询 Core/领域仓库**最新** HEAD，再按 B0（必需）、G1/G2（发现后按需）、
T1（当前任务）、T2（必要历史）、K1/K2（直接相关经验）加载；不要从旧长对话
无条件继承全部正文。重大 Human 决策、架构确认和交接发生时应立即建立**实际成功**
的耐久检查点，不等到窗口临近关闭。

若已部署且有权使用 PRMS 的隔离状态仓，则沿用本文件既有 `save/list/resume`
与 Human-relay 机制；否则使用经授权、可读回的 GitHub Run/任务档案恢复，明确
`recovery_source` 与精确 SHA，不得声称 PRMS 保存成功。需要岗位总览时，
可以在**现有**档案中维护轻量引用索引：
`role_instance_id`、`active_task_ids`、`latest_human_decision_refs`、
`task_status_index`、`source_versions`、`handoff_checkpoint`。
这些只是引用真实任务记录的导航字段，**不是**新增 WriterGate 操作、状态机、
数据库、自动窗口管理器或现行 PRMS schema 要求；不得复制形成第二套权威决策。

第一次跨窗口交班应由独立的新工作窗口核验：岗位身份、Human 决策及其来源、
任务隔离、最新源码版本、未完成事项与下一步。缺失或冲突要显示为缺口。
Fork 只产生分叉时的上下文快照；旧窗口之后的更新不会自动同步，
receiver ack 也不证明模型理解、交班成功或执行授权。以上是已批准工作方式，
**不是**宣称新平台自动集成、额外 PRMS 功能或真实交班试验已通过。

## 实测恢复状态与基线增量（2026-11-10）

下表补充上述工作方式的实测范围。研究门 G1/G2 分别检查任务恢复与恢复后的决策，
与 PRMS 的发现目录分层使用各自的上下文解释。

| 路径 | 来源与实测状态 | 证据边界 |
| --- | --- | --- |
| 空白 Codex 会话，经最小 seed 从 GitHub/Run 恢复 | #20 固定证据 `9b56abee9e8c8af78a7b2961944bedbdde97d7c4`。A 因默认 MCP 审批阻断而不可评估；仅调整 scoped 只读工具审批后的 B 为 G1 通过、G2 受限通过。 | B 恢复 Issue #19 的真实版本、Human 决策、历史审核、权限与下一步。执行侧原判 G2 部分满足，后续 GPT-6 实质审核改判 `PASS_WITH_NON_BLOCKING_GAPS`，保留显式 master 权限措辞缺口。成本最小与通用恢复成功率尚未验证。 |
| 网页版 GPT 规划基线 Fork | #21 记录 Human 转交的真实回答经 GPT-6 检查，恢复准确且决策合理。标记 `HUMAN_RELAYED_MODEL_OUTPUT / INDEPENDENT_TOOL_TRACE_NOT_AVAILABLE`。 | 原始回答来源是 Human 转交至规划对话；现有 Git 引用只承载该报告。缺独立工具读取轨迹与跨平台效率对照。#20 空白会话试验自身的基线 Fork 状态仍为未测试。 |
| 已批准隔离状态仓的 live PRMS save/list/resume | `PRMS_LIVE_NOT_TESTED`。 | 本轮 GitHub 恢复未执行该生产路径；生产授权迁移、自动化接班及平台内部身份/签名均未验证。 |

使用规划基线 Fork 时，保留基线所绑定的来源版本，再从当前任务入口读取分叉后的
Human 决策、候选、审核、未决事项与版本变化。重新核对远端状态，对差异按既有 stale
规则处理；记录实际增量读取、来源与缺口。任务恢复后，具体动作仍依据当前授权与
机制前置门判定。若评价效率，应同时记录检索量、输入与缓存用量、延迟及决策质量。

固定来源为
[原始实验档案](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---core/tree/9b56abee9e8c8af78a7b2961944bedbdde97d7c4/01_os/_runs/run-20261110-core-task-context-cold-recovery-001)、
[GPT-6 实质审核](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---core/issues/20#issuecomment-6767439407)、
[Human 转交 Fork 状态的记录与本次同步合同](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---core/issues/21)。

