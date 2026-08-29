# T2 Stage 04 冻结测试包窄修正派单 v2

## 0. 任务与角色

- repository: `chris2gao/Cybernetic_City_State_OS_v2---core`
- task: `os-v2-role-window-context-model-routing-integration-001`
- branch: `dev/os-v2-role-window-context-model-routing-integration-001`
- run: `run-20260812-角色窗口上下文模型路由集成-001`
- role: `stage_04_test_designer_correction`
- risk: `T2_semantic`, but correction scope is narrow and Human-authorized

本轮是已经冻结的 Stage04 v1 测试包的 **Human-gated narrow correction**，不是重新设计 A、Stage02 或 B，也不是 canonical implementation。

优先由原 Claude Opus 5 / Cowork Stage04 设计会话做显式 re-entry；若该会话无法明确识别或恢复，则使用新的 Claude Opus 5 correction 会话。无论哪种情况，都必须 fresh-read 远端 branch/master，并如实记录 `fresh` 或 `reentry`；不得把 conversational continuity 当作物理状态证明。

## 1. 必读耐久依据

按顺序读取：

1. `Stage04_Human窄修正授权_v1.yml`
2. `Stage04_FIX_REQUIRED接收与Human窄修正提案_v1.yml`
3. `独立接收审核/Stage04冻结测试包独立接收裁决_v1.yml`
4. `freeze_receipt_v1.yml`
5. 当前 `04_tests.yml`
6. `实现/verify_stage04_acceptance.py`
7. `fixtures/**`
8. `测试设计说明_v1.md`
9. A v1、Stage02 evidence index / conclusion；B 只可用于 candidate-result surface identification，不得作为 pass-condition 来源。

旧 freeze receipt 和独立审核裁决是 immutable history，不得修改。

## 2. 精确修正目标

必须关闭全部六个 blocker，且不得扩大成新的需求：

### ST04-IR-001 — A11 model-catalog thinness

补一个 ownership-aware negative check：

- `01_os/01_workflow/**` 与稳定入口不得持有第二份 mutable model catalog；
- 对 `model_routing` 的 pointer、invocation、receipt schema reference 必须允许；
- 不得用简单 provider/model token 扫描把合法 pointer 判红；
- 至少加入一个 conforming pointer/reference counterexample 与一个真实 duplicated mutable catalog mutation。

### ST04-IR-002 — forked_successor 过冻结

- A 强制的是 `fresh` 与 `reentry` 的可区分性；
- 不再要求第三种模式的 exact token `forked_successor`；
- 如果 implementation 自愿声明 successor/fork 模式，可测试其“不冒充 reentry / predecessor identity 明确”等语义，但不能要求某个固定名称；
- 原 M08 的 mere rename 不能继续作为缺陷 mutation。

### ST04-IR-003 — schema document-kind naming 过冻结

- 不得用 exact `role_contract.v` / `window_contract.v` / `handoff_contract.v` substring 作为唯一机制发现方式；
- 改为 naming-neutral 的 semantic/artifact-kind declaration、boot/registry binding 或等价可审计机制；
- mechanism directory 与 canonical filenames 继续不冻结；
- 必须增加 alternate-schema-name conforming probe，证明语义等价但 schema_version 名不同仍能通过。

### ST04-IR-004 — polarity / structure / provenance 误伤

修正至少以下检查：RW-T19、RW-T25、RW-T34、RW-T35、RW-T36 及相关 helper：

- `*_prohibited: true`、`*_disabled: true` 等否定声明不得误判成 enabled behavior；
- list / mapping 等 A 未限定的等价 YAML 表达应被接受；
- provider independence 只检查 normative role binding/selection，不扫描 provenance、evidence、citation 等说明性 scalar；
- 增加 conforming false-positive probes；
- 同时保留真正 enabled autonomy/quota/retention/provider-pinning mutation 的杀伤能力。

### ST04-IR-005 — validator probe dependency topology

RW-T37..RW-T42 必须继续满足：unmutated baseline validator exit 0；注入指定缺陷后 non-zero。

但 probe 环境必须：

- 使用完整 candidate tree，或
- 构造完整 boot-declared dependency closure。

不得只 staging 新机制自身而让合法的 `context_management` / `model_routing` / `communication_system` dependency 失踪。

至少加入一个 conforming fixture/variant，其中 composition validator 真实读取一个既有机制依赖，证明 unmutated baseline 仍可通过。

### ST04-IR-006 — Markdown role-table false positive

- Markdown 检测与 YAML 一样必须区分“role-like applicability table”与“canonical role source”；
- 仅出现三个 role concept 不足以判第二角色表；还需 source-of-truth/per-role normative attributes 等实质条件；
- 加一个 model/stage applicability Markdown table conforming counterexample；
- 仍需保留一个真正 duplicate normative role table mutation 能被杀死。

## 3. 必须保留

- `RW-T06` 语义保持有效：未来 canonical implementation boundary 必须包含 `01_os/02_boot/context_management/启动清单_v1.yml` 的 ownership cleanup。
- runtime-only 行为在 Stage06 前只做诚实 contract check，不伪造 runtime proof。
- RW-T30 只检查 T2 mechanism 被索引，不把既有索引漂移导入本任务。
- publisher authority preservation 不削弱。
- Human-triggered progression / no scheduler / no quota probe / T3/T4 out-of-scope 边界不削弱。

## 4. 写边界

只允许修改/新增：

- `04_测试生成/04_tests.yml`
- `04_测试生成/实现/**`
- `04_测试生成/fixtures/**`
- `04_测试生成/测试设计说明_v*.md`
- `04_测试生成/freeze_receipt_v2.yml`

必须保持字节历史，不得修改：

- `04_测试生成/freeze_receipt_v1.yml`
- `04_测试生成/独立接收审核/Stage04冻结测试包独立接收裁决_v1.yml`
- `04_测试生成/Stage04_Human窄修正授权_v1.yml`
- `04_测试生成/Stage04_FIX_REQUIRED接收与Human窄修正提案_v1.yml`
- `04_测试生成/Stage04_窄修正派单_v2.md`

不得修改：A、Stage02、B、canonical、run.yml、master 或其他任务文件。

## 5. 新冻结包要求

- `artifact_version` 必须从 1 增加；
- 生成新的 normalized digest；
- 新增 `freeze_receipt_v2.yml`，明确 supersedes v1 for active Stage04 acceptance，但 v1 保留历史；
- 测试数允许改变，不为保持 42 而保留坏测试；
- 每条新增/修改 test 仍需绑定 A success criterion 与 Stage02/internal evidence；
- B 名称、机制目录名、canonical filename、schema naming 不得成为无依据的 hard pass condition；
- 六个 blocker 各自必须有 regression/counterexample coverage；
- package validation 必须 pass；
- selftest 必须 pass，并分别报告 good tree、active mutations、boundary/conforming counterexamples；
- 当前未实现 canonical tree 应继续总体为 red，只允许 preservation/已存在事实类检查为 green；
- `git diff --check` 必须 pass；
- changed paths 必须完全落在本派单 write boundary。

## 6. 发布纪律

- 开工前 fresh-read branch/master；
- 若远端 HEAD 不是本派单/授权/run-state 等已知 foreground commits 的后代，停止并报告；
- 普通 commit + fast-forward push task branch；
- 禁止 force/rebase/squash/amend/history rewrite；
- 不改 master；
- push 后 fresh-read resulting remote head。

## 7. 独立接收仍是后置硬门

本 correction 作者不得自称 Stage04 最终独立接收者。修正完成后必须由 **新的独立会话**重新审核，优先不同模型族（OpenAI/Codex），并重新攻击六个 blocker、test derivation、false positives 与 mutation adequacy。

通过前 Stage05 仍 blocked。

完成标记：

`stage04_t2_corrected_frozen_tests_ready_for_fresh_independent_acceptance`
