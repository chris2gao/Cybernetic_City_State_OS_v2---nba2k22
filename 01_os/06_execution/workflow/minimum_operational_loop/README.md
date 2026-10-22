# 七阶段最小运行闭环 loader/runner

`run_minimum_operational_loop.py` 提供 `static`、`validate` 和 `materialize-pilot` 三个入口。
它验证 boot、registry、七阶段 schema、上下文管理、协同推演激活状态、runtime guard、
冻结测试包绑定，以及产物**声明的**写入 allowlist、重试/失效与审核角色/结论。
每阶段 payload 必填字段来自对应 schema，关键执行/审核字段另作类型与跨阶段约束检查。
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
