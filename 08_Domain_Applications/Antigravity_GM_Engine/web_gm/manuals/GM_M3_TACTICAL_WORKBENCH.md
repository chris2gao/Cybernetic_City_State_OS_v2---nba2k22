# M3-T 战术、角色、训练和轮换工作台

PR #12 F1–F4：有效蓝图无原生动作时只标native_action_status=HOLD，市场仍需原内部优先/人才缺口/财务/双方谈判；执行组合仅可选INTERNAL+VIABLE_CANDIDATE。当前演化须匹配蓝图版本/来源，旧历史不能照搬为当前策略；前态存档身份或历史线不能确认时HOLD。详见[B4/B5手册](../../docs/BPTI_B4_B5_M3_REASONING_AND_EVOLUTION.md)。


BPTI工作包C新增按需的篮球理由与球队演化：[B4/B5操作契约](../../docs/BPTI_B4_B5_M3_REASONING_AND_EVOLUTION.md)。使用原gm_decision的submit-blueprint/record-evolution，之后沿现有评审/备选/定稿；同批GM_SANITIZED、当前蓝图版本和既有DEV14权限不变。HOLD/内部优先/市场成本必须与体系角色相连，文化不随单月输赢重写。候选历史不会自动成为正式GM、玩家批准或游戏动作。

共享战术知识入口见[GM共享战术池](../../docs/GM_SHARED_PLAY_POOL_V1.md)：按名称/用途/球员职责/球队打法查共享条目，完整卡含类型状态、用途、适配及风险；球队手册是有限槽位对池的引用，同条可被多队使用。球员四PlayTypes和教练四Freelance都前槽优先、执行更多（玩家说明），但两组并非同一配置，也没有固定百分比。精确原生类型未知时不拿名称推断冒充匹配；归档在哪本书出现不证明当前档所属，正式源与批准照旧。

版本M3_T_V1，2026-10-20。复用M3A/M3B与已随PR #5合入main的DEV14；本工具仍为DEVELOPMENT_CANDIDATE，GM V4未启用。它准备可供玩家审阅的稀疏意图，不运行stage/preflight/apply，不采集、不写游戏。底层执行约定见[DEV14手册](../../docs/DEV14_STATE_IO_RUNBOOK.md)。

2026-10-20操作知识补录：[DEV23手册与玩家调用规则](../../docs/development_research/BPTI_DEV23_MANUAL_AND_PLAYER_CALLING_RULES_ADDENDUM_V1.md)。玩家说明（PLAYER_REPORTED_UI）：同一战术可以出现在多个类型中，球员四槽填类型、先匹配类型再选本队条目；1/2主用、3/4偶尔，执行效果/教练等会影响选择；CPU对打自动调用，指定按键调用属于人类操作。无固定位置资格限制，不要求固定受益人认证作为类型匹配前置；逐CRC原生类型尚未取得时仍TYPE_UNKNOWN。无需研究精确频率/系数或保证每场调用次数。

球员四个PlayTypes、球队四个Freelance与POE是不同配置层；POEOffense2/3在当前目录分别为节奏/篮板方向，不是第二/第三得分手。该补录不新增原生映射、评分选择执行器或GM权限，Knowledge/BPTI默认可读覆盖、同批GM_SANITIZED及DEV14具体审批不变。

## 1. 先取得合格来源

M3所有新prepare和市场筛选必须先通过QuerySession.require_gm_sanitized()。只消费potential_v1/GM_SANITIZED新批次；原M02及旧M3缓存不供GM球探，不改历史、不提供绕过开关。实际新全量采集由玩家另外触发。

```powershell
python -B scripts/gm_analysis.py prepare --career SAVE --batch SANITIZED_BATCH --season 2021-2022 --node-type CHECKPOINT --run A_T1 --defense-matchup IND:GSW
python -B scripts/gm_analysis.py team --run A_T1 --team IND
python -B scripts/gm_analysis.py players --run A_T1 --team IND --limit 5
python -B scripts/gm_analysis.py native --run A_T1 --team IND --target-kind PERSONAL_DEFENSE --limit 20
python -B scripts/gm_analysis.py native --run A_T1 --team IND --field-key rotation.intangibles --limit 5
```

示例球队只是查询条件，不是已授权经营。所有命令共用原--workbench/--query-root/--published-root。多个具体对手重复--defense-matchup OWNER:OPPONENT；仅这些个人对位在prepare时读入，其余未请求对位不能当已读或缺失。需要补充对手时，prepare同批新run并用--supersedes-run引用旧run；不修改封存包。列表按原cursor继续，小页可能少于limit。

M3读取DEV14同批对象键/字段/原生身份与实例/代次，不给模型raw或地址。M0保留team stats、rotation/native_objects/native_books和原有域，另有native_context元数据与coach_traits安全投影。后者复用已有DEV12读取器，在封存COACH_DEFAULT记录上解码8体系熟练度与教练评级，不打开进程，也不把最高熟练度当必须选择的体系。

球员Potential在面板中为value=null、persisted_placeholder=1、MASKED_NOT_GAME_OBSERVED；不进decoded_attributes、成长变化或市场筛选。Intangibles在轮换面板单列，同样不进入真实篮球能力/市场实力筛选。Staff属性不按Player Potential屏蔽。

## 2. 六维研究与内部优先

沿用原[分析手册](ANALYTICS_M3_WORKBENCH.md)的注释/封存，以及[GM手册](GM_M3_DECISION_WORKBENCH.md)的P1–P5、双边报价和版本。新T包的review模板增加：

```powershell
python -B scripts/gm_decision.py begin --analysis-run A_T1 --run D_T1 --mode development --season-phase REGULAR
python -B scripts/gm_decision.py template --analysis-run A_T1 --team IND
```

- internal_tactical_diagnosis_refs：使用tactical:TEAM、tactical-player:IDENTITY、tactical-playbook:TEAM、tactical-training:IDENTITY、native:ROW_ID或native-object:OBJECT_KEY等实际引用。
- rejected_internal_fixes：每个被否定内部修复的reason和evidence_refs；可以有理由HOLD，不强迫调整。
- market_gap_after_internal_assessment：status=NO_GAP/GAP_REMAINS/UNKNOWN、reason、evidence_refs。缺口也可以是合同/资产窗口，不限于球员技能。
- evidence_quality：native_fields说明来源，behavior只可BASKETBALL_REASONING/RESEARCH_HYPOTHESIS/HEURISTIC_THRESHOLD/UNKNOWN。play_type_coverage目前必须UNKNOWN；现有68槽CRC不证明真实PlayType/受益人。
- 每人的role_plan：role=STARTER/SIXTH_MAN/ROTATION/DEVELOPMENT/HOLD、minutes_target_band（有序非负两数或null）、reason。范围只是经营目标，实际换人与分钟由原版AI负责。

D1比较教练职责和熟练度；D2比较体系/当前书/实际可知与未知覆盖和反制；D3比较真实技能、四槽、具名倾向、角色与样本分钟；D4在内部改善之后讨论市场；D5比较合同、自然成长与已知训练；D6给哲学、反例和下次观察条件。Touches≥75、卡片PassingIQ阈值和教练最高熟练体系均不是自动交易或改体系规则。DEV12知识卡仅作为篮球推理/阈值假设参考，3D和CalendarSim效果保持UNKNOWN。

MARKET=VIABLE_CANDIDATE要求GAP_REMAINS及有证据的内部替代否定；报价双方都须先有此比较，不能跳过内部方案。证据不足仍可市场研究或HOLD。此条件不替球队计算统一球员价值，也不保证成交。

## 3. 在INTERNAL方案内提交稀疏动作

各动作继续放在submit-alternatives的action内。必填action_id/kind/reason/evidence_refs/expected_effect/uncertainty/counterplay/why_better_than_hold；team_id由所属方案绑定。changes严格为DEV14的五个字段：

```json
{
  "action_id":"IND_ROLE_1",
  "kind":"LINEUP_ROLE",
  "role":"SIXTH_MAN",
  "minutes_target_band":[24,30],
  "reason":"填写本批角色和机会成本比较",
  "evidence_refs":["tactical-player:从本批players取得完整身份"],
  "expected_effect":"方向性轮换假设，不保证分钟",
  "uncertainty":"疲劳和真实轮换效果未知",
  "counterplay":"若关键时段防守失衡则保留其他组合",
  "why_better_than_hold":"填写为何优于当前方案及其反例",
  "changes":[{
    "action_id":"IND_ROLE_1_INTANGIBLES",
    "object_key":"从本批native查询取得",
    "field_key":"rotation.intangibles",
    "target_value":70,
    "reason":"仅为策略性AI轮换偏置"
  }]
}
```

这只是输入形状，数字不是当前球员建议或批准。按同批Registry选择原生枚举，不能凭示例猜ID。

| kind | 可用内容 | 约束 |
| --- | --- | --- |
| COACH_DEFAULT | coach.*正常18项 | 五Sim只读；PlaybookID不能日常修改；保留19项原生读取 |
| PERSONAL_DEFENSE | personal.*，可含多名对手球员 | 必须是本批实际观察对象与双方身份；AUTO是实际枚举，不等于缺失；不能回退整体 |
| PLAYER_PLAY_TYPE | playtype.slot1..4 / initiator | 保留四槽顺序，不从CRC猜覆盖 |
| PLAYER_TENDENCY | 48个tendency.具名字段 | 51个RAW未知字段不使用/不提案，阈值是研究假设 |
| TEAM_EXCLUSIVE_PLAYBOOK_CONTENT | playbook.slot | 只改当前本队同名书的实际槽；target取当前加载CRC目录；未知动作语义仍UNKNOWN |
| TRAINING_PLAN | training.team.* / training.player.* | 球队6项、球员5项；九个通用原型不冒充每位置全部UI模板；不改单项能力/潜力/徽章 |
| LINEUP_ROLE | rotation.intangibles，25–99 | 仅软影响原版AI，不锁分钟，不使用被调OVR作市场实力 |
| TEAM_BOOK_REBIND | 独立事件后的coach.PlaybookID | 使用下一节的专用步骤，不能与旧槽位编辑拼为一次批准 |

同字段不同目标报NATIVE_FIELD_CONFLICT；相同目标合并、保留各原方案理由。多个字段的共享字节合并复用DEV14编码器。交易影响的人员/对位/训练/战术旧目标转研究，等待新来源；同队重叠交易继续遵守原执行器范围。员工聘用/合同竞价仍无执行器，COACH_CHANGE只能是受休赛期/次数约束的研究提案。

## 4. 已确认换帅后的本队手册恢复

每队每游戏赛季只允许休赛期一次主动换帅。--season-phase是玩家明确给出的业务语境，不是自动日历或休赛期控制器。换帅确认记录跨本工作台同career/season的节点累计，不通过新开节点重置。

1. 玩家实际完成并确认换帅后，使用已更新的同批当前教练来源。业务节点使用--season-phase OFFSEASON。
2. 从本批native-object证据取得完整current_coach_identity，提交event.json：event_id、kind=CONFIRMED_COACH_CHANGE、reference（真实玩家确认引用）、team_id、current_coach_identity。初始存档绑定可用INITIAL_SAVE，但节点须BOOTSTRAP/SEASON_INITIALIZATION。
3. 运行`gm_decision.py record-coach-event --run D_T1 --input event.json --expected-revision N`。这保存事实引用/业务次数，不批准游戏写入，也不声称有员工签约执行器。
4. INTERNAL动作使用kind=TEAM_BOOK_REBIND、event_id和上述通用理由/证据字段，不让模型自选目标BookID。工具匹配当前加载的本队name/enum_id/index/unique_id，生成独立单动作意图；A队/B教练恢复A书，B书不改。
5. 具体绑定经玩家另行批准并由DEV14执行后，等待玩家触发取得新来源，再prepare新包和另一份槽位内容方案。旧槽位不沿用；同节点里选了绑定又选旧战术内容时，后者标POST_REBIND_SOURCE_REQUIRED。

无需克隆/新建30本书或先研究假想共享冲突；真实无法匹配本队书时只阻断该动作。

## 5. 离线准备、终稿与执行交接

select/validate/finalize继续使用原expected-revision流程。validate调用已有gm_state_io.plan.build_plan做静态来源计划，不调用stage或任何live preflight。

```powershell
python -B scripts/gm_decision.py validate --run D_T1 --expected-revision N
python -B scripts/gm_decision.py artifact --run D_T1 --kind VALIDATION --artifact-id current --section generated_artifact_refs --limit 1
python -B scripts/gm_decision.py finalize --run D_T1 --expected-revision N
python -B scripts/gm_decision.py export --run D_T1 --output _exports/D_T1_handoff
```

工件含实际稀疏intent、数值diff、DEV14生成的digest、完整审批tuple、动作理由与假设；不含地址或raw/hex。OFFLINE_PREPARED只证明该封存来源上的规划成立，仍需匹配ACTIVE/实例/代次并执行stage、玩家具体批准、实时预检。批准tuple文件本身不能批准。

导出额外提供intent_N.json和approval_tuple_N.json，只为OFFLINE_PREPARED项生成。单独批准后由执行窗口使用现有`gm_state_io.py stage --career SAVE --source-batch B --proposal intent_N.json`；执行仍遵守DEV14完整审批元组、操作者聊天批准引用和编辑页退出要求。M3不会替玩家调用这些执行步骤。源/身份漂移、坏枚举或未观察对象只进入阻断/研究清单，不伪造“已可执行”。

## 6. 明确未覆盖

CRC→真实战术类型/受益人、51项未知倾向、位置专属UI训练模板、实时疲劳与导师关系、比赛因果系数均保持UNKNOWN/NOT_OBSERVED，交Antigravity后置扩展。原始能力/潜力/徽章、精确分钟锁定、教练合同竞价/完整休赛期市场、额外World/Gameplay开发、历史新秀注入均不属于本次M3-T。正式V3、赛季档案与30队UNASSESSED状态不自动改变。
