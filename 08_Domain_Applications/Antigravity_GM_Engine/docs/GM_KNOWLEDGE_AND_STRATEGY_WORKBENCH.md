# M2 篮球知识与球队策略工作台

BPTI B1增量：在既有知识目录增加十张SystemCard及六条开档前定性机制Claim，沿原Knowledge.bpti()/ResearchIndex查询。新增bpti-system按ID读取一张、bpti-systems按角色/反制返回1–5张摘要；普通GM先过滤来源/时间，再返回正文。研究创建覆盖与GM可读覆盖分别报告，原M2卡/数据库不替换，详见[B1手册](BPTI_B1_SYSTEM_CARDS_AND_RETRIEVAL.md)及[实际验收](development_reviews/BPTI_B1_IMPLEMENTATION_AND_ACCEPTANCE.md)。

BPTI B0增量：现有Knowledge新增按需bpti()入口和gm_knowledge的bpti-contract/bpti-source/bpti-claim/bpti-validate子命令，详见[B0契约](BPTI_KNOWLEDGE_CONTRACT_V1.md)。只提供研究引用和四类DTO，不替换下述12卡或创建第二套数据库；GM默认时间投影，研究全文须显式RESEARCH。十家族完整卡及实际球队身份仍留给后续玩家批准的B1/B3。

版本 `gm_knowledge_v1 / TEAM_STRATEGY_STATE_V1`，状态 `IMPLEMENTED_LOCAL`。这是供 GM 显式消费的参考检索与派生状态工具；现行 GM 规则不切换为 V4。与 [M1 财务工具](GM_FINANCE_WORKBENCH.md) 共用独立 `gm_workbench.sqlite`，不修改事实库。

## 查少量参考，再按卡片钻取

在仓库根目录运行，以下 PowerShell 命令只访问文件或已有静态查询副本：

```powershell
python -B scripts/gm_knowledge.py search --tag pick_and_roll --limit 5
python -B scripts/gm_knowledge.py search --field BenchDepth
python -B scripts/gm_knowledge.py search --team SAS
python -B scripts/gm_knowledge.py show --card PNR_PRIMARY
python -B scripts/gm_knowledge.py show --card DROP_CONCEPT --career mc_haliburton_2021 --batch BATCH_ID
python -B scripts/gm_knowledge.py franchise --team SAS --period 2021
python -B scripts/gm_knowledge.py rules --text 合同 --limit 5
```

将 `BATCH_ID` 替换为当前已认证批次；不指定批次时由 M0 解析最新指针。默认最多5条摘要，支持 `--tag/--field/--text/--team` 组合筛选；`show`返回一张完整卡。球队筛选只引用已研究的 GSW/SAS/OKC 试点卡；其他队返回 `NO_TEAM_PRESET`，可按篮球问题检索，不虚构队名模板。`rules --rule ID`可钻取机制条目。

内容含12张战术卡、30队2021背景参考、19条项目游戏机制、38条来源登记。现实参考、字段映射、实际游戏效果分别标证据。卡片的能力需求是概念标签，不能直接当作已定位的55项原生字段；尚无对应数据的信号保留缺口。没有自动球员打分、阵容选择或胜率预测。

带 `--career` 的卡片查询使用 M0 静态副本确定批次，再用该批次 `coaching/field_dictionary.json` 与当前 `coach_tactics_profile.json`共同解析标签。无同批教练来源时卡片仍可读，映射为 `UNAVAILABLE`；目录标签冲突同样不生成目标值。直接枚举为 `SAME_BATCH_NATIVE_ENUM`，Drop 的 NO_HEDGE/GO_OVER 为 `HYPOTHESIS_CANDIDATE`，不声称等价于 Drop。动态手册不复制固定 raw 白名单，按同批具名教练目录查询；四 Freelance 槽顺序原样返回。这些结果都不是执行请求或批准。

## 初始化30队候选

```powershell
python -B scripts/gm_strategy.py init --career mc_haliburton_2021 --batch BATCH_ID --output _exports/strategy_candidates
```

输出每队 JSON 与 index.json；目录必须不存在，默认使用 `_exports`下新目录。30队均为 `UNASSESSED`，当前核心、动作、预算、竞争窗口均未填写，没有正式分析任何球队。仅复制带来源的历史参考；不从现有阵容推导老板偏好。初始化不写工作台或正式赛季档案。

## 显式保存、读取与修订

`save`保存调用方已提供的状态，不自动生成 GM 判断。可先保存候选，也可在玩家另行触发正式分析后填写 DRAFT/REVIEWED_ANALYSIS。候选仅作开发准备；正式分析授权继续按既有流程。

```powershell
python -B scripts/gm_strategy.py save --input _exports/strategy_candidates/SAS.json --expected-revision 0
python -B scripts/gm_strategy.py show --career mc_haliburton_2021 --team SAS
python -B scripts/gm_strategy.py show --career mc_haliburton_2021 --team SAS --revision 1
python -B scripts/gm_strategy.py list --career mc_haliburton_2021
python -B scripts/gm_strategy.py export --career mc_haliburton_2021 --output _exports/strategy_summary
```

默认工作台 `database/workbench/<career>/gm_workbench.sqlite`；可用 `--workbench PATH`指定同名派生库。读命令使用只读连接，工作台路径不允许指向 saves/query_snapshots/published/seasons（解析后忽略大小写）。候选/摘要导出拒绝事实、published和正式seasons目录；不自动提交导出或上传SQLite。`export`只生成当前状态摘要、历史前驱指针与引用，历史全文仍按revision读取。

第二版须新 `state_id`、`revision=2`、`supersedes_state_id=<第一版ID>`，并填写 `change_reason`和`rejected_hypotheses`（无被否定项可为空）。`--expected-revision 1`表示预期当前只有第一版。事务比较当前修订后插入；旧预期返回 `STRATEGY_REVISION_CONFLICT`，不会覆盖已保存版本。每次保留来源批次，不自动用新批次重写旧分析。

状态schema在 `web_gm/schemas/TEAM_STRATEGY_STATE_V1.json`；已评估状态需来源证据、转向条件、同批复核标记。动作状态只能是 `HOLD/PROPOSED/RESEARCH`；拒绝 `EXECUTED/PLAYER_APPROVED`和模型提供的`approved`字段。`REVIEWED_ANALYSIS`只表示分析状态。保存接口不认证远程角色，不因为自报身份授予权限。

可选 `finance_run_id`必须引用同工作台现有 M1 run；不同career拒绝，不同batch标 `DIFFERENT_BATCH_REVIEW_REQUIRED`。未关联标 `NOT_LINKED`，不会从缺失或陈旧run推导预算。慢变量历史参考沿用原始来源，快变量判断由调用方按批次复核。

## 本轮验证与后续边界

见 [M2验收回执](development_reviews/DEV10_M2_KNOWLEDGE_ACCEPTANCE.md)。只完成内容/查询/版本存储相关检查及已有M02静态副本的本地CLI路径；Web真实连接由玩家后续建立，现金与签约实机验证继续延后。本轮未运行正式GM、采集、游戏数据发布或游戏写入。M3/M4与GM V4切换等待后续任务。
