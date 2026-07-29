---
task_version: "1.0"
task_id: "context-stage2-local-partition-001"
title: "阶段二本机默认分区运行试验"
mode: "goal"
task_level: 3

intent:
  goal: >-
    在当前本地开发环境中完成一个无管理员权限、无生产机制改动的最小运行试验，验证任务与角色默认分区、
    固定角色入口恢复、结构化交接、版本失效检查和上下文体积缩减能否沿正常工具路径工作，并如实记录
    worktree/clone 不能构成访问边界以及当前环境无法验证的能力。
  why_now: >-
    机制 2 的两路 Deep Research、NotebookLM 候选匹配、语义裁定与开放发现统计已经完成；当前最高信息增益
    来自本机运行证据。该试验结果将决定阶段二最终可行性判断和交给机制 3 的实现边界。
  definition_of_done:
    - "生成并提交本机试验报告，所有实验逐项标记 passed、failed 或 blocked。"
    - "生成可重复执行的最小脚本、fixture、非敏感日志和计算结果。"
    - "明确验证 clone/worktree 本身不能阻止同一不受限 shell 读取兄弟目录，不得包装成访问隔离通过。"
    - "新 executor 进程仅依赖固定入口和授权引用完成恢复及一个确定性小步骤。"
    - "版本哈希变化能够被确定性标为 stale，或给出明确 blocked 原因。"
    - "完成上下文输入体积代理测量，并明确其不证明模型质量提升。"
    - "只在工作分支创建本地提交，不推送 source/master，不合并。"

outputs:
  primary: "08_os/01_workflow/context-management-mechanism/evidence/09_本机默认分区试验_v1.md"
  additional:
    - "08_os/_runs/run-007-上下文管理信息收集测试/artifacts/local-partition/**"

inputs:
  required_refs:
    - "08_os/01_workflow/context-management-mechanism/requirement/A_需求建模_v1.yml"
    - "08_os/01_workflow/context-management-mechanism/evidence/00_挖掘目标与领域_v1.yml"
    - "08_os/01_workflow/context-management-mechanism/evidence/01_内部证据_v1.yml"
    - "08_os/01_workflow/context-management-mechanism/evidence/07a_机制同义裁定_v1.yml"
    - "08_os/01_workflow/context-management-mechanism/evidence/07b_开放发现统计_v1.yml"
    - "08_os/01_workflow/context-management-mechanism/evidence/07c_证据索引草案_v1.yml"
    - "08_os/01_workflow/02_信息收集与提炼/实现/证据包schema_v1.md"

scope:
  allowed_files:
    - "08_os/01_workflow/context-management-mechanism/evidence/09_本机默认分区试验_v1.md"
    - "08_os/_runs/run-007-上下文管理信息收集测试/artifacts/local-partition/**"
  forbidden_files:
    - "08_os/01_workflow/context-management-mechanism/requirement/**"
    - "08_os/01_workflow/02_信息收集与提炼/**"
    - "08_os/01_workflow/03_结果建模/**"
    - "CORE_MANIFEST.yml"
    - ".ai/**"
    - "除 allowed_files 外的全部仓库文件"
  allowed_actions:
    - "创建独立工作分支 codex/context-stage2-local-partition-001。"
    - "在系统临时目录和 allowed_files 下创建、运行并清理试验资源。"
    - "在工作分支提交精确 allowed_files。"
    - "读取完成试验所需的系统版本和非敏感环境能力信息。"

requirements:
  invariants:
    - "不创建或删除操作系统用户。"
    - "不要求管理员权限，不修改系统级 ACL、注册表、防火墙或全局 Git 配置。"
    - "不安装 Docker、WSL、内核模块、MCP 服务或其他系统软件。"
    - "若现有环境已有 Docker、WSL、权限 profile、受限工具 root 或无提权 ACL 能力，只能在临时目录内试用，不改变全局配置。"
    - "不创建、删除或修改远程 GitHub 仓库、团队、密钥、PAT 或权限。"
    - "不输出凭证、token、私钥、完整环境变量或用户私有路径内容。"
    - "任何无法技术执行的边界必须记为 failed 或 blocked，不得以模型承诺代替测试。"
  validation:
    - "git diff --name-only <signal.source_head>...HEAD 只包含 allowed_files。"
    - "报告中的每个实验都有 passed、failed 或 blocked。"
    - "至少记录一个授权读取正例和一个兄弟目录越界读取负例；若越界读取成功，该边界方案必须判为 failed。"
    - "临时资源全部清理，或逐项记录残留及原因。"
  acceptance:
    - "环境能力矩阵完整记录 OS、shell、Git、Python、Docker/WSL 可用性、当前权限和可用文件访问约束。"
    - "任务与角色工作区试验记录创建、提交、交接、清理命令及耗时。"
    - "固定入口恢复试验使用新进程，不依赖旧聊天或进程内变量。"
    - "结构化 handoff 闭环包含 planner 发布、executor 消费与发布、reviewer 最小输入审核。"
    - "上游 handoff 内容哈希变化有可重复 stale 检查。"
    - "全量任务材料、executor 最小入口包和 reviewer 最小入口包均统计字节数、字符数、文件数；只有现成可信 tokenizer 才报告 token 数。"
  stop_rules:
    - "需要管理员权限、安装软件、修改系统全局配置或远程权限时，停止该项并标记 blocked，继续其他独立实验。"
    - "发现需要修改 forbidden_files 或扩大目标时停止，不自行扩权。"
    - "发现凭证或隐私风险时停止相关动作并仅报告非敏感分类。"

authority:
  semantic_reviewer: "chatgpt"

return:
  packet_id: "codex-context-stage2-local-partition-001"
  detail_ref: "08_os/01_workflow/context-management-mechanism/evidence/09_本机默认分区试验_v1.md"

completion_policy: "completion_preserving"
---

## 实验顺序

### ENV-01 · 环境能力探测

记录 OS、shell、Git、Python、Docker/WSL 可用性、当前进程权限及可用文件访问约束。不得输出敏感环境变量值。

### PART-01 · 任务与角色工作区分区

在临时目录创建小型本地裸仓库或等价 Git 源，为 planner、executor、reviewer 创建独立 clone 或工作目录；每个角色写入唯一 sentinel 私有文件和允许发布的结构化 handoff。记录创建、提交、交接和清理的命令与耗时。

必须测试同一不受限 shell 能否读取兄弟角色目录。预期 clone/worktree 本身不能阻止读取；读取成功必须如实判为该访问边界失败。

### BOUND-01 · 可用边界原语抽查

若当前运行时已有受限工具 root、权限 profile、容器或无提权 ACL 能力，选择成本最低的一项，在临时目录测试授权读取与越界读取。没有可用原语则标记 blocked，并说明缺少能力。

### RESTORE-01 · 固定角色入口恢复

为 executor 生成固定结构化入口，至少包含任务标识、当前步骤、状态、待办、阻塞、精确输入版本和获准引用。结束第一进程或清空其会话变量，以新进程仅读取入口和授权引用，复述有效状态并完成一个确定性小步骤，不读取 planner/reviewer 私有文件。

### HANDOFF-01 · 结构化交接最小闭环

planner 发布版本化任务 handoff；executor 消费并发布结果 handoff；reviewer 只读取结果 handoff、测试说明和实现产物给出结论。修改上游 handoff 内容哈希，使用脚本或确定性检查将旧 executor/reviewer 入口标为 stale。

### SIZE-01 · 上下文体积代理测量

统计全量任务材料、executor 最小入口包和 reviewer 最小入口包的字节数、字符数、文件数。现有环境有可信 tokenizer 时可补充 token；否则不得把字符估算写成精确 token。

## Git 与发布边界

- 从 signal 的精确 `source_head` 建立工作分支 `codex/context-stage2-local-partition-001`。
- 只提交 `allowed_files`。
- `source_push_authorized: false`。
- 不推送 source/master，不合并，不修改远程权限。
- 期望最终状态：`committed_on_work_branch_not_merged`。

## 完成回传

最终回传必须包含：

```yaml
packet_id: codex-context-stage2-local-partition-001
exact_commit_sha: <工作分支提交>
changed_paths: []
test_commands: []
experiment_summary:
  ENV-01: passed|failed|blocked
  PART-01: passed|failed|blocked
  BOUND-01: passed|failed|blocked
  RESTORE-01: passed|failed|blocked
  HANDOFF-01: passed|failed|blocked
  SIZE-01: passed|failed|blocked
blocked_capabilities: []
drift_cause: null
avoided_extra_gates: []
final_original_task_status: completed|completed_with_blockers|blocked
remaining_real_human_decisions_only: []
```
