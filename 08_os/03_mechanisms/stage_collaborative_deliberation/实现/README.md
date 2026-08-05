# 阶段协同推演闭环 · 实现契约

本目录保存机制的机器契约、验证器与固定 fixture。核心契约继续使用已接受的精确 blob；当前运行状态由 `../激活状态_v1.yml` 以 append-only 方式声明为 `active_dormant`。

## 组成

- `结果对象契约_v1.yml`：8 个家族、45 个对象类型、47 个结果名；
- `状态转换与不变量契约_v1.yml`：10 个状态维度、16 条不变量；
- `路由与失败契约_v1.yml`：5 个 router、26 个失败码；
- `加载与receipt契约_v1.yml`：dormant/full/incremental receipt 与原子发布边界；
- `verify_no_canonical_live_state.py`：拒绝 canonical live instance state；
- `verify_stage_collaborative_deliberation.py`：v1 基础 mode 验证逻辑；
- `verify_stage_collaborative_deliberation_v2.py`：当前 active-dormant static validator，现场重算完整 exact-ref 图并复用 v1 的 instance、material-event、review-execution 逻辑；
- `fixtures/`：35 个固定回归用例。

当前机制可加载但默认 dormant。进入 full 或 incremental 仍需命中 profile trigger 并满足当前任务 gate；全局激活不替代其他授权。
