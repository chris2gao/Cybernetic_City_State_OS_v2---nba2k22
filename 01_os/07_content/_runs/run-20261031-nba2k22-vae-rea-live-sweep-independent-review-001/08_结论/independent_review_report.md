# NBA2K22 VAE · REA 204字段集中实机扫描独立审核报告

**审核任务**：`NBA2K22-VAE-REA-LIVE-SWEEP-INDEPENDENT-REVIEW-20261031-001`  
**执行候选**：`f1e02101ead9e48c0dd3591e8c76501e407acfab`  
**候选父提交**：`bccbb80677d20c3c09d2f9b5ea06797f501dfafc`  
**基线**：`45cc45cae0550ddcda192a2179ea48509b27f6ee`  
**任务分支**：`task/nba2k22-vae-rea-single-field-loop-20261030`  

## 一、集中结论：REWORK_REQUIRED

**承认交付有实际采样价值；不接受“204项实机原生字段映射与机制影响已经验证”的结论。** 固定GitHub提交实际包含99份球员倾向记录、19份Coach记录、86份World记录（共204）、2,265行Dossier和Python`live_analyzer.py`。用户回传本地日志包含REA list/start/load/unload/close和只读进程测试；源码也实例化`GameMemory(read_only=True)`，若该日志真实则支持存在实机读取过程的解释。本审核未现场连接游戏、未独立验证该Frida会话原始收据与授权。

然而本候选存在5个P0、5个P1和2个P2项，**部分字段身份/类型甚至有直接矛盾**。因此与此前Gemini开发完成指针不同，本审核只给予`RAW_MEMORY_CAPTURE_CANDIDATE`成熟度，不允许对这204个条目统一标`LIVE_RECEIPT`、`NATIVE_MAPPING_VERIFIED`或`GAME_EFFECT_VERIFIED`。

## 二、GitHub实际核验

1. `f1e02101`为远端REA片段任务分支真实HEAD，parent为`bccbb806`；相对于该parent仅新增/修改**207份文件**：204个field_records、1份dossier、1份completion_pointer和1份`src/vae_rea_research/live_analyzer.py`，均在任务包三项白名单内，**没有改测试代码、Core/master、REA核心**。
2. Dossier blob `f30f0c0ca66b91032b5fde040b0950ea74d94f57`，长82,264字符（2,265行+文件末换行），恰有204个字段标题；只说明文本和文件数量真实，不说明来源类型正确。
3. `iteration_ledger.jsonl`有204条，最新记录时间约为2026-10-31 03:17:47Z；而204个新`live_evidence`来自约03:31:03～03:31:09Z的批处理扫描。因此**原204条账本是之前的逐项静态研究，不是本次实机的204次新实验**。Dossier输出前端未保存独立读回字节摘要、Frida会话ID、游戏Save/PE哈希。
4. `current_checkpoint.json`仍有`evidence_added=153,unknown_fields=51,review_readiness=NOT_READY,latest_completed_commit=4e5bafd...`，与新JSON普遍被升级为`LIVE_RECEIPT`、completion_pointer所称全部live grounding出现明显状态分叉。

## 三、P0-A：Coach基址没有真正定位Coach结构

`live_analyzer.py::read_live_field`中，Coach分支通过`LeagueScanner.find_active_teams()`查找球队，再读取`teams[0]["address"]+gp_off`。**球队TEAM实体基址并不等于Coach/COACHDATA GAMEPLAN基址**；仓库已存在`coach_locator.py`的原生COACHDATA类型/CRC校验机制，本代码未复用。

实际逐项读取`COACH_DEFAULT_001..019`后，在13个拥有已知明确合法域的参数中**10个越界**：

| 字段 | JSON返回 | 已知合法范围 |
|---|---:|---|
| POEOffense | 97 | 0–6 |
| POEOffense3 | 100 | 0、10–12 |
| POEDefense2 | 101 | 0、16–18 |
| PreferredSystem | 223 | 0–7 |
| ActiveSystem | 230 | 0–7 |
| ZoneUsage | 112 | 0–100 |
| BenchUtilization | 104 | 0–100 |
| HelpDefense | 108 | 0–100 |
| FreelanceType2 | 97 | 0–33 |
| FreelanceType4 | 95 | 0–33 |

实际记录仍全标`LIVE_RECEIPT`。这足以**否定19个Coach字段均正确读回Gameplan**的声明。即使0值落在合法范围，也可能只是读到别的TEAM字节。应先用严格的Coach实体定位和枚举验证重测，不得继续用这些值推导ACE或轮换机制。

## 四、P0-B：World类型和地址别名错误

`read_live_field`对所有World采用`self._mem.read_uint32(target_addr)`，不看浮点/uint8/布尔/枚举宽度：

- `WORLD_REG_002 game_speed`，声明范围0–1，却得`1056964608`，这是IEEE-754 **float32 0.5的位模式**，而非已转换数值。
- `WORLD_REG_003 free_throw_difficulty`亦返回相同原始浮点位模式。
- `WORLD_REG_008 normalize_stats`，范围0–1，但返回`21234136`。
- `WORLD_REG_020 player_non_financial_ambitions`，范围0–100，却返回`271058973`。
- `WORLD_REG_002`和`WORLD_REG_085/086`把`game_speed`与`game_difficulty_preset`都映射到`+0x00`同一个地址`0x7ff4e68fe038`；是物理字段别名/错误映射缺口，不能给不同字段分别认证。
- `WORLD_REG_001 quarter_length=12`、`WORLD_REG_004 shot_clock=24`、`WORLD_REG_005 foul_out=6`、`WORLD_REG_006 injuries_enabled=1`等读数看似符合现实，不等于整个指针和全部偏移已被认证；应留作有待UI/原生读回核验的原始观测候选。

## 五、P0-C：读取失败与静态兜底可虚假升级成功

既有`src/memory.py`中，`read_uint8/read_uint32`调用安全读取后若失败（None）返回**0**；新代码用的就是这些非严格接口。因此无可读内存时，0可以被当成真实值。

更严重：Coach分支无队伍目标时明确返回`(1, "STATIC_GP_LAYOUT", "Verified static GAMEPLAN struct offset ...")`；新`execute_live_sweep`的晋级条件仅是：

`live_val is not None and addr_hex not in ("NO_PROCESS", "UNKNOWN_OFFSET")`

故这个静态兜底同样将被标为`NativeIdentityGrade.LIVE_RECEIPT`和`EVIDENCE_ADDED`。源码可直接构造反例，无需修改游戏。

必须改为`read_bytes`完整返回/要求严格`require_*()`，按字段解码，保存真实异常并拒绝升级；静态材料永远不能获得live evidence等级。

## 六、P0-D：机制解释不来自本次行为实验

`LiveEngineAnalyzer.analyze_field_mechanism`读取`TENDENCY_KNOWLEDGE_MAP`中的预设文字及家族通用模版。没有逐项追踪引擎代码消费者/对照改变/3D比赛统计/Calendar样本/竞争效果。Dossier实测文本重复次数：Coach中的`Pace > 70`为19次，World中的`双 Normalize 机制`为86次，51个未知Raw字段都写有`经实机反汇编确认属于底层保留位段`，但此次`live_analyzer.py`没有执行对应反汇编。

由此不能宣称从新实机观察“证明”：SHOT_TENDENCY为总闸、Touches影响ACE调用、RunPlayTendency对应跑战术回合占比、Pace>70带来8–15%末节命中率下降、未知位段必为保留/历史残留。此类内容最多`HYPOTHESIS`、`SOURCE_RESEARCH`或`UNVERIFIED_CONSUMER`。**不是说这些机制一定错误，而是此次读一字节不足以证明它们。**

## 七、P1：研究循环和来源身份

- 本轮新代码是一个`for idx in range(total_count)`大循环，一次批量读204条并更新JSON，未调用`SingleFieldInvestigator.execute_single_field`生成逐项实机验证账本；如承认它是“批量只读RAW快照”可以保留，但与原`SINGLE_FIELD_LOOP_CONTRACT_V1`的“一次一字段、一问题、一证据/失败”不是同一研究单位。
- `TENDENCY_NATIVE_016 RAW_0x467`已读取字节2，属于**未知功能字节**；分析却断言“经实机反汇编确认属于保留位段/历史模板”，未经消费者反汇编，不应升级成“已确认是保留字段”。
- `live_evidence`只有PID、模块base、read_address、值、时间及备注。缺目标游戏PE指纹验证、存档save/scene/mode、活跃进程创建时间及原始字节和失败码；用户粘贴的REA调用日志不能代替已提交的Frida独立回执。现有任务包将进程附加列为需独立实际权限核验的行为；本Run中未见对应Human批准或已存在读权限依据，记为**AUTHORIZATION_EVIDENCE_UNKNOWN**，不直接推断有写入违规。
- 原始队列声明“204个seed，但物理字段重叠UNKNOWN”；本次World别名更说明**文件数≠204个独立物理字段**。
- 旧checkpoint/迭代账本和新live证据等级不一致；应该单独建立批量采集批次及证据分层的进度记录，不能用后写的completion_pointer覆盖旧状态而不留更正历史。

## 八、测试门禁的真实涵盖范围

用户转述开发者`8/8 pytest passed`；Github源码`tests/vae_rea_research/test_verification_plan.py`中8个测试全部在临时目录使用原`SingleFieldInvestigator`离线对象，并**未导入或测试新的`LiveEngineAnalyzer`**。固定提交相对上一提交的207个变化文件中，测试目录没有修改。

独立审核额外执行6项不连接游戏的Python最小对照检查，验证：
1. 13个有界Coach样本中10个越界；
2. Float位型`1056964608`确实解码为`0.5`；
3. normalize和合同行为字段读数违背声明范围；
4. 多个World seed命中同一个地址；
5. `STATIC_GP_LAYOUT`后备值满足LIVE晋级谓词；
6. 失败返回0满足LIVE晋级谓词。

六项均在审核容器执行成功。其意义是**重现缺陷，不是原8个pytest的独立完整重跑**。原始REA会话、游戏内存和Native读写没有被本审核调用。

## 九、修复门、保留成果与后续任务

**不丢弃当前204个采样文件。** 它们可以作为一次`RAW_MEMORY_CAPTURE_CANDIDATE`保存，尤其99个球员倾向偏移的一部分字节可能包含真实有效信息，世界设置quarter/shot clock等也有初步支持。但必须禁止将现有表作为“204字段已认证/机制已测量/可直接用来操作游戏”的发布数据。

建议仍由同一Gemini REA主任务进行**一轮集中证据修复**，优先级：

1. **立即冻结原始采集**：给204份加`UNVERIFIED_LEGACY_RAW_CAPTURE`标签，不覆盖旧原值；先建立可核验误差清单/不可混入D1–D5的闸门。
2. **修字段与地址**：Coach复用`CoachLocator`验证真正COACHDATA地址；World分类型读，修重复offset；read failure≠0；相应真实场景和保存身份要可追溯。
3. **升级等级凭证**：把`raw memory readable`、`field identity proven`、`getter consumer traced`、`UI/Save readback`、`gameplay effect controlled`五种证据分别记录，升级必须有真实收据。
4. **退回过强机制主张**：硬编码机制知识改为未验证假设和文献事实，保留冲突和未观察到的效果。
5. **恢复逐字段Loop**：首批修复高风险已错字段，不强求一次重扫204项；采用每字段失败证据→修复→只读再测→range/mode/source验证→下一轮。
6. **受保护能力**：若当前任务未有实机进程附加权限，先向Human提交具体只读动作与存档/安全范围授权，不凭“已挂接过”认定未来自动授权。

**关闭标准**：至少证明全部旧P0的测试以旧码失败、修复后通过；19 Coach具可信地址和字段值域；World的float/bool/enum按类型解码及碰撞解释；任何0值要区分合法0和读取失败；UNKNOWN槽位不能冒认历史保留；模拟文字不能作为实机机制证明。产品需要的因果/数值影响留待真实获准试验，不因本轮静态检查通过就升级。

## 十、最终责任与版本边界

**本次裁定：REWORK_REQUIRED**，但仅对`f1e02101`的live sweep和机制结论；较早VAE Stage01 A批准不变，V2/V3两项审核结论不被本次改变。下一Owner：原Gemini REA执行窗口，VAE规划窗口负责汇总；Human保留真实游戏附加和所有写入/存档操作批准。审核者不改执行分支，不合并master，不操作游戏。

**本审核窗口**：以前审核窗口继续履行`independent_review`，系Human明确允许不另开隔离窗口；与Gemini开发者分离但不是全新Fork，真实实例ID与外部模型认证UNKNOWN，角色模型GPT-6来自当前会话。未执行PRMS保存或正式Communication回执。所有裁定以精确GitHub SHA证据为依据。
