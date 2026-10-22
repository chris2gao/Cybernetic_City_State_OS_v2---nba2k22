# 2021–2022 赛季 GM 长期时间线索引

- season_id: `2021-2022`
- career_id: `mc_haliburton_2021`
- season_gm_baseline: `2021-2022`（一个游戏赛季一个派生 GM 决策聊天，赛季内各节点沿用同一聊天）
- current_window: `GM-S2021-2022-W03`（R04第三组已完成30队深度研究；R05仅待玩家触发，未批准游戏写入）
- last_confirmed_exact_game_date: `2021-12-12`（PLAYER_CONFIRMED）
- current_progress_hint: `2021-12 / M02`（官方发布检查点，month_closed=false）
- index_created_real_date: `2026-10-17`
- policy: `PLAYER_RULES_20261017_V3` + `WEB_GM_DECISION_MECHANISM_V2`
- execution_state: `M02_SOURCE_REFRESHED_AND_VERIFIED; W02_TRADES_OBSERVED_IN_ROSTER; W03_R01_PROPOSED_NOT_APPROVED; GAME_UNCHANGED_BY_W03`

## 本赛季 GM 决策节点时间线（整季沿用同一 GM 聊天）

| 顺序 | 游戏时间范围 | 窗口 / 回合 | 基准数据 | 经营记录与最终状态 |
| --- | --- | --- | --- | --- |
| 01 | 2021年11月附近，**精确日 UNKNOWN**；没有确认月终 | `GM-S2021-2022-W01 / R01` | `2021-2022_M01_SIMPLE_PICKS_V1_88101a36a3e3_fbde28d7_TS2` | [本轮完整决策链](windows/W01_GM_20261017/ROUND_R01_RECAP.md) · 已批战略/研究/非约束询价，所有游戏修改暂缓 |
| 02 | **与W01相同的未知日期检查点；没有新的发布批次，不是新月月结** | `GM-S2021-2022-W02 / R01`（同赛季聊天已触发的专题续议） | `2021-2022_M01_SIMPLE_PICKS_V1_88101a36a3e3_fbde28d7_TS2`（与W01完全相同） | [本次决策归档](windows/W02_GM_20261017/ROUND_R01_RECAP.md) · [30队同批基线](windows/W02_GM_20261017/TEAM_BASELINE.json) · CHI/DET格兰特具体交易仅PROPOSED；CHA/IND暂不成交；无写入 |

| 03 | **2021-12-12 / M02 普通检查点，不是12月月结** | `GM-S2021-2022-W03 / R01`（同赛季聊天，2026-10-18起采用V3至少五轮深度决策；本R01仅粗扫） | `2021-2022_M02_DEC12_FULL_20261018_bee1cb016256_e94b241a_TS2` | [R01归档](windows/W03_GM_20261018/ROUND_R01_RECAP.md) · [30队教练/交易提案](../../decisions/mc_haliburton_2021/20261018_M02_W03_R01_GM_PROPOSED.md) · [机器可读GM意图](../../decisions/mc_haliburton_2021/20261018_M02_W03_R01_GM_INTENT.json) · 12项教练意图/1项双边交易提案，**未获玩家批准，未游戏写入** |

## 2026-10-18 W03/R04 最新进度：第三组完成，全联盟30队深度研究收齐

- 2021-12-12同一M02普通检查点，不是月结；`W03/R04`完成C组DET/TOR/HOU/OKC/SAS/PHX/MIN/POR/GSW/CHA共10队、157条当前名单记录，累计**30/30队、466条名单**。机器资料每队核对M02原生教练默认值、同队同槽位球员区间事实、合同和2022–24签位。无游戏日期推进或写入。
- [R04逐队数据人读报告](windows/W03_GM_20261018/ROUND_R04_GROUP_C_METRIC_FIRST_REPORT.md) · [C1逐人机器档案](windows/W03_GM_20261018/ROUND_R04_GROUP_C1_METRIC_FIRST.json) · [C2逐人机器档案](windows/W03_GM_20261018/ROUND_R04_GROUP_C2_METRIC_FIRST.json) · [R04回顾](windows/W03_GM_20261018/ROUND_R04_RECAP.md) · [30队总研究索引](windows/W03_GM_20261018/ALL_30_TEAMS_RESEARCH_INDEX.md) · [完整进度tracker](windows/W03_GM_20261018/TEAM_REVIEW_TRACKER.json)。
- R04新增5个**未获玩家批准**的教练单字段候选：DET/OKC/MIN `POEDefense14→13`、SAS `POEOffense5→4`、CHA `POEDefense14→15`；TOR/HOU/PHX/POR/GSW保留。三组共有15项阶段候选，**不是R06审批清单**。
- 下一轮仅在玩家明确指令后启动`W03/R05` 30队整合、双方独立交易报价与战术机会成本复核；之后`W03/R06`才最终选择教练/交易意图和Codex执行材料。员工/全球员池技术债在本次决策结束后处理，训练和个人分钟精调仍不做。

## 2026-10-18 W03/R03 最新进度：B组10队完整比赛/战术研判完成

**最新完成`W03/R03`组B：NOP/UTA/SAC/NYK/LAL/ORL/DAL/BKN/DEN/IND，10队共152条当前大名单，累计完成20/30队、309条球员记录。** M02数据仍为2021-12-12同一正式存档快照（`2021-2022_M02_DEC12_FULL_20261018_bee1cb016256_e94b241a_TS2`），无游戏时间推进或任何游戏写入。

- [R03完整比赛数据驱动报告](windows/W03_GM_20261018/ROUND_R03_GROUP_B_METRIC_FIRST_REPORT.md)；[前5队逐人JSON](windows/W03_GM_20261018/ROUND_R03_GROUP_B1_METRIC_FIRST.json)；[后5队逐人JSON](windows/W03_GM_20261018/ROUND_R03_GROUP_B2_METRIC_FIRST.json)；[R03完成回顾](windows/W03_GM_20261018/ROUND_R03_RECAP.md)；[30队完成状态](windows/W03_GM_20261018/TEAM_REVIEW_TRACKER.json)。
- **明确篮球决定非游戏执行**：NOP `POEDefense14→13`，UTA `POEOffense5→4`，ORL `POEOffense5→1`，DAL `POEDefense14→15`，DEN `POEDefense14→15`；SAC/NYK/LAL/BKN/IND有事实支持HOLD。旧R01的NOP只攻篮筐和DAL只保禁区提案已按真实新增比赛修正，不能按旧R01提交执行。
- 最新玩家标准：取消空泛“赢球哲学/球队文化”及无关模板填充，按**M01→M02新增比赛攻防指标（每场净胜、2P/3P/eFG及对手数据）→球队真实能力→教练原生参数**提出可检验调整；员工评价本节点延期，全面员工JSON与player_pool.sqlite数据访问技术问题在决策结束之后解决。球员个别属性、训练和精确分钟仍不可直接修改。
- **下一轮仅玩家继续触发`W03/R04`组C**：DET/TOR/HOU/OKC/SAS/PHX/MIN/POR/GSW/CHA；再R05全联盟双方议价和候选审查、R06唯一执行提案与玩家批准。已有教练功能可提交明确原生战术意图，不需事先预测固定+X胜率；Codex执行/玩家实机观察属于经审批后步骤。

## W03/R02：A组10队独立经营已完成，下一步为R03（当前状态）

**同一M02 2021-12-12普通检查点，无游戏日推进、无生产游戏写入。** 玩家已触发W03/R02深入研究，组A PHI/MIL/WAS/CHI/CLE/BOS/LAC/MEM/ATL/MIA共10队、**157/157名大名单球员**已形成逐人来源+六维完整球队决策档案。[本轮人读报告](windows/W03_GM_20261018/ROUND_R02_GROUP_A_TEAM_DOSSIERS.md)、[结构化六维/逐人JSON](windows/W03_GM_20261018/ROUND_R02_GROUP_A_TEAM_DOSSIERS.json)、[R02完成回顾](windows/W03_GM_20261018/ROUND_R02_RECAP.md)、[30队tracker](windows/W03_GM_20261018/TEAM_REVIEW_TRACKER.json)。

- A组教练业务目标（**未批准、未经完整Native batch生成**）：CLE/BOS/LAC各`POEDefense14→15`；ATL`POEDefense14→13`；MIA`ActiveSystem2→7`，其余PHI/MIL/WAS/CHI/MEM暂HOLD。
- 员工来源现状：同批staff_pool 30队8岗位来源已审计，但本会话`staff.json`大文件访问受限，仅能核对10名HEAD_COACH和战术字段；非主教练岗位留未知，不虚构员工效果/替换执行。
- 完整交易协议暂时0；需等B组和C组的20队独立研究以及R05双边谈判。R01旧CHA/SAS报价不是玩家批准，不能直接执行。
- **当前进度10/30深度球队已完成，下次由玩家明确触发W03/R03组B**：NOP/UTA/SAC/NYK/LAL/ORL/DAL/BKN/DEN/IND。然后R04组C、R05全联盟交叉裁决、R06唯一终稿与真正执行材料。
- 玩家确认已验证教练战术等现有功能可以直接形成决策方案，**不要求执行前先证明+X胜率**；最终Codex执行及玩家进入游戏观察为实测验证环节，仍必须经过玩家具体动作批准和Codex原生安全预检。

## 2026-10-18 新增：每队六维数据驱动决策合同（优先于旧泛化30队总结）

GM之后必须遵守`GM_DATA_TO_DECISION_V1`：[数据→诊断→六维经营→审批执行→复盘正式规范](../../manuals/GM_DATA_TO_DECISION_STANDARD_V1.md)及[每队结构化合同](../../schemas/GM_TEAM_DECISION_CONTRACT_V1.json)：**逐人覆盖当前大名单**，先分清累计/增量比赛和角色能力，再具体裁决员工留任、教练战术、阵容与AI轮换、交易签约、资产发展、赢球哲学与复盘。**R02/R03/R04分组深度研究**均须通过此质量门槛才能让`TEAM_REVIEW_TRACKER`标COMPLETE。

本局制服组8个职位可反向读取，但任免写入器未验收，不能假装已可解雇/签约教练；2K次世代主机MySTAFF的17人/四部门机制不直接适用于本PC游戏。若有历史时代人物属性/能力特殊定制由[开发规划专项](../../../docs/development_tasks/DEV_20261018_HISTORY_GRAVITY_GM_BOUNDARY_V1.md)负责规划和独立审批，**GM只通过数据支撑的交易、签约、战术促进历史风格与现实线博弈**。原W03/R01任何教练/交易均保留未批准候选，不会因本规范升级获得执行权限。

## 2026-10-18 玩家确定的新W03决策流程（高于下方旧3轮记载）

已批准的最新经营**流程规则**：[GM_MIN_FIVE_ROUNDS_V3](../../GM_DECISION_ROUNDS_V3.md)。旧“每节点最多3轮/一轮提交30队”不再适用。**本轮没有批准12项教练或CHA/SAS交易执行。**

- `W03/R01`仅用于初步分诊，属于`PRELIMINARY_SCAN_SUPERSEDED_FOR_FINAL_DECISION`，不能计入30队正式深入诊断；此前12项教练+T01均需重新论证，不是最终双边同意。
- `W03/R02`：组A 10队 PHI/MIL/WAS/CHI/CLE/BOS/LAC/MEM/ATL/MIA。
- `W03/R03`：组B 10队 NOP/UTA/SAC/NYK/LAL/ORL/DAL/BKN/DEN/IND。
- `W03/R04`：组C 10队 DET/TOR/HOU/OKC/SAS/PHX/MIN/POR/GSW/CHA。**各轮必须GitHub保存球队深度档案和真实source引用**，30队完全覆盖后写`ALL_30_TEAMS_SYNTHESIS`。
- `W03/R05`：全联盟交叉审查、教练方案冲突控制、双方GM具体报价与谈判；不得因R01候选已存在就视作双方已同意。
- `W03/R06`：唯一终稿、具体游戏修改列表、技术安全核验和Codex交接/批准包。仍需要玩家批准；教练必须由确定性离线工具生成真实批次/digest后再经玩家摘要批准。
- 如果每轮10队做不好，GM可主动降为5队：W03/R02–R07六个深入研究轮，R08整体谈判、R09终稿。可继续延长，不提前退出。**每轮由玩家显式继续触发**，不自动推进游戏。
- 用户应把本赛季V3分阶段记录理解为对旧决策**流程**的后续修订，而非宣布旧R01当时就已经完成了深度研究。

## 2026-10-18 W03/M02 最新正式状态（高优先级，覆盖下方W02历史时点文字）

- **实际最新快照**：玩家已触发Codex发布正式M02，game_date=2021-12-12，月序M02普通检查点，`latest.json`指向`2021-2022_M02_DEC12_FULL_20261018_bee1cb016256_e94b241a_TS2`，`coaching_tactics=VERIFIED_OBSERVED_SAME_BATCH`、审计PASS。**下方“latest还是M01 / 两笔交易尚待刷新”是W02历史记录，已失效，不作为当前事实。**
- **两笔先前获批交易当前名单可观察**：Jerami Grant在CHI、Coby White在DET；David Nwaba在DAL；执行动作来源仍按玩家已确认，不重新执行。
- **本轮30队GM经营已触发R01并完成浅层初步意见（尚不足以通过V3逐队深度质量门槛）**：11队共12个教练篮球意图、19队教练HOLD；一项双方一致交易候选CHA↔SAS Poeltl vs P.J. Washington + 2024 NOP原始二轮，全部`PROPOSED_NOT_APPROVED`，原始详情和完整角色风险见[R01回顾](windows/W03_GM_20261018/ROUND_R01_RECAP.md)。
- **回合使用规则（新V3）**：本节点最少走完R02–R06的3轮每轮10队深入研究+2轮整合终稿；此处旧“3轮上限”已作废。R01只是历史总览，R02仍须由玩家继续触发；不自动开始新回合或写入游戏。
- **教练原生批准闸门**：GM现在只发布已验证raw目标和篮球理由，**尚未生成离线完整native batch/摘要/digest**；任何“赞成方向”不可自动等同教练执行摘要批准。交易T01同样必须玩家逐项具体批准并由Codex只读预检后执行。
- **球员数据特别注意**：个人累计出场/得分可跨球队。MC真实Tyrese Haliburton槽1235已在IND，个人27场58.41均分不等于在IND效力27场；重复模型Ty Hali槽184不是同一人物。训练由AI管理，精确分钟不强控。

## 本赛季关键时点的权威事实与文件

1. [W01 30队冻结对比表](windows/W01_GM_20261017/TEAM_BASELINE.json)：球队赛季累计战绩、进攻/防守输出、薪资、士气相关观测、若干团队战术字段，不能当成11月独立统计。
2. [W01 R01 决策链](windows/W01_GM_20261017/ROUND_R01_RECAP.md)：包括游戏时间/现实生成时间区分、战略结论、审批、暂停执行和下轮承接条件。
3. [初次全联盟30队经营提案](../../decisions/mc_haliburton_2021/20261017_M01_LEAGUE_GM_ROUND01_PROPOSED.md)：历史原始 `PROPOSED` 版本，不覆盖旧文案。
4. [玩家审批回执](../../decisions/mc_haliburton_2021/20261017_M01_LEAGUE_GM_ROUND01_APPROVAL.md)：7项仅限战略、研究和非约束询价。对于是否已执行以独立执行回执为准。
5. [GM v2 机制](../../GM_DECISION_MECHANISM_V2.md)：外部双边谈判、胜率优先、士气次级、最新V3每个全联盟GM节点最少5个实质回合；旧3回合上限已废止。
6. [最新 GM_CURRENT](../../memory/GM_CURRENT.md)：只作快速入口，窗口历史以此处文件为准。

## 2026-10-17 最新执行反馈与数据同步约定（此节覆盖下面的历史“待执行”表述）

- 玩家明确确认两笔交易**已在游戏中成功落地**：`GM-W02-A01` CHI↔DET Jerami Grant，以及 `GM-W02-R02-A01` DAL↔HOU David Nwaba。标记 `PLAYER_REPORTED_EXECUTED`，不用再次交Codex执行，也无需重获交易批准。
- **游戏已执行 ≠ 当前GitHub数据已刷新。** 本次读取的 `published/index.json` / `published/saves/mc_haliburton_2021/latest.json` 仍指向W01/W02相同旧批次 `2021-2022_M01_SIMPLE_PICKS_V1_88101a36a3e3_fbde28d7_TS2`，尚不能从线上快照独立核验交易后5名球员新归属及3枚选秀权。玩家下次决策前会**主动触发数据源更新与同步**；GM届时按新批次实测阵容、合同、选秀权、战绩开展30队经营。
- 玩家报告：Codex已经完善自动化交易、自由球员签约、模拟休赛期签约球员脚本机制。后续 GM 可在确认对应最新已验收接口、游戏机制边界与具体审批后提出可执行方案；不凭此报告虚构CLI或认为各机制本赛季都曾运行。
- 此次反馈不是新的游戏月度经营节点，W02旧方案和当时待执行描述保留为审计历史。恢复的球队攻防和针对对手设置开发仍须等待玩家提供验收能力说明；不把其视作已经上线。

## 最新玩家批准与能力路线更新（2026-10-17）

**两笔双边模拟GM已达成共识的交易，均已得到玩家明确批准，但没有游戏执行回执：**

1. `GM-W02-A01`：CHI 接收 DET Jerami Grant；DET 接收 CHI Coby White、Derrick Jones Jr. 和 CHI 持有的 2022 POR 原始首轮 `draft_pick:2022:1:28`。玩家明确批准，`APPROVED_BLOCKED_EXECUTOR`。
2. `GM-W02-R02-A01`：DAL 接收 HOU David Nwaba；HOU 接收 DAL Sterling Brown、DAL 持有的2022与2024本队原始次轮 `draft_pick:2022:2:17`、`draft_pick:2024:2:17`。玩家明确批准，`APPROVED_BLOCKED_EXECUTOR`。

**执行职责：** 用户带上述动作清单给 Codex 的 `docs/36_EXECUTION_BASELINE_PROMPT.md` 执行窗口；球员归属、合同关联、选秀权转让必须完整业务回读并在存盘与数据库状态上分别报告。文档34第8节在本次查询时尚未验收完整交易执行器；批准不等于允许裸指针单字段交易，也不等于游戏已成交。W01/W02的原始提案及当时审批状态是历史归档，不能覆盖本段更新。

**攻防开发恢复：** 玩家收回“取消教练攻防设置开发”的指令；Codex可继续研发球队自身攻防与针对各队的攻防配置。开发完成后玩家提供实机可操作机制，GM才做具体调参方案；当前不能认定已验收或已授权写入。

**国王剧情变化：** 玩家确认MC Tyrese Haliburton已申请交易，将在后续游戏日换队；当前是尚未完成的剧情事件，绝不能当作本批已观察到的换队。

**30队工作标准：** 每个新的真实月度/季后赛游戏数据批次都要求30支球队作出经营动作或有据可查的HOLD；不能只列观察点。本次W02 R02内容与W01/W02 R01复用同一批次，不是真实的新月份。

## W02 后最新待处理事项（W01历史记录不变）

- **最新节点 W02/R01 是同批专题续议，而非新的游戏日期/月度数据**；此时仍不得计算相对W01的新增战绩。
- [W02正式待批准提案](../../decisions/mc_haliburton_2021/20261017_W02_SAME_SNAPSHOT_GM_PROPOSED.md)：`GM-W02-A01` CHI将Coby White + Derrick Jones Jr. + 持有的2022年POR首轮换DET Jerami Grant，外挂两队GM在此价格达成模拟经营层共识，**玩家尚未批准且交易执行器未验收，绝对未成交**。
- `GM-W02-A02`：CHA/IND旧MKT-02按当前样本决定 `NO_DEAL`，不锁资产、不授权交易。
- GSW防守、UTA米切尔缺席原因、DAL防守继续观察；SAC玩家哈利伯顿继续保护。W02无游戏写入、无新赛季事实。
- 玩家如批准W02-A01，仍必须先由执行端重新核验最新存档与执行器；后续有新赛季批次时，GM需要重新估价，不能直接按本批交易。
  
## 当前窗口里必须保留的判断

- 76人16–3、篮网14–5、湖人15–5、国王14–5；保护现有强势核心，不照搬现实历史赛季交易。
- 国王实役 Tyrese Haliburton vs Ty Hali 同名身份冲突；以正确球员身份进行所有审批和下一次分析。
- 勇士9–9、爵士5–13、活塞2–16：下次判断是否出现扭转，要对比新的同赛季数据。
- `MKT-01` 公牛/活塞格兰特、`MKT-02` 黄蜂/步行者特纳：只处于市场询价历史，**都没有正式双方GM一致的交易协议和执行批准**。
- 已批准 `GM-A01..GM-A07` 的范围是战略、研究和询价；本次玩家明确将所有游戏修改推迟到未来GM节点。
- Codex/开发规划基线独立调研和开发球队教练/攻防能力，GM不参与技术勘探；开发完成后给GM提供已验收可操作的项目即可。

## 赛季级命名与记忆规范（后续所有赛季遵守）

**一个游戏赛季一个派生 GM 决策聊天、一份赛季时间线。** 每个 Wxx 是该赛季的一个玩家触发决策节点，Rxx 是该节点内部的第几轮审议（最多三轮），**不是必须新开聊天**。节点完成后继续沿用本赛季 GM 聊天并等待玩家触发下次月度/季后赛/事件节点；玩家确认赛季结束并归档时，再为新赛季开新聊天和 `web_gm/seasons/<YYYY-YYYY>/INDEX.md`，保留前季总结而不把前季战绩当新季事实。因上下文容量续开聊天时，明确同赛季续接并回读本 INDEX。

建议文件结构：

```text
web_gm/seasons/
  2021-2022/
    INDEX.md
    windows/
      W01_GM_20261017/
        ROUND_R01_RECAP.md
        TEAM_BASELINE.json
      W02_GM_<real_date>/
        ROUND_R01_RECAP.md
        TEAM_BASELINE.json
        ROUND_R02_RECAP.md (如确实进入第二轮)
        ROUND_R03_RECAP.md (最多第三轮)
  2022-2023/
    INDEX.md
    windows/W01_GM_<real_date>/...
```

每次新文档顶部**必须同时标出**：
- 存档 `career_id`、`game_season`、`game_month`/精确 `game_date`（不知则 UNKNOWN）。
- `window_id`、`round_id`、`decision_id/version`、真实文档日期。
- `source_batch_id/data_updated_at`、是否月末封账、引用的已批准经营结论和执行回执。
- 本轮发生的事：**当时真实数据 → GM判断/两队议价 → 玩家批复 → 是否执行 → 真实赛场反馈 → 下轮待检**。
- 未执行和未观察的信息单独标记，不把旧提案变成已发生交易。

下一次同一赛季聊天的新节点，第一步是回读**本季上一个节点快照 + 新的最新快照**并确定两者是同一赛季、同一存档、相同统计口径。对 `total_wins/total_losses` 可进行确定性差分，计算两窗口之间战绩；场均技术数据的差异只是累计均值趋势，**不是直接得到某月技术统计**。若存档回档、赛季更替、日期未知或来源字段变动，必须标明且重新对齐基准。

## GM 与开发基线的分工

- **GM**只保留赛季决策链，获得已认证的实际功能后再做胜率优先的篮球决策；停止独立研究可写攻防字段或AI覆盖行为。
- **Codex**首先调研实际可修改范围和执行能力；玩家会把结果交给开发规划基线，完成开发和验收。
- **数据分析基线**在玩家触发后输出同批次可复用分析和跨快照变化，保证增量计算可信。
- **玩家**安排赛季节点并批准实际游戏修改，GM不使用未授权工具代替Codex执行。

该索引仅通过玩家明确触发的GM任务更新，不因新数据发布自动运行。