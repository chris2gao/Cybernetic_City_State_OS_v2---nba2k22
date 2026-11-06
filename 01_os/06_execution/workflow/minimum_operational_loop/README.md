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
