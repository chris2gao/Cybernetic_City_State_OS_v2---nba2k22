# DEV10 M2 — 篮球知识与30队长期经营状态：实现设计

状态：`RESEARCH_AND_DESIGN_READY_FOR_SOL_IMPLEMENTATION`。基于 `67bf4dc`，本轮产物是设计和研究材料；没有生成本局正式球队决策，没有切换 GM V4。依赖总纲 [DEV10 V2](DEV_20261018_10_GM_V4_SQLITE_FIRST_MASTER_PLAN_V2.md)，配套 [M1设计](DEV_20261018_10_M1_FINANCE_DESIGN_V1.md)。

研究底稿：[篮球知识、三队试点与30队参考](../development_research/DEV10_M2_BASKETBALL_AND_FRANCHISE_RESEARCH_V1.md)。机制底稿：[现有游戏机制清单](../development_research/DEV10_GAME_ENGINE_KNOWLEDGE_V1.md)。Sol 可直接整理为小型 JSON 和检索接口，无需再从巨型资料库重做研究。

## 1. 产品行为

GM按问题检索少量战术卡，看到适配角色、代价、反例、当前可用字段和来源，再结合本局事实决定内部优化、市场补强或HOLD。默认不加载全库、不把30队变成30个刻板标签。球队参考与当前策略分开，现实历史不是本局事实；球队可以根据本局证据改变战略。

本轮知识内容以12个高价值主题、GSW/SAS/OKC三个完整方法试点及30队2021历史参考为起点。30队参考不是完整组织史，也不证明老板愿意花多少钱；未取得依据的文化/支出偏好留空。不得从当前阵容倒推“这队天生是什么文化”。

## 2. TacticCardV1

```text
card_id, version, title, tags[], basketball_principle
required_roles[], required_abilities[], counters_and_weaknesses[]
opportunity_cost[], observable_signals[], unavailable_signals[]
native_links[] {scope, field, semantic_label, mapping_status,
                evidence_ref, caveat}
reference_sources[] {source_id, url, section, fact_scope}
confidence {basketball, native_mapping, in_game_effect}
game_version_scope, status=REFERENCE_OR_HYPOTHESIS, superseded_by
```

证据使用三轴，不能用单个 HIGH 把现实篮球可靠性转移给游戏效果：

- `basketball`：公开参考支持什么原则；GM适配判断另标推断。
- `native_mapping`：字段名/原生枚举能否映射；直接有标签为 `NATIVE_ENUM`，组合近似为 `HYPOTHESIS`，无接口为 `NO_DIRECT_MAPPING`。
- `in_game_effect`：本局没有实验结果时 `UNMEASURED`；可写不证明提高胜率。玩家经验“教练影响自然成长”保留为 PLAYER_OBSERVED_GENERAL，不伪造参数成长公式。

原生 raw 值不复制成第二份长期白名单。检索工具用当前 `coach_tactics_profile.json` 与所选批次字典解析 `semantic_label`；字典没有目标时仍能返回篮球卡片，具体写入目标不可生成。动态 Playbook 只用同批已加载具名条目，Freelance 保留四槽顺序。

首版检索采用 JSON 词条+标签/球队/字段过滤，最多返回5张卡摘要；按 ID 钻取全文。无需向量库、在线 embedding、全联盟预载或新外部服务。相同知识可用于历史线，年代条件显式登记，不能强制旧人物使用尚未出现的现实结果。

## 3. TEAM_STRATEGY_STATE_V1

每条状态代表“某局某队在某批次的一版派生经营判断”，不代表游戏内设置或玩家批准。字段：

```text
state_id, schema_version, career_id, team_id, team_abbr
revision, supersedes_state_id, strategist_version, created_at
source_binding, finance_run_id (optional)
identity_reference[] {reference_id, historical_period, claim, source_id}
identity_evidence[], ownership_cost_preference_if_verified
competitive_window {assessment, evidence, alternatives}
core_assets_and_hold_thresholds[] {batch_local_identity, role,
                                  retain_reason, reconsider_conditions}
contract_window, tactical_direction[] {card_id, fit, missing_roles, evidence}
current_hypotheses[], observed_challenges[], current_actions[]
change_conditions[], last_review_batch
status = UNASSESSED / DRAFT / REVIEWED_ANALYSIS
```

`current_actions`含 `HOLD/PROPOSED/RESEARCH`，不允许模型在策略状态内设置 EXECUTED/PLAYER_APPROVED。玩家审批与执行回执继续走现有独立流程。`REVIEWED_ANALYSIS`仅表示资料分析过，不能冒充玩家确认。

慢变量：组织历史参考、长期资产观、已确认老板偏好；快变量：本局竞争窗口、合同、角色缺口、近期假设。新批次不自动推翻慢变量，沿用时保留原来源；快变量必须带对应批次与复核时间。历史薪资/战绩不能当本局当前值。

### 初始化和修订

1. 显式 `strategy init` 只创建30队 `UNASSESSED` 候选结构与研究参考，当前核心/动作/老板限额留空。这是开发可用的准备结果，不冒充“30队已经分析”。
2. 正式GM被玩家触发后，用同批资料逐队生成 DRAFT/REVIEWED_ANALYSIS，说明持有与改变的条件。不要求每队进行交易或填写虚构胜率预测。
3. 修订必须带旧 state_id、新来源、变化理由与被否定假设。保留旧 revision，`latest`只是查询视图；同一预期旧版被别人更新时返回冲突，防止丢失更新。无需扩展成多用户协同系统。
4. 财务 run 不存在时仍可做篮球/文化研究，合同和预算结论标缺口。财务与策略引用不同批次时显示需复核，不能将旧 run 数值当当前资金。
5. 现实历史与历史线角色发生变化时，比较角色能力和球队当前目标，不保证某球员必须在现实母队或取得现实荣誉。历史重力人物定制仍属独立开发，不进入本模块。

## 4. 三队试点如何做得有区别

研究底稿提供三套条件式政策，均为设计假设。实现验收用**同一合成问题**验证政策能够表达不同权衡：一个即战力侧翼，需要付出未来首轮并承担多年工资；现有阵容还可内部改善。

| 参考试点 | 优先追问 | 可以转向的证据 |
| --- | --- | --- |
| GSW | 该补强是否明显改善核心现有窗口内的角色短板，内部优化能否替代，未来工资能否承担？ | 本局已无争冠核心或投入无法解决短板，就保留资产或重建；不能仅凭队名花钱 |
| SAS | 现有人才是否被合理使用，传切/角色互补能否先释放价值？ | 当本局具备争冠窗口且外部提升实质明确，可以付出资产；发展不是永不交易 |
| OKC | 资产转化时机是否成熟，新增球员能否与本局核心合同窗口配合？ | 已有成熟竞争基础时可集中资产升级；积累资产不是永远卖即战力 |

这里的区别来自公开历史启发的经营假设；所有队仍追求赢球。实验只证明状态/比较工具能表达差异，不证明这些假设适用于当前真实三队。正式本局判断由玩家另行触发 GM 后生成。

## 5. 文件、查询和工作台

建议新增 `web_gm/knowledge/tactics_v1.json`、`franchise_references_2021_v1.json`、`sources_v1.json`；机制条目用M1提供的 `game_engine_rules_v1.json`。知识 schema 放 `web_gm/schemas/`，纯检索与状态校验在 `src/gm_core/knowledge.py`、`strategy_state.py`；CLI为 `scripts/gm_knowledge.py` / `gm_strategy.py`。

知识 schema 必须要求来源、适用期和证据等级；不要求把未实测内容删光。初始化候选文件默认 `_exports`；正式赛季目录/W03档案不受本轮实现修改。

复用M1派生库，仅加：

```text
team_strategy_states(state_id PK, career_id, team_id, revision,
                     source_batch_id, supersedes_state_id, status,
                     state_json, created_at,
                     UNIQUE(career_id,team_id,revision))
```

知识 JSON 是小型版本化参考，状态 SQLite 是本局派生记录，不把两类揉成观测表。显式导出 GitHub 精简摘要时只含当前版本/历史指针/引用，不上传工作台二进制。M2可先做纯文件整理并行于M1，落库适配等M1 store稳定后串行接入；不另造第二个store。

拟议命令（实现前不可当作现有入口）：

```text
gm_knowledge.py search --tag pick_and_roll --limit 5
gm_knowledge.py show --card PNR_PRIMARY --career C --batch B
gm_knowledge.py franchise --team SAS --period 2021
gm_strategy.py init --career C --batch B --output DIR
gm_strategy.py save --input FILE --expected-revision N
gm_strategy.py show --career C --team SAS [--revision N]
```

代码不自动生成GM观点；显式 `save`保存调用方已提供的派生判断。对于远程模型，身份授权仍由玩家建立的本地运行边界处理，不因 `--role` 参数声称认证已完成。

## 6. 验证与交付条件

- 12卡、30队参考及source_id可解析，卡片实际引用当前字段；用一份内容完整性检查覆盖即可。
- 选一个直接枚举映射、一个Drop近似、一个缺失来源案例，证明输出分别保留映射/假设/缺口；不穷举所有raw值。
- 三队同一合成情景能表达各自假设、替代方案、转向条件；不写本局正式策略，不模拟比赛。
- 两个状态revision保存后旧版可读，错旧版写入不覆盖。30队初始化与30队正式评估在报告中分别计数。
- 不运行全套教练/采集/执行测试；不要求游戏UI、Web连接或对战结果验收。

实现报告逐项记录“知识已整理”“可检索”“状态可维护”的证据。M1/M2具备消费接口后可进入M3内部框架设计，按玩家安排选择模型；Web真实连接仍是正式网页生产使用前的事实条件，不是内部研发门槛。GM V4规则切换继续等待另行明确批准。
