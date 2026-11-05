# Human 工程执行授权更新 · BIC 第一批

**授权来源**：Human 2026-11-04 明确指令：“好的，你继续，但codex可以开发了，给我提示词”。

**领域**：NBA2K22 / Basketball Intelligence Core（BIC）  
**角色**：Human=授权；GPT-6=`decision_architecture`、阶段准入统筹与系列审核；Codex=`execution`；Gemini 可做只读研究。  
**授权状态**：`AUTHORIZED_FOR_BOUNDED_OFFLINE_SOURCE_DEVELOPMENT`（有范围的离线代码施工）；**不等于** OS Stage 01–05 正式通过或 Stage 06 机器完成。  
**工程任务**：`NBA2K22-BIC-B1-DEV01-BASELINE-DATA-20261104` 为当前优先；`NBA2K22-BIC-B1-DEV02-BADGE-INTELLIGENCE-20261104` 与 `NBA2K22-BIC-B1-DEV03-MECHANISM-EXPERIMENT-20261104` 可进行同范围必要的离线辅助实现，避免模块写入冲突。

## 1. 本裁决的精确变化

这是一条**晚于原 P0-only 派单和阻断回执的 Human 授权**。在本文件规定的范围内，覆盖此前“仅允许 P0、不得修改源码”的授权限制。保留旧文件和阻断回执作为历史事实，不覆盖、不删改。

现在 Codex **允许立即在自己的独立工程分支编辑业务源码、编写/运行离线测试、小规模只读夹具并循环修正**。它不必在每一次普通离线代码修改时重新请求 Human，也不应因为 Stage 01–05 的独立文书尚未正式通过而重复回复 `blocked`。这些正式阶段产物由规划侧并行闭合，任何正式阶段状态都必须来自真实验收，不由工程执行倒推。

新授权不自动豁免正式 OS Workflow、冻结测试、独立验收或重要 Human 检查点。Codex 的源代码增量以“经授权的有界离线工程开发”进行；正式提交 Stage 06/07 完成或 master 合并必须完成相应 OS 门。

## 2. 可执行内容与现有技术起点

- 继续使用已经完成 P0 的独立工作分支 `task/nba2k22-bic-batch1-p0-20261104` 及现有工作区。检查真实 HEAD、dirty state 和远端，只在自己的分支执行；如该分支有历史只读报告提交，保持其历史而不重新盘点。
- 来源：P0 固定 commit `17bca5c5e34a4bc3b153c38634681962e1600ec7`；Human 批准 A v2 Git blob `e16fdf6c4ef69b0a90b8c4abd3856617030a7ae4`；第一批发布合同；Stage02–05 候选 v2 和静态来源审查。
- DEV-01 主线：复用 `08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype/query.py`、`observation_scope.py` 与现有身份/采集来源设计，实现最小 BIC 只读数据基准接口（或现有等价接口），包含 `player_baseline`、`team_baseline`、`knowledge_status`、`coverage_report`，及 `value/provenance/status/applicability` 数据契约。模块实际路径由唯一责任人选择最小增量，不能复制新的数据库和现有功能。
- 必须按字段保留 source unit、observed_at/effective_at、save/season/mode 身份、当前缺失/陈旧/受限情况；不可把不同采集单元拼成“完整新鲜同一批”；没有真实快照不得捏造玩家能力。
- DEV-02 支持：用现成徽章 Native profile/decoder，只读判读当前持有和等级。PC22 MyLEAGUE 徽章资格、XP 和动画/成功率没有证据时仅 `UNKNOWN`，不能用 MyPLAYER 攻略代替。
- DEV-03 支持：仅离线、明确标记的合成 2×2 因素/交互计算、混杂负例、模式隔离和 3D 行为记录协议；真实 Fast Sim/3D 游戏效果的结论仍为待证。
- 在现有 WorldData、VAE、REA Bulk 和 Calendar 资产上做增量，复用旧功能与回归，不重新制造平行数据库、Native 批量执行器或累计统计系统。

## 3. 连续内部 Loop

`read pinned sources → choose smallest increment → implement → run targeted offline tests → analyze → fix → rerun → checkpoint → next increment`。

允许在同一个工程窗口内连续完成 DEV-01 关键模块及离线回归，不因单项 UNKNOWN、缺少真实存档或仍在并行进行的 Stage01 文件规范化而停止其他安全工作。真实只读数据集暂不可用时，先完成明确标注 synthetic 的 fixture/负例，留下 `REAL_DATA_NOT_VERIFIED` 缺口，继续不依赖该数据的模块。

报告增量需要有真实命令/退出码、精确 commit/文件、变更范围、可复核测试输出、性能和回归、仍未知的问题。重要数值/逻辑/越权风险立刻停止受影响工作并升级；普通问题内部 Loop 处理，系列结束统一审核。

## 4. 不得执行的操作

**本次授权不包括**：
- 连接、附加、注入或控制 NBA2K22 进程；不得运行真实日历推进或 Fast Sim 游戏操作。
- Native/REA 写入、训练操作、交易、签约、存档编辑或影响比赛状态的任何写入。
- 直接改属性、潜力、徽章；跨模式使用对手隐藏数据；夸大已认证原生机制。
- 修改受保护 `master`、合并 PR、擅自扩大业务范围至完整 30 队 BIC GM/教练/球员人格或在线/实时赛中干预。
- 将大型历史 SQLite/备份/压缩包提交到 GitHub。
- 伪造 Stage01–07 完成、Human 签字、冻结测试、真实比赛证据或游戏效果。

## 5. 结束与审核

交付最少：可调用 DEV-01 只读基准、负例与离线回归；可复核的证据来源/数据身份/UNKNOWN 策略；必要的 DEV-02/03 辅助入口或明确未完成项；有界性能测量；工程提交和 PRMS/Git checkpoint。

**工程验收与正式 OS 交付是两道不同的检查。** 工程验证结果和任务范围由 GPT-6 审查，Human 不必重复批注相同开发方向。Stage01–05 尚未取得实际正式验收回执时，代码只能标为 `AUTHORIZED_OFFLINE_IMPLEMENTATION_IN_PROGRESS`，不能自动提名完整 BIC 正式验收通过。

本次来源优先级：Human 最新明确授权（本文件） > 早期同批次 P0-only 工程施工限制；但不能覆盖 OS 真实验收门或未授权游戏操作。
