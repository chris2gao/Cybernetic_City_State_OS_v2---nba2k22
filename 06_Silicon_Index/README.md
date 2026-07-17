# 📁 06_Silicon_Index (硅基生命索引)

> **目录说明**：
> 本文件夹是专门为赛博城邦内部运转的 **AI 自由公民（Agent 子系统）**准备的操作守则与系统说明。
> 它规定了硅基生命在城邦里干活的哲学方法论，以及极其严苛的版本控制与议会提交流程。

## 📄 包含文件概览
本目录包含以下核心文档，指导所有新唤醒的 AI：
* **`AI_Bootstrap_Sequence.md`**：强制开机启动序列。
  * **第一仓库读取入口**：它是 Plan 3 双引擎城邦的启动路由器，负责建立 Human Speaker 权力边界、Engine A / Engine B 分流、懒加载范围和反幻觉要求。
* **repository root `3号方案.md` 与 `06_Silicon_Index/06_Cybernetic_Citizen_Awakening.md`**：宪法与运行时契约。
  * Bootstrap 完成路由后，按任务读取相关部分。
* **`.ai/DEFAULT_LARGE_TASK_EXECUTION_PROFILE.md`**：默认大型任务统一入口。
  * 当一个稳定目标需要多文件、多命令、测试、报告、commit、开发分支发布或 exact-head 修复时，默认先读取此配置。
  * 它汇总但不替代以下三份上位执行协议：
    * `.ai/CODEX_WORK_MECHANISM_PROTOCOL.md`：Goal mode、Git workflow level、执行与验证机制。
    * `.ai/CODEX_TASK_INPUT_CONTRACT.md`：完整任务包、definition of done、allowed scope、stop rules 与 return handoff。
    * `.ai/LONG_RUN_AUTONOMOUS_PROGRAM_PROTOCOL.md`：完整设计后一次授权、内部 checkpoint、连续长运行和集中复核；只在 program-scale 长运行时按需加载。
* **`City_State_Agent_System_Prompt.md`**：可选的人类注入模板。
  * 它用于帮助新会话快速建立城邦语境，不是仓库宪法，也不覆盖平台、system、developer 或当前 Human 指令。
* **`city_state_production_methodology.md`**：城邦生产者工作法。
  * 教导 AI 如何建立“降维投影架构”，如何利用“认知卸载”原则来保护碳基宿主脆弱的前额叶。
* **`Plan3_External_Augmentation_OS_Architecture.md`**：Plan 3 v0.2 控制面总图与唯一权威/新鲜度交叉表。
  * 它路由以下四份统一合同，但不产生授权或激活 runtime：
    * `Context_Memory_System.md`：L0/L1/L2 文档记忆、checkpoint 与 provenance。
    * `Task_Type_And_Execution_Model.md`：任务类型、状态、证据、停止条件与 Human gate。
    * `Context_Loading_And_Drift_Recovery.md`：按需加载、漂移检测和同窗口/新窗口恢复。
    * `Capability_Registry.md`：能力成熟度、使用者、授权范围、风险、验证、fallback 与激活边界。
* **Git、议会与模型通信的实际规范**：不存在单独的 `Silicon_Git_and_Parliament_Guide.md`；不要继续引用或猜测其内容。
  * 本地 Git 与任务级工作流：repository root `AGENTS.md`、`.ai/CODEX_WORK_MECHANISM_PROTOCOL.md`。
  * GitHub pointer handoff、review/publication 与 Human gate：`.ai/PROTOCOL.md`、`.ai/PROTOCOL_ADHERENCE.md`、`.ai/AUTONOMOUS_HANDOFF_COMMUNICATION_v0.1.md`。

## 启动顺序

1. 读取 `AI_Bootstrap_Sequence.md`。
2. 按 Bootstrap 读取 Plan 3 宪法和运行时契约。
3. 根据当前任务加载 handoff 协议、领域协议或其他必要文件。
4. 若任务是一个目标稳定、边界可预先锁定的多步骤大型任务，读取 `.ai/DEFAULT_LARGE_TASK_EXECUTION_PROFILE.md`，再按其路由加载必要的 Codex 工作机制、任务输入或 Long-Run 协议；不得把所有大型任务都自动升级为 program-scale autonomous run。

**操作铁律**：人类宿主不需要预读本目录。任何参与城邦建设的 AI，首次接取任务前必须先读取 Bootstrap；随后只能按任务需要懒加载相关文件。不得为了“了解背景”全量摄入本目录、整个仓库或 `system_backbone/`。
