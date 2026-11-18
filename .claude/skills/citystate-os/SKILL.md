---
name: citystate-os
description: "City-State Core OS 的地图与入口。新窗口开始工作、需要了解 OS 有哪些机制和角色、或要找某个机制该由哪个 skill 加载时使用。列出全部机制单元、五个角色各自加载什么、角色初始化方法与 B0 必读文件。"
---

# City-State OS 总入口与目录

> 生成文件，勿手改。来源：`01_os/05_registry/skills_v1.yml`。修改来源后运行 `python -B 01_os/06_execution/skills/generate_skills.py`。

## 何时加载

任何角色初始化的第一步；不确定该加载哪个机制时。

适用角色：初始化必载 = 任务规划、任务开发、审核、特色内容开发、特色内容教学或使用；按触发加载 = 无

## 必读（按顺序全部读完）

- `AGENT_WORKING_DISCIPLINE.md`
- `AGENTS.md`
- `01_os/README.md`
- `01_os/开发入口与单窗口任务规范_v1.md`
- `CORE_MANIFEST.yml`

## 命令

- `python -B 01_os/06_execution/skills/validate_skills.py --repo-root .` → skills_valid，退出 0

## 边界与停止

- skill 与角色标签都不授予任何权限；受保护动作仍按开发入口 §11 与 repository_publisher_authority_v1.yml
- 窗口是临时工作台：决定、结论、证据在形成时落进仓库或简报库

## Core OS 机制单元目录

| Skill | 内容 | 生效等级 | 任务规划 | 任务开发 | 审核 | 特色内容开发 | 特色内容教学或使用 |
|---|---|---|---|---|---|---|---|
| `citystate-os` | City-State OS 总入口与目录 | — | 必 | 必 | 必 | 必 | 必 |
| `os-mechanism-activation` | 机制激活与正式动作宪法 | L3_EXECUTION_GATED | 必 | 必 | 必 | 必 | 触 |
| `os-communication` | 正式通讯与 Human 中转交接 | L3_EXECUTION_GATED | 必 | 触 | 触 | 触 | 触 |
| `os-context-management` | 上下文管理、文件放置与工作集 | L1_BOOT_VISIBLE | 必 | 必 | 必 | 必 | 必 |
| `os-task-continuity` | 任务连续性与临时工作台 | — | 必 | 必 | 必 | 必 | 必 |
| `os-task-orchestration` | 任务编排：大任务、G/R/A/D、原型与模式 | L1_BOOT_VISIBLE | 必 | 必 | 必 | 必 | 必 |
| `os-mwu-output` | 最小工作单元输出 | L1_BOOT_VISIBLE | 必 | 必 | 必 | 必 | 触 |
| `os-model-routing` | 模型路由与接收者设置 | L3_EXECUTION_GATED | 必 | — | 触 | — | — |
| `os-stage-deliberation` | 阶段协同推演与增量再确认 | L1_BOOT_VISIBLE | 必 | 触 | 触 | 触 | — |
| `os-workflow` | 七阶段 Workflow | — | 必 | 必 | 必 | 必 | — |
| `os-task-discipline` | 任务纪律：任务包、验证、run 与完成指针 | — | 必 | 必 | 必 | 必 | — |
| `os-publication` | 发布、Git 与受保护动作 | — | 触 | 必 | 触 | 必 | — |
| `os-tools` | Windows 环境与可选外部工具 | — | — | 触 | 触 | 触 | — |
| `os-domain-content` | 领域内容（08） | — | 触 | 触 | 触 | 必 | 必 |

图例：必 = 角色初始化时加载；触 = 命中触发条件时加载；— = 不加载。只有独立验收过的 L4 才可称 operationally_active；当前没有任何机制达到 L4。

## 角色初始化

Human 说明你的角色后，调用对应的角色 skill，它会加载其余全部必载 skill：

- 任务规划（`decision_architecture`）→ `role-planner`
- 任务开发（`execution`）→ `role-developer`
- 审核（`independent_review`）→ `role-reviewer`
- 特色内容开发（`execution`）→ `role-content-developer`
- 特色内容教学或使用（`execution`）→ `role-content-user`

没有说明角色时，先问 Human 角色是什么，再初始化。

## 登记文件（系统结构的权威描述）

- `01_os/05_registry/communication_system_v1.yml`
- `01_os/05_registry/context_management_v1.yml`
- `01_os/05_registry/mechanism_activation_v1.yml`
- `01_os/05_registry/minimum_work_unit_output_v1.yml`
- `01_os/05_registry/model_routing_v1.yml`
- `01_os/05_registry/os_surface_v1.yml`
- `01_os/05_registry/prms_v1.yml`
- `01_os/05_registry/repository_guards_v1.yml`
- `01_os/05_registry/repository_publisher_authority_v1.yml`
- `01_os/05_registry/skills_and_tools_v1.yml`
- `01_os/05_registry/skills_v1.yml`
- `01_os/05_registry/stage_collaborative_deliberation_v1.yml`
- `01_os/05_registry/task_discipline_v1.yml`
- `01_os/05_registry/task_orchestration_v1.yml`
- `01_os/05_registry/workflow_minimum_operational_loop_v1.yml`
- `01_os/05_registry/workflow_publication_gate_v1.yml`
