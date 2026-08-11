# 阶段协同推演闭环加载器

## 状态

`active_dormant`：机制可被七个 workflow 阶段发现和加载，默认路线仍为 dormant。

## 顺序

1. 读取 boot 与 registry；
2. 校验全部精确路径、blob、版本、激活状态与 Human 授权；
3. 运行 `verify_no_canonical_live_state.py <repo-root>`，非零即停止；
4. 运行 `verify_stage_collaborative_deliberation_v2.py static <repo-root>`，非零即停止；
5. 解析且仅解析当前 stage 的一个 profile；
6. 未命中 trigger 时产生 dormant receipt；命中时形成 full 或 incremental 候选，并继续执行当前任务的 gate 与权限检查；
7. guard 与相应 validator 均通过后，才可在当前 run 的阶段输出目录原子发布对象与 receipt。

canonical 目录不得保存 live instance state。全局激活不替代当前任务权限，也不替代外部行动或不可逆操作的单独授权。missing、partial、stale、unknown、invalid、unauthorized 一律 fail closed，禁止 stale fallback。
