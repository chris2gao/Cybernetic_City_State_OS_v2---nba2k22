# Human 实机事实更正 · 尚无干预、无新增比赛、无因果验证

**对象**：`NBA2K22-VAE-G2-S0-BASELINE-LOOP-OBSERVABILITY-20261101-001`，原完成提交 `ca06f053b7562429480d155a112f6bc41240b49e`。
**记录类别**：`HUMAN_FEEDBACK`（交付后事实更正/实验边界补充）；**不是一轮新的开发Iteration**、不是S1/S2结果，也不改写原始loop_iterations.jsonl或完成报告。

## 1. Human 刚刚明确确认的权威现场事实

- Human **没有**在本 G1/G2/S0 任务执行期间修改 Damian Lillard 的 Shot Tendency（或其它为本Pilot设计的实验设置）。
- Human **没有**在这些任务执行期间操作游戏推进日历，也**没有**生成任何新的赛后比赛数据。游戏界面仍停留在任务之前的日历日期。
- 当前 WorldData 获得的238场联盟比赛、Lillard 16场比赛数据均是**开发本实验之前就存在于该存档的历史数据**，属于之前 Human 在新赛季前一个月左右自行模拟所得。
- 因此 G1 FULL 证实的是对**既有游戏状态及历史比赛**的实时读取、入库和导出；不能宣称这批比赛是 G1/G2 任务创建的新比赛。
- G2-S0 `READY` 最多是**历史观测基线可用 / 协议准备候选**，不是 `SETTING_CHANGE_VERIFIED`、`NEW_POST_CHANGE_GAME_VERIFIED` 或 `EFFECT_VERIFIED`。只有当前读到95，不自动证明旧16场全部在Shot Tendency=95的稳定设置期。
- 这与既有 `loop_summary.json: EXTERNAL_EVIDENCE_PENDING` 一致；不得由于代码或JSON单测PASS而改变此停止状态。

## 2. Human 定义的真实验证流程（严格等待门）

### Phase A — 设置是否实际生效（persistence/readback smoke）

先由规划模型提出需要测试的设置及证据要求，**先询问Human游戏中真实操作流程及确认步骤**，不能假设编辑菜单、保存顺序、REA写入方式或是否允许批量Setter。

**WAIT_HUMAN_AUTHORIZATION**：仅Human可操作游戏；任何设置修改必须另获Human明确授权与实际操作流程。执行者不得主动修改游戏内存/存档/设置，也不得自行推进日历或持续轮询。

Human触发操作时，模型保持停止；Human根据自己的流程进行变更、**手动模拟一场新比赛**、手动触发新数据采集，完成后再通知Gemini继续。Gemini只能在收到Human显式继续指令后执行相应读取与SQL核验。

验证必须分别记录：
- 同一已声明绑定存档的修改前值、修改后Native Getter即时读回、游戏回存或推赛后读回（能证明哪种持久性，要写哪种）；
- 此次Human生成的新比赛身份、发生于设置修改之后且确为新赛果的证据；
- 新采集的success source units、`observed_at`、本地SQLite值和源级；
- 是否被游戏/AI覆盖或还原。
**只要原生读回与SQLite一致，才可说`SETTING_CHANGE_PERSISTED`；一场比赛的FGA波动不能证明设置作用或修改真正生效。**

**WAIT_HUMAN_BATCH_AUTHORIZATION**：如后续要测试批量修改安全性，先单字段读回与持久性成功，再提出Human确认的安全受控小批次试验；验证每个目标字段/玩家独立读回、反向回滚/游戏覆盖风险及来源，不得未经授权直接批改。

### Phase B — 设置的比赛效果（mechanistic effect）

仅在 Phase A 的实际修改、安全性/批量适用条件由Human裁决通过后，建立受控S1→S2机制实验。Human可在游戏中手动模拟多场Calendar Sim，然后**手动触发新增数据采集，发完成通知**，此时Gemini才可继续。

模型读新产生的赛果与明确历史S0对照：FGA、FGA/分钟、三分出手、PTS、球员时间、战术/阵容/健康/对手变化；明确固定字段、异常场次和对照组。须用真实样本大小、方差、效应区间和不确定性；`p>0.05`只能判未检出证据，**不能直接证伪零效果或单调机制**。不能用旧的238/16场作S2。

**HUMAN_WAIT_GATE 是硬条件**：在Human完成操作并通知之前，Gemini/其他执行模型不能主动读取正在变化的游戏来推断Human是否完成、运行模拟、代替Human调用采集、启动后台监听或进行任何设置写入。允许完全离线且明确授权的研究，但不应把实验阶段错误推进。

## 3. 请求 Gemini 解释本次“测试”如何完成（只需查证现有证据）

请在新工作输入/说明中回答，不能因有`test_s0_pilot_reconciliation.py`的5/5和`test_advanced_metrics_and_boxes.py`6/6就称为设置效果测试：

1. 逐项列明5项专项测试及6项回归测试运行命令、测试对象、是否读取本地`world-v24.sqlite`、哪些是JSON结构/常量断言、哪些真实执行SQL；特别注明`test_score_discrepancy_against_sqlite`在DB缺失时可`skip`及实际receipt是否证明未跳过。
2. 确认本轮所有`s0_consecutive_games`来源于历史观察单元（例如 `live-world:00606ee2a7703ad2322a4e3d`，`observed_at=2026-10-25`），而非本轮任务后新比赛。
3. 查找是否存在任意确凿`SETTING_CHANGE_POST_READBACK`、`POST_INTERVENTION_GAME_ID`、`POST_INTERVENTION_CAPTURE_UNIT`，如无明确写`NONE` / `NOT_EXECUTED`。
4. 解释`S0 READY`、`G2 READY`、`REA PROVEN_NATIVE_READBACK`的精确来源和作用边界；历史`value=95`来自一次Snapshot不等于修改后读回。
5. 不再声称Human已操作或实验影响已测；若之前文案容易误读，请新增**更正说明**，不得覆盖旧报告或用事后补证据伪造过去实验。

## 4. 后续运作与任务状态

- `G1_FULL_CAPTURE`：既有游戏数据真实采集/本地DB链路的成功，可保留。
- `S0_HISTORICAL_BASELINE`：16场历史指标可用于假设和前测候选，设置时段稳定性需要再确认。
- `G2_PROTOCOL_READY`：只读准备候选，可保留。
- `S1_SETTING_MUTATION_VERIFIED`、`S2_NEW_CALENDAR_SIM_CAPTURED`、`G2_EFFECT_VERIFIED`：**NOT_EXECUTED**。
- 仍保持`EXTERNAL_EVIDENCE_PENDING`，不要求 Human 立即进入游戏。规划窗口在要求Human实验时先取得操作流程，而不是在Gemini执行完毕后假定已发生。
- 本新增文件只为保存Human权威证据与反馈，不批准Gemini继续做实机实验、不触发任何采集、无后台行动。
