# Core OS · Human 逐项审核的最小任务原型（候选 v0.1）

**状态：CANDIDATE / NOT HUMAN APPROVED / NOT INTEGRATED / NO LIVE EXECUTION.**
本次只实现一个可选择使用的桥接层，不修改既有七阶段 Workflow，不接管 PR #23 的 Executor、PR #35 的业务节点选择器，也不触碰 NBA2K22 T15/Issue #46（保持关闭）。

## 目标与最小链

`Human 业务目标 → 大小任务 G/R/A/D → Human + AI 对每条 Ready/Done 与具体操作逐项讨论 → 固定并审核原型版本 → 对当次参数绑定已有能力 → PR23 Executor 运行 → 真实 Done → 有界 Loop`。

**原子性不是“几条底层命令”，而是已经具备可调用、已审阅、有独立 Done 的业务动作。** 一个已稳定的 WorldData 采集器内部可有数百个读取步骤；从外部研究 Loop 看应是一个 Atom，而不是让模型每轮重写胶水脚本。

### 当前模块

- [reviewed_prototypes.py](reviewed_prototypes.py) 提供 `Criterion / Operation / Prototype / HumanReview / Capability`、`review_packet`、`compile_approved`。
- [test_reviewed_prototypes.py](test_reviewed_prototypes.py) 是离线行为测试（不会操作游戏）。
- **预览时** `review_packet` 输出每个大/小节点的 Goal、每项 Ready、每项 Done、原因 `why`、来源 `basis`、已有操作的能力 ID、版本、副作用和参数、子节点，以及稳定 digest，状态始终 `PENDING_HUMAN_REVIEW`。
- **Human 审核时** 可以删除、合并或修改过度 Ready/Done/操作步骤；每次变更重新生成 digest，旧批准不能复用。审阅每个子任务也会因父任务摘要变化而触发父任务版本复核。
- **编译时** 由可信 Host 注入真实 `review_lookup`（Human 决策存储），`capabilities`（现有函数注册表），`read_fact`（真实环境事实读取），当次 `bindings`（存档、日期等）。原型从不自我批准。未审、不同摘要、版本不匹配、缺参数都拒绝编译；不会自动写脚本或补能力。
- **执行时** 返回**已有** `atomic_tasks.Executor`，且没有自动调用 `advance`。每个 Action 只会调用绑定的已存在能力；Ready 与 Done 均交给可信领域事实，Done 不由执行器返回码推断。WRITE 还要额外经过每次实例的外部授权接口，且在真正调用前重新检查。

### Human 应审核的“采集任务”实例草案（未批准）

此处 **不是**当前 NBA WorldData 能力的已核实调用签名；以下是需要 Human 与开发模型共同对照现有代码、讨论每一步的设计实例，禁止复制为直接游戏指令。

| 节点 | 候选最小内容 | 为什么需要，以及 Human 要裁决什么 |
| --- | --- | --- |
| Goal | 采集指定范围的真实 WorldData | 确定数据范围，避免模型自行追加全量重采 |
| Ready-1 | 当前数据源/世界线绑定有效 | 是否与现有采集函数内部检查重复？应该保留在哪一层？ |
| Ready-2 | 指定来源可读 | 现有采集器是否已能一次处理来源失败并给出回执？若是，不需要模型独立重复探测 |
| Action | 调用现有只读采集能力（固定入口/版本/参数）**一次** | Human 检查是否还有临时写胶水、手动逐源调用、重新验证相同事实 |
| Done-1 | 返回本次来源/范围的真实收据 | 需哪些最低字段才代表完成，而非仅脚本 exit 0 |
| Done-2（待讨论） | 必要数据完整性校验 | 是否已有采集器自动完成？不应让模型再对全部数据做无差别复采 |
| 异常 | 已知的可复用恢复，或 `INCOMPLETE + reason + Human option` | 阻断一个 Action 不等于宣布整个父任务完成或永久终止 |

Human 需要逐项确认/删改，并明确该原型能复用多少次、哪些环境变化要求版本重审。**Human 审核是设计把关，不自动等同于具体 Native 写入/模拟授权**。

### Loop 与执行边界

1. **开发 Loop**：尚无可用能力时，先在受控开发任务中研究与实现新函数，经过 Human 审阅原型再进入复用；正常执行实例不允许自行升级为“写新脚本”。
2. **执行 Loop**：在审核通过的原型与版本范围内，按绑定能力运行，使用真实事实更新 Ready/Done；同一原型不同日期/存档可重复实例化。
3. **研究 Loop**：根据已采集成果提出下一轮业务目标/参数；不自动扩张之前批准的副作用与任务边界。
4. **例外**：能力不兼容、原型前置假设错误、真实授权缺失时，停止受影响 Action，返回未完成原因和最小 Human 选择；重新审阅**变化的原型节点**而不是反复展开所有工具。

### 范围与局限（必须清楚）

- 此候选模块**不是**全局工具安全沙箱，不能拦截不走此入口的模型 shell/Frida/操作系统调用。只有被实际 Host 接入后才对该 Host 的执行路径生效。
- `HumanReview` 是 Host **从可信记录提供**的引用而不是密码学签名；仅靠模型构造同名对象或填写 `accepted=True` 不构成 Human 审核。生产接入必须由不可由代理写入的审批存储确认真实操作者身份和摘要。
- `read_fact` / `Capability.invoke` 需由领域层可靠实现，尤其是证据来源、时效、世界线和重启后的 Outbox UNKNOWN。此模块没有凭空获得游戏安全性。
- 当前只支持单个已存在 callable 作为一个叶节点 Action，复杂的确定性子步骤应封装在既有能力里；不新增调度、日志服务或审批平台。
- 未在本轮核实 NBA 的真实采集 API 函数签名，也没有使用此候选运行游戏、自动化脚本或任何受保护写入。
- 执行机 Desktop Commander 当前离线；只有源码/测试文件提交到候选分支，**本机实测结果未验证**。不得标为 PASS 或已集成。

## 第一轮 Human 设计评审重点

请先讨论并确认：（1）真实采集操作是否已拥有稳定的一键入口，缺什么；（2）哪些检查属于采集器内部，不应由 Agent 重做；（3）哪几个最小 Ready/Done 对业务实际必要；（4）哪些异常允许实例内重试，哪些必须问 Human；（5）批准后同类型实例的复用边界。其余大/小任务后续可复用同样的审查方式，无须重复造一套 OS。

**当前验收门：`HUMAN_PROTOTYPE_REVIEW_PENDING`。** 已有候选代码不等于 Human 完成了最小条件裁决，也不等于新 Core 行为已全局启用。
