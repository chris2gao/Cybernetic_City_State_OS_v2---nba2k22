---
name: os-task-discipline
description: "City-State OS 的任务施工纪律：任务包字段、开工 preflight、受控验证、变更路径账本、run 记录与 lifecycle 枚举、completion pointer、独立审核排期。建任务、施工、收尾或审核候选时使用。"
---

# 任务纪律：任务包、验证、run 与完成指针

> 生成文件，勿手改。来源：`01_os/05_registry/skills_v1.yml`。修改来源后运行 `python -B 01_os/06_execution/skills/generate_skills.py`。

## 何时加载

规划、开发、审核角色初始化；material repository mutation 之前；收尾与交接时。

适用角色：初始化必载 = 任务规划、任务开发、审核、特色内容开发；按触发加载 = 无

## 必读（按顺序全部读完）

- `01_os/06_execution/task_discipline/README.md`
- `01_os/06_execution/task_discipline/packet_input/README.md`
- `01_os/06_execution/task_discipline/managed_verification/README.md`
- `01_os/06_execution/task_discipline/project_context/README.md`
- `01_os/05_registry/task_discipline_v1.yml`
- `01_os/03_mechanisms/task_orchestration/受控验证执行契约_v1.yml`

## 命令

- `python -B 01_os/06_execution/task_discipline/preflight/preflight_task_context.py --packet <task-packet>` → preflight ok；只报告，不授权
- `python -B 01_os/06_execution/task_discipline/managed_verification/managed_verify.py --candidate <40-char> {run,inspect}` → 退出 0 才可声明该候选验证通过
- `python -B 01_os/06_execution/task_discipline/path_ledger/changed_path_ledger.py --base <40-char>` → 实测变更路径集合

## 边界与停止

- run.yml 的 lifecycle 只能取开发入口 §5 的七个枚举值
- 缺最终记录是证据不完整，不是成功；超时不自动重试
