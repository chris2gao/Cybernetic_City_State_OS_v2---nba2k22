# Core PR #37 · 首个真实 Human 审定 PRMS 只读原型执行证据

**日期：** 2026-11-17（America/Los_Angeles）  
**性质：** 实际 Human 对话批准 + Windows 隔离工作树实机 Python 运行。不是第二次独立审核，不是生产 Host 身份认证验收。  
**业务结果：** `LOCAL_READ_ONLY_E2E_PASS`；一次已有 PRMS 函数调用，真实 Git 数据读回，最小 Done 达成。

## 1. 审定对象与来源

- Human 原话：当前会话在明确展示 G/R/A/D 及具体调用后回复 **“批准”**。
- 原型：`core-prms-registry-read-v1`。
- 原型提案固定提交：`566e8ca493e0dd5f0b116ccc3f1cd2d86b84920b`；源文件 `FIRST_PRMS_PROTOTYPE_PROPOSAL.json`。
- 用 `reviewed_prototypes.digest` 重新计算的实际摘要：`5bbfdfd45e75b936933922620a81e0c55b645a212b380256447a5c28ba9ce501`（与先前提供给 Human 的摘要一致）。
- Human 对话批准的结构化来源：`HUMAN_PROTOTYPE_APPROVAL_20261117.md`，SHA256 `3dffd7930523fed0b98dd95666c110a0b5a5444cf318430c74d3b886719cf918`。
- 现有 PRMS 读取入口：`HUMAN_PROTOTYPE_REVIEWS.json`，含准确 key、digest、scope、批准来源文件与内容 SHA256。
- 本次审批文件/manifest 固定源提交：`99e4f188f87887a3ed402d59a42deda407ebc082`。
- 适用任务：`OS-CORE-HUMAN-REVIEWED-ATOMIC-PROTOTYPES-SYSTEM-UPGRADE-20261116-001`；不扩展为其他具体原型、Native 写入或 master 合并授权。

## 2. 实际隔离 Windows 执行

- Windows 设备：`DESKTOP-FPNE2NQ`；Python 3.14.6。
- 源码隔离工作树：`E:\workspace\_maintenance\core-pr37-validation`；`git rev-parse HEAD` 严格等于 `a527cc7f4a96356310635530b45bfabcc24ee5a2`，执行前工作树 `git status --porcelain` 为空。
- 从 GitHub 固定提交读取 **真实提案、Human 批准记录、审批清单**；校验 GitHub blob、原型摘要、Human 来源文件 SHA256。
- `PRMSReviewLookup` 的负例：来源回调明确拒绝 → 无 `HumanReview` → `compile_execution` 抛 `NeedsHumanReview`，业务函数 **0 次**。
- `PRMSReviewLookup` 的正例：基于**真实 Human 会话批准的已归档文件**核对 key、digest、scope、来源文件内容及来源 SHA；得到 `HumanReview`，并经 `ExecutionModeGateway.compile_execution` 编译。
- Host 本地预绑定 `Capability('prms.catalog.mapping', 'git-blob:4fc0cca559b658282ff45581f3395780801ba01c', 'READ_ONLY', ...)`，调用的业务函数始终是现有 `catalog.py::mapping`；没有新 PRMS 查询实现。
- `GitSource` 冻结到 `a527cc7f4a96356310635530b45bfabcc24ee5a2`，核对已有 `catalog.py` blob `4fc0cca559b658282ff45581f3395780801ba01c`、`source.py` blob `1cfde9fa42b6ea573c05f203119d5df280a30332` 和读取目标 `prms_v1.yml` blob `cb86266c06acf5c3251319427420708924e18e4f`。
- 真正业务动作执行 **恰好一次**；`READY → ADVANCED → DONE`，再观察 Done=true，不用函数退出码假冒 Done。网关事件：`DENIED:COMPILE`（预期负例）、`ADMITTED:COMPILE`、`ADMITTED:EXECUTE`。
- 实际得到 `registry_id=prms_v1`、`schema_version=citystate.registry.v1`、3 项真实注册条目：

  1. `01_os/03_mechanisms/context_management/prms/**`
  2. `01_os/06_execution/boot/context_management/prms/**`
  3. `01_os/05_registry/prms_v1.yml`

- GitSource 实际读回证据：repository `chris2gao/Cybernetic_City_State_OS_v2---core`，commit `a527cc7f4a96356310635530b45bfabcc24ee5a2`，path `01_os/05_registry/prms_v1.yml`，blob `cb86266c06acf5c3251319427420708924e18e4f`，SHA256 `2a2effe4355555714c507d3b04aa6b9bbf7f447696aa96fd0bf7b18a9468a75d`，1469 bytes。
- 本次本地一次性 Host 验证脚本仅用于执行验证，放在 **Core 工作树之外**，不纳入原型或作为新的 PRMS callable。

## 3. 同一固定源码上的重新执行测试

命令：

```powershell
python -B -m pytest "E:\workspace\_maintenance\core-pr37-validation\01_os\06_execution\task_orchestration" -q --disable-warnings --maxfail=1
```

结果：**171 passed, 8 subtests passed in 0.87s；退出码 0。**

此次 pytest 是执行推进端在真实 Windows 隔离工作树中重新运行，不应冒充独立 reviewer 重新执行；之前独立源码审核 `PASS_WITH_GAPS` 的原始界定仍保留。

## 4. R4 的准确结论

**已完成：** 首个真实 Human 对话批准；内容摘要与适用范围固定；审批文档与 SHA256 登记；真实 PRMSReviewLookup 正/负例；经 Gateway→编译→一次真实 callable→真实 Done 的离线本地闭环。

**仍未证明：** 可信 Host 独立认证 Human 对话来源的生产实现。此次 `verify_human_source` 是基于已归档内容的本地上下文校验，**由执行侧提供**，不是由独立 Host 从认证会话取得的身份证明；Agent 自存 Markdown/GitHub 文件不能自行授予真实性。因此报告状态是 `R4_FIRST_REAL_PROTOTYPE_E2E_PASS_HOST_IDENTITY_ATTESTATION_PENDING`，不能说生产身份门已关闭。

**不扩大范围：** Human 最新信任优先裁决仍有效。不因本次 Host 来源认证边界重新启动通用 Shell/GUI 监管、审批服务器或新 Workflow 阶段。真实 Agent 普遍工具强制覆盖仍为 `NOT_IMPLEMENTED`。

**保护范围：** PR #37 保持 Draft，Core master 未获合并许可。本次无 NBA、游戏或 Native 操作；无 Core Python 源码变更。
