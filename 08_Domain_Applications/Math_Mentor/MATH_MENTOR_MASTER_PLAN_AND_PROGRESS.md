# Math Mentor 主计划与当前进度总账

## 1. 权威与新鲜度

> **当前证据基线：** `master@9e12064cbc51f61918dccfd48cf6915879adb962`（2026-07-15 核验）。本文件是 Human 可读的进度索引，不替代 Plan 3 宪法、领域协议、精确 Git 历史或详细合同。Human Speaker 始终拥有最终语义、发布与激活权。若摘要文字与当前 Git 物理证据冲突，以精确提交、当前文件和获批 Human 决定为准。

`9e12064...` 是本总账事实盘点的 **reconciled evidence/source baseline**，不是对发布后当前 master SHA 的预言。三文件包的发布状态按以下非自引用合同解析：accepted candidate `c461d252b4a86241745e438dd8c9cd9da6f14a72` 与 accepted review authority `0a832a28adf71eb96701ea1a98710eefe5c80193` 是输入证据；只有三文件通过正常 merged PR 实际存在于经物理核验的 current master 时，才是 `accepted_published`；最终 PR、merge commit 与 master SHA 记录在 `ai/review/latest` 的 final publication handoff，而不写进产生该 merge 的提交。

本总账只在以下三类事件后更新：获接受的 master 发布、重要 Human 架构决定、阶段或批次获接受。状态不能从旧报告标题或旧 `planned` 字样推断，必须重新核验当前 master。

本文件与 [MATH_MENTOR_CURRENT_STATE.yml](MATH_MENTOR_CURRENT_STATE.yml) 和 [MATH_MENTOR_ROLE_AND_HANDOFF_CONTRACT.md](MATH_MENTOR_ROLE_AND_HANDOFF_CONTRACT.md) 构成三文件接管包。前者是机器可读新鲜度快照，后者定义 provider-neutral 角色、通讯 packet、接管和职责分离。三者都明确服从同一规则：**精确 Git 证据覆盖陈旧摘要文字。**

## 2. 一句话系统定义

Math Mentor 是一个由 Human 治理、由可替换前台教师直接教学、由可委派后台角色承担重型编排、分层语义审查与有界执行，并建立在经审计知识节点、明确学习合同和 fail-closed 控制边界之上的 provider-neutral 数学教学编排系统。

## 3. 架构地图

| 层 | 当前权威与职责 | 当前成熟度 | 明确边界 |
|---|---|---|---|
| Plan 3 / Human Speaker | 宪法、Engine A/B 路由、最终语义与发布授权 | `accepted_published` | 模型输出不能取代 Human 授权；P3 默认关闭 |
| 前台教师 | ChatGPT/Claude 直接教学、讲解、引导提问、实时纠错并适配认知负荷 | `specified_manual_only` | 只保留轻量 delivery admission；不必重做完整编排或数学审计 |
| 后台教学编排者 | Codex/Claude Code/ChatGPT/Claude 可从快照重建状态、提出下一教学动作、组织 lesson/exercise/exam/review/multi-node plan | `specified_manual_only` | 可委派但非 runtime；不得静默改变 Human 学习目标或声称未证实的持久状态 |
| 后台语义审查者 | Codex/Claude Code/ChatGPT/Claude 按 SR0/SR1/SR2 审查数学、先修、类比边界、答案与 bridge candidate | `specified_manual_only` | SR2 只返回带证据升级；不得取代 Human/独立受权 gate，也不得把 Mode B 变成 machine proof |
| 后台执行者 | Codex/Claude Code 读取仓库、生成资源、执行确定性计算/验证、维护证据与获准提交 | `specified_manual_only` | terminal 位置或模型品牌不产生授权；不得自行扩大 mutation scope |
| 架构审查与任务分派者 | 四类兼容 agent 在完成 bootstrap 和显式 assumed-role 声明后均可接管 | `specified_manual_only` | 角色属于协议而非会话；受保护变更的作者/执行者不能自授最终接受或发布权 |
| GitHub 证据与状态层 | task packet、exact-head handoff、validation evidence 与本总账 | `accepted_published` | Git 证据记录状态，不自动授权生产行为 |
| 教学合同层 | 初始化、Lesson Plan、Prep/Socratic/Exam、复习与工具诚实性合同 | `specified_manual_only` | 文档与 prompt 存在不等于 agent runtime 存在 |
| 知识语料层 | `Pure_Math_Intuition_DB` 根节点、roadmap 与历史资产 | `statically_validated_inactive`（结构） | 全语料数学正确性与教学就绪未获认证 |
| P0 控制平面 | authority、identity、normalization、授权验证与 admission 的静态实现 | `statically_validated_inactive` | 只读、fail-closed；无生产 trust ingress、transport 或 writer |
| Bridge 层 | 14 个 legacy 内容资产与 canonical v1 合同 | `legacy_assets_unresolved` | legacy 不是 canonical typed edge，也不可被 Coordinator 正式消费 |
| 未来运行数据面 | session runtime、Coordinator、持久化、scheduler writer、observability、rollback | `absent` / `blocked` | 未经新 Human gate 不得激活或写入 |

控制关系是：Human Speaker 决定目标、歧义/跨域裁决与受保护边界；前台教师专注学习者互动并发出 `TeachingStateSnapshot`、`OrchestrationRequest`；后台编排者和语义审查者承担重型工作并返回已标注证据的 packet；前台只做目标、学生状态、review disposition 与 unresolved gate 的轻量准入；后台执行者完成有界工具/仓库工作；GitHub 保存精确证据。未来 runtime、persistence、bridge consumption 与 protected writer 必须独立获批。

## 4. 当前产品接口决定

- 兼容的学习者前台教师是 **ChatGPT** 与 **Claude**。其主要推理预算用于直接教学、讲解、提问、纠错、节奏与认知负荷适配。
- 重型教学编排和重型语义审查是第一类可委派后台角色；默认可由 **Codex/Claude Code** 承担，也允许完成相同 bootstrap/assumed-role 合同的 ChatGPT/Claude 接管。角色不绑定 provider、terminal 或当前会话。
- 前台不重做完整计划或数学审计，只检查 packet 是否匹配当前学习目标与 learner state、semantic review disposition 是否可接受、是否仍有 blocker/Human gate，然后记录 `DeliveryAdmissionRecord`。
- 当前实现形态仍是 Human 治理的手工通讯编排，所有角色状态为 `specified_manual_only`；记录架构不激活 runtime、Coordinator 或受保护 writer。
- 独立 frontend/UI 状态为 `not_required`，不是 backlog blocker。
- visualization 仍可作为可选、依赖工具的教学辅助，但不决定 Math Mentor 当前产品是否可交付。
- 旧成熟度表中关于 UI 的 `blocked/absent` 描述已被本次 Human 产品决定覆盖；除非 Human 以后改变方向，不应恢复为必做项。

## 5. 路线图与实际进度矩阵

状态词仅使用：`accepted_published`、`specified_manual_only`、`statically_validated_inactive`、`pilot_accepted`、`legacy_assets_unresolved`、`planned`、`absent`、`not_required`、`blocked`、`prohibited`。

### 5.1 LRP、P0 与 pilot

| 项目 | 交付状态 | 能力状态 | 当前事实 |
|---|---|---|---|
| LRP-01 Teacher Initialization | `accepted_published` | `specified_manual_only` | 初始化流程、最小上下文与 dry runs 已在 master；无 initializer runtime |
| LRP-02 Lesson Plan / Agent Contract | `accepted_published` | `specified_manual_only` | lesson schema、agent contracts、Exam handoff 与 bridge slot 合同已发布；无 agent pipeline |
| LRP-03 Prompt Consistency | `accepted_published` | `specified_manual_only` | Coordinator/Prep/Socratic/Exam prompt 已对齐手工教学边界；未激活 Coordinator |
| LRP-04 Test Harness / Golden Cases | `accepted_published` | `specified_manual_only` | 文档级 oracle、fixtures 与模拟存在；不是运行时 E2E 执行 |
| LRP-05 Learning State / Review | `accepted_published` | `specified_manual_only` | 状态、毕业、learned-history 与 scheduler schema 存在；writer 不存在 |
| LRP-06 Capability / Tool Truthfulness | `accepted_published` | `specified_manual_only` | 能力登记、工具诚实性与计算 handoff 已发布；工具 broker/runner 未实现 |
| P0 control-plane hardening | `accepted_published` | `statically_validated_inactive` | PR #3 已合并；静态控制面 104/104；无生产 trust ingress、runtime 或 writer |
| Four-node certified pilot | `accepted_published` | `pilot_accepted` | PR #4 发布四节点；PR #5 修复干净检出复现；范围只限 dossier 所声明证据，4/4 仍 `consumer_allowed=false` |
| Provider-neutral role/handoff archive | `accepted_published` 仅当正常 merged PR 后三文件在经物理核验的 current master 上存在 | `specified_manual_only` | accepted candidate/review refs 固定；最终 PR/merge/master 从 final handoff 与 Git 物理状态解析；没有自治 dispatcher、runtime 或 writer |

LRP 的“已发布”表示合同与文档已经落在当前 master，不表示相应生产能力已运行。LRP-04 特别不能被描述为 executable runtime 或真实 E2E。P0 的 admission、authorization 与 identity 实现是静态、只读、未激活的控制平面。

### 5.2 Knowledge Completion Program Stage 0–9

| Stage | 状态 | 当前事实与进入下一阶段的门槛 |
|---|---|---|
| 0 Inventory / classification | `statically_validated_inactive` | 历史 Stage 0 运行完成结构库存，但绑定旧 head，当前视为 historical/stale；P0 提供较新的结构基线，不等于全语料语义认证 |
| 1 Identity / Mode | `planned` | 只有有限 pilot 子集得到人工接受；全语料 identity 与 mode closure 未完成 |
| 2 Formal content | `planned` | 四节点 pilot 不能代表 667 个根节点正文已认证 |
| 3 Prerequisites | `planned` | pilot 外部先修链仍未闭合；未批准 candidate edges 为 fail-closed |
| 4 Teaching readiness | `planned` | 需要 lane-correct、Human 接受的教学证据；不能由字段存在自动晋级 |
| 5 Validation readiness | `planned` | Mode A 可用机器证据，Mode B 必须保留 Human 语义判断；没有全语料 evaluator |
| 6 Bridge readiness | `planned` | 只认证 endpoint 候选，不生成 bridge；当前无 formal bridge endpoint 获消费资格 |
| 7 Bridge landing | `planned`；当前任务 `prohibited` | P3 默认关闭；先迁移既有资产，新的 canonical bridge 需单独 Human gate |
| 8 Validation / index / consumption | `absent` / `blocked` | 没有 formal bridge admission、消费或 Coordinator runtime；`consumer_allowed=0` |
| 9 Maintenance / regression | `planned` | 需在真实发布与运行合同存在后建立持续回归、审计与回滚 |

### 5.3 Bridge、持久化与 runtime

| 组件 | 状态 | 说明 |
|---|---|---|
| Legacy bridge content assets | `legacy_assets_unresolved` | 14 个文件、10 个唯一 ID、两种不兼容 schema；内容可作为迁移候选 |
| Canonical bridge v1 typed edges | `absent` | 当前 14 个文件中 0 个满足 canonical v1 endpoint 合同 |
| Formal bridge index/admission/consumption | `absent` / `blocked` | 5 个 legacy 文件被旧索引列出并不构成消费授权 |
| Production Coordinator runtime | `absent` / `blocked` | prompt 或合同中的 Coordinator 不等于运行实例 |
| Production trust ingress / authorization transport | `absent` | model payload 内的 gate 字段不能授权写入；需可信 host 注入 |
| Learning-state writer | `absent` / `blocked` | schema 已有，持久化、原子性、审计与回滚未实现 |
| Spaced-review scheduler writer | `absent` / `blocked` | schema 已有，生产 interval policy、writer 与幂等执行未实现 |
| Standalone UI | `not_required` | Human 当前产品决定；不是缺失层阻塞项 |

## 6. 当前量化基线

### 6.1 P0 与 corpus

| 指标 | 当前耐久证据值 |
|---|---:|
| root candidate nodes | 667 |
| staging exclusions | 229 |
| unapproved candidate edges | 420 |
| explicit alias conflicts | 53 |
| deterministic UUIDv5 assignments | 667 |
| strict identity records | 666 |
| missing strict identity | 1（`topology_compactness.yaml`） |
| schema eras | E1=143, E2=496, E3=8, E4=20 |
| conflict records | 286 |
| Human-accepted pilot nodes | 4 |
| `consumer_allowed=true` | 0 |
| final clean-checkout P0 tests | 104/104 |
| production runtime active | false |

四个接受的 pilot 节点是 `COMPLEX_ANALYSIS-418`、`PDE-487`、`ABSTRACT_ALGEBRA-468`、`ALG_TOPOLOGY-676`。Mode A 的两个节点通过其限定 evaluator；Mode B 的两个节点依靠 Human 语义接受，不能写成 machine-passed。pilot 中的 provisional identity binding 不产生 production effect。

### 6.2 Legacy bridge 物理库存

| 指标 | 复算值 |
|---|---:|
| tracked `BRIDGE-*.yaml` files | 14 |
| YAML parse success | 14/14 |
| unique bridge IDs | 10 |
| duplicated IDs | 4：`BRIDGE-001`–`BRIDGE-004` |
| files involved in duplicate IDs | 8 |
| schema families | 2（Family A=9, Family B=5） |
| indexed files | 5 |
| unindexed files | 9 |
| explicit `from_nodes` / `to_nodes` endpoint objects | 0 / 0 |
| canonical schema-v1 files | 0 |
| unresolved bridge records | 14 |

这里的“14 个 unresolved”表示 14 个记录都没有可解析 endpoint；不是发现 14 条显式但解析失败的引用。索引中的 5 个文件全部属于 Family B；9 个 Family A 文件全部未索引。文件名、标题、编号接近或普通隐喻均不是 endpoint 证据。

## 7. 已完成并获接受的里程碑

1. LRP-01–06 的合同、schema、prompt 修复、文档级测试与工具诚实性文件已存在于当前 master；旧 implement plan 中六个 `planned` 已被物理产物覆盖。
2. P0 静态控制平面通过 [PR #3](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---teacher/pull/3) 发布，merge commit 为 `b3ee031`；它保持只读、fail-closed 与未激活。
3. 四节点 pilot 通过 [PR #4](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---teacher/pull/4) 发布，merge commit 为 `4902db5`。
4. 干净检出复现问题通过 [PR #5](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---teacher/pull/5) 修复；最终当前 master 为 `9e12064`，提交证据记录 104/104。
5. 当前 source mailbox 是 neutral baseline；活动任务与评审信号从 `ai/review/latest` 读取，不能从 source mailbox 猜测。

## 8. 未实现、未激活或禁止推断的能力

- `absent`：生产 Coordinator/session state machine、生产 trust ingress、授权 transport、nonce 原子持久化与跨进程 replay 防护、production evidence provider、learning-state writer、scheduler writer、legacy importer implementation、正式 bridge admission/index/consumption、真实 runtime E2E evaluator。
- `blocked`：任何依赖上述生产 trust、持久化或消费层的自动写入和 autonomous teaching integration。
- `prohibited`：从 104/104 静态测试推断 production runtime；从四节点 pilot 推断全语料正确；从课堂通过直接推断 graduated；从旧索引推断 bridge 可消费；从模型 payload 的 `human_gate` 字段推断写授权；把 `consumer_allowed` 从 0 晋级。
- `not_required`：独立 UI。它不是“缺失 blocker”，也不应被当作本计划完成条件。

## 9. Bridge 资产策略

Canonical policy key: `migrate_existing_before_new_generation`。

1. **先迁移、后生成。** 14 个 legacy 文件含有可能有价值的数学/教学连接内容，应先审计、选择、Human 数学复核、绑定精确 endpoint、迁移到 canonical v1、验证并索引；不能把它们当作可丢弃噪声，也不能批量原地改写。
2. **碰撞 fail-closed。** `BRIDGE-001`–`BRIDGE-004` 各有两个不同语义文件。现有证据不能选 winner；不得凭文件名、标题、数字或 staging precedence 裁决。
3. **endpoint 必须显式认证。** canonical `from_nodes` 与 `to_nodes` 必须使用含 `node_id`、`file`、`title`、`status` 的 reference objects；裸字符串或主题相似度不够。
4. **消费需要完整 gate。** endpoint present、prerequisite verified、lane-correct validation、indexed、learned-history satisfied 缺一不可。旧映射索引的 5 条记录只能作为 importer/audit 输入。
5. **新生成是例外。** 只有 Human 复核确认没有可接受 legacy 资产表达目标数学连接时，才能提出从 `BRIDGE-015` 起的新 canonical bridge；landing 仍需独立 Human gate。
6. **当前不实施。** 本任务不修改、生成、重命名、删除或索引任何 bridge。以后可以设计 Human 触发的 ChatGPT/Claude 手工 bridge 使用，但这不等于激活 production runtime。

## 10. Provider-neutral 教学编排、语义审查与交付准入

### 10.1 手工通讯循环

```text
学习者互动
  -> 前台教师诊断并产生 TeachingStateSnapshot
  -> 需要重型规划时发出 OrchestrationRequest
  -> 后台教学编排者重建状态、选择候选动作并可分派 BackendResourceTaskPacket
  -> 后台执行者生成资源、计算、验证与 provenance
  -> 后台语义审查者按 SR0 / SR1 / SR2 返回 SemanticReviewPacket
  -> 后台编排者汇总 TeachingActionPacket
  -> 前台教师只做 lightweight DeliveryAdmissionRecord
  -> 获准内容进入讲解、练习或 Exam；未获准内容 revise / block / escalate
  -> accepted work 才能更新 GitHub 证据与本总账
```

```yaml
teaching_orchestration_status: "specified_manual_only"
foreground_role: "teacher_with_lightweight_delivery_admission"
backend_orchestration: "delegable_specified_manual_only"
backend_semantic_review: "delegable_tiered_specified_manual_only"
provider_lock_in: false
runtime_activated: false
```

### 10.2 角色分工

- **前台教师**：直接教学、实时误解修复、节奏与认知负荷适配；发出快照/请求；只检查目标匹配、学生状态匹配、review 状态可接受和无 unresolved gate。
- **后台教学编排者**：从快照和仓库证据重建状态，选择下一教学动作候选，组织 lesson/exercise/exam/review/multi-node plan，并分派有界 worker task。
- **后台语义审查者**：审查定义、先修、数学正确性、类比边界、答案/rubric 与 bridge candidate，返回证据、局限和 disposition。
- **后台执行者**：执行仓库读取、有界生成、确定性计算、tests/formatting/evidence 和获准 branch handoff。
- **架构审查与任务分派者**：维护三文件接管包、核验 exact heads、形成 completion-preserving packet；任何兼容 agent 在 bootstrap 与 assumed-role 声明后可替换当前持有者。

详细 provider compatibility、packet 合同、职责分离和接管规则见 [MATH_MENTOR_ROLE_AND_HANDOFF_CONTRACT.md](MATH_MENTOR_ROLE_AND_HANDOFF_CONTRACT.md)。

### 10.3 分层语义审查

| Tier | 适用内容 | 后台 disposition | 前台工作 | 最终 gate |
|---|---|---|---|---|
| SR0 deterministic | 算术、声明假设内的符号等价、schema/reference checks | `tool_verified_candidate` | 只确认相关性与适用域 | 不产生 protected authority |
| SR1 bounded routine math | lesson examples、exercise solutions、已接受节点合同内综合 | `accepted_for_delivery_candidate` / `revise` / `block` | 轻量 delivery admission，无需完整重审 | 仍服从当前任务授权 |
| SR2 ambiguous/protected | 有争议定义/先修、新 bridge、Mode B 实质歧义、跨域裁决、identity conflict、目标改变 | `escalate_with_evidence` | 不得交付为已接受事实 | Human Speaker 或明确受权的独立架构/语义 gate |

后台 reviewer 可以给强建议，但模型品牌、terminal 位置或 authored packet 不能自授权。Mode B review 不能被重新标成 machine proof。

### 10.4 后端任务类与轻量准入

| 后端任务类 | 允许产物 | 前台 delivery-admission 检查 |
|---|---|---|
| lesson / example / counterexample | lesson plan、diagram-as-data、code anchor | 目标和 learner state 匹配；SR disposition 可接受 |
| exercise / answer / rubric | 难度分层题、答案、评分规则、deterministic checks | 无 unresolved correctness/blocker；不泄漏当前 exam |
| exam / classroom packet | assessment set、Exam handoff、trap evidence | 符合 Exam contract；不把 classroom pass 等同 graduated |
| multi-node / bridge candidate | synthesis 与 candidate evidence | identity/prerequisite 精确；SR2 bridge gate 未绕过 |
| review material | 复习题、错误回访、间隔建议 | 只作提案；无 writer 时不声称已排程 |
| deterministic work / repair | 计算、validation、index diagnostics、缺口报告、获准修复 | provenance 可复现；mutation scope 与 Human gate 匹配 |

当前角色合同本身不授权 production Coordinator、nonce/persistence、learning-state/scheduler write、consumer promotion、bridge mutation 或 source/master publication；三文件包的 source/master 发布仅来自独立的 Human-authorized normal-PR publication signal，不扩大其余权限。

## 11. 下一认证节点批次提案

### 推荐：Accepted-pilot prerequisite frontier（4 节点）

这是一个“共同证据角色”的 prerequisite-closure 批次：每个候选都是一个已接受 pilot 节点的直接先修前沿。它优先补齐已投入审查成本的四个 pilot 周边，而不是按数字邻接扩张。**这是提案，不是认证；任何未解决 identity 或 prerequisite 必须 fail-closed。**

| 候选 | 精确路径与身份 | Lane / Mode | 组内理由 | 当前阻断与 Human 决定 | 预期证据 |
|---|---|---|---|---|---|
| `COMPLEX_ANALYSIS-417` | `08_Domain_Applications/Math_Mentor/Pure_Math_Intuition_DB/COMPLEX_ANALYSIS-417.yaml`; UUID `e75b8557-6317-5a24-b7ba-2f35ceee6100` | MathLane_A / stored Mode A；routing 目前 inferred | `COMPLEX_ANALYSIS-418 -> n_417` | E2；formal definition、prerequisites、mapping boundary 缺失；identity `declared_consistent_unapproved`。Human 需接受 exact identity 与 lane-correct evidence | 定义复数/Argand plane；验证乘 `i` 为 90° 旋转、模保持和四次复原；明确类比边界 |
| `PDE-486` | `08_Domain_Applications/Math_Mentor/Pure_Math_Intuition_DB/PDE-486.yaml`; UUID `7d085bf4-f2cc-508f-b712-7fb9cf7933cf` | MathLane_A / stored Mode A；routing 目前 inferred | `PDE-487 -> n_486` | E2；三项语义字段缺失；open conflict `c5668ff0-934f-56e6-ba54-b6fcc39efc79`。Human 必须决定是否复用 pilot-only binding；否则移出且不得认证 | 正则自伴 Sturm–Liouville 条件、带权正交、边界条件和模态展开范围；多模态 evaluator，不冒充一般完备性 |
| `ABSTRACT_ALGEBRA-467` | `08_Domain_Applications/Math_Mentor/Pure_Math_Intuition_DB/ABSTRACT_ALGEBRA-467.yaml`; UUID `df6be666-95f8-58dd-bd25-9963ab2590fc` | MathLane_B / stored Mode B；routing 目前 inferred | `ABSTRACT_ALGEBRA-468 -> n_467` | E2；三项语义字段缺失；现有普通机械隐喻不满足 Mode B primary mapping。Human 需接受 LLM-architecture mapping 与边界 | 明确环的约定、理想、商环与同态核；保留 legacy executable 为特例 anchor；`machine_passed=false` |
| `DIFF_GEO-653` | `08_Domain_Applications/Math_Mentor/Pure_Math_Intuition_DB/DIFF_GEO-653.yaml`; UUID `8b771e3e-a23d-54bd-b5a2-1deddb8f091b` | MathLane_B / Mode B；Human-approved routing | `ALG_TOPOLOGY-676 -> n_653` | E4；formal/mapping 已获 Human 接受，但 topology 先修未闭合。`n_521/522/523/530/533` 有 roadmap entry 而 `bound_nodes=0`。Human 必须选择先补 topology corpus 或保持 manual | 沿用已接受定义与 mapping；新增可审计 prerequisite disposition；禁止用 `topology_compactness.yaml` 或标题模糊匹配代替 canonical identity |

批次共同出口证据：四份 exact identity dossier、Lane A evaluator 或 Lane B Human 语义审查、显式 prerequisite disposition、ChatGPT exact-head 接受和 Human 发布 gate。无论审查结果如何，默认 `consumer_allowed=false`，不产生 runtime、Coordinator、bridge 或 production identity 晋级。

### 被拒绝的替代批次

拒绝按编号后继选择 `COMPLEX_ANALYSIS-419`、`PDE-488`、`ABSTRACT_ALGEBRA-469`、`ALG_TOPOLOGY-677`。它们没有已证明的 `prerequisite_nodes` graph edges，全部仍是 E2 且缺 formal definition/prerequisite/boundary；`PDE-488` 另有 open identity conflict，`ALG_TOPOLOGY-677` 的代码不能支撑谱序列页转换，`ABSTRACT_ALGEBRA-469` 的小群示例不能支撑 Galois 基本定理，`COMPLEX_ANALYSIS-419` 的标量相位差也不足以支撑 RoPE 的成对多频旋转。与修补已接受 pilot 的直接先修前沿相比，它会增加语义分散与重新取证成本。

## 12. 更新协议

1. 只在 accepted master publication、重大 Human 架构决定或 stage/batch acceptance 后更新。
2. 每次更新先固定 source SHA，复核物理文件、测试证据、PR/commit 与 mailbox；旧报告只作历史线索。
3. 保留历史决定，不覆盖原证据；在下方 change log 追加一句，详细过程使用 pointer。
4. 不复制大型报告、registry 或 node body；指向精确文件和提交。
5. 同一项目可同时有“交付状态”和“能力状态”，例如 LRP 为 `accepted_published` + `specified_manual_only`。
6. 任何 unresolved identity、endpoint、authorization 或 prerequisite 必须保持 fail-closed。
7. 接管者必须按 [MATH_MENTOR_ROLE_AND_HANDOFF_CONTRACT.md](MATH_MENTOR_ROLE_AND_HANDOFF_CONTRACT.md) 完成 bootstrap、物理核验、`assumed_role` 和 `actually_read_files` 声明；不得依赖隐藏聊天记忆。
8. 每次 accepted 更新同步修改三文件包；机器快照见 [MATH_MENTOR_CURRENT_STATE.yml](MATH_MENTOR_CURRENT_STATE.yml)。

### Change log

- 2026-07-15：在 `master@9e12064cbc51f61918dccfd48cf6915879adb962` 建立首版总账；校正 LRP、P0、pilot、UI 与 legacy bridge 当前状态；记录 ChatGPT/Claude 前台、Codex/Claude Code 后台的手工教学编排架构；提出四节点 prerequisite-frontier 批次。
- 2026-07-15：同任务 correction 将角色改为 provider-neutral 可替换协议：前台教师专注教学与轻量准入，后台重型编排与 SR0/SR1/SR2 语义审查可委派；新增 current-state 与 role/handoff companion，并要求 zero-context takeover dry run。
- 2026-07-15：publication preparation 移除候选期“尚未发布”自陈述，改用 accepted candidate/review refs、merged normal PR、current-master 物理存在与 final review-branch handoff 解析发布状态；不预写未来 merge SHA。

## 13. 证据索引与未知项

### 13.1 本次全文读取或直接核验的核心证据

- 宪法与协议：`Plan 3 External Augmentation OS 总体架构设计方案 v0.1.md`、`06_Silicon_Index/AI_Bootstrap_Sequence.md`、`Universal_Layer_Execution_Protocol.md`、`.ai/PROTOCOL.md`。
- 主计划与状态：`Math Mentor Teaching System Design implement plan.md`、`KNOWLEDGE_COMPLETION_PROGRAM.md`、`MATH_MENTOR_CAPABILITY_MATURITY.yml`、`POST_P2_EXECUTION_MEMORY.md`。
- LRP：LRP-01–06 的主报告、validation 报告及其当前-master business outputs；`actually-read-files` 与 `changed-files` 附件未作为能力结论依据。
- P0：`.ai/PROGRAM_RUNS/math-mentor-p0-control-plane-hardening-0001/FINAL_REPORT.md`、`EVIDENCE/quantitative_findings.json`、`VALIDATION/validation_summary.json`、`REPORTS/architecture-and-migration.md`。
- Pilot：`.ai/PROGRAM_RUNS/math-mentor-certified-pilot-0001/FINAL_REPORT.md`、`MANIFEST.yml`、四份 dossier、identity/prerequisite evidence、validation summary，以及 `ai/review/latest` 上的最终发布与 post-verification 报告。
- Bridge：`BRIDGE_SCHEMA.md`、`BRIDGE_REGISTRY_AUDIT.md`、`知识图谱_节点映射索引.md`、当前 master 全部 14 个 tracked `BRIDGE-*.yaml`。
- 下一批：四个推荐候选、四个被拒候选、四个已接受 pilot node body、三份 split roadmap；identity registry 只做对应记录的 metadata/targeted extraction，未声称全文语义读取大型 registry。
- GitHub durable evidence：[PR #3](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---teacher/pull/3)、[PR #4](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---teacher/pull/4)、[PR #5](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---teacher/pull/5) 的 metadata、files 与 commits。
- 接管包：[MATH_MENTOR_CURRENT_STATE.yml](MATH_MENTOR_CURRENT_STATE.yml)、[MATH_MENTOR_ROLE_AND_HANDOFF_CONTRACT.md](MATH_MENTOR_ROLE_AND_HANDOFF_CONTRACT.md)；correction authority 来自 `ai/review/latest` 上的 `chatgpt-math-mentor-master-plan-progress-ledger-correction-0002` signal/task。

### 13.2 已知陈旧文字

- `Math Mentor Teaching System Design.md` 与 implement plan 的旧 blocker/`planned` 是蓝图历史，已被 LRP 物理输出覆盖。
- LRP 主报告中的 `completed_for_review` 是发布前历史状态。
- P0 master 报告中 pending PR/source publication 的文字已被 PR #3 覆盖。
- master 上 pilot 报告中 pending publication 的文字已被 review-branch 最终报告及 PR #4/#5 覆盖。
- `MATH_MENTOR_CAPABILITY_MATURITY.yml` 基线早于当前 master，未含 pilot，且 UI 旧状态已被当前 Human 决定覆盖。
- `POST_P2_EXECUTION_MEMORY.md` 自声明 historical；它不能授权新运行或 P3 bridge landing。

### 13.3 仍未知或未获确认

- 667 个根节点的全量数学正确性、教学质量与先修闭包未被语义审读；不得声称已完成。
- `topology_compactness.yaml` 的 strict identity 与 `n_521/522/523/530/533` 的 root binding 仍未解决。
- 53 个 explicit alias conflicts 与 420 条 unapproved candidate edges 仍需 Human/engineering 分批裁决。
- 14 个 legacy bridge 的数学连接是否值得迁移、准确 endpoint 与 collision disposition 均未获 Human 结论。
- 没有 production trust、persistence、scheduler、Coordinator 或 bridge-consumption 的实际运行证据。
- GitHub PR #3–#5 没有配置的 checks；104/104 来自提交的 fresh-checkout validation evidence，而不是 GitHub required check。
