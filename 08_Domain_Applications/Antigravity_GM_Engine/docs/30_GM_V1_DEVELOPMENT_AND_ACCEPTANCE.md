# GM v1.0 开发与验收

本文的测试和末尾缺口包含 v1 初次交付的历史记录，不是当前数据源覆盖声明。后续字段扩充见文档 31，当前能力见 [34_BASELINE_CURRENT_STATE.md](34_BASELINE_CURRENT_STATE.md)。常驻开发基线使用 [33_DEVELOPMENT_BASELINE_PROMPT.md](33_DEVELOPMENT_BASELINE_PROMPT.md)；读取基线不触发开发或测试。

## 本阶段范围

实现任务书 M1–M6。所有核心代码位于 `src/gm_core/`，只读 published JSON，与游戏、内存、原始 SQLite 及上传脚本无依赖。默认只准备 SIMULATION/ANALYSIS_ONLY 分析包，实际篮球经营判断由玩家触发的网页 GM 完成。没有自动模板交易、游戏写入或模型调用。

经营配置 `config/gm_policy.json` 标为 PROPOSED_PENDING_PLAYER_CONFIRMATION，不是已经批准的球队规则。正式 `docs/team_dossiers/` 未修改；每队新分析存入独立运行目录，既有正式档案不会被覆盖。

## 实现映射

| 任务 | 文件及交付 |
| --- | --- |
| M1 | data_reader/coverage：已发布入口、时间、数据/规则版本、来源可用性；未知字段不补值 |
| M2 | franchise/personas/history：每队独立身份、文化引用、目标、保护、生命周期、变化；已确认历史未提供时保持未知 |
| M3 | reports + roster/tactics/finance/trades/worldline：12 个统一模块接口，局部缺失不阻断全联盟 |
| M4 | calculations：工资差、薪资合计、位置/合同分布、快照/阵容变化、胜率、效率、薪资交换和选秀轮回 |
| M5 | models/decisions/history：运行协议、PROPOSED 方案结构及来源检查、待审批版本存储；没有批准或执行接口 |
| M6 | web_gm/GM_DECISION_SOP.md：网页 GM 逐队审查、计算、市场讨论、提案与交付顺序 |

v2/v3 只预留 Asset、NegotiationStage、ModelHandoff、HistoryRecord 等数据协议和模块扩展边界。本次不实现自动谈判、CBA 完整认证、确认历史写入、模型调度或游戏写回。

## 显式命令

以下准备命令不会启动正式 GM 回合。开发示例输出隔离到 _exports：

```powershell
python scripts/gm_prepare.py --save-id mc_haliburton_2021 --run-id V1_DEVELOPMENT_SIMULATION --mode simulation --state-root _exports/gm_v1_development
python scripts/gm_calculate.py --request PATH_TO_CALCULATION_REQUEST.json
python scripts/gm_validate_proposal.py --save-id CAREER_ID --proposal PATH_TO_PROPOSAL.json --run PATH_TO_RUN.json
```

需要保存待审批版本时，给 gm_validate_proposal 加 `--save-pending`；仅存入外部状态目录。该参数不批准、不执行、不发布。准备命令使用 `--previous-run` 选择前次分析，拒绝其他存档或未来游戏日期/采集时间；不自动搜寻并沿用历史。

默认目录为 `gm_state/careers/<save_id>/runs/<run_id>/`，内含 run.json、REPORT.md、teams/<abbr>.json。待批准方案在 careers/<save_id>/proposals/。正式 teams/history 为未来玩家确认记录预留，本版不写入。输出不可指向 published、database、config 或源码目录。

## 计算与协议限制

当前真实数据可计算已观测工资、位置和合同期限等；胜负、效率或真实球员价值所需字段不足时输出 UNKNOWN。空输入不默认等于零，零值只有实际存在时才参与计算。

生命周期完整枚举包括六种经营状态及 UNDETERMINED；当前简单候选只在真实战绩足够时提出，阈值属于待确认配置。CHAMPIONSHIP/RISING 的经营判断需要更多证据和网页 GM 判断；没有以工资/历史标签替代。

提案检查针对 GM 协议和约束，不属于日常同步 JSON 复核。READY 仅表示接口必需信息可用，不代表交易合法、玩家批准或可写游戏。所有模块默认 executable_operation_ready=false；需要具体执行时仍交独立执行窗口。

## 旧逻辑处理

- `trade_engine.py` 的生产构造入口停用，调用前即报错，不打开数据库；估值不再用 OVR 75、25 岁、500 万等缺省值。
- `gm_engine.py` 的旧工资驱动战术建议已移除，避免把对球压迫推到 12。其既有只读审计闸门保留，采集/导出/上传入口均未修改。
- 具体游戏执行器、正式球队规则和游戏写权限均未扩大。

## 测试

```powershell
python -m unittest discover -s tests -v
```

合成数据明确标记 synthetic，覆盖完整/部分/未知/冲突输入。兼容性测试只读取当前已发布正式 JSON，不连接游戏、不读取本地原始数据库、不产生正式决策。

覆盖：计算确定性、NULL/非有限/布尔输入、30 队×12 模块、缺失战绩、未观测来源、候选生命周期、独立档案、存档回退、路径隔离、未知能力、未知选秀权、玩家保护、重复资产、战术枚举、世界线分离、1984–2020 回绕、伪造批准、伪装属性编辑、未知计算和三个 CLI。

验收实际运行结果及提交版本记录在阶段交付说明；开发模拟产物存于 `_exports/gm_v1_development/`，不混入生产数据发布。

本阶段实际执行 `python -m unittest discover -s tests`：40 项测试通过。基于正式发布的 2021-11-20 检查点生成完整开发模拟，输出位于 `_exports/gm_v1_development/careers/mc_haliburton_2021/runs/V1_DEVELOPMENT_SIMULATION_FINAL/`，含 REPORT.md、run.json 和 30 份球队分析。所有正式操作清单为空；缺失战绩使各队生命周期保持 UNDETERMINED。该模拟没有进入正式 GM 回合。

## 后续能力与数据缺口

初次交付时存在上述来源限制，后续已补齐战绩/赛季累计统计、55 项能力与潜力、员工岗位归属和简单选秀权权属；合同范围已由玩家缩为大名单薪资。游戏显示年龄/OVR、逐场日志、伤病/完整轮换等仍为缺口。单来源独立生产更新尚未实现。以文档 31/34 和当前代码为准，不照抄初次交付缺口或历史测试结果作为当前结论。

v2 待玩家指令：完整资产身份/权属、双方独立谈判、游戏规则与 CBA 分离、冲突资产仲裁及多模型协议落地。v3 待玩家指令：已确认跨赛季经营史、分支与回档、时代进度和赛季关联评估。已有基础选秀年份计算和参考锚点不代表这些高级功能全部实现。
