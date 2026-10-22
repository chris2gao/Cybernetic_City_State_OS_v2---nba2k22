# DEV-20261017-04 P1：游戏外集中竞价源码交付（尚未测试）

2026-10-17。状态：**SOURCE_IMPLEMENTED / NOT_RUN / NOT_TESTED / SIMULATION_ONLY**。
P0源码与归档研究提交：`8ff4b7f`。P0实机认证未完成，见 [P0记录](DEV_20261017_04_OFFSEASON_FA_P0_RESEARCH.md)。

玩家确认没有休赛期测试副本，先交付可完成的P0与离线部分；随后明确现在不用测试，休赛期另行提示。本阶段未运行规划器、示例生成器、校验器、编译检查或单元测试。下面的入口和输出是**源码定义**，不是已运行成功的记录。不得将本交付标成P1验收通过、可处理真实休赛期，或P2/P3完成。

## 已写入的离线机制

`src/gm_core/offseason.py` 只处理冻结的输入与整数计算，不导入游戏内存、数据库、网络、模型派发或批准/执行模块。以同一输入重放会使用公开排序和整数评分。此确定性设计尚未通过运行验证。

1. 要求显式覆盖30个不同球队ID，不假设0–29连续。候选按 `candidate_id` 和稳定 `entity_id` 去重；相同姓名可对应不同实例，姓名或槽位不单独充当身份。缺连续身份/来源证据则排除。
2. 到期候选需指定已完成赛季、到期证据、无目标季承诺、选项已解决且无未决延长合同；既有FA需独立来源。普通合同、选项未决、无有效QO的RFA不进入可报价池。**当前仅能对合成输入模拟这些判定**，不会直接把月度年限当到期事实。
3. 逐候选×逐队生成报价。优先输入索价；无索价时可由上一年工资×公开整数倍率产生 `HEURISTIC_PROPOSED`，缺价格锚则不出价。中性基础策略不假称已有GM确认；显式策略可指定逐年金额参数、角色/战略分数或拒绝报价。
4. 逐项检查首年最低/最高、年限、以首年工资为基数的涨幅，以及 CAP_SPACE/Bird/Early/Non-Bird/Exception/Minimum资格。**所有这些资格当前仅接受明确的合成夹具状态**，并非认证真实游戏已支持这些路径。每项资格和个人限额均要有单独证据引用，不能只输入一个Bird年数或服务年限未知的默认顶薪。
5. 工资帽内路径既需独立签约资格/空间，也检查目标季承诺工资上界。奢侈税线不是无限签约许可。Bird等只能用于母队且要有对应资格；共享特例容量独立扣占。真实有效硬上限只有在单独提供时检查，不把apron自动当所有球队的硬上限。
6. 母队对外队最佳可行报价只有一次最终同价机会；UFA仍按公开评分自由选择，母队不会因同价自动锁人。RFA只有有效QO、匹配权及合法母队报价同时存在才模拟匹配。
7. 联盟处理顺序：按初始最高可行合同总额降序、再按候选ID。每次落定后同步占用首年签约容量、财务支用额度、名单席位和共享特例；后续候选重新检验全部报价，失效报价记录原因并回落到其他可行报价。没有可行报价则 `UNSIGNED`。
8. 球员评分为合同总额、角色分、战略分及母队偏好的公开整数加权和；同分再按合同总额、球队ID、报价类型和路径固定决胜。不使用随机数、浮点或缺省OVR/年龄。四项权重可配置，输入/权重/处理顺序保存在运行记录。
9. 输出目标季承诺工资、建议后工资、距cap/tax/apron的前后差额及占用。税率/现金结算未认证，`tax_amount`、`cash_impact`保持null；不从cash扣税。未知财务支用额度/席位/承诺工资会阻止签约建议，未知cash本身不被当作正现金许可。

## 数据契约与真实来源门槛

根对象包含 `schema_version=1`、save/season/run/version、batch/time、policy/rules/game-state版本、game_phase、native_ai_control_status、完整teams/candidates、按目标赛季索引的season_rules。

当前只接受：`purpose=SIMULATION`、`synthetic=true`、`source_profile=SYNTHETIC_OFFSEASON_V1`、`game_phase=SYNTHETIC_OFFSEASON_FROZEN`、`native_ai_control_status=SYNTHETIC_CONTAINED`。真实输入返回 `REAL_OFFSEASON_SOURCE_NOT_IMPLEMENTED`，不能靠 `approved=true` 或 `verified=true` 绕过。将来必须在P0实测后实现真实来源适配，不允许用JSON声明代替工程认证。

合成候选核心字段：

- `verified_player_identity={entity_id,scheme:SYNTHETIC,continuity_ref}`、candidate_id、display_name、previous_team_id、roster_provenance。
- `origin=EXPIRING|EXISTING_FA`、contract_years_left、next_season_salary_slots、option_status、extension_status、expiry_verified_for/expiry_evidence_ref，或free_agent_evidence_ref。
- free_agency_status、bird_rights_status、qualifying_offer的valid/matching_right及各自引用；asking_salary可空，previous_salary可作明确的启发式锚，home_preference为配置分数。

球队核心字段为当前工资、目标季承诺工资、**独立认证的**可用空间、签约支用额度、可用席位、逐候选/逐路径资格、共享特例预算、策略来源与逐候选报价参数。cash/budget可空，不将静态cap-payroll当成已认证空间。已有未决报价/占用的输入拒绝，须先归并为新的协调快照，不默默忽略其他运行的承诺。

每个目标年度需独立season_rules和引用，逐候选/路径给出最低/最高首年、最长年限与最大涨幅。不回落到2021–2022模板。所有金额为整数美元，逐年金额限制在31位正整数范围；布尔、浮点、负值、溢出及重复JSON键拒绝。合成示例中的目标季规则**不是现实NBA或本局规则**。

## 入口、产物与幂等

- `scripts/offseason_example.py --output _exports/offseason/example`：仅生成带SYNTHETIC标签的30队输入和独立模拟上下文，不自动运行规划。
- `scripts/offseason_plan.py --input PATH --output _exports/offseason/runs`：生成离线方案，不连接游戏或启动正式GM。
- `scripts/offseason_validate.py --plan-dir PATH --current-context PATH`：从冻结输入重放全部产物并对比独立上下文声明；未提供上下文、版本/批次/赛季/状态不一致、产物被改则BLOCKED。通过最多为 `SIMULATION_CONSISTENT`，**不认证live新鲜度或玩家批准**。

本次没有执行以上命令。未来由玩家通知测试后，Codex按范围运行，不要求玩家手动执行。

目录为 `_exports/<指定父目录>/<save_id>/<completed_season>/<run_id>/v<version>/`。包含 frozen_input.json、offseason_run.json、expiring_candidates.json、free_agency_offers.json、offseason_proposal.json、OFFSEASON_SUMMARY.md 和最后写入的COMPLETE标记。同版本且输入/产物相同返回NO_WRITE_NEEDED；不同输入不得覆写；中断目录保留证据并拒绝当作完整运行。不写published、正式球队档案或赛季经营档案。

幂等键按任务书为save+completed_season+run+proposal_version。同一个键只对应一个不可变目录；源批次与目标季变化也必须新建版本/运行。提案携带decision_id/version、source/policy/state、策略和计算引用。所有状态保留NOT_APPROVED，`executable_operation_ready=false`。没有内存writer、实际成交或现金扣款，幂等不冒充游戏事务。

## 未完成及后续验证清单

| 项目 | 当前状态 |
| --- | --- |
| P0实机安全停点/AI签约干扰/合同与财务语义 | 未验证，等玩家休赛期通知 |
| P1合成来源规划源码与本地CLI | 已写入，**未运行、未测试** |
| 合成示例、JSON/Markdown实际产物 | 生成器已写入，**未生成实际方案** |
| 真实最小休赛期采集/稳定跨季身份 | 未实现；不能用于正式到期扫描 |
| 真实年份最低/最高/年限/涨幅、母队权利 | 未认证；模拟资格不计为实机证据 |
| P2合同与转队关联写回 | 未实现，无执行CLI；等测试副本逐笔验收 |
| P3保存重开、下季30队、原生覆盖检测 | 未执行，不授权本次推进赛季 |

恢复测试后先覆盖任务书第9节全部离线情形：完整30队/去重/选项/续约、无QO/RFA与UFA外选、超帽无资格/合成Bird超税、竞争同一空间与特例/席位、最大最小与涨幅/错误年度、未知字段/溢出/同名克隆、重复run/跨save跨季/版本变化与产物篡改。随后只能在玩家确认测试副本和具体范围后做P0/P2/P3；单元测试成功也不升级为真实游戏签约成功。

## 源码审阅修正（未运行验证）

规划器版本 `offseason_planner_v1_1_unverified` 在源码审阅后修正两处逻辑：

- 年涨幅先按首年工资计算整数美元增量、向下取整一次，再生成逐年表，避免累计目标分别取整导致相邻年份的增量反而超过精确涨幅限制。报价保留 `annual_raise_dollars`，便于之后回放核对。
- RFA匹配仅在球员按公开评分选中外队合同时替代去向；若球员已经选择母队原有的更优报价，不用较低的同价反报价覆盖它。实际触发模拟匹配时记录 `matched_external_team_id`。

这两项来自静态源码推理，没有运行金额计算、示例或测试。恢复测试时须补充“非整美元涨幅跨多个合同年”和“母队原报价优于同价反报价”的回归覆盖；本段不构成PASS记录。
