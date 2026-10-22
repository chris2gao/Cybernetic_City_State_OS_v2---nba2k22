# DEV23 — 核心Playbook语义与角色证据 V1

日期：2026-10-20。原DEV23终结状态：**BPTI_DEV23_PARTIAL_REQUIRES_PLAYER_DESCRIPTION_TASK_CLOSED**。后续操作规则已由玩家答复，最新补录状态：`PLAYER_CALLING_RULES_CLARIFIED_CRC_TYPE_METADATA_PENDING_TASK_CLOSED`，没有待答问题或活跃等待。

交付：[PR #10](https://github.com/chris2gao/nba2k22-gm-engine/pull/10)，研究提交`583b695`、共享池实现`88a16ec`。玩家2026-10-20已接受研究并批准作为“战术知识基础设施”并入main；实际合并状态/提交以PR为准，原Draft为此前交付历史。未知类型/行为证据等级不因接收改变。

本次独立研究从main `b3ace72c807dad412a8187fc9563f78ed19f02fb`开始；B1 PR #9已合入main（`f4d615c14f0b541fc9f1395b7035952b01e0e417`）。完整机读清单见[研究库存JSON](BPTI_DEV23_PLAYBOOK_SEMANTICS_INVENTORY_V1.json)。这是DEV23研究交付，不是B2 NativeBinding实现或GM来源安装。

## 0. 2026-10-20 玩家后续澄清：按类型选战术，无固定位置前置

E09为本任务玩家直接说明，记录为`PLAYER_REPORTED_UI`，不冒充新的内存/比赛认证：战术有类型，与球员四个有序PlayType槽相对应；球员可从本队手册中随机或指定调用同类型战术；没有固定位置限制，只要球员槽位装载相应类型即可进入该类战术的调用范围。玩家同时说明四槽优先级影响很大，**第1、2槽执行频繁**。手册内容是现实中存在的篮球战术，但这不逐一认证每条动作的分支或名称。

据此修正后续B2研究前提：**类型匹配不需要先给每个CRC认证一个固定发起位置或固定第一受益球员**。原生实际分配仍可未知，不应因此阻止已经有可靠类型元数据的静态匹配。具体CRC→PlayType仍待补，当前库存尚无认证逐战术类型，所以已有TYPE_UNKNOWN结果不变。

后续E10已回答全部操作问题：允许按分类出现的多类型关系；1/2主用、3/4偶尔，执行效果及教练等会影响选择；指定调用是玩家按键，CPU对打自动执行。玩家要求不深究精确频率/算法，详见[手册与玩家规则补录](BPTI_DEV23_MANUAL_AND_PLAYER_CALLING_RULES_ADDENDUM_V1.md)。不推定等概率、四槽百分比或严格顺延，也不新增临场调用执行器。原问题全部作为历史保留；本次只检索手册/当年攻略和补录文档，没有新增游戏访问、测试或代码。

## 1. 已完成与未完成

已完成三队各68槽的静态/只读内存盘点、历史对照、球员有序类型读取、核心动作研究线索和十家族B2建议。三本共204槽、148个非零槽；从本机PE静态字符串精确CRC匹配到89个不同CRC，覆盖111个槽位。37个非零槽名称继续UNKNOWN；56个空槽也逐项保留，未用其它书补齐。

**未认证任一具体战术的原生PlayType、发起人、第一受益人或第二选择。** 本轮没有实际比赛观察，所以不能宣布Motion、Creator-Midrange或Bam Hub已经完整落地。书槽修改仍须可靠类型/动作依据及现有业务绑定；按E09，固定位置/固定受益人的认证已不是类型资格的前置条件。原研究以部分交付关闭，后续文字澄清单独补录，不保持等待任务。

| 当前本机研究对象 | book index / enum / unique_id | 非零槽 | 静态名称对应槽 | 未知名称非零槽 | 与历史同名书CRC差异 |
|---|---|---:|---:|---:|---:|
| CHI / Bulls Playbook | 2 / 2 / 3 | 44 | 19 | 25 | 0 |
| MIA / Heat Playbook | 8 / 8 / 10 | 41 | 35 | 6 | 0 |
| GSW / Warriors Playbook | 28 / 28 / 29 | 63 | 57 | 6 | 0 |

槽索引从0开始。按现有读取器分组：0–29 REGULAR、30–49 BENCH_GROUP、50–59 ENDGAME、60–67 FAVORITE。分组名称沿用项目结构，不证明调用时点。FAVORITE中如ISOLATION/POSTUP的静态标签可能是类别标识，不能把它们当成一条已解码的完整动作脚本。Heat的`FIST 14 POP`分别出现在槽2和8，保留两个槽，不能从重复数推出调用权重。

## 2. 来源、方法与可复核范围

机读文件E01–E08记录源码/文件SHA、批次、观察时间和证据用途；没有绝对内存地址、原始dump或可写请求。

- E01/E02：重新读取`coach_locator.py`、`tactical_reader.py`、`gm_state_io/registry.py`、`config/state_io_native/player.json`及provenance。PLAYBOOKDATA为0x168字节；68个uint32从相对偏移0x58起。四个PlayType位段在PLAYER相对0x168/0x169，Initiator在0x16a bit2。**相对结构布局不是当前对象地址**。
- E03：只读打开密封`query_snapshots/mc_haliburton_2021/2021-2022_M02_DEC12_FULL_20261018_bee1cb016256_e94b241a_TS2/league_state.sqlite`。原始来源批次`2021-2022_M02_DEC12_FULL_20261018`，观察时间`2026-10-18T12:12:12.253755+00:00`。从`coaching_source_captures.metadata_json.playbooks`读取84本的既存目录，只展开三本；对三队47条历史名单仅解码所需战术三字节。历史勇士缩写是`GS`，当前是`GSW`。
- E04：普通权限第一次OpenProcess被拒（Windows error 5）；玩家明确要求管理员权限后，以隐藏管理员Python进程执行现有`GameMemory(read_only=True)`与`CoachLocator.calibrate()`。重新验证模块/原生字段、球队/名单互指关系、当前教练绑定与三队书槽，读取46名当前球员的类型。进程读取权限仅QUERY_INFORMATION/VM_READ，句柄在finally关闭。没有调用正式采集、写入器或游戏UI。
- E05：本机`NBA2K22.exe`的PE timestamp为1652287197，当前模块SizeOfImage为115056640；静态文件与运行时timestamp相符。只在`.rdata`搜索NUL边界ASCII/UTF-16LE字符串，将标准CRC32与**已观测三本书的CRC集合**精确相交，保留可复核模块相对偏移。先前有限模块候选字符串读取也交叉观察到标签；不宣称对89条都逐一建立了运行时动作对象关系。
- E06：额外找到了game-root `config/play_catalog.json`（232条）及Antigravity `_research_generate_catalog.py`。该脚本穷举名称后匹配CRC，`categorize_play()`按prefix/substring猜类型；232条CRC数学上匹配，不等于类型原生认证。旧适配器所指自身`config/play_catalog.json`实际不存在，生成文件在游戏根config，不能把load函数存在当作已部署完整字典。
- E07/E08：读取M3 `attach_tactics`安全投影、DEV14同名书绑定、B0/B1契约、十张SystemCard、R1自主层级、R3映射及两份战术关系研究。旧文中的固定Touches/Shot阈值、2022结果和强受益人推论均未提升为本机事实，也没有加入普通GM可见知识。

SQLite连接使用`mode=ro`；调查用脚本/日志留在本地`_exports/dev23`，不入Git。核心历史投影相当于：

```sql
SELECT snapshot_id, save_id, observed_at, context_json, metadata_json
FROM coaching_source_captures WHERE snapshot_id = :batch;
SELECT team_id, observation_json FROM coaching_team_observations
WHERE snapshot_id = :batch AND team_id IN (3,10,29);
SELECT team_id, roster_slot, pool_slot, player_name, face_id,
       length(raw_struct), substr(raw_struct,361,3)
FROM player_source_details WHERE snapshot_id = :batch AND team_id IN (3,10,29);
```

SQLite substr从1起，361对应相对0x168。此次是专项研究派生，**没有修订历史数据库、脱敏旧库或绕过`require_gm_sanitized()`**。当前游戏存档身份/日期未经玩家确认，因此当前内存只有独立DEV23研究批次，不挂接`mc_haliburton_2021`。两次书槽相等不证明是同一个存档；47条历史名单与46条当前名单分别保存，不按旧pool_slot拼接成当期GM球员。

## 3. 三个证明层与真实覆盖

| 分类 | 本次结果 | 可推出什么 |
|---|---|---|
| UI_OR_STATIC_LABEL_VERIFIED | 111槽 / 89不同CRC | 本机静态字样存在，精确CRC与原生槽一致；没有观察UI |
| RUNTIME_ASSIGNEE_OBSERVED | 0 | 已读coach→book和player→PlayTypes，不等于某条战术分给某球员 |
| IN_GAME_EXECUTION_OBSERVED | 0 | 未开展比赛，不证明ACE按该动作执行 |
| PLAYTYPE_COVERED | 0 | 没有认证的逐战术native type |
| TYPE_MATCH_ONLY / TYPE_MATCHED_ONLY | 0 | 只有类型交集认证后才可使用，当前不输出假匹配 |
| STATIC_PLAY_TYPE_UNSERVED | 0条可认证结论 | 这是缺证据，不代表所有球员都被服务；统一TYPE_UNKNOWN |
| BENEFICIARY_UNKNOWN | 所有111条具名槽记录 | 发起、第一/第二受益人全部UNKNOWN |
| UNSUPPORTED | 实时scram/peel、保证末段指定人、保证reset/re-screen分支 | 未有认证专用控制，不是宣称原版游戏绝不发生这些动作 |

68槽的反射字段有enum descriptor，但本次读取槽0所引用descriptor的entry_count为0；没有得到可解码的“Play CRC→PlayType/actor”表。不能把字段有enum指针、球员type名称或某个`GIVE`字样当成已经找到了类型对应表。

本机静态名与CRC的对应仍是严格限定的**字符串/数学关联**，不是完整动作定义解析；若同CRC出现多字符串应保留歧义。当前库存不把一条CRC绑定到唯一球员；相同CRC在不同本/不同槽分别保留，之后发现实际分配冲突可多态追加。没有认证运行时分配时，不能先宣布其随阵容变化已得到实证。

两个旧合成候选仍隔离：CHI槽0 `0x5bc642a3`/`FIST 21 FLARE`；槽13 `0xdadcf884`/`GIVE 15 CROSS`。本轮未找到其静态字符串佐证；不指控它们不存在，也不借其猜测类型做匹配。

## 4. 三种哲学和核心动作线索

下表中“角色/用途”是篮球或名称推论，**所有原生actor、primary option、secondary option均UNKNOWN**。完整槽证据和UNKNOWN项在JSON。不是跨队借书建议。

| 重点 | 本队已见静态名称与槽示例 | 角色/用途研究方向 | 精确不足 / fallback |
|---|---|---|---|
| Warriors Motion | 槽3 FLOPPY；槽4 QUICK 32 HORNS；QUICK 2 SPLIT FIST | 移动射手接掩护、掩护连接者、第二侧选择 | 不能由名字保证Offscreen 3、Curry/Klay第一受益或split阅读；HOLD槽修改 |
| Warriors cut/handoff | 槽11 GIVE WARRIOR FIST；12 GIVE WARRIOR FIST 2；14/15 CUT POINT 2/3 | cutter与connector的球权衔接 | GIVE不是原生13/12已认证映射；切入是否来自掩护后、谁传给谁未知 |
| Bulls Creator-Midrange | 槽19 QUICK 12 PINDOWN；GIVE 32 ANGLE；FIST 25 DOWN | 接球进入创造、次持球接应的研究起点 | 公牛25个非零槽仍无静态名称；不能宣告缺ISO，也不能把pindown当保证中投/face-up；需菜单文字 |
| Heat Butler持球/攻框 | 槽2/8 FIST 14 POP；18 GIVE 52 CLEAR；24 CUT 15 LOOP | 持球创造与切入第二选择 | CLEAR≠原生Isolation enum，不能保证Butler接球；HOLD |
| Heat Bam高位策应 | 槽15 GIVE 52 RUB；16 GIVE 51 FLIP 12 | handoff passer、receiver和弱侧cutter职责假说 | 未见Bam具体分配；当前Bam PlayTypes并非据此自动改成Handoff Passer |
| PnR持球/顺下/外弹 | Heat槽5 FIST 5 SLIP DIVE；6 FIST 5 SHORT ROLL；2/8 FIST 14 POP | handler/roller/popper/短接应角色假说 | SHORT ROLL字符串不认证4v3脚本及受益人，无法保证roll/pop选择 |
| Post/High-Low | Warriors槽16 PUNCH POINT；19 PUNCH 12 HIGH；23 PUNCH 81 ANGLE；三本槽56 HIGH 4 PINCH END | post threat、entry passer和高位连接者 | 低位/高位类型、face-up、high-low第二入口未认证 |
| Elbow/Hub | GIVE HORNS QUICK、HIGH 4 PINCH END与本队已见GIVE系列 | elbow接应→手递手/空切研究 | 不因HORNS/PINCH词创建“Point-Center原生按钮”；不能借其它书的CRC |
| late-clock/reset | 三本都有ISO 1 END、ISO 1 GO END、ISO 1 FIST END、FIST 5 END等ENDGAME槽 | bailout creator、reset connector | 可确认末段组名称，不能确认时间阈值、调用概率、指定人、reset/re-screen分支 |

`QUICK 12 PINDOWN`本次匹配在**公牛**，没有在勇士已读槽中对应到该标签。它可作为研究概念示例，不能因为Motion需要就声称勇士已有该条。

## 5. 球员四有序PlayTypes与Initiator

当前46人和历史47人分别列于JSON；以下仅当前内存观测，姓名按易读顺序显示，JSON保留原生姓/名短串顺序。字段原值不是球员能力评价，Initiator=false也不是证明该人绝不能被原版AI持球使用。

| 当前球员 | 有序四槽 raw | Initiator |
|---|---|---|
| Stephen Curry | 14,13,1,12 | true |
| Klay Thompson | 14,11,12,13 | false |
| Draymond Green | 8,6,7,11 | false |
| Zach LaVine | 4,1,13,14 | true |
| DeMar DeRozan | 4,13,10,1 | false |
| Jimmy Butler | 6,1,11,10 | false |
| Bam Adebayo | 11,7,1,8 | false |

项目静态目录：0 None；1 Isolation；2 Isolation Point；3 Isolation Wing；4 P&R Ball Handler；5 P&R Point；6 P&R Wing；7 P&R Roll Man；8 Post Up Low；9 Post Up High；10 Guard Post Up；11 Cutter；12 Handoff Receiver；13 Handoff Passer；14 Mid Range；15 3 PT。这是项目沿用原生目录的标签层，本轮没有重新做UI枚举验证。

匹配规则：只对**已认证逐战术类型**做球员有序type与本队可用类型交集；完整相关元数据且交集为空才能STATIC_PLAY_TYPE_UNSERVED。当前只有名称/CRC，不满足该前提，所以46人全部TYPE_UNKNOWN；不从Curry没有15就宣布勇士无球三分失效，不把DeRozan的Initiator直接改true，不从Bam没有13就提出未经批准的改值。四槽顺序不转换成平均调用概率。

## 6. 额外发现：真实同名书匹配阻断

当前教练PlaybookID分别为2/8/28，与Bulls/Heat/Warriors本队已加载书一致；原生book identity也可读。但`src/gm_state_io/team_book.py:team_book()`将书**完整规范化名称**与team.name、abbreviation、city+name相等比较，没有处理` Playbook`后缀。

因此三队实际运行该纯匹配函数都返回`TEAM_NAMED_BOOK_MISSING_OR_AMBIGUOUS`。本轮仅为研究按明确字面`team.name + ' Playbook'`查到唯一原生对象，报告当前教练ID相符；**不修改匹配器、不绕开M3/DEV14业务限制、不生成可执行意图**。M3安全投影捕获此ValueError后书状态会保持NOT_OBSERVED，这会影响真实标签下的own-book提案入口。

这是三队实际对象支持的具体缺口，不是对所有30队/所有路径的全量断言。建议下一次由玩家单独授权最小后缀匹配修正及直接相关检查；本轮不实施、不测试、不修Issue #6。现有源注册表和执行白名单能力不变，不能宣称该研究已经修复书操作。

## 7. 给B2的限范围建议

机读文件为十个SystemCard逐一保留角色要求、已有字段类别、相关核心动作、UNKNOWN和HOLD，不填B0的native_binding_refs，不改B1 Claim/GM可读覆盖。

1. 八原生体系、正常18 coach、Freelance、四type/Initiator、具名48倾向、PERSONAL18、训练/软轮换可按既有认证字段做**方向级**研究映射；十家族与八体系不是一一对应，不生成统一固定数值。
2. Motion只可提出射手/connector/cutter责任及已知字段方向；Triangle/Post保留入口与高低位未知；Spread PnR区分持球、顺下、外弹及第二处理，不能凭FIST名称签发类型覆盖。
3. Creator-Midrange维持创造权与中投价值的篮球意图，先受B1历史可读边界约束，不能用未来DeRozan结果填当前判断；Point-Center保留hub职责，不假装有专属原生开关。
4. Transition不能解释Tempo raw为每回合秒数；护框/换防只走具体PERSONAL字段方向，OVERALL继续只读；Adaptive只是玩家触发的赛前有限方案，不是实时ACE改写。Scram/peel没有认证专用控制，UNSUPPORTED。
5. 书槽方向需要先解决实际业务匹配，再依赖新同批合规源/认证类型/具体批准。本研究CRC和旧库不能当作后续正式批次的执行许可或Desired载荷。类型未知时局部HOLD，**不阻断B3历史seed或其它已认证字段的B2工作**。
6. 普通GM来源仍须`require_gm_sanitized()`；Intangibles不当能力，OVERALL/自由PlaybookID/51匿名倾向/Ability/Potential/Badge边界不变。未启动B2–B6或DEV24，V3有效、V4未启用、真实30队UNASSESSED。

## 8. 玩家已回答，当前没有待答问题

Q4多类型、Q5四槽优先级与选择变化、Q6手动/CPU调用已经由E10回答，JSON的player_text_questions为空；此前Q1–Q3固定分配问题也不再作为待办。完整答案、官方PC手册和2021年玩家实测出处见[补录](BPTI_DEV23_MANUAL_AND_PLAYER_CALLING_RULES_ADDENDUM_V1.md)。

玩家操作说明保持PLAYER_REPORTED_UI，官方手册、社区经验和本机原生证据各自分级。不再追问精确调用率、失败阈值或教练影响系数，也不要求新比赛测试。剩余CRC类型等技术缺口照实保留，本任务没有监听或等待检查点。

## 9. 交付审计

| DEV23要求 | 本次权威证据 / 结论 |
|---|---|
| 从最新main独立调查、读取任务/契约/十卡/M3/DEV14 | base main与E01/E02/E07/E08；独立DEV23分支 |
| 每个有效槽的标识/名称/类型/批次/书身份 | JSON books逐项204槽；37非零名UNKNOWN，全部native type UNKNOWN |
| 球员四有序type、Initiator和静态匹配 | JSON players/archived_players；46当前+47历史独立来源，TYPE_UNKNOWN |
| 可行的只读进程调查 | E04原生布局/对象与受限模块字符串读取；管理员脚本已退出，句柄已关闭 |
| 名称、类型、角色、证据层与fallback | 111条play_semantics完整记录；9组core_action_research；无假受益人 |
| 至少三哲学与PnR/Post/Elbow/late-clock | 本文第4节与核心清单，明确本队候选/不足/HOLD |
| 十家族B2建议与准确限制 | JSON ten_family_B2_recommendations与本文第7节；未实现B2 |
| 机读、Markdown、问题和任务终结 | 本文+JSON，三个文字问题；PARTIAL_TASK_CLOSED |
| 不写、不采、不比赛、不扩展测试 | 只读研究/确定性提取；没有运行自动测试、旧测试、正式采集、UI、保存/重启或数据发布 |

**本次研究提取和证据审阅不是测试通过声明。** 独立Draft PR只交付研究文件及基线索引，不自动合并。所有未完成的逐战术类型/分配和比赛行为均保留未知；该部分交付状态不冒充完整语义认证。


## 附录：2026-10-20 玩家补充战术名称与2D动画（追加事实，不改原研究统计）

- **PLAYER_REPORTED_UI**：玩家在NBA2K22游戏战术界面可以观看2D棋盘式战术演示：五名球员按预设动作移动，战术差异有时只是部分跑位/动作的变化。项目尚无该演示的原生动画字节、脚本坐标/步骤，亦未证实3D赛场ACE必然按演示调用。
- 玩家提出**战术名字可能透露年代/位置/动作**，举例`9015shot`：“90→90年代；15→1号位与5号位；shot→投篮”。本例属于**待逐战术核验的名称语义说明**，非DEV23实机认证的某条原生战术，也非统一命名文法；数字组合还可能有其他命名含义，不把时代、站位、受益人无条件写死。
- 今后应从**原生CRC→native PlayType**先建立可靠类型，再对名称进行`name_tokens/role_candidates/era_candidate`假设分析；获取游戏2D预览实际可见步骤后再增加`opening_alignment/action_sequence/role_interactions/first_option/second_answer`。2D演示证明“预览设计”，不自动证明实际3D AI调用。
- 玩家说的“发起人”常指名称中的关键行动位置角色：**CALLER（谁被游戏指定调用）/ACTION_INITIATOR（谁组织第一个动作）/FIRST_OPTION（第一个终结机会）/ACTUAL_FINISHER（实战完成者）**必须区分；同一种战术可由不同球员担任位置角色，因此当前E09“无需固定位置前置”的规则继续有效。
- 详细DTO和阶段划分见[DEV28 §3.1A](../development_tasks/DEV_20261020_28_GM_NATIVE_IO_TRANSPARENCY_AND_EXECUTION_COMPLETENESS_MASTER_PLAN_V1.md)。不要求截图/录屏或启动新游戏写入，玩家文字描述为可选低成本来源；当前DEV23的111/37/56、89 CRC、原生类型UNKNOWN状态不被追认更改。

## 附录续：实际战术 `'95 FIST 15 SIDE` 对先前“仅猜测”表述的更正

用户再次确认这是NBA2K22实际存在的一条**挡拆**战术，战术名称遵循有意义的命名规则，并非只能把数值/英文当无依据词根。现有共享池 `play_pool_v1.json` **已核实**其`play_id=2K22_PLAY_79215b33`、CRC `0x79215B33`、静态名称`'95 FIST 15 SIDE`：`'95`是1995年版本，`FIST`指挡拆动作，`15`代表1号位持球发起与5号位掩护，`SIDE`代表侧翼战术版本。球员角色而非固定实名，不从SIDE词义擅自指定左/右；尚未考证具体1995年真实球队。

**更正证据等级**：实际CRC→原生名称=STATIC_LABEL_CRC_JOIN；特定名称含义和“挡拆”家族=PLAYER_REPORTED_UI；池中`types.memberships`仍为空，没有取得此条在原生枚举4/5/6/7中的准确成员关系；2D预览步骤和3D调用仍UNKNOWN。不要用先前附录的“9015shot仅作假设”否定此条已经识别的命名规则。`SHOT`与其它动作下的第二位置可能标记预设投篮者，不是总表示掩护人；比赛过程可提前出现投篮/分球机会。

**已知输入接口**：`config/state_io_native/player.json`中`PLAY_DISCIPLINE_TENDENCY`偏移**1185（0x4A1）**，另有Coach `RunPlayTendency`。这是两个不同主体的设置，不应混成单一“执行战术率”，真实数值/临场决策仍须后续观察。玩家说明与[OS 2K22 Useful Findings](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/917203-nba-2k22-useful-findings)中的战术纪律性、Run Plays、球员Touches/PlayTypes关联研究一致；严格保留社区经验与引擎认证的区别。正式GM如调整个体倾向，仍沿用户已批准的**具体提案→逐项审批→Codex受控执行**规则，不得自动修改能力/潜力/徽章。详见[DEV28 §3.1B](../development_tasks/DEV_20261020_28_GM_NATIVE_IO_TRANSPARENCY_AND_EXECUTION_COMPLETENESS_MASTER_PLAN_V1.md)。

