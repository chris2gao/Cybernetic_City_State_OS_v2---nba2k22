# BPTI R0 — 既有研究资产、初始来源与可执行性风险审计 V1

2026-10-20 | role=R3 Web GPT | stage=RESEARCH_SEED / NOT_FULL_R3 | 无游戏内存/测试/编码操作。

## 1. 对已开发系统的实际基线（GitHub main）

- PR #4现已实际合并（2026-10-20复查）。原M3-T产品手册：`web_gm/manuals/GM_M3_TACTICAL_WORKBENCH.md`；能力为各队教练19项读取/日常18项设置、本队已捕获68槽/真实CRC但战术含义未普遍解码、4 PlayTypes+Initiator、48具名倾向（未知51项不写）、PERSONAL_DEFENSE、训练/轮换、审批前离线稀疏意图。DEV14仍规定游戏修改必须具体玩家批准。
- M2既有12张战术卡：`docs/development_research/DEV10_M2_BASKETBALL_AND_FRANCHISE_RESEARCH_V1.md`；实际是战术原则知识种子，不等同10个完整篮球体系族群（缺系统性进攻第2/第3选择、角色创造权限、反制及团队组织演化）。
- 现有30队历史种子偏2021选秀/组织背景，不等于已根据最新存档评估30队：球员、合同、教练事实还需重新按新档批次绑定。BPTI Research可先制作历史参考和候选篮球哲学，不声称正式30队已分析。
- `docs/research/NBA2K22_TACTICAL_ECOSYSTEM_AND_PLAYER_BEHAVIOR_RESEARCH_V1.md` 已收集大量2K22社区资料，但仍存在“某种Tendency究竟控制什么”的冲突。接下来应把原生确定项、真实玩家报告、游戏机制猜想分别存档，拒绝写固定“神奇参数”。

## 2. 初步独立联网核查（资料有价值，不等于全文研究完成）

**A. FIBA/WABC教练文献**：https://about.fiba.basketball/en/wabc-documents 提供Coaches Manual和Level 1–3。适合R1获取掩护、防守覆盖、球员阅读、空间与决策的基本教练原理；该入口本身尚未支持任何特定2K22原生内存行为推断。

**B. NBA官方2014马刺/X&O**：https://www.nba.com/mavs/2014-playoff-primer-breaking-down-the-mavs-vs-spurs-xs-and-os 2014-04-19 Mavericks赛前战术分析，强调马刺快速二次转换、底角空切/射手威胁、低位、对手的退防与轮转反制等。对R1有价值的不是“他们传球好”，而是具体场景中的优势如何产生以及对手如何压制。

**C. NBA官方2022防守对抗**：https://www.nba.com/heat/heat-celtics-butler-tatum-conference-finals-preview ，2022-05-16 Heat/Celtics，明确换防针对持球挡拆和制造单打的战术背景。还可参考2022 Heat教练调整实例 https://www.nba.com/heat/news/coup-takeaways-heat-handle-cavaliers-behind-defensive-brilliance-strong-nights-from-tyler-herro-and-bam-adebayo ，2022-03-11。为R1/R2提供“主防守哲学—对手调整—特定球员”的具体案例，不要直接变成18项防守字段数值。

**D. 2K22当年官方Gameplay通报**：https://newsroom.2k.com/news/nbar-2k22-unveils-new-gameplay-innovations ，2021-08-31。证实该年3D比赛有具体进攻/防守/移动系统开发目标，不证明具体每一项原生Tendency作用机制，也不证明其对Calendar Fast-Sim与3D等价。

**E. 2K22社区实测和直接相互矛盾的经验**：
- https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/917203-nba-2k22-useful-findings ，2021-09：有人建议全部Touch=50增加角色球员参与；另一位玩家说明Touch主要作用于无固定战术的Freelance阶段、战术调用更多由PlayTypes/手册/教练决定。**不能二者均标为本项目实机认证**。
- https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/917203-nba-2k22-useful-findings/page4 ，2021-09：玩家报告战术手册中指定Holiday的ISO战术可能仍实际由Giannis受益，另有玩家报告特殊战术硬编码触发对象；与“PlayType名字=战术实际受益人”的简单映射冲突。R3必须建立 `PLAYBOOK_BENEFICIARY_UNKNOWN` 风险。
- https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/917203-nba-2k22-useful-findings/page10 ：不同玩家又报告高Shot Tendency导致过分集中 vs 即使Shot=0仍持续为两名球员叫战术。因控制变量、阵容与版本不同，属于相互冲突的玩家观察；不能把“Shot上限80”等当全联盟通用政策。
结论：**原生字段存在+字典可查 ≠ 已知实际AI调用机制。** 大部分篮球意图仍可通过可证的教练、角色和防守设置提出；无法准确映射的具体战术效果留UNKNOWN而不假称成功。

## 3. R1/R2/R3跨角色交接的具体待研究问题

- R1：不同体系如何创造机会/防守反制、球员何时应被赋予自由度、当对手改变覆盖时主副方案如何转换；尤其研究“不以中距离效率均值压制球星创造性”的有条件规则。
- R2：组织文化与教练体系脱钩；在2021开局每队有什么官方史证据，哪些只是事后印象；乔丹/奥尼尔/科比进入非原历史球队后如何演化身份（机制设计，不当现实事实）。
- R3：哪些真实篮球意图可由已证的2K22 PC现有映射执行，哪些需要CRC/PlayTypes/行为实测，哪些只是社区经验；对游戏子世代、玩家批准Tendencies修改权限及DEV14状态做逐项标注。

## 4. 实施前的最小研究汇合门

R1给10个体系卡的现实因果链；R2给30队2021历史参考和历史演化；R3给原生映射事实/假设/冲突表。整合后产出`BPTI_RESEARCH_INTEGRATION_V1`，由玩家批准启动Codex相应工程阶段。**BPTI代码开发可以早于Issue #6修复和季后赛校准器开发；真实新档采集以及第一赛季前仍需要独立处理正式来源。**

本文件是研究开局的证据审计，不是完整R3最终映射，更不是M4、BPTI或游戏执行完成的证明。
