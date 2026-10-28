# NBA2K22 开发规范、REA 与工作流成果向主 OS 提升的独立源证据核查

**日期**：2026-10-28  
**性质**：阶段02预调查/独立迁移候选审查；只读对照。没有运行游戏、REA或写入主 Core；没有对任何候选作正式OS发布决定。  
**主 Core**：`chris2gao/Cybernetic_City_State_OS_v2---core@446ca66ad48831f5fcdb1af18f37d07619e048c4`  
**NBA2K22 master**：`chris2gao/Cybernetic_City_State_OS_v2---nba2k22@7742568ac677b3c16079887463f05e81cb1191ed`  
**NBA2K22 PR #18**：`planning/nba2k22-myleague-role-native-execution-surface-20261028@094f1aa641f93dec2277707ad9dbf5bdb0341247`；2026-10-28核查为 `OPEN / DRAFT`，**尚非 master**。基于 `integration/nba2k22-rea-native-control-pr10-pr16-20261028`。  
**原 PRMS 规划分支**：`planning/os-prms-a0-confirmed-01b-20261028@cd018e2a3aa0c28c9b8b0db0f7c4c7df88491a21`，RC02 blob `ce037bb99e02c150f5e619eeb022b21444619b8c`。  
**根级限制**：Core-owned文件只在主Core正式授权中实施；09领域全局目录应Domain-owned。没有自动跨仓库合并许可。

## 一、摘要：能提升什么，不能直接复制什么

判定分四类：**A：Core机制优先候选**；**B：Core通用化后可采纳**；**C：仅领域规范/领域profile**；**D：证据或版本不足，需要实证**。这里的“候选”不等于获得正式Human发布许可。

| 编号 | 经验/工具 | 处理分类 | 对 Core 的具体动作建议 | 成熟度与验证缺口 |
|---|---|---|---|---|
| P-01 | 项目总索引与机读模块注册表 | A | 在 PRMS 中增加G1/G2/模块的统一索引合同与角色/任务相关载入协议；Core只提供规则，不写入NBA内容 | NBA侧已有13模块JSON和Human可读索引；PR#18 Draft；Core无相同通用模块协议；尚无自动索引覆盖测试 |
| P-02 | 任务开发时同PR同步受影响模块、来源与证据 | A | 通用 `affected_module_ids`、`source_refs_read`、`index_sync_commit`、`INDEX_SYNC_PENDING` 及recovery receipt；与Core Registry/Context机制对接 | NBA侧为人工协作合同，明确尚无CI/Hook自动强制；未来Core可先实现validator |
| P-03 | 01a共识→01b完整需求A | A | 审阅NBA的 `方法论_v0.4.md`、Boot/Registry引用，结合Core v0.2迁移；保留旧阶段ID与兼容验证 | 已回读Core `方法论_v0.2.md` (blob `4c81218b68da47305d333967400d4e03f74705f1`)，正文未包含01a/01b划分；Core未找到v0.4，入口仍指v0.2；NBA属特批先行core-owned修订，不能直接merge整个领域分支 |
| P-04 | 多模型单Owner、同一共享仓库顺序handoff | B | Core `task_orchestration` 和context的环境能力约束；在共享worktree时串行，隔离worktree时可按明示条件并行 | NBA V2为特定硬件/模型角色分工，不应强制所有领域GPT规划/Codex编码/Antigravity辅助 |
| P-05 | Producer/Consumer交付包与三层接收核验 | B | 在Core已有handoff、verification与publication contracts补齐source SHA、exact_scope、reproduction、evidence_level与`ACCEPTED_FOR_DEFINED_SCOPE` | 已有OS版本/allowlist/receipt，需先diff防止重复；无跨域回归测试 |
| P-06 | 研究先行且区分概念可转移与运行事实 | B | 抽象“领域知识研究→本环境权威原件→实际观察/执行核验”的证据成熟度；纯机械问题按EIG跳过额外研究 | NBA的游戏官方/社区、MyNBA/PC映射为具体域规则；Core stage02已有信源独立及交叉核实机制，扩展应最小化 |
| P-07 | 实现优先、精简开发期测试、候选统一独立审核 | B | 作为Core已有task_orchestration、workflow 04/07验证分层的改进规则和示例，不能免除授权、核心安全或已要求的测试 | NBA用户授予的测试取舍不可直接成为所有领域统一强制安全阈值 |
| P-08 | REA逆向工具本体 | D→B | 作为 `01_os/04_skills_and_tools/rea/` **可选工具**及 `01_os/06_execution/tools/rea/`调用wrapper、Registry入口的候选；版本可用性逐环境验证 | NBA历史环境REA6.8.0、229工具目录，Windows/Frida/资源有限成功；主Core没证据显示已装/可调用；绝不直接列为全局已验证工具 |
| P-09 | REA方法论（ABI、来源、有限预算、证据等级） | B | Core“Native研究方法与安全回执”通用模板；默认不启用附加/写入；将工具使用契约与Native逆向研究规则区分 | 历史报告/实机案例可供取证，其他系统通用性待验证 |
| P-10 | 游戏构建RVA、角色动作ID、具体交易/球探和游戏ABI | C | 留NBA2K22领域09目录/08真实原件，以Core版本化profile合同引用；不要复制进Core通用实现 | 特定游戏build和场景，只对单个参数/对象实测，不是全机制验证 |
| P-11 | 研究证据等级 / UNKNOWN / 读回语义 | A/B | 加入PRMS事件、经验、索引与操作回执的不变量；精确区分STATIC/FIXTURE/LIVE_EFFECT/SAVE_RELOAD/INDEPENDENT_AUDIT | Core已有“事件/事实/失效”理念，需统一值域，不创建第二套权威 |
| P-12 | 跨窗口REA交接/失败签名与不盲重试 | B | 纳入PRMS RecoveryPackage、tool diagnostic和失败预算指导；变化的是通用故障协议，非旧PID/旧脚本内容 | REA交接已记录失败、修复及结果；不同工具/平台不得直接套用同一超时时间 |

## 二、实际读取的精确源文件与可核对事实

下面的固定URL均可以直接打开。原件位于NBA2K22 GitHub；新分支不等于master。

1. **项目总索引**：[`PROJECT_INDEX.md`](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/blob/094f1aa641f93dec2277707ad9dbf5bdb0341247/08_Domain_Applications/Antigravity_GM_Engine/PROJECT_INDEX.md)，Git blob `d916a3e2ba5edddf8afff3b0e639bd1fd31b3015`。声明每个NBA新任务按模块定位2–5个源，P04机制知识库和P09 REA按工作性质加载；索引与项目角色事实分开；世界数据独立分支须用固定SHA查，不可断言“没有”。**检测到项目索引自己已说明其一个相对链接可能错位，应由后续验证器检查实际路径。**
2. **项目机器注册表**：[`PROJECT_MODULE_REGISTRY_V2.json`](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/blob/094f1aa641f93dec2277707ad9dbf5bdb0341247/08_Domain_Applications/Antigravity_GM_Engine/docs/development/PROJECT_MODULE_REGISTRY_V2.json)，Git blob `77721b1dac8c90dc21b6daea71606f22ac3edebb`。JSON实际可解析，`schema_version=nba2k22.project_module_registry.v2`，声明与实数均为13模块（P00-P12），P09状态`RESEARCH_PROTOTYPE_SELECTED_LIVE_EFFECTS`，P10状态`HUMAN_REVIEW_REQUIREMENTS_FIRST_PASS`；另含6条recent task和2条独立分支资产；状态明确是DRAFT_PR18_NOT_IN_MASTER。
3. **索引同步合同**：[`PROJECT_INDEX_SYNC_CONTRACT_V1.md`](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/blob/094f1aa641f93dec2277707ad9dbf5bdb0341247/08_Domain_Applications/Antigravity_GM_Engine/docs/development/PROJECT_INDEX_SYNC_CONTRACT_V1.md)，Git blob `416e9eaeadbb7b29bd414f1c5368834f54382835`。明定同PR更新模块状态、受影响文件、证据、remaining gaps、最新commit和index_sync_commit；`INDEX_SYNC_PENDING`与`MODULE_SOURCES_NOT_LOADED`为失败状态；**明确尚未部署CI/Hook保证**。
4. **跨模型V2**：[`MULTI_MODEL_TASK_OWNERSHIP_AND_VERIFICATION_V2.md`](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/blob/094f1aa641f93dec2277707ad9dbf5bdb0341247/08_Domain_Applications/Antigravity_GM_Engine/docs/development/MULTI_MODEL_TASK_OWNERSHIP_AND_VERIFICATION_V2.md)，blob `ea1d5dd76d3c0aab061154ea92e0177125c6491d`。共享仓库顺序交接、checkpoint、Codex主Owner/Antigravity有界辅助、原型连续修订和集中独立审核。
5. **跨模型V1**：[`MULTI_MODEL_TASK_OWNERSHIP_AND_VERIFICATION_V1.md`](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/blob/094f1aa641f93dec2277707ad9dbf5bdb0341247/08_Domain_Applications/Antigravity_GM_Engine/docs/development/MULTI_MODEL_TASK_OWNERSHIP_AND_VERIFICATION_V1.md)，blob `7b850cb71a2f7d513cb10b01bd78dc73140438fd`。Producer/Consumer至少有task_id、input_refs、exact_scope、artifacts、reproduction、evidence_level、acceptance；有DELIVERED_UNVERIFIED/RECEIVER_CHECKED/ACCEPTED_FOR_DEFINED_SCOPE。
6. **开发边界/测试**：[`DEVELOPMENT_BOUNDARIES_AND_VALIDATION_POLICY.md`](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/blob/094f1aa641f93dec2277707ad9dbf5bdb0341247/08_Domain_Applications/Antigravity_GM_Engine/docs/DEVELOPMENT_BOUNDARIES_AND_VALIDATION_POLICY.md)，blob `7200d0c90a8fc3a1cbdcb23cc313f772f24537b3`；[`GAME_MECHANICS_RESEARCH_FIRST_DEVELOPMENT_POLICY_V1.md`](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/blob/094f1aa641f93dec2277707ad9dbf5bdb0341247/08_Domain_Applications/Antigravity_GM_Engine/docs/GAME_MECHANICS_RESEARCH_FIRST_DEVELOPMENT_POLICY_V1.md)，blob `fc438e4e944a7c969578daf5d08fcd6c45e4eda3`。
7. **REA 原始Playbook**：[`REA_DEVELOPMENT_PLAYBOOK_V1.md`](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/blob/b16e69727987f29bff5e2ee31ce82891102ab2d9/08_Domain_Applications/Antigravity_GM_Engine/docs/development/REA_DEVELOPMENT_PLAYBOOK_V1.md)，blob `aa2dda60421c59b8db37831cf271a46979a7324f`。历史分支文件而非当前 PR #18 同路径；说明REA6.8.0/229工具、有限读取、资源、fixture、失败界限。
8. **REA 交接总录**：[`REA_WINDOW_CONTEXT_HANDOFF_20261028.md`](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/blob/094f1aa641f93dec2277707ad9dbf5bdb0341247/08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_control/REA_WINDOW_CONTEXT_HANDOFF_20261028.md)，blob `4cc0b2c487315cc26bd6f25419e0afea63f94ddc`。原文记录整游戏Ghidra四次超时、局部PE与Frida适配、权限/ABI/对象/线程校验、未知副作用不重放及实际请求的证据链，旧环境路径只是历史证据。
9. **REA实际结果**：[`VALIDATION_RESULTS.md`](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/blob/094f1aa641f93dec2277707ad9dbf5bdb0341247/08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_control/VALIDATION_RESULTS.md)，blob `1bc69dafc548ff9326719c96afc19600c2c4dad4`。特定Coach字段、原生交易及既有球探Goal的实际效果报告，另记录Append被游戏拒绝；不证明所有62个行动、Save/Reload或生产可用。
10. **REA提升边界**：[`REA提升为OS通用工具的经验继承与分层_v1.md`](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/blob/094f1aa641f93dec2277707ad9dbf5bdb0341247/01_os/07_content/_runs/run-20261028-nba2k22-role-native-execution-model-001/03_%E6%96%B9%E6%A1%88%E8%BE%B9%E7%95%8C/REA%E6%8F%90%E5%8D%87%E4%B8%BAOS%E9%80%9A%E7%94%A8%E5%B7%A5%E5%85%B7%E7%9A%84%E7%BB%8F%E9%AA%8C%E7%BB%A7%E6%89%BF%E4%B8%8E%E5%88%86%E5%B1%82_v1.md)，blob `2b5d51ef4e3273835d970fe1ad376d7d2fd1efd8`，明确`PROPOSED_FOR_OS_TOOL_GOVERNANCE`，并未接入Core。
11. **角色执行架构V2**：[`ROLE_BATCH_NATIVE_EXECUTION_ARCHITECTURE_V2.md`](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/blob/094f1aa641f93dec2277707ad9dbf5bdb0341247/08_Domain_Applications/Antigravity_GM_Engine/docs/development/ROLE_BATCH_NATIVE_EXECUTION_ARCHITECTURE_V2.md)，blob `ac7ec9ba76bb7bb13be52a5bd512e598a04e5e38`。模型决定WHAT/WHO/VALUE，聚合器检测冲突/冻结请求，执行器负责HOW、单项执行与读回；当前是未来架构合同而非已实现批处理。
12. **Core 现有机制**：[`context_management/方法论_v1.md`](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---core/blob/446ca66ad48831f5fcdb1af18f37d07619e048c4/01_os/03_mechanisms/context_management/%E6%96%B9%E6%B3%95%E8%AE%BA_v1.md)，[`task_orchestration/README.md`](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---core/blob/446ca66ad48831f5fcdb1af18f37d07619e048c4/01_os/03_mechanisms/task_orchestration/README.md)，[`04_skills_and_tools/README.md`](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---core/blob/446ca66ad48831f5fcdb1af18f37d07619e048c4/01_os/04_skills_and_tools/README.md)。Core已有有效上下文、耐久事实和事件三平面，任务编排含内部continuation/真停止，工具登记强调现场版本验证与按需调用；**因此不应另造并列OS**。
13. **阶段01差异**：Core [`01_需求建模/README.md`](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---core/blob/446ca66ad48831f5fcdb1af18f37d07619e048c4/01_os/01_workflow/01_%E9%9C%80%E6%B1%82%E5%BB%BA%E6%A8%A1/README.md)明确指向`方法论_v0.2.md`；Core当前没有v0.4文件；NBA分支[`方法论_v0.4.md`](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/blob/cd018e2a3aa0c28c9b8b0db0f7c4c7df88491a21/01_os/01_workflow/01_%E9%9C%80%E6%B1%82%E5%BB%BA%E6%A8%A1/%E6%96%B9%E6%B3%95%E8%AE%BA_v0.4.md)区分01a共识与01b完整A，并记载2026-10-23 Human特批本领域先行。应专门回Core进行语义/runner/registry兼容核销，非直接复制覆盖。

## 三、对“REA已全局安装”的精确解释

NBA历史交接材料声称用户某台Windows开发机已装REA6.8.0并接入Codex/Antigravity；真实实机验证也支持在彼时特定进程与工具环境成功。**这不能推出主Core工作环境、其他数学/英语仓库或未来新窗口也能调用REA。** Core `04_skills_and_tools/`要求每个外部工具有安装证据、版本和验证wrapper，按需注册并明确失败退路。建议先执行工具治理/环境隔离验证：

- 获取实际REA当前工具清单/schema/版本和目标系统支持矩阵，不照抄历史229条作为全部可用能力；
- 定义核心`tool adapter`、project profile、环境/进程权限，默认关闭有副作用的Attach/Write；
- 以离线fixture和隔离无害对象验证安装/版本/错误处理，不能直接拿真实游戏操作冒充Core跨域测试；
- 记录`NOT_INSTALLED / INSTALLED_UNVERIFIED / STATIC_RECOVERED / EXECUTED_UNVERIFIED / EFFECT_VERIFIED / BLOCKED`等状态，区分技能发现与具体行动授权；
- 在主Core的Skill/Tool路径注册候选，等真实安装/测试/独立审核与Human发布门后再把“可用”置为真。

## 四、正式迁入Core的最小受控变更集合（**计划**，不是已实施）

| 后续包 | 目标Core位置 | 最低实质产物 | 必须给出的负例/证据 |
|---|---|---|---|
| CORE-01 阶段01工作流修订 | `01_os/01_workflow/01_需求建模/`、Boot/Registry/runner相关 | 01a/01b规范差异对照、兼容版本、确认门；旧A不回溯伪失败 | 老版本runner通过，新的Human确认门拒绝错版/未确认A |
| CORE-02 PRMS/G1-G2目录 | `01_os/03_mechanisms/context_management/`及PRMS子机制、`01_os/02_boot/`、`01_os/05_registry/` | G1全局目录、G2域目录contract、Task/role关联检索、加载/回执/覆盖报告 | 数学域不得加载NBA项；漏目录、错误SHA、索引过期不得报READY |
| CORE-03 项目模块索引同步 | 同上加`01_os/06_execution`验证器 | 模块ID、影响范围、索引commit、证据级别/缺口、同PR一致性检查 | 代码变更却未更新Registry→INDEX_SYNC_PENDING；历史master与Draft不能串版本 |
| CORE-04 多模型交接与校验 | `01_os/03_mechanisms/task_orchestration/`、context handoff、相关validator | 单Owner、隔离与共享环境区分、producer/consumer包、最小复算 | 并行共享worktree冲突、错误SHA、已交付未接受不得记完成 |
| CORE-05 领域研究/证据成熟度 | `01_os/01_workflow/02_信息收集与提炼/`及证据包schema | 领域适用性、版本/平台事实、证据阶梯/UNKNOWN与最小研究选择 | 概念迁移不能冒充当前环境API；纯Git任务不强制无效网络研究 |
| CORE-06 REA可选工具 | `01_os/04_skills_and_tools/rea/`、`01_os/06_execution/tools/rea/`、`01_os/05_registry/skills_and_tools_v1.yml` | 适配/安装检查、版本、受控调用wrapper、权限/预算/结果回执、独立使用说明 | 未安装/权限不足时fail-closed；offline fixture不能冒充游戏效果；跨域不能继承NBA RVA |

这些包应在主Core所属的正常OS任务分支开发，不能将NBA2K22全部`08/`或`01_os/07_content`反向merge进Core。新`09_Domain_Global_Mechanisms/`属于Domain-owned，Core修改`CORE_MANIFEST.yml`所有权合同、新域生成脚手架和加载接口即可，NBA具体知识仍在域侧。

## 五、核心审查发现与优先级

**F-01（高）** Core目前未继承NBA先行的阶段01 `v0.4`，Core仍指向`v0.2`。需要做能力与Schema差分，不能因为PRMS需求已Human批准就假定Core七阶段runner知道01b。

**F-02（高）** PR #18 明确为DRAFT，13模块机器索引和同PR同步规则尚未进入NBA `master`。若Codex只读master会漏掉新版项目全貌。阶段02必须把“分支来源版本”作为检索/恢复一等字段。

**F-03（高）** Core已有context管理和tool governance；迁移应扩展而非平行引入第二套；REA是**可选外部工具**，不是每个OS自动安装的常驻机制。

**F-04（高）** REA现有部分真实游戏调用报告无法证明通用跨域可用、任意函数安全、Game Save/Reload稳定性。不得将NBA项目特定Native ID/ABI签名提升成Core全局默认。

**F-05（中）** 原NBA索引合同承认暂时没有机器强制。阶段02先用当前13模块真实注册表制作Validator的失败样本与预期输出，03再决定机器实现。

**F-06（中）** 多模型V2的物理共享仓库/角色分工是条件规则。Core应以具体workspace和任务权限进行选择；不能把“Codex永远唯一Owner”等领域政策设为全域不可改的OS规则。

**F-07（中）** NBA研究先行的内容知识输入和Core第二阶段“找可行性证据”不是互相替代。前者是领域语义理解，后者是对A可实现性判断；抽取共同验证语义而不复制所有NBA社区来源。

**F-08（中）** PRMS本身的Human批准记录与RC02已持久保存，但`run.yml`仍指向旧RC01 `confirmed:false`。这是一个已核实的**状态指针更新失败**，与产品需求是否批准分开。不能在另一仓库做迁移时绕过此前写入安全拦截来伪造正式阶段门。应在合法任务状态管理通道修正并远端读回。

## 六、可监督的下一次实交付与验收

1. **Core工作流差异包**：逐行对比Core v0.2和NBA v0.4的Schema/Boot/Registry/runner依赖，列出准确变更文件和受影响测试（不是只做摘要）。
2. **领域索引校验样本**：用现有13模块的JSON建立源SHA/路径可解析、主索引状态一致、变化模块必须同步、旧分支混用拒绝的四类负例。
3. **REA Core集成可行性包**：版本与工具schema、不同权限/环境的实际能力矩阵；只做合法的离线/受控测试，不附加真实游戏。提供未安装和失败回执。
4. **Core提升PR候选**：经过阶段02证据和阶段03设计B之后，才在Core任务分支写正式差异；Human按受保护发布动作决定是否合入Core `master`，随后按各Domain策略传播。本文不授权任何发布。

**本轮确实完成**：在GitHub真实源上找到并读取关键文档；固定PR18/Core的版本；解析13模块JSON；核对Core现有机制与未覆盖范围；提出可移植清单、反例、后续Core目标路径。  
**本轮没有完成**：运行REA、验证当前开发机器配置、执行单元测试、修改Core、创建09、修复PRMS run.yml、完成阶段02正式证据包或阶段03方案B。
