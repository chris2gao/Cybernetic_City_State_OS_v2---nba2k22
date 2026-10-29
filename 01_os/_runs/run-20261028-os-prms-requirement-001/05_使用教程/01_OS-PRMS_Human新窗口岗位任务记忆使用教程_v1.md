# OS-PRMS 人类使用教程 v1：从工作窗口恢复岗位与任务上下文

> 身份：Human 操作说明；适用首次开窗、换窗口、换任务、旧任务恢复。依据 Core/master OS-PRMS PR #10 合并版本 `e075cdf288a765b7bfd2f4891c8f384404da16e1`，以及 `01_os/03_mechanisms/context_management/prms/TASK_CONTINUITY.md`。本指南不宣称 PRMS 已作为聊天平台的自动记忆服务部署。  
> 使用范围：当前优先 Core + NBA2K22。其它领域无需更新。

## 0. 先分清三个名字

1. **模型 / 执行平台**：Human 在 ChatGPT、Codex、Gemini 等当前可用产品中选择实际模型或工具。OS `model_routing` 给出任务适配建议，但写入“GPT”或“Codex”字样不会改变用户界面中实际选定的模型。
2. **岗位 / Role**：`decision_architecture`、`implementation_owner`、`independent_review`，以及工程中登记的稳定岗位实例 ID。模型窗口可以更换，岗位可以继续存在；岗位标签不是自动权限。
3. **任务 / Task ID**：定位要恢复的某条持久工作线。恢复时只加载该任务当前方案和关联事实，不从同岗位的其它任务自动混入正文。

## 1. 什么会自动，什么不会

**在正确启动 OS/PRMS 读取程序后按规则自动：**
- 读取基础 B0（Git HEAD 与实际仓库的 AGENTS / 根 OS 入口）；按触发机制加载必要 Core 规范。
- 检索完整适用 G1 的目录/概要而不是全部正文。
- 对当前 `domain_id` 发现正式 G2（领域尚未建 09 目录时报告 UNINITIALIZED）；研究资料和 P00–P12 模块只能作为候选/按需来源。
- 根据保存的 `load_spec` 选择当前 T1 任务记录、方案、已批准决定来源、进度、后续动作、必要原始事实及原来由 Human 选中的正文。
- 按选择深度恢复相关 T2 旧任务与 K1/K2 经验；预算不足、版本漂移、缺失和检查点滞后必须报告。

**当前不会自动：**
- 打开普通 ChatGPT 新聊天时直接运行 Python/GitHub 恢复、创建/修改角色状态仓或载入所有私人任务记录。
- 自动捕获尚未显式保存的聊天、隐藏思维或临时窗口草稿。
- 自动打开另一个 GPT/Codex 窗口、把 `CONTEXT.md` 注入平台、或从 Role 字段切换底层模型。
- 未经有效任务来源，将过往所有内容认定为正式的 Human 决议。

## 2. 最省事用法：从线上任务档案恢复（现在即可使用）

适用于当前 PRMS 状态仓库尚未配置，但已有 NBA2K22 官方 GitHub Run 记录的时候。

1. Human 在产品 UI 选择本次实际模型/执行平台，开新窗口。
2. 将下面的“恢复现有 NBA 任务提示词”给该模型。修改任务、岗位、领域和必读 Run 入口。
3. 模型若可直接读取 GitHub，通过其只读连接器读资料；若没有该连接器，则 Human 转交任务索引和必要正文。绝不能把未读文件标为已读。
4. 要求输出 **恢复回执**：Core/NBA 真实 SHA、岗位、task_id、已读文件、只发现目录的 G1/G2、已载入正文、关键 Human 决定、当前未完成项、缺口、接下来一个动作。
5. 你核对回执，然后继续任务。

**可复制的新窗口提示词：**

> 请初始化 Cybernetic City-State OS，并将本窗口设为 NBA2K22 项目指定岗位的临时工作台。  
> 实际模型由本产品/当前平台提供；不要通过文本假装切换模型。  
> 领域：`nba2k22`；岗位：`decision_architecture`（可改为 `implementation_owner` 或 `independent_review`）；任务：`<填写已有task_id或Run>`；目的：继续既有任务而非从头重新建模。  
> 先读取当前 Core 和 NBA2K22 仓库 `master` 的真实 SHA 及 `AGENTS.md`、`AGENT_WORKING_DISCIPLINE.md`、`01_os/README.md`、`01_os/开发入口与单窗口任务规范_v1.md`。  
> 进入 NBA2K22 任务档案入口：`01_os/_runs/run-20261028-os-prms-requirement-001/00_OS-PRMS_规划档案总索引与下一步.md`（规划分支 `planning/os-prms-a0-confirmed-01b-20261028`），先判断它是否是我指定的目标任务；如不匹配，则查找目标任务自身的 Run 和上下文记录，不可用 PRMS 规划代替业务任务。  
> 发现 G1 与当前领域 G2 目录/概要，只展开与本任务实际相关的机制正文；按岗位、任务和 Human 已保存选择加载 T1/T2 和所需经验。若已有 PRMS 持久状态库，使用真正的 `task_cli.py resume` 恢复并读取 `CONTEXT.md`；若没有，使用已归档的 Run 正文恢复，不得声称已运行 PRMS。  
> 先交付“上下文恢复回执”，注明实际来源、关键决定、工作计划、完成/未完成、待验证事项、未加载项，以及建议的唯一下一步。此时先不进行发布或其它受保护操作。

## 3. 已配置 PRMS 状态库后的真正 Save / List / Resume

前置：已有独立于 Core/领域代码仓的 **实际可访问的持久状态位置**；已经 `REGISTER` 岗位并记录任务；Core 本地 Git checkout 包含保存记录所绑定的精确 `core_commit`。若未配置则不要声称可以跨窗口自动存储。当前随 Core 提供的 `task_cli.py save` **只允许隔离测试存储**（要求 `--isolated-test-only`），真实远端持久状态由宿主接入实现，不是这个 CLI 的默认能力。

**切换前保存 A：** Human 明确说“请先保存 A 的完整任务状态与 Human 决议，再切换 B”，由执行环境构造含 `task_id`、`task_plan`（`objective`、`plan`、`progress`、`open_items`、`next_steps`、`human_decision_refs`）和 `load_spec`（准确 Core SHA、岗位类型、`memory_choice_ref`、选中路径、历史深度等）的 JSON；调用 `SAVE_TASK_CONTEXT` 并回读持久检查点。没有成功的保存回执不能假装 A 已持久化。

**列出任务（已有 state-root）：**
```powershell
python -B 01_os/06_execution/boot/context_management/prms/task_cli.py list --state-root "<已有的独立状态仓>" --role "<role-instance-id>" --output "<新生成的目录或文件名>-tasks.json"
```

**在新会话恢复 A：**
```powershell
python -B 01_os/06_execution/boot/context_management/prms/task_cli.py resume --state-root "<已有的独立状态仓>" --role "<role-instance-id>" --task "<task-id-A>" --session "<新的唯一session-id>" --core-root "<本地Core Git仓目录>" --output "<全新且不存在的workbench目录>"
```

成功的 `--output` 目录含 `CONTEXT.md`、`recovery.json`、`bundle.json`、`plan.json`、`choice.json` 等。Human 打开 `CONTEXT.md` 并转给新窗口；必要时按 `handoff_cli.py` 做 receiver 文件回执校验。原任务不因只读 resume 被改写。

**注意：** 此命令不会创建新聊天，也不会把文件自动注入 ChatGPT。新的输出路径不能已存在。保存任务使用 `task_cli.py save --isolated-test-only` 仅适用于明确建立的隔离测试库；真实持久写入需要适配已选部署环境。

## 4. Human 推荐用语

**保存当前任务：**
“请按当前已批准任务方案显式保存本任务的目标、工作步骤、最新进度、Human 决议原文及来源、未完成项、下一步和正文加载选择。真正执行 PRMS SAVE_TASK_CONTEXT 并回读当前检查点；如果没有持久库，先形成 GitHub Run 文档和恢复索引，明确声明尚未写入 PRMS 状态库。保存完成后再切换任务。”

**恢复某任务：**
“本窗口接续 `<task-id>`，职责 `<role>`。从该任务真实持久状态生成并读取 `CONTEXT.md`；若 PRMS 未配置，则读取该任务正式 GitHub Run 和已批准决定。按任务的加载方案恢复 G1/G2、必需 T1 与选择的历史。先给恢复回执，不能混入其它任务，不能把未读资料称为已加载。”

**切换岗位但保留任务：**
“更换本窗口的实际执行模型/岗位，不改变任务 ID 与已批准决议；从同一任务持久材料恢复。涉及职责变化要重新确认任务可执行范围，模型身份标签不能代替 Human 授权。”

## 5. 自检五问

1. 此窗口真实运行什么模型、担任哪个岗位、恢复哪个 task_id？三者是否区分？
2. 是否真正拿到了 A 的已保存任务方案和最新完成/待办，而不仅是旧聊天摘要？
3. G1/G2 目录和正文是否明确区分？正式 G2 与 `08_Domain_Applications` 候选是否区分？
4. 当前任务的 Human 原始决议能追溯到具体来源吗？其它任务的事实有无混入？
5. 回执清楚报告 Core/NBA SHA、载入、缺失、预算和下一步了吗？若无状态库，是否坦白用了 Run 文件作为降级恢复？

## 6. 当前项目提示

Core PR #10 已合并 `e075cdf288a765b7bfd2f4891c8f384404da16e1`。NBA2K22 的 Core 继承同步由 Codex 执行 Issue #11，完成前不应该声称 NBA/master 已带最新 PRMS。尽管如此，只要可访问原 NBA 规划分支，已有的规划档案索引依旧可用于新窗口只读恢复。

相关权威文档：Core `01_os/03_mechanisms/context_management/prms/TASK_CONTINUITY.md`、`OPERATIONS.md`、`01_os/03_mechanisms/model_routing/README.md`、根 `AGENTS.md` 和 OS 新窗口规范。
