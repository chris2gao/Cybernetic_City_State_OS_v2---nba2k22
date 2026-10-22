# NBA2K22 PC 本世代：12种战术类别、球员PlayType与内存类型映射研究 V1

> 2026-10-20。玩家实机分类说明 + 2021年前后NBA2K社区经验核对。用于DEV28/D28-1战术全透明、Antigravity内存调查、Codex知识与执行整合；**不改原生游戏数据，不自动合并PR #12**。

## A. 研究方法：先查社区，后定向补原生证据

此前开发研究过度依赖用户逐个解释，已经纠正。社区应是**篮球战术语义与历史命名的第一参考层**，Antigravity则负责认证这台NBA2K22 PC游戏的**确切内存字段、类型枚举及与CRC/书槽的对应关系**。不同证据并列存储，不要因为“还没读到type_id”就让GM对所有已有战术一无所知。

参考：
- [Coach2K：List of NBA2K Play Types](https://coach2k.com/nba2k-playtypes/)：对Isolation、P&R、Pick and Fade Mid、Pick and Fade 3、P&R Option、Post Up Low/High等类型给出动作定义和演示实例；该网页现在可能偶尔无法直接打开，但其索引可检索。
- [Reddit 2021本世代实际Playbook示例](https://www.reddit.com/r/NBA2k/comments/o3ohgv)：逐类别归纳历史版`Fist`、`Iso`、`Give`、`Punch`、`Quick`、`Cut`真实名称，包括`'05 Fist 15 Side`、`'87 Fist 15 Spread`等。这是游戏玩家整理的具体战术名，但**不是每条本机CRC的类型认证**。
- [Operation Sports ATD球员PlayType与手册配套](https://forums.operationsports.com/forums/forum/basketball/nba-2k-basketball/891805-how-to-make-players-play-like-themselves-the-atd-guide/page2)：解释角色偏好、名单原生PlayType及可用战术未配套时的AI调用问题。
- [2021 NBA2K社区针对球员PlayTypes与倾向](https://www.reddit.com/r/NBA2k/comments/nwl1ec)：讨论隔离、内线、手递手、切入、挡拆、出手倾向之间的战术适配。属于社区实践，不将推荐数值当官方计算公式。

## B. 玩家确认：在战术界面能够选择/浏览的12种动作类别

| # | 游戏中文类型（玩家实机） | 英文资料对照（社区通用称呼，不保证UI逐字） | 篮球目的与主要协作角色 |
|---|---|---|---|
| 1 | 单打 | Isolation | 清空一侧，主要进攻球员自己制造机会 |
| 2 | 挡拆战术 | Pick and Roll | 持球者+掩护者，掩护后突破、顺下与分球 |
| 3 | 挡拆外弹中投 | Pick and Fade Mid | 掩护者外弹到中投区域接球 |
| 4 | 挡拆外弹三分 | Pick and Fade 3PT | 掩护者外弹到三分线外接球 |
| 5 | 挡拆战术选项 | Pick and Roll Option | 根据防守变化在顺下/外弹等选项中读取 |
| 6 | 低位背身单打 | Post Up Low | 低位接球背身、转身、脚步、低位出球 |
| 7 | 高位背身单打 | Post Up High | 高位/肘区接球、策应及中距离终结 |
| 8 | 后卫背身单打 | Guard Post Up | 后卫/侧翼背身利用错位、转身或分球 |
| 9 | 中投 | Mid Range | 通过掩护/绕跑/接球形成中距离机会 |
| 10 | 三分 | 3PT | 为射手制造三分线外投篮机会 |
| 11 | 手递手 | Handoff | 传递+近身掩护/连续接应创造优势 |
| 12 | 切入 | Cutter | 无球切入篮下、摆脱防守并接球终结 |

**用户列出的12项均按原意保留。** 游戏是否将其中某些子类归入父类，由Antigravity实机验证，不能任意删掉。

## C. 三种不同的数据维度，禁止混淆

1. **PLAY_CATEGORY（战术动作类别）**：玩家列出全部12项。理想结构是每条play native CRC → 可见游戏类别ID/字段→类别名称，原生真实映射尚需Antigravity从战术选择页面/内存对象定位；如原生一条play属于多个类别，应保存多成员关系；不能假定类型一定与CRC在同一个定长结构块，先观察再判断。
2. **PLAYER_PLAY_TYPE（球员四个有序玩法指派）**：仓库`config/state_io_native/player.json`与共享池`play_type_names`已有0..15枚举：None / Isolation / Isolation Point / Isolation Wing / P&R Ball Handler / P&R Point / P&R Wing / P&R Roll Man / Post Up Low / Post Up High / Guard Post / Cutter / Handoff Receiver / Handoff Passer / Mid Range / 3 PT。其编码已登记，但**具体Playbook动作分类怎样与球员这些槽在3D AI里匹配仍需关系取证**。不能因为球员有4号P&R Ball Handler就推断所有FIST战术必然属4号；既有名称`type_candidates`只能辅助搜索。
3. **PLAY_NAMING_SEMANTICS（战术名称解码）**：已在共享池发现真实`'95 FIST 15 SIDE`，CRC`0x79215B33`；玩家确认95=1995年、FIST=挡拆、15=1号位持球+5号位掩护、SIDE=侧翼版本。该家族命名具有明确的篮球语义，其余名称应按动作/数字格式/年份及演示进行家族级归纳。名称语义来源`PLAYER_EXPLAINED_NAMING_CONVENTION`，并不等于具体原生枚举ID。

## D. 给Antigravity的优先发现路线

1. 打开一支球队真实的战术书编辑/战术选择界面，使用已存在的`'95 FIST 15 SIDE`作锚点。先确认UI显示的类型及所属类别，查找该CRC在运行时关联的类型字段或索引；枚举可能存在于战术表、分类索引、过滤器映射或UI缓存，不预设物理布局。
2. 检查**类型过滤变化**对候选CRC集合的真实影响：选择“挡拆”“挡拆外弹三分”等类别，差分游戏内当前列表和对象引用，找出可复用的映射；注意书的已装载槽、全局候选池、球员个人四槽分别是不同实体。
3. 给每个确认类型输出`native_category_id / UI_localized_name / 关联候选CRC列表或映射指针 / 枚举来源 / 游戏版本 / 证据等级`；测试一个样例的真实选择/切换，不要求为每条战术反复测试3D效果。
4. 如果仅靠进程内存找不到类别，**可以向玩家请求截图**。先请求按类型过滤界面、类别总菜单及2–3个有代表性的战术详情截图。若要覆盖所有类别的全部战术，可能需要几十张甚至更多，按可复用批次组织，明确已覆盖/仍缺的类型与页面；不要求玩家在Codex活跃会话中提供全部截图/录屏；产生问题和已完成部分后`TASK_CLOSED`。
5. 游戏的2D动态战术板可再用于核对相同家族动作差异、预计参与位置和第一/第二进攻机会；**动画可见≠自动能够从内存读到坐标脚本**，无数据可用时允许小量截图或文字描述，不阻断基本类型目录发布。
6. 优先覆盖项目共享池已登记1,392条去重CRC及84本历史已加载书的本机版本；但目前历史目录不证明“当前存档全部候选都已加载”。需要按新同批来源认证完整性。

## E. 后续Codex对外输出形态

对GM返回既有`play_id, native_crc, raw_name, book_slots, fit_profile`并扩展两层可查询结构：

```yaml
native_play_category:
  native_category_id: UNKNOWN
  ui_display_name: "挡拆战术"
  category_name_source: PLAYER_REPORTED_UI
  play_membership_status: PLAYER_REPORTED_UI # specific CRC -> category (for '95 FIST 15 SIDE)
  native_mapping_status: NATIVE_ID_UNVERIFIED
player_play_type_compatibility:
  assigned_player_enum_ids: [] # from current player, not invented
  known_allowed_enums: [] # only if native relation proven
  name_inferred_candidates: [4,5,6,7]
  relation_status: UNKNOWN
name_semantics:
  year: 1995
  action: FIST
  primary_ball_handler_position: 1
  screening_position: 5
  region: SIDE
  evidence: PLAYER_EXPLAINED_NAMING_CONVENTION
preview_motion: NOT_OBSERVED
in_game_3d_call_observed: false
```

字段示例中的CRC/名字/篮球语义来自已识别条目，`native_category_id`尚未确认。静态名称可支持GM先研究战术，但不能因此生成未经授权的写入计划。

## F. 不能把类型列表研究绑到PR #12

PR #12的F1–F4已由Codex修复并等待审核合并；本文件是DEV28的后续数据透明化研究要求。不得在原PR中额外实现类型全量、战术执行器、实时比赛数据或截图采集。玩家批准的任何原生游戏修改仍由Codex按既有DEV14权限处理。
