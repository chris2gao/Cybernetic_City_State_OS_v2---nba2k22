# NBA2K22 REA · Phase A 本地工具可用性只读预检任务派发

- **任务 ID**: `NBA2K22-REA-PHASE-A-READONLY-PREFLIGHT-20261101-001`
- **运行 ID**: `run-20261101-nba2k22-rea-phase-a-readonly-preflight-001`
- **执行角色**: `execution` (模型：Gemini 2.5 Pro)
- **正式 REA 参考基线**: `baseline/nba2k22-native-execution-checkpoint-014-20261029` (SHA: `6151ef5d484914edcec2fbcfcf3bcce83a848907`)
- **工作分支**: `task/nba2k22-rea-phase-a-readonly-preflight-20261101`

## 一、任务目标与核心范围

为 Damian Lillard 的 `SHOT_TENDENCY` 95→80 单字段实验检查 REA 工具是否已经在当前 Windows 本地环境具备执行条件。
本次仅承担只读预检，不授权游戏修改。

重点核对：
1. `PLAYER_SET_TENDENCY` 和 `SHOT_TENDENCY` 是否可在本地正确编译和通过离线测试。
2. Native Index 57 与偏移 0x458 是否对应当前固定构建（SHA256: `1727ad72...`）。
3. 本地版本是否包含原生 Getter→Setter→Getter、目标身份复核、未请求字段保持检查及失败不自动重试机制。
4. 当前 WorldData 的 `team:native:28`、`player:native:2459` 是否有明确映射到 REA 的整型 Team ID 与 Player UID 的规则。
5. 检查本地游戏存档绑定、安全恢复前提、REA 运行依赖及管理员权限要求；不通过连接游戏来验证。
6. 说明现有单字段 Setter 和多字段 PATCH 的真实成熟度，明确尚未完成的实机验证。
7. 给出下一阶段需由 Human 确认的具体事项。

## 二、严格安全禁止项
- 严禁游戏进程附加（Frida attach）。
- 严禁原生 Setter 调用。
- 严禁游戏数据修改。
- 严禁日历模拟。
- 严禁新数据采集。
- 严禁后台监听进程。
- 严禁自动部署或执行任何已生成的 Native 写入脚本。
