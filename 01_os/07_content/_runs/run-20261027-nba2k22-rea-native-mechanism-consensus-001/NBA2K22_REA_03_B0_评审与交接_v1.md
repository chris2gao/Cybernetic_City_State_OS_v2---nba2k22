# NBA2K22 REA 原生机制逆向 · 阶段03结果模型 B0-v1 评审草案

状态：**阶段03模型草案，尚未由 Human 精确版本批准，也未独立工程复验**。2026-10-27。主模型：`NBA2K22_REA_03_B0_结果模型_v1.yml`。

## 版本与阶段身份

- 任务：`NBA2K22-REA-NATIVE-MECHANISM-DISCOVERY-01`；规划分支：`task/nba2k22-rea-native-mechanism-consensus-20261027`。
- A0-v1：Blob `8bd15794ad0f8b9b06363e4a04b7f806c4c55acd`，Human已批准。
- A-v1-RC01：Blob `9bcf28bd2bb3283f61bd79b07ba04b88af721c93`，Human已批准。
- 阶段02结论：**Human已批准 `partially_supported`**。作为GitHub上的准确批准载体，已写入 `02_阶段02Human正式确认与03准入记录_20261027.md`，提交 `097627969335abc275f37bdefe533aa37bc112ff`。
- 阶段02可行性证据：`36c216429d8ae1a300a6e7b88243e72879f5eda8`；原子证据：`d16ab7c91d2124d943866e3f070ab304a3963884`。
- **仓库同步状态：阶段02批准记录已上游，阶段03草案因随后仓库写入被拦截暂未同步。这一文件是本地可交接结果，不是GitHub提交版本。**

## B 实现即 A 满足：七项结果形态 + 方法类型

| A结果项 | B的可观察成果 | 建模的实现方法类型 | 真正验收边界 |
|---|---|---|---|
| RES-REA-01 | 机制图谱与三条代表机制记录，主张—原始证据可追踪 | 结构化目录/文档 | L1类型不自动升级为L2函数、L3行为 |
| RES-REA-02 | 一枚徽章深入 + 第二枚轻度对照 | 研究证据档案 | 能证明具体阈值就记录，否则提交有界UNKNOWN |
| RES-REA-03 | 一项教练进攻或防守设置深入 + 另一侧轻度对照 | 研究证据档案 | UI/存储/消费/实际生效严格分开 |
| RES-REA-04 | 交易验证与提交的函数角色、状态与关联对象影响清单 | 研究证据档案 | 没有完整事务路径就不得称“原生交易已可执行” |
| RES-REA-05 | 1–2个**有条件**原生调用PoC的真实凭据，或明确未执行/阻断报告 | 将来授权的受控实验流程与结果单 | 先教练后交易，调用必须另获精确Human许可；未执行绝不算成功 |
| RES-REA-06 | 五路线取舍及保留旧获批执行架构的变更提议 | 架构决策矩阵/文档 | 探索不自动改原交易/签约方案 |
| RES-REA-07 | 原始证据、负例和审查状态可重放的交接包 | 机器清单/审核记录 | 同一个Codex任务的多份文件不算多个独立游戏实测 |

每项B对象均有 `observable_end_state`、`required_fields`、`accepted_dispositions`、`failure_visibility`、`relations`、`basis` 和 `success_criteria`。结果形态与方法类型分别建模，未把脚本、SQL表结构或函数ABI当成用户批准的业务需求本身。

## 对象关系和独立状态维度

对象关系：`MechanismAtlas → M1徽章/M2教练/M3交易档案`；`Mechanism → Claims → 原始Evidence`；`候选原生函数 → 资格检查 → 具体授权 → 执行凭据 → 新鲜读回 → 独立复核`；`ArchitectureDecision → 三机制实证 + 已批准旧方案`。证据记录采用引用，不因不同归档文件而制造“独立双源”。

关键状态**不合并为一个万能Complete**：

- `proof_level`：L0资料线索／L1原生布局／L2静态函数／L3同模式真实行为／L4经批准的实际代表调用与新采读回；L5正式生产集成不属于本轮。
- `research_disposition`：开放、已支持到具体范围、被反证到具体范围、有边界未知、不适用本构建。
- `callability`：未评估、仅候选函数、缺少上下文、具备未来测试前提、不可安全调用、有边界未知、有实际凭据。
- `authorization`：无、已提议、Human针对具体动作授权、拒绝、过期。
- `execution`：未执行、开始、异常中止、已报告完成；**执行状态不等于验证状态**。
- `verification/review`：无新鲜读回、只有原始数据、新采证据、影响对象一致/不一致、独立评审待审/接受/拒绝。

**禁止的关键越级**：徽章比赛加成当升级阈值；MyCAREER或次世代资料当PC22事实；教练存值当已生效；交易单一字段变化当完整commit；自建Fixture当游戏函数成功；已经批准需求或阶段转换当已授权真实游戏操作；缺少执行凭据却将PoC记PASS。

## 形态分析与方案淘汰（基于当前证据，不冒充实机结论）

阶段03存在四个真正会改变结果B的离散维度：**证据层级、真实机制检验、执行路径、审核状态**。通过交叉一致性先淘汰“不作真实函数研究就宣称完成REA机制逆向”“直接上生产执行器”“以Fixture替代游戏业务测试”等冲突组合。

| 候选B路线 | 冲突/证据 | 裁定 |
|---|---|---|
| **B-C1：有来源的机制图谱 + 三代表有界验证 + 有条件教练优先PoC** | 满足Q1–Q6；保留E-REA02-104/110/111的实证未知，不强行填函数/规则 | **选择为结果B草案** |
| B-C2：只有传统内存字段清单，不研究消费者函数 | 与RES-REA-02/03/04及Q1目标不符；旧DEV07字段不能单独证明游戏机制 | 淘汰 |
| B-C3：立即以原生函数完成真实交易集成 | 与Q6教练先、RES-REA-05安全授权、原生交易未知相冲突 | 淘汰 |
| B-C4：只写独立外挂交易规则 | 保留作架构备选，但无法独自完成“能否复用原生交易”的研究 | 不作本任务主B，保留下游候选 |

这是**以现有证据裁定输出形态的模型判断**，不是证明C1的所有Native函数必能找到或调用。ACH关注证据与候选的冲突；无法获取同模式证据时标未知，不用“没有矛盾”偷换成“存在可调用函数”。

## 八条不可破坏的不变量

- **INV-01**：Any game-mechanic factual claim has source ID, first-hand or archived origin, build/mode scope and evidence maturity.（违反时 `UNSUPPORTED_CLAIM`）
- **INV-02**：Product requirement approval, technical qualification, action authorization, run receipt and independent acceptance are distinct states.（违反时 `AUTHORITY_CONFLATION`）
- **INV-03**：Missing safe PoC conditions yield NOT_EXECUTED, never PASS; bounded unknown can fulfill an honest research report only with documented attempts and Human acceptance.（违反时 `FALSE_SUCCESS`）
- **INV-04**：M1 one deep badge/one light comparison and M2 one deep coach offense or defense setting/other side light; M3 original trade validator and commit remain in scope.（违反时 `HUMAN_SCOPE_DRIFT`）
- **INV-05**：Before claiming a complete original game trade, roster, contract, finance, pick and game-event impact must be traced or each missing part explicitly identified.（违反时 `PARTIAL_TRANSACTION_CLAIM`）
- **INV-06**：No future path may silently replace Human-approved external trading/signing/draft design without separate change approval.（违反时 `SILENT_ARCHITECTURE_CHANGE`）
- **INV-07**：Old Codex 52-source manifest is archival; independent confirmation of all 52 checks or same-mode engine behavior must not be inferred.（违反时 `EVIDENCE_PROVENANCE_INFLATION`）
- **INV-08**：P0 exit and resumption of paused world-data Stage02 require distinct Human acceptance after real evidence work.（违反时 `PREMATURE_P0_EXIT`）

## 五项延后实证的准确处置

GAP-REA02-01至05分别对应自然徽章升级条件、教练消费与生效、交易验证/提交及事务完整性、安全函数调用与Human具体授权、同模式独立复核。它们被Human批准**作为后续Codex专门研究的证据缺口**，而不是被宣称已经解决。阶段03可以先构造状态、对象和失败契约；真实函数的地址、条件数值、交易调用ABI以及完整副作用不允许推断。

## 当前下一步与权限

此版本是**B0-v1讨论候选**，不是B正式版本。下一步进行B的状态图、失败反例、SC-REA-01..08双向覆盖和独立审查准备，再评估是否存在需要Human讨论的新增承重分歧。只有完成实际模型并获Human精确版本确认后，才能按OS进入下一阶段。当前不会派发Codex、操作游戏、调用游戏原生函数、修改master或恢复暂停中的世界数据阶段02。
