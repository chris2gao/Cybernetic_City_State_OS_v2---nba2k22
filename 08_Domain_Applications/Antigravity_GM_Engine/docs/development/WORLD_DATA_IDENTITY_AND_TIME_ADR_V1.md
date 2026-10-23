# WORLD-DATA-ARCH-01 存档、身份与时间 ADR V1

状态：CANDIDATE_PENDING_INDEPENDENT_REVIEW；2026-10-22。基准：407e2134bd2f595477099b2c6e3484c818059fd9。决策依据为本轮 Human 明确产品规则、DEV14 源码及原生候选证据。独立审核尚未完成。

Human 审核更新（2026-10-22）：本轮明确结论为“这次算审核通过”。详情及后续实际验证结果以 OS run 的 completion_pointer.json / human_review.md 为准；独立模型审核尚未进行，候选未合入 master。

## 1. 已确定的产品事实

**不存在存档分叉。** 每个游戏存档是独立世界；A/B 之间不合并，不继承比赛、历史、人物状态或 AI 记忆，不建 parent_world、fork、merge 业务。正常推进赛季不会生成新世界。相同姓名、PlayerID、GameID、年份和选秀模板不能建立跨档业务关系。备份文件不自动视为新世界：恢复原存档需明确登记；将副本作为另一个独立存档使用时重新登记为无父子关系的新世界，且不导入旧存档的动态历史或记忆。

本 ADR 明确覆盖 V2 与旧路线图中的“世界线分叉”措辞。旧 V1/审计/原始 AG 报告保留，不能通过改历史报告消除曾存在的错误。当前同步修订仅限任务授权文档。

## 2. ID 的取舍与真实工程含义

| 标识 | 生成者/作用域 | 生命周期与用途 |
|---|---|---|
| world_id | 外挂；一次独立游戏存档登记 | 唯一篮球世界身份，跨赛季/交易/技术重置保持；所有动态事实的隔离根 |
| save_id | 外挂/操作员；当前工作区目录名 | DEV14 路径定位符；可被技术重置复用，不能证明仍是同一个游戏 |
| save_instance_id | DEV14 UUID；一次工作区实例绑定 | create/adopt 生成；现行 reset **重新生成**，不是游戏提供的永久 ID |
| generation_id | DEV14 UUID；技术数据代际 | reset 生成；绑定库、批次、审批及恢复状态；不代表业务分支 |
| binding_id | 外挂；同 world 的历史技术绑定记录 | 封装原有三元组和同档验证证据；不替换 executor 所需原始三元组 |
| season_uid | 外挂；world 内赛季周期 | 以有证据的赛季序列登记；2021–22 只是标签，不是全局主键 |
| team_uid / team_season_uid | 外挂；world 内组织 / 赛季竞赛参与 | 交易不影响 team 身份；改名需连续性证据，赛季参与分开 |
| player_uid | 外挂；world 内实际游戏球员 | 等同 player_incarnation_id 的唯一规范名称；跨球队、跨赛季不变 |
| template_id | 外挂资源注册；静态资料版本 | 表示历史选秀素材，不能携带实例统计、人格记忆、未来成长事实 |
| game_uid | 外挂；world 内一次比赛 | 不由批次生成；赛季/竞赛和已认证原生映射确定归属 |
| batch_id / observation_uid | 外挂；一次采集 / 断言 | 重复采集产生新观察，不能产生第二个业务事件 |
| Native PlayerID / GameID | 游戏；实际稳定范围待证 | 最低按 world、binding、batch、对象类、来源命名空间保存；跨批次使用需映射证据 |
| slot / pointer / native index | 游戏运行时 | 默认为 capture-local，不能成为跨档/跨季主键；地址不进入普通角色视图 |

**决定：保留 world_id 与现有 save_instance_id 两种不同语义。** 选择依据是 [workspace.py](../../src/gm_state_io/workspace.py) 的 reset 同时替换 instance 与 generation；若 world_id 直接等同 instance，技术重置会切断连续生涯。若仅用 save_id，复用目录会错误接续其他存档。将 save_instance_id 改成稳定 ID 又会改变当前审批/防陈旧机制。因此增加一个稳定业务键，并由 TechnicalBinding 关联原有安全三元组，是解决真实语义差异所需的最小区分。GameSave/World/业务 SaveInstance 是同一个概念实体，不创建三张冗余业务身份表。

此决定只定义后继合同，当前 DEV14 不含 world_id，也未在本任务改代码。下一任务必须提供登记和同档绑定的证据格式，不能声称现行 reset 已自动保持世界历史。

## 3. DEV14 生命周期保留与适配

已静态核实 [save_context.py](../../src/save_context.py)、[workspace.py](../../src/gm_state_io/workspace.py)、[lifecycle.py](../../src/gm_state_io/lifecycle.py)、[capture_files.py](../../src/gm_state_io/capture_files.py)、[executor.py](../../src/gm_state_io/executor.py)：

- create/adopt 要求显式独立 save_id，生成实例和代际；adopt 不宣称做过新采集。当前四个未退役工作区限制是既有工程限制，本轮不改变。
- activate 检查工作区、三库绑定与来源一致性；未解决写入和 PREPARED 重置/采集日志会阻止正常操作。lifecycle lock 与 capture lease 是技术互斥，不是篮球事件。
- reset 要求精确 generation/manifest 确认，备份并核验三库和日志，生成新 instance 与 generation，更新目录并保留故障恢复。已有 published/saves 内容时因旧协议不支持 generation 而拒绝，不能绕过这个门。
- recover 恢复旧技术绑定是恢复操作，不产生第二世界。retire 停用工作区但不删除已证历史。source/decision/version/digest 绑定、前像、回读和未恢复状态继续保留。

后继模型的状态规则：

| 触发 | world_id | 技术绑定 | 历史/审批处理 |
|---|---|---|---|
| 同档正常新赛季、交易、退役 | 不变 | 无技术重置则不变 | player_uid 连续，新增 Season/归属/事实；既有有效审批仍必须通过各自 freshness/CAS |
| 同档重复采集 | 不变 | 同一 binding，新增 batch | 观察追加，业务实体去重 |
| 明确同档的纯技术重建 | 不变，仅有证据时 | 新 binding，保留旧 instance/generation | 旧批次可作同世界封存历史，但旧审批禁止复用；禁止把旧数据直接冒充新观察 |
| 无法确认加载的是哪一个存档 | 不分配猜测结果 | HOLD | 不跨绑定自动接续、不发布 |
| 目录被用于新的独立游戏存档 | 必须新登记 world_id | 新绑定 | 不继承旧世界历史或角色记忆 |
| 同一存档明确恢复较早备份 | 不变 | 需按技术安全流程重新核验/绑定 | 后发生的旧观察保留审计但标记不再属于当前有效历史；按明确恢复边界失效，禁止保留“两条可选世界线” |

恢复旧备份不是分叉：同世界只有一个当前有效事实视图。记录恢复事实、已知回退边界和被撤回断言版本；边界不明则暂停当前权威视图的推进，不能按采集时间“最新即真”。这只是同存档事实有效性的合同，不是新增恢复执行器或授权恢复游戏。跨技术代际的历史连续性只能来自登记证据和已获准保留的同档封存历史，不来自相同名字或目录。

## 4. 业务实体解析和去重

PlayerIncarnation 使用持久 player_uid。已经确认的同档同人映射在交易后保持，RosterMembership 新增区间；退休不回收 ID。再次导入同一历史模板产生新实例，不能因为模板或姓名相同而复用。PlayerID 的复用/重载/跨季稳定性待 NATIVE-ACCEPT-01；没有证据时保留 raw observation 和身份候选，不把不确定映射登记为规范事实。两组来源彼此不一致时输出 AMBIGUOUS 和证据，不能自动挑一个。

Game 的原生候选查找键至少包含 world、season、competition、source namespace 和 native GameID；它仍不是已证明唯一键。遇到碰撞、复赛、延期和无 GameID 来源，保留观察并 HOLD 业务解析。不得以“日期+主客队”兜底自动合并，也不能给每次采集一个新 game_uid 伪装解决去重。经验证映射能确认同一比赛时，两次观察指向同一个 game_uid；来源修订只改变该比赛的断言版本。

当前 TEAM/player roster slot、Box player_id、Career 索引必须经过同批次/同绑定的映射关系核验。跨批复用映射需要有效期和佐证：对应原生布局版本、无冲突对象证据、已验证连续性规则及前后来源引用。后续验收可以扩大映射有效范围，但不能预设全局唯一。

同一个已确认球员的历史单场按比赛发生时的 TeamSeason 归属统计。RosterMembership 边界晚于/早于某场的证据有冲突时，保留比赛原生球队与名单观察两者，报告质量问题，不重写旧 Box。合同球队、在场球队与发展联盟分配是不同关系。

## 5. 时间和订正

游戏时间采用 `season_uid + phase + date/sequence + precision/status` 的值对象，缺失日或比赛顺序时保留精度，不强行转成午夜时间。跨季排序用已确认 Season.ordinal，不直接排序显示字符串；无法确认原生年份时保留原码和 UNKNOWN。现实 observed_at 表示实际观察，recorded_at 表示入库，published batch 表示封存可见集合；valid_at/from/to 是游戏事实生效时间。它们互不替代。

每个事实身份与每次断言 revision 分开。修订追加 `supersedes_assertion_uid`，只允许同世界、同业务事实，保持旧版本、理由、来源、裁定者及 recorded_at。该链接是**事实订正**，不是世界父子关系。删除纠错采用撤回断言，历史审计不静默擦除。角色查询绑定 game_as_of 和 knowledge_as_of（何时已知）以及发布批次，避免未来观察污染过去决策。

重复采集且内容相同：两个观察来源、一份有效业务断言；内容不同：新的候选修订和质量记录，只有来源/身份/语义规则接受后成为当前版本；发布时间较晚不自动赢。对账失败不伪造事件，也不更改原生累计。

## 6. 六个明确反例及预期结果

下列均为人工构造的关系例，不声称当前游戏实测。测试输入与断言在 OS run，检测正例与反例。

| 场景 | 输入 | 必须结果 / 必须拒绝 |
|---|---|---|
| S1_INDEPENDENT_SAVES | A/B 都有 native PlayerID=30 的 Stephen Curry、2021–22、GameID=7；各自球员、单场、生涯 | A:p1/B:p1 是不同实例。读取 A 仅 A 记录。将 B 的 statline/career/memory 接到 A 拒绝；同档合法引用通过 |
| S2_CONTINUOUS_CAREER | A:p1 从 2021–22 到 2030–31；2024、2027 换队，三段 membership；技术重建由 i1/g1 变 i2/g2 | world/player 不变，三次比赛归属按当时球队；同档新 season 合法；旧 i1/g1 批准在 i2/g2 被拒；无同档证据不得续接 |
| S3_REPEAT_CAPTURE | b1 与 b2 观察经认证同一 game_uid=G7，比分相同；b3 有有据更正 | Game 数量仍为 1，来源观察为 3，比分修订为 2。未认证 native-key 重用 HOLD；不得仅凭相同 GameID 自动合并 |
| S4_TOTAL_MISMATCH | 已采两场得分 20+25，原生赛季总计 70 | 显示可观测和 45、原生 70、差额 25、coverage PARTIAL/CONFLICT，保留两场；不能造第三场 25 分或把 70 改为 45 |
| S5_HIDDEN_POTENTIAL | 底层含 potential、raw_struct、debug 嵌套值和 Potential 派生字段，普通 GM 请求 | 字段白名单和来源敏感传播阻止直接、嵌套、别名及派生泄露；允许有证据 points；未脱敏批次/跨档请求直接拒绝 |
| S6_SHARED_TEMPLATE | 同一静态模板 T1984 在 A、B 生成球员；A 有生涯得分和 GM/Player 记忆 | 可以共享模板引用；实例、发展、统计、记忆都独立。A 角色不得查询 B 记忆；同模板也不能把 A 生涯接给 B |

这六场景证明概念规则能表达和拒绝这些关系，不证明数据库实现、角色 API 安全或游戏 I/O。最终独立审核须检查证据与反例是否足以支持候选合同。

## 7. 待原生验收的问题与决策边界

NATIVE-ACCEPT-01 必须验证 GameID 的赛季/竞赛/重载作用域、StatBank 起点/有效记录数/容量和 InUse 关系、PlayerID 复用、Slot24 生涯索引边界与哨兵、球队/合同各身份关联。当前 season_stats_decoder 使用 7-bit season_code 加 1900，表达上限为 2027；历史遍历固定 20 次。这是源码可见的候选边界，**不能由它推出 2030–31/2035–36 已可正确解码**。概念模型不设 2027/20 季上限，native 值不明时保持 UNKNOWN。

这些是证据缺口而非要求 Human 重新决定独立存档规则。物理文件数、索引、存储规模和事务设计留给 WORLD-DATA-SCHEMA-01；任何改变“不分叉/不继承/游戏权威”的新产品决定必须回到 Human。
