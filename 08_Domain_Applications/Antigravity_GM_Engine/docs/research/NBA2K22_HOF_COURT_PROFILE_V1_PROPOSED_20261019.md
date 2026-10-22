# NBA2K22 PC本世代 — 名人堂原版基础竞技赛场配置 V1（候选）

> **2026-10-19 30队控制权澄清**：[30队玩家经营与USER/CPU球场滑块关系评估](NBA2K22_30_TEAM_USER_CONTROL_EVALUATION_V1_20261019.md)。用户拟把30队全部标为玩家经营，但这**不证明真实3D比赛所有球员都使用USER滑块**；所有原HoF USER和CPU原值与本候选分别保留，不擅自把CPU 60改为USER 52，或把所有30队设为User就当CPU栏失效。

日期：2026-10-19，Web Development。用户明确要求：以PC/PS4本世代原版Hall of Fame设置作为基线，依据可核对的Operation Sports作者数值与体验提出**一套可直接应用的全局设置组合**，用户自行体验。**这是综合来源的未实机验证组合，非任何作者已经验证的原封不动成功配置。** 本研究不实际写入游戏，所有游戏执行仍按玩家审批规则。

## 一、唯一需要覆盖的Gameplay设置（USER/CPU分别设置）

| Native setting | HoF USER→建议 | HoF CPU→建议 | 来源及可信程度 |
|---|---:|---:|---|
| Inside Shot Success | 48→**52** | 56→**60** | 次世代NBA2K22 HOF H2UKNOW在整套方案用过52/52；Eccentric作者反馈Inside60改善内线有接触终结；**52/60是不对称HoF基线的推论组合，不是原作者直接实验数值组** |
| Layup Defense Strength (Takeoff) | 50→**35** | 50→**35** | H2UKNOW次世代HOF在2022-02-25跟帖明确上下阶段都降低到35，改善勒布朗/字母哥轻接触过度投失，普通终结者仍困难 |
| Layup Defense Strength (Release) | 50→**35** | 50→**35** | 同上；原作者主帖末版曾保留Takeoff50/Release35，**跟帖修订明确两个参数均降为35** |
| Help Defense Strength | 50→**70** | 50→**70** | PS4本世代以HoF开局的IrishSalsa 70/70，**无法证明修复第三人不tag Roll Man**；另有本世代玩家提高至100仍失败 |

HoF原值来自[gu8lal8 PS4原版NBA2K22五档难度对照](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/nba-2k-basketball-sliders/920479-gu8lal8-s-competitive-sliders)；实际执行先核对Antigravity已打通的PC版本当前字段和值，不能在非HoF环境直接写为上表原值。

资料：
- [IrishSalsa HOF PS4方案引用](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/nba-2k-basketball-sliders/917042-2k22-myleague-settings-sliders)：Help Defense 70/70，明确“未列出的保持HoF默认”。
- [Eccentric NBA2K22 NG 内线改善明确回访](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/nba-2k-basketball-sliders/917100-nba-2k22-the-eccentric-edition-realistic-ng-slider-set/page10)：Inside60、Close55、Contact50观察到改善；他本人的完整套装，不可把Close55/Contact50直接用于CPU HoF原值56而称增加。
- [H2UKNOW NBA2K22 HOF](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/nba-2k-basketball-sliders/921033-nba-2k22-next-gen-settings-sliders-hall-of-fame)：次世代HoF，2月25日楼层调整Layup Defense Takeoff与Release均35，附弱终结者仍不能轻松进的反馈。
- [本世代CPU对CPU Help=100仍无弱侧轮转](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/917717-please-turn-the-help-defense-and-cutter-help-defense-back-to-were-it-was-on-release/page70)：不能保证协防70解决AI掩护责任错误。

## 二、其他所有配置保留完整原版HoF，不做无证据全局修改

- Offense其它：Close Shot、Layup、Contact Shot、Mid/3PT等USER48 CPU56维持；Shot Coverage/Timing Impact原版50/50；Pass Accuracy/Speed、Body-Up、Ball Security等维持HoF。篮下改动先只靠Inside及Layup防守两级，不影响现有三分/跳投成功判定。
- Defense其它：Driving/Inside Contact Frequency原版50/50、Jump Shot Defense Gather/Release原版50/50、Steal Success原版50/50。**不同时修改各种接触频率**。
- Attributes所有项（含Off/Def Awareness、Lateral Quickness、Speed、Strength、Rebounding、Fatigue）保留原版HoF。
- Global Tendencies所有项（Attack the Basket、Inside/Close/Mid/3PT、Backdoor Cuts、Contest等）保留原版HoF。GM赛前个人倾向另行受控设计。
- Fouls：用户实际观察正常，全部HoF原值保留。
- Movement 8项：原版HoF；中锋持球过慢另立专项，不与本次混调。
- General/Controller：原版Game Speed（PS4 HoF作者表50）、原投篮控制/真实球员命中模式、体力和伤病不变；ACE始终Offense+Defense ON。若修改滑块后UI改为Custom属正常现象，**不要设置完再次选择HoF覆盖刚刚保存的差分**。
- 不调整日历Sim Engine、不改变教练19默认/18对手整体、不修改球员个人原始能力/潜力/徽章或个人Tendency。

## 三、效果预测的证据边界

1. **主要有望改进**：普通球员合理轻度接触下的篮下终结，不至于轻度防守也基本必丢；仍要保留小后卫硬抗大中锋等低质量选择的负面结果，以及优秀终结者优势。52/60的对称/不对称组合从原版HoF出发，并非单独已验证。
2. **仍然未知**：挡拆后两人围持球者、第三人无人补防。Help70虽有PS4 HoF来源，但先例显示Help100仍无法解决原版弱侧tag/换防判断。这个缺陷可能根本无法由Gameplay协防滑块解决；不要谎称提高数值等于修复算法。GM赛前教练策略为独立方向，但原版ACE比赛时接管，用户不开发实时AI干预。
3. **潜在副作用**：更弱的Layup Defense会使玩家自己更容易上篮。若出现简单突破必进、普通球员过强，也意味着这套综合配置不可接受；应该还原已保存的HoF原值，而不是不断瞎猜新数字。

## 四、用户验证仅需一个整体印象

用户自愿使用这套有出处组合打一段正常实时比赛，之后可以直接告诉研究方：（a）篮下有人时轻度接触终结是否改善、有无过强；（b）挡拆顺下无人补防是否变化。不需要用户重复做模型猜数值小步A/B试错。最终测试判定为用户反馈后再更新文档；目前状态 PROPOSED_NOT_GAME_VALIDATED。提交文档不授权执行写入。
