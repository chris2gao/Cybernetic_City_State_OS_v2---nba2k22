# OS-PRMS 工程交接

状态：**PARTIAL_ENGINEERING_HANDOFF_PENDING_EXTERNAL_ACCEPTANCE**。本次交付可运行的工程候选；真实平台强制失权、真实 GPT/Codex 新窗口和独立审核尚未完成，不宣布 TASK_CLOSED、正式发布或生产可用。

代码验证候选：`65c42a1ba0a7b58d3e572ad739f58aa59b274300`。基线：`446ca66ad48831f5fcdb1af18f37d07619e048c4`。工程分支：`task/os-prms-implementation-20261029`；Draft [Core PR #10](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---core/pull/10)。后续交接证据提交与此代码候选分开标识；复验必须 checkout 此候选，不能把交接分支最新 HEAD 自动代入旧验证回执。

## 实际交付与证据

- D0：19 份具备固定来源指纹的主资料/补充资料已登记；规划 Run 的 A-RC01/false 陈旧指针由有效后继 Human 批准修复，NBA 规划分支远端提交为 `c58af42455c55bcb0fde668aee393b2b172f9ebe`，见 `planning_reconciliation.json`。
- D1：G1 真实树发现与 Registry 对账，G2 领域身份和发布记录核验、空目录脚手架、按需装配与实际正文回执。真实 PR18 源读出 13 个项目候选、0 个正式 G2；P04/P09 共 6 份正文核验成功。候选新增 PRMS Registry，因此基线 13 和候选 14 是不同版本快照。
- D2：真实隔离 Git 的原子 CURRENT、RoleDefinition/Instance/Assignment、只追加事件、检查点、源引用、版本/CAS、幂等操作记录及实际读回。GitHub Git Database 协议适配器默认禁写。
- D3：范围索引、来源摘录摘要、精确 stale、未知任务可见与合法终态闭合检查、任务系列恢复、K1 候选与已发布记录核验、实际字节全量复制及目标独立演化。
- D4：隔离会话能力、旧 owner 拒写、竞争 CURRENT、恢复包与 L0–L4 装配。L4 遍历冻结岗位所有可达提交并保存每个不同记录版本；上限或预算缺口返回 BLOCKED。直接 Git 绕过仍能成功，所以强制模式明确拒绝启用。
- D5：52 项 PRMS 离线测试、44 项既有 working-set 回归及其余受控检查通过；逐场景结果、失败历史、可复验命令和独立审核入口均已保存。Owner 自验不能代替独立审核。

`verification_receipt.json` 保留每个检查的实际结束记录和 stdout/stderr 字节摘要。原始 input 含本机运行信息，保留在任务外部日志目录；公布的是经筛选的结果。早先 24/41/50 项日志仅为历史检查点，不是最终候选证明。

48 场景逐项列在 `acceptance_results.json`，原始预期保留在 `acceptance_contract.json`，映射在 `acceptance_map.json`。当前统计：`{"PASS_AT_OFFLINE_SCOPE": 30, "PASS_PINNED_REAL_SOURCE_LOADING": 2, "NOT_RUN_REQUIRED_SCOPE": 12, "PASS_LOCAL_CROSS_REPO_FIXTURE": 3, "PASS_REMOTE_PLANNING_RECONCILIATION": 1}`。这些范围标签不可相加解释成完整产品验收。

## 20 项需求覆盖

| 需求 | 可消费行为 | 当前接受范围 |
|---|---|---|
| RES-001 | RoleDefinition registration and compatible version upgrade | PARTIAL_EXTERNAL_GATE |
| RES-002 | Stable RoleInstance identity | PARTIAL_EXTERNAL_GATE |
| RES-003 | RoleAssignment and task authority separation | PARTIAL_EXTERNAL_GATE |
| RES-004 | Single current session owner | PARTIAL_EXTERNAL_GATE |
| RES-005 | Git durable authority | PARTIAL_EXTERNAL_GATE |
| RES-006 | Append-only facts and Human decisions | PARTIAL_EXTERNAL_GATE |
| RES-007 | Current and checkpoint consistency | PARTIAL_EXTERNAL_GATE |
| RES-008 | Experience extraction and promotion candidate | VERIFIED_AT_DECLARED_ENGINEERING_SCOPE |
| RES-009 | Shared knowledge and publication governance | PARTIAL_EXTERNAL_GATE |
| RES-010 | Dynamic context assembly | PARTIAL_EXTERNAL_GATE |
| RES-011 | Adapters and new-window recovery | PARTIAL_EXTERNAL_GATE |
| RES-012 | Failure and retry semantics | PARTIAL_EXTERNAL_GATE |
| RES-013 | Core upgrade and domain integration | PARTIAL_EXTERNAL_GATE |
| RES-014 | End-to-end and independent acceptance | PARTIAL_EXTERNAL_GATE |
| RES-015 | Full content copy and independent target | VERIFIED_AT_DECLARED_ENGINEERING_SCOPE |
| RES-016 | Enforced takeover | PARTIAL_EXTERNAL_GATE |
| RES-017 | G1/G2/T1/T2/K1/K2 layers | PARTIAL_EXTERNAL_GATE |
| RES-018 | Source summaries and selective stale propagation | PARTIAL_EXTERNAL_GATE |
| RES-019 | Indexes and scoped retrieval | PARTIAL_EXTERNAL_GATE |
| RES-020 | L0-L4 Human selection and recovery receipts | PARTIAL_EXTERNAL_GATE |

详细实现位置、场景来源和剩余证明见 `requirements_coverage.json`。`current_checkpoint_writer_recovery_example.json` 是实际执行生成的合成隔离实例，包含 CURRENT、Checkpoint、WriterGate 拒写与恢复证明；不是 Core 活动岗位状态。`g1_g2_actual_catalog_and_loading_example.json` 是真实固定源目录与正文读取证明，未携带业务正文副本。全文可从其不可变来源重新读取。

## 独立复验

在独立检出中固定上述候选；先按现有 Core Boot 和本次任务包初始化。Python 3、Git、PyYAML、jsonschema、pytest 是离线先决条件；真实源读取还需要已有合法 `gh` 读取能力。不得为复验创建凭据、仓库或后台服务。

```text
git checkout 65c42a1ba0a7b58d3e572ad739f58aa59b274300
python -B 01_os/06_execution/task_discipline/managed_verification/managed_verify.py run --repo-root . --candidate 65c42a1ba0a7b58d3e572ad739f58aa59b274300 --plan 01_os/_runs/run-20261029-os-prms-implementation-001/verification_plan.json --attempt <existing-external-parent/new-attempt>
python -B 01_os/06_execution/task_discipline/managed_verification/managed_verify.py inspect --repo-root . --candidate 65c42a1ba0a7b58d3e572ad739f58aa59b274300 --plan 01_os/_runs/run-20261029-os-prms-implementation-001/verification_plan.json --attempt <same-attempt>
```

每次使用全新 attempt。`acceptance.py` 的零退出码表示其离线测试和逐场景核销执行成功；JSON 明示 `all_original_acceptance_passed: false`。默认审核装配不注入 Owner 叙事，但 Q22=C 的开放读取风险仍在，无法凭目录隔离保证审核者未看过本报告。

## 剩余门与下一步

1. Human 选择并另行授权独立状态仓库、信任域和有效 ref；受控入口须由独立主体掌握写权限，模型无直接有效状态写凭据。当前未创建真实状态仓库，也未实现或启用生产认证入口。
2. 在授权环境验证实际 GitHub CAS、部分上传、结果未知、旧/只读会话直接 REST 和 Git ref 写入拒绝。平台管理员越权边界必须披露。当前 `FENCING_NOT_ENFORCEABLE`，不得宣称强制接管。
3. 工程交付后由 Human 安排真实 GPT/Codex 新窗口，使用冻结真值核对身份、任务、Human 决定、来源、预算、遗漏及续作边界。隔离 Python 进程并不替代这些窗口。
4. 独立模型/会话审核此精确代码候选和原始 A/B，再由 Human 决定 Core/master 集成及逐领域更新。当前未进行这些受保护操作。

未运行游戏或 REA，未创建生产凭据或服务，未向 Core/master 或领域 master 合并。未跟踪的 5 张图片已按 Human 本次明确许可从原 Core 工作树删除。pytest 遗留共享链接仍未删除；工程检查使用独立临时目录避开它，失败证据原样保留在外部 attempt。
