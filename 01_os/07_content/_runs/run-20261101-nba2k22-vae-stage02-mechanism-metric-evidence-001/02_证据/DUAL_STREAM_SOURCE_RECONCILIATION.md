# M1 · GPT 204项与 Gemini REA 双流证据对账

**任务**：NBA2K22-VAE-STAGE02-MECHANISM-METRIC-EVIDENCE-20261101-001。Role execution，模型 GPT-6（会话声明，非平台签名）。

## 固定来源与差异

- Seed: 6436515330f77c0cc5cc675b521590adeb69c5d4，blob af5567e14e03cd9f7761e396a978311e347d7c17；204 = 99 Player Tendency + 86 World + 19 Coach，正典身份只用 `field_id`。
- GPT: f3233d285300ac40933b04e8086cf631fad46fbb，204份独立档案／204条ledger。外部来源研究 204/204 不意味着 204 次 PC22 原生读取；51条 `NO_DIRECT_NATIVE_FIELD_IDENTITY_SOURCE`；24个历史来源元数据缺漏（版本21、日期3）、3条来源计数差异和15份档案非统一顶层冲突字段需保留。
- Gemini: 6f8dfe23c3c3d4d64ee64117620233fcdfcaebfe，原 Run 有204字段档案，ledger 1441 行，源中有“LIVE_RECEIPT”自述；最新每字段 ledger 值、候选 Getter/Slot/读取地址被保存在矩阵的 `gemini` 分轴，**不提升为独立验证**。
- 独立再审: 08ace12bcf92faaef20634c4701b7d6a03876a34，`REWORK_REQUIRED_WITH_SUBSTANTIAL_PROGRESS`，3 P0、4 P1、2 P2。
- WorldData: 17ec1cea88c2bb6c36264792f70c94bef9a8bdb4，v24，100张表/1775列/20 Reader，旧存档有原生Box、节比分和赛程记录；并非当前MC存档或Advanced全页认证。

## Gemini P0 不得被遮盖

1. PE原始可执行文件与连续字节来源未通过独立认证。候选hex自校验不能证明指定可执行文件的原始字节。
2. 所谓角色Branch C与五个属性乘数不在提交的136字节指令片段完整覆盖内；不能将Role Tier→FGA压制视为已验证Native规律。
3. 204份Gemini历史记录含早期时间戳/uint32位模式被解码值覆盖风险，必须引用原始旧Git blob和追加修正记录。

## 一致性与命名冲突

- `TENDENCY_NATIVE_001` 固定Key `tendency.SHOT_TENDENCY`，Gemini Key `tendency.ShotTendency`；`TENDENCY_NATIVE_066` 固定Key `tendency.TOUCHES_TENDENCY`，Gemini Key `tendency.TouchTendency`。保留别名，**不得字符串JOIN**。
- `COACH_DEFAULT_014` 是Tempo，不是 `COACH_DEFAULT_005`（POEDefense2）；`COACH_DEFAULT_004` 是POEDefense，非02；这次用种子队列程序固定。
- `WORLD_REG_085` 的0x00在 SLOT_SLIDERS 与 `WORLD_REG_086` 的0x00在 SLOT_SETTINGS，偏移相同并不证明一个物理字段；`world.*` 与 `settings.*` 在同slot候选也需要可追溯别名验证。
- Gemini图16节点13边，末端3个比赛结果关系仍待验证；Tempo公式中的10/70是经候选字节静态运算的数学结论，不代表在本次PC22真实比赛中证实该控制器语义。

## 分轴证据政策

FIELD_ID_OR_REGISTRY、UI_SEMANTIC、NATIVE_IDENTITY、NATIVE_CONSUMER、GAME_OUTCOME 五轴独立。未经核对的Gemini Live证据只保留“开发者声称”的来源等级。对没有竞技直接作用的财务/合同/交易字段不强配FGA；所有 `proposed_metrics` 只是后续数据需求候选，不表示机制已经导致结果。

**本M1输出**：`06_执行/field_evidence_matrix.json`，204条队列顺序、候选数据、GPT/Gemini证据指针、审查风险与指标关联。下一M2–M5使用该矩阵而不修改原任务来源。

## 2026-11-01 · Human 长期研发原则补充（不扩大 Stage02）

来源：Human 在本任务窗口的直接补充指令（会话来源，首次由本次 Git 提交持久化；不是旧任务既有批准事实）。正式执行边界仍以原 task packet / dispatch 为准。

长期闭环：**原生游戏数据 → 模型分析与候选设置 → 经授权 REA 原生执行、即时独立读回 → 正常游玩或模拟 → 未来统一采集器追加新原生数据 → 检验支持/反驳/不可判定 → 版本化机制修正 → 下一轮**。

- 未知字段可继续作为单变量、有输入/竞争解释/可观察 Native 指标/证伪条件的实验建议；**无需全部204项先行理论证明**，但也不得自动批准写入或证明作用。
- Native Game Log、Advanced、Per Game 已计算结果优先于任何同名自算值；旧 Reader 未采集不等于游戏没有。后续只在另行授权的数据任务中扩展**既有统一采集体系**，不在本任务增加采集器。
- 多成熟度共存：已证部分可以在其真正获授权的运行场景中使用；未知部分保留 `NEED_EVIDENCE` / `EXPERIMENT_PROPOSAL`；当前 Stage02 不启动 VAE 或游戏操作。
- 新真实比赛证据可能支持、反驳、或无法判定。每次保留原始值、来源、存档、模式、时点及先前假说；相关不自动升格因果，旧事实不能被覆盖。
- 具体机制证据分轴见 `field_evidence_matrix.json`，反馈状态见 `mechanism_metric_links.json`，Native First 见 `metric_native_first_requirements.json`，原生读写缺口见 `data_source_gap_matrix.json`，三个后续试验门见 `pilot_experiment_contracts.json`。

**Stage02 M1–M5 原交付文件、204 / 68 / 50 / 38 / 3 范围以及未运行边界不变。**

## 独立审核后的字段级异常与来源可用性修订

以上原对账保留为历史；现行详细来源成熟度在 `06_执行/data_source_gap_matrix.json`，GPT历史字段级异常在 `06_执行/gpt_source_anomaly_index.json`。2026-11-01独立审核 `553ee3af68dba5cd42e52969e739ab0748989faa` 的2P0/2P1/2P2定向整改及静态回执见 `02_证据/INDEPENDENT_REVIEW_REMEDIATION_MATRIX.md`。旧“已确认Reader=16”说法已废止。
