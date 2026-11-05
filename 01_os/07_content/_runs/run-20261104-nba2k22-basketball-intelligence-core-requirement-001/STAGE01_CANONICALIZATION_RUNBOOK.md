# BIC Stage 01 · 规范化执行入口与真实状态

**任务类型**：已获 Human 双确认后的机器语义等价规范化。**仅需求 Stage01 产物处理，不授权篮球工程代码、Native 游戏操作或 master 合并。**

## 固定输入

- 已批准 A0/A v2 原始文档及两个独立 Human 批准凭证，全部固定在 NBA 源 commit `90d1801003e7a49531ef377137a2a975125bdd06`。
- A v2 的 Human 指定 Git blob：`e16fdf6c4ef69b0a90b8c4abd3856617030a7ae4`。源原件不改写。
- Core Stage01 最小运行器及有效的 `requirement_findings` 校验入口：`01_os/06_execution/workflow/minimum_operational_loop/run_minimum_operational_loop.py`，参考 Core master `08d8e534a3438269aa7d7eb1b080ab11c172f462`。

## 执行指令（在具备 NBA 和 Core 工作区的离线 Python 3.10+ 环境）

确认本地 Git 对象中存在以上 commit 和四个固定 blob；如未取得，仅执行**Git fetch 只读获取对象**，不得 rebase/merge/checkout 到 master。

```powershell
git -C <NBA_REPO> fetch origin task/nba2k22-basketball-intelligence-core-requirement-modeling-20261104
python -B -X utf8 <NBA_REPO>/01_os/07_content/_runs/run-20261104-nba2k22-basketball-intelligence-core-requirement-001/stage01_canonicalize_v1.py --repo-root <NBA_REPO> --core-root <CORE_REPO> --output-dir <NBA_REPO>/01_os/07_content/_runs/run-20261104-nba2k22-basketball-intelligence-core-requirement-001/_stage01_generated
```

依赖：PyYAML；测试工具不得联网、运行游戏、执行任何 Native 操作。若 Core 工具或所需 Git 对象缺失，精确记录缺项，不把无权操作转化为假的 PASS。

## 真实输出

1. `01_requirement_payload_CANDIDATE.yml`：来自获批 A0/A v2 的机器规范化 payload，包含实际确认引用、规范化 SHA-256、原文结果项及完整覆盖映射；**不是完整七阶段 `01_requirement.yml` 的已验收替代品**。
2. `stage01_normalization_report.json`：源码 blob/原始文件 SHA-256、规范化 A0/A digest、7 条非核心枚举的保守分类映射、实际 Core `requirement_findings` 结果、剩余外部阶段控制/确认绑定限制。
3. 真实命令/退出码，及对候选只读的来源校验。只有输出 `PAYLOAD_CORE_STAGE01_CHECK_PASS` 且 Core 的 `requirement_findings` 为空时，才可标记**payload 结构通过**。

转换要点：Human 报告的 3D 观察和徽章因果解释，原来的私有状态值统一**保守归类为 `candidate_inference` 并保留 `original_evidence_status`**，不可提升为 LiveEffectVerified。A0 源原件、A v2 Git blob 均不可更改。

## 剩余正式 Stage01 完成要求

此规范化工具不能生成已批准的 stage_control、完整 deliberation receipt、plan/completion acceptance 和 governed-run manifest。上述产物必须引用真实固定提交与真实验收源，由对应 OS 任务岗位审核，按相应 Core 机制完成适用阶段验证。

**Core `minimum_operational_loop validate` 是整个七阶段 Run 的提交态校验**；当 Stage 02–07 未具备时，其失败不是 Stage 01 内容失败，也不得凭 Stage01 payload 的规范化结果宣布七阶段全部通过。

本工具没有在用户本地环境执行，GitHub 发布只代表代码可执行候选已固定；后续正式验证必须报告真实机器退出码。
