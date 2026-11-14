# Issue #40 工程候选交付

completion_pointer: https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22/pull/43

本轮范围为 2026-11-08 Human 评论批准的 I0–I6 工程开发、离线测试和可审核候选交付。实机新增字段、整季模拟和存档修改的决策由 Human 根据交付判断。独立验收为待处理。

| 合同项 | 当前工程证据 | 尚未验证或尚未实现 |
| --- | --- | --- |
| I0 固定真实输入 | 原规划固定提交 `839086ae86758ff29b5321edafd6c25d99915672`。来源校验覆盖 204 条 Stage02、10 个 Coach 投影及 55 个训练候选，保留 223 项去重研究因素。0005 有 1,028 场常规赛和 2 个特殊事件。 | 原始磁盘 0003 与 0005 指纹不同，恢复线必须重新绑定。 |
| I1 原生字段控制 | 99 个物理槽，48 已命名、51 原始槽编号。Host、Bulk、Outbox 接受精确字段和资格清单；单次资格入口校验完整邻域、对象与来源，普通窗口单独检查授权。 | 新增槽实机资格为 NOT_RUN。原有认证仅 SHOT_TENDENCY。 |
| I2 分类适配器 | 223 项均有类型、单位、观察端和具体缺口。153 个动作候选包含 99 倾向、10 Coach、44 训练。Coach 位域、训练原始记录和全局单元都有可运行离线输入输出。 | 9 个 Coach、11 个训练、28 全局、19 经营、3 成长共 70 项没有本候选可执行的字段写入动作。已映射的候选还需逐类实机资格。 |
| I3 分配与容量 | 19 个首线七日窗口、981 场、380 个 H/L 席位、246 个唯一 UID、134 个重复席位。逐场保留双队、因素、UID、剂量、旧处理与对手暴露。原参考系列 120 项有 GameID，103 项有事件预留。 | 首个原参考窗未知槽缺实际剂量。另给同 53 场、五个具名字段的确切剂量示例，保留原参考。未来窗口要用 fresh 池和真实处理历史重编。 |
| I4 有界执行 | WindowRunner、NativeWindowPort、NativeCalendarPort 与 run_series 复用既有 Host、Outbox、TEST_ONLY Calendar。批准封套派生确切子批，claim 先落盘，UNKNOWN 停止并禁止重放。fixture 覆盖多字段、两次模拟及缺赛果。 | 真实类别资格与结算消费仍需补证。当前候选不会自行获得新实机权限。 |
| I5 分类采集与分析 | 同源球队/球员 Box、原生技能与健康结算、合同及交易前后状态、Coach 逐场消费证据。实现 H−C/L−C、原始剂量描述斜率、独立世界线差分、2×2 交互、bootstrap 区间与预登记检验族 FDR。 | 同世界线队伍及对手存在依赖，初筛保留 UNDERPOWERED。真实全局消费者、训练和成长结算、交易参数语义缺少独立回执。 |
| I6 持久化与查询 | 223 项指纹绑定的 SQLite 只追加进度，原子写入及重放。具备 coverage、queue、history、query、资格及窗口回执导入，失败保留在队列，LIVE/FIXTURE 分账。 | 当前没有新增真实机制结论。GM/Coach/Player 查询不会从 fixture 取得可决策效果。 |

五项指定交付均在本组内。

- [逐项覆盖与缺口](IMPLEMENTATION_COVERAGE.md) 和 [机器化 223 项覆盖](implementation_coverage.json)
- [模块、函数及测试](MODULE_DIFF_AND_TESTS.md)
- [逐 GameID 计划](GAME_ID_EXPERIMENT_PLAN.json)
- [字段协议输入输出](FIELD_PROTOCOL_SAMPLES.json)
- [小批实机资格候选](HUMAN_LIVE_TEST_APPROVAL.md)

字段协议演示样本均标为离线 fixture，真实 GameID 和基线来源分别保留。原生调用次数、游戏进程访问次数和存档修改次数在本轮均为 0。历史 SQL 回放单独固定源报告 SHA，其 49 场中 43 场符合当前同源 Box 核验，6 场排除。

精确测试结果随同 [测试记录](MODULE_DIFF_AND_TESTS.md) 保存。上述未完成项是合同要求保留的逐字段研发缺口，不代表效果已否定。是否接纳工程候选和授权下一次多字段实机验证，等待 Human 与 GPT 的结果判断。
