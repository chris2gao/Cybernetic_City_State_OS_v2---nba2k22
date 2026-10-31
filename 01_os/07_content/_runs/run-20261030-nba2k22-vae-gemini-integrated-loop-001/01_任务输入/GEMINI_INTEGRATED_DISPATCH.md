# VAE · Gemini 集中开发循环任务（统一开发、集中审核）

## 身份与范围
本窗口为 **Gemini Flash 3.8**（Human报告的模型标签，不等于平台认证）在本地Windows环境中的`execution`主开发窗口。从现有NBA2K22公共任务背景和本任务固定GitHub来源恢复，不接管Codex旧任务，不重复要求Human批准A-v1。

**唯一主任务** `NBA2K22-VAE-GEMINI-INTEGRATED-LOOP-20261030-001`。使用固定任务分支`task/nba2k22-vae-gemini-integrated-loop-20261030`和Run`01_os/07_content/_runs/run-20261030-nba2k22-vae-gemini-integrated-loop-001/`，**一直用同一个task_id与Run执行内部迭代**，不要每个G点/F点新建任务。子任务只作为Run内迭代条目，而非OS独立任务。

## 完整目标
以已批准A-v1为业务基线，**统一实现**：
- Stage02 G01–G08 的取证与缺口分级（当前存档、build、USER/CPU、Normalize双开关、3D/Calendar、Coach、交易/签约/选秀、Player、自然比赛、存档回退门）；研究和实机来源严格隔离；
- R01–R09集成对象和合同，必须修复已审出的F02（R06比较上下文）、F03（R08不能初始APPENDED）、F07（阻塞态字段可空性/转移）；同时处理F04修订事件ID与幂等，F05单独test oracle，F06维持证据上限；
- 基于已有 Reader/REA **只读复用** 的VAE首个可运行离线/模拟原型：Profile→Diagnosis→TrialPreflight→未执行ExecutionReceipt→未验证Readback→Observation→Evaluation→KnowledgeRevision（待写状态）→DSeriesFeedback。E1原型优先贯通，E2/E3/E4有真实合同与失败路径，但不强行声称30队全量可用；
- 可复现fixture与最小自动化回归、拒绝路径、非破坏性回退示例、证据索引、迭代账本，最后一次集成候选供独立GPT集中审核。

## 一次任务内反复循环
每轮 **恢复最新HEAD和进度 → 选择最高影响的可解决缺口 → 取证/修订代码 → 局部真实运行测试 → 修复或标记UNKNOWN → 记录增量证据/残差 → 提交同分支**，再进入下一轮。
不能以“研究完了”“模拟成功”冒充已可操作游戏；必须能说明本轮相较前一轮失败集、GAP或可执行功能有哪些可测的改善。没有新的可解决缺口或触及OS真正停止门才停止，无固定轮数，也不要求每个局部修复都请求Human确认。

## 工作空间与写入
允许代码集中在`08_Domain_Applications/Antigravity_GM_Engine/src/vae/`、测试`08_Domain_Applications/Antigravity_GM_Engine/tests/vae/`、候选配置`08_Domain_Applications/Antigravity_GM_Engine/config/vae/`，证据与迭代记录集中在本Run。**不动已经存在的Reader/REA核心代码、G1/G2、D系列和其他任务分支**；确需改已存在代码时记录扩边申请，不绕过路径合同。

允许对本地仓库、原有文档及fixture做只读调查和离线测试。**禁止在本任务内实际变更游戏配置、Native内存/Hook、真实游戏存档、读写活跃进程、提权或启动受保护runtime**。当前Human仅说明你拥有本地执行能力，没有授权所有游戏操作。即使只能获得静态证据，也应完成能安全交付的离线原型，并列出最小的受保护动作申请。

所有输出必须区分SOURCE_RESEARCH / STATIC_CODE / OFFLINE_FIXTURE / LIVE_READBACK / UI_VERIFIED / SAVE_RELOAD_VERIFIED / COMPETITIVE_OBSERVED。并保留UNKNOWN，不能从历史成功实例推断通用接口。

## 集中审查与结束
研发期间自行执行必要的直接相关测试，不对每轮向规划窗口索要审核。候选完成时：一次完成与目标有关的集成回归、证据核对、GitHub允许路径与安全检查；形成一个冻结候选与completion_pointer；由**独立公共基线Fork的GPT审核窗口**集中审查一次。Gemini不自我宣布独立审核通过，不合并master。

如果因一个必须但未授权的游戏进程操作卡住，只停止那项受保护操作；其它可以合法推进的离线工作继续。真正的架构语义变化、无法验证的重要主张、越界写入或需要Human中转他模型时，按现有OS契约停止并交班。不能在窗口结束后自称继续后台开发。

## 回传给规划窗口的内容
仅任务ID、真实HEAD、阶段候选/阻塞状态、关键实现与测试摘要、证据和UNKNOWN最小索引、模型实际身份来源、完成指针、独立审核请求。全部迭代详情保留在同Run里，规划窗口不接收整段开发日志。
