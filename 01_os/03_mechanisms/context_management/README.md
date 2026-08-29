# 上下文管理

全局机制，负责最小有效上下文、固定角色入口、结构化 handoff、版本 stale、文件隔离、
显式发布与产物生命周期。workflow 阶段引用本机制，不复制机制实例。

## Human 总览

- `开发总结_v1.md`：面向 Human 的实现前后对照、开发链、验证边界、质量评价和后续更新入口。

该总结用于直观检查和持续理解，不替代下面的 canonical 运行规则。

## Canonical 组成

- `方法论_v1.md`：三平面、恢复与确定性控制原则；
- `文件隔离与产物生命周期_v1.md`：文件类别、task×role 区域、发布与清理；
- `依据材料/`：A v1/v2、Human 确认、研究与运行证据；
- `实现/文件布局契约_v1.yml`：机器可读路径与生命周期契约；
- `实现/verify_context_structure.py`：结构、引用和禁止项 validator；
- `工作集与归档契约_v1.yml`：累计面（`_runs`、`_communication`、`_dev`、领域 `_runs`）
  的生命周期分类、默认可见性、归档四条资格与引用安全；
- `工作集与归档_v1.md`：上面那份契约为什么长这样，以及支撑它的实测数字。

工作集工具在 `../../06_execution/boot/context_management/working_set/`：
`visible_set.py`（默认可见集与排除量）、`lifecycle.py`（状态分类，不在枚举里一律
`unknown`）、`reference_safety.py`（引用扫描，报路径不报布尔）、
`archive_group.py`（通用归档搬移，无 force 开关）、
`validate_working_set.py`（契约与代码的漂移守卫）。

活动执行角色裁决是 `../../_dev/决定_谁执行_v0.2.md`；其 v0.1 仅作历史保留。
启动入口在 `../../02_boot/context_management/`，加载说明在
`../../06_execution/boot/context_management/`，注册表在
`../../05_registry/context_management_v1.yml`。

机制失效必须在 validator 或加载 receipt 阶段显现；不得静默退回完整历史、旧路径或
工作树“安全边界”假设。