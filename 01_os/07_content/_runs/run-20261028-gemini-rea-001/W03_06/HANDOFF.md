# W03-06 Delivery Handoff: Training, Mentorship & Player Recovery

## 1. 范围与 14 项需求覆盖
本包全面研究并闭环了 `TRAINING_AND_DEVELOPMENT` 组的 14 项需求：
- 日程训练安排与模式 (`TRAIN.TEAM_SCHEDULE`)
- 团队训练强度与主客场设置 (`TRAIN.TEAM_INTENSITY`, `TRAIN.HOME_AWAY_INTENSITY`)
- 训练重点方向与大纲 (`TRAIN.TEAM_FOCUS`, `TRAIN.TEAM_PROFILE`)
- 训练自动化与背靠背轮休 (`TRAIN.AUTOMATION`, `TRAIN.B2B_REST`)
- 个人训练重点、强度覆盖与康复 (`TRAIN.PLAYER_FOCUS`, `TRAIN.PLAYER_INTENSITY`, `TRAIN.PLAYER_RECOVERY`)
- 全队减负日 (`TRAIN.TEAM_RECOVERY`)
- 师徒关系绑定与解除 (`TRAIN.MENTOR_ASSIGN`, `TRAIN.MENTOR_REMOVE`)
- 健康、疲劳与伤病状态 (`TRAIN.HEALTH_INFO`)

## 2. 核心原生机制发现
1. **全队日程训练流水线 (`0x13256a0` / `0x1325710`)**:
   - 原版函数 `0x13256a0`（对应 `training.set_team_on_date`）处理指定日期的训练大纲。
   - 训练配置结构体大小为 30 字节（偏移 `+0xf` 至 `+0x2c`），按日记录强度（0..5）、重点类别（0..5）、背靠背轮休规则与康复日标记。
   - 业务关键：训练设置是设定接下来的模拟日程发展规则，并非单次内存直接修改球员属性与徽章数值。

2. **师徒/导师系统底层结构 (`0x124f0f0` / `0x125ed70`)**:
   - 球队 Franchise 上下文（偏移 `+0xc`）管理该队的师徒槽位。
   - 槽位严格限定为最多 10 组（指令 `0x124f112: cmp r9b, 0xa`）。
   - 每组师徒条目占用 204 字节（`0xcc`），未使用的槽位以 `0xffff` 填充。
   - 解除师徒关系通过 `0x125ed70`（`mentor.remove`），通过魔数乘法快速除以 204 计算出 0..9 的槽位索引，并重置为空槽 `0xffff`。

3. **疲劳与康复机制**:
   - 疲劳值与伤病状态在球员结构体中维护，并在训练模拟和比赛中更新。

## 3. 隔离候选与验证交付
- 交付编解码器：`training_mentorship_codec.py`
- 交付独立测试：`pytest_gemini/test_training_mentorship.py` (2 项测试全部通过)
- 成熟度状态：`PROVEN_IN_PE_AND_OFFLINE_VERIFIED`
