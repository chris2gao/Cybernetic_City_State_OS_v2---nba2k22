# DEV29 R07 — 694项知识溯源与40能力成熟度独立审核（2026-10-21）

**正式独立审核：主体研究质量接受，结案需先完成两项定向机读修正。** 当前建议状态为 `R07_REVIEW_TARGETED_CATALOG_REPAIR_REQUIRED`，而非“R07全面实机验收完成”或“FINAL-CODEX自动授权”。修正后只需复验所涉行、来源锚点与七层语义，不需要重做R01–R06或重新检索数百篇文章。

> 审查范围：GitHub main 上R07中文总指南、40组能力矩阵、694项总清单＋七分卷、R07→DEV28研究交接、R07发布自检、R06-D的20项缺口、SOURCES、R01–R06相关源目录及历史生产基线；未使用NBA2K22游戏进程，不执行采集、读写、游戏保存或全部外部网页的语义复验。R系列只准备游戏原料，独立教练/球员人格、媒体和DEV28由其它后续任务负责。

## 1. 本次独立核对：通过项

| 内容 | 核实结果 | 限制 |
|---|---|---|
| 七卷可读取JSON | PART_01..07实际各100、100、100、100、100、100、94，共**694项** | 不是694个原生字段、按钮或已采数据 |
| `ref_id`唯一性 | 实际**694/694**唯一，`R07.0001..R07.0694`连续 | 唯一不代表数据本机运行已读 |
| 原始身份组合唯一性 | `origin.path#origin.array#origin.item_id` **694/694唯一** | 其中R01有2个`manual_research_topics`人工主题ID不能按完整字面在原指南中找到，见问题A |
| 13份原始路径 | 分卷源`origin.path`涉及13个真实GitHub文件，全部能读取 | 包含一个人工R01指南主题目录 |
| JSON原始记录直接匹配 | R07引用的JSON内**682/682条**研究行可通过对应数组中的`id / key / ref / field_key`等身份字段匹配；R01指南12个人工研究主题中10个ID字面出现、2个仅为同义章节标题 | 自检不能将694解释为694条有原始机器主键 |
| 40功能族 | 40个ID唯一；参考`reference_anchors`合计**86/86**可在对应目录的真实`id/key/ref`或R01指南可见标识找到 | 此检验只证明目录项目真实存在，不证明跨机制游戏因果 |
| 来源SRC编号 | 694条引用了77种不同SRC编号，在`SOURCES.md`全部可登记定位 | 没有重新逐项认证网页是否与其原研究句子语义相符 |
| R06历史缺口 | `gaps`继承**20/20**相同的ID、优先级和状态；8 P0、10 P1、2 P2 | 缺口并不是20个玩家已批准的Codex任务 |
| R06-B/06-C历史未知项 | 10个奖项继续保持无来源；R06-C先前7个原生没有直接来源的概念未被假装认证 | 应继续标UNKNOWN，后续需要实机/新来源 |
| 运行时/执行保守性 | 40功能族的当前存档实时读回均`NOT_NEWLY_CHECKED_IN_R07`，事后存盘均`NOT_VERIFIED_FOR_THIS_CAPABILITY_IN_R07`；694项均无R07新增写入授权/逐项已认证外部原文 | **没有在R07新验证生产能力**；10项`existing_production_evidence`只是历史项目证据描述 |
| 权责 | 没有在R07开发教练、球员、媒体人格、自动谈判或游戏写入，媒体仅潜在使用者 | 符合[项目宗旨](../PROJECT_INTENT_AND_MODEL_DEVELOPMENT_BOUNDARIES.md) |

## 2. 需定向修正的两项（不要求研究返工）

### A / P2 — 两个R01人工主题ID与原始指南的字面锚点不一致

在`docs/game_mechanics/catalogs/R07_ITEM_TRACEABILITY_PART_01_V1.json`：

- `R07.0007`: `origin.item_id=K02.SHOT_ZONES`；原指南的章节标题为 **`## 4. K02.SHOT_CHART / SHOT_ZONES`**，包含`SHOT_ZONES`主题但并无完整字面`K02.SHOT_ZONES`。
- `R07.0010`: `origin.item_id=K02.PER36`；原指南讨论`Per 36 Minutes`、`Per36`，但没有完整字面`K02.PER36`。

**处理**：对这两项明确`origin_identity_kind=GENERATED_GUIDE_TOPIC_ALIAS`（或者与既有模式一致的描述性字段），加上**真实存在的指南章节/术语定位**；不要装作原始游戏或原文有该机器主键，也不应为了让复核通过就悄悄向旧R01攻略添加虚构“原始索引ID”。本次验收以有据的内容主题对应为准；建议再检查R01 12个manual topics整体分级，不让后续Codex误把`manual_research_topics`当原生JSON记录。

### B / P1 — 成熟度矩阵的`model_query_api_status`混入执行/政策和状态时序值

在`docs/game_mechanics/catalogs/R07_GAME_CAPABILITY_MATURITY_MATRIX_V1.json`，下列功能族的`model_query_api_status`不是“模型可查询事实/接口的状态”，而是**另一维度**：

| 功能族 | 当前`model_query_api_status` | 为什么不能作为查询证据 |
|---|---|---|
| F21自由市场与真实签约 | `SIGNING_WRITE_UNVALIDATED` | 签约写入不可用≠有无真实自由球员池查询 |
| F22普通交易 | `APPROVED_BOUNDED_EXECUTOR` | 交易执行验收≠交易资产/名单数据能被模型查询 |
| F23选秀权 | `EXECUTOR_OLD_PLUS3_REJECTION` | 第4/5届执行限制≠已读五届选秀权数据不可查询 |
| F26员工 | `STAFF_HIRE_FIRE_NOT_VALIDATED` | 雇聘写入未验证≠已发布Staff JSON不可查询 |
| F27世界Setup | `R07_NO_NEW_WRITE` | 没有R07写入不是查询状态 |
| F32时间/阶段与批次 | `CAPTURE_BATCH_REPORTED_SAVE_DATE_REQUIRES_VERIFICATION` | 混合批次查询与原生Save/日期的真实性 |
| F39全量采集/SQLite | `CURRENT_BATCH_PERMISSION_BOUND` | 权限前置条件本身不说明特定API可查询程度 |
| F40历史与历史重力 | `ABILITY_CHANGES_FORBIDDEN_EXCEPT_SPECIFIC_APPROVAL` | 玩家编辑能力规则不属于查询API成熟度 |

**处理**：用`NOT_CERTIFIED`、`PRIOR_SQLITE_JSON_REPORTED_SCOPE_ONLY`、`FIELD_LEVEL_UNKNOWN`等明确**查询层**的状态替换或新增相应解释；将旧执行/政策信息保留在`existing_execution_scope`、`permission_to_act`、`unknown_and_handoff_gaps`或明确的新`execution_warning`。**不要因纠正分类而擅自升级为已在当前游戏存档真实查询/写入。** 这一混淆会误导FINAL-CODEX生成错误的能力差距对账，故须在其启动前修正。

## 3. 风险评价和真实生产范围

R07实际把所有研究能力分开记录为`research/UI/static-locator/runtime-read/formal-batch/query/approved-execution`七个维度，方向正确。40项是**概念族**，既有10项生产证据引用历史基线、受限原生教练读写和批准普通交易等；不是40项经过实机测试的当前API。尤其Game Logs/逐场Box、3D-Sim来源区分、Autosave/Reload、球员实时健康、FA签约、Staff雇聘等仍有明确缺口。

694项也只是从已选定的既有研究目录汇总的**异质项目清单**，不应被误解为2K22全部内存、全部球员字段或所有战术动作原生全集。此次静态校验和原始存在性核对不等同逐项语义/模式可靠性验证。R07→DEV28交接作为研究档案可用，但不自动生成工程任务或突破真实玩家批准/球员Ability/Potential/Badge修改限制。

## 4. 审核决定和下一步

- **R07主要成果：接受**。七分卷实际可读取、694组合唯一、682原JSON源记录精确匹配、40组及86原目录锚点有效、R06缺口和证据边界保留，无需重做R系列主题研究。
- **R07机读资料正式结案：暂缓**，状态`R07_REVIEW_TARGETED_CATALOG_REPAIR_REQUIRED`，先完成上面A/B两处定向文档／JSON修正；修正范围局限分卷PART_01、40组矩阵及必要自检/PROGRESS，不新增研究、游戏执行或角色算法。
- **FINAl-CODEX尚未获授权**。定向修正通过独立复核后，用户再决定是否发起Codex对原生Registry、M0、DEV14、SQLite、latest.json、配置与R07资料做当前真实能力对账；DEV28/人格系统另由用户按需立项。
- **可继续项目规划，不要求重新R01–R06**。本报告仅记录上述发现，未改变游戏数据、选秀权V4规则或任何执行器。
