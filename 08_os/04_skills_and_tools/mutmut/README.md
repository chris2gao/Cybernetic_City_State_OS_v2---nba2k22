# mutmut

## 已验证形态

- 版本：`3.6.0`
- 环境：WSL2 Ubuntu 的 Linux 文件系统工作区
- 安装边界：专用 user-owned virtualenv；不依赖系统级安装，不使用 `sudo`
- 挂载：`verified_on_demand`
- 默认加载：否
- MCP 暴露：否
- 证据：`08_os/_runs/run-013-mutmut安装接入验证/07_测试执行/results.json`

## OS 职责

mutmut 用于测量现有 Python 测试是否能区分代码的小幅语义变化。它能把“大量源代码
与测试”压缩成较小的 surviving-mutant 审阅面，但不能证明程序正确，也不能把
survivor 自动判定为缺陷。

run-013 的校准先保留一个真实测试缺口，再增强断言并杀死该 survivor；真实目标
`inspect_schema_refs.py` 的 129 个 mutants 最终为 127 killed、2 survived。
两项 survivor 都有可执行的等价性证明：`ensure_ascii=None` 与 `False` 进入同一
falsey 分支，`UTF-8` 与 `utf-8` 解析为同一 codec。

## 调用边界

任务必须显式提供：

- WSL Linux 文件系统中的干净 Git worktree；
- 专用 virtualenv 和精确版本 `3.6.0`；
- 一个 repository 内的 mutation project；
- 一个 repository 内的 Python 单文件目标；
- 至少一个与目标完全匹配的 allowlist 条目；
- 一个先行通过的 baseline test。

canonical wrapper 是
`08_os/06_execution/tools/mutmut/invoke.sh`。它从 `HEAD` 归档项目到 `/tmp`，
复制 allowlisted 目标，先跑 baseline，再运行 mutation；退出时只清理其创建的
精确临时目录。wrapper 不提供 `mutmut apply`，也不会更改 canonical source。

## 限制与复验

- Windows 挂载目录 `/mnt/**` 不是已验证工作区。
- virtualenv 是机器态前置条件，不进入仓库，也不进入默认 boot。
- exact model token、可靠的整棵进程峰值内存和网络包行为均未直接观测；不得据此
  声称精确 token 节省、峰值内存或零网络。
- mutmut、Python、wrapper、目标配置或测试语义变化后，必须重跑 run-013 的完整
  校准、真实目标、边界和 repository-state 验证。
