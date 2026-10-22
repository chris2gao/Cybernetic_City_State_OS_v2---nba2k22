# DEV29 R07 — 独立审核A/B两项定向机读修复回执（2026-10-21）

> **交付者修复完成并自行静态校验，等待独立审核者简短复验**；状态：`R07_TARGETED_CATALOG_REPAIR_SUBMITTED_FOR_INDEPENDENT_RECHECK`。正式结案尚未获独立接受。依据：[R07独立审核报告](DEV29_R07_INDEPENDENT_REVIEW_20261021.md)。本轮不新增社区研究、源资料、原版PC22实机证据，不修改游戏存档、执行器或人格系统。

## A. 两个人工R01指南主题别名已按真实章节定位

修改文件：[R07第1卷](../game_mechanics/catalogs/R07_ITEM_TRACEABILITY_PART_01_V1.json)，并在[索引总清单](../game_mechanics/catalogs/R07_ITEM_TRACEABILITY_INDEX_V1.json)提示手工别名及分卷路径。

| ref_id | R07检索别名（不是原文机器主键） | 原攻略真实章节与术语 | 新标记 |
|---|---|---|---|
| `R07.0007` | `K02.SHOT_ZONES` | `docs/game_mechanics/guides/K01_K02_GAME_STATS.md` **第4节**标题`K02.SHOT_CHART / SHOT_ZONES`、正文`Shot Zones Aggregates` | `origin_identity_kind=GENERATED_GUIDE_TOPIC_ALIAS` |
| `R07.0010` | `K02.PER36` | 同攻略**第3节**标题`K02.PER_GAME_PER36_ADVANCED`、统计表格`Per 36 Minutes` | `origin_identity_kind=GENERATED_GUIDE_TOPIC_ALIAS` |

两项另存`origin_guide_heading`、`origin_guide_section_number`、`origin_verbatim_topic_term`，以及`origin_exact_machine_id_in_guide=false`。`R01`全部12个`manual_research_topics`同时标为`origin_machine_record_id_exists=false`，其余10项仅表示“原指南有直接字面主题”，不是原生字段或源JSON主键。**没有为了通过验证而向旧R01指南编造机器ID**。

## B. 八项查询成熟度语义已与非查询约束剥离

修改文件：[R07 40组机读能力矩阵](../game_mechanics/catalogs/R07_GAME_CAPABILITY_MATURITY_MATRIX_V1.json)。旧`model_query_api_status`在各自的`reviewed_old_query_value`中保留，非查询信息按领域归类，不丢失。

| 功能族 | 原来的错误查询值 | 现在的查询值 | 原语义留存位置 |
|---|---|---|---|
| F21 自由市场 | `SIGNING_WRITE_UNVALIDATED` | `NOT_CERTIFIED` | `execution_warning` |
| F22 普通交易 | `APPROVED_BOUNDED_EXECUTOR` | `PRIOR_SQLITE_JSON_REPORTED_SCOPE_ONLY` | `existing_execution_scope` + `execution_warning` |
| F23 选秀权 | `EXECUTOR_OLD_PLUS3_REJECTION` | `PRIOR_SQLITE_JSON_REPORTED_SCOPE_ONLY` | `execution_warning` + D06-G08 |
| F26 Staff | `STAFF_HIRE_FIRE_NOT_VALIDATED` | `PRIOR_SQLITE_JSON_REPORTED_SCOPE_ONLY` | `execution_warning` |
| F27 全局设置 | `R07_NO_NEW_WRITE` | `NOT_CERTIFIED` | `execution_warning` |
| F32 日期/存档 | `CAPTURE_BATCH_REPORTED_SAVE_DATE_REQUIRES_VERIFICATION` | `FIELD_LEVEL_UNKNOWN` | `data_integrity_warning` |
| F39 发布批次 | `CURRENT_BATCH_PERMISSION_BOUND` | `PRIOR_SQLITE_JSON_REPORTED_SCOPE_ONLY` | `query_prerequisites` |
| F40 历史世界 | `ABILITY_CHANGES_FORBIDDEN_EXCEPT_SPECIFIC_APPROVAL` | `NOT_CERTIFIED` | `world_rule_warning` |

这些“已报告的历史SQLite/JSON范围”**只表示已有业务资料/历史批次的可用性线索**，不能升级为当前存档逐字段读取或可执行性。F23旧+3执行器限制仍存在，不把五年已读来源改为五年交易规则。F40普通球员能力、潜力、徽章继续严格禁止直接更改（只有独立获准的历史线例外可讨论）；F21签约、F26员工雇聘仍无实机写入验收。

## C. 本轮再次检查的结果

| 检查 | 结果与边界 |
|---|---|
| 7卷JSON逐一fetch/parse | 100+100+100+100+100+100+94 = **694** |
| 索引`ref_id`唯一性 | **694/694** |
| `origin.path#origin.array#origin.item_id`唯一 | **694/694**（含2个已明确的人工检索别名） |
| R01人工指南主题 | **12**，其中10字面主题、2章节/术语别名 |
| R06-B十项奖项直证缺失 | **仍为10**；不补造来源 |
| R06-C原`sources=[]`项目 | **仍为7**；没有升级 |
| 40组能力及86处源锚点 | **组数40、锚点86**，执行与读回状态不升级 |
| 20项旧缺口 | **P0=8/P1=10/P2=2，原JSON语义保持** |
| 八项矩阵相对修复前版本差异 | 只有这八组的旧字段`model_query_api_status`替换，额外新增注释/警告字段；其余32组未改 |
| 本轮原生游戏动作 | **采集0、实机读回0、游戏写入0、存档重进0** |

## D. 建议独立审核复验步骤

复验第1卷`R07.0007`和`R07.0010`，逐字比对原R01指南§3/§4真实章节，再核对其余10项已声明Markdown主题性质；复验能力矩阵八项`model_query_api_status`及相应`execution_warning`/`data_integrity_warning`/`query_prerequisites`/`world_rule_warning`。确认它们未升级`current_save_realtime_readback`、`formal_capture_and_publication`、`existing_execution_scope`、`post_save_persistence`或玩家批准状态；最后抽验全部694、40/86、20缺口和两处遗留无源清单。

**本回执不等于验收通过。** 只有独立审核者可以将R07乃至DEV29研究正式结案；后续FINAL-CODEX只读工程覆盖对账仍需用户独立触发，不能由本修复默认启动。
