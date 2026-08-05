# 阶段协同推演闭环加载器

## 状态

`active_dormant`。机制可被 workflow 发现、加载并评估 trigger；默认不创建讨论 session。full 或 incremental 路线仍受当前 profile gate、任务权限与外部行动单独授权约束。

## 加载步骤

1. 读取 `08_os/02_boot/stage_collaborative_deliberation/启动清单_v1.yml` 与 registry；
2. 按 load order 校验公共方法、核心契约、append-only 激活状态、Human 激活授权、v1 基础 validator 与 v2 当前 validator 的精确路径、blob 和版本；
3. 执行 `verify_stage_collaborative_deliberation_v2.py static <repo-root>`，非零即停止；
4. 根据 workflow 引用文件解析且仅解析一个当前 profile，并验证其 activation-state 与 validator 引用；
5. 评估 profile trigger：未命中时走 dormant；命中时只形成 full 或 incremental 候选，不自动取得任务权限；
6. 注入最小机制引用、profile 引用、机器契约引用、激活状态引用和 receipt 契约，不复制机制正文；
7. 对当前 run 的阶段实例执行相应 mode validator；
8. 仅在 validator exit 0 后原子发布耐久对象与 `receipts/stage_receipt.yml`。

## 默认排除

不加载完整历史 run、原始研究报告、非活动证据版本、无关 profile、private/scratch、已 supersede 契约。实例根必须位于当前 run 的阶段输出目录；canonical 目录禁止保存 live instance state。

全局 activation 不预授权外部研究、专家工具、不可逆操作、受保护路径修改或任何当前任务之外的执行。

## 失败与回滚

missing、partial、stale、unknown、invalid、unauthorized 全部 fail closed；禁止 stale fallback。未授权行动必须零副作用，partial publish 不得产生有效 receipt。激活配置的回滚目标是 `激活状态_v1.yml` 声明的精确 staged-inert master，回滚同样需要 Human 授权。
