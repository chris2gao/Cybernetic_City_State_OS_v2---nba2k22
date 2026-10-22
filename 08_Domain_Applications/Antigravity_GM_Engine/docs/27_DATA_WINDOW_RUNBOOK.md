# 新窗口入口：数据源初始化与更新

DEV15/DEV14-H工程增量：全量流程自动在暂存阶段Potential=1净化，校验覆盖和非Potential字节指纹后才能安装/审计/导出；失败不生成新发布批次。三库安装PREPARED中断须显式recover-capture。旧未脱敏包不供GM、不能直接重发，旧公开历史不自动消失。部署状态以文档34为准，此说明不触发采集。

DEV14托管存档增量：数据任务先核对唯一ACTIVE与完整实例/代次；玩家确认实际加载档后，现有run_data_update.ps1增加 `-LoadedSaveConfirmation 'save_id:save_instance_id:generation_id'`，自动持有生命周期lease覆盖全量采集/审计/导出及本次明确授权的-Publish。UAC worker显式转交该lease，不依赖提权继承环境。新档保持NEW_UNCAPTURED直到本代次全量导出；详见[DEV14手册](DEV14_STATE_IO_RUNBOOK.md)。没有按来源局部更新或另一条生产入口。

本窗口只负责玩家明确触发的数据任务。数据完成不触发 GM 决策；GM 由玩家另行找到对应模型启动。游戏执行也由玩家批准并在执行窗口另行触发。

常驻采集基线使用 [32_DATA_CAPTURE_BASELINE_PROMPT.md](32_DATA_CAPTURE_BASELINE_PROMPT.md)，共享能力/关键词状态见 [34_BASELINE_CURRENT_STATE.md](34_BASELINE_CURRENT_STATE.md)。建立基线只读规则并等待，不开始数据任务。

## 最小阅读与职责

先读本文件和 `AGENTS.md`；按需要查文档 22（真实性/审批）、24（来源覆盖/节点）、26（玩法限制）及 `config/source_catalog.json`。不加载全部历史玩法或各队决策档案。

本窗口完成：当前地址校准、只读采集、清理、SQLite 入库、内存核验、确定性计算、网页文件导出，以及玩家要求的 GitHub 发布。数值运算使用 Python/SQL。不得生成 GM 交易/战术候选，不调用 `generate_gm_proposals`，不修改游戏、不推进选秀和历史线，不替玩家开始下一阶段。

## 玩家交给新窗口的任务信息

| 信息 | 用途 |
| --- | --- |
| 任务类型 | 初始化新局 / 更新现有局 / 仅重新发布已有有效批次 |
| save_id | 明确游戏存档；当前局为 `mc_haliburton_2021`，新局使用新 ID |
| 游戏赛季、准确日期 | 由玩家确认；不能沿用上次聊天日期当作本次日期 |
| 事件 | checkpoint、monthly_close、season_start、post_transaction、staff_change、roster_import、draft_pre、draft_post |
| 目标来源 | 全局球员池、员工池、球队/阵容、比赛统计等；按现有实现报告实际覆盖 |
| 当日比赛是否结束、是否月末 | 分开记录；11 月 20 日结束不等于 11 月闭账 |
| 是否发布 GitHub | 要求上传时才执行发布；已有长期明确授权时按其范围执行 |

缺少本次存档/准确日期等必要信息时只询问缺失项，不自行读取旧局或猜日期。玩家明确授权使用当前状态且无需准确日期时，可以使用 `-GameDateUnknown`；数据库和网页均标记日期未知，年龄保持 NULL，不能沿用旧日期。扩展来源和当前缺口见文档 31。只重发同一有效批次时，使用原批次日期，不重新采集来冒充更新。

## 初始化和更新入口

统一使用 `scripts/run_data_update.ps1`。新 save_id 会从清洁模板建立独立数据库，再采集当前局；已有 save_id 继续更新，不清空。数据任务不要使用 `--approve-game-writes`，也不要顺带应用旧局设置、门票或 POE 模板。

下面仅是已知检查点的参数示例，执行新任务前换成本次玩家给出的日期/名称：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File scripts/run_data_update.ps1 -SaveId mc_haliburton_2021 -GameDate 2021-11-20 -Season 2022 -Month 1 -Event checkpoint -Name NOV20_CHECKPOINT -GamesOnDateComplete -Publish
```

玩家已经新开 Codex 对话时，在该窗口运行即可；只有玩家还需要独立 PowerShell 终端才加 `-NewWindow`，避免把“新模型对话”与“脚本终端”混为一谈。主任务自动处理管理员采集子进程；遇到正常 UAC 提示由玩家完成系统授权。

**玩家2026-10-18确认全量-only规则**：每次新游戏数据更新统一运行现有`full_verified_v1`，刷新全部已验证来源（包括已合并main的原生教练战术）；此前“按单队、单来源分批更新”不再是待开发需求。玩家提出“更新比赛/教练/阵容/员工”均按本项目约定理解为触发完整刷新，具体存档/日期/`-Publish`仍需玩家本次授权。若玩家明确提出排除某来源，则先说明当前只支持全量，不可违反排除要求。最新全量代码尚未进行首次正式教练数据生产采集/发布；见[DEV08启用规划](development_tasks/DEV_20261018_08_COACHING_FULL_REFRESH_FIRST_PRODUCTION_V1.md)。游戏显示年龄/OVR、逐场日志等未观测来源仍保留缺口，不因全量刷新而编造。

每次都重验当前 PID、模块和锚点；缓存失效重新扫描。玩家提供的 CE 地址只作线索，不能直接沿用。读失败、身份不符、来源变化或审计失败即停止后续导出/发布。

## 到哪里停止

数据内部步骤为：备份 → 校准/只读采集 → 清理入库 → 采集审计 → 确定性计算/自动导出 → 按本次要求发布 → 记录数据更新时间与上传时间并交付回执。按文档 29，不运行 JSON 哈希、全字段或下载比对。结束状态为 `DATA_READY_AWAITING_PLAYER`。

只汇报：

- save_id、玩家确认日期、data_updated_at 和 uploaded_at；snapshot_id、batch_id、commit 作定位信息。
- 实际采集来源、记录数量、审计结果、已计算差异和未观测字段。
- 数据库/阅读包位置；发布成功时给 GitHub 数据入口和数据库 Release。
- 本地成功而发布失败等部分完成状态，不能把失败环节称为成功。
- 说明“数据任务结束，GM 决策待玩家另行触发”。不附带交易、训练或历史加成建议。

旧目录里可能保留早期 `GM_REPORT_*` / `gm_decision_manifest_*`；它们不是本次数据任务的产物，不读取后冒充新决策，也不为隐藏历史而删除。

## 可直接复制到新窗口

```text
这是数据任务。先读 docs/27_DATA_WINDOW_RUNBOOK.md，再按项目规范执行。
任务：更新现有局（新局时改成初始化，并使用新的 save_id）。
存档：mc_haliburton_2021。
游戏赛季/日期：【填写本次真实赛季和日期】。
事件：【填写检查点、月末、赛季开始或其他节点】。
目标数据源：【填写】。
当日比赛已结束：【是/否】；本月已结束：【是/否】。
按全量-only约定处理新数据更新；明确排除某来源的请求不得违背其限制自动执行。已完成批次若只需重新上传，走现有重发入口，不把旧来源标成新采集。
完成已授权范围内的采集、清理、内存核验、数据库更新及确定性计算后上传配置的 GitHub 仓库。
只交付本次数据、审计、缺口和发布回执，到此结束，不启动 GM 决策或游戏执行。
```
