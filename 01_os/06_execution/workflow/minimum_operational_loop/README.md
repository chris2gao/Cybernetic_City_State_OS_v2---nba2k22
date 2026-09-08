# 七阶段最小运行闭环 loader/runner

`run_minimum_operational_loop.py` 提供 `static`、`validate` 和 `materialize-pilot` 三个入口。
它验证 boot、registry、七阶段 schema、上下文管理、协同推演激活状态、runtime guard、
冻结测试包绑定，以及产物**声明的**写入 allowlist、重试/失效与审核角色/结论。
每阶段 payload 必填字段来自对应 schema，关键执行/审核字段另作类型与跨阶段约束检查。
`materialize-pilot` 复制并验证 fixture，不执行真实业务施工或测试进程。声明角色不同也不
证明现实中的审核独立。实际必需检查执行与日志证据使用 task_discipline 的 managed_verification；
确定性 runner 不替代模型或 Human 的语义判断、执行隔离或最终独立验收。
输出根不得位于 canonical workflow、boot、mechanism、registry 或 execution 目录。
