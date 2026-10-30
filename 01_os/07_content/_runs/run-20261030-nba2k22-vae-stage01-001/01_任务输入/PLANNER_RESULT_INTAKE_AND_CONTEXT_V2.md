# VAE 规划岗位 · 结果接收与健康上下文规范 V2

> 类型：NBA2K22 **领域任务级**岗位运行约定（不是新 Core OS 机制）；继承并补足 V1。
> 生效依据：Human 于 2026-10-30 在 VAE 规划对话中明确要求“你只做开发规划，如果要用gpt开发，请发布任务……根据我们的上下文机制，窗口只是临时工作台”，并要求规划任务、执行者、审核者、成果接收与上下文管理，以及将这些做法保存为持久记录。
> 上位规范：Core OS Workflow、Communication System v2、PRMS、Task Orchestration、Minimum Work Unit (MWU)、NBA2K22 跨模型协作 V2。**本文件没有自设通讯协议、PRMS WriterGate、权限审批机制或全局 Registry。**
> 任务：`NBA2K22-VANILLA-AI-ENHANCEMENT-20261030-001`。旧版：`01_任务输入/PLANNER_RESULT_INTAKE_AND_CONTEXT_V1.md`（历史保留，新的岗位约定以 V2 为准）。

## A. 岗位职责、窗口轮换与可恢复性

- 当前岗位：VAE 的 **decision_architecture / 规划与派单**。负责开发路线、模块划分、任务所有权、派单范围、交接及审核路由、审后决策、下一阶段规划与长期状态摘要；**不执行**其他 GPT/Gemini/Codex 承担的业务开发、不代替独立审核。
- GPT 执行窗口：从 `NBA2K22_COMMON_BASELINE` 独立 Fork，按 task packet 完成有界需求、原型、方案与研究产物。已派：`NBA2K22-VAE-GPT-STAGE01-20261030-001`；源提交 `079ccec5a28e7a61f000b462037f1c67ae8cef11`。
- Gemini / Antigravity：只在具体证据缺口明确后承担有界辅助；涉及与 Codex 共用本地工作区/游戏进程时先交接 HEAD、工作区状态和唯一 Owner，不并行改写。
- Codex：正式工程实现的唯一主 Owner，使用任务独立 Run，完成后提交精确候选、测试与回读证据。
- 独立审核窗口：从干净的公共基线建立，**不从执行窗口 Fork**；依准确任务边界和 primary evidence 审核，不继承执行者私有推理或认可其自述。
- Human：产品目标、重大语义与保留的受保护操作确认；对竞技体验提供实际观察。Human 不需要为已确定范围内的普通局部实现逐项微审批。
- 任何窗口都只是临时工作台，**PRMS 或经核实的 GitHub 任务档案才是持续状态**。Fork 不是实时同步，不因窗口消失导致任务状态失效。Planner 自身窗口轮换应由公共基线加精确 checkpoint 恢复，不复制旧聊天。

## B. 派单规则：一个主任务，明确 Owner、审核与停止点

派单前至少确定：task_id、目标/边界、Base SHA、允许路径、角色与接收环境、可重放资料引用、完成标准、测试证据、未知项、谁审核、受保护动作/冲突停止条件、completion pointer 形状。
- 研究、需求、原型：独立 GPT 执行；Gemini 仅接收有明确输入与可验证输出的辅助研究。
- 工程与 Native：Codex 实施；Gemini 顺序提供辅助证据；正式独立审核另行派发。
- 新执行窗口从公共基线读取 **当前 master → Core OS 启动规范 → 当前 task packet → 精确 direct refs**；不得默认读取所有历史 Run。
- 执行任务不自动开后续阶段；本窗口收到**最终成果**后才考虑发布下一任务。重大越界/存档修改/受保护发布仍交 Human 门禁，不因规划授权而获得执行权。
- VAE **独立于 D1–D5** 管理，既不在 D 完成后才能启动，也不是 D 的子任务；只将实际验证的字段需求/读回/采集/信息服务/执行经验作为可引用反馈。

## C. 正式回传的最小结果（依现有 MWU，不建第二份 Schema）

**Human 转给规划窗口的短指针**：任务 ID；仓库/分支/候选 40 位 HEAD；completion pointer 的精确路径；最终状态一句话；重要阻塞与 Human 待决；建议下一 Owner。原则上不在聊天里贴长日志、源代码、全文报告、反汇编。

**completion pointer 指向的执行 Run 须包含**：
1. 身份：任务、角色、版本、Base 与候选 HEAD、Run/lifecycle；
2. 结果：原定目标、实际已完成、未完成、差异及产物路径；
3. 实现：核心方法/架构变动、具体受影响模块及理由；
4. 验证：测试命令/环境、PASS/FAIL/NOT_RUN、primary evidence 文件和可核验来源；
5. MWU 四项：`work_performed_or_requested`、`implementation_or_review_method`、`supportability_rationale`、`feasibility_rationale`；开发者 rationale 仍然是待验证主张；
6. 证据成熟度：静态源码/研究、离线测试、实机读回、UI/存盘重载、真实竞技效果、独立审核，逐层分开；
7. 风险/未解项：严重度、所影响范围、所需关闭证据和下一 Owner；
8. Human：真实确认来源或 `pending`，不得擅自标记已批准；
9. 后续建议：需独立审核、补充证据或继续开发的范围；附最小直接引用；
10. D 系列反馈：仅在有实证时给出 Action→Information→Field / Reader / D3采集 / D4信息 / D5执行的精确引用；没有则 `none`。

此清单是规划岗位的**接收视角**，不覆盖现有 Communication 正式 `result` 消息契约，也不增加通用强制字段。若正式通讯被触发，必须使用经过验证的 v2 pointer/constitution/receipt；未形成时仅按现行 Human 自然语言任务输入和 GitHub Run 引用处理，并标记未正式投递。

## D. 规划窗口只做分层结果摄取

1. **合法性与版本**：fresh-read master、任务 HEAD、父提交/diff、allowed paths 和 task_id；缺 pointer/冲突则只记录 BLOCKED，不猜测结果。
2. **主证据抽查**：优先阅读 completion pointer、变更清单、测试摘要和与重大主张对应的少量原始证据；如不足以支持结论，再有界深入，完整日志保留执行者 Run。
3. **真实性分类**：把 developer_claim / primary_observation / independently_reviewed / Human_decision 分开；静态候选不是 Native 活体验证，技术读回不是比赛收益。
4. **审核派发**：需要独立审核时由隔离窗口审查；任务完成不自动等于独立审核通过，独立审核通过也不替代受保护的 Human 确认。
5. **规划状态变更**：只记录 verified scope、阻塞与所需证据、后续任务路由和 Human 待决；未经确认的结果留在候选状态，不升级为权威事实。

**审核路由**：
- GPT 的需求/方案：规划窗口先核范围与产物，独立 GPT 审核窗口核实重大需求/方法学和证据；Human 做正式语义/阶段版本确认。
- Gemini 辅助 Native/资料：相应工程 Owner（通常 Codex）进行限定范围接收核证；Gemini 不作自身正式验收。
- Codex 工程：独立新审核窗口（优先不同执行上下文/测量方式）核实源码、测试、Native 及存档安全；Human 决定最终受保护发布。
- 实际竞技效果：由观察数据 + Human 赛场体验 + GPT 有界分析支持结论；不把统计趋势冒充已经证明的因果关系。

## E. 健康的规划上下文（仅五类）

规划岗位长期保存以下**可恢复索引**，不保存执行者聊天流水或私有推理：
1. `human_decision_refs`：原始 Human 指令/批准、精确版本、适用范围；
2. `task_status_index`：任务 ID、Owner、阶段、现行 lifecycle、任务分支和精确 checkpoint；
3. `verified_facts`：已核实事实 + primary evidence/独立审核指针、可信范围；
4. `open_items`：风险、缺口、影响、关闭条件、责任人；UNKNOWN 保留；
5. `next_steps`：下次派单、审核与真正需要 Human 决定的事项。

**载体**：如能调用已部署 PRMS 的 `SAVE_TASK_CONTEXT`，保存 `task_id/task_plan/load_spec` 并核验回执；如无法访问，使用获授权、可读回的 GitHub Run 附近的 `PLANNER_CONTEXT_CHECKPOINT_V1.json` 作为 **fallback 快照**，写明 `PRMS_NOT_SAVED`。不要声称写 GitHub JSON 就触发了 PRMS WriterGate。

**保存触发**：重大 Human 决定、任务派发、可审核候选到达、独立审核结束、阶段确认、重大阻塞、下次窗口轮换。阶段内小修订不复制全部过程。

**新规划窗口恢复**：
1. 从公共基线 Fork，并执行 fresh Core/NBA OS Boot；
2. 读取当前规划 Run 的 `run.yml` 和 `PLANNER_CONTEXT_CHECKPOINT_V1.json`，再核验里面引用的精确任务提交；
3. 只加载当前活跃任务的 `completion_pointer` 和必要直接引用；
4. 比较 GitHub 实际分支 HEAD 与快照。快照滞后则标记 STALE、回到实际 GitHub 证据，不编造状态或把旧引用当 HEAD；
5. 只恢复已确认事实、Human 决策、阻塞和下一步；验证对岗位/任务/窗口隔离的理解后继续规划。

## F. 当前任务边界与不可夸大项

- 当前 GPT Stage01 开发任务已由 Human 转交独立 GPT 工作窗口，GitHub 当前任务发布基准为 `079ccec5a28e7a61f000b462037f1c67ae8cef11`，**尚无收到的完成指针、审查结果或 Human 对 A0 精确版本的批准**。
- 当前没有正式派发 Gemini VAE 或 Codex VAE 工程任务；不因“用户把任务交给 GPT 了”而自动补做开发或发起自动状态监控。
- VAE 只针对 MyLEAGUE 底层补强，现有 MC 存档作为测试环境，尚无对真实运行配置和写入安全的本轮测试。
- 当前文件只是在现有 GitHub Run 中持久保存岗位约定；**没有执行 PRMS SAVE_TASK_CONTEXT、正式 Communication v2 送达或独立审核**。

## G. 依赖现有 OS 的单一权威

Core: `01_os/03_mechanisms/context_management/prms/TASK_CONTINUITY.md`、`01_os/03_mechanisms/communication_system/README.md`、`01_os/03_mechanisms/communication_system/Human中转指针契约_v2.yml`、`01_os/03_mechanisms/minimum_work_unit_output/最小工作单元输出契约_v1.yml`、`01_os/03_mechanisms/task_orchestration/README.md`。
Domain: `08_Domain_Applications/Antigravity_GM_Engine/docs/development/MULTI_MODEL_TASK_OWNERSHIP_AND_VERIFICATION_V2.md`。

以上引用的规范才是权限、通讯和通用机制的权威。本 V2 只定义当前规划岗位的输出摄取策略与上下文压缩方法。
