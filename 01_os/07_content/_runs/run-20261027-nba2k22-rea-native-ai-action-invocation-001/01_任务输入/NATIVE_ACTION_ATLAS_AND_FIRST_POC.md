# Codex最小技术回报格式｜Native Action Atlas + 首个真实函数调用

本文件只是Codex执行任务的**可读对照**，不要求先写完文档再开发；所列函数/参数为**尚待实证的目标**，不是已经存在或能调用的事实。

## 1. Native Action Atlas（最少每类一条、允许UNKNOWN）

| ID | 领域 | 外部意图示例 | 优先研究对象 | 实机调用证据 |
|---|---|---|---|---|
| C1 | 教练防守/进攻设置 | `SET_POE(team, defense=PROTECT_PAINT)` | 已知COACHDATA字段→**改变字段的原生Setter**→游戏状态 | UNKNOWN |
| C2 | 轮换/战术/训练 | `SET_ROTATION(team,player,minutes)` | AI球队轮换Manager/共享业务服务 | UNKNOWN |
| C3 | 球员属性/倾向/徽章 | `SET_PLAYER_ATTRIBUTE(player,attribute,value)` | AI成长/训练或共享原生属性应用函数；不要假定AI直接编辑全部数值 | UNKNOWN |
| C4 | AI–AI交易 | `TRADE(teamA,teamB,assets)` | AI交易实际validator/commit与共享事务核心 | UNKNOWN |
| C5 | 签约/续约 | `SIGN(team,free_agent,contract)` | 原生合同/市场业务提交 | UNKNOWN |
| C6 | 选秀/选秀权 | `DRAFT(team,pick,prospect)` | 原生AI选秀选择/状态提交 | UNKNOWN |

按实际研究对每项最少填写：

```yaml
action_id: C1-SET-POE-DEFENSE
target_game: PC22_OFFLINE_MYLEAGUE
mechanism_category: NATIVE_AI_DISPATCH | SHARED_NATIVE_ENGINE_SERVICE | HUMAN_UI_ONLY | UNVERIFIED
external_input_contract: {team_id: int, defense_enum: int}
native_function:
  function_locator: RVA_OR_SYMBOL_OR_OBJECT_METHOD_SOURCE_REQUIRED
  inferred_or_confirmed_signature: UNKNOWN
  ABI_this_thread_lifetime: UNKNOWN
  actual_AI_caller_proven: false
  shared_game_service_proven: false
real_game_POC:
  status: NOT_EXECUTED
  authorization: PENDING_FOR_FIRST_EFFECTFUL_CALL
  before: UNKNOWN
  after: UNKNOWN
  effects: UNKNOWN
fallback_existing_memory:
  known: true
  native_replacement_qualified: false
next_best_experiment: TRACE_SETTER_OR_VALIDATED_NATIVE_CALL
```

`POE 13=PROTECT_PAINT` 已是上一轮当前构建的类型/数值候选，仍须针对被操作的具体对象和方法上下文核查。其`原生Setter函数`**目前尚未定位**；不能因之前的`GetOpponentGameplanIndex`而宣称已经找到修改入口。

## 2. 首次成功PoC必须呈现的最小证据

```text
Game Build / Test Save / Date / Scene / AI or shared native action provenance
Object identity and object life/readable mapping
Action: TEAM_X COACH SET_DEFENSE_FOCUS value=13 (or better low-risk action)
Located game-owned function/method, signature confidence, ABI context
Native invocation attempt count and elapsed time
Before(game): [relevant POE/current setting]
Call(game): [real native call address by RVA/private local, invocation return/exception]
After(game):  [fresh current state reading, unchanged unrelated bits]
Result: REAL_GAME_EFFECT_VERIFIED or EXECUTED_UNVERIFIED or NOT_EXECUTED
Limits: whether call came from proven AI path or verified shared engine service
Cleanup: REA script detach, game survival, test save policy
```

如入口并非原生函数而只是直接写入一个字节，必须标记`MEMORY_WRITE_ONLY_NOT_NATIVE_ACTION`，**不能冒充达成本轮目标**。如因窗口/权限不能进行live调用，提供足以说明下一步最优实验的函数/参数/上下文和未通过哪一级资格，而非一页“安全原因未知”。

## 3. 成功的对照不是AI战术收益研究

对于C1，不要求预先证明比赛防守选择、篮板率或内外线效率变化。只要真实游戏接收设置并证明**原版机制完成了这项业务动作**，就已达到本次原生Setter PoC目标。

对于C4–C6，原版本身的交易、签约、选秀属于关系性事务，**因此**“完成业务动作”的定义包含其原生要求的最小关联对象一致性（而非单指针修改），这不是深度策略效用研究。

## 4. 优先解决的上一轮结构误区

- 原研究以`AI_gameplay_consumer`为主线，现在必须先找`mutator/Setter/Command/Commit`；consumer仅用于证明动作是否真应用。
- STAFF池范围/352步长/引擎AI Controller均应作为带来源的适用性假说；已批准有界只读探索不应被未知身份前置假设硬阻断。
- 共享业务Native方法可能不要求`engine_control==AI`才能合法设置目标对象：需按实际代码证据确定，**禁止在未调查函数前给所有方法加绝对AI Controller守卫**。
- Frida`NativeFunction`/Interceptor只是技术手段，不等于REA已经证明参数签名和调用时机。
- 工具`return true`、Python状态字典模拟或值写入但原版事务没有生效，均不构成Native成功。
