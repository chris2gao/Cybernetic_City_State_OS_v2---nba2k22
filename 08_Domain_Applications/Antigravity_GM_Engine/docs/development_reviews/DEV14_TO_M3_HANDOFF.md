# DEV14 → M3 实现交接

**窗口②接收回执，2026-10-20：** 玩家已将PR #5合入main：最终开发`f68d75d`、合并`570419a`。M3在原PR #4以`82083b5`整合，原生查询和M3分析查询同时保留；随后完成M3-T消费层与本轮8项最小验收，见[M3-T报告](M3_T_IMPLEMENTATION_AND_ACCEPTANCE.md)。PR #4已按玩家批准合入main（504a4c0）、正式本地工作区已同步，V4未启用。发现的完整Registry元数据脱敏误判作为底层待办记录，未擅自修改窗口①引擎。下文“未合并”等为窗口①当时交付的历史记录。

2026-10-20。负责窗口①，PR [#5](https://github.com/chris2gao/nba2k22-gm-engine/pull/5)，分支`codex/dev14-state-io`；**未合并，不是main部署**。最新可执行代码提交：[b1452b0da7cc3dff0de3e14e46deaa7791482725](https://github.com/chris2gao/nba2k22-gm-engine/commit/b1452b0da7cc3dff0de3e14e46deaa7791482725)。本交接和开发规范V2随后为文档提交；最终PR head见[PR提交列表](https://github.com/chris2gao/nba2k22-gm-engine/pull/5/commits)及交付回执。它们不再改变该实现。

## 玩家最新简化要求（优先）

一个save_id对应`database/saves/<save_id>/`，其中联盟库、完整球员池、控制库各自独立，所有档复用同一schema；不是在一个共享表里靠复杂逻辑分档。active指针只选工作目录，不替玩家加载游戏。现有基本ID/原值核对保留，不再扩展隔离研发；需要时可物理复制仓库及数据库。

玩家明确接受操作者信任，不要求反伪装/权限签发系统。聊天中的具体批准继续有效，Codex可引用批准、携完整tuple和显式写入开关运行；review是可选工具，不要求玩家操作终端。MANUAL_OPERATOR_TRUST_ONLY是人工信任声明，不是真人身份认证；文件/approved=true本身不能批准提案。

**任何扩展设计和更多测试必须先询问玩家并等待确认。** 已完成范围按现有证据交付，不自行追加。详见[开发规范V2](../DEVELOPMENT_BOUNDARIES_AND_VALIDATION_POLICY.md)。

## 版本与底层入口

| 合同 | 本次实际版本/入口 |
| --- | --- |
| 引擎/NativeSession适配器包 | `DEV14_V1.2_H_DEV15`，`src/gm_state_io/__init__.py`；NativeSession无独立版本号，锁定此代码commit和registry_version |
| 字段目录 | `Registry.version`为当前字段布局/权限的SHA256指纹；profile与config/state_io_native来源沿用，新增rotation.intangibles |
| 控制库 | `database/gm_control_schema.sql`，user_version=1；approval_records.binding_json/journal注明人工信任，完整审批tuple不变 |
| 观察表 | state_io_captures/state_io_objects/observed_setting_values沿用；新增两库player_potential_masks(snapshot_id,policy_json)，mask_version=potential_v1 |
| M0 | `gm_sqlite_m0_v1` API兼容，新增rotation/native_objects/native_books和require_gm_sanitized()；静态副本只读，原旧批不改 |
| 原生值编码 | 现有coach_codec/defense_codec/native codecs；Intangibles复用config.raw_to_rating/rating_to_raw，25–99→原生0–222，非直接写评分数字 |
| CLI | scripts/gm_state_io.py：stage/validate/preflight/apply/rollback/receipt/reconcile及存档生命周期；scripts/gm_data_query.py：受限查询 |

## 读取：给M3的安全DTO

M3数据适配器先创建QuerySession，然后**调用`session.require_gm_sanitized()`**，再用原来的query接口。旧M02对CodeX的静态审计仍可读，GM消费拒绝UNMASKED_HISTORICAL_BATCH_EXCLUDED_FROM_GM；不可通过旧公开资料恢复真潜力。source_binding也披露Potential可见性和GM资格。

```powershell
python -B scripts/gm_data_query.py rotation team --career A --batch <batch> --team CHA --role WEB_GM
python -B scripts/gm_data_query.py native_objects search --career A --batch <batch> --team CHA --target-kind COACH_DEFAULT --role WEB_GM
python -B scripts/gm_data_query.py native_books search --career A --batch <batch> --role WEB_GM --limit 20
python -B scripts/gm_state_io.py registry --domain tactics --limit 20
```

值域查询返回object_key/field_key/value/source_status/registry_version及实例/代次；native_objects给selector/native_identity/field_keys，不给raw、地址或SQL写接口；native_books给已加载name/enum_id/index/unique_id。仍默认20、最多50、固定批次游标。只用有来源的对象；AUTO值不等于缺失，UNKNOWN不补值。

## 稀疏意图、批准与结果

普通意图不写前像/地址/approved字段，由底层取同批源展开：

```json
{"decision_id":"M3_EXAMPLE","version":1,"reason":"非批准示例","changes":[{"action_id":"A1","object_key":"同批查询返回的对象键","field_key":"rotation.intangibles","target_value":65,"reason":"轮换优先级假设"}]}
```

普通operation可省略，默认为GM_STATE_CHANGE。stage只写本档Desired，输出change_set_id/digest/动作数和diff；validate离线，preflight整批RO，均不批准。apply需exact审批JSON（save_id/save_instance_id/generation_id/source_batch_id/decision_id/version/action_ids/digest）、真实玩家批准引用、显式approve-game-writes、载档tuple及editors-closed。源、人物、前值漂移拒绝；不沿用旧指针。review是可选前台替代。完整命令见[DEV14手册](../DEV14_STATE_IO_RUNBOOK.md)。

仅新档初绑或确认换帅后的绑定允许下面的附加合同，且这一批只含一个coach.PlaybookID变更：

```json
{"operation":"TEAM_BOOK_REBIND","decision_id":"REBIND_EXAMPLE","version":1,"reason":"恢复本队书，示例未批准","event":{"kind":"CONFIRMED_COACH_CHANGE","reference":"玩家确认的换帅记录","team_id":31,"current_coach_identity":{"来自native_objects.native_identity":"完整原对象"}},"changes":[{"action_id":"B1","object_key":"现任主教练对象键","field_key":"coach.PlaybookID","target_value":17,"reason":"此数字必须来自本队同名已加载书，示例值不可执行"}]}
```

event.kind只可INITIAL_SAVE或CONFIRMED_COACH_CHANGE。team_id/current_coach_identity须等于观察对象；按当前加载团队名和书name/enum_id/index/unique_id匹配，目标错误或歧义单动作阻断。绑定后**重新取源**、另提案和批准编辑本队68槽；不能带切书前旧槽前像。没有克隆/新建30本书或共享冲突研究。每队每季仅休赛期一次主动换帅是M3业务门禁，**本底层没有实现员工签约或该经营计数器**。

成功为MEMORY_VERIFIED，回执/journal含完整绑定、逐块readback、approval_trust、是否保存=false；Intangibles另记intangible_before/after及来源。失败仅条件恢复仍为本次after的字节，部分失败留原进程锁。receipt只读，reconcile比较后续批次，绝不自动采集/回写/推进比赛。

## 实际读写清单

| 可使用 | 当前限制 |
| --- | --- |
| 19默认字段的既有原生能力 | 普通GM只写其中不含PlaybookID的18项；PlaybookID仅TEAM_BOOK_REBIND；5 Sim始终只读；Tempo语义UNKNOWN |
| 18个人防守字段 | 双方native ID唯一定位；缺观察对象或身份不符明确拒绝，不回退整体 |
| 18整体防守读取 | 普通写入明确OVERALL_DEFENSE_GM_DISABLED_USE_PERSONAL |
| 本队书68槽 | owner须为本队、同名书身份匹配；CRC只取本批加载目录，未知实际战术行为仍UNKNOWN |
| 四PlayTypes/Initiator、48具名倾向 | 沿用原生字段/codec；51未命名倾向只读，不猜行为 |
| 球队6项、球员5项训练 | 已知当前布局；缺根/身份则NOT_OBSERVED，导师关系尚未接入 |
| rotation.intangibles | 所有30队可提案，25–99，唯一PLAYER 0x440；不开放其他Ability/Potential/Badge/合同写入，不锁分钟 |
| 4项双侧Gameplay、50项世界设置 | 原生能力沿用，不等于这些设置已获全局批准 |

## Potential与新秀注入

full_verified_v1在RO采集/初步检查之后，在暂存双库自动sanitize_player_potential，**早于正式安装、哈希、备份、M0、JSON与发布**。覆盖pool结构化/JSON/raw、名单详情和全部已知DEV14 PLAYER raw镜像，仅0x441→1。覆盖数与排除Potential的字节指纹校验；Staff/Intangibles/合同/身份/新秀0x70不变。未知别名或PLAYER镜像失败关闭。幂等复查不重复改库。

1是MASKED/NOT_GAME_OBSERVED占位，不参与球探、成长或定价。新发布副本的历史行也净化，但旧封存M02、Git历史/Release不改；旧原始公开内容未删除，不能作为GM绕过路径。无净化标记旧包重发被阻止。

`query_historical_draft_class(...,for_native_injection=True)`和`preflight_native_rookie_source`拒绝GM_SANITIZED/mask_version，错误SANITIZED_PLAYER_POOL_NOT_NATIVE_INJECTION_SOURCE。独立原生DTO预检保留原Potential，不授予注入执行。**实际私有来源采集、权限隔离存储、历史注入执行器未实现**，本轮没有为此开新工程。详见[DEV15](../DEV15_ROTATION_AND_POTENTIAL_RUNBOOK.md)、[GM知识](../../web_gm/manuals/GM_POTENTIAL_FOG_AND_ROTATION_BIAS.md)。

## 本轮验证及证据边界

- 47项定向集成检查通过：4项既有DEV14关键路径、8项H/Book/Intangibles、6项Potential、5项教练导出、24项M0。日志`_exports/dev14_closeout_tests.log`，结果`_exports/dev14_closeout_results.json`。全部合成SQLite/内存后端；未开游戏。
- 玩家简化审批信任后仅跑3项直接相关检查通过（与上项有重叠，不算新增50个独立案例）：缺具体批准拒绝、完整聊天批准引用的CLI合成执行、可选review作用域及旧代次拒绝。没有因此重跑47项。
- 27个改动Python文件AST、2个配置JSON语法检查通过，未导入游戏；git diff --check通过。旧M02只读打开30队/教练，新增GM遮蔽访问检查拒绝，未改变原副本/发布包。原A/B/C/D的119项记录仅为历史，不冒称本次重跑。
- A/B同M02/同player ID交换pool，stage/activate/capture前置拒绝；同批正确pool恢复正常。暂存替换保留三库来源，失败恢复完整旧字节，中断显式恢复。合成Intangibles写回/条件恢复仅0x440，Potential邻字节不变；无实机效果或存盘结论。

## PR #4兼容审阅与接力

只读核对PR #4 head `fa62fb2d371438cd9d8062e1fa842e7c8eede4ad`的analysis_inputs.py与analysis_packet.py，没有合入/实施M3。QuerySession构造/query/close和普通DTO约定仍在，但**并非直接互换**：PR#4独有team_stats投影及CLI `team stats`必须保留；PR#5新增rotation/native_objects/native_books/遮蔽检查也必须保留。M3 loader先require_gm_sanitized；decoded_attributes中的Potential仍标MASKED，不能拿1做评估。

实际重叠路径：`src/gm_data_access/query.py`、`scripts/gm_data_query.py`、`AGENTS.md`、docs/24、32、33、34、36；PR#4还扩展`tests/test_gm_data_access.py`，整合时保留它的覆盖，不能用旧版本整文件覆盖。本PR没有改动analysis_inputs/analysis_packet或M3经营器。

推荐用户审阅并单独决定PR#5是否合并；窗口②接准确实现commit，再将获准main整合至PR#4，保留上述API并做M3工作。**任何新增设计或更多测试先问玩家**；本交接不自动授权P1–P5重跑或扩展。PR#4合并、GM V4、下一次生产采集/发布和正式游戏写入均另由玩家触发。
