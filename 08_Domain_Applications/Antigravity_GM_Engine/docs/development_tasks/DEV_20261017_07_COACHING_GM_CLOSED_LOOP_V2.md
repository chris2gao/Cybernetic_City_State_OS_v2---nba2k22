# DEV-20261017-07 — 教练战术系统最终开发规格 V2

**2026-10-17 最新玩家指令；本规格优先于同任务V1、DEV05/DEV06中所有关于Sim字段为GM能力、18项“可选”、单对手防守“以后再做”与战绩测试的旧陈述。**

- `status=V2_REQUIREMENTS_APPROVED_FOR_DEVELOPMENT / CODEX_IMPLEMENTED_ON_PR1 / FORMAL_GAME_WRITES_NOT_APPROVED`
- `repo=chris2gao/nba2k22-gm-engine`，NBA2K22 Windows PC，MC存档中的终极联盟；工程基线是[PR #1](https://github.com/chris2gao/nba2k22-gm-engine/pull/1)、head `5daeed8dc0001b5052dce1cfc97d6c22ee9317c3`（开工前先校验最新PR HEAD）。
- 玩家职责：每次自行触发采集/GM决策/批准具体战术/委派执行及推进游戏；Codex开发只写代码和隔离局最小安全校准，**不改正式存档**；GM对30支球队分别独立作经营决策。
- **不需要模拟比赛或实际比赛胜率效果测试，也不需要为早已通过的六POE重复保存/重启测试**。此处的必要验收仅证明“目标对象正确、编码/允许值正确、写入可回读和恢复、批次不误写其它队、数据同步可信”。

**玩家实施期间的后续修正优先：** 已确认四个百分比倾向为0–100，BenchDepth是人数且不得以9→10测试样本限制GM；四Freelance按完整原生目录与顺序接口开放，不重复菜单/保存重启验证。玩家最终明确开放原生Tempo读写、标注界面含义未确认，不称为已验证的进攻节奏；其他教练实际值用于推断实用参考而非强加样本白名单。下文Tempo的旧UI描述不再是开放门槛；19项及A–E工程范围不变，真实采集/发布仍须玩家另行触发，开发只交付现有PR而不自动合并。

## 1. 业务语义：三类对象，不能混淆

| 类别 | GM是否控制 | 存储scope | 业务要求 |
|---|---|---|---|
| **球队默认教练战术** | 是，19项 | `COACH_DEFAULT`，按球队当下的HEAD_COACH对象，不是全联盟公共参数 | 面对所有对手的该队基础打法 |
| **指定对手整体防守理念** | 是，重点，18项原生候选 | `VS_OPPONENT_DEFENSE`：该队→某一对手的GAMEPLAN整体防守设置 | 对这一个对手的差异化压迫、掩护、包夹、防守策略 |
| **独立模拟参数** | **否** | 教练`SimPace/SimPress/SimHelpDef/SimOffReb/SimDefReb` | 由玩家自行模拟时控制；只读兼容，**排除GM批量修改及GM教练手册的可执行字段列表** |

此处“全局”表示**单支球队的默认设置覆盖其面对的所有对手**，不是“全联盟级Simulation Sliders”，也不代表GAMEPLAN有单独全队默认的18项整体防守表。

严格禁止直接修改普通球员能力、潜力、徽章、倾向、性格、教练/球员熟练度或全联盟模拟滑块。Gameplan逐球员防守者及球员轮换写入并非本版额外业务要求，不能把对应内存槽当成全队整体设置。

## 2. 19项球队默认战术：本轮全部开发

### 2.1 已技术验收的默认六项POE（直接复用PR#1）

| 字段 | 用途 | 原生合法值 |
|---|---|---|
| `POEOffense` | 进攻重点 | 0无偏好、1突破、2外线射手、3低位、4挡拆、5中立、6围绕得分核心 |
| `POEOffense2` | 进攻节奏策略 | 0无偏好、7耐心组织、8中立、9主动快速出手 |
| `POEOffense3` | 进攻篮板策略 | 0无偏好、10冲抢进攻篮板、11中立、12控制退防 |
| `POEDefense` | 防守重点 | 0无偏好、13护框、14中立、15限制外围 |
| `POEDefense2` | 防守侵略性 | 0无偏好、16保守、17中立、18身体对抗 |
| `POEDefense3` | 防守篮板/转换 | 0无偏好、19冲抢防守篮板、20中立、21快速转换 |

COACHDATA `+0x13C`一组little-endian 32bit，共六×5bit，顺序Defense bit0/5/10、Offense bit15/20/25；bit30/31保留。六项此前已经按用户UI确认并隔离局保存/重启验证，**不需要再次做无意义重复试验**。新batch继续使用多字段合并一次4byte写、旧共享整块前值比对、保留位保护及玩家批准门槛。历史`TEAM+0xEB2`旧writer继续永久封禁。

### 2.2 两项球队主教练体系（本轮必需）

- `PreferredSystem`：教练偏好战术体系，`COACHDATA+0x108`，bit16,width4。
- `ActiveSystem`：当前激活体系，同块bit28,width4。
- 值域：0 Balanced，1 Grit & Grind，2 Pace & Space，3 Perimeter，4 Post，5 Triangle，6 Seven Seconds，7 Defense。
- **只针对球队当前HEAD_COACH身份进行受控设置**；Codex用一次正常UI字段改变/静态代码已有证据确定这两个选项的实际生效/同步关系，必要时对成对修改制定规则，但不碰体系熟练度/评分。体系和PlaybookID共享原生32bit块，必须合并mask，保护邻居位。

### 2.3 主教练战术手册（本轮必需）

- `PlaybookID`，`COACHDATA+0x108`，bit8,width8；由主教练选择影响球队使用的战术手册。
- 只准从**当前游戏进程已加载的有名手册目录**中选择合法枚举ID/有效引用；历史扫描得到84本，仅是历史计数，不能写死84、随意接受0–255或改68个共享战术CRC槽。
- 与两项体系共享字节块，写入前验证动态目录和当前主教练关联，换帅/重启必须重新校准。

### 2.4 六项教练数值滑块（本轮必需）

用户明确看到当前PC终极联盟“教练比赛计划”界面数字**1–100**；这属于本局用户UI观察，**执行允许值以本局实际UI映射为准**，不是从8-bit存储宽度猜1–100的原生raw数值。某些历史MyLeague/社区名单可能出现0–100或BenchDepth=11，必须以当前界面为准；可一次核对UI最小/最大/步长及raw变动来建立映射，无需对每个整数反复存档测试。

| 原生字段 | COACHDATA内偏移 | 对GM的篮球语义/正确性重点 |
|---|---|---|
| `BenchDepth` | `+0xDE` 8bit | 替补深度/参与轮换数量；检查UI的1–100是否经过转换成实际人数/权重，**不能把值11直接解释11%** |
| `RunPlayTendency` | `+0xE0` 8bit | 运行战术手册预设战术的频度倾向；越高一般越常执行set plays |
| `ZoneUsage` | `+0xE2` 8bit | 使用区域联防的倾向，越高一般越倾向区域防守 |
| `BenchUtilization` | `+0x138` 8bit | 替补使用/主力出场分配，与BenchDepth分开理解 |
| `Tempo` | `+0x148` bit9,width8 | 实际比赛教练进攻节奏滑块，区别于POEOffense2及已排除的SimPace |
| `HelpDefense` | `+0x148` bit17,width8 | 实际比赛协防强度，区别于已排除的SimHelpDef |

**著名教练取值的轻量调研**：Codex可只读抽查本存档几个著名在任主帅，例如Kerr、Spoelstra、Popovich、Thibodeau、Nurse、Lue，报告六项原始值和菜单显示值以解释“长轮换、强调预设战术、常用联防、强协防”等风格；**不能编造他们在此游戏存档中的精确数值，也不能把现实NBA声誉当原生内存观察**。若当前存档没有某教练，不要求再加载其它局。

外部线索：
- [旧MyLeague教练参数说明](https://gamefaqs.gamespot.com/boards/2000208-sports-and-racing-nba/76861758)：Help Defense、Run Plays和Zone Usage的高/低倾向，历史记载0–100。
- [2K22自定义名单的教练滑块示例](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/nba-2k-basketball-rosters/921430-zten11-s-nba-2k22-roster-xbox-player-two-way-value-impact)：Run Plays=60、Zone Usage=0、Bench Depth=11、Bench Utilization=100，是社区**自定义名单**而非2K22 PC官方内置主教练值。
- [2K Coaching分类概述](https://nba2k.fandom.com/wiki/Coaching)：Coach Gameplan包含分钟安排、轮换、System Proficiency和Edit Playbook；不表示本轮同步开发逐球员PlayingTime写入。

### 2.5 四套Freelance进攻战术（本轮必需）

玩家确认此菜单存**四套按照优先级排列**的Freelance进攻配置，比赛中可以使用，不需要进行战绩效果证明。GM操作模型应呈现`freelance_sets:[slot1,slot2,slot3,slot4]`，按1→4保留顺序，支持一次改其中某槽/整套数组，不把它们当成互不关联的随机枚举。

| 字段 | 原生位置 |
|---|---|
| `FreelanceType` | `+0xFC` bit25,width6 |
| `FreelanceType2` | `+0x148` bit26,width6 |
| `FreelanceType3` | `+0x15C` bit3,width6 |
| `FreelanceType4` | `+0x15C` bit9,width6 |

Codex从当前游戏进程已加载的原生enum表与游戏菜单确认全部可选名称/RAW映射；保护同块`Tempo`、`HelpDefense`及未知bit；不必为证明四套使用频率跑CPU对抗赛。**能够设四套是要求，四套均匀使用概率不是产品假设**。

## 3. 新重点：仅针对指定对手的整体防守理念，不能与默认战术混合

用户描述：教练比赛计划在**指定某一对手球队**页面，会多出现“整体防守理念”设置，内容包括施压、Force Direction、持球掩护、Hedge、换防、协防、包夹等。这些仅在该队**面对指定对手**时使用，不是`COACH_DEFAULT`，不能对全联盟改，也不能误改其它28个对手。

### 3.1 现有可复用结构

- `FRANCHISE_GAMEPLAN_MANAGER`：本次存档每队有29条其它有效球队Gameplan，30队共870条；容量35、每条`GAMEPLAN=0x370`字节，逐条按内部`TeamId/OpponentId`定位。
- 对手记录中的六POE `+0x17E..+0x183`是逐字节，**不同于教练默认位域**；整组防守候选来自`GAMEPLAN_MATCHUP_DEFENSIVE_SETTINGS`的8byte位域，V1代码在Gameplan中按12byte条目扫描，条目带`matchup_id`、`defender_id`。
- **必须先确定页面“整体/All”对应的是哪一条条目/特殊ID、哪个覆盖层或者一个额外gameplan对象。** 现有的`defensive_matchups`不应无条件视为整体设置。玩家没有要求修改每个对手球员的个人对位，也没有授权修改球队默认19项之外的其他Gameplan进攻字段。
- `IsInUse`全部读到0而部分方案已有差异；不能假设0=禁用，更**不能**为“激活”盲改为1。必须从当前UI一次实际变动获取启用、继承默认、取消/恢复原值的安全证据。

### 3.2 十八个原生防守候选字段

| # | 原生名 | 中文界面功能候选 |
|---:|---|---|
| 1 | `PressureOnball` | 对球压迫 |
| 2 | `PressureOffball` | 无球压迫 |
| 3 | `ForceDirection` | 逼迫进攻球员向底线/中路 |
| 4 | `ScreenDefenseOnBall` | 持球掩护的持球防守者策略 |
| 5 | `ScreenDefenseHedge` | 持球掩护中掩护人防守者(Hedge)策略 |
| 6 | `OffballScreenDefense` | 无球掩护策略 |
| 7 | `PostDefense` | 低位防守 |
| 8 | `DoubleTeamPerimeter` | 外线包夹 |
| 9 | `DoubleTeamPost` | 低位包夹 |
| 10 | `ScreenDefenseOnBall5` | 中锋参与挡拆时的持球防守策略（原生名为OnBall5，须与本局UI核对） |
| 11 | `ScreenDefenseHedge5` | 中锋相关Hedge策略 |
| 12 | `SwitchRule` | 换防规则 |
| 13 | `OnballHelp` | 持球突破协防逻辑（需与UI标签匹配） |
| 14 | `ScreenHelp` | 掩护协防 |
| 15 | `ExtendPressure` | 延伸压迫 |
| 16 | `TagOnRoll` | Roll man协防或tag轮转 |
| 17 | `StayAttached` | 是否跟紧原防守目标 |
| 18 | `PreRotate` | 预轮转 |

这些是V1当前已定位的18个原生字段**候选**；界面“整体防守理念”的实际可编辑字段集合可能并非这18个一一对应，应以PC菜单和原生反射信息建立**准确UI→作用域→地址→合法枚举**目录。部分名称原文并不等于确切篮球语义，允许先保留原名/UNKNOWN，不编造菜单描述。例如`PressureOnball`有候选`AUTO/GAP/MODERATE/TIGHT/SMOTHER`，其它各选项不能用这个值域套用。

### 3.3 唯一必要的定位步骤（不做非必要实验）

在复制测试存档中，用UI指定一支球队→一个对手→**整体/All**→一项防守设置做一次可逆选择，记录该GAMEPLAN的所有权/有效条目、变化的防守8byte块、manager/默认COACHDATA及其它28条对手记录，仅执行**最小差分、回读、恢复**。明确：
1. 是否修改了正确对手、正确overall条目而非个人matchup、是否有额外标记或继承/回退状态；
2. 是否不污染同队其它28对手、主教练默认19项或其它29支队；
3. 存储位、原生合法enum、共同块保护、对手ID/如果引用球员则身份保护；
4. 写回后UI重新进入可见正确值，恢复/取消后正确回到默认。**不必再跑长期保存重开、赛果和重复大量设置尝试**。但若无法解决激活/继承语义，执行器必须保持此模块BLOCKED，不能假称已经可以针对单队生效。

待已确认后，给批次方案引入`scope=VS_OPPONENT_DEFENSE`，必填`team_id`、`opponent_team_id`、`defensive_setting_scope=OVERALL`及明确旧/目标值，不能与同队全局19项混淆。支持多个不同对手设置，但不要求给全30队×29个对手统一写一遍。GM可针对强投篮/挡拆/低位球队作独立战术布局，无需一场场效果验证。

可参考[2K22防守设置社区讨论](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/nba-2k-basketball-online/919827-next-gen-2k22-defensive-settings)中的菜单词汇，但其讨论主平台为PS5/XSX，不能代替PC本局的enum。

## 4. 必须交付的30队受控批量执行（继承DEV07 V1基础）

- 一个`COACHING_BATCH_CHANGE`批次覆盖1–30支球队，GM可以HOLD某队；可同时含某队`COACH_DEFAULT`全局战术动作、该队面对某对手的`VS_OPPONENT_DEFENSE`动作。键按`team_id + scope + opponent_team_id(可选)`去重，禁止同一块同字段相互冲突。
- **整批预演（无进程写入权限）**：基于同一已发布`source_batch_id/game_date/coach identity`读取所有前值，校验合法raw、需加载Playbook/Freelance enum、整体防守对手身份、字段是否正式`production_enabled`，生成规范化批准`batch_id/decision_id/version/action_ids/digest`；JSON自带`approved:true`不能算批准。
- **玩家实际批准后** Codex执行角色在当前游戏进程先**只读预校验全部目标**；任何球队、主帅、对手、旧共享块值或对象身份不符，则整批**零写入**；编辑页必须关闭（已知编辑UI缓存可能覆盖）。
- 先持久journal写入所有共享块preimage并fsync，持有独占lock。逐队对原生COACHDATA和对应Gameplan已认证范围用masked writes，读回全部目标与未授权位。运行时失效立即停。
- 失败逆序条件回滚已写目标（仅当前仍等于刚写目标的块可安全恢复），失败时明确`PARTIAL_UNRECOVERED_MANUAL_REVIEW`；不能声称跨30队RAM存在物理瞬时原子指令，也不能将for循环30次单动作执行器包装为原子事务。
- 成功返回`COMMITTED_VERIFIED_IN_MEMORY`与全队HOLD/APPLIED/BLOCKED及字段修改摘要，**不是已经写入正式游戏保存文件**；回执带当前局游戏时点供下一次来源捕获，但执行完成不能自动启动数据采集。
- 所有正式游戏动作需玩家具体明确批准；“同意开发”只是授权编码，不是授权改所有30队战术。

## 5. 必须交付正常玩家触发的教练数据来源

- 将新`coaching_tactics` production source接入现有 `scripts/run_data_update.ps1` → 同批只读内存源捕获`src/auto_pipeline_ingest.py`→SQLite→`src/export_web_gm.py`→原有`published/saves/<save_id>/latest.json`及`manifest.json/source_coverage.json`→`-Publish`时使用`scripts/publish_web_snapshot.py`上传到GitHub。**用户不触发则不运行**；无`-Publish`只本地导出。
- SQLite保留snapshot-scoped 30队默认19项真实`raw`、coach/head-coach身份/coach version/readiness以及单对手整体防守经认证的记录。与游戏源批次、`data_updated_at`、`game_date`、`snapshot_id`严格绑定；禁止用单独晚于采集的本地snapshot冒充同一比赛时点。
- 给网页版GM的轻量源建议`coaching/teams.json`（30队19默认项、当前可执行状态）和`coaching/field_dictionary.json`（UI文字/raw/单位/合法值/作用域/四套Freelance优先级），独立对手设置按`coaching/opponents/<team>.json`按需分队或带索引按需读取。不要每次GM启动一口气读全部870条Gameplan/18字段的大文件。
- 五项`Sim*`如作为兼容来源保留，只能标`GM_CONTROL_DISABLED`，**不要引导GM修改它们**。历史`TEAM+0xEB2` legacy `poe_*`保持`LEGACY_UNVERIFIED`，修改`src/gm_core/coverage.py`与GM接口以原生COACHDATA为进攻防守战术事实，不得复活旧地址语义。
- 新来源30队缺失或非法、同批coach身份歧义时标`COACHING_SOURCE_CAPTURE_FAILED`并阻止发布虚假完整新包，保留last-good快照/latest；旧存档历史batch不追填当前新教练值。不为更新来源申请RW句柄或修改游戏状态。
- 源工程是否已经在本地与正式执行仓库合并，需Codex根据PR#1真实HEAD和发布守卫检查；源码未部署main前不能假设GM能在main读到新来源。

## 6. 两份正式角色操作手册，必须与真实可运行代码严格一致

### 6.1 GM模型：`web_gm/manuals/GM_COACHING_OPERATIONS.md`

应包含：
- 入门入口`published/index.json→latest.json→batch/coaching/teams.json+field_dictionary.json`、save_id/season/batch/date/coach身份检查与未知值规则。
- **19项全局战术**及**指定对手整体防守**的中文篮球含义、实际合法原生enum/滑块UI取值映射、四套Freelance ordered优先级、可变更已认证状态；明确排除五项Sim及逐球员Matchup/轮换写入。
- 30队按球员既有能力/真实阵容/教练打法逐队`HOLD|PROPOSED`，所有真正调整有team_id、coach identity、原始共享块、合法目标值、具体对手可选及篮球合理性，不要推算固定提升胜率幅度、不全队复制一套“最优”。
- 生成与执行端完全相同的`COACHING_BATCH_CHANGE`契约/真实示例，标`PROPOSED`，独立玩家批准才可执行。改变教练/存档或数据滞后时需重新提案。
- 每赛季GM聊天按玩家触发的节点继续，不自动推进下一月、采集或执行；教练系统可用**无需比赛模拟效果验证**。

完成后`web_gm/baselines/GM_BASELINE.md`、`web_gm/GM_DECISION_SOP.md`、`web_gm/memory/GM_CURRENT.md`都应能找到这本手册与当前真实白名单，旧DEV07“仅六项”的历史计划不得继续误导GM。

### 6.2 Codex执行模型：`docs/40_COACHING_EXECUTION_RUNBOOK.md`

- 玩家逐批明确批准`batch_id/decision_id/version/action_ids/digest`；原生对象/当前进程/主教练岗位/旧值验证，先关闭Coach Gameplan编辑页，`--coach-editor-closed`是操作者明确声明，**脚本不具备UI自动检测**。
- 真实运行命令（需与`--help`吻合）：获取合法只读source/战术snapshot→GM批次检验/dry-run→整批preflight→以批准摘要执行→比对所有目标/未授权位→journal/receipt→条件回滚/崩溃人工恢复。
- 明确`COACH_DEFAULT`与`VS_OPPONENT_DEFENSE`不同对象和原生编码，不能拿COACHDATA packed codec写GAMEPLAN；Playbook动态加载验证、6滑块合法UI/raw映射和Freelance顺序必须在执行时再次检查；五项Sim禁止GM执行。
- 批次失败处置、锁/缓存/第三方AI修改/存档换帅/PID变化/旧值改变、`PARTIAL_UNRECOVERED`人工审计。无玩家批准时不得打开读写权限。
- 不自动做数据采集、SQLite发布、GM回合或游戏日期推进。生成供用户回传GM的每队执行结果与真实游戏日期/数据源关联。

更新`docs/36_EXECUTION_BASELINE_PROMPT.md`、`docs/28_EXECUTION_WINDOW_RUNBOOK.md`、`docs/34_BASELINE_CURRENT_STATE.md`和`AGENTS.md`的最短索引。两本手册须从真实实现代码/命令生成，而非本研究文档概念接口。

## 7. 用户要求“非必要不测试”：精简验收标准

**严禁要求Codex安排多组快模拟、游戏胜率A/B、按月推进、每个滑块的100个数字逐个保存、全部870对手逐条实测。** 已通过的默认六POE不再重复证明。

仅保留极少量实际安全必要验证：
1. 真实UI/rva/枚举/位域/可见值↔raw字段定位；滑块一次小步变更和恢复，尤其BenchDepth UI单位；两个System关系/Playbook引用/四Freelance顺序。
2. **单一对手整体防守**做一次“整体/All”最小UI差分，辨别与player matchup数组的区别；`IsInUse`激活/继承不明时禁止盲写，阻断并上报。
3. 单字段安全masked写回、原值恢复（只在复制测试存档）、邻接位和其它28对手/其它29队不受影响；需要时做最短必要UI可见性校验。
4. 30队batch dry-run/内存假对象失败注入，尤其一项全局变更+单对手防守混合的跨对象rollback；最小两对象隔离局写/读/恢复就够，不必把所有30队逐个实机写一次。
5. 玩家触发数据采集、SQLite/JSON/源审计/旧latest保留/无-Publish不上传、双手册CLI一致性。正常批次发布守卫仍应保留。
6. 仅确有技术疑义（如UI编辑器缓存覆盖、游戏落盘不持久）才安排一次针对性的保存核验。**程序不得因为少测而将无法确认的内存字段误放行**：未确认的字段保持`BLOCKED`并说明原因。不能用“无需胜率测试”替代必要写入安全。

## 8. 交付和完成定义

Codex优先在现有PR#1分支接续工程并提交PR供用户审查，不自动合并main。交付：
- 源码（原生字段profile、19项全局codec/reader/受控写器、指定对手overall defense codec、1–30队批处理、采集/SQLite/JSON集成）
- `web_gm/manuals/GM_COACHING_OPERATIONS.md`
- `docs/40_COACHING_EXECUTION_RUNBOOK.md`
- `docs/development_reviews/DEV_20261017_07_COACHING_INTEGRATION_REPORT.md`
- `docs/development_reviews/DEV_20261017_07_COACHING_BATCH_ACCEPTANCE.md`
- `docs/development_reviews/DEV_20261017_07_COACHING_SOURCE_PUBLICATION_ACCEPTANCE.md`
- 已更新GM/EXECUTION/共用基线、字段矩阵和`source_catalog`；真实测试命令/结果/commit SHA。

**只有以下5项都达到技术可用，才报“教练机制完整开发完成”：**
A. 每队19项默认教练战术可安全按合法值受控修改；
B. 指定对手页面的“整体防守理念”已认证正确整体条目、独立覆盖、合法写入/回退，并供GM使用（不是借逐球员matchup冒充）；
C. 30队批次可做全队预验证、玩家逐批审批、条件rollback；
D. 正常玩家触发的数据更新和-Publish可把真实教练字段交网页GM；
E. GM手册+Codex执行手册与实际代码CLI一致并被基线引用。
**无需比赛胜率实验。** 若某字段因为缺真实映射/激活语义无法安全写入，报告`PARTIAL_BLOCKED`与明确原因，不能假称全部完成。任何工程开发授权都**不授权正式局的具体战术修改**。
