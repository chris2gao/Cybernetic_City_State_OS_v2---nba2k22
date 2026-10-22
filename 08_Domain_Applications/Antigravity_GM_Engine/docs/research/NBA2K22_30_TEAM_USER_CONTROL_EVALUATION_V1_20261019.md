# NBA2K22 PC MyLEAGUE — 30支球队全部玩家控制评估 V1

日期：2026-10-19。用户提出：与其担心游戏CPU球队在幕后修改经营自动化/原生球队设置，不如新MyLEAGUE里把**30队全部设为玩家控制**，由外挂GM统辖全部经营。本报告针对这一具体决策；**不授权直接改现有MC或MyLEAGUE存档**。

## 结论

**建议30队全部成为User-controlled franchises，但“由玩家经营”≠“比赛中10名球员都消费USER Gameplay Sliders”。** 两个维度必须分开：

1. **Franchise/Team Ownership（GM经营）**：有权调整球队交易、签约、训练、教练计划、对手防守和经营自动化。全部30队设为User可帮助将商业决策交给外挂GM/Codex，并防止原生非玩家球队按普通CPU球队自动交易（在相应Automation已设Manual时）。
2. **In-game Input/Controller（比赛实际控制）**：真人控制一个/一队，或手柄居中、两队完全由原生AI在3D场上打；另有日历快速模拟。**目前没有NBA2K22 PC同构源码/针对全部GamePlay字段的一致验证，能够证明第1维决定所有球队都用USER滑块**。不应凭此删除CPU栏或把HoF CPU默认56错误改为USER48。

### 公开玩家证据

- [cdcool NBA2K22 PC CPUvsCPU MyLeague](https://forums.operationsports.com/forums/forum/basketball/nba-2k-pc-forum/918715-cdcool-nba-2k22-cpu-vs-cpu-myleague-sliders)：2021年直接写明`CONTROLLING ALL TEAMS in MYLEAGUE`，却`Watching every game, not Simming anything`；证明球队玩家所有权不强制真人操控上场球员，是本项目直接可复制架构。
- [MyLeague 2019 30队控制+可独立选择Game Participation自动化](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/881984-myleague-question)：全控球队后Game Participation等可单设Auto/Manual。没有证据指出Ownership单独覆盖Gameplay User/CPU。
- [MyLeague 2015全队管理与自动化分组参考](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball-rosters/844191-the-indiana-high-school-athletic-association-one-and-done-player-lock-experience)：30队控制、经营Manual，但`Game Participation Auto, Injury Auto, Before Games Auto`，方便日历推进。
- [NBA2K22玩家2022年教练Gameplan旧数据影响轮换](https://www.reddit.com/r/NBA2k/comments/vhpyvz)：默认计划与指定对手计划能互相覆盖，与全队所有权是不同层级；切成User不应承诺根除原生比赛中调分钟、伤病/轮换重建。
- [2K17-18 Operation Sports USER/CPU滑块作用讨论](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/nba-2k-basketball-sliders/847158-cpu-sliders-user-s-cpu-teammates)：不同玩家对USER是否影响AI队友有**互相矛盾的实验结论**，并有人认为不同滑块类型作用对象不同。跨年证据不足以决定2K22的USER/CPU消费规则。**精确通道待证**。
- [2K22 PC本世代HoF CPU/USER默认不同](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/nba-2k-basketball-sliders/920479-gu8lal8-s-competitive-sliders)：Inside/Close/Mid/3PT/Layup/Contact Success，HoF CPU约56、USER约48，说明误判所有球员通道可能影响整个比赛生态。

## 推荐的30队运营配置

| 类别 | 设置 | 目的 |
|---|---|---|
| 经营权限 | **30支球队玩家控制User/Controlled=Yes** | 统一拥有30队前台管理权；不意味着场上真人操控 |
| 30队 Team Automation | Trade/Trade Offers/FA Signings/Contract Extensions/Waivers/Staff Management/Scouting/Draft/Team Options/Qualifying Offers：**全部Manual或Off** | 外部GM独立商业决策与用户审批后Codex执行；根据某菜单是`Manual`还是`Off`选择可用值 |
| Game Participation | **Auto**（如果有） | 不必逐一确认82场×30/2，允许在日历正常推进/AI自动比赛；用户可以选择某场真实3D比赛 |
| Injury/Lineup Before Game | **Injury Auto暂保留**，其它经营层Before Games/Lineup根据当前Codex执行支持选择；当30队Manual导致无合法阵容时需保底应急 | 已知原版会在伤病和针对对手预设场景重配轮换，不能宣称全控=绝对不覆盖 |
| Coaching ACE | **ON** | 原生3D比赛时临场调整策略和暂停 |
| Offensive/Defensive Playcalling | **AUTO** | GM赛前策略→ACE调用实际战术 |
| In-Game Substitutions / precise minutes | **AUTO** | 用户曾明确精确分钟会被游戏AI覆盖，不强制锁分钟 |
| Training Automation | **暂Auto**，获得受控原生训练接口后再Manual | 避免训练停摆 |
| Season transitions / owner firing | 原生GM/老板夺权选项OFF如有 | 外挂独立经营不希望被踢出工作流 |
| USER Gameplay Sliders | **保留现有HoF原值及另行批准的HOF Court V1差分** | 不根据经营球队数直接更改 |
| CPU Gameplay Sliders | **同样保留**，明确记录HOF原值与获批差分 | 未证为全部USER，不删除CPU滑块 |
| Simulation Engine | 原版正常，按项目政策不擅自调 | 日历模拟和现场3D判定不同 |

## 对先前HOF Court V1的影响

上次[HOF Court V1研究提案](NBA2K22_HOF_COURT_PROFILE_V1_PROPOSED_20261019.md)采用HoF基础的USER 48→52、CPU56→60（Inside Shot Success）；其他上篮防守35/35、协防70/70。**这是一套USER/CPU不对称的拟合候选，本身未验证**。

如果真实3D比赛只有CPU在操作，且两侧按CPU通道，则两队可能都受CPU 60影响；如果一侧按USER而另一侧按CPU，则52/60仍有差异。**现在无法给这两种情形选择唯一已证实的结果。**因此30队改User不应自动让CPU56→60差分“失效”，也不应为所谓公平现在无证据把CPU60降到USER52。需要以后Antigravity或既有可靠社区针对`on-court controller/team ownership → effective slider channel`作定位；不必让玩家用模型随口值做盲目A/B。

玩家之后可能亲自操控某队，也可能只观看两个AI球队：这两条应属于同一世界规则下不同的控球模式，维护两侧原始值和实际使用模式记录。在3D AIvsAI观赛时，若最终发现USER/CPU侧具有不合理的倾斜，应由独立赛场研究提案统一偏置参数，而不是通过改全30队经营权绕开规则。

## 已知代价

- 经营Manual更多，常规赛日历可能有30队消息/伤病通知/休赛期不可逆签约提示；不能假设所有选项都自动被完全静默跳过。
- `Game Participation=Manual`可能让日历需要逐场确认，**选Auto是关键**；结合独立观察需要时选择手动进入某场3D比赛。
- 某些Automation字段在不同年份可以套用所有User球队，而不是独立一队（[2019玩家例子](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/882783-is-there-a-way-to-give-up-control-of-teams-in-myleague)）；我们所有30队都采用相同经营权限，影响反而可接受，但需要按字段/队范围记录。
- 关原生签约/新秀/裁员后，外挂批准动作必须与游戏赛季结算节点对齐；若受控Codex实际写入能力尚未完成，先留阻塞或不跨休赛期，不应让游戏与外部数据库分叉。
- Gameplan已存在球队默认/对手专项及NBA2K22 AI轮换重建，30队User未必阻止原版自动写实际分钟或针对对手战术覆盖。

## 最终推荐与最小验收

1. **新建独立MyLeague时优先选择30队全User控制**。保留一次性原值与Team Automation表；市场依外挂，原版3D比赛和ACE保持不动。
2. **先只确认经营权限的效果**：玩家进入设置看到每队为User、相同交易/签约自动化均Manual、Game Participation=Auto；在此基础上日历正常推进，不强迫为30队逐场打游戏。控球队名单教练仍按已有Codex受控接口应用。
3. **滑块消费侧暂标`UNKNOWN`**。不因Ownership假定全部使用USER；保持所有USER和CPU HoF档配置，等待可复核技术证据。精确映射不是决定是否全队User经营的前置要求。
4. 任何变更正式保存须玩家批准；本档仅研究，没有实际读取/修改用户本机内存，也不把比赛仿真结论冒充源码已验证。

Status: RESEARCH_RECOMMENDATION_NOT_APPLIED.
