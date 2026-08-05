# 阶段协同推演与增量再确认机制

这是一个全局、按条件调用、默认休眠的协同建模机制。它在承重目标、语义、证据、方案、风险、异议、权责或版本有效性不足以支持可靠决定时，建立可追溯追问与有状态讨论；在不需要时保持休眠。

## 当前集成边界

本目录包含公共方法、阶段 profile 契约、七个阶段 profile、精确依据材料、结果对象与状态/不变量契约、路由与失败契约、加载与 receipt 契约、validator 及测试 fixture。对应 boot、registry、loader 和七个 workflow reference 位于各自 canonical 区。

当前状态为 `staged_inert`：代码与引用可以被静态验证，但机制尚未 activation。把本机制接入 master 只建立可发现、可验证的休眠候选，不自动改变任何 workflow 的运行行为；activation 必须另行获得 Human 精确授权。

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
- `阶段profiles_v1.yml`：当前七个 workflow 阶段的 staged profile 集；
- `依据材料/`：需求、证据、结果契约、方案、测试与 Human 授权的精确来源清单；
- `实现/`：结果对象、状态转换、路由失败、加载 receipt、validator 与 fixture。

## 运行原则

- reference-not-copy：阶段只引用 profile，不复制机制正文；
- reasoned disposition：票数或模型数量不能代替对异议的理由化处置；
- authority separation：事实支持、共同理解、偏好、决定、授权、执行、审核和验证分开；
- append-only change control：已确认版本通过后继产物、影响分析和再确认更新；
- fail closed：缺失、部分、陈旧、未知、无效或未授权时阻断；
- no self-review：执行者自检不能代替独立审核；
- no automatic authority：测试通过或模型一致不能自动授权执行、激活或集成。
