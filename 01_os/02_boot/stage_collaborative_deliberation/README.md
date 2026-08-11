# 阶段协同推演闭环启动入口

当前状态为 `active_dormant`：机制可发现、可加载，默认不创建讨论 session。

`启动清单_v1.yml` 冻结公共方法、核心契约、激活状态、Human 授权、canonical runtime guard、v1 基础 validator 与 v2 当前 validator 的精确路径和 blob。加载时先运行 runtime guard，再运行 v2 static；任一非零结果均 fail closed。

未命中 profile trigger 时走 dormant 并产生 receipt；命中时仍须通过当前任务的 start gate 与权限检查。全局激活不替代其他授权。
