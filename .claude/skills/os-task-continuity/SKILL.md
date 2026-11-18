---
name: os-task-continuity
description: "City-State OS 中窗口是临时工作台、任务与岗位才是持续的。保存或恢复任务上下文、轮换窗口、交班、从 run 或简报库恢复任务时使用（含 PRMS save/list/resume 与 handoff）。"
---

# 任务连续性与临时工作台

> 生成文件，勿手改。来源：`01_os/05_registry/skills_v1.yml`。修改来源后运行 `python -B 01_os/06_execution/skills/generate_skills.py`。

## 何时加载

每个角色初始化；重大决定或交接时落检查点；窗口轮换或恢复任务。

适用角色：初始化必载 = 任务规划、任务开发、审核、特色内容开发、特色内容教学或使用；按触发加载 = 无

## 必读（按顺序全部读完）

- `01_os/03_mechanisms/context_management/prms/README.md`
- `01_os/03_mechanisms/context_management/prms/TASK_CONTINUITY.md`
- `01_os/03_mechanisms/context_management/prms/OPERATIONS.md`
- `01_os/03_mechanisms/context_management/prms/loading_rules_v1.yml`
- `01_os/03_mechanisms/context_management/prms/record_schemas_v1.json`

## 命令

- `python -B 01_os/06_execution/boot/context_management/prms/cli.py --repo-root . --commit <40-char> --repository <owner/repo> catalog --output <outside-repo.json>` → SCANNED_SCOPE_COMPLETE；只发现，不加载正文、不授权
- `python -B 01_os/06_execution/boot/context_management/prms/task_cli.py --state-root <isolated-state> --role <role> {save,list,resume}` → 只在已获批准的隔离状态仓上运行；未部署时用 run / 简报库恢复并写明 recovery_source

## 边界与停止

- live PRMS save/list/resume 为 PRMS_LIVE_NOT_TESTED；恢复回执不授予执行权
- Fork 只是快照；receiver ack 不证明模型理解或交班成功
