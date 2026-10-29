# Codex 统一开发任务 · Core Workflow / 开发规范 / REA 五阶段交付（启动提示词）

## 任务身份、范围与源

你是 Cybernetic City-State OS 的**唯一工程实现 Owner：execution**。本次只执行一个完整工程任务：

\`OS-CORE-WORKFLOW-REA-PROMOTION-20261029-001\`

**同时**实现以下能力：主Core的 Stage01（01a A0→01b完整A）机制直接替换；NBA2K22实践形成的通用研发规范；REA作为Core按需外部工具的适配；NBA2K22领域的REA Profile关联；统一测试和可审核交付。

Human明确批准“可以混入，一起完成。分阶段执行呗”，并确认**不兼容旧任务、不做过度设计**。这是本任务范围和简化方向的约束，不要擅自将REA拆为另一待启动产品任务；也不要把五个阶段当成五次Human微审批。按 S1→S5 连续工作，每段提交可审计代码/测试证据，最后一次整体验收。

源码仓库：
- Core权威仓 \`https://github.com/chris2gao/Cybernetic_City_State_OS_v2---core\`
- NBA领域仓 \`https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22\`
- 规划分支 \`planning/os-core-workflow-rea-upgrade-20261029\`
- 本Run相对根 \`01_os/07_content/_runs/run-20261029-os-core-workflow-rea-promotion-001/\`

**首先必读**：本Run \`03_统一实施/01_Workflow开发规范_REA统一五阶段工程计划_v1.md\`；这是唯一最新实施范围。随后读取 \`00_任务章程_升级范围与串行路线_v0.1.md\`、\`01_W1信息收集/01_Core_v0.2_NBA_v0.4_差异与兼容首轮核对.md\`、\`02_W1设计/01_阶段01双层需求建模_直接替换方案_v1.md\` 作为早期来源与W1已确认细节；**早期“旧Run兼容”“REA另起任务”条款已被Human新裁决覆盖**。

必须从当前远端Core/master与NBA/master准确读取SHA、AGENTS、OS Boot/Registry/权属与任务规则后动手。2026-10-29的检查快照：Core/master \`e075cdf288a765b7bfd2f4891c8f384404da16e1\`；NBA/master \`4a7d3de013fdddee66b64c0a8a31b6d346982540\`。Source SHA仅作锚点，不能替代fresh read。

NBA域的 \`PR #18\` 仍是 OPEN/DRAFT，固定HEAD \`094f1aa641f93dec2277707ad9dbf5bdb0341247\`。必须从该精确来源阅读：
- \`08_Domain_Applications/Antigravity_GM_Engine/PROJECT_INDEX.md\`
- \`docs/development/PROJECT_MODULE_REGISTRY_V2.json\` 和 \`PROJECT_INDEX_SYNC_CONTRACT_V1.md\`
- \`docs/game_mechanics/README.md\`（仅按相关主题）
- \`research/rea_native_control/REA_WINDOW_CONTEXT_HANDOFF_20261028.md\`
- \`ROLE_MODEL_MECHANISM_GUIDE.md\`、\`VALIDATION_RESULTS.md\` 与相关行动目录（按范围）

同时从 Core 当前版本读取：
- \`01_os/01_workflow/01_需求建模/\` 的活动规范、Schema
- \`01_os/01_workflow/02_信息收集与提炼/\` 的现行规范
- \`01_os/02_boot/workflow_minimum_operational_loop/启动清单_v1.yml\`
- \`01_os/05_registry/workflow_minimum_operational_loop_v1.yml\`
- \`01_os/06_execution/workflow/minimum_operational_loop/run_minimum_operational_loop.py\`
- \`01_os/03_mechanisms/stage_collaborative_deliberation/\`、\`task_orchestration/\`、\`context_management/prms/\`
- \`01_os/04_skills_and_tools/README.md\`、\`01_os/05_registry/skills_and_tools_v1.yml\` 及现有按需工具适配样本

## S1：直接替换Stage01

把Core现行单层A规范更新为**01a共识A0与其Human确认→01b最终需求结果A与其独立Human确认**。完整A具体列出最终交付品的组成、行为、关系、合法输出、完整性验收和证据缺口（非数据库项目无需SQL）。02继续核实事实，03继续设计实现B。

最小改变活动方法论、README、Schema、Runner、Boot、Registry及相关fixtures/tests；保持七个Workflow stage_id、现有Git阶段链和其他六阶段职责。不存在旧模式运行入口：不做旧任务兼容层、迁移器、双profile、历史Run追溯测试。旧Git历史保留不改写。

负例必须拒绝：仅A0确认、把A0充当A、错误版本的Human确认、空/不映射的结果项、旧单层A冒充新完成。不要声称机器可以判断全部需求语义充分性；Human/模型负责语义确认，程序落实结构和版本约束。

## S2：通用开发规范最小实现

复用现有Core mechanism/PRMS，不做第二套OS。提炼并实现：
1. Project Index + Module Registry：任务定位项目全貌、\`affected_module_ids\`、\`source_refs_read\`、Draft/master实际差异，变更与同PR索引同步，缺漏 \`INDEX_SYNC_PENDING\`；NBA13模块数据仍在域内。
2. 多模型/开发协作：一个共享工作区单写Owner、明确交接source SHA，独立审查不得以开发者自评替代验证；对不同任务可选择不同实际模型，不强制Codex供应商绑定。
3. 失败与交付：有限重试、不同故障分类、未知外部副作用不盲重放、读回证据、实际结案差异/下一步；不用游戏级门禁复杂化普通文档任务。
4. 阶段02证据分类：领域背景 vs 可行性证据、未知/静态/离线/真实效果等成熟度；不把未经实证的资料或研究数量当作已实现功能。

只提交能发现、复用、真正检查的最小文档+schema/validator变化；若功能已在Core存在，直接引用已有权威，不复制实现。

## S3：Core按需REA工具接入

在 \`01_os/04_skills_and_tools/rea/\` 和 \`01_os/06_execution/tools/rea/\` 实现 **可运行的可选工具适配**，并更新skills_and_tools Registry。具备：
- 检测本机REA CLI/版本/工具schema与可用后端；没有安装时可准确输出 NOT_INSTALLED；
- 有限成本、安全范围与输入/退出码契约；结构化Evidence/Result/错误回执；
- Windows/PowerShell历史场景优先，环境不支持时正常退化，不强制全OS安装；
- 按需发现和调用，不默认加载、安装、提权、启动、attach或写进程；
- 区分历史Windows某机REA6.8.0/229工具与当前实际装载；只读/无害执行成功不等于游戏内副作用已验证。

不要尝试整游戏Ghidra自动导入，历史证据明确该路线多次超时。优先支持本地局部PE/metadata分析、有限观察及可证明的失败处理。能运行就提供真实CLI执行回执；无法安装/不可达时用离线契约测试并准确标注，不要把Mock当成真实REA的成功。

## S4：NBA2K22领域REA Profile

NBA游戏专有内容必须保留在域：存档/EXE身份、RVA/ABI、游戏对象、交易/教练/球探等确定性动作和实机成熟度，不能写进Core通用工具适配。

在独立NBA工作分支或配套PR中，依据 PR18 精确来源接入Core通用REA adapter的Domain Profile、文档索引和测试fixture。保护NBA现有业务内容与PR18尚未合并的独有开发资料，避免直接向旧master导入整个PR18。Core在没有NBA资料时也能运行。

本阶段不用启动游戏、调用交易/训练/选秀/写入原生内存，不再消费历史实机测试批单；只完成接口、配置、读回模拟与证据级别正确表达。

## S5：统一集成、测试与交付

Core S1/S2/S3 在**一个Core任务分支、一个目标Core PR**按阶段提交；S4 在NBA自身的合规分支/配套PR，两个PR相互关联但保持所有权。每阶段都有可复验测试与commit，最后联合验证：
- Stage01双确认门正反例、七阶段结构、其他阶段主链；
- Core PRMS任务恢复、G1/G2/Registry无回归；
- 项目索引发现及错误来源/Draft/未同步负例；
- REA缺装/版本漂移/成功无害调用/timeout/错误回执；
- Core通用层不依赖NBA代码，NBA Profile不假称未证实Native动作已成功；
- 可复制的“如何使用REA工具”和“如何从项目入口找到相关研发规范”操作说明。

最终向Human提供：五阶段完成/受阻表、代码路径、Core PR/NBA PR与HEAD、实际测试命令/输出、未运行项、已改善的可见行为、独立审核复验命令、提交分支和索引同步状态。

**不要只完成S1就把整个主任务标DONE；也不要因为暂缺游戏或安装环境就停止整个工程。** 对已编程功能可离线验证，真实工具/系统条件不具备就诚实列出阻断，完成其余合法任务并交付。尽量避免中间多轮Human确认，除非涉及新产品取舍、真实受保护发布或需要实际执行游戏副作用操作。

**明确禁止**：直接合并Core/master或NBA/master、触碰其它OS领域、创建与本任务无关的新权限/持续服务、开发NBA GM/Coach/Player人格系统、把旧单层Stage01留为活动profile、把NBA游戏RVA放进Core。

## 最终指令

请先输出简短的“精确来源读取与五阶段工作范围回执”，随后作为唯一工程Owner连续完成S1、S2、S3、S4、S5。所有提交和测试必须能从GitHub远端回读。最后向Human交付两个仓库的实际PR/commit与独立审核包。
