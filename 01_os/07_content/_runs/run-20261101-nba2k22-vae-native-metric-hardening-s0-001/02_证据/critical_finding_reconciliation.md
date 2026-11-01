# 关键问题核实与整改对齐报告 (Critical Finding Reconciliation)

## 一、概述与整改背景

在本轮任务 `NBA2K22-VAE-NATIVE-METRIC-HARDENING-S0-20261101-001` 中，执行岗位针对规划总线（Engineering Owner: Codex）提出的 8 项关键物质性发现（F01–F08）进行了详尽的代码审查、独立数学核算与工程整改。

整改原则：
1. **真实证据第一**：严格区分 Native 引擎原生存储、单场 Box 推导、UI 动态计算以及暂未发现原生存储的统计量，杜绝任何“过度标注”或“将代理指标伪装成原生指标”。
2. **规范主键一致性**：完整保留 Stage02 M3/M4 已审核批准的全部 38 项指标 Canonical ID，额外发现的原生指标独立放入别名与清单映射表。
3. **安全边界与数据完整性**：绝对禁止读取或探测潜在值受限区间 `RESTRICTED_PLAYER_RANGES`；在逐场查询中严格去重、保留 DNP/NULL 语义，并在球队单场统计中按激活球员 (`in_use == 1`) 计算分钟数与总计。

---

## 二、F01–F08 逐项核实与整改对齐详情

### F01_METRIC_ID_DRIFT（38 项指标需求 ID 漂移）
- **核查事实**：
  上轮交付将 Stage02 M3 已审核确定的 38 项规范 ID 替换为了自行命名的 38 项 ID（仅 14 项完全匹配，24 项规范 ID 缺失，引入了 24 项不同名称的 ID）。
- **整改措施**：
  1. 完整恢复 `c812042e:metric_native_first_requirements.json` 中定义的全部 38 项 Canonical Metric ID，无任何删改或名称替换。
  2. 上轮额外发现的原生统计项（如 `PLAYER_GAME_SCORE_HISTORY`、`PLAYER_PER_RANKINGS`、`TEAM_POSSESSIONS`、`TEAM_LARGEST_LEAD` 等）移入 `06_执行/accepted38_metric_coverage.json` 的 `discovered_native_metric_aliases` 独立映射区，保持主键引用完整性。
- **状态**：`RESOLVED` (已闭环)

---

### F02_NATIVE_GAMESCORE_NOT_UNIFIED（Native GameScore 未打通统一链路）
- **核查事实**：
  `family_codec.extract_player_advanced_metrics(raw)` 能够解析 PLAYERDATA 偏移 580 处的 5 场原生 GameScore float32 数组，但现有 `refresh_world` 尚未将其持久化入 SQLite 数据库；而 `query.player_game_log` 是基于单场 `player_game_boxes` 重新计算 Hollinger GameScore，却在摘要中被误标为 Native 采集链路打通。
- **整改措施**：
  1. 在 `query.player_game_log` 中明确将单场 Box 计算结果重命名为 `game_score_box_derived`（同时保留 `game_score` 兼容键），溯源标记明确为 `HOLLINGER_GAMESCORE_BOX_DERIVED; computed from single-game boxline counting stats`。
  2. 将 PLAYERDATA 偏移 580 的原生 GameScore 历史数组真实状态标记为 `RESEARCH_CANDIDATE_ONLY; NOT_INTEGRATED_INTO_DB`，诚实说明当前数据已能通过安全切片读取，但未写入主数据库表。
- **状态**：`RESOLVED` (已闭环)

---

### F03_GAMESCORE_SAMPLE_CONFLICT（GameScore 样本数值冲突与独立验算）
- **核查事实**：
  在上轮交付摘要中记录了一组统计数据：“22 PTS, 8/17 FGM/FGA, 2/4 3PM/3PA, 4/4 FTM/FTA, 1 OREB, 5 DREB, 5 AST, 1 STL, 1 BLK, 2 TOV, 3 PF”，并声称其 Hollinger GameScore 为 21.10；而底层 dossier 附带的 Joel Embiid 真实对波士顿比赛统计则为：“27 PTS, 10/23 FGM/FGA, 4/7 3PM/3PA, 3/3 FTM/FTA, 4 OREB, 9 DREB, 4 AST, 1 STL, 3 BLK, 4 TOV, 3 PF”，公式计算亦为 21.10。
- **独立数学核算与公式对账**：
  Hollinger GameScore 标准公式为：
  $$\text{GameScore} = \text{PTS} + 0.4 \times \text{FGM} - 0.7 \times \text{FGA} - 0.4 \times (\text{FTA} - \text{FTM}) + 0.7 \times \text{OREB} + 0.3 \times \text{DREB} + \text{STL} + 0.7 \times \text{AST} + 0.7 \times \text{BLK} - 0.4 \times \text{PF} - \text{TOV}$$

  **样本 A（测试夹具中的 22 分样本）**：
  - PTS = 22
  - FGM = 8, FGA = 17
  - FTM = 4, FTA = 4 (FTA - FTM = 0)
  - OREB = 1, DREB = 5
  - AST = 5, STL = 1, BLK = 1
  - PF = 3, TOV = 2
  - 代入公式计算：
    $$\text{GameScore}_A = 22 + 0.4 \times 8 - 0.7 \times 17 - 0.4 \times 0 + 0.7 \times 1 + 0.3 \times 5 + 1.0 + 0.7 \times 5 + 0.7 \times 1 - 0.4 \times 3 - 2$$
    $$= 22 + 3.2 - 11.9 - 0 + 0.7 + 1.5 + 1.0 + 3.5 + 0.7 - 1.2 - 2 = 17.50$$
  - **结论 A**：样本 A 的真实 GameScore 为 **17.50**，绝不可能等于 21.10。

  **样本 B（Dossier 实机采集 Joel Embiid 真实比赛样本）**：
  - PTS = 27
  - FGM = 10, FGA = 23
  - FTM = 3, FTA = 3 (FTA - FTM = 0)
  - OREB = 4, DREB = 9
  - AST = 4, STL = 1, BLK = 3
  - PF = 3, TOV = 4
  - 代入公式计算：
    $$\text{GameScore}_B = 27 + 0.4 \times 10 - 0.7 \times 23 - 0.4 \times 0 + 0.7 \times 4 + 0.3 \times 9 + 1.0 + 0.7 \times 4 + 0.7 \times 3 - 0.4 \times 3 - 4$$
    $$= 27 + 4.0 - 16.1 - 0.0 + 2.8 + 2.7 + 1.0 + 2.8 + 2.1 - 1.2 - 4.0 = 21.10$$
  - **结论 B**：样本 B 的真实 GameScore 恰好精确等于 **21.10**。
- **根因分析**：
  上轮报告编写时，报告摘要误将测试用例中的样本 A 计数数据（22 分）与实机采集的样本 B 算得结果（21.10）混排在同一段落，造成了表述矛盾。本轮通过独立数学验算彻底确认两套数据的独立性与准确值。
- **状态**：`RESOLVED` (已闭环)

---

### F04_READER_READINESS_OVERPROMOTION（Reader 就绪度过度晋级）
- **核查事实**：
  上轮将 38 项指标中的 31 项笼统标记为 `REAL_NATIVE_READABLE`，混淆了原生静态内存、实机读回、夹具测试、派生率、UI 动态计算与数据库查询可用性等不同维度。
- **整改措施**：
  全面废除单一维度的 `REAL_NATIVE_READABLE` 标签，为所有 38 项指标建立 6 维评级矩阵：
  1. `GAME_NATIVE_SOURCE`：内存槽位/引擎存储来源
  2. `LIVE_READ`：实机安全读取能力
  3. `READER_CODE`：Reader 模块实现状态
  4. `REFRESH_INGEST`：入库状态
  5. `QUERY`：统一查询层暴露状态
  6. `DATA_GRAIN`：数据粒度
- **状态**：`RESOLVED` (已闭环)

---

### F05_TOUCHES_PROXY_MISLABEL（Touches 代理指标误标）
- **核查事实**：
  上轮使用估算公式 `FGA + 0.44 * FTA + TOV + 0.33 * AST` 作为 Touches 的代理，并将其直接对齐为 `MET_TOUCHES_NATIVE`。由于静态内存中目前并没有发现逐场触球次数计数器，推导公式绝不能冒充原生真实触球。
- **整改措施**：
  1. 将推导公式彻底重命名为 `EXPERIMENTAL_POSSESSION_LOAD_INDEX`（实验性球权负荷指数）。
  2. 在 `query.player_advanced_metrics` 中，将 `touches_native` 显式置为 `None`，并在溯源中明确声明：
     `'met_touches_native': 'NO_NATIVE_SOURCE_FOUND; Touches not stored in static memory tables'`。
  3. 严禁将该代理指标用于正式 GM 决策或参数校准。
- **状态**：`RESOLVED` (已闭环)

---

### F06_SNAPSHOT_QUERY_SEMANTICS（快照查询语义与去重完善）
- **核查事实**：
  1. `player_game_log` 直接 JOIN `capture_units`，当同一场比赛被多次采集时会出现重复记录。
  2. 统计缺失或未出场（DNP）被无条件转为 0，掩盖了真实比赛状态。
  3. `player_advanced_metrics` 仅用 `ORDER BY total_id DESC`，未对赛季/阶段/时间做限定。
  4. `team_advanced_metrics` 的单场均值未过滤赛季，也未对多次采集单元去重。
- **整改措施**：
  1. 在 `player_game_log` 中引入窗口函数 `ROW_NUMBER() OVER (PARTITION BY b.game_id ORDER BY u.observed_at DESC, u.unit_id DESC)`，确保同一场比赛跨采集单元只保留最新观测。
  2. 严禁无条件将 `None` 转换为 0；对 DNP 球员保留 `points=None, fg_pct=None, game_score=None`，并显式标记 `is_dnp=True`。
  3. 在 `player_advanced_metrics` 和 `team_advanced_metrics` 中，通过 JOIN `capture_units` 增加赛季过滤及 `is_final DESC, observed_at DESC` 严格时效排序。
  4. 在 `team_advanced_metrics` 的单场 Box 均值计算中，增加 `games.season_id` 过滤及最新采集单元去重 CTE。
- **状态**：`RESOLVED` (已闭环)

---

### F07_TEAM_BOX_COMPLETENESS（球队 Box 完整性与动态分钟数计算）
- **核查事实**：
  上轮在汇总球队单场数据时，无条件累加了所有球员列表（未检查 `in_use == 1`），且死板硬编码 `minutes_raw = 240 + 25 * OT`，未能反映非标准节长或实际出场分钟数。
- **整改措施**：
  1. 在 `live_world.py`、`owner_capture.py` 和 `schedule_reader.py` 中，统一过滤 `[p for p in full[side+'_players'] if p.get('in_use', 1)]`。
  2. 动态累加激活球员的实际出场分钟数：
     ```python
     active_mins = sum(p.get('minutes', 0) for p in team_players)
     minutes_raw = active_mins if active_mins > 0 else (240 + full.get('overtime_count', 0) * 25)
     ```
  3. 保持单场得分与 Game Header 得分一致，杜绝不激活席位脏数据污染。
- **状态**：`RESOLVED` (已闭环)

---

### F08_PRIVATE_PLAYER_INTERVAL（受限球员区间隔离与安全切片）
- **核查事实**：
  `extract_player_advanced_metrics` 原先要求传入完整的 1264 字节 PLAYERDATA，如果用于实机实时读取，可能触及受保护的潜力与隐藏区间 `RESTRICTED_PLAYER_RANGES = ((785, 786), (880, 882), (930, 931), (1089, 1090))`。
- **整改措施**：
  1. 显式定义高级统计安全区间：
     `ADVANCED_METRICS_RANGES = ((544, 552), (580, 620), (768, 772), (780, 785))`
  2. 增加模块级断言，物理证明这四个区间与受限区间完全不相交：
     ```python
     assert not any(a < hi and lo < b for a, b in ADVANCED_METRICS_RANGES for lo, hi in RESTRICTED_PLAYER_RANGES)
     ```
  3. 重构 `extract_player_advanced_metrics`，使其既支持 1264 字节的安全读取，也原生支持传入仅包含安全切片的字典结构（`dict` of bounded slices），彻底解除对完整结构体读取的依赖。
- **状态**：`RESOLVED` (已闭环)
