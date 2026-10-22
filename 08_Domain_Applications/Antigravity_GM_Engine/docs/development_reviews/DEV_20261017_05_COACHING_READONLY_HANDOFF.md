# DEV-20261017-05：Codex 原生代码与实时内存只读调研交接（玩家转述）

- 收录日期：2026-10-17
- 文档性质：`USER_RELAYED_CODEX_READ_ONLY_FINDINGS`。玩家将 Codex 在另一个窗口里的完整调查摘要贴入开发规划基线。
- **证据级别边界**：本报告记录该摘要供后续研发使用，**Web GPT 没有拿到调查脚本、原生反编译注释、抓包、测试日志或截图，也没有独立复核游戏进程**。Codex开发时须在当前进程重新定位并记录验证证据；不能把此文件当作已经完成安全写入/游戏效果验收。
- 开发任务：[DEV_20261017_06_COACHING_IMPLEMENTATION_V1.md](../development_tasks/DEV_20261017_06_COACHING_IMPLEMENTATION_V1.md)
- 本次无任何正式存档写入、无自动比赛推进、无游戏数据发布。

## A. 关键纠错（最高安全级别）

旧`src/strategy_manager.py`将`TEAM+0xEB2`等作为POE枚举处理不可靠；Codex据原生代码称`+0xEB2`在访问路径中被读取、递增并写回，像计数处理。**不能再用该偏移做战术写入**。需要查`src/bootstrap_new_game.py`中对`StrategyManager.set_team_strategy()`的调用。正式新编码以前阻断旧writer和相关初始化调用，不要让`--approve-game-writes`间接触发旧错误路径。票价逻辑独立保留。

## B. 默认教练六项POE，COACHDATA + 0x13C

原生字段表、CRC32匹配和进程枚举由Codex调查摘要报告。**32-bit共享小端位域，每项5bits，bits30..31保留，不得修改**。

| 原生字段 | 起始bit | 精确允许原生值（0为NO_PREFERENCE） |
| --- | ---: | --- |
| `POEDefense` | 0 | 0,13,14,15 |
| `POEDefense2` | 5 | 0,16,17,18 |
| `POEDefense3` | 10 | 0,19,20,21 |
| `POEOffense` | 15 | 0,1,2,3,4,5,6 |
| `POEOffense2` | 20 | 0,7,8,9 |
| `POEOffense3` | 25 | 0,10,11,12 |

原生含如GET_SHOOTERS_OPEN、PICK_AND_ROLL_OFFENSE、PATIENT_OFFENSE、PROTECT_PAINT、PLAY_PHYSICAL、RUN_IN_TRANSITION，**只收录确定有源码/原生枚举映射的名称**，不能自造每个数字的中文释义。用户报告目前30队主教练读出中性默认组合；该事实仅该时刻/该存档。

## C. 独立 Sim 数值设置和教练滑块

- `SimPace`：VERY_LOW/LOW/AVERAGE/HIGH/VERY_HIGH。
- `SimPress`、`SimHelpDef`、`SimOffReb`、`SimDefReb`：LOW/AVERAGE/HIGH。
- 这些存在于教练`+0xF4`附近**其他共享位域**；报告中无各字段精确start_bit/width，不能凭名字和偏移直接写。
- `BenchDepth +0xDE`、`RunPlayTendency +0xE0`、`ZoneUsage +0xE2`、`BenchUtilization +0x138`。
- `Tempo`、`HelpDefense`在`+0x148`共享位域；精确bit布局需要实际内存profile。
- `PreferredSystem`、`ActiveSystem`有八类原生体系，不能通过直接提高`System Proficiency`改变球队或球员能力。

## D. 战术本和对手独立Gameplan

- 教练字段`PlaybookID`，Gameplan字段`PlaybookId`是两条独立引用。
- 当前进程加载84本战术本，每本结构大小`0x168`，名称、ID、68个按用途排列的战术CRC槽；**84是本次加载目录计数，不是永久上限**。书本ID必须在当前加载表中存在，CRC源对象需校验。
- `FRANCHISE_GAMEPLAN_MANAGER`+`GAMEPLAN`有有效对象。玩家报告：联盟根来自`NBA2K22.exe + 0x632B478`所指向的原生访问路径；每队结构从联盟根`+0x19CFD0`开始，步长`0x13E70`，**必须依实际球队ID字段遍历映射，不能team ID当下标**。这里的偏移都只是该代码版本的重新定位线索，需每PID复验指针链。
- 每队Gameplan管理器容量35，记录`0x370`字节，当前每队29条有效针对其他NBA球队记录，总`30×29=870`；剩余容量槽不可认为是有效对手记录。
- 指定对手记录内六项POE字段`+0x17E..+0x183`（由摘要标示为6个位置；**不要假设与教练32bit共享bit域同编码，先验证Gameplan是否逐字段byte存储**）；滑块`+0x184..+0x189`；Playbook/Freelance分别`+0x18A`、`+0x18B`。
- 所有针对对手Gameplan的`IsInUse`目前均为0！**仅修改记录并不证明真正启用。** 未验证启用语义、有效触发及回退时，正式执行器该模块应仅只读/预案输出，不写该开关也不声明生效。
- 球员轮换对象含PlayerId/RotationSpot/PlayingTime和高级轮换；球员runtime slot不等于跨存档身份。
- 具体防守设置另有8字节位域、18个设置，原生含OnBall/OffBall、ScreenDefenseOnBall/ScreenDefenseHedge(独立字段)、Force Direction、Post、内外DoubleTeam、Switch、Stay Attached、Pre Rotate等；`OnBallPressure`有效选项AUTO/GAP/MODERATE/TIGHT/SMOTHER。**报告未给18字段完整位位置/掩码，开发该模块写入前必须补齐**。

## E. 进程与证据新鲜度

调查原进程PID9960→重启PID992，原生根路径重定位后读到关键结构。玩家报告在PID992中步行者POE块`0x7FF4E6C2304C`，勇士`0x7FF4E6C23E0C`；**这些绝对地址仅是历史观测，绝不可硬编码入业务程序、正式存档或新PID**。

结论：可推进**正式受控代码开发**，但需要Codex工程初始阶段重新确认本次调查的具体base/field/width/enum表和相关符号，开展必要的隔离存档安全写入验证；不需要Codex先模拟整个月或20/100场比较胜率。比赛效果由玩家实际推进一个游戏月后通过前后同一批次口径比较。
