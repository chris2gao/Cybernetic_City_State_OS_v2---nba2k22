# NBA2K22 · BIC Wave1/Wave2 子 A 确认绑定与 Stage 01 正式准入预备任务

## 1. 岗位、授权与完成目标

**任务 ID**：`NBA2K22-BIC-W1-W2-CHILD-A-BIND-STAGE01-ADMISSION-20261105-001`  
**领域**：Cybernetic City-State OS / NBA2K22 Basketball Intelligence Core  
**执行岗位 / 模型**：`execution / Codex`  
**协调 / 证据审核**：`decision_architecture / GPT-6`  
**Human 新裁决**：子 A0 v1 与子 A v1 已经过**分别、真实的 Human 确认**。现仅授权在离线子 Run 中绑定子 A 的固定 Human 记录、更新哈希/依赖并运行真实适用校验、准备正式 Stage01 owner 决策包。不自动授权 Stage01/02–07 `complete`、正式 Stage04 冻结或 `master` 合并。

**最终目标**：将 Stage01 的**双 Human 需求确认来源**绑定成合法一致的已提交证据，使真实 Core `requirement_findings` 返回 `[]`；在仍缺正式阶段 owner 授权时，停在 `PENDING_STAGE01_OWNER_ACCEPTANCE`，一次性提交下一层 owner 决策材料。不要以双需求确认替代 Stage01 plan/completion 接受或后续阶段完成门。

## 2. 固定仓库、来源和签收依据

正式 NBA 仓库：`chris2gao/Cybernetic_City_State_OS_v2---nba2k22`  
Core 仓库：`chris2gao/Cybernetic_City_State_OS_v2---core`

- 子 Run 固定交付候选：`b96fab3684e39062f073abac5e83a930d485ed62`
- 子 Run 开发分支：`task/nba2k22-bic-wave1-wave2-offline-scoped-run-20261105`
- 既有子 Run 目录：`01_os/07_content/_runs/run-20261105-nba2k22-bic-wave1-wave2-offline-subscope-001/`
- 固定 Core master：`08d8e534a3438269aa7d7eb1b080ab11c172f462`
- **子 A0 已批准**：模型 `NBA2K22-BIC-W1-W2-OFFLINE-A0-001`、v1，`normalized_sha256=908827305fd94f67a902e79830f08bebaea5f26dc0aade073f5fe647748a46c9`
- A0 原始批准 Git ref：`7428864602f7d29ee9620db36b7b975f3e2b70c8:01_os/07_content/_runs/run-20261105-nba2k22-bic-scoped-a0-human-confirmation-001/HUMAN_CHILD_A0_CONFIRMATION_20261105.json`
- **子 A 已批准**：模型 `NBA2K22-BIC-W1-W2-OFFLINE-A-001`、v1，固定 Core `requirement_confirmation_digest=693fede10af802267f3657a4f961b812252449d3ebfc1135527f64b88afe2fda`
- **子 A 的新 Human 独立批准 Git ref**：`21fda5b02926e3c720ad127843ba4e9a0ce256c3:01_os/07_content/_runs/run-20261105-nba2k22-bic-scoped-child-a-human-confirmation-001/HUMAN_CHILD_A_CONFIRMATION_20261105.json`
- 子 A 确认前 GPT-6 审核报告：`97cfb4af1439bf4fd55e31a7f33c76cbb175e1df`，路径 `01_os/07_content/_runs/run-20261105-nba2k22-bic-child-a-owner-review-001/CHILD_A_OWNER_ADMISSION_HUMAN_REPORT.md`。

Human 最新原话（精确裁决，不得重新解释）：

> 批准子 A v1：NBA2K22-BIC-W1-W2-OFFLINE-A-001，固定 Core requirement_confirmation_digest SHA-256 为 693fede10af802267f3657a4f961b812252449d3ebfc1135527f64b88afe2fda。确认七项 OFF-SC 对应 OFF-RES01–07、OFF-Q01–07 及覆盖矩阵。原完整 BIC 父任务保持未完成。不授权 Stage01–07 自动通过、Stage04 正式冻结、master 合并或真实游戏/Native 写入。

子 A0 与子 A 是**两条不同的 Human 决定和 Git 记录**，不可使用同一 `confirmation_ref`。

## 3. 本次执行顺序

### A. 准备与固定核对

1. 检查本机 NBA/Core 两仓实际 HEAD、工作区干净度、远端和分支关系。独立工程分支上操作，不更改 `master`。若分支已经前进，核对后在合法分支中应用最小增量，避免覆盖其他提交。
2. 固定 Git 读取上述子 A0、子 A 两份 Human 原始 JSON，以及上一子 Run `01_requirement.yml`、`NORMALIZED_BINDINGS.json`、`A0_BINDING_INTEGRITY.json`、`ACCEPTANCE_MATRIX.json`。
3. 验证两份记录的原话、模型、版本、原始来源及 SHA，原文副本应与 Git 原始 blob 一致。禁止以人工重写确认或自造签名取代原记录。
4. 使用固定 Core `normalized_sha256(consensus_A0)` 与 `requirement_confirmation_digest(payload)` 计算；**在尚未修改旧 A 的确认字段之前**，它们必须分别恰好等于 `908827...48a46c9` 与 `693f...afe2fda`。如果不匹配，保留阻断并呈报差异；不能反向修改 Human 已批准摘要。

### B. 绑定真实子 A Human 批准

1. 保留 `consensus_Human_confirmation` 的原始 A0 `confirmed=true` 及精确 A0 `confirmation_ref`。
2. 保留 `requirement_result_A.consensus_ref` 与已签收 A0 的绑定。
3. 将 `payload.Human_confirmation` 更新为 `confirmed=true`，`model_kind=requirement_result_A`、正确 `model_id`、版本和**批准的原 Core digest 不变**。
4. 将新 `Human_confirmation.confirmation_ref` 填入可不可变地指向新 Human JSON 的 `commit:path`；与 A0 引用必须不同。
5. 用 `git show` 读取该 ref，与存入子 Run `sources/` 的原始副本逐字节比较并记录 Git blob、SHA-256、来源提交和路径。
6. 不修改七项 `OFF-SC` 原文、`OFF-RES`、`OFF-Q`、任何父 BIC A0/A v2、或两批已审核业务源码和代码测试。

### C. 传播真实 Artifact 和 manifest 哈希

修改 Stage01 `01_requirement.yml` 后，其文件 SHA-256 必然改变。按已有 `manifest.yml` 真实依赖顺序重新计算 Stage01–07 的 SHA-256、上游 `input_refs` 和相关 manifest/运行引用；任何受影响的候选验证资料需注明旧数据绑定的固定版本与新版本的区别，不能原地抹除真实历史。

保留 stage control：
- 原 `status=candidate_pending_owner_acceptance`，除非另有**实际** owner plan/completion 历史才可改变。
- `stage_control.plan_acceptance`、`completion_acceptance`、`action_id` 不得从双 Human 需求确认伪造。
- Stage04 `frozen=false` 且正式冻结引用仍为空；Stage06 `attempts=[]`；Stage07 `completion=false`。

### D. 真实 Core 适用校验与逐项停门

使用固定 Core 文件实际运行：

- `requirement_findings(payload, 1)`：在两份 Human 记录及 SHA/ref 全部匹配之后，**预期为 `[]`**。若出现其他 finding，用真实原因整改，不伪造。
- `evidence_findings(stage02_payload, requirement_payload)`：预期 `[]`；这是材料结构/来源检查，不是 Stage02 owner 的 plan/completion 接受。
- Stage01–07 当前候选必填字段、类型、manifest/input_ref hashes、七项覆盖交叉映射、正负测试清单及来源一致性，应全部校验。
- 旧 `65 passed` 只可作为历史工程测试，不代表正式 Stage04 owner 冻结后的新子 Run 执行证据。
- **完整 Core `validate`** 只应对实际满足合法 owner/stage-control/history 先决条件的已提交 Run 运行；现阶段若仍未满足，记录 `NOT_RUN_PENDING_STAGE01_OWNER_ACCEPTANCE`，不重复制造已知拒绝。

保存固定测试候选 SHA、实际命令、退出码、stdout/stderr、精确结果和哈希。可复用既有受控 `managed_verify`，不要因此造新的状态仓或重复大回归。

### E. 最终 owner 决策包与停止点

将 Stage01 双 Human 需求确认记录和适用 Core 源码检查完成的事实，与**尚未发生的正式阶段接受**区分开。根据真实 Core Workflow/Stage 控制合同，形成一个 `STAGE01_OWNER_ADMISSION_PACKAGE.json`，列明需要 Human/合法 owner 作出的 plan/completion 接受、stage control 以及任何必要前序/历史依赖，不先填写其批准值。

最终交付：
- 实际工作分支和固定新 Git SHA；
- 两份 Human 原始 Git ref、子 Run 副本及完整 SHA/Blob 绑定；
- 确定的子 A0 和子 A 两个固定规范化摘要；
- 七阶段依赖清单、manifest 和真实 Core 阶段检查回执；
- owner 待决事项清单、受控测试原始日志与恢复 `CHECKPOINT.json`；
- `STAGE01_OWNER_ADMISSION_HANDOFF.md`：只提出下一项真正的 owner 决策，不拆成重复微型任务。
- PRMS 能合法保存时按现有机制执行；否则写 `NOT_SAVED`，以 Git Run 恢复。

**停止点：`PENDING_STAGE01_OWNER_ACCEPTANCE`**，不得自称正式 Stage01/完整 Run 已通过。

## 4. 不变的禁止范围

不修改父 BIC 的 Human A0/A v2、源码数值和已审核 Wave1/Wave2 业务逻辑；不补造授权或历史签名；不合并/推进 `master`；不执行 NBA2K22 游戏进程、存档、日历或 Native/REA Getter/Setter；不自动进入 Stage02–07 的正式 owner 完成门、Stage04 正式冻结、Stage06 真实操作或 Stage07 独立验收；不开展 Wave3 新业务开发。

普通绑定、哈希、文档和离线校验工作用**一次内部 Loop 连续完成**，不要每完成一个普通字段就要求新的 Human 许可。
