# NBA2K22 第一大任务阶段02 · 原生字段来源取证交接 V1（候选派单，未执行）

**上游门禁**：Human 已于 2026-10-24 明确批准完整 01b 需求结果 A，见 [批准记录](NBA2K22_TASK1_01B_HUMAN_APPROVAL_RECORD_20261024.md) 与 [需求结果 A v1.9](NBA2K22_TASK1_REQUIREMENT_RESULT_MODEL_V1_9.md)，以及 [阶段02/03实质交付要求](NBA2K22_TASK1_01B_STAGE02_03_CONCRETE_DATABASE_DELIVERABLES_V1.md)。

**当前阶段状态**：`02_READINESS_AND_HANDOFF_CANDIDATE`，**不是**实际 Native 验证完成，不代表已进行游戏内存访问或完成 OS 正式 task/run 创建。本单用于在已有 OS 任务 ID 下开工前确认环境、依赖、权限和验收计划。

## 1. 与现有 OS 任务对齐，而非新造重复项目

根据当前 `master` 的 `NBA2K22_OS_TASK_BACKLOG_V1.json`：
- **P0 `NATIVE-ACCEPT-01`**：AG01B–01D 的 GAME/StatBank/身份/生涯数据来源核验、边界和负例、可复测最小证据；已有 OS 状态记录为 `planned_not_dispatched`，前置 `OS-BASELINE-01`。
- **P1 `WORLD-DATA-COVERAGE-01`**：全体目标真实 PC22 UI 字段逐项覆盖、缺口分级（教练/财务/伤病、G League/新秀等）；已有 OS 状态记录为 `planned_not_dispatched`，前置 `NATIVE-ACCEPT-01`。
- 当前 backlog 的 `OS-BASELINE-01` 状态为 `candidate_pending_independent_review`；此状态**可能随仓库新审查而变化**。实际派单前必须复读最新 registry、run 和完成指针并核对前置门禁，不能仅凭旧规划文字断言已经关闭或永久阻塞。
- 若实际任务目标超出已有任务包，再按 OS 建立新任务；不得把 `NATIVE-ACCEPT-01` 与 `WORLD-DATA-COVERAGE-01` 无依据合并成一个不受控大任务。

## 2. 阶段02唯一目标和实质性验收物

**目标**：真实 NBA2K22 PC 离线 MyLEAGUE **游戏 UI/Native 来源的可复验逐字段证据**。不是数据库表数设计、不是世界线数值优化、不是原版游戏写入。

应交付以下工程资料并能双向追溯：
1. **Source Evidence Catalog**：每一个被声称存在的游戏 UI/原生字段，记录真实场景/Tab/对象、游戏显示文字/单位、实际原生来源、Getter/offset/bit结构或解码过程、候选数据类型和枚举/有效值域、读出值和来源证据、来源版本、权限与已证/UNKNOWN状态。
2. **Field Coverage & Gap Matrix**：以01b的 [146注册+39研究入口分卷](NBA2K22_TASK1_01B_FIELD_COVERAGE_GAP_MATRIX_V1.md) 作为待核对线索，而不是答案。按真实游戏栏目逐项增补现有工程未登记的字段；对不存在、不可读、无法定位的每项说明原因、影响和Q10例外状态。
3. **身份和关系证明**：限定同一独立存档，核对赛季/比赛/球员/球队/员工/选秀资产的身份、可重用原生ID、跨赛季/采集时点稳定性；包含假同名、跨档相同ID、staff池槽位映射、季后赛系列赛关联、选秀池身份等负例。
4. **时间与权限证据**：当前/历史赛季 Box 与玩家Tab高阶统计可用窗口、已完成历史来源、赛季最终状态、字段新鲜度；普通 GM 的隐藏球员 Potential 在查询及导出时不可泄漏。
5. **取值域和转换可验性**：区分游戏原始编码、必要显示转换及独立数学计算；特别核查 `original_contract_years` 与 `extension_length` 同 offset 833、Badge“2-bit”与五种标签映射等冲突，来源不确定保留 UNKNOWN。
6. **真实证据与测试**：可回放但脱敏的受控 fixture、明确游戏版本/存档上下文、校验脚本与原始运行结果、真实阅读截图或合法文字核对，正例和负例；研究说明、测试、独立验收结论彼此标注不同证据等级。

**不能提前宣布阶段02完成**：没有真实 PC22 场景逐字段证据和可复验的 Reader/解码核对；无法证明字段值域时不能发明上限；不能把研究文件的 `NATIVE_VERIFIED` 当作本任务独立核验。

## 3. 有界执行顺序

- **Step 0 / Readiness**：遵守当前 OS root 四份入口、读取最新 `master` SHA、真实 OS `OS-BASELINE-01` 完成指针和任务包状态；建立任务工作分支、`task_id`、明确 `allowed_changed_paths`、验证计划、风险与独立审核节点。不可直接在旧01b分支上开发 Native/Schema 代码。
- **Step 1 / 最小高价值证据链**：选择真实单档中的已知 GAME/赛季对象，验证 `SEASON_SCHEDULE` → 游戏双方球队 → `BOXSCORE_STATBANK` 球员 Box → 季赛统计索引与来源、边界和错误情况。只读，不动实际游戏历史。
- **Step 2 / 原生扩展核对**：研究 GAME 状态和赛程、Player Card 的真实可读字段、Staff/team映射、合同、选秀资产、G League、球队统计等，按基础对象证据逐项追加；读取合法值域而不假设目标设置“最佳值”。
- **Step 3 / UI 覆盖扩展**：前置原生核心通过后推进 `WORLD-DATA-COVERAGE-01`，逐页对应实际游戏 UI 与原生读数/解码/数据库逻辑字段；未验证与无法读的字段必须在 Q10 缺口表里可查。
- **Step 4 / 独立审核**：执行者给出源证据与原始日志，另一独立窗口/不同测量途径复查并出具 PASS / FIX_REQUIRED / REJECT；不能由研究或开发者自己声称“已独立验证”。

## 4. 任务角色与权限

- **候选执行路由**：复杂原生/身份/契约核证交 Codex（本地受控环境，T2 semantic 候选），Gemini/Antigravity 仅针对有界 UNKNOWN 来源探索或 Reader 验证协助，网页 GPT 的**另一独立审核会话**可复核原始资料和代码证据；具体模型、风险、运行方式以实际 OS routing preflight/当前 Human 路由为准。
- **允许的静态预备动作**：读取 GitHub 仓库中已存在的原生研究、SQL/Decoder 源文件以及获准的实验 fixture；建立只读缺口清单。
- **未经另行适用授权不得做**：使用远程桌面或终端访问用户本地路径 `E:\workspace\Cybernetic_City_State_OS_v2 - nba2k22`、启动或操作 NBA2K22 游戏/进程/内存、写入真实游戏/存档、生产数据库迁移、运行敏感本地操作（DCR）、强推/重写历史或将候选并入 `master`。
- **第一大任务第三阶段必须仍按人类已批准的实质交付规格**形成完整表数、逐字段和值域、关系与设计理由、可运行 SQLite DDL、数据采集/查询和正负例；阶段02不可因为专注边界而放弃提供阶段03真正需要的原生证据。

## 5. 派单落地清单（当前还未满足/未执行）

| 必备 | 当前结论 |
|---|---|
| A 内容审批 | `HUMAN_APPROVED_REQUIREMENT_RESULT_A`，见2026-10-24批准记录 |
| 最新 OS `OS-BASELINE-01` 前置门禁 | **TO_REVALIDATE**，backlog仍记录候选待独立审核 |
| P0正式任务包、独立run与准确 `master` base SHA | **NOT_YET_CREATED**；发工前新建，不使用聊天旧SHA |
| 本地真实游戏/内存读取/DCR权限 | **NOT_GRANTED_BY_THIS_APPROVAL** |
| GitHub静态研究线索 | **AVAILABLE_AS_CANDIDATE_SOURCES**，不是实机通过 |
| 阶段02 实机/Native字段核证 | **NOT_RUN** |

阶段02应按照既有OS任务链开始，无须重新争论 01b 已获批准的产品范围，也不可跳过尚未满足的 OS 物理执行和独立审核门禁。
