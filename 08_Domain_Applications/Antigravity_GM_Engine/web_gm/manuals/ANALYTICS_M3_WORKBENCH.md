# M3A 分析工作台操作手册

2026-10-20 M3-T增量见[M3-T手册](GM_M3_TACTICAL_WORKBENCH.md)：prepare/筛选/导出首先require_gm_sanitized；原M02只保留历史兼容审计用途，不作为新GM球探来源，旧未脱敏缓存拒绝。新T包增加同批教练体系、四槽/48具名倾向、训练/轮换及显式对手个人防守面板；Potential/null和Intangibles偏置与真实篮球能力分开。原统计/注释/封存继续保留；当前八项最小验收和完整目录脱敏待办见[交付报告](../../docs/development_reviews/M3_T_IMPLEMENTATION_AND_ACCEPTANCE.md)。

本工具把既有M0静态快照整理为 `GM_DECISION_PACKET_V1` 分析包，供候选GM协议研究。它不会采集、调用模型或修改游戏事实。网页连接由玩家后续建立；本地CLI成功不等于网页验收。M3B见[GM手册](GM_M3_DECISION_WORKBENCH.md)。

所有示例在仓库根目录运行。派生库默认 `_exports/dev10_m3/gm_workbench.sqlite`；实际使用可固定另一独立派生库，后续每次传同一 `--workbench`。路径名必须为 `gm_workbench.sqlite`；拒绝位于saves/query_snapshots/published/seasons中的文件。`--query-root`默认database/query_snapshots，`--published-root`默认published，均只读。

## 1. 固定来源并准备事实

```powershell
python scripts/gm_analysis.py prepare --career CAREER --batch BATCH --season 2021-2022 --node-type CHECKPOINT --run A01
python scripts/gm_analysis.py show --run A01
python scripts/gm_analysis.py team --run A01 --team SAS
python scripts/gm_analysis.py players --run A01 --team SAS --limit 20
```

career/batch/season/node-type必须明确。节点可选BOOTSTRAP、SEASON_INITIALIZATION、CHECKPOINT。旧实验来源需显式 `--allow-local-audited`，不会因此取得生产GM资格。`prepare`只产生DRAFT_FACTS，不自动诊断重建/争冠或制造球员估值。

`players`返回已解码能力值、合同摘要、原始累计统计、身份和证据引用。若truncated为true，继续原命令并传返回的 `--cursor`，直到next_cursor为空；页内可能因字节预算少于limit。默认20、最多50。人物identity只在该批次有效，不能用姓名/槽位当永久ID。

`team`给出累计与可比区间指标、员工关联、教练当前值摘要、财务/签位背景、诊断和缺口；整体防守记录通过evidence按指定对手查看。八个底层员工关联与六个可任免UI岗位分别记录，任免和效果公式仍未知。

## 2. 指标、区间和版本引用

已有球队累计计数由新增 `q_team_stats` 安全视图提供；也可运行 `gm_data_query.py team stats --career CAREER --batch BATCH --team SAS`。没有新采集。旧快照无该来源时明确SOURCE_UNAVAILABLE。

指标保留输入、分母、公式版本、样本、来源引用和UNKNOWN原因。包括比赛数、eFG、3PAr、2P%、3P%、FTr、估算失误率、AST/TOV、场均得失分与篮板；百分比为fraction。失误率使用 `FGA+0.44*FTA+TOV`，明确HEURISTIC。poss/标准ORtg/DRtg/NetRtg及篮板率未认证，不由原始同名字段推定。

需研究区间时增加以下明确上下文：

```powershell
python scripts/gm_analysis.py prepare --career CAREER --batch CURRENT --season 2021-2022 --node-type CHECKPOINT --previous-batch PREVIOUS --history-context BRANCH_A --previous-season 2021-2022 --previous-history-context BRANCH_A --run A02
```

两批须同career/赛季/显式历史上下文、日期有序且球队来源年一致。缺少前批上下文会保留NOT_COMPARABLE。程序先减累计计数，再重算比率；负计数只影响相关指标，0场为NO_NEW_GAMES。历史上下文是调用方明确提供的语境，不冒充内存观测。

人物多字段唯一匹配仅为TEMPORAL_CANDIDATE，可列暂定能力/合同/累计变化；歧义不计确证成长。交易后球员累计不算新队贡献，跨季合同槽变化也不自动解释为新签或涨薪。

`--finance-run F01`引用同工作台不可变M1运行；跨career拒绝，不同batch仅为参考并标REVIEW_REQUIRED，cash不变成签约容量。`--strategy-ref SAS:1`可重复，固定M2分析revision；不静默取latest。`--supersedes-run A01`建立新运行的前任引用，原封存包不覆盖。M2知识卡固定记录为参考，历史球队文化不自动决定当前目标。

## 3. 填入分析并封存

导入文件格式如下；对不同球队重复teams元素即可，不要求一次填满30队：

```json
{
  "teams": [{
    "team_id": 25,
    "evidence_refs": ["team:25"],
    "annotations": {
      "diagnosis": "填写有来源的判断或明确证据不足",
      "talent_gap_evidence": "说明全员供给与缺口，或为何无法判断",
      "utilization_hypothesis": "使用问题假设及替代解释",
      "internal_levers": "内部改善方向或有理由HOLD",
      "market_clues": "待筛选角色与机会成本",
      "strategy_change_signals": "可推翻当前方向的证据",
      "alternatives_explanations": "其他可能解释"
    }
  }]
}
```

```powershell
python scripts/gm_analysis.py import-analysis --run A01 --input annotations.json --expected-revision 1
python scripts/gm_analysis.py seal --run A01 --expected-revision 2
```

每次写入返回新revision，下次使用该值。导入只接受注释，不能覆盖来源、指标和访问记录；批准/执行声明会拒绝。全部30队完成注释才能SEALED_COMPLETE，其余SEALED_PARTIAL可用于有限研究，不能声称全联盟分析完成。封存后新诊断需prepare新run。

## 4. 真正筛选市场并保存补充证据

保存query.json，例如以下明确字段研究；阈值属于研究假设，不是游戏规则：

```json
{
  "query_id": "Q_SHOOTER_01",
  "source_domain": "roster",
  "role_question": "与内部替代相比，是否有可研究的投射供给？",
  "filters": [{"native_field":"attributes.3pt_shot.value","operator":"gte","value":75}],
  "excluded_team_ids": [29],
  "order_by": [{"native_field":"attributes.3pt_shot.value","direction":"DESC"}],
  "limit": 5
}
```

```powershell
python scripts/gm_analysis.py screen-market --run A01 --team GSW --query query.json --limit 5
python scripts/gm_analysis.py market --run A01 --team GSW --limit 5
```

source_domain为roster/pool/staff。字段限M0已开放标量及当前profile登记的 `attributes.FIELD.value`；操作符eq/gte/lte/is_null。排序使用显式字段并以identity破同值，没有隐含球员总价值。缺失能力不补0，unknown_required_field_count单列；筛选人口/匹配总数是SQL计数，实际返回身份才是READ，均不代表已逐项ASSESSED。pool非在队模型仍SCOUTING_ONLY，不证明FA或签约资格；staff候选只作参考。

封存后仍可追加同批筛选，程序保存独立查询/访问回执和候选；不修改封存包或追认基线已读。相同query_id不能换条件，新问题使用新ID。续页保持同一文件/limit并传cursor。即使零匹配也保留查询回执。

## 5. 证据与精简导出

```powershell
python scripts/gm_analysis.py evidence --run A01 --ref team_stats:25:made
python scripts/gm_analysis.py evidence --run A01 --ref metric:25:efg
python scripts/gm_analysis.py export --run A01 --output _exports/A01_handoff
```

可回查ref：team:ID、team_stats:ID[:FIELD]、metric:ID:NAME、interval:ID:FIELD、player:完整identity、staff:完整identity、coaching:ID、defense:ID:OPPONENT_ID、finance:ID、pick:asset_id、knowledge:card_id，以及显式链接的strategy/finance_run引用。market:候选ID引用补充查询和数值；candidate返回screen_query_ref可继续追溯。

导出目录必须明确且不存在，拒绝事实/正式赛季目录。产物为index、30队短注释、access coverage、methods/gaps；完整人物明细仍按本地有界查询。丢失静态来源时不会回退到活跃数据库。导出不自动提交GitHub，也不上传工作台SQLite。

运行形状与业务校验由标准库Python校验器统一负责，未新增jsonschema依赖，不宣称执行了外部JSON Schema验证。当前仍以V3为正式GM协议；M3B代码存在不构成V4启用。
