# 第二代 OS 替换与退役方案 v1

> 状态：已被 `第二代OS替换与退役方案_v2.md` 取代；仅保留为不可变历史设计证据，
> 不再作为活动任务拆分或执行依据。
>
> 形成日期：2026-08-02。
>
> 评估基线：`master@5739a297ab71ecd37197524fa121a0b9b28da942`。
>
> 当前 Human 决定：新 OS 完成前不触碰任何领域仓；替换工作只在 core 内推进。

## 0. 目标

本方案把第二代 OS 从“已具备开发治理和上下文管理能力”推进到“能够替代第一代 OS 的活动系统”。
替换不是一次性删除旧 `.ai` 栈，而是先在新 OS 中建立等价或更好的机制，经过真实 workflow
运行和独立测试，再切换启动入口，最后将旧系统降为兼容层或历史证据。

替换程序的五个阶段依次是：

1. 新通讯机制；
2. 新 Token 与资源管理机制；
3. 端到端 workflow 通用实现；
4. 其余全局环境机制补齐；
5. bootstrap 切换、兼容期和旧 OS 退役。

前两个机制同时承担新 workflow 的前两次真实试验。通用 workflow 不应在完全没有运行证据时
凭空设计，而应从这两次真实运行中提取重复出现的 artifact、transition、stop condition、
review loop、Human gate 和 receipt。

## 1. 当前替换判断

### 1.1 已经可以由新 OS 接管的部分

新 OS 已经具备较完整的开发治理控制面：

- `08_os/` 的目录、canonical、run 流量、领域内容和所有权已经分层；
- 一个窗口一个任务、精确 base、allowed paths、独立审核和 Human gate 已有统一规范；
- 本地 Git、GitHub API connector 和 GitHub CLI 已有按传输区分的发布门；
- registry、failure surfacing、文件生命周期和耐久证据已制度化；
- 上下文管理已有方法论、boot manifest、机器契约、validator、registry 和 loader；
- 确定性工具已有按需登记、真实性验证和调用边界。

因此，新开发任务的结构、证据、registry、发布纪律和上下文管理应继续只在第二代 OS 中演进。

### 1.2 尚不能整体退役旧 OS 的原因

当前仍有四类缺口：

1. 通讯、状态和 handoff 仍由旧 `.ai` 栈提供主要 canonical；
2. Token、上下文、模型和工具成本虽有旧方案，但尚未成为新 OS 的正式资源机制；
3. 七阶段 workflow 尚未形成统一可运行的阶段契约和 runner；
4. 环境能力发现、安全边界、审计恢复、版本迁移、并发协调等全局机制尚不完整。

准确结论是：第二代 OS 已经是成熟的开发治理框架，但还不是完整的端到端任务运行系统。

## 2. 替换原则

### 2.1 用新 workflow 建新机制

通讯机制和资源机制都必须按新 OS 的七阶段 workflow 执行：

```text
需求建模 A
  → 信息收集与提炼
  → 结果建模 B
  → 从证据生成测试
  → 步骤拆分
  → 执行
  → 独立测试与审核
  → 完成或退回上游阶段
```

第一次可以人工驱动，但每个阶段必须留下结构化、可验证、可复用的耐久产物。

### 2.2 旧系统是证据源，不是默认复制源

旧 `.ai` 通讯、token、lane、mailbox、release binding 和 compliance gate 都有真实运行经验，
应作为高价值证据输入。是否保留、改造或拒绝，必须由新 workflow 的证据和测试决定；不得因为
旧系统“已经存在”就整套平移，也不得因为目标是新系统就丢弃已付出代价得到的有效不变量。

### 2.3 一次一个机制，不顺手造第二套权威

每个任务只完成一个明确机制或一个明确的 workflow 基础设施目标。兼容期内必须写清：

- 哪个路径是活动 canonical；
- 哪个路径只是 adapter；
- 哪个路径只是历史证据；
- 同一状态或授权不得同时由两套系统独立裁定。

### 2.4 先真实跑通，再抽象

通讯机制是第一条真实 workflow；资源机制是第二条。P3 的通用 workflow 实现从两次运行中
抽取共同结构，避免继续设计一条从未完整运行过的流程。

### 2.5 分层切换，不直接删除

替换顺序是：新机制完成 → 兼容 adapter → 双读单写或明确单权威验证 → bootstrap 切换 →
观察期 → 旧 canonical 退役。任何阶段都必须有回滚点和明确的单一状态权威。

## 3. P1：新通讯机制

### 3.1 目标

在第二代 OS 中建立 provider-neutral、低 token、可审计、可验证的通讯、状态与 handoff 机制，
使一个真实任务能够从派单、执行、审核、定点修复到完成，不依赖旧 `.ai` 通讯 canonical 来
解释当前状态。

建议目标结构：

```text
08_os/03_mechanisms/communication/
08_os/02_boot/communication/
08_os/06_execution/communication/
08_os/05_registry/communication_v1.yml
```

旧 `.ai` 路径在兼容期只作为 adapter 或证据源，不立即删除。

### 3.2 阶段一：需求建模 A

A 至少覆盖：

- Human、前台审核/派单者、后台执行者之间的消息传递；
- machine pointer、Human operational content、durable Human brief 的结构分离；
- 长任务、报告、日志和证据只存 GitHub，聊天只传紧凑指针和必要总结；
- task、branch、head、status、授权和证据的明确绑定；
- 状态新鲜度与动作授权分离；
- dispatch、completion、review、revision、blocked、conflict、Human gate；
- local Git、GitHub connector、GitHub CLI 等不同环境；
- 同上下文 fast path 与新上下文完整初始化；
- 最低充分 token，而不减少独立证据、验证和问责；
- 不建立两套并存且可独立改变状态的通讯权威。

A 必须由 Human 确认并绑定版本；后续需求变化不得静默继承旧确认。

### 3.3 阶段二：信息收集与提炼

主要证据源：

- `.ai/PROTOCOL.md`；
- `.ai/communication_compliance/`；
- `.ai/HANDOFF_INIT_PROMPT.md`；
- `.ai/STATE.yml`、mailbox、brief、lane 与 release-binding 机制；
- `.ai/TOKEN_USAGE_PROFILE.md` 中与通信成本相关的规则；
- `AGENT_WORKING_DISCIPLINE.md` 中已发生的通讯和证据漂移事故；
- 当前 pointer-only 实际工作记录；
- 其他成熟代理系统的任务状态、消息队列、事件溯源和 CAS 设计，必要时做外部研究。

对旧系统的每一项能力给出：保留、改造、拒绝或待验证，并记录理由和失败历史。

### 3.4 阶段三：结果建模 B

B 应明确：

- 通讯事件模型；
- pointer schema；
- Human 内容载体；
- 当前状态和 transition graph；
- actor identity、state evidence、Human authority 的边界；
- immutable refs 与 mutable current-head 的关系；
- fast path 和 full initialization；
- connector/local/CLI 的传输差异；
- compatibility adapter；
- release、迁移、回滚和旧系统退役条件。

建议保留的旧系统不变量：

1. machine pointer 与 Human 内容结构隔离；
2. 长内容只通过耐久引用传递；
3. 状态新鲜度不等于授权；
4. event、actor origin、Human authority 分离；
5. state transition 使用 immutable evidence 与 current-head CAS；
6. same-context fast path 只读当前状态和非空 refs；
7. 缺失、陈旧、冲突或无法解引用时 fail closed；
8. validator 只证明 eligibility，不自行授权或执行状态改变。

### 3.5 阶段四：冻结测试

实现前至少冻结以下测试：

- 正常 dispatch、completion、review、revision、blocked 和 Human gate；
- pointer 缺字段、字段顺序错误、重复键或未知事件；
- mutable ref 冒充 immutable evidence；
- 旧 STATE 或旧 event 重放；
- `human_gate` 文本冒充真实授权；
- 执行者自报计数直接成为审核结论；
- 长任务或完整报告误贴聊天；
- branch/head 不一致；
- 同一事件重复消费或双重 transition；
- local Git、connector、CLI 三种环境；
- 同上下文 fast path 与 context boundary full load；
- 一个真实跨模型任务的完整闭环。

测试必须从 A 与证据推出，并在实现循环开始后冻结。改变验收语义需要退回阶段四，而不是在
实现压力下削弱检查。

### 3.6 阶段五至七

- 阶段五把 B 拆成 schema、validator、loader、adapter、migration 和真实试验步骤；
- 阶段六按步骤实现，保持判断与确定性执行分离；
- 阶段七由独立模型族和不同测量工具复验，不接受执行方自报成功。

### 3.7 完成条件

通讯机制完成必须同时满足：

- 新 canonical、boot、loader、registry 和 validator 齐全；
- 正例、负例、重放、冲突和迁移测试通过；
- 一个真实任务完成派单→执行→审核→修复→完成闭环；
- 聊天未承载长任务、长报告或完整日志；
- 当前状态、证据和授权均可从新机制独立解释；
- 旧 `.ai` 通讯路径只作为明确 adapter 或历史证据；
- 回滚到旧机制的条件和步骤经过测试。

## 4. P2：新 Token 与资源管理机制

### 4.1 目标

新机制不只管理 token，而是管理完成任务所需的全部稀缺资源：

- context window；
- input/output/reasoning tokens；
- cache read/write；
- tool output bytes；
- wall time；
- 模型档位和 reasoning effort；
- `standard`/`ultra` 等 execution mode；
- subagent 数量和 rollout budget；
- retry、repair 和 review 轮次；
- Human 注意力和往返次数；
- 质量事故与返工成本。

建议目标结构：

```text
08_os/03_mechanisms/resource_management/
08_os/02_boot/resource_management/
08_os/06_execution/resource_management/
08_os/05_registry/resource_management_v1.yml
```

### 4.2 旧方案作为证据

重点研究：

- `.ai/TOKEN_USAGE_PROFILE.md`；
- `.ai/TOKEN_USAGE_OPERATIONAL_NORMS.md`；
- `.ai/DEFAULT_LARGE_TASK_EXECUTION_PROFILE.md`；
- `.ai/CODEX_TASK_INPUT_CONTRACT.md`；
- `AGENT_WORKING_DISCIPLINE.md` 中关于限流、懒加载和工具输出的实测；
- 新通讯机制 P1 的实际 token 和 Human 往返数据。

旧方案中的供应商品牌、旧 mailbox、Fable 名称、本机绝对 Local Bus 路径不能直接成为新机制
canonical；它们只能作为特定环境证据或 compatibility input。

### 4.3 目标产物

任务资源配置至少包含：

```yaml
task_resource_profile:
  risk_tier: T0_mechanical | T1_standard | T2_semantic | T3_high_risk
  model_capability_floor: <minimum-sufficient-capability>
  reasoning_effort: <runtime-supported-value>
  execution_mode: standard | ultra | <runtime-supported-mode>
  rollout_token_budget: <positive-limit-or-null>
  context_budget: <limit-and-loading-policy>
  tool_output_budget: <per-call-and-task-limit>
  retry_budget: <bounded-count>
  repair_budget: <bounded-count>
  review_budget: <bounded-count>
  cache_policy: <immutable-cache-rules>
  invalidation_events: [head_change, publication, context_boundary, conflict]
  measurement_required: true | false
```

每个测量 run 至少记录：

- task type、provider、model、effort、mode；
- input/output/reasoning tokens；
- cache read/write；
- tool output bytes；
- reported cost 与 wall time；
- retry、repair、review 次数；
- validation result；
- quality incidents；
- metric source 和不可观测项。

### 4.4 核心原则

1. 测量后再预算；
2. 选择最低充分能力，不选择最低价格本身；
3. immutable blob 可缓存，HEAD、status、gate 等 mutable facts 在触发事件后必须失效重读；
4. 工具输出在调用端限流，而不是读取后假装没看见；
5. 同一失败不得原样重跑，必须改变证据、假设或修复；
6. Human 往返是资源，避免把一个完整目标拆成无意义微任务；
7. token 优化不得减少独立证据、验证覆盖或问责链；
8. provider price 和 model availability 是时效事实，使用前必须重新核验。

### 4.5 验收

至少选择 3–5 个匹配任务做旧方案与新方案对照：

- 同一目标；
- 同一验收标准；
- 同等级最低能力；
- 质量和证据完整度不下降；
- Human 往返轮次下降或不增加；
- token、tool output、wall time 或总成本至少一项有可测改善；
- 质量事故和返工成本单独统计，不能用低 token 掩盖失败。

“最佳 Token 方案”的定义不是固定预算表，而是根据任务类型、风险、环境和实测数据，动态选择
最低充分资源的机制。

## 5. P3：端到端 workflow 通用实现

### 5.1 含义

端到端 workflow 实现不是再写一份流程说明，而是让系统能够把 Human 的原始需求真正从
阶段一推进到阶段七，生成可校验产物、管理阶段 transition、在失败时退回正确上游，并在
Human gate 停止。

当前新 OS 能很好地管理单个开发任务，但还不能统一运行自己声明的七阶段工作流。

### 5.2 每阶段机器契约

每个阶段必须定义：

- 输入 schema；
- 输出 schema；
- artifact version；
- 完成条件；
- validator；
- allowed transitions；
- 失败分类；
- retry budget；
- 可退回阶段；
- executor/reviewer separation；
- Human gate；
- receipt 和 durable evidence。

建议统一产物：

```text
<run-root>/<run-id>/
├── run.yml
├── 01_任务输入/
├── 02_需求建模/
├── 03_信息收集/
├── 04_结果建模/
├── 05_测试生成/
├── 06_步骤拆分与执行/
├── 07_测试执行/
└── 08_结论/
```

具体目录是否全部需要，应由实际阶段产物决定；不得为了形式创建空目录。

### 5.3 Workflow runner

建议位置：

```text
08_os/06_execution/workflow/
```

第一版不需要无人值守 Coordinator，只需完成：

- 读取当前 run 和阶段状态；
- 校验前一阶段产物与版本；
- 阻止跳过必要阶段；
- 根据 transition graph 创建下一阶段任务包；
- 保持测试冻结；
- 记录 retry、repair、backtrack；
- 生成 receipt；
- 在 Human gate、权限变化、目标变化或不可恢复 blocker 处停止；
- 验证当前状态只有一个权威来源。

### 5.4 从 P1/P2 提取，而不是重造

P1 和 P2 每次运行都必须保留：

- artifact shapes；
- transition decisions；
- stop conditions；
- review correction loop；
- Human decisions；
- token/resource measurements；
- 失败和退回原因。

P3 只把两次真实运行中重复、稳定、可泛化的部分提升为 workflow canonical。仅出现一次、
依赖具体机制的做法不应直接写成全局规则。

### 5.5 完成条件

- 七个阶段均有活动 schema 和 validator；
- runner 能从阶段一推进到阶段七；
- 至少一个真实任务端到端成功；
- 至少一个失败案例按证据退回上游并重新推进；
- 测试冻结未被实现阶段修改；
- executor 与 reviewer 分离；
- transition、Human gate、receipt 和状态可重放；
- 不依赖旧 `.ai` workflow canonical 才能解释运行。

## 6. P4：全局环境机制补齐

### 6.1 已有基础较好的机制

#### 上下文管理

当前已有 canonical 方法论、文件生命周期、boot manifest、loader、registry、机器布局契约和
validator，是第二代 OS 最完整的全局环境机制。

#### 发布与仓库权限

发布传输矩阵、publisher authority、Human gate、精确 base、非 force CAS 和远端读回已较成熟。
后续需决定其长期 canonical 是仓库根级基础设施，还是在新 OS 中增加正式 mechanism adapter；
不能重复建立第二份可独立授权的规则。

### 6.2 必须补齐的机制

#### A. 通讯、状态与 handoff

P1 完成。它是当前最大缺口，也是其他机制进行跨模型运行和审核的基础。

#### B. Token 与资源管理

P2 完成。它为模型选择、context、工具输出、retry、repair、review 和 Human 成本提供统一机制。

#### C. Workflow 生命周期与退回

P3 完成。把七阶段从文档结构变成可运行的状态机和 runner。

#### D. 环境与能力发现

需要统一 environment/capability receipt，至少测量：

- OS、shell、路径语义；
- 可用工具及版本；
- 模型、effort、mode 和 subagent 可用性；
- repository transport；
- network、filesystem、sandbox、ACL 和 secrets 能力；
- runtime limits；
- 缺失项、不可观测项和失效条件。

环境事实必须测量，不能靠角色名或历史 note 推断。receipt 是事实，不授权动作。

#### E. 安全、隐私、secret 与访问边界

需要统一威胁模型和机制，明确区分：

- cooperative instruction boundary；
- workspace partition；
- enforced access boundary；
- credential/secret handling；
- network/data exfiltration；
- tool ACL 与 task allowlist；
- logging、redaction 和 retention；
- 正例与拒绝测试。

clone、worktree、窄提示词和 load profile 都不得被描述为强访问控制。

#### F. 审计、观测与恢复

需要统一定义：

- event log；
- run receipt；
- immutable evidence；
- current-state snapshot；
- failure taxonomy；
- replay 和 recovery；
- stale detection；
- orphan artifact 和中断任务处理；
- audit report 与 Human decision 的分离。

现有 run、registry 和 receipt 可作为基础，但目前缺少跨机制统一恢复合同。

#### G. OS 发布、版本、迁移与回滚

切换前必须建立：

- OS release version；
- semantic release commit 与 binding；
- compatibility matrix；
- migration plan；
- domain freeze 与解除条件；
- canary 或测试仓；
- rollback point；
- deprecated、adapter、historical 的生命周期；
- 删除旧 canonical 前的 reachability 和 loader 证明。

#### H. 并发、lane 与任务协调

单线程替换阶段可以暂缓，但在并行 backend 或 unattended automation 前必须完成：

- task ownership；
- lane identity；
- event ordering；
- current-head CAS；
- duplicate delivery；
- conflict detection；
- cutover epoch；
- task cancellation 和 session retirement。

旧 lane 机制是证据源，不应自动成为新机制。

#### I. 耐久 routing memory

非首批 blocker，但需要定义：

- 只保存稳定、低风险、routing-only 的事实；
- `source_ref`、`last_verified`、失效条件；
- 不保存 standing approval、current task state、secret 或 gate；
- 定期验证和删除陈旧断言。

### 6.3 暂不进入首批替换范围

以下能力在没有单独 Human gate 和威胁模型前保持未激活：

- authoritative Local Bus；
- live communication gateway；
- scheduler；
- Coordinator；
- unattended mutation；
- 自动跨仓发布；
- secrets 自动处理。

## 7. P5：切换、兼容和旧 OS 退役

### 7.1 切换前门禁

只有同时满足以下条件，才允许宣布新 OS 成为默认活动系统：

- 新通讯机制完成真实跨模型闭环；
- 新资源机制完成匹配任务实测；
- workflow runner 完成真实端到端任务和失败退回；
- environment capability receipt 可用；
- security/privacy/access boundary 有明确威胁模型和测试；
- audit/recovery 和 OS release/migration 机制可用；
- bootstrap、AGENTS 和 load profile 已有新 OS 路由；
- domain 仓仍保持冻结，直到 Human 明确解除；
- 回滚到旧入口经过测试。

### 7.2 兼容期规则

兼容期必须采用单一权威原则。可选模式：

- 新系统单写，旧系统只读 adapter；
- 新系统 authoritative，旧系统接收 shadow mirror；
- 旧系统 authoritative、新系统 shadow，仅限正式 cutover 前的验证期。

禁止双写后让两套系统都能独立改变当前状态。任何 mirror 都必须标记非权威，并有一致性检查。

### 7.3 Bootstrap 切换

切换任务至少修改并验证：

- `06_Silicon_Index/AI_Bootstrap_Sequence.md`；
- `AGENTS.md`；
- 新 OS boot manifests；
- registry；
- compatibility adapters；
- release/binding evidence；
- startup receipts；
- C0/C1/C2 或其新等价分类；
- Human gate 和 rollback pointer。

### 7.4 旧 OS 退役条件

只有满足以下条件才删除或归档旧 canonical：

- 没有活动 loader、bootstrap、task packet 或 state transition 依赖；
- 所有必要历史证据已由 immutable ref 保留；
- 新机制覆盖旧系统的必要不变量；
- 旧路径删除不会使现有证据 blob 不可达；
- registry、manifest、reference graph 和 domain upgrade 测试通过；
- Human 明确批准退役和删除范围。

退役后旧 `.ai` 内容可分为：

- compatibility adapter；
- immutable historical evidence；
- superseded design；
- approved deletion。

不得使用“旧”这一标签直接推导可删除。

## 8. 推荐任务顺序

```text
P1  communication mechanism
  ↓
P2  resource/token mechanism
  ↓
P3  workflow contracts + runner
  ↓
P4a environment capability discovery
P4b security/privacy/access boundary
P4c audit/recovery
P4d OS release/migration/rollback
P4e concurrency/lane, when parallelism is needed
  ↓
P5  bootstrap cutover + compatibility observation
  ↓
Human gate: legacy retirement and domain-freeze release
```

每个任务都使用当前 `08_os/开发入口与单窗口任务规范_v1.md` 的单窗口任务包、模型路由、
发布传输矩阵、独立审核和 completion pointer。

## 9. 下一窗口的第一任务入口

下一窗口先建立 P1 的阶段一需求建模任务，不直接写通讯协议实现。建议任务身份：

```yaml
task_id: os-v2-communication-requirement-modeling-001
objective: >-
  使用第二代 OS 阶段一机制，为新通讯系统形成结构化需求建模 A 和 Human 确认，
  明确目标、边界、失败模式、兼容期和验收方向；不实现通讯协议。
risk_tier: T2_semantic
expected_outputs:
  - 08_os/_runs/<new-run-id>/02_需求建模/A_通讯机制需求建模_v1.yml
  - 08_os/_runs/<new-run-id>/02_需求建模/Human确认_v1.yml
next_stage: stage_2_evidence_collection
```

实际 branch、base SHA、run-id、allowed paths、模型和测试由下一窗口从当前远端 master 重新测量，
不得沿用本方案形成时的 SHA。

## 10. 总结

替换程序不是“先补通讯，再把旧目录删掉”。正确路径是：

1. 用新 workflow 完成通讯机制；
2. 用同一 workflow 完成资源机制并测量成本；
3. 从两次真实运行中抽取通用 workflow；
4. 补齐环境发现、安全边界、审计恢复、发布迁移和必要的并发机制；
5. 切换 bootstrap，经过兼容观察和回滚验证后，再由 Human 决定旧 OS 退役与领域仓解冻。

这样第二代 OS 不只是文档结构替代旧系统，而是用自己的 workflow 建成、验证并最终运行自己。
