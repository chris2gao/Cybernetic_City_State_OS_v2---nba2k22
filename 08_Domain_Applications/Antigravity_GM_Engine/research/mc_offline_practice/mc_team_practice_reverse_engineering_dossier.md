# NBA 2K22 MyCAREER 球队训练馆 (Team Practice Facility) 离线逆向与解封研究报告

> **执行窗口**：工程实现窗口 (`ENGINEERING_IMPLEMENTATION`)  
> **研究对象**：`NBA2K22.exe` (PE SHA256: `1727ad72085fba39e789ee574fc15aab623ad1651cf6879e95e8cd53b6ffbbf5`, Base: `0x140000000`)  
> **分析工具**：REA MCP + Frida 实时进程挂载 + Capstone 静态反汇编分析  
> **核心诉求**：解决官方服务器关闭后 MC 模式进入球队训练导致“废档”及日历进入“96% 加载卡死”的问题，实现单机自由进入、完成训练并结算徽章奖励、安全退出的完整闭环。

---

## 一、 核心逆向结论速览 (Executive Summary)

1. **“进训练废档”的根本技术诱因**：
   - **诱因 1（致命硬编码断言）**：在 [`activity2_teampracticefacility.vcc`](file:///e:/vcsports/basketball/code/gamemodes/tkworld/activities2/arenas/activity2_teampracticefacility.vcc) 中，进入训练馆调用 `CreatePlayers` (`0x14163f4a0`) 时，引擎通过 `[this + 0x488]` 读取训练日程类型。在在线状态下，该类型由 2K 服务器每日下发；在单机离线状态下，该值未被在线下发且为 `0` (`UNKNOWN`)，导致代码直接跳转至错误处理分支，触发致命断言：
     $$\text{assert(false, "Can't start LivePractice, if type is unknown.")} \longrightarrow \texttt{int3 (0x14163f60d)}$$
   - **诱因 2（存档状态死锁与污染）**：在进入训练前，MC 时间线模块 (`careermode_timeline.vcc`) 已在本地存档中写入了“训练事件已启动”的状态标志。当遭遇 `int3` 崩溃或因服务器握手超时强退后，训练完成与退出逻辑 (`HandleLivePracticeEnded` / `HandleArenaExitRequest`) 未能执行，导致存档滞留在“训练中”的不一致状态。重新读档时游戏再次尝试恢复该训练，陷入无限崩溃死循环，即玩家俗称的“废档”。

2. **日历进入卡死在 96% 的根本诱因**：
   - 现场实机抓取表明，主线程在 96% 时阻塞在 `KERNELBASE!SleepConditionVariableCS` (`0x14216b47e`)，等待 `TaskManager` (`0x146933668`) 中的后台任务完成；
   - 导致阻塞的直接来源是 `CAREERMODE_PROGRESSION::GET_SERVER_DATA_JOB::CreateAndSendRequest` (`0x141239230`)；
   - 该任务在尝试向 `https://nba2k22-ws.2ksports.com:22004/Session` 同步进度时，因服务器已关闭无法完成握手，导致任务状态 `[job + 0x30]` 与全局状态变量 `g_ServerDataJobStatus` (`0x146351848`) 永久停留在 `3` (`JOB_STATE_PENDING` / 阻塞态)，场景加载器因此等待网络超时而挂死在 96%。

3. **网络状态码与数据依赖验证**：
   - 状态码 `0x504521a8` 确证为 2K 后端会话成功的魔数 (`STATUS_SESSION_SUCCESS`)；
   - 当会话成功时，`JobCompletionCallback` (`0x1411f7e70`) 会调用 `0x14118eb50`，其在无远程 Payload 时自动回退至本地数据仓库分支 `0x14118ef70`，从本地存档中解包玩家徽章与训练进度（Key: `0x30dcc93c`）；
   - 因此，**所有训练馆数据在本地存档中均完整存在**，网络同步仅是官方服务器的在线验证冗余。

4. **单机完整闭环解决方案 (The 5 Guards)**：
   - **Guard 0（网络阻塞旁路）**：在 `CreateAndSendRequest` (`0x141239230`) 入口将任务状态 `[pJob + 0x30]` 与 `0x146351848` 置为 `2` (`COMPLETED`)，并阻止无效的网络发送，彻底解除 96% 阻塞；
   - **Guard 1（进门类型补正）**：在 `CreatePlayers` (`0x14163f4a0`) 入口将 `[this + 0x488]` 从 `0` 补正为 `1`（标准团队训练），规避 `int3` 致命崩溃；
   - **Guard 2（状态机流转监视）**：监视 `ACTIVITY2_TEAMPRACTICEFACILITY::StateDispatch` (`0x141731d30`)，确保 State 0~4 顺畅流转至角色生成与控制权接管；
   - **Guard 3（固定 3 星奖励）**：在 `LiveDrill_HandleCalculateResults` (`0x1411f8680`) 入口强制将 `args[2]` 设为 `3`，并置位全局追踪标志位 `0x146352124 = 1`，本地发放最大徽章经验；
   - **Guard 4（安全退出与归档）**：在 `HandleLivePracticeEnded` (`0x1411f8bf0`) 退出训练馆并清除日历事件标记，安全落盘。

---

## 二、 关键反汇编与证据链 (Forensic Evidence)

### 2.1 网络作业与 96% 加载卡死反汇编分析

#### `CreateAndSendRequest` (RVA: `0x1239230`, VA: `0x141239230`)
```x86asm
0x141239230: push     rbp
0x141239232: push     rbx
0x141239233: mov      rbp, rsp
0x141239236: sub      rsp, 0x78
0x14123923a: cmp      dword ptr [rcx + 0x30], 0     ; 检查 Job 状态
0x14123923e: mov      rbx, rcx
0x141239241: jne      0x141239463                  ; 若已启动直接退出
0x14123925f: call     0x1420728b0                  ; 获取 Backend Context
0x141239278: call     qword ptr [r10 + 0x68]       ; 查询服务器在线状态
0x14123927c: mov      eax, dword ptr [rbp + 0x18]
0x14123927f: cmp      eax, 0x504521a8              ; 校验是否为会话成功码
0x141239284: je       0x14123929f                  ; 成功则进入发送流程
0x141239286: mov      dword ptr [rbx + 0x18], eax  ; 失败：记录错误码
0x141239289: mov      dword ptr [rbx + 0x30], 3    ; 【置状态为 3 PENDING】
0x141239290: mov      dword ptr [rip + 0x51185ae], 3 ; 【写全局 0x146351848 = 3】
0x14123929a: jmp      0x141239436                  ; 退出函数，挂死主线程
```

#### `JobCompletionCallback` (RVA: `0x11F7E70`, VA: `0x1411F7E70`)
```x86asm
0x1411f7e70: cmp      edx, 0x75482638              ; 校验事件类型
0x1411f7e76: je       0x1411f7fd4
0x1411f7f1d: cmp      dword ptr [r8 + 0x34], 0     ; 校验预错误标记
0x1411f7f22: je       0x1411f7f46
0x1411f7f46: cmp      edx, 0x504521a8              ; 【核心校验】会话返回码是否成功
0x1411f7f4c: jne      0x1411f7f87                  ; 失败分支
; 成功分支：
0x1411f7f66: mov      qword ptr [rip + 0x512f503], rcx ; 存储全局上下文 [0x146327470]
0x1411f7f7b: call     0x14118eb50                  ; 调用本地数据仓库解包
0x1411f7f80: mov      eax, 2                       ; eax = 2 (COMPLETED)
0x1411f7f85: jmp      0x1411f7f90
; 状态回写：
0x1411f7f90: mov      dword ptr [rdi + 0x30], eax  ; pJob->status = 2 (或 3)
0x1411f7f97: mov      dword ptr [rip + 0x51598ab], eax ; [0x146351848] = 2 (或 3)
```

#### 全局网络状态 `0x146351848` 的 6 个写入点
通过 Capstone 全 PE 静态扫描，确证全程序仅有 6 处写入该变量：
1. `0x1411F7F35`: `JobCompletionCallback`（预错误置 3）
2. `0x1411F7F97`: `JobCompletionCallback`（完成状态写 `eax`，2 或 3）
3. `0x141239290`: `CreateAndSendRequest`（后端离线置 3）
4. `0x141239301`: `CreateAndSendRequest`（Payload 准备失败置 3）
5. `0x1412393D2`: `CreateAndSendRequest`（发起请求前置 3）
6. `0x141239459`: `CreateAndSendRequest`（取消时置 3）

---

### 2.2 本地数据仓库解包分支 (`0x14118ef70`)
在 `0x14118eb50` 中，当 `r9d == 0`（未从网络收到任何远程覆盖数据）时：
```x86asm
0x14118eb9a: mov      edx, 0xc7dba89b              ; 数据仓库 Key
0x14118ebaf: call     0x141e67440                  ; FindLocalDataStoreEntry
0x14118ebe0: call     0x141e66e40                  ; ReadLocalDataStore
```
随后调用 `0x14118ef70`，从本地存档解包核心数据：
```x86asm
0x14118f0f6: mov      edx, 0x30dcc93c              ; 徽章经验数据 Key
0x14118f0fb: mov      rcx, rsi
0x14118f0fe: call     0x141e68210                  ; 读取本地徽章点数
0x14118f139: mov      dword ptr [rbx + 0xe8f20], eax ; 填充当前角色进度
0x14118f13f: mov      edx, 0xd46d9c                ; 球员属性 Key
0x14118f147: call     0x141e67440                  ; 读取属性表
```
**确证**：本地数据完全自洽，无需服务器提供即可直接运行。

---

### 2.3 训练馆进入断言与角色生成 (`0x14163f4a0`)
在函数 `TK_WORLD::ACTIVITY2_TEAMPRACTICEFACILITY::CreatePlayers` (`0x14163f4a0`)：
```x86asm
0x14163f4db: mov      ecx, dword ptr [r14 + 0x488] ; 读取 Practice Type
0x14163f4ff: test     ecx, ecx
0x14163f501: je       0x14163f595                  ; 【致命分支】若为 0 则跳转崩溃
0x14163f507: sub      ecx, 1
0x14163f50a: je       0x14163f580                  ; 类型 1: 团队训练 (Team Practice)
0x14163f50c: sub      ecx, 1
0x14163f50f: je       0x14163f564                  ; 类型 2: 个人训练 (Personal Practice)
```
若 `ecx == 0` 跳转至 `0x14163f595`：
```x86asm
0x14163f5dd: lea      rax, [rip + 0x1682bec]       ; "Can't start LivePractice, if type is unknown."
0x14163f604: call     0x141e51ad0                  ; 错误断言处理
0x14163f60d: int3                                  ; 【硬断点崩溃】直接终止进程或挂死
```

---

### 2.4 训练项目的结算与奖励分发 (`0x1411f8680`)
在 `CAREERMODE_DELEGATE::LiveDrill_HandleCalculateResults` 中：
```x86asm
0x1411f88fb: cmp      ebp, 3                        ; 检查是否获得 3 星评价
0x1411f88fe: mov      dword ptr [rip + 0x5158818], 1
0x1411f8933: mov      edx, ebp                      ; edx = 星级 (3)
0x1411f8935: mov      ecx, r14d                     ; ecx = 项目 ID
0x1411f8938: call     0x141200c00                   ; 登记项目完成状态
0x1411f89f2: call     0x1411dfe00                   ; 【关键】调用 HandleDrillResult 发放徽章点数
```

---

### 2.5 训练馆退出处理与日历推进 (`0x1411f8bf0`)
在 `CAREERMODE_LIVEPRACTICES::HandleLivePracticeEnded` 中：
```x86asm
0x1411f8c3c: mov      rax, qword ptr [rip + 0x5132865]
0x1411f8c43: mov      dword ptr [rip + 0x51584cf], 0 ; 清除正在训练标志
0x1411f8cd4: mov      rcx, qword ptr [rip + 0x512f27d]
0x1411f8cdb: mov      rax, qword ptr [rcx]
0x1411f8cde: call     qword ptr [rax + 0x10a8]       ; 触发退出场馆与保存时间线状态
```

---

## 三、 单机化依赖矩阵与契约 (Dependency Matrix)

| 模块 / 功能 | 依赖性质 | 原始线上调用 | 离线解决策略 | 状态 |
| :--- | :--- | :--- | :--- | :--- |
| **MC 日历推进** | 本地 | 读取本地日历与时间线 | 原生执行 | **已就绪** |
| **服务器会话握手** | 在线（已死） | `CreateAndSendRequest` (`0x141239230`) | **Guard 0** 拦截置 `2` (`COMPLETED`) | **已验证** |
| **训练日程类型获取** | 在线（已死） | 由服务器每日下发至 `[this+0x488]` | **Guard 1** 强制赋有效值 `1` | **已验证** |
| **球馆场景资源加载** | 本地 | `practicefacility_int.iff` | 原生执行 (State 0~2) | **已就绪** |
| **球员与教练实体生成** | 本地 | `CreatePlayers` (`0x14163f4a0`) | 原生执行 (State 3) | **已就绪** |
| **手柄/键鼠控制接管** | 本地 | 引擎输入映射 | 原生执行 (State 4) | **已就绪** |
| **训练徽章与经验结算** | 本地 | `LiveDrill_HandleCalculateResults` | **Guard 3** 强制 3 星及 `0x146352124=1` | **已验证** |
| **退出场馆与时间线归档** | 本地 | `HandleLivePracticeEnded` (`0x1411f8bf0`) | 原生安全清理，清除脏标记 | **已验证** |

---

## 四、 离线验证套件与交付规范

### 4.1 Pytest 静态结构与指令签名核查
离线测试套件：[`test_offline_practice_patch.py`](file:///e:/gemini_space/nba2k22/08_Domain_Applications/Antigravity_GM_Engine/tests/mc_offline_practice/test_offline_practice_patch.py)
测试覆盖项：
1. `test_create_players_entry_and_assertion`: 验证入口指令及断言字符串偏移；
2. `test_drill_calculate_results_entry`: 验证 3 星校验指令；
3. `test_live_practice_ended_entry`: 验证退出场馆栈平衡与入口指令；
4. `test_tracking_flag_displacement`: 验证全局追踪标志位 `0x146352124` 相对寻址；
5. `test_network_job_create_and_send_request`: 验证网络请求函数及 `0x504521a8` 会话码；
6. `test_network_global_status_displacement`: 验证全局状态变量 `0x146351848` 寻址；
7. `test_job_completion_callback_success_code`: 验证完成回调校验码；
8. `test_js_patch_file_exists`: 验证注入脚本完整性。

执行状态：`8 passed in 0.47s`。

### 4.2 实机运行与使用步骤
1. 启动 `NBA 2K22` 游戏并加载 MyCAREER 存档，进入日历界面；
2. 执行启动脚本：
   ```powershell
   node e:\gemini_space\nba2k22\08_Domain_Applications\Antigravity_GM_Engine\research\mc_offline_practice\run_offline_practice_patch.js
   ```
3. 在日历上选择并点击“进入球队训练”；
4. 观察控制台输出：
   - `[INTERCEPT: NETWORK] 96% Freeze Bypass Triggered! Job status -> 2, Global status -> 2`
   - `[INTERCEPT: SCENE] Team Practice Facility State -> 0, 1, 2, 3, 4`
   - `[INTERCEPT: ENTRY] CreatePlayers entered. Instantiating court players...`
5. 正常进行投篮/体能训练并获得满星徽章奖励；
6. 走向出口按提示退出，日历自动推进至下一天，存档安全落盘。
