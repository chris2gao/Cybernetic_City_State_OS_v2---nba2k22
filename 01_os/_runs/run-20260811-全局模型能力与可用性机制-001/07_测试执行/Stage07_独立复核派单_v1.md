# Stage 07 独立测试执行与实现复核派单 v1

Task: `os-v2-global-model-capability-and-availability-routing-001`

Role: **independent Stage 07 reviewer**。你不是 Stage 06 executor，不得修实现来让审核通过。

## 推荐 reviewer

优先使用新的 Anthropic 会话，推荐当前可用的 `Claude Opus 5`。surface 不作为硬编码前提：
Claude Desktop Cowork / Claude Code Desktop 中哪个当前真实可用且能 fresh-read/write 本任务分支，就使用哪个。
开始时必须报告 exact UI/model label、surface；若 reasoning/effort 控件不存在，记录 `not_exposed`。

本任务 Stage 06 executor 为 `Codex Desktop / GPT-5.6 Sol / max`，因此 reviewer 必须是不同会话且不同模型族。
Stage 04 测试作者也曾是 Claude Opus 5 / Cowork；本轮必须是**全新独立会话**，不得依赖旧会话记忆或旧结论。

## Git 物理基线

- repository: `chris2gao/Cybernetic_City_State_OS_v2---core`
- branch: `dev/os-v2-global-model-capability-and-availability-routing-002`
- Stage 06 dispatch base: `a97d32ddd24cc9a94aaedea8adb045d4cdf6308c`
- implementation commit: `3e3b608ac2c265d6aa4eb31471e8f1eae05603a4`
- Stage 06 evidence head: `f89a81ba26f2e697fa1423a37185b28728d82ae0`
- 本 Stage 07 派单创建前 branch head: `677a4ebb14b69e09b6f9b182c9bcda135452ad09`
- master expected from current task evidence: `1fbab0f3e0a84aebbc04035d720dbfea110bf0f4`

以上 SHA 都是 pointer。开工时 fresh-read 远端物理状态；若 branch 只因本 Stage 07 dispatch/run evidence 正常 fast-forward，可继续。任何未知 canonical mutation 都停止。

不得 checkout、merge、rebase 或读取 quarantined：
`dev/os-v2-global-model-capability-and-availability-routing-001`。

## 最小加载顺序

不要默认加载全部 `_runs`。按以下顺序：

1. `AGENT_WORKING_DISCIPLINE.md`
2. `AGENTS.md`
3. `01_os/README.md`
4. `01_os/开发入口与单窗口任务规范_v1.md`，重点 §7.1、§8、§9、§11
5. `01_os/01_workflow/07_测试执行/README.md`
6. `01_os/01_workflow/07_测试执行/实现/最小运行schema_v1.yml`
7. 本 run：
   - `01_需求建模/requirement/A_需求建模_v3.yml`
   - `01_需求建模/requirement/人类确认_v3.yml`
   - `02_信息收集与提炼/Stage02_证据结论_v2.yml`
   - `02_信息收集与提炼/证据对齐与冲突消解_v1.yml`
   - `03_结果建模/B_结果模型_v1.yml`
   - `04_测试生成/04_tests.yml`
   - `04_测试生成/freeze_receipt_v2.yml`
   - `04_测试生成/实现/verify_stage04_acceptance.py`
   - `05_步骤拆分/05_steps.yml`
   - `06_执行/Stage06_Human实施边界授权_v1.yml`
   - `06_执行/Stage06_执行证据_v1.yml`
   - `06_执行/Stage06候选接收裁决_v1.yml`
   - `08_结论/completion_pointer_v1.yml`
8. primary diff：直接审 `a97d32... -> 3e3b608...`，不要用 executor 摘要代替 diff。
9. 只读 Stage 06 实际 canonical paths：
   - `01_os/03_mechanisms/model_routing/**`
   - `01_os/02_boot/model_routing/**`
   - `01_os/06_execution/boot/model_routing/**`
   - `01_os/05_registry/model_routing_v1.yml`
   - `01_os/03_mechanisms/README.md`
   - `01_os/开发入口与单窗口任务规范_v1.md`

## 核心原则

Stage 07 不是“再看一次 28/28”。必须同时回答：

1. frozen tests 是否由 reviewer 独立复现；
2. 实现是否满足 B 与 Stage 02 evidence 的**意图**，而非只满足 validator 字面；
3. primary diff 是否在授权 boundary 内；
4. 是否有 evidence laundering、错误 source attribution、semantic dilution 或 overfitting；
5. 是否需要 `invalidate_upstream`。

不得因为 executor 已经报告 `28/28` 就跳过任何测试或语义检查。

## 必须独立执行的机器验证

至少实际运行：

```text
python <run>/04_测试生成/实现/verify_stage04_acceptance.py package <run>
python <run>/04_测试生成/实现/verify_stage04_acceptance.py selftest
python <run>/04_测试生成/实现/verify_stage04_acceptance.py acceptance <repo-root>
python 01_os/03_mechanisms/model_routing/实现/verify_model_routing.py static <repo-root>
git diff --check a97d32ddd24cc9a94aaedea8adb045d4cdf6308c..3e3b608ac2c265d6aa4eb31471e8f1eae05603a4
```

并独立计算/核验：

- Stage 04 normalized test package digest 是否仍为
  `72898d54c86ca52449aa96f1dfaed0d6ca8153b93dbc9ae36089a9e8edb55478`；
- publisher authority SHA-256 是否仍为冻结基线；
- primary diff changed paths 是否全部属于 Human Stage 06 boundary；
- `04_测试生成/**` 在 Stage 06 implementation/result commits 中是否字节未变；
- master 未修改；quarantined branch 未复用。

必须至少增加一组**不依赖 Stage 06 executor 自带 evidence/validator 的独立测量**，例如独立 YAML strict parse、source-ref resolution table、手工/脚本 cross-check registry/boot/pointer，或直接 semantic diff audit。

## 必须逐项攻击的四个问题

### R7-P1 source-ref 可解析性

`模型与产品面目录_v1.yml` 使用了 `OAI_*`、`GOOGLE_*`、`ANTH_*`、`GEMINI_PASS` 等 source ID。

审核：

- 它们是否能通过 canonical pointer 或明确耐久 evidence ref 确定性解析到实际来源？
- 如果 canonical catalog 只有 opaque token、没有任何解析入口，是否仍满足 A/B 的“source/ref + evidence-backed”语义？
- 不得把“字段非空”当作“来源可审计”。

若需要当前外部事实验证，只用 provider 官方一手来源；把 web/current verification 与 repository-derived evidence 分栏。

### R7-P2 新出现的 Cowork / Opus 5 surface

Stage 04 的冻结 receipt 已实际记录：
`Claude Desktop — Cowork mode (Claude Agent SDK host) / Claude Opus 5`。

当前 catalog 的 Claude 主 surface 是 `claude_code_desktop / Sonnet 5`。

判断：

- Cowork/Opus 5 是本任务 A/B 明确 scope 外、可作为后续 catalog update 的新观察；还是
- 它已经使 B10/current-surface-set 或“global routing 当前活动目录”的陈述不完整到构成 blocker。

不要因为它没有冻结 test 就忽略；也不要因为它后来出现就自动扩大原需求。给出 scope-aware 判定。

### R7-P3 Claude Opus 4.8 的 surface attribution

catalog 当前有：
`surface_id: antigravity`, `model_label: Claude Opus 4.8`, `registered: false`。

核对 Stage 02 evidence：是否支持“Opus 4.8 是 Antigravity surface 的 discovered candidate”这一具体绑定。
如果证据只证明 Anthropic Claude/Claude Code 上的 Opus 4.8，而不是 Antigravity，则这是错误 attribution；`registered: false` 不能把错误事实变成可接受事实。

### R7-P4 validator 深度

不要只确认 `verify_model_routing.py` exit 0。检查它是否足以兑现 B13：

- schema/duplicate keys；
- source/freshness；
- surface-specific parameter evidence；
- boot/registry/pointer；
- registry coverage；
- 非法 cost/quota fields；
- diagnostic evidence 不得形成 hard qualification。

若冻结测试只覆盖最低字面，而 implementation 明显遗漏 B13 的关键承诺，应报告 blocker 或 upstream/test gap，而不是因 28/28 自动放行。

## 其他语义审核重点

逐条核 B01–B13，至少确认：

- workflow 没复制 catalog；
- availability = registered default + Human override；
- route authority 恒为 routing_only；
- API capability 没冒充 Web/Desktop surface parameter；
- project observation 与 vendor catalog 分离；
- Antigravity 非盲测试仍为 diagnostic；
- §7.1 已变薄且没有遗留价格表/静态型号路由；
- §8/§9/§11、T3、publisher authority 没被削弱；
- 没有 quota watcher/crawler/scheduler/fixed fallback；
- no master publication。

## 写入边界

本轮只能新增：

`01_os/_runs/run-20260811-全局模型能力与可用性机制-001/07_测试执行/**`

不得修改：

- canonical implementation；
- A / Stage 02 / B / Stage 04 / Stage 05 / Stage 06 evidence；
- completion pointer；
- `run.yml`；
- master；
- quarantined branch。

发现 blocker 只报告，不修。

## 输出

### 如果最终通过

至少生成：

1. `07_verification.yml`，满足 Stage 07 最小 schema；
2. `独立复核报告_v1.md`，列出 primary-diff findings、B01–B13 adjudication、四个 attack point 的结论、独立测试结果；
3. 可选的机器验证 receipt/output summary，但不要提交巨大日志。

`07_verification.yml` 至少要有：

- `status: complete`
- Stage 03 / 04 / 06 predecessor SHA-256 binding
- reviewer identity 与 executor identity 分离证据
- `payload.reviewer_role`
- `payload.verdict: accepted`
- `payload.test_results`
- `payload.implementation_claims`
- `payload.upstream_invalidation`
- `payload.completion: true`

Human-facing verdict 只能是：

- `PASS`
- `PASS_WITH_NON_BLOCKING_NOTES`

### 如果有 blocker

**不要伪造 schema-compliant accepted completion。**

生成 `07_blocking_review_v1.yml` + `独立复核报告_v1.md`，明确：

- `review_verdict: FIX_REQUIRED` 或 `REJECTED`
- blocking finding IDs
- failure 属于 implementation defect、Stage 04 test gap，还是需要 invalidate Stage 02/03
- 精确修正边界建议

Stage 07 保持未完成。

## Git / publication

在 `-002` task branch 正常 commit + push review evidence。允许普通 fast-forward source-branch push；禁止 force/rebase/squash/amend/history rewrite。

push 后 fresh-read remote HEAD，报告 exact 40-char SHA。不得发布 master。

完成通过标记：

`stage07_independent_verification_complete_ready_for_Human_integration_gate`

若阻塞：

`stage07_independent_verification_fix_required`
