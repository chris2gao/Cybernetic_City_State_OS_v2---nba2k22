# Codex 探索原型：人可以直接看懂的演示和语义测试

状态：`EXPECTED_FUTURE_PROTOTYPE_NOT_IMPLEMENTED_BY_THIS_PLANNING_RUN`。这些是**待开发输入/输出契约示例**，不是游戏实测和伪造测试日志。Codex可根据仓库语言、框架和真实业务证据调整命名、字段、文件架构，只要**行为语义不降低**。

## 1. 人可观看的“原型纵切”

最小demo需要让Human清楚看到这样的终端交互：

```text
$ <codex-chosen-cli> knowledge show AI_COACH_DEFENSE_M1
subject: AI-controlled Coach
game_scope: PC22 / offline MyLEAGUE
fact: [Only evidence-proven game semantics here; current unknown remains UNKNOWN]
why_choose: [example reasoning only if evidence supports it]
can_reason: YES (with evidence/unknown qualifiers)
can_execute: NO (until qualified backend and authorization)
evidence: E-...
$ <codex-chosen-cli> action simulate --fixture fixture/coach_setting_case.json
intent: COACH_SET_DEFENSIVE_SETTING (synthetic example, not a proven 2K22 native call)
actor_control: AI
native_backend: UNQUALIFIED
memory_backend: OWNED_FIXTURE_QUALIFIED_ONLY
route: VALIDATED_MEMORY_WRITE_FIXTURE
game_target: false
affected_state_checked: [the synthetic state fields]
result: FIXTURE_ONLY_PASS
$ <codex-chosen-cli> action assess --source game_unknown/coach_setting
native_backend: NOT_QUALIFIED
memory_backend: NOT_QUALIFIED
route: NO_SAFE_PATH
game_target: false
result: NOT_EXECUTED
reason: Need original AI callsite and current-game field/consumer/readback evidence.
```

**这段命令格式不是已存在CLI**；禁止将其复制为真实运行回执，未来需由Codex实际运行并提供机器可检验记录。原型的重点是让Human看见知识与执行能力**相互独立**，以及可追溯的“为什么选这种后端/为什么阻断”。

## 2. 可执行语义负例——写成测试，但不捏造游戏数据

| 测试ID | 诱导错误 | 必须看到的程序行为 |
|---|---|---|
| PROTO-N01 | AI角色查询Player专属MyCAREER徽章解锁规则 | 作为当前PC22 MyLEAGUE AI成长事实时拒绝 |
| PROTO-N02 | 只有Native类型字段名，没有实测实例/消费者 | 机制卡`L1`且行动不可用 |
| PROTO-N03 | 教练UI设置写入成功，但AI比赛消费者未知 | 知识留`stored_only`，不得上报游戏已生效 |
| PROTO-N04 | 玩家确认交易函数当作AI-AI交易函数 | `HUMAN_ONLY_EXCLUDED` |
| PROTO-N05 | AI模型代表球队，但游戏控制标志仍Human | 拒绝`AI_AI_PATH_PROVEN`并明确控制权冲突 |
| PROTO-N06 | Native函数未资格验证，MemoryWriter也只是历史参考 | `NO_SAFE_PATH`，绝不盲写 |
| PROTO-N07 | 自建Fixture调用成功 | Receipt必须含`game_target=false`，游戏L4不可提升 |
| PROTO-N08 | 原生与内存Fixture产生不同受影响对象集合 | 路由不得声明两后端等价 |
| PROTO-N09 | 有证实机制知识但执行两条路均不可用 | 知识可读且行动保持`NOT_EXECUTED` |
| PROTO-N10 | 调用返回成功而最新游戏状态不一致 | 结果`EXECUTED_BUT_UNVERIFIED/FAILED`，不是成功 |
| PROTO-N11 | Human未授权当前真实游戏注入/Hook/函数写入 | 无进程附加或副作用的动作发起 |
| PROTO-N12 | 给GM/Coach/Player普通知识库注入无权限Native隐藏字段 | 分发拦截而内部证据保留 |
| PROTO-N13 | 交易仅球员队伍ID变化，薪资/合同/选秀权一致性未知 | 不把它当完整AI-AI交易提交 |
| PROTO-N14 | 把同一个Codex旧Run的两份文件计作独立游戏实证 | 标识`SINGLE_ORIGIN`而非`INDEPENDENTLY_CONFIRMED` |

测试应在阶段演示运行记录中体现至少几个最承重负例；不要求为每个字段生成机械匹配断言。**追加至少两条Codex自己从真实工程发现的负例**（例如字段缓存、负值语义、AI设置覆写、游戏build差异），若无发现明确`NO_NEW_CASE_FOUND`且列探索范围。不可通过删除或削弱断言来制造绿灯。

## 3. 知识的真正可用性示例

请给一个将来`Coach AI`可阅读的自然语言知识卡样本，其中清楚分开：

- **已证游戏事实**：有原始Evidence、build/AI场景、合法值/作用（若已证）；
- **研究假说**：历史指南或推断，不作为行动依据；
- **决策指导**：在什么比赛场景适用的建议，说明哪部分是模型策略而非游戏原版算法；
- **行动可用状态**：可只读、可建议、可由已认证后端执行、未准许/未证；
- **使用限制**：控制权、缺少消费者、时效性、敏感字段可见性。

就算原生game消费函数未被证明，也要给出`FieldSemantics / UNKNOWN / NextEvidenceRequired`的有用知识说明，而不能只复制反编译命名。GM与Player角色使用同一Schema但必须保留角色差异。

## 4. 路由算法可接受伪码（非最终实现限定）

```text
validate(actor AI scope, build, object identity, business preconditions)
if qualified_native_backend AND exact_current_action_authorization:
    try native function → fresh game readback → verify all applicable invariants
elif qualified_memory_backend AND exact_current_action_authorization:
    try guarded memory write → fresh game readback → verify all applicable invariants
else:
    return NO_SAFE_PATH / NOT_EXECUTED, keeping knowledge readable
```

合格Native和Memory能力是**两个不同的证据结论**，不能由`auto`兜底来替代。即使后端选择合格，当前动作没有Human执行许可也必须拒绝执行，但可计算“理论上可行”的模拟路线。若Native实际调用失败，**不能在未知副作用后不经检查自动重试Memory**。

## 5. 人类看原型的验收提问

- 这张机制卡明确回答“这个字段在游戏里是什么意思、为什么要这样改”了吗？还是只列字段名？
- 我们实际找到的是AI调用链还是玩家UI事件？
- 一个AI人格只拥有知识权限时，是否会误触发读写游戏？
- Native不能调用时，究竟有哪些理由支持Memory写入，而不是“以前能改”的惯性？
- 自建Fixture的PASS和真实PC22的PASS是否分开展示？
- 除了原计划三个代表性领域，Codex是否发现了值得后续投入的第四个机制？价值、证据和成本是什么？

**期望**：让Human用真实研发成果而不是只看表格列数，判断原型能否服务预期游戏玩法。
