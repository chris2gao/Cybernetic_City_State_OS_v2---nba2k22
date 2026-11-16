# 金蛋 F01/F02 集中整改

当前任务：`OS-CORE-GOLDEN-EGG-F01-F02-20261116`。在原实现分支继续，基于
`bd185822822543350e9d3c07a1174285b47b788d`；复核来源为
`cb61ee8b257e8a4d7291bc1ec3837ae5dc966a92:01_os/_dev/golden_egg_workflow_20261116/GPT_CODE_REVIEW_BD185822_20261116.md`。
本次只整改 F01/F02；下方原候选记录保留为历史，不当作本轮测试结果。

实现方法：只调整既有 `next_business_action()` 末尾的选择逻辑。Ready 的实际业务先执行；
无 Ready 业务时，只考虑未完成业务的明确 `depends_on` 前置链。已 Done 前置不再向下
展开；同 scope 或 diagnostic/preflight 标签本身不构成依赖。没有业务节点、任务本身是
必需检查时，仍允许检查；必需工作受阻时不自动选择无关 optional。独立必要业务/安全
动作仍需通过原授权、依赖、停止通道、UNKNOWN 与尝试记录检查。

支撑性：现有有限依赖图已经校验存在性与无环，本次复用它，没有新字段、规划器、
调度器、状态系统或权限机制。原 Ready 观察、批准矩阵、父 Done、时间统计与 CLI 接线
保持原实现。T03/T12 只补上真实前置关系，既有断言不变。

可行性与提交前实证：

- 先新增 F01/F02 负例。`--review-before` 直接加载固定旧提交的真实 runner，两个方法
  覆盖五个场景，得到 **5 个 AssertionError、0 个运行错误，退出 1**，符合负例预期；
  不是用另写的错误算法替代旧实现。原始日志已保存。
- 修改后快速检查 **24 tests OK，退出 0**；其中新增五个方法覆盖 F01/F02、传递前置链、
  局部排障与独立必要安全行动的保护。实际 CLI 选择并启动同一工程测试也 **退出 0**。
- AST 对照确认原 **19 个测试方法的断言全部未改**，T01/T02/T09 整个方法 AST 相同；
  原工程候选 v2 字节 SHA256 仍为 `9b871027c2a5898b429e0ee1f900c9c1ebd169f8c91643ecb91f64811ac51b43`。
- 提交前快速测试 unittest 时间 **3.988 秒**、外层调用 **5.022485 秒**；实际 CLI 练习
  外层调用 **4.488008 秒**。这些口径不等同模型推理时间或整个任务耗时。

最终固定提交按 `verification_plan.json` 运行 managed verification：原反例、旧提交
F01/F02 反例、当前工程检查、实际 CLI、**一次完整 Core 回归**，随后同候选 `inspect`。
完整回归在快速检查通过后集中运行；结果以外部、绑定本提交的 Attempt 为准，不预写 PASS。
完整原始证据目录：`C:/Users/gk/.codex/tmp/golden-egg-f01-f02-20261116/`。

当前候选继续依赖可信领域输入，不认证权限与事实；T15 仍 NOT_RUN。工程与必要验证结束后
停在 Human/GPT 对本次差异的复核边界，不代表正式 Stage04/Stage07 或 master 集成已批准。

本轮变更文件：既有 runner、其 README、本 Run 的 `test_business_decisions.py`、
`task_packet.yml`、`run.yml`、`verification_plan.json`、`RESULT.md`，无新增 Run 或平台。

## 原候选 bd185822 的历史记录

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

第一次 managed verification 对 `68a5da72fa894d6a8537e6cea35abc383efcd722`
在启动测试前拒绝：`candidate_outside_packet_allowlist`。原因是任务包使用目录尾 `/`，
而该验证器要求递归目录显式写成 `/**`。已按同一目录范围修正任务包，未改验证器、
测试预期或业务源码；该次拒绝不计入测试通过。

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
