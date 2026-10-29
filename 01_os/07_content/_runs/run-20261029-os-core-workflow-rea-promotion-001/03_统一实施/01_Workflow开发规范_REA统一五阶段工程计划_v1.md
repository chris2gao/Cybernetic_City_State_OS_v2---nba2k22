# OS Core 统一工程任务：Workflow 开发规范升级 + REA 可选工具接入（五阶段计划 v1）

**任务 ID**：OS-CORE-WORKFLOW-REA-PROMOTION-20261029-001  
**2026-10-29 Human 最新裁决**：“可以混入，一起完成。分阶段执行呗。”  
**继承前一裁决**：“不需要兼容旧任务，不要过度设计……替换掉旧的对应语义内容，完成迁移即可。”  
**状态**：PLANNING_READY，实际工程开发尚未开始；属于 NBA2K22 的 OS 规划分支资料，Core 代码所有权仍在 Core。  
**执行方式**：一个主任务、一位 Codex 工程 Owner、分阶段提交和验收、一次最终集成审核；不把 Workflow 与 REA 分成需要二次授权启动的两个产品任务。
**主仓**：chris2gao/Cybernetic_City_State_OS_v2---core  
**配套域仓**：chris2gao/Cybernetic_City_State_OS_v2---nba2k22  
**不触碰**：其余领域仓库。  
**不授权**：Core 或 NBA master 无审核直接合并、运行游戏/不可逆原生业务操作、系统级自动安装或修改管理员权限。

## 1. 最新仓库取证

- 2026-10-29 复核 Core/master = \`e075cdf288a765b7bfd2f4891c8f384404da16e1\`（已包含 PRMS）。
- 2026-10-29 复核 NBA/master = \`4a7d3de013fdddee66b64c0a8a31b6d346982540\`；Core Issue #11 已 CLOSED。新工程启动前务必再 fresh-read。
- NBA PR #18 仍 OPEN/DRAFT，HEAD \`094f1aa641f93dec2277707ad9dbf5bdb0341247\`；其 PROJECT_INDEX、13模块注册表、REA交接、Action Surface 属于该明确来源，不等于 NBA/master 文件已存在。
- 规划分支：\`planning/os-core-workflow-rea-upgrade-20261029\`。当时分支基于NBA旧master；不要直接把规划分支合并进新master或用它倒灌Core，正式工程应以各仓新master建任务分支。
- 方法来源：Core Stage01 \`方法论_v0.2.md\` blob \`4c81218b68da47305d333967400d4e03f74705f1\`，NBA Stage01 \`方法论_v0.4.md\` blob \`78f6ea4edb00ee21d246ca662ae8ce188b8131d6\`；后者保留A0/A区分和明确交付对象，但新Core主语义只采用一个活动版本。
- REA历史来源：NBA PR18 \`research/rea_native_control/REA_WINDOW_CONTEXT_HANDOFF_20261028.md\`；历史Windows机器证实REA 6.8.0存在，但当前目标环境每次必须实际检测，不能把历史工具数229写成现在实时已安装。
- 先前规划的 \`00_任务章程\`、\`01_W1信息收集\`、\`02_W1设计\` 均为早期分包/直接替换的过程材料；**本文件是后继统一工程范围**，不重新引入旧任务兼容。

## 2. 五阶段工程（按序推进，完成前一阶段再进入下一阶段）

### S1 · Core Workflow Stage01 唯一语义替换

**目标**：Stage01 = 01a共识A0→Human确认→01b完整需求结果A→Human确认；02查证，03定实现B，七个stage_id保留不变。

**改动范围**：\`01_os/01_workflow/01_需求建模/\`（活动方法论、README、必要结果项模板）、\`01_os/02_boot/workflow_minimum_operational_loop/\`、\`01_os/05_registry/workflow_minimum_operational_loop_v1.yml\`、Stage01 Schema、七阶段runner和直接相关fixtures/tests。复用 \`stage_collaborative_deliberation\` 和历史发布门的已有职责，避免第二套验证器。

**最小结果**：单一活动规范，无双模式profile、旧任务兼容器、旧Run迁移器。程序能拒绝仅有A0、错误版本的A确认、空结果项/缺success criterion映射；语义充分性仍归模型/Human，不能用字段计数声称完全理解。其它六阶段主流程不改。

**阶段完成**：文件引用一致、同一分支/commit中的新规范测试真实通过、固定测试证据可复验。

### S2 · 通用开发工作规范与阶段02证据升级

**目标**：只吸收NBA已证明有价值、且对Core一般任务可重用的规范；优先在既有OS/PRMS/Task Orchestration中扩展，禁止造第二套OS。

**四个最小交付**：

1. **项目目录/模块索引规范**：按需发现项目目录、机器可读模块Registry、关联源码/研究/任务；记录 \`affected_module_ids\`、\`source_refs_read\`、实际 source SHA 与 Draft/master 区分。修改模块实现时同PR同步受影响模块的索引；缺漏显示 \`INDEX_SYNC_PENDING\`。Core只提供通用结构和轻量校验，NBA13模块数据留在领域仓。
2. **多模型顺序协作与独立审核**：实际工作区共享时单一写入Owner、研究/执行/审核岗位分工、交接的确切commit和可重现证据；按任务而非供应商强制选择工具，不规定全OS永久只用Codex。
3. **失败收敛与完成定义**：错误签名/工具层级区分、重复尝试止损、操作结果未知不盲重放、受限预算、真实readback、关闭任务时记录计划-实际差异和待办；对无副作用的普通开发任务不要套用游戏级流程。
4. **研究与证据成熟度**：02阶段优先查证可行性，领域知识只按需做语义背景；对研究资料区分原始/静态、fixture/离线验证、特定实测效果、独立审核、UNKNOWN。历史实测范围不能凭条目数量推广。

**阶段完成**：只变更必要的Core上下文/任务编排/02阶段和Registry文档、最小验证器、反例测试；已存在功能以引用而非重复实现。

### S3 · REA Core 可选工具的通用接入

**目标**：把可移植的 REA 接入流程、能力与失败回执作为 **Core on-demand tool**，而非全局必装机制，更不是让篮球游戏原生ABI进Core。

**位置（候选）**：
- \`01_os/04_skills_and_tools/rea/README.md\`：安装与适用边界、版本/工具schema探测、选择调用/失败解决策略；
- \`01_os/06_execution/tools/rea/\`：可复验的CLI/包装器、只读/无害离线查询、输出标准化；
- \`01_os/05_registry/skills_and_tools_v1.yml\`：按需发现，默认不加载/不启动。

**最小可执行功能**：发现 CLI/npm 或宿主已有 REA 入口；探测实际当前环境、版本和工具能力；规范化调用输入、有限预算、退出码、原始证据路径和结构化回执。对缺装、版本不兼容、后端未安装、权限不足、超时和状态未知作准确反馈。已有受测工具才登记 \`verified\`，否则记录 \`AVAILABLE_UNVERIFIED\` 或 \`NOT_INSTALLED\`，不凭历史REA6.8.0一笔带过。PowerShell/Windows为已有证据场景，Core代码应允许运行于无REA的机器并如实降级。

**优先实践**：局部 PE/metadata/静态定位优先、可控Frida观察、失败签名去重、source fingerprint、证据可重现；不是把 REA 整个229工具再封一层，更不是创建默认会附加管理员游戏进程的自动Agent。

**阶段完成**：当前实际能执行的无害REA工具用 wrapper 测通并保留真实回执；若执行环境没有REA，则最低交付代码+可复现fixture测试+明确未安装状态，不能声称REA真实调用已验证。无须等待游戏启动。

### S4 · NBA2K22 REA 专有 Profile 与项目规范接合

**目标**：Core工具只承担可移植的调用机制、来源、回执；NBA领域保存专有目标身份、游戏版本/RVA、MyLEAGUE对象/调用约束、GM/Coach/Player 的确定性业务动作。

**来源**：PR #18 @ \`094f1aa641f93dec2277707ad9dbf5bdb0341247\` 的P04、P09、P12及 \`ROLE_MODEL_MECHANISM_GUIDE.md\`、\`VALIDATION_RESULTS.md\`、\`REA_WINDOW_CONTEXT_HANDOFF_20261028.md\`。不能把62静态动作、229工具/历史管理员PID当成当前实机全部可运行。

**最小结果**：NBA Domain-owned 的REA Profile/入口说明与通用 Core adapter 对应；更新项目索引与模块注册表（所在真实PR/branch），区分LiveEffectVerified / StaticRecovered / Pending；用结构化输入输出离线fixture证明 Core<>Domain 边界。此阶段不需要运行NBA2K22进程或重放交易、球探、训练等历史副作用动作。

**阶段完成**：Core无需 import NBA代码；NBA可以按 task_id/affected_module_ids 找到REA Profile和实际工具合同，证明正确发现来源和对缺失Core工具的提示。

### S5 · 统一集成、完整测试与交接

- Core的S1/S2/S3可在**同一个主工程任务分支、同一个最终Core PR**分阶段提交，减少无意义审批；S4按NBA领域所有权可在单独关联分支/PR，**不要把NBA整个08合入Core**。
- 前四阶段每阶段运行本阶段针对性测试并记 Git commit；最后跑Core现行七阶段、PRMS、机制Registry、工具发现回归和 S1–S4的负例。
- 固定Core PR、NBA配套分支/PR各自的源码SHA、变更路径、实际命令/输出、未运行原因、当前工具环境、成功/失败/UNKNOWN分项；准备独立审核。
- 正式合并Core/master和NBA/master属于两个明确发布动作；本次人类“合并范围”是**同一个工程任务范围**，不是自动合并或执行游戏授权。若用户之后明确批准最终合并，可按OS现行发布门处理。
- 旧Run直接使用Git历史保留，不要求七阶段新语义能继续跑旧Run；不改写Git历史本身。

## 3. 冻结验收原则

1. **可用优先**：最终要能实际运行Core Stage01新规则、实际在有REA的环境按任务调用已选工具、NBA能发现专有Profile，而不止有更多的YAML/README。
2. **单一权威**：Core是Workflow和通用REA工具接口的唯一Owner，领域只保留NBA Profile/业务知识，不反向复制通用Core。
3. **轻量**：不做旧需求兼容、不重建PRMS、不建额外服务/权限体系、不把全部REA工具安装到每个项目。
4. **明确事实成熟度**：本地fixture、真实CLI调用、NBA游戏实际效果、独立审核、发布可用是不同状态。
5. **完整性**：完成后有可运行源码、具体使用命令、固定来源、测试证据、独立审核输入与Human可读教程；不以文档更新冒充工程完成。

## 4. 下一动作

本计划已包含Human同意的“统一范围与分阶段执行”。GPT准备Codex实施提示词、保留独立审核角色；Codex作为唯一实现Owner，从Core新master和NBA真实来源开始，按S1→S5连续开发。仅遇真实新产品方向、受保护发布或对游戏产生副作用的操作时需Human另行裁决。全部阶段完成后才做统一最终评审。
