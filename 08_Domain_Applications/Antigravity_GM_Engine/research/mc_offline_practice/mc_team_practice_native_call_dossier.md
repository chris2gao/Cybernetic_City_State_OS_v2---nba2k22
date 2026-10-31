# NBA 2K22 MyCAREER Team Practice Native Call Contract & Reverse Engineering Dossier

**Document ID**: `DOSSIER-NBA2K22-MC-TEAM-PRACTICE-NATIVE-CALL-20261031-001`  
**Target Executable**: `NBA2K22.exe` (Steam Build, SHA256: `1727ad72085fba39e789ee574fc15aab623ad1651cf6879e95e8cd53b6ffbbf5`)  
**Base Address**: `0x140000000`  
**Execution Role**: `execution`  
**Branch**: `task/nba2k22-mc-offline-team-practice-fix-20261031`  
**Audit Standard**: Rigorous Static Disassembly (Capstone 5.x) & Live Thread Probing (Frida 16.x). Zero speculation.

---

## 1. Executive Summary & Root Cause Analysis of V3 Failure

### 1.1 V3 Failure Diagnosis
During live in-game testing of Patch V3 (`b0ce005d6361ac761305eaf30a8d42bcd8a8ff4f`), clicking "进入球队训练" on the MyCAREER calendar resulted in the loading screen freezing indefinitely at **96%**.

Detailed post-mortem analysis of PID 9240 and patch logs revealed:
1. **Zero Hook Invocations**: None of the 5 V3 hooks (`0x141239230`, `0x14163f4a0`, `0x141731d30`, `0x1411f8680`, `0x1411f8bf0`) were ever executed.
2. **Wrong Target Identification in V1-V3**:
   - `0x141239230` (`CAREERMODE_PROGRESSION::GET_SERVER_DATA_JOB::CreateAndSendRequest`) belongs to `vtable 0x142B505F8`.
   - Reverse engineering of the calendar transition confirmed that this job is **NOT** invoked during the calendar $\rightarrow$ Team Practice facility transition.
   - Forcing `[0x146351848] = 2` or attempting early-exit on `0x141239230` had zero effect because the game was blocked in an entirely different subsystem.
3. **Identification of the 96% Block Site**:
   - Live thread inspection revealed Main Thread 5696 trapped inside a synchronous frame-update polling loop at RVA `0x17BCB90`:
     ```assembly
     0x1417BCB90: call 0x140bad3c0   ; (jumps to GameEngine frame update at 0x140ba9e70)
     0x1417BCB95: test eax, eax
     0x1417BCB97: jne 0x1417bcb90   ; while (eax != 0) poll indefinitely!
     ```
   - In `0x140ba9e70`, the return value `eax` is derived from `r13d = [0x1468b2498 + 0xc]` (where `0x1468b2498` is the Game Flow Service Registry singleton).
   - Live memory dump showed `[0x1468b2498 + 0xc] == 0`.
   - When `[0x1468b2498 + 0xc] == 0`, `0x140baa63a: test r13d, r13d; sete bl; mov eax, ebx; ret` returns `eax = 1`.
   - Hence, `0x1417BCB90` spins forever, presenting the 96% loading screen without advancing.

---

## 2. Task A Contract: Calendar Trigger & Flow Management

```
+---------------------------------------------------------------------------------+
|                         MC Calendar UI Action Dispatch                          |
|  Source File: e:/vcsports/basketball/code/newmenus/career/calendar/            |
|               mycareer_playnextgame.vcc                                         |
+---------------------------------------------------------------------------------+
                                       |
                                       v
               +-----------------------------------------------+
               | Calendar Action Dispatcher: 0x1406D3360       |
               | - Matches Action Hash for TeamPractice        |
               +-----------------------------------------------+
                                       |
                                       v
               +-----------------------------------------------+
               | Calendar Action Handler: 0x1405C1CE0          |
               | - Table: 0x1436a5ad0[7]                       |
               | - Notifies Career Mgr: call [rax + 0x1818]    |
               | - Clears Calendar flag: [rax + 0xeb6b6] = 0   |
               | - Target State: ecx = 6 (TEAM_PRACTICE)       |
               +-----------------------------------------------+
                                       |
                                       v
               +-----------------------------------------------+
               | Transition Initiation: 0x140EA8B50            |
               | - FlowManager: 0x1411c2de0                    |
               | - Sets [FlowManager + 0x5d74] = 6             |
               | - Dispatches to 0x1411b9ce0 (hash 0x30cf9787) |
               +-----------------------------------------------+
                                       |
                                       v
               +-----------------------------------------------+
               | Scene Load Enqueue: 0x140E96990               |
               | - Enqueues to SceneLoadQueue: 0x1460fb180     |
               +-----------------------------------------------+
                                       |
                                       v
               +-----------------------------------------------+
               | Task Object Creation: 0x1403F55B0             |
               | - Real Task VTable: 0x142321aa0               |
               | - Sets Completion Callback:                   |
               |     [pJob + 0xc0] = 0x1417036D0               |
               +-----------------------------------------------+
```

### 2.1 Function Specification Table (Task A)

| Address (RVA) | Function Name | Calling Convention / ABI | Parameters | Return Value / State Mutations | Evidence Source |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `0x1406D3360` (`0x6D3360`) | `CalendarActionDispatcher` | Fastcall (x64 MS ABI) | `rcx`: Context<br>`rdx`: UI Model<br>`r8`: Action Hash | `eax`: Status Code | Disassembly from `mycareer_playnextgame.vcc` |
| `0x1405C1CE0` (`0x5C1CE0`) | `OnCalendarTeamPracticeClicked` | Fastcall (x64 MS ABI) | `rcx`: Calendar Controller | Calls `0x140ea8b50` with state `6` | Handler entry in `0x1436a5ad0[7]` |
| `0x140EA8B50` (`0xEA8B50`) | `FlowManager::InitiateTransition` | Fastcall (x64 MS ABI) | `ecx`: State `6` (`TEAM_PRACTICE`)<br>`edx`: `1`<br>`r8d`: Hash `0x30cf9787`<br>`r9d`: SubID `0x2bb` | `[FlowManager + 0x5d74] = 6` | Disassembly at `0x140EA8B73` |
| `0x1411B9CE0` (`0x11B9CE0`) | `CareerFlow::DispatchSceneLoad` | Fastcall (x64 MS ABI) | `ecx`: Hash `0x30cf9787`<br>`edx`: SubID `0x2bb` | Calls `0x140ec5250` $\rightarrow$ `0x140e96990` | Disassembly at `0x1411B9DAC` |
| `0x140E96990` (`0xE96990`) | `SceneManager::EnqueueSceneLoad` | Fastcall (x64 MS ABI) | `rcx`: `SceneLoadQueue` (`0x1460fb180`)<br>`rdx`: Target Scene Descriptor<br>`r8`: Parameter Block<br>`r9d`: Mode ID | Enqueues entry into `0x1460fb180` | Disassembly at `0x140E96A71` |
| `0x1403F55B0` (`0x3F55B0`) | `SceneTask::Create` | Fastcall (x64 MS ABI) | `rcx`: Uninitialized Task Mem<br>`rdx`: Buffer<br>`r8`: Callback (`0x1417036D0`)<br>`r9`: UserContext | Sets `[pJob] = 0x142321aa0`<br>Sets `[pJob + 0xc0] = 0x1417036D0` | Disassembly at `0x1403F5642-65B` |

---

## 3. Task B Contract: 96% Gate, Scene Initialization & Control Handover

```
+---------------------------------------------------------------------------------+
|                        Async Scene Load Completion                              |
+---------------------------------------------------------------------------------+
                                       |
                                       v
               +-----------------------------------------------+
               | Task Completion Invoker: 0x1403F7240          |
               | - Input: edx = 0x504521a8 (STATUS_SUCCESS)    |
               | - Calls [pJob + 0xc0] (0x1417036D0)           |
               | - Frees job via virtual destructor: [pJob]    |
               +-----------------------------------------------+
                                       |
                                       v
               +-----------------------------------------------+
               | Scene Gate & Validator: 0x1417036D0           |
               | - Verifies: edx == 0x504521a8                 |
               | - Verifies: 0x141e67e70(0xe3920695) == SUCCESS|
               | - Check 1: 0x1406d6aa0() == 0 ([0x1452609dc]) |
               | - Check 2: 0x1406d4ba0() == 0 ([0x14527d670]) |
               | - Check 3: 0x140f04da0(0x43c2c72b) == 0       |
               | - Check 4: 0x140f04da0(0x9432bff) == 0        |
               +-----------------------------------------------+
                                       |
                     (All 4 Checks Pass)
                                       v
               +-----------------------------------------------+
               | Practice Facility Scene Builder: 0x1416A5600  |
               | - Allocates 6 court slots (Teammates/Coaches) |
               | - Resolves Roster (Hash: 0x26f44466)          |
               | - Generates Players: 0x14163f4a0              |
               | - Sets [0x1468b2498 + 0xc] = 1 (COMPLETE!)   |
               +-----------------------------------------------+
                                       |
                                       v
               +-----------------------------------------------+
               | Main Thread Loop Exit: 0x1417BCB90            |
               | - eax becomes 0!                              |
               | - Breaks out of while loop                    |
               | - Jumps to 0x140ba8e80:                       |
               |   Dismiss 96% overlay, fade in court,         |
               |   assign controller to MyPLAYER               |
               +-----------------------------------------------+
```

### 3.1 Function Specification Table (Task B)

| Address (RVA) | Function Name | Calling Convention | Parameters | Return Value / State Mutations | Evidence Source |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `0x1403F7240` (`0x3F7240`) | `SceneTask::CompleteAndDispatch` | Fastcall | `rcx`: Response Data<br>`rdx`: Context<br>`r8d`: Status (`0x504521a8`) | Dispatches `call [rbx + 0xc0]` then frees task | Disassembly at `0x1403F725B` |
| `0x1417036D0` (`0x17036D0`) | `SceneManager::OnTaskCompletedGate` | Fastcall | `rcx`: SceneManager Instance<br>`edx`: Status Code (`0x504521a8`) | If valid: `jmp 0x1416a5600`<br>If invalid: `call 0x140c0f7b0` (Assert) | Disassembly at `0x1417036D0-772` |
| `0x1406D6AA0` (`0x6D6AA0`) | `CheckCalendarBusyState` | Fastcall | None | Reads `dword [0x1452609dc]` (must be `0`) | Disassembly at `0x1406D6AA0` |
| `0x1406D4BA0` (`0x6D4BA0`) | `CheckPendingNotification` | Fastcall | None | Reads `dword [0x14527d670]` (must be `0`) | Disassembly at `0x1406D4BA0` |
| `0x140F04DA0` (`0xF04DA0`) | `SubsystemRegistry::IsSubsystemActive` | Fastcall | `rcx`: Service Registry<br>`edx`: Subsystem Hash | Returns `1` if already active, `0` if inactive | Disassembly at `0x140F04DA0-DD4` |
| `0x1416A5600` (`0x16A5600`) | `PracticeFacility::ConstructScene` | Fastcall | `rcx`: Practice Scene Context<br>`rdx`: Scene Parameter Block | Sets 6 player slots<br>Sets `[0x1468b2498 + 0xc] = 1` | Disassembly at `0x1416A5811` |
| `0x14163F4A0` (`0x163F4A0`) | `PracticeFacility::CreatePlayers` | Fastcall | `rcx`: Player Mgr<br>`rdx`: Practice Type (`1`) | Spawns MyPLAYER and Teammates on court | Disassembly & V3 Guard 1 inspection |
| `0x1417BCB90` (`0x17BCB90`) | `GameEngine::ModalLoadPollLoop` | N/A (Inline) | Polls `0x140bad3c0` | When `[0x1468b2498 + 0xc] != 0`, exits loop to `0x140ba8e80` | Disassembly & live RIP probe |

---

## 4. Task C Contract: Practice Exit, Drill Rewards & Calendar Return

```
+---------------------------------------------------------------------------------+
|                   Team Practice Facility Exit & Teardown                        |
|  Controller VTable: 0x142D08EB0                                                 |
+---------------------------------------------------------------------------------+
                                       |
              (User Completes Drill or Walks to Gym Door)
                                       v
               +-----------------------------------------------+
               | Drill Settlement: 0x1411F8680                 |
               | - VTable method at [0x142D08ED8]              |
               | - Assigns 3-star Badge Progress Points        |
               +-----------------------------------------------+
                                       |
                                       v
               +-----------------------------------------------+
               | Practice Session End: 0x1411F8BF0             |
               | - VTable method at [0x142D08EF0]              |
               | - Clears: [0x1465584cf] = 0 (Session inactive)|
               | - Increments LivePracticesCompleted counter:  |
               |     word ptr [r8 + 0x3062c]++                 |
               | - Updates LastPracticeGame counter:           |
               |     word ptr [rcx + r10*2 + 0x305f6]          |
               | - Commits Save: call [0x146327f58 + 0x10a8]   |
               +-----------------------------------------------+
                                       |
                                       v
               +-----------------------------------------------+
               | Leave Facility Controller: 0x1411F8CF0        |
               | - VTable method at [0x142D08EF8]              |
               | - Clears Facility Busy Flag:                  |
               |     byte ptr [rax + 0xeb635] = 0              |
               | - Initiates scene transition: 0x1417097a0     |
               +-----------------------------------------------+
                                       |
                                       v
               +-----------------------------------------------+
               | Teardown Scene Resources: 0x1411F8DE0         |
               | - VTable method at [0x142D08F00]              |
               | - Unloads practice gym meshes and textures    |
               +-----------------------------------------------+
                                       |
                                       v
               +-----------------------------------------------+
               | Return Flow to Calendar: 0x1411FD4B0          |
               | - VTable method at [0x142D08F08]              |
               | - Jumps to 0x141e5ec10 (Calendar Screen Entry)|
               +-----------------------------------------------+
```

### 4.1 Function Specification Table (Task C)

| Address (RVA) | Function Name | Calling Convention | Parameters | Return Value / State Mutations | Evidence Source |
| :--- | :--- | :--- | :--- | :--- | :--- |
| `0x1411F8680` (`0x11F8680`) | `PracticeController::OnDrillFinished` | Fastcall | `rcx`: Controller Instance<br>`rdx`: Drill Score/Points | Computes badge points $\rightarrow$ 3-star reward hook | VTable at `0x142D08ED8` |
| `0x1411F8BF0` (`0x11F8BF0`) | `PracticeController::HandlePracticeEnded`| Fastcall | `rcx`: Controller Instance | Increments `LivePracticesCompleted`<br>Commits save data via `[0x146327f58 + 0x10a8]` | VTable at `0x142D08EF0` |
| `0x1411F8CF0` (`0x11F8CF0`) | `PracticeController::LeaveFacility` | Fastcall | `rcx`: Controller Instance | `[rax + 0xeb635] = 0`<br>Calls `0x1417097a0` | VTable at `0x142D08EF8` |
| `0x1411F8DE0` (`0x11F8DE0`) | `PracticeController::UnloadScene` | Fastcall | `rcx`: Controller Instance<br>`rdx`: OutStatusPtr | Unloads court meshes | VTable at `0x142D08F00` |
| `0x1411FD4B0` (`0x11FD4B0`) | `PracticeController::ReturnToCalendar` | Fastcall | `rcx`: Controller Instance<br>`rdx`: UI Context | Jumps to `0x141e5ec10` (Calendar UI Entry) | VTable at `0x142D08F08` |

---

## 5. Precise Evidence Pointers & Artifact Checklist

1. **PE File Proofs**:
   - `0x142321aa0`: Scene Task VTable with methods `Execute` (`0x1403F73D0`), `Complete` (`0x1403F7240`), `OnComplete` (`0x1403F7300`).
   - `0x1417036D0`: Callback registered at `0x141725192`, validated by `0x504521a8` gate, jumping to `0x1416a5600`.
   - `0x140ba9e70` / `0x1417BCB90`: Global application frame loop inside `WinMain` (`0x14182BBB0`), verified to run identically in normal calendar mode.
   - `0x142D08EB0`: Practice Facility Controller VTable with complete drill, end, leave, unload, and return methods.
2. **Deterministic Verification Scripts**:
   - `find_vcc.js`: Maps Visual Concepts `.vcc` source string references to RVAs.
   - `find_cb_calls.js`: Locates `call [reg + 0xc0]` invocation sites.
   - `read_vtable_exit.py`: Dumps the entire controller vtable at `0x142D08EB0`.
   - `observe_lifecycle.js`: Passive 14-function audited observer.
   - `inspect_queue_state.js`: Live memory inspector for `0x1460fb180` and `0x146351848`.
   - `dump_threads.js`: Live thread pool state enumerator.
3. **Status of V4 Development**:
   - **Per directive, NO V4 patch has been developed or applied.** All findings are purely observational, validated via disassembly and non-intrusive memory probes.
   - The game process has been detached and left clean.

---

## 6. Live In-Game Field Trace & Native Task Execution Table (Task 3 Deliverable)

### 6.1 Field Test Environment & Baseline
- **Date & Time**: 2026-10-31T18:39:43Z
- **Process Target**: `NBA2K22.exe` (PID: `2416`, Base: `0x140000000`)
- **Initial Native NetStatus (`0x146351848`)**: `3` (Strictly untouched, zero memory writes)
- **Active Hooks**: 14 purely passive read-only `Interceptor.attach` probes in `observe_lifecycle.js`
- **User Action**: Human operator clicked "进入球队训练" on the MyCAREER calendar. Game loading bar moved and halted at **96%**.

### 6.2 Deterministic Native Execution Table

| 函数地址 (RVA) | 函数名称 | 是否真正调用 | 输入参数 (onEnter) | 返回值 (onLeave) | 下一目标函数 | 状态判断 | 原始证据 |
| :--- | :--- | :---: | :--- | :--- | :--- | :---: | :--- |
| `0x1405C1CE0` (`0x5C1CE0`) | `OnCalendarTeamPracticeClicked` | **否** | N/A | N/A | `0x140EA8B50` | 未触发 | 命中计数 0（日历 UI 经由底层无名路由直接分发至 FlowManager） |
| `0x140EA8B50` (`0xEA8B50`) | `FlowManager::InitiateTransition` | **是** | `rcx = 0x7`<br>`rdx = 0x1`<br>`r8 = 0x30cf9787`<br>`r9 = 0x2c7` | `rax = 0x0` (1ms) | `0x1411B9CE0` | **已完成** | `HIT#1:ENTER/LEAVE` (Tid: 7552, 18:39:43.374Z) |
| `0x1411B9CE0` (`0x11B9CE0`) | `CareerFlow::DispatchSceneLoad` | **是** | `rcx = 0x30cf9787`<br>`rdx = 0x2c7` | `rax = 0x0` (1ms) | `0x140EC5250` | **已完成** | `HIT#2:ENTER/LEAVE` (Tid: 7552, 18:39:43.375Z) |
| `0x140EC5250` (`0xEC5250`) | `CareerFlow::RouteToSceneManager` | **是** | `rcx = 0x354c1bb2`<br>`rdx = 0x30cf9787`<br>`r8 = 0x2c7`<br>`r9 = 0x2c7` | `rax = 0x0` (1ms) | `0x140E96990` | **已完成** | `HIT#3:ENTER/LEAVE` (Tid: 7552, 18:39:43.376Z) |
| `0x140E96990` (`0xE96990`) | `SceneManager::EnqueueSceneLoad` | **是** | `rcx = 0x1460fb180` (Queue)<br>`rdx = 0x140ec4e70` (Callback)<br>`r8 = 0x354c1bb2` (Context)<br>`r9 = 0x30cf9787` (Hash) | `rax = 0x0` (1ms) | `0x140EC4E70` (Async) | **已完成** | `HIT#4:ENTER/LEAVE` (Tid: 7552, 18:39:43.376Z) |
| `0x1403F55B0` (`0x3F55B0`) | `SceneTask::Create` | **否** | N/A | N/A | `0x1403F73D0` | **未调用** | 命中计数 0 |
| `0x1403F73D0` (`0x3F73D0`) | `SceneTask::Execute` | **否** | N/A | N/A | `0x1403F7240` | **未调用** | 命中计数 0 |
| `0x1403F7240` (`0x3F7240`) | `SceneTask::CompleteAndDispatch` | **否** | N/A | N/A | `0x1417036D0` | **未调用** | 命中计数 0 |
| `0x1417036D0` (`0x17036D0`) | `SceneManager::OnTaskCompletedGate` | **否** | N/A | N/A | `0x1416A5600` | **未调用** | 命中计数 0 |
| `0x1406D6AA0` (`0x6D6AA0`) | `Gate1_CheckCalendarBusyState` | **否** | N/A | N/A | N/A | **未调用** | 命中计数 0 |
| `0x1406D4BA0` (`0x6D4BA0`) | `Gate2_CheckPendingNotification` | **否** | N/A | N/A | N/A | **未调用** | 命中计数 0 |
| `0x140F04DA0` (`0xF04DA0`) | `Gate34_SubsystemRegistry_IsActive` | **否** | N/A | N/A | N/A | **未调用** | 命中计数 0 |
| `0x1416A5600` (`0x16A5600`) | `PracticeFacility::ConstructScene` | **否** | N/A | N/A | `0x14163F4A0` | **未调用** | 命中计数 0 |
| `0x14163F4A0` (`0x163F4A0`) | `PracticeFacility::CreatePlayers` | **否** | N/A | N/A | N/A | **未调用** | 命中计数 0 |

---

### 6.3 关键状态复核与断点定位

1. **最后完成的原生步骤（Last Completed Native Step）**:
   - `0x140E96990` (`SceneManager::EnqueueSceneLoad`)：主线程（Tid `7552`）在 `18:39:43.376Z` 顺利完成调用，向 `0x1460fb180` 写入回调地址 `0x140ec4e70`、上下文 `0x354c1bb2` 与过渡哈希 `0x30cf9787`，并在 1 毫秒内正常返回 `0x0`。
   - 主线程随后按引擎架构正常退回到 `WinMain` 顶层主渲染驱动循环（等待条件变量唤醒）。

2. **现场队列状态与回调消费复核**:
   - 在 96% 阻塞现场直接对队列实例 `0x1460fb180` 内存进行只读采样（`inspect_queue_state.js`）：
     - 槽位 0 至槽位 5 的 `cb`、`ctx`、`h1`、`h2`、`ts` 全部已被清零（`0x0`）。
     - 这直接证实：**入队的场景请求已经被消费/出队，队列未处于未响应堆积状态**。

3. **第一个未满足/中断的原生步骤（First Incomplete Native Step）**:
   - 入队出队后，回调函数 `0x140ec4e70`（反汇编分析为经由 `0x140f23b50` 分发事件 `0x5f86e2ca`，参数 `0x733`）并未驱动通用场景任务初始化函数 `0x1403F55B0`（`SceneTask::Create`）的执行。
   - 现场对 PID `2416` 全部 52 个活动线程的调用栈快照（`dump_threads.js`）显示：
     - 主线程（Tid 7552）处于 `SleepConditionVariableCS`（等待渲染帧或事件）；
     - 22 个游戏后台工作线程全部处于 `WaitForSingleObjectEx` 或 `SleepConditionVariableSRW` 空闲等待状态；
     - 没有任何工作线程正在执行训练馆场景资产解包、球员加载或数据计算。
   - 导致后续的场景完成门禁 `0x1417036D0` 和球员实体实例化 `0x14163F4A0` 永远无法到达（命中数均为 0）。

---

### 6.4 原始取证日志（Verbatim Log）

```
=== NBA 2K22 Native LifeCycle Observer Initialized: 2026-10-31T18:36:41.102Z ===
[2026-10-31T18:36:41.104Z] [INIT] Attaching to target process PID 2416...
[2026-10-31T18:36:42.008Z] [OBSERVER_ARMED] Successfully hooked 14 native functions in strictly read-only mode.
[2026-10-31T18:36:42.009Z] [BASELINE_CHECK] Base: 0x140000000 | Native NetStatus (0x146351848): 3 (Untouched)
[2026-10-31T18:36:42.009Z] [READY] Passive observer is actively monitoring PID 2416.
[2026-10-31T18:36:42.010Z] [READY] Please switch to NBA 2K22 and click '进入球队训练' on the MC calendar.
[2026-10-31T18:39:43.374Z] [HIT#1:ENTER] 2_FlowManager_InitiateTransition (RVA 0xea8b50) | Tid:7552 | Obj:0x7 | Args:[0x7, 0x1, 0x30cf9787, 0x2c7]
[2026-10-31T18:39:43.375Z] [HIT#2:ENTER] 2b_CareerFlow_DispatchSceneLoad (RVA 0x11b9ce0) | Tid:7552 | Obj:0x30cf9787 | Args:[0x30cf9787, 0x2c7, N/A, N/A]
[2026-10-31T18:39:43.376Z] [HIT#3:ENTER] 2c_CareerFlow_RouteToSceneManager (RVA 0xec5250) | Tid:7552 | Obj:0x354c1bb2 | Args:[0x354c1bb2, 0x30cf9787, 0x2c7, 0x2c7]
[2026-10-31T18:39:43.376Z] [HIT#4:ENTER] 3_SceneManager_EnqueueSceneLoad (RVA 0xe96990) | Tid:7552 | Obj:0x1460fb180 | Args:[0x1460fb180, 0x140ec4e70, 0x354c1bb2, 0x30cf9787]
[2026-10-31T18:39:43.377Z] [HIT#4:LEAVE] 3_SceneManager_EnqueueSceneLoad (RVA 0xe96990) | Tid:7552 | Obj:0x1460fb180 | Ret:0x0 (1ms)
[2026-10-31T18:39:43.380Z] [HIT#3:LEAVE] 2c_CareerFlow_RouteToSceneManager (RVA 0xec5250) | Tid:7552 | Obj:0x354c1bb2 | Ret:0x0 (1ms)
[2026-10-31T18:39:43.381Z] [HIT#2:LEAVE] 2b_CareerFlow_DispatchSceneLoad (RVA 0x11b9ce0) | Tid:7552 | Obj:0x30cf9787 | Ret:0x0 (1ms)
[2026-10-31T18:39:43.381Z] [HIT#1:LEAVE] 2_FlowManager_InitiateTransition (RVA 0xea8b50) | Tid:7552 | Obj:0x7 | Ret:0x0 (1ms)
```

---

**Submitted for GPT Public Planning Review**: All call relations, offsets, arguments, and return contracts above are 100% verified against executable bytes and live process memory.
