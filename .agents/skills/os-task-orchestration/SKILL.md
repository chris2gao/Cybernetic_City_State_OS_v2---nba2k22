---
name: os-task-orchestration
description: "City-State OS 的任务粒度与执行纪律：默认一个长周期大任务、什么时候不该停/必须停、G/R/A/D 原子任务、 Human 审定的任务原型、默认 EXECUTION 与受委托的 DEVELOPMENT、Agent 自报。每个角色初始化时加载。"
---

# 任务编排：大任务、G/R/A/D、原型与模式（L1_BOOT_VISIBLE）

> 生成文件，勿手改。来源：`01_os/05_registry/skills_v1.yml` + `01_os/02_boot/task_orchestration/启动清单_v1.yml`。修改来源后运行 `python -B 01_os/06_execution/skills/generate_skills.py`。

## 何时加载

每个角色初始化；拆任务、判断是否该停、执行已审原型、遇到能力缺口时。

适用角色：初始化必载 = 任务规划、任务开发、审核、特色内容开发、特色内容教学或使用；按触发加载 = 无

## 启动必读（角色初始化时读完，约 10 KB）

- `01_os/03_mechanisms/task_orchestration/README.md`

## 按动作读取（做到这一步时再读）

- 拆分任务、判断该继续还是必须停时：`01_os/03_mechanisms/task_orchestration/大任务与长时执行契约_v1.yml`
- 定义或检查 G/R/A/D 节点与父任务 Done 时：`01_os/03_mechanisms/task_orchestration/原子任务与结果驱动执行模型_v1.md`、`01_os/03_mechanisms/task_orchestration/原子任务场景验证_v1.md`
- 设计或执行可复用任务原型、遇到能力缺口、判断 EXECUTION / DEVELOPMENT 时：`01_os/03_mechanisms/task_orchestration/最小任务原型与执行编译契约_v1.md`
- 对候选做受控验证时：`01_os/03_mechanisms/task_orchestration/受控验证执行契约_v1.yml`

## 程序读取（validator / runner 读取；只在修改这些文件或排查校验失败时读）

- `01_os/02_boot/task_orchestration/启动清单_v1.yml`
- `01_os/03_mechanisms/task_orchestration/loop_iteration_schema_v1.json`
- `01_os/05_registry/task_orchestration_v1.yml`

## 入口程序（调用即可，不必通读源码）

- `01_os/06_execution/task_orchestration/big_task/closure_preflight.py`

## 命令

- `python -B 01_os/06_execution/task_orchestration/big_task/closure_preflight.py --packet <task-packet>` → 只报告，不授权
- `python -B -m pytest 01_os/06_execution/task_orchestration -q` → 全部通过

## 边界与停止

- 普通任务分支发布不是停止条件；大不等于危险
- STOP ACTION ≠ STOP GOAL：能力缺口返回 INCOMPLETE 与一个最小 Human 决定，不自行转开发
- 自报（AGENT_SELF_REPORT）与 Host 实际拒绝（HOST_OBSERVED）分开记录
