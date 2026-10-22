# M4 开发问题交接索引

ENGINEERING_FEEDBACK_ONLY / GM_V4_NOT_ENABLED

这是本次显式导出的有界问题页，不是实时监控或全部历史。详细原始事件保留在本地派生工作台；本目录仅含小型引用和摘要。

下次由玩家主动触发 Web DEVELOPMENT 时先读本页，再按证据提出最小研究/实现范围、成本与任务书草案，等待玩家批准。导入、分流、建议负责人、导出均不授权开发或游戏写入。

工程状态：M4_ENGINEERING_COMPLETE_AWAITING_PLAYER；正式GM：GM_V4_NOT_ENABLED。
待完成门：web_DEVELOPMENT, web_ANALYTICS, web_GM, sanitized_production_capture, gm_consumed_sanitized_batch, actual_30_team_research, GSW_SAS_OKC_no_write_rehearsal, issue6_fix, BPTI_before_new_save, postseason_capture_interface, dual_engine_calibrator_interface, player_V4_switch_and_new_save, M4_engineering_integration。
准备状态依据日期：2026-10-20T13:42:21.080095+00:00；完整分项见 [readiness.json](readiness.json)。

问题页：4 项；全池按状态/严重程度计数：[{"count":1,"severity":"P1","status":"DEFERRED"},{"count":3,"severity":"P2","status":"DEFERRED"}]。
还有下一页：False。游标与筛选见 [index.json](index.json)，用CLI继续查询/导出。

## DEV-5600dd26e1086b0b0f45 · P1 / DEFERRED

DEV14完整Registry字段目录被误识别为PLAYER Potential镜像

- 类别 / 证据等级：OTHER_VERIFIED_ENGINEERING_ISSUE / STATIC_REPORT（ENGINEERING_EVIDENCE）。
- 来源：{"code_version":"7e8ba1a71ee350ea722ea262f1da70bce51bfc49","error_code":"UNKNOWN_PLAYER_POTENTIAL_JSON_MIRROR","producer":"M3_T_REPORTED_EVIDENCE","source_stage":"MANUAL_RESEARCH"}；作用域：{"kind":"SYSTEM"}。
- 首次 / 最近：2026-10-20T10:20:13+00:00 / 2026-10-20T10:20:13+00:00；独立事件数：1；修订：1。
- 能力 / 影响：DEV14_FULL_REGISTRY_POTENTIAL_SANITIZATION；已有合成报告记录UNKNOWN_PLAYER_POTENTIAL_JSON_MIRROR；下一次完整目录生产路径有阻断风险，未证明全部生产采集必然失败
- 预期：后续独立修复区分字段目录与真正PLAYER Potential值/镜像，保留原脱敏保护
- 最小复现或阅读条件：阅读M3-T报告与Issue #6的已有合成复现记录；本M4不重新运行净化器；原条件：state_io_captures.metadata_json含完整Registry及world.contracts_and_finances.player_potential_factor目录键
- 已知限制：首次时间为GitHub Issue登记时间，不是已知游戏故障起点；occurrences是独立导入证据事件数，不是生产故障次数；本次只导入已存在报告，未重现、修复或运行DEV14测试；没有生产采集证据
- 建议负责人：DEV14窗口①或另行批准的独立开发模型；下次触发：玩家单独批准Issue #6最小修复范围及验证后，且在需要完整目录生产采集之前
- 玩家决定：玩家2026-10-20：不扩展本轮，记录给DEV14窗口①后续修复；Issue #6为BACKLOG_ONLY
- 原始证据：[https://github.com/chris2gao/nba2k22-gm-engine/issues/6](https://github.com/chris2gao/nba2k22-gm-engine/issues/6)；[docs/development_reviews/M3_T_IMPLEMENTATION_AND_ACCEPTANCE.md](../../docs/development_reviews/M3_T_IMPLEMENTATION_AND_ACCEPTANCE.md)
- [详情及最近历史](DEV-5600dd26e1086b0b0f45.json)。完整历史通过 `show --issue DEV-5600dd26e1086b0b0f45` 分页读取。

## DEV-6762086a63b1e16ed03c · P2 / DEFERRED

DEV19 BPTI：正式新档前的篮球哲学与战术认知工程

- 类别 / 证据等级：DEVELOPMENT_FEATURE_CANDIDATE / RESEARCH（RESEARCH）。
- 来源：{"producer":"PLAYER_DEV19_DEV20_ROADMAP","source_stage":"MANUAL_RESEARCH"}；作用域：{"kind":"SYSTEM"}。
- 首次 / 最近：2026-10-20T13:42:21.080095+00:00 / 2026-10-20T13:42:21.080095+00:00；独立事件数：1；修订：1。
- 能力 / 影响：BPTI_BEFORE_NEW_SAVE；规划已登记，工程尚未实施；本事件时间仅为规划引用整理时间
- 预期：按DEV19分阶段独立授权；M4不实施篮球认知或球队绩效分析
- 最小复现或阅读条件：阅读已批准记录的规划指针；不是故障复现
- 已知限制：未来规划需求，不是发现的Bug，不自动启动任务或游戏操作
- 建议负责人：玩家后续指定的研究/Antigravity/Codex窗口；下次触发：玩家在M系列工程完成后单独触发规划或批准实现
- 玩家决定：玩家M4任务：此项明确后置，仅允许登记规划任务指针
- 原始证据：[docs/development_tasks/DEV_20261020_19_BPTI_BASKETBALL_PHILOSOPHY_AND_TACTICAL_INTELLIGENCE_MASTER_PLAN_V1.md](../../docs/development_tasks/DEV_20261020_19_BPTI_BASKETBALL_PHILOSOPHY_AND_TACTICAL_INTELLIGENCE_MASTER_PLAN_V1.md)；[docs/development_tasks/DEV_20261020_20_M4_SYSTEM_EVOLUTION_ENGINE_IMPLEMENTATION_V1.md](../../docs/development_tasks/DEV_20261020_20_M4_SYSTEM_EVOLUTION_ENGINE_IMPLEMENTATION_V1.md)
- [详情及最近历史](DEV-6762086a63b1e16ed03c.json)。完整历史通过 `show --issue DEV-6762086a63b1e16ed03c` 分页读取。

规划指针：按DEV19分阶段独立授权；M4不实施篮球认知或球队绩效分析

## DEV-a5bb834b34b7b9973f2d · P2 / DEFERRED

季后赛逐场、球员与高阶统计采集接口

- 类别 / 证据等级：DEVELOPMENT_FEATURE_CANDIDATE / RESEARCH（RESEARCH）。
- 来源：{"producer":"PLAYER_DEV19_DEV20_ROADMAP","source_stage":"MANUAL_RESEARCH"}；作用域：{"kind":"SYSTEM"}。
- 首次 / 最近：2026-10-20T13:42:21.080095+00:00 / 2026-10-20T13:42:21.080095+00:00；独立事件数：1；修订：1。
- 能力 / 影响：POSTSEASON_CAPTURE_INTERFACE；规划已登记，工程尚未实施；本事件时间仅为规划引用整理时间
- 预期：未来独立采集工程；本轮不采集、不扩充游戏来源
- 最小复现或阅读条件：阅读已批准记录的规划指针；不是故障复现
- 已知限制：未来规划需求，不是发现的Bug，不自动启动任务或游戏操作
- 建议负责人：玩家后续指定的研究/Antigravity/Codex窗口；下次触发：玩家在M系列工程完成后单独触发规划或批准实现
- 玩家决定：玩家M4任务：此项明确后置，仅允许登记规划任务指针
- 原始证据：[docs/development_tasks/DEV_20261020_19_BPTI_BASKETBALL_PHILOSOPHY_AND_TACTICAL_INTELLIGENCE_MASTER_PLAN_V1.md](../../docs/development_tasks/DEV_20261020_19_BPTI_BASKETBALL_PHILOSOPHY_AND_TACTICAL_INTELLIGENCE_MASTER_PLAN_V1.md)；[docs/development_tasks/DEV_20261020_20_M4_SYSTEM_EVOLUTION_ENGINE_IMPLEMENTATION_V1.md](../../docs/development_tasks/DEV_20261020_20_M4_SYSTEM_EVOLUTION_ENGINE_IMPLEMENTATION_V1.md)
- [详情及最近历史](DEV-a5bb834b34b7b9973f2d.json)。完整历史通过 `show --issue DEV-a5bb834b34b7b9973f2d` 分页读取。

规划指针：未来独立采集工程；本轮不采集、不扩充游戏来源

## DEV-fbfcbf7760e7bd831da0 · P2 / DEFERRED

3D与Calendar Fast-Sim独立年度校准器

- 类别 / 证据等级：DEVELOPMENT_FEATURE_CANDIDATE / RESEARCH（RESEARCH）。
- 来源：{"producer":"PLAYER_DEV19_DEV20_ROADMAP","source_stage":"MANUAL_RESEARCH"}；作用域：{"kind":"SYSTEM"}。
- 首次 / 最近：2026-10-20T13:42:21.080095+00:00 / 2026-10-20T13:42:21.080095+00:00；独立事件数：1；修订：1。
- 能力 / 影响：DUAL_ENGINE_CALIBRATOR_INTERFACE；规划已登记，工程尚未实施；本事件时间仅为规划引用整理时间
- 预期：未来独立校准工程；首个真实季后赛才积累校准数据，本轮不实现公式或32滑块调节
- 最小复现或阅读条件：阅读已批准记录的规划指针；不是故障复现
- 已知限制：未来规划需求，不是发现的Bug，不自动启动任务或游戏操作
- 建议负责人：玩家后续指定的研究/Antigravity/Codex窗口；下次触发：玩家在M系列工程完成后单独触发规划或批准实现
- 玩家决定：玩家M4任务：此项明确后置，仅允许登记规划任务指针
- 原始证据：[docs/development_tasks/DEV_20261020_19_BPTI_BASKETBALL_PHILOSOPHY_AND_TACTICAL_INTELLIGENCE_MASTER_PLAN_V1.md](../../docs/development_tasks/DEV_20261020_19_BPTI_BASKETBALL_PHILOSOPHY_AND_TACTICAL_INTELLIGENCE_MASTER_PLAN_V1.md)；[docs/development_tasks/DEV_20261020_20_M4_SYSTEM_EVOLUTION_ENGINE_IMPLEMENTATION_V1.md](../../docs/development_tasks/DEV_20261020_20_M4_SYSTEM_EVOLUTION_ENGINE_IMPLEMENTATION_V1.md)
- [详情及最近历史](DEV-fbfcbf7760e7bd831da0.json)。完整历史通过 `show --issue DEV-fbfcbf7760e7bd831da0` 分页读取。

规划指针：未来独立校准工程；首个真实季后赛才积累校准数据，本轮不实现公式或32滑块调节

