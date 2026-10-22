# DEV-20261018-09 — NBA2K22 PC 本世代：中锋“月球运球”、MC主宰、佳得乐原生机制研究

- 日期：2026-10-18
- 阶段：`RESEARCH_AUTHORIZED / RUNTIME_READ_ONLY_FIRST / NO_GAME_WRITE_APPROVAL`
- 开发执行：Codex 本地 Windows / NBA2K22 进程；规划：Web GPT Development
- 玩家已有现场：**游戏已运行，处于一个《终极联盟》测试存档、CPU/AI 的「持球速度、持球加速度」比赛滑块设置页面。先利用当前页面；不要先退出、切换存档、进入MC或重启游戏。**
- 玩法：NBA2K22 PC **Current Gen/本世代**，名人堂难度；不是次世代。只针对用户描述的中锋/低持球能力球员运球时**连球的弹跳及整套动作都变得极慢**的“月球漫步”现象。玩家已确认帧率、运行环境正常；不再把VSync、GPU、整体游戏速度或降低难度当研究主线。

## 0. 工作边界、优先级和结果交付

三条并列研究，不要以一个猜出的指针在正式游戏里写值：
1. **P0 首要、趁CPU页面还开着**：找到当前NBA2K22版本原生`Movement / Speed with Ball (Min)`及`Acceleration with Ball (Min)` 的实际存储/消费路径；有必要连同Max、USER/CPU双侧核对；比较《终极联盟》和MC是否共用**底层机制**，以及MC是否使用同一**有效的设置实例**。预留受控全局滑块接口，不允许直接改普通球员`speed_with_ball`或`acceleration`能力。
2. **P1 MC Takeover**：能否在已创建的MyPLAYER中**切换主宰类型**（首要目的），区别于主宰充能条、比赛中激活、Team Takeover。定位保存来源、原生枚举、有效身份与运行期对象。不能通过修改人物能力/潜力/徽章绕道改变主宰。
3. **P2 MC Gatorade**：玩家说“佳得乐激活”，先辨别`Gatorade consumable boost`（消耗品）、`weekly Gatorade workout/turbo extra stamina bar`（每周锻炼/额外体力槽）、`Gym Rat`（永久奖励）三类数据和生效时机；查清当前离线/停服环境哪些状态真实存在/生效，不能统称“佳得乐开关”。

**研究本身准许只读内存、代码逆向、查看UI和工程实现。未批准任一进程内存改值、编辑MC角色、自动解锁/消费道具、保存正式存档。** 在当前《终极联盟》测试存档中若需要真实UI变化作差分，先保存页面显示原值，由**玩家本人改一次数值并改回**，或另行获得玩家对本次测试UI操作的明确批准；Codex只做只读成对采样。之后若需要程序写回验证或保存，须再请玩家明确批准测试存档+字段+原值→目标值+回滚方案；不能以“测试存档已打开”推定无限写入许可。禁止触碰在线服务器、VC、商店交易、账号授权或未经许可的收费权益。

本任务可以交付**只读研究结果+必要的独立定位器代码**，不强求三个机制都成为可写执行器。无法确定的对象按`UNKNOWN/READ_ONLY/BLOCKED`报告，不编造地址、UI含义、效果及持久化。

## 1. P0 当前页面优先：真实CPU持球运动设置定位

### 1.1 现场取证

- 先确认实际NBA2K22.exe PID、进程创建时间、模块基址/PE指纹、当前页面位置、存档为测试存档、CPU侧还是USER侧、游戏难度名人堂以及**页面显示的真实四项CPU值**；不要将示例数值当游戏实测。
- 当前页面相关四项优先：
  - `CPU.SpeedWithBallMin` / Speed with Ball (Min rating)
  - `CPU.AccelerationWithBallMin` / Acceleration with Ball (Min rating)
  - `CPU.SpeedWithBallMax` / Speed with Ball (Max rating)
  - `CPU.AccelerationWithBallMax` / Acceleration with Ball (Max rating)
- 第二步再核对对应USER值。若页面只展示部分项，先完整读取现有页；**不要为看其它页面丢失第一份证据**。
- 可利用当前界面字符串/值映射、进程只读遍历、CE已知工具或界面脚本，但必须区分：**UI编辑缓存**、**滑块设置对象**、**保存结构**、**比赛实际使用的值**。内存中等于某个可见数字的地址不等于已找到有效滑块。
- 最小差分方案：截图/记录CPU某个Min原值A；玩家在这个测试存档的游戏UI中将该项`A→A+1`（若越界则可逆`A→A-1`），Codex只读扫描候选；再由玩家`→A`还原，再扫描。一次只改一项，观察当前页、离开页、重新进入页时是否同步；保存不是本阶段必要条件。若USER要接着自己操作页面，应先取得玩家确认。
- 再通过另一项独立值确认索引/步长/CPU与USER区分。校验候选值实际类型（`uint8/int32/float/0..1`等）、地址对象布局/有效范围、生命周期，记录原始bytes与相邻字段；当前地址可作证据，不作为下一次启动的固定绝对地址。
- 对原有`src/slider_manager.py`的静态`ADDR_SLIDERS=0x063319F8`、`ADDR_SETTINGS=0x06332630`以及旧`OFFSETS_SLIDERS`只作**历史候选**：此前地址/语义不可靠，禁止直接调用`lock_realistic_sliders`或将旧偏移认证为这四个Movement字段；该方法还会顺带修改伤病、交易、时间等完全不相关的设置。
- 如果已有内存读取器无法读取当前UI，可实现小型只读进程/页面探针，或使用玩家批准的GUI读取方式；不要尝试用未确认的地址先写出“正确值”。

### 1.2 要证明的关键功能路径

- 《终极联盟》的UI CPU/USER配置与游戏实际Gameplay配置是不是同一份？打开菜单时变了、离开菜单还在不等于比赛消费该地址；尽可能通过原生读取路径/调用点/可观察结构证明，无法确认要标`CONSUMER_UNVERIFIED`。
- **MC和《终极联盟》可以共用底层引擎，但不代表两模式必然读取同一实例或继承终极联盟测试存档的滑块。** 判断MC是否有自己的用户侧/CPU侧设置、是否在加载MC/选难度时重置/强制覆盖、是否有保存层替代、HOF是否切换配置。研究必须给出`SAME_ENGINE_CONFIRMED`、`SAME_SETTINGS_INSTANCE_CONFIRMED`、`MC_SOURCE_UNKNOWN/OVERRIDDEN`等**分级**结论，不能只因同进程内存在相同字段就判“MC已可修改”。
- 标清玩家控制的MC球员走哪个侧：USER或CPU，队友/对手走哪个侧。当前页是CPU，**可能只能控制AI**，不能直接说CPU参数修复MC玩家本人。必要时读取两侧，但不假定映射。
- 区分“UI滑块能变”与“低球员持球动画能变”。2021年Current Gen玩家对`with ball` Movement滑块的真实比赛效果存在争议，允许独立修改界面却并不证明会改变持球动画；请给出**效果状态未知**，直到玩家正常实战反馈。
- 不使用修改`Game Speed`、帧率、难度、球员`speed_with_ball`或`acceleration`属性作为兜底；若证据显示Movement两个Min根本不参与MC运球，请如实报告`MOVEMENT_SLIDER_NOT_CONSUMED_OR_UNKNOWN`，进一步研究实际动作播放/运球速度函数，但不直接patch代码/强行加速所有中锋。

### 1.3 平衡方案

- 当前先只找真实参数和可控范围，**不事先设定值**；从CPU/USER本局原值起，按玩家实际观察和社区参考评估。可列社区*完整滑块组的参考*：Current Gen/PC RES2等曾使用持球Min速度35–40、Min加速度30–50（方案不一），不能当唯一最佳值、不能不看原值就把设置改成固定35/50。
- 只允许将来*有玩家单项批准*的最小变更用于测试存档：优先Min参数、保持Max及无球运动/整体游戏速度/HOF与球队人员能力不变，读回、复原。关注中锋第一步、投篮节奏、后卫差距；玩家正常打球反馈，不要求模拟大量比赛或保存重启A/B。

## 2. P1 MC主宰类型定位

- 对照NBA2K22 **PC Current Gen**，通常创建角色后不能像次世代/Mamba Mentality那样在官方菜单自由更换已成型角色的主宰（社区事实，非作弊不可改的技术证明）。
- 只读确认当前MyPLAYER身份和模板、当前显示主宰类型、原生enum、角色持久数据、派生算法/缓存及当前比赛充能条与激活标记。至少区分`TAKEOVER_TYPE` / `TAKEOVER_METER` / `TAKEOVER_ACTIVE` / `TEAM_TAKEOVER`，防止改错对象。
- 优先研究是否存在**直接调整类型的原生字段或模板选择**，以及变更是否导致合法模板校验/模式切换后恢复；不通过属性/徽章/潜力改变计算结果。无真实MC现场时先代码、资料、可见schema分析；等玩家切换MC模式的明确操作时再做只读实际比较，不擅自中断当前终极联盟CPU页。
- 可行则仅提交**受控提案接口设计**（对象绑定、前值、目标原生type、进程/存档指纹、可逆性、风险、玩家批准）。没有确凿安全证据则结论`READ_ONLY_RESEARCH_ONLY`，不编造“永久修改成功”。

## 3. P2 MC佳得乐状态定位

- 三类分别登记：**消耗品库存/效果/场次**；**每周锻炼完成、加成及额外Turbo/体力槽**；**Gym Rat资格、永久加成、UI显示状态**。说明可能的覆盖关系：Current Gen玩家反馈已取得Gym Rat时，原有每周加成未到期前界面可能仍显示临时效果，不能因没显示图标断言未生效。
- 只读查实际MC本地存档/运行时对象；用UI可见状态和来源验证对应当前MyPLAYER，不碰其他角色。不可将提升`stamina`玩家能力或直接写徽章表当“佳得乐激活”。若存储/生效依赖已关闭的2K网络服务、在线商店或不可访问的服务端账户资格，要明确判`OFFLINE_UNAVAILABLE`或`SERVER_SIDE_UNVERIFIED`；不做伪造购物凭证/货币或在线授权。
- 若有真实可控的本地功能标记，提交其读写可行性、是否真的作用于体力槽、是否随重新载入被覆盖的证据；**未经具体许可不试写、不保存、不承诺永久生效**。

## 4. 交付给玩家的阶段结果

### P0 首批（保持当前游戏页面）

1. `current_page_evidence`：PID/进程指纹、模式/CPU页面、四个CPU显示值、可信的当前读取位置/类型/原始bytes和证据链；区分UI buffer和真实setting、相邻4/8个运动滑块。
2. `movement_field_matrix`：CPU/USER×WithBall Min/Max Speed/Acceleration的`UI_CONFIRMED / NATIVE_SETTING_CONFIRMED / GAMEPLAY_CONSUMER_CONFIRMED / MC_CONSUMER_UNVERIFIED`逐项状态及风险。
3. `legacy_slider_manager_audit`：旧偏移为何不可信、不能使用的入口、如需独立读取/写入模块建议的文件/命令/是否批准等。
4. 明确下一次最小实机证据需玩家做什么。能证明真实读路径即可停止，不为“完全验证”做重复无意义测值或大量UI试验。

### P1/P2 首轮

- 一张主宰表（类型/充能/激活/保存，定位证据与`POSSIBLE/BLOCKED`）；一张Gatorade表（消耗品/周锻炼/额外体力槽/Gym Rat，激活及有效来源）。
- 以**当前真正观测到的数据**列研发建议：`IMPLEMENTABLE_WITH_SEPARATE_APPROVAL`、`RESEARCH_ONLY`、`UNAVAILABLE_OFFLINE`；不要凭历史CE表/讨论推断正式局可写。
- 若研究工具或字段profile需要代码开发，可在**本任务范围**提交**只读工具**和最小离线逻辑测试；不要默认生成可写执行器、向main宣传成正式已认证功能。
- 新文档建议：`docs/development_reviews/DEV_20261018_09_MC_FEATURES_RESEARCH.md`；将本次实际源码、当前进程证据和待批准项链接至`docs/34_BASELINE_CURRENT_STATE.md`，并在必要时更新研究用profile。测试存档里的观测证据禁止拼入正式生产`published/`或`league_state.sqlite`，全量数据同步规则不变。

## 5. 用户下一步批准门槛

本任务授权**研究与只读定位**，及在仓库内实现对应研究工具/报告；并不授权游戏内存写入、修改终极联盟真实比赛滑块、保存测试更改、MC主宰切换、佳得乐激活、任何普通球员能力写入。

Codex交付第一次研究回执后，用户可分别决定是否开发`GLOBAL_GAMEPLAY_MOVEMENT`受控执行器、是否允许某个*具体测试局*的滑块最小写入及恢复、是否实现`MC_TAKEOVER_TYPE`或`MC_GATORADE_STATUS`受控接口。正式GM系统（30队教练、交易、数据采集）保持独立，不自动触发任务。

## 6. 社区研究依据（只做候选线索，不是内存技术验证）

- NBA2K22 Current Gen玩家实际讨论`Speed with Ball / Acceleration with Ball`滑块可能不生效：https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/nba-2k-basketball-sliders/916877-speed-min-and-max-sliders
- NBA2K22 Current Gen RES2运动滑块完整方案：https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/nba-2k-basketball-sliders/917713-res2-2k22-all-star-current-gen-sliders
- NBA2K22 Current Gen 主宰创建后不能通过官方流程切换：https://www.dbltap.com/posts/nba-2k22-current-gen-takeover-tier-list-01fftsev5jzy
- NBA2K22 Current Gen Gym Rat与周加成覆盖的玩家实测：https://www.reddit.com/r/NBA2k/comments/pouwos

所有推断以当前版本、当前进程和玩家游戏画面为最终实际证据；不将Next Gen的Mamba Mentality/City规则移植到PC Current Gen。
