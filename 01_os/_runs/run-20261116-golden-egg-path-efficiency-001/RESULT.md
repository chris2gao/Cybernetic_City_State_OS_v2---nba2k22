# 金蛋 Workflow 最小工程候选

任务：`OS-CORE-GOLDEN-EGG-PATH-EFFICIENCY-CANDIDATE-20261116`。
状态：工程候选完成，等待当前 Human 指定的 Human/GPT 集中复核。
`candidate_ready_for_independent_review` 是既有 lifecycle 枚举，不表示已独立验收，
也不恢复本任务已取消的单独审核模型交接。

固定输入来自 `a3c4c1b7a80d22300a4644933c8689f423c61807` 的 v2 合同、A0/A/B 记录、
测试候选 v2；精确入口见 `task_packet.yml`。工程分支
`task/core-golden-egg-path-efficiency-20261116`，基于实际核对的 master
`043ac4864bdc871b03929faafd8bc6bd47d4ee2f`。
PR23 `6d97d2d3e2527f38e688998e9b8de03553046dbe` 仅复用有限依赖、独立 Done、
UNKNOWN 不重放的设计约束，未合并 Draft 或建立第二套 Atom/Chain/Executor。

## 实际改变

既有 `run_minimum_operational_loop.py` 增加两个显式 CLI 路径：

- `next-business-action`：按有效性绑定局部失效事实；在满足 Ready/依赖的候选中优先决定性
  preflight，再选业务和可选准备；保留批准的业务矩阵；UNKNOWN/未确认尝试要求领域
  reconciliation；受阻节点不会遮住无关安全节点；父 Done 必须有独立观察。
- `business-time-quality`：只汇总既有报告；区分记录层级、duration 算术和、来源报告的
  ON 区间、事件跨度；缺失计数/耗时为 null，唯一工具墙钟与未观测归因保持未知。
  时间结果不改变动作权限与 Done。

Stage05/06/07 的既有 README 仅连接这条候选路径，原冻结、摘要与角色保护未改。
源码修改只在既有 runner 中；没有新增 scheduler、monitor、审批或 workflow 阶段。

## 可复算的真实任务接入

```text
python -B 01_os/_runs/run-20261116-golden-egg-path-efficiency-001/exercise_task_path.py
```

调用链：本任务 `engineering_task_decision.json` → 既有 runner 的
`next-business-action` CLI → `next_business_action` → 选择 `engineering`
（先于可选文案）→ 从 `verification_plan.json` 解析同名 check → 实际启动该 Python 检查。
不是只检查返回值：子进程确实运行测试，输出和真实退出码进入 managed verification 日志。
`exercise_task_path.py` 只用于本任务一次有界实证，不循环、不重试、不任意派发业务动作。

`actual_decision_result.json` 是提交前该路径的实际回执；其中 UTC 起止时间是该子进程的
调用跨度，unittest 报告的测试时间是另一口径，不作为整个模型工作时间。
最终提交上的完整复验由同一 `verification_plan.json` 驱动，结果在本地外部 Attempt 中。

## 反例前后与适用范围

`test_business_decisions.py --before` 是明确标识的朴素错误策略，三个断言分别失败：
T01 仍选择 `local_show` 而不是 `reachable_source`；T02 把已批准 target 55 改为 56；
T09 选择 `allocator_ui` 而不是 `fixture_check`。这不是宣称旧 Core 曾自动执行 NBA 动作。
仅三项全部按断言失败、无运行错误时返回预期退出码 1；后续用相同断言测试候选策略。
没有修改固定 v2 测试输入或降低预期。

| 测试 | 工程结果与边界 |
| --- | --- |
| T01 | PASS；已知不可用对象不再选取；新 fetch 观察允许重试。before 为断言 FAIL。 |
| T02 | PASS；20 行 UID/field/before/target 在 PID/worldline 变化后不变，拒绝不同 proposed choice。before FAIL。 |
| T03 | PASS；仅失效 PID 绑定观察，静态来源与批准决定复用。 |
| T04 | PASS，离线选择；缺 exact setter authority 的动作受阻，现有只读授权不外推。无真实权限发放。 |
| T05 | PASS；UNKNOWN 资源与未确认尝试不自动重放，无关安全步骤可继续。持久 journal/readback 仍归领域。 |
| T06 | PASS；子 Done 不证明父 Done，独立父观察才可完成。 |
| T07 | PASS，fixture 层；Final 199–202 与 Pending 假设冲突先阻断，无 Native dispatch、未改 Calendar。 |
| T08 | PASS；直接运行既有 unfrozen/digest drift/reviewer separation 三个负例。未伪造正式冻结。 |
| T09 | PASS；安全检查已可用且身份/权限具备的场景先查 fixture，失败后停止受影响准备。before FAIL。 |
| T10 | PASS，选择层；已知本地可用优先于不可用远端，已尝试未确认 probe 不重放。 |
| T11 | PASS，选择层；复用同范围只读授权；停止的 Computer Use 不会选中。未实际调用 CU。 |
| T12 | PASS；局部 diagnostic 可做一次，记录 attempted 后停止；不创建修复平台。 |
| T13 | PASS；104 个执行项、177 条分层记录，MCP 28.0956785 秒；ON 2761.724 秒仅为来源报告区间。未知墙钟/归因不猜测。 |
| T14 | PASS；事件至 blocker 2522.492 秒、采集结束至 blocker 989.254684 秒；没有据此放宽安全条件。 |
| T15 | NOT_RUN；另行授权的 NBA 实机对照，父研究验收仍未完成。 |

提交前诊断结果：19 项工程检查通过（含 T01–T14、实际 CLI、固定输入 hash、依赖优先级、
缺失绑定、未知时间处理）；既有相关 Core 回归 **53 passed, 161 subtests passed**，
pytest 测量 **569.34 秒**。上次被中断窗口的回归终态未保留，不计为一次通过；本次重跑
的 stdout/stderr 已完整保存。回归 check 的超时由 300 改为 1200 秒，依据这次实际
运行时间；命令、断言、预期退出码不变。

固定候选验证入口：

```text
python -B 01_os/06_execution/task_discipline/managed_verification/managed_verify.py run --repo-root . --candidate <this-commit> --plan 01_os/_runs/run-20261116-golden-egg-path-efficiency-001/verification_plan.json --attempt <external-evidence-parent/new-attempt>
python -B 01_os/06_execution/task_discipline/managed_verification/managed_verify.py inspect --repo-root . --candidate <same-commit> --plan 01_os/_runs/run-20261116-golden-egg-path-efficiency-001/verification_plan.json --attempt <same-attempt>
```

四个必需 check：`before_counterexamples`（预期 1）、`engineering`（0）、
`actual_decision_path`（0）、`core_regression`（0）。本地完整诊断日志与最终 Attempt
位于 `C:/Users/gk/.codex/tmp/golden-egg-20261116/`，不将原始本地日志或解释器路径发布为公共证据。
固定输入 YAML SHA256：`9b871027c2a5898b429e0ee1f900c9c1ebd169f8c91643ecb91f64811ac51b43`。

## 剩余缺口

这是显式 opt-in 的工程候选；没有部署为所有模型或领域任务的强制决策门。
模型/领域必须提供真实的优先级、事实依赖、最小权限和父 Done 观察；该函数不认证
Human 身份、事实来源真伪或签名，也不会自动发现哪条检查是决定性的。
journal、资源预留、CAS、真实副作用和跨重启 reconciliation 仍由领域原实现负责。
这些测试证明给定离线场景中的选择行为与既有保护未退化，不证明 NBA 当前实机兼容性、
正式 Stage04/Stage07 验收或整个 OS 已 operational。

工程交付后停止，交由 Human/GPT 集中复核。没有修改 master、PR34、NBA、游戏或存档。
