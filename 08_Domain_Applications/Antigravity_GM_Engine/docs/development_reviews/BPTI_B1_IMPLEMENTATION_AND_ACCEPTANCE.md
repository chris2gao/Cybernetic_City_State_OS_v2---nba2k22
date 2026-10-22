# BPTI B1 — 十体系卡与知识检索实现/验收

2026-10-20。状态：**BPTI_B1_ENGINEERING_COMPLETE_AWAITING_PLAYER**。
任务：DEV25；契约：BPTI_KNOWLEDGE_V1；知识文件：BPTI_SYSTEM_CARDS_V1。
独立分支：codex/bpti-b1-system-cards；独立 Draft PR，不自动合并。
用法及内容边界：[B1手册](../BPTI_B1_SYSTEM_CARDS_AND_RETRIEVAL.md)。

## 1. B0合并与独立B1起点

玩家本次明确授权“当前PR #8可以合并，直接合并后”。
确认PR #8 head仍为已审核的538eef31615a22c4163017a58152c9bb26202d21，
随后Ready并合并，GitHub返回MERGED，合并提交e4b397e721a5b2fa91de557db5c1dc339e66f437。
重新fetch main后，干净工作树从该main建立独立codex/bpti-b1-system-cards，
没有把B1追加到旧B0分支，也没有改原目录的其他采集开发分支。

已读取最新AGENTS、政策V2、B0契约、DEV22/DEV25、R1原报告、R1审核及R4整合；
本轮不重跑B0静态审核或测试。

## 2. 实际工程交付

| 要求 | 证据 |
| --- | --- |
| 十个唯一SystemCard | web_gm/knowledge/bpti/system_cards_v1.json，沿用B0 SYSTEM_IDS和TypedDict |
| 完整篮球因果与创造力 | 每卡七段CHAIN，含入口/第一优势/回应/阅读/第二优势/再反制/失败重置；角色技能、五AGENCY、失效与人员/财务机会成本 |
| 三类观察与Box Score限制 | observable_signals用OUTCOME / MECHANISM / CONTEXT / NOT_FROM_BOX_SCORE短串，不改B0契约 |
| 来源和历史截止 | 六条R1-P-*定性机制Claim，parent_claim_id回指原R1-C-*，保留R1-S*和原文位置；原40复合Claim及91Source文件未修改 |
| 有界CLI/API | 原Knowledge.bpti()和ResearchIndex增加system/search_systems/system_coverage；gm_knowledge增加bpti-system/bpti-systems |
| GM安全投影 | 先对整卡所有Claim做B0来源/时间裁剪，再匹配角色/反制；不可用卡card=null，不回填正文、摘要或未来来源标题 |
| 既有系统复用 | 原M2入口/文件目录，未建数据库/第二套查询执行平台；未生成SystemBlueprint、M3动作或NativeBinding |
| 文档/长期状态 | B1手册/本报告，AGENTS、33、34、M2手册和B0合同增量入口 |

查询默认最多5张摘要、允许1–5，全文只按ID读取一张；无运行时R1全文读取。
篮球反制/角色标签和十家族不是八种2K原生体系的一对一映射。

## 3. 三种覆盖必须分开

实际2021-10-19视图输出：

- **SYSTEM_CARD_10_OF_10_CREATED**：10张已建立，全部使用B0契约通过研究形状校验。
- **RESEARCH_QUERY_COVERAGE = 10/10**：显式RESEARCH可读全部十张完整卡和来源。
- **GM_ELIGIBLE_COVERAGE = 6/10**：仅允许六张已提取早期定性机制的参考内容；不是十张都可用于普通GM，也不是本局球队已评估。

| 普通GM可读 | 支持范围 |
| --- | --- |
| MOTION_READ_REACT | 移动/掩护/连接/第二侧阅读；不带后来赛季助攻比例或赛果 |
| TRIANGLE_INSIDE_OUT | 早期空间三角、低位与弱侧阅读；不保证套用到当前阵容成功 |
| SPREAD_PICK_AND_ROLL | 截至2021-07-08报道可知的覆盖阅读与主动选择防守对象 |
| POINT_CENTER_ELBOW_HUB | 早期中锋传球/手递手/空切职责；Plumlee资料不冒充Jokic本人统计 |
| SWITCHABLE_PRESSURE_DEFENSE | 2019–20案例的换防/错位机制；排除后来Boston换防比例 |
| ADAPTIVE_MULTIPLE_SYSTEMS | 早期打法演化与2018–19有限多覆盖机制；排除后来人物荣誉与赛果 |

普通GM NOT_READY / RESEARCH可读的四张：

- ISOLATION_MIDRANGE_CREATION：主要复合主引含开档后表现；
- POST_HIGH_LOW：尚未提取足够明确的开档前子命题时间范围；
- TRANSITION_EARLY_OFFENSE：主要实证案例在开档后；
- DEFENSE_FIRST_RIM_PROTECTION：主要护框实证含开档后数据。

六条细粒度Claim为SUPPORTED_INTERPRETATION，未自升VERIFIED；
历史赛季用保守日历闭区间表达，不把边界日冒充事件精确日期。
具体原生字段/效果始终UNKNOWN，不因GM参考资格而变成已认证指令。

## 4. 实际最小验证：一次，仅三项

实际命令：

~~~powershell
python -B scripts/check_bpti_b1.py
~~~

实际结果：**Ran 3 tests in 0.157s — OK**，退出码0。

| 授权项 | 实际覆盖 |
| --- | --- |
| B1-T1 | 十个SYSTEM_IDS完整且唯一；B0 validate_bpti_knowledge校验；七段链、必要角色/技能、自主权、反制/第二答案、失效/成本/观察字段非空；原生绑定为空 |
| B1-T2 | 同一CLI parser/run与API按ID、CONNECTOR角色、SWITCH条件返回有界结果；超过5张拒绝；摘要不含完整链；Claim与Source能回查实际R1原文指定行；输出实际10/10/6覆盖 |
| B1-T3 | 最小合成未来事件或UNKNOWN复合Claim污染卡时整卡隐藏，搜索不泄露正文；研究仍保留材料；缺源不能升VERIFIED；批准/原生写入注入拒绝；不就绪卡仍明确UNKNOWN原生支持 |

通过后没有重跑、追加验证、旧B0/M3/DEV14集合、全项目测试、实机或比赛效果测试。
B0代码函数复用是本次实现依赖，不代表重新执行其测试集合。
临时知识文件构建脚本只用于生成本次交付文件，不是游戏或额外统计验证。

## 5. 已知限制和停止点

B1使用已归档研究及其来源索引，没有另做逐篇网络认证；
Claim/卡片文本需如实保持所声明的早期机制范围，不声称自动识别任意错误引用下的未来句子。
当前是整卡投影；不以无逐段证据的局部拼接方式宣称四张未就绪卡也已可用。
卡片没有带入后来赛果、隐藏Potential或球员未来巅峰能力，角色不能由历史名气自动确定。

所有native_binding_refs为空，查询native_support=UNKNOWN_NOT_MAPPED_B1。
CRC/具体战术动作/受益人、ACE、Tempo、51匿名倾向和3D/Calendar效果未认证；
DEV23、B2原生映射、B3三十队身份、B4自动接M3、B5演化、B6综合验收、
DEV24真实采集均未实施。V3继续有效，V4未启用，实际三十队仍UNASSESSED。

没有游戏访问、真实采集/数据发布、新档、球员能力/潜力/徽章修改或游戏内存写入。
source_catalog、正式执行能力表、采集基线32没有新增游戏能力需要登记。
B1完成后停止，等待玩家审核；下一阶段DEV23必须另行明确批准。
