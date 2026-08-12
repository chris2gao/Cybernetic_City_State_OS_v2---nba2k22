# Stage 06 Codex 执行派单 v1

Task: `os-v2-global-model-capability-and-availability-routing-001`

Role: **Stage 06 canonical implementation executor**。

推荐执行 surface/model：**Codex Desktop / GPT-5.6 Sol**。若 Codex 当前 UI 暴露 `max` reasoning，使用 `max`；否则使用该 surface 实际可用的 `high`。开始时记录 exact model/UI label 与实际 reasoning setting。若 Human 明确该模型 unavailable，停止并回传，不自行更换模型。

选择 Codex 的原因：Stage 04 frozen tests 由 Claude Opus 5 / Cowork 生成；Stage 06 使用 OpenAI 模型族实现，避免测试作者与实现者同模型族。模型选择只影响 routing，不授予任何额外权限。

## Git 物理基线

- repository: `chris2gao/Cybernetic_City_State_OS_v2---core`
- active task branch: `dev/os-v2-global-model-capability-and-availability-routing-002`
- dispatch-preparation head: `1a5ed723f39e5f626e4351c6dd1092e4791f40c3`
- master expected at dispatch: `1fbab0f3e0a84aebbc04035d720dbfea110bf0f4`

本派单文件自身会使 branch 在上述 preparation head 之后再 fast-forward 一个普通 commit。开工必须 fresh-read 远端真实 HEAD；若仅包含本派单 commit，正常继续。不要使用 quarantined `dev/os-v2-global-model-capability-and-availability-routing-001`。

## Human 已授权的 Stage 06 boundary

授权证据：

`01_os/_runs/run-20260811-全局模型能力与可用性机制-001/06_执行/Stage06_Human实施边界授权_v1.yml`

活动任务包：

`01_os/_runs/run-20260811-全局模型能力与可用性机制-001/01_任务输入/任务包_v4.yml`

允许修改且只有这些：

- `01_os/03_mechanisms/model_routing/**`
- `01_os/02_boot/model_routing/**`
- `01_os/06_execution/boot/model_routing/**`
- `01_os/05_registry/model_routing_v1.yml`
- `01_os/开发入口与单窗口任务规范_v1.md`
- `01_os/03_mechanisms/README.md`
- `01_os/_runs/run-20260811-全局模型能力与可用性机制-001/**`

`allowed_changed_paths` 是整个 Stage 06 objective 的授权边界，不是要求所有路径都必须修改。

## 明确禁止

- 修改 `master`；
- force / rebase / squash / amend / history rewrite；
- 修改 `01_os/01_workflow/**` 语义；
- 修改 `01_os/03_mechanisms/context_management/**`；
- 修改 `01_os/05_registry/repository_publisher_authority_v1.yml`；
- 修改 Stage 04 frozen tests、validator、fixtures、mutations 或测试设计说明；
- 实现 role mechanism、task-envelope / long-running mechanism；
- 启用 Claude Code CLI；
- 自动账户/quota crawler、watcher、scheduler、fallback inventory；
- formal Antigravity qualification；
- 读取/保存 credential、token、cookie、browser profile；
- merge/reuse quarantined `-001` history；
- 自行扩大 boundary。

## 最小加载顺序

不要默认加载整个仓库或全部历史 `_runs`。

1. fresh-read remote branch/master physical state；
2. `AGENT_WORKING_DISCIPLINE.md`；
3. `AGENTS.md`；
4. `01_os/README.md`；
5. `01_os/开发入口与单窗口任务规范_v1.md` 中 bootstrap/task packet/test/review/publication 相关部分；
6. 本任务 `01_任务输入/任务包_v4.yml`；
7. `06_执行/Stage06_Human实施边界授权_v1.yml`；
8. `05_步骤拆分/05_steps.yml`；
9. `04_测试生成/04_tests.yml`；
10. `04_测试生成/freeze_receipt_v2.yml`；
11. `04_测试生成/实现/verify_stage04_acceptance.py`；
12. `03_结果建模/B_结果模型_v1.yml`；
13. `02_信息收集与提炼/Stage02_证据结论_v2.yml` 与 `证据对齐与冲突消解_v1.yml`；
14. `01_需求建模/requirement/A_需求建模_v3.yml` 与 `人类确认_v3.yml`；
15. 只读取实现直接需要的相邻 canonical：`03_mechanisms/README.md`、context-management 相邻结构、相关 registry/boot/loader conventions。

## 开工前基线

在修改 canonical 前实际执行并保存结果：

- Stage 04 `package`；
- Stage 04 `selftest`；
- Stage 04 `acceptance . --expect-red`；
- `git diff --check`；
- branch/master/topology/dirty state；
- frozen `test_package_sha256`。

预期历史基线是 5/28 green、23 red，但必须报告实测，不能复制预期冒充结果。

若 frozen digest 不再精确等于：

`72898d54c86ca52449aa96f1dfaed0d6ca8153b93dbc9ae36089a9e8edb55478`

立即停止并回传 `invalidate_upstream: workflow_stage_04_test_generation`。

## 严格按 Stage 05 顺序施工

### S1 — core routing contract

完成 `S1_core_routing_contract`，只实现该 step objective 所需内容。

绑定测试：

`MR-T01 MR-T04 MR-T05 MR-T06 MR-T07 MR-T08 MR-T25 MR-T26`

全部通过才能进入 S2。

失败若是局部实现缺陷，可重试；最多 3 次。需要改变已确认 Human availability / routing_only / no-cost-quota / no-auto-fallback 语义才能通过时，不要改测试，按 `05_steps.yml` invalidate upstream。

### S2 — surface catalog + project evidence

绑定测试：

`MR-T09 MR-T10 MR-T11 MR-T12 MR-T13 MR-T14 MR-T15 MR-T16`

使用 Stage 02 已接受 evidence；不要自行把 API 参数冒充 consumer/desktop surface 参数。未知保持 `unknown`。invalid/nonblind Antigravity observations 只能 diagnostic，不能 formal qualification。

全部通过后进入 S3；最多 3 次。

### S3 — boot / registry / loader / validator / failure surfacing

绑定测试：

`MR-T03 MR-T21 MR-T22 MR-T23 MR-T24 MR-T27 MR-T28`

MR-T24 必须是真实负例：删掉 freshness field 后机制 validator 非零退出。不得用只检查文件存在性的 validator 伪装 fail closed。

全部通过后进入 S4；最多 3 次。

### S4 — entry thinning + preserve controls

绑定测试：

`MR-T02 MR-T17 MR-T18 MR-T19 MR-T20`

把 `开发入口与单窗口任务规范_v1.md` §7.1 中 volatile model/price catalog 迁出，只留下稳定 routing preflight、Human availability、executor_profile 绑定、`routing_only` 与 canonical pointer。

不得削弱 §8 / §9 / §11 / T3 / publisher authority；`repository_publisher_authority_v1.yml` 必须保持冻结 SHA 字节一致。

全部通过后进入 S5；最多 3 次。

### S5 — full package closure

不增加新语义。

必须实际执行：

- Stage 04 `package` => exit 0；
- Stage 04 `selftest` => exit 0；
- Stage 04 `acceptance .` => **28/28 green**；
- frozen digest 仍为 `72898d54c86ca52449aa96f1dfaed0d6ca8153b93dbc9ae36089a9e8edb55478`；
- `git diff --check`；
- changed paths vs allowlist；
- publisher authority frozen SHA；
- no binary/temp/cache/personal absolute path/secrets；
- master unchanged；
- quarantined branch untouched。

若三次预算耗尽，或失败证明 A / Stage02 / B / frozen tests 任一上游不成立，必须使用 `05_steps.yml` 的 `invalidate_upstream`，不得降低测试标准。

## 实现原则

- 优先最小、直接、repository-convention-consistent 的实现；
- 不为了“未来可能有用”增加 crawler、daemon、scheduler、复杂 scoring engine、fallback reservation；
- catalog 是 evidence-backed 活动事实，不是永久真理；
- project observation 与 vendor catalog 分离；
- model + product surface 是一等身份；
- surface 参数必须有 surface exposure evidence；
- Human availability override 是 task-time authority；
- routing output 永远 `authority: routing_only`；
- 本任务不创建真正的账号探测/自动路由后台服务。

## 证据与提交

建议每个 S1-S4 在该 slice 的绑定测试全绿后形成一个有意图的普通 commit；S5 / evidence 再形成结果 commit。不是硬性要求 commit 数量，但不得 squash/amend/rewrite。

运行证据写入本 run 的 `06_执行/**`，至少记录：

- baseline；
- 每 step attempts、实际失败、修复与最终 test IDs 状态；
- 28/28 closure；
- frozen digest；
- actual changed paths；
- canonical files；
- source commit(s)；
- master/quarantine 状态；
- evidence honesty。

普通 push 当前 task branch 已授权，不需要为 boundary 内确定性修复反复向 Human 请求逐文件批准。

## Stage 06 完成条件

只有以下全部成立才可声明 Stage 06 candidate complete：

1. S1-S4 均通过各自 frozen test IDs；
2. S5 28/28 green；
3. package/selftest 均 exit 0；
4. frozen digest 未漂移；
5. changed paths 全在授权 boundary；
6. publisher authority 未改；
7. no master write；
8. no quarantined history reuse；
9. evidence 已耐久写入 run 并 push；
10. push 后 fresh-read remote HEAD 与本地发送 head 一致。

不要执行最终独立审核。不要发布 master。Stage 07 / final independent review 由后续不同模型族新会话完成。

## 完成回传

pointer-only 为主：

```yaml
completion_pointer:
  packet_id: os-v2-global-model-capability-and-availability-routing-001
  stage: workflow_stage_06_execution
  status: candidate_ready_for_stage07
  executor:
    surface:
    model:
    reasoning_setting:
  source_branch: dev/os-v2-global-model-capability-and-availability-routing-002
  source_base: <fresh-start-head>
  source_head: <40-char>
  validation:
    frozen_test_package_sha256: 72898d54c86ca52449aa96f1dfaed0d6ca8153b93dbc9ae36089a9e8edb55478
    package:
    selftest:
    acceptance: 28/28
    step_attempts:
      S1:
      S2:
      S3:
      S4:
      S5:
  repository:
    changed_paths: []
    out_of_scope_paths: 0
    publisher_authority_unchanged: true
    master_modified: false
    quarantined_branch_reused: false
    worktree_clean: true
  publication:
    transport: local_git
    resulting_remote_head: <40-char>
    fast_forward_verified: true
    force_push: false
  next_owner: foreground_stage07_and_independent_review
```

完成标记：

`stage06_candidate_28_of_28_ready_for_stage07`
