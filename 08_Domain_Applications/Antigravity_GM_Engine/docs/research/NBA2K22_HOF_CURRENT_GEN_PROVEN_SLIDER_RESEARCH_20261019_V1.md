# NBA2K22 PC本世代名人堂赛场问题 — 有来源的成功经验研究 V1

日期：2026-10-19；Web Development。**最高优先用户指令**：所有用户此前亲自打的几十场实时比赛都以**原版名人堂（Hall of Fame, HoF）参数**为基础；今后研究和可能的差分必须保留HoF原始基线，不能让玩家从Pro/All-Star套装重来。**用户不参加模型提出的任意小幅A/B数值试错**：Web Development责任是主动检索玩家已亲自试过、明确报告结果的真实2K22来源，分辨平台/难度/改动原因、成功与失败，不猜最佳值，也不向用户要求录制数十场场景和人工回归试验。

本文高于[赛场眼测V1](NBA2K22_LIVE_COURT_USER_EYE_TEST_20261019_V1.md)里的“交给玩家做3–5回合A/B”建议和[Live Court Gameplay V3](NBA2K22_LIVE_COURT_GAMEPLAY_PARAMETERS_V3.md)里泛化的逐项A/B研究顺序；旧文档仅作为历史记录。本轮**没有生成正式推荐游戏配置、没有对游戏做任何写入**。游戏实场ACE始终ON，不开发C2/C3实时AI监控，不研究日历Sim/Sim Engine，不卡住GM M3。

## 1. 用户已明确的两个失真（EYE_TEST，非AI臆测）

- **防守**：挡拆后两人会围持球人，roll man顺下到篮下无人补防；**用户明确回答“B，没有人补防。或者至少搞成换防”**。这比前轮“可能是换防失败或夹击后弱侧补位”更加具体：第三人从未合理接手，玩家接受合理的真换防，不能把两人挤球但没人管roll man当作正常换防。
- **进攻终结**：普通球员即使近筐遇到普通防守也几乎不进，只有超级终结者/明显高大对小后卫时能进；小后卫敢正面挑战大中锋，Shot IQ和终结判定都可能有关。
- **正常现象HOLD**：NBA2K22 HOF没有观察到系统性CPU超人速度/投篮、抢断篮板作弊；勇士跑动传切和伦纳德强突可观；整体犯规/体能/篮板正常。**不得将“需要取消HoF难度”作为先验结论**。

## 2. 原版HoF滑块基线，绝不混同名义“50”

### 2.1 有界可靠的PS4本世代默认对照（记录原贴版本和2022作者，而非我们PC当前存档实测）

来源：[gu8lal8 2K22 COMPETITIVE — PS4作者的五档默认值对照](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/nba-2k-basketball-sliders/920479-gu8lal8-s-competitive-sliders)；文章说明作者是**PS4本世代**，这段为他记录的官方模式默认值表，不等于玩家本机build确认。

| 选项 | 作者记录的 HoF CPU | 作者记录的 HoF USER |
|---|---:|---:|
| Inside Shot Success | 56 | 48 |
| Close Shot Success | 56 | 48 |
| Mid-range/3PT Shot Success | 56 | 48 |
| Layup Success | 56 | 48 |
| Contact Shot Success | 56 | 48 |
| Shot Coverage Impact | 50 | 50 |
| Layup Defense Strength Takeoff/Release | 50 | 50 |
| Help Defense Strength | 50 | 50 |
| Defensive Awareness | 50 | 50 |

**关键**：用户在HOF打球时，社区对照显示HoF并非所有关键成功率都为50，且USER/CPU不对称。今后比较必须从**用户本机实际当前HoF配置**出发，而不是社区套装里的全部50；先设置HoF档并保存两侧原值，再判断哪些已经改过。无需因此让用户亲自逐项回报，交给Antigravity的现有内存可读接口获取。

### 2.2 确实“以HOF开局然后差分”的本世代MyLeague例子

[Operation Sports — 2k22 MyLeague settings/sliders（PS4本世代2021-09-15；被引用的IrishSalsa方案）](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/nba-2k-basketball-sliders/917042-2k22-myleague-settings-sliders)：明确先选Hall of Fame，没提到的维持HoF默认；CPU进攻不动、帮助防守70/70、接触发生率55/55或60/60等，展示方法确实可执行。**但是并没有证明帮助防守70已经修好roll man没人补防或普通球员篮下打铁**，所以不能直接推荐这套数值；这一组部分另有针对罚球/节奏的Sim研究和人物倾向编辑，不属于本轮修复证据。

## 3. 防守 PnR 无人管roll man：必须承认原生机制缺陷，仍缺高可信完整成功方案

### 3.1 与用户观察几乎相同的本世代直接证据

[Operation Sports — 2021-11-19 Last Gen的CPUvsCPU玩家报告，帖子#1037、#1042](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/917717-please-turn-the-help-defense-and-cutter-help-defense-back-to-were-it-was-on-release/page70)：
- 两个防守者过度围持球人，掩护/背掩护后没人正确保护篮下；弱侧防守者启动帮助通常太迟。
- 作者指出**Help Defense=100、Over/Drop、Pre-Rotate**等都未让防守责任明显恢复，ACE OFF时一样发生。
- 进一步怀疑掩护接触动画无法触发正常的轮转响应；尝试多个接触敏感度/力量全局值也未有效解决。**这些是作者推断，不是已证明引擎内部原因**。
- 证明“直接把Help Defense调至100就解决用户的问题”**没有充分依据**。

[Operation Sports — 2K22战术研究者vannwolfhawk观察截图/逐回合描述](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/917717-please-turn-the-help-defense-and-cutter-help-defense-back-to-were-it-was-on-release/page25)：他认真逐次回看PnR发现“roll man没有tag”、drop大个防守到位问题、弱侧轮转虽然有时启动但太迟；部分测试已经把防守滑块调很高，仍提出只有游戏原生改善drop才会可靠修复。此帖覆盖不同平台与补丁；作为机制故障交叉佐证，**并不等于当前PC每一版本都一样**。

[Operation Sports — 2021-10-23补丁后的变化](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/917717-please-turn-the-help-defense-and-cutter-help-defense-back-to-were-it-was-on-release/page51)：不少玩家认为首发时的协防/弱侧轮转经过补丁削弱，不能把2021刚发售版的“成功方案”视为最后一个2022 PC Build仍有效。

### 3.2 晚期本世代玩家反馈同时包含“有改善”和“并未解决”

[Operation Sports — 2022-05-21 防守是否已修好？](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/923019-has-2k-fixed-help-defense-paint-defense-pnr-defense-yet)：PC本世代玩家说比前补丁版本改善；也有人建议提高CPU+USER协防、防守意识，报告可以改善整体防守挑战，但其他玩家回报会造成过快贴防、不自然的防守反应；**这些并未证明解决roll man专属Tag轮转**。

相反证据：[2K22 Impressions #1592](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/916673-nba-2k22-impressions-thread/page107)有HoF默认下防挡拆不错的玩家；不能因此断言每个build与球队都不可修。

### 3.3 当前证据结论与可研究路径

- `PnR roll-man untagged`的直接历史证据等级：**高（玩家明确描述，含PC本世代）**。
- `Help Defense高值直接修复`：**负面或互相冲突；不推荐**。
- `Defensive Awareness提高增强整体防守`：**部分正面反馈但带副作用；并非专门修复弱侧tag**。
- `Drop/Hedge/Switch/PreRotate/StAyAttached某个固定组合成功修复`：**尚未找到2K22本世代HoF并在比赛中持续奏效的可靠报告，不编造**。
- 由于原版ACE始终ON且无模型实时监控，我们只能考虑已证明的**比赛前防守策略**与原版Gameplay环境配置；真正的防守责任算法并不一定开放给滑块。研究可以继续深入“2022 PC最终Build、整套HoF配置、P&R防守恢复成功回访”，**找不到就保持待证**，不拿提高CPU命中/移动造成的难度来“掩盖防守漏洞”。

## 4. 篮下终结过严：找到了有修订和实际改善反馈的玩家经验

### 4.1 Eccentric 2022-01-16，同一症状、作者明确记录“已有改善”

[Operation Sports — 2K22 Eccentric Edition page10, #137–#138](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/nba-2k-basketball-sliders/917100-nba-2k22-the-eccentric-edition-realistic-ng-slider-set/page10)：
- 玩家先反馈奥尼尔、张伯伦、姚明在被人防守后难以完成篮下终结。
- 原作者承认同样现象，分析Inside/Close/Layup/Contact Success与Shot Coverage Impact共同作用。
- 后续Edit说明观察到`Inside Shot Success=60`、`Close Shot Success=55`、`Contact Shot Success=50`带来改善，`Layup Success=50`仍允许防守充分的上篮不进。
- **这是明确的受益经验，但属于NEXT GEN研究，且这些数值以作者当时整套滑块配置为条件**；并非可对本世代名人堂56/48基线直接照搬的推荐数值。

### 4.2 H2UKNOW 2022-02 HoF NEXT GEN，针对轻微接触减弱影响

[Operation Sports — NBA2K22 Next Gen Settings/Sliders Hall of Fame](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/nba-2k-basketball-sliders/921033-nba-2k22-next-gen-settings-sliders-hall-of-fame)：基于HoF。作者解释因詹姆斯/字母哥受到轻微接触就离谱打铁，将Layup Defense Strength（起跳/释放）下调到35附近。反馈低水平终结者仍旧不具备无视防守的能力。方向性支持**减弱轻度接触的过度惩罚，而不是使人人都轻松进**。此为PS5/XBS next gen，没有本局PC交叉验收。

### 4.3 J-Kits 2022-02-26 HoF NEXT GEN，持续版本与实战视频

[Operation Sports — J-Kits KingSimKits HOF v2.3](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/nba-2k-basketball-sliders/917660-j-kits-kingsimkits-nba-2k22-12min-hof-sim-sliders-real-stats-gameplay)明确作者是PS5 next gen/12分钟/HOF，最新版2022-02-26将Layup Defense (USER/CPU Takeoff)改20/18，Release改16/13，同时保留其他出手和环境设置，给出多场真实比赛影片、观众反馈；认为2K对手臂干扰的影响过于极端。
- 这**证明他为降低干扰权重进行多轮迭代**，不等于证实单独改Takeoff参数就解决了本世代所有篮下问题。
- 注意其起跳/释放值很低，与Eccentric并非相同方案，**不可拿来跨版本“平均”**。

### 4.4 可证结论：优先研究影响方向，不下虚构数值

证据共同支持：本游戏系列在轻度干扰判定/接触内线终结有“过度惩罚”问题，已有玩家借**投篮防守干扰权重（Layup Defense Strength Takeoff/Release、Shot Coverage）与Inside/Close/Contact Success组合**获得改善。
**但目前没有“本世代PC HOF原始默认 + 同问题 + 记录完整成功参数组”的强证据**。因此本轮不发布正式`LIVE_COURT_PROFILE`数值，继续集中找这种来源。未来已有来源的配置也必须整体标记源难度/USERCPU通道/平台和搭配，不让用户替模型乱试。

## 5. 候选优先级与禁令

| 研究对象 | 证据排序 | 下一步需要的证据 | 禁止的错误做法 |
|---|---|---|---|
| HoF 真实默认 | 本世代PS4表+当前用户确认HOF | Antigravity已打通的当前UI/内存状态读回 | 把50当全部HOF默认，或换成Pro基础 |
| P&R 没人tag roll man | 本世代CPUvsCPU直述+跨版多玩家互证 | 本世代PC最后补丁后的真正修复回访，战术策略与结果对应 | 无证据提高Help Defense到100、只加CPU能力 |
| 接触篮下几乎不进 | Next Gen HoF与玩家实战明确改善反馈 | 本世代HOF独立成功案例；参数互相作用说明 | 随机拟合Inside/Close/Layup数值，或把Next Gen成功值照搬 |
| 正常机制 | 玩家已证篮板、犯规、疲劳、明星突破、勇士战术成立 | 无进一步必要 | 为了做滑块套装强行改正常机制 |

## 6. 研究流程与输出契约——把验证工作留给资料研究方

1. 只搜**NBA2K22本世代PC/PS4/XboxOne，HoF原生为起点**的持续更新帖子；优先有前版配置、实际问题、最终版反馈、多位玩家交叉确认的页面。遇到次世代PS5必须在结果第一屏标红`NEXT_GEN / NOT_DIRECTLY_TRANSFERABLE`，不能宣称本局适用。
2. 每份资料按`source/author/date/platform/game_patch/difficulty/default_or_custom/USER_CPU/target_symptom/changed_values/claim/result_confirmed/independent_followup/side_effect/external_roster_edit_required`归档。结果是`REPORTED_SUCCESS`、`REPORTED_FAILURE`、`UNPROVEN`、`CONFLICTING`四类。
3. 优先寻找可复制并且不需要批量改球员能力/徽章/个人倾向的方案；若一个“成功包”通过批量修改原始球员数据实现，要标`DISALLOWED_FOR_GM`，不能称Gameplay调参能独立达到同样效果。
4. 不安排玩家做“3–5次挡拆观察+模型给一组假数值再让玩家跑A/B”的工作流。**模型负责调查前人成功经验、解读其原因与证据局限，玩家可自行决定要不要使用已有成熟方案，但用户不替模型反复摸索参数效应**。
5. 在当前业务阶段GM M3仍首位。该研究成果只进入GitHub报告，直到存在足够可移植来源、玩家批准后才交Codex/Antigravity落实实际参数；不自行改赛场世界配置。

### 资料目录

- [真实HoF基线研究 PS4](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/nba-2k-basketball-sliders/920479-gu8lal8-s-competitive-sliders)
- [MyLEAGUE PS4 “先HOF再差分”范例](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/nba-2k-basketball-sliders/917042-2k22-myleague-settings-sliders)
- [2021本世代CPUvsCPU PnR轮转失效](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/917717-please-turn-the-help-defense-and-cutter-help-defense-back-to-were-it-was-on-release/page70)
- [2022 PC本世代帮助防守仍有争议](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/923019-has-2k-fixed-help-defense-paint-defense-pnr-defense-yet)
- [NBA2K22 Eccentric 真实篮下改进记录（次世代）](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/nba-2k-basketball-sliders/917100-nba-2k22-the-eccentric-edition-realistic-ng-slider-set/page10)
- [NBA2K22 H2UKNOW名人堂轻接触终结（次世代）](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/nba-2k-basketball-sliders/921033-nba-2k22-next-gen-settings-sliders-hall-of-fame)
- [NBA2K22 J-Kits多轮HOF修订+实战视频（次世代）](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/nba-2k-basketball-sliders/917660-j-kits-kingsimkits-nba-2k22-12min-hof-sim-sliders-real-stats-gameplay)
