# NBA 2K22

这是特色领域仓库 `nba2k22`。通用 OS 来自 City-State core，特色资料和代码由你稍后手动放入本目录。

## 目录与工作边界

- `01_os/`：共享 OS 的工作流、机制和执行入口，不在领域仓库修改 core-owned 文件。
- `08_Domain_Applications/`：本仓库的特色内容目录，即 Human 指定的“08 文件夹”。
- `01_os/07_content/_runs/`：OS 指定的领域任务运行证据位置，不是特色业务实现的存放位置。
- 进入任务仍先读根级 `AGENTS.md` 和 `01_os` 两份入口；处理本目录时同时遵循本目录的 `AGENTS.md`。

当前没有导入任何特色业务资料、既有游戏工程或旧仓库内容；这里只提供 OS 基础和初始化说明。
不创建 `08_os`，它不是新的 OS 副本；不把业务代码塞进共享机制目录。

## 上游与更新

- 自身仓库：`https://github.com/chris2gao/Cybernetic_City_State_OS_v2---nba2k22`，`origin` 的默认推送只指向本仓库。
- OS 上游：`https://github.com/chris2gao/Cybernetic_City_State_OS_v2---core`，通过 `core` 远端读取。
- 初始 OS 提交：`3ae48d2183a6e77d63a43783c7e1999edc01711e`。这是创建基线，不冒充以后每次升级后的当前版本。
- 新仓库保留与 core 的共同 Git 历史，不使用复制粘贴覆盖 OS。

需要更新 OS 时，由 Human 发起对应升级任务，按 OS 的范围、验证和发布纪律执行：

```powershell
git fetch core --no-tags
git merge core/master
```

共享 core 不修改本目录，因此正常的三方合并保留本领域资料。
若发生冲突，不强行覆盖、不重写历史；先说明冲突，再按当前任务权限解决。
没有启动自动拉取、自动合并、后台进程或定时器。

## 本次启用依据

Human 于 2026-10-22 明确要求创建并启用这六个领域仓库、以后按需接收 OS 更新。
这项较新的明确指令是本仓库的启用依据，替代 `CORE_MANIFEST.yml` 中 2026-08-02
“core 仍在建设期”的旧冻结要求对本次新建与后续明确请求升级的限制。
未在领域仓库改写那份 core-owned manifest；也未解除其他任务的安全、范围和发布门禁。
具体配置见 `domain.yml`。本次只配置仓库，不自动执行任何特色业务任务。
