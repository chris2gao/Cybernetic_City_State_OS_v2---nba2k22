# NBA2K22 BIC · 子 A0 Human 确认绑定与子 A 重新提交任务

**任务 ID**：`NBA2K22-BIC-W1-W2-CHILD-A0-BIND-AND-A-PREPARE-20261105-001`  
**执行岗位**：`execution`  
**执行模型**：Codex  
**规划/检查**：GPT-6 / `decision_architecture`  
**本任务授权**：已获 Human 正式确认的固定子 A0 v1 可用于建立真实确认绑定；允许离线 OS 文书/脚本修订、精确 Core 结构验证、Git 留痕。**不批准子 A、不批准七阶段完成、不授予正式 Stage04 冻结或 master/Native 权限。**

## 一、固定输入（不得重新讨论或重新开发）

仓库：`chris2gao/Cybernetic_City_State_OS_v2---nba2k22`

- 子 Run 工程候选：`a9a9a444907c6b35aa6bcd4da5c7f123cba522e9`
- 子 Run 目录：`01_os/07_content/_runs/run-20261105-nba2k22-bic-wave1-wave2-offline-subscope-001/`
- 固定 Core 源码：`08d8e534a3438269aa7d7eb1b080ab11c172f462`
- 已签收的**子 A0 模型**：`NBA2K22-BIC-W1-W2-OFFLINE-A0-001`，v1
- 子 A0 真正批准的固定 `normalized_sha256`：`908827305fd94f67a902e79830f08bebaea5f26dc0aade073f5fe647748a46c9`
- **Human 子 A0 确认持久化记录**：提交 `7428864602f7d29ee9620db36b7b975f3e2b70c8`，路径 `01_os/07_content/_runs/run-20261105-nba2k22-bic-scoped-a0-human-confirmation-001/HUMAN_CHILD_A0_CONFIRMATION_20261105.json`。
- 已发布的独立 owner 准入预审：`95d871848ae99e97393e34c66941b577bff86336`；其报告是技术预审，不是子 A 的 Human 批准或 Stage07 独立验收。

原始 Human 批准内容：`批准子 A0 v1：NBA2K22-BIC-W1-W2-OFFLINE-A0-001，固定规范化 SHA-256 为 908827305fd94f67a902e79830f08bebaea5f26dc0aade073f5fe647748a46c9。确认七项 OFF-SC 离线验收范围及排除边界；原完整 BIC 父任务保持未完成。不授权子 A、后续阶段自动通过、master 合并或真实游戏操作。`

继续在已存在的子 Run 工程分支 `task/nba2k22-bic-wave1-wave2-offline-scoped-run-20261105` 开发或使用单独的阶段绑定工作分支；先核对真正 HEAD 和未提交文件。**不要修改独立批准来源分支或 master**。引用已发布的确认记录，必要时只在子 Run 中添加准确来源引用，不改动 Human 原话。

## 二、精确更新子 A0 确认绑定

1. 从固定 Git ref 读取该 Human A0 记录，核验 `model_id`、`artifact_version=1`、`normalized_sha256`、七个 OFF-SC 和未授权边界。
2. 使用现行固定 Core `normalized_sha256` 对子 Run `01_requirement.yml` 内 `consensus_A0` 重新计算。**只有和 Human 批准值完全一致**，才能将 `payload.consensus_Human_confirmation` 标为 `confirmed=true`；否则保留阻断并说明字节/语义差异，不能改用户批准的 SHA 来凑匹配。
3. 将 `consensus_Human_confirmation.confirmation_ref` 填为可追溯到上述 Git **固定提交与路径**的真实、唯一引用（可使用 `sha:path` 或经 Core 认可的其它不含糊形式），保持 `model_kind=consensus_A0`、`model_id`、版本、digest 一致；明确这是当前 Human **子 A0 的一次真实批准**，不是整阶段的 plan/completion 接受。
4. 将该精确批准引用填入 `payload.requirement_result_A.consensus_ref.confirmation_ref`，其 `model_id`、`version`、`sha256` 同步匹配子 A0。
5. 保持 `payload.Human_confirmation.confirmed=false` 和 `confirmation_ref=null`。不得借用 A0 批准、父 A v2 或之前的路线批准填补子 A 的第二个独立 Human 确认。

## 三、重新计算子 A 摘要与传播阶段引用

固定 Core 的规则：

- `normalized_sha256(value)` 使用 `yaml.safe_dump(..., allow_unicode=True, sort_keys=True, width=4096)` 之后对 UTF-8 字节取 SHA-256。
- `requirement_confirmation_digest(payload)` 使用同一规则，对删去 `Human_confirmation` 和 `consensus_Human_confirmation` 两个字段后的完整 Requirement payload 求哈希。
- 因为子 A 的 `consensus_ref.confirmation_ref` 已变更，旧暂定子 A digest `c8184084a9229cedc67de04735a481d387f121561ea4e7be0de0592396ad5b93` **必须废弃**；写入实际新摘要及产生它的固定脚本/命令回执。

根据 `01_requirement.yml` 的变更，重新生成 `manifest.yml` 和所有受到上游 SHA 影响的 `input_refs`、阶段 Artifact 哈希、owner 候选包的来源引用与恢复文件。需避免遗漏由 Stage01 新 SHA 引起的传递更新；保留旧版本 Git 历史，不原地消灭此前提交过的证据。子 A0 内容、7 项 OFF-SC 原文、父 BIC A0/A v2、Wave1/Wave2 工程代码及历史测试材料不得改变。

**验证时的合理预期**：

- `requirement_findings(payload,1)` 不再返回 `stage1_confirmation_binding:consensus_A0`。
- 因为子 A 尚未获 Human 批准，预期应返回 `stage1_confirmation_binding:requirement_result_A`。若有别的错误，修复引用或结构问题，不伪造第二次批准。
- `evidence_findings` 仍应真实检验与更新后的 Requirement 对应，不声称 Stage02 owner 正式接受。
- 七阶段依旧为候选，`stage_control` 不得凭空填充，Stage04 保持 `frozen=false`，Stage06 不得伪造执行记录，Stage07 不得写完成。
- 正式完整 `validate` 仍未具备七阶段完成条件，除非确实存在合法 owner 接受和执行证据；避免在同一已知待决状态下反复调用完整门。

## 四、内部 Loop 与真实交付

使用单个内部 Loop 完成文件更新、Core 适用检查、规范化 SHA、Git/manifest 引用校验和文档更新。允许为新状态修订旧 `check_scoped_payloads.py` 的**预期阻断断言**，但不得把有意保留的子 A 未确认结果误标为完整 PASS。

交付：

- 固定新 Git SHA 和独立分支/Run 路径；
- Human A0 原始记录的精确固定 commit/path、规范化摘要与已绑定的 `consensus_ref`；
- **重新生成的子 A 固定规范化 SHA-256**、子 A 完整候选内容及七项覆盖清单；
- Core `requirement_findings` 和 `evidence_findings` 的真实执行回执及原始日志；
- Stage01 Artifact、manifest 和后续受影响 refs 的一致性报告；
- Git Run/PRMS 恢复检查点（未成功保存 PRMS 就写 `NOT_SAVED`）；
- 汇总给 GPT-6/Human 的 `CHILD_A_CONFIRMATION_HANDOFF.md`，**明确子 A 尚未确认**，只提交单一下一步 Human 决策。

完成时停在 `PENDING_CHILD_A_CONFIRMATION`。不要在未获得第二次 Human 决议前继续办理 Stage02–07 的 owner 正式接受，也不要重新开发 DEV-01～05、合并 master 或操作真实 NBA2K22/Native。
