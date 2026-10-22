# DEV06 执行器验收记录与剩余边界

2026-10-17。**默认六项POE达到EXECUTOR_IMPLEMENTED_READY_FOR_PLAYER_APPROVAL；正式局未执行。** 仅六项production_enabled=true；其他按字段保留只读或隔离编码。玩家最后要求停止重复保存测试，改为整理可修改范围及指定对手评估。

| 要求 | 实际证据 | 结论 |
| --- | --- | --- |
| 旧TEAM writer及调用者 | setter内存访问前拒绝；bootstrap调用清除；AST检查 | PASS |
| 六项5bit及合法枚举 | 合法/非法值遍历、bit30/31、相邻位和完整块保护 | PASS |
| 同块六项一次写 | PHI／AI IND各一次4byte写及恢复 | PASS 实机 |
| 原生模块、字段、球队教练岗位名单 | 每次重新校准，30队主教练双向关联、PE、enum CRC、手册 | PASS；真实换帅未实操 |
| 独立批准及退出编辑页前提 | 缺任一零句柄；就绪字段仍须具体批准 | PASS mock；关闭编辑页后实机使用 |
| PID、身份、前值失效 | 拒绝不匹配；实际旧PID方案仅RO、无RW | PASS mock及真实重启 |
| 初始两队事务 | IND／GS进攻重点5→2→5，幂等、完整30教练恢复 | PASS 实机 |
| 中文菜单采用 | PHI重点及关闭编辑页后的耐心进攻；AI IND六项玩家全部确认 | PASS 玩家确认；无截图依赖 |
| 保存完全退出重启 | PHI重点2持久；IND六项2/7/10/13/16/19持久；PID和创建时间均变 | PASS 实机 |
| 新进程恢复 | 旧计划拒绝，新快照独立动作恢复IND六项；30队24已知字段全部原值 | PASS 实机内存 |
| 恢复后再次保存重载 | 玩家明确停止重复测试 | NOT_RECHECKED_BY_PLAYER_DIRECTION |
| 恢复非目标保护 | 同进程其他29完整教练记录、目标非授权字节及手册内容不变 | PASS 实机 |
| 并发及失败恢复 | 不覆盖第三方变化；先落preimage；条件恢复／PARTIAL_UNRECOVERED | PASS mock |
| 幂等历史回执 | NOT_REVALIDATED_CACHED_RECEIPT，不误报当前状态 | PASS mock |
| 五Sim／体系／手册 | 精确编码；SimPace2→4→2内存验证，其余未独立实机验收 | FORMAL_DISABLED / SAFE_WRITE_PENDING |
| 滑块／Freelance | 范围、单位或槽关系未认证 | READ_ONLY |
| 指定对手Gameplan | 870条原始IsInUse=0；可离线预设；从不改IsInUse | MATCHUP_EXECUTION_BLOCKED_NOT_ACTIVATED |
| 18防守／轮换 | 原生掩码、enum CRC及capture-local引用 | READ_ONLY |
| 多球队原子批次／生产来源 | 单队单action、本地JSON，未接入生产SQLite/发布 | NOT_IMPLEMENTED |
| 比赛效果 | 无比赛模拟或推进 | SIM_EFFECT_PENDING_PLAYER_MONTH |

最终命令：python -B -m unittest discover -s tests -p test_coaching_safety.py -q，37项通过。此前GM协议8项、覆盖5项、三个CLI帮助和真实快照派生的离线预演通过；最终只重跑受profile及批准门槛影响的安全套件。没有运行verify_web_export、同步hash、下载比较或比赛模拟。

公开[技术证据](DEV_20261017_06_COACHING_TECHNICAL_EVIDENCE.json)保留阶段差异；早期未验证持久性仅属当时阶段，以后续PHI及IND实际重启证据为最终结论。默认值在指定对手页面出现不等于独立对手覆盖认证。具体范围及未来风险验证见[能力与对手评估](DEV_20261017_06_COACHING_CAPABILITIES_AND_MATCHUP.md)。
