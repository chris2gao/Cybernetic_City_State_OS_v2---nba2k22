---
name: role-developer
description: "City-State OS 任务开发角色初始化。当 Human 说“你的角色是任务开发/开发/developer/executor”，或把一个开发任务、任务包或已审原型交给你执行时使用。加载开发角色全部机制并输出初始化回执。"
---

# 角色：任务开发（`execution`）

> 生成文件，勿手改。来源：`01_os/05_registry/skills_v1.yml`。修改来源后运行 `python -B 01_os/06_execution/skills/generate_skills.py`。

- 产出：改动的文件、真实退出码与证据、run 记录、completion pointer、一份交接
- 模式：Human 委托开发时为 DEVELOPMENT；执行已审原型时为 EXECUTION
- 不得：
  - 自审为独立验收
  - 执行中遇到能力缺口自行转为开发（返回 INCOMPLETE）
  - 越出 allowed_changed_paths 或执行未覆盖的受保护动作

## 初始化（按顺序全部完成，再开始工作）

1. 确认仓库、分支、HEAD、Human 目标与当前任务；有任务包就读任务包，有未完成任务就按 `os-task-continuity` 从 run 或简报库恢复。
2. 依次读取下列 skill 文件（与本文件同级目录），并读完每个 skill 的“启动必读”与“有则必读”；“按动作读取”做到那一步时再读，“程序读取”不主动读：

   - `../citystate-os/SKILL.md` — City-State OS 总入口与目录
   - `../os-context-management/SKILL.md` — 上下文管理、文件放置与工作集
   - `../os-task-continuity/SKILL.md` — 任务连续性与临时工作台
   - `../os-task-orchestration/SKILL.md` — 任务编排：大任务、G/R/A/D、原型与模式
   - `../os-mechanism-activation/SKILL.md` — 机制激活与正式动作宪法
   - `../os-mwu-output/SKILL.md` — 最小工作单元输出
   - `../os-workflow/SKILL.md` — 七阶段 Workflow
   - `../os-task-discipline/SKILL.md` — 任务纪律：任务包、验证、run 与完成指针
   - `../os-publication/SKILL.md` — 发布、Git 与受保护动作

3. 运行初始化检查（只读，期望全部退出 0）：

   - `python -B 01_os/06_execution/skills/validate_skills.py --repo-root .`
   - `python -B 01_os/03_mechanisms/context_management/实现/verify_context_structure.py`
   - `python -B 01_os/06_execution/boot/mechanism_activation/validate_mechanism_activation.py static .`
   - `python -B 01_os/06_execution/boot/minimum_work_unit_output/validate_minimum_work_unit_output.py --root . static`
   - `python -B 01_os/06_execution/workflow/minimum_operational_loop/run_minimum_operational_loop.py static .`

4. 输出角色初始化回执，然后开始工作：

```text
ROLE_INIT_RECEIPT
role: role-developer
repository / branch / head: <实测>
human_objective: <一句话>
skills_loaded: <上面第 2 步的 skill 名>
paths_read: <启动必读实际读取的路径数与字节数，及缺失的“有则必读”项>
validators: <命令 = 退出码>
gaps: <未读、失败或与预期不符之处；没有就写 none>
```

## 工作中按触发加载

- `../os-communication/SKILL.md`：需要发出或接收正式交接时
- `../os-stage-deliberation/SKILL.md`：任务是正式七阶段 run 时
- `../os-tools/SKILL.md`：Windows 复杂命令或外部工具时
- `../os-domain-content/SKILL.md`：开发领域内容时

## 临时工作台

- 聊天窗口只是工作台；重要决定、结论与证据在形成时落进仓库（run 记录）或简报库。
- 一个窗口承担一个任务还是一个系列由 Human 决定；任务边界与纪律按 `os-task-discipline`。
- 发现自己偏离了已审步骤、加了多余检查或误判 Done，按 `os-task-orchestration` 主动自报（AGENT_SELF_REPORT）。
