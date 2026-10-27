# 阶段02 · REA 实时观测能力增量及 Overall 来源边界（阶段性外部报告）v1

**性质**：2026-10-27 Human 在规划窗口提供 `REA_DIFFICULT_ITEMS_EVALUATION_20261027.md`；这是一份Codex侧有界研发评估报告的**二手规划摘录/来源登记**，不是当前GPT对游戏/Windows的独立实测，也不是该后续Codex任务已完成/已发布的证明。本Run暂未取得此REA任务的Git固定commit、完整原始脚本/证据、独立验收回执。**原始用户上传仅存在本会话附件，未将原件提交公共仓库；待Human以后提供正式工程交付地址和固定SHA，再做全文证据回指。**

**上游产品权限**：10月26日固定 v25 `DIFFICULT_ITEMS.md`（Blob `0aefaa0db2ca899122ffc9e64a1e0b5edd382601`）曾记录 Overall `HUMAN_DEFERRED`、允许当时任务不交付；本次Human明确另让Codex有界重新探索，并提交观察报告。**重开独立研究 ≠ 旧A要求自动改变 ≠ 正式Overall已经纳入核心验收**。继续遵守“只读取游戏原生已有数据，不额外开发统计计算引擎”。

## 1. 仅由新报告支持的事实（非本规划窗口直接复测）

| 事实 | 观察范围及可信边界 | 对统一容器建模的影响 |
|---|---|---|
| 当前 PLAYERDATA 有元数据匹配 | 报告：963字段、1264字节布局；缓存原始字段索引150/CRC1370230541/`+0x16C` `float32`，有效标志索引334/CRC2166828986/`+0x31C` bit6；字段名称复用既有literal/CRC表，不是本次新发现名称 | `overall_cache_raw_float`、`cache_valid` 和源版本/CRC/offset成为**有证候选源字段**，实际数据库字段命名仍按v25现有字典/03有证设计，不擅自增加DDL |
| 当前PLAYER描述符数3390 | 仅抽样源槽0..5，六名球员姓名与双ID对应，缓存6/6均valid，前后两个采样一致，三个既有getter代码窗口与内存匹配 | 只可证明**这六人/该进程/该构建**的有效缓存读取，不可升格为3390全池正确或跨赛季身份完成 |
| 原生getter路径 | 报告结合旧代码指出valid=1走缓存`+0x16C`，valid=0进入重算RVA0x99B670；本轮**没调用getter或重算函数**，未hook、未显式写游戏内存 | `valid=0`必须返回`SOURCE_UNAVAILABLE_OR_UNKNOWN`而不是旧缓存/猜算的Overall；无效缓存处理属于Reader正确性，不要求GPT规划重算 |
| 六个float32实读 | Ben0.866666675、Seth0.779117107、Danny0.782149017、Tobias0.854910135、Embiid0.952591836、Drummond0.782066464（完整精度/出处以原件为准） | 可仅按原始float32及其有效性存源证据；`float32 ×100 + nearest-even`的87/78/78/85/95/78是**候选显示映射**，报告所有rounding_independent_integer均为null |
| Human两份UI样本 | Ben基础87，Embiid基础95/加成显示96，与两项整数候选相符；游戏模式、同刻快照、进程/档案对象完全同步未独立证明 | **基础Overall候选**与**加成后UI Overall**必须分开表达；不把87/95认定全场景`VERIFIED_UI_OVERALL`，也不以基础缓存填96 |
| REA性能与局限 | 六人读数约4.447s、元数据匹配约3.477s；NBA2K22完整EXE的Ghidra分析四轮provider_timeout，总失败等待约26.6分钟 | 后续Codex将REA限定在有清晰目标/字节和终止预算的实时内存观察；当前整EXE静态分析路线**停止重试**，无证不得将完整xref当已实现 |
| 对其他困难项 | 攻防聚合评分、教练40槽年份、战术CRC文字、完整S1–S8、历史身份和UI舍入等均为潜在有界复用场景，**本轮尚未逐个完成研究** | 不依据Overall工具成功宣布这些字段获得正确来源，不擅自调整原来所有领域的UNKNOWN |

报告已列出可供以后按正式交付核对的原始证据ID：`ev_4e96182cf713435a7784bad37625176e9130a7cc02e443849f4c81bb30af6638`和`ev_d78dbbd7986dce021ccd9f6bb5b672aa7f2c7c0598da1dfda8e82ea3caf3a729`；它们**不是本规划任务访问过的工具证据**，仅为报告作者声明的追溯线索。完整日志清单和实机权限边界由报告原件保存；不根据本摘录重建/执行脚本。

## 2. 对 B0 五层容器设计的具体增量（无需新架构ADR）

1. **来源层 L1**：支持`source_layout_version / source_field_crc / source_byte_offset / native_type / valid_flag / actual_observed`等元数据项，同时记录`source_grade=REPORTED_REA_LIVE_OBSERVATION_NOT_INDEPENDENTLY_REPLAYED`。原始数据可读 ≠ 自动成为真实UI解释。
2. **身份层 L2**：每次读缓存先验证`save/build/process/roster_descriptor/unique_id/preserved_id`与目标对象，不能沿用本报告一次固定偏移/地址到不同构建/进程；双ID当前匹配仅对六样本成立。
3. **typed事实 L3**：可保留原生缓存`float32`与valid位；可选保留有算法版本的`integer_candidate`，但不可当`game_ui_overall`已验证。若原生有独立加成/显示来源，需独立证据与字段/显示口径。v25既有`overall_raw`兼容列先核复用，不凭报告直接新增schema。
4. **历史 L4**：记录`observed_at/source_unit`和有效性；valid从1到0只能证明缓存不可用，不能把上次有效值偷当新读数或将旧Overall标成当前真实值。
5. **访问 L5**：普通角色仅使用已核准字段和来源等级。未知缓存或UI舍入不可用于确定性游戏评级/模拟，不赋予写权限。原生Getter的`recompute`调用不是本报告授权的Reader操作。

## 3. 后续Codex任务中的受控调查目标（此处不发新任务）

- **优先级1**：仍以整体游戏容器/字段覆盖、选秀/合同/身份/奖项等领域为主；Overall是在Human已经额外批准研究的困难项，不自动挤占整个A的核心完成门。
- **条件验证**：获得足够同一`save+game_stage+entity+time`的UI基础/加成显示对照，再检查`float32`口径及舍入；观察valid=0出现时正确标UNKNOWN，报告重算路径但不自行触发函数；必要时有界检查显示加成来源。
- **工具策略**：优先小规模REA/Frida attach与明确字节/时间预算；完整EXE反编译当前路径不再重复四轮失败。新工具实现稳定可复用的Native源码/metadata读取后，再更新Reader/Codec设计及版本，控制反证/失败预算。
- **禁止范围**：不因找到了缓存自行设计Overall加权公式；不为证据复现进行实时写入、Hook、游戏推进、存档修改，除非后续Human另行授权；不要求GPT自己运行REA。
- **正式归档门**：等Human提供Codex此次任务的最终工程报告、exact commit、原始证据/元数据版本与审核/失败边界，核对本报告与正式固定来源后提升证据等级；如新研究推翻旧结论，保留两版证据及新增修正裁决。

## 4. 本轮能力结论

`REA_BOUND_CURRENT_PLAYERDATA_METADATA_AND_VALID_CACHE_SAMPLED` 已获得**Codex报告级**证据，足以为后续规划新增“缓存有效位/原生值/显示候选分层及工具取证门”，**不足以证明OVERALL_FUNCTIONAL_COMPLETENESS、全池/全场景UI可靠性、原生Writer能力或整个EXE反编译成功**。不借新工具能力扩大当前“容器存食材”产品边界。

**规划文件落点**：本文件作为阶段02接续和S1目标字段研究的补充事实；本Run正式`stage02_evidence_verdict`不改变，`B0`仍为设计候选，Codex工程原型分包仍`NOT_DISPATCHED`。
