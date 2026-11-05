# Human · NBA2K22 赛季闭环测试操作手册 v1

任务：`NBA2K22-LIVE-HOST-CLOSED-LOOP-INTEGRATION-20261102-001`
**这是开发目标中的约定触发协议，不表示 Host 已经上线。** 只有执行者完成 S1/S2 后，以下命令才能直接驱动真实工具；在此之前，它们用于向 Codex/Gemini 表明 Human 具体希望执行的阶段，不得跳过现有验证门。
默认：用户手动在 NBA2K22 日历里进行模拟，Host 只读核验进度并调用获准的采集/REA。
*用户无需预先决定“已恢复旧档还是新档”——初始化时必须只读确认当前存档、世界线和游戏日期；用户可以在命令里指定偏好。*

## A. 第一次启动：绑定并做完整初始快照

```text
启动 NBA2K22 赛季闭环测试。
存档：当前游戏正在使用的存档（可能是已恢复旧档，也可能是新档，请只读检测并核对）。
模式：先运行4轮试点，每轮推进7个游戏日。
首次操作：只读环境/数据库/世界线检查，初始化独立测试历史，然后采集全量数据。
决策范围：GM、教练、球员都可提出候选意图。
实际写入范围：默认不自动执行；目前仅将已实机验证的 PLAYER_PATCH_TENDENCIES / SHOT_TENDENCY 作为候选。
要求：报告游戏日期、存档实例、数据库位置、实际采集家庭、行数与耗时，再进入第一轮决策。
```

如果当前存档回到了旧数据库已记载的“未来时间”，Host 必须新建分支世界线/隔离的数据库绑定，不能直接沿用旧观测作为当前事实。不需要额外询问已经在游戏里可读取的 PID/日期。

## B. 完成一轮采集并生成决策（只读，不执行 Setter）

```text
开始第1轮赛季决策。
先确认当前游戏日期与上轮数据快照是否一致。
读取最新 WorldData、可用的球员卡高阶统计和最近7个游戏日的日历模拟结果。
让 GM、教练、球员分别生成有依据的决策候选，逐条写入 Decision Outbox。
只展示决策摘要、预计修改的对象/字段/旧值/目标值、原因、证据来源、冲突、未支持动作和下一轮验证指标。
不要修改游戏；等待我审核计划。
```

第1轮替换为第N轮即可。**模型如果只有分析建议而没有真正由角色/Host 认证的决定，不得伪造 ActionIntent。** 若条件不足，可提交明确的 NO_CHANGE/NOT_CAPTURED 结果。

## C. 封存决策并获取 Digest（只读）

```text
冻结第1轮决策，完成执行前预检。
按角色权限和依赖规则验证 Decision Outbox，生成不可变计划和 plan_digest。
重新读取游戏里每个拟修改字段的 Native Getter，检查 CAS 和玩家/球队身份。
把每条将真实执行、No-op、不能执行和有冲突的意图分别列清楚。
只报告计划与风险，不调用任何 Native Setter。等待我确认。
```

冻结并不代表“全部意图已允许真实执行”。未知/未成熟的交易、教练、球员属性等动作保留 NOT_EXECUTED 或待进一步审批。

## D. 真正授权执行一轮（唯一真实修改许可入口）

```text
授权执行第1轮已封存的计划。
plan_digest：<复制上一步实际返回的完整摘要>
实际执行范围：仅限本轮清单中已认证的 SHOT_TENDENCY 项目。
执行规则：使用已有 REA 单 Session、多 Chunk，执行前确认最新存档和 Getter 原值。
每条只尝试一次；UNKNOWN/CAS mismatch 立即停止，不自动重放或自动恢复。
完成后自动核对原始 Native 回执、Journal 和独立 Getter，并将真实结果写入 Decision Outbox。
不要推进游戏日历；给我本轮执行耗时、成功/未执行/失败明细。
```

只有当上一步实际返回 digest，且 Host 已进行当前世界线和授权范围核验后才执行。上面的 `<...>` 是用户必须从正式计划复制的占位符，绝不可使用示例值冒充授权。

## E. 用户在游戏中模拟日历，然后进入下一轮

```text
我已在 NBA2K22 游戏界面完成日历模拟。
请检查当前实际游戏日期、比赛完赛状态和最新进程/存档上下文。
进入第2轮：按7游戏日周期触发采集新增的全量数据，验证 SQLite 数据和前一轮修改结果，然后生成新一轮 GM/教练/球员决策候选放入 Outbox。
不要自动执行 Native Setter，先给我决策摘要。
```

这条文本无需填写日期；Host 以游戏真实读取为准。如日期未推进、新比赛未完成或读取到正在进行的比赛，返回 `SAME_STATE_REPEAT/INCOMPLETE_GAME_IN_PROGRESS` 和原因，不伪造新采集；如果已经有设置改变但无新完赛比赛，用户可额外要求 `强制按当前状态做只读采集`，Host 需明确采用 FULL/force 与新鲜度语义。

## F. 查看进度、暂停和继续

```text
查看当前 NBA2K22 赛季闭环状态：当前游戏日期、已完成轮次、最新 WorldData 快照、Outbox 状态、已执行动作、未执行/UNKNOWN 和最近7天的结果证据。
只读查询，不修改游戏。
```

```text
暂停赛季闭环测试。保持现有 Outbox、已冻结计划、数据库历史和 Journal，不执行新的 Setter，不推进游戏。
```

```text
继续赛季闭环测试。先核对实际存档、世界线、游戏日期、上次未完成/UNKNOWN 状态与运行日志，再从安全检查点继续；不自动重试未知结果。
```

## G. 四轮通过后扩整赛季

```text
四轮试点通过后，将本次已绑定的 NBA2K22 世界线扩展为整赛季测试。
常规赛按每7个游戏日安排一个采集与决策周期，交易截止日、全明星、季后赛系列结束、休赛期关键节点增加事件检查点；同日合并重复采集。
目标20–40个有效观测周期/赛季，不盲目凑次数。
每轮由我在游戏中完成日历模拟并发出继续指令；任何真实写入仍需本轮正式 plan_digest 的授权。
维护赛季日志，记录每轮采集耗时、角色决策、Native 写入和之后的比赛表现。
不要在无人触发时自动推进游戏或执行下一轮。
```

## H. 如需主动选择新档/恢复档

- 老档：`初始化时使用我已经恢复的 MyLEAGUE 存档；若发现数据库已有将来的历史，请生成独立 worldline 分支，不覆盖旧事实。`
- 新档：`我已进入新的 MyLEAGUE 存档，请从零初始化新的世界线和数据库绑定，旧历史保留且不要混入新档。`
- 强制初始 FULL：`采集全量数据。`（允许该世界线当前状态的全源刷新；并非许可改变比赛状态）
- 后续比赛后 INCREMENTAL：`采集新增的全量数据。`（尊重完赛检测与年份跳过机制）

## I. 固定每轮验收回执

每轮 Host 给 Human 至少一份简洁摘要：
`cycle_id | game_date_before | game_date_after | save/worldline/epoch | snapshot/refresh_id | capture_wall_seconds | latest_final_games_count | outbox_intents_total | conflicts_count | sealed_digest | live_authorized_intents | setter_success | noop | unsupported | blocked | unknown | independent_readback | next_proposed_game_date | evidence_refs`。

所有原始 Native、SQLite、WorldData recency evidence 以 Run/Outbox/Journal 指针保留，避免每轮将千条原始 JSON 全部发到聊天窗口。

## J. 成熟度声明

- 已认证：现有 Player SHOT_TENDENCY 真实批量 Setter 的100项10.32s及独立读回；WorldData Player Details 84.65s 单 Family 实机优化；Outbox 离线完整闭环。
- 尚待完成：新 Host 真实接线、四轮带 Human 的端到端实机赛季测试；所有角色/Coach/交易/签约全动作实机覆盖。
- 已授权：Human 自主选择日历推进和赛季测试节奏；真实 Setter 必须以本轮独立计划与指令限定，不能拿泛化的“随便测试”代替清晰的写入范围。
