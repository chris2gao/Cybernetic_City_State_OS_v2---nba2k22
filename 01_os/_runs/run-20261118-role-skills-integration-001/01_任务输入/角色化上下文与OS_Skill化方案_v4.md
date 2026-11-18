# 角色化上下文加载与 Core OS Skill 化方案（待 Human 审定）

- 依据：core master `e0bdd7fa2ab233bafa4c65644cadce475f66a1c7`；任务开始前的 Claude Code worktree（分支 `claude-win/exciting-lewin-7bc50e`），工作区干净，**本方案阶段仓库零改动**。
- 输入：Human 2026-11-18 对角色分工、窗口定位、新旧整合与 Skill 化的说明（本窗口对话），以及 `20261118_公共上下文基线.md`、`20261118_机制缺口详细说明与Skill化评估.md`。
- 性质：这是一份“方案对比 + 施工设计”，按开发入口 §7.2 呈现给 Human 审定。审定后作为同一个大任务的输入施工。

**修订记录**
- v1（2026-11-18）：初稿。
- v4（2026-11-18）：Human 随后说明“领域仓库与 core 仓库除了 08 文件夹不一样之外全部一样”，这取代 v3 的 Q1 = A，实际是“只有 08 归领域”。§2.4 改写，新增 I16（把其余领域路径收进 08），I14 改为 skill 目录整体归 Core，领域角色 skill 改为 Core 提供的通用 skill，从 08 读领域内容。新增待确认 Q2：08 内部布局。
- v3（2026-11-18）：Human 确认 Q1 = A，现有领域拥有路径全部保留（已被 v4 取代）。
- v2（2026-11-18）：按 Human 对第 7 节 D1–D6 的答复修改——D1 写明领域仓合并方式并新增 §2.4；D2 不设辅助角色；D3 核对最新 workflow 改动后修改 I7（不删 `PASS_WITH_NON_BLOCKING_NOTES`，改为由审核结论推导）；D4 暂不加 hooks；D5 叠加层并入合同；D6 集中审核后 Human 确认集成。第 7 节改为“已定事项 + 仍待确认”。

---

## 0. 目标（按 G/R/A/D 写）

- **Goal**：Human 只需告诉模型“你的角色是 X（在仓库 Y）”，模型就自己加载该角色需要的全部 OS 机制与上下文，并把聊天窗口当作临时工作台开始工作，不再需要手写提示词。
- **Done（可观察的业务结果）**：在一个全新窗口里，只说“你的角色是审核”，模型能①列出它加载了哪些 skill、哪些机制正文，与本方案第 3 节的矩阵一致；②按审核机制完成一次真实审核（读 primary evidence、给出 MWU 格式结论）。规划、开发角色各做一次同样的验证。**生成了 skill 文件、validator 全绿都不算完成。**
- **Ready**：本方案获 Human 审定；第 7 节的遗留裁决有答复。

---

## 1. Core OS 完整目录

### 1.1 全量盘点（实测）

仓库中除运行流量（`01_os/_runs/`、`01_os/_communication/`）外共 **414 个跟踪文件**；registry 的 83 个路径模式覆盖其中 271 个，**143 个没有被任何 registry 条目覆盖**，主要集中在七阶段 workflow 各阶段（41 个）、stage_collaborative_deliberation（46 个，多为 fixture）、`_dev/`（19 个）、根目录（10 个）。完整逐文件清单（路径、类别、字节数、登记它的 registry、用途）可由只读脚本重新生成；施工时会落进仓库作为目录的数据源。

按“功能区”划分：

| 区 | 内容 | 运行时要读的规范类材料 |
|---|---|---|
| 根目录 | `CLAUDE.md` `AGENTS.md` `GEMINI.md` `AGENT_WORKING_DISCIPLINE.md` `README.md` `CORE_MANIFEST.yml` `.claude/settings.json` `.githooks/` `new-domain.ps1` | B0 入口约 114 KB（纪律、AGENTS、`01_os/README.md`、开发入口） |
| `01_workflow/` | 七阶段规格、各阶段 schema、阶段方法论 | 约 140 KB |
| `02_boot/` | 7 个机制的启动清单 + 协作伙伴入口 | 约 12 KB |
| `03_mechanisms/` | 7 个全局机制正文与契约 | 约 365 KB（含依据材料） |
| `04_skills_and_tools/` | windows、check-jsonschema、mutmut、cosmic-ray、rea 及选型说明 | 约 73 KB |
| `05_registry/` | 15 个登记文件（含发布权限、守卫） | 约 85 KB |
| `06_execution/` | 38 个命令入口、库、测试、fixture | 只需接口（`--help` 已实测） |
| `_dev/` | 活动设计与被取代版本 | 约 128 KB，大部分是历史 |

### 1.2 机制单元目录（也就是将来的 skill 清单）

把上面这些整理成 13 个“机制单元”。每个单元对应一个 skill，单元之间不重叠：

| # | Skill 名（草案） | 覆盖什么 | 主要来源 | 成熟度 |
|---|---|---|---|---|
| U0 | `citystate-os` | OS 总入口：B0 纪律、全部机制目录、角色列表、角色初始化方法 | 根目录四件 + `01_os/README.md` + 开发入口 | — |
| U1 | `os-mechanism-activation` | 正式跨端点动作的宪法路径、触发注册表、物理事实双向绑定 | `03_mechanisms/mechanism_activation/` | L3 待验收 |
| U2 | `os-communication` | Human 中转的正式交接：消息、端点卡、v2 指针、接收方 bootstrap、归档 | `03_mechanisms/communication_system/` | L3 待验收 |
| U3 | `os-context-management` | 三个信息平面、文件放置与生命周期、工作集与归档、项目资料发现与索引同步、workspace 边界 | `03_mechanisms/context_management/`（除 prms） | L1 |
| U4 | `os-task-continuity` | 窗口是临时工作台：检查点、PRMS save/list/resume、窗口轮换、交接 | `context_management/prms/` + TASK_CONTINUITY | 候选，未部署 |
| U5 | `os-task-orchestration` | 大任务与长时执行、G/R/A/D 原子任务、任务原型、EXECUTION/DEVELOPMENT、自报与拒绝记录 | `03_mechanisms/task_orchestration/` | 未盘点、无 boot |
| U6 | `os-mwu-output` | 派单、交付、审核三个边界的最小输出 | `03_mechanisms/minimum_work_unit_output/` | active_global |
| U7 | `os-model-routing` | 选执行者/审核者、receiver_setup、模型目录 | `03_mechanisms/model_routing/` | L3 待验收 |
| U8 | `os-stage-deliberation` | 阶段协同建模：统一当前模型、可行性依据、阶段 gate、状态维度、receipt | `03_mechanisms/stage_collaborative_deliberation/` | L1，active_dormant |
| U9 | `os-workflow` | 七阶段链、阶段产物与 stage_control、冻结测试、三出口、runner、发布门 | `01_workflow/` + `06_execution/workflow/` | minimum_operational |
| U10 | `os-task-discipline` | 任务包、preflight、受控验证、路径账本、run 与 lifecycle、completion pointer、审核排期 | 开发入口 §2–§11 + `06_execution/task_discipline/` | candidate |
| U11 | `os-publication` | 发布传输矩阵、发布权限与需确认动作、push 守卫、Git 流程 | 开发入口 §1.1/§6 + `repository_publisher_authority_v1.yml` + `repository_guards_v1.yml` + `.githooks/` | — |
| U12 | `os-tools` | Windows 环境纪律与可选外部工具 | `04_skills_and_tools/` + `06_execution/tools/` | 登记≠加载 |

领域仓库在此之上加自己的单元（见第 2.3 节）。

---

## 2. 角色

### 2.1 Human 定义的五个角色与现有 OS 角色的对应

| Human 角色 | 所在仓 | 对应现有 `collaboration_role` | 默认模式 | 产出 | 不得做 |
|---|---|---|---|---|---|
| **任务规划** | core / 领域 | `decision_architecture` | —（设计与派单） | 与 Human 共建的当前模型、任务包、原型设计、路由与派单、裁决记录 | 默认不做后端实现；不得兼任自己派出的 T2/T3 任务的最终审核 |
| **任务开发** | core / 领域 | `execution` | DEVELOPMENT（Human 委托开发时）或 EXECUTION（执行已审原型） | 改动的文件、退出码与证据、completion pointer、一份交接 | 不得自审为独立验收；执行中缺能力不得自行转开发 |
| **审核** | core / 领域 | `independent_review` | — | MWU 格式的审核结论、primary evidence 清单、findings | 不得改执行分支；不得读执行者私有上下文；审核通过不等于集成授权 |
| **特色内容开发** | 领域 | `execution` + 领域内容 | DEVELOPMENT | 领域内容、领域机制、领域证据 | 不得改 core-owned 路径（`CORE_MANIFEST.yml`），需要 core 改动要向上游提 |
| **特色内容教学或使用** | 领域 | `execution`（业务运行） | **EXECUTION only** | 按已审原型完成的真实业务结果（教学、使用） | 不写代码、不加临时脚本或新 Ready/Done；缺能力返回 `INCOMPLETE` |

现有的第四个协作角色 `auxiliary_mechanical`（确定性的重复/批量工作）**不设为角色**（Human 裁决 D2：分工不必过细）。它归入“任务开发”，不做单独的角色 skill；model_routing 合同里的这个路由标签不改，只是不再对 Human 呈现为一个岗位。

### 2.2 窗口定位

- 窗口是**临时工作台**，角色和任务才是持续的。任务的连续性由任务包、run 记录、简报库和 PRMS 承担，不由聊天承担。
- 一个窗口做一个任务还是一个系列，**由 Human 决定**。现行开发入口 §1–§2 写“一个窗口一个任务”，按 Human 本次说明改写（见第 5 节 I6）。
- 每个角色都要遵守：重要决定、结论、证据在形成时落进仓库或简报库；窗口可以随时关闭、随时从角色 + 任务恢复。

### 2.3 领域仓库

领域仓库在 Core 的 13 个单元之外增加：
- `domain-catalog`：领域内容目录（复用现有“项目资料发现与索引同步契约”和 PRMS 的 G2 领域目录：08 模块、09 目录）。
- 领域内容机制：登记在 08 的 `domain_mechanisms.yml` 里，由通用领域 skill 按目录加载，不在 skill 目录里另建。
- 两个领域角色 skill：`role-content-developer`、`role-content-user`，**由 Core 提供通用版本**，在所有仓库中完全一样，运行时从 08 读取该领域的内容（见 §2.4）。

具体领域内容在各领域仓库的 08 里施工。

### 2.4 领域仓合并方式（Human 裁决 D1）

Human 的说明：领域仓合并就是**把 Core 的 OS 内容合并进领域仓并覆盖，只保留特色内容；`08` 文件夹不动**。

对照仓库现状：
- `CORE_MANIFEST.yml` 的 `domain_merge_procedure.currently_frozen` 自 2026-08-02 起冻结领域合并，写明“须由 Human 明确指令解除并记录于此”。本任务把 Human 这次的说明记进去，作为解除依据，并写明合并方式：Core 拥有的路径一律以 Core 为准覆盖，领域拥有的路径不动。
- 合并本身在各领域仓里执行，是**本任务完成并集成到 core master 之后**的独立任务（每个领域一个），不在本窗口做。
- **领域拥有路径的范围（Human 2026-11-18 说明）**：领域仓库与 core 仓库**除了 `08_Domain_Applications/` 之外全部一样**。所以领域拥有路径收窄为 08 一个目录，其余全部以 Core 为准。
- 与仓库现状的差距：`CORE_MANIFEST.yml` 现在还登记了 `01_Research_Reports/`、`02_Protocols/`、`03_Daily_Execution/`、`09_Domain_Global_Mechanisms/`、`01_os/07_content/`（含领域运行记录根 `01_os/07_content/_runs/`）为领域拥有；PRMS 的领域目录功能读 09 的 `domain_mechanisms.yml`；上下文管理把 `01_os/07_content/_runs/` 当作领域运行记录的累计区。这些都要收进 08（I16），否则领域仓“除 08 外与 core 一样”做不到。
- 建议的 08 内部布局（待 Q2 确认）：

  ```text
  08_Domain_Applications/
  ├── domain.yml                 领域身份与模块目录入口（PRMS 已在读，位置不变）
  ├── domain_mechanisms.yml      领域机制目录（原 09_Domain_Global_Mechanisms/domain_mechanisms.yml）
  ├── <领域模块>/                 特色内容本体（原 01/02/03 的研究、协议、日常执行按领域需要归入）
  └── _runs/                     领域运行记录（原 01_os/07_content/_runs/）
  ```

- 领域角色 skill 因此**由 Core 提供通用版本**（`role-content-developer`、`role-content-user`），它们在运行时读 08 的 `domain.yml` 和 `domain_mechanisms.yml` 加载领域内容。skill 目录在所有仓库完全一样，领域差异全在 08。
- 各领域仓现有的 01/02/03/09/07_content 内容，在“逐个领域合并”任务里迁入 08；本 core 任务只改 Core 侧的规则、代码与测试。

---

## 3. 角色 × 机制单元加载矩阵

图例：**必** = 角色初始化时就加载；**触** = 命中触发条件时加载；**参** = 只需知道存在与入口；— = 不加载。

| 单元 | 规划 | 开发 | 审核 | 特色内容开发 | 教学/使用 |
|---|---|---|---|---|---|
| U0 citystate-os | 必 | 必 | 必 | 必 | 必 |
| U3 context-management | 必 | 必 | 必 | 必 | 必 |
| U4 task-continuity | 必 | 必 | 必 | 必 | 必 |
| U5 task-orchestration | 必 | 必 | 必 | 必 | 必（只用 EXECUTION 部分） |
| U1 mechanism-activation | 必 | 必 | 必 | 必 | 触（有正式交接时） |
| U6 mwu-output | 必 | 必 | 必 | 必 | 触 |
| U9 workflow | 必 | 必 | 必 | 必 | — |
| U10 task-discipline | 必 | 必 | 必 | 必 | — |
| U2 communication | 必 | 触 | 触 | 触 | 触 |
| U7 model-routing | 必 | — | 参 | — | — |
| U8 stage-deliberation | 必 | 触（正式七阶段 run） | 触（正式七阶段 run） | 触 | — |
| U11 publication | 参 | 必 | 触（核对发布读回） | 必 | — |
| U12 tools | — | 触 | 触 | 触 | — |
| 领域 domain-catalog | 触 | 触 | 触 | 必 | 必 |
| 领域内容机制 | 触 | 触 | 触 | 必（相关部分） | 必（相关部分） |

- **五个角色共有**：U0、U3、U4、U5。
- **Core 三个角色共有**：再加 U1、U6、U9、U10。
- **各角色专属**：规划 = U2 必载 + U7 + U8；开发 = U11 + U12；审核 = 独立性规则（在 U5、U9、U10 里）+ 发布读回核对。

按材料体量粗估，规划角色初始化读取约 400 KB 规范材料，开发和审核约 300–350 KB，教学/使用约 200 KB（施工后实测）。

---

## 4. Skill 架构

### 4.1 三层结构

1. **入口层** `citystate-os`：一页 OS 地图。说明 OS 是什么、13 个单元各管什么、五个角色各加载什么、角色初始化怎么做。这一层就是 Human 说的“让模型一下子了解 Core OS 都有什么机制”的那份完整目录。
2. **角色层** `role-planner`、`role-developer`、`role-reviewer`（Core）；`role-content-developer`、`role-content-user`（领域）。每个角色 skill 写：角色定义、产出、不得做的事、**必载单元清单**、触发单元清单、初始化检查、初始化回执格式。
3. **机制层** U1–U12：每个 skill 的 description 写触发条件；正文写 boot 的精确读取清单（必须全读）、入口命令与退出码、receipt 字段、停止条件、“不授权”边界。

### 4.2 不复制正文

skill 是**薄适配层**：只写“何时加载、读哪些精确路径、调用哪些命令”，不抄机制正文。正文仍在 `01_os/` 原处，只有一份。基线里已经发现过两份拷贝漂移的实例（`_dev/开发产物与文件隔离规范_v1.md` 与机制文件），这一条是为了防止再发生。

### 4.3 单一数据源与防漂移

- 在每个机制的 registry 文件里加一个 `skill:` 块（name、description/触发条件、适用角色、必读路径引用 boot load_order）。
- 一个生成脚本从 registry + boot 生成全部 SKILL.md。
- 一个 validator 检查 SKILL.md 与 registry/boot 是否一致（路径存在、blob 与 boot pin 一致、每个 registry 机制都有 skill、矩阵与角色 skill 一致）。不一致就失败，接到现有静态验证里。

### 4.4 放在哪里、谁能读

| 工具 | 读取位置 | 依据 |
|---|---|---|
| Codex | 仓库内 `.agents/skills/<名>/SKILL.md`（从当前目录逐级向上到仓库根） | [Codex 官方文档 Agent Skills](https://developers.openai.com/codex/skills) |
| Antigravity | `.agents/skills/<名>/SKILL.md` | 仓库 `GEMINI.md` 第 58–59 行（2026-07-25 从安装包实测） |
| Claude Code | `.claude/skills/<名>/SKILL.md` | Claude Code 项目 skill 约定 |

所以 canonical 放 `.agents/skills/`，同时生成一份 `.claude/skills/` 镜像，validator 保证两份字节一致。**Claude Code 是否也读 `.agents/skills/` 我没有核实**；如果读，就不需要镜像。

### 4.5 角色初始化流程

1. Human：“你的角色是审核”（可加仓库和任务）。
2. 模型调用 `role-reviewer`。
3. 角色 skill 要求：确认仓库/分支/HEAD/Human 目标 → 读 B0 → 调用全部“必载”单元 skill 并读完其清单 → 跑初始化检查（只读 validator，期望退出 0）→ 有任务就加载任务包或从 PRMS/run 恢复。
4. 输出**角色初始化回执**：角色、仓库、HEAD、已加载 skill 及其清单版本、实际读取路径、validator 退出码、缺口。回执字段沿用现有 boot receipt（mechanism_version、loaded_paths、validator_exit_code），不另造格式。
5. 开始工作；工作中命中触发条件再加载“触”类单元。

### 4.6 Skill 能做和不能做的

- 能做：让“何时加载什么”从“模型自己记得”变成“工具层常驻的描述 + 命中即加载”，解决“只读不运行”的发现与触发问题。
- 不能做：强制执行。模型仍可能不调用。强制要靠 hooks（例如 `SessionStart` 提醒先做角色初始化）和权限，这一步作为可选后续（第 7 节 D4）。

### 4.7 草案示例

**`.agents/skills/role-reviewer/SKILL.md`**

```markdown
---
name: role-reviewer
description: City-State OS 审核角色初始化。当 Human 说“你的角色是审核/独立审核/reviewer”，或要求对某个候选、PR、run 做独立审核时使用。加载审核角色必需的 OS 机制并输出初始化回执。
---
# 角色：审核（independent_review）

产出：MWU 格式审核结论（PASS / FIX_REQUIRED / REJECT）、已审 primary evidence 清单、findings 与残余风险。
不得：修改执行分支；读取执行者私有上下文；把执行者理由当证据；把审核通过当集成授权。

## 初始化（按顺序全部完成）
1. 确认仓库、分支、HEAD、被审对象与 Human 目标。
2. 调用并读完：citystate-os、os-context-management、os-task-continuity、os-task-orchestration、os-mechanism-activation、os-mwu-output、os-workflow、os-task-discipline。
3. 运行：validate_mechanism_activation.py static、validate_minimum_work_unit_output.py static、run_minimum_operational_loop.py static（期望退出 0）。
4. 输出初始化回执（角色、HEAD、已加载 skill、读取路径、validator 退出码、缺口）。

## 触发加载
- 被审对象是正式七阶段 run → os-stage-deliberation
- 需要核对发布读回 → os-publication
- 需要 Human 中转结论 → os-communication
```

**`.agents/skills/os-mechanism-activation/SKILL.md`**

```markdown
---
name: os-mechanism-activation
description: City-State OS 正式跨端点动作的宪法路径。当要让另一个模型或端点行动，或要发出/接收任务范围内的 request、response、result、correction、blocked、decision 时使用；普通 Human 对话不需要。
---
# 机制：mechanism_activation（L3，待独立验收；authority_effect: none）

## 必读（boot load_order，全部读完）
- 01_os/03_mechanisms/mechanism_activation/README.md
- 01_os/03_mechanisms/mechanism_activation/正式动作宪法_v1.yml
- （……其余 boot 清单路径，由生成器从 boot 写入）

## 入口命令
- python -B 01_os/06_execution/boot/mechanism_activation/validate_mechanism_activation.py static .  → 期望 validation_passed / 0

## 停止条件
- 接收方不唯一 → FORMAL_ACTION_BLOCKED_UNTIL_RECIPIENT_RESOLVED
- 绕过 resolver/gate → INVALID_FORMAL_ACTION
```

---

## 5. 新旧内容整合清单（按 Human 原则：以最新为主，过时或冲突的去掉或合并）

| # | 问题 | 新旧判断（实测日期） | 处理 |
|---|---|---|---|
| I1 | “禁止默认预载 `_runs/_dev`”与 boot 要求读其中文件冲突 | 禁载规则是 2026-08 上下文管理的可见性设计；Human 本次明确“按角色加载，不存在授权和禁载区” | 改写为**可见性规则**：累计区不做默认枚举和扫描；任何已加载 skill、boot 或任务精确列出的路径直接读。改 `CLAUDE.md`、`AGENTS.md` 启动第 9 条、开发入口 §1 第 7 条、`01_os/README.md`。顺带把 `01_os/README.md`“无条件读远端 40 位 SHA”改成与 CLAUDE/AGENTS 一致 |
| I2 | `_dev/开发产物与文件隔离规范_v1.md` 与机制文件重复且已漂移 | 机制文件与机器契约 `文件布局契约_v1.yml` 一致，`_dev` 那份有一格不一致 | 保留机制文件，删除 `_dev` 拷贝；boot、validator CM033、registry、开发入口 §12 改指机制文件 |
| I3 | D2 裁决 `_dev/决定_谁执行_v0.2.md` 是活动规则却放在设计区 | 活动、唯一 | 移入 `03_mechanisms/context_management/`，同步改所有引用；v0.1 留在 `_dev/` 作历史 |
| I4 | P2 receipt 来源叠加层：活动规则放在 `_runs`，且内部绑定停在 2026-08-04 | receipt 字段至今未变（仅路径改名） | 把“receipt 字段来源声明”**并入** `实现/加载与receipt契约_v1.yml`，boot 不再钉这份 `_runs` 文件，validator v2 改为检查并入后的合同。原叠加层留在 `_runs` 作历史证据，不改写 |
| I5 | 激活授权 `_runs/…/Human授权_全局机制激活_v1.yml` | Human 原始授权记录 | **保留原位**，它是证据，不是规则；skill 按精确路径引用 |
| I6 | “一个窗口一个任务” | Human 本次说明：窗口是临时工作台，单窗口还是系列由 Human 决定 | 改开发入口 §1、§2 与 `AGENTS.md` 相应表述；任务边界、task packet、allowed paths 等纪律不变 |
| I7 | 审核结论五套词表 | 定义时间：开发入口 §9 2026-08-01；Workflow 07 与 SD-09 2026-08-05；MWU 2026-08-29（最新）。按 Human 裁决 D3 又核对了最近的 workflow 改动（见本表下方说明） | **审核者给出的结论统一用 MWU 的 `PASS / FIX_REQUIRED / REJECT`**；§9 旧词表（无代码读取、实践仅用 2 次）改为这套。**Workflow 07 的阶段完成值保留** `PASS / PASS_WITH_NON_BLOCKING_NOTES`，改为由审核结论推导：MWU `PASS` 且无 findings → `PASS`；MWU `PASS` 且只有非阻断 findings → `PASS_WITH_NON_BLOCKING_NOTES`；`FIX_REQUIRED` / `REJECT` → 阶段不能完成，走重试或上游失效。推导规则写进 07 阶段 README 与七阶段契约；07 产物带 MWU 结论时，runner 检查两者一致。SD-09 `review_state` 补上与 MWU 的对应说明。历史 run 不改写 |
| I8 | 阶段协同推演残留固定轮数 `round_minimums: {full: 5, incremental: 2}` | profile 契约 2026-08-17 已明确删除 | 删除该行；`round_result` 等字段保留（讨论仍可按轮记录，只是没有最低轮数） |
| I9 | task_orchestration 没有 boot，minimum_work_unit_output、task_orchestration 不在机制盘点 | — | 补 task_orchestration boot；两者加入 `机制生效等级与盘点_v1.yml`，等级如实标 |
| I10 | registry 有 143 个文件未覆盖 | — | 补登记（skill 生成器以 registry 为数据源，必须先完整） |
| I11 | 任务原型契约抬头与 §12 仍写“候选 / Draft” | PR #37 已于 `e0bdd7fa` 合并 | 改为已合并的事实（**已获批准**）；同时把 PR #37 run 的 `lifecycle` 从 `candidate_pending_validation` 更正为合并后的值 |
| I12 | 模型目录未登记 Claude Opus 5.5 | — | 登记 claude_code_desktop / Claude Opus 5.5，来源为 Human 当次观察（**已获批准**） |
| I13 | `GEMINI.md` 写“本项目刻意只用两个根文件” | 被 Skill 化决定取代 | 改为说明 `.agents/skills/` 的用途 |
| I14 | `CORE_MANIFEST.yml` 未覆盖 skill 目录 | — | `.agents/skills/` 与 `.claude/skills/` 整体列为 core-owned。领域不在这里加 skill：领域角色 skill 由 Core 提供通用版，领域差异写在 08（§2.4） |
| I15 | `CORE_MANIFEST.yml` 领域合并 HOLD | Human 裁决 D1 | 记录解除依据与合并方式：除 `08_Domain_Applications/` 外全部以 Core 为准覆盖，08 不动 |
| I16 | 领域拥有路径散在 6 处 | Human 2026-11-18 说明：除 08 外与 core 一样 | `CORE_MANIFEST.yml` 的 `domain_owned_paths` 收窄为 `08_Domain_Applications/`；PRMS 的 `domain.py`、`catalog.py`、`examples.py` 及测试把 09 目录路径改到 08；上下文管理的领域运行累计区 `01_os/07_content/_runs/` 改为 `08_Domain_Applications/_runs/`（`工作集与归档契约_v1.yml`、`文件布局契约_v1.yml`、`文件隔离与产物生命周期_v1.md`、`verify_context_structure.py`）；`01_os/README.md` 与开发入口 §3 去掉 `07_content/` 一区；`01_os/07_content/README.md` 删除；`new-domain.ps1` 的领域脚手架改到 08。具体布局以 Q2 为准 |

**I7 为什么不再删除 `PASS_WITH_NON_BLOCKING_NOTES`（D3 核对结果）**：2026-09 以来的 workflow 改动里没有一次涉及审核结论词表。最近几次（2026-11-11 至 11-17）的方向是：真实业务 Done 优先、测试或审核通过不能代替业务结果、05→06 绑定已审原型、07 要核对执行轨迹是否来自批准计划、默认 EXECUTION 模式。2026-09-12/13 加固的是 stage_control 与发布门，发布门直接读取 07 的完成值；开发入口 §9.3 也写明“不修改 07 阶段与七阶段闭环已有的完成判据”。所以删掉一个完成值既不是最新规范的方向，还会动到最近加固的发布门。改为**“审核结论一套 + 阶段完成值由它推导”**：审核者只写一套结论，阶段完成判据不变。施工时 07 阶段的推导规则同时写进最新要求：审核要核对业务 Done，以及执行轨迹是否来自批准计划。

---

## 6. 施工计划（一个大任务，内部迭代）

1. 建任务包与 run（`01_os/_runs/<新 run-id>/`），本方案原文放进 `01_任务输入/`。
2. 整合 I1–I14（先做，因为 skill 要指向整合后的路径）。
3. 补 registry（I10）与 `skill:` 块，写生成器和 validator，生成 13 个机制 skill + 3 个 Core 角色 skill + 领域模板，同步 `.claude/skills/` 镜像。
4. 跑全部只读 validator 与相关测试；受控验证按 managed_verify 执行。
5. **真实业务验证**（第 0 节 Done）：开新窗口，分别只说“你的角色是规划/开发/审核”，检查加载结果是否与矩阵一致，并各做一个小的真实任务。结果如实记录，不一致就修。
6. 推任务分支；一次集中独立审核（不同会话）；master 集成按你的确认。
7. 之后另开任务：逐个领域仓按 §2.4 的方式合并 Core，并在领域仓建领域目录与两个领域角色 skill。

---

## 7. 裁决记录与仍待确认

### 7.1 已定（Human 2026-11-18 答复，本窗口对话）

| # | 事项 | Human 答复 | 方案中的落点 |
|---|---|---|---|
| D1 | 领域仓合并 | 把 Core 的 OS 内容合并进领域仓并覆盖，只保留特色内容，08 文件夹不动 | §2.4、I15、§6 第 7 步 |
| D2 | `auxiliary_mechanical` | 不加入也行，分工不必过细 | §2.1：不设角色，归入任务开发 |
| D3 | 审核词表统一 | 核对是否符合最新 workflow 机制规范，修复方向以最近几次 workflow 改动为主 | I7 已按核对结果修改（保留阶段完成值，改为由审核结论推导） |
| D4 | hooks | 先不加，以后再看怎么用 hook 让模型更好地应用机制 | 本任务不做 |
| D5 | P2 叠加层 | 可以（并入合同） | I4 |
| D6 | 集中独立审核后由 Human 确认 master 集成 | 可以 | §6 第 6 步 |
| Q1 | 领域合并时保留哪些领域路径 | 先答 A（全部保留），随后说明“除 08 外与 core 全部一样”，以后者为准：只有 08 归领域 | §2.4、I15、I16 |

### 7.2 仍待确认

- **Q2 08 内部布局**：按 §2.4 的建议，领域机制目录放 `08_Domain_Applications/domain_mechanisms.yml`，领域运行记录放 `08_Domain_Applications/_runs/`，原 01/02/03 的内容由各领域按需归入 08 的模块目录。是否同意？
- D3 的处理按核对结果写为“保留 `PASS_WITH_NON_BLOCKING_NOTES`，由审核结论推导”（§5 表下说明）；施工中若发现与最新 workflow 规范不符之处，再单独报告。

---

## 8. 风险与未知

- Claude Code 是否读 `.agents/skills/` 未核实（影响是否需要镜像）。
- Skill 只解决发现与触发，不解决强制；模型是否真的按角色加载，要靠第 6 步真实验证测量，不能由文件存在推断。
- 各角色初始化读取量约 200–400 KB，规范材料有冗余（例如开发入口与 AGENTS、纪律之间的重复叙述），后续可以再压缩，本任务不做。
- 统一审核词表（I7）后，历史 run 里的旧词仍在；它们是历史证据，不再用新 runner 重验。
- 领域部分只做模板；真实领域角色要等 D1 解除后在各领域仓施工。

## 9. AGENT_SELF_REPORT

- 本方案的目录统计来自本窗口的只读脚本（registry 路径模式匹配），143 个未覆盖文件的数字依赖我对 registry 模式的解析，施工时会用正式生成器重算。
- 第 3 节矩阵是我的提议，不是仓库既有规则；需要你审定。
- Codex 读取 `.agents/skills/` 来自 OpenAI 官方文档；Antigravity 来自仓库 `GEMINI.md` 的历史实测；均未在本窗口实际运行这两个工具验证。
