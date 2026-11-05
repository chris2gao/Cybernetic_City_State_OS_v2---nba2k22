# BIC 第一批 · 下一执行入口：Stage 02 定向只读证据核验

**Task ID**: `NBA2K22-BIC-B1-STAGE02-TARGETED-EVIDENCE-20261104-001`  
**岗位**：`research + execution(read-only)`；建议接收模型 Codex（沿用已完成 P0 的上下文），Gemini 可并行做徽章研究。**发布模型/责任**：GPT-6 `decision_architecture`。  
**当前状态**：`ACTIVE_FOR_TARGETED_READONLY_EVIDENCE`。这是有边界的证据调查授权，**不等于** Stage02 正式 OS 完成门通过，**不授予**业务源码修改、Native 接入/写入、日历推进、存档修改或 master 合并的权限。

## 纠正此前派单的循环阻塞

已知 P0 已固定在 `17bca5c5e34a4bc3b153c38634681962e1600ec7`，不得再重复 P0 或第 4 次相同 `blocked` 回执。Stage 01 源语义 A0/A v2 均已获 Human 确认，正式机器规范化在**独立的 Stage01 任务分支并行进行**；它阻断的是发布正式 Stage02 PASS 和 DEV01 正式业务源码施工，而不是对静态事实、已有只读存档、现行可读来源的独立证据调查。

**本次新工作是目标明确的 Stage02 证据研究任务，而非对原有 DEV01 实施合同的自动放权。**

## 必读固定输入（直接链接到对应 GitHub 文件）

1. [P0 只读交接及证据矩阵](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/blob/17bca5c5e34a4bc3b153c38634681962e1600ec7/01_os/07_content/_runs/run-20261104-nba2k22-bic-batch1-p0-001/P0_STAGE02_INPUT_POINTER.md)
2. [Stage02 已判定证据候选](02_evidence_CANDIDATE_v1.json) — `E-01`～`E-09`；来源固定，UNKNOWN 保留。
3. [Stage03 结果 B 候选](03_result_B_CANDIDATE_v1.json) — 六项 `B01`～`B06`，不是实施许可。
4. [Stage04 15 项测试候选](04_tests_CANDIDATE_v1.json) — 现为 `frozen=false`，没有运行结果。
5. [Stage05 七步候选](05_steps_CANDIDATE_v1.json) — 只供校对依赖和唯一源码归属。
6. [Stage01 规范化脚本与执行说明](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/blob/task/nba2k22-bic-stage01-canonical-normalization-20261104/01_os/07_content/_runs/run-20261104-nba2k22-basketball-intelligence-core-requirement-001/STAGE01_CANONICALIZATION_RUNBOOK.md) — **平行任务**；当前窗口不用等其结束才可做以下只读调查。

## 必须实际完成的 Stage02 增量（只读，不是二次盘点）

### E02-R1 · DEV01 WorldData 真实记录与跨来源一致性

根据 P0 确认的现有 `query.py`、`observation_scope.py` 和统一身份字段，**在已有、明确允许读取的本地历史存档或世界数据 SQLite 快照中**选择一个可复核数据单元。仅执行只读 SQL 或已有 query/Reader，不重新采集、不启动 NBA2K22、不推进日历。

目标验证：`player_card/team_card` 的 `UniqueId/PreservedId` 绑定、save/season/mode、按字段 observation_unit/observed_at/effective_at、缺失字段与受限字段。若没有真实可用存档，明确返回 `MISSING_REAL_DATASET` 和所需来源特征；不能造球员数据。

**输出**：`STAGE02_DEV01_REAL_READ_EVIDENCE.json`（数据集路径的相对位置/安全脱敏指纹，原始来源 commit、只读命令/退出码、数据身份、实际返回值或安全摘要、字段来源一致性及负例）。不要把大的 SQLite 或完整快照提交到 GitHub。

### E02-R2 · DEV02 徽章事实与资格证据分层

从已验证的球员 Native badge profile/decoder 中追踪**当前拥有与等级事实**；将 MyLEAGUE 徽章取得资格、XP、自然成长、动画/成功率逐项分为 `STATIC_SOURCE`、`HISTORICAL_LIVE_OBSERVATION`、`RESEARCH_REFERENCE`、`UNKNOWN`。P0 已确认 R04 资料可能混入 MyPLAYER 门槛，不可据此认证 PC22 MyLEAGUE。

**输出**：`STAGE02_DEV02_BADGE_EVIDENCE_GAPS.json`（支持/反证、每条 Native 规则的实际来源路径/SHA，清楚区分未查到与证明确实不存在）。不运行游戏，不修改训练与徽章。

### E02-R3 · DEV03 可比较性与模式边界

复用 P0 找到的 Calendar、REA Bulk、game_mode 和 VAE 历史报告，确认**只读的实验输入**支持哪些可比较单位、是否有明确 game mode、赛程/球队等聚类因素和 3D 行为证据。2×2 因素算例可在离线合成小夹具上核查“独立效应/交互效应”公式，但结果不得成为 NBA2K22 因果证据。真实 Native 操作仅列为未来授权需求。

**输出**：`STAGE02_DEV03_EXPERIMENT_FEASIBILITY.json`（能确定/不能确定的因素与混杂、固定来源、最小离线算例结果、需要何种独立实机授权）。

### E02-R4 · 证据差异与承重决策

交付 `STAGE02_BIC_EVIDENCE_ADJUDICATION.md`：针对 `E-01`～`E-09` 各一条判断，列原始来源、版本、适用模式、独立性、已验证程度、反证、闭合条件和对应 `B01`～`B06`。标记 `SUPPORTED_STATIC / SUPPORTED_READONLY_REAL / HISTORICAL_ONLY / RESEARCH_REFERENCE / UNKNOWN / CONTRADICTED`。不得将 Stage02 研究成果伪写成正式 OS Stage02 通过。

## 继续/停止逻辑（重点：不再因旧 Stage01 标志原地等待）

- 能做 E02-R1/R2/R3 的任何一项时，继续执行已获准的**只读研究 Loop**：读 → 核验 → 分析 → 记录 → 下一项，直到 R4；本任务允许小型、定向的离线数据检查，不含新业务源码开发。
- 某个来源缺失，只阻断该来源下的事实认定，记录 `UNKNOWN` 并推进其他独立来源；**不得因一个已知缺口整体停机**。
- 如果出现对范围、数据隐私或实机授权有重大不确定，暂停该危险动作并提交精准差异；其他安全研究继续。
- Stage 01 规范化和 Stage 02 研究**并行**；后续将真实证据用于正式阶段准入，并由规划岗提交受限 DEV01 工程合同。没有正式准入不启用源码实施。

## 对当前 Codex 窗口的下一条动作

按上述 R1→R2→R3→R4 执行（没有真实存档则记录局部缺口并继续 R2/R3），只提交新读证据，不再重复 P0 文件扫描、旧回归和 blocked 状态汇报。所有提交必须附精确 SHA、相关源文件和只读验证回执。**不要把尚未取得的 Stage01 机器 PASS 当成这轮只读研究的前置条件。**
