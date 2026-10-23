# GAME_FIELD_LIFECYCLE_RULES_V0 — 字段生命周期与年龄规则

**V0 候选；不宣称原生验收。** 每项事实绑定当前世界、对象、来源、游戏有效时间、现实观察时点、Decoder/layout 和批次，必要时含修订与订正来源。

| 类型 | 内容 | 处理 |
|---|---|---|
| STABLE_IDENTITY | world_id/player_uid/game_uid/team_uid | 由外挂绑定，跨采集批次稳定性要有原生证据 |
| RELATIVELY_STATIC_PROFILE | 出生年份、真实历史选秀、身材 | 保留来源及修订，罕变不等于永不变 |
| MUTABLE_SETTING | 游戏规则/滑块/教练战术 | 当前游戏值与配置默认值分离 |
| DYNAMIC_NATIVE_OBSERVATION | 球员能力、徽章、倾向、球龄、合同、健康、训练 | 追加带时间的原生观察 |
| GAME_EVENT | 实际比赛、交易、选秀、合同签约、荣誉 | 去重业务事件，不以提案或两次采集伪造历史 |
| GAME_NATIVE_AGGREGATE | 游戏自身 SeasonTotals/CareerTotals/游戏高级 UI | 原样保存口径，不以我们统计覆盖原生数据 |
| EXTERNAL_DERIVED_CANDIDATE | age_derived/TS/eFG/Per36/角色评分 | 按上层需求再计算，版本化公式与输入引用 |
| RESEARCH_ONLY_CANDIDATE | 外站标签、未认证 Getter/偏移、跨版本菜单 | 不填当前存档数据，不开放角色查询 |

## Human 明确提供的年龄计算候选

```text
age_derived = original_draft_year - birth_year + years_pro
```

`original_draft_year` 是球员真实历史选秀来源年；`world_draft_season` 是独立存档内实际发生的选秀赛季，两者不混用；`years_pro` 为游戏记录的 NBA 职业球龄，动态变化。1984 - 1963 + 5 = 26 是计算示例，**不是游戏读取的事实值**。该公式源于玩家长期 MyLEAGUE 经验，是优先开发候选，尚未证明等于所有 PC22 游戏内部年龄逻辑；独立年龄内存槽不是 Flash 的阻断任务。

Flash 应对同档 UI 的 `display_age_observed` 与 `age_derived` 分开保存。重点验证出生日期边界、新秀球龄0、异年历史选秀、未选秀球员、休赛期跨年、退休复出和不同存档职业路径。缺任一输入即 UNKNOWN，不以世界年份自补。发现 UI 值不同则保留双值和差异，不反向改写原始资料。

## 观察与质量

KNOWN 的 0 只有真实来源时成立；UNKNOWN、NOT_OBSERVED、NOT_APPLICABLE、WITHHELD、PARTIAL 和 CONFLICT 必须区分。同一球员已采两场得分45，游戏原生赛季累计70，采集覆盖 PARTIAL 时不构成已证 CONFLICT；须先验证完整覆盖、赛事口径、球队 stint、赛季与时点。时间是 game valid time / observed_at / recorded_at / published_batch 四层，纠正产生 revision 和 supersedes，历史原始字节仍保留。

## 数据权限与执行

隐藏 Potential 及其它受限原生字段不进入普通 GM、公开 SQL、调试导出；敏感性或来源缺失时默认拒绝。静态 Profile 有读写编解码配置不表示获得真实游戏修改授权；后续每项动作单独核实绑定、前置条件、Human 批准、Readback、Save/Reload、关联对象副作用和失败恢复。球员自然成长只由游戏模拟产生。
