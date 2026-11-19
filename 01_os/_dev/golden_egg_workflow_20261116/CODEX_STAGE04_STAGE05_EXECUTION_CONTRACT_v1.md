# Codex 执行任务合同 · Core OS 金蛋执行链 Stage04 → Stage05（2026-11-16）

**角色：** `execution / Codex`。**当前授权阶段：** 读取、核验候选测试、复用现有证据并准备唯一准确的冻结/实施前置缺口说明；**不是**已经获批的测试冻结、生产源码修改或受保护分支合并授权。

**正式目标：** 在保留现有七阶段、安全边界和独立审核要求的前提下，让 Workflow 在实际执行时优先推动 Human 的真实 Goal/Done，避免重复 Ready、重建已批准分组以及关键阻断检查过晚；在条件满足后，最小化改造 Stage05–07，后续以 NBA2K22 受控对照观察效率改善。不要把本合同误解为“重新开发 OS”。

## 0. 唯一入口与固定版本（先读后执行；不要先做全库搜索）

Core repo: `https://github.com/chris2gao/Cybernetic_City_State_OS_v2---core`

Handoff branch: `task/core-golden-egg-workflow-stage04-handoff-20261116`

Read exactly this pinned handoff commit before doing anything else: `b07eb3c2ec4c0900f82e8eb3aca031fe805b2d92`

- `01_os/_dev/golden_egg_workflow_20261116/OS_CORE_GOLDEN_EGG_STAGE04_TEST_CANDIDATE_v1.yml`
- `01_os/_dev/golden_egg_workflow_20261116/OS_CORE_GOLDEN_EGG_MINIMUM_ENGINEERING_SCOPE_v1.md`

Important pinned refs:
- Core baseline `043ac4864bdc871b03929faafd8bc6bd47d4ee2f`; verify fresh actual master before proposing a diff.
- PR #23 Draft reference: `6d97d2d3e2527f38e688998e9b8de03553046dbe`, with `01_os/06_execution/task_orchestration/atomic_tasks.py` and `test_atomic_tasks.py`; never claim merged.
- PR #34 separate fact monitor candidate: `f82d7d49b1c0673cbcc965f8474fd73baf15a8d9`; do not reimplement.
- NBA GE-01 evidence: `https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/issues/46`; private raw source `C:/Users/gk/Documents/ChatGPT/nba2k22/ge46-monitored-20261116/`, especially `events.jsonl` and `WORKFLOW_BEHAVIOR_AUDIT.md`. Raw events never go to public GitHub.

Do not conflate the above **candidate handoff** with a canonical seven-stage `04_tests.yml`; status is explicitly `CANDIDATE_NOT_FROZEN`.

## 1. Human 已决定什么，尚未决定什么

**Human 已确认：** A0方向、单独确认完整需求A-v1、进入结果模型B和测试设计；目标是**正确性、安全性 + 实际业务结果 + 执行路径和耗时效率**。工作链：A0 → A → evidence → B → independent evidence-based tests → bounded implementation → actual Done。Human 明确要求 GitHub 直接交接，避免本地文件转发和无根据的再规划。

**A-v1 的结果边界：**
- RES-01：最小 Ready 与决定性阻断优先；
- RES-02：既有证据、权限及已批准业务选择的局部复用/精确失效；
- RES-03：保持 Action 稳定；辅助工作须有新的实质收益；
- RES-04：业务 Done 独立真实验证；Loop 局部纠错；时间质量分开报告；
- RES-05：最小融入既有七阶段，不新建一套 OS。
10 个成功标准 `SC-01..SC-10` 的实测映射已在候选 YAML 中，不能代入自行创造的成功定义。

**B-v1 是候选方案，不是已证实实现：** 复用 PR #23 的 `T=(Goal,Ready,Action,Done)` 语义，Stage05 映射业务节点与依赖，Stage06 选择就绪高价值 Action/低成本关键阻断核验、局部失效与保留批准分组，Stage07 验证真实 Done 与时间证据；无新阶段/审批器/监控/通用调度器。

**尚无正式授权：** 该聊天版本 A/B 尚未登记为完整 canonical Stage01–03 committed artifacts，候选测试尚无独立测试充分性结论、Human 冻结批准引用及 Core runner 的 normalized hash。你的自审不能冒充独立审核或 Human freeze receipt。任何 Native Setter/Calendar/saves/master merge 都不在此任务授权内。

## 2. G/R/A/D 执行链

### G1 · 固定源与缺口核验

R：上述固定 GitHub 文件可以读取；本地私有 GE-01 证据只有在精确验证必要时读取。

A：
1. 读两文件，核对 T01–T15（8 P0、4 P1、3 P2）与 `SC-01..SC-10` 的覆盖和来源；避免重复爬取仓库历史。
2. 只读对照当前 Core Stage04 schema (`01_os/01_workflow/04_测试生成/实现/最小运行schema_v1.yml`)、七阶段 runner、PR #23 当前参考测试及 PR #34 的实际发布状态。
3. 逐项区分 `VERIFIED_EXISTING`、`GAP_NEEDS_CHANGE`、`UNKNOWN`；测试充分性评价必须区分“执行者预检查”和“真正独立审核”。
4. 特别检查候选测试对真实源证据的归因。测试 T13/T14 必须保留工具调用、执行项、墙钟/UNKNOWN 的口径区别。T15 是将来授权后真实对照，绝不可用 synthetic fixture 宣称已通过。

D：一份紧凑缺口表，准确标出 Core 已有能力、应改的最少机制与正式测试冻结必缺的**唯一或少量真实前置**。在证据充分时不要扩展另一次大型研究。

### G2 · Stage04 正式冻结门（不得伪造）

R：Stage01–03 的精确正式产物和绑定、由 B 作者之外的测试语义充分性判断，以及当前 Human 对冻结的实际确认，均按照 Core 正式规则成立。

A：条件全部满足时，使用 Core 原有 runner 形成带证据 refs、`freeze_authorization_ref` 和正确 normalized `test_package_sha256` 的正式 Stage04 包；保留冻结前内容与变更理由。没有这些条件时，**不得**填造 `frozen: true`、Human confirmation、完整 Stage04 PASS 或“测试已冻结”。

D：若条件满足，报告冻结版本、确切 SHA、审查来源与 runner 结果；否则输出**一次**精确的 missing-gate 说明，停止正式冻结，不继续重复取源/制造附件。阶段04预检查和有限的非正式离线验证可在允许范围内完成，但不能以这些顶替正式冻结。

### G3 · 满足正式冻结后才激活的最小工程实现

R：G2 正式冻结成立、适用的 Core implementation task/allowed paths 和 Human 受保护动作授权已明确；现有开发角色允许进入工程阶段。

A：
1. 优先复用 PR #23 的最小语义与既有 Stage05/06/07，先跑未修改的基线测试，写最小失败反例，特别是 T01/T02/T09。
2. Stage05 只补真实业务节点/依赖/局部失效约定；Stage06 使 Ready/关键阻断优先与已批准 Action 稳定性在实际决策中生效；Stage07 真实 Done 与时间质量报告采用现有来源。所有变化须能被测试观察，而非仅新增 README。
3. 保留现有冻结测试、独立 review、写入 allowlist、权限、UNKNOWN 不重放；一般业务优化不产生新 Human 微审批。
4. 本阶段只在当前实施任务授权边界内提交 task branch 和证据；不要重写 Core OS、引入新调度器或无限回归。T15 放到后续真正获批的 NBA2K22 对照测试。

D：准确的 changed paths、测试输入/输出、未通过项、真实 Done 观察与审查就绪状态；不能以通过合成测试宣称游戏业务成功。

## 3. 禁止事项

- 禁止修 NBA2K22 Calendar / 执行游戏 Native 写入、模拟、存档操作。
- 禁止建立新监控器、Dashboard、泛化 Agent scheduler、审批平台、反复 PRMS/Issue 或每节点 Git receipt。
- 禁止修改冻结测试来迎合实现、伪造 Human 决定、自行宣称独立审核通过。
- 禁止未获批准合并 master、强推、改写 Git 历史；不得借“效率”跳过授权或安全门。
- 禁止先复述所有研究材料、重新扫描整个仓库或写无关的大量讨论文档；以两份固定文件和局部源码为主。
- 不将 GE-01 私有日志、游戏数据、用户名/本地路径敏感细节上传公开仓库。GitHub 仅可放脱敏、可核验的索引与结论。

## 4. 执行效率与汇报

你正在协助纠正历史上 **54 分钟、零完成研究闭环** 的高准备成本问题。当前也应遵循：
- 尽早指出关键 blocker，不因未知而循环取源；
- 只检查与当前动作依赖的资料；
- 已知成功的工具路径优先；失败换源必须有新信息；
- 不把纯时间间隔自动解释成模型思考，也不把已执行工具 duration 直接当作墙钟；
- 新发现不影响当前任务边界时不要重新生成原方案；
- 完成一次 G1 只读定位或遇真实 G2 冻结门，即给出明确结论，不用“准备工作”无限延期。

**交付格式（一次性汇总，不铺陈扫描日志）：**
1. 固定 Core 版本、分支、已读文件 blob SHA；
2. 15项测试覆盖和有证据的问题（简明）；
3. `READY_TO_FREEZE` / `BLOCKED_BY_MISSING_FORMAL_APPROVAL_OR_ARTIFACT` 等真实状态；
4. 若能工程执行，列出具体最小改动、测试输出与候选 commit；否则写“需要 Human 的唯一具体下一动作”，并在此停止。

以上是给 Codex 的实际任务合同，不是自动批准正式冻结或下游工程的 Human 签名。