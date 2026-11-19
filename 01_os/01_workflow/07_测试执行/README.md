# 07 · 测试执行

跑测试，判定通过与否。

## 核心机制

**测试环境与执行机制。** 同样用 skill 与工具完成——需要时搭测试环境，
**机制简单有效即可**。

## 输入 / 输出

- 输入：实现、冻结的测试
- 输出：测试结果，喂回阶段五的循环

## 审核不只是看灯

**审核实例核的是实现对 B 与证据，不只是"套件是不是绿的"。**

只读测试结果的审核会退化成确认一盏灯亮着，而阶段六已经说明为什么这不够：
实现可以满足测试的字面而不满足意图，且不需要碰任何测试。

## 角色约束

审核由**独立实例**做（a 或 b），不由执行实例（e）自审。

**一条复用限制**：a 可以定义需求并在之后审核实现是否满足它——需求方本就是恰当的验收方。
但 **a 不能同时产出 B**，否则它在审自己的推导。

## 审核结论与阶段完成值（Human 决定 2026-11-18）

审核者只写一套结论：全 OS 统一的审核结论 `PASS / FIX_REQUIRED / REJECT`
（`03_mechanisms/minimum_work_unit_output/最小工作单元输出契约_v1.yml` 的
`independent_review_machine_floor.verdict_allowed_values`），写在 07 产物 payload 的
`review_verdict`。本阶段的完成值 `verdict` 由它推导，不另作判断：

| 审核结论 `review_verdict` | findings | 阶段完成值 `verdict` | 去向 |
|---|---|---|---|
| `PASS` | 无 | `PASS` | 可完成 |
| `PASS` | 只有非阻断项 | `PASS_WITH_NON_BLOCKING_NOTES` | 可完成，非阻断项随完成记录保留 |
| `FIX_REQUIRED` | 有阻断项 | 不能完成 | 回阶段五循环：重试或上游失效 |
| `REJECT` | — | 不能完成 | 上游失效或 Human 裁决 |

审核时同时核对两件事（最近 workflow 改动的要求）：真实业务 Done 是否出现，以及执行轨迹中的
操作是否来自批准计划（`03_mechanisms/task_orchestration/最小任务原型与执行编译契约_v1.md` §4）。
阶段协同推演 `状态转换与不变量契约_v1.yml` 的 SD-09 `review_state` 中，`pass` 与
`pass_with_nonblocking_notes` 对应审核结论 `PASS`，`fail` 对应 `FIX_REQUIRED` 或 `REJECT`。

runner 在 payload 带 `review_verdict` 时检查：取值必须在统一词表内，且只有 `PASS` 能让阶段完成；
不带该字段的历史 run 仍按原规则读取，不追溯改写。

## 完成

全部步骤执行完毕、全部测试通过，工作流终止。

**没有单独的验收阶段。** 再加一个等于暗示测试不充分，那样的话缺陷在测试里。

## 最小运行状态

`实现/最小运行schema_v1.yml` 与统一 runner 已实现 reviewer/executor 分离、冻结测试结果全集、
实现主张到 B 与证据的绑定、上游失效和完成判定。只有 `PASS` 或
`PASS_WITH_NON_BLOCKING_NOTES`、全部冻结测试通过且无上游失效时，闭环才能完成。

独立审核的判断本身仍由独立模型或 Human 作出；runner 只验证审核包的结构、身份分离和引用闭合。

金蛋工程候选另外以领域父Done观察和 `business-time-quality` 报告实际结果与时间质量。
工具返回、子步骤通过和duration算术和均不替代真实业务结果；未观测时间不归因为模型思考。
T01–T14工程检查与后续另行授权的T15实机效果对照分开交付，SC-10保持待验证。
该候选入口不改本阶段正式冻结全集、审核角色或签收要求。
