# NBA2K22 VAE Stage02 · 机制—比赛指标证据整合执行合同

> Human批准：2026-11-01；发布岗位 `OS_PUBLIC_DEVELOPMENT_PLANNER` (`decision_architecture`)；本文件为**执行派单**，不是开发完成回执。
>
> **任务 ID**：`NBA2K22-VAE-STAGE02-MECHANISM-METRIC-EVIDENCE-20261101-001`
>
> **执行岗位**：`execution`；**建议执行模型**：GPT-6（公共基线 Fork；不需要本地游戏访问），实际执行模型由后续 Run 回执登记。
>
> **工作分支**：`task/nba2k22-vae-stage02-mechanism-metric-evidence-20261101`；**精确基线**：`45cc45cae0550ddcda192a2179ea48509b27f6ee`。
>
> **唯一允许写入范围**：`01_os/07_content/_runs/run-20261101-nba2k22-vae-stage02-mechanism-metric-evidence-001/`。不改 master、Core、其他研究分支或其它 Run。远端发布为普通任务分支，**不自动合并**。

## 1. Human 裁决与任务目的

MC 单机化插入任务已结束，恢复 VAE 主线。先做 **Stage02 M1–M5 机制及其比赛指标的证据整合**，再单独组织数据研究和采集完善。

**最高优先级原则：原生已计算统计优先（Native-Computed First）**。

Human确认 NBA2K22 球员档案页除了基本 Box 之外，还展示**丰富的高阶数据和逐场数据**。这是当前的 `HUMAN_REPORTED_UI_PRESENT` 发现线索；在没有特定页面/Native Reader 同步证据前，不把任何*具体字段*自动升级成 `NATIVE_READER_VERIFIED`。

检索指标时按以下次序确定采集需求：

1. **寻找游戏已计算的该指标**：优先当前 PC22 本世代原生球员卡逐场/高阶页，及球队、联赛统计页、比赛记录、其它Native对象与Getter。记录实际显示标签、字段归属和数据粒度；本轮无法实机验证时明确下一数据任务需核查的入口。
2. **查已有读取能力**：WorldData v24 Reader、原版 Player Card/Statistics 研究文档、REA Native Getter或其它证据。把 `game_native_exists` 与 `existing_reader_available` 当成**两个独立事实**。
3. **若游戏已有，但当前 Reader 未采集**：归类为 `NATIVE_FOUND_READER_GAP` 或 `NATIVE_CANDIDATE_READER_GAP`，给下一个数据任务提出定位/读取需求。**不得因为采集器缺失就改为计算派生指标。**
4. **若在界定范围内确认游戏本身没有该统计指标**：可提出 `DERIVED_FALLBACK_PROPOSAL`，说明基础输入、算法、单位、可比性、误差和适用模式；不在本轮实施新的计算器。
5. **来源仍不确定**：标注 `NATIVE_DISCOVERY_REQUIRED` / `UNKNOWN`；不编造UI入口、Native位置、Getter、字段公式。

**禁止将 Box Score 视为统计数据的全部；禁止用外部NBA.com追踪类指标的存在推定 2K22 本身也有；禁止将“当前采集器没采到”写成“游戏没有”。**

## 2. 必读源：精确SHA、真实成熟度与工作边界

先执行 Core OS 开机入口（远端 Core/NBA master SHA、AGENT_WORKING_DISCIPLINE、AGENTS、OS README、开发入口规范），并读取本 Run 的 `run.yml`、`01_任务输入/task_packet.json`、`01_任务输入/verification_plan.json`。

- **唯一204字段种子队列**：`6436515330f77c0cc5cc675b521590adeb69c5d4` 的
  `01_os/07_content/_runs/run-20261030-nba2k22-vae-stage01-001/01_任务输入/VAE_FIELD_INVENTORY_SHARED_V1.json`；blob `af5567e14e03cd9f7761e396a978311e347d7c17`。共 **99 tendency / 19 coach / 86 world**；同名或相同offset不构成相同物理字段。
- **GPT外部研究 Sweep1** `f3233d285300ac40933b04e8086cf631fad46fbb`：
  `01_os/07_content/_runs/run-20261030-nba2k22-vae-gpt-external-single-field-loop-001/`。
  204份字段档案、总结、审计及Gemini只读交接。51个明确 `NO_DIRECT_NATIVE_FIELD_IDENTITY_SOURCE` 不意味着剩余153项已认证；24项来源元数据缺口、3条ledger/档案来源数差异、15个非统一冲突字段不能消失。
- **Gemini REA候选** `6f8dfe23c3c3d4d64ee64117620233fcdfcaebfe`：
  `01_os/07_content/_runs/run-20261030-nba2k22-vae-rea-single-field-loop-001/`。
  重点 `02_证据/MECHANISM_RELATIONSHIP_GRAPH_V1.json`、`TELEMETRY_VALIDATION_CONTRACTS_V1.json`、`NATIVE_DISASSEMBLY_FORENSIC_RECEIPT_V1.json`、204字段记录和代码。
- **Gemini集中整改独立复审** `08ace12bcf92faaef20634c4701b7d6a03876a34`：
  `01_os/07_content/_runs/run-20261031-nba2k22-vae-sweep5-remediation-independent-rereview-001/08_结论/consolidated_sweep5_independent_rereview.md`。
  结论为 **`REWORK_REQUIRED_WITH_SUBSTANTIAL_PROGRESS`**，P0/P1未闭合；原始PE字节来源认证、角色控制完整分支及历史回读等不能视为已证。
- **既有游戏机制知识库** `094f1aa641f93dec2277707ad9dbf5bdb0341247`：
  `08_Domain_Applications/Antigravity_GM_Engine/docs/game_mechanics/`，尤其 `guides/K01_K02_GAME_STATS.md`（Game Logs/Box/高阶统计）、`guides/K03_K12_PLAYER_PROFILE_AGENCY.md`（倾向/Touches等）、`guides/K04_COACH_AND_PLAYS.md`（POE/ACE/Playbook/Freelance）、`guides/K05_K10_K11_WORLD_RULES_SIM_HISTORY_SAVE.md`（3D vs 日历Sim/Normalize）。
- **Gemini旧集成稿** `803183ca0fd8d5512df602b31c864cadcd72abf8` 的 `PER_SETTING_MECHANISM_DOSSIER_V3.md` 可作假说资料；其“精确体能损失阈值/ACE必定覆盖”等未证内容不得升级。
- **WorldData v24 候选** `17ec1cea88c2bb6c36264792f70c94bef9a8bdb4`：
  `08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype/BASELINE_HANDOFF.md`、`field_dictionary.json`、`source-coverage.json` 及只读 Reader。候选基线100表、1,775列、20家族；**并非完整数据需求、当前真实存档或所有原生高阶统计字段已采集的证明**。
- **先前 Stage02 资料规划** `190044b49e1867e07882ad48a94e553233fc571f` 的 `VAE_NEXT_PHASE_MECHANISM_DATA_INTEGRATION_PLAN_20261031.md`；历史Codex G01–G03阶段任务 `90f42546b2e6d17bd52f28f3e9b26342888a4bcc` 已 `deferred`，不得继承其“已执行”身份。

所有来源文件按其当时固定SHA读取；无明确证据不得用最新版无引用文件替换已冻结审计对象。

## 3. 执行包 M1–M5（同一个长任务）

### M1 · 204字段双线证据表

对固定队列**全部204个 `field_id`** 建立一条独立条目，保持队列顺序：字段/原生候选、语义、数据类型/枚举、GPT外部论据与冲突、Gemini读取/Opcode/消费者候选、独立审核限制、适用模式、已知交互、比赛行为假设、可测指标、未知缺口。

记录**分轴证据等级**而非单个“verified”：
- `FIELD_ID_OR_REGISTRY`: 静态库存名；
- `UI_SEMANTIC`: 真正PC22同版本UI语义证据；
- `NATIVE_IDENTITY`: 对应存档/对象/地址/类型读取证据；
- `NATIVE_CONSUMER`: 实际调用与消费者静态/动态线索；
- `GAME_OUTCOME`: 比赛可观测关系与受控因果级别。

所有轴可独立为 `UNKNOWN` / `CANDIDATE` / `STATIC_DISASSEMBLY_LEAD` / `LIVE_RECEIPT_CANDIDATE` / `INDEPENDENTLY_VERIFIED` / `PENDING_GAMEPLAY_VALIDATION` 等合适标签。**不要用来源自己写的 `LIVE_RECEIPT` 标签覆盖独立复审。** 不属于竞技影响的世界财务/交易字段标 `NO_DIRECT_GAMEPLAY_METRIC_IDENTIFIED`，不要硬配某项Box数据。

### M2 · 分层机制图

使用 `field_id` 为唯一正典身份，并另行记录Project/Native别名。关系节点至少分为 `SETTING` / `CONTEXT` / `GAME_BEHAVIOR` / `NATIVE_CONSUMER_CANDIDATE` / `OBSERVABLE_METRIC`。

每条边具备方向、条件、竞争假说、证据层、精确来源SHA+路径、反证方式；可标 `UNRESOLVED` 不凑数量。

重点检查：
- `TENDENCY_NATIVE_001` Shot、`TENDENCY_NATIVE_066` Touches、PlayTypes、角色层级、Run Plays、POE、Freelance、ACE → 球权与出手选择。
- `COACH_DEFAULT_014` Tempo、`COACH_DEFAULT_001..006` POE、`COACH_DEFAULT_010/013` 轮换、世界比赛时长与Normalize → 节奏、效率、疲劳。
- `COACH_DEFAULT_015` HelpDefense、防守POE、个人防守倾向与防守属性 → 护框、协防、对手三分/禁区出手、篮板。
- `COACH_DEFAULT_016..019` 四个有序Freelance、Playbook和战术实际执行与ACE覆盖。
- 3D CPU-vs-CPU、Calendar SIM、User-vs-CPU分别建适用条件；没有共同引擎证明时不能合并效果。

已有Gemini图只有16节点/13边，三条到比赛效果的边 `PENDING_GAMEPLAY_VALIDATION`。新图可以扩展“待证假说”而不是虚构新认证。

### M3 · 设置 → 游戏行为 → 比赛指标矩阵（Native-First）

按机制分类形成 `Action/Setting → Information → Field → Behavior → Metric → Evidence` 的可查询需求。

至少覆盖这些现象：
1. 核心FGA不足 / Usage不均；
2. Touches和Shot争议；
3. 三分总量与Spot Up/Off Screen区别；
4. 突破、造犯规、禁区与中距离；
5. Post Up和挡拆Roll/Pop；
6. POE进攻重点、Playbook实际调用和Freelance；
7. Tempo/Pace与转换进攻；
8. BenchDepth/Utilization、轮换、疲劳；
9. HelpDefense、POEDefense、个人盯人与协防；
10. 护框/禁区保护与外围漏防；
11. 对手失误制造与防守施压；
12. ORB/DRB与退防取舍；
13. 3D和日历Sim是否同方向；
14. World模拟统计与游戏时长/Normalize口径；
15. 其它有明确来源的可测关联。

每个MetricRequirement包括：
- 精确定义、单位、归属主体（game/team/player/possession/shot/period）、单场/逐节/赛季/长期粒度；
- **优先原生路径**（Player Card的具体待核Tab、Game Log、Advanced、Team Stats、Native Getter/世界Reader），**已证明/仅Human报告/待定位**分别标识；
- 如有：已有Reader路径与字段、绑定游戏构建/存档/来源类型、数据新鲜度和可用状态；
- 若目前找不到：后续数据任务的*调查步骤*，不能跳过直接写公式；
- 若已证明原生不存在：仅列派生候选及输入、适用条件和误差说明；
- 区分动作事件、传统Box、游戏原生高级统计、外部计算代理、实时状态；不将USG%当Touches、不将FGA/36当真实投篮动作频率、不把估算Pace当原生Pace；
- 可比控制：分钟、出场、对手、阵容、伤病、比赛版本、比赛模式、赛程阶段、Quarter Length、Sim Quarter Length、Normalize Stats 和 Normalize Played Minutes（若实际可读）、ACE临场覆盖。

**游戏原生已计算值优先于自算同名指标**，因为游戏高级数据的定义/舍入/统计口径可能与篮球常用外部公式不同。若可选的外部公式不同，必须分别命名并标 `ESTIMATED_PROXY`，不能覆盖原生值。

### M4 · Data-source差距表，不做采集工程

只做现有数据能力和下一个数据任务的需求差距清点：

- `GAME_NATIVE_CALCULATED_CONFIRMED`（有明确游戏内/Native证据）；
- `HUMAN_REPORTED_GAME_UI_CANDIDATE`（确认有这一类页面，具体字段未认证）；
- `WORLDDATA_READER_CONFIRMED_ON_OLD_SAVE`（固定旧存档验证）；
- `SOURCE_CODE_OR_SCHEMA_ONLY`；
- `NATIVE_FOUND_READER_GAP`；
- `NATIVE_DISCOVERY_REQUIRED`；
- `DERIVATION_ONLY_AFTER_NATIVE_ABSENCE`；
- `UNKNOWN`。

优先列出球员卡逐场Advanced/Per Game、Game Log、分区投篮、球队高级统计、原生比赛数据、教练和防守状态等**候选调查入口**，逐项附带缺失来源证据和下一轮只读Reader/Getters的最低判定要求。

输出用于后续D1–D5/WorldData的**语义信息需求合同**，不得冻结SQLite DDL、日志物理格式，不得修改旧v24采集器或新建平行数据库。

### M5 · 首批三个小规模实验合同

仅设计，不执行。优先：
1. Shot + Touches + Coach Run Plays/POE/Freelance → 球权/出手份额；
2. Coach Tempo + POE + 轮换 → Pace/转换/体力/效率；
3. HelpDefense + 防守POE + 个人防守 → 护框/协防/对手投篮结构。

每份包含：假设、竞争解释、目标字段（正典 `field_id`）、可核实Native入口、优先游戏已计算指标、必要基础指标、数据可得性状态、最小实验单元、S0前值、S1 REA修改及即时独立回读方案、S2若干后续真实比赛、3D与日历Sim分层、对手/阵容/分钟/伤病/Normalize/ACE控制、成功/失败/不确定判定。

在没有真实样本、身份和对照时，输出 `NEED_EVIDENCE` / `INCONCLUSIVE`，不输出“调高X必增加Y”的生产规则；本轮不授权任何Setter或实际游戏实验。

## 4. 交付物和位置

只在 `01_os/07_content/_runs/run-20261101-nba2k22-vae-stage02-mechanism-metric-evidence-001/` 下发布：

| M | 必须交付文件 | 内容门 |
|---|---|---|
| M1 | `02_证据/DUAL_STREAM_SOURCE_RECONCILIATION.md` + `06_执行/field_evidence_matrix.json` | 精确204条、各证据轴、源SHA、冲突与未证事项 |
| M2 | `06_执行/mechanism_metric_links.json` | 有向关系、条件、等级、反例，禁止无出处Native结论 |
| M3 | `06_执行/metric_native_first_requirements.json` | 原生指标优先、具体数据粒度、计算仅后备 |
| M4 | `06_执行/data_source_gap_matrix.json` | 已有/未见/Reader缺口与下一D系列候选入口 |
| M5 | `06_执行/pilot_experiment_contracts.json` | 三个受控实验计划，未执行；用户实测与模型推断分开 |
| 测试 | `07_测试执行/verification_receipt.json` | Python确定性检查与抽样源级语义审查 |
| 收尾 | `08_结论/completion_pointer.md` + `run.yml` | 最终远端SHA、完成边界、独立审核候选与后续数据任务建议 |

允许附加少量**真正必要**的脚本用于确定性测试，但只准在本 Run 内；不重复搭建 OS 验证框架或大规模新代码。

## 5. 核验与完成门

执行并留下可重复结果：

- `M01` 固定队列所有204个ID均唯一、顺序一致、99/19/86家族数一致。
- `M02` GPT、Gemini、独立审核、旧WorldData来源SHA绑定，关键冲突显示而非覆盖。
- `M03` 证据等级无越级；PE/REA争议P0仍开放，不推出204项游戏效果认证。
- `M04` 所有Metric需求含Native-first发现/候选路径及Reader独立状态；不得默认自算。
- `M05` 数据粒度（single game / period / season）、3D vs Sim、两个Normalize概念不能混淆。
- `M06` WorldData v24候选覆盖与游戏实际拥有的数据分开标记。
- `M07` 三个实验合同可证伪、含混杂项和不确定结论。
- `M08` 没有游戏/REA写入、采集器改动、物理数据库锁定、自动调参部署。
- `M09` 任务分支上新改动只在允许的Run；非force发布，GitHub远端读回一致。

交付验收分层：**结构和需求完整性**可到PASS；**Native读取、真实游戏对照和改善效果**保持NOT_RUN或UNKNOWN，直到未来获准的独立数据与实测任务。交给全新 `independent_review` 岗位复核；Human决定后续是否正式接受。

## 6. 给下一执行窗口的明确指令

你是从 `NBA2K22_COMMON_BASELINE` Fork 的**独立执行岗位**，不承担主线规划或独立审核。先读OS入口与本 Run 状态，查远端任务分支最新HEAD，然后连续完成M1–M5和测试，不因一个单字段`UNKNOWN`停止整个任务；日志标明局部缺口并继续。

**本任务不要求 Human 逐步确认，已授权的内容研究与任务分支提交可直接完成。** 遇到新增重大语义裁决、修改游戏/存档、跨任务写入、master合并或其他真正保护边界，停止相关动作并交回 Human。

不要假装已经读取了用户当前游戏的高级统计数据；本轮的重点是**准确提出应该去游戏哪里找、怎样验证这些原生数据以及为什么它们可以观测某种行为**。机制模型先到可审查状态，数据实际采集与完善在下一个独立任务。
