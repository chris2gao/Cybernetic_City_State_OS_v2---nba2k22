# DEV29 R07研究发布自检与独立审核检查清单（2026-10-21）

> **本文件是研究交付者的静态自检，不是独立验收。** 当前状态`R07_RESEARCH_PUBLISHED_PENDING_INDEPENDENT_REVIEW`；只有用户/独立审核模型检查后才能作R07研究结案决定。R01–R06现有研究证据不因此升级为原生UI/运行时/数据发布或可写权限。

## 1. 实际交付
- [40个功能族/10条既有生产来源/20项缺口矩阵](../game_mechanics/catalogs/R07_GAME_CAPABILITY_MATURITY_MATRIX_V1.json)；
- [694项可追溯研究总入口](../game_mechanics/catalogs/R07_ITEM_TRACEABILITY_INDEX_V1.json)和其中`parts[].path`指定的7份分卷，每卷94–100项；
- [R07中文证据七层与可观察/可执行信息总指南](../game_mechanics/guides/R07_OBSERVABLE_ACTION_EVIDENCE_MATURITY_GUIDE.md)；
- [R07→DEV28非授权证据差距交接](../game_mechanics/R07_TO_DEV28_EVIDENCE_HANDOFF.md)；
- 已更新资料库README、PROGRESS、Bootstrap、34基线、开发长期记忆、视觉证据索引。

## 2. 自检实际运行和结果

| 验证项 | 静态核查结果 | 限制 |
|---|---|---|
| 总清单与7卷读取 | 7份JSON均GitHub回读并JSON解析 | 总清单不含全部`items`，必须按`parts[].path`逐卷读 |
| 逐项身份 | 合计694条，ref_id唯一694/694，`origin.path#array#item_id`唯一694/694 | 含12个R01指南主题与682条不同源JSON研究对象，绝非694原生字段 |
| 来源字段保留 | 分卷存储`source_ids`、`project_refs`及`original_research_source_refs_raw`；所登记SRC编号在SOURCES存在 | SRC**编号存在**不代表其原网页逐项语义匹配；`direct_source_support_verified_in_R07=false` |
| R06-B有界修复继承 | 31项历史/奖项/媒体概念中的10类没有直接来源，均保留`source_ids=[]`及`RESEARCH_CANDIDATE_UNSOURCED` | R06-B独立修复已通过，但未来PC22奖项菜单仍未实证 |
| R06-C缺源继承 | 38项里原JSON有7项`sources=[]`；另外4项只有项目/非SRC引用未被错归为无证据 | 项目文档/源码引用不自动证明PC22原生菜单或Save持久 |
| 功能族完整性 | 40项唯一ID，86个定位锚点全部对应原研究文件中真实项目ID；涉及12个原目录源文件，R01指南主题另行确认 | 86锚点是跨目录身份映射，不等于86条原生因果或读写能力 |
| 既有生产证据 | 10条历史范围/阶段/权限综述，明示出处为34/37/38/40/27及相应手册 | 没有对当前新batch做全量复算或实机重测 |
| 遗留问题 | R06-D的20项已继承，P0=8、P1=10、P2=2 | 不自动等于20个获批Codex/DEV28任务 |
| 中文指南对齐 | F01–F40、REAL-01–10、P0 G01–G08全部出现，路径和README/Baseline/Bootstrap已读回 | 不能以指南出现某能力就推断生产已支持 |
| 新原生现场认证 | 0新菜单完整截图、0新实时读取、0游戏存盘实验、0游戏写入、0新正式批次 | 本次纯研究，静态证据等级必须诚实保留 |

## 3. 要求独立审核人重点判断（不可由本窗口自行盖章）

1. **来源真实性**：抽样从`index.parts[].items[].origin`返回原始目录，比对`source_ids`和`original_research_source_refs_raw`的真实含义；对于已知错误SRC-0178，不应再映射其它10类奖项。逐页语义核查未完成的项目保留`SOURCE_CLAIM_NOT_AUDITED`含义，不得假称来源全面认证。
2. **成熟度正确性**：检查七维是否真正独立；尤其Global Slider注册、动态Box、教练字段部分写回、Approved Trade、自由市场签约源码存在之间，不能自动串联成“可执行”。
3. **既有生产对照**：对照最新`docs/34_BASELINE_CURRENT_STATE.md`、`docs/37_APPROVED_TRADE_EXECUTOR.md`、`docs/38_APPROVED_SIGNING_EXECUTION.md`及`docs/40_COACHING_EXECUTION_RUNBOOK.md`；是否夸大身份稳定、名单人数、赛季统计细度、Coach Matchup范围、签约真实验证、普通球员能力修改权限。
4. **模式与时间**：3D Gameplay、Calendar Sim、SimCast Jump-in、Normalize Stats/Minutes与GameID结果对照不可替代；`GAME_SEASON`、1984–2020选秀年度与外部历史纪元不能合并。
5. **保存真实性**：SteamCloud、MyLEAGUE Save/SaveAs/Autosave、DEV14托管存档、SQL数据库新发布批次全部是独立对象；R07没有证明任何新的退出/重新载入。
6. **信息公开范围**：未来Coach/Player/GM/Media列的是潜在资料使用视角，并非当前可访问的角色ACL、原生游戏新闻写入或人物人格规则。隐藏Potential、私人报价不得自动对Media开放。
7. **可使用度披露**：项目确实已有若干历史生产读源和有限获批执行器，但694异质目录项、40功能族和10既有生产证据并不产生可以当场统计的“已上线原生字段百分比”；需要以后拿到实际schema/manifest和实时field-level readback才可计算真实覆盖率。
8. **工程闸门**：研究经独立验收才可考虑用户另授权FINAL-CODEX的**静态对账任务**；本次未启动DEV28、Codex、游戏写入、人格/世界流程开发。选秀权旧+3守卫属于单独授权维护问题。

## 4. 下一步规范

当前是**研究资料发布，等待独立审核**。如审核发现局部来源归因或成熟度偏高，定向修订对应条目与指南，而非重启R01–R06。R07可以研究结案并同时保留大量原生PC22 UI/内存/存档未知；研究结案不等于DEV28实现或世界六类模型已能实际读取所有事实。

建议独立审阅状态值：`R07_REVIEW_PENDING`，最终正式状态由玩家后续独立审核决定。不得让本自检文档的出现构成自动批准。
