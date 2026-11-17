# Core PR #37 · R1/R2整改后独立工程审核交付

**岗位：** independent_review（须是与开发会话隔离的新模型端点）  
**对象：** Core PR #37；代码固定测试提交 `a527cc7f4a96356310635530b45bfabcc24ee5a2`；本交付文档的后续提交不改变这个已测试源码。  
**权限：** 只读、独立检查；不得修改代码、刷新测试标准、启动任何 NBA 游戏操作或合并 master。

## 固定需要审什么

**R1 / HIGH 原问题：** `Prototype.procedure=()` 可进入编译，Human 看不到真正步骤。
- 阅读 `01_os/06_execution/task_orchestration/reviewed_prototypes.py`，检查 `compile_approved` 对叶节点是否要求实际 `ProcedureStep` 或固定文档 `procedure_ref`；原型摘要是否覆盖引用；Host 能力目录是否与原型引用完全匹配；父任务能否使用已审核子节点避免无谓步骤展开。
- 负例：原型没有任何步骤或引用，但即便有一个测试版 `HumanReview(accepted=True)` 也不得执行。
- 正例：确实绑定的 `ProcedureStep` 可执行；成熟工具已有操作说明无需每轮展开。此代码不自动证明文档是真正被 Human 看过。

**R2 / HIGH 原问题：** 可选日志故障阻断合法业务。
- 阅读 `execution_mode_gateway.py` 的 `_record`、`audit_faults`、`on_audit_fault`，以及 `test_execution_decision_audit.py` 的相关反例。
- 正例：可选审计异常只提醒一次，不阻断已授权操作，不泄露日志路径敏感详情；业务授权和真实 Done 仍成立。
- 负例：领域真实写入权限拒绝，不能因审计故障放开；原有安全 Journal 与 Outbox 等领域责任并未被统一审计替代。

**R4 / MEDIUM 实际边界：**
- `prms_review_lookup.py` 的 `PRMSReviewLookup` 匹配原型 key/digest、任务 scope、Run 中精确的批准记录和源文件 SHA256，还依赖 Host 核对 Human 来源。
- 测试 `test_prms_review_lookup.py` 的正例来自 **合成审批 fixture**，不是 Human 的真实逐项批准。
- 实际 Run 的 `HUMAN_DECISION_MODE_SEPARATION.md` 为架构批准，测试必须证明该文档**不会**被转换为具体原型 `HumanReview`。
- **不能**把 R4 宣告为真实 Human 原型端到端 PASS；真实首个原型审核尚未发生，也不能凭开发者编写 `accepted=True` 伪造完成。

**R3 与测试范围：** 全域 Shell/GUI 拦截仍不存在；Human 已裁决采用信任优先与 Agent 自报，全面沙箱不是普通任务前置。报告代码层正反例，不要声称捕获了真实 Claude/Codex 所有动作。

## 施工侧验证事实（不等于独立审核）

- 授权 Windows 隔离 worktree，git 固定源码 commit `a527cc7f4a96356310635530b45bfabcc24ee5a2`。
- `python -B -m pytest 01_os/06_execution/task_orchestration -q --disable-warnings --maxfail=1`。
- 结果：**171 passed, 8 subtests passed，进程退出码 0**。
- 本次尚无完整七阶段回归 PASS；测试夹具的模拟 HumanReview 不构成真实 Human 审批事实。

## 独立审核应交付

`PASS / PASS_WITH_GAPS / FAIL`（对已实现源码行为、R1/R2 高优缺陷与 R4 真实边界分别说明），每项给出固定文件/函数及直接证据，不直接复述开发者总结。明确是否仍有影响主目标或不可接受的逻辑错误。独立审核的结论与 Human 对 master 集成的授权彼此独立。

**外部审核尝试：** Claude 凭据过期、Codex Windows 只读命令被策略阻断，均无有效结论；详见 [INDEPENDENT_REVIEW_ATTEMPT.md](INDEPENDENT_REVIEW_ATTEMPT.md)。\n\n**当前状态：** R1/R2 开发侧整改与本机测试 PASS；R4 读取机制开发侧测试 PASS，真实 Human 原型审批案例尚无；整体尚未 independent_review PASS，也未获 master 合并授权。
