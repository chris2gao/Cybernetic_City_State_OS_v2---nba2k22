# WORLD-DATA-ARCH-01
## NBA2K22平行篮球世界：概念数据模型、存档隔离、实体身份与历史事实架构

**建议执行：Codex GPT-6 Astra**

**风险等级候选：T2_semantic，最终以OS实际Preflight为准**

**项目仓库：**

`https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22`

**业务目录：**

`08_Domain_Applications/Antigravity_GM_Engine/`

**任务目标：**

为NBA2K22平行篮球世界建立完整、严谨、可扩展的数据概念架构与领域逻辑模型，为下一阶段关系数据库设计、统一原生采集系统、长期历史记录和GM/Coach/Player独立模型提供可靠的数据结构基础。

本任务只完成架构设计和规范文档，不执行生产数据库迁移。

---

## 一、先初始化OS并恢复项目上下文

读取当前远端`master`的精确SHA。

已知2026-10-22基准：

`407e2134bd2f595477099b2c6e3484c818059fd9`

执行时必须重新确认，不直接沿用历史SHA。

按OS规范读取：

- 根`AGENT_WORKING_DISCIPLINE.md`和`AGENTS.md`
- `01_os/README.md`
- `01_os/开发入口与单窗口任务规范_v1.md`
- `08_Domain_Applications/AGENTS.md`及`domain.yml`
- OS的Model Routing、任务编排、Minimum Work Unit及受控验证契约

随后读取以下NBA2K22业务文档：

- `docs/development/NBA2K22_PROJECT_DEVELOPMENT_BASELINE_V1.md`
- `docs/development/NBA2K22_PLANNING_MODEL_ENTRY_V1.md`
- `docs/development/NBA2K22_OS_TASK_BACKLOG_V1.json`
- `docs/development/PARALLEL_BASKETBALL_WORLD_DATA_ARCHITECTURE_V2.md`
- `docs/PROJECT_INTENT_AND_MODEL_DEVELOPMENT_BOUNDARIES.md`
- `docs/development/PROJECT_CAPABILITY_AND_DELIVERY_LEDGER_V1.json`

进一步按需查阅：

- `database/schema.sql`
- `src/gm_state_io/`
- `src/gm_data_access/`
- `src/source_extensions.py`
- `research/native_access/AG_NATIVE_01C/`
- `research/native_access/AG_NATIVE_01D/`
- DEV14与FINAL-CODEX相关审计资料

不要机械读取整个仓库，尽可能通过现有知识总账定位相关证据。

根据OS规范建立独立Task Packet、分支、验证计划和Run证据。

建议分支：

`task/world-data-arch-01`

---

## 二、玩家已经确定的存档业务规则

**这部分是已经确定的产品需求，不允许重新解释。**

### 1. 每个游戏存档都是独立世界

NBA2K22不同游戏存档：

- 完全独立；
- 数据相互隔离；
- 各自拥有连续发展的赛季和历史；
- 不存在存档之间的世界线分叉；
- 不存在跨存档合并；
- 不存在存档间历史或人物记忆继承。

存档A与存档B即使同时处于2021–2022赛季，拥有相同的球员姓名、原生PlayerID或GameID，也不能混淆。

**严禁开发世界线分叉树、父子世界关系、存档合并与冲突解决等不属于本项目的机制。**

### 2. 游戏推进不产生新世界

同一个存档从2021–2022赛季推进到2035–2036赛季，始终是同一个连续的篮球世界。

球员成长、退役、交易、选秀和比赛记录都属于该存档的连续历史。

### 3. 技术代际不等于世界线分叉

当前DEV14包含：

- save_id
- save_instance_id
- generation_id

必须研究这些字段的真实工程作用。

其中generation用于现有的技术重置、隔离和生命周期安全处理，不意味着游戏出现新的分叉世界。

允许保留真正必要的技术标识，但不能新增不需要的分叉业务。

如果新概念模型认为`world_id`与`save_instance_id`可能重复，应评估是否确实需要两个独立身份，不要为了架构复杂而制造冗余。

### 4. 历史选秀模板不等于游戏球员

项目会循环使用1984–2020年历史选秀球员资料。

同一个历史选秀模板可能在不同独立存档中被使用。

但这些实际出现在各存档中的游戏球员拥有各自独立的职业生涯。

静态模板资料可以复用；实际比赛、球员状态、角色记忆和生涯统计必须严格存档隔离。

---

## 三、建立完整篮球世界的领域概念模型

不要简单根据现有SQLite表反推架构。

首先从NBA2K22游戏对象和长期产品目标出发建立领域划分。

至少研究以下领域：

### A. 游戏世界与时间

- GameSave / SaveInstance
- Season
- SeasonPhase
- GameCalendar
- ObservationTime
- CaptureBatch

### B. 球队与球员身份

- Franchise / Team
- TeamSeason
- Player
- PlayerIncarnation
- DraftTemplate
- Staff / Coach

### C. 球队经营与资产

- RosterMembership
- Contract
- Salary
- WaivedSalary
- DraftPick
- TeamFinance
- Trade
- Signing
- StaffEmployment

### D. 比赛与统计

- Game
- TeamGameResult
- PlayerGameStatline
- BoxScore
- SeasonTotals
- CareerHistory
- RecordBook
- Awards

### E. 球员和教练动态状态

- PlayerAttributes
- Tendencies
- Badges
- Injury
- Fatigue
- Morale
- Training
- CoachSettings
- Playbook
- TacticalConfiguration

### F. 原生数据证据

- NativeObject
- NativeIdentityMapping
- CaptureObservation
- DecoderVersion
- SourceManifest
- DataQualityReport

### G. 独立AI参与者与受控执行

- GM角色
- Coach角色
- Player角色
- AgentObservation
- AgentDecision
- Approval
- ExecutionReceipt
- GameReadback

这里列出的是概念对象候选，不意味着每一个名称必须成为独立数据库表。

应通过实体属性、关系基数、生命周期和实际需求判断最终结构。

---

## 四、建立稳定身份模型

重点设计：

1. 游戏存档身份。
2. 不同存档之间的完全隔离。
3. 球队长期身份与某赛季球队状态。
4. 球员真实游戏实例与历史选秀模板。
5. 单场比赛的稳定业务身份。
6. 球员跨球队、跨赛季的职业生涯关联。
7. 原生PlayerID、GameID及Slot索引的适用范围。
8. 技术generation与正常赛季演化的关系。
9. 数据采集批次与实际篮球世界实体身份之间的区别。

必须明确：

- 哪些ID来自游戏；
- 哪些ID由外挂生成；
- 哪些ID只在一个存档有效；
- 哪些ID只在一个采集批次有效；
- 哪些关系已经有原生证据；
- 哪些关系仍然待验证。

**不得仅凭姓名、数组索引、内存指针或没有证据的原生ID全局唯一假设，直接关联跨赛季球员或比赛。**

---

## 五、区分不同类型的数据及其生命周期

明确建立下列数据的语义边界：

**1. 事件事实**

已经发生的比赛、交易、签约、选秀、奖项等。

必须具备稳定身份、实际发生时间、来源和历史保留规则。

**2. 状态观察**

某一时刻的球员能力、阵容、合同、财务、伤病及教练设置等。

同一个对象在不同时间有不同状态。

不能将这些状态强行写进比赛事件。

**3. 原生累计统计**

游戏原生Season Stats、生涯历史累计等。

它们是原生观察，不一定等于我们曾经完整收集了所有单场事件。

**4. 派生统计**

TS%、eFG%、最近10场表现、胜负切片等。

必须记录公式、数据范围和实际来源。

**5. AI分析与决策**

GM、Coach、Player对游戏事实的判断、意愿和行动。

它们不是游戏原生事实，不能反向污染原生数据库。

还需要区别：

- 游戏内时间；
- 实际采集时间；
- 数据发布批次；
- 状态生效时点；
- 数据订正与版本。

---

## 六、原生数据证据与未知字段

以AG-NATIVE-01C/01D为重点样本，考虑：

- SEASON Game记录；
- Player BoxScore StatLine；
- PLAYER_STATS；
- 球员生涯索引；
- TEAM_MATCHUP_MATRIX；
- PLAYER/TEAM对象；
- 已有教练与训练设置。

注意这些结构仍有未完成的原生工程验收。

对于Native资料，必须区分：

- 已有原生证据；
- 只有离线Fixture证明；
- 经UI交叉验证；
- 通过公式推导；
- 静态候选；
- 未知。

本任务可以依据真实样本设计对象关系，但不得宣布AG-NATIVE-01D已完成全部游戏原生验证。

特别保留后续Codex需要核实的GameID作用域、StatBank记录边界和PlayerID稳定性等问题。

---

## 七、明确旧数据库的重构方向

现有：

- `league_state.sqlite`
- `player_pool.sqlite`
- 月度统计表
- 当前球员表
- 赛季统计表
- 批次发布系统
- DEV14存档控制系统

均可作为第一代工程资产重新评估。

本任务需要识别：

1. 哪些旧表混淆了身份、状态和历史；
2. 哪些原有字段可以迁移；
3. 哪些历史数据没有足够证据，必须保留未知；
4. 哪些已验证安全机制应当保留；
5. 哪些接口需要由下一代数据平台替换；
6. 哪些原有表可以被正式淘汰。

但不要在本任务实施正式DDL迁移。

SQLite仍是优先考虑的数据库引擎，实际物理库数量和拆分方案留给后续`WORLD-DATA-SCHEMA-01`评估。

---

## 八、必须完成的反例验证

需要通过具体的数据关系示例证明概念模型能够处理：

**场景1：两个独立存档**

两个存档都存在Stephen Curry，甚至可能有相同的原生PlayerID和赛季年份。

验证两个球员实例、比赛记录和生涯历史不会发生交叉关联。

**场景2：同一存档连续多个赛季**

球员从2021–22持续成长到2030–31，中间交易多次。

验证长期人物身份不丢失，赛季球队归属和比赛记录仍然准确。

**场景3：重复采集同一场比赛**

同一场比赛先后被采集两次。

验证这不意味着发生了两场比赛，且原始观察与订正能够正确表达。

**场景4：单场统计与赛季累计不一致**

不能自动伪造缺失比赛或修改原生数据来消除差异。

应保留数据质量问题和待验来源。

**场景5：球员隐藏属性**

普通GM查询不应看到Potential等禁止公开的字段。

即使底层原生记录存在这些字节，也不能通过通用查询接口泄露。

**场景6：同一历史选秀模板进入不同存档**

两个存档分别使用同一历史球员模板。

验证实际球员身份、生涯发展和人格记忆相互独立。

这些是概念架构测试，不需要运行真实NBA2K22进程。

---

## 九、正式交付文档

所有文档放入：

`08_Domain_Applications/Antigravity_GM_Engine/docs/development/`

### 必交成果

**A. 世界领域数据模型**

`WORLD_DATA_DOMAIN_MODEL_V1.md`

包含领域划分、实体定义、关系基数、生命周期、Mermaid ER图，以及为何选择这些实体的理由。

**B. 存档、身份与时间ADR**

`WORLD_DATA_IDENTITY_AND_TIME_ADR_V1.md`

明确独立存档隔离、球员与球队长期身份、比赛身份、历史时间和技术代际，特别记录“不存在存档分叉”。

**C. 机器可读实体字典**

`WORLD_DATA_ENTITY_CATALOG_V1.json`

包含每个概念对象的ID、领域、主要属性、关系、身份作用域、生命周期、已证来源及UNKNOWN字段。

**D. 数据真实性与质量契约**

`WORLD_DATA_SOURCE_AND_QUALITY_CONTRACT_V1.md`

明确原生证据、状态观察、历史事件、累计统计、派生计算、数据缺失、潜力脱敏和可信度标签。

**E. 旧系统重构及下一任务交接**

`WORLD_DATA_LEGACY_IMPACT_AND_SCHEMA_HANDOFF_V1.md`

列出旧数据库与新领域模型的映射、可以迁移的能力、结构性缺口，以及`WORLD-DATA-SCHEMA-01`应当接收的具体输入与未决问题。

### 需要同步修订

检查并修订以下旧架构文档中的错误存档分叉表述：

- `PARALLEL_BASKETBALL_WORLD_DATA_ARCHITECTURE_V2.md`
- `NBA2K22_OS_TASK_BACKLOG_V1.json`
- `OS_GOVERNED_NEXT_STAGE_ROADMAP_20261022.md`

确有必要时同步更新文档权威索引和项目开发基线。

**不要修改历史V1审计文档来掩盖过去的错误。应保留历史，使用新ADR明确修订。**

---

## 十、任务边界

本任务允许：

- 分析已有业务代码、数据库Schema和研究证据；
- 设计完整数据领域与关系；
- 提出架构替代方案及设计决定；
- 创建Mermaid图和JSON实体字典；
- 设计数据不变量与反例；
- 修订本任务直接涉及的架构文档；
- 执行文档、JSON和关系一致性检查；
- 按OS任务机制创建与提交运行证据。

本任务禁止：

- 修改篮球游戏进程；
- 修改游戏存档；
- 运行真实赛季推进；
- 修改原生球员能力；
- 正式迁移SQLite；
- 删除旧生产数据库；
- 开发完整新采集器；
- 编写并应用生产DDL；
- 开发GM、Coach或Player人格；
- 将原生候选字段冒充已经验收；
- 修改共享OS核心；
- 未经Human批准提交master。

DCR远程本地访问必须另行获得玩家明确授权。开发模型若通过自身已授权工作环境工作，应遵守OS的本地范围和发布规则，不得把本任务当作额外DCR授权。

---

## 十一、验收标准

本任务不能只靠架构文档字数验收。

必须满足：

1. 概念实体定义完整，关系基数清楚。
2. 游戏存档严格独立，**不存在分叉业务模型**。
3. 可以解释球员跨赛季、跨球队的连续职业生涯。
4. 原生ID与业务ID的作用域明确，未知部分保留验证条件。
5. 游戏事件、状态、累计统计、派生数据与AI决策被严格区分。
6. 六个反例场景均有明确处理结果。
7. 原有DEV14身份和生命周期机制得到正确理解，而不是全部推倒重来。
8. 已验证能力可以迁移到新架构，旧Schema不构成永久设计限制。
9. 不将研究成果升级为生产事实。
10. 完整记录下一阶段Schema设计所需的输入、约束和未证问题。
11. JSON、文档引用、ER定义、任务ID及OS变更范围检查通过。
12. 独立任务分支已提交，包含真实OS测试及完成指针，等待独立审核。

如果发现新的重大产品语义问题，记录候选方案与依据，向玩家提交明确的选择建议。

不因一般字段命名或文档组织细节反复请求确认。

---

## 十二、完成与交接

建议在同一个Codex架构设计窗口内完成研究、建模、方案比较、反例验证、文档修订及任务分支提交。

不要把每个实体或每张ER图拆成独立任务。

任务完成后：

1. 按OS要求运行验证；
2. 确认工作区与文件变更范围；
3. 提交独立任务分支；
4. 推送并回读远端完整SHA；
5. 生成Completion Pointer；
6. 将当前Backlog中本任务状态更新为实际候选状态；
7. 向玩家提交架构决策摘要；
8. 停止执行，等待独立审核与玩家接收。

不得自动启动`WORLD-DATA-SCHEMA-01`或生产数据库重构。

**最终目标：让下一位数据库开发模型无需重新讨论游戏世界的基本实体和身份，就能够依据本轮获审架构开始设计规范的SQLite逻辑与物理Schema。**