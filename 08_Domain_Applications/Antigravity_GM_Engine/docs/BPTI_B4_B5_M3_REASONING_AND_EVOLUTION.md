# BPTI B4/B5：M3 篮球理由与球队演化

工作包 C 在现有 M3 候选流程中按需启用。沿用 Knowledge.bpti、密封 M3 分析包、同一个 gm_workbench 与 DEV14；没有新事实库、第二套市场/审批/执行器。V3 继续有效，GM V4 未启用；历史队史和合成验收不评定真实 30 队。

## 入口与顺序

使用现有 scripts/gm_decision.py，显式指定已有工作台、run 和 expected-revision。新增 submit-blueprint 与 record-evolution；原 submit-review、submit-alternatives、select、validate、finalize、artifact、export 保留。以下描述为使用契约，不代表已运行正式 GM。

1. 先由原 gm_analysis 准备并密封当前 GM_SANITIZED 分析包，再 begin 候选 run。CLI 对新增两类写入重新打开该 career/batch 的 QuerySession，require_gm_sanitized 并核对绑定；不可用则返回 HOLD，不保存。
2. submit-blueprint 的输入包含 team_id、source_binding、blueprint、why_this_basketball、identity_application、role_evidence、decision_context、alternative_implications、native_actions。blueprint 严格沿用 B0 SystemBlueprint（含 DRAFT_UNAPPROVED）；coach_ref 为该队当前对象引用，角色引用当前名单，证据按游戏日期裁剪。四个狭窄家族只能用获准的早期机制，不解锁整张研究卡。
3. role_evidence 每项给 player_ref、skill_fields、evidence_refs、reason。字段必须是该分析包实际可见的 decoded_attributes，不能用姓名、Potential、Intangibles 或 OVR 代替技能。研究不自动生成巅峰球员或数值写入。
4. identity_application 给 retained_values、role_fit、internal_priority、market_after_internal、tradeoffs；decision_context 给 coach_fit、development_plan、market_gap_reason、identity_role_tradeoff。alternative_implications 对 HOLD/INTERNAL/MARKET 分别给 means、cost、change_conditions。保留身份与当前角色冲突要明说，财务仍引用 M1 的现有证据/情景，不能把原始 cash 当可签约容量。
5. native_actions 必须使用现有 M3 动作 DTO。B2 支持方向与现有 native_intent 双重限制；未确认的方向、CRC 类型/Tempo 篮球含义等不能变成承诺。支持的动作才可进入 INTERNAL；未知方向留 HOLD/研究。实际值、枚举和字节仍由 DEV14 既有纯规划器独立核对。
6. submit-review 和 submit-alternatives 必须携当前 bpti_blueprint_revision。D1–D6 保留原评审证据并加入教练/战术/角色/市场/培养与身份理由；三个备选写入相应机会成本与转向条件。可执行原生动作须逐项等于支持候选；不支持的内部动作保留 BLOCKED/HOLD，不能进入执行组合。蓝图有效但无支持动作时，native_action_status 为 HOLD，整体篮球理由仍为候选；MARKET 独立经过原 M3 的内部比较、GAP_REMAINS、财务与双边同版谈判规则。来源/知识不合格不提供原生执行支持。蓝图换版后旧评审/备选或旧演化不能用于定稿；需要重做当前演化，历史记录不删除。

这是一层对明确判断的组织、约束和留痕，不能替代 GM 的篮球推理，也不预测胜率、回合效率或比赛效果。第一优势、对手反制、第二答案、球员自主权与 UNKNOWN 必须一起保留。

## B5 演化与组织惯性

record-evolution 引用当前蓝图版本，给 level、previous_ref（首次为 null）、observed_changes、decision_reason、retained_culture、proposed_culture、coach_alignment、reconsider_conditions。observed_changes 每项含 kind、evidence_refs、observation、uncertainty；当前事实引用须存在于密封分析包，观察说明属于调用者的候选判断，不认证因果。

六级为 ROLE_TWEAK、SECONDARY_BRANCH、CO_PRIMARY_SYSTEM、TACTICAL_REBASE、COACH_ALIGNMENT_CHANGE、ORGANIZATIONAL_REIDENTIFICATION。换教练层级需 COACH 观察；只是经营建议，没有教练市场执行器。角色和战术可较快调整；文化默认延续前态。文化重构另需 MANAGEMENT 和 LONG_TERM 证据、跨季 long_term_context（seasons、management_reference、why_tactics_or_coach_alone_insufficient）。一个月输赢不能独立改写文化。

previous_ref 为 {run_id, artifact_id: team_id 字符串, revision}，CLI 从同 career/同队已有 BPTI_EVOLUTION 不可变记录解析前态，不接受内嵌自造历史。前态还须具有相同且非空的 save_id/save_instance_id/generation_id；已记录的 history_branch_context 必须连续一致，批次和赛季可以变化。旧记录的分支上下文从原已存 run 恢复。身份缺失、实例/代次变化或分支不连续返回 HOLD；当前没有可认证的跨实例血缘桥接，重复 career 或手填同名世界线不能替代证明。每次保存使用原 decision run CAS；artifact --kind BPTI_EVOLUTION --artifact-id TEAM --artifact-revision N 可追溯。前态系统、文化、变化、当前技能/角色、教练适配与反转条件一起留存。历史记录不是玩家批准；跨队球星按该存档可见技能与新组织背景判断。

## 交接与权限

BPTI_BLUEPRINT/BPTI_EVOLUTION 使用现有 decision_artifacts 版本表，不增加数据库/表。artifact 仍有界分页，export 新增 bpti_artifacts.json；final/candidate 仅携派生理由和历史引用，正式 M2 保存仍需原显式操作。

内部具体动作只有 category=INTERNAL 且 status=VIABLE_CANDIDATE 才能进入选定执行组合；BLOCKED/RESEARCH/NOT_APPLICABLE 可保留在研究或 HOLD 叙述中。

可支持的选中动作继续经原 M3 validate → prepare_native_artifacts → DEV14 纯 build_plan 输出未批准 intent/approval tuple。不会安装 Desired、获得玩家批准、发起游戏写入、采集或发布事实。原姓名/对象身份、同批来源、CAS、批准元组、本队书/新同批全目录 CRC 等保护不变。

普通 GM 仍禁止 Ability/Potential/Badge/OVERALL、匿名51倾向和自由 PlaybookID。Intangibles 只可用作既有25–99软轮换偏置，不是侦察能力或精确分钟锁。B4 当前不从未认证 CRC 类型推导装载动作；这不改变现有 DEV14 本队书接口权限。TEAM_BOOK_REBIND 仍需独立初始存档/换帅事件、确认和新来源后再提槽位方案。真实比赛、AI 执行、存盘、V4 激活和 DEV24 均未由本交付完成。
