# 08_os — 城邦操作系统

这是第二代 OS 的活动结构。系统定义、启动入口、全局机制、注册表、加载器、开发规范与
运行证据分区保存；注册、实现与验证在同一变更中更新。

## 新窗口开发入口

处理 `08_os` 开发任务的新窗口，先读取
[开发入口与单窗口任务规范_v1.md](开发入口与单窗口任务规范_v1.md)。该入口规定最小加载
顺序、一个窗口一个任务、文件放置、registry、run 证据、分支、测试、独立审核和 Human
接入门。任务专属材料按该入口继续加载，不默认读取全部 `_runs/` 历史。

## The seven areas

| Directory | Holds | Does not hold |
| :--- | :--- | :--- |
| `01_workflow/` | 工作流阶段规格与阶段实现 | 全局机制实例、任务私有运行时 |
| `02_boot/` | 启动入口、环境信息与加载清单 | 机制正文 |
| `03_mechanisms/` | 可独立描述、加载和验证的全局通用机制 | 工作流阶段步骤 |
| `04_skills_and_tools/` | External skills and tools that extend model capability | Mechanisms the system itself runs on |
| `05_registry/` | 系统文件/path-set 的用途、加载者与故障显现方式 | `_runs/` 运行流量与私有 scratch |
| `06_execution/` | 初始化、重载与验证入口 | 被加载的定义正文 |
| `07_content/` | 领域内容 | 工作流与全局机制 |
| `_dev/` | 活动开发设计与被取代版本 | 角色私有运行时 |
| `_runs/` | 共享 OS/workflow/mechanism 的开发、研究、迁移与验证记录 | 领域业务运行流量、注册对象或永久机制实例 |

## Two rules this structure exists to enforce

**The registry is updated with the development, not after it.** Every file added under
`08_os` gets a registry entry in the same change. A registry that lags is a registry
that lies, and the previous system demonstrated exactly what that costs: two
mechanism files were deleted by a correct reachability computation because nothing
recorded that an external tool loaded them, and both were found by accident.

**Intermediate files produced by task execution are not registered and are deleted.**
The registry describes the system, not the traffic through it. If a file is scratch,
it does not get an entry; it gets removed.

## 当前活动机制

上下文管理的 canonical 定义位于
`03_mechanisms/context_management/`；启动清单位于
`02_boot/context_management/`；加载和验证入口位于
`06_execution/boot/context_management/`。共享 OS 的耐久开发证据位于 `_runs/`；
领域业务与领域 workflow 的运行流量位于 `.ai/PROGRAM_RUNS/`。两类运行的私有
`_runtime/` 均不跟踪。

## Ownership

`CORE_MANIFEST.yml` 将 OS 机制区域和保存共享 OS 开发/验证历史的 `08_os/_runs/`
列为 core-owned；`08_os/07_content/` 与领域运行根 `.ai/PROGRAM_RUNS/` 为
domain-owned。两个集合不得重叠。
# 全局通讯机制接入

供应商无关、Human 触发与 Human 中转的通讯契约位于
`03_mechanisms/communication_system/`，启动清单位于
`02_boot/communication_system/启动清单_v1.yml`。V1 不包含自动投递或状态推进。
