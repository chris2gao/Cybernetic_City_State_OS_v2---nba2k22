# NBA2K22 第一大任务 · Codex初始数据库原型实施交接 V0.1（派单候选）

**状态：CODEX_HANDOFF_CANDIDATE_NOT_DISPATCHED；没有启动本地执行。** 依据Human批准的 V0.4开发方式、[ADR-01/02批准记录](NBA2K22_TASK1_INITIAL_PROTOTYPE_ADR01_ADR02_HUMAN_DECISION_20261024.md)及[59表初始原型 V0.2](NBA2K22_TASK1_INITIAL_DATABASE_PROTOTYPE_ARCHITECTURE_V0_2.md)。需求A v1.9/审核包V0.3仍是最高产品范围；原型表数可调整，须有完整字段/源责任去向。

## 1. 工程目标与单一Owner

**唯一工程Owner：Codex**。本规划GPT负责产品范围/架构设计和Human重大裁决，不替Codex自审实施。Gemini承担有界原生取证子包，回交原始证据给Codex。

**必须交付真实能运行的SQLite原型和随代码发展的完整表字典，不是另一份架构综述**。首个输出应直接可检验地展示已确认存储拓扑下的数据库文件创建、最小有证fixture导入、常见JOIN及错误/权限负例。

- **ADR-01固定方向**：每个独立游戏存档一个事实SQLite，SQLite内部有唯一不可变save_id，不能跨档关联/复制继承；SQLite不是游戏Save。
- **ADR-02固定方向**：球员Attributes/Tendencies使用typed字段族观察宽表，Badge/PlayType是关系子表，真实采集不可因数值相同而去重。潜力字段走受限通道。
- **允许工程调整**：按来源证据增减59张候选表、修正列/索引/局部关系、增加原生字段族，但必须登记来源与差异，不得更改已决根本方向、删减获批范围、制造历史或隐匿敏感字段。

## 2. 先完成一份贯通的SQLite工程切片

按已有代码和真实来源证据，建议的**实际实施顺序**（不作为中间新增Human审批关）：

1. 将[初始原型V0.2](NBA2K22_TASK1_INITIAL_DATABASE_PROTOTYPE_ARCHITECTURE_V0_2.md)转为可执行设计：完整候选表清单、来源等级，旧`database/schema.sql`27张表保留/重构/废弃的逐表映射，新增字段角色/时间语义；未证取值标`UNKNOWN`。
2. 建立单档库的`saves`（单记录存档身份）、`seasons`、`capture_runs`、`capture_units`、`teams`、`players`、`games`、`player_game_boxes`及一个`player_attribute_snapshots` typed子集（只用已证字段/原生线索准确标级）。SQLite DDL需真实执行，`foreign_keys=ON`且实际验证跨档导入拒绝，失败采集不污染可信当前值。
3. 用**已有受控和可复制的fixture**连接AG Native候选读取接口：`SEASON_SCHEDULE`、`BOXSCORE_STATBANK`、`Slot1 PLAYER`、`Slot24 PLAYER_STATS`。将`RESEARCH_CLAIM`与真实独立验证分开，不能把假样本或计算值标作游戏原生事实。
4. 实装球员能力/倾向typed快照和独立Badge/PlayType两类子表，证明一次真实有效捕获只产生一次同unit数据、不同unit合法观察均存档，`unknown/not_owned/0`不混同。普通GM读视图无法查询或导出Potential；如果源头有受限观察，要从普通业务表实际隔离。
5. 逐步覆盖完整59表候选的对象与字段，Native探索出现新事实直接改Schema并记录`ADR/change note`；每域真实源码/字段→DB列→查询结果可追踪。**一张通用表或仅一个Box切片都不能称全库完成**。
6. 交付最终可运行DDL、明确最终表数、逐表所有字段/合法范围/来源/单位/PK/FK/索引/设计理由、原生Reader与入库、真实/计算状态、百年容量基准、权限/历史/失败负例和完整Q10缺口；原生来源尚未查明则列明，不能宣布全部通过。

## 3. 开发/验证最小检查集合

开发期间仅针对每次受影响模块做必要SQLite smoke和Reader sanity：建库、插入/读取与实际JOIN，`PRAGMA integrity_check`、`foreign_key_check`、有效unit幂等、坏unit不污染、跨档bundle被拒绝、普通GM不能取得Potential。**不要求每新增一张表做独立审核或Human签字**。完整候选交付后按OS集中验证与独立审核；交付后问题按OS最多两轮新证据/新修复措施处理。

## 4. 正式OS任务边界/前置依赖

沿用当前master backlog既有任务ID与依赖，不自行发明“平行永久主任务”：
- `WORLD-DATA-ARCH-01`：依赖`OS-BASELINE-01`，负责ER、实体身份/时间语义、全面原型架构与已决Human ADR。旧backlog文本中`season forks`的条目与新Human明确禁止跨档分叉的约束相冲突，以Human批准规则为准；应在正式任务包明确覆盖和修正。
- `NATIVE-ACCEPT-01`：依赖`OS-BASELINE-01`，做独立Native来源/身份/有效值核证；Codex作为工程验收Owner，可消费Gemini短包。
- `WORLD-DATA-SCHEMA-01`：依赖`WORLD-DATA-ARCH-01`，负责完整候选DDL、模型表/字段和值域/迁移。
- `WORLD-DATA-PROTOTYPE-01`：依赖`WORLD-DATA-SCHEMA-01`，交付真正可执行隔离fixture和查询。

**这些OS编号的正式执行须以派单时最新master、run/completion pointer、`allowed_changed_paths`、风险档、模型路由、独立审核、当前审批权限为准。** 不能因本交接文档把后续Schema/Prototype任务强行并到尚未完成依赖的ARCH任务；可由同一Codex工程Owner在满足依赖后连续推进。若现有OS过度碎片化阻断必要连续研发，应提交简明依赖调整的证据与建议供Human按实际受保护边界决定，而不是私自绕过。

**未授权行为**：不在本交接中开本地受保护路径、附着真实游戏进程/读取运行内存、修改游戏Save、生产迁移、push master或重写历史。用户批准架构方向不是这些动作的默认许可。

## 5. 首次面向Human的实质性报告

报告首个真实原型SQLite文件/DDL的相对路径、候选表总数和本次真正可运行表数、源证据矩阵状态、实际通过的JOIN/隔离/幂等测试、旧27表去向、Gemini有界缺口任务建议。若只是新增规划文档、没有可运行原型，不得报告原型开发已完成。一般结构修复由Codex在边界内继续，只有重大的已决ADR冲突、新的游戏本地DCR、Q10最终例外、master或生产动作时请Human决定。

**交接状态：READY_TO_PREPARE_OS_PACKET，但未派发，也无本地/Native实机执行证据。**
