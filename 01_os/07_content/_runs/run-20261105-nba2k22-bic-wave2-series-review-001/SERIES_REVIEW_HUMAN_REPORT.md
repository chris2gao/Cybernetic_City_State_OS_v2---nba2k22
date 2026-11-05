# BIC 第二批 DEV-04 / DEV-05 · GPT-6 独立系列审核

**固定工程对象**：`b308660b3112738a4df52e412448d821c3d4b932`，相对第一批验收 SHA `aec3dbaacd1d56b0c7cc1d40c2f70607493b9a4b` 前进 2 提交、19 个变更文件。  
**审核角色**：`independent_review` / GPT-6。  
**最终裁决**：`TARGETED_REMEDIATION_REQUIRED`；第二批离线原型主体成立，但 **3 项 P1、1 项 P2** 需在同一内部 Loop 内关闭，再做差异复审。  
**完整结构化结果**：同目录 `BIC_WAVE2_SERIES_REVIEW_v1.json`。本次不操作游戏、不动开发分支、不合并 master。

## 一、确定的正面证据

- `bic_diagnostics.py`、`bic_plans.py`、`bic_wave2_cli.py` 均实际存在。确实复用第一批 `player_baseline/team_baseline`、`knowledge_query`、`coverage_report`、徽章判读、2×2 合成实验与现有 REA Core Profile 桥接。
- Native 计划均携带 `execute=false` 与独立 Human 实机授权门。本次没有发现真实 Setter、交易、存档写入、日历推进或比赛模拟的调用。
- 相对优势/弱点基于已有未认证评分转换候选，且标为 `HYPOTHESIS`；没有将 Box Score 直接认证为真实 3D 战术效果。
- 交付的 pytest 日志为 `57 passed, 1 warning in 31.46s`、外层回执退出码 0，外层计时约 31.94s；其中 Wave2 新增 16 个正反测试。原 warning 为此前已独立溯源的 `PytestReturnNotNoneWarning`。
- 已对四份公开交付文件（`tests.stdout.log`、`verification_receipt.json`、`ENGINEERING_HANDOFF.md`、`synthetic_validation.json`）独立计算 SHA-256，与 `delivery_manifest.json` 完全吻合。
- Pascal Siakam 与 Nikola Jokic 历史案例确实存在，保留 `REAL_DATA_NOT_VERIFIED`、缺失构建绑定和 Native 执行 `NEEDS_VALIDATION`。大 SQLite 的前后 SHA 相等是工程回执中的真实陈述，但审核者**没有重新打开该本地文件**。
- 本次审核只读检查源码和归档测试，没有在原 Windows/Codex 环境重新执行 57 项测试；不能把交付测试结果写成审核者新跑的一轮实测。

## 二、必须整改

### P1 / BIC-W2-R01 · Native 历史部分验证不得扩展成通用已准备状态

`bic_plans.py:90-131` 对任何动作级 `LiveEffectVerified`、参数域符合且 `before_source` 非空的请求，可能输出 `OFFLINE_PLAN_READY`。

固定 REA Native 来源 `094f1aa641f93dec2277707ad9dbf5bdb0341247` 的 `COACH_SET_KNOWN_CURRENT_SETTINGS` 只验证了精确输入 `team_id=20 / RunPlayTendency:90→55`，但动作目录也允许其他合法枚举字段。将未经验证的 `POEOffense2:0→7` 与调用方自填前值来源提交给当前纯离线计划器，静态控制流可达“READY”，尽管该参数的原生效果并未获得历史精确认证。

**要求**：将 Schema 完备和可执行证据成熟度分开；准确绑定历史精确输入的字段/值/前值；任何无新鲜 Getter 来源或无法认证的参数保持 `NEEDS_VALIDATION`（或显式 Schema-only）；所有计划继续 `execute=false`，不新增 Native 操作。加入严格负例。

### P1 / BIC-W2-R02 · 诊断的顶层 FACT 不得超出来源认证等级

`bic_diagnostics.py:77-94` 主要依据 `OBSERVATION_AVAILABLE`、数值和新鲜度给出 `FACT`，没有用来源 `knowledge_status` 或整个基准的 `REAL_DATA_NOT_VERIFIED` 约束顶层可信度。

两份已提交历史案例，各有 6 项诊断标记为 `FACT`，支持来源却是 `UNVERIFIED_OBSERVATION`，数据状态为 `REAL_DATA_NOT_VERIFIED`。这不是认为原始数值错误，而是**机器可消费的事实等级可能被抬高**。

**要求**：将“数据库里确有一条观测值”“其与调用方假设的数值比较”和“已认证的游戏事实”分开表达。原始数值、来源、时间和候选角色结果均保留；合成或未认证历史数据不得以不加限定的 `FACT` 影响下一步决策；测试真实历史边界和合成负例。已认证 Native 机制仍不得凭属性比较得出。

### P1 / BIC-W2-R03 · 固定阵容比较要绑定同一来源范围

`bic_diagnostics.py:46-58` 的 `_same_context` 已核对存档 ID、赛季、截止时间、比赛模式和构建，但不检查 `observation_scope.scope_sha256`。不同采集集合只要上述标签相同，就可能被当作同一固定球队世界线使用。

**要求**：在同一固定世界/快照诊断中校验范围指纹及可用数据库来源身份；不一致时明确拒绝或降低为不适用/待验证。注意同一合法 Scope 内的不同字段来源单元允许不同，不能为了修正问题破坏第一批设计。加入两个数据库/Scope 同标签但不同单位集合的负例。

### P2 / BIC-W2-R04 · PlayType 缺失必须满足采集完整性

`query.py:634-644` 返回每个已观察非空槽位的最新值，并不是全部 PlayType 槽位已采集的证明；`bic_diagnostics.py:128-134` 只需至少一个新鲜槽位，就可能将“不含目标代码”判为 `CONFLICT`。

**要求**：仅当有完整、可信且同 Scope 的槽位集合时，才允许以“不包含要求的 PlayType”断言不匹配。部分采集/遗漏槽位的负判断保持 `UNKNOWN`；正向命中可以说明已登记，不代表该战术在比赛中实际执行。增加新鲜部分槽位的反例。

## 三、审核与执行规则

- **允许继续**：在现有第二批分支用一次小范围内部 Loop 修改 R01–R04，保留全部已通过的 WorldData/DEV01–03 与本批诊断架构。
- **不必重新申请**：Human 已批准此范围内的离线普通开发和内部 Loop；不要重复 P0、旧需求或无关旧回归。
- **测试门**：新增上述定向负例，并重跑第二批相关 `57` 项回归（或等价超集）；保存原始命令、退出码、完整 stdout/stderr、性能与 SHA。
- **交付门**：新的固定工程 SHA、R01–R04 修复证据、测试和恢复检查点。GPT-6 对新 SHA 做一次差异复审。正式 OS Stage 01–07 仍由独立准入链条处理。
- **依旧禁止**：真实 NBA2K22 进程操作、Native/REA 写入、存档更改、游戏模拟和主线合并。

**总体判断**：不推翻 DEV-04／DEV-05 设计，不重做已交付成果；先修正“证据等级”“同一世界线”和“原生计划准备度”这三类会直接影响未来自动决策可靠性的逻辑，再关闭本批系列审核。
