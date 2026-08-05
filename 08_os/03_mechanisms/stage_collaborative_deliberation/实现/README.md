# 阶段协同推演闭环 · 实现契约

本目录保存机制的机器可读实现契约、validator 与固定测试 fixture。核心契约继续使用已接受的精确 blob；当前运行状态由上级目录的 append-only `激活状态_v1.yml` 声明为 `active_dormant`。

## 组成

- `结果对象契约_v1.yml`：8 个对象家族、45 个唯一对象类型、47 个 MM 结果名及两项组合映射；
- `状态转换与不变量契约_v1.yml`：10 个独立状态维度、16 条跨维度不变量、append-only 转换；
- `路由与失败契约_v1.yml`：5 个 router、26 条失败码并集与 exit class 映射；
- `加载与receipt契约_v1.yml`：load result、dormant/full/incremental receipt 可见性与原子发布边界；
- `verify_stage_collaborative_deliberation.py`：v1 基础 validator，继续提供 instance、material_event、review_execution 及历史 static 逻辑；
- `verify_stage_collaborative_deliberation_v2.py`：当前 activation-aware validator，在复用 v1 非 static 逻辑的基础上验证 active-dormant 状态、Human 授权、boot/registry、七引用与 append-only overlay；
- `fixtures/`：正例、退出码、15 个 canonical 反例、material-event 与 review/execution 用例。

字段存在不等于模型充分。结果对象与验证过程必须同时遵守四层模型空间、承重维度判定和 schema 充分性 fail-closed 规则。

当前机制已全局激活为 `active_dormant`：可发现、可加载、可评估触发条件，默认不创建 session。full 或 incremental 仍由当前 profile trigger、任务级 gate 与权限共同决定；全局激活不替代外部行动授权或不可逆操作授权。
