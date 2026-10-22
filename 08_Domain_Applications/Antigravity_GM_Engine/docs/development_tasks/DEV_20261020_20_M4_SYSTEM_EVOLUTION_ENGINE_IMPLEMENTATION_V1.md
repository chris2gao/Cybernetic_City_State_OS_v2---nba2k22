# DEV20 — M4外挂系统自我进化与开发反馈引擎：Codex实施任务 V1

**2026-10-20工程回执：** 本任务已在独立`codex/dev10-m4-system-evolution`实现并通过所授权5项最小检查，状态M4_ENGINEERING_MAIN_MERGED / GM_V4_NOT_ENABLED；玩家审核后批准跨存档局部事件ID小修正，定向test_02通过，PR #7已合入main（c51fa36）。起点为已合并PR #4的main `5a49d71`；下文PR #4待合并是规划时历史。见[实现与验收](../development_reviews/M4_SYSTEM_EVOLUTION_IMPLEMENTATION_AND_ACCEPTANCE.md)、[操作手册](../M4_SYSTEM_EVOLUTION_WORKBENCH.md)和[开发问题索引](../../web_gm/development_feedback/CURRENT.md)。后续项目保持原后置边界。

2026-10-20 · 玩家要求M系列Codex继续完成M4，先完成工程，不自动启动游戏。任务所有者：M系列Codex窗口②；基于M3-T/DEV14现有能力。状态：IMPLEMENTATION_TASK / AWAITING_CODEX_EXECUTION。

## 0. 最新权威业务边界（覆盖旧M4混合定义）

**本次M4是外挂工程系统的“自我进化/开发问题管理”功能，不是30队GM经营绩效评价器。**

严格拆开三件事：
- **GM经营反馈**：交易、教练、战术、轮换和赛果之间的关系，归GM/分析模型现有M2/M3及未来BPTI的球队经营职责；本M4不研究策略好坏、不调整球队设置、不自动提出新交易。
- **3D vs Calendar Fast-Sim校准器**：季后赛玩家标记3D比赛、两套统计对照、32项Simulation Sliders年度改良，是M系列结束后的**另立项目**；本M4不写来源分类、校准公式和滑块调节代码。
- **M4系统自我进化**：从现有采集/读取/分析/提案/审批/执行/模型交接的**工程证据**识别缺口、BUG、接口阻断与功能请求，沉淀去重问题池，供Web Development下次主动审阅、形成任务，玩家决定是否立项。

本定义按玩家2026-10-20最新明确分工优先于旧DEV10 V1/V2中把 GM_STRATEGY_DRIFT、ACTION_EXPECTATION_MISMATCH、action_hypotheses/outcome_comparisons列为M4必做的段落。可保持旧类型兼容，但**不在本次开发GM赛果比较/篮球预测/战术复盘模块**。

所有操作由玩家显式触发的工作流产生或手动运行；无后台守护、通知任务、实时扫描、跨模型自动唤醒、自动Coder任务。此规划不是游戏写入、正式采集、Bug修复、BPTI开发或V4正式启用的许可。

## 1. 开发起点和分支方式

- 当前DEV14 PR #5已合入main；M3A/M3B/M3-T在PR #4（head `7e8ba1a71ee350ea722ea262f1da70bce51bfc49`）本地工程完成、8项范围内合成验收，但PR #4仍Draft/未合并、GM V4未启用。开始前**重查远程状态**，不得因文档的旧SHA判断部署。
- **先读最新origin/main/AGENTS.md与docs/DEVELOPMENT_BOUNDARIES_AND_VALIDATION_POLICY.md V2**，以及docs/33、docs/34、M3-T验收报告和M4任务书。
- 若PR #4尚未合并：在其当前head创建**独立M4开发分支**（如`codex/dev10-m4-system-evolution`），再同步最新main的本任务与最新开发规范；不要向PR #4原分支直接追加M4代码；M4 PR可暂以PR #4分支为base形成stacked PR，PR #4正式合并后再改base/rebase，不自动合并。
- 若PR #4已经由玩家另行批准合并：从最新main独立开M4分支。禁止Codex自己合并PR #4、M4 PR或修改正式游戏。
- 复用现有`gm_workbench.sqlite`、受控CLI、既有健康/诊断/执行回执。不要新开第二套游戏权威事实库、内存Executor、重做DEV14或建设自主管理平台。

## 2. M4-A 最小可用工程问题模型

复用M2/M3工作台存储方式，在**派生**工作台中增加最小必要的`development_issues`及可追踪的`development_issue_events`（若项目已有等价表则复用），而不是建独立主数据库。

事件/问题必须能够保留：
- 稳定`issue_id/fingerprint`，`category`，`title`，`first_seen/last_seen`，`occurrences`。
- `career_id`（若问题仅限某档）、`save_instance_id/generation_id/source_batch/run_id`（实际有才填）；系统级问题允许无档，不可伪造来源。
- `source_stage/producer`（CAPTURE, ACCESS, ANALYTICS, GM_INTERFACE, APPROVAL, EXECUTION, HANDOFF, MANUAL_RESEARCH等）和`affected_capability`。
- `evidence_refs`、精简`repro_steps`、`actual/expected`及来源支持的`confidence`，不能把猜测标为已实机确认。
- `severity`（P0/P1/P2，不自动取代玩家优先级）、`status`（OPEN/TRIAGED/DEFERRED/RESOLVED/DISMISSED）、`proposed_owner`、`next_review_trigger`、`related_issue_ids`、`player_decision_ref`（如有）。
- `scope/known_limits`、必要版本/修订号；更新历史不覆盖。
- 常见类别：DATA_CONSUMER_UNREADABLE、SOURCE_SEMANTICS_CONFLICT、SOURCE_STALE_OR_MISSING、DECISION_PACKET_MISSING_OR_STALE、NATIVE_FIELD_UNAVAILABLE、EXECUTION_CONTRACT_FAILURE、OPERATIONS_HANDOFF_FAILURE、DEVELOPMENT_FEATURE_CANDIDATE、OTHER_VERIFIED_ENGINEERING_ISSUE。

需要清楚区分证据事件与问题标题，多个批次同一根因能合并追踪（稳定fingerprint，不把batch当指纹唯一因子），但不同存档/身份或实质不同错误不能盲目合并。对重复输入提供幂等性或明确的occurrence策略，不把同一次导入算成多次故障。工作台更新用项目已有revision/事务做冲突保护。

## 3. M4-B 输入、最小诊断、分流

先实现一个**离线明确触发的导入接口**，接受小型`development_event.json`或有相同信息的既有结构化来源。不要求立即在采集、GM、分析和执行脚本里各添加大型hook。

允许从现有工具实际产生的以下工程证据采集（有则处理、没有明确NOT_OBSERVED）：
- 采集/发布的source_health、审计或已登记错误结果；
- M0消费者访问/查询错误与同批失配；
- M3的源包不可用、执行就绪/策略转换接口阻断（**只记录系统故障，不评价篮球方案优劣**）；
- DEV14离线规划/执行审批/回读回执里的工程错误与未支持对象；
- 人工明确输入的技术缺口或用户要求的新增能力。

只观察已存在的记录，禁止为发现问题主动运行正式采集、游戏访问、写入或无关脚本，也不准改写既有事实库/历史快照。事件没有真实证据时为RESEARCH/UNKNOWN，不使用“已复现”描述。

请建立受控有界CLI（可用建议名称`scripts/gm_development_feedback.py`，准确命令以实现为准）：`ingest`、`list`、`show`、`triage`（显式输入文件和expected-revision）、`export`。读取默认分页/上限，避免一次dump所有问题、员工或游戏源。系统可作分类/候选优先序建议，但不自动修bug、不自动生成需执行的PR、不自动批准项目、不自动关闭玩家DEFERRED状态。

**特定既有问题用作手工样例，而非修复授权**：GitHub Issue #6（DEV14完整Registry元数据中`world.contracts_and_finances.player_potential_factor`误判为球员Potential镜像）应该能够登记成一个`DEFERRED`开发候选，证据引用M3-T报告和Issue #6；该问题尚未修复，未来由独立开发模型处理，不许Codex在M4改`src/player_potential_mask.py`或额外重跑DEV14测试。

`DEV19 BPTI`与季后赛采集/年度引擎校准器可登记为`DEFERRED`状态、类别`DEVELOPMENT_FEATURE_CANDIDATE`的未来**规划任务指针**（规划状态仅存于roadmap说明，不新增PLANNED状态枚举），不得把它们冒充发现的BUG，不自动实现。

## 4. M4-C 跨模型交接和持续演化

为开发规划窗口输出轻量人类可读的`web_gm/development_feedback/CURRENT.md`及机器可读索引/导出（可采用该目录或已有等价路径）：
- 当前P0/P1/P2开放问题和已暂缓项（可读前N个、基于证据优先）；
- 问题ID/来源/首次、最近出现/重复次数/影响/证据路径/建议owner；
- 每项最小复现步骤、阻断范围、已知UNKNOWN、明确玩家决定；
- 链接原始GitHub Issue、代码/验收/来源证据，不复制巨大JSON/raw/内存地址/私密路径；
- 下次开发窗口阅读索引后，在**玩家主动触发开发规划时**提出最小必要的研究/实现方案、成本估算和任务书草案，并等待玩家批准开发。

GitHub是跨模型交流的持久化通道；M4 CLI默认写本地派生文件/待提交报告。**本任务可以提交M4代码/文档/合成示例到M4 PR，不得默认为每次运行自动push、创建Issue或触发Codex。**

不去评定GM的交易或战术是否取得理想比赛效果，也不比较两种比赛模拟统计；这些是其他独立模块的职责。

## 5. M4-D V4上线准备状态（只生成真实状态，不上线）

增加一个精简的**readiness/blocked report**，依据真实已有证据描述：
- M0–M3-T工程合同/代码是否就绪，PR #4是否实际合并；
- 三个Web消费者的真实连接是否已由玩家验证，未验证填PENDING；
- 真实已脱敏新生产批次是否存在与被GM消费，未知/不存在时PENDING；
- 30队真实研究/GSW-SAS-OKC无写入演练的证据是否存在，不存在时UNASSESSED/PENDING；
- Issue #6是否仍阻断真实full-registry采集，按真实状态说明；
- BPTI是用户明确的**正式新档前置工程**，但M4本轮**不实施BPTI**；
- 哪些事项属于玩家之后另行触发或批准的门。

只输出`M4_ENGINEERING_COMPLETE / GM_V4_NOT_ENABLED`等分别的状态。**不得自动把V3 SOP切到V4，不能把工程合成验收写成生产验收，不能直接启动球队经营或新档。**

## 6. 本次唯一授权的最小验证（仅合成/静态）

本轮明确授权以下5项直接相关的最小验证，不自行扩大：
1. 输入一条有真实样例结构的源错误事件 → 可存储、查询、追踪证据，不修改事实库。
2. 同一问题跨批重复与重复导入 → fingerprint、occurrences、历史及幂等行为正确；不同问题不混并。
3. 人工triage的状态/版本/玩家批准引用 → 无授权不会自动变RESOLVED/APPROVED，过期revision不覆盖。
4. 有界list/show和CURRENT小型导出 → 返回可追溯摘要、不包含大raw、内存地址或不应上传的敏感内容。
5. Readiness报告能将“PR #4未合并/GM V4未启用/真实连接待验收/Issue #6待修”如实显示，不伪称READY。

将Issue #6作为合成/离线导入样例，不进入本次底层修复。若以上授权测试通过，不追加测试文件、重跑同一组、全量旧M3集合或DEV14 119项。需要任何**新增设计/扩展测试/额外回归/新的技术模块**先说明范围、原因与预计成本，征得玩家明确批准再做；若测试样例本身写错，仅修必要样例并对受影响项做定向复验，原已通过项不重跑。

## 7. 交付要求与停止点

- 独立M4分支、独立Draft PR，不合并，不改PR #4。
- 完成可运行M4工程（Schema/存储/API或CLI/报告导出/最小已授权验证），不只写设计。
- 同PR提交README/CLI用例、`docs/development_reviews/M4_SYSTEM_EVOLUTION_IMPLEMENTATION_AND_ACCEPTANCE.md`和更新必要的docs/33/34/AGENTS.md状态索引；尽量增量追加，避免重写旧历史。
- 报告真实source、commit、已运行测试、缺失、未来需要玩家触发的条件和本次未做内容；工程功能完成后停在`M4_ENGINEERING_COMPLETE_AWAITING_PLAYER`。
- 不修Issue #6；不写BPTI；不开发季后赛抓取或模拟滑块调校；不做正式游戏运行/写入、采集、发布、真实GM回合、GM V4切换或自动合并。
- 不启动下一阶段；后续正式开档的BPTI、Bug修复和数据校准由玩家单独授权。

## 8. 必读文件

- 最新`origin/main/AGENTS.md`、`docs/DEVELOPMENT_BOUNDARIES_AND_VALIDATION_POLICY.md` V2、`docs/33_DEVELOPMENT_BASELINE_PROMPT.md`、`docs/34_BASELINE_CURRENT_STATE.md`；
- `docs/development_tasks/DEV_20261018_10_GM_V4_SQLITE_FIRST_MASTER_PLAN_V2.md` §D/运营反馈规则/V4门；
- `docs/development_tasks/DEV_20261018_10_GM_V4_FOUNDATION_DECISION_OBSERVABILITY_MASTER_PLAN_V1.md` §7（旧GM反馈段落按本任务覆盖）；
- `docs/development_reviews/M3_T_IMPLEMENTATION_AND_ACCEPTANCE.md`、`web_gm/manuals/GM_M3_TACTICAL_WORKBENCH.md`（PR #4分支）；
- `docs/development_tasks/DEV_20261020_19_BPTI_BASKETBALL_PHILOSOPHY_AND_TACTICAL_INTELLIGENCE_MASTER_PLAN_V1.md`（BPTI任务隔离和正式开档门）；
- GitHub Issue #6：https://github.com/chris2gao/nba2k22-gm-engine/issues/6 。
