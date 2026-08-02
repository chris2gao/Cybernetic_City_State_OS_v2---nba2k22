# 环境与能力 receipt

本机制定义任务在依赖环境能力前应读取的事实契约。receipt 把“当前实测可用”与“registry
曾验证过”分开，也把宿主能力、任务授权和发布门禁分开；任何字段都不授予写入、发布或激活权限。

## P0 边界

- 本阶段只定义 schema、正负例语义和一次真实测量。
- 本阶段不实现 loader，不写入 `08_os/06_execution/`，也不进入 boot。
- P1/P2 可把通过本 schema 的 receipt 作为输入，但必须在 `invalidation_events` 命中后重测。
- 实测脚本只存在于 run 的 `_runtime/`，完成后删除；run 中只保留脱敏 receipt 与验证摘要。

## Canonical 文件

- `实现/环境能力receipt_schema_v1.yml`：v1 JSON Schema。受任务包固定路径约束，该文件以
  `.yml` 命名但内容是严格 JSON；验证时复制为逐字节同哈希的临时 `.json` 后调用已登记 wrapper。
- `实现/正例与负例说明_v1.md`：正例、四类必拒负例、路径脱敏和验证口径。

## 不变量

1. 顶层必须覆盖 `environment_class`、`model_availability`、`toolchain`、
   `publication_transport`、`boundaries` 与 `runtime_limits`。
2. 每个事实都是 observation，必须带 `measurement_source`；`observed` 必须有 `value`，
   `not_observable` 必须有 `reason` 且不得伪造 value。
3. receipt 只保存路径语义、类别、仓库相对引用或占位符；schema 递归拒绝 Windows drive-root、
   UNC 及常见个人 Unix home/mount 绝对路径形态。
4. `measured_at` 记录本次测量时刻；`invalidation_events` 明确何时失效，不把历史 receipt
   当作当前能力。
5. toolchain 同时报告安装可见性和本次是否验证可运行；registry 中的历史版本不能冒充当前实测。

## 故障显现

结构或路径约束错误在下一次 schema 验证时显现；环境漂移只在命中失效事件后的重测中显现。
若消费者跳过重测，错误可能延迟到下一次工具调用或发布门禁，因此 P1/P2 必须把失效检查作为输入前置条件。
