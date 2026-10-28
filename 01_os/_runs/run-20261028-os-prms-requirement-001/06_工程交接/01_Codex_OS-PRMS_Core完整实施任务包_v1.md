# OS-PRMS Core 实现任务包 v1 — 供 Codex 在 Human 指派后执行

**状态**：DESIGN_HANDOFF_READY / ENGINEERING_NOT_STARTED。该文件是可执行工程任务合同，不是 Codex 已接单、代码已提交、测试通过或 Core/master 已发布的回执。
**任务**：os-prms-global-persistent-role-memory-20261028-001
**工程唯一 Owner**：Codex。GPT 仅是需求/设计规划基线与后续审核协助，独立最终审查另派。
**领域侧资料仓**：chris2gao/Cybernetic_City_State_OS_v2---nba2k22
**规划分支**：planning/os-prms-a0-confirmed-01b-20261028
**Core 目标仓**：chris2gao/Cybernetic_City_State_OS_v2---core
**禁止**：未经 Human 对受保护操作的有效确认，不合并或修改 Core/master、不自动合并任何领域 master；不创建或授权新的真实私有状态仓库、不启用常驻服务、不处理真实敏感岗位数据；不访问NBA2K22游戏、REA、存档或进程。

## 0. 第一动作：读取真正的项目/OS背景

先按 Core 和目标仓当下的 AGENTS、OS Boot、任务权限与发布规则启动，读取 fresh master/目标分支 SHA。若 Core 安全/权限契约与本任务包不一致，以当下可证明的有效规则为准并报告冲突。**不要仅凭本提示词自定义新权限。**

必须逐份读取、核对 Git blob、写出 source_refs_read（均从 NBA2K22 本Run目录相对定位）：

1. `03_需求建模/29_OS-PRMS_完整需求结果模型A_v1-RC02_整合封版.md` — Human已批准完整A；blob ce037bb99e02c150f5e619eeb022b21444619b8c。
2. `01_任务输入/16_完整需求结果A_v1_RC02_Human确认与版本绑定记录.md` — A批准来源。
3. `01_任务输入/17_Human批准设计B及G1G2细化版本绑定_v1.md` — B批准与细化后继。
4. `04_方案设计/01_OS-PRMS_完整设计B_v1-RC01_初始候选.md` — B原始设计，归档blob 7b12ecb88c8d9150c8d3cffc8a71f91d97f96f48；原文写待审核属于历史状态，以批准后继记录解释。
5. `04_方案设计/06_G1G2机制全集分类与按需加载细化_B-v1-RC01-ADDENDUM-CATALOG-01.md` — G1/G2清单及Q52=B，归档blob df209a2bbc52014bdc1442890adcd599c01c1fb3。
6. `04_方案设计/07_G1G2来源全集机器盘点_v1.json` — 固定树与NBA13模块机读目录；它是静态设计快照，不是运行时。
7. `04_方案设计/03_B-v1-RC01_工程验收场景_28项.yml` 与 `04_方案设计/08_G1G2补充工程验收场景_20项.json` — 合计48个候选测试场景，全部NOT_RUN，只有真实测试才能升级结果。
8. `02_信息收集/01_现有能力与G1G2来源映射_v1.md`、`02_信息收集/02_NBA开发经验升级Core可迁移性审查_v1.md` — 既有能力与领域经验；REA技术知识仅作为索引候选，本任务不运行REA。
9. `04_方案设计/05_PRMS串行实施与Core升级路线图_v1.md` — 本项目与后续工作流/REA升级严格串行。

同时读取 Core 当前的 `CORE_MANIFEST.yml`、`01_os/02_boot/context_management/启动清单_v1.yml`、`01_os/05_registry/context_management_v1.yml`、`01_os/03_mechanisms/context_management/`、`01_os/03_mechanisms/mechanism_activation/`、`01_os/06_execution/boot/context_management/`、工作集可见性和归档实现。不得根据 NBA 旧继承副本猜 Core 最新代码。

NBA 领域入口：`08_Domain_Applications/Antigravity_GM_Engine/PROJECT_INDEX.md` 和 `docs/development/PROJECT_MODULE_REGISTRY_V2.json`，来源为 Draft PR #18 @ 094f1aa641f93dec2277707ad9dbf5bdb0341247；P00–P12是十三个项目模块，不是13个已发布G2。其他领域的09缺失仍须显式报告。

## 1. 承重不变量（不可由Codex简化掉）

- B0固定OS Boot和真实Human/任务权限不能被可选记忆选择覆盖。
- G1完整发现来自目标已安装Core的正式机制/Workflow/Boot/Registry清单；G2只来自当前domain_id的已正式发布09，08业务/研究/源码只是候选或来源。目录可发现≠原文已载入≠机制可运行≠动作获授权。
- G1与G2目录概要全面发现；真正canonical正文按岗位、任务、机制依赖与Human当前会话选择加载。所有跳过、未注册、缺失、陈旧和因预算过滤的项目都必须可计数/追溯。
- 独立可变岗位记忆state repo不混入可向领域传播的Core代码树。必须有稳定Role、追加不可改史事件、单有效CURRENT、Checkpoint、source SHA、增量摘要/索引与血缘。
- 会话接管只承诺PRMS有效CURRENT写入失权；旧窗口无法通过有效Git/REST旁路直接改state ref的反例必须成功。合作式epoch检查不能冒充强制WriterGate。
- 不可盲目重试返回未知的外部动作。发布超时要读回当前ref和operation_id，未发布候选不得污染有效CURRENT。
- 全量复制要求把全部可复制内容真实写入目标仓并校验，不是只复制目录、摘要或原路径指针。
- T1当前/仍未结束系列可恢复，T2已确认终态历史默认索引；生命周期UNKNOWN仍须可发现，不擅自归档或删除。
- K1经验仅是候选；经独立审核和Human/owner正式批准后方可作为K2进入G1或G2。
- Core所定义机制生效等级L0_DEFINED..L4_E2E_ADVERSARIALLY_VERIFIED与PRMS加载深度L0..L4是不同概念，不可混合或从文件存在直接推导运行成功。

## 2. 一个主任务、顺序开发

D0 基线与状态修复：完整核对A/B后继批准、Core/Domain实际SHA、权限与Run。当前Run的 `run.yml` 仍可能是旧RC01/confirmed:false；按有效仓库机制合法同步并远端读回，保持历史证据。**如果写入被安全检查拒绝，停止该写操作并明确阻断，不换载体绕过安全检查。**

D1 机制目录：Core规范/Schema与Validator、G1树/Registry交叉校验、G2按domain_id隔离、09 ownership/新域脚手架、加载回执。最先复现 Core 7机制/7阶段/7Boot/13Registry 与 NBA 13候选、六领域隔离的确定性清单，并显式报告任何新版本变化。

D2 持久状态协议：先在离线临时Git沙盒实现单ref有效CURRENT、事件/检查点、CAS/非force提交、操作幂等与读回；再决定是否有获准的隔离GitHub测试仓可作线上验证。不能未经确认建立真实状态库或默默替换为Core public repo。

D3 检索/生命周期：增量Summary/Index，依赖SHA变化精准stale，T1/T2归档/UNKNOWN，K1候选与K2发布，跨角色全量复制与风险报告。摘要不可替代Human批准原件。

D4 写入门和恢复：可信session身份+WriterGate受控写入；旧写晚到、直写REST/Git旁路、broker故障、commit未知、并发接管反例；G1/G2摘要发现、Human当前会话可选正文、预算限制与ContextRecoveryReceipt。若受限于实际平台无法验证强制隔离，应返回FENCING_NOT_ENFORCEABLE并把相应需求标未完成，向Human提出具体技术替代选择，不暗降级为“已通过”。

D5集成和独立验收准备：Core程序、Boot/Registry扩展、领域G2目录兼容、48候选场景的可运行测试与证据。真实新 GPT/Codex 恢复应有固定答案对照、实际读取路径/哈希和遗漏统计。独立审查必须与工程实现Owner不同，Human最终决定master/领域集成。

上述 D0–D5 顺序推进；新设计规范的Core升级可在授权的Core任务分支先行，不代表软件已上线。开发中不把每次可逆技术选择升级为Human审批；但重大新产品取舍、真实凭据/状态仓准入、Protected ref发布、历史改写等不得推定已授权。

## 3. 输出物与真正的完成定义

**交付要求**：源代码、可重复测试命令、固定输入和raw输出、通过/失败的分项结果、覆盖的RES-001..020、28+20场景逐项证据、Git commit/PR、源和目标哈希、失效/残余风险、Core和领域的差异及精确引用、独立审核所需的最小复验方式。完成工程任务前必须更新相关项目索引/模块机器表并远端读回，不得只在聊天中说“已同步”。

不能报告为通过：仅有索引文件、Mock/fixture没有平台写入证明、GitHub Contents SHA作为多文件原子事务、源文件显示“已部署”但没有实际loader回执、B本身获得Human批准、或前期NBA2K22原生游戏实测。

**受保护发布**：Codex默认仅在适当的Core task branch创建PR；不自行合并master，不自动传播到领域，不激活服务。未来新私有状态仓库的创建/权限配置、真实Human身份凭据与跨仓保护政策需得到实际明确批准。若这些前置条件未解决，先交付能合法完成的实现及准确BLOCKED项，而非假装整个系统成功。

## 4. 拟交付的最终Human可读报告

- 工作完成与尚未完成的功能列表（不是只有代码文件数）。
- 哪些G1/G2真实存在，哪些只是规划，哪些已实际加载，来源和SHA是什么。
- 采用的state store/WriterGate实际技术方案与旧窗口绕过测试结果。
- 新窗口恢复几项Human批准/任务进度/历史经验，漏失和token成本。
- 48项测试逐项真实状态和独立审核意见。
- Core master与每个领域是否已集成的真实状态，不能由PR存在推断上线。

**本文件发布即为规划交接资料，Codex的实际执行仍须由适当任务入口发起；不自动启动代码开发。**
