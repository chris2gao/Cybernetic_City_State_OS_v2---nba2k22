# REA 开发使用手册 V1 — 阶段性研究稿

**2026-10-27；状态：Human 已暂停探索，本文仅整理已发生的实验，供下一轮规划使用。不是完整探索结案、独立验收、生产接口或游戏修改许可。** 后续任务以 Human 新提供的边界及游戏资料为准。

研究分支：`task/rea-development-exploration-01`；起点 master：`7742568ac677b3c16079887463f05e81cb1191ed`。领域根为 `08_Domain_Applications/Antigravity_GM_Engine/`。运行证据根为 `01_os/07_content/_runs/run-20261027-rea-development-exploration-01/`（下称 RUN）。

## 1. 新 Codex 从哪里开始

1. 按当前仓库 OS 入口启动，fresh-read 远端 master。本文的固定 SHA 只用于溯源。
2. 先读 [规划交接](../../../../01_os/07_content/_runs/run-20261027-rea-development-exploration-01/08_结论/PLANNING_HANDOFF.md)，再按问题打开 RUN 的具体证据；不预载全部历史。
3. 工具用法看本文；实验脚本看 [研究目录](../../research/rea_development/README.md)。实际 MCP 输入契约在 RUN `06_执行/evidence/rea-tool-contracts.json`，对应 REA **6.8.0、229 工具**。版本变化时以当前 tools/list 为准。
4. 开始新的运行实验前，加载该轮任务包、当前进程/模块/构建和读写范围。旧 PID、绝对地址、状态或本轮运行许可不能代替新绑定。

已装环境为 Node 24.22.1、REA 6.8.0、Ghidra 12.1.4、JDK21。229 个工具是目录数量，不证明各平台后端均可用。当前 Windows 实测通过 Frida 和 ZIP 资源链路；大游戏 Ghidra 路线失败。已有注册可用时直接使用，不必每次重跑 doctor、setup 或重装。

## 2. 对应项目三阶段

Human 本轮提出的三阶段是开发顺序；仓库的五层架构和“采集→分析→Coach→Player→GM→审批执行”六步业务循环仍可并存，不能互相替代。

| 开发阶段 | REA 可以承担的工作 | 本轮支持程度 |
| --- | --- | --- |
| 一：整理游戏数据信息、形成增删改查能力 | 字段布局、有效位、原生枚举、getter/code 字节核对、身份/快照前后稳定性；形成带来源的字段候选 | 当前元数据和 Overall 样本通过；不等于完整 CRUD，新增/删除对象仍需原生分配器和索引生命周期 |
| 二：成千上万条批量底层执行 | 有界进程内脚本、整批 before 校验、批量写后回读、失败恢复、低开销事件捕获 | 4,096 条自建记录真实写入和恢复通过；游戏批量写入未测试，不证明事务原子性、合法性、提交或存档持久化 |
| 三：GM/球员/教练人格使用真实游戏机制 | 给角色提供实测事实、动作前提、反馈和未知状态；用原生观察核对外部动作回执；调查呈现接点 | 工具能支持桥接研究；没有开发人格系统，也没有把角色意图直接变成任意内存写入 |

基础知识入口：[开发基线](NBA2K22_PROJECT_DEVELOPMENT_BASELINE_V1.md)、[既有路线图](OS_GOVERNED_NEXT_STAGE_ROADMAP_20261022.md)、[项目级协作V2](MULTI_MODEL_TASK_OWNERSHIP_AND_VERIFICATION_V2.md)。第一阶段 v25 等交付候选不在本轮 master 中时，应按精确提交读取，不把候选当已接入主线。

## 3. 选择工具，而不是默认整包反编译

| 问题 | 首选路线 | 当前限制 |
| --- | --- | --- |
| 现成源码/SQLite/普通架构 | 正常代码、SQL 和仓库工具 | 不需要 REA 健康检查 |
| 当前字段定义、缓存、代码窗口 | `instrument_with_frida`，或显式 Frida session | 管理员游戏要求同等权限；Frida 会注入代理 |
| 谁调用已知函数、参数和返回 | 有界 Frida `Interceptor.attach`，先自建 fixture 验证 | 本轮仅自建 native-ABI 回调验证；没有对游戏设置 hook，不保证未知 ABI 安全 |
| 大 EXE 局部定位 | 离线 PE 字符串、注册模板、`.pdata` 与 Capstone，随后 REA 核对 live bytes | 辅助脚本不是 REA 伪代码；RIP-relative LEA 和 unwind 范围只是局部覆盖 |
| `.iff` 等资源容器 | 先看文件魔数；可识别 ZIP 时 `open_binary → inspect_artifact` | 本轮只证实本机模组 newscorebug.iff；不能概括所有 IFF 或 0A 等大容器 |
| 资源清单/安全解包/版本变化 | `inspect_analysis_view`、`extract_artifact`、`compare_artifacts` | 资源关系不证明引擎加载或画面效果 |
| 全游戏 Ghidra 调用链 | 本轮暂停该路线 | 原始及三次不同修复均超时；不得无新证据重复建库 |

`trace_native_values` 是静态依赖跟踪，不是实时值。macOS native UI/LLDB、Linux GDB/Rizin、抓包等平台工具不能因在目录中出现就认定 Windows 可用。本任务没有为这些后端安装或启用运行时。

## 4. 最短可复用流程

### 4.1 管理员游戏只读观察

脚本入口：`research/rea_development/invoke_game_probe.ps1`。它核对管理员身份、唯一游戏进程、路径、固定 SHA256、脚本哈希，并拒绝覆盖已有证据标签。

本轮固定游戏：`E:/Games/NBA 2K22/NBA2K22.exe`，SHA256 `1727ad72085fba39e789ee574fc15aab623ad1651cf6879e95e8cd53b6ffbbf5`。构建变化时先停止，重新推导配置，不调整校验来绕过差异。

在已获该轮管理员观察授权的 PowerShell 中，命令形式为：

```powershell
& .\08_Domain_Applications\Antigravity_GM_Engine\research\rea_development\invoke_game_probe.ps1 -Script '<审阅后的绝对JS路径>' -OutputDirectory '<新的证据目录>' -Tag '<新的唯一标签>' -DurationMs 500
```

REA CLI 核心调用为：

```text
rea instrument-with-frida attach <fresh-pid> --script-file <absolute-js> --duration-ms 500 --format json
```

等价 MCP 输入（需运行 MCP 的进程自身具备访问权限）：

```json
{"mode":"attach","pid":1234,"source_kind":"file","path":"C:/reviewed/probe.js","duration_ms":500}
```

这里的 PID、文件路径都是占位符。普通权限 MCP 不能因为游戏已运行就自动获得管理员权限；本轮使用提权后的固定脚本运行 CLI。脚本的关键字检查只是防误用，**不是 JavaScript 安全沙箱**。

每次声明目标、预算、预期、失败信号和停止条件；先验证布局再读值；双读类型头/根/描述符和目标字段检查稳定性；输出所需投影。检查 `messages` 中的脚本 error，不能只看 CLI exit=0；核对 `cleanup_error=null` 和目标仍存活。显式字节预算不包含 Frida 自身访问。

### 4.2 有界元数据读取

`discover_native_seams.py` 在固定 EXE 中识别注册模板；`build_metadata_probe.py` 生成 `metadata/growth/presentation` 三种只读观察脚本；`decode_metadata.py` 把当前元数据 CRC 与离线 literal 候选匹配。

本轮识别了 4,008 个模板注册候选，但只选择部分结构核对。不能把模板匹配数量当作全部类型或已实现功能数量。重要修正：该模板参数映射是 **r9=类型名、r8=schema、rdx=字段数组、rcx=类型对象**；应以当前 initializer bytes 再确认。

类型头本轮读取 count@0、字段表指针@8、schema指针@32、类型名指针@40；结构字段记录40字节。保留原始10个word；offset、位宽等解释附来源。元数据中的 size/type 信息**不能无条件当连续可复制字节数**：指针、数组、基类和嵌套对象要另外解释。CRC 有歧义时保留全部候选，不按名字猜值。

```text
python -X utf8 research/rea_development/discover_native_seams.py --out <scratch>
python -X utf8 research/rea_development/build_metadata_probe.py --source <scratch>/native-seams.json --out <scratch> --mode growth
python -X utf8 research/rea_development/decode_metadata.py --dir <scratch> --tag growth
```

这些路径相对领域根。先离线生成并审阅 JS，再运行上一节的管理员入口。本轮读的是类型定义，不是调参实例或球员私有值；读到字段名不代表已读到实际机制数值。

### 4.3 资源容器

本机 `Mods/newscorebug.iff` 的 ZIP SHA256 为 `494ed356b69219ab43bfb69fd4b1d61dc30c24e990ba7ba71a100bbd6d4eb852`。没有证明该模组当前加载，也不把它当原版内容。

```text
open_binary {path: <iff-path>}
inspect_artifact {detail: "summary"}
inspect_analysis_view {
  source: {kind: "retained-evidence", evidence_id: <inventory-evidence-id>},
  view: {kind: "inventory", collection: "occurrences", offset: 0, limit: 20,
         fields: ["logical_path", "entry_kind", "declared_size"]}
}
extract_artifact {}
export_evidence_bundle {path: <new-json-path>}
close_binary {}
```

summary 的 parent inspection ID 与 `inventory_evidence_ids` 有区别，查询 inventory 时使用后者。合法列是 `entry_kind`，不是 `kind`。`extract_artifact` 在当前版本只接受 integrity policy，由 REA 选择新临时目录；读返回的 `output_root`，不要凭空传 destination 参数。解包不会部署到 Mods。

返回结果可能很大：完整保存在本地，只向模型打印 ID、计数、所选路径和错误摘要。`compare_scorebug_candidates.mjs` 示范同一会话保留完整左右 inspection Evidence 再比较，并导出 bundle。不要把几百 KB 的整个图反复灌入上下文。

SCNE 是 JSON-like 片段，并非严格 JSON；本轮解析时补外层花括号、对缺失值使用解析占位并忽略尾逗号，保留转换计数；占位不等于游戏语义的 null。VCUIELEMENT 只解析 JSON 前缀，后部二进制未解。研究副本只改一处 `VC_MinTextScale`，不把整个场景重新序列化为普通 JSON。

## 5. 已发生的实验与证据强度

| 实验 | 实测结果 | 可支持的结论 |
| --- | --- | --- |
| Overall 既有研究 | 6人有效缓存；Human 在球队名单确认 Ben87、Embiid基础95/加成96 | 两例支持基础Overall解释；加成链、无效缓存和多场景仍未知。此证据来自本任务前的实际实验，非新发明算法 |
| 元数据/代码引用 | 13结构、21处LEA live bytes；2.719秒、显式10880字节 | 当前字段定义及代码片段匹配，未观察这些代码执行 |
| 成长/徽章元数据 | 9结构；2.614秒、9936字节 | MyLEAGUE成长、比赛徽章效果和CAREERMODE结构可分别定位；未求得成长公式 |
| 转播设置元数据 | 5结构；2.632秒、23989字节 | ticker/声音/赛后切镜/采访人数等定义存在；未取得当前开关实例值 |
| 4,096条批量 fixture | 写入2.965秒、恢复2.810秒；目标进程两次自验4096/4096 | 自建静止内存中的传输、before检查、回读、恢复；不是游戏批量写验收，不是原子CAS |
| native-ABI调用 fixture | 3.119秒，16事件，reader(21)=42、writer(21)=43 | REA能承载有界入口/返回拦截；没找到游戏字段的真实生产者 |
| scorebug资源 | 260成员、9SCNE、107UI节点，其中44 SceneText | 现有模组可清单/解包/解析；加载、触发、实时信息注入仍未知 |
| 资源副本比较 | 259 occurrence未变；root和scorebug_intro.SCNE共2处changed，无增删矛盾 | 只改1个内部成员，根容器哈希随之变化；并非改了两个内部文件 |

没有可靠的任务级实际模型费用数据。记录工具耗时、返回字节和事件数；本地后端耗时、目录字节和模型账单不可相互换算。

## 6. 徽章与联盟机制：研究接点

当前已匹配：`FRANCHISE_MENTOR::BADGE` 含 Type、Level、IsActive、Progression、DateLastChecked；MENTOR 含持续天数、Compatibility、开始日期和徽章数组。`FRANCHISE_PROGRESSION_TUNING` 含 PhaseFactors、教练影响、随机因子、WorkEthicBonus、训练进退步倍率等。

`BADGE_TUNING::COMMON_SPOT_UP` 和 SHOOTING_BADGES 的距离、接球后时间、防守干扰、ShotChanceBonus 等是**比赛效果/触发条件候选**；不能把它们解释成“学会该徽章要求某属性达到X”。`CAREERMODE_PROGRESSION::BADGES::TUNING` 的升级点数及声望解锁结构单独标 MyCAREER，不迁移到 MyLEAGUE。

下一轮应先选一种具体徽章/导师关系和资料中的条件假说，绑定当前身份、模式、自然游戏日期及UI进度；找到实例和读写消费者后，观察自然刷新。仅靠 cmp 常数或字段名不能形成成长门槛表；更不能用直接编辑徽章替代机制验证。

## 7. 比赛沉浸感与自定义赛场

已建立16个**检索家族**的候选目录，覆盖半场、采访、更衣室、首发、赛后、统计字幕、回放、暂停、ticker、场馆、观众、解说、scorebug、呈现队列、碰撞和动画。它们有交叉；字符串条数不是功能个数。旧版/CAREER标签可能是残留或共用，不能称为“被关闭内容”。

当前确认场景为 Human 报告：MyLEAGUE存档已运行约一个月，停在日历、控制步行者。无比赛窗口观察，因此**隐藏/关闭功能数量、当前已启用数量、真实动态注入能力均为 UNKNOWN**。

可优先形成三条后继路线：

- 信息层：SceneText/统计通知/ticker，绑定角色公开数据→审阅→呈现DTO→原生文本消费者；外部角色隐私与Potential不能送入公开转播。
- 呈现层：SCNE/VCUI/材质/动画/记分牌布局，先研究副本和资源diff，再在单独批准场景验证加载及UI效果。
- 物理层：碰撞/脚步/布料/轨迹等对象和调参；与转播呈现分别验收，不用字幕变化证明物理引擎改变。

要认定一项“原有但关闭”，至少需要模式/平台匹配的资源与依赖、代码可达性、已定位的状态/开关、在对应场景的调用证据，及排除缺资产/旧版残留等解释。要认定“可实时注入”，还需线程与生命周期、字符串编码与容量、所属对象、before校验、渲染回读、退出恢复。以上尚未在游戏中验证。

## 8. 故障与边界

整个EXE Ghidra原始330秒、延长600秒、禁入口分析330秒、再禁Subroutine References并给code seeds330秒均失败。已耗尽该签名三次修复预算；不得把此前失败改成成功，也不得在暂停期间重开。小型PE成功只证明后端安装。

游戏改值、原生函数调用、开关激活、比赛/日期推进、存档写入、生产接入和master合并均未发生。独立fixture的写入/hook与游戏实验明确分开。所有本轮会话已清理；研究副本仍在游戏目录外。原游戏和模组没有修改。

本稿是可复用的操作与证据入口；综合探索仍暂停，后续任务需补资料和边界。具体缺口及建议见 RUN 的规划交接，不能由本手册自动启动。
