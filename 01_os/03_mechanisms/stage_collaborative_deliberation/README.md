# 阶段协同推演与增量再确认机制

这是一个全局、按条件调用、默认休眠的协同建模机制。它在承重目标、语义、证据、方案、风险、异议、权责或版本有效性不足以支持可靠决定时，建立可追溯追问与有状态讨论；在不需要时保持休眠。

## 当前集成与激活边界

本目录包含公共方法、阶段 profile 契约、七个阶段 profile、精确依据材料、结果对象与状态/不变量契约、路由与失败契约、加载与 receipt 契约、激活状态、validator 及测试 fixture。对应 boot、registry、loader 和七个 workflow reference 位于各自 canonical 区。

当前全局状态为 `active_dormant`：机制已可被七个 workflow 阶段发现、加载并评估触发条件，但默认路线仍为 `dormant`，不会自动创建讨论 session。只有命中当前 profile 的条件并满足任务级 start gate 与权限要求时，才进入 full 或 incremental；全局激活不替代外部行动授权、不可逆操作授权或当前任务的其他 Human 门。

当前运行状态的权威记录是 `激活状态_v1.yml`；本次任务范围内的契约修订不改变该激活记录。正文修订后的实际 blob 必须同步到当前 boot 与 workflow 引用，历史指针不改写。其中历史 `staged_inert` candidate-state 字段仅表示激活前候选状态，由该 append-only 激活记录对当前运行状态作明确后继解释。

## 核心判断

模型完整性不等于“字段已经填满”。缺口判断由四层模型空间共同决定：

1. 通用建模 substrate；
2. 当前 workflow stage 的 required model fields 与门；
3. 当前任务的目标、成功条件、下游消费方、风险与权限；
4. 前三层不足以表达承重维度时的领域专用 schema。

凡可能改变目标、决定、风险、测试、授权、依赖、版本有效性或下游验收的维度，必须满足以下之一：

- 以有依据的值被表示；
- 带理由与范围被明确判定为无关；
- 作为未知项被阻断或耐久延期，并给出重访触发器。

只检查字段存在性、把模型自信当成现实不确定性、或在 schema 充分性未知时继续推进，均不允许通过。

## Canonical 组成

- `方法论_v1.md`：激活、建模空间、缺口识别、追问、讨论、停止、变更与权责方法；
- `阶段profile契约_v1.yml`：阶段 profile 的机器可读字段与不变量；
- `阶段profiles_v1.yml`：当前七个 workflow 阶段的 profile 集，默认路线均为 dormant；
- `激活状态_v1.yml`：当前全局 active-dormant 状态、Human 授权、后继解释与回滚目标；
- `依据材料/`：需求、证据、结果契约、方案、测试与 Human 授权的精确来源清单；
- `实现/`：结果对象、状态转换、路由失败、加载 receipt、validator 与 fixture。

## 运行原则

普通、可逆、范围内工作以当前 Human 任务输入及持久任务范围为基础，不因换阶段重复要求已覆盖的
Human 确认，也不新建 task authority code、nonce 或 delegation chain。现行政策见
`01_os/05_registry/repository_publisher_authority_v1.yml`。新承重决定超出已有委托、未覆盖的受保护
动作和独立最终验收仍分别保留其门；普通实例通过不代表审核通过或允许 master 集成。
旧 authority helper 仅用于显式历史输入或对已存历史证据的核验，不是新普通实例的隐式备用路径。
讨论是否继续由实际承重缺口与就绪证据决定，不设固定轮次下限。

- reference-not-copy：阶段只引用 profile，不复制机制正文；
- default dormant：全局可加载不等于每个任务自动进入讨论；
- reasoned disposition：票数或模型数量不能代替对异议的理由化处置；
- authority separation：事实支持、共同理解、偏好、决定、授权、执行、审核和验证分开；
- append-only change control：已确认版本通过后继产物、影响分析和再确认更新；
- fail closed：缺失、部分、陈旧、未知、无效或未授权时阻断；
- no self-review：执行者自检不能代替独立审核；
- no automatic authority：测试通过、模型一致或全局激活不能自动授权外部行动、不可逆操作或其他任务执行。
