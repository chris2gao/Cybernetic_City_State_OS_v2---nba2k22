# OS-PRMS 规划档案总索引 — 已批准 A/B 与 Codex 工程交接

**日期**：2026-10-28  
**所在仓库**：`chris2gao/Cybernetic_City_State_OS_v2---nba2k22`  
**归档分支**：`planning/os-prms-a0-confirmed-01b-20261028`  
**作用**：唯一入口，面向未来 GPT、Codex、独立审核者和 Human。它索引所有重要资料，不代替各文件原始内容或自动赋予运行权限。

## 当前权威判断

1. **需求 A-v1-RC02 已获 Human 确认**；来源及精确 SHA 见 `01_任务输入/16_完整需求结果A_v1_RC02_Human确认与版本绑定记录.md`，完整 A 文件在 `03_需求建模/29_OS-PRMS_完整需求结果模型A_v1-RC02_整合封版.md`，Git blob `ce037bb99e02c150f5e619eeb022b21444619b8c`。
2. **设计 B-v1-RC01 已获 Human 批准**；后续提出必须细化“G1机制全集、领域G2隔离、Q52=B按需加载、完整性检查”，由 `01_任务输入/17_Human批准设计B及G1G2细化版本绑定_v1.md` 绑定。
3. **G1/G2细化已归档为B的后继说明**；不将新的目录列表擅自升级成已上线机制，也不声称六领域已部署09。
4. 设计中由 GPT 做建模、Codex 做单一工程实现 Owner、独立审核者验收。**真实工程代码、Git状态仓、WriterGate、恢复程序和E2E验证尚未开发/通过**。
5. 本档案位于 NBA2K22 的 domain-owned Run，未修改 Core/master、任何领域master或游戏环境。

## 先读的文件（均相对本 Run 根目录）

| 顺序 | 文件 | 用途和状态 |
|---|---|---|
| A-1 | `03_需求建模/29_OS-PRMS_完整需求结果模型A_v1-RC02_整合封版.md` | Human已批准的20项RES需求权威 |
| A-2 | `01_任务输入/16_完整需求结果A_v1_RC02_Human确认与版本绑定记录.md` | A批准版本证据 |
| B-1 | `01_任务输入/17_Human批准设计B及G1G2细化版本绑定_v1.md` | B正式批准及附录说明 |
| B-2 | `04_方案设计/01_OS-PRMS_完整设计B_v1-RC01_初始候选.md` | Human后续批准的原始设计候选；原文待审核状态保留历史 |
| B-3 | `04_方案设计/06_G1G2机制全集分类与按需加载细化_B-v1-RC01-ADDENDUM-CATALOG-01.md` | 7 Core机制、7 Workflow、7 Boot、13 Registry、六领域与NBA13模块、加载合同 |
| B-4 | `04_方案设计/07_G1G2来源全集机器盘点_v1.json` | 固定 SHA 来源清单；静态设计快照、不是实际加载证明 |
| B-5 | `04_方案设计/03_B-v1-RC01_工程验收场景_28项.yml` | 28项产品工程验收候选，均尚未运行 |
| B-6 | `04_方案设计/08_G1G2补充工程验收场景_20项.json` | 20项加载/目录/隔离负例候选，均尚未运行 |
| E-1 | `02_信息收集/01_现有能力与G1G2来源映射_v1.md` | Core/Domain功能复用和缺口取证 |
| E-2 | `02_信息收集/02_NBA开发经验升级Core可迁移性审查_v1.md` | NBA开发规范、索引同步与REA经验的候选继承判断 |
| P-1 | `04_方案设计/05_PRMS串行实施与Core升级路线图_v1.md` | 先PRMS、后工作流/REA/其它OS升级 |
| P-2 | `04_方案设计/02_B-v1-RC01_Human初始审核摘要_历史候选.md` | 审核前原文快照，批准状态已由B-1后继解释 |
| C-1 | `06_工程交接/01_Codex_OS-PRMS_Core完整实施任务包_v1.md` | 已执行的工程任务合同，保留历史输入 |\n| H-1 | `05_使用教程/01_OS-PRMS_Human新窗口岗位任务记忆使用教程_v1.md` | **现用指南**：指定岗位、按任务保存/恢复、G1/G2按需读取、Human转交与上下文回执 |
| H-2 | `05_使用教程/02_Fork共用上下文基线与四类岗位窗口规划_v1.md` | **规划候选**：公共母窗Fork成4种OS岗位模型、G1/G2/P00–P12共用索引、岗位激活提示词；尚未实测自动Fork |

## 最新进度追加（2026-10-29，保留原 A/B 不改写）

- Core PR [#10](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---core/pull/10) 已按 Human 最终限定的**任务上下文保存、切换与恢复**范围通过独立静态审查，并合入 Core/master，merge commit `e075cdf288a765b7bfd2f4891c8f384404da16e1`。工程代码验证候选为 `26daab91962354e5bc37391e523771e239ada4ed`。
- Codex 交付记录为 77 项 PRMS 测试、44 项工作集回归和 8 项管理检查通过；11 项真实 GitHub/宿主/模型窗口测试仍为 NOT_RUN。现有恢复方式为**显式保存+Human中转**，不声称聊天平台自动注入或已部署生产状态仓。
- NBA2K22/master 当时仍在进行 [Core Issue #11](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---core/issues/11) 的专项继承同步；Human 已明确取消其他领域的同步要求，**只涉及 Core 与 NBA2K22**。在 GitHub 远端回读同步完成前，不声称 NBA/master 已继承 PRMS。
- 原 Run `run.yml` 已在工程 D0 进行修正并远端回读确认 `requirement_A=OS-PRMS-A-v1-RC02`、`confirmed:true`，设计 B Human 确认也已记录。历史旧指针以 Git 版本保留。
- 本档案 **H-1 使用教程**说明当下可立即从 GitHub Run 恢复上下文，以及未来有独立持久状态仓时如何使用 `task_cli.py save/list/resume`。尚未配置真实状态库的窗口不得声称已完成 PRMS 事务保存。

## 下一步

- Codex 依 Issue #11 在 NBA2K22 领域安全继承 Core 更新并远端读回；不更新其它领域。
- Human 新开 GPT/Codex 窗口时优先遵循 H-1，指定目标领域/岗位/任务，通过现存 Run 或真正保存的 PRMS 状态进行只读恢复。
- 若日后启用真实岗位状态库，应单独记录其实际部署配置与保存回执，再验证跨窗口加载。当前不启动后台协调器。

**维护规则**：本索引是入口与状态快照；任何新里程碑都要绑定真实 Git source/ref。不得把设计、离线测试、代码已合并、真实运行部署这四个概念混同。
