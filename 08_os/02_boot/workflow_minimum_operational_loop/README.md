# 七阶段最小运行闭环启动入口

本入口加载跨阶段运行契约、七个阶段 schema、统一 runner 与 registry，并先验证上下文管理、
阶段协同推演 active-dormant 状态、canonical runtime guard 和 v2 static。

默认协同路线为 `dormant`，每阶段仍必须产生有效 receipt；本入口不自动创建 session，
不授权外部行动或不可逆操作。运行产物只进入 `08_os/_runs/<run-id>/`、
`08_os/07_content/_runs/<run-id>/` 或仓库外目录，不得进入 canonical 路径。
