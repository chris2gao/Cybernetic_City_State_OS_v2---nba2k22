# Codex · Core OS 金蛋 Workflow · 最小工程候选执行任务 v2

**任务**：`OS-CORE-GOLDEN-EGG-PATH-EFFICIENCY-CANDIDATE-20261116`  
**执行角色**：`execution / Codex`；**评审方式**：Human 最终裁决 + GPT 证据/代码复核；本任务取消单独独立审核模型交接。  
**状态**：`IMPLEMENTATION_CANDIDATE_AUTHORIZED_BY_CURRENT_HUMAN_CONTINUATION`，**不是**正式 Core Stage04 冻结 / Stage07 PASS / master 合并授权。

## 0. 最新合同覆盖旧阻断的范围

此合同替换同目录旧版 `CODEX_STAGE04_STAGE05_EXECUTION_CONTRACT_v1.md` 对 **当前工程候选实施** 的 G1→G2→G3 严格前置顺序。**旧任务正式冻结仍 blocked 是事实，不需要再次验证。**现在先以固定测试候选进行小范围、可复核、独立 task-branch 工程研发；正式七阶段集成与 Human 冻结将另行按实际规则办理，不伪造任何门票。

### 唯一输入（固定交接源）

仓库：`https://github.com/chris2gao/Cybernetic_City_State_OS_v2---core`

从当前 handoff 分支固定 Commit 读取，**不要从已过期的旧测试文件开启工程**：

- `01_os/_dev/golden_egg_workflow_20261116/GOLDEN_EGG_A0_A_B_AND_REVIEW_DECISION_v1.md`
- `01_os/_dev/golden_egg_workflow_20261116/OS_CORE_GOLDEN_EGG_ENGINEERING_TEST_CANDIDATE_v2.yml`
- 本合同。

源码对照：Core master `043ac4864bdc871b03929faafd8bc6bd47d4ee2f`；PR #23 `6d97d2d3e2527f38e688998e9b8de03553046dbe` 为可选择复用的 Draft 参考（非 master）；PR #34 监控器不修改。真正开工前**只核一次**当前 master 和任务分支；版本不同则明确差异，不全库搜索。

## 1. 本次实际 Goal 与 Done

**Goal**：最小实现“已批准业务分配保持稳定、Ready 局部失效与复用、关键阻断优先、停止无信息重复工具行动、真实父 Done、时间事实不误用”，让实际的 Stage05/06 执行决策能被可失败的测试观察；不开发通用 Agent 调度平台。

**候选 Done（不是正式总体 Done）**：
- 同一业务例子中，T01（无新信息重复取不可用 SHA）、T02（worldline 不重分组）、T09（最小必要身份具备时先进行决定性日历安全检查）有“改造前失败/正确实现后通过”的对照。
- 当前工程候选的 T01–T14 在适用范围内有实际运行结果；既有 Core 测试运行并报告退化情况；无法落实的必须标注 `NOT_RUN/BLOCKED`，不伪造通过。
- 至少一个**实际任务决策调用路径**使用该逻辑，而非只新增 README/不可达 helper。
- 不侵犯授权、不自动重试 UNKNOWN，不改变已批准矩阵；父 Done 不以工具测试替代。
- 精确 changed paths、测试命令/退出码、实现 commit/分支、残余 gap、实际执行耗时/UNKNOWN 交付给 Human/GPT。

**上层验收**：T15 是后续另行授权 NBA2K22 实机对照；当前不调用游戏，不把候选工程通过等同于 SC-10 满足。

## 2. 最短 G/R/A/D

**G1 源码定位**：读取上述三文件、PR23 Atom/Chain/Executor 和现有 Stage05/06/07 与 runner 的必要入口；只找实际调用路径和需要改的点。**Done**：可指定真实被调用的函数/契约与最小变更位置。

**G2 先跑反例**：使用新候选的 T01/T02/T09 和必要既有负例，先证明朴素实现/当前行为失败；冻结这份工程候选输入，后续只能修实现。**Done**：留下可复算 `before` 证据。

**G3 最小修改**：在新 task implementation 分支实现局部 Ready 失效、关键阻断优先与业务选择稳定，采用已有受控入口；其余既有保护机制直接复用。阶段 05–07 只作有真实必要性的最小连接，不要新 runner、scheduler、审批、monitor、全局设置扫描或第八阶段。**Done**：新代码被实际路径调用，且 T01/T02/T09 等反例按原定义通过。

**G4 验证收束**：执行 T01–T14 合理可运行部分及现有相关回归；注明哪些只测静态/离线机制，哪项尚未实机。输出小型差异与测试事实，提交代码到普通 task branch 并停止。**Done**：交付 Commit + 结果，无 master 合并、无自我独立验收。

## 3. 写入与作用范围

- **工程分支**：从核实后的 Core master 创建单独 `task/core-golden-egg-path-efficiency-20261116`（不在之前的手工交接文档分支里混入生产代码）；先检查是否存在，存在则核对实际 HEAD，禁止覆盖他人历史。
- **初步允许修改路径**（是可变更上界，不是逐文件强制任务）：`01_os/03_mechanisms/task_orchestration/**`、`01_os/06_execution/task_orchestration/**`、`01_os/01_workflow/{05_步骤拆分,06_执行,07_测试执行}/**`、`01_os/06_execution/workflow/minimum_operational_loop/**`、必要时 `01_os/_runs/**` 的精简公开证据。优先复用已有文件；确需触碰 `AGENTS.md`、跨阶段 Boot、发布权限、全局审核/授权语义等**范围外的承重规则**时停止并说明唯一必要决议。禁止修改 Core master、旧测试候选 v1/v2、PR #34、任何 NBA 文件、存档或 Native 进程。
- 同样不允许在实现时静默改变冻结测试/工程候选预期；必要修订须由 Human/GPT 裁决，不交给 Codex 自己降低标准。
- 真实权限、场景、资源锁、Native CAS 与副作用 UNKNOWN 仍由原领域所有者管理；此工程不激活任何业务侧副作用。

## 4. 不要再做的事

- 不要第四次检查旧 G2 的三项缺失材料；这是**上游正式冻结门的已知事实**，不是当前候选实施的 Ready。
- 不要求独立审核模型交接，不再重新讨论 A0/A/B，不创建新需求任务、全量探索或临时审批系统。
- 不用虚假的 `frozen:true`、`freeze_authorization_ref`、Stage07 PASS 来绕过正式结构规则。
- 不借效率目标设固定倒计时、跳过安全前提或在 UNKNOWN 状态重放副作用。
- 没有实际改变决策行为时，不以 README、单元测试数量、文档或单纯引用 PR23 作为候选 Done。

## 5. 交付到 Human/GPT

一次性提供：`branch / head / changed paths / 实际接入入口 / T01,T02,T09 before-after / T01–T14 结果及既有回归 / 实测与不可测边界 / 剩余唯一 blocker`。

**可用既有工具自动提交普通 task branch；仅 Human 可批准受保护 master 集成。** 无需等待新的独立审核窗口。该交付仍是工程候选，Human/GPT 合并裁决后才进入后续独立授权的 GE-01 类实机对照。
