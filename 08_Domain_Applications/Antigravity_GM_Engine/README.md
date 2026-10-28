# NBA 2K22 Antigravity 外部总经理引擎 (External GM Engine)

> **最新项目导航（2026-10-28）**：**[NBA2K22 外挂系统全项目总索引](PROJECT_INDEX.md)** → [13模块机器注册表](docs/development/PROJECT_MODULE_REGISTRY_V2.json) → [旧游戏资料库](docs/game_mechanics/README.md) → [REA经验交接](research/rea_native_control/REA_WINDOW_CONTEXT_HANDOFF_20261028.md) → [角色批量原生执行架构](docs/development/ROLE_BATCH_NATIVE_EXECUTION_ARCHITECTURE_V2.md)。**所有下一轮开发先加载导航和相关模块，完成后同步对应索引**。当前索引与架构仍在Draft PR #18，master未部署。以下旧双库物理划分/直接内存写/旧六阶段执行片段属于历史工程与数据流程描述；数据链暂不改，但执行目标已改为角色能力驱动的批量Native函数调用，具体看架构V2。



> **OS治理下的NBA2K22项目开发知识入口（2026-10-22，候选）**：[正式开发基线](docs/development/NBA2K22_PROJECT_DEVELOPMENT_BASELINE_V1.md) · [开发规划模型入口](docs/development/NBA2K22_PLANNING_MODEL_ENTRY_V1.md) · [40族能力与交付总账](docs/development/PROJECT_CAPABILITY_AND_DELIVERY_LEDGER_V1.json) · [历史开发任务索引](docs/development/NBA2K22_HISTORICAL_TASK_REGISTER_V1.json) · [16项后续工作Backlog](docs/development/NBA2K22_OS_TASK_BACKLOG_V1.json) · [文档权威/上下文恢复](docs/development/NBA2K22_DOCUMENT_AUTHORITY_INDEX_V1.md)。本业务树以OS仓库为写入目标；历史旧仓库URL只作固定SHA来源。**研究已发现/代码已实现/生产已发布/真实游戏验收分别标记**，任何进程写入及DCR本地访问均须玩家另行批准。该知识入口与业务刷新均处任务候选分支，尚未自动进入master。


> **OS 纳管状态（2026-10-22）**：本项目已正式迁入 **Cybernetic City-State OS v2** 系统，作为 `08_Domain_Applications/Antigravity_GM_Engine` 领域应用纳管。
> **新官方仓库**：[chris2gao/Cybernetic_City_State_OS_v2---nba2k22](https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22)（分支：`master`）
> **最新数据架构纲领**：[平行世界数据架构 V2 蓝图](docs/development/PARALLEL_BASKETBALL_WORLD_DATA_ARCHITECTURE_V2.md)（全面允许重构双 SQLite、采集容器与 Schema）
> **历史基准仓库**：[chris2gao/nba2k22-gm-engine](https://github.com/chris2gao/nba2k22-gm-engine)（历史 commit 证据保留）



> [**项目级开发意图（所有模型先读）**](docs/PROJECT_INTENT_AND_MODEL_DEVELOPMENT_BOUNDARIES.md)：这里的最终目标不是只有GM最优决策器：六个独立阶段为采集→数据分析→教练→球员→GM→汇总执行。**DEV29 R系列只研究游戏机制/动态事实/静态可选项/作用与联动，DEV28提供原生可用的I/O工具；教练和球员独立人格系统另立任务，不能由研究或接口工程编写规则来冒充人格。** 此文档高于下面旧版运行子流程的历史描述。

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![Platform Windows](https://img.shields.io/badge/Platform-Windows%20x64-0078D6.svg)](https://microsoft.com)
[![PyWin32](https://img.shields.io/badge/Memory%20API-PyWin32%20%2B%20ctypes-yellow.svg)]()
[![NBA 2K22 Compatible](https://img.shields.io/badge/Game-NBA%202K22%20(Steam%20%2F%20Offline)-orange.svg)]()

> **以可复核的 NBA 2K22 实测数据驱动外部 GM 建议；任何游戏或决策规则写入都由玩家批准。**

**网页版 GPT 三基线（新增，角色隔离与跨窗口持久记忆）：** [入口及初始化提示词](web_gm/baselines/README.md) · [职责/数据闭环/记忆协议](docs/35_WEB_GPT_BASELINES_AND_MEMORY_PROTOCOL.md)。网页版 GPT 分为 **GM 决策 / 开发规划 / 数据整理分析** 三个独立基线，使用 GitHub 文档与 `web_gm/memory/` 跨新聊天交接。数据整理分析端在可用 Python 环境计算并将 `ANALYSIS_ONLY` 报告/JSON 回写 `docs/gm_analysis/`；Codex 仍负责游戏数据采集、源数据库和工程实现。Codex 自身的基线为文档 32（采集）、33（开发）、36（执行），共用文档 34 的当前状态，两者不能混用。

**GM v1.0 开发入口：** [开发与验收](docs/30_GM_V1_DEVELOPMENT_AND_ACCEPTANCE.md)、[网页 GM 工作规程](web_gm/GM_DECISION_SOP.md)。`src/gm_core/` 只做离线事实准备、确定性计算和提案协议；v2/v3 预留接口，数据同步流程保持不变。

**当前同步已简化为时间方式：** 自动导出 JSON 和数据库 ZIP，上传后在 latest.json 显示 `data_updated_at` 与 `uploaded_at`。网页 GM 只看更新时间判断新旧，不做 JSON 额外检查。见 [29_SIMPLE_DATABASE_SYNC.md](docs/29_SIMPLE_DATABASE_SYNC.md)。

当前分工与玩法见 [26_GAMEPLAY_ROLES_AND_WORLDLINE_RULES.md](docs/26_GAMEPLAY_ROLES_AND_WORLDLINE_RULES.md)：Codex 本地处理数据并上传，网页 GPT 担任 GM，玩家审批后带回本地执行。起始 2021–2022，历史选秀 1984–2020 顺序轮回；正常属性成长交给游戏，历史重力逐项批准，MC 成长故事暂缓。旧自动觉醒/体系加点已停用。

**完整项目（玩家已授权公开）：** [chris2gao/nba2k22-gm-engine](https://github.com/chris2gao/nba2k22-gm-engine)。**完整数据库备份：** 对应 [GitHub Releases](https://github.com/chris2gao/nba2k22-gm-engine/releases) 中的 ZIP（联盟与球员池 SQLite）；网页阅读入口为 `web_gm/START_HERE.md` 和 `published/index.json`。数据库作为 Release 附件发布，不在 Git 文件历史中反复覆盖二进制文件。

---

> **最新架构修订（2026-10-22）**：旧双SQLite、月度表、采集脚本和容器都是可重构的第一代工程，不是平行篮球世界的设计上限。新的[完整数据架构V2](docs/development/PARALLEL_BASKETBALL_WORLD_DATA_ARCHITECTURE_V2.md)要求先确定世界线、人物/球队/比赛身份与事件/状态/历史/来源模型，再定SQLite实体、文件数、自动化管线及原库迁移；保留已验证事实、用户审批和数据安全的不变量。该修订优先于下方V1链接和旧架构说明。

> **2026-10-22 平行篮球世界架构共识**：NBA2K22保留比赛、规则状态与球员自然成长的权威地位；外挂通过**原生对象读取 → 现有双SQLite事实镜像及长期历史账本 → 独立AI角色与扩展规则 → 玩家审批后的有限执行/游戏读回**构建平行世界。五层技术架构不改变玩家确定的采集→分析→教练→球员→GM→执行六阶段。新的AG研究Decoder/fixture只是候选来源，不代表已集成生产。数据模型可与Codex验收并行设计，但正式迁移/采集发布需要独立通过验证和批准。详细见[项目级共识](docs/PROJECT_INTENT_AND_MODEL_DEVELOPMENT_BOUNDARIES.md)、[平行世界数据架构及食材成熟度](docs/development/PARALLEL_BASKETBALL_WORLD_DATA_ARCHITECTURE_V1.md)、[Native I/O蓝图V2](docs/development/NATIVE_GAME_DATA_SYSTEM_RECONSTRUCTION_AND_IO_BLUEPRINT_V2.md)及[当前状态](docs/34_BASELINE_CURRENT_STATE.md)。

## 一、当前运行数据闭环

数据初始化/更新、GM 决策和游戏执行由玩家分别触发。数据窗口先校准当前游戏进程地址，再由只读 Python 脚本抓取、清理、入库、审计、计算及按要求发布，交付后停止。玩家另行让 GM 读取该批次并开始决策；具体方案经玩家批准并带到执行窗口后才处理游戏执行。所有数值计算使用 Python/SQLite，阶段之间不自动衔接。

```
[NBA 2K22 当前进程]
       │ 每次重验 PID、模块与签名锚点；缓存失效时扫描可读内存
       ▼
[按存档隔离的数据源] ──► [确定性抽样审计 + 数据摘要] ──► [数据交付，停止]
      SQLite/JSON                    PASS 才开闸
玩家另行触发 GM → 形成方案，停止 → 玩家批准并另行触发执行
```

独立修改器和历史选秀注入模块仍在代码库中；它们属于单独功能，不能把月度采集和 GM 建议流程描述为已自动执行热写回。

当前进程访问需要 Python 执行进程有足够的 Windows 权限。本次确认 Codex 工具执行器仍未继承桌面管理员令牌：普通执行 `OpenProcess` 得到错误 5；通过 `Start-Process -Verb RunAs` 启动的管理员 PowerShell 子进程运行只读校准器成功。未来实机采集必须用管理员子进程启动实际 Python 脚本，详见 [22_DATA_SOURCE_AND_DECISION_GOVERNANCE.md](docs/22_DATA_SOURCE_AND_DECISION_GOVERNANCE.md)。

---

## 二、目录结构与文档导航

```
e:\games\NBA 2K22\Antigravity_GM_Engine/
│
├── README.md                           # 本总览文档与快速上手指南
│
├── docs/                               # 核心技术规范文档库
│   ├── 01_SAVE_READING_GUIDE.md        # 任意存档读取流程、时序与操作规范
│   ├── 02_DATA_STRUCTURE_SPEC.md       # 球队、教练、球员、控制台字节偏移全景表
│   ├── 03_MODIFICATION_MECHANISM.md    # 内存热写入、多副本同步、交易注入与新秀名单协议
│   ├── 04_GM_DECISION_ENGINE.md        # 30队老板画像、CBA劳资规则与月度交易撮合推演模型
│   ├── 05_STAFF_AND_PLAYER_GROWTH.md   # 制服组签约生态、资金池与球员战术熏陶动态成长机制
│   ├── 06_HISTORICAL_DRAFT_SYSTEM.md   # 1984起步历史选秀名单库、MC内存顺位覆盖与选秀夜纠偏
│   ├── 07_PLAYER_TENDENCY_GUIDE.md     # 球员真实倾向底层逻辑与全量字节偏移修改规范
│   ├── 08_TIMELINE_AND_EVOLUTION.md    # 2022~2026 真实大迁徙、延迟觉醒与MC哈利伯顿豁免协议
│   ├── 09_TEAM_ROSTER_CORE_PROFILES.md # 30队老板运营与“3+2决胜阵容”精细化名录
│   ├── 10_GAME_SETTINGS_AND_SLIDERS.md # 游戏全局设置、拟真滑块、关闭原生交易与防通胀防雪崩指南
│   ├── 11_HISTORICAL_GRAVITY_AND_REALITY_ENGINE.md # 历史重力法则、现实数据裁决与跨时代建队决策规范
│   ├── 12_NATIVE_MENTORSHIP_AND_STAFF_GUIDE.md # 2K原生导师系统、制服组职能与游戏自带机制赋能指南
│   ├── 13_TACTICAL_STRATEGIES_AND_BUSINESS_OPERATIONS.md # 球队攻防策略、战术手册调优与主场商业运营全景指南
│   ├── 14_TRADE_VALUATION_AND_ASSET_POOLS.md # 外部多智能体交易系统、动态价值评估模型与全联盟资产池规范
│   ├── 15_DATA_FEEDBACK_LOOP_AND_DUAL_SYNC_SYSTEM.md # 赛场数据验证机制与内外双轨协同交易架构规范
│   └── team_dossiers/                  # 30支球队官方初始化建队档案库 (30/30 全量就绪)
│       ├── 【中部赛区 5 队已就绪】
│       │   ├── 01_IND_PACERS.md        # 印第安纳步行者 (哈利伯顿未来主队/空间大核)
│       │   ├── 02_MIL_BUCKS.md         # 密尔沃基雄鹿 (字母哥卫冕争冠/利拉德剧本)
│       │   ├── 03_CLE_CAVALIERS.md     # 克利夫兰骑士 (青年三塔风暴/米切尔交易)
│       │   ├── 04_CHI_BULLS.md         # 芝加哥公牛 (风城豪门高票房/中投复兴)
│       │   └── 05_DET_PISTONS.md       # 底特律活塞 (状元康宁汉姆/乐透冲刺期)
│       ├── 【大西洋赛区 5 队已就绪】
│       │   ├── 06_NYK_KNICKS.md        # 纽约尼克斯 (麦迪逊吸金巨头/迎候布伦森)
│       │   ├── 07_BOS_CELTICS.md       # 波士顿凯尔特人 (双探花18冠执念/神级引援)
│       │   ├── 08_PHI_76ERS.md         # 费城 76 人 (恩比德MVP巅峰/西蒙斯换哈登)
│       │   ├── 09_BKN_NETS.md          # 布鲁克林篮网 (全联盟第一门票/2023大爆炸)
│       │   └── 10_TOR_RAPTORS.md       # 多伦多猛龙 (加拿大国家大盘/巴恩斯新人王)
│       ├── 【太平洋赛区 5 队已就绪】
│       │   ├── 11_LAL_LAKERS.md        # 洛杉矶湖人 ($500天价票与6600万金库/里夫斯觉醒)
│       │   ├── 12_GSW_WARRIORS.md      # 金州勇士 (硅谷大通中心票房神话/2022总冠军)
│       │   ├── 13_LAC_CLIPPERS.md      # 洛杉矶快船 (首富鲍尔默金元帝国/卡乔健康管理)
│       │   ├── 14_PHX_SUNS.md          # 菲尼克斯太阳 (萨沃尔到伊什比亚/杜兰特大交易)
│       │   └── 15_SAC_KINGS.md         # 萨克拉门托国王 (小萨博尼斯大交易/点亮光剑破荒)
│       ├── 【西北赛区 5 队已就绪】
│       │   ├── 16_DEN_NUGGETS.md       # 丹佛掘金 (约基奇三双大核/2023总冠军王朝基石)
│       │   ├── 17_MIN_TIMBERWOLVES.md  # 明尼苏达森林狼 (华子超巨爆发/戈贝尔世纪交易)
│       │   ├── 18_OKC_THUNDER.md       # 俄克拉荷马雷霆 (SGA超神觉醒/普雷斯蒂15首轮帝国)
│       │   ├── 19_UTA_JAZZ.md          # 犹他爵士 (安吉资产收割/马尔卡宁神箭觉醒)
│       │   └── 20_POR_TRAIL_BLAZERS.md # 波特兰开拓者 (西蒙斯干拔接班/利拉德2023离队剧本)
│       ├── 【西南赛区 5 队已就绪】
│       │   ├── 21_DAL_MAVERICKS.md     # 达拉斯独行侠 (东契奇魔术控场/欧文加盟总决赛)
│       │   ├── 22_MEM_GRIZZLIES.md     # 孟菲斯灰熊 (莫兰特空中飞人/小贾伦DPOY防守)
│       │   ├── 23_HOU_ROCKETS.md       # 休斯顿火箭 (申京欧洲步策应/格林闪电爆发)
│       │   ├── 24_NOP_PELICANS.md      # 新奥尔良鹈鹕 (锡安内线坦克/琼斯锁头防守)
│       │   └── 25_SAS_SPURS.md         # 圣安东尼奥马刺 (波波维奇纪录/静候2023文班亚马)
│       └── 【东南赛区 5 队已就绪】
│           ├── 26_MIA_HEAT.md          # 迈阿密热火 (热火铁血文化/绝境巴特勒黑八奇迹)
│           ├── 27_ATL_HAWKS.md         # 亚特兰大老鹰 (特雷杨超远引力/穆雷后场双枪)
│           ├── 28_ORL_MAGIC.md         # 奥兰多魔术 (长臂铁锁阵/2022状元班凯罗)
│           ├── 29_CHA_HORNETS.md       # 夏洛特黄蜂 (三球空接Showtime/2023榜眼米勒)
│           └── 30_WAS_WIZARDS.md       # 华盛顿奇才 (库兹马单打/2023拆队彻底推倒)
│
├── database/                           # 本地标准化数据底座
│   ├── schema.sql                      # SQLite 关系型数据库建表 DDL
│   ├── saves/<save-id>/                # 每局独立数据库、球员池、审计、备份和报告
│   ├── templates/save_template.json    # 新局稳定默认规则
│   ├── league_state.sqlite             # 旧版共享库（兼容路径）
│   ├── league_snapshot.json            # 格式化全联盟 JSON 快照数据
│   └── trade_reports/                  # 历次月度 GM 交易与战术决策公报 (Markdown)
│
└── src/                                # 核心源码实现
    ├── config.py                       # 偏移量字典、体系枚举与能力值换算公式
    ├── memory.py                       # 默认只读的 Win32 进程访问；写入需显式授权
    ├── scanner.py                      # 30 支核心现役球队与焦点球员通用定位器
    ├── dumper.py                       # 一键全联盟状态提取与入库 CLI
    ├── modifier.py                     # 属性、倾向、球星专属互动与交易开关修改器
    ├── gm_engine.py                    # 从只读数据库生成带审计状态的 GM 候选建议
    ├── growth_engine.py                # 球员动态战术成长与制服组签约模拟引擎
    ├── draft_engine.py                 # 历史选秀名单生成、内存注入与选秀夜纠偏工具
    ├── slider_manager.py               # 全局设置、关闭AI交易、12分钟单节与拟真伤病内存锁写工具
    ├── strategy_manager.py             # 球队攻防策略(POEs)、战术手册与门票物价经济实机管理器
    ├── trade_engine.py                 # 外部动态交易评估与多智能体谈判撮合引擎
    ├── init_database.py                # 21 张规范化数据表迁移初始化工具
    ├── bootstrap_new_game.py           # 创建/复用独立新局数据库；游戏写入需显式批准
    ├── save_context.py                  # 模板创建、save-id 校验与数据路径隔离
    ├── address_calibrator.py            # 每次抓取前动态校准内存锚点
    ├── auto_pipeline_ingest.py          # 严格读取、清理并落库
    ├── audit_sampling.py                # 摘要绑定的确定性脚本审计
    ├── snapshot_integrity.py             # 批次数据摘要和原子 JSON 输出
    ├── monthly_data_collector.py       # 已停用的旧采集器（防止绕过地址校准和批次审计）
    ├── market_pool_engine.py           # 已停用的旧市场模型（含未验证硬编码交易）
    ├── monthly_pipeline.py             # 已停用的旧内存写入决策脚本
    ├── season_rules.py                 # 从新局模板加载并校验赛季规则
    ├── verify_system_integrity.py      # 只检查源码和内存 SQLite schema，不打开游戏或正式数据库
    └── run_monthly_cycle.py            # 数据专用：备份→抓取→审计→报告，等待玩家
```

---

## 三、项目规范文档导航

当前执行规则由 [22_DATA_SOURCE_AND_DECISION_GOVERNANCE.md](docs/22_DATA_SOURCE_AND_DECISION_GOVERNANCE.md) 统领；新局和月度流程细节见文档 18 与 21。文档 16 和 19 是历史/未来方案，不代表现行自动化能力。

**新窗口只需从这里开始：** [27 数据初始化与更新](docs/27_DATA_WINDOW_RUNBOOK.md)；[28 已批准方案执行](docs/28_EXECUTION_WINDOW_RUNBOOK.md)。两份文档均含可复制的任务提示词。

* 📖 **[01_SAVE_READING_GUIDE.md](file:///e:/games/NBA%202K22/Antigravity_GM_Engine/docs/01_SAVE_READING_GUIDE.md)**
  详细阐述了读取任意存档（MC/终极联盟）的 5 阶段执行顺序，解释了为什么必须进入存档后读取，以及如何以零性能损耗提取数据。
* 📖 **[02_DATA_STRUCTURE_SPEC.md](file:///e:/games/NBA%202K22/Antigravity_GM_Engine/docs/02_DATA_STRUCTURE_SPEC.md)**
  最详尽的字节级数据字典：包含球队步长 `0x1258`、球员步长 `0xDF0`、现役球队过滤掩码、主教练 8 大战术体系枚举、40+ 项攻防属性、战术角色分配与性格位域。
* 📖 **[03_MODIFICATION_MECHANISM.md](file:///e:/games/NBA%202K22/Antigravity_GM_Engine/docs/03_MODIFICATION_MECHANISM.md)**
  修改注入与防崩指南：剖析 2K22 内存“多副本缓存”陷阱与终极广播解决方案、挂载超巨专属被动动作（库里抖肩、利拉德看表等）、MyLEAGUE 强制交易过审与 MC 模式真实历史选秀名单“偷梁换柱”注入协议。
* 📖 **[04_GM_DECISION_ENGINE.md](file:///e:/games/NBA%202K22/Antigravity_GM_Engine/docs/04_GM_DECISION_ENGINE.md)**
  外部 GM 决策大脑规范：30 队老板人格与建队哲学矩阵、争冠/重建生命周期状态机、超巨引力法则、主帅下课换帅机制与 CBA 薪资配平。
* 📖 **[05_STAFF_AND_PLAYER_GROWTH.md](file:///e:/games/NBA%202K22/Antigravity_GM_Engine/docs/05_STAFF_AND_PLAYER_GROWTH.md)**
  制服组生态与动态战术成长规范：主帅/助教/神医/球探签约模型、MC 模式休赛期节点介入、以及球员在体系熏陶下的异变（如乔丹打跑轰进化出三分）。
* 📖 **[06_HISTORICAL_DRAFT_SYSTEM.md](file:///e:/games/NBA%202K22/Antigravity_GM_Engine/docs/06_HISTORICAL_DRAFT_SYSTEM.md)**
  历史选秀名单与 MC 模式接管机制：1984 钻石一代起步、60 槽位内存偷梁换柱覆写、以及选秀夜大交易纠偏协议。
* 📖 **[07_PLAYER_TENDENCY_GUIDE.md](file:///e:/games/NBA%202K22/Antigravity_GM_Engine/docs/07_PLAYER_TENDENCY_GUIDE.md)**
  球员真实倾向底层逻辑与全量字节偏移修改规范：Operation Sports ATD 真实 NBA 追踪数据换算公式、99 项底层倾向偏移表与打磨验证流程。
* 📖 **[08_TIMELINE_AND_EVOLUTION.md](file:///e:/games/NBA%202K22/Antigravity_GM_Engine/docs/08_TIMELINE_AND_EVOLUTION.md)**
  2022~2026 真实大迁徙与球员觉醒时间线：阐述“交易前角色球员、交易后觉醒超巨”的延迟觉醒机制、六大交易窗口、以及玩家 MC 角色哈利伯顿的专属豁免协议。
* 📖 **[09_TEAM_ROSTER_CORE_PROFILES.md](file:///e:/games/NBA%202K22/Antigravity_GM_Engine/docs/09_TEAM_ROSTER_CORE_PROFILES.md)**
  30 支球队核心运营画像与精细化调整名录：确立“3+2 决胜五人组”架构（2 当家核心 + 1 爆发潜力星进行深层重构；2 战术拼图修正赛场倾向），全面指引老板决策与实机比赛体验。
* 📖 **[10_GAME_SETTINGS_AND_SLIDERS.md](file:///e:/games/NBA%202K22/Antigravity_GM_Engine/docs/10_GAME_SETTINGS_AND_SLIDERS.md)**
  游戏全局设置与拟真滑块权威指南：系统阐述为什么必须彻底关闭游戏原生 AI 交易、调校“高频轻伤、极低大伤”伤病体系、抑制“全联盟评分通胀”、建立健康合同与自由市场、以及更衣室防雪崩死亡螺旋策略。
* 📖 **[11_HISTORICAL_GRAVITY_AND_REALITY_ENGINE.md](file:///e:/games/NBA%202K22/Antigravity_GM_Engine/docs/11_HISTORICAL_GRAVITY_AND_REALITY_ENGINE.md)**
  历史重力法则、现实数据裁决与跨时代建队决策规范：阐述“赛场实战为王、赢球才是硬道理”的终极裁决准则；确立历史冠军重力场与现实打破机制；剖析 1984 乔丹等跨时代新秀在现代小球体系下的战术改造、非公牛球队文化冲突与巨星逼宫交易；建立 2K 历史名单版权缺失补偿协议；以及制服组四大职能（训练师、队医、CFO、教练）对球员成长、伤病防御与商业运营的实机赋能体系。
* 📖 **[12_NATIVE_MENTORSHIP_AND_STAFF_GUIDE.md](file:///e:/games/NBA%202K22/Antigravity_GM_Engine/docs/12_NATIVE_MENTORSHIP_AND_STAFF_GUIDE.md)**
  2K 原生导师系统、制服组职能与游戏自带机制深度赋能指南：坚决奉行“最大化利用游戏自带底层引擎”原则；深度解析 2K 原生“球员导师系统 (Player Mentorship)”运作机理、徽章传承与倾向同化；确立 30 支核心球队经典老将导师配对矩阵；明确训练师真正决定游戏内成长速率、队医真正削减伤病概率与天数、CFO真正影响门票与签约；制定 GM 阵容构建与制服组补强铁律。
* 📖 **[13_TACTICAL_STRATEGIES_AND_BUSINESS_OPERATIONS.md](file:///e:/games/NBA%202K22/Antigravity_GM_Engine/docs/13_TACTICAL_STRATEGIES_AND_BUSINESS_OPERATIONS.md)**
  球队攻防策略、战术手册调优与主场商业运营全景指南：深度解析并调校 2K 底层球队攻防重点 (POEs)——进攻节奏、快攻推进、冲抢前板、贴身施压、无球盯防、挡拆沉退/冰封/无限换防与弱侧轮转；剖析主帅战术手册 Plays 编号与球员 4 阶战术角色、实战倾向的共振联动；全量解密场馆分级票价（场边/下层/上层/包厢）、餐饮周边特许物价与球迷上座率弹性联动模型；实现月度技战术与商业齿轮的完美运转。
* 📖 **[14_TRADE_VALUATION_AND_ASSET_POOLS.md](file:///e:/games/NBA%202K22/Antigravity_GM_Engine/docs/14_TRADE_VALUATION_AND_ASSET_POOLS.md)**
  外部多智能体交易系统、动态价值评估模型与全联盟资产池规范：构建五大球员资产池（自有在册、自由球员、货架筹码、新秀池、未来首轮签库）与制服组资产池；制定客观量化评估模型（即战力、年龄衰减、潜力溢价、合同红利/毒药惩罚、选秀权分级量化）；确立两大老板基于生命周期（争冠/重建/上升/平庸）的主观博弈与双赢撮合公式；明晰五大交易否决红线（非卖品、CBA超标、毒药无补偿、位置拥堵、宿敌税），提供最真实严肃的联盟交易生态。
* 📖 **[15_DATA_FEEDBACK_LOOP_AND_DUAL_SYNC_SYSTEM.md](file:///e:/games/NBA%202K22/Antigravity_GM_Engine/docs/15_DATA_FEEDBACK_LOOP_AND_DUAL_SYNC_SYSTEM.md)**
  赛场数据验证机制与内外双轨协同交易架构规范：建立“战术假设 $\rightarrow$ 内存注入 $\rightarrow$ 实战运行 $\rightarrow$ 数据验收复盘”四步量化验证闭环；深入论证并确立“外部战略大脑总账本 + 内部实机热写入执行”的内外双轨协同黄金架构；明晰球员非卖品与货架筹码 (Trade Block) 的动态轮转机理与每月 GM 标准化操作流程 (SOP)。
* 📖 **[16_MONTHLY_MULTI_DIMENSIONAL_DECISION_PIPELINE.md](file:///e:/games/NBA%202K22/Antigravity_GM_Engine/docs/16_MONTHLY_MULTI_DIMENSIONAL_DECISION_PIPELINE.md)**
  全联盟 30 支球队 6 维度月度决策自动化流水线规范：涵盖生命周期状态机重估、教练帅位安全指数、战术策略 POE 针对微调、上座率票价调控、多边大交易撮合与内存原子写入。
* 📖 **[17_MULTI_SEASON_DATABASE_AND_MODELING_SPEC.md](file:///e:/games/NBA%202K22/Antigravity_GM_Engine/docs/17_MULTI_SEASON_DATABASE_AND_MODELING_SPEC.md)**
  多赛季标准化时序数据库与战略建模全景规范：21 张规范化数据表架构；保障横跨几十个赛季（2022~2050+ 或历史重构）的动态演进数据同构性；双阶段建模引擎（赢球路线审计 + 技战术软肋诊断 + 补强引援决策）。
* 📖 **[18_NEW_GAME_SOP_AND_SYSTEM_VERIFICATION.md](file:///e:/games/NBA%202K22/Antigravity_GM_Engine/docs/18_NEW_GAME_SOP_AND_SYSTEM_VERIFICATION.md)**
  新局模板创建、月度采集/审计/GM 闭环及当前已知校验边界。
* 📖 **[19_MONTHLY_GM_TURN_BASED_SOP.md](file:///e:/games/NBA%202K22/Antigravity_GM_Engine/docs/19_MONTHLY_GM_TURN_BASED_SOP.md)**
  月度 GM 交互方案说明；自动聊天驱动和游戏内回写仍属于规划内容，当前实际入口见快速上手。
* 📖 **[20_HISTORICAL_DRAFT_POOL_AND_INJECTION_SPEC.md](file:///e:/games/NBA%202K22/Antigravity_GM_Engine/docs/20_HISTORICAL_DRAFT_POOL_AND_INJECTION_SPEC.md)**
  历史球员池数据结构、raw 0x70 新秀分类和目标槽位注入边界说明。
* 📖 **[21_DATA_CAPTURE_AND_SAVE_TEMPLATE.md](file:///e:/games/NBA%202K22/Antigravity_GM_Engine/docs/21_DATA_CAPTURE_AND_SAVE_TEMPLATE.md)**
  数据源自动抓取、地址重验、失败关闭、批次摘要、制服组原始记录隔离和每局模板数据库规程。
* 📖 **[22_DATA_SOURCE_AND_DECISION_GOVERNANCE.md](file:///e:/games/NBA%202K22/Antigravity_GM_Engine/docs/22_DATA_SOURCE_AND_DECISION_GOVERNANCE.md)**
  数据真实性、地址重校准、Python 数值计算、只读 GM、玩家审批及当前实测状态的总规范。
* 📖 **[23_RESTART_CAPTURE_VERIFICATION.md](docs/23_RESTART_CAPTURE_VERIFICATION.md)**
  实际重启后的地址变化、全扫描恢复、入库审计、缓存复用及重启前后数据比较证据。
* 📖 **[24_DATA_SOURCE_REGISTRY_AND_PLAYER_TRIGGERS.md](docs/24_DATA_SOURCE_REGISTRY_AND_PLAYER_TRIGGERS.md)**
  玩家主动触发的数据更新、完整来源清单、当前缺口与独立数据窗口。
* 📖 **[25_GITHUB_AND_WEB_GM_PROTOCOL.md](docs/25_GITHUB_AND_WEB_GM_PROTOCOL.md)**
  GitHub 仓库、审计数据库归档、网页阅读包、固定版本读取与 GM 审批协议。

---

## 四、快速上手使用说明 (Quick Start)

### 一次性任务窗口与常驻基线

- [数据采集基线完整提示词](docs/32_DATA_CAPTURE_BASELINE_PROMPT.md)：关键词、内存/数据库入口、采集范围与结束边界。
- [迭代开发基线完整提示词](docs/33_DEVELOPMENT_BASELINE_PROMPT.md)：架构、开发流程、验证边界与文档维护。
- [批准方案执行基线完整提示词](docs/36_EXECUTION_BASELINE_PROMPT.md)：玩家批准清单、实时对象/原值、写入与回读、失败/重复执行处理。
- [三类基线共用当前状态](docs/34_BASELINE_CURRENT_STATE.md)：已实现功能、关键词映射、来源缺口与执行能力表。

玩家可分别建立采集、开发、执行三个只读初始化的基线对话，再另开一次性任务窗口；每个任务从文件读取最新版。当前脚本仍是全量更新，单来源独立生产更新尚未实现；执行也只使用实际已验收且获具体批准的能力，不能凭提示词声称任意修改已支持。

### 1. 环境准备
* 支持 Windows 10 / 11 64 位操作系统；
 * Python 3.10+ 与 `pywin32`（`win32process`、`win32api`、`win32con`）；SQLite 使用 Python 标准库。

### 2. 新开游戏存档
启动游戏进入目标存档后，给这局分配一个唯一 ID：

```powershell
python src/bootstrap_new_game.py --save-id my_career_01
```

默认初始化只完成数据源校准、采集并审计基线快照，不修改游戏。只有玩家明确批准本次初始设置后，才额外传入 `--approve-game-writes` 应用比赛设置和球队策略。重复使用相同 ID 不会重置数据库；开另一局必须选择不同 ID。

实际运行 Python 的进程必须以与游戏相同或更高的 Windows 权限级别启动。错误 5 代表没有抓取到数据，不能继续 GM 决策。

### 3. 月度数据采集与 GM 建议
每次推进到要复盘的节点时使用同一 ID：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts\run_data_update.ps1 -SaveId mc_haliburton_2021 -GameDate 2021-11-20 -Season 2022 -Month 1 -Event checkpoint -Name NOV20_CHECKPOINT -GamesOnDateComplete -Publish -NewWindow
```

玩家主动触发后，任务在独立终端完成 UAC 提权、只读采集、隔离数据库入库、审计、Python 计算/差异、网页 JSON 导出及独立复核；`-Publish` 将通过验证的阅读包和数据库 ZIP 同步到配置的 GitHub 仓库，省略则保留本地。当前玩家已授权公开仓库及本次数据发布。`-NewWindow` 为单独的无模型数据窗口。每次替换 GameDate、Event 与 Name；示例为玩家确认的 11 月 20 日日终，非月末。当前工资规则只支持 2021-2022。游戏写入与正式球队决策变更仍须玩家批准。

底层只读权限检查仍可使用 `scripts/run_admin_data_capture.ps1 -CalibrationOnly`。`run_data_update.ps1` 不按现实日历或游戏重启自动运行。

`-RescanOnly -SaveId <已采集存档ID>` 使用临时缓存模拟 PID 变化，测试生产校准器重新扫描，并逐条比较该存档的球员 BLOB 与实时内存；不改正式运行时缓存。真实重启验证记录与步骤见 [23_RESTART_CAPTURE_VERIFICATION.md](docs/23_RESTART_CAPTURE_VERIFICATION.md)。

---

## 五、核心关键突破

1. **球队 ID 校准：**
   现役 30 队使用 ID 集合 `{0..6, 8..29, 31}`；全明星保留 ID 7 和 30 不计入。校准要求完整 ID 集合，避免把球队数量或队伍映射误报为通过。
2. **当前内存访问依赖：**
   `memory.py` 默认使用只读句柄；写入入口单独授权。管理员启动器已通过完整采集。一次实际游戏重启（PID 5224 → 1608）后的自动全扫描、入库审计和新缓存重复采集已验证通过；证据见 [23_RESTART_CAPTURE_VERIFICATION.md](docs/23_RESTART_CAPTURE_VERIFICATION.md)。
3. **历史新秀数据与目标注入分开：**
   球员池查询按 `raw_struct[0x70] & 0xE0 == 0xE0` 筛选并排重。目标选秀槽位注入接口尚未验证完成，文档不把候选查询等同于已经能在 MC 中自动覆盖名单。
