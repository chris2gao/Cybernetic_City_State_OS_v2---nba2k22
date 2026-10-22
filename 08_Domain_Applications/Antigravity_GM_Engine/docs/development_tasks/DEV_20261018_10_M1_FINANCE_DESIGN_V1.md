# DEV10 M1 — 财务、三年合同与资产情景：实现设计

状态：`DESIGN_READY_FOR_SOL_IMPLEMENTATION`；设计基线：`67bf4dc`。玩家在 M0 合并后明确开始后续流程，本轮按约定完成 Astra 设计，随后交 Sol 实现。本文不是 M1 已实现回执，也不批准经营规则或游戏动作。

权威总纲：[DEV10 V2](DEV_20261018_10_GM_V4_SQLITE_FIRST_MASTER_PLAN_V2.md)。开发取舍：[实现优先规范](../DEVELOPMENT_BOUNDARIES_AND_VALIDATION_POLICY.md)。真实 Web 连接由玩家后续建立，不阻塞本地工程。

## 1. 要交付的实际能力

让 GM 对任意球队回答四个不同问题：现有合同有多少已读金额；未来三个赛季在明确假设下承担多少工资；某项经营方案增加什么成本与占用什么资产；规则是否足以判断这笔操作可执行。已知部分立即计算，未知部分定位到具体字段或规则，不让一项缺口使整份分析失效。

首版提供全联盟三年表、单队合同钻取和方案对比。三年定义为所选批次所属赛季及随后两个赛季，输出完整赛季字符串。需要三个未来赛季时显式传起始赛季，不静默改变口径。金额为整数美元，不依赖模型心算。

至少比较 `KEEP`、`INTERNAL_COACHING`、`TRADE_OR_SIGNING`；无合理交易时后者可标“无候选”，不得为了凑数虚构交易。教练方案不产生球员薪资变化，但不据此宣称所有经营成本为零。

## 2. 当前实现与复用点

| 现有入口 | 本轮处理 |
| --- | --- |
| `gm_data_access.snapshots.load_snapshot` / `QuerySession` | 固定同批静态双库，复用来源绑定、小结果查询及只读机制 |
| `q_players.contract`、`salary`、`years_left` | 提供六薪资槽、选项和延期等已采字段；JSON 值缺失保留缺失 |
| `q_finance` / `q_finance_semantics` | 原始球队金额及语义说明；cash 不进入可签约额度 |
| `q_picks` | 使用同批认证的三届简单选秀权，不导入现实保护/交换条款 |
| `gm_core.calculations.observed_sum/difference/draft_pick_window` | 复用确定性计算；另加“已知小计+覆盖情况”，不改旧函数缺失语义 |
| `gm_core.calculations.salary_exchange` | 空 outgoing/incoming 当前会返回 UNKNOWN；新情景明确空集合为该边零金额，不把缺失金额当零 |
| `gm_core.finance.metrics` | 保留既有代理标签和旧调用；新能力通过独立显式入口提供 |
| `gm_core.offseason` | 仅参考纯金额计算和数据形状；保留 `SYNTHETIC_ONLY` 及既有资格保护，不以真实月度名单直接启动竞价 |
| `approved_signing_executor` | 闸门仍关闭；财务分析不导入执行器，不打开开关 |

源码核对依据为上述文件及 `config/memory_field_profile.json`、[休赛期 P0](../development_reviews/DEV_20261017_04_OFFSEASON_FA_P0_RESEARCH.md)、[签约说明](../38_APPROVED_SIGNING_EXECUTION.md)。六薪资槽与当前/未来赛季的精确滚动关系未认证，不能用年限一个字段消除这个缺口。

## 3. 数据契约：金额、时间和可信度分别表达

顶层 `FinanceRunV1`：

```text
schema_version, calculation_version, run_id, created_at
source_binding {career_id, snapshot_id, batch_id, game_date, data_updated_at,
                publication_status, query_version}
base_season, horizon_seasons[], season_anchor_evidence
rule_set_id, assumptions[], teams[], scenarios[]
status = ANALYSIS_ONLY
```

每个 `MoneyValue`：`value`（整数或 null）、`unit=USD`、`basis`（OBSERVED / CALCULATED / SCENARIO）、`coverage`（COMPLETE / PARTIAL / NONE）、`source_refs[]`、`assumption_ids[]`、`unknown_reasons[]`。已观察到编码值不等于已观察到其商业含义；来源证据与使用假设同时保留。

`PlayerContractInput` 包含批次内 `identity`、team_id、name（仅显示）、`salary_slots[1..6]`、years_left、original_contract_years、contract_option、extension_length/option、contract_type及各自证据。禁止用姓名拼接为永久 ID。跨批身份配对留给后续明确映射；单个 M1 run 不跨批拼名单。

球队逐年输出：

- `observed_slot_amounts`：原样列出已读槽位及覆盖情况，不称为未来保证支出。
- `known_salary_subtotal`：有明确季节归属、且不依赖未决条件的金额小计。没有可归属条目时为 null；部分缺失时可以输出小计，但完整总额为 null。
- `projected_salary_total`：按显式假设计算的情景总额；每个假设关联具体玩家与赛季，不能只在页脚笼统写“估算”。
- `conditional_salary`：选项、延期或槽位歧义产生的分支；不强行合并为保证薪资。
- `known_contract_count`、`uncertain_contract_count`、`known_roster_occupancy`；名单上限或自由球员资格未认证时不输出虚假“空位”。
- `salary_cap_proxy_gap`、`tax_line_proxy_gap`：仅当有适用该季的明确参考/配置时计算，名称含 proxy；`signing_capacity` 独立给值或 UNKNOWN。
- `pick_assets[]`：year/round/original_team/current_owner/asset_id/eligibility；未来新秀工资另列未知，不按现实顺位补造。

## 4. 三年计算算法

1. 在 CLI/适配层锁定一个 `source_binding`，取30队身份、名单合同、财务语义和简单选秀权。内部可迭代分页；给模型只输出30队概览或指定队详情，不能默默少读一页。
2. 读取批次所属赛季。日期仅帮助定位，不能替代“休赛期已过账”的玩家信息。缺少赛季锚点时接受明确 `--base-season` 并记录为调用者假设。
3. 先建立六槽原始金额清单。原生低31位金额解释复用现有 profile；不在这里修改采集解码器。
4. 建立可计算的 `SLOT_SEQUENCE_ASSUMED` 情景：明确假设 slot1 对应 base_season、slot2/3顺延。即使 raw 完整，该季归属仍为 SCENARIO，直到后续证据认证。未知年限、延期或选项不会被删除；影响到的年度另列未知/分支。
5. 不用 `years_left==1`直接认证次季自由球员。情景可假设当前合同到期，但必须保留下一季延期/选项未知。零薪资槽本身不证明无合同；正数槽也不证明未来保证支出。
6. 选项只在已知作用年度时构造 exercise/decline 两个分支；原生 `2_YEAR_TEAM_OPTION` 无年度映射时不擅自当最后一年。延期不自动叠加到原合同，防止重复计算。条件缺失时仍保留非受影响年度和原始槽小计。
7. 合并每队每年的金额、覆盖人数和假设。未来工资帽/税线可由情景参数显式提供（固定/逐年列表）；不自动沿用2021规则或预测增长率。没有参数仍能生成合同表。
8. 保存为派生记录；来源不完整、财务政策未批准或执行器未启用分别标记，不用一个全局 BLOCKED 抹掉全部已算结果。

本阶段优先把可计算的情景做好，不追加原生UI、跨年滚动、游戏保存或现金实测。未来修正时间映射时新建 calculation_version/run，保留旧假设与结果，不篡改历史观测。

## 5. 方案与经济约束

`ScenarioV1`：`scenario_id, kind, source_run_id, assumptions, moves, team_year_deltas, assets_before_after, rationale, opportunity_cost, finance_eligibility, executor_readiness, approval_status=NOT_REQUESTED`。

- 交易：对每个球员从 A 扣除同一工资向量并向 B 加入；简单签按同一 asset_id 转移。输出双方三年工资和人数变化。一个情景内资产只能分配一次、送出方必须拥有；互斥备选情景可重复使用同一资产。交易本身不改变原合同，不写资金或假设现金补偿。
- 签约/续约：输入明确的逐年金额及生效季；“新增合同”“替换当前合同”“未来延期”必须区分。不能在已有合同上无意双算。未认证自由球员来源时允许成本研究，资格 UNKNOWN；执行器未验收时为 `BLOCKED_EXECUTOR`，不会因此阻止工资情景比较。
- 内部优化：关联 M2 战术卡及现有19/18字段提案，金额变化仅统计本次明确包含的合同变化。当前人员维持方案与内部方案都保留资产灵活性，但不声称必然增加胜场。
- 机会成本：列出失去的球员角色、下一次续约窗口、消耗的三届选秀权和可替代方案。无依据不将一枚签折成固定美元，不将能力加权分数伪装胜场价值。

经济政策采用可注入 `ExternalFinancePolicyV1`，不在本轮替玩家决定硬限制：

```text
policy_id, version, status (DRAFT / PLAYER_CONFIRMED), evidence_ref
applies_to {career_id, seasons[], phases[]}
team_spending_limit_by_season (optional)
counting_basis = ROSTER_CONTRACT_SALARY_ONLY (first supported basis)
unknown_cost_handling, expires_after_season
```

首版建议候选：用“逐队逐年自定工资支出预算”表达老板意愿，已知合同加新方案占用预算；税费、收入、死钱等没有可靠口径时另列未覆盖项，不从 raw cash 反推预算。此候选保持 DRAFT。未批准时返回规则资格 UNKNOWN，同时继续输出可审阅的成本和预算需求；不把 UNKNOWN 等同批准或一律否决所有研究。

现实参考只入知识层：[NBA 2021–22 官方工资帽/税线公告](https://www.nba.com/news/salary-cap-set-at-112-4-million-for-2021-22-season)给出 $112.414m / $136.606m。两值仅属2021–22 NBA参考，不能认证本局 cap、实际税额或未来年度规则。M1 不重建完整 CBA、不采用后续赛季的第二土豪线。

## 6. 实现位置与派生存储

建议新增：

| 文件 | 职责 |
| --- | --- |
| `src/gm_data_access/finance_inputs.py` | 同批只读输入适配；产出纯数据 DTO，不把连接交给 gm_core |
| `src/gm_core/finance_projection.py` | 纯计算：槽位/时间归属、逐年汇总、未知传播 |
| `src/gm_core/finance_scenarios.py` | 纯计算：KEEP/内部/交易签约比较、所有权和工资向量变换 |
| `src/gm_workbench/store.py` | 仅派生库连接/事务/版本；拒绝 saves/query_snapshots 路径 |
| `scripts/gm_finance.py` | 显式运行、查询结果与导出精简报告，不调用采集或执行器 |
| `web_gm/knowledge/game_engine_rules_v1.json` | 由本轮机制清单整理的小型规则条目 |

首次只建 `database/workbench/<career>/gm_workbench.sqlite`（ignored），三张表即可：

```text
finance_runs(run_id PK, career_id, batch_id, snapshot_id, base_season,
             calculation_version, rule_set_id, source_binding_json,
             assumptions_json, status, created_at)
finance_team_years(run_id, team_id, season, result_json,
                   PRIMARY KEY(run_id,team_id,season), FK run_id)
finance_scenarios(run_id, scenario_id, kind, result_json,
                  PRIMARY KEY(run_id,scenario_id), FK run_id)
```

启用 foreign_keys；一次 run 事务提交；相同 run_id 再写拒绝或明确幂等返回，不能覆盖历史。不做完整事件总线、角色认证平台、自动迁移所有旧库。M2后加自己的表，M3/M4复用此根目录。公开交接由显式 export 写入指定小目录，默认 `_exports`；数据库和查询快照不入Git。

拟议 CLI（实现时以真实 `--help`为准，当前不可运行）：

```text
gm_finance.py project --career C --batch B --horizon 3 --assumptions FILE
gm_finance.py compare --run RUN --scenario FILE
gm_finance.py show --run RUN [--team SAS] [--scenario S]
gm_finance.py export --run RUN --output DIR
```

`project/compare`为派生写入，只有明确调用才执行；`show`只读。默认输出30队精简总览，各队可钻取。金额单位/假设/版本/来源随结果返回。拟议接口无需新增外部服务。

## 7. 足够证明本次实现的验收

仅做直接相关案例，复用 M0 保护，不重测 SQL 攻击矩阵或所有导出路径：

1. 一个小型合成合同集：完整、缺槽、选项未知、延期未知并存；证明已知小计、情景、完整总额三者不混淆。证明 horizon 年份与显式槽位假设一致。
2. 同一交易双方工资向量对消；空送出边为零、缺失金额为未知；重复资产不重复出售。续约替换不双算。
3. DRAFT/错年度政策不变成执行资格，cash异常不影响合同计算；部分UNKNOWN不阻塞无关结果。
4. 派生 run 完整保存和读取，事实库路径不能成为写入目标。采用一个事务中断案例即可，不展开故障注入平台。
5. 现有 M02 静态副本生成30队三年结果，只钻取 GSW/SAS/CLE；验收依据是来源、金额计算与标识，不要求真实签约或已知未来财务。

本设计回合没有运行这些测试/查询。实现结束提交独立 M1 验收与commit/PR，更新 docs33/34 和必要使用手册。新知识/派生能力不登记成新游戏观测来源，不改执行能力表的已验收状态。
