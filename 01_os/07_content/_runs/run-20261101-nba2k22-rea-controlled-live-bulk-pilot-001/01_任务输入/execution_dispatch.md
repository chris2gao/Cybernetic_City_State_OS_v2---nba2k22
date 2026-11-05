# NBA2K22 REA · Human 授权的真实批量执行试点

任务 ID：NBA2K22-REA-CONTROLLED-LIVE-BULK-PILOT-20261101-001
OS 岗位：execution；技术规划：GPT-6 / decision_architecture；实际执行模型由 Gemini 如实登记。
分支：task/nba2k22-rea-controlled-live-bulk-pilot-20261101
固定上游安全候选 SHA：568f795f75a0099d6560c1fa448a5ef37f9e7b8e

## 1. Human 授权事实与边界

Human 在本次对话明确裁决：**“批准，许可授权，直接做批量的测试吧。”** 随后再次确认：“execute-authorized，我不是已经批准了嘛，难道我也没有权限批准？”
这构成当前任务的 Human 授权来源，足以批准本任务的受控实机批量测试。无需 Human 再签一次、无需第二名签署者、不把候选 Two-Man Rule 当作既成制度。Gemini 不得以缺少新的授权信或额外授权码为由停止。**不得伪称聊天授权等价于密码学签名**。
授权范围：当前 NBA2K22 实机上针对一个已验证的、可恢复的测试存档，执行 Player SHOT_TENDENCY 的真实多项、多分块测试；允许必要的只读识别、内存 Getter、备份确认、Native Getter/Setter 和写后读回；授权不涉及 Coach、交易、签约、球员能力、游戏推进、生产级10k真实写入或 master 合并。
在此明确范围内，Gemini 可自主设计有限递增试验，无需每个批次重新询问 Human；但不能越出范围或自动重试 UNKNOWN。

## 2. 对 execute-authorized 的函数级实现指导（重点）

原 bulk_executor.py 的 cli_execute_authorized 即便 --allow-live-mutation 也无条件退出 LIVE_AUTHORIZATION_VERIFIER_NOT_AVAILABLE。这是**缺少实现的代码门**，不是 Human 无权授权。
读取并复用：bulk_executor.py::{cli_execute_authorized,BulkExecutorService.run_with_transport,BulkFridaScriptCompiler.compile_chunk,ReaChunkTransportAdapter.execute_chunk,ExecutionJournal}；transport.py::{LiveExecutionContext,ReaCliTransport.execute}；run_native_program.ps1；runtime/{common.js,gui_once.js,player_stats.js}；已有 data/native_bindings.json 和 Action Registry。
选择最小实现：保留旧入口的默认安全模式，但新增本任务范围内的明确 live pilot manifest/启动参数；启动器将本次 Human 许可记录绑定到实际 plan_digest、chunk_digests、game SHA256、PID+进程启动时点、存档实例/名单生命周期、精确 action/字段/对象/旧值/新值、调用预算、一次性 attempt_id，并在每次执行前验证匹配。不能把仅仅 --allow-live-mutation=true 或任意 authorization_ref 文本当成无限权限；也不得要求 Human 另发第二次批准。
通过条件时，真实 Bridge 调用既有 ReaCliTransport，使用受控 request_id、chunk_id、精确脚本 SHA 和现有 Runner；禁止额外提权、无界批量、自动安装或 Hook 重复。必须修复 JS send 回执中缺 batch_id/save_instance_id 等身份字段的问题，并在 Python 端强制校验；请求上下文、Runner 证据及异常状态保留完整。
执行期间始终持有跨进程互斥锁，避免并发运行；Claim 在潜在 Setter 之前持久写入；未知结果不重试、不接受自行填报 independent_source=true 或 applied=true 解除锁；出现异常时保存 UNKNOWN 和没有执行的后缀，不自动补偿反写。
若 GitHub 上的技术证据与现场状态矛盾，停止执行并报告**具体阻断事实**，而不是将 Human 授权误报为不存在。

## 3. 实际批量试验流程

先完成代码修复和离线回归（原 78 项 + 新增 Live Bridge/互斥/协议/故障注入），并将待执行版本固定为 Git SHA；对关键 Native 执行路径开展一次有针对性的代码审查，**不新增 Human 授权流程**。
现场确认游戏 EXE SHA256=1727ad72085fba39e789ee574fc15aab623ad1651cf6879e95e8cd53b6ffbbf5、PID+启动时点、当前测试存档/世界线、可恢复冷备份、当前 active roster 与编辑态。若无法确认存档身份/备份，禁止写入并报告真实 blocker；这不是要求用户重批。
读取 10–30 条候选 Player SHOT_TENDENCY 的实时 Getter；优先跨2支球队、至少2个分块，不能复用旧 Lillard 95→80 的历史值与身份猜测。测试前先执行同样多项、至少2分块的真实 Getter/No-op；它应产生零 Setter 调用并保存完整 REA evidence。
然后执行**有界的真实多字段批量**：首个写入批次建议 10–20 条已确认对象的 SHOT_TENDENCY（经现场值域、备份和调用预算自动收紧），每名球员只更改一个字段，每项变化幅度最多1；至少2个 chunk，按确定性顺序执行。无需人为制造错误或为小批量另求 Human 批准。如某值已到边界，选择其他已读取且有效的对象，不自行切换存档。
仅在首批完整读回且无未知结果后，可以在本次授权范围内进行**另一个小规模增量批次**用于重复性能观察，但必须是新计划、新 exact CAS、新 claim，绝不重放已经 UNKNOWN 的意图；不自动扩展到1000或10000真实 Setter。
每笔记录：actual player/team/field、getter-before、requested、getter-after、原始156B未请求字段差异证据、cache flag、plan/chunk digest、游戏构建和进程 epoch、Runner证据ID与时长。失败、越界写、cleanup异常、CAS mismatch或 UNKNOWN 立即全批停止，禁止自动重试/反写。Human 自己负责决定是否恢复冷备份。
游戏 UI 核对和自动 Getter 读回分开登记；不强制赛季推进、游戏保存、全量 WorldData 采集，不将 Mock 效能外推为实机性能。

## 4. 内部开发 Loop、验收和停止

Gemini 按有界增量：分析已固定源码 → 实现 → 正反测试 → 定位失败 → 改进 → 记录 checkpoint → 继续。记录每轮实际模型、修改、测试命令与退出码、失败集合变化、准确SHA；不因无新证据的重复测试计 Loop。
所有真实运行步骤必须区分 OFFLINE_MOCK / NODE_VM / LIVE_NOOP / LIVE_SETTER。最终报告每个意图唯一回执、守恒 planned=applied+noop+blocked+unknown+not_executed+reused，统计真实 Setter 调用与实际 session 时间；报告性能范围和限制。
如果离线运行时安全门未闭合、备份不可靠、身份不清、GameBuild不匹配、Runner异常、未知写入结果或者超过本次任务范围，直接停止并保存证据。**正常完成任务范围不再需要 Human 第二次许可**；若提出扩大为跨域/上万次实机写入，才另行请求新的明确裁决。
禁止操作 master、修改原上游 Run 历史、在未获授权范围外操作其他 Native 功能。

## 5. 允许修改和交付

允许修改：research/rea_native_control/bulk_executor.py、transport.py、run_native_program.ps1（仅必要）、新增 live_bulk_pilot.py 和相关 tests、新 Run 证据文件；原 native bindings、role_batches、registry 和已恢复业务 Runtime 默认只读，若确需突破范围，应报告边界。
交付：代码+固定最终 SHA；真实批量参数及不可泄露的安全脱敏存档标识；代码测试和故障注入收据；存档备份验证凭据（不上传存档）；Runner evidence / Getter、Setter、UI读回；Loop JSONL与可复算摘要；完成门说明。若未能执行真实写入，必须报告 BLOCKED_BEFORE_LIVE_MUTATION 和原因，不能宣称 LIVE_BULK_PASSED。
**本任务授权来自 Human，技术测试通过是执行前提但不是新的批准人。**
