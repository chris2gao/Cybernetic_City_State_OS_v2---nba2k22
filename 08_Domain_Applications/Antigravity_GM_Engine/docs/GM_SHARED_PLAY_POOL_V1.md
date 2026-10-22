# GM共享战术池、用途与适配性 V1

接收决定：玩家2026-10-20明确接受DEV23成果，并批准[PR #10](https://github.com/chris2gao/nba2k22-gm-engine/pull/10)作为“战术知识基础设施”合入main（工程提交88a16ec，实际merge commit查PR）。这是工程/知识接收，不是逐战术原生类型、比赛效果或游戏执行认证；本页已列缺口继续有效。

2026-10-20，玩家明确追加授权：创建每条战术的类型/用途/球员与球队适配结构，复用共享池与球队手册引用，并确认球员四PlayTypes及球队四Freelance都按前槽优先、执行更多理解。该授权只覆盖本页的知识数据与读取入口，不自动开展整套B2–B6、游戏写入或测试。

> **2026-10-20玩家新增的战术理解线索**：游戏战术详情页有2D棋盘式动态演示，原生类型可与每人四个PlayTypes关联；战术名称中的数字/英文动作可以为阵型、参与位置、篮球年代和终结方式提供**推断线索**。用户举例`9015shot`中“90代表90年代、15代表1/5号位、shot代表投篮”，这是一条**待具体战术核验的举例解释**，不是已认证的2K22通用命名规则。已有名称推测的`type_candidates`只能帮助检索，不能升级`types.memberships`；第一执行者/指定呼叫人/实际终结者也须分开。后续原生类型→名称语义→2D预览动作序列的取证规划已正式收入[DEV28 §3.1A](development_tasks/DEV_20261020_28_GM_NATIVE_IO_TRANSPARENCY_AND_EXECUTION_COMPLETENESS_MASTER_PLAN_V1.md)；**2D预览内容不自动证明3D实战CPU战术调用**。玩家无法提供截图，必要时仅要求文字描述，不能作前置阻断。新增信息不授权直接游戏写入。

## 2026-10-20 战术命名语法正式更正

用户确认 NBA2K22 的真实战术 **`'95 FIST 15 SIDE`** 属于**挡拆**。现有共享池已经包含 `2K22_PLAY_79215b33` / CRC `0x79215B33`，且具有 `STATIC_LABEL_CRC_JOIN` 来源。`'95` 指1995年，`FIST` 为挡拆动作，`15` 表示1号位持球参与与5号位设置掩护，`SIDE` 表示侧翼执行版本。类似`'85`、`'05`可区分战术的时代设计背景；具体原始NBA球队仍需历史考证。

应把`YEAR/ACTION/POSITION/LOCATION/FINISH`作为**真实的领域命名规则**解析，而不是一概降级为随机字符串。计划中的两人动作、动作受益人和真实场上终结者仍须区分；若动作目标是5号位投篮，名字中的后位数字可表示预计投篮者，不总是掩护人。用户进一步说明`Play Discipline`球员倾向及教练`Run Plays`设置与战术被完整执行或提前改变有关，此观察得到2K22社区战术纪律/Touches/PlayTypes关系讨论的支持，但固定概率与准确内存字段仍需验证。

**证据严格分层**：此条原生名称/CRC已在池中；“挡拆家族”来自用户直接确认（`PLAYER_REPORTED_UI`）；`types.memberships`当前为空，没有具体`native_type_id`认证，不能擅自填4/5/6/7或宣称真实3D执行已验证。由Codex在DEV28 D28-1将解释规则加到**版本化原始种子与生成器**，避免只更改派生`play_pool_v1.json`被重建覆盖。详见[DEV28 §3.1B](development_tasks/DEV_20261020_28_GM_NATIVE_IO_TRANSPARENCY_AND_EXECUTION_COMPLETENESS_MASTER_PLAN_V1.md)。

## 1. 实际交付和覆盖

- `src/gm_core/play_pool.py`：纯DTO/引用查询，`Knowledge.play_pool()`按需加载，默认M2/B1逻辑保持原入口。
- `web_gm/knowledge/plays/observed_catalog_v1.json`：从已有密封SQLite归档提取的84本加载目录；包含各本68槽和静态名称证据，不含球员属性、原始镜像或运行时地址。
- `web_gm/knowledge/plays/play_pool_v1.json`：按CRC唯一存储的1,392条引用，不按球队重复建卡；1,345条有静态名称，47条名字未知，455条由多本书引用。
- 1,335条有**基于名字的定性用途推断**；49条用途未知；8条仅见于Favorite组，保留类别/快捷项语义未知，不能冒充完整脚本。未知与Favorite项也有结构，不编造用途。
- `scripts/build_gm_play_pool.py`：离线生成器；只读显式种子JSON，写知识文件，不读游戏/SQLite或调用执行器。首轮种子整理只使用已有归档与本机PE静态标签，没有新采集或进程访问。

**当前1392条的精确原生类型成员关系均未认证。** 每条都有`types`字段，当前状态UNKNOWN、memberships为空；名称推测的类型候选另放`type_candidates`，不能悄悄升级。结构和GM只读用途检索已实现，完整逐条原生分类尚未完成，不能把名称覆盖冒称类型覆盖。

该池是当前已加载过目录的**已知子集**，不是宣称全部游戏资产均已穷尽。原始归档批次`2021-2022_M02_DEC12_FULL_20261018`只作来源标记；不挂接当前游戏档，也不认定任何球队现在仍使用这些槽。没有调用旧库玩家能力/Potential或将旧库装作GM_SANITIZED来源。

## 2. 数据结构：一个条目，多本手册引用

原生ID使用`2K22_PLAY_<8位CRC>`，不是把名字作为唯一键；同名但不同ID不合并，同CRC的多个候选静态名保留歧义。

| 每条字段 | 含义 |
|---|---|
| play_id / native_crc | 共享引用标识，不能当批准写请求 |
| names / name_status | 静态字样与CRC关联、未知或歧义 |
| entry_kind | 普通已加载引用 / 仅Favorite项 |
| types.status / memberships | 多类型成员列表，每个type_id有独立证据等级/来源；支持玩家说明或后续原生认证 |
| type_candidates | 名称产生的候选枚举，仅候选，不参与默认精确类型过滤 |
| purpose / purpose_status | 用途说明，清楚标NAME_INFERRED或UNKNOWN |
| fit_profile_ids | 规范化适配资料引用；读取完整卡时解析为player_fit/team_fit/poor_fit_or_counters |
| action_tags / naming_clues | FIST、POP、SHORT_ROLL等字面线索；不用词根证明引擎分支 |
| evidence_refs | 原始目录、静态标签、用途解释和玩家规则的来源 |
| known_in_books（读取时解析） | 同一条在多本书的引用及槽索引；有归档批次与分页，不表示所有权/当前指派 |

用途/适配模板存一次，完整查询会把实际内容放回`fit`；因此GM无需自己再次按词根猜适配。模板包括挡拆、接掩护投篮、手递手、低位、单打、切入、高位连接，以及POP外弹、短顺下、SPLIT等细分线索。每个模板都有球员技能/职责、适合的球队组织方式、不适配/被克制条件、已有M2知识引用与推断等级；没有固定位置白名单或数值能力加成。

例如`FIST 14 POP`的普通挡拆说明结合POP的外弹说明，完整卡会提示持球创造者、能投篮的掩护接应者、空间队友，以及无射程/换防限制等代价。`FIST 5 SHORT ROLL`会附带短接应传控者与弱侧投射的适配说明。**数字可以表示动作参与位置**：玩家已确认如 `FIST 15` 中 `1` 是主要持球发起位置、`5` 是掩护位置；但不同动作类型中数字的具体职责不同，不能将 `14/5` 一律解析为固定受益人，也绝不是原生 PlayType 枚举编号。

同一条可被多队装进各自手册；可参考其他队已有动作来选共享池条目，**写入目标始终是本队书**。这不要求某动作先天属于该队，也不允许改其它队容器。现有DEV14已经要求目标CRC来自本次所有已加载书的目录（`loaded_play_crcs`），不是仅限本队原有CRC；本页不改该执行代码，历史池也不能替代新同批来源。

## 3. 优先级与槽位容量

玩家新增规则同时适用于球员四类型和教练四Freelance：越前优先级越高、执行更多。球员1/2主要、3/4偶尔；Freelance四槽同样保持有序，但不套用球员四槽的具体频率描述。效果、教练和多个因素会影响调用，不追索精确概率、严格顺延公式或失败阈值。CPU对打自动选择，人类按键指定调用另属临场操作。

本版本复用当前PC结构：总68槽，Regular30、Bench20、Endgame10、Favorite8。不同容器的空位分别计算，不能把Favorite空位当Regular添加容量；Regular满时需替换，不能无限追加。容量来自当前schema，不把其它平台攻略的“50条”转为本机边界。查询只报告归档占用，不生成add/replace/stage或修改提案。

原生精确类型补录时，允许在种子中增加可追溯的`type_memberships`：键是小写8位CRC，例如`0x2958bec7`，值为成员列表，每项包含`type_id`、`evidence_status`（PLAYER_REPORTED_UI或NATIVE_TYPE_VERIFIED）和`evidence_refs`。不知道就不填，禁止把生成器词根候选复制成已认证成员。该落点用于已获得事实的人工补录，本轮没有新建元数据调查/审批系统。

## 4. GM读取入口

复用`Knowledge.play_pool()`和`gm_knowledge.py`，没有新事实数据库或第二套GM系统。以下为使用示例，**本轮没有运行自动化测试，也不声称这些示例全部做过验收**：

```powershell
# 数量、已知/未知与两种四槽规则
python -B scripts/gm_knowledge.py play-coverage

# 查一条具体战术，解析用途、类型状态、完整适配与前5个手册引用
python -B scripts/gm_knowledge.py play-show --play-name "FIST 14 POP"
python -B scripts/gm_knowledge.py play-show --play-id 0x2958bec7 --offset 5

# 按名字、动作、球员职责或球队打法找候选
python -B scripts/gm_knowledge.py play-search --text "SHORT ROLL" --limit 3
python -B scripts/gm_knowledge.py play-search --role SHOOTING_SCREENER --limit 3
python -B scripts/gm_knowledge.py play-search --team-style MOTION --action-tag CUTTING --limit 3

# 默认只匹配已声明且有来源的原生类型；当前没有该元数据，返回0是真实缺口
python -B scripts/gm_knowledge.py play-search --play-type 15
# 显式查看按名称推断的类型候选，输出不会标TYPE_MATCHED_ONLY或获批
python -B scripts/gm_knowledge.py play-search --play-type 15 --include-inferred-types

# 查归档某一本的容量与5个槽；枚举28是该归档的Warriors，不能假定当前档相同
python -B scripts/gm_knowledge.py play-book --book-id 28 --limit 5
```

search/show的引用页/book的槽位页都限制每次1–5项，返回next_offset；一个完整show条目含规范化适配说明。按ID顺序展示，不伪造排名/成功率。精确名字有多个原生ID时要求明确ID，不能静默选错。同名/同类型、用途相似都不等于同一动作对象。

普通战术搜索不把仅Favorite出现的8项当完整战术候选；要研究这些类别/快捷项，可显式play-show或在play-book中查看，原生记录不删除。

类型过滤默认不含推断，显式开启才返回`NAME_INFERRED_CANDIDATE_ONLY`。有PLAYER_REPORTED_UI成员也保留该等级，不升级为内存认证。只读引用卡不直接接M3正式经营、Desired或游戏写入；正式方案仍需新同批合格来源和现有审批。本页不绕过B1历史Claim裁剪，不向其注入任何后续NBA赛果、未来能力或新SystemCard。

## 5. 来源、构建与交付限制

原始目录的84本和静态标签已放在版本化种子，故离线重建不要求持有游戏或管理员进程：

```powershell
python -B scripts/build_gm_play_pool.py
```

用途/适配是现有M2通用篮球知识与战术字面线索的定性解释，非逐条视频认证；无法识别就UNKNOWN。补充查阅的[2K22原作者手册制作说明](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/nba-2k-basketball-rosters/916550-nba-x%E2%80%99s-o%E2%80%99s/page11)也区分动作、人员适配及CPU/人类使用差异，但该文含2021-11后实际赛季观察，本轮**没有将其球队/战术清单或后续赛季事实导入普通GM**，也没有据此认证本机类型。官方操作入口与较早攻略参见[DEV23补录](development_research/BPTI_DEV23_MANUAL_AND_PLAYER_CALLING_RULES_ADDENDUM_V1.md)。

本轮已执行：从既有归档提取无地址种子、静态名称CRC联接、离线构建、构建期间DTO/引用一致性检查及生成覆盖统计。没有新增或运行测试脚本、旧测试集合、真实GM、比赛或游戏读写。执行器、source_catalog及受控写入能力不变；已记录的team_book后缀匹配问题未修，不将池入口存在当作它已解决。


## 2026-10-20 玩家12类战术分类与球员PlayType必须分别记录

玩家补充12类可见战术：单打、挡拆、挡拆外弹中投、挡拆外弹三分、挡拆选项、低位背身、高位背身、后卫背身、中投、三分、手递手、切入。**这些是战术目录的动作类型**；仓库`play_type_names=0..15`（含None）则是球员4槽适用的角色/分配类型。不要把二者当作同一枚举，也不要把`type_candidates=[4,5,6,7]`从名字推断升级为已证本机native membership。真实`play_crc→战术类别`及战术类别→球员PlayType兼容须独立认证。

玩家明确表示：若运行时内存/已加载战术数据不能可靠识别分类，可在Antigravity调查中**向玩家索取必要截图**，可能需要几十张；先查看游戏里所有类型的候选列表，必要时逐类截图/标记覆盖率，而非要求每条1,392 CRC均视频演示。社区先行检索，实机类型枚举随后认证。

具体表格、英文对应、取证和GM字段要求详见[12类战术/内存映射研究](development_research/NBA2K22_PLAYBOOK_12_CATEGORY_AND_NATIVE_TYPE_MAPPING_V1.md)。本次只更新文档，战术池JSON、生成器、native枚举尚无新可认证填充。
