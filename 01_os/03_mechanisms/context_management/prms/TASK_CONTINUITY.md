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

