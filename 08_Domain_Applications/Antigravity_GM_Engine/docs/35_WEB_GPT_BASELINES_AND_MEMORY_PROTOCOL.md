# 网页 GPT 三基线分工、Python 分析与持久记忆协议


> [**所有网页GPT角色首先了解项目意图及范围**](PROJECT_INTENT_AND_MODEL_DEVELOPMENT_BOUNDARIES.md)：目前研究与基础建设任务是**为独立模型提供游戏原料和工具，不是开发它们的人格**。未来六阶段依次采集、数据分析、Coach、Player、GM、执行；Coach/Player人格尚未开发，现有主要是GM。DEV29 R知识研究只查玩法/数据/控制/联动，DEV28才做I/O接口，Agent人格/谈判/记忆机制由未来独立开发任务解决。下文DEV29 V3里关于“自主权、拒绝和人格”的描写只作目标与素材背景，**不能转成R系列必交的软件行为协议**。

## 2026-10-20 DEV29 V3：多角色自主涌现和R04全量球员原生数据研究

玩家确定最终系统是**30队GM、教练、球员、媒体等独立模型参与真实NBA2K22虚拟联盟**，依照各自身份、目标、记忆、风险偏好，自行选择/拒绝/谈判并根据比赛反馈不断改变；不是单一GM模型的最优策略执行机。旧BPTI篮球哲学/角色规则作为参考资料，不可剥夺独立角色的决策权。[DEV29 V3权威计划](development_tasks/DEV_20261020_29_NBA2K20_23_FRANCHISE_MECHANICS_INTELLIGENCE_PREREQUISITE_V3.md)；[R04完整球员系统研究任务书](development_tasks/DEV29_R04_PLAYER_FULL_PROFILE_AND_AGENCY_RESEARCH_SPEC_V1.md)。

研究职责增加：GM模型反推独立GM的观察、谈判与经营行动；Analytics仍负责完整逐场数据与玩家表现反馈；研究窗口收集NBA2K20–23球员个人档案、全部属性、倾向、徽章/人格徽章、伤病耐久、训练偏好、Play for Win/Loyalty/Financial Security及其玩法用途；开发基线负责Agent资料来源/读写权限/DEV28完整能力矩阵；Codex仍只做研究结束的工程索引和确定性接口交付。保持R01已结束、R02 NEXT、R03训练、R04球员、R05经营、R06世界与媒体、R07整合。

角色在游戏世界中的同意/拒绝/承诺/谈判是业务模拟，**所有现实游戏写入仍须玩家单独批准**；外部人格长期记忆优先外部SQLite，不安全重用原生字段。普通球员能力/徽章/潜力的直接修改禁令保留；只在获批的历史世界线例外中可能改变。原游戏自然成长为权威。

## 2026-10-20 DEV29 V2网页GPT长期多轮知识工程的职责覆盖

玩家确认PR #12已合并，决定让新网页GPT窗口而非Codex研究NBA2K20–23/MyLEAGUE/MyNBA的实际玩法、设置、每场/高阶统计、图文截图与机制联动；详见[DEV29 V2](development_tasks/DEV_20261020_29_NBA2K20_23_FRANCHISE_MECHANICS_INTELLIGENCE_PREREQUISITE_V2.md)。所有研究轮次必须以[docs/game_mechanics/README.md](game_mechanics/README.md)为共用仓库入口，按[PROGRESS](game_mechanics/PROGRESS.md)断点恢复，写入中文实用攻略/原生可选项候选/数据证据要求，并保留源码、图片索引与版本差异。研究主责在网页开发规划/研究GPT；GM/Analytics提供业务判据；Codex仅最终FINAL-CODEX做资料完整性、机器索引、现有数据库与DEV28开发接口的工程收尾。此前V1“R0-C由Codex作为前期资料审计主责”的流程被V2覆盖。无真实原生数据不得将`KNOWN_IN_SERIES`标为`PC22_NATIVE_READ_VERIFIED`。

版本：WEB_GPT_BASELINES_V1；建立日期：2026-10-17。**本文件专供 ChatGPT 网页版（Web GPT）使用，同时供 Codex 了解责任划分。** 不取代 Codex 已有的 `docs/32_DATA_CAPTURE_BASELINE_PROMPT.md`、`docs/33_DEVELOPMENT_BASELINE_PROMPT.md`、`docs/36_EXECUTION_BASELINE_PROMPT.md` 及共用状态 `docs/34_BASELINE_CURRENT_STATE.md`。

## 1. 项目角色（必须遵守）

- **玩家**：推进 NBA2K22 游戏时间；分别触发数据采集、GM 决策、游戏执行；对具体方案版本授予或拒绝批准；决定历史选秀进度。玩家能要求分析/开发文档工作，但不因此授予游戏写入权限。
- **Codex 数据/执行端**：Windows 本地游戏内存校准、只读来源采集、源审计、SQLite 入库、JSON/数据库 ZIP 发布，及另行授权的具体游戏执行。Codex 维护源数据生产脚本和工程实现，不能因数据发布完成就自动开启 GM 决策。
- **Web GPT · GM 决策基线**：30 队独立建队、赛季战略、比赛/阵容/战术判断、交易与选秀资产经营、老板/教练文化、历史与现实线的经营取舍；发出明确、可核实、待玩家批准的 PROPOSED 方案。**GM 决策和球队长期经营方向的责任人**。
- **Web GPT · 开发规划基线**：读取用户需求和当前代码/能力状态、提出分阶段技术方案、实现规格、Codex 任务书、代码审查/验收及缺口跟踪；默认不擅自改游戏源数据或执行引擎。**需求设计、任务下发文本和独立验收的责任人**；工程代码落地由 Codex 执行。
- **Web GPT · 数据整理分析基线**：从 GitHub 最新已发布数据读入分析环境，使用真实仓库 `src/gm_core` / `scripts/gm_*.py`（能安全执行时）和 Python/SQL 加工，形成可追溯统计、30 队量化观察、分析包及 GitHub 回写。**GM 分析加工与分析报告/JSON 发布的责任人**。Codex 只为它维护必要的采集与计算脚本，不需要每次代做 GM 经营分析。

**分离原则**：采集来源 → 分析加工 → 经营决策 → 玩家批准 → 独立游戏执行。玩家可以分别触发这些动作；分析窗口不能把数据更新解释为 GM 启动，GM 决策不能把方案提交解释为执行授权。Web GPT 的三类窗口是手动新开的聊天，彼此不自动调用、不自动同步聊天上下文，唯一可复现共享介质是 GitHub 文档与数据。

## 2. 三份网页版基线

从 `web_gm/baselines/README.md` 选择：

1. `web_gm/baselines/GM_BASELINE.md`：正式经营判断和待批准决策；
2. `web_gm/baselines/DEVELOPMENT_BASELINE.md`：需求、系统架构、Codex 规格与验收；
3. `web_gm/baselines/ANALYTICS_BASELINE.md`：数据读取、本地 Python 计算、分析数据/报告同步。

**初始化一个基线不是执行任务。** GM 的派生窗口按**游戏赛季**而非单次决策任务划分：玩家为每个赛季新开**一个 GM 决策聊天**，在同一聊天中由玩家逐次触发月度、交易截止日、季后赛、休赛期或事件节点；每个节点结束后完成文档交付并在原聊天待命，**不能把“本节点停止”理解为“关闭本赛季窗口”**。每节点最多三轮 GM 审议只是节点内部限制，不是赛季回合上限。赛季结束由玩家确认、完成收官总结后，下一赛季再开新聊天；上下文溢出需重开时作为同赛季续接。开发规划、数据分析仍可一次任务一个聊天。所有新聊天与每次新 GM 节点都应核对 GitHub 最新规则、所属 CURRENT、赛季 INDEX 和数据批次，不凭聊天缓存推断事实。

## 3. 持久记忆：GM 按赛季连续经营，节点记录与长期认知分离

目录：

```text
web_gm/memory/README.md
web_gm/memory/GM_CURRENT.md
web_gm/memory/DEVELOPMENT_CURRENT.md
web_gm/memory/ANALYTICS_CURRENT.md
web_gm/memory/gm/sessions/<run_id>.md
web_gm/memory/development/sessions/<run_id>.md
web_gm/memory/analytics/sessions/<run_id>.md
```

- 每个新工作聊天启动时：读所属基线 → 对应 `*_CURRENT.md` → 任务要求及相关链接 → 线上最新版规则/数据；GM 还读取当前赛季 `web_gm/seasons/<season_id>/INDEX.md` 与上一个节点回执。GM 同一聊天中的**每个新节点**也应核对最新来源；不要默认读取全部三基线历史。
- 每个任务或 GM 节点完成时：先将结果保存为**新的不可变任务/节点记录**（本岗位 sessions 目录，附完成/未完成/证据/来源/commit）；GM 再同步其 `web_gm/seasons/<season_id>/INDEX.md` 和所属 `GM_CURRENT.md`。历史 `Wxx/ROUND_Ryy` 是决策节点的归档编号，不再要求月度新开聊天；节点完成后**在本赛季聊天待命**，不自动做下一节点。不要把整个聊天转录复制进记忆。
- `*_CURRENT.md` 是可覆盖的精简索引，sessions 是历史证据；旧任务记录不能自动升级为已确认真相。每个事实必须有来源批次，经营主张必须注明 PROPOSED 或玩家确认状态。
- 未完成或者 GitHub 写入失败：如实说明，不能在聊天中宣称已经持久化。修改报告前检查 GitHub HEAD/目标文件 SHA；避免同名覆盖冲突与覆盖其他窗口的记录。
- 玩家没有启动游戏决策时，分析窗口可以保存 `ANALYSIS_ONLY` 数据产物，但**不能**替 GM 写出“批准的球队战略”。玩家没有批准时，GM 只记录未批准提案，不能将它并入已确认经营历史。

更多格式见 `web_gm/memory/README.md`。

## 4. 数据与分析真相规则

DEV-10 V2/M0增加玩家授权的本地命令行只读入口，见 [SQLite手册](GM_SQLITE_QUERY_ACCESS.md) 与 [消费者契约V2](../web_gm/data_contracts/CONSUMER_DATA_CAPABILITIES_V2.md)。只访问从同批审计备份生成的静态双库，不连活动saves，不把派生结果写事实。GitHub小型来源指针、报告和角色记忆继续保留。玩家在本次开发明确将三个Web实际终端连接延后到工程完成之后；不阻塞本轮实现，不代表已连接或已验收。本轮不建设派生工作台、不改变GM现行轮次或触发条件。

始终以最新有效 `published/saves/<career_id>/latest.json` 为入口，读取 `data_updated_at`、`uploaded_at`、`batch_path`、`game_date`。正常同步只依赖时间；不恢复 JSON 哈希、逐字段检查、ZIP 回下载。分析需要的源事实审计与数据语义由 Codex 源脚本处理。

- `published/` 与 Release ZIP：**游戏事实的只读来源**；网页分析不得直接修改、覆盖、伪造其中的记录，也不修改 `latest.json`。
- `docs/gm_analysis/`：Web GPT 数据整理分析基线发布的量化结果、只读研究结论、结构化 JSON；必须带 `ANALYSIS_ONLY`、`career_id`、`source_batch_id`、计算方法/版本、局限，不能写成游戏观测。
- `web_gm/memory/`：跨窗口任务记忆/索引，不是游戏观测库和玩家批准簿。
- `gm_state/`：既有 v1 本地准备与待审批协议区域，不能把网页文件自写的 `approved=true` 当作玩家批准。
- `docs/team_dossiers/`：历史文化参考；未经玩家具体批准不修改正式球队档案，不将参考剧情、预定交易或冠军视为已发生。
- `config/gameplay_policy.json` 及文档 22/26：当前已确认规则。 `config/gm_policy.json` 经营阈值仍是待玩家确认草案，不能强制用于真实球队定性。

计算必须用 Python/SQL/确定性工具；`NULL` 就是未知，不以 OVR、年龄、潜力或薪资默认值补齐。引用已观测的 55 项能力时不称其为 OVR。交易选秀权只使用每批认证的年、轮、原球队、当前持有球队；最多接下来三届游戏选秀年，不能混同 1984–2020 历史新秀轮回届次。普通球员能力/潜力/徽章/倾向不得编辑；历史重力按玩家逐项批准；MC 成长暂缓。

## 5. 代码运行及 GitHub 双向闭环：现实能力与证据

目标流程：读取 repo 代码和最新 `published/` JSON → 在当前可用 Python 环境进行确定性计算 → 网页 GPT 分析 → 将 Markdown/JSON 保存到 `docs/gm_analysis/` → GitHub Contents API 提交 → 再读取确认。

- 当运行环境允许 Git 克隆/下载文件时，检出**固定 commit**，执行项目原脚本，并记录确实执行的命令、Python 版本、文件和测试结果。
- **当前已验证的替代路径**：通过获授权的 GitHub 连接读取需要的文件/代码，将紧凑事实或实际文件放入可执行 Python 环境计算，再经 GitHub 连接提交。必须写明是「抽取输入做与仓库算法相符的本地计算」，不得谎称完成 clone 或原样执行 `gm_prepare.py`。
- 网络/本地文件环境可能在新窗口不同；任务开始时检验所用工具实际权限和路径。无法运行原脚本时，可以精确移植所需确定性计算，输出受限制的 `ANALYSIS_ONLY` 报告，或明确记载 `BLOCKED`。不得用聊天心算冒充脚本。
- 仓库文件的分析提交属于 Web GPT 分析职责，不要求 Codex 每次转发。但不能由分析提交自动触发采集、GM、游戏执行；不能把 GitHub 文件写入视为游戏状态发生改变。
- Web GPT 的开发基线可以设计修改方案并审查，而 Codex 的文档 32、33、36（共用状态为 34） 继续管理**它自己的本地数据/开发/执行基线**。名字相似不代表角色或工作窗口可以替代。

## 6. 每次分析、GM、开发的交接标准

**分析 → GM**：链接 `docs/gm_analysis/` 结果（Markdown+JSON），锁定职业存档、批次、采集时间、规则、计算版本，概述 30 队指标及未知字段。未经 GM 回合审议的生命周期只是候选值。

**GM → 玩家/执行端**：同一赛季聊天中逐节点给出逐队经营判断、跨队冲突、具体候选操作的 ID/版本/证据/双方动机/风险和需批准项；获批前保持 PROPOSED。GM 不向 Codex 发送自动执行指令，也不自动开展下个节点。

**开发 → Codex**：任务书记录改动目标、源代码入口、数据契约、禁区、测试/验收标准及不应触发的阶段；验收仅基于已提交代码和实际测试证据。

**Codex → 分析/GM**：最新合法来源批次及变更说明，保留采集/上传时间；网页窗口自行读取，不要求 Codex 重新作 GM 主观判断。

## 7. 仅文档更新的特别说明

创建或调整网页版基线、索引与分析文档，不等于触发游戏采集、GM 正式决策或执行。此协议记录职责和交接，**不新增自动化守护进程、跨模型实时共享内存或后台任务**。


## 2026-10-20 开发新前置：DEV29全系列游戏机制与能力目录

- 三份网页版基线加Codex、Antigravity共同引用：[DEV29 NBA2K20–23终极联盟机制完整研究](development_tasks/DEV_20261020_29_NBA2K20_23_FRANCHISE_MECHANICS_INTELLIGENCE_PREREQUISITE_V1.md)。用户要求**先弄清20–23系列游戏到底能看到哪些逐场和高阶数据、能设置哪些教练/训练/战术/经营动作，以及人类玩家怎样玩**；DEV29 R0-A/B/C是DEV28 D28-0～D28-5工程的正式前置知识门槛，不能以仅有现有SQLite字段目录代替。
- 研究输出：可人读`FRANCHISE_MECHANICS_ATLAS`、可机读`FEATURE_DATA_CONTROL_MATRIX`、GM反推的`GM_DECISION_TO_EVIDENCE_MATRIX`。每项标明版本/模式/资料证据/真实PC22 UI与内存/采集/GM查询/写回状态，并允许UNKNOWN；不仅给攻略知识，更直接驱动Codex和Antigravity下一步发现/开发任务。
- 网页GM负责哪些判断需要哪些数据；网页Analytics负责Game Logs/Box/Advanced基础与派生差别；网页开发负责验证技能/机制→工程需求；Codex做实际源、查询、受控执行能力矩阵；Antigravity找缺失内存。游戏修改仍需玩家具体批准，正式GM与分析不能把累计当逐场证据。
