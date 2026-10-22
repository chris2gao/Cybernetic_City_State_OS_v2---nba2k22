# DEV-20261017-TACTICS | NBA2K22 PC 教练战术对模拟比赛的影响：开发价值评估 V1

> **2026-10-17 流程变更提醒：本页早期建议的Codex开发前大规模A/B模拟效果实验已被玩家最新指令取代。当前有效研发/验收流程以 [DEV-20261017-05 V2](../development_tasks/DEV_20261017_05_COACHING_MEMORY_DISCOVERY_V1.md) 为准：确认内存技术可行后直接开发，玩家运行一个游戏月后通过最新赛季累计比赛数据差值评估效果。旧测试方法保留为历史思路，不作为Codex的当前必做事项。**


- 状态：ASSESSMENT_ONLY / RECOMMEND_P0_EXPERIMENT / NO_EXECUTION_APPROVAL
- 日期：2026-10-17
- 负责人：Web GPT DEVELOPMENT
- 适用平台：项目 PC Windows NBA2K22（不要将次世代 PS5 / XSX MyNBA 新功能默认为PC功能）
- 本文仅保存设计论证、证据和拟议测试门槛，不是授权 Codex 修改正式存档或自行启动工程开发
- 玩法限制：`PLAYER_RULES_20261017_V3`，玩家单独批准战术游戏写入；普通球员能力、倾向、徽章、潜力不可因战术优化而改变

## 核心结论

**建议增加“GM 战术决策 → 玩家批准 → Codex 受控执行”能力，但按快速模拟有效性分层建设。**
最高优先级不是全字段对手战术/实时教练AI，而是辨认并验证普通快速模拟真正读取的 `Sim Points of Emphasis`、教练体系、进攻侧优先级、节奏、轮换等控制量。该模块可能以不修改任何个人属性的方式影响全联盟比赛结果；当前实际胜率提升仍未证实。不要混淆CPU现场比赛的ACE动态指令与快速模拟的统计计算。

## 外部证据分级

1. 官方 2K 于2021年发布 NBA2K22 next-gen MyNBA Conditional Coaching 可以在“sim games”时触发特定条件战术指导，但明确仅对PS5/Xbox Series X|S所述新功能，不能作为PC版已有功能的证据：https://newsroom.2k.com/news/nbar-2k22-adds-new-features-to-mynba-for-playstation-5-and-xbox-series-xs-consoles
2. 2019年 Operation Sports 关于 Sim Points of Emphasis 的社区讨论区分即时模拟与实际CPU比赛，称模拟侧受Sim POE与投篮倾向影响；这是跨代社区证词，不是2K22 PC源代码验证：https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/883442-does-sim-points-of-emphasis-only-affect-simmed-games-only
3. 2017年 Operation Sports 的完整赛季模拟实验报告指出 Sim POE 明显改变部分模拟统计分布，但无法作为2K22 PC胜率变化的精确系数：https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/nba-2k-basketball-sliders/845857-getting-a-realistic-myleague
4. 专门针对NBA2K22的社区真实化名单项目明确为30队调校教练与POE以追求模拟数据真实性：https://www.operationsports.com/nba-2k22-attention-to-detail-roster-from-celticlg-and-crew/
5. 2022年玩家讨论提示 NBA2K22模拟所用playbook、战术调用分布可能起作用：https://www.reddit.com/r/NBA2k/comments/vekpkp/
6. NBA2K22玩家报告普通Sim与SimCast/Live下三分频率变化，但样本单一且混杂模拟节长差异，不当作结论：https://www.reddit.com/r/NBA2k/comments/12b8i27
7. 2K22 PC 使用非次世代控制台版本；不能假设上述Next Gen条件教练工具可用：https://steamcommunity.com/app/1644960/discussions/0/5208960061407312439/

## 仓库已审事实与缺口

- `src/strategy_manager.py` 提供 `StrategyManager.get_team_strategy` 与 `set_team_strategy`，读写Team结构 `0xEB2..0xEBC` 多种POE字段；setter只验证uint8 0..255并回读，不证明真实枚举、批量执行或模拟比赛作用。其底层偏移可作P0线索，不可当完成实机认证。
- `src/gm_core/tactics.py` 为分析/提案；`src/gm_core/coverage.py` 注册offense/defense当前观测；`config/gm_policy.json` 的 `poe_on_ball` 枚举仍未认证且已有历史实测值与旧文档冲突；禁止用旧注释填充分档。
- `config/memory_field_profile.json` STAFF 存在 `preferred_system` / `active_system` 8类体系编码；不能由此推断能写教练/系统或在快模拟中生效。
- `docs/34_BASELINE_CURRENT_STATE.md` 明确球队策略基础setter不等于已验收GM业务执行器。游戏内存被AI回写、存档/读档效果、每对手配置对象、模拟使用的独立Sim POE地址及战术手册列表均待认证。
- 玩家表示 Codex 最近已经找到可写内存地址，但尚未在这轮GitHub资料中核验新发现的提交或实验记录；应要求Codex提供具体字段、截图、写前后值与存档持久化证据。

## 优先级分层与适用场景

P0：游戏菜单中明确称`Sim Points of Emphasis`的字段、团队进攻重点、模拟节奏、第一至第三得分选择；优先验证快速模拟数据表现。
P1：体系/教练适配、进攻篮板/防守篮板、快攻设置、轮换配置（字段实测且影响模拟后）。
P2：战术手册与比赛实时防守POE，包括on-ball/off-ball/PnR/help防守；分别验证其对普通Sim、SimCast、CPU-v-CPU/玩家比赛的作用。
P3：针对对手的专门赛前布置和比赛实时动态修改；没有模拟引擎证据不开发实时脚本，不把AI本来已有的ACE替换为GM微操。

高层策略归Web GPT GM：建立各队季前/交易后阵容-体系-节奏-得分点方案；真实战术枚举与游戏执行归Codex；玩家逐次具体批准。每赛季开始或每月玩家主动触发复核，而非每场自动触发。教练可以在实际比赛中动态执教，GM负责预设风格，不强行禁用ACE。

## P0：最小定量验证计划（独立测试存档，不修改正式局）

1. **记录环境并备份**：NBA2K22 PC版本、名单、球队、角色、赛季、比赛设置、模拟节长、CPU教练设置、AI自动策略开关、原字段/原POE值。复制相同起点存档；保证阵容、球队能力、伤病及轮换配置在每个实验条件一致。
2. **先定位语义**：从游戏界面分别修改 `Sim POE` 与 `Coach Gameplan/Defensive Settings` 和 `Playbook`，Codex只读比较各自影响的底层字段；确认原始枚举、枚举展示名、独立/共用存储与存档持久性。不根据旧0xEBx表武断映射Sim POE。
3. **同源A/B/C/D**：
   - A 对照：保留原始战术；
   - B 仅变更**Sim POE**，选一个明显但合理的可验证方案；
   - C 仅变更现有`Coach Gameplan`比赛攻防策略；
   - D 仅变更体系或战术手册（如果安全已验证）。
   同期测试普通快速模拟(`Sim Through Date`)、SimCast和真实CPU-v-CPU；分开出具结果，不混合求均值。
4. **重复并控制方差**：至少用两种不同阵容风格的球队；相同存档快照重跑各组，建议每种条件至少做多次（例如10个批次×10场/批，受游戏所需时间可缩小）。不要认为重复读档保证同一随机种子。若无法每组同样赛程/对手，记录对手/主客场并用配对或控制回归；可用随机化/轮换顺序避免先后偏置。单场结果不能当显著性。
5. **观测不只胜负**：场均得分/失分、ORtg/DRtg或每百回合净胜分（仅在总回合数据有效时）、节奏、3PA、助攻、罚球、篮板、头号得分手出手份额、胜率、相对对手实力与主客场；未观测字段NULL。使用Python统计每组差额与不确定区间，阐明采样误差。
6. **AI覆盖/持久性**：开赛前→中场/终场→快速模拟前后→存档重开后读取同一字段。要确认变化是常驻Team设置还是比赛局部临时值；若自动覆盖，记录恢复时点。只读检测不代表允许自动再写回。
7. **准入门槛**：一项战术只有经过“游戏UI↔内存字段一致 + 合法取值 + 快速模拟中统计指标可重复影响 + 存档后仍保留 + 不受未知AI覆盖”才标`SIM_VALIDATED`；否则仅`GAMEPLAY_ONLY`、`UNCERTAIN`或`NOT_EFFECTIVE`。实机打比赛有效不证明快速模拟有效；统计变化也不自动证明胜率提升。

测试不可通过改变球员能力、徽章、倾向实现。必要的最小设置只改复制存档；正式执行另需具体玩家批准。

## 后续仅在P0通过后逐阶段开发

P1：维护每队`season_tactical_identity`、`verified_game_strategy`、`sim_poe`、`last_verified_source`；GM结合阵容、比赛表现提出`PROPOSED`候选修改；参数带枚举、来源、原值、目标值、预期作用、风险；玩家批准后Codex受控写入+回读。GM核心仍保持纯离线。
P2：仅将P0证实对真实CPU比赛或模拟有效且可持久化的字段做完整策略配置；针对阵容交易或关键球员流失时提出适配建议。
P3：对手特异性与运行中变阵属于按需研发，不验证不开放；不以脚本实时强制AI战术，不阻止游戏原生合理教练调整。

## 本次行动界限和开发决策

推荐投入“P0实验 + 有效模拟战术参数P1开发”；不推荐现在开发全部防守细节、逐对手策略批量下发、实时控制引擎。若快速模拟只受Sim POE影响，则将其作为GM正式可写核心而其他字段仍为参考/比赛用；若无效，则不应投入长期工程。
本次仅是开发价值评估，无Codex任务自动启动、无正式游戏数据/策略写入、无赛季推进。