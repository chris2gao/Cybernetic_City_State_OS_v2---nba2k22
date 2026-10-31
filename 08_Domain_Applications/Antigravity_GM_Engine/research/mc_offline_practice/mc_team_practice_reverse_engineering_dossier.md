# NBA 2K22 MyCAREER 球队训练馆 (Team Practice Facility) 离线逆向与解封研究报告 (V3 - Audited)

> **执行窗口**：工程实现窗口 (`ENGINEERING_IMPLEMENTATION`)  
> **研究对象**：`NBA2K22.exe` (PE SHA256: `1727ad72085fba39e789ee574fc15aab623ad1651cf6879e95e8cd53b6ffbbf5`, Base: `0x140000000`)  
> **分析工具**：REA MCP + Frida 实时进程挂载 + Capstone 静态反汇编分析  
> **当前阶段**：运行器身份强校验落地、内核命名互斥体实现、网络 Job 精准谓词限定与分层事实日志。

---

## 一、 核心逆向与架构确证 (Executive Summary)

1. **“进训练废档”的根本技术诱因**：
   - **诱因 1（致命硬编码断言）**：在 [`activity2_teampracticefacility.vcc`](file:///e:/vcsports/basketball/code/gamemodes/tkworld/activities2/arenas/activity2_teampracticefacility.vcc) 中，进入训练馆调用 `CreatePlayers` (`0x14163f4a0`) 时，引擎通过 `[this + 0x488]` 读取训练日程类型。在在线状态下，该类型由 2K 服务器每日下发；在单机离线状态下，该值未被在线下发且为 `0` (`UNKNOWN`)，导致代码直接跳转至错误处理分支，触发致命断言：
     $$\text{assert(false, "Can't start LivePractice, if type is unknown.")} \longrightarrow \texttt{int3 (0x14163f60d)}$$
   - **诱因 2（存档状态死锁与污染）**：在进入训练前，MC 时间线模块 (`careermode_timeline.vcc`) 已在本地存档中写入了“训练事件已启动”的状态标志。当遭遇 `int3` 崩溃或因服务器握手超时强退后，训练完成与退出逻辑 (`HandleLivePracticeEnded` / `HandleArenaExitRequest`) 未能执行，导致存档滞留在“训练中”的不一致状态。重新读档时游戏再次尝试恢复该训练，陷入无限崩溃死循环。

2. **日历进入 96% 卡死机理与异步作业架构**：
   - **底层 `TaskManager`**：工作线程池负责物理与网格流式解包，主线程在 `0x141f9a9a0` 处作为 Task Pump 运行，空闲时通过 `0x14216b440` (`SleepConditionVariableCS`) 挂起，新任务入队通过 `0x14216b530` 触发 `0x14216b3f0` (`WakeAllConditionVariable`) 唤醒。
   - **上层 `CareerProgression JobManager` 与精准身份验证**：
     * 目标作业类型：`CAREERMODE_PROGRESSION::GET_SERVER_DATA_JOB`
     * 实例大小：`0x350` 字节（由 `0x141213132` 在 `ProcessLevelChanges` 中分配）
     * 专属虚表指针：`0x142B505F8`
     * 成员函数偏移：`CreateAndSendRequest` 位于虚表指针偏移 `-0x28`（即虚表槽位 `0x142B505D0`）
   - **原生提前退出分支逻辑与前置条件**：
     ```x86asm
     0x14123923a: cmp dword ptr [rcx + 0x30], 0
     0x14123923e: mov rbx, rcx
     0x141239241: jne 0x141239463                  ; 若状态非 0，直接跳转尾部
     ...
     0x141239463: add rsp, 0x78
     0x141239467: pop rbx
     0x141239468: pop rbp
     0x141239469: ret                              ; 原生提前返回
     ```
     **精准修改谓词**：仅当 `vtable == 0x142B505F8` 且 `[pJob + 0x30] == 0`（初始未开始态）时，才允许将其状态置为 `2`（`COMPLETED`），从而引导执行原生提前退出分支。若虚表不匹配或状态已为 `2` / `3`，则**只记录日志，绝对不改写**，彻底杜绝误伤 MC 其它网络作业。

3. **运行器身份强校验与内核级防重入锁**：
   - **真实 EXE 路径与 SHA256 强制核验**：通过 PowerShell 查询目标 PID 的真实磁盘路径，并用 `crypto.createHash('sha256')` 核验哈希（`1727ad72085fba39...`）。路径缺失或哈希不符立即硬退出；
   - **Win32 命名互斥体防重入**：通过 `kernel32.dll!CreateMutexA` 申请 `Local\NBA2K22_OFFLINE_PRACTICE_PATCH_MUTEX`。若返回错误码 `183` (`ERROR_ALREADY_EXISTS`)，说明已有补丁驻留，立即中止，实现真正的进程级互斥。

---

## 二、 补丁协同 Guard 矩阵 (The 5 Guards)

| Guard 编号 | 目标函数 RVA | 目标函数符号 | 触发条件与动作 | 状态 |
| :--- | :--- | :--- | :--- | :--- |
| **Guard 0** | `0x1239230` | `GET_SERVER_DATA_JOB::CreateAndSendRequest` | **精准判定**：虚表必须为 `0x2B505F8` 且 `s30==0` 时置 `2`；其余情况只读记录 | **已落地** |
| **Guard 1** | `0x163f4a0` | `TK_WORLD::...::CreatePlayers` | 校验 `[this+0x488]`，若为 `0` 补正为 `1`（标准团队训练），规避 `int3` 崩溃 | **已落地** |
| **Guard 2** | `0x1731d30` | `ACTIVITY2_TEAMPRACTICEFACILITY::StateDispatch` | 监视 State 0~5 场景流转（资源分配、贴图加载、校验、角色生成、控制权） | **已落地** |
| **Guard 3** | `0x11f8680` | `LiveDrill_HandleCalculateResults` | 强制 `args[2] = 3`（固定三星），置位 `0x146352124 = 1` | **已落地** |
| **Guard 4** | `0x11f8bf0` | `CAREERMODE_LIVEPRACTICES::HandleLivePracticeEnded` | 记录训练结束与退出，确保日历正常推进，安全归档 | **已落地** |

---

## 三、 分层诚实事件日志契约

控制台与运行日志严格按以下事实分层输出，不提前合并为成功结论：
* `[IDENTITY]`：目标进程真实磁盘路径与 SHA256 校验通过；
* `[ATTACH]`：Frida 成功附加至目标 PID；
* `[HOOK_MOUNTED]`：内核命名互斥体创建成功，二进制指令签名验证通过，Hook 挂载完成；
* `[JOB_FUNCTION_HIT]`：`CreateAndSendRequest` 被调用（记录 Job 指针、虚表及调用者 RVA）；
* `[JOB_SKIPPED_UNCONFIRMED]`：虚表不匹配或状态非初始，放弃改写；
* `[JOB_IDENTIFIED]`：虚表与状态均匹配，确认目标 Job 身份；
* `[JOB_STATE_MODIFIED]`：`[pJob+0x30]` 状态被改写为 `2`；
* `[JOB_ORIGINAL_FUNCTION_RETURNED]`：原函数通过原生提前退出分支返回；
* `[PRACTICE_SCENE_LOADING]`：球馆场景状态机发生状态推进（State 0~5）；
* `[CREATE_PLAYERS_HIT]`：`CreatePlayers` 函数被调用；
* `[PRACTICE_TYPE_NORMALIZED]`：训练类型从 0 补正为 1；
* `[PLAYERS_INSTANTIATED]`：`CreatePlayers` 干净返回；
* `[DRILL_REWARD_PROCESSED]`：训练项目结算并赋予三星；
* `[PRACTICE_EXIT_TRIGGERED]` / `[PRACTICE_EXIT_RETURNED]`：退场函数进入与返回；
* `[OBSERVATION_REQUIRED]`：提示 Human 进行游戏内实机观察。

---

## 四、 离线自动化测试套件

测试脚本：[`test_offline_practice_patch.py`](file:///e:/gemini_space/nba2k22/08_Domain_Applications/Antigravity_GM_Engine/tests/mc_offline_practice/test_offline_practice_patch.py)
* 测试覆盖：
  1. `test_create_players_entry_and_assertion`: 验证入口指令及断言字符串偏移；
  2. `test_drill_calculate_results_entry`: 验证 3 星校验指令；
  3. `test_live_practice_ended_entry`: 验证退出场馆栈平衡与入口指令；
  4. `test_tracking_flag_displacement`: 验证全局追踪标志位 `0x146352124` 相对寻址；
  5. `test_network_job_create_and_send_request`: 验证网络请求函数及 `0x504521a8` 会话码；
  6. `test_network_global_status_displacement`: 验证全局状态变量 `0x146351848` 寻址；
  7. `test_job_completion_callback_success_code`: 验证完成回调校验码；
  8. `test_js_patch_file_exists`: 验证注入脚本完整性。
* 执行状态：`8 passed in 0.51s`。

---

## 五、 干净启动游戏与加载 Hook 的准确步骤

若需重新开始一次干净的实机测试：
1. **清理环境**：确保没有其它 Frida 实例或旧 Node 脚本驻留；
2. **启动游戏**：启动 `NBA2K22.exe`，加载已备份隔离的 MyCAREER 存档，进入日历主界面；
3. **加载补丁**：在终端执行：
   ```powershell
   node e:\gemini_space\nba2k22\08_Domain_Applications\Antigravity_GM_Engine\research\mc_offline_practice\run_offline_practice_patch.js
   ```
4. **检查挂载回执**：确认控制台打印 `[IDENTITY] Target executable verified successfully` 与 `[ARMED] Guards active`；
5. **在日历中点击进入**：点击“进入球队训练”，观察控制台分层日志输出。

---

## 六、 明确尚未证明的事项清单 (Unproven Items)

按科学审计准则，以下事项**必须保留为 UNPROVEN**，交由 Human 实机实测判定：
1. **【待实机验证】** 仅将 `[pJob + 0x30]` 设为 `2` 并走提前退出分支，日历层的时间线状态机是否能在完全不收到后续异步通知的情况下，顺利推进球馆场景切换；
2. **【待实机验证】** 本地球馆贴图模型资源（`practicefacility_int.iff`）在当前球队上下文中是否能完整流式加载完成，有无其它未知资源缺失导致的停滞；
3. **【待实机验证】** 角色控制权接管（State 4）在离线状态下，是否会因缺少在线球员外观同步而产生异常。
