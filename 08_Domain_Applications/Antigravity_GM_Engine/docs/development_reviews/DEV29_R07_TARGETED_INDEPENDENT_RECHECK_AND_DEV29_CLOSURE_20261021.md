# DEV29 R07 A/B 定向修复独立复验与 DEV29 研究结案（2026-10-21）

> 审核角色：新网页 GPT 开发规划／独立审核窗口。**正式结论：R07 定向修复 PASS，DEV29 R01–R07 游戏机制研究阶段结案；PC22 目标存档原生 I/O 与持久性仍有缺口。**
>
> 审核基准：GitHub `main` @ `0b56525fcf42f11b0f42b223946ca003e8d8ad0f`（复验启动时）；修复前对照 `829c7f717238`（矩阵）及 `4e8814bd36f3`（R07 Part 01）。
>
> 结案状态：`DEV29_RESEARCH_CLOSED_WITH_PC22_NATIVE_IO_GAPS` / `R07_RESEARCH_CLOSED_AFTER_INDEPENDENT_RECHECK`。
> 本报告**不是**启动 FINAL-CODEX、DEV28、Codex 额度、游戏采集／写入、真实 Save 或任何人格开发的批准。

## 一、检查范围与来源

复核此前 [独立初审](DEV29_R07_INDEPENDENT_REVIEW_20261021.md) 的两项保留意见、[定向修复回执](DEV29_R07_TARGETED_CATALOG_REPAIR_20261021.md)、[R07 总索引](../game_mechanics/catalogs/R07_ITEM_TRACEABILITY_INDEX_V1.json)及全部 7 卷、[40 族能力成熟度矩阵](../game_mechanics/catalogs/R07_GAME_CAPABILITY_MATURITY_MATRIX_V1.json)、[原R01指南](../game_mechanics/guides/K01_K02_GAME_STATS.md)、13 份引用原始文件、[R06-D原始缺口](../game_mechanics/catalogs/R06D_CROSS_DOMAIN_MECHANISMS_AND_GAPS_V1.json)、R06-B/R06-C缺证目录，以及修复前 Git 文件版本。

本次是**跨窗口的原始文件静态审核**：无 PC22 运行进程、当前存档采集、实机菜单比对、玩家批准的执行、Save/Reload 或外部网页逐条语义复核。已发布研究资料只在已有证据等级范围内接受。

## 二、两项修复的独立结论

### A / 原R01两个人工检索主题别名：PASS

- `R07.0007` 的 `origin.item_id=K02.SHOT_ZONES` 在原指南中**不是**机器主键；其真实标题为第4节 `K02.SHOT_CHART / SHOT_ZONES`，正文可找到 `Shot Zones Aggregates`。
- `R07.0010` 的 `origin.item_id=K02.PER36` 同样不是原始机器主键；真实标题为第3节 `K02.PER_GAME_PER36_ADVANCED`，正文出现 `Per 36 Minutes`。
- 现行两个条目均有 `origin_identity_kind=GENERATED_GUIDE_TOPIC_ALIAS`、`origin_machine_record_id_exists=false`、准确章节标题/编号/原文术语、`origin_exact_machine_id_in_guide=false`。
- R01其余十个 `manual_research_topics` 的主题标记在原文中可找到字面对应，但全部十二条均已明确为Markdown人工主题，而非JSON或NBA2K22 Native机器主键。
- 与修复前Part01对照，本轮只增加或修正这十二条的身份语义和别名证据；Part01条目数100不变。

### B / 八个功能族混合查询、执行与权限维度：PASS

修正后真正的 `model_query_api_status`：
- F21、F27、F40：`NOT_CERTIFIED`；
- F22、F23、F26、F39：`PRIOR_SQLITE_JSON_REPORTED_SCOPE_ONLY`；
- F32：`FIELD_LEVEL_UNKNOWN`。

原本属于签约写入、已审批交易、选秀权旧+3阻断、员工雇聘、R07无新写、GameDate/Save真实性、批次权限及人物能力禁改的值，均保留在对应的 `execution_warning`、`data_integrity_warning`、`query_prerequisites`、`world_rule_warning` 或既有 `existing_execution_scope` 中，并有 `reviewed_old_query_value` 和解释。

逐族比较修复前矩阵：**仅F21/F22/F23/F26/F27/F32/F39/F40**的查询状态与新增证据/警示注释变化；其他 **32/40** 功能族不变。四十族的 `current_save_realtime_readback`、`formal_capture_and_publication`、`existing_execution_scope`、`post_save_persistence`、`permission_to_act` 五组原有能力字段 **均未改变**。未将任何查询字段校正误解释为游戏写入或真实Save证据的升级。

## 三、完整性与旧缺口保持验证

| 检查项 | 独立重验值 |
| --- | --- |
| JSON分卷与条数 | 7卷：100+100+100+100+100+100+94 = **694** |
| 连续 `R07.0001…R07.0694` 与唯一ref_id | **694/694** |
| `origin.path#origin.array#origin.item_id` 唯一 | **694/694** |
| 13份原始资料路径可读 | **13/13** |
| 原JSON记录直接身份对应（id/key/ref/field_key/native_registry_key） | **682/682**；分卷1–3为288/288，分卷4–7为394/394 |
| R01人工Markdown主题 | 10原文字面主题 + 2明示章节别名 |
| 功能族与唯一ID | **40/40** |
| `reference_anchors` 原路径/数组/项目身份 | **86/86** |
| R06-D继承缺口 | **20/20完全一致**；P0=8，P1=10，P2=2 |
| R06-B没有对应直证的奖项 | **10**条依然 `sources=[]` |
| R06-C无直接来源的阶段/保存概念 | **7**条依然 `sources=[]` |
| 当前存档实时读回 / Save持久性 | 40族仍分别为 `NOT_NEWLY_CHECKED_IN_R07` 和 `NOT_VERIFIED_FOR_THIS_CAPABILITY_IN_R07` |

**统计含义：**694是不同研究资料种类组成的检索项，不是694个原生字段；40是能力族，不是40个可用API；86是原目录锚点，不是游戏UI/运行时认证次数。项目历史生产证据可用于后续对账，不等于本轮新增实机证据。

## 四、独立审核裁定

- **R07 A/B两个定向问题均已修复，通过独立复验；R07研究正式结案。**
- **DEV29 R01–R07公开资料/知识矩阵研究阶段正式结案**，不需重新搜索R01–R06、返工R07或继续扩大研究索引。
- 研究完成不表示PC22最新存档的原生单场Game Logs、双边Box/Shot、真实GameDate、3D/Sim分离、历史Save、自由市场签约、员工雇聘、Playbook原生类型或未来选秀权执行均已验证。
- 选秀权V4规则已经取消人为三届交易上限，但旧执行器+3限制仍是**另一个待玩家授权的独立小型工程缺口**，不因研究结案自动修复。
- 保留[六阶段模型职责](../PROJECT_INTENT_AND_MODEL_DEVELOPMENT_BOUNDARIES.md)：采集→数据分析→独立教练（未实现人格）→独立球员（未实现人格）→各队GM→用户批准后的汇总执行。R07只提供游戏原材料，不实现Coach/Player/Media人格、意愿或谈判策略。
- **下一许可门禁**：如玩家以后明确批准，启动有界 `FINAL-CODEX` 只读静态工程能力对账，比较R07与Registry/Native Profiles/DEV14/SQLite/manifest/查询/既有有限执行器；其后另批DEV28 D28-0～D28-5真实缺口实施。未经批准一律不启动，不暗示DEV28已完成。

本审核未执行代码开发、游戏内存写入、球员属性修改、合同执行、真实Save、赛季推进或人格开发；提交的仅是研究审核档案。
