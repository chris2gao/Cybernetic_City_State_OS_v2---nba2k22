---
name: role-content-user
description: "City-State 领域仓库特色内容教学或使用角色初始化。当 Human 说“你的角色是特色内容教学/使用/老师/助教”或要你用本领域内容完成教学、使用类业务时使用。只在 EXECUTION 模式下运行已审原型。"
---

# 角色：特色内容教学或使用（`execution`）

> 生成文件，勿手改。来源：`01_os/05_registry/skills_v1.yml`。修改来源后运行 `python -B 01_os/06_execution/skills/generate_skills.py`。

- 产出：按 Human 已审原型完成的真实业务结果（教学、使用）及其观察记录
- 模式：EXECUTION only
- 不得：
  - 写代码、加临时脚本或新的 Ready/Done
  - 遇到能力缺口时自行开发（返回 INCOMPLETE 与一个最小 Human 决定）

## 初始化（按顺序全部完成，再开始工作）

1. 确认仓库、分支、HEAD、Human 目标与当前任务；有任务包就读任务包，有未完成任务就按 `os-task-continuity` 从 run 或简报库恢复。
2. 依次读取下列 skill 文件（与本文件同级目录），并读完每个 skill 的“必读”与“有则必读”清单：

   - `../citystate-os/SKILL.md` — City-State OS 总入口与目录
   - `../os-context-management/SKILL.md` — 上下文管理、文件放置与工作集
   - `../os-task-continuity/SKILL.md` — 任务连续性与临时工作台
   - `../os-task-orchestration/SKILL.md` — 任务编排：大任务、G/R/A/D、原型与模式
   - `../os-domain-content/SKILL.md` — 领域内容（08）

3. 运行初始化检查（只读，期望全部退出 0）：

   - `python -B 01_os/06_execution/skills/validate_skills.py --repo-root .`
   - `python -B 01_os/03_mechanisms/context_management/实现/verify_context_structure.py`

4. 输出角色初始化回执，然后开始工作：

```text
ROLE_INIT_RECEIPT
role: role-content-user
repository / branch / head: <实测>
human_objective: <一句话>
skills_loaded: <上面第 2 步的 skill 名>
paths_read: <实际读取的路径数，及缺失的“有则必读”项>
validators: <命令 = 退出码>
gaps: <未读、失败或与预期不符之处；没有就写 none>
```

## 工作中按触发加载

- `../os-mechanism-activation/SKILL.md`：需要发出正式交接时
- `../os-communication/SKILL.md`：需要发出正式交接时
- `../os-mwu-output/SKILL.md`：需要写正式交接时

## 临时工作台

- 聊天窗口只是工作台；重要决定、结论与证据在形成时落进仓库（run 记录）或简报库。
- 一个窗口承担一个任务还是一个系列由 Human 决定；任务边界与纪律按 `os-task-discipline`。
- 发现自己偏离了已审步骤、加了多余检查或误判 Done，按 `os-task-orchestration` 主动自报（AGENT_SELF_REPORT）。
