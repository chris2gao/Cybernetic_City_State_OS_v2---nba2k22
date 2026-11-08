# 模块变更与验证

| 批次 | 工程入口 | 证据边界 |
| --- | --- | --- |
| I0 | 固定输入提交 `839086ae86758ff29b5321edafd6c25d99915672`，`factor_inventory.py` | 逐输入 SHA-256、原始来源交叉映射、GameID 集合和未分配事件集合均检查。 |
| I1 | `native_factor_slots.py`、SeasonCycleHost、Bulk、Outbox | 描述符分别记录物理偏移和 Native 参数索引。离线编译不同槽，核对类型、CAS、邻域和锁。真实 S4 资格继承原有单字段。 |
| I2 | `factor_adapters.py` | Coach 位域和训练日记录按类型生成现有动作参数。世界全局读取精确注册单元。保留管理、成长和缺少真实命令的待开发项。 |
| I3 | `factor_assignment.py`、`factor_lab_cli.py` | 从固定 0005 来源重编逐 GameID 和双方处理历史。独立恢复线的身份和正式事件仍需绑定。 |
| I4 | `factor_runner.py`、TEST_ONLY Calendar | 复用授权、Outbox、收据和原生日历入口。保存执行前声明，遇不确定停止。跨窗口同时检查日期与世界线。多类别真实事件 writer 未启用。 |
| I5 | `world_data_prototype/factor_readback.py`、`factor_analysis.py` | 游戏样本核对同源 Box、比赛状态和比分/FGA。结算对照检查独立世界、身份和来源。真实训练、成长、经营事件采集仍需逐类别绑定。 |
| I6 | `factor_progress.py` | GM、Coach、Player 可查询来源、区间、可靠性和限制。离线样本与实机进度分账。 |

离线回归 146 项测试及 15 项子测试通过，覆盖 Host、Bulk、Outbox、训练、会话和归档日历。多字段 fixture 覆盖三种倾向槽、6 个 setter、2 个短窗、6 场模拟安排以及其中 1 场缺失赛果。验证了拒绝重放、邻域异常停机和 0003 冷备拒绝。Coach 和训练样本独立记录类型化动作、设置读回、事件来源和分类对照。一次 Coach fixture 因选了未注册枚举而被拒绝，样本改用注册的中性、防守内线、防守外线枚举后重跑通过。

留存 WorldData 历史回放固定到源报告 SHA-256 `cb3813edea21c8f1444ae4d6ba084ad08b230b5b3a83beee64235971e4f0f8e6`。49 场进入只读检查，43 场符合本次同源 Box 检查，6 场排除。工程阶段没有新增游戏进程访问、setter、日历调用或存档改动。历史单字段证据不计为本次新字段资格。

Draft 后追加的接线核对覆盖两处。未知槽走同一份公开 PLAYER 邻域读取器，读取前后核对进程、日期、存档绑定并拒绝重复 Native UID。WorldData 从 Host 的绑定状态构造现有 CalendarSimOrchestrator，校验其数据库归属，再走采集与结算读回。接线后重跑 Host 和全因素测试共 78 项通过。追加五字段确切剂量校验后，全因素测试单独重跑 19 项通过。历史同源 SQL 回放单独核验真实数据。

独立写资格入口复用 Host 的封存、Outbox 原生资源锁与回执。资格批次将完整邻域纳入原生计划摘要和实际 setter 前比较。独立读回另检查完整邻域、原对象身份及磁盘指纹。普通 S4 与 Calendar 各自保留既有授权路径，资格封套的日历预算固定为 0。Host、Bulk 和传输回归通过 108 项。补齐锁存储绑定与未知结果拦截后，全因素与回执校验通过 38 项。资格测试使用离线替身，未生成真实资格回执。

固定日历依赖为 PR #42 的 `ada6f30051eb9a2f17193af6985497eeb789ea1c`，用于测试入口。主工作线固定为 PR #41 的 `cdb2a3b2b9f9de79fe068b1644c6ba147d05d8e5`。本候选需要独立工程审核与后续实机资格裁决。
