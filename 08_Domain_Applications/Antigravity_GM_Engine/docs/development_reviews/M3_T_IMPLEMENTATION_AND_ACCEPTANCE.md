# DEV13 / M3-T 实现与最小验收

日期2026-10-20，分支codex/dev10-m3-design，原PR #4已由玩家批准，Ready后正式合并至main，合并提交`504a4c0656bad0e890c3783c89c656fca5b2e647`，开发head `7e8ba1a`。正式本地工作区已同步；本次Git收尾没有追加测试。状态：M3_T_ENGINEERING_MAIN_MERGED；GM_V4_DRAFT_NOT_ENABLED；REAL_CAPTURE_NOT_TRIGGERED。本页是主线窗口②的交付，不取代DEV14窗口①的原生验收。

## 接收和整合

按任务先fetch并读取origin/main的AGENTS、开发规范V2、docs33/34，再接收DEV14_TO_M3_HANDOFF、DEV18与运行手册。PR #5已经正式合并：main为570419a，DEV14最终开发提交f68d75d。原交接中的“未合并”为交付时历史，本次按Git实态更新说明。

整合提交82083b5保留原M3 fa62fb2及其前任。实际冲突为query.py、gm_data_query.py和docs34：保留team_stats/team stats，同时保留DEV14全部新域、rotation、native_objects/native_books和脱敏检查；状态索引保留双方历史。没有用旧整文件覆盖DEV14，也没有重写采集、三库架构、原生codec或执行器。

## 实际完成的接口

| 范围 | 实现 |
| --- | --- |
| 安全数据桥 | analysis_inputs先require_gm_sanitized；固定同批读取原M3及DEV14对象/字段。named tendency按队分区，个人防守按显式OWNER:OPPONENT读取；不展开全联盟所有个人对位。来源带实例/代次/Registry版本 |
| Coach与Book | 保留19项教练读取、普通18项动作；M0 coach_traits在DEV14封存COACH_DEFAULT raw上复用原DEV12读取器取得8体系熟练度/评级，移除地址和“最高=最优”结论。native_books增加已捕获68槽，native_context投影安全元数据，不新增原生采集 |
| 球员与发展 | 技术能力与4PlayTypes/Initiator/48具名倾向、训练6+5字段、负荷样本及轮换bias进入按队事实。Potential只显示MASKED/null，Intangibles与真实能力/市场筛选分离；两者不作确证成长变化 |
| D1–D6 | 全员role_plan、目标分钟区间（非锁定）、内部战术证据、被否定内部修复、内部比较后的市场缺口及证据质量。CRC覆盖固定UNKNOWN；Touch/最高熟练度不自动转交易或改体系；双方需先比较内部替代再报价 |
| 正常动作 | COACH_DEFAULT、PERSONAL_DEFENSE、PLAYER_PLAY_TYPE、PLAYER_TENDENCY、TEAM_EXCLUSIVE_PLAYBOOK_CONTENT、TRAINING_PLAN、LINEUP_ROLE。禁OVERALL及自由PlaybookID；坏字段/未知对象不伪造准备成功 |
| 换帅与归位 | 显式season_phase语境、COACH_EVENT工件记录真实操作者确认引用；同工作台同career/season跨节点每队仅休赛期一次。TEAM_BOOK_REBIND自动匹配当前加载本队同名书，只生成独立单动作；绑后新来源再另提槽位。无员工合同/签约/竞价执行器 |
| 组合和交接 | 同对象同字段不同目标冲突、同值合并；交易后战术/训练/对位及换书后旧战术进入重计划。适配层调用原gm_state_io.plan.build_plan，输出真实digest/完整tuple/数值diff/稀疏intent，不调用stage/preflight/apply |
| CLI/导出 | gm_analysis native分页/字段/人物过滤、prepare --defense-matchup；gm_decision --season-phase、record-coach-event、现有审议/组合/终稿；导出额外intent_N.json与approval_tuple_N.json，仅限OFFLINE_PREPARED项 |

实现复用原模块和工作台，无新增业务数据库或反伪/权限服务。gm_core继续只接DTO；只有数据适配层调用DEV14静态来源/规划器。M3不接受raw、地址或自报批准，不更改被观察事实。旧未脱敏M3缓存也不向GM返回原潜力。

## 八项明确授权的最小验证

命令：`python -B -m unittest discover -s tests -p test_m3_t_integration.py -v`。测试资料全为隔离合成SQLite/原生记录，30队90个在队身份，不冒充真实466人或实际30队经营。

| 目标文件要求 | 对应检查及最终结果 |
| --- | --- |
| 1 原M3核心不丢失 | test_01：精确30队全员集合、M3主要入口保留、一队review/alternatives及共享工作台往返、team_stats和DEV14新视图同时可用；PASS。不重跑旧P1–P5/15项集合 |
| 2 新查询正确消费 | test_02：有序四槽/48具名倾向、实际样本场均分钟、8体系值、当前绑定和代次来源；高Touch不自动定角色、最高熟练度不宣称最优；PASS |
| 3 遮蔽潜力不作事实 | test_03：Potential/null/占位语义、与bias一起排除真实技能筛选；无mask标记源与旧缓存拒绝；PASS |
| 4 各类稀疏意图 | test_04：教练、两名个人防守、PlayType、具名倾向、球队/个人训练和Intangibles合并为8项，原DEV14规划器实际接受，冲突目标拒绝；PASS |
| 5 正常GM禁用项 | test_05：整体防守、自由切书拒绝；PASS |
| 6 换帅后恢复本队书 | test_06：OFFSEASON确认事件/同季第二次与常规赛限制、独立单动作恢复A书；新POST_B来源上另提A槽内容，B书未变；PASS |
| 7 缺口诚实 | test_07：疲劳/位置专属模板/3D与Sim效果未知；CRC-only不能称STATIC_VERIFIED；未完成内部比较不升级市场方案；PASS |
| 8 批准和原值边界 | test_08：规划无批准/无地址raw，原合成PLAYER字节不变，Ability/Potential字段与越界bias拒绝；PASS |

准备fixture时补齐了现有净化器要求的真实净化凭据，未给历史数据补标。首轮8项中6通过、2个样例断言失败：AccessError需匹配code而非message；球队与球员训练示例动作ID需各自唯一。修正后只重跑test_03/test_04并通过，未重跑已过6项；没有运行旧DEV14的119项、旧M3集合、网页连接、现金或任何实机验证。既有M02证据仅保留为历史兼容资料，本轮没有把它用于新GM研究。

上述通过后仅补充show摘要的season_phase/事件信息、将球员Potential/Intangibles筛选禁用明确限于players/pool（不误禁Staff），并完成文档和提交收尾；依开发规范V2未另跑检查或复跑已通过测试。因此这里报告的是八项目标的已有证据，不声称最终整棵代码已再做一次全量回归。

## 一个已发现、未纳入本轮修复的底层依赖问题

合成源若在state_io_captures.metadata_json中保留完整Registry（包括未观察的World域），现有player_potential_mask._unknown_mirrors会把目录键`world.contracts_and_finances.player_potential_factor`当作球员潜力别名，返回UNKNOWN_PLAYER_POTENTIAL_JSON_MIRROR。该项是世界设置目录名称，并非原始球员潜力值；本轮未改底层净化器。

本次M3专用fixture只包含实际观察的战术/训练/轮换字段目录，并调用真实sanitize_player_potential生成两库凭据，再经现有M0封存验证。这证明M3消费合格的DEV14脱敏接口，不证明完整生产采集已经运行。**玩家2026-10-20明确选择“不扩展本轮，记录给DEV14窗口①后续修复”**；本轮不修改净化器、不追加所询1项检查。若保留现有完整目录，未来生产采集有此已知阻断，交DEV14窗口①处理。

## 剩余资料与交付层级

- Antigravity后置：CRC→真实PlayType/受益人/动作知识；51项未知倾向；更多位置专属训练UI模板；实时疲劳与历史疲劳单位/方向。当前训练九个通用原型按原profile使用，不冒称全位置模板；导师关系也未接入。
- 本轮未研究Intangibles对合同/交易/模拟的副作用，未做精确分钟锁定、教练合同市场、单项能力/潜力/徽章写入、额外Gameplay/World或历史新秀注入。
- 原M1财务、双边交易条款、终稿历史继续保留；交易仍为SPECIFIC_TRADE_INTENT、等待独立实时交易计划。Native OFFLINE_PREPARED仍需匹配ACTIVE和stage、真实玩家批准、实时预检与回读，不等于Desired已写入、更不是实际执行/存盘回执。
- 实际30队策略仍UNASSESSED、正式研究0队，V3继续生效，V4未启用，M4未启动。没有新生产采集/发布、游戏访问/写入、正式球队档案或GM_CURRENT/赛季INDEX变更。

操作入口：[M3-T手册](../../web_gm/manuals/GM_M3_TACTICAL_WORKBENCH.md)。PR #4工程实现已按玩家批准正式合并；合并不授予正式GM运行、生产采集或游戏写入批准。
