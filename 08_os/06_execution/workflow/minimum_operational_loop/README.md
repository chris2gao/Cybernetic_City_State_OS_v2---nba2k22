# 七阶段最小运行闭环 loader/runner

`run_minimum_operational_loop.py` 提供 `static`、`validate` 和 `materialize-pilot` 三个入口。
它验证 boot、registry、七阶段 schema、上下文管理、协同推演激活状态、runtime guard、
冻结测试、写入 allowlist、重试/失效与独立审核。确定性 runner 不替代模型或 Human 的语义判断。
输出根不得位于 canonical workflow、boot、mechanism、registry 或 execution 目录。
