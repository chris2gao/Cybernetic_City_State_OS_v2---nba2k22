# OS-PRMS Fork 共用基线与角色窗口方案 v1（规划候选）

本方案供 Human 创建 GitHub/PRMS 来源可追溯的 NBA2K22 公共上下文母窗口，再使用 GPT/Codex 的窗口 Fork 派生不同岗位模型。**不是已经上线的自动聊天注入程序，也不改变 Core 四个标准协作角色。**

依据：Core/master e075cdf288a765b7bfd2f4891c8f384404da16e1；Core model_routing/协作角色与接收者设置契约_v1.yml；Core PRMS/TASK_CONTINUITY.md；NBA Draft PR18 项目总索引 094f1aa641f93dec2277707ad9dbf5bdb0341247。使用时必须重新核对当前 HEAD；NBA Issue #11 正在进行时，不宣称 NBA/master 已更新。

## 1. 窗口结构

NBA2K22_COMMON_BASELINE（只读公共上下文，禁止在母窗处理独立业务任务）
- decision_architecture：需求、架构、规划、重大方案选择；推荐 GPT 规划窗口。
- execution：工程实现、代码与验证；推荐 Codex 等可运行代码的窗口。
- independent_review：独立反证和验收；从母窗直接 Fork，不能从开发者执行窗口 Fork。
- auxiliary_mechanical：资料检索、清单、批量机械作业、证据归档；不得代替最终审核或新 Human 产品裁决。

四种是 Core 已定义的 collaboration_roles，并非 GPT/Codex/Gemini 产品名。实际底层模型要由 Human 在产品中选择，不能靠提示词声称已切换模型。NBA 的 GM、Coach、Player 是领域业务人格，不是上述四类工程协作角色。

当前只需一个 NBA 公共母窗，内含 Core + NBA 公共资料。如果未来同时启动多个领域，可先 Fork 一个 Core-only 公共母窗，再从它派生 NBA 母窗；不要提前创建无用窗口。

## 2. 母窗口加载边界

必须实际读取：
- Core 与 NBA 当前 master SHA，AGENT_WORKING_DISCIPLINE.md、AGENTS.md、01_os/README.md、01_os/开发入口与单窗口任务规范_v1.md、CORE_MANIFEST.yml。
- Core PRMS/README.md、PRMS/TASK_CONTINUITY.md、model_routing/README.md，及完整 G1 机制/Workflow/Boot/Registry **目录概要**，显示来源和生效等级，不默认全文注入所有文件。
- NBA 08_Domain_Applications/domain.yml 与项目索引 08_Domain_Applications/Antigravity_GM_Engine/PROJECT_INDEX.md、docs/development/PROJECT_MODULE_REGISTRY_V2.json。P00–P12 共13模块，应列全名称、状态和当前真实 Git 来源。初始项目索引在 Draft PR #18；只有真实完成合并后才可称在 NBA/master。
- 有原件支撑的跨任务 Human 共识：真实游戏原生状态与数据来源的权威边界、GM/Coach/Player 决定 WHAT/WHO/VALUE、REA只负责 HOW、研究候选不等于实机已验证、重要历史记录不能静默改写。
- 当前 NBA 正式 G2 目录（不存在则明确 UNINITIALIZED）、PRMS 任务保存/恢复/人工中转规则。

不得默认全文加载：所有 01_os/_runs、694 条游戏研究、P09 REA源码、数据库全字段、任何单一执行者私有叙事。母窗不承接某个业务任务，不赋予角色权限，不修改仓库。

## 3. 母窗提示词

请初始化 Cybernetic City-State OS/NBA2K22 的只读公共上下文基线。本窗口的唯一任务是构建可供后续 Fork 的公共导航与已批准共识，不承担某个特定开发、规划、验收业务任务，也不自行做新 Human 决定。

首先从当前远端仓库实际取得 Core 与 NBA master 的精确 SHA，遵循 AGENTS.md、AGENT_WORKING_DISCIPLINE.md、01_os/README.md、01_os/开发入口与单窗口任务规范_v1.md 以及 CORE_MANIFEST.yml。按真实 Boot/Registry 核实全局机制。

只读收集和摘要：B0 核心启动与规则；G1 机制/Workflow/Boot/Registry 全部目录与触发条件；NBA 领域身份、G2 正式发布状态；全项目 PROJECT_INDEX.md 与 PROJECT_MODULE_REGISTRY_V2.json 中 P00–P12 全部13模块的名字、成熟度、canonical入口；来源明确的跨任务 Human 已批准共识；PRMS 的显式保存与新窗口恢复机制。

优先用项目导航索引而非全文装入全部研究与源码。绝不把 Draft PR18 的内容冒称已经进 master，不把 P00–P12 当成正式 G2，也不调用游戏/REA、改仓库或生成某个具体任务的方案。

最后提供 NBA_COMMON_BASELINE_RECEIPT，包含 Core/NBA SHA、逐项 G1/G2 与 P00–P12目录、已读原文与仅索引材料的区别、共有 Human 决定及来源、缺口、版本差异、任务 Fork 时对应 Pxx 扩展路径。只有真实来源已读并且主要清单无未解释缺口，才写 NBA_COMMON_BASELINE_READY。Human 从此条回复 Fork；之后母窗不承接业务对话。

## 4. Fork 子窗激活提示词

本窗口从 NBA_COMMON_BASELINE_READY 公共母窗口 Fork。继承分叉时的公共目录和共识，但不会自动获得最新 Git 版本或其他子窗之后的决策。现激活：
- domain_id: nba2k22
- collaboration_role: 【decision_architecture | execution | independent_review | auxiliary_mechanical】
- 实际平台与模型: 【以此处实际产品设置为准】
- role_instance: 【已有角色实例ID，或无】
- task_id / Run / PR / source: 【具体填写】
- 本次目标: 【具体填写】
- 操作边界: 【只读/允许的工程分支和文件路径】
- 验收成果: 【具体填写】
- 上下文深度: 先加载 B0 + G1/G2目录 + 当前任务T1；其它资料按当前任务和已保存的 Human 选择展开。

先核对当前 Core/NBA HEAD 与母窗口来源版本的变化；根据任务涉及的 Pxx/G1/G2 触发实际读取，而不是全部资料全文注入。若已有已保存的 PRMS state/task，可执行 task_cli.py resume 并读 CONTEXT.md；否则只读该任务的 GitHub Run 和 Human 批准原件，明确标注 GITHUB_RUN_RECOVERY，不得伪称 PRMS 状态库已保存。

输出任务恢复回执：角色与任务 ID、原文来源、已批准共识、当前进度、未完成事项、已载入正文、只发现目录与缺失内容、建议下一步。独立审核岗位不能继承开发执行者的私有论证或沿用其自评当结论。完成该回执后开始本岗位工作。

## 5. Fork 使用方法和长期一致性

1. 新建一个独立 GPT（或 Codex）母窗，发送上述母窗提示词，核对 BASELINE_READY 并保留母窗不做其它业务。
2. 从其 BASELINE_READY 回复 Fork，每个子窗第一条输入按上述模板明确岗位、task_id、范围。
3. 规划岗位生产的正式决策先归档到 GitHub Run 或真实 PRMS State；执行岗位读取已发布任务合同；审核岗位从干净母窗 Fork，独立固定代码 SHA 验证。
4. Fork 是公共前缀的分叉快照，不是活动共享Git分支。A子窗后续决定不会自动回写母窗或传播给 B；需要先入正式持久资料再显式恢复。
5. 基线过期则在新版公共母窗重读差异，保留旧基线的 source SHA 与 Human 决议来源，不以旧 fork 私自假装同步成功。
6. 跨 GPT 与 Codex 产品没有可假定的直接共用会话 Fork；用同一 GitHub 公共索引/已保存任务记录在不同平台分别初始化基线。

## 6. 验收建议（未执行）

BASE-01 四个 Core 协作角色及NBA P00–P12 完整可发现，正式发布与候选分开。
BASE-02 同一母窗 Fork 规划、开发、审核，分别只加载各自必读任务原文。
BASE-03 审核窗没有开发窗私有叙事；实际源码回读独立进行。
BASE-04 子窗新决定不改变其它子窗或母窗，持久记录必须显式写入。
BASE-05 Core/NBA SHA 变化后检测到差异，过期内容不冒充最新。
BASE-06 未配置 PRMS state 时使用 Run 恢复且诚实标注；配置后才调用 resume。

**计划状态**：FORK_BASELINE_DESIGN_V1；不是要求 Codex 立刻开发新的自动 Fork 功能。
