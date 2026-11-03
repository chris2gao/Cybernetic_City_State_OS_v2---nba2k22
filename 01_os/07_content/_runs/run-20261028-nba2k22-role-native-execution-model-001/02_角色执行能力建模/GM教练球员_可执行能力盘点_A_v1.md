# NBA2K22 MyLEAGUE — GM、教练、球员原生执行能力盘点 A-v1（供Human审阅）

**规划日期**：2026-10-28  
**固定研发生效来源**：PR #17集成提交`84195f47`（master尚未合并）。  
**目标**：把“外挂角色不必思考执行原理，只需提供明确对象和值即可参加联盟经营/执教/球员职业活动”所需要的所有游戏动作逐项列清。**本文件不是已实现功能清单，也不是新的Codex开发/测试授权。**

## 1. 功能模型的边界

- **GM模型**作球队选择、球员资产交易协商、合同报价与签约目标、员工和球探分配、选秀人选及球队经营决定；执行层只是接收对象UID及参数执行。**绝不自动配平薪资/挑另一位球员、重算交易、替换报价或寻找最优战术。**
- **Coach模型**决定具体体系、战术槽位、四槽Freelance、个人防守、阵容、分钟和训练；执行层只修改指定游戏设置，并返回现有游戏状态与结果。比赛效果的深层策略模型后置。
- **Player模型**的转会诉求、合同选择意向、上场角色/训练建议，首先是**对外部GM/Coach的确定消息**，不是自动改游戏属性或TeamID。只有当原版游戏确有独立的角色业务动作时才映射Native；管理员编辑球员能力属于另一类明确的世界修改命令，不能默认为所有Player人格均可自行改能力。
- **World Admin/Season Controller**推进日期、比赛、赛季和调整世界设置。这些是三角色参加完整联盟的环境依赖，默认不授予任何单一球队人格。
- **读取能力**：40组历史能力数据研究和12类当前REA Reader另列下文，不视为已全量打通。
- **跨平台来源**：统一以联盟经营业务功能为规划领域，旧跨年份/机型资料用于搜集动作，不再以差异提醒排除能力；实际外部调用所需Native参数/ABI以PC22代码为准。

### 统一输入→执行合同

```text
GM / Coach / Player 决策模型:
    action_id + save_id + team_id/player_uid/staff_uid/prospect_uid/pick_uid
    + exact_target_values + optional game_phase
        ↓
NativeControlFacade:
    resolve_current_game_object → serialize_exact_native_args → native business call
    → fresh read of affected game objects → return result
        ↓
Outcome:
    APPLIED / GAME_REJECTED / UNRESOLVED_BINDING / CONTEXT_NOT_READY / RESULT_UNKNOWN
```

**必要参数校验**：对象UID、归属关联、枚举、物理容量/ABI/当前函数生命周期；**非执行层职责**：薪资谈判、资产估值、交易配平、选秀评分、教练战术优化。游戏Native内部固有规则仍可能拒绝，不宣称任何输入必成功。一次未知结果禁止自动重放。

## 2. 当前覆盖数量及成熟度

| 类型 | 数量 |
|---|---:|
| 原子操作/角色请求/世界操作（第一次需求种子） | **183** |
| 领域组（按完整联盟生命周期重新拆分） | **14** |
| 可映射到现有REA Registry的需求条目 | **50** |
| 尚无明确一对一REA Action映射的需求条目 | **133** |
| 历史研究的数据范围组 | **40** |
| 已登记REA数据读取dataset | **12** |
| 已宣称完整覆盖的REA dataset | **0** |

> 映射数不是“已实现功能数”。一个Native handler可以实现多个参数，反过来同一业务动作可能需要多个函数。现有62条REA实现目录不等于完整183条需求。下面表里的`LIVE_EXACT`仅指具体样例已有实机证据。

**成熟度解释**：`LIVE_EXACT` 指此前某个固定输入成功；`STATIC` 指静态调用链已恢复但该动作待实测；`PROJECT_NATIVE` 指原生字段/枚举研究存在但执行链未闭合；`PARTIAL` 有局部ABI或逻辑；`RESEARCH` 表示历史资料有业务操作线索；`EXTERNAL` 表示外挂模型交互；`WORLD_EDIT` 独立世界编辑；`READ_SUBSET` 表示只有部分读取能力。

## 3. 已有 Native 里程碑：不能丢弃，但不能扩大

| 明确业务功能 | 已验证范围 | 代表调用 / 当前限制 |
|---|---|---|
| 教练防守设置 | 指定Coach 当前POEDefense 14→13 | `COACH_APPLY_DEFENSE_POE`；仅本次存值效果 |
| 教练新字段 | IND `RunPlayTendency` 90→55，其余9项不变 | `COACH_SET_KNOWN_CURRENT_SETTINGS`；其余字段仍应逐项标注 |
| 直接原生交易 | 一笔指定两队、一换一不等薪资交易成功 | `TRADE_EXECUTE_AGREED_PACKAGE`→Native `Process`；签权/多资产组合尚待实际验证 |
| 已有球探目标修改 | IND Goal0设为指定候选UID33143 | `SCOUT_SET_EXISTING_GOAL_TARGETS`；不等于已完成实际考察或报告解锁 |

在原先已成功的一对一正常交易之外，不需要重复证明交易的工资合法性、交易返回收据或自动存档；执行层只执行GM输入的已同意资产包。

## 4. 逐条执行动作需求（14组）


### GM：名单、阵容与人员归属（12项）

| 能力 ID | 要执行或读取什么 | 外部模型提供的输入 | 原生预期结果 | 当前级别 / 已有关联 |
|---|---|---|---|---|
| `GM.ROSTER.LIST_MOVE` | 指定球员进入/离开球队有效名单 | `team_id`、`player_uid`、`roster_slot`、`destination` | 原生名单归属变更 | RESEARCH |
| `GM.ROSTER.STARTER_SET` | 指定首发五人 | `team_id`、`ordered_player_uids`、`positions` | 更新首发 | PARTIAL / `TEAM_SET_STARTERS` (NOT_FOUND_WITH_SEARCH_SCOPE) |
| `GM.ROSTER.BENCH_ASSIGN` | 指定替补及候补 | `team_id`、`player_uid`、`role` | 更新替补角色 | PARTIAL |
| `GM.ROSTER.POSITION_ASSIGN` | 指定球员位置或副位置 | `player_uid`、`primary_position`、`secondary_position` | 更新球员位置 | RESEARCH |
| `GM.ROSTER.ROLE_ASSIGN` | 指定球队角色/定位 | `team_id`、`player_uid`、`role_id` | 更新角色字段 | RESEARCH |
| `GM.ROSTER.ROSTER_SLOT_SWAP` | 名单槽位调换 | `team_id`、`from_slot`、`to_slot` | 调换名单排序 | RESEARCH / `TEAM_SET_ROSTER_ASSIGNMENT` (NOT_FOUND_WITH_SEARCH_SCOPE) |
| `GM.ROSTER.G_LEAGUE_ASSIGN` | 下放G League | `team_id`、`player_uid` | 更新所属及双向关系 | RESEARCH |
| `GM.ROSTER.G_LEAGUE_RECALL` | 召回G League球员 | `team_id`、`player_uid` | 回归球队名单 | RESEARCH |
| `GM.ROSTER.INACTIVE_SET` | 设置激活/非激活状态 | `team_id`、`player_uid`、`active` | 更新激活名册 | RESEARCH |
| `GM.ROSTER.WAIVE` | 裁员/放弃指定球员 | `team_id`、`player_uid`、`waiver_mode` | 原版裁员事务 | PARTIAL / `RELEASE_WAIVE_PLAYER` (PARTIAL_BINDING) |
| `GM.ROSTER.TEAM_ASSIGN_CONTRACT` | 基于已同意合同指定归属 | `team_id`、`player_uid`、`contract_ref` | 原版签约归属 | PARTIAL |
| `GM.ROSTER.ROSTER_LEGALITY_READ` | 读取名单占用与限制 | `team_id` | 球队可用槽、当前人数、约束 | READ_SUBSET / `READ_TEAM_ROSTER_BASIC` (CALL_LOGIC_RECOVERED) |

### GM：球员与选秀权交换（10项）

| 能力 ID | 要执行或读取什么 | 外部模型提供的输入 | 原生预期结果 | 当前级别 / 已有关联 |
|---|---|---|---|---|
| `GM.TRADE.EXECUTE_AGREED` | 直接执行已同意交易包 | `team_a`、`team_b`、`players_a`、`players_b`、`picks_a`、`picks_b` | 原生Process处理双方给定资产 | LIVE_EXACT / `TRADE_EXECUTE_AGREED_PACKAGE` (CALL_LOGIC_RECOVERED) |
| `GM.TRADE.MULTI_PLAYER` | 多球员资产包交易 | `team_a`、`team_b`、`players_a`、`players_b` | 原生交易提交 | STATIC / `TRADE_MULTI_PLAYER_PACKAGE` (CALL_LOGIC_RECOVERED) |
| `GM.TRADE.PICK_ONLY` | 选秀权交换 | `team_a`、`team_b`、`picks_a`、`picks_b` | 原生签权转移 | STATIC / `TRADE_PICKS` (CALL_LOGIC_RECOVERED) |
| `GM.TRADE.MIXED` | 球员加选秀权混合交换 | `team_a`、`team_b`、`players_a`、`players_b`、`picks_a`、`picks_b` | 原生交易提交 | STATIC / `TRADE_MIXED_ASSETS` (CALL_LOGIC_RECOVERED) |
| `GM.TRADE.THREE_TEAM` | 三方交易指定资产流 | `teams`、`directed_assets` | 三队交易事务 | RESEARCH |
| `GM.TRADE.TRADE_BLOCK_ADD` | 球员/签权列入交易货架 | `team_id`、`asset_uid`、`offer_meta` | 更新可交易资产列表 | RESEARCH |
| `GM.TRADE.TRADE_BLOCK_REMOVE` | 移出交易货架 | `team_id`、`asset_uid` | 移除交易候选 | RESEARCH |
| `GM.TRADE.PICK_ASSIGNMENT` | 指定选秀权权属操作 | `pick_uid`、`from_team`、`to_team` | 原生签权归属变化 | PARTIAL |
| `GM.TRADE.FINDER_READ` | 读取游戏的Trade Finder候选 | `team_id`、`asset_uid` | 返回游戏本身列出的提案 | RESEARCH |
| `GM.TRADE.TRADE_HISTORY_READ` | 查看实际成交记录 | `season_id`、`team_id` | 返回交易历史/联盟消息 | READ_RESEARCH |

### GM：签约、合同与自由市场（16项）

| 能力 ID | 要执行或读取什么 | 外部模型提供的输入 | 原生预期结果 | 当前级别 / 已有关联 |
|---|---|---|---|---|
| `GM.CONTRACT.FA_SIGN` | 签约指定自由球员 | `team_id`、`player_uid`、`years`、`annual_salary`、`clauses` | 原生签约事务 | PARTIAL / `SIGN_FREE_AGENT` (PARTIAL_BINDING) |
| `GM.CONTRACT.EXTEND` | 指定球员续约 | `team_id`、`player_uid`、`years`、`salary_schedule`、`options` | 更新续约合同 | PARTIAL / `RE_SIGN_PLAYER` (PARTIAL_BINDING) |
| `GM.CONTRACT.RE_SIGN` | 原队重新签约 | `team_id`、`player_uid`、`contract_terms` | 合同与名单生效 | PARTIAL |
| `GM.CONTRACT.CONTRACT_OFFER` | 发出指定合同报价 | `team_id`、`player_uid`、`terms` | 生成原版报价 | PARTIAL |
| `GM.CONTRACT.OFFER_ACCEPT_OR_REJECT` | 对已发报价接受/拒绝 | `offer_uid`、`decision` | 原生报价状态变化 | RESEARCH |
| `GM.CONTRACT.TEAM_OPTION` | 执行球队选项 | `team_id`、`contract_uid`、`accept` | 下一年合同有效性 | RESEARCH / `CONTRACT_OPTION_ACTION` (PARTIAL_BINDING) |
| `GM.CONTRACT.PLAYER_OPTION` | 执行球员选项 | `player_uid`、`contract_uid`、`accept` | 球员合同选项生效 | RESEARCH / `CONTRACT_OPTION_ACTION` (PARTIAL_BINDING) |
| `GM.CONTRACT.QUALIFYING_OFFER` | 向指定RFA提供资质报价 | `team_id`、`player_uid`、`offer_terms` | 资质报价登记 | RESEARCH |
| `GM.CONTRACT.MATCH_RFA` | 匹配指定报价 | `team_id`、`player_uid`、`offer_uid` | 原版报价匹配 | RESEARCH |
| `GM.CONTRACT.RENOUNCE_RIGHTS` | 放弃指定自由球员权利 | `team_id`、`player_uid`、`right_kind` | 更新工资帽保留/签约权利 | RESEARCH |
| `GM.CONTRACT.CAP_HOLD_RELEASE` | 解除指定工资帽保留额 | `team_id`、`cap_hold_uid` | 更新可用空间 | RESEARCH |
| `GM.CONTRACT.HARDSHIP_SIGN` | 按明确条款执行困难合同 | `team_id`、`player_uid`、`contract_terms` | 特殊合同事务 | RESEARCH |
| `GM.CONTRACT.TWO_WAY_SIGN` | 双向合同签约 | `team_id`、`player_uid`、`contract_terms` | 双向球员合同归属 | RESEARCH |
| `GM.CONTRACT.ROOKIE_SIGN` | 新秀合同签约 | `team_id`、`player_uid`、`pick_uid`、`contract_terms` | 新秀加盟与合同登记 | RESEARCH |
| `GM.CONTRACT.CONTRACT_EDIT` | 管理员编辑合同存值 | `contract_uid`、`field_id`、`new_value` | 世界编辑，不是谈判自动执行 | WORLD_EDIT |
| `GM.CONTRACT.CONTRACT_RENEGOTIATE` | 修改/替换待处理报价参数 | `offer_uid`、`new_terms` | 报价对象更新 | RESEARCH |

### GM：教练与员工市场（8项）

| 能力 ID | 要执行或读取什么 | 外部模型提供的输入 | 原生预期结果 | 当前级别 / 已有关联 |
|---|---|---|---|---|
| `GM.STAFF.STAFF_POOL_READ` | 查看可聘员工池 | `role_code`、`filter` | 人员候选及属性 | READ_RESEARCH |
| `GM.STAFF.HIRE` | 雇用指定员工 | `team_id`、`staff_uid`、`role_code`、`salary`、`years` | 原生员工合同与岗位关联 | PARTIAL / `TEAM_MANAGE_STAFF` (PARTIAL_BINDING) |
| `GM.STAFF.FIRE` | 解雇指定员工 | `team_id`、`staff_uid` | 解除岗位与合同 | PARTIAL / `TEAM_MANAGE_STAFF` (PARTIAL_BINDING) |
| `GM.STAFF.EXTEND` | 续聘指定员工 | `team_id`、`staff_uid`、`contract_terms` | 更新职员合同 | RESEARCH |
| `GM.STAFF.REASSIGN` | 调整员工岗位 | `team_id`、`staff_uid`、`role_code` | 球队岗位归属 | RESEARCH |
| `GM.STAFF.REPLACE_HEAD_COACH` | 更换球队主教练 | `team_id`、`new_coach_uid` | 主教练关联及原版业务刷新 | RESEARCH |
| `GM.STAFF.STAFF_BUDGET_SET` | 设置员工预算（如可用） | `team_id`、`budget_value` | 原生员工预算状态 | RESEARCH |
| `GM.STAFF.STAFF_ATTRIBUTE_SET` | 管理员调整职员能力字段 | `staff_uid`、`field_key`、`value` | 职员能力/特性存值变更 | PARTIAL / `STAFF_SET_ATTRIBUTE` (REFERENCE_ONLY) |

### GM：选秀球探与候选管理（14项）

| 能力 ID | 要执行或读取什么 | 外部模型提供的输入 | 原生预期结果 | 当前级别 / 已有关联 |
|---|---|---|---|---|
| `GM.SCOUT.PROSPECT_LIST` | 查询本届选秀候选人 | `draft_class_uid`、`filters` | 当前可见候选身份列表 | READ_SUBSET / `SCOUT_LIST_CURRENT_PUBLIC_PROSPECTS` (CALL_LOGIC_RECOVERED) |
| `GM.SCOUT.PROSPECT_PROFILE` | 查询候选球员公开资料 | `prospect_uid`、`team_id` | 已公开信息 | READ_SUBSET / `SCOUT_READ_PROSPECT_INFO` (PARTIAL_BINDING) |
| `GM.SCOUT.GOAL_REPLACE` | 替换已有球探目标槽 | `team_id`、`goal_index`、`prospect_uids` | 原生既有Goal记录目标变更 | LIVE_EXACT / `SCOUT_SET_EXISTING_GOAL_TARGETS` (CALL_LOGIC_RECOVERED) |
| `GM.SCOUT.GOAL_APPEND` | 新增球探任务 | `team_id`、`prospect_uids`、`priority` | 向Trip添加Goal；满槽可能拒绝 | STATIC_REJECTION_OBSERVED / `SCOUT_ASSIGN_TARGETS` (CALL_LOGIC_RECOVERED) |
| `GM.SCOUT.SCOUT_EXECUTE` | 执行指定已配置球探行程 | `team_id`、`trip_ref` | 消耗游戏考察行动并更新进度 | STATIC / `SCOUT_EXECUTE_CURRENT_TRIP` (CALL_LOGIC_RECOVERED) |
| `GM.SCOUT.SCOUT_PROGRESS` | 查询考察进度 | `team_id`、`prospect_uid` | raw进度和已解锁的状态 | READ_SUBSET / `SCOUT_READ_PROGRESS_RAW` (CALL_LOGIC_RECOVERED) |
| `GM.SCOUT.SCOUT_REPORT` | 查询已获得球探报告 | `team_id`、`prospect_uid` | 真实可见评估/报告 | PARTIAL / `SCOUT_READ_PROGRESS_REPORT` (PARTIAL_BINDING) |
| `GM.SCOUT.SCOUT_PRIORITY` | 指定球探任务优先级 | `team_id`、`goal_index`、`priority_raw` | 更新任务优先级 | PARTIAL |
| `GM.SCOUT.SCOUT_AUTOMATION` | 指定球探自动/手动 | `team_id`、`automation_value` | 球探自动化配置 | RESEARCH |
| `GM.SCOUT.SCOUT_STAFF_ASSIGN` | 指派指定球探人员 | `team_id`、`scout_uid`、`trip_or_region` | 更改人员及考察任务关联 | RESEARCH |
| `GM.SCOUT.WORKOUT_ASSIGN` | 安排新秀试训 | `team_id`、`prospect_uids`、`workout_slot` | 赛前试训业务 | RESEARCH |
| `GM.SCOUT.MEDICAL_REPORT` | 读取候选体测/体检 | `team_id`、`prospect_uid` | 当前可见结果 | RESEARCH |
| `GM.SCOUT.BIG_BOARD_VIEW` | 查询选秀大名单/自定义次序 | `team_id`、`draft_class_uid` | 当前名单与用户顺位 | RESEARCH |
| `GM.SCOUT.BIG_BOARD_SET` | 按给定顺位更新球队选秀名单 | `team_id`、`ordered_prospect_uids` | 原生名单排序 | RESEARCH |

### GM：选秀大会及选秀班（10项）

| 能力 ID | 要执行或读取什么 | 外部模型提供的输入 | 原生预期结果 | 当前级别 / 已有关联 |
|---|---|---|---|---|
| `GM.DRAFT.CURRENT_PICK_READ` | 查询当前大会选秀权 | `draft_session` | 当前签位及持有者 | STATIC / `READ_CURRENT_DRAFT_PICK` (CALL_LOGIC_RECOVERED) |
| `GM.DRAFT.DRAFT_SPECIFIED` | 使用当前指定选秀权选择指定候选 | `team_id`、`pick_uid`、`prospect_uid` | 原生选择与签位消费 | STATIC / `DRAFT_SELECT_PROSPECT` (CALL_LOGIC_RECOVERED) |
| `GM.DRAFT.PICK_OWNER_READ` | 查询选秀权当前所有者 | `pick_uid` | 拥有者/年份/轮次 | READ_SUBSET / `DRAFT_STAGE_REQUIRED_CONTEXT` (CALL_LOGIC_RECOVERED) |
| `GM.DRAFT.PICK_RIGHTS_TRANSFER` | 执行明确的选秀权交易权属 | `pick_uid`、`new_team_id` | 原生资产事务 | PARTIAL |
| `GM.DRAFT.LOTTERY_READ` | 查询选秀顺位及抽签结果 | `season_id` | 乐透结果及顺位 | RESEARCH |
| `GM.DRAFT.DRAFT_RESULT_READ` | 获取已完成的选秀结果 | `season_id`、`round` | 选中球员和签位 | RESEARCH |
| `GM.DRAFT.DRAFT_CLASS_SET` | 选择使用指定Draft Class | `season_id`、`class_uid` | 更新本届候选池 | RESEARCH |
| `GM.DRAFT.DRAFT_CLASS_IMPORT` | 导入指定选秀班 | `file_ref`、`season_id` | 导入外部候选名单 | RESEARCH |
| `GM.DRAFT.DRAFT_CLASS_EDIT` | 管理员调整候选球员档案 | `prospect_uid`、`field_id`、`value` | 编辑新秀档案 | WORLD_EDIT |
| `GM.DRAFT.DRAFT_RIGHTS_STASH` | 指定海外球员签权/留队安排 | `team_id`、`prospect_uid`、`decision` | 更新选秀权利业务 | RESEARCH |

### 教练：攻防设置和体系（16项）

| 能力 ID | 要执行或读取什么 | 外部模型提供的输入 | 原生预期结果 | 当前级别 / 已有关联 |
|---|---|---|---|---|
| `COACH.STRATEGY.POE_O1` | 进攻重点POEOffense | `team_id`、`native_enum_0_6` | 更新当前教练进攻重点 | STATIC / `COACH_APPLY_OFFENSE_POE` (CALL_LOGIC_RECOVERED) |
| `COACH.STRATEGY.POE_O2` | 进攻节奏倾向POEOffense2 | `team_id`、`native_enum_0_or_7_9` | 更新当前教练取向 | STATIC |
| `COACH.STRATEGY.POE_O3` | 进攻篮板与退防POEOffense3 | `team_id`、`native_enum_0_or_10_12` | 更新当前教练取向 | STATIC |
| `COACH.STRATEGY.POE_D1` | 防守重点POEDefense | `team_id`、`native_enum_0_or_13_15` | 更改当前教练防守重点 | LIVE_EXACT / `COACH_APPLY_DEFENSE_POE` (PRIOR_LIVE_SUCCESS) |
| `COACH.STRATEGY.POE_D2` | 防守对抗取向POEDefense2 | `team_id`、`native_enum_0_or_16_18` | 更新防守取向 | STATIC |
| `COACH.STRATEGY.POE_D3` | 防守篮板与转换POEDefense3 | `team_id`、`native_enum_0_or_19_21` | 更新防守取向 | STATIC |
| `COACH.STRATEGY.RUN_PLAY` | 设置RunPlayTendency | `team_id`、`value_0_100` | 修改战术调用倾向 | LIVE_EXACT / `COACH_SET_KNOWN_CURRENT_SETTINGS` (CALL_LOGIC_RECOVERED) |
| `COACH.STRATEGY.ZONE_USAGE` | 设置ZoneUsage | `team_id`、`value_0_100` | 修改联防使用倾向 | STATIC / `COACH_SET_KNOWN_CURRENT_SETTINGS` (CALL_LOGIC_RECOVERED) |
| `COACH.STRATEGY.BENCH_DEPTH` | 设置BenchDepth | `team_id`、`depth_integer` | 修改板凳深度 | STATIC / `COACH_SET_ROTATION_POLICY` (CALL_LOGIC_RECOVERED) |
| `COACH.STRATEGY.BENCH_USE` | 设置BenchUtilization | `team_id`、`value_0_100` | 修改替补使用倾向 | STATIC / `COACH_SET_ROTATION_POLICY` (CALL_LOGIC_RECOVERED) |
| `COACH.STRATEGY.PREFERRED_SYSTEM` | 教练偏好体系 | `team_id`、`system_enum_0_7` | 修改偏好体系 | PROJECT_NATIVE |
| `COACH.STRATEGY.ACTIVE_SYSTEM` | 球队当前体系 | `team_id`、`system_enum_0_7` | 修改当前执行体系 | PROJECT_NATIVE |
| `COACH.STRATEGY.HELP_DEFENSE` | 协防倾向 | `team_id`、`value_0_100` | 修改帮助防守设置 | PROJECT_NATIVE |
| `COACH.STRATEGY.TEMPO` | 球队比赛节奏参数 | `team_id`、`tempo_raw` | 更改节奏取向 | PROJECT_NATIVE |
| `COACH.STRATEGY.ACE_MODE` | 设定ACE智能战术开关/模式 | `team_id`、`ace_mode` | 启用或关闭自动调整 | RESEARCH |
| `COACH.STRATEGY.COACH_AUTOMATION` | 教练自动战术/轮换控制 | `team_id`、`automation_group`、`value` | 指定自动化范围 | RESEARCH |

### 教练：战术手册、战术和Freelance（18项）

| 能力 ID | 要执行或读取什么 | 外部模型提供的输入 | 原生预期结果 | 当前级别 / 已有关联 |
|---|---|---|---|---|
| `COACH.PLAYBOOK.PLAYBOOK_SELECT` | 球队战术手册替换 | `team_id`、`book_id` | 更新当前球队战术书 | PARTIAL / `COACH_REPLACE_PLAYBOOK` (PARTIAL_BINDING) |
| `COACH.PLAYBOOK.BOOK_SLOT_READ` | 读取4分区共68个战术槽 | `team_id`、`section` | 返回CRC、顺序、槽位 | PROJECT_NATIVE |
| `COACH.PLAYBOOK.BOOK_ADD` | 在指定分区/槽位添加战术 | `team_id`、`section`、`slot`、`play_crc` | 加入具体战术 | PARTIAL / `COACH_ADD_REPLACE_PLAY` (PARTIAL_BINDING) |
| `COACH.PLAYBOOK.BOOK_REPLACE` | 替换指定已存在的战术 | `team_id`、`section`、`slot`、`play_crc` | 替换该槽CRC | PARTIAL / `COACH_ADD_REPLACE_PLAY` (PARTIAL_BINDING) |
| `COACH.PLAYBOOK.BOOK_REMOVE` | 删除指定战术槽 | `team_id`、`section`、`slot` | 该槽释放 | PARTIAL |
| `COACH.PLAYBOOK.BOOK_SWAP` | 调换两条战术顺序 | `team_id`、`section`、`slot_a`、`slot_b` | 调整战术优先级 | RESEARCH |
| `COACH.PLAYBOOK.BOOK_REGULAR` | 指定常规区战术内容 | `team_id`、`regular_slots_30` | 原生常规区更新 | RESEARCH |
| `COACH.PLAYBOOK.BOOK_BENCH` | 指定替补区战术内容 | `team_id`、`bench_slots_20` | 替补区更新 | RESEARCH |
| `COACH.PLAYBOOK.BOOK_ENDGAME` | 指定末段区战术内容 | `team_id`、`endgame_slots_10` | 末段区更新 | RESEARCH |
| `COACH.PLAYBOOK.BOOK_FAVORITE` | 指定偏好区战术内容 | `team_id`、`favorite_slots_8` | 快捷战术更新 | RESEARCH |
| `COACH.PLAYBOOK.PLAY_POOL_LIST` | 获取当前可选战术池与12类分类 | `category_id`、`filter` | 候选战术CRC和名称 | READ_RESEARCH |
| `COACH.PLAYBOOK.PLAY_PREVIEW` | 读取指定战术预览/说明 | `play_crc` | 战术参与位置与已公开描述 | RESEARCH |
| `COACH.PLAYBOOK.FREELANCE_1` | 设置第一Freelance槽 | `team_id`、`freelance_enum` | 更新有序自由进攻首槽 | PROJECT_NATIVE |
| `COACH.PLAYBOOK.FREELANCE_2` | 设置第二Freelance槽 | `team_id`、`freelance_enum` | 更新有序自由进攻第二槽 | PROJECT_NATIVE |
| `COACH.PLAYBOOK.FREELANCE_3` | 设置第三Freelance槽 | `team_id`、`freelance_enum` | 更新有序自由进攻第三槽 | PROJECT_NATIVE |
| `COACH.PLAYBOOK.FREELANCE_4` | 设置第四Freelance槽 | `team_id`、`freelance_enum` | 更新有序自由进攻第四槽 | PROJECT_NATIVE |
| `COACH.PLAYBOOK.OPPONENT_PLAN_FIND` | 读取/创建指定对手的Gameplan | `team_id`、`opponent_team_id` | 返回或创建计划对象 | STATIC / `COACH_ENSURE_OPPONENT_GAMEPLAN` (CALL_LOGIC_RECOVERED) |
| `COACH.PLAYBOOK.OPPONENT_PLAN_EDIT` | 编辑指定对手完整Gameplan | `team_id`、`opponent_team_id`、`fields` | 保存特殊对手计划 | PARTIAL / `COACH_SET_GAMEPLAN` (PARTIAL_BINDING) |

### 教练：对指定对手球员的个人防守（18项）

| 能力 ID | 要执行或读取什么 | 外部模型提供的输入 | 原生预期结果 | 当前级别 / 已有关联 |
|---|---|---|---|---|
| `COACH.DEFENSE.PRESS_ON` | 持球压力 | `team_id`、`opponent_uid`、`native_enum` | 设置防守压力 | PROJECT_NATIVE |
| `COACH.DEFENSE.PRESS_OFF` | 无球压力 | `team_id`、`opponent_uid`、`native_enum` | 设置无球盯防 | PROJECT_NATIVE |
| `COACH.DEFENSE.FORCE_DIRECTION` | 逼迫进攻方向 | `team_id`、`opponent_uid`、`native_enum` | 设置方向 | PROJECT_NATIVE |
| `COACH.DEFENSE.ONBALL_SCREEN` | 防有球掩护策略 | `team_id`、`opponent_uid`、`native_enum` | 设置绕掩护 | PROJECT_NATIVE |
| `COACH.DEFENSE.HEDGE` | 掩护人防守策略 | `team_id`、`opponent_uid`、`native_enum` | 设置延阻/沉退 | PROJECT_NATIVE |
| `COACH.DEFENSE.OFFBALL_SCREEN` | 无球掩护防守 | `team_id`、`opponent_uid`、`native_enum` | 设置无球策略 | PROJECT_NATIVE |
| `COACH.DEFENSE.POST_DEFENSE` | 背身防守策略 | `team_id`、`opponent_uid`、`native_enum` | 设置低位守法 | PROJECT_NATIVE |
| `COACH.DEFENSE.DOUBLE_PERIMETER` | 外线包夹 | `team_id`、`opponent_uid`、`native_enum` | 设置包夹 | PROJECT_NATIVE |
| `COACH.DEFENSE.DOUBLE_POST` | 低位包夹 | `team_id`、`opponent_uid`、`native_enum` | 设置包夹 | PROJECT_NATIVE |
| `COACH.DEFENSE.SCREEN_ONBALL5` | Center后缀有球策略 | `team_id`、`opponent_uid`、`native_enum` | 更新特殊有球策略 | PROJECT_NATIVE |
| `COACH.DEFENSE.HEDGE5` | Center后缀延阻策略 | `team_id`、`opponent_uid`、`native_enum` | 更新特殊Hedge | PROJECT_NATIVE |
| `COACH.DEFENSE.SWITCH_RULE` | 换防规则 | `team_id`、`opponent_uid`、`native_enum` | 设置换防 | PROJECT_NATIVE |
| `COACH.DEFENSE.ONBALL_HELP` | 持球协防 | `team_id`、`opponent_uid`、`native_enum` | 设置持球帮助 | PROJECT_NATIVE |
| `COACH.DEFENSE.SCREEN_HELP` | 掩护协防 | `team_id`、`opponent_uid`、`native_enum` | 设置掩护帮助 | PROJECT_NATIVE |
| `COACH.DEFENSE.EXTEND_PRESSURE` | 延伸防守压力 | `team_id`、`opponent_uid`、`native_enum` | 设置延伸压迫 | PROJECT_NATIVE |
| `COACH.DEFENSE.TAG_ON_ROLL` | 顺下补位 | `team_id`、`opponent_uid`、`native_enum` | 更新补位 | PROJECT_NATIVE |
| `COACH.DEFENSE.STAY_ATTACHED` | 保持盯防 | `team_id`、`opponent_uid`、`native_enum` | 更新盯防 | PROJECT_NATIVE |
| `COACH.DEFENSE.PRE_ROTATE` | 提前轮转 | `team_id`、`opponent_uid`、`value_0_or_1` | 设置预轮转 | PROJECT_NATIVE |

### 教练：出场阵容、分钟与角色（10项）

| 能力 ID | 要执行或读取什么 | 外部模型提供的输入 | 原生预期结果 | 当前级别 / 已有关联 |
|---|---|---|---|---|
| `COACH.ROTATION.ROTATION_ORDER` | 安排轮换先后顺序 | `team_id`、`ordered_player_uids` | 更新轮换表 | PARTIAL / `TEAM_SET_MINUTES_ROTATION` (NOT_FOUND_WITH_SEARCH_SCOPE) |
| `COACH.ROTATION.PLAYER_MINUTES` | 设置某球员分钟数 | `team_id`、`player_uid`、`minutes` | 更新分钟分配 | PARTIAL |
| `COACH.ROTATION.STARTING_FIVE` | 设置五个首发 | `team_id`、`ordered_player_uids` | 指定先发 | PARTIAL / `TEAM_SET_STARTERS` (NOT_FOUND_WITH_SEARCH_SCOPE) |
| `COACH.ROTATION.SECOND_UNIT` | 指定替补阵容 | `team_id`、`ordered_player_uids` | 指定第二阵容 | PARTIAL |
| `COACH.ROTATION.PLAYER_ROLE` | 指定球员上场角色 | `team_id`、`player_uid`、`role` | 更新轮换角色 | PARTIAL |
| `COACH.ROTATION.SITUATIONAL_LINEUPS` | 配置情景五人组 | `team_id`、`lineup_type`、`player_uids` | 关键时段阵容配置 | RESEARCH |
| `COACH.ROTATION.INJURY_SUBSTITUTION` | 伤病或缺阵触发轮换替代 | `team_id`、`missing_player_uid`、`replacement_uid` | 更新可上场阵容 | RESEARCH |
| `COACH.ROTATION.MATCHUP_ASSIGN` | 指定对手球员/防守者关系 | `team_id`、`attacker_uid`、`defender_uid` | 更改指定防守对位 | RESEARCH |
| `COACH.ROTATION.LIVE_SUBSTITUTION` | 比赛暂停时指定换人 | `game_id`、`player_out_uid`、`player_in_uid` | 游戏原生临场换人 | RESEARCH |
| `COACH.ROTATION.LIVE_CALL_PLAY` | 比赛中指定某条已装载战术 | `game_id`、`play_crc`、`initiator_uid` | 执行临场战术指令 | RESEARCH |

### 团队/个人训练、康复与导师（14项）

| 能力 ID | 要执行或读取什么 | 外部模型提供的输入 | 原生预期结果 | 当前级别 / 已有关联 |
|---|---|---|---|---|
| `TRAIN.TEAM_SCHEDULE` | 指定球队日期训练完整配置 | `team_id`、`native_date_key`、`training_payload` | 更新该日训练 | STATIC / `TRAIN_TEAM_SET_SCHEDULE` (CALL_LOGIC_RECOVERED) |
| `TRAIN.TEAM_INTENSITY` | 仅修改该日训练强度 | `team_id`、`native_date_key`、`intensity_raw_0_7` | 更新3bit强度并保留其它字段 | STATIC / `TRAIN_TEAM_SET_INTENSITY` (CALL_LOGIC_RECOVERED) |
| `TRAIN.TEAM_FOCUS` | 设置球队训练重点比例 | `team_id`、`native_date_key`、`focus_percentages` | 改变培养项目分配 | STATIC |
| `TRAIN.TEAM_PROFILE` | 设置训练类型/子项目 | `team_id`、`native_date_key`、`profile_types`、`subfocus_points` | 改变训练内容 | STATIC |
| `TRAIN.HOME_AWAY_INTENSITY` | 设置主客场训练强度 | `team_id`、`home_intensity`、`away_intensity` | 修改主客场训练负荷 | PROJECT_NATIVE |
| `TRAIN.AUTOMATION` | 训练自动化开关 | `team_id`、`automation_enabled` | 原生训练自动化状态 | PROJECT_NATIVE |
| `TRAIN.B2B_REST` | 背靠背前后休息 | `team_id`、`rest_before`、`rest_after` | 更新休息策略 | PROJECT_NATIVE |
| `TRAIN.PLAYER_FOCUS` | 指定球员训练重点/类型 | `team_id`、`player_uid`、`training_type` | 设置球员培养方向 | PROJECT_NATIVE |
| `TRAIN.PLAYER_INTENSITY` | 指定球员训练强度或覆盖 | `team_id`、`player_uid`、`intensity`、`override` | 指定个体负荷 | PROJECT_NATIVE |
| `TRAIN.PLAYER_RECOVERY` | 为指定球员配置康复重点 | `team_id`、`player_uid`、`recovery_mode` | 原生康复设置 | PROJECT_NATIVE |
| `TRAIN.TEAM_RECOVERY` | 配置球队康复策略 | `team_id`、`injury_recovery` | 更新球队康复开关 | PROJECT_NATIVE |
| `TRAIN.MENTOR_ASSIGN` | 安排球员导师关系 | `team_id`、`mentor_uid`、`mentee_uid` | 原生导师关联 | PARTIAL / `TRAIN_PLAYER_MENTOR_ASSIGNMENT` (PARTIAL_BINDING) |
| `TRAIN.MENTOR_REMOVE` | 取消导师关系 | `team_id`、`mentor_uid`、`mentee_uid` | 解除关系 | PARTIAL |
| `TRAIN.HEALTH_INFO` | 查询体力/疲劳/伤病进度 | `player_uid`、`season_or_date` | 返回游戏当前健康数据 | READ_RESEARCH |

### 球员原生属性/球风/资料编辑（独立于人格决策）（16项）

| 能力 ID | 要执行或读取什么 | 外部模型提供的输入 | 原生预期结果 | 当前级别 / 已有关联 |
|---|---|---|---|---|
| `PLAYER.EDIT.ATTR_SET` | 设置单项能力 | `player_uid`、`attribute_key`、`value` | 更新原生能力 | PARTIAL / `PLAYER_SET_ATTRIBUTE` (PARTIAL_BINDING) |
| `PLAYER.EDIT.ATTR_BATCH` | 批量设置已给能力键 | `player_uid`、`attribute_map` | 更新多个能力 | PARTIAL |
| `PLAYER.EDIT.TENDENCY_SET` | 设置单项倾向 | `player_uid`、`tendency_key`、`value` | 更新原生倾向 | PARTIAL / `PLAYER_SET_TENDENCY` (PARTIAL_BINDING) |
| `PLAYER.EDIT.TENDENCY_BATCH` | 批量设置倾向 | `player_uid`、`tendency_map` | 更新多个倾向 | PARTIAL |
| `PLAYER.EDIT.BADGE_SET` | 设置球员徽章等级 | `player_uid`、`badge_id`、`level` | 更新徽章 | PARTIAL / `PLAYER_SET_BADGE` (PARTIAL_BINDING) |
| `PLAYER.EDIT.BADGE_REMOVE` | 删除指定徽章 | `player_uid`、`badge_id` | 移除徽章 | PARTIAL |
| `PLAYER.EDIT.PLAY_TYPE_1` | 设置球员战术类型1槽 | `player_uid`、`play_type_enum_0_15` | 更新槽位1 | PROJECT_NATIVE / `PLAYER_SET_PLAY_TYPES_1_TO_4` (PARTIAL_BINDING) |
| `PLAYER.EDIT.PLAY_TYPE_2` | 设置球员战术类型2槽 | `player_uid`、`play_type_enum_0_15` | 更新槽位2 | PROJECT_NATIVE / `PLAYER_SET_PLAY_TYPES_1_TO_4` (PARTIAL_BINDING) |
| `PLAYER.EDIT.PLAY_TYPE_3` | 设置球员战术类型3槽 | `player_uid`、`play_type_enum_0_15` | 更新槽位3 | PROJECT_NATIVE / `PLAYER_SET_PLAY_TYPES_1_TO_4` (PARTIAL_BINDING) |
| `PLAYER.EDIT.PLAY_TYPE_4` | 设置球员战术类型4槽 | `player_uid`、`play_type_enum_0_15` | 更新槽位4 | PROJECT_NATIVE / `PLAYER_SET_PLAY_TYPES_1_TO_4` (PARTIAL_BINDING) |
| `PLAYER.EDIT.PLAY_INITIATOR` | 设置战术发起者标志 | `player_uid`、`enabled` | 更新战术发起权限 | PROJECT_NATIVE |
| `PLAYER.EDIT.PLAYER_VITALS` | 编辑位置号码身高体重等资料 | `player_uid`、`field_key`、`value` | 管理员变更个人资料 | PARTIAL / `PLAYER_SET_EDITABLE_INFO` (PARTIAL_BINDING) |
| `PLAYER.EDIT.DURABILITY_SET` | 指定身体耐久字段 | `player_uid`、`durability_key`、`value` | 更新耐久性 | PARTIAL |
| `PLAYER.EDIT.INJURY_STATUS` | 指定伤病状态字段 | `player_uid`、`injury_key`、`value` | 更新游戏伤病状态 | RESEARCH / `PLAYER_SET_EDITABLE_INFO` (PARTIAL_BINDING) |
| `PLAYER.EDIT.POTENTIAL_SET` | 指定潜力字段 | `player_uid`、`potential_value` | 世界线编辑行为 | PARTIAL |
| `PLAYER.EDIT.DNA_IMPORT` | 将指定DNA配置应用到球员 | `player_uid`、`dna_ref` | 原生完整玩家资料应用 | RESEARCH |

### 球员人格的请求与回应（非原生编辑器）（9项）

| 能力 ID | 要执行或读取什么 | 外部模型提供的输入 | 原生预期结果 | 当前级别 / 已有关联 |
|---|---|---|---|---|
| `PLAYER.AGENCY.TRADE_REQUEST` | 球员提出转队诉求 | `player_uid`、`preferred_team_uids`、`conditions` | 向GM提交外挂请求不直接改球队 | EXTERNAL |
| `PLAYER.AGENCY.CONTRACT_RESPONSE` | 球员接受/拒绝外挂报价 | `player_uid`、`offer_id`、`decision` | 给GM模型的明确答复 | EXTERNAL |
| `PLAYER.AGENCY.ROLE_REQUEST` | 提出首发/角色或分钟诉求 | `player_uid`、`requested_role`、`requested_minutes` | 向教练提出要求 | EXTERNAL |
| `PLAYER.AGENCY.TRAINING_REQUEST` | 提出个人训练重点 | `player_uid`、`focus`、`intensity` | 向教练提出训练请求 | EXTERNAL |
| `PLAYER.AGENCY.MENTOR_REQUEST` | 申请指定导师 | `player_uid`、`mentor_uid` | 向教练或GM提出请求 | EXTERNAL |
| `PLAYER.AGENCY.PLAYSTYLE_REQUEST` | 提出四槽类型或打法偏好 | `player_uid`、`play_types_or_tendency_pref` | 经决策协商转业务设置 | EXTERNAL |
| `PLAYER.AGENCY.EXTENSION_PREFERENCE` | 球员合同/续约偏好 | `player_uid`、`term_preferences` | 作为合同谈判输入 | EXTERNAL |
| `PLAYER.AGENCY.MORALE_FEEDBACK` | 球员反映士气/球队角色 | `player_uid`、`reason`、`desired_change` | 外挂人格状态/事件 | EXTERNAL |
| `PLAYER.AGENCY.INJURY_REPORT` | 球员请求休息/康复 | `player_uid`、`health_context`、`requested_action` | 向教练或球队提出请求 | EXTERNAL |

### 世界线与比赛/赛季操作（非默认赋予任何角色）（12项）

| 能力 ID | 要执行或读取什么 | 外部模型提供的输入 | 原生预期结果 | 当前级别 / 已有关联 |
|---|---|---|---|---|
| `WORLD.SETUP_OPTIONS` | 选择联盟结构、队数、季长等 | `save_id`、`settings_map` | 世界线初始化 | RESEARCH |
| `WORLD.GAMEPLAY_SLIDERS` | 设置USER/CPU Gameplay滑块 | `save_id`、`slider_key`、`value` | 改变比赛环境参数 | RESEARCH |
| `WORLD.SIMULATION_SLIDERS` | 设置日历模拟参数 | `save_id`、`setting_key`、`value` | 改变Simulation Engine配置 | RESEARCH |
| `WORLD.NORMALIZE` | 设置标准化分钟/统计开关 | `save_id`、`normalize_flags` | 改变统计口径 | RESEARCH |
| `WORLD.TEAM_AUTOMATION` | 设置球队自动管理开关 | `team_id`、`automation_fields` | 移交或撤回原版自动化 | RESEARCH |
| `WORLD.CPU_CONTROL` | 设置球队人类/AI控制位 | `team_id`、`controller_mode` | 改变内建控制者；不等于外挂人格 | RESEARCH |
| `WORLD.ADVANCE_DATE` | 推进指定联盟日期/阶段 | `save_id`、`target_date_or_event` | 游戏内日历进展 | RESEARCH |
| `WORLD.SIMULATE_GAME` | 模拟指定比赛 | `game_uid`、`mode` | 产生真实比赛结果 | RESEARCH |
| `WORLD.SIMCAST_MODE` | 选择SimCast/QuickSim/3D运行方式 | `game_uid`、`mode` | 比赛执行方式 | RESEARCH |
| `WORLD.OFFSEASON_STEP` | 执行指定休赛期阶段 | `save_id`、`phase_action` | 休赛期状态改变 | RESEARCH |
| `WORLD.LEAGUE_RULE_CHANGE` | 设定联盟规则变更 | `season_id`、`rule_id`、`decision` | 联盟规则生效 | RESEARCH |
| `WORLD.DRAFT_CLASS_WORLD` | 选择赛季的选秀班来源 | `season_id`、`class_id` | 下一届选秀候选池变化 | RESEARCH |

## 5. 数据读取范围：40组旧研究 → 12类Reader仍未全量覆盖

下面的40组是**旧游戏资料对“哪些信息可供角色使用”的研究分类**，不是40个已调通的游戏Native Getter。每项的真实字段级可用状态仍应通过自己的Reader字段/索引登记判定。

| 来源研究组 | 必须考虑的读取信息家族 |
|---|---|
| F01 | 赛程、对阵及GameID |
| F02 | 逐场球员及球队Game Logs |
| F03 | 逐场双方Box与比赛细节 |
| F04 | 投篮图、热区及出手类型 |
| F05 | 球队赛季统计与战绩 |
| F06 | 球员赛季累计与每场指标 |
| F07 | 全球球员模型池及新秀身份 |
| F08 | 30队名单归属与人数核验 |
| F09 | 教练19项默认设置、POE与体系 |
| F10 | 整体防守与对手Gameplan |
| F11 | Playbook、战术与Freelance |
| F12 | ACE及真实战术执行反馈 |
| F13 | 个人属性、耐久、潜力数据 |
| F14 | 球员倾向及个人PlayTypes |
| F15 | 球队/个人训练设置 |
| F16 | 实时体力、疲劳及伤病 |
| F17 | 自然成长与退化历史 |
| F18 | Loyalty/财务偏好/人格徽章参考 |
| F19 | 合同条款、选项与Bird状态 |
| F20 | 球队薪资与市场可支出能力 |
| F21 | 自由市场与真实签约 |
| F22 | 普通球员交易与审批执行 |
| F23 | 简单选秀权权属及V4规则 |
| F24 | Draft Class导入、轮回与真实选秀 |
| F25 | Scouting、Mock Draft及不完全信息 |
| F26 | 员工、职位、薪资及雇聘 |
| F27 | Setup、Game Speed与世界设置 |
| F28 | 日历Simulation引擎设置 |
| F29 | 3D Gameplay与USER/CPU滑块 |
| F30 | Normalize Stats/Minutes与统计冲突 |
| F31 | 3D、SimCast、QuickSim模式事实 |
| F32 | 游戏时间、阶段、数据批次身份 |
| F33 | 奖项、名人堂与历届获奖者 |
| F34 | NBA纪录、生涯纪录及队史 |
| F35 | 社交媒体、实力榜和新闻 |
| F36 | League Rule Changes与生效规则 |
| F37 | Save、Autosave、重载和SteamCloud |
| F38 | 历史比赛、交易、选秀跨年留存 |
| F39 | 外挂全量采集/SQLite/发布与重发 |
| F40 | 三套时间轴、历史参考和历史重力 |

### 统一查询接口应当返回

`object_uid`、`save_id`、`season_id`、`game_date/capture_at`、`field_key`、`raw_value`、`display_value`、`unit/enum`、`source`、`freshness`、`role_visibility`、`coverage_unknowns`。这是需求合同，不代表这轮已实现。

特别不能漏：球队/球员的基础和进阶统计、比赛逐场Box、真实合同与签权、教练Gameplan、完整球员属性/倾向/徽章、联盟工资/财务、选秀球探进度和报告、历史奖项与交易新闻、世界设置及当前赛季阶段。

## 6. 下一步做什么，才是真正做到“足够参加游戏”

1. **先请Human按业务领域审阅**：哪些是每个GM/Coach/Player人格真正可请求的动作，哪些属于世界管理员/特殊编辑；旧研究中的经营权限不是当前Native调用能力。
2. 对保留项补`value_domain`：教练六种POE原生enum、余下13项设置、18项个人防守、战术book 68槽+12类、4Freelance、4PlayTypes、训练原生64字节结构与日期键、合同条款及球探目标槽等，已有值直接引用权威资料，未知不伪造。
3. **角色可发现能力API**：先有`list_actions(role,phase)`、`describe_action(action_id)`、`get_allowed_values(action_id,target_context)`、`read_current_state(...)`、`execute_exact_action(...)`，每项返回当前`AVAILABLE/STATIC_CANDIDATE/UNKNOWN`。这会让人格模型知道“可以调整什么、有什么含义、给什么参数”。
4. 能力完成门不是单元测试计数，而是**动作全集覆盖率**：每项要么完整Native调用合同与实例证据，要么确切代码障碍，无法覆盖时明示属于外挂消息/世界操作；不要因为只打通一种交易就宣称交易域全部完成。
5. **本轮不发布Codex任务，不执行游戏，不修改master**。先完成Human需求共识与结果建模，之后一次性制定按能力清单全覆盖的Codex实现任务。

## 7. 需要Human重点裁决的三个逻辑边界

- **球员原生编辑权**：`Player`人格能自行改变属性/徽章吗？还是仅管理员/GM特殊世界修改，Player只能提出训练/发展要求？目录已标为`WORLD_EDIT_OR_ALLOWED_ROLE_CONTEXT`，未代Human裁定。
- **经营下的球队自动化**：外挂全面接管GM/教练/球员后，`World`何时推进赛季、调用QuickSim/3D、处理休赛期阶段？这必须有统一阶段控制器，不能由30个GM并发推进。
- **Role数据权限**：未来哪些字段（球员真实潜力、未解锁球探、人格私人状态）可由对应角色查看，不能因内部Native字段可读就自动给全联盟所有角色。

**可追溯来源**：`01_资料归集/既有终极联盟资料来源与复用索引_v1.md`、完整机读操作目录与REA交叉表。本稿是第一轮大范围能力种子，仍需去重、细化字段值域与Human确认，绝不因当前183项就宣称完整游戏能力穷尽。
