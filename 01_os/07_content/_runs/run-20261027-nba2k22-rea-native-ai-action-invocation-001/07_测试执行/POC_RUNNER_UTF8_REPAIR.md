# 首次启动的UTF8许可读取修正

管理员Windows PowerShell的默认ANSI读取破坏含中文的许可JSON，ConvertFrom-Json在读取许可时失败。该检查在获取游戏进程/写target记录/启动REA之前，输出目录只有admin-error.txt与准备文件；没有REA Evidence、没有进程attach、没有Native调用，3次调用预算尚未消耗。

将runner读取许可文件显式设为`-Encoding UTF8`，保留相同已批准JS SHA256，使用新输出目录执行。此为一次有明确编码错误证据的启动修复，不重复任何已产生游戏副作用的操作；原错误保留在本机poc-01/admin-error.txt。
