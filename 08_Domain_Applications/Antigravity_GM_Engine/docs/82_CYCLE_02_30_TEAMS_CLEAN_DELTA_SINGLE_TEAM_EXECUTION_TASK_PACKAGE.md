# 🚀 NBA 2K22 全联盟 30 队纯增量独立执行文件修改执行任务数据包
# (Cycle 02 30-Team Clean Delta Single-Team Native Live Execution Task Package)

> **任务标识 (Task ID)**: `TASK-NBA2K22-30-TEAMS-CLEAN-DELTA-EXECUTION-READY`  
> **所属业务周期**: `season_2021_2022_cycle_02` (2021-2022 赛季全维度战术与攻防博弈干净纯增量单队落地)  
> **审核闭环状态**: **已通过 OS Loop 闭环自愈核验 (3031 项数值交叉比对，100.0% 完美收敛，0 差异)**  
> **派单角色**: `role-planner` / `decision_architecture` (规划决策架构)  
> **受派角色**: `role-developer` / `batch_executor` (修改执行模型 / 数据注入端点)  
> **关联标准**: [`43_FULL_DIMENSIONAL_NATIVE_MOD_PROTOCOL_V2.md`](file:///E:/workspace/Cybernetic_City_State_OS_v2%20-%20nba2k22/08_Domain_Applications/Antigravity_GM_Engine/docs/43_FULL_DIMENSIONAL_NATIVE_MOD_PROTOCOL_V2.md) 与 [`49_NBA2K22_TACTICAL_SYSTEM_AND_GAME_THEORETIC_TUNING_STANDARD.md`](file:///E:/workspace/Cybernetic_City_State_OS_v2%20-%20nba2k22/08_Domain_Applications/Antigravity_GM_Engine/docs/49_NBA2K22_TACTICAL_SYSTEM_AND_GAME_THEORETIC_TUNING_STANDARD.md)  
> **代码基线**: `task/nba2k22-v2-full-dimensional-realism-rebalance` (Commit: `aa566a6e`)  
> **目标生涯存档**: `MyLEAGUE0005` (已恢复至交易后干净无污染底档)  
> **目标数据库**: `C:\nba2k22\saves\MyLEAGUE0005\league_state.sqlite`  

---

## 一、 生成文件存放绝对路径 (File Locations)

全联盟 30 支球队的纯增量单队执行文件均已双向镜像持久化，执行模型可从以下任意目录直接读取：

### 1. 运行环境导出目录（执行模型推荐优先读取路径）
* **绝对路径**: `C:\nba2k22\exports\single_team_execution\`
* **文件清单 (共 30 份单队 JSON，单文件仅 19~27 KB)**:
  ```text
  00_PHI_native_mod.json    08_MEM_native_mod.json    16_ORL_native_mod.json    24_OKC_native_mod.json
  01_MIL_native_mod.json    09_ATL_native_mod.json    17_DAL_native_mod.json    25_SAS_native_mod.json
  02_WAS_native_mod.json    10_MIA_native_mod.json    18_BKN_native_mod.json    26_PHX_native_mod.json
  03_CHI_native_mod.json    11_NOP_native_mod.json    19_DEN_native_mod.json    27_MIN_native_mod.json
  04_CLE_native_mod.json    12_UTA_native_mod.json    20_IND_native_mod.json    28_POR_native_mod.json
  05_BOS_native_mod.json    13_SAC_native_mod.json    21_DET_native_mod.json    29_GSW_native_mod.json
  06_LAC_native_mod.json    14_NYK_native_mod.json    22_TOR_native_mod.json    31_CHA_native_mod.json
  15_LAL_native_mod.json    23_HOU_native_mod.json
  ```
* **关联核验文档**:
  * 审计报告: `C:\nba2k22\exports\single_team_execution\30_TEAMS_CLEAN_DELTA_AUDIT_REPORT.md`
  * 闭环回执: `C:\nba2k22\exports\single_team_execution\30_TEAMS_CLEAN_DELTA_VERIFICATION_RECEIPT.json`

### 2. 本地 Git 工作区目录
* **绝对路径**: `08_Domain_Applications/Antigravity_GM_Engine/database/tactics/single_team_execution/`
* 与上述导出目录保持 100% 同步镜像。

---

## 二、 执行模型操作规范与触发命令 (Execution Instructions)

执行模型可根据当前环境（游戏是否在前台运行）选择以下执行方式：

### 方式 1：单队独立执行 (逐队注入，推荐用于精细核验)
执行模型每次只处理一队，例如执行印第安纳步行者（IND）或费城76人（PHI）：

* **实机内存热注入 (游戏运行在前台 MyLEAGUE 主界面)**:
  ```powershell
  python 08_Domain_Applications/Antigravity_GM_Engine/src/inject_season_cycle_rebalance.py --spec-path "C:\nba2k22\exports\single_team_execution\20_IND_native_mod.json" --commit
  ```
* **底层数据库离线注入 (无论游戏是否运行均可直接写入)**:
  ```powershell
  python 08_Domain_Applications/Antigravity_GM_Engine/src/inject_season_cycle_to_sqlite.py --spec-path "C:\nba2k22\exports\single_team_execution\20_IND_native_mod.json" --commit
  ```

---

### 方式 2：全联盟 30 队流水线一次性执行 (自动化批处理)
执行引擎已原生支持传入整个文件夹路径，引擎将自动按 `00_PHI` 至 `31_CHA` 的顺序依次遍历 30 队执行：

* **实机内存热注入 (挂接运行中的 NBA2K22.exe)**:
  ```powershell
  python 08_Domain_Applications/Antigravity_GM_Engine/src/inject_season_cycle_rebalance.py --spec-path "C:\nba2k22\exports\single_team_execution" --commit
  ```
* **底层数据库离线注入 (写入 league_state.sqlite 并自动创建前置快照)**:
  ```powershell
  python 08_Domain_Applications/Antigravity_GM_Engine/src/inject_season_cycle_to_sqlite.py --spec-path "C:\nba2k22\exports\single_team_execution" --commit
  ```

---

## 三、 执行前置安全守则 (Preflight Guard Rules)

执行模型在执行修改前，必须确认以下铁律：
1. **底档干净确认**: 确保当前存档是刚刚完成现实交易（西蒙斯在篮网、哈登在76人）的纯净底档，未受到旧版全员 99 占位数值污染；
2. **0x90 外观指针保留**: 写入引擎已内建硬性守卫，绝对保留所有球员 `0x90` 处的 64 位指针，严防身材畸形与游戏闪退；
3. **教练菜单关闭守则**: 实机内存热注入时，确保游戏画面停留在 MyLEAGUE 大厅或日历界面，严禁在“教练战术面板/轮换滑条”子界面执行，避免退出菜单被 UI 临时缓存反向覆写；
4. **内存写入后触发存盘**: 实机热写入完成后，在游戏内按日期向前模拟 1 天或手动保存存档，触发游戏引擎将内存数据刷入本地物理存盘文件。

---

## 四、 核心球员重点核验基线 (Ground-Truth Spot Checks)

执行完成后，执行模型可通过回读核验以下 3 大核心标志位，确保注入绝对准确：
* **步行者 泰瑞斯·哈利伯顿 (Slot 2)**: 触球 `84`，**分球 `90` (严禁出现 99)**，战术纪律 `88`，顺外弹 `0`，三分 `85`，推进特权 `1`，战术类型 `[4, 5, 14, 12]`；
* **篮网 本·西蒙斯 (Slot 10)**: 触球 `50`，出球 `90`，顺外弹 `90`，战术纪律 `90`，推进特权 `1`，战术类型 `[13, 7, 11, 4]`；
* **76人 詹姆斯·哈登 (Slot 12)**: 触球 `82`，分球 `95`，推进特权 `1`，高位挡拆支配大核。
