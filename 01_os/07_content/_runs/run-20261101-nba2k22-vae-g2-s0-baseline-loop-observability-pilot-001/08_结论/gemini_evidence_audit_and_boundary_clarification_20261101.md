# Gemini 实机证据核查与实验边界澄清报告

- **任务 ID**: `NBA2K22-VAE-G2-S0-BASELINE-LOOP-OBSERVABILITY-20261101-001`
- **对应提交**: `c2d6c3b0d87efcd1869c5eb3c6ece5b74d7ce04d`
- **核查响应文件**: `08_结论/human_clarification_no_new_calendar_games_20261101.md`
- **OS 角色**: `execution` (Gemini 2.5 Pro)
- **状态维护**: **`EXTERNAL_EVIDENCE_PENDING`** (严格挂起，等待 Human 明确授权与操作通知)

---

## 一、专项测试与回归测试具体执行核查

在提交 `ca06f053` 中，共记录了 5 项专项测试（来自 `test_s0_pilot_reconciliation.py`）与 6 项回归测试（来自 `test_advanced_metrics_and_boxes.py`）。经逐行核对源码与执行回执，具体执行内容、断言类型及数据源如下：

### 1. 5 项专项测试 (`test_s0_pilot_reconciliation.py`)

| 测试方法名称 | 测试对象 | 断言类型 | 是否读取 `world-v24.sqlite` | 是否被跳过 (Skip) | 真实执行说明 |
| :--- | :--- | :--- | :---: | :---: | :--- |
| `test_score_discrepancy_scope_structure_and_counts` | `score_discrepancy_scope.json` | **纯 JSON 结构与常量断言** | **否** | **未跳过** | 断言 JSON 文件中的 238 场总数、222 场完全一致、16 场差异、4 场 $\le 3$、6 场 $\le 4$、10 场 $> 4$ 以及 5 场加时、11 场奇才截断分类。 |
| `test_score_discrepancy_against_sqlite` | `world-v24.sqlite` & `score_discrepancy_scope.json` | **真实本地 SQL 查询比对** | **是** | **未跳过** (实际执行 16 次查询) | 遍历 16 个差异案例，在本地 `world-v24.sqlite` 真实执行 `SELECT period_points FROM game_period_scores` 与 `SELECT points FROM player_game_boxes`，逐场重新计算差值并断言与 JSON 记录的 `max_team_delta` 完全一致。代码包含 `if not DB_PATH.exists(): self.skipTest(...)`，但运行环境数据库路径确凿存在，回执明确记录 `skipped: 0`，测试真实完整执行。 |
| `test_s0_pilot_selection_and_sample_adequacy` | `s0_selected_pilot_baseline_and_sources.json` | **纯 JSON 结构与常量断言** | **否** | **未跳过** | 断言选定 Pilot 为 `PILOT_01_SHOT_TOUCHES`，目标为 Lillard（`player:native:2459`），样本量为 16 场（$\ge 10$），`all_games_score_conserved == True`。 |
| `test_s0_pilot_game_isolation_and_metric_distributions` | `s0_selected_pilot_baseline_and_sources.json` | **纯 JSON 内存数据与统计断言** | **否** | **未跳过** | 校验 JSON 中 16 场比赛 ID 与 16 场差异比赛零重叠，且每场比分严格守恒；断言 FGA（19.875）、PTS（29.562）、MIN（36.375）、TS%（0.663）等预计算分布均值。 |
| `test_rea_g2_preflight_contract` | `one_pilot_g2_rea_preflight.json` | **纯 JSON 契约与边界断言** | **否** | **未跳过** | 校验原生偏移为 `0x458`，当前值为 95，拟议修改为 80，明确断言只读边界 `authorization_status == NOT_AUTHORIZED_IN_EXECUTION_RUN` 和 `game_mutation_policy == STRICT_READ_ONLY`。 |

### 2. 6 项回归测试 (`test_advanced_metrics_and_boxes.py`)

| 回归测试方法名称 | 测试对象 | 测试机制与数据源 | 是否读取 `world-v24.sqlite` |
| :--- | :--- | :--- | :---: |
| `test_decode_schedule_date_bitfield` | 日期位域解码函数 | 纯内存算术位移计算测试（Year/Month/Day bitmask） | **否** |
| `test_extract_player_advanced_metrics_decodes_per_and_gamescore` | 原生结构体解包函数 | 纯内存伪造 1264 字节 `bytearray` 结构体切片解包（`struct.pack_into`） | **否** |
| `test_team_game_boxes_all_26_columns_populated` | 球队单场 Box 提取管道 | 在 `setUp()` 中创建**临时临时目录 SQLite 数据库**，写入合成数据并验证 26 列 | **否** |
| `test_player_game_log_and_advanced_metrics_query` | 比赛日志与高阶视图查询 | 在临时 SQLite 数据库中插入合成单场 Box，查询 `player_game_log` 视图 | **否** |
| `test_bounded_safe_intervals_and_dict_extraction` | 字段安全字典区间 | 校验内部静态字典常量与边界范围 | **否** |
| `test_game_log_deduplication_and_dnp_semantics` | 去重 CTE 与 DNP 语义 | 在临时 SQLite 数据库中测试重复单场数据与 0 分钟 DNP 过滤逻辑 | **否** |

**结论**：上述 11 项测试中，只有 `test_score_discrepancy_against_sqlite` 真正连接并查询了历史 `world-v24.sqlite`；其余 10 项均为离线 JSON 断言、内存算法单测或临时数据库的合成测试。**绝无任何测试涉及真实游戏写入、日历推演或实机模拟效果验证。**

---

## 二、修改 Shot Tendency 后的原生数值读回证据核查

- **核查判定**：**`NOT_EXECUTED` (NONE)**。
- **事实依据**：
  1. 本次开发全流程严格遵守只读约束，未对 `NBA2K22.exe` 进程发送任何内存写入调用，未通过游戏 UI 修改设置，亦未调用任何 REA Setter 工具。
  2. 游戏中的真实 Shot Tendency 数值未发生任何修改。
  3. 因此，**不存在任何修改后的原生数值读回证据**（即不存在 `SETTING_CHANGE_POST_READBACK`）。
  4. 产物中记录的 `baseline_s0_value: 95` 仅源自历史抓取的静态快照表 `player_tendency_snapshots`（采集单元 `live-world:abffaed591a079206825b8fe`，时间戳 `2026-10-24T14:24:50`）。

---

## 三、修改设置后新生成的比赛 ID 与采集单元核查

- **核查判定**：**`NOT_EXECUTED` (NONE)**。
- **事实依据**：
  1. 本任务执行期间，未推进游戏日历，未启动模拟或比赛，亦未触发任何新的实机采集管道。
  2. 因此，**不存在任何修改设置后新生成的比赛 ID**（即不存在 `POST_INTERVENTION_GAME_ID`），亦**不存在任何新的赛后采集单元**（即不存在 `POST_INTERVENTION_CAPTURE_UNIT`）。
  3. 基线 JSON 中记录的 16 场比赛（Native Game ID 13 至 236）全部来自历史采集单元 `live-world:00606ee2a7703ad2322a4e3d`（时间戳 `2026-10-25T17:47:21`），属于任务开展前就已固化在存档数据库中的历史比赛。

---

## 四、原报告中 `READY` 的精确边界与范围澄清

- **原报告判定词**：`S0_BASELINE_READY` / `READY`。
- **精确作用边界**：
  - **涵盖范围**：仅代表**“S0 历史观测数据完整守恒”**以及**“G2 实验对比协议（假说、偏移、对照组、证伪条件）方案就绪”**。即：
    1. 历史 16 场日历模拟比赛被证明数据质量达标（$\ge 10$ 场、100% 节次与球员比分守恒、全勤无伤病）。
    2. G2 实验所需的原生结构体偏移（`0x458`）、只读边界及证伪标准设计完毕。
  - **绝不涵盖范围**：原报告的 `READY` **绝对不代表**设置修改已验证（`SETTING_CHANGE_VERIFIED`）、新比赛已生成（`NEW_POST_CHANGE_GAME_VERIFIED`）或机制效果已验证（`EFFECT_VERIFIED`）。
  - **对齐规范**：所有涉及实际设置修改、新比赛模拟和效果评价的阶段，真实状态严格属于 **`NOT_EXECUTED`**，依规保持在 **`EXTERNAL_EVIDENCE_PENDING`**。

---

## 五、Lillard 16 场 S0 比赛的历史属性与设置恒定性客观局限

1. **确认为历史比赛**：
   - 经对 `world-v24.sqlite` 原始记录核对，Lillard 的 16 场日历模拟比赛比赛日期为游戏内 `2021-10-20` 至 `2021-11-20`，其实际采集入库时间戳统一为 `2026-10-25T17:47:21Z`。确凿属于本任务启动前由 Human 预先模拟并捕获的历史数据。
2. **当前单点快照 95 的客观局限**：
   - 数据库中的 `shot_tendency_raw = 95` 源自采集单元 `live-world:abffaed591a079206825b8fe`（采集时间 `2026-10-24T14:24:50Z`），是一次**单时间点的全量快照**。
   - 2K 原生游戏引擎在单场赛后 Box 中并不持久化记录当时的倾向属性值。
   - 因此，**当前读到的快照值 95，不能在形式逻辑上独立证明历史 16 场比赛在进行模拟时，每一场的 Shot Tendency 都处于绝对恒定的 95**（不能完全排除该历史阶段是否存在未记录的手动调整、系统默认更新或士气微调）。它仅能作为当前最合理的历史基准参考候选，不能作为历史恒定性的铁证。

---

## 六、后续行动边界与挂起声明

1. **绝对禁止自主实机操作**：
   - 本工作窗口严禁执行任何游戏内存修改、设置写入、日历推演、后台轮询监听或自动化实机采集。
2. **保持 `EXTERNAL_EVIDENCE_PENDING`**：
   - 本任务的所有离线代码核验、测试分析和数据归因均已就绪且边界清晰。
   - 任务状态保持为 **`EXTERNAL_EVIDENCE_PENDING`**。
   - 后续任何涉及实机设置修改（Phase A）或新增日历模拟与赛后采集（Phase B），将完全处于等待状态，必须等待 Human 给出明确的授权指令与操作完成通知后，方可继续下游核验。
