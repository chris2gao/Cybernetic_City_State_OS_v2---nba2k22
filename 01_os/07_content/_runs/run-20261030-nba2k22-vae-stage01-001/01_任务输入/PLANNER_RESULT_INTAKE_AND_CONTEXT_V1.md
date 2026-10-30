# VAE 规划窗口 · 成果接收与上下文健康约定 v1

> **归属与效力**：NBA2K22 VAE 项目级任务补充约定，不是新 Core OS 机制、不变更任何既有 Schema、Human 审批门禁或通讯协议。
> **角色边界**：规划窗口负责目标/任务拆分、派单、审阅最终证据摘要、安排独立审核和后续规划；执行窗口承担本任务实际开发。规划窗口不得把执行者自述当独立审核结果。
> **关联任务**：`NBA2K22-VANILLA-AI-ENHANCEMENT-20261030-001`，此文仅用于当前 VAE 规划 Run。
> **已派发执行任务**：`NBA2K22-VAE-GPT-STAGE01-20261030-001`，发布任务工作分支 HEAD 起点 `079ccec5a28e7a61f000b462037f1c67ae8cef11`。

## 1. 单一权威链

1. **Human 原始裁决**：保留实际指令与来源；计划、模型摘要或推测不能生成 Human 审批。
2. **OS + GitHub 固定事实**：使用当下真实 master、task branch 和精确 SHA/路径，核对 task packet、Run、阶段产物及测试证据。
3. **执行报告**：仅作为“声称及指向证据的索引”，不是已经审计的事实；先核实存在/范围，再安排独立审核。
4. **独立审核报告**：必须来自独立窗口，对执行者关键论据与原始证据进行复核；只在审核覆盖的范围内认可。
5. **规划决策**：只将 Human 已裁决事项、已验证范围及明确待证假设转为下一任务需求。

完整实现记录、调试过程、Native 反汇编、原始日志、长篇研究与上下文快照保留在各执行者 Run 中；**不要复制进规划窗口的角色记忆**。

## 2. 执行窗口回传信息（引用现有 Minimum Work Unit 和 completion pointer）

执行窗口按其 task packet 的 required_completion_pointer 与 Core `minimum_work_unit_output` 交付正式结果。本表只说明**规划窗口期望的紧凑视图**，不另定义强制通讯 Schema。

| 栏目 | 回传的最小内容 | 不能遗漏 |
|---|---|---|
| 身份 | task_id、执行角色、任务阶段、源仓库、工作分支、base SHA、候选 HEAD SHA | 不能只给“完成了” |
| 交付状态 | 任务目标、实际完成范围、未完成范围、具体产物路径 | 完成、部分完成、阻塞必须区分 |
| 工程变化 | 改了哪些模块、关键机制/接口是什么、最重要的设计差异 | 不贴代码全文 |
| 证据与测试 | 测试类别、执行命令/环境、通过/失败/未运行、真实证据路径/回执 SHA | 离线/模拟/静态/原生实机/UI/保存重载不可混为一谈 |
| 论证 | work_performed_or_requested、implementation_or_review_method、supportability_rationale、feasibility_rationale | 关键结论必须有对应 primary evidence |
| 风险/缺口 | 阻塞项、影响范围、严重程度、何种证据能关闭、下一责任人 | 不得把 UNKNOWN 强行填为 PASS |
| 人类决策 | 已有 Human 确认的精确来源；尚待 Human 选择的事项 | 不得冒充本窗口或 executor 的批准 |
| 建议交班 | 独立审核候选、下一步建议、必要的最小 direct refs | 开发者建议不等于规划决定 |
| D 系列反馈 | 若真实产生了 Action→Information→Field、Reader、采集、决策服务或REA接口经验，给出精确引用 | 没有则写 none，不拔高成熟度 |

**返回给 Human 转交规划窗口的消息应尽可能短**：任务 ID、最终候选 SHA、completion pointer 路径、结论一句话、是否阻塞/需 Human 决策、建议下一责任人。其余全部让规划窗口从精确 SHA 按需读取。

## 3. 根据执行者类型安排审核

- **GPT 开发窗口**：完成阶段需求/方案时交付版本化需求、论证和可观察验收，Human 负责语义/阶段确认；遇到独立核证要求，交由独立于开发窗口的审阅者。不能自行把 A0 候选改成 Human 已确认。
- **Gemini / Antigravity**：只承担有界辅助研究，交付所查范围、原始证据、成熟度、可复核步骤与 UNKNOWN；由后续 Codex 或相应主 Owner 接收，规划窗口只接收缺口与结论摘要。
- **Codex**：是正式工程实现唯一主 Owner；交付精确代码 HEAD、变更模块、工程测试和 Native/游戏读回证据，随后由不同窗口做独立审核。
- **独立审核窗口**：必须核对关键 primary evidence、任务范围和测试充分性，明确通过/拒绝/部分支持、残余风险、适用范围和对执行者论证的评估；不能复述执行者结论替代核查。
- **Human**：负责关键产品语义、受保护操作（如 master 发布/存档写入）的确认。规划窗口不替 Human 做确认。

**当前 GPT 执行任务已派发，规划窗口不重复执行或主动扩展其范围。** Gemini 尚无新任务；等待确切证据缺口后才派发，且与 Codex 共用本地工作区时必须顺序执行。

## 4. 规划窗口信息摄取门

收到回传时依次进行：
1. **核身份**：精确 task_id、branch、base/HEAD、文件路径与是否属于派发范围；
2. **核事实**：先读 commit diff/changed paths、completion pointer、必要测试摘要；仅疑点才深入 raw evidence；
3. **核成熟度**：区分未执行、离线测试、运行时读回、UI/保存证据、效果试验、独立审核；
4. **核结论**：执行者声称不自动升级；有矛盾则记录 finding 并发独立审查或补充验证；
5. **核影响**：只更新相应任务进度、待决项、下一工作单元，不复制开发全过程。

规划窗口的**健康上下文只保留五类索引信息**：
- 当前 Human 决策与准确来源；
- 当前任务清单（task_id、owner、阶段、状态、checkpoint SHA）；
- 已经确认的工程/游戏事实及对应证据指针；
- 风险、未解决问题与阻塞关系；
- 下一项派单和审核安排。

每次重大 Human 决策、正式阶段完成、重大阻塞、审核完成或工作台轮换，按既有 PRMS `SAVE_TASK_CONTEXT` 完成真实保存并检查回执；如环境无可用 PRMS 写入，使用当前获准的 GitHub Run/任务档案及精确 SHA 恢复，明确 `PRMS_NOT_SAVED`，不自造替代 WriterGate。

## 5. 当前 VAE 小型任务看板（本文件生成时的事实快照）

| 事项 | 状态 | 权威引用 |
|---|---|---|
| VAE Stage01 A0 | 候选，未绑定 Human 版本确认 | `296668026310faed42a7427c09664668e9d21ef0:01_os/07_content/_runs/run-20261030-nba2k22-vae-stage01-001/01_需求建模/A0_需求共识候选_v1.yml` |
| VAE GPT-Stage01 | 已发布开发任务；Human 表示已交由新 GPT 开发窗口，尚未收到结果 | `079ccec5a28e7a61f000b462037f1c67ae8cef11:01_os/07_content/_runs/run-20261030-nba2k22-vae-gpt-development-001/01_任务输入/task_packet.yml` |
| Gemini VAE 辅助 | 未派发 | 等 GPT 提出具体调查缺口 |
| Codex VAE 工程 | 未派发 | 等明确方案及工程实施范围 |
| 独立审核 | 未派发 | 等可审核候选 |
| 当前游戏事实和写入 | 未读取/未执行 | 首批真实游戏配置需另外按安全与权限边界验证 |
| PRMS / Communication 正式回执 | 尚未获得 | 不能声称这份 GitHub 规划文件等于 PRMS save 或 formal v2 message |

## 6. 对现有 OS 的依赖（只引用，不复制）

- Core `01_os/03_mechanisms/context_management/prms/TASK_CONTINUITY.md`：岗位窗口可替换、任务持续记录、CURRENT/PRMS 和降级 GitHub 恢复。
- Core `01_os/03_mechanisms/communication_system/README.md`、`Human中转指针契约_v2.yml`：正式消息、载体、Human 中转、可检验指针。
- Core `01_os/03_mechanisms/minimum_work_unit_output/最小工作单元输出契约_v1.yml`：完成报告的四项核心论证与审阅要求。
- Core `01_os/03_mechanisms/task_orchestration/README.md`：大任务连续执行，必须停止的行为边界。
- NBA `08_Domain_Applications/Antigravity_GM_Engine/docs/development/MULTI_MODEL_TASK_OWNERSHIP_AND_VERIFICATION_V2.md`：各开发模型职责、顺序共享本地仓库、原型优先。

此文不产生新通讯端点、不宣称自动通知、自动进度推进、额外验收门或新增 Schema。后续实际状态以独立 Run、精确 GitHub SHA 和 Human 决策为准，不能仅用此处快照替代。
