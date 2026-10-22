# DEV-20261017-TACTICS | 模拟比赛教练战术评估

- 日期：2026-10-17
- 状态：ASSESSMENT_DOCUMENTED / NO_CODEX_TASK_STARTED / NO_GAME_WRITE_AUTHORIZED
- 评估报告：[DEV_20261017_COACH_TACTICS_SIMULATION_ASSESSMENT_V1.md](../../../../docs/development_reviews/DEV_20261017_COACH_TACTICS_SIMULATION_ASSESSMENT_V1.md)
- 报告创建提交：b599e174e5d0b1ff6e445ab4ae4c07ad9904e125
- 玩家问题：NBA2K22 PC教练页面可修改各队攻防和战术手册，AI实机对战动态变阵，普通快速模拟是否动态调整未知；Codex新找到部分写地址，咨询是否值得增强GM可用战术控制。
- 评估：建议**条件开发**。优先验证快速模拟的Sim POE和赛季战术体系是否对模拟分布/胜负有效；其次验证实际比赛防守、playbook、对手专属配置；不预设普通快速模拟运行完整ACE或次世代条件教练。
- 当前代码：`src/strategy_manager.py`存在0xEB2..0xEBC球队策略getter/setter，但仅uint8范围验证；`src/gm_core/tactics.py`分析端，`config/gm_policy.json`中`poe_on_ball`枚举冲突；字段读取或字节写入不是可用业务执行器。
- 外部证据：2K官方的模拟Conditional Coaching仅明确次世代主机；社区报告Sim POE影响模拟统计、NBA2K22战术/Playbook可能起作用，但具体 PC 版游戏模拟胜率效果未知。
- 后续：等待玩家决定是否安排Codex P0实验；不能在无具体批准时修改正式队伍策略；本次只写评估和记忆文件。
