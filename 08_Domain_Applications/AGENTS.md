# 本领域内容的工作约定

> **NBA2K22领域启动路由**：凡任务涉及`Antigravity_GM_Engine/`，在按OS最低加载顺序后，优先阅读`08_Domain_Applications/Antigravity_GM_Engine/PROJECT_INDEX.md`和`docs/development/PROJECT_MODULE_REGISTRY_V2.json`，再按模块加载游戏机制资料、数据底层及REA原生调用证据。任务完成后按其`PROJECT_INDEX_SYNC_CONTRACT_V1.md`同步模块索引与任务记录。此路由不覆盖root/Core协议，也不默认加载整个资料库。



本目录由领域仓库独立维护；共享 OS 的入口和安全约束仍然适用。

- 所有特色内容的开发使用 `01_os` 的工作机制，不建立第二套 OS 或通讯系统。
- 特色综合资料、代码与业务产物放在本目录；OS 指定的任务运行证据按既有领域 run 规范放置。
- 不在领域仓库修改 `CORE_MANIFEST.yml` 声明的 core-owned 文件；需要 OS 改动时回到 core 开发。
- OS 更新按本目录 README 的 Human 启用说明按需执行，保留业务内容，不自动激活同步任务。
- 不把旧安装路径、凭据、私钥或 `.env` 内容随业务资料导入 Git。
