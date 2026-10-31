# NBA 2K22 MyCAREER 球队训练馆 (Team Practice Facility) 离线逆向与解封研究报告 (V2)

> **执行窗口**：工程实现窗口 (`ENGINEERING_IMPLEMENTATION`)  
> **研究对象**：`NBA2K22.exe` (PE SHA256: `1727ad72085fba39e789ee574fc15aab623ad1651cf6879e95e8cd53b6ffbbf5`, Base: `0x140000000`)  
> **分析工具**：REA MCP + Frida 实时进程挂载 + Capstone 静态反汇编分析  
> **当前阶段**：GPT 评审意见落实、全局守护器收窄、条件变量完成机制厘清与测试规范升级。

---

## 一、 核心逆向结论速览 (Executive Summary)

1. **“进训练废档”的根本技术诱因**：
   - **诱因 1（致命硬编码断言）**：在 [`activity2_teampracticefacility.vcc`](file:///e:/vcsports/basketball/code/gamemodes/tkworld/activities2/arenas/activity2_teampracticefacility.vcc) 中，进入训练馆调用 `CreatePlayers` (`0x14163f4a0`) 时，引擎通过 `[this + 0x488]` 读取训练日程类型。在在线状态下，该类型由 2K 服务器每日下发；在单机离线状态下，该值未被在线下发且为 `0` (`UNKNOWN`)，导致代码直接跳转至错误处理分支，触发致命断言：
     $$\text{assert(false, "Can't start LivePractice, if type is unknown.")} \longrightarrow \texttt{int3 (0x14163f60d)}$$
   - **诱因 2（存档状态死锁与污染）**：在进入训练前，MC 时间线模块 (`careermode_timeline.vcc`) 已在本地存档中写入了“训练事件已启动”的状态标志。当遭遇 `int3` 崩溃或因服务器握手超时强退后，训练完成与退出逻辑 (`HandleLivePracticeEnded` / `HandleArenaExitRequest`) 未能执行，导致存档滞留在“训练中”的不一致状态。重新读档时游戏再次尝试恢复该训练，陷入无限崩溃死循环。

2. **日历进入 96% 卡死机理与 TaskManager / JobManager 关系厘清**：
   - **引擎双层异步体系**：
     * **底层 `TaskManager`（工作线程池）**：处理物理、网格渲染、流式加载等工作任务。主线程在 `0x141f9a9a0` 处作为 Task Pump 运行，当任务队列为空时，调用 `0x14216b440` (`SleepConditionVariableCS`) 挂起；当新任务通过 `0x14216b530` 入队时，调用 `0x14216b3f0` (`WakeAllConditionVariable`) 唤醒。
     * **上层 `CareerProgression JobManager`（玩法异步作业）**：`GET_SERVER_DATA_JOB` 是玩法层 HTTP 任务。其在 `0x141239230` 中尝试发起网络通信。在官方服务器关闭后，因后端检查失败或超时无法获得有效回包，状态变量滞留在 `3` (`JOB_STATE_PENDING`)，日历加载流程因而停止推进，表现为进度停在 96%。
   - **原生提前退出分支确证**：
     反汇编分析表明，在 `CreateAndSendRequest` 入口处存在原生状态检查：
     ```x86asm
     0x14123923a: cmp dword ptr [rcx + 0x30], 0
     0x141239241: jne 0x141239463 ; 若非 0 直接跳转尾部返回
     ...
     0x141239463: add rsp, 0x78
     0x141239467: pop rbx
     0x141239468: pop rbp
     0x141239469: ret
     ```
     当在入口将 `[rcx + 0x30]` 赋有效非零值（如 `2` = `COMPLETED`）时，函数**立即执行原生提前退出分支**，完全跳过网络派发调用（`0x141e51ad0`），不产生未决网络请求，也不覆写全局变量。

3. **收窄与移除全局定时覆写器**：
   - 彻底废除每 100ms 强制改写 `0x146351848` 的定时器逻辑；
   - 仅在命中被确认的 `GET_SERVER_DATA_JOB` 时执行一次性精准修补，避免对 MC 其它离线/本地状态造成全局污染。

4. **实机运行身份与防重入机制**：
   - 启动前核验 `NBA2K22.exe` SHA256 哈希值、PID 以及 5 个关键 Native 函数的机器码签名；
   - 进程内设立全局驻留锁 `globalThis.__NBA2K22_OFFLINE_PATCH_ACTIVE__`，杜绝重复注入未知状态补丁。

---

## 二、 关键底层机制分析 (Technical Architecture)

### 2.1 任务管理器 (TaskManager) 唤醒与等待机制

通过反汇编确证 2K22 底层 TaskManager 的条件变量机制：

```x86asm
; 1. 唤醒逻辑：TaskManager_Signal (RVA: 0x216B3F0, VA: 0x14216B3F0)
0x14216b3f0: sub      rsp, 0x28
0x14216b3f4: cmp      qword ptr [rcx + 0x10], 0
0x14216b3f9: jne      0x14216b402
0x14216b3fb: xor      eax, eax
0x14216b3fd: add      rsp, 0x28
0x14216b401: ret
0x14216b402: mov      qword ptr [rcx + 0x18], rdx
0x14216b406: call     qword ptr [rip + 0x88fc4] ; IAT 0x1421F43D0 -> WakeAllConditionVariable
0x14216b40c: mov      eax, 1
0x14216b411: add      rsp, 0x28
0x14216b415: ret

; 2. 入队唤醒：TaskManager_EnqueueTask (RVA: 0x216B530, VA: 0x14216B530)
0x14216b530: mov      qword ptr [rdi + 8], rcx
0x14216b534: mov      qword ptr [rdi + 0x10], rax
0x14216b53a: mov      qword ptr [rcx + 0x10], rdi
0x14216b546: mov      qword ptr [rax + 8], rdi  ; 双向链表插入
0x14216b54a: call     0x14216b3f0              ; 触发 WakeAllConditionVariable 唤醒工作线程
```

**分析**：主线程在 96% 时的 `SleepConditionVariableCS` 属于工作线程池的空闲等待，只要有新任务推入队列即可被正常唤醒，并不存在针对网络请求的特定系统级死锁。

---

### 2.2 原生网络作业提早返回与数据自洽性

#### `CreateAndSendRequest` (RVA: `0x1239230`)
- **入口地址**：`0x141239230`
- **机器码前缀**：`40 55 53 48 8b` (`push rbp; push rbx; mov rbp, rsp`)
- **原生判断**：
  * 若 `[rcx + 0x30] == 0`：继续向下执行在线检查；
  * 若 `[rcx + 0x30] != 0`：直接 `jne 0x141239463` -> `ret` 提前返回。
- **离线安全方案**：在 `onEnter` 拦截时将 `[rcx + 0x30]` 预置为 `2` (`COMPLETED`)，引擎原生走提前退出逻辑，完全避免创建底层网络套接字。

#### 本地数据解包自洽性 (`0x14118eb50` / `0x14118ef70`)
- 当未接收到远程数据覆盖时，函数使用本地数据仓库 Key `0xc7dba89b` 与 `0x30dcc93c`，从本地存档中解包玩家现有徽章点数与训练项目列表；
- 证明本地存档自包含所有必要数据，不依赖在线服务。

---

## 三、 单机化 5 重协同 Guard (The 5 Guards)

| Guard 编号 | 拦截目标 RVA | 目标函数 / 模块 | 核心操作与作用 | 状态 |
| :--- | :--- | :--- | :--- | :--- |
| **Guard 0** | `0x1239230` | `GET_SERVER_DATA_JOB::CreateAndSendRequest` | 预设 `[job+0x30]=2`，引导原生提前退出，跳过网络外发 | **已实现** |
| **Guard 1** | `0x163f4a0` | `TK_WORLD::...::CreatePlayers` | 校验 `[this+0x488]`，若为 `0` 补正为 `1`，避免断言崩溃 | **已实现** |
| **Guard 2** | `0x1731d30` | `ACTIVITY2_TEAMPRACTICEFACILITY::StateDispatch` | 监视 State 0~5 场景流转（模型加载、验证、实体创建、控制权） | **已实现** |
| **Guard 3** | `0x11f8680` | `LiveDrill_HandleCalculateResults` | 强制 `args[2] = 3`（固定三星），置位 `0x146352124 = 1` | **已实现** |
| **Guard 4** | `0x11f8bf0` | `CAREERMODE_LIVEPRACTICES::HandleLivePracticeEnded` | 记录训练结束与退出，确保日历正常推进，安全归档 | **已实现** |

---

## 四、 离线自动化测试套件

测试脚本：[`test_offline_practice_patch.py`](file:///e:/gemini_space/nba2k22/08_Domain_Applications/Antigravity_GM_Engine/tests/mc_offline_practice/test_offline_practice_patch.py)
* `test_create_players_entry_and_assertion`: 验证入口指令及断言字符串偏移；
* `test_drill_calculate_results_entry`: 验证 3 星校验指令；
* `test_live_practice_ended_entry`: 验证退出场馆栈平衡与入口指令；
* `test_tracking_flag_displacement`: 验证全局追踪标志位 `0x146352124` 相对寻址；
* `test_network_job_create_and_send_request`: 验证网络请求函数及 `0x504521a8` 会话码；
* `test_network_global_status_displacement`: 验证全局状态变量 `0x146351848` 寻址；
* `test_job_completion_callback_success_code`: 验证完成回调校验码；
* `test_js_patch_file_exists`: 验证注入脚本完整性。

执行结果：`8 passed in 0.54s`。

---

## 五、 实机运行与 Human 测试操作指南

### 5.1 运行前置检查
1. 确认游戏进程 `NBA2K22.exe` 正在运行，且停留在 MyCAREER 日历主界面；
2. 确认存档已提前备份（尽管不修改底层存档格式，仍遵循防御性测试原则）。

### 5.2 启动补丁守护器
在终端执行：
```powershell
node e:\gemini_space\nba2k22\08_Domain_Applications\Antigravity_GM_Engine\research\mc_offline_practice\run_offline_practice_patch.js
```
控制台将输出身份核验结果与武装日志：
```
[IDENTITY] Located target process: NBA2K22.exe (PID: 9240)
[ATTACH] Successfully attached to PID 9240
[HOOK_MOUNTED] Base: 0x140000000 | Binary signatures verified | Global status: 3
[ARMED] All guards active: Guard0_NetworkJobEarlyExit_0x1239230, Guard1_PracticeTypeNormalize_0x163f4a0, Guard2_SceneStateMonitor_0x1731d30, Guard3_DrillFixed3Star_0x11f8680, Guard4_PracticeEndedExit_0x11f8bf0
```

### 5.3 Human 游戏内测试步骤与观察清单
在日历上点击**“进入球队训练”**，按顺序观察并记录以下现场回执：
1. **进度条观察**：加载条是否顺利突破 96% 并关闭加载界面；
2. **场景视口**：游戏画面是否成功切换至球队训练球馆内；
3. **实体生成**：球场上是否能观察到 MyPLAYER 角色、队友及教练实体；
4. **控制权验证**：手柄左摇杆 / 键盘 WASD 是否能够正常控制 MyPLAYER 在场内跑动、运球；
5. **训练触发**：靠近训练项目（如投篮机或体能区）按确认键启动，完成后是否弹出 3 星完成结算；
6. **退场与归档**：走向球馆大门选择退出，游戏是否平稳黑屏过渡并返回 MC 日历，日历日期是否推进。

---

## 六、 明确尚未证明的事项清单 (Unproven Items)

按科学逆向准则，以下事项**尚未经 Human 实机实测确证**，不能提前假定成立：
1. **【待实机验证】** 仅将 `[job + 0x30]` 预置为 `2` 促使 `CreateAndSendRequest` 原生退出后，日历层的时间线状态机是否能在完全不收到后续异步通知的情况下，100% 触发球馆场景的实例化切换；
2. **【待实机验证】** `practicefacility_int.iff` 本地资源包中是否包含此存档所选球队的完整训练馆贴图，有无因特定球队球馆贴图缺失引发额外异步挂起的可能；
3. **【待实机验证】** 角色控制权接管（State 4）在离线模拟状态下，是否会因缺少在线账号的自建球员捏脸/装备数据（FaceScan / Apparel）而产生空指针回退。
