# BIC Wave1 + Wave2 · OS 准入闭环与集成候选预检查

**领域**：NBA2K22 / Basketball Intelligence Core / Cybernetic City-State OS  
**任务 ID**：`NBA2K22-BIC-W1-W2-OS-INTEGRATION-READINESS-20261105-001`  
**来源**：Human 已确认继续下一步；第一批与第二批离线工程通过 GPT-6 系列代码审核。  
**执行岗位/模型**：`execution / Codex`（独立、离线）；规划和独立系列审核 `decision_architecture / GPT-6`。  
**本次授权**：准备阶段证据、运行实际离线验证、创建并测试**独立集成候选分支**。**不授权**真实 NBA2K22 游戏/Native 写入，不授权 `master` 合并、PR 自动合并、批准 Human 阶段门，或更改已确认需求的语义。  
**任务完成模式**：一个连续内部 Loop；允许分支内持续研究→修正→测试→检查点，完成两个工作流后统一交接。一个独立门受阻不影响另一独立安全工作流。

## 0 · 固定证据与当前远端事实

| 对象 | 固定 SHA / 版本 | 状态 |
|---|---|---|
| NBA `master` | `66f8f73f1a91597f4562b834c2acad332ad9de5b` | 截至 2026-11-05 核验 |
| Core `master` | `08d8e534a3438269aa7d7eb1b080ab11c172f462` | 截至 2026-11-05 核验 |
| Wave1 已审核代码 | `aec3dbaacd1d56b0c7cc1d40c2f70607493b9a4b` | 离线代码审核 PASS |
| Wave2 已审核代码 | `cdcb293f8a690725cf9168225cc2046ab0574b2b` | 离线代码审核 PASS |
| Wave1 审核凭证 | `3f27b421e0c1813dbfb890c4583c97e76dfd6f98` | 独立审核分支 |
| Wave2 审核凭证 | `13414798d5992336e28ae1df7e14bf17fbae6a04` | 独立审核分支 |
| Human 确认的 A v2 Git blob | `e16fdf6c4ef69b0a90b8c4abd3856617030a7ae4` | 需求语义已确认 |
| Stage01 准入候选脚本分支 | `task/nba2k22-bic-stage01-canonical-normalization-20261104` | 已发布、未有真实 Core PASS |
| 阶段 02–05 候选分支 | `task/nba2k22-bic-batch1-stage02-05-evidence-model-20261104` | 候选，不是正式批准 |
| P0 固定交付 | `17bca5c5e34a4bc3b153c38634681962e1600ec7` | 已完成，不重做 |

远端比较：`NBA master → Wave2` 为 **ahead 8、behind 0、83 文件变更**；`Wave1 → Wave2` 为 **ahead 3、behind 0**。列表中未发现 `.sqlite/.db/.zip/.bak` 等大归档文件路径，但必须在实际候选目录检查大小和 Git diff；该事实不能代替完整数据治理检查。

固定预检查文件：本 Run `PRECHECK.json`。

## 1 · 工作流 A：正式 OS 证据与阶段合同闭环

此处不能通过制造“PASS JSON”解决阻断。任务是**生成真实可校验的阶段产物并运行真实 Core 校验**，并且正确区分 BIC 全量需求和已交付的 Wave1/Wave2 局部范围。

### A1 · Stage 01 Human 双确认规范化

1. 在单独的规范化/验收工作分支运行已发布的 `stage01_canonicalize_v1.py`，核对原始 `A0 v1 / A v2` 四个固定 Git blob、两个 Human 确认原始凭证；不可修改已批准原件。
2. 使用当前 Core 固定 SHA 的 PyYAML `safe_dump(...,allow_unicode=True,sort_keys=True,width=4096)` 和 `normalized_sha256` 计算规范化 A0 与 A 摘要。要求实际运行 `requirement_findings`，保存运行命令、退出码、源码 SHA 和完整结果。
3. 维护每个私有 `evidence_status` 的无损原值与保守 Core 枚举映射；严禁把 Human 报告的观察、MyPLAYER 研究或 Native 假设升级为 `live_effect_verified`。
4. **关键身份门**：旧 Human 只批准了固定 JSON Git blob。新规范化 A payload 的内容摘要不是旧 Git blob 摘要；必须用字段级等价映射证明仅发生机器表示变换。Core 结构验收不能凭空认证 Human 对变换文本的再次授权。如存在承重语义变化，仅将变化项提交 Human 裁决。
5. 补齐可实际被 Core 接受的 `01_requirement.yml`、run manifest、deliberation/stage control 和真实批准映射；不伪造 Human 签名、未发生的阶段完成回执。

**Core runner 真实 CLI**（命令中的 Core/NBA 根目录和 Run 路径以本机真实环境为准）：
```powershell
python -B -X utf8 <CORE_REPO>/01_os/06_execution/workflow/minimum_operational_loop/run_minimum_operational_loop.py static <CORE_REPO> --json-output
python -B -X utf8 <CORE_REPO>/01_os/06_execution/workflow/minimum_operational_loop/run_minimum_operational_loop.py validate <NBA_REPO>/<RUN_RELATIVE_PATH> --repo-root <NBA_REPO> --candidate <EXACT_COMMITTED_CANDIDATE_SHA> --json-output
```
实际 `validate` 是**完整已提交 Run + 发布历史门**，不是只有 Stage01 的单文件格式检查。必须有真正可检查的完整 Run 才能调用作为正式完成门；若缺 predecessor/owner authorization，记录精确阻断，不要把单文件静态检查叫 Stage01/七阶段 PASS。

### A2 · Stage02–05 阶段候选规范化与裁定

优先复用已完成的 12 个来源、9 条证据判断、Stage03 B v2 六项结果、Stage04 15 个测试候选和 Stage05 七步候选；结合已存在的 Wave1/Wave2 实际代码、65 项相关测试归档和两份独立审核凭证，形成唯一且具版本的证明链。

- Stage02：标明静态源码已验证、历史读取实际报告以及 `UNBOUND/REAL_DATA_NOT_VERIFIED` 限制。缺乏 MyLEAGUE XP/3D 效果认证**不是**普通离线源码已通过的反证。
- Stage03：结果 B 应准确对应已交付 Wave1/Wave2 的**局部能力**；完整 BIC 的 SC-05（BIC-vs-BIC 对抗）以及尚未实现的竞争目标不得标记为已满足。
- Stage04：为实际已授权的离线工程范围建立冻结测试包与来源摘要，区分**先前实跑**（41、65 项记录）、旧合成预检查与**正式冻结后的**测试，不得将未冻结前的运行记录当作冻结后动态结果。
- Stage05：以已经交付的真实模块和依赖填写步骤、结果/测试对应关系，保存源码修改边界、迭代记录、性能限制与停止门。
- Stage06/07：只就 Wave1/Wave2 *离线成果子范围* 组织候选实现/验收证据；不把完整 BIC 目标的 Stage06/07 偷渡为 PASS。若 Core 标准不支持部分 Run，提议合法的子 Run/增量架构并说明原 Run 的仍未完成状态，不能自行改变 OS 合同。

若 OS owner 必须由 Human 做新的**实质性阶段确认**，仅准确列出该项；其他材料应继续完成，不得因它再次全线 `blocked`。

### A3 · 正式验收运行与原始回执

对实际已提交的候选 Run 执行官方 CLI；保存准确 SHA、exit code、findings、相关 schema/validator commit、发布/历史门结果。若运行器拒绝完整 Run，写成 `NOT_PASSED:<exact blocker>`，**不要假 PASS，也不要进入无收益的反复重试**。

## 2 · 工作流 B：两批工程独立集成候选（不改 master）

**该工作流可与 A 并行**，绝不能仅因 Stage01 尚待正式门就停止安全的离线集成预检查。

1. 在当前固定 `master` 上新建独立集成候选分支，建议 `task/nba2k22-bic-wave1-wave2-integration-candidate-20261105`。检查本机 `master` 及远端，如较本预检查有新提交，更新 ancestry 和冲突结论。
2. 对当前两批工程提交链运行 `git merge-base --is-ancestor <CURRENT_MASTER_SHA> cdcb293f8a690725cf9168225cc2046ab0574b2b` 和 `git diff --stat --name-status`。若 master 仍是祖先，**仅在独立集成候选分支**执行 `git merge --ff-only cdcb293f8a690725cf9168225cc2046ab0574b2b`；绝不可对 `master` 做 FF 或 merge。否则编制冲突报告与最小化迁移候选，不直接覆盖新版 master。
3. 确认已包含 Wave1 和 Wave2 的实际代码、测试、固定历史回执和无大型历史数据库文件。检查 DB/schema/迁移脚本不能误删；不重新追溯全部 WorldData。
4. 两份独立审核报告**位于独立审核分支**，应以精确 refs 关联到集成候选的交付 manifest；如需把审核回执复制到新分支，必须只作内容相同的文档增量，保留原 SHA、来源和回执，不冒充工程作者签名，不自动合并审核分支的其他历史。
5. 在集成候选分支运行与本版本一致的 BIC 相关 `65` 项测试或等价超集；检查 `bic_cli.py` 与 `bic_wave2_cli.py` 的离线调用和旧 `query_at` 隔离；保留实际命令、退出码、环境、耗时和原始日志。不得为了集成随意改核心数值/诊断逻辑；若需要修改，先形成变更清单并标记须补充代码审核。
6. 检查大文件（SQL schema/migration/小夹具保留、历史 SQLite/备份不进远端）和源文件哈希，编写 `INTEGRATION_CANDIDATE_REPORT.json`、`INTEGRATION_DIFF.md`、`RUN_REPRODUCIBILITY.md`。

**当前集成状态只可标记**：`INTEGRATION_CANDIDATE_TESTED` 或 `INTEGRATION_CANDIDATE_BLOCKED_WITH_EVIDENCE`；是否批准正式合并需要另一个可复核的 Human 决定。

## 3 · 连续内部 Loop、最终交付及停止门

工作流 A/B 中的普通格式错误、缺少测试/文档、引用不一致、阶段性 UNKNOWN，使用内部 Loop 修复和留痕；**不要每一个增量重新请求 Human 或 GPT**。不可伪造已有 Human 确认、Core 正式 PASS、Native 实机验证或把仍未实现的全量 BIC 功能说成完成。

**最终交付应同时包含**：

- A：Stage01 正规化来源/摘要/绑定/实际 Core 回执，Stage02–05 的阶段材料及 Stage06–07 子范围标注；完整 OS gate 列表、真实剩余障碍。
- B：独立集成候选的固定 HEAD、包含两批代码的证据、相关回归、改动/大文件/许可证等安全检查、可复核的集成差异及非合并状态。
- 两条线分别有 PRMS/Git Run 恢复检查点，PRMS 不可用则明确记录 `NOT_SAVED`。
- 一份交给 GPT-6 的 `GOVERNANCE_AND_INTEGRATION_HANDOFF.md`，逐项明确 `DONE / PENDING_HUMAN / UNKNOWN / BLOCKED_WITH_REASON`；提供精确文件链接和 commit。

完成后停止在**候选交付和审核检查点**，不提交 master 合并、不操作 NBA2K22、不扩大到第三批篮球业务开发。
