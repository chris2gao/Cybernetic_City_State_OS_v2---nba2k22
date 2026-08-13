# 通讯系统执行入口

所有入口均为一次性显式命令；加载本目录不会启动后台进程或产生 live state。

- `task_space_initializer/initialize_task_space.py`：在本地通讯根创建任务空间；`--root`
  可选，解析优先级为显式参数、`CITYSTATE_COMMUNICATION_ROOT`、最后
  `Path.home() / ".citystate" / "communication"`；
- `validator/validate_communication_system.py`：纯校验入口，不授权、不发布；
- `validator/receiver_bootstrap.py`：按精确 v2 pointer 复验 constitution/receipt 后读取封闭上下文；
- `publisher/publish_message.py`：经 resolver/gate 发布不可变 constitution、消息、索引和
  compliance receipt，并输出供 Human 转交的 v2 pointer；
- `publisher/republish_github.py`：在 Web/Human 显式触发时按材料、消息、索引顺序写入任务仓库并执行一次非强推收敛；
- `convergence/converge_task.py`：对精确 task 路径执行一次 fail-closed Git 收敛；
- `archive/archive_task.py`：满足前置条件后整体归档任务并删除显式 private runtime；
- `validator/run_frozen_stage04_tests.py`：只读加载冻结 Stage04 oracle，并把每个案例路由到上述生产实现；不回退到 Stage04 synthetic adapter。

受保护动作必须同时绑定当前任务权限结构和 `required_refs` 中可物理读取的 Human 授权文件。
发布器先读取并绑定发送方/接收方端点卡，再验证文档与权限引用，最后按“消息→发送方索引”顺序提交；
任一步失败均不留下可见的悬空消息。归档命令只接受任务目录内可读的完成指针、残留记录和
private-runtime 策略引用，并在仓库内运行时确认为未跟踪且已忽略后才执行删除。

任何命令非零退出后都停止，由 task navigation owner 或 Human 决定是否继续。

新 formal action 不接受直接 publisher bypass 或仅有自然语言正文的 receiver bootstrap。
历史 v1 消息读取必须显式选择 `--legacy-v1`，不得用该模式新建 formal handoff。
