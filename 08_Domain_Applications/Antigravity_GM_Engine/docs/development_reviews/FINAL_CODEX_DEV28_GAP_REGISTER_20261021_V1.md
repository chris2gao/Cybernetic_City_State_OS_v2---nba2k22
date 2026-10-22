# FINAL-CODEX：R06继承缺口与DEV28工程交接 V1

完成日期2026-10-22；原审计main基准`0eaf44f4ff06e7f2cf3c9d078b8f4b064fd2e1f5`。状态：`FINAL_CODEX_AUDIT_COMPLETED_PENDING_PLAYER_REVIEW` / `TASK_CLOSED`。

**20项全部继承，不把研究结案改写为20项工程已经解决。** 源优先级P0=8、P1=10、P2=2保持；19项为尚有未证层的技术/语义/参考边界，G20的研究质量复核已由DEV29结案决定覆盖，仍保留十项无来源候选的证据限制。本轮没有实施DEV28。

## 1. 读取与判定规则

源为`docs/game_mechanics/catalogs/R06D_CROSS_DOMAIN_MECHANISMS_AND_GAPS_V1.json#open_gaps`，各项ID、优先级与历史status原样保留在[机读矩阵](FINAL_CODEX_CAPABILITY_MATRIX_20261021_V1.json)的`inherited_gap_mapping`。该源status是历史记录，不自动优先于`DEV29_R07_TARGETED_INDEPENDENT_RECHECK_AND_DEV29_CLOSURE_20261021.md`的最新研究结案。

下表中的“未来最小证据”是后续有界工作包的接收条件候选，**不是本轮执行计划或新增统一门禁**。按适用对象取证，不要求所有功能都先补齐全部P0。实机读回、UI、批准写入、Save/Reload、生产发布各自独立授权；已经豁免的重复教练UI/保存测试不因本报告重新要求。

通用复用底座为DEV14 Registry/codec/NativeSession、save workspace/代际与lease、full_verified_v1双库暂存/安装、M0封存查询、已有审批tuple/CAS/回读/journal。不另造事实库、审批系统或角色决策程序。

## 2. 20项逐一工程关联

| 继承ID / 原优先级 / 关联族 | 玩家与模型用途；已有基础 | 当前未解决层与工程结论 | 后续归属、最小实际证据与缺失返回 |
|---|---|---|---|
| D06-G01 / P0 / F01–F06 | 理解真实对手/比赛表现；已有球员/球队赛季累计、未合并match候选 | `PARTIAL_SOURCE_CANDIDATE_NOT_PRODUCTION`。main无Schedule/GameLog/双边Box/Shot安全实体，指定两套SQLite无match表。候选忽略InUse、跳过未来比赛；Box不是Shot。证据：source_extensions、query.DEFAULTS、候选reader152起 | D28-3→D28-5。先复用候选并修确定性问题；未来同GameID双边Box/比分/日期/身份及目标页完整列对照，明确原生留存窗口。缺源返NOT_OBSERVED，Shot返UNKNOWN，不由累计反造 |
| D06-G02 / P0 / F04/F27–F29/F31 | 区分3D/SimCast/QuickSim以及USER/CPU消费侧；有world与4项court滑块 | `MODE_ID_AND_CONSUMER_UNKNOWN`。设置登记不证明比赛模式/效果；WasSimulated布尔不够。证据：court.json、adapters.capture_objects、候选flags | D28-2/D28-3。未来每种真实模式样本与控制侧/时刻来源，先识别模式，不强求推导引擎公式；返回MODE_UNKNOWN |
| D06-G03 / P0 / F03/F30 | 防止分钟/得分解释冲突；现有一个normalize_stats物理槽 | `PARTIAL_STATIC_MAPPING`。world/settings经(slot RVA,offset)去重后只一项0x600，不能认证Stats/Minutes两开关。证据：registry.__init__、settings.fields.simulation | D28-2→D28-3。未来PC22两UI开关独立身份/原值与同GameID数据口径；保存效果如需另批。复用去重机制，不能复制第二字段；UNKNOWN_INDEPENDENT_NORMALIZE_MAPPING |
| D06-G04 / P0 / F01/F32/F39 | 保证决策属于同档同日同阶段；已有批次时间与DEV14代际stamp | `HOST_BINDING_IMPLEMENTED_NATIVE_TIME_UNKNOWN`。选定旧批日期USER_CONFIRMED且无save_instance/generation；候选原生日期未证。证据：latest、封存manifest.context、capture_files.source_stamp、snapshots.load_snapshot | D28-3。未来当前存档确认、原生日历/phase与批次stamp对照；旧归档不补伪代际。无证保留USER_CONFIRMED/PHASE_UNKNOWN，禁止跨档拼接 |
| D06-G05 / P0 / F37/F39 | 确认游戏真正保存并可恢复；已有宿主workspace/lease与安装恢复 | `GAME_SAVE_RELOAD_NOT_VERIFIED`。DEV14管理外挂数据不是游戏Save API。交易有历史重启归属报告，人数修复后保存重载未验收。证据：37手册、receipt.persistence、lifecycle | D28-4按具体动作证据补足；获批测试档、同对象/版本的保存前后与真实reload证据。复用journal，不自动保存/重启；PERSISTENCE_NOT_VERIFIED |
| D06-G06 / P0 / F07/F24 | 正确执行1984–2020新秀轮回；有真实池raw/tag及历史目录 | `CATALOG_PRESENT_DRAFT_LIFECYCLE_UNKNOWN`。当前loaded class、已完成选秀和轮回触发未认证；DraftEngine读取目录不等于注入器。证据：historical_rookies.is_historical_rookie、DraftEngine.get_draft_class | D28-2/D28-4。未来实际loaded class/选择完成与新秀身份对照；新任务具体批准后才讨论注入。GM_SANITIZED的Potential不能当原生源；DRAFT_PHASE_OR_CLASS_UNKNOWN |
| D06-G07 / P0 / F08/F19/F21 | 外部到期/竞价/合同写回避免原生流动干扰；有合同读取与签约源码 | `SOURCE_ONLY_SIGNING_BLOCKED`。两个签约闸门false；休赛期planner只准synthetic，阶段/原生AI签约覆盖未实证。证据：approved_signing_executor16–17、offseason._validate_input、P0研究报告 | D28-4。复用既有合同codec/审批身份，不重做报价人格；未来具体获批签约对象的FA关联、合同/名单/计数/读回和AI副作用证据；真实休赛期源另证。REAL_OFFSEASON_SOURCE_NOT_IMPLEMENTED / UNKNOWN |
| D06-G08 / P0 / F08/F22/F23 | 按玩家V4合法处置简单签；已有300 verified未来签与有限Owner转让 | `KNOWN_POLICY_CODE_MISMATCH`。V4取消固定3届，draft_assets.trade_window仍range(next,next+3)，query._views亦next+3，旧manifest/picks eligible保持历史口径。证据：policy_id、draft_assets16–19、query._views | D28-4独立小包。另批后同步实际守卫/调用方/投影并做直接相关离线检查；不改成固定5届，不宣称所有已读资产可交易。当前明确LEGACY_WINDOW_POLICY_MISMATCH，执行失败不得绕过 |
| D06-G09 / P1 / F09–F12/F14 | 理解教练设置与真实战术选择；已有19默认、整体批量、个人防守引擎、BPTI引用 | `CONTROLS_PARTIAL_EFFECT_UNKNOWN`。普通GM18默认（不含自由BookID）、PERSONAL；OVERALL只读；逐CRC类型/2D动作、ACE实际效果无全量认证。证据：coach profile、plan.build_plan、team_book、DEV14验收 | D28-1优先原生目录/类型/语义，D28-2/D28-5接查询。复用48倾向、4+1、68槽和既有enum，不做重复值试验；未来代表性类型/书绑定/2D证据，实际比赛效果另层。TYPE_UNKNOWN / EFFECT_NOT_QUANTIFIED |
| D06-G10 / P1 / F13/F15–F18 | 选择训练与负荷需要实际健康；已有训练6+5、stamina/durability与历史布局候选 | `SETTINGS_IMPLEMENTED_DYNAMIC_HEALTH_UNKNOWN`。训练不是只有离线writer：NativeSession resolver/capture和codec已接；其来源是玩家报告native tested，旧批无对应对象。历史数组/导师/当前疲劳未完整适配。证据：training.json、adapters.capture_objects、provenance | D28-2/D28-3/D28-5。未来当前健康事件/原生时间域、训练生效与真实序列，按完整对象页面核对；不先推训练因果系数。导师只读待adapter；HEALTH_NOT_OBSERVED，不拿评分当即时体力 |
| D06-G11 / P1 / F07/F24/F25 | 避免同名clone或球探信息误认；有池槽身份/tag与M0歧义输出 | `PARTIAL_BATCH_LOCAL_IDENTITY`。全知池不等于球探界面/进度，跨季永久身份与loaded class关联未证。证据：QuerySession.pool/player identity、historical_rookies、候选load_player_name_catalog | D28-2/D28-5。复用批次局部身份与歧义拒绝；未来clone/实际Draft选择/球探页来源对照；不设计“穿透雾区”模型。MULTIPLE_CANDIDATES / SCOUTING_NOT_OBSERVED |
| D06-G12 / P1 / F33 | 查询真实历届获奖者；已有研究目录 | `TEN_UNSOURCED_CANDIDATES_REMAIN`。10项sources=[]仍是候选，不认证原生奖项台账。证据：R07结案报告§三、R06-B | D28-2/D28-3。未来精确PC22奖项页/记录与身份、年份、来源，不能拿统一社区来源背书所有奖；AWARD_NOT_OBSERVED |
| D06-G13 / P1 / F34 | 区分单场/常规季/季后赛/生涯纪录；有研究维度 | `NATIVE_RECORD_AND_REFRESH_UNKNOWN`。未在所审pipeline/M0找到完整原生记录实体；不推论游戏没有此功能 | D28-2/D28-3。未来页面完整分类/值/刷新时点与原生对象对照，复用统一批次身份；RECORD_SCOPE_UNKNOWN |
| D06-G14 / P1 / F02/F17/F33/F34/F38 | 保持跨季球队/球员事实；有封存批次历史访问 | `HISTORY_RETENTION_UNKNOWN`。旧库team_season_history/staff_dynasty_history为空；5条growth不证明自然成长。候选season文本不实现100赛季采集 | D28-3/D28-5。先查真实保留窗口，再按原触发节奏归档；未来测试档跨季GameID/对象关系对照须单独许可。旧Box沿当场队伍，不用当前队重写；HISTORY_NOT_OBSERVED或证实后HISTORY_NOT_RETAINED |
| D06-G15 / P1 / F35 | 让媒体/GM区分原生事实与叙事；有跨版本机制引用 | `PC22_NATIVE_MEDIA_SOURCE_UNKNOWN`。没有本次认可的无Mod PC22消息/实力榜/Mock源；不能笼统称所有概念都是新版 | D28-2/D28-3/D28-5。未来具体消息类型/时间/公开范围与目标页，复用来源标签；不做Media人格。MEDIA_SOURCE_UNKNOWN |
| D06-G16 / P1 / F36 | 知道规则提案及生效期；有world/settings子集 | `RULE_EVENT_LIFECYCLE_UNKNOWN`。静态设置字节不能证明投票、合法候选和跨季生效 | D28-2/D28-3。未来PC22提案/投票/生效对象与UI，必要跨季另批；复用slot去重和enum。RULE_EFFECTIVE_PHASE_UNKNOWN |
| D06-G17 / P1 / F19–F21/F26 | 区分球员合同、球队现金、staff预算和签约能力；已有合同/财务/staff投影 | `FACTS_PRESENT_SEMANTICS_AND_EXECUTION_GAPS`。cash原始值保留，signed32是未证假设，cap/tax模板不是实测空间；staff未映射不等于自由教练，无雇聘执行器。证据：finance.semantics、source_extensions、38手册 | D28-2/D28-4/D28-5。复用现有读取、工作台和关闭的签约源码；未来具体预算单位/时点/合同与资格证据。遵守玩家已缩小的合同范围，不自动扩成完整CBA；FINANCIAL_ELIGIBILITY_UNKNOWN |
| D06-G18 / P2 / F40 | 平衡现实线/历史轮回与游戏事实；已有gameplay_policy | `REFERENCE_BOUNDARY_DEFINED_NOT_NATIVE_ERA`。2K23 Eras是跨版本参考，1984周期为玩家规则；不需要开发PC22 Era菜单来“解决”它 | D28-0/D28-2文档/来源标签维护；无需实机造一个不存在的已认证入口，不修改历史raw；CROSS_VERSION_REFERENCE_ONLY |
| D06-G19 / P2 / F37 | 分清云文件可靠性与游戏持久性；有宿主目录/lease | `CLOUD_NOT_GAME_SAVE_PROOF`。本轮未查Steam账号或云状态；不由本地文件存在推保存成功 | D28-4仅具体存档许可需要时核对；先复用G05证据，不重复建云监控；CLOUD_STATUS_UNKNOWN / GAME_SAVE_NOT_VERIFIED |
| D06-G20 / P1 / 治理项，无单一族 | 保持研究质量且不反复重开R系列；已有正式独立结案 | `RESEARCH_REVIEW_CLOSED_WITH_SOURCE_LIMITS`。原status=REPAIR_SUBMITTED_REVIEW_PENDING为历史；以最新结案报告覆盖。10条无直证仍无直证，研究接受没有把它们升级为native事实 | D28-0交接继承，不安排重做R06逐条研究。使用UNKNOWN/source=[]，未来需要具体能力时另行取证；不阻断本次审计结案 |

## 3. 去重后的后续工作包候选

| 包 | 对应缺口与价值 | 已有部分不重建 | 最小新增范围 / 前置 |
|---|---|---|---|
| D28-0 覆盖与来源台账 | 全部20项，特别G20；避免重复开发/误认当前 | 本次40族矩阵、源索引、证据catalog与静态复核方法 | 接收本审计；按具体页面/完整对象登记状态，所有post-baseline发现另审；不是再做694项研究 |
| D28-1 Playbook类型与绑定 | G09；原DEV28指定的首个高价值执行缺口 | 本队书68槽、事件rebind、CRC共享池、名称引用、4+1 codec | 原生目录/实际绑定/CRC类型→合法选项查询，代表性2D说明；类型/名称/实际3D结果独立；AG原生证据须单独任务 |
| D28-2 静态完整对象/语义 | G02/G03/G06/G10–G13/G15–G18 | 232逻辑注册、物理slot去重、PLAYER raw和现有profile | 以PC22真实页全列/子对象与原生关系为覆盖单位，补现有codec未映射部分；不得以几个GM偏好字段冒充完整对象，也不假设游戏内部SQL |
| D28-3 动态比赛/健康/时间与事实链 | G01–G04/G10/G14等 | match候选、既有赛季累计、双库stage、source stamps/full_verified_v1 | 先确定性修复候选再原生取证，接正式同批完整性与历史保留；Shot/模式/Normalize未证则显式缺失，禁止新常驻抢抓 |
| D28-4 有限执行完整性 | G05–G08/G17/G19 | trade v2、roster计数、防重放、DEV14审批与签约关闭闸门 | +3维护可独立小包；具体签约/员工/选秀要独立许可与实证；不新建谈判人格或自动操作存档 |
| D28-5 模型安全查询 | G01/G09–G17；将已读对象实际暴露为有界合法事实/选项 | M0封存双库、白名单、来源binding、GM_SANITIZED门槛 | 补具体已认证实体/字段投影与语义，提供缺失状态；未来Coach/Player/Media可见性需独立定义，现有统一接口不等于角色ACL已验收 |

建议先接收D28-0成果，然后沿原计划优先D28-1；同时把D28-3候选的事务/身份/查询问题整理为一个小型确定性修复任务，原生证据另批。V4旧+3维护可作为D28-4独立小包，不必等所有比赛或历史源认证。此为排期建议，不自动并行派单。

## 4. 已有能力与后续接收边界

不重复开发：正式全量更新与timestamp发布；M0静态快照投影；DEV14 per-save三库/代际/审批/CAS/日志；既有普通交易与简单签Owner转让；教练codec/默认19与已认证overall；个人防守适配、命名48倾向/PlayTypes/训练6+5/四项court/50world的现有代码。应补的是具体缺失证据、正式批次、合法语义和查询/执行层之间的连接。

`POST_BASELINE_NATIVE_DISCOVERY_PENDING_SEPARATE_REVIEW`：AG-NATIVE-01/01B及`dev/native-io-exploration@227b3acc…`不计入本次40族成熟度，不借此解决G17或更新native来源结论。新版蓝图V2作为未来方法约束，不代表上述包已实施。

缺口登记完成即本任务可结案；剩余UNKNOWN不要求玩家现在提供截图、启动游戏或运行其它模型。下一步由玩家审阅并选择独立工程任务。
