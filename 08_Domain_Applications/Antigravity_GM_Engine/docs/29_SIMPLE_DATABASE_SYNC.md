# 数据同步：只看更新时间

玩家已要求简化同步。本文取代旧文档中 JSON 哈希、全字段复核、下载归档比对和网页逐项验收的要求。

## 自动流程

玩家触发更新并要求上传 → 脚本校准地址、采集、入库 → 自动导出 JSON 和完整数据库 ZIP → 上传 GitHub → 记录上传成功时间 → 结束。数据更新不触发 GM 决策。

采集前的地址校准与采集审计继续由脚本执行。同步阶段不调用模型，不运行 JSON 哈希、逐字段或导出结果比对，也不重新下载数据库做比较。`verify_web_export.py`、`test_web_export_guards.py`、`verify_repository_delivery.py` 是旧同步方案的工具，不作为当前日常同步步骤。

## 固定线上入口

`published/saves/<save_id>/latest.json`，当前局为 `mc_haliburton_2021`。

- `data_updated_at`：游戏数据这次实际采集完成的时间，UTC ISO 格式。重发旧数据时保持原时间。
- `uploaded_at`：这次上传数据库后，脚本记录的发布完成时间，UTC ISO 格式。
- `game_date`：玩家确认的游戏内日期，与上面现实时间分开。
- `batch_path`：本次 JSON 数据目录。
- `archive_url`：本批完整数据库下载入口。
- `upload_status`：`PENDING_UPLOAD` 表示尚未完成；`UPLOADED` 且有 uploaded_at 时表示脚本已完成上传步骤。

`published/index.json` 也显示每局的数据更新时间和上传时间。数据库 ZIP 内的两个 SQLite 均有 `data_sync_metadata` 表，保存相同的 `data_updated_at`，ZIP 另含一份 `data_update.json`。以后新采集的本地数据库同样写入这个表；旧采集重新导出时只给备份副本补入原采集时间，不伪装成重新采集，也不修改旧采集证据。

数据库内部保存数据更新时间；上传成功时间保存在 GitHub 的 latest/index 和发布回执中，不为补写上传时间而再次改动已经上传的数据库文件。

## 网页 GM 怎么用

玩家让 GM 开始时，重新读取 main 分支的 latest.json：

1. 看当前存档的 `data_updated_at`，与上次使用的时间比较；相同表示采集数据没有更新，更晚表示新数据。
2. 看 `uploaded_at`；尚未填入时等待本次上传完成。
3. 按 `batch_path` 读取需要的球队、球员或选秀 JSON。无需哈希、逐字段核验或数据数量验收；commit 和 batch 可保留作定位信息，不作为玩家判断新旧的必要步骤。

只有上传时间变新、数据更新时间没变，表示重新发布了同一批旧数据。连接读不到本次时间时如实报告，不用旧对话记忆宣称已经更新。

## 失败与重试

导出、git push 或数据库上传命令失败，脚本直接报错，不输出整体成功回执。JSON 先上传，数据库附件完成后再写 uploaded_at 并提交；中途失败的入口可以保持 PENDING_UPLOAD。对同一批次重试上传不必重新读取游戏内存。

玩家于 2026-10-17 明确授权保持公开仓库，并上传本次游戏数据库和 JSON。数据库归档放公开 GitHub Release，JSON 放仓库；两者均由脚本生成和上传。发布脚本按 `config/github_sync.json` 的可见性配置检查目标仓库。日常流程以时间判断新旧，不保留额外的 JSON 检查步骤。
