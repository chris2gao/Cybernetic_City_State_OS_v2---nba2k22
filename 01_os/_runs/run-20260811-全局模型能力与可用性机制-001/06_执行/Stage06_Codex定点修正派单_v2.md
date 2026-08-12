# Stage 06 Codex 定点修正派单 v2

## Role

你是 Stage 06 implementation executor — post-delivery correction round 1。

推荐 surface：Codex Desktop / GPT-5.6 Sol；若 UI 暴露 max，使用 max；否则使用实际最高可用档并记录。

你不是 test designer，不是最终 reviewer。

## Repository / branch

Repository:
`chris2gao/Cybernetic_City_State_OS_v2---core`

正式分支：
`dev/os-v2-global-model-capability-and-availability-routing-002`

开始前 fresh-read 远端 branch/master/current worktree；不要采信聊天 SHA。
严禁使用 quarantined `dev/os-v2-global-model-capability-and-availability-routing-001`。

## Active packet / frozen package

活动任务包：
`01_os/_runs/run-20260811-全局模型能力与可用性机制-001/01_任务输入/任务包_v5.yml`

Stage 05 v2：
`01_os/_runs/run-20260811-全局模型能力与可用性机制-001/05_步骤拆分/05_steps_v2.yml`

Stage 04 corrected frozen package：
`01_os/_runs/run-20260811-全局模型能力与可用性机制-001/04_测试生成/04_tests.yml`

必须绑定：
- artifact_version: 3
- test_count: 35
- test_package_sha256: `848b691712166a968c821ad6e53cafaf477b86bf7b1d7773306ad4e6ebf3e48c`

freeze receipt：
`04_测试生成/freeze_receipt_v3.yml`

不得修改任何 Stage04 v3 测试、fixture、mutation 或 verifier。

## Correction trigger

独立 Stage07 reviewer 已确认旧 candidate 虽然旧包 28/28，但存在三个 blocker：

### F1 — unsupported surface/model attribution

当前 candidate 把 `Claude Opus 4.8` 写成 `surface_id: antigravity`。Stage02 只支持 Antigravity Opus 4.6；Opus 4.8 是 Anthropic/Claude Code 侧 discovered/unregistered candidate。

修复必须由 Stage02/B10 证据决定：可将 Opus 4.8 正确绑定到 `claude_code_desktop` 且保留 discovered/unregistered 语义，或删除该候选；不得继续挂在 antigravity。

### F2 — canonical source refs 不可解析 + evidence laundering

当前 catalog 的 source tokens 没有从 mechanism declared load surface 可达的 resolution contract；其中 `C08_Antigravity_Pro_access` 是 claim ID，不是 source ID。

旧 Stage06 为过旧 MR-T25 曾把真实 `GOOGLE_AG_PRICING` 替换成 claim identity。corrected MR-T25 已修复误伤。

本轮必须恢复/建立真实 source chain：
- canonical mechanism 必须存在从 boot declared load surface 可达的 source-resolution entry point；
- catalog/source_exposure tokens 必须解析；
- primary provider sources 与 independent research refs 的 kind + url/ref/path 必须可审计；
- `GOOGLE_AG_PRICING` 等 source identity 可合法出现于 evidence metadata；
- 不得再用项目 claim ID 冒充 source ID。

不要过拟合测试建议的文件名；source-resolution entry point 的具体文件名不是 frozen requirement。

### F3 — mechanism validator 没兑现 B13

机制自己的 validator 必须真实 fail closed，不是只让 Stage04 外层 verifier发现错误。

corrected negative probes MR-T31–MR-T35 至少要求 validator 对以下情况 non-zero：
- registered bogus/unresolvable source ref；
- unregistered bogus/unresolvable source ref；
- registry path 不存在；
- registry coverage 缺失；
- mechanism/catalog version binding drift；
- illegal cost/quota routing semantic field；
- required pointer breakage。

MR-T33 / MR-T35 在旧 candidate 已绿，但仍需保持。

## Existing good behavior to preserve

不要重写整个机制。旧 candidate 已正确满足并必须保持：
- independent global mechanism；
- Human availability override；
- routing_only authority；
- no cost/token/quota optimization；
- no automatic fallback chain；
- no background quota/account probe；
- model × surface separation；
- surface-specific parameter profiles；
- vendor catalog 与 project observation ledger 分离；
- diagnostic evidence 不产生 hard qualification；
- §7.1 thinning；
- §8/§9/§11/T3/publisher authority controls 不削弱。

旧 Gemini 3.1 Pro mechanical-only 硬编码规则已被当前 Human-confirmed A v3/B11 intentionally superseded；本轮不要重新塞回入口。

Cowork/Opus 5 是当前 task scope 外的新 surface observation；本轮不扩 A/B catalog scope。

## Allowed writes

严格沿用 Human 已授权 Stage06 boundary：
- `01_os/03_mechanisms/model_routing/**`
- `01_os/02_boot/model_routing/**`
- `01_os/06_execution/boot/model_routing/**`
- `01_os/05_registry/model_routing_v1.yml`
- `01_os/开发入口与单窗口任务规范_v1.md`
- `01_os/03_mechanisms/README.md`
- `01_os/_runs/run-20260811-全局模型能力与可用性机制-001/**`

实际只修改修 blocker 所需的最小 canonical 子集；allowed paths 是授权边界，不是改动配额。

禁止修改：
- Stage04 v3 frozen package/files；
- A v3 / Stage02 / B v1；
- `01_os/01_workflow/**` semantics；
- context_management；
- repository_publisher_authority_v1.yml；
- master；
- quarantined -001；
- force/rebase/squash/amend/history rewrite。

## Execution order

按 Stage05 v2：

1. S1：先复验应保持全绿，不为本轮改语义。
2. S2：修 F1/F2，目标 10/10。
3. S3：修 F3，目标 12/12。
4. S4：复验 5/5，禁止回归入口/发布/审核控制。
5. S5：完整 35/35 closure。

每个 slice 最多 3 次施工内 retry。当前是交付后 correction round 1；不要把施工内 deterministic iteration 与交付后 correction round 混淆。

## Required verification

必须实际执行：

- `verify_stage04_acceptance.py package <run_root>` → exit 0, digest `848b6917...e48c`
- `verify_stage04_acceptance.py selftest <repo_root-or-required-args>` → exit 0, good 35/35, active mutations 36/36 killed
- `verify_stage04_acceptance.py acceptance <repo_root>` → 35/35
- mechanism validator static → exit 0
- MR-T31–T35 负例实际由 corrected acceptance/selftest 证明 non-zero
- `git diff --check`
- changed paths vs v5 allowlist
- publisher authority SHA unchanged
- Stage04 v3 directory bytes unchanged from correction dispatch baseline
- no binary/cache/personal absolute path/secret pattern introduced
- master unchanged
- quarantined branch not reused

## Evidence

不要覆盖旧 `Stage06_执行证据_v1.yml`，它是历史。

新增：
`06_执行/Stage06_定点修正执行证据_v2.yml`

至少记录：
- fresh source head/master;
- exact executor surface/model/reasoning;
- candidate base / correction implementation commit / result head;
- F1/F2/F3 remedy mapping;
- before 29/35 and after actual result;
- S1-S5 attempts;
- package/selftest/acceptance actuals;
- corrected digest;
- publisher authority hash;
- changed paths/out-of-scope;
- evidence honesty: executor self-verification is not final independent acceptance。

新增 completion pointer：
`08_结论/completion_pointer_v2.yml`

不要覆盖 v1。

## Publication

正常 commit + push `-002`；推荐保持 implementation commit 与 evidence/result commit 分离。
禁止 force/rebase/squash/amend/history rewrite/master publication。

push 后 fresh-read remote branch head，回传精确 40 位 SHA。

## Completion

若 35/35 且没有新 blocker：
`stage06_corrected_candidate_35_of_35_ready_for_fresh_stage07`

若发现需要改 Stage04/A/Stage02/B 或超出 boundary：
停止并 `invalidate_upstream`，不得自行扩边界。
