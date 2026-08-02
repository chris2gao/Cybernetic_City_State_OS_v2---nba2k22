# 第二代 OS 替换与退役方案 v2

> 状态：活动总体方案；取代 v1，供后续单窗口任务拆分与审核使用，不自行授权实现、
> 发布、迁移、切换或退役。
>
> 形成日期：2026-08-02。
>
> 评估基线：`master@0fc7e1c16f0947d9f311f80b55059de75600a8b8`。
>
> 历史基线：v1 来自 `origin/dev/os-v2-replacement-program-plan-001@034cebc5`，
> 本版依据独立审核、Human 裁定和 P0 实测重新落地，不把旧候选分支当作当前状态。
>
> 当前 Human 决定：新 OS 完成前不触碰任何领域仓；替换工作只在 core 内推进。

## 0. 目标

本方案把第二代 OS 从“已具备开发治理和上下文管理能力”推进到“能够替代第一代 OS 的活动系统”。
替换不是一次性删除旧 `.ai` 栈，而是先在新 OS 中建立等价或更好的机制，经过真实 workflow
运行和独立测试，再切换启动入口，最后将旧系统降为兼容层或历史证据。

P0 环境与能力发现最小版已完成并合入 `master@0fc7e1c`。其后的五个阶段依次是：

1. 新通讯机制；
2. 新 Token 与资源管理机制；
3. 端到端 workflow 通用实现；
4. 其余全局环境机制补齐；
5. 新 OS 默认活动系统宣告、兼容观察和旧 OS 退役。

前两个机制同时承担新 workflow 的前两次真实试验。通用 workflow 不应在完全没有运行证据时
凭空设计，而应从这两次真实运行中提取重复出现的 artifact、transition、stop condition、
review loop、Human gate 和 receipt。

### 0.1 裁定与证据绑定

本版把下列裁定作为活动计划语义。决策来源是 brief vault 中的
`core/03_决策档案/2026-08-02_第二代OS替换方案独立审核意见.md`，P0 状态来源是
`2026-08-02_P0独立审核结论.md`、`2026-08-02_P0第1轮修正复验结论.md` 和
`master@0fc7e1c` 的物理文件；这些引用提供证据，不自行授权后续动作。

| 编号 | 活动裁定 |
| :--- | :--- |
| A1 | P1/P2 直接使用阶段 1–4 的既有 schema。P3 是对账补齐：新增阶段 5–7 schema、全部 validator、transition graph 和 runner，并只按真实运行证据修订既有四份 schema。不得再声称“七阶段尚无 schema”。 |
| A2 | `06_execution/<area>/<name>/` 的 area-first 布局是既有 canonical。机制 loader 进入 `mechanisms/<name>/`，通用校验器进入 `validators/<name>/`；`communication/`、`resource_management/` 直接挂在 `06_execution/` 根部均属违规。现有 `boot/context_management/` 是唯一已知例外，按 §2.6 归一化。 |
| A3 | P1 完成时切换全部 core 窗口的通讯 canonical，而不是宣告整个新 OS 已接管。Token/资源在 P2 前仍由 `.ai/TOKEN_USAGE_PROFILE.md` 路由，workflow 在 P3 前仍由 `01_workflow/` 既有规格路由；§7.1 分成通讯切换门和默认活动系统宣告门。 |
| A3-附 | 领域仓解冻必须与“通讯 canonical 已通过兼容观察期”绑定，不得单独裁定。 |
| B1 | P0 已完成：capability receipt 机制和本机实测以 `master@0fc7e1c` 中的 run-020 receipt 为准，本方案只引用，不重述或改写测量事实。 |
| B2 | P2 使用 `_runs/` 历史数据作为旧基线，新方案单跑；缺失字段写 `not_observable`，只有关键指标无法恢复时才补对照跑。 |
| C1 | 不设置阶段性冻结复核门；每个 P 保留技术性 kill criteria，失败时降级、回滚或停止切换，不用“继续冻结吗”制造新的例行 Human gate。 |
| C2 | 总体规划文档可豁免七阶段 workflow，但豁免不适用于通讯、资源、runner 或任何机制实现任务。 |
| D1 | 替换方案由 `05_registry/os_program_v1.yml` 独立登记，不属于 context management registry。 |
| D2 | run 阶段编号统一为 `00_任务输入 / 01_需求建模 … 07_测试执行 / 08_结论`。 |

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
3. 阶段 1–4 已有实现 schema，但阶段 5–7 schema、七阶段 validator、transition graph 和
   runner 尚未形成统一可运行合同；
4. capability receipt 最小版已经完成，环境 checker 的 canonical 化及安全边界、审计恢复、
   版本迁移、并发协调等全局机制仍未收口。

准确结论是：第二代 OS 已经是成熟的开发治理框架，但还不是完整的端到端任务运行系统。

### 1.3 P0 遗留项与唯一落点

| 项 | 落点与时限 | 本方案中的处理边界 |
| :--- | :--- | :--- |
| N1 路径形态盲区 8 类 | 新建独立任务 `personal-path-shape-coverage-001`；在 P1 阶段二消费环境证据前完成 | 现有 master 没有可复用的 `.ai/TASKS/personal-path-gate-integration-001.md`，不得把未合入草稿当 canonical；本版只裁定，不扩 schema 正则。 |
| N2 `--mode tracked 08_os` 的 4 处既存命中 | 新建 `personal-path-tracked-baseline-cleanup-001`；在 tracked 模式成为接入门前完成 | 由 core backend 精确处理 run-014 validator 与开发对话日志，保留历史语义并接受独立审核；不在机制任务中顺手改。 |
| N3 registry brace path-set | 纳入未来 `registry-validator-v1-001` | validator 必须确定性支持现有 brace finite-set 语法，或先以独立迁移任务改成逐项 entry；未知语法必须 fail closed，不得静默漏项。 |
| N5 文档缺少第 4 种 checker 结局 | `env-capability-checker-promotion-001` | 与 checker canonical 提升同一任务补入文档。 |
| N6 `schema_only_disagreement` 语义偏宽 | `env-capability-checker-promotion-001` | 拆成“已知 schema-only 合法差异”和“无法解释的 schema-only 分歧”两个 code；两者仍非零退出，后者保持硬失败。 |

run-020 的 `independent_receipt_check.py` 只保留为不可变历史证据。可复用 checker 的 canonical
落点裁定为 `08_os/06_execution/validators/environment_capability/`；提升、回归、registry 同步及
run-020 原件的 superseded 说明都由 `env-capability-checker-promotion-001` 完成，且不得修改
run-020 文件本身。

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

本总体规划文档只裁定阶段边界、依赖和落点，不实现机制，因此获 C2 豁免，不为本文件另造
七阶段 run。该豁免不得被通讯、资源、workflow runner、loader、validator、adapter 或其他
任何机制实现任务援引；这些任务仍必须按活动 workflow 留下阶段产物和审核证据。

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

替换顺序是：新机制完成 → 兼容 adapter → 双读单写或明确单权威验证 → 对应层的 canonical
切换 → 观察期 → 旧 canonical 退役。通讯层在 P1 先切；新 OS 默认活动系统宣告仍留到 P5。
任何阶段都必须有回滚点和明确的单一状态权威。

### 2.6 `06_execution` area-first 布局

`08_os/开发入口与单窗口任务规范_v1.md` §3 的 `06_execution/<area>/<name>/` 是已有
canonical，不是本方案新造的约定。活动落点如下：

- workflow runner：`06_execution/workflow/<name>/`；
- mechanism loader/adapter：`06_execution/mechanisms/<mechanism>/`；
- 通用或可复用 validator：`06_execution/validators/<name>/`；
- boot 目录只保存环境建立和启动入口，不保存 mechanism loader；
- skills/tools 分别进入 `06_execution/skills/<name>/`、`06_execution/tools/<name>/`。

因此 v1 建议的 `06_execution/communication/` 和 `06_execution/resource_management/` 作废；
通讯与资源 loader 分别进入 `mechanisms/communication/` 和
`mechanisms/resource_management/`，environment capability checker 进入
`validators/environment_capability/`。

当前唯一已知偏差是 `06_execution/boot/context_management/` 中放置了 mechanism loader。
它可以在 P1 需求建模期间继续作为历史兼容入口，但必须在 P1 第一次新增 communication loader
的同一实现变更中迁到 `06_execution/mechanisms/context_management/`，同步更新 boot manifest、
registry、引用和回归测试；最迟不得晚于通讯 canonical 切换门。旧路径届时只能是明确的兼容
pointer 或 approved deletion，不能与新路径同时成为 loader 权威。

### 2.7 技术性 kill criteria

不设置例行的阶段冻结复核门，但每个 P 必须在下列条件触发时停止推进：

| 阶段 | kill criteria 与降级结果 |
| :--- | :--- |
| P1 | 在任务修正预算内仍不能证明状态唯一性、事件防重放或真实 rollback：不得切换通讯 canonical，成果降级为 `adapter_only`，core 窗口继续使用旧通讯入口。 |
| P2 | 无法诚实记录关键资源指标或新方案导致证据/质量下降且无法归因：保持 `.ai/TOKEN_USAGE_PROFILE.md` authoritative，新机制只作 measurement candidate。 |
| P3 | runner 无法保持冻结测试、唯一 transition 或可重放 backtrack：不得成为 workflow canonical，继续由既有阶段规格和人工调度运行。 |
| P4 | 任一安全、审计、恢复或发布机制存在不可观测的受保护动作路径：该机制被排除出默认活动声明，并阻断 P5。 |
| P5 | 观察期出现双权威、状态漂移、领域仓误解冻或 rollback 失败：立即回到已验证旧入口，保持领域仓冻结并停止退役。 |

## 3. P1：新通讯机制

### 3.1 目标

在第二代 OS 中建立 provider-neutral、低 token、可审计、可验证的通讯、状态与 handoff 机制，
使一个真实任务能够从派单、执行、审核、定点修复到完成，不依赖旧 `.ai` 通讯 canonical 来
解释当前状态。

建议目标结构：

```text
08_os/03_mechanisms/communication/
08_os/02_boot/communication/
08_os/06_execution/mechanisms/communication/
08_os/05_registry/communication_v1.yml
```

旧 `.ai` 路径在兼容期只作为 adapter 或证据源，不立即删除。

### 3.2 阶段一：需求建模 A

A 必须直接使用
`08_os/01_workflow/01_需求建模/实现/需求建模schema_v1.md`，不得另造 schema，且恰好覆盖
以下十一类需求：

1. Human、前台审核/派单者、后台执行者之间的消息传递；
2. machine pointer、Human operational content、durable Human brief 的结构分离，以及长任务、
   报告、日志和证据只存耐久载体；
3. task、branch、head、status、授权和证据的明确绑定；
4. 状态新鲜度、actor identity、证据与动作授权的分离；
5. dispatch、completion、review、revision、blocked、conflict、Human gate；
6. local Git、GitHub connector、GitHub CLI 等不同传输；
7. 同上下文 fast path 与新上下文完整初始化；
8. 最低充分 token，而不减少独立证据、验证和问责；
9. 单一通讯权威、兼容 adapter、shadow 和禁止双写的边界；
10. P1 完成时全部 core 窗口切换通讯 canonical 的兼容期与 rollback 语义，并明确 Token/资源
    在 P2 前仍由 `.ai/TOKEN_USAGE_PROFILE.md` 路由、workflow 在 P3 前仍用既有规格；
11. 通讯 canonical 切换门与新 OS 默认活动系统宣告门的边界，以及领域仓解冻必须绑定通讯
    观察期通过这一条件。

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
- core 仓内非 `08_os` 任务类型的 dispatch、执行、审核和 Human gate；
- 通讯层切换后 Token/资源与 workflow 仍沿用旧 canonical 的分层边界；
- 从新通讯入口回到旧 bootstrap 的真实 rollback；
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
- 回滚到旧机制的条件和步骤经过真实测试；
- 通过 §7.1 的通讯 canonical 切换门并把全部 core 窗口切到新通讯入口；
- 切换不改变 Token/资源和 workflow 层的活动 canonical，也不解除领域仓冻结。

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
08_os/06_execution/mechanisms/resource_management/
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

旧基线优先来自 `_runs/` 中已经发生的匹配任务，新方案只运行一次，避免同一目标的第二次执行
被缓存、已知路径或已经消解的歧义污染。每个比较必须记录：

- 旧 run 的 immutable ref、新 run 的 exact base 和相同或差异化的验收口径；
- task type、能力档位、质量和证据完整度是否可比；
- Human 往返、token、tool output、wall time、reported cost、质量事故和返工成本；
- 历史字段缺失时明确写 `not_observable` 及原因，不补写估计值；
- 只有关键指标无法从历史恢复、导致核心结论不可判定时，才授权补做对照跑；
- 配对不完美处显式记录，不能把相关性写成因果改善。

“最佳 Token 方案”的定义不是固定预算表，而是根据任务类型、风险、环境和实测数据，动态选择
最低充分资源的机制。

## 5. P3：端到端 workflow 通用实现

### 5.1 含义

端到端 workflow 实现不是再写一份流程说明，而是让系统能够把 Human 的原始需求真正从
阶段一推进到阶段七，生成可校验产物、管理阶段 transition、在失败时退回正确上游，并在
Human gate 停止。

当前新 OS 能很好地管理单个开发任务，阶段 1–4 已有实现 schema，但阶段 5–7 schema、
全部 validator、transition graph 和 runner 尚未补齐，因而还不能统一运行七阶段工作流。

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
├── 00_任务输入/
├── 01_需求建模/
├── 02_信息收集与提炼/
├── 03_结果建模/
├── 04_测试生成/
├── 05_步骤拆分/
├── 06_执行/
├── 07_测试执行/
└── 08_结论/
```

具体目录是否全部需要，应由实际阶段产物决定；不得为了形式创建空目录。

### 5.3 Workflow runner

建议位置：

```text
08_os/06_execution/workflow/citystate_workflow/
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

P1 和 P2 直接使用以下既有实现 schema，不另建平行版本：

- `01_workflow/01_需求建模/实现/需求建模schema_v1.md`；
- `01_workflow/02_信息收集与提炼/实现/证据包schema_v1.md`；
- `01_workflow/03_结果建模/实现/B_schema_v1.md`；
- `01_workflow/04_测试生成/实现/测试schema_v1.md`。

每次运行都必须保留：

- artifact shapes；
- transition decisions；
- stop conditions；
- review correction loop；
- Human decisions；
- token/resource measurements；
- 失败和退回原因。

P3 对账这四份 schema 与两次真实运行，只在证据要求时作版本化修订；不得默认废弃或重造。
P3 新增阶段 5–7 schema、七阶段全部 validator、统一 transition graph 和 runner，把两次运行中
重复、稳定、可泛化的部分提升为 workflow canonical。仅出现一次、依赖具体机制的做法不应
直接写成全局规则。

### 5.5 完成条件

- 阶段 1–4 既有 schema 经对账仍可追溯，阶段 5–7 有活动 schema，七阶段均有 validator；
- transition graph 明确唯一允许转换、backtrack 和 Human gate；
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

P0 已在 `master@0fc7e1c` 建立 environment/capability receipt schema、本机实测和历史 checker
证据。实测 receipt 位于
`08_os/_runs/run-020-环境能力发现最小版/08_结论/环境能力receipt_实测_v1.yml`；它是 P1/P2
输入事实，不授权动作，也不得由本方案重写。后续仍需收口 canonical checker，并至少保持以下
测量范围：

- OS、shell、路径语义；
- 可用工具及版本；
- 模型、effort、mode 和 subagent 可用性；
- repository transport；
- network、filesystem、sandbox、ACL 和 secrets 能力；
- runtime limits；
- 缺失项、不可观测项和失效条件。

环境事实必须测量，不能靠角色名或历史 note 推断。receipt 是事实，不授权动作。

`env-capability-checker-promotion-001` 把 run-020 checker 提升到
`06_execution/validators/environment_capability/`，补齐 N5/N6 并同步 registry；run-020 原件
保持不可变，作为旧行为对照和 provenance evidence。

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

## 7. P5：默认活动宣告、兼容观察和旧 OS 退役

### 7.1 两道不可混同的门

**第一道：通讯 canonical 切换门，在 P1 完成时通过。** 必须同时满足：

- P1 §3.7 的 canonical、boot、loader、registry、validator 和真实跨模型闭环全部完成；
- capability receipt 可用，通讯状态唯一性、重放、冲突和全部 core 窗口场景通过冻结测试；
- 从新通讯入口回到旧 bootstrap 的 rollback 已真实执行并成功；
- compatibility adapter 只有一个写入权威，旧 `.ai` 路径不会独立改变当前状态；
- Token/资源仍明确指向 `.ai/TOKEN_USAGE_PROFILE.md`，workflow 仍明确指向 `01_workflow/`
  既有阶段规格；
- 领域仓继续冻结，解冻条件绑定为“通讯 canonical 已通过兼容观察期”，不得单独批准。

通过第一道门只表示全部 core 窗口的通讯、状态和 handoff canonical 已切换，不表示新 OS
整体接管，也不授权旧系统退役或领域仓解冻。

**第二道：新 OS 默认活动系统宣告门，留在 P5。** 只有同时满足以下条件才可通过：

- 新通讯机制完成真实跨模型闭环；
- 新资源机制完成匹配任务实测；
- workflow runner 完成真实端到端任务和失败退回；
- environment capability receipt 可用；
- security/privacy/access boundary 有明确威胁模型和测试；
- audit/recovery 和 OS release/migration 机制可用；
- bootstrap、AGENTS 和 load profile 已有新 OS 路由；
- domain 仓仍保持冻结，直到 Human 明确解除；
- 回滚到旧入口经过测试。

两道门必须分别形成版本绑定 evidence；第一道门的通过不能复制为第二道门的结论。

### 7.2 兼容期规则

兼容期必须采用单一权威原则。可选模式：

- 新系统单写，旧系统只读 adapter；
- 新系统 authoritative，旧系统接收 shadow mirror；
- 旧系统 authoritative、新系统 shadow，仅限正式 cutover 前的验证期。

禁止双写后让两套系统都能独立改变当前状态。任何 mirror 都必须标记非权威，并有一致性检查。

### 7.3 分层 Bootstrap 路由与观察

P1 的通讯切换任务只修改并验证通讯、状态和 handoff 的启动路由，同时保留 Token/资源与
workflow 的旧 canonical 指针。P5 在其余阶段完成后再更新默认活动系统声明、兼容矩阵和退役
入口。相应任务至少覆盖：

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
- 通讯 canonical 的兼容观察期已有独立结论；领域仓解冻与该结论在同一 Human 决定中绑定；
- Human 明确批准退役和删除范围。

退役后旧 `.ai` 内容可分为：

- compatibility adapter；
- immutable historical evidence；
- superseded design；
- approved deletion。

不得使用“旧”这一标签直接推导可删除。

## 8. 推荐任务顺序

```text
P0  environment capability receipt minimal（已完成：master@0fc7e1c）
  ↓
T2  environment capability checker canonical promotion + N5/N6
  ↓
P1  communication mechanism（完成时通过通讯 canonical 切换门）
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
P5  default-active declaration + compatibility observation
  ↓
Human gate: legacy retirement；domain-freeze release 必须绑定通讯观察期结论
```

每个任务都使用当前 `08_os/开发入口与单窗口任务规范_v1.md` 的单窗口任务包、模型路由、
发布传输矩阵、独立审核和 completion pointer。

## 9. 下一窗口的第一任务入口

本方案通过独立审核并由 Human 合入后，下一窗口先收口 environment capability checker，
不直接写通讯协议实现。任务身份：

```yaml
task_id: env-capability-checker-promotion-001
objective: >-
  把 run-020 的 independent_receipt_check.py 提升到
  08_os/06_execution/validators/environment_capability/，补齐 N5 文档与 N6 分类，
  保留 run-020 原件为不可变历史证据。
risk_tier: T1_standard
expected_outputs:
  - 08_os/06_execution/validators/environment_capability/
  - 08_os/_runs/<new-run-id>/
next_stage: os-v2-communication-requirement-modeling-001
```

checker 收口并合入后，P1 阶段一必须使用既有 `需求建模schema_v1.md` 形成通讯需求建模 A，
目录编号使用 `01_需求建模/`，并停在 Human 对具体 A 版本的确认门。实际 branch、base SHA、
run-id、allowed paths、模型和测试均由各窗口从当前远端 master 重新测量，不得沿用本方案的 SHA。

## 10. 总结

替换程序不是“先补通讯，再把旧目录删掉”。正确路径是：

1. 用新 workflow 完成通讯机制；
2. 用同一 workflow 完成资源机制并测量成本；
3. 从两次真实运行中抽取通用 workflow；
4. 补齐环境发现、安全边界、审计恢复、发布迁移和必要的并发机制；
5. P1 先切通讯 canonical；P5 再宣告默认活动系统，经过兼容观察和回滚验证后，由 Human
   决定旧 OS 退役，并把领域仓解冻绑定到通讯观察期结论。

这样第二代 OS 不只是文档结构替代旧系统，而是用自己的 workflow 建成、验证并最终运行自己。
