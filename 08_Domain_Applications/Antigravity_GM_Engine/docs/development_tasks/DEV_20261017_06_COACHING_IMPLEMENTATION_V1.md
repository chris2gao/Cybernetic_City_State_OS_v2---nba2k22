# DEV-20261017-06 | NBA2K22 PC 30队教练战术与对手 Gameplan 受控执行器实施任务 V1

- **状态：AUTHORIZED_FOR_ENGINEERING_DEVELOPMENT_ONLY / IMPLEMENTATION_NOT_VERIFIED / FORMAL_GAME_WRITES_NOT_APPROVED**
- 2026-10-17，Web GPT DEVELOPMENT 任务交接给 Codex DEVELOPMENT。玩家明确表示「可以开发」，后续**一个游戏月由玩家正常推进并触发数据采集，才评价比赛效果**。
- 关联：[只读调研摘要（玩家转交）](../development_reviews/DEV_20261017_05_COACHING_READONLY_HANDOFF.md)；[上一轮调研任务书V2](DEV_20261017_05_COACHING_MEMORY_DISCOVERY_V1.md)；`AGENTS.md`、`config/gameplay_policy.json`、`docs/33_DEVELOPMENT_BASELINE_PROMPT.md`、`docs/34_BASELINE_CURRENT_STATE.md`、`docs/36_EXECUTION_BASELINE_PROMPT.md`。
- 游戏：NBA2K22 Windows PC/终极联盟，历史起点2021–22；`policy_id=PLAYER_RULES_20261017_V3`。禁止一般球员能力、潜力、徽章、倾向、性格写入，历史重力仅专项审批，MC故事继续禁用。禁止修改联盟级 Simulation Sliders 为某队作弊。
- **重大证据边界**：Codex先前调查的原生地址、字段名、枚举与结构由玩家文字转交，**未随本窗口提交原生反编译证据/调查脚本/实时读档日志**，因此本任务视作研发定位线索。Codex应在现用版本/进程复核并输出证据；**此前全部仅只读，不能将它当作经过正式游戏写回认证**。
- 本任务授权产品**代码编写、单元测试、以及隔离测试存档上的必要最小安全写入验证**。不授权改变玩家正式局30队战术、启动GM决策、自动采集、上传事实库、模拟比赛、推进游戏时间或调用其他模型。正式应用仍须网页GM具体版本提案→玩家批准→Codex执行基线独立执行。

## 1. 本轮实际交付目标与范围梯度

最小完整可用核心为 **30队教练默认六项POE的只读快照、原生合法枚举映射、离线提案校验、受控写入及回滚**。随后按风险依次完成：五项独立 Sim 数值、教练滑块/八种体系、已加载战术本合法选择、对手Gameplan只读与条件启用/条件执行、防守18项设置、轮换。

**优先级 P0（必须实现）**
- 不再允许旧`TEAM+0xEB2`等作为教练POE写入。禁用/迁移所有历史调用路径，尤其`src/bootstrap_new_game.py`第4阶段调用`strat.set_team_strategy`，不得继续用旧签名在初始化时写内存。保留不相关球票功能，原全局初始化不应在未批准下自动写入。
- 新`COACHDATA+0x13C`六项32-bit共享bitfield读取、合法枚举、按mask写回；PID变化重校准、教练与球队身份双向核验。至少两支球队与进程重启分别验证。
- 离线GM`TACTIC_CHANGE`提案/验证与本地独立受控执行契约：严格批准、team/coach/save/source/old_value/target_value白名单、持久备份、回读、幂等、错误报告；未批准时无法取得写权限。
- 输出30队初始`coaching_snapshot`与变更执行回执格式，便于网页GM下一月对战术效果追踪；不强制Codex在开发期做赛果对照。

**优先级 P1（核心确认后实施，缺精确bit不猜写）**
- `SimPace`、`SimPress`、`SimHelpDef`、`SimOffReb`、`SimDefReb`（教练`+0xF4`附近共享位域），**先补齐真实位偏移、width、合法数值，才能实现写入**。
- `BenchDepth(+0xDE)`、`RunPlayTendency(+0xE0)`、`ZoneUsage(+0xE2)`、`BenchUtilization(+0x138)`；`Tempo/HelpDefense`在`+0x148`共享位域：先用原生证据确认宽度/数值单位和位布局。
- `PreferredSystem/ActiveSystem`八种原生体系及教练角色、真实活动主教练校验；**不改所谓体系熟练度或球员属性**。

**优先级 P2（独立提交，缺安全证据只读/阻断）**
- 教练默认`PlaybookID`与Gameplan`PlaybookId`，在**当前已加载的**战术本ID目录内选择。Codex原报告本次加载84本（`0x168`字节/本、68个CRC槽），数量随名单变化，不许硬编码84为上限。优先只做选择合法战术本，不开展共享战术本结构的直接编辑；涉及68槽内容的自定义编辑须证明合法来源/共享引用隔离，否则保持只读。
- 对手`FRANCHISE_GAMEPLAN_MANAGER`、`GAMEPLAN`：支持29个NBA对手记录的**只读扫描、排序及方案预设**；发现`IsInUse=0`可能是未启用，**禁止只改POE就宣称生效，禁止猜测将IsInUse置1**。只有确认原生UI启用/取消/回退的状态机与关联字段并在隔离局完成最小验证后，才为该子模块开启受控写入；否则`MATCHUP_EXECUTION_BLOCKED_NOT_ACTIVATED`。
- 8-byte/18项防守结构：`ScreenDefenseOnBall`、`ScreenDefenseHedge`不同；`OnBallPressure`合法AUTO/GAP/MODERATE/TIGHT/SMOTHER。逐字段存储真实掩码和枚举，未齐全则保留只读/UNVERIFIED。
- 轮换PlayerId/RotationSpot/PlayingTime以及高级轮换：身份/名单连续性、分钟数及轮换约束不明确则只读，不允许越界或跨赛季引用旧人物slot。

P1/P2功能可分阶段交付，**不要因少数高难子功能阻塞已完成P0/P1的正式代码提交**；只把经过安全验证的字段标 `EXECUTOR_READY`。各模块的普通快速模拟效果在玩家运行一个游戏月前一律标`SIM_EFFECT_PENDING_PLAYER_MONTH`，即使字段读写成功也不宣称增加胜率。

## 2. 原生位置与定位规则：必读纠错

### 2.1 教练默认POE是共用32位块

`COACHDATA + 0x13C`，按**little-endian unsigned32**读取（需当前游戏版本复核）。从LSB起：

| 字段原生名 | bitStart | width | 唯一允许原始枚举 |
| --- | ---: | ---: | --- |
| `POEDefense` | 0 | 5 | `0,13,14,15` |
| `POEDefense2` | 5 | 5 | `0,16,17,18` |
| `POEDefense3` | 10 | 5 | `0,19,20,21` |
| `POEOffense` | 15 | 5 | `0,1,2,3,4,5,6` |
| `POEOffense2` | 20 | 5 | `0,7,8,9` |
| `POEOffense3` | 25 | 5 | `0,10,11,12` |

0为`NO_PREFERENCE`。仅原生字段/枚举表已证实的项目采用精准英文标签，如`GET_SHOOTERS_OPEN`、`PICK_AND_ROLL_OFFENSE`、`PATIENT_OFFENSE`、`PROTECT_PAINT`、`PLAY_PHYSICAL`、`RUN_IN_TRANSITION`；**不得臆造具体数值到名称的完整对应**，由Codex现场解析补齐字段目录。

编码必须使用**只改目标5bit的Read→Validate→Mask→Write→Readback**，例如：

```python
def with_enum_field(old_u32: int, shift: int, new_enum: int, allowed: frozenset[int]) -> int:
    assert shift in (0, 5, 10, 15, 20, 25)
    if type(new_enum) is not int or new_enum not in allowed:
        raise ValueError("INVALID_NATIVE_COACHING_ENUM")
    mask = 0x1f << shift
    return (old_u32 & ~mask) | (new_enum << shift)
```

实际执行**每次32位块先以安全API读取确切4 bytes**，不能采用`read_uint32`在失败时返回0的便捷接口，不能用`write_uint32`自动掩码/截断；禁止改bits30–31、相邻5bit字段、未知标志。批量修改同一块应从统一前值合并所有获批字段生成**一次完整4byte写入**，避免逐5bit多次读写导致相邻值覆盖。执行前复核原始32bit与方案记录的old block完全一致；不一致停止并重新形成提案，**不自动覆盖游戏/AI刚刚修改的数据**。写后逐字段和未授权位值检查。旧地址`TEAM+0xEB2`禁写。

### 2.2 Sim 位域 ≠ 六项POE

`SimPace`五档，`SimPress`/`SimHelpDef`/`SimOffReb`/`SimDefReb`各三档，在教练`+0xF4`附近独立共享bitfield。需要Codex补`relative_address + start_bit + bit_width + 真实enum raw编码 + 当前归属对象`才允许写；不能假设`+0xF4`整块仅这些设置，也不能用六项POE枚举写到这组字段。

`Tempo`和`HelpDefense`于`+0x148`的packed字段也类似；标注与`SimPace`不同。凡profile只有“附近”或偏移没有位域宽度，禁止生成生产setter。

### 2.3 单场对手方案 ≠ 默认POE

调查报告：`NBA2K22.exe+0x632B478`是原生访问链所关联的联盟根**定位线索**；在已解引用的联盟根结构`+0x19CFD0`起每队块步长`0x13E70`，必须**以内部team_id实际值匹配30支队伍**，不得TeamID当数组索引或固定把teams排序强绑定地址。Gameplan每队管理器容量35、记录`0x370`，实测29条有效对手，30队合计870条。在扫描中验证对手ID唯一、不是本队、有效对手集合符合本局，再输出记录。额外6容量槽可能为空/其他用途，不访问为有效方案。

Gameplan内六POE占`+0x17E..+0x183`六个位置，滑块`+0x184..+0x189`，PlaybookId/Freelance分别`+0x18A/+0x18B`；**记录结构与默认`COACHDATA+0x13C`的5bit packed字段不同，需另立`gameplan_codec`，必须先核验每字节/位含义**。

已观察到`IsInUse`全部=0：可能代表对手方案禁用、尚未触发或采用特殊约定。没有确认激活语义前，**仅只读/生成PROPOSED，不向它写值或修改IsInUse**。若未来玩家选择按29个对手分别施策，也必须证明游戏AI实际加载对应方案才能标`MATCHUP_EXECUTOR_READY`。

### 2.4 教练战术本、教练身份与球员身份

- 主教练`PlaybookID`和对手Gameplan`PlaybookId`不能混用；所有ID查当前进程真实加载书本表，名称/CRC/实际引用校验，不能以任意整数和84固定枚举集通过。
- 68个战术CRC槽可能在加载表中共享：未经验证的编辑会影响多队。V1禁止修改共享战术本内容；优先实现已有战术本的选择。
- 每次重启、教练解雇/换队、球队角色变化，必须重新解析教练/球队关联，重新校验当前对象。临时绝对地址如`0x7FF4E6C2304C`与`0x7FF4E6C23E0C`和此前PID 9960/992仅历史证据，**不进入任何生产常量、数据库主键或跨会话缓存**。
- 轮换PlayerId/临时slot亦是需二次核验的身份，不得单独持久化作未来写入键。

## 3. 工程切分与旧入口兼容修复

建议目录，Codex可据现有项目习惯调整，但层界必须一致：
- `config/coach_tactics_profile.json`：仅写真实复核的字段、对象定位、bit/bytes、原生合法取值、证据版本；不存PID或绝对地址。未确认字段明确标`UNVERIFIED_READ_ONLY`。
- `src/coach_locator.py`：只读定位联盟→球队（按ID遍历）→主教练对象→对应已加载战术本/对手manager；PID/身份校验。
- `src/coach_codec.py`：纯bit编码/解码、掩码、enum验证、相邻bit保护，可离线Python单测。
- `src/coaching_reader.py`：30队只读当前配置、对象/原生字段覆盖率、未验证范围；产生供GM读取的结构化只读JSON。
- `src/coaching_executor.py`：**独立于`gm_core`** 的受控执行器，不允许`gm_core`导入游戏写模块，默认dry-run；成功执行后回读与回滚回执。
- `src/gm_core/coaching.py`（或复用`tactics.py`）：仅离线审查、合规提案、实际已认证enum与来源字段检查；不持有GameMemory句柄。
- `scripts/coaching_snapshot.py`、`scripts/coaching_validate.py`、`scripts/coaching_execute.py` 可按Codex工程规范命名，但生产脚本必须有`--help`，默认只读。执行入口缺少玩家授权则绝不打开读写handle。

**高危旧入口治理**：
1. 查找所有`StrategyManager.set_team_strategy`和`STRATEGY_OFFSETS`与`0xEB2/0xEB3...`写操作的调用；包括`src/bootstrap_new_game.py`循环30队调用`set_team_strategy`、脚本、测试、其他模块。
2. 立即拒绝旧setter在任何路径执行（明确`LEGACY_TEAM_POE_OFFSETS_REVOKED`）或在确保用户明确使用新版字段意义且不误解原参数时采用新的名字/映射；**绝不能悄悄把旧off_pace/fastbreak_focus的旧数值映射到全新不同语义的原生SimPOE**。
3. 新局初始化时原旧战术模板跳过/报阻断并报告需要另行确定正确教练配置；票价功能与合法全局Sliders不受旧POE禁令波及。旧配置不自动写入新策略。防止批量初始化部分成功后误称30队战术已设置。
4. 更新历史文档`docs/13_...`最前方“旧TEAM POE偏移已撤销，严禁执行”的醒目告示，保留历史资料而不误导；更新`config/gm_policy.json`战术枚举为**新profile已验证字段**的引用或阻断，不能继续沿用旧`poe_on_ball`未经证实的数值开放执行。
5. 确保其他功能/数据采集路径不依赖旧伪POE含义；旧数据已有字段只作为历史观测保留并标注`LEGACY_UNVERIFIED`，不要改写已发布的源事实或给旧batch追认。

## 4. 受控执行接口、批准与回滚

### 4.1 提案样例（纯结构示例；不携带真实授权）
```json
{
  "decision_id": "GM-COACHING-2022-M01-R01",
  "version": 1,
  "career_id": "YOUR_SAVE_ID",
  "source_batch_id": "YOUR_FROZEN_BATCH",
  "game_season": "2021-2022",
  "game_date": null,
  "policy_id": "PLAYER_RULES_20261017_V3",
  "status": "PROPOSED",
  "action_id": "TACTIC-A001",
  "scope": "COACH_DEFAULT",
  "team_id": null,
  "verified_coach_identity": null,
  "opponent_team_id": null,
  "codec_version": "NATIVE_COACH_POE_V1",
  "changes": [
    {"field": "POEOffense", "before_raw": null, "after_raw": null}
  ],
  "expected_effect": "风格预设，模拟胜率尚未验证",
  "effect_status": "SIM_EFFECT_PENDING_PLAYER_MONTH",
  "execution_authorized": false
}
```
空值仅表示schema示例，不可当作可执行操作。真实方案必须绑定有证据的球队、主教练、游戏日期/来源批次、当前可读前值、合法枚举和版本；不同coach/对手与未知原值不予执行。用户在聊天中批准的具体动作作为**外部独立授权输入**，不能由提案JSON自填`approved:true`或`execution_authorized:true`自证。

### 4.2 预演和执行安全
- 只读/预演默认启用；开发阶段可提供隔离局最小技术写验证，正式入口必须由执行角色按玩家具体批准的`decision_id/version/action_ids`显式调用。未经批准和权限复核，连读写handle都不要申请。
- 对象比对：PID、模块版本、联盟save身份（若无法直接观测，以玩家确认+当前球队/主教练/名单指纹合验）、team_id/coach ID/对手ID、当前字段old raw及完整共享bit块原值。不存在、歧义、来源过时则fail closed。
- 同一个32bit共享块多个修改：先验证全部原值，构造新块一次写，再读回整块及各字段；不触及未授权bit，包括30–31保留位。读取失败为UNKNOWN，不以0替代。
- 对多对象方案：先预验全套，再按批准动作有序执行；出错停写，**仅当目标当前值仍与本执行器刚写目标一致才进行安全回滚**，失败记录`PARTIAL_UNRECOVERED`，不清除AI或其他并发修改。
- 运行前保存具体受影响字段/共享字节的`preimage`到受限本地执行日志，避免保存大量无关进程内存；记录命令、来源版本、回读证据，不在Git公开真实PID绝对地址。
- 幂等：按`career_id + decision_id + version + action_id`记录结果；重复已完成版本返回已执行而非再写一次；新的GM方案必须有新版本/新快照/原值。
- 不能把“Windows WriteProcessMemory返回成功”当成“游戏界面/存档接受”；开发期需隔离测试存档验证菜单重开、存档退出重进、非目标字段完整性；模拟战绩效果留到玩家一个游戏月。
- **拒绝**：未批准、错存档/教练、失效PI​​D、非法枚举、缺已加载战术本、`IsInUse`不明、同名球员歧义、字段mask不明、旧地址路径及企图改联盟滑块/普通球员能力。

### 4.3 三种状态要分别报告
1. `LOCATED_READ_ONLY`：有证据能准确读取，但从未写入。
2. `TEST_SAVE_WRITE_VERIFIED`：在隔离测试存档可控写入、回读、恢复且已验证保存；尚未授权正式赛季经营使用。
3. `EXECUTOR_IMPLEMENTED_READY_FOR_PLAYER_APPROVAL`：受控生产接口及测试完成，玩家明确批准具体战术后才可用于正式局；**不是已经正式执行，更不是证明快速模拟有效**。

## 5. 数据发布与网页GM整合

- 30队源事实放到项目来源/SQLite与发布JSON中时须先由Codex经过只读审计的捕获和导出代码确定性生成，不允许开发文档手写来源数据/编造结果。`data_updated_at`、`uploaded_at`照现有源同步时戳语义，不能因方案文件更新刷新游戏采集时间。源目录登记只更新真实已采集和通过验证的新字段。
- GM离线接口必须能读取新合法枚举元数据、当前球队教练体系/六POE/Sim设置及readiness，发出`TACTIC_CHANGE`具体行动方案并继承`src/gm_core/decisions.py`的`execution_authorized:false`制度。不要把`config/gm_policy.json`以前待确认的战术政策当作玩家已确定风格或30队主观偏好。
- 一次性开发不运行正式30队GM会议，不代替GM决定每支球队目标风格。玩家后来在GM赛季窗口具体触发并审批30队哪些球队改变战术。
- 月度评价由玩家推进一个游戏月后再单独触发数据源采集、网页分析端计算：同存档同赛季累计`ΔW, ΔL, ΔG`，可验证累计总量先差再取新期间场均，记录具体战术生效时间及当月有无交易/球员离队。一个月观察不足以单凭战绩确认因果，有效状态`SIM_EFFECT_PENDING_PLAYER_MONTH`直至真实数据评估。
- `source_batch_id`、GM方案版本、具体已批准和已执行回执必须关联，否则标`TACTICAL_MONTH_EVALUATION_BLOCKED`，不要对未落地战术推断效果。

## 6. 必要最低测试（不执行批量模拟比赛）

### 纯Python单元测试/假内存
- 六字段按5bit依次编码/解码，每项所有合法枚举值双向一致；不合法非列表值拒绝(尤其1..31大多数非法)；bit30/31不变。共块多字段一起变更也不污染其他字段。
- 模拟共享`SimPace/SimPress`等尚未知mask字段保持写入阻断，等位域确认后再开放。
- 两队主教练块隔离、team_id不等于目录下标，30队没有重复主教练归属；人数不足、coach指针/岗位不匹配时拒绝。
- Gameplan容量35/29有效对手/870仅在本次样例，别硬编码逻辑上限；重复对手/自对手、IsInUse全0时必须禁写；未验证的对手模式回退禁写。
- Playbook当前加载表存在/不存在、名称+ID映射、68槽CRC只读、共享引用不被误改。
- 防守位域`ScreenDefenseOnBall != ScreenDefenseHedge`，不因名似合并；未知位域禁写。
- 默认只读、无批准请求写入计数0；非法/错教练/变化的前值/重启PID要阻断；合法测试模拟写入后检查未授权位仍完全保留。
- `bootstrap_new_game.py`通过`--approve-game-writes`触发旧策略writer的回归必须被阻断/改造，票价功能测试不应因此被误删。
- `src/gm_core`没有导入GameMemory、`write_* `或`strategy_manager`直接现场写入；仅准备、生成、验证方案。
- Git状态、测试命令、通过/失败、具体模块覆盖范围必须交报告；不要复用旧测试PASS当新版本证据。

### 隔离测试存档的最低技术验证
- 一次合法默认POE更改 → 读回→同一教练/球队在游戏UI中可见→保存退出重进仍一致→恢复原值；可再对另一支球队重复。无需多场模拟。
- 若写回返回成功但游戏菜单显示另一值、重启丢失、默认策略重新覆盖，标`WRITE_NOT_ACCEPTED_OR_NOT_PERSISTENT`，该字段保持production禁用。
- 后续Gameplan真正启用需独立在隔离存档证明`IsInUse`状态机及UI加载行为；还未做到时展示只读和未开放执行的清晰状态。
- 不触及游戏内任何普通球员评分及能力。

## 7. Codex开发顺序与交付定义

**阶段 0（先修高危老接口）**：在不触发正式局写入的前提下，立即停用`TEAM+0xEB2`所有战术writer。追查调用者，包括`bootstrap_new_game.py`。错误要有可测试的fail-closed效果。

**阶段 1（P0正式实现）**：依据本次用户转发的原生调查，在当前进程重验证COACHDATA默认POE字段/对象及合法枚举→`coach_locator + coach_codec + reader`→`gm_core`离线提案→执行器dry-run/批准门槛/最小隔离测试存档写入与回读→提交GitHub。

**阶段 2（P1可行扩展）**：读取其余模拟sliders、教练滑块、体系，补齐bit/枚举资料并分别实施；不保证所有字段同一天可写，明确哪些只读。

**阶段 3（P2选择性扩展）**：战术本合法已加载目录和选择；对手Gameplan 870条只读/若启用机制真实证实则受控写；18项防守和轮换在完整bit/引用验收前不要盲写。

**阶段 4（交付闭环）**：源码、测试、字段矩阵、实机只读/隔离写入技术证据、接口/调用说明、禁止列表、技术执行回执格式、Github commit，以及`docs/34_BASELINE_CURRENT_STATE.md`/文档13/执行基线36的真实能力表更新。Codex开发结束停止，不自动做正式GM战略、不推进一个月、不自动采集。

建议报告：
- `docs/development_reviews/DEV_20261017_06_COACHING_IMPLEMENTATION_REPORT.md`
- `docs/development_reviews/DEV_20261017_06_COACHING_FIELD_MATRIX.json`
- `docs/development_reviews/DEV_20261017_06_COACHING_EXECUTOR_ACCEPTANCE.md`

若只完成部分模块，报告按字段分别写`READ_ONLY`、`SAFE_WRITE_PENDING`、`TEST_SAVE_VERIFIED`、`PRODUCTION_APPROVAL_REQUIRED`、`BLOCKED`。**只读调研结构事实不等于已写入或已证明快模拟效果**。

## 8. 完成后的玩家接力

Codex向玩家交付：哪些具体教练战术现在技术上可写，具体业务入口和合法枚举/使用方式；哪些模块仍阻塞与原因；禁用旧入口是否已经覆盖所有调用者。玩家将能力说明交Web GPT DEVELOPMENT独立审查，之后交同赛季GM窗口按30队经营模型提出`TACTIC_CHANGE`。只有玩家批准具体球队方案才交Codex EXECUTION执行并记录实际生效游戏月份。玩家正常推进一个月后再触发数据采集/ANALYTICS/GM，观察战术是否发挥作用，必要时下一轮修正；所有步骤均由玩家分别触发，无后台任务。
