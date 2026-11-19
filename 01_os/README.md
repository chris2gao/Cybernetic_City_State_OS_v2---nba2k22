# 01_os — 城邦操作系统

这是第二代 OS 的活动结构。系统定义、启动入口、全局机制、注册表、加载器、开发规范与
运行证据分区保存；注册、实现与验证在同一变更中更新。

## Repository-wide 新窗口入口

根级 router 对每个 repository working window 启用 repository-wide always-on
bootstrap：确认仓库、工作分支与 Human 目标，读取 `AGENT_WORKING_DISCIPLINE.md` 与
`AGENTS.md`，然后无条件读取 `01_os/README.md`（本文件）和
`01_os/开发入口与单窗口任务规范_v1.md`（[打开文件](开发入口与单窗口任务规范_v1.md)）。
远端 `master` 精确 40 位 SHA 只在 material write、不可变证据或发布/受保护动作边界
fresh-read，不作为每个窗口的启动门。进入本 repository 工作本身就进入 OS discipline；
这不表示其余 OS 内容被全部加载。

**按角色加载。** Human 说明角色（任务规划、任务开发、审核；领域仓另有特色内容开发、
特色内容教学或使用）后，模型调用对应角色 skill（`role-planner`、`role-developer`、
`role-reviewer`、`role-content-developer`、`role-content-user`），由它加载该角色需要的
全部机制 skill 并输出角色初始化回执。`citystate-os` skill 是整个 OS 的目录。skill 位于
仓库根 `.agents/skills/`（Claude Code 读 `.claude/skills/` 镜像），由
`06_execution/skills/generate_skills.py` 从 registry 生成，不手改。聊天窗口是临时工作台，
一个窗口承担一个任务还是一个系列由 Human 决定。

`current Human natural-language request` 本身就是有效 task input。已有
`durable task packet` 时加载它；若尚无 packet 且工作会造成 `material repository
mutation`，须按开发入口在第一次 business/canonical write 前建立 task packet 与 run
evidence，不要求 Human 手工粘贴固定初始化包。累计区（`_runs/`、`_communication/`、
`_dev/`、`08_Domain_Applications/_runs/`）不做默认枚举或整区读取；已加载 skill、boot
清单或当前任务精确列出的路径直接读取，没有另外的授权或禁载区。

## The areas

领域内容不在 `01_os/` 内：领域仓库 = 最新 core + 领域自有的 `08_Domain_Applications/`（领域内容、
`domain.yml` 与领域运行记录）和 `09_Domain_Global_Mechanisms/`（领域加载配置，即领域机制目录
`domain_mechanisms.yml`）。core 不带这两个目录，领域仓经合并 core 升级 OS（Human 决定 2026-11-18）。

| Directory | Holds | Does not hold |
| :--- | :--- | :--- |
| `01_workflow/` | 工作流阶段规格与阶段实现 | 全局机制实例、任务私有运行时 |
| `02_boot/` | 启动入口、环境信息与加载清单 | 机制正文 |
| `03_mechanisms/` | 可独立描述、加载和验证的全局通用机制 | 工作流阶段步骤 |
| `04_skills_and_tools/` | External skills and tools that extend model capability | Mechanisms the system itself runs on |
| `05_registry/` | 系统文件/path-set 的用途、加载者与故障显现方式 | `_runs/` 运行流量与私有 scratch |
| `06_execution/` | 初始化、重载、验证与 skill 生成入口 | 被加载的定义正文 |
| `_dev/` | 活动开发设计与被取代版本 | 角色私有运行时、活动规则 |
| `_runs/` | 共享 OS/workflow/mechanism 的开发、研究、迁移与验证记录 | 领域业务运行流量、注册对象或永久机制实例 |

## Two rules this structure exists to enforce

**The registry is updated with the development, not after it.** Every file added under
`01_os` gets a registry entry in the same change. （依据：入口依据与事故记录_v1.md §R-1）

**Intermediate files produced by task execution are not registered and are deleted.**
The registry describes the system, not the traffic through it. If a file is scratch,
it does not get an entry; it gets removed.

## 当前活动机制

上下文管理的 canonical 定义位于
`03_mechanisms/context_management/`；启动清单位于
`02_boot/context_management/`；加载和验证入口位于
`06_execution/boot/context_management/`。共享 OS 的耐久开发证据位于 `_runs/`；
领域业务与领域 workflow 的运行流量位于 `08_Domain_Applications/_runs/`。两类运行的私有
`_runtime/` 均不跟踪。

## Ownership

`CORE_MANIFEST.yml` 将 OS 机制区域和保存共享 OS 开发/验证历史的 `01_os/_runs/`
列为 core-owned；`08_Domain_Applications/`（含领域运行根 `08_Domain_Applications/_runs/`）
与 `09_Domain_Global_Mechanisms/` 是仅有的两个 domain-owned 路径。两个集合不得重叠。
# 全局通讯机制接入

供应商无关、Human 触发与 Human 中转的通讯契约位于
`03_mechanisms/communication_system/`，启动清单位于
`02_boot/communication_system/启动清单_v1.yml`。V1 不包含自动投递或状态推进。

## 全局 Minimum Work Unit 输出

正式 material work unit 在以下三个边界必须加载
`02_boot/minimum_work_unit_output/启动清单_v1.yml` 并遵循
`03_mechanisms/minimum_work_unit_output/最小工作单元输出契约_v1.yml`：

- decision / architecture 的正式派单；
- execution completion / handoff；
- independent review completion。

该契约要求“做/要求了什么、方法、supportability rationale、feasibility rationale”，并由角色补充
结果、证据、边界或审核字段。reviewer 必须把 executor rationale 当作待验证命题，以 primary
evidence 检查其支撑性，而不是把 rationale 本身当证据。

这只是一项 output obligation：不适用于每个工具调用、微操作或 private reasoning，不要求
chain-of-thought，不改变 communication envelope、task scope、model routing 或 Human confirmation
规则，`authority_effect: none`。Legacy artifact 不因缺少 MWU 字段而被追溯判无效。
