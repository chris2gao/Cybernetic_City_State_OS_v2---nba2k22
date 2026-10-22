# BPTI B1 — 十体系知识卡与有界检索

工作包B当前增量见[B2/B3手册](BPTI_B2_B3_NATIVE_BINDINGS_AND_TEAM_IDENTITIES.md)：原卡文件不变；四个NOT_READY整卡仍封闭，但可通过四个早期细粒度mechanism_entries得到GM_ELIGIBLE_MECHANISM_ONLY。当前入口覆盖10/10，完整卡仍6张；原生绑定关联在查询结果native_binding_refs，不能把参考入口当完整行为认证。下表描述B1原阶段。


2026-10-20。文件版本 BPTI_SYSTEM_CARDS_V1，复用 BPTI_KNOWLEDGE_V1。
权威任务：[DEV25](development_tasks/DEV_20261020_25_BPTI_B1_SYSTEM_CARD_IMPLEMENTATION_AND_CODEX_MODEL_GUIDE_V1.md)。
运行证据与交付状态见[B1验收报告](development_reviews/BPTI_B1_IMPLEMENTATION_AND_ACCEPTANCE.md)。

PR #8已获玩家本次明确合并授权，合并提交 e4b397e721a5b2fa91de557db5c1dc339e66f437。
本阶段从该最新main建立独立 codex/bpti-b1-system-cards；不追加到旧B0分支。
V3继续有效，GM V4未启用；以下是知识工具，不是正式经营任务。

## 1. 实际知识文件

[system_cards_v1.json](../web_gm/knowledge/bpti/system_cards_v1.json)含十张独立SystemCard和六条细粒度Claim。
每张使用B0原TypedDict，无额外DTO字段；十家族组合使用，不是固定球队模板。

每张卡有完整七段优势链、带必要技能的角色列表、五种AGENCY、对手反制、第二答案、
失效条件、阵容/财务机会成本、观察限制、Claim引用及空native_binding_refs。
防守卡的defensive_counter_options描述对方进攻如何反制；不是防守enum表。
球员自主职责仍是SCRIPTED_ENTRY / STRUCTURED_READ / CREATIVE_OPTION /
BAILOUT_RIGHT / RESET_RIGHT，不能编译为原生五个开关。

observable_signals沿用list[str]，采用稳定前缀：

- OUTCOME：比分、助攻、失误等结果；不自动证明篮球因果。
- MECHANISM：覆盖、传球链、掩护/切入等机制；须有真实回合/影像/跟踪证据。
- CONTEXT：人员、空间、对手、接球位置等上下文。
- NOT_FROM_BOX_SCORE：明确哪些行为不能从Box Score单独推断。

卡片描述应观察什么，不声称本局已采集这些指标或知道其效果量。

## 2. CLI与API：先摘要，再按ID读取一张

沿用 scripts/gm_knowledge.py。原search/show/franchise/rules与B0子命令继续保留。

~~~powershell
# 一次读取一张普通GM可用卡；显式给游戏日期
python -B scripts/gm_knowledge.py bpti-system --system-id MOTION_READ_REACT --as-of 2021-10-19

# 有界摘要，按体系ID、角色或反制条件查询
python -B scripts/gm_knowledge.py bpti-systems --system-id SPREAD_PICK_AND_ROLL --as-of 2021-10-19 --limit 1
python -B scripts/gm_knowledge.py bpti-systems --role CONNECTOR --as-of 2021-10-19 --limit 2
python -B scripts/gm_knowledge.py bpti-systems --counter SWITCH --as-of 2021-10-19 --limit 2

# 开发研究可显式读取尚未满足GM历史条件的卡和其永久出处
python -B scripts/gm_knowledge.py bpti-system --system-id ISOLATION_MIDRANGE_CREATION --audience RESEARCH
python -B scripts/gm_knowledge.py bpti-claim --claim-id R1-P-MOTION_PRE2021 --audience RESEARCH
python -B scripts/gm_knowledge.py bpti-source --source-id R1-S02 --audience RESEARCH
~~~

示例不是额外执行授权；实际运行的检查仅见验收报告。
API：

~~~python
index = Knowledge("web_gm/knowledge").bpti()
index.system("MOTION_READ_REACT", as_of=player_game_date)
index.search_systems(role="CONNECTOR", counter="SWITCH", limit=2, as_of=player_game_date)
index.system_coverage(as_of=player_game_date)
~~~

search_systems / bpti-systems只返回system_id、title、角色与反制短标签、Claim ID和可用状态。
默认最多5张摘要，可选1–5，超过限制拒绝；truncated提示未显示完，可用具体ID再钻取。
它不dump十张完整卡，也不在查询时读取R1全文。查询只读小型知识JSON，不接游戏/数据库。

角色使用PRIMARY_CREATOR、SECONDARY_CREATOR、CONNECTOR、POST_HUB、
MOVEMENT_SHOOTER、CUTTER等可组合标签；匹配不区分大小写，也可输入描述片段。
反制标签如SWITCH、BLITZ、DENY、TOP_LOCK、FRONT_POST、FIVE_OUT，同样只是篮球条件。
过滤会先裁剪GM可用性，再匹配文本，不从被屏蔽卡回填角色或反制摘要。

## 3. 研究覆盖与GM覆盖分开

在2021-10-19视图下，预期范围由实际system_coverage和三项检查记录确认：

| 体系 | 普通GM内容 |
| --- | --- |
| MOTION_READ_REACT | 截止日前移动、掩护、传球与读防守的定性机制 |
| TRIANGLE_INSIDE_OUT | 早期三角空间、高低位、入口与弱侧阅读 |
| SPREAD_PICK_AND_ROLL | 截至2021-07-08报道可知的挡拆/DHO覆盖阅读 |
| POINT_CENTER_ELBOW_HUB | 2019–20及此前前场中轴、手递手与切入职责 |
| SWITCHABLE_PRESSURE_DEFENSE | 2019–20换防、错位及应对的定性机制 |
| ADAPTIVE_MULTIPLE_SYSTEMS | 早期打法演化与2018–19有限方案的适应原则 |
| ISOLATION_MIDRANGE_CREATION | NOT_READY；R1主引含开档后赛季表现，保留RESEARCH |
| POST_HIGH_LOW | NOT_READY；复合来源尚未拆出足够明确的开档前时间边界 |
| TRANSITION_EARLY_OFFENSE | NOT_READY；R1主要实证案例在开档后，保留RESEARCH |
| DEFENSE_FIRST_RIM_PROTECTION | NOT_READY；R1主要护框实证含开档后数据，保留RESEARCH |

这是卡片级别的全有或全无投影，不做没有逐段证据绑定的片段拼接。
普通GM可读的六张也只是在陈述篮球原理/推论，不是逐命题VERIFIED、2K22效果或真实球队评估。
四张NOT_READY仍已完整建立，显式RESEARCH可读取；不是篮球思想无效或已证不能使用。

## 4. 来源、时间和不泄露

B0的91 Source / 40复合Claim原文件保持不变；六条R1-P-*细粒度Claim位于新卡文件。
Knowledge.bpti()把它们按需合入原ResearchIndex；无第二份权威来源或数据库。
新Claim以parent_claim_id回指R1-C-*，保留原文行定位和永久R1-S*源。
卡片本身的evidence_claim_ids只引用相应合法机制提取；四张未就绪卡继续引用B0 UNKNOWN复合Claim。

六条均为SUPPORTED_INTERPRETATION，不批量升VERIFIED。
时间字段是据归档历史赛季采用的保守闭区间，年初/年末是范围界限，不冒充某场比赛精确日期。
挡拆Claim用R1审核明确记录的2021-07-08公开报道日期作为可知见证点。
retrospective_only明确只提取早期机制；不带后来冠军、交易、职业结局或隐藏潜力。
POINT_CENTER引用Plumlee传球材料只支持中锋传球职责，不把它当作Jokic个人表现证据。

普通GM有效历史截止仍为min(玩家日期, 2021-10-19)。
任一支持Claim为未来、UNKNOWN、缺源或时间不清，整卡返回NOT_READY、card=null及不含正文的阻断原因。
显式RESEARCH可以查全文和Source永久URL。GM保留稳定ID/原文位置，沿B0规则隐藏可能透露未来的来源标题/URL。

这是一套如实编写、来源约束的知识消费合同，不声称用语义分类器自动识别任意作者
在错误引用下写入的未来句子；卡片/Claim文本必须保持所声明的早期机制范围。
B1没有重新访问并逐篇认证所有外文网页，不把研究接收状态当作新认证。

## 5. 原生支持与停止点

所有卡native_binding_refs为空，所有查询明确native_support=UNKNOWN_NOT_MAPPED_B1。
Triangle名字不等于已认证原生Triangle战术包；Motion、Point-Center也没有固定一对一原生体系。
CRC、实际受益人、ACE、Tempo语义、51未知倾向及3D/Calendar效果仍未证。
卡片不生成原生值、地址、游戏修改、批准、SystemBlueprint或M3 D1–D6动作。

已更新BPTI合同索引、M2手册、AGENTS、开发基线33和共享状态34。
本次没有真实采集/发布、游戏访问、能力/潜力/徽章修改或正式GM。
B1完成后停下。下一阶段是DEV23，必须等玩家审核并另行明确批准。
