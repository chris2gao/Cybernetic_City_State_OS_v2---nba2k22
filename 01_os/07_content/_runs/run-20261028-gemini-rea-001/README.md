# Gemini × REA · 并行候选研究分支：总览与任务顺序

状态：`EXPERIMENTAL_BRANCH_ISOLATED_NOT_FOR_MASTER` · 2026-10-28。仅是有边界的工程探索实验，不覆盖Codex正式工程结果。此文档建立在正式 PR #19 `task/role-native-execution-system-20261028@39086984adfa554d36315382d41bc2e5d2e54c39` 上，工作分支 `gemini_rea`。

## 任务职责和为什么独立

- **Human**：选择功能顺序，批准真实游戏测试或最终合并，裁决业务边界。
- **GPT规划模型**：分配一次只处理一个具体业务能力的任务，保留全部缺口。
- **Gemini（Flash）**：按任务局部静态PE/现有代码证据探索、实现**隔离候选**、编写可复现的离线测试和准确缺口报告。不能凭函数名/字段偏移把UNKNOWN升级为生产接口，不自行发布已通过认证的结论。
- **Codex**：唯一正式工程 Owner，执行独立核对、修复、集成、离线重演、必要的获批实机测试，决定是否把特定候选引入PR #19。
- **用户产品目标**：第一版仅 GM 管球队建设/合同/人员，Coach 管战术/轮换/球员倾向/训练；人格冲突和Player人格暂缓。保持原版比赛引擎运行和自然成长。当前 PR #19 研发功能多于第一版所需，**不要删除或更改原功能**。

由于原有领域协作规范限定共享机器/目录中的 Codex 与 Gemini 应**顺序使用同一套运行环境**，本分支隔离不表示可同时使用相同本地工作树、相同管理员游戏进程、同一REA静态工作目录。若Codex仍在活跃修改同一检出目录，Gemini必须使用独立clone/worktree并确认不会更改/覆盖Codex未提交文件；不具备独立工作空间时，先只做GitHub分支上的资料整理，等本地资源空闲。不得擅自重置、清理或切换Codex正在写入的工作树。

## 先读（单次最小上下文）

1. 仓库根 `AGENTS.md`、`AGENT_WORKING_DISCIPLINE.md`、`01_os/README.md`；领域 `08_Domain_Applications/Antigravity_GM_Engine/AGENTS.md`；按OS七阶段/授权要求执行，不以实验分支绕过。
2. `08_Domain_Applications/Antigravity_GM_Engine/PROJECT_INDEX.md`、`docs/development/PROJECT_MODULE_REGISTRY_V2.json`、`docs/development/PROJECT_INDEX_SYNC_CONTRACT_V1.md`；只按领域加载P04(机制资料)、P06(教练)、P09(REA)、P10(批次)和本任务需要的项目模块；其他不重扫。
3. **必读完整REA经验** `research/rea_native_control/REA_WINDOW_CONTEXT_HANDOFF_20261028.md`；配合 `README.md`、`DISCOVERY_NOTES.md`、`CONTROL_CALLBACK_DISCOVERY.md`、`ROLE_EXECUTION_PROGRESS.md`、`ROLE_MODEL_MECHANISM_GUIDE.md`、`VALIDATION_RESULTS.md`；认真理解REA历史上哪些实机成功、哪些只有静态、为何全游戏Ghidra超时、如何做局部PE/Capstone和Frida线程/ABI/对象身份/独立读回。
4. **必读功能知识** `docs/game_mechanics/README.md`、`PROGRESS.md`、`SOURCES.md`及当前任务相关的 `guides/K04_COACH_AND_PLAYS.md`；这是业务操作需求和枚举语义参考，不等于每项Native可调用。
5. **工程真实进度** `01_os/07_content/_runs/run-20261028-role-native-execution-system-001/PROGRESS_POINTER.json`、`coverage_current.json`、当前`data/action_registry.json`、`data/native_bindings.json`、`facade.py`、`runtime_codegen.py`、相关`runtime/`处理器；项目PR19的`72动作、65绑定、61对应/184需求`是该提交快照，不要用目录计数代替游戏验收。

**源基线不可混淆**：PR18规划HEAD `094f1aa641f93dec2277707ad9dbf5bdb0341247`；当前实验直接继承PR19 HEAD `39086984adfa554d36315382d41bc2e5d2e54c39`。这些是固定来源SHA；以后PR19继续前进应记录新的源SHA和相对差异，不能盲目将两个分支整体互相合并。

## 后续任务清单：一个一个执行，未授权的下一任务不得抢跑

| ID | 单独目标 | 依赖/焦点 | 结束条件 | 当前状态 |
|---|---|---|---|---|
| **GREA-01** | **针对特定对手的Gameplan真实写入/提交链** | 从已有ensure对象和Coach默认Apply出发，寻找对手专属字段/原生提交链及上下文，先静态恢复 | 调用链证据＋可复现候选，或有边界的精确阻碍报告 | **FIRST ACTIVE TASK** |
| GREA-02 | 18项个人防守原生Setter | 基于GREA-01是否确证Gameplan对象生命周期；每字段枚举/对象/Setter | 分批完成经证据支持的个人防守接口 | 未授权 |
| GREA-03 | 本队Playbook 68槽增删改换 | 共享战术池CRC、本队Book、原生提交/刷新 | 精确槽位与事务，不改共享战术定义 | 未授权 |
| GREA-04 | 4 Freelance槽、球队体系及其他全局Coach设置 | 已有十字段之外，不把byte域当UI合法值 | 独立有证据的Setter及值域 | 未授权 |
| GREA-05 | 完整首发/轮换/位置/分钟配置 | 继承当前精确分钟Setter；定位非Career角色操作 | 与原分钟动作独立的完整轮换业务 | 未授权 |
| GREA-06 | 个人训练、导师、康复、团队训练剩余项 | 区分已恢复日期patch和未完成个人业务 | 真实函数合同、精确字段语义 | 未授权 |
| GREA-07 | GM完成签约、续约、合同选项 | 基于已恢复报价/撤回，**不将Offer返回当签约** | 原版最终加盟及合同归属链候选 | 未授权 |
| GREA-08 | GM名单、员工雇佣与解雇 | 完整岗位/合同/名单业务 | 原生业务接口候选 | 未授权 |
| GREA-09 | 选秀、选秀权交易及球探完成链剩余缺口 | 不重复先前球探Goal实测 | 新的精确 Native 业务调用候选 | 未授权 |

上表只是规划顺序，GREA-01完成及Codex检查后再单独发布下一任务。GREA-02和GREA-03可以根据GREA-01证据交换先后，不能默认并行或宣称全域完成。

## 对 Gemini 所有任务的硬约束

- 首选现有REA工具/有界局部PE字节分析和当前工程恢复脚本，**不重新安装工具，不默认整游戏Ghidra、无限xref、反复超时**。REA插件/本地PE不可用时立即记录条件和原始错误，转已存在静态证据；禁止虚构工具响应或Native签名。
- **本系列默认只授权源码、静态证据及离线合成测试**。不得附加或操纵用户当前游戏，不调用会改变存档的Native函数，不操作UI、日期、比赛、Save/Reload，不修改防护/签名程序。若需实机操作，提交独立最小测试场景等Human批准。
- 不允许直接写入游戏业务对象字段冒充原生业务执行。可构造私有Native参数（前提真实签名已证）。禁止拿无关的MyTEAM/Career函数当MyLEAGUE Setter。
- 不替GM决定交易、不配薪、不替教练选战术、不发明原生enum语义或100%成功宣称。
- **候选代码仅放实验专用目录** `research/rea_native_control/experimental/gemini_rea/`（含离线脚本、测试、证据索引）；不得修改现有正式`facade.py`、`role_batches.py`、`data/action_registry.json`、`native_bindings.json`、`runtime/`、`PROJECT_INDEX.md`、`PROJECT_MODULE_REGISTRY_V2.json`以伪造完成。未来被Codex接受时由其负责正式集成及索引同步。
- 既有原生成功案例不能在新的游戏环境里盲目重复。无独立读回时效果`UNKNOWN`；静态恢复与离线测试只可声明`STATIC_CANDIDATE`、`OFFLINE_TESTED`，不可声明`LIVE_VERIFIED`。
- 每个任务以新单独提交和`GREA_HANDOFF`报告结束。没有实证时提交准确缺口；失败也可能是有价值的排除证据。保留不确定项，不做大量猜测。
- 如遇Codex PR19更新，不自行改基线/强制rebase/merge；固定源HEAD、报告差异，后续由Human/Codex决定选择性移植。实验失败则保持隔离；是否删分支由Human之后裁定。

## Codex后续接收（目前不执行）

Codex以`GREA_HANDOFF_TEMPLATE.md`标准逐项审查：固定候选SHA、来源/构建、原始指令字节或记录、目标函数真实ABI与上下文、负面搜索、离线fixture和重放命令、是否曾附加游戏、所有UNKNOWN。先独立复核，再修复，获独立Human实机授权后验证结果。**只通过验证的具体提交/文件进入正式工程，不直接合并完整实验分支，也不把实验目录直接发布为生产模块**。

## 当前任务

只执行 `GREA_01_OPPONENT_GAMEPLAN.md`。Human下一步批准第二任务前停止；这不是放弃后续领域，只是减少上下文与风险。

## 2026-10-29 Human 新批准的继续工作（覆盖旧“下一任务未授权”状态）

Human已批准**Gemini先在独立分支多做有界研究，由Codex最后集中复核/整理**。本Run中GREA-01原候选必须先自审修正，随后可依次进行GREA-02个人防守、GREA-03 Playbook，两者仍只研究静态证据，不自称游戏实机成功；每包至多4轮内部反证循环。**最新生效的任务文件**：`GREA_CONTINUOUS_RESEARCH_WAVE_02.md`。本Wave授权高于本文件旧的“GREA-02未授权”字样，仅限W02 A/B/C；GREA-04至09及游戏状态修改仍未授权。完成三个包后Gemini停止，统一交Codex审核；Codex PR19不从此实验分支整体合并。
