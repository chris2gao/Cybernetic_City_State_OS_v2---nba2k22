# DEV10 — GM游戏机制知识底稿 V1

研究范围：本项目 NBA2K22 PC Current Gen 与玩家外挂规则。核对代码基线 `67bf4dc`。本页供M1/M2结构化整理，状态 `RESEARCH_REFERENCE`；不同证据层不得互相冒充，不改变当前执行权限。

结构化规则字段为 `rule_id, version, applies_to, claim, scope, source_evidence, confidence, native_field, can_observe, can_execute, execution_condition, superseded_by`。`can_execute`不能只给真假：区分实现可用但须具体批准、未验收、禁止、无接口。正式运行应读取最新 capability 表，历史研究记录不是永久权限。

| rule_id | 已核对的结论 | 证据及使用方式 |
| --- | --- | --- |
| PHASE_TRIGGER | 采集、GM决策、游戏执行分别由玩家触发 | `config/gameplay_policy.json`；EXTERNAL_PLAYER_APPROVED；开发不能自动推进阶段 |
| FULL_CAPTURE | 所有新生产更新走全量已认证来源 | `AGENTS.md` 全量政策；没有单来源更新开发任务 |
| STATIC_FACTS | M0从同批静态双库按需读取，小结果/聚合；角色名参数不是认证 | `src/gm_data_access/`、`docs/GM_SQLITE_QUERY_ACCESS.md`；实现已合并，Web连接延后 |
| COACH_DEFAULT_19 | 19默认字段可提案、经明确批准受控执行 | `config/coach_tactics_profile.json`、`docs/40_COACHING_EXECUTION_RUNBOOK.md`；模板/策略不等于批准 |
| OVERALL_DEFENSE_18 | 针对指定对手整体组批改18字段，保留对象及未选字段 | `coaching_overall.py`及同批字典；不是逐人防守/任意内存槽接口 |
| TEMPO_RAW | 原生Tempo raw开放；UI含义/效果未知 | 玩家明确选择，见GM教练手册；不能自动翻译成PACE或百分比 |
| ROTATION_INDIRECT | BenchDepth/BenchUtilization可间接影响轮换；个人分钟由AI安排 | `web_gm/manuals/GM_COACHING_OPERATIONS.md`；不开发锁分钟和循环补写 |
| NATURAL_GROWTH | 玩家经验支持教练对自然成长有影响；无具体增幅公式 | 同手册及gameplay_policy；训练、普通能力/倾向/徽章编辑均排除 |
| TRADE_SIMPLE | 普通球员转队和简单选秀权有受控执行路径；合同不随普通交易重写 | `docs/37_APPROVED_TRADE_EXECUTOR.md`、标准v2执行器；名单计数/身份/回执机制复用 |
| TRADE_ECONOMY | 外挂经营决策不由原生CPU报价或原生薪资匹配自动否决 | DEV10 V1 M1玩家方向；这不是无限预算授权，独立经济规则需版本化 |
| PICKS_THREE_DRAFTS | 简单年/轮/原队/现主队，只交易接下来三届未完成选秀 | gameplay_policy、`q_picks.trade_eligible`；现实保护/互换不复制进玩法 |
| SIGNING_FINAL_CONTRACT | GM先确定球员、目标队和逐年合同；本地执行不重新谈判 | `docs/38_APPROVED_SIGNING_EXECUTION.md`；源码未实机验收，两个开关False |
| OFFSEASON_SIM | 已有离线竞价核心只接synthetic输入 | `src/gm_core/offseason.py:plan`实际入口检查；不是生产到期池或已实现的全联盟流动封锁 |
| OFFSEASON_EXPIRY | 年限为1、无NBA归属都不足以认证真正到期/可签对象 | 休赛期P0报告、M0的EXPIRY_NOT_CERTIFIED；研究资格不等于执行资格 |
| SALARY_SLOTS | 六槽金额为现有31位字段；未来赛季映射/延期/选项时点部分未知 | memory_field_profile与P0；M1允许显式假设情景，不把假设写回来源 |
| CASH_SEMANTICS | raw cash保留；signed32仅假设；预算差/工资帽差不是可签资金 | `src/gm_data_access/finance.py`；本轮不追加现金实测或修正 |
| NATIVE_FINANCE | cap/tax模板是配置参考，预算/收入周期不足以认证完整财务资格 | P0、finance_semantics；未知项只限制依赖它的结论 |
| STAFF | 同批员工与8岗位可读；完整雇佣/换岗写回未验收 | docs34能力表；2K次世代MySTAFF不能充当PC认证 |
| HISTORY | 1984–2020顺序新秀循环；历史线参考不覆盖本局事实 | gameplay_policy、docs26；历史重力人物定制独立立项，普通GM不改属性 |

## 供GM使用的机制判断顺序

先依据同批阵容、能力、合同和现有战术辨认问题，再比较内部优化与市场方案；交易或签约到执行端前必须已经定案。对于暂未验收的执行器，可以保留合理的业务研究候选与成本情景，不谎报已经能执行，也不用技术缺口否定整套经营分析。

休赛期愿景是外挂决定合同到期、竞价、去向与合同，减少原生球员流动对经营的干扰。**当前来源只证明规划/合成模拟与待验签约源码存在；没有证据证明原生自动流动已被完全封锁、到期池已认证或整个休赛期链路已生产运行。** 以后实现按具体任务补齐，而非在知识卡中将愿景改写为已部署能力。

## 版本与更新

来源偏移/编码更正仍由采集模块负责；知识库记录适用版本，不修改历史数据。执行能力改变时更新 docs34/36/28及对应手册，知识条目通过引用同步。M1财务模型和M2策略状态是派生能力，不向 `source_catalog`添加虚假游戏事实来源。
