# Plan 3 External Augmentation OS 总体架构设计方案 v0.1

## 0\. 定位

Plan 3 External Augmentation OS 是 Cybernetic City-State OS 的外挂增强系统。

它不是试图把单个大模型训练成全能体，而是在大模型外部建立一个本地化、可回溯、可审计、可扩展的环境系统，为多个独立大模型提供：

* 持久记忆

* 上下文管理

* 文档化任务回溯

* Git / GitHub 协作通道

* 本地工具调用能力

* skill / app / MCP / terminal 能力接入

* Human Speaker 可读的简报与决策入口

* 长任务、短任务、规划任务、漂移恢复任务的执行规范

核心目标是：让模型升级带来的智能自然涌现，同时用 Human Speaker、边界、工具、文档和验证系统控制风险，而不是用过度规则束缚模型。

---

## 1\. 最高控制原则

### 1.1 Human Speaker 是绝对总线

Human Speaker 负责：

* 任务路由：判断任务进入 Engine A 还是 Engine B。

* 跨域转译：把知识判断转成工程任务。

* 最终裁判：处理冲突、争议、模糊语义、科学证据分歧。

* 授权门：批准 master/source push、runtime activation、Coordinator activation、destructive Git、secret-sensitive work。

AI 不得绕过 Human Speaker 自行改变任务目标、跨域裁决、激活 runtime、推 master、处理秘密材料或执行破坏性操作。

### 1.2 双引擎模型

Engine A：工业基建自动化引擎

* 范围：代码、程序、测试、重构、脚本、协议文档落地、确定性计算。

* 模式：规划 → 执行 → 验证 → 复盘。

* 代表工具：Codex、terminal、git、GitHub、测试脚本、静态检查、确定性计算工具。

Engine B：人类主持的元老院知识法庭

* 范围：医学、心理学、数学、哲学、认知科学、语义争议、跨学科含混问题。

* 模式：Human Speaker 主持，多个模型举证、反驳、合题，必要时调用外部事实核查。

* 原则：AI 不能把 Engine B 的知识裁决自动降格成 Engine A 的执行任务。

---

## 2\. 总体分层架构

### Layer 0：Constitution Layer / 宪法层

负责回答：这个系统为什么存在，谁有最终权力，AI 不能越过什么边界。

核心文件：

* 3号方案.md

* 06\_Silicon\_Index/AI\_Bootstrap\_Sequence.md

* 06\_Silicon\_Index/06\_Cybernetic\_Citizen\_Awakening.md

职责：

* 定义 Human Speaker。

* 定义 Engine A / Engine B。

* 定义 AI 公民的运行红线。

* 定义懒加载、反幻觉、验证优先、工具边界。

### Layer 1：Bootstrap Layer / 启动层

负责回答：一个新模型、新窗口、新 Codex 会话如何进入城邦。

核心文件：

* 06\_Silicon\_Index/AI\_Bootstrap\_Sequence.md

* README.md

* 06\_Silicon\_Index/README.md

* .ai/HANDOFF\_INIT\_PROMPT.md

职责：

* 不全量吞仓库。

* 先读任务。

* 判断 Engine A / Engine B / Human gate。

* 找到最小必要上下文。

* 识别当前任务是否需要 .ai handoff。

* 识别是否处于 context boundary / drift recovery。

### Layer 2：Context Memory Layer / 上下文记忆层

负责回答：长期任务、短任务、新窗口、漂移恢复如何通过文档找回上下文。

计划核心文件：

* 06\_Silicon\_Index/Context\_Memory\_System.md

建议内部分层：

L0：Current State Index

* 当前任务 ID

* 当前分支

* 当前 head

* 最新 handoff

* 最新 Human decision

* 当前 blocker

L1：Decision / Roadmap Memory

* 已接受的架构决策

* 已完成的 program

* 下一阶段 roadmap

* 重要分支和报告索引

L2：Evidence / Report Memory

* 完整 CODEX\_REPORTS

* diff audit

* validation ledger

* test results

* post-merge verification

* risk audit

职责：

* 让新模型不用读全仓库，也能通过索引恢复状态。

* 让长任务中断后可以回到最近可信 checkpoint。

* 让不可逆漂移后可以通过新窗口重新 bootstrap。

* 明确 ChatGPT 当前只能通过 GitHub 文档恢复，不具备 Codex 本地上下文记忆分支能力。

### Layer 3：Task Execution Layer / 任务执行层

负责回答：不同任务类型应该怎么执行、什么时候停、什么时候继续。

计划核心文件：

* 06\_Silicon\_Index/Task\_Type\_And\_Execution\_Model.md

任务类型：

* read\_only\_review

* planning\_task

* short\_goal\_task

* long\_run\_program

* implementation\_patch

* protocol\_patch

* merge\_publication

* drift\_recovery

* capability\_installation\_or\_tooling\_task

* engine\_b\_senate\_court\_task

核心规则：

* 默认 completion-preserving。

* Human 授权任务 A 后，不得拆成 A1 / A2 / A3 / A4。

* cleanup、validation、report、mailbox neutralization、post-verification 只要在授权范围内，就折叠进原任务。

* 只有新权限、目标变化、destructive Git、secret risk、runtime activation、Coordinator activation、master/source push 未授权等才触发 Human gate。

### Layer 4：Context Loading And Drift Recovery Layer / 按需加载与漂移恢复层

负责回答：什么时候加载什么文件；漂移后如何恢复；不可逆漂移后如何新窗口重置。

计划核心文件：

* 06\_Silicon\_Index/Context\_Loading\_And\_Drift\_Recovery.md

恢复模式：

1. Same-window fast path

* 连续 review loop。

* 只读最新 handoff、brief、report、changed files。

2. Context-boundary reload

* 新窗口。

* 先读 AI\_Bootstrap\_Sequence.md。

* 再读 .ai/HANDOFF\_INIT\_PROMPT.md 和 task-specific refs。

3. Drift recovery reload

* 发现协议漂移、任务碎片化、错误 base、错误分支、错误目标。

* 先承认 drift。

* 读取最近 accepted handoff 和 protocol。

* 合并回原始任务 A。

4. Irreversible drift new-window reset

* 当前窗口污染严重、上下文不可逆、模型反复 loop。

* 生成 L0/L1/L2 handoff。

* 新窗口从 bootstrap \+ handoff 重新加载。

5. Codex local memory branch recovery

* Codex 可用本地分支、worktree、Git log、reports 恢复执行上下文。

* 需要明确与 ChatGPT GitHub-only recovery 区分。

### Layer 5：Capability Registry Layer / 能力注册层

负责回答：模型外部有哪些工具、skill、app、terminal、MCP、Obsidian 通道，谁能用，何时能用，边界是什么。

计划核心文件：

* 06\_Silicon\_Index/Capability\_Registry.md

能力类别：

1. terminal\_shell

* 使用者：Codex。

* 用途：测试、脚本、确定性验证、本地文件操作。

* 风险：destructive command、secret leak、环境污染。

2. git\_github

* 使用者：Codex、ChatGPT GitHub Connector。

* 用途：分支、commit、push、handoff、review、模型间通信。

* 边界：no push –all、no force push、no unauthorized master/source push。

3. deterministic\_calculation

* 用途：数学计算、验证、统计、格式转换。

* 原则：模型不擅长确定性计算时，交给工具。

4. web\_search\_scrape

* 用途：最新资料、文献、网页采集。

* 边界：必须引用来源；高风险知识不可凭记忆。

5. obsidian\_human\_brief

* 目标：给 Human 发送长期简报、任务索引、决策备忘。

* 当前状态：planned / not yet implemented。

* 边界：不能把私人信息、secrets、未审查内容写入公开仓库。

6. app\_plugin\_mcp

* 用途：未来连接 Gmail、Slack、Drive、Figma、Linear、browser、MCP servers。

* 边界：需要明确授权和 auth scope。

7. domain\_specific\_skill

* 例：Firecrawl、PubMed search、Math verification、Code audit skill。

* 原则：skill 是外部增强，不是替代 Human Speaker 的权力。

8. runtime\_coordinator

* 状态：future / protected。

* 激活需要 Human explicit authorization。

---

## 3\. 推荐新增文件

本方案后续应通过一个 completion-preserving task 补齐以下文件：

1. 06\_Silicon\_Index/Plan3\_External\_Augmentation\_OS\_Architecture.md

* 总体架构总图。

* 定义 Plan 3 外挂增强系统的分层模型。

2. 06\_Silicon\_Index/Context\_Memory\_System.md

* 定义 L0/L1/L2 文档记忆层。

* 定义 GitHub / reports / mailbox / branch / handoff 的记忆职责。

3. 06\_Silicon\_Index/Task\_Type\_And\_Execution\_Model.md

* 定义短任务、长任务、规划任务、merge publication、drift recovery、Engine B 法庭任务等类型。

4. 06\_Silicon\_Index/Context\_Loading\_And\_Drift\_Recovery.md

* 定义按需加载、漂移检测、恢复、新窗口重置、Codex 本地记忆分支和 ChatGPT GitHub recovery。

5. 06\_Silicon\_Index/Capability\_Registry.md

* 定义 terminal、GitHub、Obsidian、skill、app、MCP、deterministic calculation、runtime/coordinator 等能力状态和边界。

---

## 4\. 当前系统符合度评估

当前系统已经具备：

* Plan 3 宪法层

* Human Speaker 权力模型

* Engine A / Engine B 路由

* AI\_Bootstrap\_Sequence 启动入口

* .ai handoff / mailbox 协议

* long-run / completion-preserving 执行规则

* GitHub 文档化协作路径

* 部分 skill / script 原型

当前系统缺少：

* 统一 Context Memory System

* 统一 Task Type Index

* 统一 Context Loading / Drift Recovery Runbook

* 统一 Capability Registry

* Obsidian human brief 通道设计

* Codex local context memory branch 规范

* ChatGPT GitHub-only recovery 规范

* 工具能力 implemented/planned/forbidden 状态表

总体判断：

Plan 3 OS v0.1 已经成立为文档化控制层；下一阶段目标应是 Plan 3 External Augmentation OS v0.2，补齐 context memory、task taxonomy、drift recovery、capability registry 四大控制面。