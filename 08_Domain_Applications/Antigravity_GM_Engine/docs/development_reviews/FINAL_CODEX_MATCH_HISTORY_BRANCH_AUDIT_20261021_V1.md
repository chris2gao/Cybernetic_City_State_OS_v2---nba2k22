# FINAL-CODEX 比赛历史候选分支独立技术审核 V1

完成日期：2026-10-22；原任务编号：FINAL-CODEX-MATCH-HISTORY-BRANCH-REVIEW-V1。负责者：Codex。状态：`FINAL_CODEX_AUDIT_COMPLETED_PENDING_PLAYER_REVIEW` / `TASK_CLOSED`。

**结论：目前不建议合并。** 有可复用的五层关系模型、查询展示和统计计算候选；原生结构认证、身份、事务、失败完整性与查询隔离均有阻断。应在另行授权后选择性适配，不应按落后提交数全部重写，也不能直接迁入生产库。

## 1. 固定版本与证据范围

| 对象 | 固定版本 / 核验结果 |
|---|---|
| 原审计 main 基准 | `0eaf44f4ff06e7f2cf3c9d078b8f4b064fd2e1f5` |
| 候选实现 | `b4e17e1419b1cf9105f0a68dba7719e4d407104b` |
| 恢复任务指定封存提交 | `4b995e70e20659ce7d6198da16bde21b8a606001`；父提交为上述候选，`git diff --name-status b4e17e1 4b995e7` 为空 |
| merge-base | `d94959bee1416fb7271a703419fc05af72b8814d` |
| 与原审计基准关系 | main 独有384个提交，候选实现独有1个；加封存空提交后分支独有2个。该计数只描述固定基准 |
| 实现差异 | 8文件、1994行新增；本轮未合并、rebase或覆盖任何分支 |

以下行号指候选实现 `b4e17e1`，封存提交代码相同；当前架构对比指原审计 main。2026-10-21曾运行的4项测试证据与2026-10-22静态复核分开记录。未打开游戏进程，也未执行 Reader、Capture CLI 或其 `--dry-run`。

`dev/native-io-exploration@227b3acc60be03b49c89fb0fbac13d2a8182ce02` 属 `POST_BASELINE_NATIVE_DISCOVERY_PENDING_SEPARATE_REVIEW`。本报告不审收它的 ROSTERDATA / WAIVED_SALARY 新成果，不用它追认此候选结构。

## 2. 八个文件逐项复用判定

| 文件 | 判定 | 可复用部分 / 必须处理部分 |
|---|---|---|
| `database/match_history_schema.sql` | `REUSE_WITH_ADAPTATION` | 五层关系和按日期/球队/球员的索引有用；需映射正式存档代际、批次、来源和保留规则，避免 REPLACE 删除子记录 |
| `database/schema.sql` | `DO_NOT_INTEGRATE_YET` | 末尾173行重复嵌入比赛DDL；不能直接覆盖当前 main schema，不能在本轮建表或迁移 |
| `src/match_history_reader.py` | `REQUIRES_NATIVE_VALIDATION` | 日期、赛程、StatLine解码候选可保留；结构、位域、身份、边界、终局语义尚无本任务可接受的实机回执。`save_match_data_to_db` 的事务设计另需重做 |
| `src/auto_pipeline_ingest.py` | `REDESIGN_REQUIRED` | 新增15行挂接依赖旧流水线；吞异常继续、无覆盖清单、外层事务被提交，须重新适配现有 staged full_verified_v1 |
| `scripts/capture_match_history.py` | `DO_NOT_INTEGRATE_YET` | 参数与展示可参考；独立直写、默认池、存档解析副作用、缺生命周期租约，不满足当前生产入口契约 |
| `scripts/query_match_history.py` | `REUSE_WITH_ADAPTATION` | 日期/单场/球队/球员展示与白名单排序可复用；数据库解析与连接必须替换为封存快照M0入口，修正跨季聚合及歧义选择 |
| `tests/test_match_history.py` | `REUSE_WITH_ADAPTATION` | 四项合成回归可保留，但命名中的 atomic 不构成失败原子性证明；不能替代真实样本及当前架构兼容验证 |
| `docs/41_MATCH_HISTORY_AND_BOXSCORE_ECOSYSTEM.md` | `DO_NOT_INTEGRATE_YET` | 可复用业务目录；“100%实机”“全自动原子入库”“零崩溃风险”“100赛季”等结论缺证，偏移与公式需纠正 |

没有文件被判为可直接获准合并；这不否认其中通用SQL/格式化/公式代码的复用价值。

## 3. 原生布局认证表

认证等级按字段分别成立：`STATIC_CANDIDATE` 为源码候选；`DOCUMENTED_ONLY` 为仅文档断言；`PRIOR_RUNTIME_EVIDENCE` 要有历史运行回执；`REAL_CAPTURE_VERIFIED` 要有实际同档同批采集；`UNVERIFIED` 表示语义或身份未证。本次没有任何比赛历史字段达到后两种运行/采集等级。

| 字段/对象 | 源码或文档依据 | 本次状态与问题 |
|---|---|---|
| SEASON根槽 RVA `0x632B4B8` | reader常量、`get_season_pointer`约145行；文档§2.1 | `STATIC_CANDIDATE`；仅解引用模块基址+RVA并检查低地址，无当前build签名、类型大小或运行回执。它是RVA，并非固定绝对地址；ASLR本身不是否定依据 |
| 根大小3,526,944字节 | 文档§2.1 | `DOCUMENTED_ONLY`；Reader未用该大小认证对象 |
| Date、Period、Current/NextGameIndex | `capture_season_match_data`约161–164行 | `STATIC_CANDIDATE`；代码在根+0/+4、+28/+32取值。文档把CurrentGameIndex写在+0x28，与Schedule起点+40混淆，不能据文档改代码 |
| Schedule起点、数量、容量 | 根+40；数量从Schedule+104520；容量上限1742，最小接受100 | `STATIC_CANDIDATE`；文档称容量1232并把数量偏移混成根偏移。1742×60=104520说明代码内部边界关系，但不认证真实容量；短赛季/特殊阶段可能被错误拒绝 |
| StatBank偏移、长度、行容量 | `STATBANK_OFFSET=112308`；文档§2.1称`0x1B6AC (112308)` | 偏移`STATIC_CANDIDATE`、长度/容量`DOCUMENTED_ONLY`。确定性算术：`0x1B6AC=112300`，`112308=0x1B6B4`，相差8字节；不能猜选哪一个正确。文档1,087,012字节/45,292行也未由Reader验证 |
| SEASON_GAME60字节 | date0、played4、GameID8、主客ID12/14、Box20..43、节比分44..51、OT52/53、flags56 | `STATIC_CANDIDATE`；ID范围、有效赛程与真实记录长度未由当前PC22样本认证 |
| BOXSCORE24字节 | StatLinesIndex:uint16；主客球员数各byte；w20两组possessions位域 | `STATIC_CANDIDATE`；无StatBank总长或索引+行数上界验证；团队篮板部分被计算但未纳入汇总 |
| Player StatLine24字节 | 6个uint32；PlayerID低16位，InUse bit16，Minutes7位，PlusMinus有符号8位；其余FG/FT/REB/AST等 | `STATIC_CANDIDATE`；合成布局自洽不能认证真实字段。对位防守字段亦无独立实机依据 |
| PlayerID与池 | `load_player_name_catalog`43行，raw[0x2F8:0x2FA]作dict键 | 字段位置有项目既有PLAYER布局背景；**关联正确性仍UNVERIFIED**。默认legacy池、同ID覆盖、同名clone和代际关系未约束，不能借已有池认证Box行身份 |
| 终局/模拟/3D/SimCast/季后赛 | flags status bits11..12、sim bit18、period bits6..8 | `UNVERIFIED`语义；只能说源码这样解释。无真实不同模式/阶段样本。WasSimulated=0不能直接称3D实打 |

日期位域可确定性解码给定字节，但玩家提供的season_id、未知枚举默认REGULAR、无played_date时退回计划日期，都不能提升为真实游戏当前时间或实际比赛阶段。

## 4. P0/P1问题与实际影响

| ID / 等级 | 精确代码位置 | 确认的问题 / 影响 |
|---|---|---|
| MH-01 P0 | reader61–67 `ensure_match_history_schema` | `executescript()`会提交已有待决事务，函数又无条件commit。`save_match_data_to_db(conn=外部连接)`仍调用它，破坏调用者控制事务的承诺；后续异常无法回滚已提交的外层工作 |
| MH-02 P0 | pipeline新增match段 `except Exception`，位于原联赛一致性检查前 | 抓取/落库失败打印后继续，原manifest/audit没有match必需来源状态。可形成“旧来源成功、match缺失/部分写入”却整体成功的批次；这与将match列为必需来源后的full_verified_v1不兼容 |
| MH-03 P0 | reader game_uid生成；schema PK/FK | `{season_id}_G{game_id}`无save_instance/generation/batch/checkpoint。独立物理库可防部分跨档冲突，但同一档恢复分叉/重建代际仍可能覆盖；还不能保留多次观察的来源版本 |
| MH-04 P0 | query57 `resolve_db_path`；save_context101/154 | 指定路径不存在可退回默认或测试库；save解析会create/open/init数据库。SQLite常规连接不是mode=ro。既有具体save也可能退回legacy/test，存在跨档或合成数据混入风险 |
| MH-05 P0 | reader187–207 | `status==2 OR was_sim==1`可把“非终局但模拟标记为1”当完赛；真实标记组合尚未取证。未完赛行随后continue，只留日计数，不能提供完整未来赛程 |
| MH-06 P0 | reader229–277 | `stat_idx`、num_h+num_a没有容量/索引边界；InUse解出后不用。无GameID唯一性、TeamID有效目录、球员双队重复/身份有效性核验，错误偏移可能产生貌似合理事实 |
| MH-07 P1 | reader531/552/591，schema的ON DELETE CASCADE | 对比赛INSERT OR REPLACE会先删除旧父记录并级联删除旧Box；重建不完整时可能丢旧子行，且无历史版本。相同完整fixture两次写入通过不证明该问题不存在 |
| MH-08 P1 | reader score/winner与统计汇总段 | 无FGM≤FGA、3PM≤FGM、FTM≤FTA、主客比分/球员PTS汇总等一致性核对；0比0或平分也可能被选出主队胜者。未知回合强制max(1.0)把缺失转成伪有效分母 |
| MH-09 P1 | reader364–428 `build_team_row`/USG | DRTG用对手得分除本队poss；若两队回合不同，应明确采用对手或经定义的共同口径。Pace固定48与每OT5分钟，USG固定240+25OT；实际节长、Normalize及原生分钟口径未证明 |
| MH-10 P1 | query球队/球员/standings/leader函数 | 多个查询不限定season；同名候选最多5条后直接取首条；team统计跨季混算；limit可负且部分先fetchall再截断，无M0输出预算/来源绑定 |
| MH-11 P1 | capture CLI入口与`--dry-run`路径 | dry-run仍构造Reader读取进程；未接ACTIVE save确认/代际租约，默认球员池未跟目标save绑定，独立直写不经staged安装、sanitize、审计或封存 |
| MH-12 P1 | 文档§2、§3、§6；reader输出DTO | 原始字节与衍生指标未分证据层，公式未逐字段记录版本/分母。单个布尔模式不能认证QuickSim/SimCast/3D；未知阶段默认值掩盖缺口 |

所有风险均为静态结论或显式条件推论，没有声称已在生产造成事故。未修复任何源码。零分母并非普遍未防护：代码对多项比率已有条件判断；问题在于未知值、口径、校验和来源标识，不能照搬初稿的“分母溢出”断言。

## 5. 与DEV14/M0正式架构的兼容边界

当前main `gm_state_io.capture_files.install`、lifecycle、capture_bridge 已实现独立save目录、save_instance/generation、完整文件暂存安装日志及同批绑定；应复用，不另建审批中心。`auto_pipeline_ingest.py`在暂存双库sanitize后安装。候选无法通过复制15行挂钩继承这些保证。

未来最小完整性方案应由另行工程任务决定：已声明为必需的match来源失败则该批不发布为完整；可选来源明确NOT_OBSERVED及原因，不能冒充必需来源完成。必须区分无比赛/未完赛、来源不可用、解码不可信、存储失败；不得拿上批数据补成本批、不得为了match单独产生混合时点生产批。

审计的有效封存快照和active库均无五张match表。该结论限于已检查的两套本地库与指定批次，不推广为“所有历史数据库都不存在”。M0的DEFAULTS没有match实体；不存在的domain视图返回不可用并保留来源缺失，不应该直接调用候选CLI绕过。

最新已发布批次为 `2021-2022_M02_DEC12_FULL_20261018_bee1cb016256_e94b241a_TS2`。其game_date为USER_CONFIRMED，缺save_instance/generation和potential_v1。当前QuerySession可作owner只读审计，但`production_gm_eligible=false`，GM入口拒绝旧未脱敏批次。旧档保持原封存；未来新采集需既有GM_SANITIZED规则，比赛历史关联不得借全局池泄露隐藏Potential或把脱敏字节反注入游戏。

## 6. 四项既有合成测试：证据与局限

2026-10-21在临时目录仅复制8个必要文件，未复制memory模块、数据库、游戏执行器或上传脚本，禁用pytest自动插件和缓存。结果：**4 passed in 0.08s，退出0**。2026-10-22确认封存提交与测试输入代码无差异，沿用此证据，未反复重跑。可复现入口见本次提交的审计脚本`--run-existing-tests`选项。

| 现有测试 | 实际证明 | 未证明 |
|---|---|---|
| `test_decode_schedule_date` | 构造packed整数经生产日期decoder得到预期年月日 | 游戏原生位域/年份循环/非法日期 |
| `test_boxscore_statline_unpacking` | 测试内自行pack/unpack与算式的示例 | 没有调用Reader的StatLine解码路径，不能说Reader全字段已测 |
| `test_team_advanced_metrics_formulas` | 测试内固定公式算术 | 没有调用Reader闭包，未验证两队回合不等、节长、OT或Normalize口径 |
| `test_database_schema_and_atomic_upsert` | 内存SQLite建表、完整单场fixture两次写入后的行数/值及3项查询不抛错 | 未注入失败；未断言外层事务、回滚、历史保留或跨档隔离；“atomic”名字不构成证明 |

未来最小回归需求随修复包授权：外部事务失败与REPLACE历史保留；不存在目标save禁止fallback；同GameID不同generation；非法索引/ID/InUse与非终局sim组合；两队比分与Box不一致；5/12分钟、OT、Normalize。真实结构样本对照另为原生证据任务。此处只列需求，未新增或运行这些用例。

## 7. DEV28归属及最小后续路径

F01–F03是未合并候选；F04没有ShotChart/坐标/事件实现；F05–F06已存在赛季累计来源，不能由Box候选替代或反推逐场；F31模式仍未知，F32日期/阶段依赖原生核对，F37/F38/F39分别涉及存档、保留和正式批次。继承D06-G01～G05，并关联G14的跨季保留。

建议D28-3**优先评估复用该分支候选**，按以下分阶段接收，而不是批准现状合并：

1. 保存候选解码/SQL/查询展示和固定输入证据；标明STATIC_CANDIDATE。
2. 另批确定性修复：外部事务所有权、禁fallback、明确代际/批次、终局/边界检查和派生口径；继续隔离生产。
3. 未来获批原生取证：以PC22真实页面及完整列/子对象为边界，核对root/Schedule/StatBank、同场双边Box、身份和各比赛模式；不能只验证“GM想用的几列”。
4. 验证合格后，另批接入现有full_verified_v1暂存/失败/manifest/sanitize/封存链；不创建独立混合时点来源。
5. 接M0有界查询和真实历史留存验证，明确无法获取的Shot/跨季事实UNKNOWN；游戏Save/Reload须单独许可。

这五步均未在本轮实施。审核任务结束；合并阻断已明确，未知证据不保留为后台等待。
