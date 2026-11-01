# VAE 原生高级统计与指标加固开发循环日志 (Loop Increment Log)

**任务 ID**: `NBA2K22-VAE-NATIVE-METRIC-HARDENING-S0-20261101-001`  
**执行角色**: `execution` (Antigravity)  
**工程 Owner**: Codex (规划总线)  
**分支**: `task/nba2k22-vae-native-metric-hardening-s0-20261101`  
**派发基线 HEAD**: `1aba14c67f92881a650c5a67d04f8081f43fe74e`

---

## 一、迭代概览与循环脉络

| 循环轮次 | 目标任务包 | 涉及模块 / 文件 | 核心产出与验证结论 | 状态 |
| :--- | :--- | :--- | :--- | :--- |
| **Loop-01** | 环境初始化与 8 项物质性问题诊断 | `scratch/inspect_canonical38.py`<br>`scratch/inspect_plan.py` | 验证 PID 10404 运行态；确立 F01–F08 根因与数学验算事实。 | `COMPLETED` |
| **Loop-02** | H1/H2/H3/H5 代码加固 | `family_codec.py`<br>`query.py`<br>`live_world.py`<br>`owner_capture.py`<br>`schedule_reader.py` | 修复受限区间切片、单场去重、DNP 语义保留、球队激活球员过滤与代理指标更名。 | `COMPLETED` |
| **Loop-03** | H4 针对性单元测试加固 | `tests/test_advanced_metrics_and_boxes.py` | 新增 2 项测试用例，覆盖安全切片字典提取、跨单元单场去重与 DNP 保留；6/6 专项通过。 | `COMPLETED` |
| **Loop-04** | 全套回归与负向基准测试 | `tests/` 全套测试套件 (discover) | 运行全部 307 项测试（含历史 305 项 + 本轮 2 项），耗时 143.1s，0 错误 0 失败通过。 | `COMPLETED` |
| **Loop-05** | 交付物生成与 S0 基线就绪度闭环 | `02_证据/`<br>`06_执行/`<br>`07_测试执行/`<br>`08_结论/` | 输出完整的核实对齐报告、38 项覆盖度、数据源矩阵及 S0 Pilot 就绪度报告。 | `COMPLETED` |

---

## 二、各轮次详细实施与技术决策

### Loop-01：环境初始化与问题根因诊断
1. **进程态核查**：确认目标游戏进程 `NBA2K22.exe` 处于持续运行中（PID 10404，基址 `0x140000000`）。
2. **规范主键核验 (F01)**：通过 `git show c812042e:metric_native_first_requirements.json` 导出 Stage02 M3 的 38 项 Canonical ID，对比发现上轮交付仅有 14 项匹配，确立“必须 100% 恢复规范 ID，额外发现放入别名表”的原则。
3. **数学验算对账 (F03)**：
   - 样本 A（22 分用例）：算得 GameScore 为 17.50，不是 21.10。
   - 样本 B（27 分真实比赛）：算得 GameScore 为 21.10。
   - 查明系上轮报告摘要文案错位导致，两套数据均有独立事实来源。
4. **受限区间防护 (F08)**：查明 `RESTRICTED_PLAYER_RANGES = ((785, 786), (880, 882), (930, 931), (1089, 1090))`，确定高级统计安全读取区间为 `((544, 552), (580, 620), (768, 772), (780, 785))`，两者严格互斥。

### Loop-02：原生代码加固
1. **`family_codec.py`**：
   - 引入常量 `ADVANCED_METRICS_RANGES` 并加入硬断言校验。
   - 重构 `extract_player_advanced_metrics`，既支持 1264 字节安全提取，也支持传入安全切片字典。
2. **`query.py`**：
   - `player_game_log` 引入 CTE 窗口函数 `ROW_NUMBER() OVER (PARTITION BY b.game_id ORDER BY u.observed_at DESC, u.unit_id DESC)` 进行最新单元去重。
   - 增加 DNP / NULL 识别与保护，禁止无条件将 `None` 强转为 `0`。
   - 重命名单场 GameScore 为 `game_score_box_derived`，并诚实说明原生数组未入库。
   - `player_advanced_metrics` 增加 `season_id` 限定与时效排序；将 Touches 代理公式改名为 `EXPERIMENTAL_POSSESSION_LOAD_INDEX`，原生触球置 `None`。
   - `team_advanced_metrics` 增加赛季过滤及跨采集单元去重。
3. **`live_world.py` / `owner_capture.py` / `schedule_reader.py`**：
   - 统一使用 `[p for p in team_players if p.get('in_use', 1)]` 进行数据累加。
   - 动态累加激活球员的实际出场分钟数作为 `minutes_raw`。

### Loop-03：针对性单元测试加固
1. 修改 `test_advanced_metrics_and_boxes.py`：
   - 更新旧有用例断言，匹配更名后的 `game_score_box_derived` 与 `experimental_possession_load_index`。
   - 新增 `test_bounded_safe_intervals_and_dict_extraction`：测试安全区间互斥性与字典切片提取。
   - 新增 `test_game_log_deduplication_and_dnp_semantics`：测试多次采集单元去重及 DNP 球员 NULL 语义保留。
2. 运行结果：`Ran 6 tests in 2.163s, OK`。

### Loop-04：全套回归与负向基准测试
1. 执行 `python -m unittest discover -s 08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype/tests`。
2. 运行结果：`Ran 307 tests in 143.137s, OK`。全部 307 个测试用例全部通过，零失败、零回归。

### Loop-05：基线准备与 S0 数据就绪度
1. 依照 Human 确定的原则（以正常游玩数据记录为主，不频繁进行专门比赛实验），以 **Calendar Sim** 为基准。
2. 对 M5 的 3 个 Pilot 组进行 G1（数据入库门）与 G2（效果验证门）分级评估：
   - Pilot 1 (Shot+Touches+Coach): G1 `READY`, G2 `PARTIAL` -> Overall `S0_READY`
   - Pilot 2 (Tempo+POE+Rotation): G1 `READY`, G2 `PARTIAL` -> Overall `S0_READY`
   - Pilot 3 (HelpDefense+Defense POE): G1 `PARTIAL`, G2 `PARTIAL` -> Overall `S0_PARTIAL`
3. 严格遵守只读约束：本阶段零游戏内存写入、零存档篡改、零参数调整。
