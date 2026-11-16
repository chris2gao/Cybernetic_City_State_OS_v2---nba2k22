# 七阶段最小运行闭环 loader/runner

## 草稿候选绑定同步

`sync-candidate <draft-run-root> --repo-root <checkout>` 预览实际 unified diff，退出码 1 表示有待同步的文件。加 `--apply` 才写入。它按已有阶段顺序从实际 Artifact 字节刷新下游 `input_refs`、Manifest 哈希和版本。初次同步后再预览应返回 0 且差异为空。输入错误返回 33。

仅接收 canonical Run 根中的 `candidate_pending_validation` Run 和按阶段 schema 标为 `planned` 的 Artifact，允许仅物化连续的前几个阶段。Run 的 `task_packet_ref` 必须绑定当前任务分支 HEAD 中的任务包 blob，且 Manifest 与每个 Artifact 都要在该任务的 `allowed_changed_paths` 内。完整的提交祖先历史为同一 Run 的 Artifact 与 Manifest 版本提供下限。检测到正式签收、完成或已发布状态时拒绝，后继处理走正式失效与再确认。

命令不创建 Artifact、版本、Human 确认或完成记录，也不执行 `validate`。用户编辑 Artifact 时负责确定语义版本及受影响的 Human 确认，正式门仍复核冻结、签收和历史。单文件原子替换，最后写 Manifest，重新运行可修复未完成的绑定同步。

`run_minimum_operational_loop.py` 提供 `static`、`validate` 和 `materialize-pilot` 三个入口。
它验证 boot、registry、七阶段 schema、上下文管理、协同推演激活状态、runtime guard、
冻结测试包绑定，以及产物**声明的**写入 allowlist、重试/失效与审核角色/结论。
每阶段 payload 必填字段来自对应 schema，关键执行/审核字段另作类型与跨阶段约束检查。
Stage01唯一活动规范要求A0/A双确认及内容/版本绑定、具体结果项和SC/RES/EVQ覆盖。
Stage02区分背景与可行性，保留来源版本、成熟度和限制；背景或UNKNOWN不能单独支撑B。
`materialize-pilot` 复制并验证 fixture，不执行真实业务施工或测试进程。声明角色不同也不
证明现实中的审核独立。实际必需检查执行与日志证据使用 task_discipline 的 managed_verification；
确定性 runner 不替代模型或 Human 的语义判断、执行隔离或最终独立验收。
输出根不得位于 canonical workflow、boot、mechanism、registry 或 execution 目录。

完整验证使用 `validate <run-root> --repo-root <repository> --candidate <40-character-commit>`。
它从指定提交的 regular Git blobs 读取 manifest、七阶段产物及 schema，不读取工作区副本
作为候选证据。结构通过后，复用 publication gate 的七阶段历史解析，调用同一个协同推演
owner 检查每阶段 plan 与 completion。owner / gate 拒绝通过 runner 退出码 34 传出，
诊断保留 gate 的实际失败码与原因；候选源或结构错误为 33，缺少 candidate 为 41。

被检仓库中的 Python 文件是候选数据，不作为判定程序执行；判定程序来自当前 runner
所在安装树。本入口不使用 publication boundary 豁免，因为调用者明确要求验证这个 run。
验证单个 run 不是整个分支的发布准许，也不是运行了业务测试、真人认证或独立验收。
`validate_structure` 及静态 pilot 正例仍只提供结构证据，不能代替完整提交态验证。

## 显式业务决策候选入口

`next-business-action <input.json>` 调用同一 runner 的 `next_business_action`，
对一个有限业务步骤集合返回一个选择，不运行工具、不循环、不创建后台任务或授予权限。
这是金蛋工程候选的 opt-in 路径，不改变 `validate` 的七阶段冻结与签收规则。

输入包含 `goal`、`context`、`facts`、`steps`、`parent_done`。每条 fact 带
`value`、`source_ref`、`bindings`；bindings 是明确的有效性条件，例如
`{"pid":8352}`。不匹配或缺少的上下文使该 fact 失效，其他事实及 false 观察仍可复用；
空 bindings 仅适用于领域已确认不随当前上下文变化的来源/决定，不能用它掩盖 live 依赖。

每步含 `step_id/goal/kind/requires/depends_on/done/scope`，可附
`resource/channel/choice_ref/proposed_choice`。模型/领域先确定真实必需前提和依赖，
仅把已证明可执行的决定性检查标成 `preflight`；其顺序优先于业务动作与可选准备。
`diagnostic` 限定有证据的局部排障，不是通用高优先权。任何优先级均不绕过 Ready/依赖。
步骤内容仍归模型与领域所有者；此入口不会从命令字符串猜测风险或自动发现依赖。

`approved_choices` 保存批准的业务选择；PID/worldline变化不会改它。引用它的动作不得
携带不同 proposed_choice。`stopped_channels`、`blockers`、`attempted` 和
`unknown_resources` 由当前 Human/领域观察提供。受阻节点不会隐藏无关安全节点，
但被尝试而未确认 Done 的动作及 UNKNOWN 资源要求领域 journal/readback，不自动重放。
调用方必须在执行前耐久登记副作用尝试并在之后读回；纯选择函数不是持久幂等服务，
不能在重启后清空这些输入来宣称安全。

每步和父任务的 `done` 都指向独立领域观察；子步骤结束不等于父 Done。
输入内容来自可信领域适配/任务执行者，这个选择器不认证 Human、事实真伪或权限签名。
冻结摘要、allowlist、独立验证等既有完整门仍走原 `validate` / managed verification。

`business-time-quality <input.json>` 接收既有报告汇总 `metrics` 及可选
`first_event/first_blocker/capture_end`；不新采集事件，也不代替 factmon。
输出分层计数、duration算术和、REPORTED监控区间及事件跨度；唯一工具墙钟与未观测归因
保留UNKNOWN，不据耗时批准动作或宣布研究完成。
缺失的计数或耗时字段返回 null（未知），不会当作零；事件时间戳必须带明确时区。

可复算的实际调用及T01–T14测试位于
`01_os/_runs/run-20261116-golden-egg-path-efficiency-001/`；T15真实业务对照未激活。
