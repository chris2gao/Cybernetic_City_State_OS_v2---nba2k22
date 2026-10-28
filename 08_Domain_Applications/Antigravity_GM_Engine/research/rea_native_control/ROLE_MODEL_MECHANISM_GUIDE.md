# 给外部GM、Coach、Player模型的机制与执行说明

> **当前角色入口（PR #19工程候选）**：角色先通过`RoleCapabilityService`的`list_role_capabilities`、`describe_action`、`get_allowed_values`加载身份许可和准确参数，再提交逻辑需求ID的`RoleActionBatch`，由`submit_decided_actions`核对host身份、阶段和范围。下文Native action示例用于说明执行器的底层格式，不能替代角色授权。[批次合同](ROLE_BATCH_EXECUTION.md)、[四槽PlayType合同](PLAYER_PLAYTYPE_NATIVE_CONTRACT.md)与[属性/倾向合同](PLAYER_STAT_NATIVE_CONTRACT.md)记录当前接口；完整M0–M5仍未完成，也没有因工程接入而新增实机许可。

适用：本仓库PC NBA2K22离线MyLEAGUE，固定EXE SHA256 `1727ad72085fba39e789ee574fc15aab623ad1651cf6879e95e8cd53b6ffbbf5`。本目录为研发接口候选，实机范围见[验证报告](VALIDATION_RESULTS.md)与[data/native_live_validation.json](data/native_live_validation.json)。角色名称表示使用者，不是原生权限机制。

外挂中的GM、教练和球员模型根据外部数据作决定，GM之间负责协商并检查交易。这里说明机制和确定参数的执行方法；执行器不生成策略、不评估球员、不配平薪资、不在失败后换资产或目标。收到确定请求后，解析当前游戏对象、编码输入、调用原生函数并独立读回。

## 1. 角色模型如何提交

最小请求：`action_id`、`parameters`、用于对应回执的`request_id`。球队使用当前游戏的逻辑`team_id`，球员使用原生`PLAYER UID16`，选秀权使用`PICK UID32`；它们不是姓名、名单槽、球队中文名或UI顺位。外部数据必须保留这些ID与本次存档身份。禁止把另一个存档的同名球员直接当当前对象。

```json
{"action_id":"COACH_SET_KNOWN_CURRENT_SETTINGS","parameters":{"team_id":20,"settings":{"RunPlayTendency":55}},"request_id":"coach-ind-001"}
```

角色模型只交逻辑ID和值；执行者从当前进程解析指针，角色模型不传内存地址。执行前后读取是检查对象及效果，不重新判断经营决策。类型、UID归属、数组长度、EXE/ABI、可读内存和生命周期检查属于正确调用所必需的技术条件；薪资匹配、能力匹配、交易公平性与双方是否同意属于外部决策。

`prepare`和`render`不访问游戏；提供显式启用的管理员REA transport后，`dispatch`才运行。函数返回与实际效果分开：`REJECTED_BY_GAME`保留原输入；`NATIVE_CALL_RETURNED_EFFECT_NOT_TESTED`还需独立读取；缺回执为`UNKNOWN`，先查状态，不能直接重放。`REAL_NATIVE_EFFECT_VERIFIED`只说明该次原生状态发生了预期变化，不等于UI、存盘重载或生产集成通过。

### 1.1 四槽PlayType接口增量

**PlayType增量**：`PLAYER.EDIT.PLAY_TYPE_1..4`各自只允许对应的单槽对象，例如槽位1参数`{team_id,player_id,slot_values:{"1":4}}`。类别0..15有既有PC22名称；共享Native action可处理显式多槽，但单槽角色权限不能越到其它槽。Player还必须匹配自己的`player_scope`。四个专用Setter已有静态恢复和离线实现，UI/模拟/持久化未实测；详见[调用合同](PLAYER_PLAYTYPE_NATIVE_CONTRACT.md)。

## 2. 交易：执行外部已经同意的资产包

使用`TRADE_EXECUTE_AGREED_PACKAGE`或`control.gm_trade(...)`。这是本轮新增的默认执行路径；旧`TRADE_PLAYERS`等动作保留历史完整检查路径，供审计引用，当前GM执行不走它们。

```json
{
  "action_id":"TRADE_EXECUTE_AGREED_PACKAGE",
  "parameters":{
    "team_a":20,"players_a":[7239],"picks_a":[],
    "team_b":1,"players_b":[7716],"picks_b":[]
  },
  "request_id":"agreed-trade-example-replace-with-current-ids"
}
```

上例是本轮已经消费的实测输入格式，不能重复提交；实际效果见验证报告。`players_a/picks_a`从A转给B，B侧反向。输入须完整提供六个键，空数组表示无该类资产。球队必须不同；球员ID整数0..65534，签权ID整数0..4294967294；所有资产合计最多18个原生提案槽。球员必须确实在输入一侧当前名单且当前/合同TEAM关系一致；签权须由原生Getter核对UID和当前归属。同一资产只能出现一次，不能提交空资产包。这里没有“薪资必须接近”或“能力必须匹配”的输入规则。

调用：构造私有1668字节TRADE → 对每个球员`AddPlayer`，对签权`GetByID/UniqueID/AddPick` → 原生上下文Getter `0xbaa7e0` → `int Process(TRADE*,context*,int32*)`，RVA `0x12e93b0`。**不调用外围FullCheck，也不额外调用Validate或旧提交Wrapper**。Process内部固有的资产存在/归属等检查仍可能拒绝，不能承诺任意输入必成功。没有修改函数代码、薪资、合同报价或安全工具。

预期效果是指定资产归属转移；需分别回读双方名单及球员当前/合同球队。原生Process还有自身内部账务/事件处理，本轮未穷举审计全部历史、副作用与自动保存行为。多球员、签权和混合包有恢复的调用逻辑，但单次球员测试不能证明其所有组合。返回非零表示Process接受，最终是否按请求交换以回读为准；不自动恢复。

## 3. 球探：指定候选，与执行考察分开

先用`SCOUT_LIST_CURRENT_PUBLIC_PROSPECTS`取得当前届次的公开UID，用`SCOUT_READ_TRIP_BUDGET`读取指定球队现有Goal及剩余次数。`SCOUT_READ_PROSPECT_INFO`返回身份与原始排名字节，`SCOUT_READ_PROGRESS_RAW`返回该球队对候选的原始点数、workout/medical标记；都不是完整已解锁报告，不提供隐藏能力。

| 要执行什么 | 动作及确定输入 | 原生效果与限制 |
|---|---|---|
| 新增一组指定候选目标 | `SCOUT_ASSIGN_TARGETS {team_id,player_ids,priority_raw?}` | 初始化私有Goal→SetSpecific→Append；最多3个Goal，满槽可原生拒绝，不自动删槽。`priority_raw`若提供为0或1 |
| 明确替换已有目标的候选 | `SCOUT_SET_EXISTING_GOAL_TARGETS {team_id,goal_index,player_ids}` | goal_index为当前存在的0..2；只对这一Goal调用SetSpecific，不追加、不自动执行行程 |
| 执行当前已配置考察 | `SCOUT_EXECUTE_CURRENT_TRIP {team_id}` | 会进入实际考察业务，可能消耗次数和改变进度；本轮未实测，不随分派自动执行 |

目标是**当前选秀届次的DRAFT_PROSPECT**，不是随便一名NBA名单球员。`player_ids`为UID整数数组；新增要求1..17，已有Goal setter的结构允许0..17，空数组的业务用途未实测。不要重复候选。解析到公开候选的真实DRAFT_PROSPECT*后，临时构造指针数组传入 `void SetSpecific(Goal*,count,prospect**)`，RVA `0x1322f30`，不能把PLAYER*直接传入。

```json
{"action_id":"SCOUT_SET_EXISTING_GOAL_TARGETS","parameters":{"team_id":20,"goal_index":0,"player_ids":[33143]},"request_id":"ind-scout-slot0"}
```

读回该槽的focus、数量和UID，并确认其它槽与次数。**已有Goal setter只证明目标记录被设置**：Trip有另一个聚合目标缓存，原版DoScout会重新构建它；本轮不通过消耗行程证明完整消费链。分派成功不等于已经完成考察或新增完整球探报告。本轮的“Append满槽被拒绝”和“明确设置既有Goal”是两次不同请求，分别保留证据。

## 4. 教练：当前可以设置的10项

使用 `COACH_SET_KNOWN_CURRENT_SETTINGS {team_id,settings}` 或 `control.coach_settings(team_id,settings)`。settings可包含下表中一个或多个键；不包含的已知字段从当前Coach保留。`COACH_SET_ROTATION_POLICY`只接受BenchDepth/BenchUtilization，不是首发或逐人分钟表。

| 参数键 | 可传原生值 | 作用含义 |
|---|---|---|
| POEOffense | 0无偏好；1冲击篮筐；2为射手创造空位；3低位进攻；4挡拆；5均衡；6围绕得分手 | 进攻侧重点 |
| POEOffense2 | 0无偏好；7耐心进攻；8均衡节奏；9自由出手 | 进攻节奏倾向 |
| POEOffense3 | 0无偏好；10冲抢进攻篮板；11均衡；12限制对方转换 | 进攻篮板与退防取向 |
| POEDefense | 0无偏好；13保护内线；14均衡；15限制外线投篮 | 防守侧重点 |
| POEDefense2 | 0无偏好；16保守；17均衡；18身体对抗 | 防守对抗取向 |
| POEDefense3 | 0无偏好；19保护防守篮板；20均衡；21发动转换 | 防守篮板与转换取向 |
| RunPlayTendency | UI有历史Human确认0..100；原生存储uint8 | 执行战术频率 |
| ZoneUsage | UI有历史Human确认0..100；原生存储uint8 | 区域联防频率 |
| BenchDepth | 原生uint8；UI端点尚未确认 | 板凳深度，轮换人数上限含义；已观察9、10不代表最大值 |
| BenchUtilization | UI有历史Human确认0..100；原生存储uint8 | 替补球员使用率倾向 |

枚举来自[data/coach_settings.json](data/coach_settings.json)和仓库[coach_tactics_profile.json](../../config/coach_tactics_profile.json)。频率/板凳UI信息是以前的玩家确认，不是本轮重新做UI测试。源码当前验证存储值0..255；不要将整个uint8域解释成UI支持范围。这里只解释选项，不量化它们对胜率、回合、出场时间或具体AI行为的因果影响，相关公式和本轮比赛效果均UNKNOWN。

执行机制：从当前球队解析Coach及默认Gameplan，复制私有880字节Gameplan，保留当前已知Coach投影，只替换输入字段；调用 `void Apply(Gameplan*,CoachData*)`，RVA `0x146eaa0`；核对整个352字节Coach预期投影和原始Gameplan未改，再另开只读会话回读。当前只闭合三个引用槽均NULL分支，非NULL引用所有权/赋值过程未恢复时不调用。

本轮已证明IND/Rick Carlisle的RunPlayTendency **90→55**，其余9项不变。旧实例防守14→13是继承成功；不把这两次推成所有10项、所有球队、长期Gameplan持久性或比赛效果都已验证。

## 5. 已恢复格式、尚未实测的其它机制

| 机制 | 模型需要给定 | 已知效果 / 尚缺证据 |
|---|---|---|
| `TRAIN_TEAM_SET_INTENSITY` | team_id、原生date整数键、value=0..7 | 读取该日训练，保留其它字段，用原生服务设置3bit强度；UI标签、公历转换和当前场景实效待证，不能自动换日期 |
| `TRAIN_TEAM_SET_SCHEDULE` | team_id、原生date、完整training对象 | `percentage_per_focus`:3个有限float32；`profile_per_focus`:3个uint8；`points_per_subfocus`:38个uint8；`intensity_raw`:0..7。编码64字节私有输入调用0x1325f10；游戏可能对比赛日/无记录日no-op。各索引语义及总和约束UNKNOWN，不生成训练策略 |
| `COACH_ENSURE_OPPONENT_GAMEPLAN` | team_id、不同的opponent_team_id | 找到/创建对手Gameplan的原生入口；可能创建记录，非纯读；不等于完整持久计划编辑 |
| `DRAFT_SELECT_PROSPECT` | 当前team_id、实际PICK UID、当届player_id | 已有调用链，必须真实当前选秀场景；可能推进顺位。本轮日历场景不调用，不制造场景 |
| 球员/员工编辑、签约续约、裁员、首发/逐人分钟、完整Playbook、导师 | 尚无完整可执行合同 | ABI、对象生命周期、commit或refresh等存在具体缺口，见ACTION_SURFACE；不能收到一个值就盲目调用 |

Player模型现在可以使用外部系统已有数据作决策，并提出已支持机制的确定请求；本轮没有恢复“任意球员编辑/徽章修改”等原生服务，也没有把游戏自然成长替换成外挂数值写入。

## 6. 执行者需要的数据与交接回执

执行前至少携带：当前游戏构建、存档/会话身份、最新逻辑实体ID、当前模式/页面；交易给双方资产方向，球探给追加或指定既有槽，教练给准确字段键和值，训练给实际原生日期。当前名单/归属变化后须重新解析，不沿用旧指针。执行时需要与管理员游戏相同的权限，使用标准管理员启动。

回执保留原始请求、实际调用链与次数、原生返回、独立回读前后值、其它受检字段、错误或UNKNOWN及原始证据位置。对一次请求不自动改值、追加业务、恢复或重试；缺回执先独立读状态。外部模型根据回执决定下一条请求，本执行器不代替它们决策。

本轮原始证据和例外在[当前验证报告](VALIDATION_RESULTS.md)，全部静态动作在[ACTION_SURFACE.md](ACTION_SURFACE.md)。成熟度按**具体字段/输入组合**登记，存在源码接口不代表实机通过。

### 属性与倾向的角色参数增量

`PLAYER.EDIT.ATTR_SET` / `.ATTR_BATCH`与`.TENDENCY_SET` / `.TENDENCY_BATCH`使用当前球队/球员UID，单字段为`field_id,value`，批量为非空`values`字典。通过`get_allowed_values`加载当前角色的具体字段含义和范围；能力/耐久UI整数25..99，倾向整数0..100，执行器不自动钳位或替模型决定数值。普通GM仅有明确授予的Intangibles例外；其余能力/耐久只向获授权的世界编辑身份开放。48个已命名倾向可按明确授权提供给GM/Coach/Player，Player还须匹配自身UID；51个未命名位置只供明确世界编辑，含义保持UNKNOWN。Potential和未分类能力不开放，徽章仍不可调用。完整参数、原生副作用与未实测范围见[合同](PLAYER_STAT_NATIVE_CONTRACT.md)。

### 徽章的明确联动接口

`PLAYER.EDIT.BADGE_SET`只向明确授权的WORLD_ADMIN身份开放；普通GM/Coach/Player不能自增徽章。通过`get_allowed_values`取得98个非NONE内部名称、每项上限1/4和完整联动组；输入`team_id,player_id,field_id,value,expected_before,expected_after`。两个状态对象必须完整列出可能联动的对或三元组，单独技能则只有一个字段。执行器保留原版flag0规则、检查临时有效等级及断言条件；原版规则与明确after状态不符就拒绝，不改选值或绕过规则。内部名称不等于已认证MyLEAGUE UI选项。详见[徽章合同](BADGE_NATIVE_CONTRACT.md)，目前只有静态和离线证据。
