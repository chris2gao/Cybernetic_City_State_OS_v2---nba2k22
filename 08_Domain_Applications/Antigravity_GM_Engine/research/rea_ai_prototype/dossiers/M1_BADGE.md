# M1｜AI自然徽章成长：CatchAndShoot深入、CornerSpecialist轻对照

范围：固定PC22构建、offline MyLEAGUE的AI球员。`PLAYER`实体不等于HumanController。选择两徽章是利用现成机制资料和类型定义开展有界研究，不声称已证明它们共用成长函数。

来源链：`SRC-R04A-BADGES`、`SRC-R03-MENTOR`是项目指南；`SRC-PRIOR-METADATA/GROWTH`来自b16e6972的同一个旧Codex run；`static_ai_seams.json`与`candidate_function_fragments.json`是本轮新离线PE观察。精确commit/blob/hash见source_registry。不把旧两份文件算两次独立实机证明。

## 主病例

- CatchAndShoot出现在旧类型/效果资料：`BADGE_TUNING::SHOOTING_BADGES`的CatchAndShoot子对象及COMMON_SPOT_UP中的接球后时间、距离、防守和bonus字段，是比赛效果候选。它们不提供自然学会/升级阈值。
- `FRANCHISE_MENTOR::BADGE`有Type、Level、IsActive、Progression、DateLastChecked；MENTOR含DurationInDays、Compatibility、MentorshipStartDate、NumberOfBadgeEntries和Badges。L1只支持这些定义存在，实际进度单位与成长规则未知。
- 本轮M1定位到LinkMentor引用片段RVA范围19965988..19966354、SetMentorsInCurrentTeam片段20067334..20068330，分别解码88、247条指令。`.pdata`可能只界定fragment；类型/断言名与cmp常数不是完整函数签名、AI入口或成长阈值。L2仅支持局部静态引用和分支。

## 轻对照

CornerSpecialist同属技能徽章候选。其场上效果调参中的角落距离和干扰条件不能与CatchAndShoot的接球时间条件混为成长条件；没有本轮同模式自然成长轨迹，阈值及周期均UNKNOWN。

## AI路径、后端与可读知识

目标为AI自然成长，MyCAREER Human积分/声望/自主选级排除；“MyCAREER NPC与MyLEAGUE AI共用算法”为Human线索，非实证。尚无AI自然成长调用点、controller分发、计算公式或完整更新副作用。

Player/Coach可用知识：知道需要观察既有导师/学员关系、进度与日期，能提出训练或观察请求；不能告诉球员“三分达到X必升级”。不是直接改徽章的执行建议。

Native：NOT_QUALIFIED；Memory：NOT_QUALIFIED；route：NO_SAFE_PATH。没有尝试游戏成长函数调用、徽章写入或推进日期。无L3/L4。

后继：固定一名AI球员、一枚徽章、一个已存在导师关系与允许自然时间范围；只取公开进度投影和更新时机，先明确实例与身份，再观察分支/消费者。跨模式比较需各自证据，不用相似名字合并。

结论：`BOUNDED_UNKNOWN`。本轮推进了类型到局部代码的候选链，尚未解决成长条件；无安全执行路径也不会让已有知识失去可查询价值。
