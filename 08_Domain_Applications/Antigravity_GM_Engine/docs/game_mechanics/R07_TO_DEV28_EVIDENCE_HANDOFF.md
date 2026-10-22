# DEV29 R07 → DEV28 与 FINAL-CODEX：真实游戏信息/操作能力缺口交接（研究资料）

> 2026-10-21。**状态：R07研究报告已发布，独立审核待完成；本文不是开发任务、PR说明、游戏采集请求或Codex授权。** R01–R06已研究结案，目标NBA2K22 PC本世代MyLEAGUE。R07给出[40组能力矩阵](catalogs/R07_GAME_CAPABILITY_MATURITY_MATRIX_V1.json)、[694条源索引](catalogs/R07_ITEM_TRACEABILITY_INDEX_V1.json)和[中文指南](guides/R07_OBSERVABLE_ACTION_EVIDENCE_MATURITY_GUIDE.md)。

**R07索引体积与读取约定**：`R07_ITEM_TRACEABILITY_INDEX_V1.json`现在是7卷的JSON清单（694项总计）；不能把清单缺少`items[]`理解为资料丢失。使用`parts[].path`逐卷读取，不要依赖GitHub单个超大Contents API响应。分卷保留原始网页来源和项目Profile/文档依据。

## 1. 最终工程问题

在不破坏游戏既有自然成长/原生合同/实际比赛规则前提下，确认哪些**已研究的信息**在当前真实存档里已经①有原生来源②被完整读回③同批SQLite/JSON发布④提供模型安全查询⑤属于经过玩家当次批准的有限执行器能力。缺口由后续获批的DEV28或小范围Codex落实，R07不决定具体实现方法、更不触发执行。

`R07_GAME_CAPABILITY_MATURITY_MATRIX_V1.json`的40组并非40个已实现API。`R07_ITEM_TRACEABILITY_INDEX_V1.json`的694项并非694项已读原生字段；静态registry是来源线索，研究候选需要PC22实际菜单与GameID/PlayerID/SaveId比对。**项目存在的生产来源要核对真实最新manifest/latest.json，不以本文件基线里的历史数量冒充现批次。**

## 2. 三个必须由未来执行任务逐层验证的清单

**A. 已登记/已有业务执行器，但边界有限**：原生教练设置、Player/Team指针关联、15人名单容量、简单Draft Asset Owner、合同/Staff研究Profile、World和Gameplay候选偏移。已有Approved Trade v2仅对受支持普通交易有玩家实证；FA签约实际写入关闭、普通球员Ability/Badge/Potential不可编辑；抽象字段`technical_registry_writable`不等于可让各独立模型任意调用。

**B. 已有完整采集及模型数据包来源**：球员池、30队阵容、球队/球员赛季聚合、员工、未来简单Pick、部分Coach默认及Overall Defense。每批独立标记`save_id/save_instance_id/generation_id/game_date/data_updated_at/uploaded_at/batch_id`；不得把不同时点来源拼为最新联合快照。查询需提供当前Source status和缺项`NOT_OBSERVED`，并禁止泄漏隐藏球员潜力给未获权观察者。

**C. 仍未证或缺失的游戏原生细项**：Game Logs与单场Box/Shot、比赛生成方式及Normalization两开关、季后赛与Offseason阶段/Save重载、真实历史Draft完成、Native AI签约、奖项/纪录/社会媒体、跨季GameID/交易历史和Staff雇聘等。前代/别代百科或静态功能名字不足以声明本局已能查询。

## 3. D06-G01..G08作为优先研究证据需求，而非自动建开发任务

| 关联 | P0缺口 | 将来验收必须看到 | 当前限制 |
|---|---|---|---|
| F01–F04 | G01单场统计 | 同一真实GameID的两队Box/投篮资料、来源时间，无法采应显式NOT_OBSERVED | 赛季累计不能反造Game Logs |
| F27–F31 | G02模式判别 | 3D CPUvsCPU、USERvsCPU、SimCast、日历Sim来源分别标注 | 不能把球队User控制身份当Game Slider消费者 |
| F03/F30 | G03两个Normalize | Stats与Minutes分别UI/原值/真实只读回照 | 不能用单一Registry值冒充两个PC22按钮 |
| F32/F39 | G04 GameDate/批次身份 | UI/原生GameDate、save generation、manifest、批次和gamephase一致性 | GitHub日期不是GameDate |
| F37/F39 | G05存档持久性 | 获准测试档Save→退出→Reload→原值对照 | 读取/上传新SQLite不等于已保存游戏 |
| F07/F24 | G06历史新秀轮回 | 当前已加载Draft Class的身份、真实已完成选秀、下一循环年 | NBA2K23 Eras不是PC22 PC原生模式 |
| F19/F21 | G07休赛期AI合同 | 阶段边界的原生名单/合同自然变动、休赛期报价/签约可观察性 | Synthetic FA规划器不是实机签约 |
| F22/F23 | G08 Pick政策V4代码差距 | 用户另外批准后，小范围移除旧+3人工拒绝并完善校验/测试 | 不把+3替换成+5，也不能由R07直接改执行器 |

其余20缺口完整见[原R06-D源目录](catalogs/R06D_CROSS_DOMAIN_MECHANISMS_AND_GAPS_V1.json)；所有“证据优先级”只是给未来开发审核方参考，真实任务排期和授权由玩家决定。

## 4. 给FINAL-CODEX的未来最小对账口径（未经启动）

若用户之后单独下达FINAL-CODEX任务，建议先执行**只读静态对账**，而非立即逆向/写入：
- 对照`config/state_io_native/*.json`、`config/memory_field_profile.json`、`src/gm_state_io/registry.py`和R07索引，去重已重叠的物理Native slot，不将研究候选直接注册可写。
- 对照`docs/34_BASELINE_CURRENT_STATE.md`、最近一次有效`full_verified_v1`采集manifest、`published/saves/<save_id>/latest.json`、GM SQLite查询及现有交易/教练验收回执，逐项标出**已有原生源但未查询、已有真实数据但未发布、只有静态地址、仅其它平台资料、用户批准的有限写入**等不同状态。
- 优先审视既有读源能否用于准确的GameID/Box/日期/Normalize/Offseason索引；如果游戏当前没有相应数据，不能凭现实NBA.com或Season Totals推导出2K22逐场Game Log。
- 对当前游戏/本地PC所有进一步操作另获玩家独立批准；重启、保存、比赛推进和写入资产均不属于静态对账范围。R07研究者不派单、不启动CodeX。

## 5. 角色系统独立开发边界

GM/Coach/Player/Media可见资料按公开/球队/个人/管理员合法视角分类，只是需求与信息安全研究。谁坚持某一战术、球员是否要求加薪、Coach是否请求交易、媒体报道如何影响关系，均属于未来独立模型的行为设计，不在DEV28和R07的实现范围。**不使用2K22原生属性/潜力/徽章字节作为外挂人格记忆存储。**

**交接状态：`R07_RESEARCH_PUBLISHED_PENDING_INDEPENDENT_REVIEW`；R07通过独立审核以后，用户才能另行选择是否发起DEV28/FINAL-CODEX技术任务。**


## 2026-10-21 R07审核后机读语义修复（独立复验待完成）

依据[定向修复回执](../development_reviews/DEV29_R07_TARGETED_CATALOG_REPAIR_20261021.md)，R07索引第1卷两个`manual_research_topics`为人工作成的指南主题别名、并非源机器主键；40组矩阵的F21/F22/F23/F26/F27/F32/F39/F40已将`model_query_api_status`中的执行限制、批准规则和Save/GameDate语义剥离，保留在独立限制字段。**DEV28/FINAL-CODEX后续读矩阵时，查询成熟度只看`model_query_api_status`并与历史有效batch核对，不能从`execution_warning`倒推查询能力；同样不能从SQLite查询范围倒推可写业务。** R07修复待独立复验，不自动授权工程启动。

