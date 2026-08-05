# 阶段协同推演闭环加载器

## 状态

`staged_inert`。本文定义加载行为，不授权 activation。

## 加载步骤

1. 读取 `08_os/02_boot/stage_collaborative_deliberation/启动清单_v1.yml` 与 registry；
2. 校验所有精确路径、blob、版本和 staged 状态；
3. 执行 `verify_stage_collaborative_deliberation.py static <repo-root>`，非零即停止；
4. 根据 workflow 引用文件解析且仅解析一个当前 profile；
5. 注入最小机制引用、profile 引用、机器契约引用和 receipt 契约，不复制机制正文；
6. 对当前 run 的阶段实例执行相应 mode validator；
7. 仅在 validator exit 0 后原子发布耐久对象与 `receipts/stage_receipt.yml`。

## 默认排除

不加载完整历史 run、原始研究报告、非活动证据版本、无关 profile、private/scratch、已 supersede 契约。实例根必须位于当前 run 的阶段输出目录；canonical 目录禁止保存 live instance state。

## 失败与回滚

missing、partial、stale、unknown、invalid、unauthorized 全部 fail closed；禁止 stale fallback。未授权行动必须零副作用，partial publish 不得产生有效 receipt。回滚目标是本次加载前的精确已接受 checkpoint。
