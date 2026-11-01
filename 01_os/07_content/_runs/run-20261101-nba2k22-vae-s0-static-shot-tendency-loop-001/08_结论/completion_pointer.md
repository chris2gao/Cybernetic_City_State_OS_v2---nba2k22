# NBA2K22 VAE · S0 静态投篮倾向机制研究完工指针

- **任务 ID**: `NBA2K22-VAE-S0-STATIC-SHOT-TENDENCY-LOOP-20261101-001`
- **运行 ID**: `run-20261101-nba2k22-vae-s0-static-shot-tendency-loop-001`
- **执行角色**: `execution` (模型：Gemini 2.5 Pro)
- **工作分支**: `task/nba2k22-vae-s0-static-shot-tendency-loop-20261101`
- **固定派发 HEAD**: `adf371dc62a633b4f2fab5446ac24b3d2087e6de`
- **完成判定**: **`OBJECTIVE_MET`**（离线静态实证分析与方案设计已 100% 达成；后续 Phase A 实机设置实验进入严格等待门 `WAIT_HUMAN_AUTHORIZATION`）

---

## 一、S0 静态实证分析核心结论

在 Human 权威确认此前一个月日历模拟未发生人为数值修改的前提下，本次研究对 `world-v24.sqlite` 中累积的 238 场模拟比赛及 461 名注册球员进行了全联盟横截面计量分析：

### 1. 投篮倾向是日历模拟出手体量的核心正向调节器
- **双变量强相关性**:
  - `ShotTendency` vs 场均出手 (FGA/G): **$r = 0.9303$**
  - `ShotTendency` vs 每 36 分钟出手 (FGA/36): **$r = 0.9008$**
  - `ShotTendency` vs 球队出手占比 (Team Shot Share): **$r = 0.9316$**
  - `ShotTendency` vs 出场时间 (MPG): $r = 0.6960$
- **6 阶分箱严格单调递增**:
  - 极低倾向 (0–49, $N=28$): 均值 41.4，FGA/36 为 **7.62**，出手占比 **4.94%**
  - 低倾向 (50–64, $N=108$): 均值 55.6，FGA/36 为 **11.65**，出手占比 **8.12%**
  - 中等倾向 (65–74, $N=52$): 均值 66.8，FGA/36 为 **14.08**，出手占比 **10.41%**
  - 高倾向 (75–84, $N=44$): 均值 77.6，FGA/36 为 **16.09**，出手占比 **14.13%**
  - 极高倾向 (85–94, $N=27$): 均值 87.8，FGA/36 为 **17.92**，出手占比 **17.54%**
  - 精英倾向 (95–100, $N=9$): 均值 95.9，FGA/36 为 **19.39**，出手占比 **19.44%**

### 2. 多元计量回归模型（控制角色、能力、时间与战术）
- **模型 3（全要素多元控制模型，解释度 $R^2 = 0.8446$）**:
  $$\text{FGA/36} = 0.6601 + 0.2145 \cdot \text{ShotTendency} - 0.1414 \cdot \text{MPG} + 0.0282 \cdot \text{Touches} + \dots$$
  - `ShotTendency` 偏回归系数 **$\beta = 0.2145$**（$t = 16.83$，$p < 10^{-15}$，95% CI: $[0.1895, 0.2394]$）。
  - 三分能力（$t = -1.66$）与中投能力（$t = 1.76$）的边际出手影响不显著，表明 2K22 日历模拟中能力主要影响命中率，而出手频率高度被倾向参数支配。
- **模型 4（球队出手占比全要素模型，$R^2 = 0.9370$）**:
  - `ShotTendency` 偏回归系数 **$\beta = 0.0017$**（$t = 17.35$），即投篮倾向每提升 10 点，球员占全队总出手的份额平均增加 **1.7%**。

### 3. Damian Lillard 同侪对标与 -15 点干预评估
- **Lillard 处于联盟顶格区间**: 投篮倾向 95，触球倾向 99，场均 36.38 分钟，FGA/36 为 19.67，出手占比 23.09%，与 Luka Doncic (20.32)、Stephen Curry (20.19)、Trae Young (20.33) 形成高度一致的 19.6–20.4 出手通道。其队友 CJ McCollum 倾向为 88，FGA/36 为 15.90（低 3.77 次），出手占比 17.8%（低 5.3%）。
- **静态投影测算**: 倾向由 95 下调至 80（$\Delta = -15$），多元模型预期 $\Delta \text{FGA/36} = -3.22$，在 Lillard 出场时间下对应 $\Delta \text{FGA/G} \approx -3.25$（由 19.88 降至约 16.63 次），球队出手占比下降约 2.55%（降至约 20.5%）。
- **核心方法论警示**: 横截面静态斜率仅为**合理假说生成器**，绝对不能直接等同于个体动态因果剂量响应（需考虑队友 McCollum/Nurkic 的球权再分配与教练跑战术判定）。

---

## 二、首个真实设置生效实验建议（Phase A Smoke Plan）

本计划作为待 Human 授权时的准备预案，**本次严格不执行**：

1. **实验性质**: **设置持久性与读回冒烟测试 (Persistence & Readback Smoke Test)**。
2. **严格等待门工作流**:
   - `WAIT_HUMAN_AUTHORIZATION`: 向 Human 请教游戏内真实修改菜单入口与确认流程，等待 Human 明确授权。
   - `WAIT_HUMAN_ONE_WEEK_SIM_AND_CAPTURE`: Human 在游戏内操作 Lillard 倾向（95 $\to$ 80）并存盘，手动模拟 1 周比赛（约 3–4 场），随后 Human 显式发出“Gemini 采集数据”指令。
   - Gemini 执行 `FULL` 全量刷新，比对原生偏移 `0x458` 内存读回与 SQLite 持久化值是否为 80。
   - **严格边界区分**: 1 周冒烟测试仅证明“设置是否成功存盘且未被游戏引擎重置”，坚决不将短期小样本 FGA 波动作为因果效果证明。

---

## 三、OS Loop 可观测首个试点统计报告

- **总迭代轮次**: 4 轮（有效迭代 4 轮，全部成功，0 次破坏与回归）。
- **触发类型分布**: `PLANNED_INCREMENT` 4 轮（100.0%）。
- **迭代递进事实**:
  1. `iter-001-source-join-audit`: 联接 6 张核心表，确认偏移 `0x458`，审计 16 场比分差异，输出 [`static_source_join_quality.json`](file:///E:/gemini_space/nba2k22/01_os/07_content/_runs/run-20261101-nba2k22-vae-s0-static-shot-tendency-loop-001/06_执行/static_source_join_quality.json)。
  2. `iter-002-cohort-filtering-and-distributions`: 划分阶梯人群（合格轮换 268 人，纯净轮换 257 人），计算 6 阶单调分箱与相关矩阵，输出 [`static_shot_tendency_s0_summary.json`](file:///E:/gemini_space/nba2k22/01_os/07_content/_runs/run-20261101-nba2k22-vae-s0-static-shot-tendency-loop-001/06_执行/static_shot_tendency_s0_summary.json)。
  3. `iter-003-multivariate-models-and-lillard-peer-study`: 求解 4 组多元回归，完成 Lillard 同侪横向对标与假说评估，输出 [`static_shot_tendency_s0_analysis.md`](file:///E:/gemini_space/nba2k22/01_os/07_content/_runs/run-20261101-nba2k22-vae-s0-static-shot-tendency-loop-001/06_执行/static_shot_tendency_s0_analysis.md)。
  4. `iter-004-phase-a-smoke-design-and-replay-tests`: 制定 Phase A 预检方案，构建专用回归套件 [`test_static_shot_tendency_replay.py`](file:///E:/gemini_space/nba2k22/08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype/tests/test_static_shot_tendency_replay.py)，执行 8/8 通过，输出 [`static_analysis_replay_tests.json`](file:///E:/gemini_space/nba2k22/01_os/07_content/_runs/run-20261101-nba2k22-vae-s0-static-shot-tendency-loop-001/07_测试执行/static_analysis_replay_tests.json)。
- **停止类别 (Stop Class)**: **`OBJECTIVE_MET`**（离线研究目标全部达成；实机操作严格等待 Human 授权）。

---

## 四、交付物清单

1. 完整静态实证研究长篇报告：
   [`static_shot_tendency_s0_analysis.md`](file:///E:/gemini_space/nba2k22/01_os/07_content/_runs/run-20261101-nba2k22-vae-s0-static-shot-tendency-loop-001/06_执行/static_shot_tendency_s0_analysis.md)
2. 机器可读统计汇总数据：
   [`static_shot_tendency_s0_summary.json`](file:///E:/gemini_space/nba2k22/01_os/07_content/_runs/run-20261101-nba2k22-vae-s0-static-shot-tendency-loop-001/06_执行/static_shot_tendency_s0_summary.json)
3. 字典与数据源联接质量审计：
   [`static_source_join_quality.json`](file:///E:/gemini_space/nba2k22/01_os/07_content/_runs/run-20261101-nba2k22-vae-s0-static-shot-tendency-loop-001/06_执行/static_source_join_quality.json)
4. OS Loop 增量观测日志：
   [`loop_iterations.jsonl`](file:///E:/gemini_space/nba2k22/01_os/07_content/_runs/run-20261101-nba2k22-vae-s0-static-shot-tendency-loop-001/06_执行/loop_iterations.jsonl)
5. 专用重放与边界自动化测试套件：
   [`test_static_shot_tendency_replay.py`](file:///E:/gemini_space/nba2k22/08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype/tests/test_static_shot_tendency_replay.py)
6. 机器可重算测试执行回执：
   [`static_analysis_replay_tests.json`](file:///E:/gemini_space/nba2k22/01_os/07_content/_runs/run-20261101-nba2k22-vae-s0-static-shot-tendency-loop-001/07_测试执行/static_analysis_replay_tests.json)
7. OS Loop 观测统计汇总：
   [`loop_summary.json`](file:///E:/gemini_space/nba2k22/01_os/07_content/_runs/run-20261101-nba2k22-vae-s0-static-shot-tendency-loop-001/08_结论/loop_summary.json)
8. 本完工指针：
   [`completion_pointer.md`](file:///E:/gemini_space/nba2k22/01_os/07_content/_runs/run-20261101-nba2k22-vae-s0-static-shot-tendency-loop-001/08_结论/completion_pointer.md)
9. 运行生命周期元数据：
   [`run.yml`](file:///E:/gemini_space/nba2k22/01_os/07_content/_runs/run-20261101-nba2k22-vae-s0-static-shot-tendency-loop-001/run.yml)
