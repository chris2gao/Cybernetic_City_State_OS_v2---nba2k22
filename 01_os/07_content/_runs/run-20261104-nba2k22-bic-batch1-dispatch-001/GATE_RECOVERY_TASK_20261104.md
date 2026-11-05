# BIC 第一批 · P0 阻断裁定与 Stage 01–05 准入恢复工作单

**工作单 ID**：`NBA2K22-BIC-B1-GATE-RECOVERY-20261104-001`  
**岗位/规划模型**：`decision_architecture / GPT-6`。对应工程承接：`execution / Codex`（仅准入材料与只读验证）；Human 保留工程执行与实机操作授权权。  
**结果状态**：`RECOVERY_PLAN_PUBLISHED / GATES_NOT_PASSED / DEV01_IMPLEMENTATION_BLOCKED`  
**来源**：Human 批准 BIC 01b A v2、第一批 DEV-01/02/03 的任务安排与发布；Codex P0 只读盘点完成，干净分支 `task/nba2k22-bic-batch1-p0-20261104`、HEAD=`66f8f73f1a91597f4562b834c2acad332ad9de5b`，报告同一阻断连续复核三次。  
**重要边界**：这不是变相扩大 `task_packet.json` 的工程许可；发布本工作单只允许筹备和验证准入文档。没有批准任何游戏进程操作、真实模拟、保存/恢复、Native 写入、DEV-01 业务代码实现、master 合并。

## 0. 判定：Codex 的 BLOCKED 正确，不要再执行三次相同门检

Codex P0 只读盘点可接受为**对方报告的已做工作**，但在相应原始盘点文件和固定 commit 远端可用之前，规划岗不宣称已经独立复核 P0 具体发现。当前远端没有 P0 的内容证据，不要求重新读取全库或重跑原测试。**不得用新标签或假 PASS 绕过阶段门。**

不能把 `01b_Human_confirmation_v2.json` 的真实批准直接等价于可通过机器校验的正式 `01_requirement.yml`；也不能把已发布的三个 DEV 合同当成已经获批准执行工程源码的合同。当前阻断是流程材料与来源绑定缺失，而非篮球目标需求未被 Human 认可。

## 1. 当前可立即开始的两项文档任务

### 1A · Stage01 规范化与正式验证修复（继承已获 Human 批准的需求建模任务）

输入（精确固定，不得修改原件）：

- 需求分支：`task/nba2k22-basketball-intelligence-core-requirement-modeling-20261104`。
- A0：`01a_A0_consensus_v1.json`，Human 确认：`01a_Human_confirmation_v1.json`。
- A v2：`01b_requirement_result_A_candidate_v2.json`，**Git blob `e16fdf6c4ef69b0a90b8c4abd3856617030a7ae4`**，Human 独立确认：`01b_Human_confirmation_v2.json`。
- 预检：`01b_Stage01_completion_gate_preflight_v1.json`，B01–B05。
- Core 规范起点：`chris2gao/Cybernetic_City_State_OS_v2---core@08d8e534a3438269aa7d7eb1b080ab11c172f462`，以执行时核实的最新 master + 精确 SHA 为准；查看 `01_os/01_workflow/01_需求建模/实现/需求结果模型模板_v1.yml`、`最小运行schema_v1.yml`、`01_os/06_execution/workflow/minimum_operational_loop/run_minimum_operational_loop.py`。

**具体动作，仅文档/静态验证**：

1. 在现有 BIC 需求 Run 的隔离工作分支创建**单独版本**的正式 `01_requirement.yml` 候选，保留已确认 A0/A v2 原件及独立 Human 批准的完整来源链；提供机器字段到已确认 JSON 段落/SC/RES/EVQ 的逐字段无损映射与转换差异。不能将人类对原始 Git blob 的批准伪装成对未经展示的新业务语义的批准。
2. 用 Core runner 源码中实际 `normalized_sha256` 定义（PyYAML `safe_dump(...allow_unicode=True,sort_keys=True,width=4096)`）计算**规范化 A0 digest 与排除两份确认字段的全要求 payload digest**，严格区分 Git blob SHA-1、原文件 SHA-256、规范化 digest。
3. 按 `requirement_findings` 的闭合 `evidence_status` 枚举规范化不合法旧标签；在旁路映射报告保留原值与来源，确保不会因转换丢失机制知识或把研究变成实证。A0 `consensus_ref` 必须仅包含规范字段及实际 A0 确认引用；两份 Human 确认不同且模型 ID/版本正确。
4. 生成符合 OS 同一 Run 的 `stage_control`、deliberation receipt、plan/completion acceptance 和必要 manifest 的候选绑定；为每项保存固定 Git commit 和 blob SHA。**只创建实际有来源和已履行的记录，不伪造 Human/审核签字、未运行的测试或完成门 PASS。**
5. 先执行 Stage01 适用的规范校验与静态结构检查，再根据 Core 的正式运行能力执行相应提交态验证，保存命令、Core/NBA exact SHA、退出码、标准输出和失败诊断。注意 `minimum_operational_loop validate` 面向完整七阶段 Run；在 02–07 尚未齐备时不得拿其失败推断 Stage01 语义错，也不得拿单阶段静态 PASS 声称完整 Run PASS。
6. 如果转换出现新的承重语义变更，**暂停并请求 Human 对变更点确认**。仅结构差异可经来源/哈希绑定证据核对，不要求 Human 重新回答已确认 Q1–Q18。

交付：`01_requirement.yml` 正式候选、来源映射表、哈希/身份绑定核算、真实静态/提交态验证回执、未完成项/下一阶段准入裁决。阶段标记须与实际独立验收一致。

### 1B · P0 结果证据持久化（使用已完成盘点，禁止重跑）

接收方 Codex 将**已经完成**的只读资产盘点和一次状态汇总持久化到自己的 P0 分支，至少包括：

- `P0_REUSE_GAP_MATRIX.md`：DEV01 的 WorldData/查询/身份/字段/原生读回，DEV02 徽章已知/未知，DEV03 Calendar/REA/VAE 原生实验能力，分别标 `REUSE | EXTEND | MISSING | UNVERIFIED`，每项给精确 commit、文件路径与真实已证等级。
- `P0_EVIDENCE_HANDOFF.json`：工作分支、固定 base/HEAD、查验时间、可复核的只读命令及观察来源、实际限制、后续需要的实验/权限、未知/矛盾及关键接口复用关系。允许引用旧证据，但不重跑消耗资源的旧测试。
- `P0_STAGE02_INPUT_POINTER.md`：说明 P0 实际做了什么、未做什么、开发未获授权、Stage02 使用哪些确定性来源。

仅新增以上报告/允许的审阅文档，不修改现有工程源码、数据库或游戏存档，不强行 cherry-pick 派发分支。保留 P0 的原工作区，先提交到本地 P0 分支，再经当前允许的公开/审核流程推送该分支；推送后提供确切 commit 和文件链接。若 P0 原始盘点根本未形成结构化文件，只整理已查过的来源，不重新启动全库盘点。

## 2. Stage 02–05 候选衔接：依次做，不假装已完成

| OS 阶段 | 应交付的 BIC DEV01–03 业务材料 | 不能写成 PASS 的条件 |
|---|---|---|
| Stage02 信息收集 | 基于 P0 真实源代码与已获批 A v2，分级整理 WorldData、原生徽章/成长证据、Calendar、REA、VAE 与游戏模式可读性；列出来源独立性、缺口、版本及证据限制 | P0 证据未落地，历史研究被误当成当前 PC22 原生读回 |
| Stage03 结果建模 B | 明确 DEV01 读取/解释接口，DEV02 徽章状态与资格推断语义，DEV03 因果实验计划/结果/证据状态；设计统一身份、保存版本、模式与知识可信接口（先查已有实现） | 把开发任务摘要或模型意见冒充被审核的 B 成果 |
| Stage04 测试生成 | 冻结真实查询与缺失/陈旧/跨存档负例，徽章等级与资格反例，2×2 交互和混杂/3D vs Fast Sim 区分；测试编号/输入/输出/来源可复核 | 没有实际可运行测试资产、测试环境或冻结引用 |
| Stage05 步骤拆分 | 划分唯一模块归属/依赖与增量，指定实际允许源码路径、数据迁移/回滚边界、每轮 Loop 检查点、停止门、性能与验收 | 未获批 Stage02–04，却先将源码施工和 Native 写入标成允许 |

P0 只读盘点的来源可用于 Stage02，但不能直接替代 Stage02 的来源质量裁定。Stage03–05 的最终版本必须引用前一阶段**真实批准**的 artifact 和 commit。可预先形成草案，不得预先填写机器通过、测试通过或 Human 凭证。

## 3. DEV-01 工程执行合同草案：仅供后续 Human 批准，不在此处生效

**拟批准对象**：`NBA2K22-BIC-B1-DEV01-BASELINE-DATA-20261104`，接收方 Codex，来源本批 `dispatch/DEV01_DATA_BASELINE.md`。原工作分支 `task/nba2k22-bic-batch1-p0-20261104` 作为连续性起点，不因任务发布自动获得代码写权限。

拟许可范围（须以 Stage05 真实完成版本和 Human 正式批准的具体合同为准）：

- 在现有 `08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype/` 或经过证据确认的统一查询/卡片入口内完成**只读** BIC player/team 数据基准输出、来源/知识状态/日期/模式/存档身份说明；增加针对本功能的测试和小体积夹具。
- 如果确实需要 Schema 变更、原生读取能力扩展、特殊进程接入或另一个工具包，作为变更候选独立陈述风险和增量，不默许展开。
- **禁止** NBA2K22 游戏进程附加/模拟推进/存档修改、直接球员属性/徽章/潜力改写、Native Setter、无授权训练、实际 REA 写入、大规模历史数据库推上 GitHub、改变 A0/A v2 原始事实、合并 master。
- 每轮增量留下真实离线测试命令/退出码、回归/性能、源证据和 PRMS 检查点。默认内部 Loop，重大数值或逻辑风险停下，系列结束统一审核。

**工程放行门**：必须同时存在可复核 Stage01 正式完成或适用阶段验收证据、Stage02–05 正式准入产物、Human 对**指定 DEV-01 合同 + 版本/目录范围**的清晰授权。任何一个缺失都继续 BLOCKED。DEV02/03 不随 DEV01 自动获批。

## 4. 规划岗收件要求（下一步不再循环问是否可施工）

1. Codex 提供已有 P0 证据的远端固定文件 + commit；若本地 P0 未推送，明确说明而不是重复发送“blocked”。
2. Stage01 准入修复提供正式候选及实际验证回执；规划岗核验来源、准入与是否需要额外 Human 裁决。
3. Stage02–05 逐阶段给出可见的真实审查版本；未满足条件不得派发 DEV01 源码修改。
4. 合同准备完成后向 Human 提交**一次具体的 DEV-01 受限工程执行批准请求**，而不是提前从已通过的批次规划中推断工程权限。

**结论**：P0 已完成（Codex 自述），DEV-01 业务工程仍 BLOCKED。先固化证据和处理 Stage01/02–05；禁止重复 P0、虚构 PASS、扩大权限。