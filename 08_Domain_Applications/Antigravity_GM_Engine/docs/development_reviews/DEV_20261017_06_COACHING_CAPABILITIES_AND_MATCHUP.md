# 教练比赛计划可修改范围与指定对手评估

2026-10-17，基于已复核原生字段及本次隔离局证据。玩家最后要求停止重复保存重载测试，改为梳理全部已定位设置及高风险缺口。以下范围为教练比赛计划；不包含联盟交易规则、全局滑块、球员成长或人物属性。

## 默认设置：24个已定位字段

“正式可用”指执行器技术门槛通过，仍须玩家批准具体球队、版本、动作及值。`writable=true`仅说明存在受控编码能力，不能替代正式验收。当前14字段具备隔离编码，只有六项POE正式门槛开放；其余10字段只读。明细及实际观察值见[机器清单](DEV_20261017_06_COACHING_CAPABILITY_INVENTORY.json)。观察到的最小/最大值不是菜单合法边界。

| 字段 | 内容或已确认值域 | 当前修改能力／风险 |
| --- | --- | --- |
| POEOffense | 进攻重点：0无偏好、1GET_TO_BASKET、2GET_SHOOTERS_OPEN、3FEED_THE_POST、4PICK_AND_ROLL_OFFENSE、5NEUTRAL_OFFENSE_FOCUS、6RUN_OFFENSE_THROUGH_SCORER | 正式可用，须具体审批 |
| POEOffense2 | 进攻节奏：0无偏好、7PATIENT_OFFENSE、8NEUTRAL_OFFENSE_TEMPO、9SHOOT_AT_WILL | 正式可用；先退出编辑页 |
| POEOffense3 | 进攻篮板：0无偏好、10CRASH_OFFENSIVE_BOARDS、11NEUTRAL_OFFENSE_REBOUND、12LIMIT_TRANSITION | 正式可用，须具体审批 |
| POEDefense | 防守重点：0无偏好、13PROTECT_PAINT、14NEUTRAL_DEFENSE_FOCUS、15LIMIT_PERIMETER_SHOTS | 正式可用，须具体审批 |
| POEDefense2 | 防守强度：0无偏好、16PLAY_CONSERVATIVE、17NEUTRAL_DEFENSE_TEMPO、18PLAY_PHYSICAL | 正式可用，须具体审批 |
| POEDefense3 | 防守篮板／转换：0无偏好、19CRASH_DEFENSIVE_BOARDS、20NEUTRAL_DEFENSE_REBOUND、21RUN_IN_TRANSITION | 正式可用，须具体审批 |
| SimPace | 0VERYLOW、1LOW、2AVERAGE、3HIGH、4VERYHIGH | 隔离编码；2→4→2内存验证，未独立保存认证 |
| SimPress | 0LOW、1AVERAGE、2HIGH | 隔离编码；未独立实机验收 |
| SimHelpDef | 0LOW、1AVERAGE、2HIGH | 隔离编码；未独立实机验收 |
| SimOffReb | 0LOW、1AVERAGE、2HIGH | 隔离编码；未独立实机验收 |
| SimDefReb | 0LOW、1AVERAGE、2HIGH | 隔离编码；未独立实机验收 |
| PreferredSystem | 原生八种体系0–7 | 隔离编码；未验证与ActiveSystem的加载／覆盖关系 |
| ActiveSystem | 原生八种体系0–7 | 隔离编码；不能顺带写体系熟练度 |
| PlaybookID | 当前加载且名称可识别的战术本ID | 隔离编码；未独立选择验收；不改共享战术内容 |
| BenchDepth | 8-bit存储 | 只读；真实菜单范围及单位未认证 |
| RunPlayTendency | 8-bit存储 | 只读；不能仅由存储宽度推定0–100可写 |
| ZoneUsage | 8-bit存储 | 只读；范围未认证 |
| BenchUtilization | 8-bit存储 | 只读；范围未认证 |
| Tempo | +0x148，bit9，width8 | 只读；不是POEOffense2，也不是SimPace |
| HelpDefense | +0x148，bit17，width8 | 只读；不是SimHelpDef |
| FreelanceType | 原生6-bit枚举 | 只读；与其他三个槽的选择／激活关系未认证 |
| FreelanceType2 | 原生6-bit枚举 | 只读 |
| FreelanceType3 | 原生6-bit枚举 | 只读 |
| FreelanceType4 | 原生6-bit枚举 | 只读 |

八种体系原生标签为BALANCED、GRIT_AND_GRIND、PACE_AND_SPACE、PERIMETER、POST、TRIANGLE、SEVEN_SECONDS、DEFENSE。COACHDATA反射共有142字段，不代表142项都属于教练比赛计划或都可安全修改；身份、能力、合同等不得因共享对象而纳入写入。

## 指定对手是否需要修改

**默认方案用于建立球队的基础打法；指定对手是有具体例外时才需要的独立能力。** 例如玩家批准某队平时采用一套进攻重点，但面对特定对手时要换另一套，则默认COACHDATA本身无法表达两个不同的目标。此时有必要开发并验收针对该对手的覆盖。没有具体对手例外需求时，不必为同一基础打法把29条记录全部写一遍。

这是产品范围建议，尚不是对2K22原生加载顺序的已证实描述。当前证据如下：

- 已定位每队独立的29个有效对手记录，共870条，所有权及对手集合均验证；COACHDATA与Gameplan的存储布局不同。
- 修改默认配置后，玩家在“所有球队”和“指定对手”页面都看到目标值。该现象说明本次默认修改能在对应页面呈现，**不能证明可以仅修改一个对手而不影响其余对手**。
- 现有870条记录的`IsInUse`原始值均为0；部分对手POE字节与当前默认值不同。原生UI／保存操作期间还观察到部分PHI对手字节变化。执行器对Gameplan写入次数始终为0。因此不能凭0断定禁用，也不能由字节差异认定已独立生效。
- 可以读取、排序并离线生成`VS_OPPONENT`预设；实际执行仍报`MATCHUP_EXECUTION_BLOCKED_NOT_ACTIVATED`。不会猜写`IsInUse=1`或批量复制默认值。

将来确需独立对手覆盖，优先进行有针对性的只读差分：玩家在隔离局只改变一个对手的一项已知POE，比较对应记录、管理器、默认教练块及其他28个对手；再观察回退默认和重新载入。仅在原生激活、继承、取消及保存机制得到证据后开放该子模块。这里记录下一阶段验证设计，不自动发起这一轮测试或菜单操作。

## 其余只读范围及真正需要关注的风险

对手Gameplan还包含六项POE、HelpDefense、RunPlayTendency、ZoneUsage、BenchDepth、BenchUtilization、LineupFormFactor、PlaybookId、FreelanceType；它们都因激活语义未明而保持只读。普通轮换记录能读取PlayerId、RotationSpot、PlayingTime，但人物引用、分钟单位和约束未验收，高级轮换也未开放。

防守8-byte结构的18字段已定位为：PressureOnball、PressureOffball、ForceDirection、ScreenDefenseOnBall、ScreenDefenseHedge、OffballScreenDefense、PostDefense、DoubleTeamPerimeter、DoubleTeamPost、ScreenDefenseOnBall5、ScreenDefenseHedge5、SwitchRule、OnballHelp、ScreenHelp、ExtendPressure、TagOnRoll、StayAttached、PreRotate。已保存逐字段真实掩码与原生枚举CRC；尚未完整还原标签及证明人物匹配和覆盖语义，所以保持只读。ScreenDefenseOnBall与ScreenDefenseHedge绝不合并。

后续高风险验证集中于：滑块合法范围和单位；两个体系字段的加载关系；四个Freelance槽的作用；Gameplan独立覆盖和回退机制；防守人物匹配及轮换约束。已验证六项POE不再为每个合法值逐次保存重启。Sim枚举及体系枚举布局已经原生确认，不能再描述成“取值未知”；它们缺的是各自实机采用／持久性证据。

本轮六项已在内存恢复原值。玩家叫停恢复后的额外保存重载，所以不声称恢复后的存盘结果已再次验证。比赛效果保持`SIM_EFFECT_PENDING_PLAYER_MONTH`。
