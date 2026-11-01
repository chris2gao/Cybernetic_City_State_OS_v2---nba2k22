# NBA2K22 VAE / REA Phase A · GPT 规划窗口恢复档案（2026-11-01）

> **文档性质**：窗口即将达到长度上限时，Human 主动要求的跨窗口 CONTEXT / PRMS 交接备份；保存**当前进行中的项目状态、未执行任务、实机权限边界与恢复步骤**。不是工程实现，不是独立审核，不是对任何 Setter 的授权；不改 master、游戏或 SQLite。
>
> **写入范围**：本独立 handoff 分支，仅追加资料。以下“已完成/已验证”均须按各来源的证据等级理解。新窗口必须读取精确 SHA，而非靠聊天记忆恢复或把单个报告当全部事实。

## 0. 最重要的恢复结论（先读）

1. 当前工作属于 **VAE Stage02 后续证据研究 → G2 Shot Tendency 静态 S0 → 准备首次 REA Phase A 实机设置生效验证**。静态分析已经完结；**真实 Lillard 95→80 修改从未执行**。
2. **当前精确停止点：REA 本地工具“只读预检”尚待 Gemini 执行并提交报告**。上一 GPT 已给出预检执行提示词，但聊天中**没有收到 Human 确认已发给 Gemini 或 Gemini 完工回执**。不能把“已派发提示词”当成“已执行”。
3. 预检不允许附加游戏进程、调用 Setter、写内存、推进日历、采集、自动安装或常驻监听。已确认唯一可以做的是本地现存代码/依赖/固定版本/离线测试和安全边界检查。
4. 即使预检结果 READY，**下一阶段写入仍需要 Human 明确单次授权**，包含具体存档、球员、球队、字段、值、执行方式和游戏操作流程。首次只做一个字段，绝不默认批量写入。
5. Human 明确控制**推进日历、手动发起 Gemini 全量采集、以及真实游戏操作**；Gemini 在 Human 操作期间停止当前实验流程，完成后等 Human 明确通知才开始分析。
6. 历史 238 场联盟模拟及 Lillard 16 场是 Human 在当前研发开始前模拟约一个月所得；**这期间没有人为调整任何球员/教练等数值**。这些历史数据允许直接用作未人为干预的静态 S0；它们不是本次 Gemini/GPT 测试新生成的比赛，不能冒充“修改后的实机效果”。
7. 大体积 SQLite、WAL/SHM、压缩数据库和原始内存只留本地。GitHub 只保存代码、Schema、轻量脱敏测试与来源信息；**禁止新推数据库/备份**。历史 Git 大文件暂不重写历史。
8. OS 内部开发 Loop 是常规有界研究、开发、测试、修正、记录的循环；不要求每个小增量另开独立审核。正式七阶段 Workflow、Human 决策门、Core §9 风险审核与 §11 真正停止门不变。Loop 观测和真实 post-delivery 整改应分开计数。

## 1. 岗位与项目边界

- 领域：Cybernetic City-State OS / nba2k22；线上 NBA 仓库：https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22
- Core 仓库：https://github.com/chris2gao/Cybernetic_City_State_OS_v2---core
- 当前窗口承担 **GPT 规划总线/decision_architecture** 的研究评估、需求设计、行动派发及适度复核；不是 execution、不是 independent_review，也不直接控制游戏。
- Human 负责授权、实机操作、关键裁决；Gemini 2.5 Pro 曾承担 G1、G2、S0 任务执行，Codex 负责部分 REA/OS 原生工程；GitHub/PRMS 承载长期证据，聊天仅是临时工作台。
- 公共基线角色 NBA2K22_COMMON_BASELINE；需要重新 Fork 时从公共基线激活相应岗位，明确任务 ID、角色、来源 SHA、权限及任务边界。
- 核查时所见 NBA master HEAD：45cc45cae0550ddcda192a2179ea48509b27f6ee；Core master HEAD：934425cf43d4fe3307b0112142aec1ba434a5734。**不是当前各试验分支的代码替代品**。恢复时再读取远端最新 HEAD。

## 2. 已完成及现有成果（按因果先后）

### G1 · WorldData 一次性 FULL 采集链路
- 分支 task/nba2k22-vae-calendar-sim-g1g2-readiness-loop-20261101
- 已核对交付 SHA：63f86a26e8cee99f40eedc1312f045b5f60d0c37
- MyLEAGUE0003，save_id=nba2k22_test_01，运行模式 FRANCHISE。G1 FULL 从**已存在的存档数据**真实读取内存并入本地 world-v24.sqlite，处理 20 类 Reader（其中16类新增成功，4类年度已有状态复用），无新比赛生成、无日历推进。
- 当时累积 238 场已完赛日历模拟、476 球队比赛 Box、6133 活跃球员 Box；原始大型数据库/二进制数据在本地被 Git 忽略。历史来源含 FULL_NATIVE_BOX 及 REUSED_FROZEN_BOX，来源追踪不可丢。
- 238 场中222场球员得分对账严格吻合，16场不吻合。后续报告将其中5场对应加时节次截断、11场对应 Wizards 时间/缺失条目；具体底层根因不能超出原始证据。
- 重要：某次 FULL 采集不要求“必须先产生新比赛”；Human 仍须主动要求 Gemini 开始采集。

### G2-S0 · 单组历史基线与首个 Loop 观测样本
- 分支 task/nba2k22-vae-g2-s0-baseline-loop-observability-pilot-20261101
- 最新 Human 操作协议提交：d7e6b0a03a9a166bcf243a26d8353095f6cd9228
- Lillard：player:native:2459；开拓者 team:native:28，16场历史模拟，FGA/G=19.875，PTS/G≈29.562，MIN/G≈36.375；历史单点 Shot Tendency=95。
- 人工没有在这段历史期间修改设置；历史单点快照仍不是逐场原生值证明。原 G2 的 READY 只指静态 S0 和协议准备，**不能**说干预、持久性或影响已验证。
- 结构化 Loop：4个初始开发增量（PLANNED_INCREMENT），没有 post-delivery 整改。原暂停原因 EXTERNAL_EVIDENCE_PENDING；保留事实澄清，不伪加一轮开发。
- Human 更正及固定三场景协议原文：
  01_os/07_content/_runs/run-20261101-nba2k22-vae-g2-s0-baseline-loop-observability-pilot-001/08_结论/human_static_baseline_and_three_trigger_protocol_20261101.md

### S0 静态投篮倾向研究与交付后复算
- 分支 task/nba2k22-vae-s0-static-shot-tendency-loop-20261101
- **最终 HEAD：08405457517b2242562e855c9fdfe59c1c1a9a6e**
- 首次交付1988ca3a后曾发现快照表行数与时序选择疑点；一次定向整改完成，无需再重复整改/静态研究。
- Gemini 的真实本地 SQLite 复算器：
  08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype/recalculate_s0_static_metrics.py
- 核验说明：
  01_os/07_content/_runs/run-20261101-nba2k22-vae-s0-static-shot-tendency-loop-001/06_执行/post_delivery_numeric_reconciliation.md
- 回执（Gemini报告，GPT核过代码但**未亲自运行本地数据库**）：
  - 合格轮换球员268人（至少10场且≥15 MPG）；净化样本257人。
  - Shot Tendency vs FGA/G 相关 r=0.9303；vs FGA/36 r=0.9008；vs 球队出手占比 r=0.9316。
  - 多元 OLS FGA/36 模型 Shot Tendency β=0.2145、R²=0.8446；团队份额模型 β≈0.0017、R²=0.9370。
  - Lillard 16场 FGA/G=19.875，FGA/36≈19.670，球队出手份额≈23.09%。
  - 历史原始捕获行数：player_tendency_snapshots和player_attribute_snapshots累计各13,667行；G1报告1,848行为特定增量批次口径。player_vitals_observations 23,837行。所有快照排序已改为 cu.observed_at DESC, unit_id DESC，旧字典排序在本实例碰巧无数值差异。
  - 实时SQL复算测试在Gemini环境8/8、0 skip、0 error；另6项合成回归通过。**本GPT核验的是GitHub源码与测试收据，非在Human本机亲自运行**。
  - 原理边界：静态强相关**不等于**个体干预因果；Lillard 95→80 的 -3.25 FGA/场只是横截面情景投影，**不是**真实写入效果或必达阈值；能力对命中率需另行实验。
- S0阶段 Loop 合计5轮 = 4轮初始开发 + 1轮 REVIEW_FINDING 驱动的交付后定向整改，stop=OBJECTIVE_MET（仅静态研究）；后续 Phase A 另立Human等待门。
- S0前置研究完成，**不要在新窗口重新要求一次无必要的全量采集、历史月模拟或回归审计**。

### Core Loop Observability v0.1
- Human 已批准 Core 独立试点，Core分支 task/core-development-loop-observability-model-20261101；HEAD f3ae6b83897c04f6ee7758a9b32fc8ea2d06cea5。
- 准备在3–5个真实开发任务上验证 loop_iterations.jsonl + loop_summary.json；必须是真实有界、有证据的增量，标注触发、因果、测试、变化、SHA和停止原因；不能以命令、对话和测试数冒充轮次。
- 内部开发 Loop 可持续，首次交付后定向整改限制最多2轮；真实Human门、七阶段与正式审核仍按Canonical。已有试点（G2、S0）不需要重新补做。

## 3. REA Phase A 原生能力：最新发现，重要！

**特别注意版本分裂：REA Native执行代码在独立冻结检查点，不在 S0 VAE 分支的工程树里，也不在当时 NBA master 中。**

- REA 冻结分支 baseline/nba2k22-native-execution-checkpoint-014-20261029
- 精确 SHA：6151ef5d484914edcec2fbcfcf3bcce83a848907
- 原生能力总报告：
  08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_control/TASK_CLOSURE_20261029.md
- 具体倾向设置：
  08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_control/PLAYER_STAT_NATIVE_CONTRACT.md
- Registry/字段：
  research/rea_native_control/data/action_registry.json
  research/rea_native_control/data/player_stat_fields.json
  research/rea_native_control/data/native_bindings.json
- 处理器/入口：
  research/rea_native_control/runtime/player_stats.js
  research/rea_native_control/cli.py
  research/rea_native_control/run_native_program.ps1
  research/rea_native_control/PLAYER_EDITOR_READ_CONTRACT.md
  （相对路径前缀统一为 08_Domain_Applications/Antigravity_GM_Engine/。）

**已有候选接口**
- 单字段 action_id：PLAYER_SET_TENDENCY，kind=MUTATE，capability=CALL_LOGIC_RECOVERED，handler=player.stats；**不是 PRIOR_LIVE_SUCCESS**。
- 批量同球员多字段 action_id：PLAYER_PATCH_TENDENCIES（非原子事务），尚未真实批量验证；不建议第一次测试批量。
- 本次拟议单字段：SHOT_TENDENCY，Native index=57，PlayerData 偏移1112/0x458，uint8 0..100；当前历史值95，**提议**新值80（-15）。
- 宿主传参键：team_id / player_id / field_id / value；目标 WorldData标识：team:native:28 / player:native:2459（开拓者 Lillard）。**这两个前缀ID不保证直接等于 REA 内部整数ID，必须在本地只读预检与实际运行前匹配。**
- 原生索引 Setter 路径恢复：原版 0x990a10(PLAYER*, native_stat_index:int, value:int)；对应原版 Getter0x978360。运行器设计检查当前队伍/球员唯一身份、前值、目标预期字节、其它156个相关字节、缓存标志及后读回；错误不自动重试/不暗中回滚。
- CLI 只有catalog/plan/emit 预备，不会自动执行；实际 REA Transport + Windows管理员权限 +固定 EXE SHA256（1727ad72085fba39e789ee574fc15aab623ad1651cf6879e95e8cd53b6ffbbf5）+指定PID/授权引用才可能执行。原冻结状态 CLOSED_WITH_DEFERRED_SCOPE/full_goal_complete=false，不是生产级Writer。
- 原 Checkpoint014 只拥有本 Setter的 PE/静态恢复、离线合成ABI测试，**没有Lillard这一字段的真实Native写入、独立读回、Game UI显示、Save/Reload、后续一周持久性或机制造成的比赛效果证据**。
- 历史其它原生成功（指定Coach设置、球探、交易）不能外推为此字段成功。
- 近期 GPT **只读检查了GitHub**，没有读取/连接/修改Human的Windows本地游戏；本地工具是否已部署、REA依赖、exe匹配、当前现场PID及存档身份均仍待检。

## 4. 当前活动任务：REA 本地只读预检（尚未收到回执）

上一个 GPT 规划窗口已经提供了如下工作建议：
- 在当前Windows本地**只读**核对 Checkpoint014 工具代码、可用运行依赖、REA固定EXE构建、ActionRegistry/NativeIndex57/0x458、Getter→Setter→Getter和保护机制；进行**离线测试**；
- 核查 MyLEAGUE0003/nba2k22_test_01 与REA游戏场景、整型team_id/player_id 的身份规则；本地部署状态与操作前提；
- 输出环境检查报告、命令/离线回执、问题清单，以及 READY_FOR_HUMAN_AUTHORIZATION 或 NOT_READY 的**预检判定**；
- 不启动游戏、不附加游戏进程、不调用任何Setter或Native写入、不做日历模拟、不采集新数据、不自动部署、不后台监听、不合并master。
- Human在本会话**没有反馈Gemini已收到或完成这份任务**；新窗口开始时首先问/等Human交付Gemini结果，不要虚构已完成或重复派发已经运行的请求。
- 此预检尚未正式创建单独GitHub执行任务合同；如Human希望由本规划窗口创建，可在保留现有技术锚点的前提下另建独立只读任务，不能把本交接文档当授权。

**本交接时的准确状态**：
VAE_STATIC_S0=OBJECTIVE_MET；
REA_PLAYER_SET_TENDENCY_CODE=RECOVERED_OFFLINE_CANDIDATE；
REA_LOCAL_READONLY_PREFLIGHT=DISPATCH_PROMPT_PREPARED_EXECUTION_UNCONFIRMED；
REA_LILLARD_95_TO_80_LIVE_WRITE=NOT_EXECUTED；
ONE_WEEK_POST_WRITE_SIMULATION=NOT_EXECUTED；
POST_WRITE_FULL_CAPTURE=NOT_EXECUTED；
SETTING_PERSISTENCE=NOT_VERIFIED；
TENDENCY_EFFECT_CAUSAL=NOT_VERIFIED；
HUMAN_WRITE_AUTHORIZATION=NOT_GRANTED_IN_THIS_WINDOW。

## 5. Human 已确定的三类真实游戏协作流程（无需重问）

**场景A 普通数据更新**：规划模型告诉Human需要哪些新数据并停止；Human主动对Gemini说“采集数据/全量采集”，Gemini收到Human指令后执行当前采集管道、更新本地SQLite并给出收据；Human再通知分析模型继续。没有新比赛也可触发FULL。

**场景B 修改生效和批量安全性测试**：在单次明确授权且确认已实际修改后，规划模型告诉Human“请模拟一周比赛，然后通知 Gemini 触发采集；采集完成再告诉我”。Human亲自模拟一周、亲自触发Gemini采集，Gemini等待Human明确输入后采集；分析模型比对前/后原生Getter与SQLite，核对具体对象、是否被覆盖、是否保持，必要时逐个检查批量目标。仅一周新赛果不证明因果效果。

**场景C 游戏机制效果验证**：Phase A真正通过后，规划模型根据样本需求请求Human“模拟N天比赛，然后通知Gemini采集”。Human推进指定天数、主动触发采集、完成后通知；模型再分析新比赛FGA、FGA/36、三分、得分、队友份额、出场时间、阵容/伤病/教练等，并与历史S0及对照组比较。不允许模型自行推进/推断Human已完成。

**共通 WAIT_HUMAN_GATE**：只要涉及Human正在执行日历模拟或要触发采集，Gemini必须暂停该实验；不启动常驻进程或轮询。操作完成通知≠采集完成通知。**若实际菜单、保存路径或执行权限有未确认细节，仅针对缺失点询问Human，不重新询问上述三流程。**

## 6. 下一窗口预计的有限工作顺序（不要跳步）

1. 载入本档与相关精确SHA，激活规划角色 OS_PUBLIC_DEVELOPMENT_PLANNER/decision_architecture，确认不是 independent_review、execution。
2. 查询Human是否已把上次“REA Phase A 本地工具只读预检”提示词交给Gemini，或直接接收其报告。**目前未知**，不要先假定。
3. 收到Gemini报告后只针对可能阻断实机的事项判断：分支/依赖/构建SHA/身份/Getter/Setter/安全门；查证其真实本地测试回执。没问题则通过预检；仅关键错误定向整改，不反复审核细节。
4. 此时**还未被授权执行Setter**。将精确实机写入合同（一次写入 Lillard SHOT_TENDENCY 95→80；若当前数值或身份不匹配立即停止；独立readback、其它字节保持、安全失败无自动重试；Game save场景固定）呈交Human，先确认其实际操作流程、存档安全恢复方案及授权。
5. Human确认后，只有明确授权的本地REA执行者才可运行一次写入；写后即时readback记录。**不可因预检READY直接启动**。
6. Human亲自模拟一周→Human主动触发Gemini FULL采集→Human通知规划模型→核验当前值/保存持久性和其它字段。Phase A验收通过再计划Phase B N天效果实验。
7. 后续如批量Setter应用，应从单字段成功开始，再进行受控小批量逐目标核验；不可把合成批量测试等价为真实批量安全。

## 7. 重要证据区分、技术风险

- WorldData采集器和REA Setter分属不同开发分支与技术路径，切换分支不得破坏本地唯一活跃游戏/SQLite；不要直接把REA冻结代码粗暴合并到VAE/master。先做最小显式工具准备。
- 旧历史S0的16场是可用的静态**未人为修改**样本，但不同球员的横截面关联只是规划实验的证据，不等于 Lillard 95→80 后真实会少投3.25次。
- 若冒烟测试出现读回80但一周后恢复95，说明有生命周期或原版AI覆盖问题，不能无依据认定“调用失败”；分开即时Setter/保存/模拟/采集时点。
- 发生实机 unknown/部分完成不能自动重试、自动回滚或换对象，要保留原始收据、请Human确认。
- 批量操作非ACID，不能直接将一次单字段成功升级为任意99项倾向任意人数批量安全。
- Score对账中确有16场异常；不要为追求看起来完美而改动真实历史或伪造因果解释。
- Gemini并非能独立操作Human流程中日历推进、触发新采集；在Human明确指令前不得认为发生。
- 报告中的“100%成功”和“READY”必须标出是离线SQL、静态恢复、合成测试还是 live write/effect。
- 尚未授权清理Git历史大文件；后续数据库产生只保本地。

## 8. 来源索引与继续时的验证入口

GitHub NBA：
1. VAE S0最后复算HEAD 08405457517b2242562e855c9fdfe59c1c1a9a6e：
   https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/commit/08405457517b2242562e855c9fdfe59c1c1a9a6e
2. Human三流程最新原文（G2分支d7e6b0a）： 
   https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/blob/d7e6b0a03a9a166bcf243a26d8353095f6cd9228/01_os/07_content/_runs/run-20261101-nba2k22-vae-g2-s0-baseline-loop-observability-pilot-001/08_%E7%BB%93%E8%AE%BA/human_static_baseline_and_three_trigger_protocol_20261101.md
3. REA原生能力冻结点6151ef5：
   https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/tree/6151ef5d484914edcec2fbcfcf3bcce83a848907/08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_control
4. REA字段与动作契约：
   https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/blob/6151ef5d484914edcec2fbcfcf3bcce83a848907/08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_control/PLAYER_STAT_NATIVE_CONTRACT.md
5. 原生角色任务结项及缺口：
   https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/blob/6151ef5d484914edcec2fbcfcf3bcce83a848907/08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_control/TASK_CLOSURE_20261029.md
6. Core Loop Human批准试点，Core SHA f3ae6b8：
   https://github.com/chris2gao/Cybernetic_City_State_OS_v2---core/blob/f3ae6b83897c04f6ee7758a9b32fc8ea2d06cea5/01_os/_runs/run-20261101-core-development-loop-observability-model-001/08_%E7%BB%93%E8%AE%BA/human_approved_pilot_plan_20261101.md

## 9. 新GPT窗口首条启动模板（复制整段即可）

### 岗位
NBA2K22 OS 规划总控续任；role=decision_architecture（OS_PUBLIC_DEVELOPMENT_PLANNER），非执行/非独立审核。

### 恢复输入
请先读取本 handoff 文档及“来源索引”内精确GitHub SHA。以前任存档为正式任务上下文，不虚构缺失工作或当前实机状态。Fork是静态快照，任何更新以Human最新通知及仓库实证为准。

### 当前工作
接续 VAE S0 强静态关联研究后的 REA Phase A：单次 Lillard SHOT_TENDENCY (Native index57, PlayerData+0x458) 95→80，最终验证REA原生Setter的准确性与持久性，而非游戏内UI手动编辑。**当前先等待/核验Gemini的本地只读预检结果**；尚无实机写入授权。

### 不得做的事
不擅自运行REA Setter、不附加游戏、不改存档、不模拟日期、不触发采集、不推数据库、不合并master；不把静态统计当因果实验证明；不重新询问Human已经明确的三种采集/模拟流程。若下一步需要实际操作菜单/存档细节，针对缺失处向Human确认。

### 输出
先给出“已恢复的已完成工作/未完成工作/精确下一步”，如Human已给Gemini预检报告则直接核验报告并推进准备，不反复重复静态研究。

---

**本档位置为独立handoff任务分支而非master。保留所有旧任务的真实来源及等待门，重要新事实应继续以append-only补充。**
