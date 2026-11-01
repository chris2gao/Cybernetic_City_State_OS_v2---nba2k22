# 角色模型需要知道哪些数值与输入：现有证据合同 A-v1

**目标**：让外部GM、Coach、Player模型能问`describe_action`、`get_allowed_values`，然后向Native执行层发送**自己已决定**的参数。这里列的是原生现有证据，不做策略最优解释或决策算法。游戏机制引用见`01_资料归集/既有终极联盟资料来源与复用索引_v1.md`。

## 1. 当前 Coach 可解释的十项参数

| 输入字段 | 已有原生取值/含义 | 可证明的执行层 |
|---|---|---|
| `POEOffense` | 0无偏好、1冲击篮筐、2让射手得到机会、3低位进攻、4挡拆进攻、5均衡、6围绕得分手 | 通用Apply已恢复，具体枚举全面实机未覆盖 |
| `POEOffense2` | 0无偏好、7耐心、8均衡、9快速自主出手 | 通用Apply已恢复 |
| `POEOffense3` | 0无偏好、10冲抢进攻篮板、11均衡、12限制对手转换 | 通用Apply已恢复 |
| `POEDefense` | 0无偏好、13保护内线、14均衡、15限制外线投篮 | 14→13曾实机成功 |
| `POEDefense2` | 0无偏好、16保守、17均衡、18身体对抗 | 通用Apply已恢复 |
| `POEDefense3` | 0无偏好、19保护防守篮板、20均衡、21发动转换 | 通用Apply已恢复 |
| `RunPlayTendency` | 角色可理解的UI范围0..100；原生当前字段是uint8 | 90→55曾实机成功 |
| `ZoneUsage` | UI意图0..100，原生当前字段uint8 | Setter/Projection路径已恢复，单字段未实机新证 |
| `BenchDepth` | 原生uint8；**真实UI最大轮换人数尚未证实** | 有当前字段，但不能直接以uint8上限=255开放 |
| `BenchUtilization` | UI意图0..100，原生当前字段uint8 | Setter/Projection路径已恢复，单字段未实机新证 |

**额外教练对象设置不能漏**：旧K04还列`PreferredSystem/ActiveSystem`，对应原生0..7：Balanced、Grit and Grind、Pace and Space、Perimeter、Post、Triangle、Seven Seconds、Defense；以及Tempo、HelpDefense（来源记录的取值0..100）、4个Freelance槽、PlaybookID、ACE/教练自动配置和对手Gameplan。**不因为新REA仅封装10项，就从执行需求模型删除其余字段。**

## 2. 战术、手册和个人防守的独立动作合同

- **球队战术手册**：4个区块`Regular(30)`、`Bench(20)`、`Endgame(10)`、`Favorite(8)`，**共68个原生槽**。应提供`read_book(team)`、`list_play_candidates(type)`、`add/replace/remove/swap_play(team,section,slot,play_crc)`、`replace_playbook(team,book_id)`。同一CRC可被不同球队引用，不允许错误修改共享池本体。
- **球员PlayTypes**：每人四个**有序**槽，当前原生研究枚举0..15：0 None、1 Isolation、2 Isolation Point、3 Isolation Wing、4 P&R Ball Handler、5 P&R Point、6 P&R Wing、7 P&R Roll Man、8 Post Up Low、9 Post Up High、10 Guard Post、11 Cutter、12 Handoff Receiver、13 Handoff Passer、14 Mid Range、15 3PT。四槽是“允许被安排的战术类型”，**不是**直接向某球员写四个play CRC。
- **十二种战术类别**：单打、挡拆、中投外弹、三分外弹、挡拆选项、低位、高位、后卫背身、中投、三分、手递手、切入。**类别显示标签和球员PlayTypes枚举不应机械强配**；CRC→类别的全部当前映射尚需恢复。
- **Freelance**：教练4个有序槽；旧研究已登记34种原生枚举raw0..33，具体名字与Native应用/保存路径须用既有字典展开和补齐，不应直接要求决策模型输出裸内存地址。
- **针对对手个人防守**：以下18个**各自独立的**设置项都要能按`team_id, opponent_uid, field, native_enum`执行：`PressureOnball`、`PressureOffball`、`ForceDirection`、`ScreenDefenseOnBall`、`ScreenDefenseHedge`、`OffballScreenDefense`、`PostDefense`、`DoubleTeamPerimeter`、`DoubleTeamPost`、`ScreenDefenseOnBall5`、`ScreenDefenseHedge5`、`SwitchRule`、`OnballHelp`、`ScreenHelp`、`ExtendPressure`、`TagOnRoll`、`StayAttached`、`PreRotate`。原生enum字典以旧V2/DEV14真实记录为源，本次没有逐字段填未经证实的数值。

## 3. GM 资产和合约的原生输入合同

### 交易

```json
{"action_id":"TRADE_EXECUTE_AGREED_PACKAGE","parameters":{
 "team_a":20,"team_b":1,
 "players_a":[7239],"players_b":[7716],
 "picks_a":[],"picks_b":[]}}
```

- `team_id`是当前存档逻辑球队ID；`player_uid`为原生PLAYER UID16；`pick_uid`为原生PICK UID32，交易双方资产方向必须明确。
- 现有私有提案物理容量18个资产元素。**此容量是当前结构证据，不是对外部GM“交易价值”限制**。同一资产不能重复，输入不能是空交易。
- 当前默认Native执行路径为`AddPlayer/AddPick→context→Process`，**跳过外围FullCheck/经营匹配**。Process内部对象与资产存在性检查仍属于游戏原生执行；薪资/实力协商由GM自己完成。
- 已实测的是指定球员不等薪一换一；多球员、签权、混合包需要保留独立成熟度，不把调用参数存在当成所有包已经测试。

### 合同/签约

`GM.sign(team_id,player_uid,terms)`中的`terms`应明确`years`、逐年薪资、合同类别、球队或球员选项、延期条款/交易限制等，**不得让执行器自动生成报价**。已有原生字段研究包含：
- 合同年限`original_contract_years`、`years_left_on_contract`、`extension_length`；
- `contract_year_1..6`六个独立raw金额槽；
- `contract_option` 0 Null、1 Team Option、2 Player Option、3 2-Year Team Option；
- `extension_option`、`contract_type` (0 Core、1 Hardship、2 Two Way、3 Euro Stash、4 Lineup)；
- `no_trade`、`extension_no_trade`、`bird_years`、`two_way_days_left`、`euro_stash_years_left`。
这些字段是**结构研究**；签约Native Offer→Accept→Process真正完整事务尚不具备可执行合同，不能将可编辑某个合同字节等于签约成功。

## 4. 员工、训练、选秀和球探的参数合同

- **STAFF职位原生码**：0 Head Coach、1 Assistant Coach、2 Head Scout、3 Trainer、4 GM、5 Governor、6 CFO、7 Assistant GM。13项字段/八类F..A+能力评级来自旧R05C，但员工雇聘、岗位关联、合同/解聘Native入口仍是需求缺口。
- **Training**：已有`TEAM_TRAINING(team_id,native_date_key,payload64)`调用候选，其中三项float focus、三项uint8 profile、38项uint8 subfocus和`intensity_raw` 0..7；仅调整强度时须保留其余输入字段。旧K06`home_intensity/away_intensity` 0..5是**不同字段和不同概念**，不能将两者合成一个所谓“通用强度枚举”；训练日的date_key编码与很多子索引的具体语义仍需恢复。
- **球探**：已验证`SCOUT_SET_EXISTING_GOAL_TARGETS(team_id,goal_index=0..2,prospect_uids)`对已有Goal修改；历史静态结构有最多3个Goal槽、指定人选最多17个；满槽Append已经返回0拒绝，`SCOUT_EXECUTE_CURRENT_TRIP` 尚未实测。安排目标≠完成考察，原始点数≠角色已解锁完整报告。
- **选秀**：`DRAFT_SELECT_PROSPECT(team_id,pick_uid,prospect_uid)`仅当当前原生选秀大会处于对应签位时才可尝试；输入签位当前持有者和本届真实候选。此为静态恢复，尚无实机选秀成功证据。
- **玩家能力/倾向/徽章**：旧PLAYER研究有39项明确名字的非耐久能力、16项Durability、48项已命名倾向、另有未知字段和Gameplay/Personality Badge参考名录；**字段/标签存在不等于原生完整编辑函数已恢复**。将每个字段的`field_id,display_name,type,range,meaning,NativeSetterStatus`作为后续字段级结果模型，不能一概开放给Player人格直接修改。

## 5. 要交给所有角色模型的机制说明卡

```yaml
action_id: COACH.SET_POE_DEFENSE
who_may_request: [COACH]
target: {team_id: required}
values:
  13: "保护内线"
  14: "均衡"
  15: "限制外围投篮"
  0: "无偏好"
meaning: "选择对应球队防守侧重点"
known_game_effect: "当前Coach字段可通过原生Apply更新；精确比赛收益不研究"
native_execution: "COACH_APPLY_DEFENSE_POE / known current-Gameplan projection"
implementation_status: "LIVE_EXACT_FOR_14_TO_13"
required_readback: ["target_team_and_coach_identity","current_POEDefense"]
```

其它动作使用相同卡片原则。**文档要让模型知道可做什么、有何含义、给出哪些值与ID、怎样提交；不是告诉模型哪个选项最好。**

本页完全不运行游戏、也不改旧REA实现代码，现有值域每项另有历史出处，不以这份规划稿提升可执行性等级。
