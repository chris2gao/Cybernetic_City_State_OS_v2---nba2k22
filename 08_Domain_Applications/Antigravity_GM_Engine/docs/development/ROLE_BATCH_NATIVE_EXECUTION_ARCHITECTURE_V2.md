# NBA2K22 外挂系统 · 身份能力驱动的批量原生执行架构 V2

**架构状态**：Human 于2026-10-28明确的新目标执行链；本文件是**架构规划与接口合同**，不是宣称执行器已经批处理实现，也不改变现有数据采集/SQLite。源码变更与实机操作另按OS阶段授权。  
**继承证据**：[REA最新窗口交接](../../research/rea_native_control/REA_WINDOW_CONTEXT_HANDOFF_20261028.md)、[PR16角色指南](../../research/rea_native_control/ROLE_MODEL_MECHANISM_GUIDE.md)、[PR16真实效果](../../research/rea_native_control/VALIDATION_RESULTS.md)。

## 1. 从“模型提案—人工执行/内存热写”转成“角色能力—批量Native执行”

```text
                        NBA2K22 MyLEAGUE（真实游戏引擎）
                                   │ 原有只读采集与来源校验
                                   ▼
         原有世界数据平台（Native Getter/Decoder、SQLite、历史/同批采集）
                                   │ 数据分析、角色可见裁剪
                                   ▼
         RoleDataView + RoleCapabilityProfile（给定身份/可用动作/取值）
                          ┌────────┼───────────┐
                          ▼        ▼           ▼
                       GM模型   Coach模型    Player模型
                          │        │           │
                          └──────决策/协商/互相同意────────┘
                                   ▼
                   RoleActionBatch（每角色多条精确指令）
                                   ▼
                  Execution Aggregator / Coordinator
        归集、冻结输入/身份/游戏时点、处理重复与冲突报告、依赖顺序
                      （不为角色重新制定业务决策）
                                   ▼
                 Native Control Facade + ActionRegistry
                   按场景解析对象、raw枚举/ABI、Native调用
                      （REA有界线程/进程/业务函数）
                                   ▼
                       NBA2K22 原生服务实际执行
                                   ▼
               每条原生操作状态/关联对象即时读回/效果归档
                                   ▼
                 原有数据采集下一批次读取更新世界事实
```

**数据链暂不重做**：继续以当前有证据的游戏Reader、既有SQLite事实镜像/历史规则、同批身份/可见性与数据分析来源为基础。长期架构V2可另阶段重新设计，但不因本次执行架构修改自行迁移数据库。

## 2. 决策与执行边界（已确定）

| 责任主体 | 必须决定/提供 | 不属于其职责 |
|---|---|---|
| GM模型（每队独立） | 球员及签权资产、双方已同意交易包、合同目标/条款、员工聘任、选秀与球探对象，相关球队管理选择 | Native RVA/ABI/交易提案内存、具体Hook线程 |
| Coach模型（每队独立） | 目标球队/对手、POE/体系/Playbook槽位及CRC、轮换/分钟、训练参数 | Native Gameplan结构、固定“全联盟最优防守”规则 |
| Player模型（各自身份） | 自己的诉求、是否同意合同/角色/训练等，以及其本人获授权的明确游戏操作输入 | 擅自把人格状态写入球员能力/TeamID；替整队GM决定交易 |
| 角色协商/博弈层 | 将涉及多个主体的操作达成一致，并输出已经协商完毕的确切参数 | Frida脚本、执行过程中的业务参数替换 |
| 统一批次汇总器 | 接收所有已提交且通过身份/依赖约束的指令，形成可排序批次、标识重复和相互冲突的目标，反馈各主体进行重新协商 | 评估交易公平、替GM配薪、挑选替代球员、替教练修改战术 |
| Native执行层（Codex职责） | `action_id`→已恢复函数/对象/参数格式→实际调用；返回单项是否执行和游戏当前效果 | 主动挑人、估值、预言游戏策略效果、自动更换参数 |
| 游戏引擎 | 原生执行副作用/返回/允许或拒绝的业务行为、后续比赛与成长 | 外挂人格的策略与长期记忆 |

**交易**：直接`TRADE_EXECUTE_AGREED_PACKAGE`在既有特定场景中通过原生`Process`完成不等薪互换；外围`FullCheck`、外挂工资匹配/公平性判断不再是Native执行器必须追加的决策逻辑。仍要解析真实两队、资产UID、私有提案、调用上下文、对象存在/身份及游戏内部不可规避的错误。不能由此推断所有多方或签权交换已实测。

**球探**：模型决定候选目标，执行器负责精确设置已存在目标或执行获准行程；不先替GM排名。安排Goal与真正消耗球探次数、报告解锁是不同操作。  
**设置类**：执行器提供所有已掌握的枚举名称/原始值/说明，模型自己选择；不评价新值在比赛中最终有何胜率收益。

## 3. “身份能力”要提前提供给角色模型

角色加载`RoleCapabilityProfile`，至少包含：

- `role_type`（GM/COACH/PLAYER）、`actor_uid`、`team_scope`、`save/world/season/phase`；
- 该角色可**读取**哪些数据及隐藏/未球探信息的遮蔽规则；
- 可**申请/执行**哪些Action ID；可操作对象类型及Native可用条件；
- 每个可调项：`value_type`、`allowed_values`或范围、每个值的可理解中文/英文含义、必要参数和游戏已知影响；
- `source_status`：已实机成功特定值、调用链已恢复未测、仅研究候选、不支持；
- `executor_action_id`、`required_context`、`known_effect`、`unknowns`；
- `documentation_version`和`game_build_fingerprint`，避免模型使用过期值域。

需求接口：

```text
list_role_capabilities(role_type, actor_uid, game_context)
describe_action(action_id, role_type, game_context)
get_allowed_values(action_id, target_uid, game_context)
read_role_visible_data(role_type, actor_uid, scope)
submit_decided_actions(actor_uid, role_action_batch)
```

上述是**未来统一合同**，不是在PR #18已实现的REST接口。已有资料源是`docs/game_mechanics`、`ROLE_MODEL_MECHANISM_GUIDE.md`、REA Registry、当前角色可见数据平台。对于未知原生enum要明确`UNKNOWN`，**不能展示成可执行选项**。

## 4. 模型输出“批量指令”，不是每个指令即时执行

外部模型根据已加载身份权限、可见数据和已协商的结果，产生可收集的批次。示例格式（**示意合同，不是现有代码接受该JSON的证明**）：

```json
{
  "batch_id": "worldA-season1-review001",
  "world_id": "worldA",
  "save_instance_id": "saveA",
  "game_phase": "REGULAR_SEASON",
  "data_snapshot_ref": "capture-batch-001",
  "capability_catalog_version": "v2",
  "intents": [
    {
      "intent_id": "cmd-001",
      "issuer": {"role": "COACH", "actor_uid": "coach-x", "team_uid": "team-x"},
      "action_id": "COACH_SET_KNOWN_CURRENT_SETTINGS",
      "target": {"team_uid": "team-x"},
      "parameters": {"RunPlayTendency": 55},
      "dependencies": [],
      "agreement_ref": null
    },
    {
      "intent_id": "cmd-002",
      "issuer": {"role": "GM", "actor_uid": "gm-a", "team_uid": "team-a"},
      "action_id": "TRADE_EXECUTE_AGREED_PACKAGE",
      "target": {"team_a": "team-a", "team_b": "team-b"},
      "parameters": {"players_a": ["player-01"], "players_b": ["player-02"], "picks_a": [], "picks_b": []},
      "dependencies": [],
      "agreement_ref": "both-GMs-agreed-to-package-id"
    }
  ]
}
```

- ID为**语义占位符**，执行前必须根据真实世界线映射原生UID，不能把`team-x`直接当作Native整数。
- 决策模型可以提交多条，汇总器不能暗中合并不同目标值或替两边改交易资产。
- `agreement_ref`用于表明已在**外挂决策/博弈层**完成的协商，不是执行器再做一次工资/能力评估。
- 若角色请求的是合同谈判/换帅诉求而不是已确定游戏状态操作，先作为**外挂消息**由对应GM/Coach处理，不能未经同意直转Native执行。

## 5. 汇总器要做什么 / 不做什么

应做：`collect` → `dedupe exact intent_id` → `detect_same_field_or_asset_conflict` → `confirm_role_and_agreement_context` → `freeze_payload` → `order_by_explicit_dependencies_and_game_phase` → `dispatch_each_native_action` → `record_result` → `publish_current_game_readback`。

不应做：替换球员、寻找合法报价、推荐球探/新秀、计算“最优”战术、自动决定哪位GM赢得资产争议、静默跳过未同意的行动。

发生同一球员同时被不同交易请求占用、同一场景同一字段目标值冲突、合同/签权与前一操作产生关联问题时，标记`CONFLICT_REQUIRES_ROLE_RESOLUTION`并退回原主体；**不能把未达一致的两条命令强行串行执行**。已达共识的跨球队事务只作为**一次Native交易调用**，不拆成两次`TeamID`写。

## 6. 批量执行的真实性与故障规则

- Native动作接口保留`REA NativeActionRegistry`/Facade和现有已证Gameplan、Trade、Scouting机制；不再将旧直接改业务内存列为首选执行后端。
- 执行前作必要`UID/版本/ABI/内存访问/对象归属/游戏阶段`校验；**不要**重建一套GM决策时已经处理的工资公平、阵容策略规则。
- 每条按`intent_id`记录`NOT_EXECUTED`、`APPLIED_READBACK_CONFIRMED`、`REJECTED_BY_GAME`、`UNKNOWN_EXECUTION_OUTCOME`，与原请求一一绑定。若没有确定的Readback，则不能宣称成功。
- 多条批次不是跨整个游戏引擎的ACID事务。部分成功后按已发生事实记录，未执行的继续标未执行；一个成功事务不能被“按批回滚”臆造逆操作。
- 状态不明时不得自动重放、不得向游戏再次提交相同资产交易。游戏原生保存/自动保存由游戏自行负责，本架构不新增Save/Reload研究任务。
- 真实游戏调用仍受当前OS/Human所批准的**任务范围/角色执行权限**约束；加载索引或`allow`配置本身不扩大授权。后续批处理可以由Human一次性批准明确的操作集合，不必人为逐字段重复许可。
- 实际批次调用次数、时间预算、线程绑定、内存边界由Native执行器负责，模型不需要知道RVA。

## 7. 下一阶段的工程完成门

未来Codex先从**最终确认的角色动作列表**开发，不能凭当前62项Registry的现有函数范围自我定义“已完成全域”。一个功能须交付：

1. `describe_action`中人类模型可理解的**功能、允许值与影响/不确定性**。
2. 正确接收外部模型的目标、UID、原生参数并构造实际业务函数调用。
3. 原生函数可用性状态：已实机验证的精确实例与未测输入分开。
4. 对目标游戏对象的读回，以及单条和批次状态报告。
5. 更新`PROJECT_INDEX.md`和`PROJECT_MODULE_REGISTRY_V2.json`中相关模块，链接到具体PR、Evidence与新的已知缺口。

**本PR只规定架构，不实现RoleCapabilityProfile服务、汇总器或Native批处理执行。** 数据底座和已有游戏研究文档不被本轮修改，等Human审定完183项第一轮动作和能力值域再制定新Codex任务。