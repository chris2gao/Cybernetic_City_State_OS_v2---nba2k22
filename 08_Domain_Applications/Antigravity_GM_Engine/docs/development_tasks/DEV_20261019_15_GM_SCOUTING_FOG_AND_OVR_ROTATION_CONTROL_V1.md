# DEV15 V2 — 所有球员潜力值入库后统一=1 + 30队Intangibles引导原版轮换

> **2026-10-19 开发模型窗口职责（最新）**：[DEV18两个Codex窗口接力](DEV_20261019_18_TWO_CODEX_WINDOWS_HANDOFF_AND_BOOK_DEFAULT_V1.md)明确本文件的底层工作由**独立DEV14 Codex窗口①/PR#5**负责。M系列Codex窗口②/PR#4只在用户转交`DEV14_TO_M3_HANDOFF.md`和稳定接口后实施GM战术与球队经营，不应在PR#4重复实现数据库、内存编码、潜力脱敏和审批执行器。新档各队本名Playbook为用户确认的默认业务前提，**取消预先研究克隆/共享书冲突的前置开发**；仍保留正常Book Native ID和内存写入回读校验。PR合并和游戏真实变更仍需用户授权。

**日期：2026-10-19 · 最终业务决议：玩家。执行：Codex（数据库处理、DEV14字段与M3接入），Antigravity（已有NBA2K22原生字段数据和教练训练适配器）。**
**本V2明确取代本文件此前的V1研究型限制。** 两项业务规则已经确定，**不再以调查Intangibles对交易/模拟/合同等副作用或潜力遮蔽方案优劣为前置开发条件**。仍必须保证程序写入正确对象、正确字段、前后读回、操作可逆；这属于工程正确性而不是副作用研究。

## 一、权威用户决定

1. **轮换**：所有30队的GM都可在球队经营中提出单字段`Intangibles`综评补偿调整（按本局原生可用值25–99），目的明确是影响原版游戏AI的首发、第六人、轮换优先级/分钟分配。继续允许教练BenchDepth/年轻-老将/体系及训练影响分钟，不开发“锁定精确分钟”/反复强制回写；无须在本任务额外验证它是否改变交易估值等其他游戏系统。用户已经决定接受相关游戏机制未知副作用，不用研究此项来推迟开发。
2. **潜力**：采集游戏原始数据**完成后、生成不可变查询副本/导出/发布前**，自动运行确定性后处理，将**所有球员（包括球队名单、全员球员池、未来历史选秀班候选）数据库中的真实Potential统一覆盖为1**。不是“只给GM看脱敏字段”、不是需要模型逐项改，更不是更改游戏内存/存档中潜力。GM规则文档必须明确说明：**Potential=1是人为遮蔽占位值，非真实观测，绝不能用作成长判断或筛选。** 原版游戏照常自主成长。
3. **审批**：既有项目基本规则仍为玩家审议GM产生的真实游戏写入批次；“30队可随意调整Intangibles”意指GM可自由提出任何合法25–99策略性变更，不需要像其他普通Ability那样禁止提案，也不需要每次副作用研究。正式apply继续走玩家批准、DEV14稳定digest、game process/save/generation绑定、内存CAS、写前备份、读回及条件恢复。**额外豁免仅限Intangibles 0x440一个原生字段**，不开放邻近Ability/Potential/徽章/合同等。
4. **知识定位**：修改显示OVR可改变AI轮换输入，但不等于提升场上投篮/速度/传球等篮球技术；GM在讨论交易或球队实力时区分策略性偏置的Displayed OVR与原始能力和比赛表现，不要求研究对其他系统是否有额外影响。

## 二、已核实真实源码字段，Codex无需重新寻址

当前`main`的`config/memory_field_profile.json` → `fields.PLAYER`：
- `intangibles`：offset **1088 = 0x440**，1 byte，`conversion=rating`；
- `potential`：offset **1089 = 0x441**，1 byte，`conversion=rating`。
- `fields.STAFF`也有同名potential，但不属于球员，不要混用偏移。来源池`src/dump_player_pool.py`明确用`raw_struct[0x441]`生成`raw_potential`与`potential`。
- DEV14 PR#5 `src/gm_state_io/registry.py`目前没有注册单独`PLAYER_ROTATION_OVR_BIAS`动作：球员Intangibles属于原Attribute区域，原保护会阻挡普通写入。新增**唯一精确allowlist例外**，模块/SQL/ACL/日志只允许已审批的特定球员`intangibles`一个字节；绝不提升对整段`0x41F-0x455`的写权限。
- 获取真实球员身份必须复用DEV14 `PLAYER_TENDENCY/PLAYER_PLAYTYPE`所用按当前存档/球队/球员唯一定位，不能使用名字或裸地址定位。修改后记录`intangible_before/after`、可观测OVR与分钟反馈来源批次；反馈可在之后的正式运营批次自然积累，不要为了开发先强迫打多场。

## 三、潜力统一脱敏的自动化位置与范围

### 3.1 插入已有正式采集管道，不能变成独立人工步骤

`src/auto_pipeline_ingest.py`当前流程是：
1. 同一只读NBA2K22内存会话采集球队及阵容：`src/source_extensions.py` `player_details()`将`attributes.potential.raw/value`写入`player_source_details.details_json`、同时保留`raw_struct BLOB`；
2. `src/dump_player_pool.py`采集整个历史球员池到`player_pool`，含`raw_potential`、`potential`、`source_details_json.attributes.potential`、`raw_struct`；另可能有缓存/staging文件；
3. 原管道`stamp_database`、两库commit、`os.replace(player_pool_stage_path,player_pool_db_path)`，再计算`player_pool_sha256`、`snapshot_digest`、JSON`ingest_manifest`，之后`export_web_gm.py`、M0查询副本、`run_data_update.ps1 -Publish`发布到GitHub。

**新增强制阶段：`sanitize_player_potential(...)`**：必须在原生RO采集/初步完整性验证之后、两库正式commit/替换及所有正式哈希/JSON/SQLite备份/上传之前，运行在**本批staging SQLite**中的后处理事务。不得在已发布只读文件上临时再打补丁；任何失败`POTENTIAL_SANITIZATION_FAILED`直接拒绝发布本批。支持显式本地CLI`python -B scripts/sanitize_player_potential.py --career <save> --batch <batch> --dry-run`用于校验，但正常full_verified_v1**自动调用**，不需人工额外执行。脚本在测试库和隔离副本上可以重复幂等运行。

### 3.2 必须消除所有球员真实潜力副本

覆盖所有球员，不仅30队当前名单：

| 来源 | 必须写入值或变更 |
|---|---|
| `player_pool.potential` | **1** |
| `player_pool.raw_potential` | **1**（原值不在GM可见DB留下） |
| `player_pool.source_details_json.attributes.potential` | 覆盖`raw`、`value`为1，并标`visibility=MASKED_BY_GM_WORLD_RULE` / `evidence=NOT_GAME_OBSERVED` |
| `player_pool.raw_struct` | 仅将PLAYER结构**byte[0x441]置1**；其它byte原样。慎防其它未脱敏原始结构副本 |
| `player_source_details.details_json.attributes.potential` | `raw=1,value=1`，同样标MASKED而非游戏实测 |
| `player_source_details.raw_struct` | 仅byte[0x441]置1，其他字节不动 |
| 各项选秀池、历史新秀、已发布球员详情JSON、rosters、同批`state_io_objects.raw`（如含PLAYER完整结构）、通用`observed_setting_values`、静态快照、缓存及可查询导出 | 检测真实潜力衍生内容；所有会被保存/交GM的PLAYER原始全结构同样遮蔽此字节，或**不要发布原始结构**。若有其他potential别名/存储字段，用注册字段扫描覆盖。对无法确定的隐蔽结构，先Fail Closed，不谎称全遮蔽 |

与人物相关的Staff记录、球队世界线数据或真实游戏内存不改。**不要把整个`raw_struct`替换成全零**，更不要直接抹去其它属性、历史新秀分类码、潜力以外的成长数据、徽章。已知Player结构字节0x440为`intangibles`，必须保持不变。采集需继续保留球员合法身份、契约等供GM经营。
- 原始Potential不得在正式发布档或GM可访问的`_exports/archives`、`published/saves`及M0 SQLite查询副本残留。**原生游戏内存照常保留真实Potential**。只保留原始批次的必要非反演指纹、脱敏版本与覆盖计数，不保存GM可读明文真实Potential。
- 初始只读内存校验可以检查原生实值，后处理的`Potential=1`必须在data provenance明确为**人为遮蔽，不是来自游戏的观测结果**。不得因DB潜力被置1而影响游戏本身原生计算/自然成长。
- 如果旧M02与之前已发布历史批次仍有真实Potential，不能假装新算法让其自动消失。GM正式启用前需明确**历史档访问策略**：旧原始数据归档禁供GM读取，或经用户明确批准重新发布经过净化的GM可见副本，并注明源批次/脱敏版本，不在原immutable历史上暗改。GitHub仓库或连接器若仍暴露旧原始Potential，文档须准确披露。

### 3.3 强制自动校验（不用重复研究真实潜力效果）

- `SELECT COUNT(*)`确认所有player_pool有效记录`raw_potential = 1 AND potential = 1`；所有roster详情`json_extract(...,'$.attributes.potential.value')=1`且`raw=1`；所有Player raw_struct`hex(substr(raw_struct,0x441+1,1))='01'`或Python逐行检查；不可信缺位/错长度拒绝发布。
- 统计每档每批`pool_total / roster_total / masked_json_count / masked_blob_count / missed_rows`，若已识别含潜力字段却未处理任一行必须FAIL。
- 为防止抹到intangible等相邻能力，运行前后除0x441以外的PLAYER结构字节摘要一致；特别断言原生`intangibles` 0x440前后完全相同，30队身份/合同/历史新秀标签数量不变。
- **幂等**：同一批再运行一次既不产生二次语义变化，也不使数据库、哈希/manifest自相矛盾；哈希与`latest`依据脱敏后的数据计算；下一次正常采集重复运行不要求人工处理。
- **双库失败一致性**：league/pool staging按DEV14安全处理，若处理到第二库失败不允许只发布第一库脱敏，保持旧已发布批次不动；只新增直接相关的合成小测试即可。

### 3.4 GM长期信息说明（要求Codex同步文档）

在`web_gm/manuals`或GM V4的必读知识文件写清：
> “NBA2K22原版球员真实Potential已在数据采集后统一人为替换为1。该数值是模拟现实NBA未知未来发展潜力的遮蔽占位值，**不反映任何球员真实潜力、成长空间或选秀价值**。GM不得按照Potential=1判断球员潜力相同/低潜力，必须利用年龄、当前能力、历史成长、比赛表现、训练、伤病/可用性和机会成本进行不确定性预测。”

市场报价、球探、30队GM、历史新秀与M3的`decoded_attributes`必须同样遵守这条规则；当`potential=1`仍出现在字段显示时明确标注`MASKED`。

### 3.5 严禁脱敏球员池反向成为历史选秀注入源（新增确定性工程保护）

仓库真实的`src/historical_rookies.py`→`query_historical_draft_class(db_path,year)`会从`player_pool`表读取`raw_potential`、`potential`和**完整`raw_struct`**并返回查询结果；`src/dump_player_pool.py`也自称历史选秀注入引擎的来源模块。这意味着当GM库已将PLAYER`raw_struct[0x441]`置1时，**任何把查询结果的raw_struct直接用于人物/历史新秀注入游戏的代码，都可能意外将真实原生潜力写成1**。这属于游戏数据完整性风险，**不属于用户已取消的Intangibles副作用研究**，必须防止。

具体决议：
- **所有GM可见和发布的球员池数据库必须Pot=1**，不能因“以后需要注入”让真实潜力漏到GM。
- 如果历史选秀执行确实需要保留新秀真实原生Potential，必须从**GM和GitHub普通发布完全不可访问的、未脱敏的私有注入专用来源**取得（可为采集过程中的仅本地受控原始缓冲/权限隔离主档，或由游戏原生当前存档重新读取并校准）；**不得把GM发布库中的`raw_struct`当成可逆转的官方人物源**。
- 如当前项目尚未完成私有注入来源接口，历史选秀相关写入调用面对`potential_mask_version`时必须**Fail Closed**，返回`SANITIZED_PLAYER_POOL_NOT_NATIVE_INJECTION_SOURCE`；不能悄悄使用Potential=1构建未来历史新秀。这条约束适用于Codex和Antigravity已有/以后所有注入适配器。
- 读写分类清晰：`source_role=GM_SANITIZED`与`source_role=NATIVE_INJECTION_PRIVATE`、`mask_version=potential_v1`、`player_raw_masked=true`。GM不能通过注入专用私有来源读取真实Potential；原始游戏内存中Potential本身始终不更改。
- 直接相关验收：从GM库调用历史注入接口，必须拒绝`masked`结构；从独立受控原生来源执行同一个球员的预检，必须保持原生Potential原值、无需修改技能/徽章。**不需要为了此安全约束研究综评补偿影响合同、模拟或其它业务**。


## 四、轮换控制完整GM闭环（让DEV13直接用）

- 核实真实原生位置排序、首发5、主要第6人、教练BenchDepth/BenchUtilization/年轻-年长、体系熟练度、实际最近若干场分钟（无法自动观察时UNKNOWN）。**用户总结的1–10分钟变化经验不需要再做副作用研究，不当作精确公式**。
- GM给每个轮换球员指定`role`及`minutes_target_band`或目标分钟值，方案必须在240分钟常规配额/人员健康/犯规/加时约束下合理。根据优先级优先使用`Intangibles`偏置、教练板凳/体系及首发影响；本任务允许各队有策略地调整每人的25–99而不是仅偶尔例外一次。
- 每次通过DEV14建立`PLAYER_ROTATION_OVR_BIAS`动作，保存本人旧值和新值、赛前原因、获批状态、原生内存回读；后续正常月度正式采集记录实际分钟/首发/轮换变化与GM目标的误差，供下一轮自动形成建议。**不设置额外副作用研究/验证门禁，不开发强制锁分钟**。
- 显示OVR若被该机制提升不应被GM以为原始篮球技能真实增强。玩家可选择接受显示OVR参与原版市场或Sim算法的自然影响，外挂GM角色判断依旧基于真实技能和球队目标。
- 除`Intangibles`特定allowlist以外，原始Ability、Potential、Badge、合同、身体属性的直接写入仍按项目原禁令。

## 五、当前已实现与剩余工作

**DEV14 PR#5已实质接入**：19默认+18整体、个人防守、68槽Playbook、球员4PlayTypes/Initiator、99倾向读取/48已命名写、6项球队训练+5项球员训练、4项Gameplay USER/CPU、50项当前已可用世界线设置。全部经合成/静态M02验证，正式生产/游戏持久化尚未验证。**这不是“只做接口”**。

**DEV15新增的确切缺口只有**：
1. 在正式full_verified_v1后发布前加入自动Pot=1全库净化脚本并校验，覆盖已有所有Player镜像/原始字节；
2. 将已存在的`intangibles`字段映射为DEV14极窄合法写动作，打通游戏进程真实身份与M3轮换提案/结果反馈；
3. 更新GM数据语义、老批次可见性和M3与DEV14的状态/审批接口。**不重复开发已支持的世界/训练/战术读写框架**。

**与DEV14-H顺序**：三库同generation安全加固与真人审批由[DEV14-H](DEV_20261019_14H_DEV14_POST_REVIEW_HARDENING_V1.md)负责。本任务可在单独分支开发，但PR整合前必须采用最新DEV14-H已认证身份和approval规则。PR#4/#5仍未合并，不得直接用main的旧代码报告V4已可运行。

## 六、验收与交付（轻量且直接）

- 提交可复用`scripts/sanitize_player_potential.py`（或项目风格等价模块）以及`full_verified_v1`**强制自动调用**；记录覆盖计数/版本/FAIL错误码/净化后哈希；最少一个双库含roster/pool/JSON/raw_struct的合成用例，证明所有Potential=1且Intangibles等其它原始数据不动；失败不得发布。
- 轮换动作注册/codec/提案/批准与受控读回完成；一份合成`PLAYER_ROTATION_OVR_BIAS`计划与不同球员共享Batch的正确性，无需为“对其他系统的影响”额外实施测试。游戏内正式写入仍待玩家按正常经营节点批准。
- 文档：`docs/DEV15_ROTATION_AND_POTENTIAL_RUNBOOK.md`、GM V4知识说明、相应DEV13和source_catalog索引以及定向验收；不通过删源数据库或打乱已封存历史来缩短开发。
- Codex额度受限时优先**Potential自动净化+文档**，再做Intangibles字段注册和轮换M3提案；不可因为50多个未知Tendency、全部教练战术心理机制或额外副作用研究阻塞。

**成功定义**：每次正式采集后交GM的数据中任一球员Potential统一=1（并明确非实测），而30队GM可以按轮换目标修改经审批的Intangibles，引导原版AI自主调整上场时间。