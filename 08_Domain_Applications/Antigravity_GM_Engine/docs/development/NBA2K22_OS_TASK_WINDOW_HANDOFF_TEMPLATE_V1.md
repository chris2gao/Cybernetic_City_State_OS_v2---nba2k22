# NBA2K22 OS任务窗口：派单、开发交接与长期记忆模板 V1

> 本模板用于**新窗口入场与任务闭合**，不取代OS真实的task packet、run.yml、verification_plan、managed_verify或completion pointer的canonical契约。标有占位符的内容必须按任务时点实测填入；不得复用历史HEAD、历史验收、预估测试数。核心OS始终以当前master版本为准。

## A. 建立新任务窗口前：分发最小信息

**第一步：OS必读（真实入口，不复制旧内容）**

1. 当前远端`master`精确40位SHA；
2. 根`AGENT_WORKING_DISCIPLINE.md`、`AGENTS.md`；
3. `01_os/README.md`与`01_os/开发入口与单窗口任务规范_v1.md`；
4. 领域`08_Domain_Applications/AGENTS.md`与`08_Domain_Applications/domain.yml`；
5. 只按本任务读相关OS model_routing/verification/MWU boot manifests、registry及validators，不默认递归读取`01_os/_runs/**`。

**第二步：业务最小上下文**

- 产品宗旨：`08_Domain_Applications/Antigravity_GM_Engine/docs/PROJECT_INTENT_AND_MODEL_DEVELOPMENT_BOUNDARIES.md`。
- 当前目标架构：`docs/development/PARALLEL_BASKETBALL_WORLD_DATA_ARCHITECTURE_V2.md`（前提：迁移候选已进入master；否则只以明确候选SHA读取）。
- 项目计划：`docs/development/OS_GOVERNED_NEXT_STAGE_ROADMAP_20261022.md`。
- 机读依赖：`docs/development/NBA2K22_OS_TASK_BACKLOG_V1.json`中对应任务ID。
- 仅取**直接依赖任务**的completion pointer、已获批ADR或证据目录；用户尚未批准的方案只作候选参考，不自动当权威。

上述`docs/`是相对业务根目录。旧仓库R系列/FINAL-CODEX/AG01D/DEV14需时按具体证据ID与源SHA打开，而不是每窗口整本重读。

## B. 新窗口可复制的派单壳（内容示例，不是固定的执行命令）

```yaml
task_id: <from-current-backlog>
repository: chris2gao/Cybernetic_City_State_OS_v2---nba2k22
goal: <one-precisely-bounded-objective>
exact_base_sha: <fresh-remote-master-or-Human-designated-parent>
branch: <new-task-branch>
risk_tier: <OS-preflight-result>
allowed_changed_paths:
  - <exact-business-or-domain-run-path>
sources:
  - <actual-source-commit-and-canonical-doc>
requirements:
  - <behavior-or-schema-contract>
non_goals:
  - <not-another-task>
prohibitions:
  - modify_core_owned_files
  - game_write_without_Human_approval
  - DCR_without_explicit_prior_Human_approval
  - master_write_without_Human_confirmation
  - treat_fixture_replay_as_live_game_acceptance
verification_plan: <candidate-tracked-JSON-plan>
required_tests:
  - <check-id-not-precomputed-test-result>
execution_profile:
  model: <OS-model-routing-selection-at-task-time>
  effort_and_surface: <supported-current-parameters>
independent_review: <new-session-other-than-executor-and-dispatch>
expected_deliverables:
  - <code-or-ADR-or-evidence-within-path-boundary>
  - <run.yml-and-completion_pointer>
stop_conditions:
  - new_product_semantic_choice
  - scope_escape
  - uncovered_protected_action
  - evidence_cannot_support_claim
```

正式task packet具体字段以OS第7节为准；这里是Human可读的简约壳，不代替canonical YAML。不要将来源路径的预估清单当成比`allowed_changed_paths`更窄的二次范围门。

## C. 长任务窗口的工作约定

- 同一目标内部允许：设计→开发→确定性修复→有界测试→提交→发布普通任务分支→收尾，不需要每步新窗口或重新授权。
- 每次实际的源码/Schema/ABI决定必须在项目ADR或字段字典记录：**决定、选择依据、反例、未证边界、对现存世界线/旧存档影响**。
- 触发Human介入的是真正新的语义抉择、超界、未确认的master/真实游戏写入/运行时激活、secret安全问题或必须转交独立模型；不是通用进度更新。
- DCR本地访问永远提前向玩家逐次请求，说明确切路径、预计命令或动作和为何远端不足。禁在未获准下自动执行本地验证；本地不可观测就标`NOT_RUN`。
- 不使用“41 passed”“完整Box”“全部数据已生产化”一类外推；真实测试命令、退出码、环境、fixture/当前游戏来源必须绑定。
- 导出SQLite样本测试不得重建受Git跟踪的原始fixture数据库；使用临时位置或任务隔离工作目录，提交原始文件hash。
- 小范围本地实验与正式world库迁移/实机修改是不同动作；必须明确区分。

## D. 一次任务收尾的耐久文件（业务与OS各归其位）

| 存储层 | 放什么 | 不放什么 |
|---|---|---|
| 领域规范（`08_Domain_Applications/.../docs/`） | 获接收的ADR、Schema契约、数据字段字典、Reader协议、业务API与正式计划 | 一次性的stderr、未确认的模型推断当作事实 |
| 领域run（`01_os/07_content/_runs/<run-id>/`） | 任务包、run.yml、候选验证计划、详细测试/哈希/变更清单、review findings、completion pointer | 共享OS机制定义、凭据、完整进程内存 |
| Git commit / 分支 | 对应实际工程变更、可追溯源码与审阅结果 | 从旧工作区中未经确认的本地临时数据 |
| 下一窗口输入 | 最新master SHA、当前backlog节点、必要ADR和直属前置pointer | 旧聊天的全文或全项目run历史 |

`run.yml.lifecycle`只能是OS七值枚举（`research_only`、`candidate_pending_validation`、`candidate_ready_for_independent_review`、`verified_on_demand`、`integrated_and_verified_on_demand`、`deferred`、`excluded`）。`status:`可作说明但不能替代`lifecycle:`。

OS的独立审核必须在不同会话完成：派单/执行同人不能宣称T2/T3任务已最终独立通过。评审看原始证据、未证结论和执行者论证，出正式verdict（契约内PASS/FIX_REQUIRED/REJECT；对Human沟通可另解释建议`ready_for_human_integration`等）。

## E. 最小可追溯completion handoff字段

```yaml
handoff:
  task_id: <current>
  source_branch: <branch>
  base_sha: <verified-40>
  head_sha: <verified-40>
  objective_done: <exactly-what-is-done>
  outputs:
    - <artifact-path>
  changed_paths: <actual-git-list-or-manifest-ref>
  verification:
    commands: [<real-executed-command-with-exit-code>]
    not_run: [<explicit-boundary>]
    failures: [<unresolved>]
    scope: <pass-fail>
  key_decisions:
    - decision_ref: <ADR-or-specific-doc>
  provenance:
    - <source-game-save-generation-fixture-and-version>
  downstream_contract:
    - <stable-fields-and-APIs-other-tasks-may-consume>
  limitations:
    - <concrete-not-yet-proven>
  next_task_ids:
    - <from-machine-backlog>
  reviewer: <different-session-required>
  Human_gate_required: <exact-protected-action-or-none>
```

OS canonical completion pointer应具备自身的transport、CAS、remote SHA readback、diff scope、dirty状态等机器字段；本模板是跨窗口业务摘要。下一窗口必须从仓库重新确认全部可变状态，而不是用本摘要代替最新检查。

## F. 例：ARCH与NATIVE并行的上下文依赖

`WORLD-DATA-ARCH-01`窗口只读V2、当前旧Schema、DEV14身份/代际、安全契约、原生候选的关键ID，不需要读取所有AG逆向汇编。它向下游输出`WorldID/SeasonID/GameUID/PlayerIncarnation/temporal-source ADR`。

`NATIVE-ACCEPT-01`窗口只读AG01D核心源码、fixture、Final Codex旧match-history审计、原生游戏记录/StatBank关联验证入口；它向下游输出真实身份/统计字段认证与UNKNOWN矩阵。

`WORLD-DATA-SCHEMA-01`消费上述两个输出（若NATIVE部分尚未验收，只能按未知状态建可扩展候选表），不得把未验字段强行标`NOT NULL`或发布生产数据。
