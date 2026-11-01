# NBA2K22 × REA：本窗口上下文与逆向经验交接

整理日期：2026-10-28。用途：Human在新窗口开始下一项任务前加载本文件，继承本窗口已经完成的研究、操作经验、失败结论、真实能力与证据入口。**这是知识交接，不是自动执行脚本，也不启动下一项游戏实验。**

本文件汇总可审计的经验，不是聊天逐字备份；具体结果以固定提交、原始Evidence和实际运行记录为准。本次整理没有附加游戏、调用游戏函数、改业务内存、推进日期或保存。版本、路径与进程状态分别标注；新任务重新校准易变化项，不能把历史地址当当前地址。

## 0. 新窗口先读这一页的结论

1. REA已经全局安装并实际用于Windows管理员NBA2K22。已验证的主要价值是**有界Frida观察/调用 + 本地PE局部分析 + 原始证据保留**。不要从零重装，不要默认再跑整个游戏Ghidra。
2. 整游戏Ghidra路线曾原始失败一次、三种修复仍失败，约26.6分钟等待；该路线已停止。后来真正跑通业务靠局部PE/元数据、完整调用者和有界实机验证，不依赖整游戏伪代码。
3. 本窗口已先后完成：Overall缓存研究、元数据/成长/资源探索、自建批量与调用fixture、AI机制原型、只读身份守卫纠正、原生教练与交易调用、九域控制接口静态发现，以及新教练字段/球探目标/不等薪资直接交易验证。
4. 最新业务实测候选为 **`7c970db264809ef0c82c978fd13953cdee00fb24` / Draft PR #16**。本文件追加在此基础上；这串SHA固定描述业务实测基线，不会随交接文件发布改变。
5. **外部GM、Coach、Player模型负责分析、协商与决策；执行层提供机制文档，接收明确ID/资产/取值并执行。** 不开发薪资匹配、能力匹配、交易公平性、协商或策略逻辑。当前默认交易直接Process，跳过外围FullCheck；原生Process内部资产身份检查仍存在。
6. **已经成功的交易和球探动作不能因为换窗口、模型报错或缺少旧聊天而重放。** 先读原始回执及独立前后证据；状态不明先只读，不自动再提交。
7. 所有成功只按具体字段/对象/输入组合报告。原生变更、UI、比赛效果、Save/Reload、生产接入、独立审核、master集成是不同状态。

## 1. 工程、分支和资料权威

正式仓库：[chris2gao/Cybernetic_City_State_OS_v2---nba2k22](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22)。本地工作仓库：

```text
C:\Users\gk\Documents\ChatGPT\nba2k22\rea-development-exploration-01
```

该目录本身才是本次Git仓库；父目录`C:\Users\gk\Documents\ChatGPT\nba2k22`不应被默认当仓库。领域根简称`D`：`08_Domain_Applications/Antigravity_GM_Engine/`；领域Run根简称`R`：`01_os/07_content/_runs/`。下文路径中D/R需展开为这两个前缀。

本次整理fresh-read远端master为`7742568ac677b3c16079887463f05e81cb1191ed`，PR16业务头为`7c970db264809ef0c82c978fd13953cdee00fb24`。这是整理时快照，下一窗口须重新读取。最新REA工作不在master里，**从master没找到不能判定成果不存在**。

| 阶段 | 固定来源 / 入口 | 状态与继承方式 |
|---|---|---|
| 初始安装、Overall与通用探索 | `task/rea-development-exploration-01@b16e69727987f29bff5e2ee31ce82891102ab2d9` | 历史综合探索被Human暂停；可继承结果，不自行恢复整套探索 |
| AI机制原型与只读身份纠正 | [PR #10](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/pull/10)，`cfce2c88bcaf38362ff7270242cd982bd9757415` | 原型与局部研究；不是三机制全部破解 |
| 原生动作调用 | [PR #12](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/pull/12)，`f6b2f5deb73218406f034c5418896c4bfade8e64` | 教练防守与旧单换单取得真实效果；Human确认成功并要求结束测试 |
| 九域静态发现 | [PR #14](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/pull/14)，`2bdda79c6513f463252d7d01834218edb590eec9` | 61静态动作、36函数/布局、19种handler、12类部分Reader；该轮无新游戏测试 |
| 新机制实机验证与角色指南 | [PR #16](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/pull/16)，`7c970db264809ef0c82c978fd13953cdee00fb24` | 新增默认直接交易动作后62个动作、38绑定/布局；三类具体新效果及满槽拒绝，等待独立审核 |

这些PR存在依赖链，PR16以PR14发现分支为base；本窗口没有合并master，也没有代替独立模型验收。旧README/知识卡中的“NO_SAFE_PATH”“本轮未运行”是对应阶段的历史结论；其中Coach/交易已有后续进展，不能用旧卡覆盖最新证据。徽章自然成长等未解决项仍保留UNKNOWN。

新窗口加载顺序：fresh master → 根`AGENT_WORKING_DISCIPLINE.md`、`AGENTS.md` → `01_os/README.md`、`01_os/开发入口与单窗口任务规范_v1.md` → 当前Human任务 → 当前任务包 → 本文件和直接有关的证据。不预载所有Run。Core PR8的`OS-EVIDENCE-FEEDBACK-LOOP-01`提供授权范围内方法自由度与反馈分流，不代表可以扩任务目标或凭角色名称取得权限。

## 2. Human已明确的工作方式

- 外挂接管所有球队的GM，以及Coach、Player等角色。角色模型根据外挂取得的数据和外部信息决定WHAT，执行模型说明HOW并执行确定请求。
- 交易由GM模型之间博弈、协商并检查；本层关注执行，不能再擅自增加薪资匹配、估值、接受概率或能力检查。测试中的薪资不匹配无须配平；最新一次不等薪资测试明确要求不用恢复。
- 教练/攻防/训练等需提供“可设什么、所有已知值、已知影响、必要数据和如何执行”的文档。不能用“有一个Setter”替代机制说明，也不能编造胜率/成长公式。
- Human先批准过具体批单，之后明确“全部批准，你可以自行决定”“以后不用询问”。当前已定义范围内可以自主选择方法、修复和收尾，不逐探针重复申请。后续任务按其实际范围和当前场景解释持续授权；**已消费的旧批单不是重复执行授权，本文也不自动启动新实验**。
- 游戏管理员运行，需要同等权限的执行工具。采用标准UAC管理员启动专用脚本；全权限不等于绕过操作系统安全工具。新窗口确认当前进程和存档，不沿用旧PID/绝对地址。
- Human纠正只读身份守卫：STAFF池范围、352步长对齐、核心team_id和字段值域在只读探索中是待证假设，不是硬阻断。实际可读性、有限范围和异常隔离保留。写入/原生调用仍需正确对象、归属、ABI和参数。
- 不做无关开发。缺场景可标DEFERRED；未知可标UNKNOWN。不要用测试数量、JSON数量、减少UNKNOWN数量替代下游可用能力。

## 3. 已装环境和本地入口

| 项目 | 本窗口使用/核对结果 |
|---|---|
| Node | 系统由24.19.0直接升到 **24.22.1**，Human要求不保留旧版本；本次文档整理重新运行`node --version`仍为v24.22.1 |
| REA npm包 | 全局 **rea-agents 6.8.0**；本次直接读包元数据确认，工具目录可见229项 |
| Ghidra / JDK | 历史安装验证为 **Ghidra12.1.4 / Temurin21.0.12.1+1**，官方包SHA校验过；本次未再次启动后端 |
| Ghidra路径 | `C:\Users\gk\.local\share\rea-tools\ghidra_12.1.4_PUBLIC` |
| REA JDK路径 | `C:\Users\gk\.local\share\rea-tools\jdk-21.0.12.1+1` |
| Node / CLI | `C:\Program Files\nodejs\node.exe`；`C:\Users\gk\AppData\Roaming\npm\node_modules\rea-agents\scripts\rea.mjs` |
| 实验Python | `C:\Users\gk\AppData\Local\Python\pythoncore-3.14-64\python.exe`；静态PE辅助使用Capstone |
| REA skill | `C:\Users\gk\.agents\skills\reverse-engineer-anything\SKILL.md`及其runtime/recovery参考；按当前工具schema调用 |
| 安装接入范围 | Codex与Antigravity全局接入；229工具不代表229个可选后端都安装/可用 |

REA注册文件历史位于`C:\Users\gk\.codex\config.toml`与`C:\Users\gk\.gemini\config\mcp_config.json`，已有`.rea.backup`和`.rea-schema.backup`。这里只记录路径，**不要为了恢复上下文读取或导出整份配置/凭据**。

目录传输优化曾设置`REA_MCP_OUTPUT_SCHEMA_PROFILE=off`：tools/list紧凑序列化从3,504,983降到302,346字节，仍229工具；只是减少重复输出schema，服务端校验和输入契约保留。不能将91.37%目录字节减少说成账单token减少91.37%。不要为文档加载擅自改配置。

已有工具可用就直接完成任务，不每次doctor/setup/重装。Skill与npm发布身份可能不同；当前可调用工具schema优先，不能因最新skill提到某功能就假设已装6.8.0支持。历史参考仓库commit`morluto/rea@570abe95f2a35b5c580a5ec2fca90c33d4114bdc`不是本地npm包的同一个身份。

### 3.1 本地证据/scratch目录

共同前缀`C:\Users\gk\Documents\ChatGPT\nba2k22\`：

| 目录 | 用途 |
|---|---|
| `rea-onboarding` | 安装报告、原始整EXE超时、小PE对照、Overall评价、早期资源/fixture探索 |
| `rea-ai-issue9-runtime` | AI机制原型与只读身份调查的私有运行材料 |
| `rea-ai-issue11-runtime` | 原生动作实验私有材料 |
| `rea-native-control-discovery-runtime` | 九域静态发现scratch |
| `rea-native-validation-runtime` | 四批实测、标准管理员启动、保留/审计/发布脚本及受控验证日志 |

当前成果的权威副本在Git中的Run和research；scratch是找精确日志的补充，不把某个外部临时脚本当永久生产入口。新任务创建新证据目录，不覆盖旧label或复用started标记。

## 4. 游戏、模式和最后一次实测状态

固定游戏：`E:\Games\NBA 2K22\NBA2K22.exe`，历史大小83,688,840字节；完整SHA256：

```text
1727ad72085fba39e789ee574fc15aab623ad1651cf6879e95e8cd53b6ffbbf5
```

本窗口场景先是Human报告终极联盟/MyLEAGUE存档已运行约一个月、日历界面、控制步行者；随后明确为可恢复独立测试存档。最近四批PID **10940**、启动UTC **2026-10-28T06:38:23.0486449Z**，仅为历史审计身份；本次整理未查询游戏，不声称它此刻仍在运行。

| 留给Human的最后效果 | 历史已证状态 |
|---|---|
| IND Rick Carlisle防守重点 | 旧原生Apply留为13/PROTECT_PAINT；最新Coach读取仍为13 |
| IND RunPlayTendency | 最新Batch01把90设为55；另外9项已知Coach设置不变 |
| 旧交易 | Jordan Nwora UID9842：MIL→WAS；Anthony Gill UID9879：WAS→MIL |
| 新交易 | Malcolm Brogdon UID7239：IND20→MIL1；Donte DiVincenzo UID7716：MIL1→IND20；两者当前/合同归属都转移 |
| IND球探 | Goal0改为仅Sam Perkins UID33143；Goal1/2保持，总Goal3，次数raw7，Perkins进度raw69 |

没有专门保存、恢复或日期推进；**是否游戏自动保存未观测**。不要宣称“肯定没存盘”，也不要假设重启后这些效果还存在。若新进程/存档与历史不一致，重新读取，不自动“修复回旧测试状态”。

## 5. 选择正确工具路线

| 当前问题 | 优先路线 | 已付过代价的误区 |
|---|---|---|
| 现成Python/JS/SQL架构 | 正常仓库工具 | 不必先跑REA诊断 |
| 字段、有效位、当前实例、代码窗口 | REA/Frida有限读取、双读和逻辑身份 | 元数据定义不是实例值；Frida注入不是外部RPM纯被动读 |
| 已知函数由谁调用、参数/返回 | 有事件上限/时间上限的Interceptor；明确实际场景 | `trace_native_values`是静态依赖，不是live trace；0事件不等于没有调用 |
| 大PE定点定位 | 本地PE字符串/类型注册/RIP引用/`.pdata`/Capstone，再按需live bytes核对 | 辅助反汇编不是Ghidra伪代码，局部xref不是完整调用图 |
| 已恢复业务函数 | 明确ABI、真实对象与线程、私有输入、单次调用、独立回读 | 名称或字段CRC不能证明可调用；不能在Frida工作线程盲调 |
| `.iff`等资源 | 先魔数；确为ZIP再open/inspect/extract/compare | 本机模组存在不等于原版/已加载；容器可读不等于实时渲染注入 |
| 全游戏Ghidra | 当前停用路线 | 不通过更长timeout重复付首次建库成本 |

### 5.1 整游戏Ghidra失败及恢复经验

四次分别：原始330.834秒；期限延长600.824秒；禁入口反汇编+3函数种子330.826秒；同时禁Subroutine References并给code种子330.829秒。后两次线程诊断涉及thunk/Subroutine References。原始一次加三次不同修复均`provider_timeout`，总等待约26.6分钟，已记录全局`C:\Users\gk\.codex\FAILURE_LOG.md`。

小型Windows PE `where.exe`静态分析71.230秒成功；只证明安装与小目标后端有效。Windows P0对裸x64代码片段明确不支持。没有确认OutOfMemoryError，不能把超时改写成确定内存不足。当前适配器close会删除临时Program/project，Evidence bundle不等于可重开的完整Ghidra库。

若将来确需重开，必须有不同的、可验证的可复用导入/局部分析方案；不要原样重试。已成功导入的小目标应在同一分析会话成组查询、导出证据再关闭，避免每个CLI命令重新导入。

模型容量错误、MCP连接断开、宿主deadline、REA provider_timeout、Frida消息错误、进程权限不足是不同故障。宿主超时不证明后台已停止；涉及可能已改变游戏状态的调用，不能因客户端没收到结果就重试。连接恢复按当前skill参考执行，必要时重启客户端；本窗口曾遇到`Selected model is at capacity. Please try a different model.`，已恢复后先核对Git/回执，没有重放业务。

同一失败签名最多三次具体修复，每次要有新证据/新假设/不同补救。三次耗尽后保留证据与问题再继续独立可做的工作；不把一个后端失败说成REA整体不可用。

## 6. 局部PE、元数据和函数资格经验

### 6.1 静态发现的可靠推进顺序

1. 固定完整EXE SHA，复用已有profile、v25布局、注册表、codec和R系列来源；不要把已有算法重新归功于REA。
2. 窄范围精确字符串和命名家族查找；交易早期只查`TRADE::`漏掉核心，扩为`Franchise_Trade_*`才找到共享业务路径。扩大命名假设比整库反编译有效。
3. 查RIP-relative引用、注册initializer和真实调用者；记录范围和命中截断，不把有界搜索未命中说成函数不存在。
4. x64 `.pdata`条目可能只是fragment。跟随UNW_FLAG_CHAININFO，把同一primary的fragment组合，检查实际参数/栈/返回和嵌套call；入口几十字节不足以断定完整函数。
5. 本轮函数恢复上限为primary附近24KiB、最多32 fragment。超限就保留partial，不悄悄扩成整游戏；RET后可能有jump table，Capstone线性解码不保证每字节可执行。
6. ABI、对象所有权、模式分支、真实调用线程、返回约定和后置效果都明确后，才从候选进入可调用计划。固定代码指纹用于防漂移，不能代替语义证据。

复用：`D/research/rea_native_action/pe_local.py`提供Image/hash/section/RVA换算、unwind_chain、instruction_rows；`D/research/rea_native_control/tools/recover_functions.py`生成有界完整fragment证据。Capstone辅助分析不是REA Provider伪代码，来源标签要正确。

### 6.2 元数据中的经验修正

早期模板识别约4,008个注册候选，不等于全游戏类型数。该注册模板实证映射：**r9=类型名、r8=schema、rdx=字段数组、rcx=类型对象**，新构建仍需检查initializer bytes。

当时类型头取count@0、字段表指针@8、schema@32、类型名@40；字段记录40字节，保留原10个word再解释offset/bitwidth。CRC经literal候选匹配，重名/冲突保留候选。结构size/类型码不能无条件当连续可复制长度，指针/数组/基类/子对象另解析。

旧实验实际读取13个结构/21个LEA片段，2.719秒、显式10,880字节；成长9结构2.614秒、9,936字节；呈现5结构2.632秒、23,989字节。它们证明定义/代码窗口，不证明定义对应活实例或代码被执行。

## 7. Frida与管理员进程的实用方法

### 7.1 最短运行形态

已安装CLI可用以下**模板**，PID/path必须由当次任务解析，不照抄：

```text
rea instrument-with-frida attach <fresh-pid> --script-file <reviewed-absolute-js> --duration-ms 500 --format json
```

同等MCP输入历史为`{mode:"attach",pid:<fresh>,source_kind:"file",path:<absolute>,duration_ms:500}`；以新窗口实际schema为准。普通权限MCP不能自动访问管理员游戏，本窗口用标准`Start-Process -Verb RunAs -WindowStyle Hidden`启动专用PowerShell，再运行固定Node/REA路径。进程/构建/脚本SHA核对和结果输出都放在该管理员脚本内。

当前可复用源码：`D/research/rea_native_control/transport.py`、`run_native_program.ps1`、`validation_runtime_identity.ps1`、`validation_batch.py`、`run_validation_batch.ps1`。后端默认不启用，不自动提权、安装、选目标或重试。

`LiveExecutionContext`包含明确范围引用、允许action集合、最大外部游戏调用数、enabled和expected_pid。它是显式运行上下文，不是认证系统，也不意味着需要Human对每次探针重新批准。精确批单保留输入、程序SHA、PID/启动时间、预算、先决读取与异常停止；started文件排他创建，避免误重放。

### 7.2 有限读取和身份假设

- 游戏地址读取前用`Process.findRangeByAddress`逐段检查真实可读性；限定单次、累计字节和遍历条数，异常隔离，输出逻辑ID和所需投影。
- 只读时STAFF池区间/对齐、核心team_id、名字/值域是身份假设，不能封死探索。早期guard拦过教练指针；重查219条TEAM目录发现5条PHI/IND记录，PHI5000/IND5018教练NULL，非核心IND788则可读到David Copelovici候选且反向TEAM一致。核心PHI/IND读到Doc Rivers/Rick Carlisle。
- 该重查10.922秒、显式2,724字节/65,536预算、异常0。原失败地址当时没记录，不能声称精确复原历史指针；也没证明存在可读非空池外对象。名字与互链只是布局证据，原生调用仍严格核对真实对象。
- 读后再读关键头/根/身份以防场景变化，不把一次稳定读当永久身份。Frida内部内存访问不计入脚本显式预算，报告时写清。
- 私有分配是另一类地址：早期C1副本回读把`Memory.alloc`送入游戏range清单检查而失败。修复是对**自己持有且长度已知的分配**按自有边界直接readByteArray；不是放松任何游戏指针检查。

### 7.3 业务函数必须在合适线程执行

不能假定Frida脚本线程可安全调用MyLEAGUE原生业务。当前成功桥位于`runtime/gui_once.js`：

1. `EnumWindows`筛选本进程可见NBA窗口，用`GetWindowThreadProcessId`取得其GUI线程。
2. `Interceptor.attach(user32!PeekMessageA).onLeave`中只在该线程、且一次性invoked标记未置位时执行。
3. 用`PostMessageW(WM_NULL)`唤醒；没有点击菜单或推进日期。
4. 调用前置位invoked，finally detach；未进入线程则4秒截止并detach。最新批次REA会话15秒，累计显式读取上限1MiB。

这证明已测试的业务入口在该线程可用，不证明所有引擎函数都应在GUI线程。Hook会临时改代码/注入代理，不称为完全被动只读。旧900ms、最多12事件的Gameplan索引hook为0事件，仅`NOT_OBSERVED_IN_WINDOW`，不能推出从不调用。

### 7.4 ABI和返回约定不能凭函数名猜

所有下表RVA只适用固定PC22 SHA，参数为Win64。结构/所有权/生命周期仍看Binding和完整调用者。

| 服务 | RVA | 实证ABI/重点 |
|---|---|---|
| Coach Apply | 0x146eaa0 | `void(GAMEPLAN*,COACHDATA*)` |
| AddPlayer / AddPick | 0x12dec20 / 0x12de850 | `int(TRADE*,TEAM* from,TEAM* to,asset*)` |
| Validate | 0x12ec930 | `int(TRADE*)`；基础身份/结构检查 |
| FullCheck | 0x12e1800 | `int(TRADE*,int currentTeamInTrade,context*,int,int,int32*)`；旧路径 |
| 旧提交Wrapper | 0x132b840 | `int(TRADE*,int32*)`；本地FullCheck→Process成功后返回0 |
| 直接Process | 0x12e93b0 | **`int(TRADE*,context*,int32*)`，三个参数，非一个**；非零成功 |
| 交易context Getter | 0xbaa7e0 | `pointer()`；原调用者Getter后把结果放RDX传Process |
| PICK按ID / 反核UID | 0xf3ca00 / 0x947330 | `pointer(uint)` / `uint(PICK*)`；不能猜对象某offset是UID |
| Player按ID | 0xf3f580 | `pointer(uint PLAYER_UID)` |
| 球探Init / SetSpecific / Append | 0x1257560 / 0x1322f30 / 0x1244580 | `void(Goal*)` / `void(Goal*,int,PROSPECT**)` / `int(Trip*,Goal*,TEAM*)` |
| 团队训练 / 取某日训练 | 0x1325f10 / 0x12f1390 | `void(TEAM*,int date,input*)` / `pointer(TEAM*,int date)` |
| 当前pick选择记录 | 0x92a6a0 / 0x92a700 | 常规`pointer(int round,int slot,int tableKind)`；扩展`pointer(int round,int slot)` |
| 选指定新秀 | 0xec9610 | `void(PLAYER*,TEAM*)`，第二参不是PICK |

`0x12e79c0`返回“当前球队是否参与交易”bool，不能误读成球队索引。一个函数返回0成功，另一个返回1成功；不要用统一约定覆盖原调用者。

## 8. 原生结果缺失、证据保留与换窗口恢复

CLI exit0、游戏存活、cleanup_error=null，**都不能单独证明业务成功或原生返回已捕获**。须检查normalized_result.messages中的script error、truncation、native-call-stage和唯一结果消息。当前桥在每次外部游戏call前后发送STARTED/RETURNED，并把“不明状态”作为独立结果。

最关键反例是PR12交易：真实提交整体37.384秒，但原始REA没有任何脚本消息。原生返回、准确调用数、事件回调仍UNKNOWN。没有重试交易；独立新REA只读比对前后，确认Nwora/Gill恰好互换，Human也确认成功。派生效果收据不能补写成缺失的原生返回收据。

最新四批则都有完整消息、独立读取，29次有限附加、14次外部原生调用。外部预算不包含游戏内部嵌套call，也不包含user32技术辅助。四个管理员launcher exit0，无message error/truncation、cleanup_error均null。原始REA snapshot state仍写running，保留原样；CLI/launcher已完整结束，不伪造DETACHED回执。

每次保留：精确request、program.js、目标身份、原始evidence.json、stdout/stderr、started/result、manifest逐文件SHA、退出记录、独立前后值与UNKNOWN。完整大文件落盘，只输出ID/计数/选定字段；Evidence ID存在不代表新窗口已执行或独立复现。

**换窗口后的处理顺序**：读本文件及完成指针 → 查当前branch/head和旧实际收据 → 了解已消费动作与仍留效果 → 加载新任务 → 若新任务需要现场，重新绑定进程/存档/对象 → 准备新批次。不要运行旧launch_standing_batch、旧approval文件或历史started目录来“继续”。

## 9. 具体研究结果与尚未解决的机制

### 9.1 Overall与困难项目

Human指定的[DIFFICULT_ITEMS.md固定交付源](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/blob/a3927fb150a213201e404cca043ced4f57409bd1/08_Domain_Applications/Antigravity_GM_Engine/world_data_prototype/DIFFICULT_ITEMS.md)含Overall、复杂攻防聚合评分、教练历史阶段、战术CRC文字、全生命周期、历史人物、UI单位/舍入等。早期Overall曾HUMAN_DEFERRED，后来Human明确重开有界研究，不能只见旧状态就拒绝。

PLAYERDATA元数据本次匹配963字段、结构1264字节：缓存float32在+364/0x16C（字段索引150、CRC1370230541）；有效位在+796/0x31C bit6（索引334、CRC2166828986）。valid=1返回cache；valid=0走重算0x99b670的结论来自既有getter代码，本窗口**没调用重算**，无效缓存必须UNKNOWN。

6名球员valid均1、前后稳定：Ben Simmons0.866666675、Seth Curry0.779117107、Danny Green0.782149017、Tobias Harris0.854910135、Joel Embiid0.952591836、Andre Drummond0.782066464。复用旧codec的整数候选87/78/78/85/95/78；包含float32乘100及nearest-even假设，未观察实际线程MXCSR，不能宣称舍入独立或全部UI验证。

Human在球队名单确认Ben87，并更正Embiid为**基础95、加成96**；之前96/97误报撤销。两个样本支持基础值解释，不解释加成来源，不证明跨模式/伤病/士气/全名单。两次REA实机观察合计7.924秒，读值1,642字节、元数据38,897字节；没有正式接入生产Reader。

后继最有价值的是“谁生成、谁读取、何时失效/清空/提交”的调用链与显示加成，不是重新造批量读取器。复杂攻防评分、教练年份、CRC文字等仍无完整解决证据。

### 9.2 徽章、导师与自然成长

已见`FRANCHISE_MENTOR::BADGE`的Type/Level/IsActive/Progression/DateLastChecked，MENTOR的持续时间/Compatibility/开始日期/Badges，以及联盟成长调参PhaseFactors、MinCoachEffect、WorkEthicBonus等定义。

CatchAndShoot/CornerSpecialist场上接球时间、距离、防守、bonus等是**比赛触发/效果候选**；不是学会/升级门槛。MyCAREER升级点数/声望解锁不能迁成MyLEAGUE AI自然成长规则。LinkMentor、SetMentors局部代码只支持候选分支，不是完整成长公式、AI调用点或周期。

此机制仍BOUNDED_UNKNOWN，没有自然日期推进/真实升级轨迹，没有可调用的任意徽章Setter。旧Python Native模型和字典Memory模型是fixture，模拟cache_epoch/applied_focus不是发现的游戏字段。

### 9.3 Coach：当前已恢复10项投影

COACHDATA352字节、Gameplan880字节。共享POE字+316，六项5bit：Defense bit0、Defense2 bit5、Defense3 bit10、Offense bit15、Offense2 bit20、Offense3 bit25。必须掩码保留非目标位。旧lookup索引0有效，0xFF缺失；35..254不能盲读35容量数组。

| 字段 | 已恢复选项 |
|---|---|
| POEOffense | 0无偏好，1冲篮筐，2射手空位，3低位，4挡拆，5均衡，6围绕得分手 |
| POEOffense2 | 0无偏好，7耐心，8均衡，9自由出手 |
| POEOffense3 | 0无偏好，10进攻篮板，11均衡，12限制对方转换 |
| POEDefense | 0无偏好，13保护内线，14均衡，15限制外线 |
| POEDefense2 | 0无偏好，16保守，17均衡，18身体对抗 |
| POEDefense3 | 0无偏好，19防守篮板，20均衡，21发动转换 |
| RunPlayTendency / ZoneUsage / BenchUtilization | uint8；历史Human确认UI0..100，分别战术频率/联防频率/替补使用率 |
| BenchDepth | uint8；轮换人数上限含义，UI端点UNKNOWN，测试9/10不是允许域上限 |

当前代码技术编码允许byte0..255，不代表整个区间都获UI意义验证。Apply前复制私有Gameplan、按当前Coach保留其它投影，只改输入，再核对完整352字节预期和原Gameplan不变。当前只闭合三个引用槽均NULL分支。

**命名纠正**：+0x120起三个槽不能称已证“自由战术/playbook”；共享lookup也处理PLAYER UID，现称未定引用对象槽。+0x148 bits17..24的system_proficiency只是旧探针便利标签。非空分支、完整持久Gameplan、Playbook、ACE、比赛消费者、胜率影响尚未闭合。

实测：PR12私有副本/真实14→13/恢复14后，Human另要求留13验看；最新RunPlayTendency90→55另9项不变。当前投影可以应用，不能宣称重新进入编辑器/引擎覆盖/SaveReload后必然保持。Bench设置不等于逐人分钟和首发配置。

### 9.4 交易：旧完整检查路径与当前直接执行

私有FRANCHISE_TRADE为1668字节，18个92字节元素；分配带前后canary。由原生AddPlayer/AddPick生成资产元素，不自己重建估值或修改合同。+8 bit22是IsAIInitiated，bit23是ForceLegalMoney；私有输入设前者、后者不置位。这个标志不证明原版AI自主决策链已经破解。

旧PR12：MIL Nwora9842↔WAS Gill9879，首年均1,517,981，走Validate/FullCheck/Wrapper，提交消息缺失但独立名单/合同归属与Human确认支持效果。其他28队只核了摘要，不宣称完整字节/历史/签权/失败原子性审计。

**当前默认**`gm_trade`→`TRADE_EXECUTE_AGREED_PACKAGE`：确定资产→原生Add→context Getter→直接Process。没有外挂经营检查，也不调用额外Validate/FullCheck/旧Wrapper。Process固有Validate仍可检查资产存在/归属；没有patch引擎代码去去掉它。

最新实测IND Brogdon7239（首年raw21,700,000）↔MIL DiVincenzo7716（4,675,830），Process返回1。独立读取两队恰好换这两人、IND15人/MIL14人保持、两人当前/合同TEAM均转移、六年工资不变；差额17,024,170自然反映在salary_total_raw。没有测试原FullCheck是否会拒绝，因此表述为“不等薪资直接执行成功”，不伪造具体违法规则判定。

输入六键：team_a/team_b、players_a/players_b（UID16数组）、picks_a/picks_b（UID32数组）；A侧给B、B侧给A，球队不同、同资产一次、至少一资产、总≤18。这些是参数/物理规则；不代表薪资/公平性检查。签权UID必须原生Getter反核，不能猜+0x10。多球员、签权、混合包有静态逻辑，未由此次一换一推广成全组合实测。

### 9.5 球探：追加、已有Goal设置、实际考察是三个动作

原生布局：DRAFT_CLASS96,016，最多150候选；DRAFT_PROSPECT640；PerTeamData16；Goal148；Trip960，最多3 Goal、每Goal最多17目标。团队记录36槽、stride0x13e70，Trip=record+0x13aac；按真实team_id匹配记录，PerTeamData按**record index**，不能直接按team_id索引。

SetSpecific输入必须DRAFT_PROSPECT*数组，不能传PLAYER*。当前class pool index压在目标条目低8位；Goal+0x88 flags低3位focus、bits12..19计数，读取时仍保留界限与quality_flags。

Batch02初始化私有Goal→SetSpecific([33143])→Append，因IND3槽已满返回0；独立读取旧三槽指纹、次数7和进度69保持，**这是拒绝**。

Batch03按后续Human范围明确另发`SCOUT_SET_EXISTING_GOAL_TARGETS {team_id:20,goal_index:0,player_ids:[33143]}`，只调用SetSpecific一次；独立确认Goal0从11人变单一Perkins，focus2，其它槽/次数/进度保持。不能偷换成“Append成功”。

已有Goal修改尚未证明Trip聚合缓存即时刷新；0x13191d0会合并但不清旧聚合，不能单调它冒充完整重建。原DoScout会先清聚合再逐Goal重建/消费；0x1261d40是独立消耗次数的业务，本轮未调用。目标记录成功不等于报告解锁、UI显示或考察已完成。

公开候选身份/原始专家排名/原始进度可读；Perkins点数69、workout/medical均false。原始点数、排名字节、是否医疗不等于隐藏能力公开或完整报告。追加1..17目标，已有槽0..2且实际存在；源码允许已有槽空列表0..17，空列表业务意义未实测，不自动清槽。

### 9.6 训练、选秀、签约及其余缺口

训练日输入64字节：input+8的3个float32、+20的3个profile byte、+23的38个subfocus byte、+61的3bit intensity（0..7），原生写56字节daily并设override。单改强度先取该日daily保留其它值。原生可能比赛日/无记录no-op；原生日期键转换、索引语义、UI强度标签未知，不能自动换日期找成功。训练本轮未实测。

选秀当前root+b8/bc/c0为type/round/slot，原生获取当前PICK，反核指定pick_id、owner和+0x10选人槽为空，再`DraftSelect(PLAYER*,TEAM*)`。当前记录存在不证明UI正在选秀；可能推进顺位。日历场景未调用，DEFERRED_NO_SCENE。

签约44字节报价中25字段和部分函数已恢复，但初始化、status/type/flags、Offer→Process完整提交不齐；Offer接受不等于签约。Waive真实八参数含未知标志；内部release helper不是完整裁员服务。Editor Save/Flush依赖全局editor、parent/child buffer和refresh，不是任意属性Setter；父copy超界仍partial。导师manager/数组参数、完整轮换/首发/分钟、Playbook/完整Gameplan提交仍未合格。

九域Reader目录12类均coverage_complete=false；当前Player只输出身份/17合同字段，不是全部属性、倾向、徽章。已有生产v25/Reader可复用，不能因此把本原型接入生产、重新设计数据库或人格系统。

## 10. Fixture、资源和沉浸感探索经验

自建4096条记录批量fixture：apply2.965秒、restore2.810秒，进程自身独立读回均4096/4096，含before负例；证明工具传输/局部恢复，不证明NBA对象索引、并发、原子CAS、业务提交、存盘安全。Native ABI fixture16事件、3.119秒，reader(21)=42、writer(21)=43；不算游戏真实调用点。

本机`Mods/newscorebug.iff`实为ZIP，历史SHA`494ed356b69219ab43bfb69fd4b1d61dc30c24e990ba7ba71a100bbd6d4eb852`；260成员、9SCNE、107UI节点/44SceneText。只证明该模组容器，不概括所有IFF或大0A，不证明当前加载或原版隐藏功能。

REA资源工作流经验：open_binary→inspect_artifact(summary)→inventory分页→extract_artifact→compare/export→close。inventory应使用返回的inventory_evidence_id，不能误用父inspection ID；列名`entry_kind`而非`kind`。当时extract只收integrity policy、输出目录由工具返回，不能捏造destination参数；以当前schema为准。

SCNE是JSON-like，需处理外层花括号、缺失值和尾逗号，记录占位和转换；占位null不是游戏null语义。VCUI仅解析JSON前缀，另24,384字节二进制未知。研究副本只改一处`VC_MinTextScale`，没有整个资源重序列化/部署。

比较显示root+scorebug_intro.SCNE两处changed，其余259 occurrence不变：实际只改一个内部成员，根容器哈希随之改变，不是两个内部文件修改。原EXE、模组、素材、改后IFF不上传Git，只存脚本/清单/哈希/Evidence。

呈现索引16个检索家族有交叉，字符串数量不是功能数量。认定“原有但关闭”还要模式/平台匹配、资源依赖、代码可达、开关实例和实际场景调用，排除旧版残留。实时注入文字还需编码/容量、对象所有权、线程、消费者、渲染反馈和退出恢复。半场/采访/更衣室、隐藏内容总数、实时信息注入均UNKNOWN；本窗口只有日历场景，没有这些比赛效果。

## 11. 当前代码、证据和用量索引

### 11.1 优先读取的当前文件

- [角色模型机制指南](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/blob/7c970db264809ef0c82c978fd13953cdee00fb24/08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_control/ROLE_MODEL_MECHANISM_GUIDE.md)：外部模型的字段、值、影响、输入JSON和执行分工。
- [实机验证报告](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/blob/7c970db264809ef0c82c978fd13953cdee00fb24/08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_control/VALIDATION_RESULTS.md)：最新三个效果、拒绝、原始证据与未验证轴。
- [动作覆盖表](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/blob/7c970db264809ef0c82c978fd13953cdee00fb24/08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_control/ACTION_SURFACE.md)：静态基线与新增直接交易路径；配合[data/native_live_validation.json](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/blob/7c970db264809ef0c82c978fd13953cdee00fb24/08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_control/data/native_live_validation.json)的逐例覆盖。
- [当前README](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/blob/7c970db264809ef0c82c978fd13953cdee00fb24/08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_control/README.md)、`contracts.py`、`registry.py`、`facade.py`、`runtime_codegen.py`：准备/渲染/单次dispatch，默认inert，不能仅有方法名就宣布可调用。
- `runtime/common.js`：有限读取、fresh roots/team/prospect解析、代码指纹、call budget和分阶段消息。
- `validation_batch.py`：prepare不碰游戏；exact-script transport、PID/启动绑定、排他case、一次效果及独立读取。**旧prepared/approval文件用于审计，不用于新任务执行**。
- `tools/audit_live_observations.py --check`：只读核对保留真实观察、所有文件SHA、Git blob、请求/调用和独立效果，不附加游戏。

### 11.2 精确历史入口

| 问题 | 固定入口 |
|---|---|
| 初始工具完整手册 | [b16e6972 / REA_DEVELOPMENT_PLAYBOOK_V1](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/blob/b16e69727987f29bff5e2ee31ce82891102ab2d9/08_Domain_Applications/Antigravity_GM_Engine/docs/development/REA_DEVELOPMENT_PLAYBOOK_V1.md) |
| 初始52项证据 | 同commit：`R/run-20261027-rea-development-exploration-01/06_执行/evidence/SOURCE_MANIFEST.json`；该轮README与PLANNING_HANDOFF |
| 原型/身份纠正/徽章 | `D/research/rea_ai_prototype/README.md`、`dossiers/M1_BADGE.md`、M2_COACH.md、M3_TRADE.md；`R/run-20261027-nba2k22-rea-ai-prototype-exploration-001/` |
| 原生首调用与旧交易缺收据 | `D/research/rea_native_action/REPORT_20261027.md`、README、action_atlas及evidence/manifest、extension_manifest；`R/run-20261027-nba2k22-rea-native-ai-action-invocation-001/` |
| 九域完整静态逻辑 | `D/research/rea_native_control/DISCOVERY_NOTES.md`、data/native_bindings.json、read_catalog.json；`R/run-20261027-nba2k22-myleague-native-control-discovery-001/` |
| 最新实际业务验证 | `R/run-20261027-nba2k22-myleague-native-control-validation-001/08_结论/COMPLETION.md`、REQUIREMENTS_AUDIT；07_测试执行/batch-01..04及LIVE_OUTCOME_AUDIT.json |
| 最新Human职责/授权修订 | 同validation Run的`01_任务输入/HUMAN_EXECUTION_ONLY_SCOPE_UPDATE.md`，03_方案设计/HUMAN_APPROVAL_BATCH_01/02.md及IMPLEMENTATION_DECISIONS.md |
| A/B阶段讨论的来源边界 | `R/run-20261027-nba2k22-rea-native-mechanism-consensus-001/`，只按当前问题读具体文件；旧候选/冻结版本不改写 |

初始手册不在当前PR16工作树中，但固定Git commit可`git show <sha>:<path>`读取，或使用上方固定在线链接。不要因某文件不在当前目录而创建伪副本或认定它不存在。

安装/Overall仅本地的第一手报告：`rea-onboarding/REA_INSTALLATION_AND_TEST_20261027.md`、`evaluation-20261027/REA_DIFFICULT_ITEMS_EVALUATION_20261027.md`；主要发现也在b16旧Run中归档。

### 11.3 最新四批精确预算与来源

| 批次 | Manifest SHA256 | 会话/外部游戏call | 实际内容 |
|---|---|---|---|
| 01 | b6074763b5260c5ac6e30a454ecb6a8a832853ec6f1afb964ea0ee3b10f4d8a8 | 6/1 | 新Coach字段及只读 |
| 02 | 7c7d45475ded7bd5a72b24b986baf5a00424b26a9c32bcb166f5804b365ed4f6 | 7/4 | Player Getter一次，球探Init/Specific/Append三次，被拒绝 |
| 03 | 2e41c4ca36a733e55e7fc5e3b635dab11a48820f7ed3e85a19ad57d2088fdd91 | 7/1 | 两队只读与Goal0设置 |
| 04 | 1c037007c0fd6ad0881e6b6f5b450048a41e0abf32df4b08c8ca33deef4114d7 | 9/8 | 四次Player Getter、AddPlayer两次、context与Process各一次 |

Coach实际证据`ev_fdcd36d4e4bca9a380d8ad3622943f0c6c5b2c12fac332e59037a92a0536ad26`，独立读`ev_0b3698af41a6a33fdaeeefb4e519d4579024bb616b918266bea25978ad6321e4`；Goal设置`ev_c71c0d11cd9dbc166e91d8e2057247191e21c5253b15803ad26761dd41018c97`、独立读`ev_698eda52debf62935fee6319bfecba3a204030eb31186aad6c09b564d4aa9a9a`；新交易`ev_51940f985b1457dc16c9658ba2b2fecc57030d49ed27cd7470e7fff8a896f781`，四份独立后读见LIVE_OUTCOME_AUDIT。

PR16业务候选7c970db2的Managed Run/Inspect两检查success；本地完整日志`rea-native-validation-runtime/managed-final-7c970db2`。这只验证声明的源码与保留实机观察，不是独立审核。新文档发布的候选校验另存新Run，不覆盖旧收据。

历史PR12新增10条REA操作共119.107秒，其中私有提案13.391秒、完整检查9.771秒、提交37.384秒、独立回查9.580秒、最后Coach10.685秒；是工具整体耗时，不是纯引擎时间。没有可靠的REA单次token/货币费用拆分，不能用秒数、响应字节或本地后端推算账单。后续成本试验分别统计首次启动/导入、查询、附加/观察/清理、模型解读；不把任务耗在虚构额度计算。

## 12. 文本、发布与证据文件的工程教训

- Windows输出用`python -X utf8`，JSON/Markdown显式UTF-8；PowerShell有时写BOM，读取原始JSON用utf-8-sig。包含中文的脚本/路径尤其不要依赖默认编码。
- 多行逻辑写脚本文件，别塞进长`-Command`/`-c`；Shell quoting错误会放大输出。不要把JSON.stringify当shell转义，不用常见系统变量名当临时变量。
- `rg`按确切目录/文件/命中上限查；Git先status -sb、diff --stat、log -n。大REA图和所有原始Evidence留盘，模型只读所需片段；不要重复吞全部日志或tools/list。
- 私有输入、原始证据、派生分析分别保留，跨来源不要把同一作者的manifest/findings重复算独立实证。导出不要含EXE、存档、模组资产、绝对运行时地址或凭据。
- **真实发生的发布错误**：Batch03/04准备文件首次Git入库CRLF→LF，工作树审计通过但Git blob与原脚本SHA不符。后加`** -text`不会自动重入旧索引。已只对两个准备目录`git add --renormalize`恢复原始执行字节，提交7c970db2；没改raw/哈希，没重跑游戏。现在审计同时检查工作树及`git show HEAD:path`字节SHA。细节在原validation Run `07_测试执行/PUBLICATION_BYTE_REPAIR.md`。
- 不使用force push、不重写旧PR或原始记录。任务分支正常commit/push与Draft PR属于收尾；master合并另行处理。PR已创建要attach到当前聊天。
- 仓库受控检查需绑定最终精确候选，实际`managed_verify.py run`后同候选`inspect`；通过什么写什么。文档跟进不重跑游戏。不要把一次旧检查套到新HEAD，也不要因诊断失败丢掉完整日志。

## 13. 下一窗口的最小起步材料与模板

加载本文件后，下一窗口应能准确回述：角色层与执行层分工、当前三个新效果与旧交易、停止的整Ghidra路线、目前未知机制、当前分支/证据身份，以及业务提交不能重放。**在Human发下一任务前，只恢复知识和报告就绪，不自行挑一个新探索方向。**

新任务真正需要的输入通常是：具体机制和资料、目标模式/页面/对象、预期可调项或待验证假设、当前测试存档/恢复条件、允许的状态变化。已有委托和执行权不要反复询问；只有实际缺少且无法从现有证据得出的信息才问，继续不依赖答案的独立工作。

可直接复制给新窗口的加载提示：

> 请先读取《REA_WINDOW_CONTEXT_HANDOFF_20261028.md》全文，并按其中引用的固定来源恢复本窗口REA上下文。当前阶段仅加载知识，不重跑任何历史游戏批次；先fresh-read仓库状态，区分master与PR候选。继承外部GM/Coach/Player负责决策、执行层负责机制文档和确定参数执行的分工。不要重装已可用REA，不重启耗尽预算的整游戏Ghidra路线，不将fixture/元数据/局部静态/原生效果/UI/SaveReload混为完成。完成加载后简述已知能力、关键经验和未知，等待我提供下一份有界任务及资料。新任务到来后按已授予范围自主完成，不重复请求例行许可。

本文件是Human手动转交的上下文资料，不是跨端点自动消息，没有自动派发、后台调度或其它模型已接收的含义。
