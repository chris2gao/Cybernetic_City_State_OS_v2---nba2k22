# DEV16 — M3/DEV14/DEV12 统一设置能力收尾与GM运营整合（用户7点定稿）

> **2026-10-19 最新分工覆盖本文件早期任务分派**：[DEV18双Codex窗口接力](DEV_20261019_18_TWO_CODEX_WINDOWS_HANDOFF_AND_BOOK_DEFAULT_V1.md)是最高优先级：DEV14独立Codex窗口①拥有全部SQLite/采集/原生Codec/审批/自动Pot=1/Intangibles，M系列Codex窗口②只负责DEV13和GM业务。新档30队各有本队同名手册、换帅后恢复绑定；取消Antigravity预先研发30队克隆/共享书冲突的要求。AG剩余CRC知识/51倾向/训练模板/疲劳是后期增强。以下Codex小项按此重新划分，不可由一个窗口同时抢写两个PR。

> **2026-10-19 DEV17最新开发顺序**：[Codex主线优先与同名Book归位](DEV_20261019_17_CODEX_FIRST_MAINLINE_TEAM_BOOK_COACH_RULES_V1.md)。**每队每赛季仅休赛期换帅一次**；A队聘B教练，先将A队当前Coach的原生BookID恢复指向**A队同名且独占的Book**，然后修改A书以适应B教练体系和A球员；不修改B书。休赛期员工签约/竞价留待后续项目，本轮只做GM业务门禁与实际换帅后恢复绑定接口。**Codex先完成已知字段DEV14/M3-T主线，不等AG补全部CRC真实动作、51未知倾向或额外训练模板与疲劳解码**；只有同名书定位/独占或CRC槽位写入出现真实阻塞时，AG做最小专项。下文旧“AG先全部补齐才允许Codex开工”的先后顺序被此段覆盖。

**2026-10-19 · 文档状态：开发任务正式交接 / 尚未执行 · Codex（公共采集/执行/M3接入）+ Antigravity（原生战术手册、倾向、训练字典补齐） · 任何正式游戏写入仍须玩家批准。**

本文件是本轮用户对此前DEV13/14/15开发边界的**最新权威澄清**，优先于旧文档中将“每个同类型字段都需逐项副作用试验、单项属性训练、全部战术手册实测、所有Gameplay都得改”作为任务的要求。**绝不重做已经实现的DEV14 A/B/C/D**。

> **2026-10-19 最新用户强制运营规则**：详见[GM个人防守与球队专属手册政策](../../web_gm/manuals/GM_DEFENSE_AND_TEAM_PLAYBOOK_POLICY_V1.md)。本轮明确**日常GM只用PERSONAL_DEFENSE，OVERALL_DEFENSE只读不写**；**日常GM不主动切换coach.PlaybookID，靠修改本队独占原生Playbook的战术槽经营**；换帅触发手册归属重新核查和本队专属书改造。多个球队引用同一PHI等原生book时禁止任何单队改槽，先交Antigravity核实/实现独立原生书及必要的受控技术绑定。以下较早“先整体再个人/日常切书再改槽”的文字已由此规定取代。

## 0. 业务定稿（七项）

| 用户确认事项 | 应做 | 明确不做 |
|---|---|---|
| 1 教练设置冲突 | **日常GM仅写针对具体对手球员的PERSONAL_DEFENSE**；OVERALL_DEFENSE保留RO，杜绝整体设置覆盖个人配置 | 日常“先整体再个人”的写入流程；将限制当作篮球策略冲突 |
| 2 战术手册 | **一队独占一本原生手册**，日常GM不切PlaybookID而改本队独占书的68槽；换帅重评与必要受控技术绑定；AG补CRC↔战术类型及安全修改 | 修改多球队共享PHI书、把显示名称当独立原生书、因想换打法随意切书 |
| 3 球员4个战术类型 | 直接用现有玩家数据的4有序PlayTypes、Initiator、能力、Tendency和球队手册，动态调整 | 仅依据OVR硬匹配；重复开发个人PlayType读取 |
| 4 球员99项倾向 | 现48个具名字段直接使用；Antigravity补其余51未知位的语义/合法值域，再交统一Registry按同种byte codec入库/启用 | Codex单独重新找99个地址或未解名就写RAW_0x... |
| 5 球队/个人训练 | 仅开放球队训练强度/自动强度/背靠背休息、球员**位置适用的训练模板/原型、个人强度与恢复相关设置**；GM每批读取球员疲劳/比赛负荷/近期上场数据，决定训练强度和模版；游戏自主成长 | 逐项调整真实投篮/防守属性训练量、直接增加球员Ability/Badge、要求GM管理一百多个单属性训练子项、把导师徽章注入当本项目必需 |
| 6 世界线 | DEV14统一读写已支持的50项native字段照原来类型规则批处理；同一编码类别由Antigravity**一项有代表性的玩家实测成功**可作为该家族整体实现的工程验收证据，其余参数再按字段字典检验值域和地址布局 | 对同类的每项参数一一反复手工测试；将未登记布局的剩余世界设置假装已接入 |
| 7 Gameplay平衡 | 当前4项USER/CPU+Current/Custom已经够用，同族后续按相同codec扩展时共用已验证模式 | 为求“全局完整”盲目把未提出调整的Gameplay其它滑块全设一遍 |

**另沿用最新用户定稿**：
- `Intangibles`（PLAYER byte0x440，25–99）成为30队GM可建议的轮换影响因子，仍经用户具体批准及DEV14执行，原版AI动态换人，不锁分钟。玩家不要求调查它影响交易/合同/Sim等其它功能。
- 每次正式采集完成后、正式发布前，所有在队与历史球员池数据库Potential（PLAYER byte0x441、JSON和结构化列）统一置1，元数据标人为遮蔽，游戏原生Potential不改。**GM脱敏raw_struct不得用于历史新秀原生注入**；详见[DEV15 V2](DEV_20261019_15_GM_SCOUTING_FOG_AND_OVR_ROTATION_CONTROL_V1.md)。

## 1. 本次复查证实的真实实现状态（PR#5 head 31f2682）

- `src/gm_state_io/registry.py`实际已经注册：19 Coach默认、18 Overall+Personal防守、4 slot PlayTypes/Initiator、PLAYER Tendency从0x458至0x4BA共99字节（48已命名可写/51 UNKNOWN只读）、68槽当前手册CRC、6项Team Training、5项Player Training、4项Gameplay USER/CPU的原生映射、按`world.json`/`settings.json`现存布局注册的50项World。
- `src/gm_state_io/adapters.py`中的`NativeSession.capture_objects()`及`src/gm_state_io/plan.py`和`executor.py`已提供源RO捕获、字段计划、物理合并/读回，非“空框架”。Antigravity新增字段只需扩充字典及Adapter，不再开发第二套全量采集。
- `config/state_io_native/training.json`实际`enums.player_types`**仅有9种已定义训练原型（0..8）**：All-Around、Two-Way、Offensive、Defensive、Athletic、Rebounding、Playmaking、Outside、Inside。用户看到的**“各位置约10套模版”**可能是另一个UI位置专属模版分类；现有字段清单尚未证明9个通用原型与每个位置全部UI模板的对应关系，**交Antigravity补准确的PG/SG/SF/PF/C → UI模板编号、原生枚举与训练成长侧重的映射**。不要自行假设每位置恰有10个，更不能把“player_type=8”写成任意位置第8套相同UI页面。
- 同份training.json具有`player_training.progressive_fatigue_history @0x2F5`与`flags.progressive_fatigue_history_point_count`等**原生读布局**；但当前DEV14注册和`capture_objects()`仅捕获5项`player_training.flags`写入字段，并**未自动提供可理解的球员实时疲劳状态**。Antigravity提供实际解码/单位/游戏页面对应及可信当前数值，Codex加入只读`PLAYER_FATIGUE`（不可写）；来源仅给历史趋势则标HISTORY_ONLY，不伪称实时疲劳量。比赛负荷从同批场均分钟、近期赛程和训练设置综合输入，超出已观测字段标UNKNOWN。
- `src/gm_state_io/plan.py`目前明确禁止同批`OVERALL_DEFENSE+PERSONAL_DEFENSE`同一team/opponent、同批`coach.PlaybookID + PLAYBOOK_SLOT`；**这是执行排序/身份失效的保护，不是逻辑上两种战术不能兼容**。原生真实同块多个Coach POE和多个Bitfields已经由编码器合并，没有普遍教练参数冲突。
- `src/gm_state_io/registry.py`对世界字段基于`slot+offset+type`且只注册有效RVA布局，同时对`CPUAttributeBoost`等语义未证字段暂只读。用户的“家族一次成功代表该类型读写可用”只省去每字段手工实战测试，**不意味着跳过字段正确名称/单位/枚举/slot/位宽验证，或让缺地址的世界字段自动可写**。
- [DEV14工程PR#5](https://github.com/chris2gao/nba2k22-gm-engine/pull/5)未正式完成生产采集/实际整套游戏落地；[M3 PR#4](https://github.com/chris2gao/nba2k22-gm-engine/pull/4)尚未合并。必须尊重用户的合并审批，不因文本“开工”就合并PR/写游戏。

## 2. 什么叫“同类设置一次实测通过即验收该类”

把验证压缩为**家族级结构验证 + 自动类型校验**：
1. 每个原生布局家族保持唯一Codec/Resolver，如World`SLOT_TRADE:uint32`、`SLOT_TRADE:float32`、Coach共享位域、Player Tendency uint8、USER/CPU双镜像Gameplay、PlayerTraining flags与Playbook CRC slot。用户已经和Antigravity实测成功的样本归入家族证据。
2. 对全家族其它字段**不要求重复在游戏里逐项改一个再核查**。通过静态native field定义确认正确slot/offset/type/byte-group/值域/枚举，套同一`decode / encode_patch`，只跑最少的合成边界测试并由正常正式采集覆盖。
3. **不同编码家族不能彼此替代**：写一个World uint32通过不证明另一个新位置的浮点/位域也一样；单字节倾向通过不证明跨指针的Playbook全套替换（用户已实测后者曾失败，属于必须按新版本适配的不同操作）。
4. 已有合法字段、程序CAS、变更计划批准、来源身份仍须保留，不允许“因为同类型测过”就把内存定位/原值验证/越界容忍省去。额外效果量化、对非目标系统副作用研究**不是这轮验收门禁**。
5. 语义没命名的51 Tendencies须Antigravity补真实UI词条或字段字典，不得只因为其物理布局一致就让GM有权猜测其用途并修改。

## 3. 具体开发边界与责任

### Antigravity — 本地游戏知识/字典补齐（**主要负责A类可读能力**）

- **AG-1 Playbook**：整理实际当前68槽和可用战术目录，解决之前曾出现的替换失败，在本地当前游戏版本上采用已修复的安全替换实现；输出Play CRC/真实战术ID/UI名称/PlayType匹配/适合发起位置/动作说明、可用名单/本目录支持情况、共享手册Owner范围。将主教练熟练体系、ActiveSystem、Playbook适配关系作为标签提供，而不是自动视体系最高Proficiency=必须切换。现实战术知识可用合理篮球动作对应（split action、PnR、handoff、Spain PnR、flare、stagger、pin-down等），实际没有证据证明对应到当前游戏某CRC时标`BASKETBALL_ANALOGY`而非`ENGINE_VERIFIED`。 **新增：证明Team独占的原生Book身份（不是同名）与owner映射；共享Book不准改，先验证可用专属预留/clone和技术性绑定。**
- **AG-2 Tendencies**：补51字节对应的真正原生行为字段、方向、上下限和玩家UI实际名称；只对能对上名称且位置正确的字段从UNKNOWN→NAMED_FIELD。未识别仍read-only，不能构造“RAW_0x...”意义。
- **AG-3 Training**：提供真正当前游戏各位置训练模板清单/枚举索引及每模板影响的**成长方向说明**（不做单属性微调或直接变更）；与现有0..8通用`player_type`联系或标为另一个列表；给出`progressive_fatigue_history`/当前疲劳的实际解码与取值方向、最近比赛体力/伤病风险可读信号。只把`fatigue`作为GM只读信息，人物原始Ability和Badge不开放。教练强度已有6+5写接口，重新使用。
- **AG-4 应交付**：以已存在的`config/state_io_native/...` profile模式提交`playbook_catalog.json`、`tendency_dictionary_extended.json`、`training_template_catalog.json`、`fatigue_read_profile.json`（文件名可调），每条字段明确`exact_original_id/name/range/location/read_codec/write_capability/evidence`；已证原生家族仅提供一例可读/可恢复/可验证证据，不按99项重复手测。先保留Antigravity独立本地工作区，交Codex整理线上，不能绕过用户权限擅自在主项目重写。

### Codex — DEV14/DEV13通用确定性集成（**主要负责B类协议和GM使用**）

- **CD-1**：已有DEV14-H三库一致性和真人批准来源问题仍按现有任务小修，不因此扩大成大重构。
- **CD-2**：用现有`Registry`注册并读取AG给出的字段：Playbook catalog、补名倾向、分位置球员训练模板、只读Fatigue。只读字段标read-only，正确识别动态值域并使用统一命令`gm_state_io stage/preflight/apply`；不写第二套原生批处理程序。
- **CD-3**：优先将Antigravity已解决的槽位安全替换接入DEV14，但**GM只能修改当前本队独占手册**：原生owner集合必须严格等于本球队，且Book实体/指针独立；共享book报SHARED_PLAYBOOK_MUTATION_BLOCKED。换帅后或建档初始若实际教练绑定共享书，须经玩家另行批准技术性绑定到本队专属原生书（如果AG证明可实现），再重采本队新槽位，GM根据现任教练体系改造。日常不开放直接切PlaybookID。
- **CD-4**：GM只产生逐名对手球员的PERSONAL_DEFENSE稀疏批量，继续采集/只读Overall，不把Overall+Personal拆成两个日常获批批次；GM整体防守写动作默认拒绝OVERALL_DEFENSE_GM_DISABLED_USE_PERSONAL。个人匹配身份唯一、Gameplan提交与回读/恢复沿用DEV14，无法定位个人时不回退修改整体。
- **CD-5**：训练业务只给GM`team_training_intensity/rest`、`player_training.position/player_type/intensity/recovery`及真实`fatigue_observed`，加上近期比赛使用量；**不引入单项属性训练输入**。同批可包含多队不同强度与多球员模板/强度，自动分离关联的原生storage block。
- **CD-6**：DEV13的M3D1-D6决策必须由教练/体系→真实Playbook/个人4Types/Tendency→球员原始技术能力→当前疲劳与训练强度→实际先发/轮换→交易需要这一链条驱动。个人角色、手册可执行性、现实动作模拟知识都必须有来源等级；仍允许HOLD。
- **CD-7**：世界线当前已登记50项/Gameplay4项按家族批量修改继续使用已完成DEV14，不为未需求的其它Gameplay设置开新项目；尚未登记的其它世界字段如需要后续可在AG统一Profile确认布局后追加，别声称“50=全部100+”。
- **CD-8**：继续按[DEV15 V2](DEV_20261019_15_GM_SCOUTING_FOG_AND_OVR_ROTATION_CONTROL_V1.md)落实Potential=1自动入库后处理与Intangibles 25–99轮换。潜力脱敏GM库不可用于原生历史新秀注入，游戏本身潜力不得改。

## 4. 两类旧执行冲突已由GM业务规则消除

**个人防守**：原版整体防守会覆盖个人设置。新GM仅对匹配的对手球员创建PERSONAL_DEFENSE，可以一个批次按需修改多人多字段，所有整体设置保持只读原值。代码保留原来OVERALL+PERSONAL同批阻断，但普通GM根本不再提交OVERALL；无需“先整体后个人”。不能定位对手球员就标个人对象不可用，不向所有人统一覆盖。

**战术手册**：GM日常只修改本队实际独占书中的68槽，不通过PlaybookID换战术风格。当前游戏如果多位教练引用同一原生PHI书，修改该书会影响所有Owner，**不是靠批准两个Owner就可安全规避的事**。Codex新增独占校验，AG先确认30队各拥有独立Book，必要时专门技术绑定、经用户批准；不能独占时停止手册写入。换帅后重新读取教练和Book关系、确保球队专属书归属，再按新理念和阵容重新改槽，而非随意切换到别队手册。

**工程界限**：一个Coach多个共享bit位域的编码器仍然可以一次安全合并；整体与个人防守的逻辑覆盖、原生Playbook物理共享是业务/资产边界，不要求重构整个内存写入框架。具体授权与实例流程详见[GM运营政策](../../web_gm/manuals/GM_DEFENSE_AND_TEAM_PLAYBOOK_POLICY_V1.md)。

## 5. 任务顺序（匹配Codex额度有限）

1. **独立Codex窗口①（PR#5）先做**：DEV14-H + DEV15 V2 Potential入库后统一=1、Intangibles单字段与受控Coach BookID动作、交接文件。不重做原DEV14。
2. **M系列Codex窗口②（PR#4）接棒**：读取窗口①最终交接与最新源码后，以已有DEV14字段实现GM闭环及本队同名书归位的决策动作；AG扩展后置。
3. **后期AG扩展**：先由AG补实际原生字典，窗口①接字段注册/原生解码，窗口②在GM分析消费新增信息；不要求Codex②直接开发Native Decoder，训练仍不开放单属性微操。
4. **随后M3-T**：M3按同一batch批次使用这些事实，形成可依据对手应对的HOLD/INTERNAL/MARKET，用户批准后利用DEV14执行；世界线/Gameplay已有统一读写不另做。
5. 不应把每个World字段、99个Tendency字段、每套模板都跑实机A/B作为工程完成门槛；只检查不同原生存储/编解码类型的代表样本与结构完整性。真实GM战术决策可由后续常规比赛反馈渐进校准。

## 6. 简洁验收清单

- 只运行定向合成/旧M02静态校验；已有PR#5 119项全部复跑不必要。没有新字段来源时标`UNKNOWN`，不能做假的完成报告。
- 一个coach批次多个不同POE位域可正确合并；GM只写PERSONAL不写OVERALL；共享的原生Book禁止单队改槽，独占书修改不得影响另一队；换帅或技术性专属绑定后必须重新采集书槽事实，不得用旧书slot提交。
- 轮换可以通过Intangibles获批操作，原版ACE仍负责临场，失败可恢复；GM没有真实Ability、Potential、徽章的普通直接写权限。
- 训练能覆盖球队强度、B2B休息、玩家所需按位置的训练模板和球员强度，疲劳只读；**不新增逐属性训练或徽章直接修改**。
- 99 Tendency原始位可读，具名部分可写，新补充的51需实际名称/编码后才放开；real-world Play知识来源/CRC映射标可信级别。
- World同存储家族一条代表样本成立后，所有有认证slot/offset/type的字段走统一读写与自动范围/前值校验，不要求额外逐项手测；Gameplay当前只4项。
- 实机运行不由本任务自动执行；所有真实批次由玩家单独批准、明确存档、正确hash、实时读回。PR#4/#5不自动合并，GM V4不自动上线。

**成功判据**：30队GM能够在确定性DEV14底座之上，针对真实NBA2K22教练、Playbook、球员使用与倾向、疲劳-训练-比赛负荷进行有证据决策，批次动作可以安全执行；不强迫用户或Codex把已证同类字段重复研究。