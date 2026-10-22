# 2021–2022 赛季 · GM 决策窗口 W01 · 第 1 回合 R01（封存）

| 索引字段 | 本轮记录 |
| --- | --- |
| career_id | `mc_haliburton_2021` |
| game_season | `2021-2022` |
| game_month_hint | `2021-11`（历史玩家进度提示；未经当前游戏日期验证） |
| game_date_exact | `UNKNOWN`；生产 `latest.json.game_date=null` |
| checkpoint_type | `IN_SEASON_SNAPSHOT`；`month_closed=false`，**并非已验收的11月月终** |
| window_id | `GM-S2021-2022-W01` |
| round_id | `R01`（一轮完成的30队经营审查；后续审批、机制纠偏不另计GM决策回合） |
| decision_id | `GM-20261017-M01-R01 v1` |
| real_document_date | `2026-10-17`（文档生成日，绝非游戏日期） |
| source_batch_id | `2021-2022_M01_SIMPLE_PICKS_V1_88101a36a3e3_fbde28d7_TS2` |
| data_updated_at | `2026-10-17T11:50:28.464724+00:00` |
| uploaded_at | `2026-10-17T11:53:08.959661+00:00` |
| audit | `PASS_VERIFIED`（32项） |
| game_execution | `NONE`（本轮未批准写入，且本阶段玩家明确冻结经营写入） |
| conclusion | `STRATEGY_APPROVED; RESEARCH_APPROVED; TRADES_NOT_APPROVED; GAME_ACTIONS_DEFERRED` |

## 1. 同一游戏时间窗口的决策链（保持原记录不可变）

1. **观测**：Codex发布2021–22赛季首个GM生产快照；30队战绩及球员赛季累计统计，注意最新游戏精确日期未知。原始 `published/saves/mc_haliburton_2021/latest.json` 链接对应原始数据批次。
2. **W01/R01 GM初案**：[30队12模块经营决策](../../../../decisions/mc_haliburton_2021/20261017_M01_LEAGUE_GM_ROUND01_PROPOSED.md)，当时文字状态为`PROPOSED`。其市场 MKT-01（CHI/DET 格兰特）和 MKT-02（CHA/IND 特纳）只是示意性询价。
3. **玩家审批**：[7项批准回执](../../../../decisions/mc_haliburton_2021/20261017_M01_LEAGUE_GM_ROUND01_APPROVAL.md)和[结构化记录](../../../../decisions/mc_haliburton_2021/20261017_M01_LEAGUE_GM_ROUND01_APPROVAL.json)：GM-A01..GM-A07 全部获**战略/研究/非约束询价**范围批准；**不授权游戏写入、不构成两队已经达成成交**。
4. **机制纠偏**：[GM v2外部决策机制](../../../../GM_DECISION_MECHANISM_V2.md)、[纠偏会话](../../../../memory/gm/sessions/20261017_GM_V2_MECHANISM_CORRECTION.md)：交易由两队外挂GM独立谈判，达成一致后交玩家批准，再由Codex执行；原生NBA2K22交易AI和交易难度不是决策裁判。赢球优先，士气/化学反应次级；每一游戏时间节点最多3个GM对话回合，默认1轮。
5. **最新玩家停写决定**：本窗口保留已形成的战略与交易询价历史，但因Codex当前不可用于执行，玩家决定**本月所有涉及游戏数据的经营修改均不执行**；不要擅自找Antigravity替代。暂停到玩家开启下个月GM节点；**新窗口必须先重新观察游戏结果，旧操作不得自动复活或被视为已成交**。
6. **开发分工最新指令**：Codex先研究NBA2K22可修改的球队/教练攻防项目；玩家再将研究结果交开发规划基线设计实现。**GM不参与此开发规划或可写字段勘探**；待新能力验收后GM只消费其提供的已验证操作范围。

## 2. 冻结的首轮战况（OBSERVED，赛季累计不是当月数据）

| 球队 | 当前战绩 | 本轮 GM 战略 | 下轮主要检查 |
| --- | --- | --- | --- |
| PHI | 16–3 | 争冠核心保持 | 西蒙斯/恩比德贡献及强队稳定性 |
| BKN | 14–5 | 三核心保持 | 核心得分、替补内线与比赛净胜趋势 |
| LAL | 15–5 | 三核心保持 | 威斯布鲁克角色与三核搭配是否持续奏效 |
| SAC | 14–5 | 玩家哈利伯顿保护 | 双后卫效率、低失误延续和阵容补强 |
| GSW | 9–9 | 保留库里/克莱/格林，评估适配 | 传切、内线角色和胜率趋势 |
| UTA | 5–13 | 暂缓拆队，查明出勤小样本 | 米切尔仅2场的原因**未知**，下一次需确认 |
| DET | 2–16 | 坎宁安年轻核心重建 | 格兰特市场价值、成长周期及资产机会成本 |

完整30队同口径实测数据已冻结在[TEAM_BASELINE.json](TEAM_BASELINE.json)中；全部名单细节仍以当期不可变 `published` 批次为准。**未记录的球队并非未分析**，见30队原案。

## 3. 要保留的交易与人员线索（并非执行）

- `MKT-01`，公牛 ↔ 活塞，目标 Jerami Grant：原议价想法包括 Coby White + Derrick Jones Jr. + 已验证公牛持有的2022年开拓者原始首轮；是条件讨论，不是双方一致的正式协议。下轮根据球队战绩变化重新判断双方是否仍然值得谈。
- `MKT-02`，黄蜂 ↔ 步行者，目标 Myles Turner：原议价想法包括 Mason Plumlee + P.J. Washington + 2024年凯尔特人原始次轮（当前黄蜂持有）；也是条件讨论，不是已批准交易。
- `SAC`：实役 `Tyrese Haliburton` `pool_slot=1235`，该批出场19场场均54.16分；另有 `Ty Hali` `pool_slot=184` 未取得当期场上样本，**不能混淆人物身份**。
- `UTA`：Donovan Mitchell仅2场样本、Miye Oni仅1场样本；不能凭赛季均场上时间编造受伤或教练雪藏。
- `CLE/NOP/ORL/UTA`：球队现金有约42.9亿异常读数，未经过经济字段校验，不用于票价和现金预算决策。
- `chemistry`：当前30队均为70，无法根据单批横截面判定士气冲突，不阻断赢球优先的未来操作。
- 没有可靠的**当前教练计划分钟、真实伤病、球员交易申请、完整士气个人字段**；不可将未观测等同于没有发生。

## 4. 该窗口的最终状态（非第二轮经营决策）

| 对象 | 最终状态 |
| --- | --- |
| GM-A01/A02 | 玩家已批准战略方向/保护核心原则，不需执行器 |
| GM-A03/A04/A05/A06 | 玩家已授权研究或非约束询价；尚未出现可执行成果 |
| GM-A07 | 玩家已认可继续保持禁止普通能力改值、暂停历史重力 |
| MKT-01/MKT-02 | `INQUIRY_ONLY / NO_BILATERAL_CONSENSUS_RECORDED / NOT_EXECUTED` |
| 战术、轮换、人员、票价、交易、合同、选秀资产写入 | `DEFERRED_TO_NEXT_PLAYER_TRIGGERED_MONTHLY_GM_WINDOW` |
| Codex | 游戏执行当前不可用，玩家表示之后另行开发；本回合不调用 |
| Antigravity | 玩家有顾虑，本回合不自动指定为交易/战术执行者 |
| 30队实际游戏阵容变更 | `NONE_KNOWN_FROM_THIS_GM_ROUND`；游戏自行产生的变化需下一快照查明，不可断言没有 |

## 5. 下一次 GM 节点：如何利用本轮信息而不重复开会

下次由玩家另行启动新游戏月/季后赛节点，先取最新 `published/index.json` 和当前存档 `latest.json`，再读本文件+当前新批分析成果。

- 先确认`save_id`、`season`、实际游戏日期和来源批次是否变化；若精确日期仍UNKNOWN继续保留，**不能自动猜到12月**。
- 同赛季、同save、相同赛季累计口径的两快照可确定性计算：`delta_wins=new_total_wins-old_total_wins`，`delta_losses` 同理，`delta_games=delta_wins+delta_losses`；发现负增量、不同赛季、存档读档回退、统计口径变动应停止按“当月”差分。
- 赢球分析依次看：新期间胜负增量、球队得失分及效率趋势、核心球员出场场次与场均产出、当前阵容/资产变动、战术/教练有效配置。赛季均场值不可直接相减当作本月技术统计；若有可靠的赛季累计总量再相减求区间指标。
- `MKT-01/MKT-02` 先根据新数据重新估价和两队GM内部判断，真实双边同意才提出新版本待玩家批准，**本窗口旧批准不延续为交易执行批准**。
- 每个新时间节点至多3轮GM对话，通常一次输出完整可审批方案；`NO_CHANGE` 合理。新战术可写内容以开发规划基线/Codex以后提供的已验收能力表为准，GM不参与开发。
- 不直接编辑球员能力与潜力；不把本月未执行操作误归因于下月战绩变化。

**该窗口以文档封存，等待玩家开启下一游戏时间节点。**