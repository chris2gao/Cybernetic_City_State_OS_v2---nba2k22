# WORLD-DATA-ARCH-01 数据真实性与质量契约 V1

状态：CANDIDATE_PENDING_INDEPENDENT_REVIEW；2026-10-22。适用概念见[领域模型](WORLD_DATA_DOMAIN_MODEL_V1.md)与[实体字典](WORLD_DATA_ENTITY_CATALOG_V1.json)。本合同不认证任何未验原生字段。

Human 审核更新（2026-10-22）：本轮明确结论为“这次算审核通过”。详情及后续实际验证结果以 OS run 的 completion_pointer.json / human_review.md 为准；独立模型审核尚未进行，候选未合入 master。

## 1. 数据类别与不可互换的证明

| 类别 | 必需证据与时间 | 生命周期与禁止推论 |
|---|---|---|
| 事件事实 EVENT_ASSERTION | 同世界稳定事件身份、实际发生时间及精度、原生来源或已执行并回读的回执 | 追加修订；计划/批准/名单差异不自动证明交易或签约发生 |
| 状态观察 NATIVE_OBSERVATION | 主体、字段、观察时间、已知有效时间、batch/binding/decoder | 不覆盖旧观察；能力、合同、伤病不强塞到比赛流水 |
| 原生累计 NATIVE_OBSERVATION | 主体/season/competition/team-stint/as-of、原始来源 | 原生 SeasonTotals 独立保留，不等于单场收集完整 |
| 派生 DERIVED | 公式 ID/版本、参数、单位、输入断言集合与覆盖范围 | 缺输入则 PARTIAL/UNKNOWN；新公式产生新结果；不得标成原生 UI 值 |
| AI | Actor/安全观察集合/时间/模型或策略版本/决定状态 | 分析与记忆不改游戏事实；人物意见不能充当真人批准 |
| STATIC_RESOURCE | 模板或研究版本、真实来源年代、适用性和权限 | 可复用定义，不复用世界历史；真实 NBA 未来知识不得自动进入游戏角色 |

采用来源对象、产生过程和责任主体分开的可追溯结构，参考 [W3C PROV-DM](https://www.w3.org/TR/prov-dm/)。这里只借用其证据组织原则，不引入第二套 OS、PROV 运行引擎或外部服务。

## 2. 字段级证据轴

每个字段保留 origin、evidence_refs、scope、observed/valid time、decoder/layout version、acceptance status。证据标签可并存，**不是一条从低到高自动晋升的等级**：

- NATIVE_EVIDENCE：存在带存档/版本范围的原生观察或研究记录，注明 producer 和是否本轮复验。
- FIXTURE_ONLY：只在固定样本回放或构造例上验证；不能外推当前进程和全联盟。
- UI_CROSS_CHECKED：具体同存档、同时间、同字段的 UI 对照；不能扩大到其它列或游戏效果。
- DERIVED_WITH_FORMULA：通过明确公式产生；包括 Decoder 输出中的 TS%、eFG%、胜负切片和由投篮数计算的得分。
- STATIC_CANDIDATE：代码/字段目录存在，动态值或语义尚待证。
- UNKNOWN：未证的具体事实或关系，并带下一步验证条件。

工程 maturity（实现/未发布/已发布/可查询）、原生语义、UI、执行和 Save/Reload 分开记录。当前仅静态读了 AG01C/01D 文档与 Decoder，**没有运行其历史 41 个测试，也没有重新读取游戏**。历史 Curry16 场/18 指标对齐仅为被引用的研究样本结论。

## 3. 主要原生样本如何进入模型

| 来源 | 模型承载 | 本轮可据以设计的内容 | 保留的未知 |
|---|---|---|---|
| AG01D SEASON_GAME 60B | Game、TeamGameResult、BoxScore | 候选 header、队标识、日期、状态、比分/StatBank 引用 | GameID 稳定范围、flags、加时/延期、有效比赛边界 |
| AG01D 24B StatLine | PlayerGameStatline | 候选 PlayerID、InUse、投篮/篮板等字段 | StatBank records 边界、ID 解析、未出场语义、分钟精度 |
| Slot24 PLAYER_STATS 48B | SeasonTotals | 原生累计与 Box 汇总对账的候选关系 | team-stint vs season-total、跨季编码、统计模式 |
| PLAYER +0xFC / 历史索引数组 | CareerHistory | 球员→原生赛季记录的候选连接 | 索引容量/哨兵、年份、退役持久性、超过 20 项 |
| Slot44 | Record-like team matchup observation / DerivedStatistic 输入 | AG01D 将其解释为 TEAM_MATCHUP_MATRIX | 仍待独立验证；**不是逐场赛程来源** |
| Slot10 / SEASON | GameCalendar | AG01D 报告的真正赛程候选 | 二者对应关系、身份/未赛/延期覆盖 |
| PLAYER/TEAM 与现有 SourceExtensions | PlayerIncarnation/Franchise 映射、StateObservation | 按批次、对象、字段 profile 解码 | 不能把 roster slot、名字、绝对地址当永久 ID |
| 教练/训练设置 | StateObservation/TacticalConfiguration | 当前配置观察 | 设置生效、真实战术执行、Save/Reload 仍需独立证据 |
| Slot39 Record Book | RecordBook | 原生纪录观察及来源分类 | 内置 NBA 历史不等于此存档发生的 Game，尾部 flags 待证 |

原 AG01C “Slot44 是赛程”的结论保留原文作为历史；新消费者按 AG01D 修订解释并保持待验，不能读取旧 schedule_decoder 输出就直接创建 Game。其所谓 schedule fixture 也不得无声明改称当前已认证赛程。

## 4. 字段值、缺失、时间与发布

字段值为 `{value, status, unit, origin, evidence_refs, sensitivity}`。KNOWN 的 0 必须来自真实观察或有效公式；UNKNOWN、NOT_OBSERVED、NOT_APPLICABLE、WITHHELD、CONFLICT 分别表示未证、未采、不适用、权限遮蔽、证据矛盾，value 不充假零。被遮蔽 placeholder=1 属于派生替代，不是真实 Potential=1。

时间采用[ADR](WORLD_DATA_IDENTITY_AND_TIME_ADR_V1.md)的 game valid time、observed_at、recorded_at 和 publication batch。批次时间不代替事件发生时间；未知生日或交易日期不由采集日期补齐。SourceManifest 声明本批次对象/字段覆盖、布局/Decoder、哈希、绑定、质量规则及敏感裁剪；不能以“全量”掩盖某域 NOT_OBSERVED。

受限原始字节保存在原生证据层，规范字段与 AI 记录分层。raw payload 不进入角色 SQL、导出、异常信息或调试响应。对每个 factual assertion，source_refs 至少一项且能追溯到本世界来源；静态模板引用不能充当比赛发生证据。

## 5. 质量门与失配处置

1. **身份门**：所有业务引用 world 一致，native mapping 来源/范围/版本有效，无歧义。失败则隔离观察，不发布猜测实体。
2. **结构门**：对象长度、索引范围、集合边界和适用布局；UNKNOWN 不能被“分配容量”冒充有效记录数。
3. **关系门**：Game/Season/competition、team sides、PlayerGameStatline 的实际球队、Contract/Pick/Actor 引用一致。FINAL 完整 Box 恰有两队，单修订各侧唯一。
4. **统计门**：只对相同主体、赛季、竞赛、球队口径、截至时间和足够覆盖的数据比较可加指标。比分等式、sum-to-season 是有适用条件的核查；百分比、四舍五入分钟、对手指标不能无条件相加。DNP 与 NOT_OBSERVED 不同。
5. **权限门**：固定 world/actor/as-of/批次及字段投影；已验证脱敏 manifest 才允许普通 GM 消费。
6. **发布门**：完整 cohort、失败闭合、哈希、恢复和重复发布幂等。部分数据可在显式授权的 PARTIAL 视图中展示；不能宣称完整的生产批次通过。

发现 45 vs 70：保留两者与 discrepancy=25，记录可能为遗漏比赛、口径、时点或解码差异；没有证据不得选定原因。不会造出不存在的 25 分比赛，不改原生值。关联约束错误阻断相关规范数据，其他域只有在其发布合同明确允许且无依赖污染时可独立发布，不能借 PARTIAL 绕过完整批次门。

## 6. 普通 GM 及未来角色的安全合同

普通 GM 只获取明确白名单 DTO，默认拒绝新字段、任意 SQL、通用 JSON/raw payload 和任意关联穿透。请求同时验证 actor 的 world、subject/球队授权、game_as_of、knowledge_as_of、published batch 和 `GM_SANITIZED/potential_v1` 或后继已审策略。已有旧批缺标记就拒绝，不能重写封存历史伪装已脱敏。

Potential 的直接字段、中文/别名、raw_struct 原位字节、debug 嵌套、模板反查及由其参与的派生评分都属于敏感来源；别名不降低敏感性。派生结果继承输入限制，序列化只能按具体 DTO schema 递归投影。日志、错误、缓存、导出也服从同一边界。当前 JSON 的 GM 示例允许字段是概念测试最小视图，不宣称已经定义所有 GM 生产 API。

Coach/Player 未获权限的字段同样默认拒绝，不因角色名字推定可以看隐藏值；角色全面许可矩阵由后续 WORLD-ACTOR-DATA-01 细化。角色自身表达的意愿/记忆仍是 AI 来源。Actor→Observation→Decision→Approval→Receipt→Readback 全程同 world；新技术绑定使旧批准失效。回读一致、UI 效果和保存重载分别报告。

## 7. 订正与审计

业务事实稳定 ID 与来源断言 revision 分开。同一 game 的原始字节可在多个批次不同；相同内容不重复计算比赛，有据更正追加版本。冲突不靠“最后写入覆盖”。撤回保留审计及原因，同世界恢复备份时只调整当前有效历史的选择，不生成分叉。原生累计不会因后来的推导冲突被修改，AI 不能发布到 NATIVE_OBSERVATION 命名空间。

本任务的概念检查只验证这些样例关系、字段投影和文档契约。实际 API 攻击面、SQLite 事务和游戏布局必须在相应后续任务复验。
