# NBA2K22 VAE Stage02 — 机制与比赛指标证据整合完成指针

**Task:** NBA2K22-VAE-STAGE02-MECHANISM-METRIC-EVIDENCE-20261101-001  
**Role:** execution · **Model:** GPT-6（会话声明，非平台签名证明）  
**Branch:** `task/nba2k22-vae-stage02-mechanism-metric-evidence-20261101`  
**Dispatched SHA:** `f27846c86e92345e279ad01816593d909595f472`  
**Pre-closeout verified content HEAD:** `7340552eef77fa130bf62c3229c261b45d77fdc0`。最终发布SHA应以随后GitHub远端真实branch HEAD为准，无法在同一提交内自引用其自身SHA。

## M1–M5交付

- M1: `02_证据/DUAL_STREAM_SOURCE_RECONCILIATION.md`、`06_执行/field_evidence_matrix.json`。固定204个ID：99球员倾向、86世界设置、19教练字段；以queue `6436515330f77c0cc5cc675b521590adeb69c5d4` / blob `af5567e14e03cd9f7761e396a978311e347d7c17`为正典。
- M2: `06_执行/mechanism_metric_links.json`：68个分层节点，50条带条件、来源SHA/路径、竞争假说及反证方法的有向边。0条新增已证比赛因果边。
- M3: `06_执行/metric_native_first_requirements.json`：38个指标语义需求、16组设置→行为→指标映射。**原生游戏计算优先**；当前Reader缺失不构成游戏不存在，不开展默认自算。
- M4: `06_执行/data_source_gap_matrix.json`：38条来源缺口；16项有旧存档Reader候选、4项仅代码/Schema、9项Human UI类别候选、9项需原生发现。旧WorldData v24的100表/1775列/20家族与当前MC数据严格区分。
- M5: `06_执行/pilot_experiment_contracts.json`：3个S0/S1/S2实验语义合同（Shot/Touches/POE，Tempo/轮换，HelpDefense/防守），均未运行、无Setter授权、无新采集器/DDL。
- 测试：`07_测试执行/verification_receipt.json`；九项M01–M09前发布静态门均PASS，正式远端发布回读另在会话中核验。

## 来源限制与风险

- GPT Sweep 1: `f3233d285300ac40933b04e8086cf631fad46fbb`，204/204外部单字段研究；51条确切无直接Native身份来源标记，24处元数据缺口、3条ledger来源计数偏差、15项非统一顶层冲突字段需保留。
- Gemini: `6f8dfe23c3c3d4d64ee64117620233fcdfcaebfe`，原始图16节点13边、三项效果仍待比赛验证。其自行声明的LIVE_RECEIPT、角色Branch C、Tempo和统计派生建议均未升格。
- 独立再审: `08ace12bcf92faaef20634c4701b7d6a03876a34`，`REWORK_REQUIRED_WITH_SUBSTANTIAL_PROGRESS`，3 P0（真实PE取证、Branch C/五能力证据覆盖、历史原始收据），4 P1、2 P2尚未闭合。
- WorldData v24候选: `17ec1cea88c2bb6c36264792f70c94bef9a8bdb4`，有旧存档Native Box和赛程读取，却未认证PC22当前Player Card全部Advanced/Per Game逐场字段。
- 术语限定：USG% != Touches；原生Pace != 基础Box估计Possessions；FGA/36 != 真实出手决策率；Normalize Stats != Normalize Played Minutes；3D CPU-vs-CPU != Calendar SIM；同offset不同Slot并非同字段。
- 三个实验均只设计。当前窗口没有进入游戏、开启REA修改、运行采集器、建立SQL、改变主线、合并master或固定D系列格式。

## 阶段完成门

**执行交付状态：`EXECUTION_DELIVERED_READY_FOR_INDEPENDENT_REVIEW_WITH_EVIDENCE_GAPS`**。结构完整性通过；Native PE来源、当前统计逐项存在性、游戏因果与效果成熟度均未独立验证。交Human/规划总线固定本次最终分支HEAD，Fork新的 `independent_review` 审核岗位。后续D1–D5仅在独立审核和Human决定后开展原生数据发现与Reader缺口收敛。

GitHub API publication: expected branch HEAD 7340552eef77fa130bf62c3229c261b45d77fdc0, non-force compare-and-swap, only this Run path; API transport local hooks NOT_APPLICABLE, equivalent remote scope and ref gates executed.

## Human 补充原则的后续证据治理（2026-11-01）

原有完成状态与固定审查对象不变。
长期闭环：**原生游戏数据 → 模型分析与候选设置 → 经授权 REA 原生执行、即时独立读回 → 正常游玩或模拟 → 未来统一采集器追加新原生数据 → 检验支持/反驳/不可判定 → 版本化机制修正 → 下一轮**。

- 未知字段可继续作为单变量、有输入/竞争解释/可观察 Native 指标/证伪条件的实验建议；**无需全部204项先行理论证明**，但也不得自动批准写入或证明作用。
- Native Game Log、Advanced、Per Game 已计算结果优先于任何同名自算值；旧 Reader 未采集不等于游戏没有。后续只在另行授权的数据任务中扩展**既有统一采集体系**，不在本任务增加采集器。
- 多成熟度共存：已证部分可以在其真正获授权的运行场景中使用；未知部分保留 `NEED_EVIDENCE` / `EXPERIMENT_PROPOSAL`；当前 Stage02 不启动 VAE 或游戏操作。
- 新真实比赛证据可能支持、反驳、或无法判定。每次保留原始值、来源、存档、模式、时点及先前假说；相关不自动升格因果，旧事实不能被覆盖。

本次是同一任务原 Run 文件内的追加式版本修订，不代表前次独立审核已进行、游戏已操作、任何 Setter 被授权，或未来自动采集已上线。最终修订提交以远端最新分支 HEAD 为准。

## 2026-11-01 独立审核后定向整改补充

独立审核 `553ee3af68dba5cd42e52969e739ab0748989faa` 裁定2 P0、2 P1、2 P2，执行原窗口按其S02-P0-01至S02-P2-06交付有证据等级限定的整改，正式详情在 `02_证据/INDEPENDENT_REVIEW_REMEDIATION_MATRIX.md`。

- 修订 M3/M4 全部16项旧Reader过高标签；7项空值列、2项Join未验、1项公式派生PTS、4项球员fixture Box、1项时期fixture、1项属性混合来源；余22项原分类保留。
- M2原15个可观察指标Bundle全部有真实指标ID与粒度；三条图路径固定；12个孤立节点列出研究边界。
- M1 原GPT 24/3/15异常与51项NO_DIRECT结果固定源级逐字段索引可查询。
- 旧M09已明确为发布前门与此前实际发布SHA两类收据；本次最终新SHA在提交之后通过远端独立查询确认。
- Human长期闭环与3个未执行试验不变；无新Native/当前游戏证明、实机试验、采集器或物理SQL。

**本次执行修订状态：`EXECUTION_REWORK_DELIVERED_PENDING_INDEPENDENT_REREVIEW`，需独立复审重新裁定。**
