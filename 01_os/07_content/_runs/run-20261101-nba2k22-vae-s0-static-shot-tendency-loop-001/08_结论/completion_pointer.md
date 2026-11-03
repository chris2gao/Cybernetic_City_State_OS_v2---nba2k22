# NBA2K22 VAE · S0 静态投篮倾向机制研究完工指针

- **任务 ID**: `NBA2K22-VAE-S0-STATIC-SHOT-TENDENCY-LOOP-20261101-001`
- **运行 ID**: `run-20261101-nba2k22-vae-s0-static-shot-tendency-loop-001`
- **执行角色**: `execution` (模型：Gemini 2.5 Pro)
- **工作分支**: `task/nba2k22-vae-s0-static-shot-tendency-loop-20261101`
- **派发 HEAD**: `adf371dc62a633b4f2fab5446ac24b3d2087e6de`
- **复算输入 HEAD**: `8d1de51b0cd5dc52be41511b80e4bcf3a5cece43`
- **完成判定**: **`OBJECTIVE_MET`**（离线静态实证分析、二次定向数值复算与 Phase A 预检设计 100% 达成；后续实机设置实验严格保持在等待门 `WAIT_HUMAN_AUTHORIZATION`）

---

## 一、S0 静态实证分析核心结论与二次定向复算结果

在 Human 权威确认此前一个月日历模拟未发生人为数值修改的前提下，本次研究在本地物理数据库 `world-v24.sqlite` 上完成了两轮严格的计量经济学求解与二次定向复算（详见 [`post_delivery_numeric_reconciliation.md`](file:///E:/gemini_space/nba2k22/01_os/07_content/_runs/run-20261101-nba2k22-vae-s0-static-shot-tendency-loop-001/06_执行/post_delivery_numeric_reconciliation.md)）：

### 1. 核心统计指标 100% 精确可复算
- **双变量强相关性**:
  - `ShotTendency` vs 场均出手 (FGA/G): **$r = 0.9303$**（实时复算值：0.9303，误差 $< 0.0001$）
  - `ShotTendency` vs 每 36 分钟出手 (FGA/36): **$r = 0.9008$**（实时复算值：0.9008，误差 $< 0.0001$）
  - `ShotTendency` vs 球队出手占比 (Team Shot Share): **$r = 0.9316$**（实时复算值：0.9316，误差 $< 0.0001$）
  - `ShotTendency` vs 出场时间 (MPG): **$r = 0.6960$**（实时复算值：0.6960）
- **6 阶分箱严格单调递增**（$N = 268$）：
  - 极低倾向 (0–49, $N=28$): 均值 41.4，FGA/36 为 **7.62**，出手占比 **4.94%**
  - 低倾向 (50–64, $N=108$): 均值 55.6，FGA/36 为 **11.65**，出手占比 **8.12%**
  - 中等倾向 (65–74, $N=52$): 均值 66.8，FGA/36 为 **14.08**，出手占比 **10.41%**
  - 高倾向 (75–84, $N=44$): 均值 77.6，FGA/36 为 **16.09**，出手占比 **14.13%**
  - 极高倾向 (85–94, $N=27$): 均值 87.8，FGA/36 为 **17.92**，出手占比 **17.54%**
  - 精英倾向 (95–100, $N=9$): 均值 95.9，FGA/36 为 **19.39**，出手占比 **19.44%**
- **多元计量回归模型（控制角色、能力、时间与战术）**:
  - **模型 3（全要素多元控制模型，解释度 $R^2 = 0.8446$）**:
    $$\text{FGA/36} = 0.6601 + 0.2145 \cdot \text{ShotTendency} - 0.1414 \cdot \text{MPG} + 0.0282 \cdot \text{Touches} + \dots$$
    - `ShotTendency` 偏回归系数 **$\beta = 0.2145$**（标准误 $0.0127$，$t = 16.83$，$p < 10^{-15}$，95% CI: $[0.1895, 0.2394]$）。
    - 三分能力（$t = -1.66$）与中投能力（$t = 1.76$）的边际出手影响不显著，表明在控制倾向后，能力主要决定命中率，而出手体量主要被倾向支配。
  - **模型 4（球队出手占比全要素模型，$R^2 = 0.9370$）**:
    - `ShotTendency` 偏回归系数 **$\beta = 0.0017$**（$t = 17.35$），即投篮倾向每提升 10 点，球员占全队总出手的份额平均增加 **1.7%**。

### 2. 疑点专项审计与确认
1. **快照表行数归因**: 物理数据库 `world-v24.sqlite` 实际包含 `13,667` 行倾向快照与属性快照（分布于 13 个 Capture Unit，含 3 个 3,390 行的批量技能单元与 10 个 live-world 单元）。G1 报告的 `1,848` 行是当时特定 4 个批次（$4 \times 462$）的增量审核范围，并非数据库全貌。同时更正了 `player_vitals_observations` 行数复制笔误（实为 `23,837` 行）。
2. **快照时序排序核查**: 针对全联盟 462 名球员进行逐人对账，证明由于最新单元（`player-skill:e01990ebd0990e8eaa3a1c77`）的字典序恰与时序最高位重合，时序排序 `cu.observed_at DESC` 与字典排序 `unit_id DESC` 选出的快照记录**完全无差异（0 人差异，0 数值差异）**。现已正式固化时序排序。
3. **推断边界精确化**: 明确澄清相关性不代表独占因果性，$-3.25$ 出手变化属于基于全联盟经验的**理论情景投影**，而非实机必须达成的因果硬性门槛。

---

## 二、首个真实设置生效实验建议（Phase A Smoke Plan）

本计划作为待 Human 授权时的准备预案，**当前窗口严格不执行**：

1. **实验性质**: **设置持久性与读回冒烟测试 (Persistence & Readback Smoke Test)**。
2. **严格等待门工作流**:
   - `WAIT_HUMAN_AUTHORIZATION`: 向 Human 请教游戏内真实修改菜单入口与确认流程，等待 Human 明确授权。
   - `WAIT_HUMAN_ONE_WEEK_SIM_AND_CAPTURE`: Human 在游戏内操作 Lillard 倾向（95 $\to$ 80）并存盘，手动模拟 1 周比赛（约 3–4 场），随后 Human 显式发出“Gemini 采集数据”指令。
   - Gemini 执行 `FULL` 全量刷新，比对原生偏移 `0x458` 内存读回与 SQLite 持久化值是否为 80。
   - **严格边界区分**: 1 周冒烟测试仅证明“设置是否成功存盘且未被游戏引擎重置”，坚决不将短期小样本 FGA 波动作为因果效果证明。

---

## 三、OS Loop 可观测性完整统计报告

- **总迭代轮次**: 5 轮（内部开发 4 轮 + 交付后定向整改 1 轮，100% 成功，0 次破坏与回归）。
- **触发类型分布**:
  - `PLANNED_INCREMENT`: 4 轮（80.0%）
  - `REVIEW_FINDING`: 1 轮（20.0%）
- **迭代递进事实**:
  1. `iter-001-source-join-audit`: 联接 6 张核心表，确认偏移 `0x458`，审计 16 场比分差异，输出 [`static_source_join_quality.json`](file:///E:/gemini_space/nba2k22/01_os/07_content/_runs/run-20261101-nba2k22-vae-s0-static-shot-tendency-loop-001/06_执行/static_source_join_quality.json)。
  2. `iter-002-cohort-filtering-and-distributions`: 划分阶梯人群（合格轮换 268 人，纯净轮换 257 人），计算 6 阶单调分箱与相关矩阵，输出 [`static_shot_tendency_s0_summary.json`](file:///E:/gemini_space/nba2k22/01_os/07_content/_runs/run-20261101-nba2k22-vae-s0-static-shot-tendency-loop-001/06_执行/static_shot_tendency_s0_summary.json)。
  3. `iter-003-multivariate-models-and-lillard-peer-study`: 求解 4 组多元回归，完成 Lillard 同侪横向对标与假说评估，输出 [`static_shot_tendency_s0_analysis.md`](file:///E:/gemini_space/nba2k22/01_os/07_content/_runs/run-20261101-nba2k22-vae-s0-static-shot-tendency-loop-001/06_执行/static_shot_tendency_s0_analysis.md)。
  4. `iter-004-phase-a-smoke-design-and-replay-tests`: 制定 Phase A 预检方案，构建专用回归套件 [`test_static_shot_tendency_replay.py`](file:///E:/gemini_space/nba2k22/08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype/tests/test_static_shot_tendency_replay.py)，输出初步回执。
  5. `iter-005-post-delivery-numeric-reconciliation`: 响应规划总线核查输入，编写独立复算模块 [`recalculate_s0_static_metrics.py`](file:///E:/gemini_space/nba2k22/08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype/recalculate_s0_static_metrics.py)，完成物理数据库全量指标重算对账，升级测试套件为实时 SQL 执行（8/8 通过，0.947s），输出 [`post_delivery_numeric_reconciliation.md`](file:///E:/gemini_space/nba2k22/01_os/07_content/_runs/run-20261101-nba2k22-vae-s0-static-shot-tendency-loop-001/06_执行/post_delivery_numeric_reconciliation.md) 与更新后的测试回执。
- **停止类别 (Stop Class)**: **`OBJECTIVE_MET`**（离线研究与复算目标完全达成；实机操作严格等待 Human 授权）。

---

## 四、交付物清单

1. 交付后定向数值复算与口径审计报告（新增）：
   [`post_delivery_numeric_reconciliation.md`](file:///E:/gemini_space/nba2k22/01_os/07_content/_runs/run-20261101-nba2k22-vae-s0-static-shot-tendency-loop-001/06_执行/post_delivery_numeric_reconciliation.md)
2. 独立确定性数值复算脚本（新增）：
   [`recalculate_s0_static_metrics.py`](file:///E:/gemini_space/nba2k22/08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype/recalculate_s0_static_metrics.py)
3. 升级版实时数据库重算自动化测试套件：
   [`test_static_shot_tendency_replay.py`](file:///E:/gemini_space/nba2k22/08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype/tests/test_static_shot_tendency_replay.py)
4. 机器可重算测试执行回执 (v2)：
   [`static_analysis_replay_tests.json`](file:///E:/gemini_space/nba2k22/01_os/07_content/_runs/run-20261101-nba2k22-vae-s0-static-shot-tendency-loop-001/07_测试执行/static_analysis_replay_tests.json)
5. 字典与数据源联接质量审计 (v2)：
   [`static_source_join_quality.json`](file:///E:/gemini_space/nba2k22/01_os/07_content/_runs/run-20261101-nba2k22-vae-s0-static-shot-tendency-loop-001/06_执行/static_source_join_quality.json)
6. 完整静态实证研究长篇报告：
   [`static_shot_tendency_s0_analysis.md`](file:///E:/gemini_space/nba2k22/01_os/07_content/_runs/run-20261101-nba2k22-vae-s0-static-shot-tendency-loop-001/06_执行/static_shot_tendency_s0_analysis.md)
7. 机器可读统计汇总数据：
   [`static_shot_tendency_s0_summary.json`](file:///E:/gemini_space/nba2k22/01_os/07_content/_runs/run-20261101-nba2k22-vae-s0-static-shot-tendency-loop-001/06_执行/static_shot_tendency_s0_summary.json)
8. OS Loop 增量观测日志（含第 5 轮整改记录）：
   [`loop_iterations.jsonl`](file:///E:/gemini_space/nba2k22/01_os/07_content/_runs/run-20261101-nba2k22-vae-s0-static-shot-tendency-loop-001/06_执行/loop_iterations.jsonl)
9. OS Loop 观测统计汇总：
   [`loop_summary.json`](file:///E:/gemini_space/nba2k22/01_os/07_content/_runs/run-20261101-nba2k22-vae-s0-static-shot-tendency-loop-001/08_结论/loop_summary.json)
10. 本完工指针：
    [`completion_pointer.md`](file:///E:/gemini_space/nba2k22/01_os/07_content/_runs/run-20261101-nba2k22-vae-s0-static-shot-tendency-loop-001/08_结论/completion_pointer.md)
11. 运行生命周期元数据：
    [`run.yml`](file:///E:/gemini_space/nba2k22/01_os/07_content/_runs/run-20261101-nba2k22-vae-s0-static-shot-tendency-loop-001/run.yml)
