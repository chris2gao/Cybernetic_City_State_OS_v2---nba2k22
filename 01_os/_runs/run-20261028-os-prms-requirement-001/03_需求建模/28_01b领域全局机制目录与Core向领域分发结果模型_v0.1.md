# OS-PRMS 01b · 领域全局机制根目录与Core→Domain继承分发结果模型 v0.1

- **状态**：DRAFT_IN_DISCUSSION；01b专题模型（非RC01批准版、非实施方案B），承接Human新的同级领域目录及Core最终权威要求。
- **最新Human输入**：01_任务输入/14_Human领域全局机制同级目录与核心仓库继承要求_v1.md。
- **父约束**：A0 Q1–Q19正式确认、01b Q20–Q51已确认、完整A v1-RC01仍CANDIDATE_PENDING_HUMAN、27号主题模型及其Q52（全局加载深度）仍未裁决。
- **范围**：只把目录归属、机制提升、核心与领域继承关系、版本/缺口回执、测试义务建模；不实际创建根09，不更新CORE_MANIFEST、不修改主OS仓库，不运行merge，不启动开发。

## 1. 经仓库独立核对的权威关系

\`CORE_MANIFEST.yml\`：主库为 \`git@github.com:chris2gao/Cybernetic_City_State_OS_v2---core.git\`，其01_os/03_mechanisms、01_os/02_boot、01_os/05_registry、01_os/06_execution等属core-owned。domain_owned_paths含08_Domain_Applications和01_os/07_content，尚未声明候选09。主Core \`new-domain.ps1\`从Core clone，\`origin\`改名\`core\`后添加领域\`origin\`，故具有Git历史祖先联系，但GitHub fork字段为false。

NBA2K22 \`08_Domain_Applications/domain.yml\`：\`upstream_remote: core\`、\`publication_remote: origin\`、\`update_policy: Human_requested_on_demand_three_way_merge\`、\`automatic_updates_enabled: false\`。三仓Core、NBA2K22、maths2.0经GitHub按\`3ae48d2183a6e77d63a43783c7e1999edc01711e\`的compare证实该提交为master共同历史祖先。GitHub独立仓库不是GitHub Fork关系。

注意：\`CORE_MANIFEST\`某段仍记载2026-08-02冻结历史，本仓\`domain.yml\`记录2026-10-22特定Human enablement；两者说明**不能由一条过时概述擅自假定可随时自动同步所有领域**。本规划采用按仓库Human请求、实际门禁确认的升级条件。

## 2. 根目录建议：09_Domain_Global_Mechanisms/

候选树（产品目标，不是当前创建的真实路径）：

\`\`\`text
repository_root/
├── 01_os/                            # shared core：PRMS通用引擎/契约/Boot/Registry
├── 08_Domain_Applications/           # 领域源码、业务资料、具体应用
└── 09_Domain_Global_Mechanisms/      # 领域全局机制（领域所有）
    ├── README.md                     # 域机制入口/有效版本与加载责任
    ├── domain_mechanisms.yml         # 本仓领域机制权威目录
    ├── knowledge_catalog.yml         # 指向领域材料的知识目录（不是复制一切）
    └── <domain-mechanism-id>/         # 正式领域机制定义/版本或外部权威引用
\`\`\`

**归属不变量**：
1. 09整体是domain-owned；绝不可加入core_owned_paths。Core可以定义所有领域共同遵守的结构合同、validator及生成模板，但不能将NBA2K22的机制正文推入数学/英语仓库。
2. 09不取代08业务内容：源码、知识全文、业务数据、任务运行证据仍保存在其权威所有者原目录；09目录可以放本领域真正经正式发布的全局机制规范，也可以只保存到08中权威内容的可核验索引。不可混同“目录存在”和“已批准为全局机制”。
3. OS通用PRMS、全局角色、上下文装配、安全、任务生命周期、目录发现协议，应在**主Core**对应的\`01_os/\`核心机制区规范化。领域只提供其扩展目录和注册项，不能复制核心PRMS代码形成另一套真相源。
4. 本次规划Run位于NBA2K22下\`01_os/_runs/\`，已有当前任务允许路径但属于manifest定义的core-owned路径；它是本阶段的历史来源，**不是今后可直接把NBA领域分支反向合并进Core的证明**。最终核心接收需在Core适用仓库审查/授权/移植经过确认的规范内容，并分别保护domain-owned路径。

## 3. 领域总目录的逻辑字段（待A整合）

\`DomainGlobalCatalog\`：
- \`domain_id\`, \`domain_repo_ref\`, \`catalog_version\`, \`source_commit_sha\`, \`declared_scope\`, \`catalog_status\`, \`mechanism_entry_refs\`, \`indexed_count\`, \`unindexed_count\`, \`missing_refs\`, \`generated_at\`；
- \`core_compatibility\`与\`core_protocol_version\`用于证明目录遵循同一PRMS contract；不等于领域机制原文必须与Core内容相同；
- \`coverage_scope\`、\`excluded_count\`与\`is_exhaustive_within_scope\`不可互相猜测。

\`DomainGlobalMechanismEntry\`：
- \`mechanism_id\` / \`canonical_ref\` / \`mechanism_version\` / \`source_commit_sha\` / \`owner=domain\`；
- \`purpose\`、\`capability\`、\`applicable_tasks\`、\`role_applicability\`、\`dependencies\`、\`trigger_conditions\`、\`required_context_refs\`；
- \`governance_status\`（proposed/reviewed/published/stale等候选）、\`activation_status\`（单独治理）、\`loading_priority\`、\`summary_refs\`、\`source_evidence_refs\`；
- \`promoted_from_experience_refs\`、\`review_receipt_ref\`、\`approval_ref\`；如果仅导航到08原件，不能把导航摘要误报为正式机制全文。

物理字段名、YAML/JSON编码、文件分片及角色加载算法在02/03验证；01b明确要求这些逻辑信息可追溯、可校验。

\`domain.yml\`未来需新增/兼容声明领域全局机制目录根及其有效目录引用；Boot/Registry需识别\`domain_id\`与可选/必需G2目录（缺失/空目录时必须有明确结果），严禁默认读遍完整08。

## 4. 规划到交付的两条升级流水线

**A. 通用PRMS Core规划与实现**
- 本Run仅形成01b完整A候选，经Human精确确认方可进入02。
- 02基于Core和领域仓库实证已有结构、分发冲突、能力；03设计B获得Human确认后按Q35=C/Q36=B**直接纳入Core规划体系**，无需把独立“迁移规划项目”作为产品必经门。
- Core规划规范≠运行程序已完成；随后按04–07及实际core-owned授权开发/测试/独立审核/受保护发布。
- 禁止将NBA领域整个08目录或领域任务运行记录随PRMS规范反向合并到Core；仅抽取/校验被确认的通用成果及需要的可审核依据。

**B. 任一领域中的经验→全局机制**
- TaskEvent/ExperienceCard仍有原始来源和现行有效性；任务关闭后T1退出默认上下文，但T2历史可追溯。
- 对可复用经验提出PromotionCandidate，评估适用范围、证据、已有机制是否已覆盖；选择 \`G1_core\`（跨领域通用）、\`G2_domain\`（仅当前领域）、\`remain_task_history\`（不提升）。
- 候选须有目标owner、差异、依赖与兼容、验证与审核、Human需要的受保护动作确认。经过对应流程方可正式发布到Core G1或领域09 G2；不得“完成任务”自动提升为canonical或绕过master保护。
- 例如REA若满足全局适用性，可候选进入Core能力/工具目录；具体成熟度与内容范围需真实证据，不因举例宣布REA已移植。

## 5. Core更新后的领域继承

\`\`\`text
Core：正式PRMS通用机制版本及规范
  ↓ 经Human要求/发布门，核验本领域上游commit与差异
Domain A (NBA2K22)：继承通用Core + 自身09领域全局机制 + 自身08应用
Domain B (Maths)：   继承通用Core + 自身09数学机制 + 自身08教学应用
Domain C (English)： 继承通用Core + 自身09英语机制 + 自身08学习应用
\`\`\`

- 版本记录：Core源commit、目标domain现行commit、合并结果与接受回执。不得以同名机制或GitHub forks关系替代精确祖先。
- 领域09独立存储，Core merge不得覆盖domain-owned真实内容。规范兼容性、缺目录/旧版本、冲突、升级失败须返回可观察状态。
- 不允许自动在六个仓库执行git merge；每仓根据自身\`update_policy\`和Human授权及受保护发布规则独立完成。
- Core仓库可定义未来新领域脚手架创建09结构；现行\`new-domain.ps1\`只提示填08/03，未来如更改需在Core授权开发中连带调整生成器与manifest/validator/Boot接口；本阶段不执行。

## 6. 关键验收（未来，不是当前测试通过）

| SC | 触发 | 可观察要求 |
|---|---|---|
| SC-DGM-01 | 新建NBA2K22工作窗口 | 正确发现当前Core通用机制目录及仅本领域正式发布的09目录，不把08全部文件直接列为正式机制 |
| SC-DGM-02 | 数学OS窗口 | 发现同一Core contract但数学领域G2，不载入2K机制 |
| SC-DGM-03 | 某项08源规范变更 | 相应09索引/概要stale，保留原始来源版本；不将旧索引当已验证最新 |
| SC-DGM-04 | 一项REA领域经验拟升级Core | 生成promotion candidate与来源/适用性/差异，未经实际审核批准不得自动发布 |
| SC-DGM-05 | Core通用PRMS升级，经Human要求传播 | 域侧按精确core commit、三方合并和保护门验证，09不被覆盖，报告各域实际接受状态 |
| SC-DGM-06 | Core升级与领域09机制不兼容/目录缺失 | 显示compatibility/missing/conflict，阻断不能核验的恢复，不隐式把领域能力标为available |
| SC-DGM-07 | 本领域当前任务完成 | T1从自动活动装配退出，T2史可索引；K1经验只有正式发布后才进入G1/G2 |
| SC-DGM-08 | 用户仅同意加载G1而拒绝G2 | 加载回执明确G2未授权、不自动补读；若任务必须依赖G2则报告缺口/阻断 |

SC均为NOT_RUN。Q52（全局加载深度）未裁决，这里只定义机制“能被正确发现”的要求，不预先决定每次是否全文预加载；Human选择与现有固定Boot权威不互相覆盖。

## 7. 讨论缺口与是否需要追问

- 本次Human明确倾向根08同级并可建立新目录，\`09_Domain_Global_Mechanisms/\`是规划模型的具体推荐，不需要为编号/命名制造新Human微审批；若Human有不同命名需求，后续改候选即可。
- 是否把新根目录写入所有现有领域仓库、何时实际创建属于执行授权与后续设计，不在01b实施。
- **Q52仍待Human决定**：G1/G2“全局加载”代表全正文默认还是全目录概要+相关正文加载。本问题会改变预算、启动与验收，不能代选。
- 是否每新窗口都询问Human还是可复用明确同一任务/岗位范围，是后续承重问题；先承接Q52结论。
- Core/Domain受保护发布遵守既有门，不将“最终向其他仓库分发”解释为当前自动修改所有master。

## 8. 完整A与阶段限制

本候选属既有RES-017..020、RES-013、RES-009等的补充，不变更A0 Q1–Q19和01b Q20–Q51，不自动改变20 RES计数。最终字段/追踪及目录要求应纳入后继RC02候选并明确Human审查；完整A仍待Human精确确认，02–07未启动。
