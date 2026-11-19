---
name: os-task-discipline
description: "City-State OS 的任务施工纪律：任务包字段、开工 preflight、受控验证、变更路径账本、run 记录与 lifecycle 枚举、completion pointer、独立审核排期。建任务、施工、收尾或审核候选时使用。"
---

# 任务纪律：任务包、验证、run 与完成指针

> 生成文件，勿手改。来源：`01_os/05_registry/skills_v1.yml` + `01_os/02_boot/task_discipline/启动清单_v1.yml`（读取分层 `read_tiers`）。修改来源后运行 `python -B 01_os/06_execution/skills/generate_skills.py`。

## 何时加载

规划、开发、审核角色初始化；material repository mutation 之前；收尾与交接时。

适用角色：初始化必载 = 任务规划、任务开发、审核、特色内容开发；按触发加载 = 无

## 启动必读（角色初始化时读完，约 5 KB）

- `01_os/06_execution/task_discipline/README.md`

## 按动作读取（做到这一步时再读）

- 建或读任务包时：`01_os/06_execution/task_discipline/packet_input/README.md`
- 对候选做受控验证时：`01_os/06_execution/task_discipline/managed_verification/README.md`、`01_os/03_mechanisms/task_orchestration/受控验证执行契约_v1.yml`
- 同步项目资料索引时：`01_os/06_execution/task_discipline/project_context/README.md`
- 写或读任务包、选择执行者、向 Human 请求批准或确认时：开发入口细则 §7（含 7.1 模型路由 preflight、7.2 Human 确认与大任务预确认）：`01_os/02_boot/os_entry/开发入口_按动作细则_v1.md`
- 固定执行环境、设计或执行测试、写证据、做候选受控验证时：开发入口细则 §1.2 执行环境约定与 §8 测试与证据标准（含 8.1）：`01_os/02_boot/os_entry/开发入口_按动作细则_v1.md`
- 派审核、做独立审核或安排审核时机时：开发入口细则 §9 独立审核与 Human 决策 / 确认（含 9.1–9.3）：`01_os/02_boot/os_entry/开发入口_按动作细则_v1.md`
- 写 completion pointer 或收尾交接时：开发入口细则 §10 completion pointer 最小模板：`01_os/02_boot/os_entry/开发入口_按动作细则_v1.md`

## 程序读取（validator / runner 读取；只在修改这些文件或排查校验失败时读）

- `01_os/02_boot/task_discipline/启动清单_v1.yml`
- `01_os/05_registry/task_discipline_v1.yml`

## 命令

- `python -B 01_os/06_execution/task_discipline/preflight/preflight_task_context.py --packet <task-packet>` → preflight ok；只报告，不授权
- `python -B 01_os/06_execution/task_discipline/managed_verification/managed_verify.py --candidate <40-char> --plan <plan.json> --attempt <outside-repo-new-dir> {run,inspect}` → 退出 0 才可声明该候选验证通过
- `python -B 01_os/06_execution/task_discipline/path_ledger/changed_path_ledger.py --base <40-char>` → 实测变更路径集合

## 边界与停止

- run.yml 的 lifecycle 只能取开发入口 §5 的七个枚举值
- 缺最终记录是证据不完整，不是成功；超时不自动重试
