# NBA2K22 01b · 世界线关键设置与依赖审批清单模板 V1

**状态：审批模板，不是已批准的任一世界线配置实例。** 来源 Q46–Q47、Q49、Q52=A。01b只规定字段语义及审批门槛；将来具体世界线项目及真实 PC22 读回路径、参数值需由 Human 批准和阶段02证实。

## 每份世界线版本的标识

| 字段含义 | 本次模板状态 | 审批要求 |
|---|---|---|
| `worldline_config_version` | UNASSIGNED | 由具体世界线定义 |
| `intended_save_scope` | UNASSIGNED | 独立存档；绝无继承/分叉/合并关系 |
| `manifest_revision` | V1_TEMPLATE | 修订不改已确认的历史配置观测 |
| `Human_approval_ref` | PENDING | 关键级别和修改必须Human确认 |
| `applicable_game_version` | TARGET_PC22_VERIFY | 仅目标 NBA2K22 PC/MyLEAGUE 来源 |

## 逐字段审批与实际开档读回

| 世界线版本 | 设置域 | 原始字段/游戏页签 | 预期值与单位 | 关键级别 | 依赖操作 | 判等方式/容差 | 读回证据与时点 | 审批状态 | 失败后行为 |
|---|---|---|---|---|---|---|---|---|---|
| 待定 | 世界线/联盟/比赛 | 待阶段02核证真实字段 | 待Human配置 | PENDING_CLASSIFICATION | 待列依赖机制 | 待Human确认比较规则 | NOT_OBSERVED | PENDING_HUMAN_APPROVAL | 未证关键项不得认为通过 |

- `intended_configuration` 的外部预期值、`observed_game_configuration` 的实际游戏读数以及 `configuration_reconciliation` 的核对结论必须分开保存，并按每次开档上下文重新读回，不借用旧开档结果。
- **关键且不一致/无法核验**：阻断确实依赖该设置的外部模拟操作，记录真实缺口与原因，保持只读诊断和异常采集通路；**非关键差异**按批准策略标记，不冒充全量成功。
- 未获 Human 确认关键级别、阈值/比较规则、所依赖操作或变更者，不得自行降低关键性或设置系统全通过。模板不自行确定任何真实 Slider 值。
- 本文不是未来设置器、游戏写入程序或数据库DDL的实现任务；只为01b结果A审核提供数据契约样例和交接要求。
