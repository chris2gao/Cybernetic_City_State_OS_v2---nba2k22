# 阶段协同推演闭环 · 实现契约

本目录保存机制的机器可读实现契约、validator 与固定测试 fixture。当前实现已经覆盖 P2–P7 的完整 staged-inert 链，但不产生 activation 权限。

## 组成

- `结果对象契约_v1.yml`：8 个对象家族、45 个唯一对象类型、47 个 MM 结果名及两项组合映射；
- `状态转换与不变量契约_v1.yml`：10 个独立状态维度、16 条跨维度不变量、append-only 转换；
- `路由与失败契约_v1.yml`：5 个 router、26 条失败码并集与 exit class 映射；
- `加载与receipt契约_v1.yml`：load result、dormant/full/incremental receipt 可见性与原子发布边界；
- `verify_stage_collaborative_deliberation.py`：static、instance、material_event、review_execution 四种确定性验证模式；
- `fixtures/`：正例、退出码、15 个 canonical 反例、material-event 与 review/execution 用例。

字段存在不等于模型充分。结果对象与验证过程必须同时遵守四层模型空间、承重维度判定和 schema 充分性 fail-closed 规则。

当前实现为 `staged_inert`。boot、registry、loader 和 workflow reference 只建立可发现与可验证链；activation 与 master 集成分别需要 Human 授权，二者不得相互替代。
