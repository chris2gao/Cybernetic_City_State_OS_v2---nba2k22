# Core PR #37 · 正式 Human 设计审核交付包

**日期：2026-11-17** · **审核对象：整个 Core OS 通用机制，不是 NBA2K22 采集任务**  
**PR：** https://github.com/chris2gao/Cybernetic_City_State_OS_v2---core/pull/37  
**代码基线（本次审查读回）：** `13085112a792ef1247dd7925c411bc1cb7a33d81`  
**状态：HUMAN_DESIGN_REVIEW_PACKET_DELIVERED / NOT_FINAL_ACCEPTANCE。**

## 0. 本包为什么出现

之前开发者多次称“等待 Human 审核、独立审核”，但没有实际交付**要审核的内容、判定依据和问题清单**。这是流程失误。本包是一个具体、可在聊天中逐项讨论的交付，而不是另一个要求 Human 审批准时报告的流程。

## 1. 已有 Human 共识，不应重复提请表决

1. Human + AI 逐项设计真实大/小任务原型的 Goal / 最小 Ready / 具体操作 / 最小 Done，首次共同审核、后续大量复用；
2. `EXECUTION` 与 `DEVELOPMENT` 分离，已授权的开发任务可编写/测试，执行中的能力缺口不可擅自升级为开发；
3. 被网关实际拒绝的请求可留结构化记录，重复异常可触发 Human 的模型–OS 适配性复盘；拒绝率并非自动处罚；
4. OS 信任 Agent 的诚实与纠错；不可见的偏差可以由 Agent 自报；自报不是 Host 观察到的拒绝；权限与工作纪律分离；
5. 不建立全域 Shell/GUI 监视、逐次工具批准、复杂身份安全平台或新的 Workflow 阶段；保留已有受保护操作权限。

这些已由 Human 在对话中明确确认，见本 Run 下三份 `HUMAN_DECISION_*.md`。**不要让 Human 再回答同样的问题。**

## 2. Human 实际应审核的对象（不是 24 个源码文件）

| 审核点 | 目前承诺的 OS 行为 | 人类判断标准 | 本次建议 |
| --- | --- | --- | --- |
| A 任务原型 | 首次与 Human 讨论每项必要条件及其操作细节，冻结后复用 | Human 真能看见“第 1 步做什么、为什么、哪个已有函数、可删哪些检查” | **应保留，不能只有四字段标题** |
| B 执行 Loop | 沿已审原型调用现有能力，根据真实 Done 推进；偏差时停止受影响动作 | 不因额外准备剥夺业务目标；重复执行不重新设计 | **已获共识** |
| C 诚信自报 | 即使 Host 无法看到，Agent 也应承认自己的额外操作与错误 | 自报应有事实、影响、纠正；不被当作违规处罚 | **已获共识** |
| D 权限 | 对真实 Native/发布/破坏性操作仍需独立权限 | 不因信任取消现实权限，也不借权限建立全面监督 | **已获共识** |
| E 审计负担 | 真实工具拒绝记录；正常运行尽可能轻量 | 不能因日志系统、统计或新回执让业务停止 | **按下面缺陷整改** |

## 3. 根据实际代码发现的明确问题（开发者自查，不冒充独立审核）

### R1 / HIGH：实际步骤明细仍可缺席

`reviewed_prototypes.Prototype.procedure` 默认空元组，`_nodes()` 不要求至少给出可审核的实际步骤；`review_packet()` 可以生成仅有 Goal/Ready/Done 和 callable ID 的审核包。**这不保证最初 Human 想审的“实际执行流程、各项检查为什么必要”一定呈现。**

**建议整改：** 首次建立新可复用原型时输出可讨论的 Procedure（工具内部/Host 单独步骤、原因、证据、复用条件）。不要求每次调用重新展开，也不能把每个 CPU/底层系统调用当成任务。允许已审成熟函数以其版本化操作说明作为精简引用；引用缺失要标出而不是默认“已审”。

### R2 / HIGH：审计落盘失败现在可能阻断正常业务

`execution_mode_gateway._record()` 在 `audit_sink` 抛错时将异常向上传播，先于工具调用；`test_execution_decision_audit.py::test_unavailable_durable_sink_prevents_admission_before_tool` 特意把这种行为写为预期。对于**普通只读或可重复的已批准操作**，仅因 JSONL 日志目录不存在就取消业务动作，和最新“信任优先、不制造额外前摇”的 Human 裁决矛盾。

**建议整改：** 业务执行的 Ready/Done 与可选观测日志分离。普通受授权操作的日志故障只应单次报告并继续；只有具体领域原本就强制的安全/交易 Journal/发布审计，才由原有权限规则决定是否阻断。Agent 自报日志从来不应成为执行门槛。

### R3 / MEDIUM：通用网关代码并未接管真实 Agent

`ExecutionModeGateway` 是一个可以被 Host 使用的 Python 入口；目前并无证据表明 Codex 或 Claude 的全部 Shell/GUI 请求已经走它。对本次 **信任优先** 的执行纪律，**全域 Host 接管不是 Human 的必备前置条件**；但不能把这份代码表述成已经完成全工具强制约束。

**建议处理：** 声明“已实现可调用参考层 + Agent 纪律”，生产路径可在具体高风险领域按已有授权逐步适配；不展开独立通用沙箱工程。

### R4 / MEDIUM：Human 审核来源尚未真正绑定现有 PRMS 决策

`compile_approved` 接收外部 `review_lookup`，测试由固定 `HumanReview(..., accepted=True)` 构建。它能验证摘要匹配，但尚不能证明从真实 Human 对话或既有 PRMS 读取了审批。**这不是请求用户每次验证身份，而是避免机器生成的默认值被误读为 Human 已讨论过。**

**建议处理：** 复用现有 Human 裁决记录链接、任务原型版本、审批范围；不创建新认证服务。可先在已有工作流中通过人工审定的文档实例做端到端案例。

### R5 / MEDIUM：验证范围不要虚报

此前 Windows 在固定源码 `1021bed9de29ab37c740734d455fb0db1b10ab8a` 上执行了 `161 passed, 8 subtests passed`，证明 `task_orchestration` 离线行为，不证明真实 Agent 行为、阶段 05→06 业务端到端复用，也不是独立审核。不得将通过次数直接等同于 OS 完成。

## 4. 审核如何结束，而不是无限待办

**Human 设计审核**：你只需要判断上面的 OS 行为是否符合你的工程意图；已批准原则不重问。建议按 R1、R2 的最小整改方案落实；R3、R4 保持范围清楚并以现有 PRMS 实例验证。不需要 Human 读源码。

**工程审查**：整改后由与开发者独立的模型针对 R1/R2 的反例、PR23 回归、模式转换、异常不盲重试、自报/网关记录分类、变更范围和实际 Git SHA 进行检查；明确 `PASS / PASS_WITH_GAPS / FAIL`。这是工程事实核验，不将结果偷换成 Human 业务裁决。

**是否合并 master**：必须以实际修订 SHA、测试和独立审核的结论，以及 Human 对集成的单独授权决定。当前 PR 维持 Draft，不把本审核包标记为最终验收。

**建议当前结论：设计方向已获得 Human 共识；实现检查存在 R1、R2 两项应修问题，正式独立审核与集成尚未完成。不要因此增加一个新系统级治理项目。**


## 5. 2026-11-17 工程整改补充（保留原始审核问题作为历史）

上述 R1/R2 是**修复前的确认问题**，不能把本原始交付包误读为当前源码仍未修。

- R1 已在 `reviewed_prototypes.py` 添加“实际步骤或与 Host 同版本一致的文档来源”编译门；没有操作明细的候选可以预览讨论但不能执行；相应反例通过。
- R2 已使可选审计故障只产生一次警告，普通已授权调用继续，领域独立安全许可仍有效；相应反例通过。
- PRMS 审核来源新增 `prms_review_lookup.py`：合成获批文件能运行正向编译，真实的 OS 架构 Human 裁决不能伪造成具体原型批准；**尚缺第一份真实 Human 逐项批准的具体原型**。
- 开发侧 Windows 离线测试源码固定 `fd6bac894ee2dc7fff2379ef8ca5c5af02753550`：171 passed、8 subtests passed、退出码 0；不是独立验收或生产 Agent E2E。
- 独立审核精确合同：[REMEDIATION_REVIEW_HANDOFF.md](REMEDIATION_REVIEW_HANDOFF.md)；此文件追加说明不代表 Human 对新代码自动批准。

**当前：** HIGH R1/R2 开发侧标记 `REMEDIATED_PENDING_INDEPENDENT_REVIEW`，R4 `PRMS_BINDER_TESTED_REAL_PROTO_APPROVAL_PENDING`，Core master 不变。
