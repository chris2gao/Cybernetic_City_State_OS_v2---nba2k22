# VAE 下一阶段技术规划与数据接口边界 · 2026-10-31

## 输入与证据状态
- Gemini REA固定候选 `b3e39f867364b4610fc57f5cc798c7ab33232eeb`，源报告称40/40离线测试；四机制成果、Graph及3个`PENDING_GAMEPLAY_VALIDATION`度量需求实际在云端。
- 机制图存在字段主键不一致：`COACH_DEFAULT_005`被描述为Tempo，但原REA档案`COACH_DEFAULT_014`是Tempo；`TENDENCY_NATIVE_002`被描述为Touches，但原档案是`TENDENCY_NATIVE_066`。目前图单测固定了错误常量，必须更正并加对照约束。
- `coach_pacing.py`计算`edx`但主输出用`round(offset*0.6)`，对宣称原样x86整数指令的结果有未闭合歧义；当前不能直接接GM/教练自动决定生产调参。旧角色模型、原生字节真实性同样需集中独立复核。
- 当前GPT外部研究 `9fa8fc51d408c1a34c35d65a3cd693a973824a37`处于SWEEP1 115/204，研究不断进展，独立于Gemini REA证据。
- Human确认：**新采集系统尚未开发，其业务数据需求确定，包括静态和动态游戏数据；物理表、事件日志和字段命名格式没有确定**。旧采集不作为新接口格式权威。不要使用Gemini`TELEMETRY_VALIDATION_CONTRACTS_V1.json`直接固定D3数据库设计。

## 决定的下一步（单个集成整改包 + 集中审核，而非拆碎）
**Gate 0: 集中审核（已派发）**
- 独立GPT审核任务`NBA2K22-VAE-MECHANISM-INTEGRATION-INDEPENDENT-REVIEW-20261031-001`，派单`3c378d05a42be50d7f105256d5bb978bd88eefa5`，固定源`b3e39f867364b4610fc57f5cc798c7ab33232eeb`。
- 范围：原生候选证据与程序集、字段ID映射、数值运算复现、图关系真实性、游戏效果边证据、fixture安全、遥测业务需求定位。不得改变来源或宣称实际游戏数据已见到。
- 审核先于新“可投产 Native模型”采纳。

**Gate 1: Gemini现有REA代码集中工程整改（审核后单包）**
- 修复主键映射，机制图必须从权威`field_id`目录构建或执行一致性校验，不手工发明同名字段ID；受版本/实体/模式限定。
- 可执行的Native数学模块严格分离`verified opcode`和`uncalibrated heuristic`，含整数负数与边界向量；无法证实则降级结论，不输出生产调参建议。
- 机制图边区分`Native读取/算法运算/候选消费者/未证明的比赛效果`，每条带来源SHA与证据等级；修复自引用测试依赖。
- 决策接口在缺实机来源、权限或关键信息时必须`NO_CHANGE / NEED_EVIDENCE`，可给建议但不得自发调用Setter。保留当前只读逆向成果，不改既有Reader/REA/D层共享核心。

**Gate 2: VAE逻辑数据与效果验证接口（同一个Gemini集成包，与D系列解耦）**
- 先定义**信息需求**而非物理格式：每个机制输出需收集的静态字段（存档、球队/球员、游戏模式、教练/倾向/角色/配置原值与版本）及动态数据（比赛/采集时间、个人/球队统计、轮换、训练/疲劳若实可读、设置前后事实）、身份关系、来源/新鲜度、可比条件。
- 将三个Telemetry条目作为`MetricRequirement`候选：FGA/36（可由FGA+上场时间推算，注明公式）、Pace/48（需足够回合构成数据，注明估算与原生差异）、Fatigue-rate（仅有赛末体能无法计算精确第四节下降率，记录MISSING，不可伪造）。
- 中间仅设计可重放逻辑接口：`MechanismEvidence`、`MetricRequirement`、`ObservationContext`、`BeforeAfterComparison`、`EvidenceEvaluation`、`KnowledgeRevision`作为**概念契约**，不是正式JSON/SQL/日志字段规范。
- 用Fixture/旧采集样例做分析引擎正确性测试和数据缺失、权限/归属、用户CPU、不同Normalize、3D与Calendar、季度和赛季口径混用拒绝案例。
- Data source实现只能作为未来D2/D3/D4 Adapter接口占位；新D系列完成字段/数据库后由其提供真实快照、历史和角色信息服务，不允许VAE自己替代构建平行数据库。
- 保存按字段`Action→Information→Field→Metric→Evidence`需求，交给D1需求映射；真实数据到位后映射适配，而非先固定数据格式。

**Gate 3: 集成验收与后续实证**
- Gemini在原有REA任务后续迭代中集中提交工程候选，不按每机制拆开发任务；另一个GPT新独立窗口一次集中审核。
- 原生程序运算正确、图关系证据完整与真实比赛改善效果分开验收；后者保持`PENDING_GAMEPLAY_VALIDATION`直至未来正常游玩时实际采集。
- GPT外部机制研究继续SWEEP并与REA按同一字段ID和来源版本交叉参考，不得以互联网资料冒认Native实证。
- 真实比赛反馈采用原User已确认的低频快照及重要操作后采集、历史只追加、不覆盖，比较数据缺失或统计口径不同返回`INCONCLUSIVE`。

## 分工与当前权限
VAE规划GPT：云端证据、规划、派单、合规与进度管理；独立GPT审核：固定SHA一次集中审核；Gemini Flash 3.8：本地REA与集成工程；GPT研究模型：外部资料循环；D系列未来团队：实际采集、存储与角色数据服务。Codex暂无额度。
不要求规划窗口连接本地；若下一工程阶段确实需要原生动态验证码与受保护操作，执行者提交具体动作、隔离测试存档、回退与验证场景，Human另行授权。没有本次授权的游戏或存档写入。
