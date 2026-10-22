# DEV — NBA2K22 PC MyLEAGUE 原生GM经营能力/内存入口查找清单 V1

> **2026-10-19 玩家职责修订**：本V1中把员工任免、完整Playbook、阵容角色、原生选秀/球探/自由市场UI等交给Antigravity研究的任务分配已被玩家修改。**新的权威分工为[原生控制与外挂市场边界V2](DEV_20261019_MYLEAGUE_NATIVE_GM_CONTROL_DISCOVERY_V2.md)**：员工合同/教练与阵容由Codex开发；签约/休赛期/选秀/球探经营逻辑由外挂GM虚拟市场承担、Codex处理必要游戏结果同步；Antigravity继续训练、导师、疲劳/伤病读数、士气和赛场事件等。V1保留为历史查找目录，不应直接执行旧优先级。

- 2026-10-19；Web Development。**Antigravity调研工作清单，并非所有模块立即开发的授权。** M3 GM V4仍是首要开发任务。玩家确认先前交给Antigravity的**全局设置已全部可实际设置和修改**；以用户已验收成果为起点，不要求重复全局设置扫描。
- 目标：每项真正的人类终极联盟经营动作都寻找对应内存**对象/配置→决策输入→提交操作或受控写入→业务状态读回**，让GM在每月/休赛期检查点可以通过外挂完成同等或更多操作，而不是只掌握菜单图片。
- 权威当前能力入口：[当前工程状态](../34_BASELINE_CURRENT_STATE.md)、[GM能力缺口审计](../research/NBA2K22_MYLEAGUE_GM_CAPABILITY_GAP_AND_MONTHLY_TRAINING_V1.md)、[PC玩法手册](../research/NBA2K22_PC_MYLEAGUE_PLAYER_OPERATIONS_AND_SYSTEMS_GUIDE_V1.md)、[已证教练执行](../40_COACHING_EXECUTION_RUNBOOK.md)。M0/M1/M2已合并正式main，30队策略仍未评估/GM V4未启用。普通球员/简单签位交易有限验收；签到自由市场的真实执行与员工、训练/选秀操作未认证。
- 非目标：重新寻找玩家已认证的全局滑块；重复查已知教练19默认/对手整体18个字段；把旧`src/slider_manager.py`偏移未经实机认证当成新增入口；直接修改球员原始能力/潜力/徽章/倾向以制造竞争优势；未经玩家批准运行任何游戏修改。

## A. 优先级说明

- **P0**：最近就能明显提高GM经营和赛场竞技决策能力，优先查找**可读+可控的实际操作**。
- **P1**：休赛期长期经营不可缺；可随游戏阶段出现时查找，不需强迫跳赛季/新开局来找。
- **P2**：人物/媒体/联盟历史后续会用到，先登记可读来源与页面，暂不抢占M3。

## B. P0：七个原生能力簇

| ID | 查找能力 | 优先取证字段和操作 | GM价值 | 当前避免重复 |
|---|---|---|---|---|
| NC01 | **球队训练+个人专项计划** | 全队训练类型/强度/休息；每人训练方向/强度/重点属性类别/未来持续时间；启用CPU自动训练/队伍覆盖；计划生效时间/保存情况 | GM按月做稳健负荷与培养分配 | 全局成长速率已经属于已确认全局设置，不重查 |
| NC02 | **当前球员疲劳、恢复、伤病与可用性只读** | 累积疲劳/体能、比赛负荷、伤病标志与名称、伤病剩余时长、复出/可激活状态、是否恢复自动、身体状态随时间变化 | 没有这些读数不能安全实行高强度月度训练；也影响交易与轮换 | 当前`source_catalog.json` `injuries_availability_rotations`明确NOT_OBSERVED；读状态不等于要改伤病 |
| NC03 | **六职位制服组招聘/解除/换任** | CFO、GM、主教练、助教、首席球探、训练师：在职、候选、职位空缺、合同剩余/工资、员工实际加成字段；聘用/解聘/更换后的双向员工-球队指针、岗位占用与预算变动 | 让GM真正招聘教练和管理人员、建立独立组织文化 | 已有8个底层STAFF枚举和队反向指针**可读**；不因8个代码就声称6个UI岗位之外还能任命2人；已有1458员工池读数 |
| NC04 | **球队战术内部结构/执行优先级** | Playbook完整战术列表、增删战术、执行顺序/类别、球员Play Type/调用优先级，1/2/3得分选择（**只在当前PC界面实际存在时**）、实际使用主教练与球队体系联动、自动调用战术设置 | 教练19字段之外真正决定球员采用哪种打法；M3战术推导最有价值 | 已有`PlaybookID`仅表示手册标识，不等于完整战术；`PreferredSystem`不代表已控制每人战术调用；个人Play Type若属于原始球员数据，实际写入需单独边界审批 |
| NC05 | **球队阵容角色/出场资格** | 首发五人、非首发名单/激活名单、12/13人名单槽、两向合同和G-League归属/召回、球队角色、主要得分选项、默认阵容组（Tall/Quick/Defense等实际可用项）、阵容自动化与玩家控制边界 | GM落实已批准的人员管理与临场阵容结构 | 已验证交易只说明归属和人数可写，不说明所有激活/先发操作可写；**不重新开发精确每人分钟锁定**（游戏AI覆盖） |
| NC06 | **导师/徽章培养原生关系** | 导师对象、学生对象、每名学员可选的目标徽章与槽、徽章兼容约束、导师持续时间、学习进度（若UI存在）、解除/替换导师关系 | GM能够安排长期传帮带与职业培养 | 改导师关系不是外挂直接改徽章；可观察自然结果，不直接加徽章 |
| NC07 | **运行时攻防AI/教练临场覆盖** | ACE/Coaching策略实际状态、CPU自动调整开关、暂停后的进攻/防守策略、实时针对对手布置、换人自动/手动模式；区分预设内存块和比赛中实时状态块 | GM的教练战略是否真的在3D比赛发挥效果；日后打磨实时场上引擎的重要基础 | 已有指定对手整体防守18字段，不要重新实现；不能假装已有逐回合自动写入能力 |

参考证据：系列[Coaching指南](https://nba2k.fandom.com/wiki/Coaching)有Coach Gameplan、Edit Playbook与预设阵容概念；[NBA2K22玩家](https://www.reddit.com/r/NBA2k/comments/wsvt1u)提到通过Edit Playbook选择球员战术类型；[2022讨论](https://www.reddit.com/r/NBA2k/comments/yd446s)提到球队得分选项、Play Type与自动战术调用的关系。原生菜单位置与PC当前版本值域仍以玩家实机为准。跨版本/次世代Conditional Coaching不直接视为PC已存在。

## C. P1：四个休赛期经营能力簇

| ID | 查找能力 | 优先取证字段和**实际阶段操作** | 对GM的直接意义 |
|---|---|---|---|
| NC08 | **完整合同/签约/解除** | 自由球员身份确认、当前报价/意愿（如果有）、合同可用年限与球队/球员选项、报价提出与接受状态、续约资格/资格报价、裁员/释出、合同执行后球队人数与财政更新；识别2K合同承诺实际写入与名单更新链路 | M1情景工具目前仍不等于游戏签约执行闭环；解决真实经营最重要的剩余交易动作 |
| NC09 | **休赛期阶段机与不可逆操作** | 季后赛结束→选秀乐透→退休/员工→选项/资格报价→选秀→自由市场→训练营→新赛季的**实际PC顺序**；当前`phase_id`、按下推进后的提交/重置、结束条件、是否允许返回、CPU是否暗中代操作 | 让GM在正确时点决策，防止CPU抢先签人或跳过一届选秀 |
| NC10 | **原生选秀大会与历史选秀班绑定** | 本届选秀名单来源/已导入班ID、候选人唯一身份、球队选秀顺位、`on_clock`队、已选新秀/球队资产、实际选中动作、签约/入队、乐透与选秀结束状态；新秀轮回不可重复导入 | 从外部1984→2020历史库真正落地到游戏选秀流程，而不仅仅在SQLite里列出潜力新秀 |
| NC11 | **球探命令与知识状态** | 球探员工特质/预算（已采者复用）、球员名单、侦察选择/优先级/任务分派、进度/已揭示能力/球探报告、赛季重置时点 | 支持独立球探和GM不完全信息；当隐藏完整潜力在池中可见时，也要定义GM允许知道的信息边界 |

**休赛期操作不能只找字段**：优先定位“值在内存修改”和“游戏事务已经正式提交”是不是两回事。很多选秀/签约页面的内存可能只是UI临时选择/报价缓冲，没经过正确提交程序会被游戏重建。研究时如未获批准只做读取和UI正常操作差分，不直接强制触发任何交易。

## D. P2：后续球员/媒体世界会需要的只读事实，尽量顺路记录

| ID | 读数来源 | 为什么未来重要 | 当前建议 |
|---|---|---|---|
| NC12 | **原生士气/职业诉求/个性**：Morale、Team Chemistry、角色满意度、Play For Win、Financial Security、Loyalty、地理/大市场/天气等个性徽章，球队角色/续约/交易请求状态 | 给未来球员模型一个游戏原生初始人格，而不是凭名气幻想私人动机 | 优先只读、保存范围、默认不写球员情绪/职业愿望/原始倾向 |
| NC13 | **真实单场比赛、伤病、交易与新闻事件**：日程、GameID、box score、末节/关键比赛事件（若引擎可见）、本局季后赛树、成就/纪录触发、颁奖、退役/里程碑 | 数据分析反馈/媒体连续剧/林疯狂、记录与季后赛氛围，区别月度累计统计与真正逐场事件 | 先定位只读事件源；不要求Antigravity现阶段做赛场内采访资源注入 |
| NC14 | **球队形象与经营环境**：球迷支持、票价/销售收入、老板目标/财务容忍度（若当前PC世界存在）、市场规模、搬迁/扩军阶段状态及稳定队ID | 将来能比原生GM更真实模拟预算和老板，扩展到球队经济市场 | 全局货币和设置不重查；不要直接修改团队现金/声誉制造结果 |
| NC15 | **自然成长反馈**：球员训练与比赛导致的自然能力进步记录、训练效果、导师徽章增长的源头与历史时间 | 告诉GM原生训练是否有效及休赛期谁变强 | 只读结果，不允许直接改成长/潜力/徽章；是否存在历史记录以UI及真实内存证据为准 |

上述人物相关线索可参考[2K22 Attention to Detail玩家阵容项目](https://www.operationsports.com/nba-2k22-attention-to-detail-roster-from-celticlg-and-crew/)对Play For Win/Financial Security/Loyalty的记录；2K19玩家观察的是社区跨年经验，不能当原生2K22精确因果：[Barnsey帖](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/nba-2k-basketball-sliders/863174-barnsey-s-myleague-player-progression-regression-sliders-2k19/page6)。

## E. Antigravity每条发现的交付契约

要找的是**GM能否实际操作某项经营行为**，不只是一个会动的内存地址。每项至少交付：

```yaml
capability_id: NC04.PLAYBOOK_PLAYER_PRIORITIES
game_build: "NBA2K22_PC_CURRENT_GEN"
ui_entry: "player observed menu path"
scope: TEAM                 # WORLD/TEAM/PLAYER/STAFF/MATCHUP/DRAFT_PHASE
entity_identity: "stable within current save/batch; dynamic ptr reconstruction"
native_value_type: "int32/bitfield/float/pointer/container/action"
range_or_enum: "observed"
memory_locator: "verified current build pointer-chain or RVA + validity checks"
menu_before_after: "read-only UI change delta evidence"
read_supported: true
write_supported: "unverified until authorized differential test"
transaction_commit_mechanism: "native UI action / additional update call / unknown"
gameplay_effect: "observed / inferred / unknown"
persistence: "while menu open / after exit / after game save / after restart / unverified"
cpu_overwrite_risk: "yes/no/unknown"
event_stage: "PRESEASON / REGULAR / OFFSEASON / IN_GAME / UNIVERSAL"
related_gm_query_source: "observed M0 batch / not yet captured"
source_reference: "test record and file links"
safety_policy: "approval required; no arbitrary player ability/tendency write"
status: "UI_OBSERVED / MEMORY_READ / WRITABLE_TESTED / EFFECT_VERIFIED"
```

- 路径、值域和原始地址**按当前NBA2K22进程及PC存档**观测，动态指针需可重新定位；保留游戏页面的前后差分证明，不要求为每个字段做大量模拟比赛。
- **读/写与实际效果必须拆分**：菜单上被改值≠游戏引擎已消费；教练上任可能自动重置Playbook/体系，需要顺路记录这种副作用。
- **操作对象身份不可混淆**：尤其员工双方引用、球员球队归属/在场名单、选秀回合与已选顺位、不同球队/阶段的写入范围。
- 是否在当期阶段可写、是否跨菜单/保存/重启仍有效；以确实做过的范围记载，不逼着为了“全测”提前跳赛季。
- 对不确定字段保留`UNKNOWN`，可继续完成其他条目；尽量**先查一处页面→拿到可用布局→交付一个可复用控制能力**，而非要求一次找完所有菜单才交付。
- 新增来源进入项目时应按玩家现有流程纳入下一次触发的完整`full_verified_v1`批次，不能为了员工/训练分割生产采集。独立外挂决策与游戏执行权限仍需用户审批。

## F. 最合理的首批发现顺序

1. **NC01 + NC02：训练与疲劳/伤病**。训练方案若不知当前疲劳，月度规划可能伤及主力；应同时拿到设置与真实观测数据。可顺手查看导师NC06。
2. **NC03：六职位员工任免**。球员员工候选已在库中，欠缺实际任免与主教练战术联动；投资回报高。
3. **NC04 + NC05：完整战术手册和球队角色/阵容**。这是最贴近M3与未来实时赛场竞技打磨的入口。
4. **NC08–NC11：签约、休赛期、历史选秀、球探**。在用户实际到该阶段时顺势找到行动入口，不为测试强制推进当前存档。
5. **NC07：临场攻防与ACE**。不要求现阶段实时AI外挂控制器；先搞清教练预设何时被覆盖，留给赛场引擎专项。
6. **NC12–NC15：只读记录**。以后球员/媒体/赛事系统会再深入。

## G. 确切边界

- **已确认**：玩家声明本轮全局设置已可以通过内存修改，不重新当“全局设置不可写”；已实现原生19默认/18对手整体及有限交易。
- **未确认**：六人招聘、训练、导师、球探、实际选秀与员工职位切换的全套可安全写入尚没有现行代码/实机业务验收；本研究中的所有新字段均为Antigravity发现候选而非真实偏移。
- **禁止重置现有项目规则**：普通球员原始能力及个人倾向不得因GM经营而直接修改；球员倾向属于未来赛场专项研究，但写回策略需要玩家特别审批。历史线重力仍另行批准。
- **不扩大M3任务**：M3只使用当前可观测事实与已批准能力，新增Native Control经过实际验证再逐项接入。对新模块允许开发期存在后来才发现的Bug，但不得将未知“已完成”写入能力表。
