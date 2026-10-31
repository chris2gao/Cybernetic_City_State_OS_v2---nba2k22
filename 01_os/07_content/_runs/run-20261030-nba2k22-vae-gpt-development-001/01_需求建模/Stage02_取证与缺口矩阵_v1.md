# VAE Stage01 · 证据与Stage02取证矩阵 v1

本文件仅用于Stage02任务准备，不是已完成的Stage02 evidence_package。静态来源不等于已生效游戏配置；REA特定实例不等于通用游戏Setter。没有当前存档和游戏运行权限。

## 来源索引与证据等级

| 源ID | 固定依据 | 本轮可支持 | 不能支持 |
|---|---|---|---|
| H01 | 本任务task_packet @079ccec5a28e7a61f000b462037f1c67ae8cef11 | Human四域、迭代、任务边界 | 新存档写入授权 |
| H02 | 规划A0-v1 @57106954627f0d8d540d83e8ea9773faee51cac4 | 产品候选与明确未确认 | Human对A0版本批准 |
| OS01 | Core Stage01方法及schema @934425cf43d4fe3307b0112142aec1ba434a5734 | 八槽位、Human确认门 | Stage01 runner通过 |
| M01 | NBA docs/game_mechanics/guides/K05_K10_K11_WORLD_RULES_SIM_HISTORY_SAVE.md @45cc45cae0550ddcda192a2179ea48509b27f6ee | 3D/Calendar、Normalize、侧别的研究风险 | 当前PE地址/当前Profile |
| M02 | NBA config/state_io_native/settings.json及court.json @45cc45cae0550ddcda192a2179ea48509b27f6ee | 静态候选、单位及旧建议值 | Live Getter、原生存盘验证 |
| N01 | NBA research/rea_native_control/VALIDATION_RESULTS.md @6151ef5d484914edcec2fbcfcf3bcce83a848907 | 有限Coach/Goal/交易实机技术效果 | 所有E1–E4接口安全、UI、SaveReload及竞技改善 |
| N02 | NBA docs/development/ROLE_BATCH_NATIVE_EXECUTION_ARCHITECTURE_V2.md @6151ef5d484914edcec2fbcfcf3bcce83a848907 | 角色—执行层候选职责与授权边界 | 批量执行服务已部署 |
| P01 | NBA docs/development/NBA2K22_DOCUMENT_AUTHORITY_INDEX_V1.md @45cc45cae0550ddcda192a2179ea48509b27f6ee | 权威及历史证据定位 | 代替各项源证据 |
| B01 | NBA docs/development/NBA2K22_TASK1_REQUIREMENT_RESULT_MODEL_V0_1.md @45cc45cae0550ddcda192a2179ea48509b27f6ee | 项目01a/01b式需求表达参考 | VAE Stage03 B完成 |

相对来源根：08_Domain_Applications/Antigravity_GM_Engine/。直接引用以固定仓库SHA为锚，不以日后HEAD取代历史场景。来源标题中的“实机”只说明其限定案例。

## 源一致性与冲突

- settings.json 静态字段 max_contract_rating 存在 min=70 但 default=40 的元数据不一致；不能用其默认值校验当前存档。
- K05相关研究指出两个Normalize开关（Played-to-Sim Minutes与Stats）可能独立，settings.json里一个normalize_stats字段不证明同时覆盖。
- 30队经营身份User-controlled、手柄阵营归属、USER/CPU Gameplay侧别和每个场上AI真实消费路径是不同维度。
- 3D Gameplay调节不必然改变Calendar Simulation；Box、日历、已归一化统计不相同就保留SCORE_CONFLICT。
- 旧court.json中的建议滑块值是研究假设，不是当前实际启用的HoF Profile。
- E4能力/潜力/徽章编辑有WORLD_ADMIN门禁，底层Reader与原生技术存在并不赋予普通GM权利。
- 自然玩一场观察可以表明相关性，不能量化唯一因果效应。

## 最小后续取证队列

| Gap | 优先级 | 验证方法 | 成功标准 | Owner建议 |
|---|---|---|---|---|
| G01 | P0 | 当前存档和game build、模式、scene、PE、Profile只读采样 | 字段与save/时点独立可核，无法识别即停止写入 | Codex Reader + Human |
| G02 | P0 | 目标参数UI与Getter一致性、USER/CPU消费 | 字段原值/单位/侧别证明；缺失UNKNOWN | Codex +有界Gemini |
| G03 | P0 | Played/Sim Quarter、两个Normalize、同game场内Box/日历 | 区分独立开关并标记冲突来源 | Codex + Human |
| G04 | P1 | 首选Coach一项设置，在当前场景验模式、球队身份和读回 | 只对特定字段及场景下结论 | Codex |
| G05 | P1 | 联盟交易/签约/选秀的时点及能力、Human权限 | supported或DEFERRED有证据 | Codex |
| G06 | P1 | Player真实字段、WORLD_ADMIN权限、现实来源时点 | 技术读回与角色可见性独立 | Codex + Human |
| G07 | P0 | 同save Game ID、自然比赛、观察批次与Side/Normalize记录 | 一条可复核3D或Calendar观察轨迹 | Human +可复用Reader |
| G08 | P0 | 可恢复独立存档、回退权限与原值保留 | 独立试验的安全与撤回条件经Human同意 | Human + Codex |

这八项是Stage02输入。即便通过只读取证，也不自动获得REA写权限或进入实际游戏测试。

## 未验证能力的输出词汇

RESEARCH_ONLY、OFFLINE_TEST_ONLY、LIVE_SCOPED、UNKNOWN、MODE_UNVERIFIED、AUTHORIZATION_PENDING、TECH_PATH_BLOCKED、TECH_READBACK_SCOPED、UI_VERIFIED、SAVE_RELOAD_VERIFIED、COMPETITIVE_OBSERVED、INCONCLUSIVE。后一级不得凭前一级推断。
