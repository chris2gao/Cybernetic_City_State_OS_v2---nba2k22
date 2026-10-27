# REA阶段02｜旧游戏机制研究资料与真实Native来源交叉索引 v1

**核对范围**：游戏资料来自正式master `7742568ac677b3c16079887463f05e81cb1191ed`；新REA工具探索证据来自 `task/rea-development-exploration-01@b16e69727987f29bff5e2ee31ce82891102ab2d9`。这份**来源导航与矛盾矩阵**不等于重新独立打开所有社区/官方网址，不等于今次游戏取证。一级Game真实场景仍由Codex在新授权任务完成。

## 已经存在的机制资料（不用再次让Human口述基础攻略）

| 资料及固定Git Blob | 已存在哪些素材 | 当前可信边界 / 对本P0用途 |
|---|---|---|
| `docs/GAME_MECHANICS_RESEARCH_FIRST_DEVELOPMENT_POLICY_V1.md` @`fc438e4e944a7c969578daf5d08fcd6c45e4eda3` | 2026-10-20研究先行政策，先已有源→官方/社区→实际PC本世代Native，次世代只作机制假说 | 已获批的“游戏机制查清再开发”方法；必须按平台/模式/数据类型分层，不把文献说法直接解释为PC22原生函数 |
| `docs/game_mechanics/SOURCES.md` @`9a3cc7315ff7684075eb8174d50f1229a03ad58c` | 含2K22 PC官方手册、Operation Sports、Reddit及旧研究编号（如`SRC-0004`、`SRC-0040/41/46/48`、`SRC-0059`），很多已有平台适用性和来源不足标记 | 作为**来源发现索引**；一个长目录内的转载不等于多个独立证据，也未逐条验证里面的链接现在仍可用 |
| `docs/game_mechanics/catalogs/PLAYER_BADGES_R04_A_REFERENCE.json` @`f3902a8e3f80296a2d790b24a2b989216d18315f` | 有80 gameplay badges+20 personality candidates的研究参考，部分来自`2kfilmroom` | 文件明示 `RESEARCH_REFERENCE_NOT_NATIVE_BADGE_DICTIONARY`、原始badge native ID未知，MyPLAYER条件不能自动变成MyLEAGUE自然成长阈值；**不得默认改badge** |
| `docs/12_NATIVE_MENTORSHIP_AND_STAFF_GUIDE.md` @`ff8a8b25e86fe5e5fd6fd31f92d5d18d6e4e4ce3` | 导师对、员工效果和徽章升级的应用思路 | 存在训练师成长倍率1.8、徽章速度40%、队医伤病减少60%等**未从本次原生证据确认的数字断言**；只把它们作为待核的攻略假说，不应进入游戏常量或正式Mechanism Atlas结论 |
| `docs/39_COACHING_TACTICS.md` @`4a484b80b541d2cf79fbd2d138447d0162b73637` | 旧DEV06/V1部分POE等内存读写、UI/保存重启的历史资料，主动警告V1不能代替V2 | **已写内存且恢复**不等于识别真实原生设置函数/比赛AI消费路径；还需read-after-consumer |
| `docs/40_COACHING_EXECUTION_RUNBOOK.md` @`42eb6b1b276de95d4a6d986b7bb689169b5d6a42` | DEV07 V2的CLI、受控批次、前置检查和条件恢复；19项默认字段有既往不同等级源证据、对手整体防守已做隔离写/恢复 | 最有价值的**M2具体字段/对象归属入口**，但文件明确“正式生产采集/发布尚未运行”，不能挪用原字段写授权；先查真实原生setter/consumer而非再造旧内存执行器 |
| `docs/game_mechanics/catalogs/R05B_TRADE_PICK_ROSTER_MECHANICS_V1.json` @`58769beb2fcf0026ea03588caf03a1a449f7e039` | 16个原生交易菜单研究选项，14项roster Native布局，CBA公式为历史规则参考，有既有执行器线索 | `pc22_game_menu_directly_verified=false`、`engine_effect_status=PC22_EFFECT_UNVERIFIED`的研究行不可据此证明原生validator/commit；工资匹配公式不得无证按游戏现行规则执行 |
| `docs/37_APPROVED_TRADE_EXECUTOR.md`（本轮尚未读全文） | 名称提示既有获准交易执行器，应在今后Codex任务按固定源核验 | **没有证据声称此执行器调用原生交易函数**；作为有界实现对照，不自动重构或替换 |
| `docs/game_mechanics/RESEARCH_INPUTS_VS_AGENT_EXECUTION_BOUNDARY.md` @`5f1d5fb083cafd52e78106014dab720540d97b85` | 已明确游戏知识/角色决策/执行与批准是不同任务 | 本P0只探机制可复用性，不开发GM/Coach/Player新人格，不擅自修改旧交易执行路由 |
| `docs/game_mechanics/MECHANISM_CARD_TEMPLATE.md` @`0acd7c5d24786edf3d8d6087b0673a6ce7f30396` | 旧研究卡包含版本、菜单、Source/Visual、输入输出和执行边界 | 复用**语义研究卡的字段**，本任务Machine Atlas需额外补`Native function/ABI/thread/state/side effects`，但旧`SRC-####`不自动升级到REA代码证据 |

## 三个代表机制中真正可缩短的研究路线

### M1｜一枚自然升级徽章（Q4=A）

`旧R04徽章名字/来源`→`FRANCHISE_MENTOR::BADGE Progression/DateLastChecked`（当前REA仅**类型定义**）→`游戏真实同一玩家/导师/徽章实例`→`更新进度的函数及比较分支`→`同模式自然时间/操作前后状态`→`能否证明具体能力阈值`。如果只得到`BADGE_TUNING::SHOOTING_BADGES`中的投篮加成，那是**比赛生效规则**而非**徽章自然升级**；分类为不同mechanic，不填升级阈值。若真实自然升级根本不使用某个能力值门槛，也要允许`EVIDENCED_NO_SUCH_THRESHOLD_FOR_SCOPE`，但需要相应分支证据。

### M2｜一项实际教练攻防设置（Q5=A、Q6=B）

优先从已记录的`默认POE`或经Human已知的易观察教练Gameplan字段**自主选一项**：`UI`→`旧V2真实Native归属/字段`→`原生设置函数/消费函数`→`队伍真实策略/比赛AI应用时机`。如果旧内存修改路径只证明了`UI/Native回读`，则标`PERSISTED_ONLY`并等待比赛消费者证据。以Q6=B，未来教练函数PoC可以作为第一候选，但**只有ABI/this/线程/依赖/副作用被证实并且另获Human具体授权时**才执行。

### M3｜原生交易验证、提交和副作用（Q2=A）

从旧`R05B`、`37_APPROVED_TRADE_EXECUTOR`及市场/名单Native Reader提出路径假说：`trade menu/proposal`→`validator legality`→`commit dispatch`→`roster+contract+salary+pick+ledger/news`。既有游戏外直接写字段执行器的成功不是原生函数重用验证。必须判定每个副作用是否由原生机制或外挂单独修补完成；无法限定全部必要状态时，即使候选函数存在，仍只能`NATIVE_CALLABILITY_UNKNOWN/NOT_SAFE`。

## 来源语义三分规则

1. **攻略/原生设定背景**：社区、官方手册、旧机制研究卡用于提出`hypothesis`、菜单语义、测试用例；跨平台本世代/次世代差异必须明确。
2. **工程实物/布局证据**：当前或旧Native profile、Reader、Frida real game metadata/types、代码片段，可确认某些对象/字段候选，但不默认功能生效。
3. **原生机制完成的证据**：函数callsite、游戏正确状态、实际条件分支、前后场景与受影响业务对象、Human授权情况下的fresh readback/独立审核；没有这些不授予PoC或生产执行成熟度。

**当前来源独立性**：项目旧文档之间常引用同一官方/社区资料，不能算独立双源；Codex手册、其findings与相同run原始Evidence是**同一研究血缘**。实机独立验收仍需另有来源路线或Human游戏UI核对，无法获得时在OS证据索引标`SINGLE_ORIGIN_UNRESOLVED`而不是制造两份证据。

**边界**：本轮仅GitHub静态检索＋只读单个固定REA归档；未向任何公网玩家询问、未打开历史`SOURCES.md`里的每条URL，也未运行Codex脚本或改动Game。所有新代码/实测留以后另行授权的Codex。
