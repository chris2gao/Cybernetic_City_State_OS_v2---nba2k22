# 阶段02｜Codex REA暂停探索固定来源核销及可继承能力矩阵 v1

**对象**：Human交付固定源 `task/rea-development-exploration-01@b16e69727987f29bff5e2ee31ce82891102ab2d9`，源任务状态 `PARTIAL / HUMAN_PAUSED`；本任务阶段02的**只读证据二次利用**。没有重新打开、运行、恢复这个Codex任务，也没有现场游戏操作；研究代码和原始数据留在源分支，不复制或启动实验脚本。**规划归纳的来源等级仅覆盖已实际阅读的材料，不代表对全部52文件运行SHA256或独立复测。**

## 1. 精确来源与审查范围

| 固定资料 | 原 Git Blob | 实际使用范围 |
|---|---|---|
| `08_结论/PLANNING_HANDOFF.md`（源Run） | `9c3dbc11ee5268a3e4e4a9ed28dcdd5a2a6e1376` | 任务暂停、实验结果、五类后续建议、场景和整体非目标 |
| `docs/development/REA_DEVELOPMENT_PLAYBOOK_V1.md`（领域路径） | `aa2dda60421c59b8db37831cf271a46979a7324f` | REA 6.8.0、229工具目录、Windows实际已用后端、三阶段实验、管理员边界、资源分析和Ghidra失败 |
| `research/rea_development/README.md`（领域路径） | `4fb247a17a24b9e27c378d3a682d0cc411713bf4` | 有界脚本说明，区分游戏read-only探针、fixture实际写与模组离线副本 |
| `06_执行/evidence/SOURCE_MANIFEST.json`（源Run） | `c26a28615f5b87544088a3f9716eedf6fbdde897` | 52项文件/声明SHA256/字节数，合计2,695,321字节；**manifest为作者哈希声明，非本GPT逐个计算验证** |
| `growth-findings.json` | `a799c013f7dbd86a76dde0d8b72c6627e9a5f181` | 9种源类型的`types`/候选字段、`limitations`、cleanup状态；`growth-evidence.json` Blob `89345f04c77170dcb1d0d19900306f43b6851142`检查了Frida normalized payload |
| `metadata-findings.json` | `11cc8909b104067ee2cecdff08e88965469ba94f` | 13种源类型名单/字段定义、明确静态定义非实例；`metadata-metrics.json` Blob `443299267fd38f0e50e7214e56e25e5c304f3b50` |
| `bulk-fixture/bulk-fixture-results.json`及`apply-evidence.json` | `593e5e3740fb85f0fb9985e0d9875ee61bb2b423` / `0772aaf04ef09cb4d6da8f2a5e3709c7dcad1248` | 4096个自建对象修改/恢复、负CAS、子进程独立读取、`game_target:false` |
| `call-trace-fixture/call-trace-results.json`及`trace-evidence.json` | `290d40661d8a677664f77427c662e8a320f7081f` / `3fea86f0c3a528fc040dc144004781dfa1407b6c` | 16条自建Native ABI trace，`game_target:false` |
| `prior-overall/overall-live-findings.json` | `37a5114c4e3e23864e5e83adac7cb8f8891f0ae9` | 先前6个原生Overall缓存样本/有效位，基础UI两样本吻合；不等于升级阈值或Native重算可调用 |

固定仓库：`chris2gao/Cybernetic_City_State_OS_v2---nba2k22`；源目录分别位于 `01_os/07_content/_runs/run-20261027-rea-development-exploration-01/` 和 `08_Domain_Applications/Antigravity_GM_Engine/`。所有上表Blob来自此次固定commit GitHub连接器回读。**来源独立性**：报告、findings和脚本出于同一Codex任务，自建程序自检不是第三方独立游戏验收；元数据有原生live观察的源证据，但分析结论仍需对游戏语义复核。

## 2. 真正已获证的能力、等级与禁用的外推

| 研究结果 | 这份来源支持的狭义命题 | 不支持的夸大结论 | 对本REA P0模型的作用 |
|---|---|---|---|
| REA与Windows/Frida | 旧实验在管理员权限下，可有界attach固定NBA2K22进程读取所选Native元数据；源报告13结构/21代码片段，2.719秒；9 growth结构2.614秒；cleanup无错、进程存活 | 所有229工具都能在Windows运行、读任何结构无需权限、代码片段已被执行 | `RES-REA-01/07`可优先采用局部源探针和固定构建/RVA追溯；新运行需要新Human范围授权 |
| 已出现联盟徽章与成长定义 | `FRANCHISE_MENTOR::BADGE`、`MENTOR`、`FRANCHISE_PROGRESSION_TUNING`，含`Progression`、`DateLastChecked`、`PhaseFactors`、`MinCoachEffect`、`WorkEthicBonus`等候选字段 | 已读游戏真实活实例值、已得“能力N升级徽章X”的规则和实际消费者调用 | `RES-REA-02`的先行来源定位，可设计一个徽章/导师场景的L1→L2→L3验证 |
| 徽章比赛效果类型 | `BADGE_TUNING::COMMON_SPOT_UP`/SHOOTING/DEFENSIVE/PERSONALITY等包含射程、投篮加成、干扰等字段候选 | **比赛触发/效果参数**就是**成长/等级升级条件** | 建模明确拆分`badge_effect_trigger`与`badge_level_upgrade`两个不同mechanic_id，不用近名字段代替阈值 |
| MyCAREER结构 | `CAREERMODE_PROGRESSION::BADGES::TUNING`有积分、解锁、声望等名称 | MyLEAGUE套用MyCAREER徽章升级公式 | 强制模式标记与拒绝跨模式推断；若确证共享函数再依据具体证据变更 |
| fixture批量写/恢复 | `game_target=false`的Python自建静止进程，4096条写后子进程核对4096/4096，恢复再核对4096/4096，apply2.965s、restore2.810s，CAS前置负例有效 | NBA2K22实体index/生死期/部分失败/事务/缓存/UI/存档已安全写；真实游戏能力4096已达标 | `RES-REA-05`未来只复用**有限工具底座/预检模式**，不赋予真实交易或批量Writer成熟度 |
| fixture调用拦截 | 自建Native ABI reader(21)=42、writer(21)=43，共16事件，3.119秒；`game_target=false` | 已找到或Hook游戏本体交易/教练函数、ABI已知、函数可安全重入 | `RES-REA-03/04/05`未来可用此验证Frida观测可行，但游戏函数的this/线程/生命周期需重新取证 |
| 游戏模组场景/资源 | 本机newscorebug.zip型IFF 260成员、9SCNE、44 SceneText；一处资源副本内部参数对比可识别更改 | 属于原版已加载内容、游戏引擎的实时信息注入已证、或成为A-v1-RC01必交成果 | **仅二级线索**；不扩大本P0徽章/教练/交易三代表范围 |
| Overall缓存旧证据 | 六名player有效cache的float32原生观察与两份基本UI提示；增强值及无效缓存重算未解决 | Overall全域已完成、游戏机制可安全调用、可以由外挂自行重算 | 说明有界Native缓存观测的实际能力，可复用字段来源验证模式但不是本次三代表闭环 |
| Ghidra整EXE | 游戏大EXE原始330秒、延长600秒、禁入口330秒、再禁引用330秒均超时，作者判定无新方案不得继续重试 | 整个游戏函数图已解析完，或者REA局部能力全部不可用 | **明确停止条件**，使用局部PE/字符串/metadata/xref、Capstone验证，不无限重试整EXE |

**特别说明**：`growth-findings.json`中的`instance_values_read`、`getter_calls`、`hooks`、`memory_writes`字段不能只因存在于JSON就认定执行过；以该文件实际数值、Source/手册限制和针对具体mechanic的实测共同判断。

## 3. 按已批准A-v1-RC01的结果项映射已知素材

| 结果项 | 旧Codex直接可复用 | 必须新增的现场/静态证据 | 不应重做 |
|---|---|---|---|
| `RES-REA-01` Mechanism Atlas | 固定二进制元数据候选、字段CRC、REA证据结构与脚本/工具契约 | 徽章/教练/交易各有确切`mechanic_id`、真实UI和同模式函数消费者、负例/来源成熟度 | 不重新盲扫已得同构建全部注册模板 |
| `RES-REA-02` 一徽章深入 | `FRANCHISE_MENTOR`和PROGRESSION字段路线、BADGE_EFFECT与CAREERMODE反例 | **MyLEAGUE当前实例**徽章身份/球员/导师/日期/可观察条件，成长前后与实际consumer，数值门槛或有界否定 | 不先研发全部徽章；不把比赛buff冒充成长条件 |
| `RES-REA-03` 一教练设置深入 | 有界meta+trace工具基础，`FRANCHISE_PROGRESSION_TUNING`中的coach影响只是成长路线关联 | 实际MyLEAGUE进攻/防守UI参数→球队/教练Native对象→真正消费函数→生效状态 | 不拿成长的`MinCoachEffect`冒充战术执行语义 |
| `RES-REA-04` 交易机制 | 函数观测fixture技术、已有Player/Team/Finance/Market Reader可以当状态来源候选 | 游戏真实交易validator/callsite、commit联动名册/合同/工资帽/选秀权、事务生命周期、调用前置/线程 | 不把fixture函数地址、一次字段改变当成原生交易完成 |
| `RES-REA-05` 有条件PoC | 自建负CAS、fresh readback、trace脚本概念 | **另行Human许可**的具体离线档/教练设置目标、当前游戏线程/ABI/对象/失败处理，后采的新Native事实一致性 | 不直接迁移fixture脚本指向真实游戏PID |
| `RES-REA-06` 架构复用矩阵 | 通过现有手册区分read、mechanism、safe invocation三层 | 三代表对`native_reuse`与`memory_edit/external_simulation/hybrid`成本和一致性的实证 | 不以REA工具成功自动重写旧产品交易方案 |
| `RES-REA-07` 证据与交接 | 52项manifest、脚本、源码/构建与受控资源预算记录 | 正式将来新CodeX任务使用的实际commit/新Evidence/负例/隔离档恢复与独立复核 | 不要求重新上传游戏EXE/模组素材/修改后的IFF |

## 4. 证据可信度与当前范围结论

- **E-REA02-001／直接固定材料**：源commit、handoff/playbook/README、manifest均可Git固定回读，历史研究暂停的状态成立。
- **E-REA02-002／原生观测（归档、同一Codex来源）**：meta和growth Frida source Evidence及findings一致显示游戏对象**类型定义**已实读；对应运行环境/窗口没有在本GPT重新复现。`L1_TYPED_LAYOUT_OBSERVED_FOR_THE_LISTED_TYPES`是合适结论，**绝非L2-L3完整徽章公式**。
- **E-REA02-003／自建fixture实证（非游戏）**：4096批量操作和16事件trace的`game_target:false`从results与REA原始归档可核，技术能力只限Owned Fixture。
- **E-REA02-004／非核心资产探索**：资源包/呈现素材为二级研发布局，当前无原版运行时消费证据，不应成为本P0退出门。
- **E-REA02-005／明确反证/停止条件**：整体EXE Ghidra当前策略多次超时，建议有界本机证据路线；没有证据证明“REA整体不可用”。

**整体判断：`STATIC_SOURCE_AND_REPORTED_RUNTIME_CAPABILITIES_PARTIALLY_SUPPORTED`**。A-v1-RC01七项**均未由这份暂停材料单独完成**；其大价值是已把“是否能在Windows原生对象获得类型信息/可控Frida观察、自建批量及函数观测底座”从纯猜想变成有原始归档的局部实证，从而大幅收窄下游Codex真实游戏机制追踪的起点。

## 5. 源使用与验证缺口

已读内容包括固定commit与源分支中上述入口、52项清单、`growth-evidence/findings/metrics`、`metadata-findings/metrics`、`bulk-fixture apply`、`call-trace fixture results/evidence`、`prior-overall findings`。未逐一读取或本地重跑52项、未重新计算它们全部SHA256、未加载整个scorebug大体积证据、未执行GitHub上的JS/Python/PowerShell脚本、未连接Windows/game/REA服务、未访问内存/函数。老Evidence ID存在于归档不意味着后续本GPT已调用原REA Provider。

后续Codex若以此作工程基线，须先校验实际执行进程、EXE SHA和工具版本可用，重新获授权并创建**本轮新证据目录**，不以2026-10-27旧PID/地址/脚本范围复用授权。
