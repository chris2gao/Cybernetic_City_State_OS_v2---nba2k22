# execution_fact_monitor

只读解析 Codex 原生日志、生成执行事实记录的本地前台工具。默认关闭，不修改源日志，
也不修改官方 Codex 程序。只采集 Codex 已经产生的执行事件，不捕获模型消息或推理内容。

## 命令

```powershell
# 读取已有 Codex 会话（一次性回放）
python -B -X utf8 factmon.py replay --session "会话日志.jsonl" --out ".\debug_output"

# 显式开启前台增量监控（Ctrl+C 停止，退出并释放资源）
python -B -u -X utf8 factmon.py watch --session "会话日志.jsonl" --out ".\debug_output"

# 由事件记录生成 Human 报告
python -B -X utf8 factmon.py report --events ".\debug_output\events.jsonl"
```

## 产物

- `events.jsonl`：统一执行事件记录（机器可读，每行一个事件）。
- `report.md`：Human 可读执行事实报告（时间线 + 概览 + 错误/未知标注）。

## 采集范围

- `response_item`：`custom_tool_call` / `function_call`（工具调用）、
  `custom_tool_call_output` / `function_call_output`（工具结果）。
- `event_msg` `item_completed`：`CommandExecution`（实际命令 + 状态 + 退出码 + 输出）、
  `FileChange`（变更文件路径 + 类型，不复制内容）、`McpToolCall`（MCP server/tool/参数）。

不采集 `message` / `reasoning` / token 等模型内容；不判断操作是否合理。源日志缺字段时
标记 `UNOBSERVED`，不推断。

支持本机实际日志的 `duration: {secs,nanos}`、MCP `result` 和 function-call
`arguments`。调用与结果按原始 ID 关联；无调用的结果仍显示，不能假造其缺失调用。
每条事实保留源文件与行号（回放）或字节偏移（监控），不依靠文件快照或 Git diff。
报告按已知时间排序，正文截断处可查完整 events.jsonl。不同层级记录不能相加作为独立
操作数；源日志没有业务 Done、缺失结果或无归属时间时，工具不自动补算或判定。

## ON / OFF

只有手动运行 `watch` 才有附加监控。它从启动时文件末尾读取新增完整 JSONL 行，
不回放历史；需要历史时先使用 `replay`，watch 可在同一 events 文件追加。
不自动发现会话，不注册服务或后台任务。Ctrl+C 后退出，轮询和事件写盘均停止；
原生 Codex 日志继续由 Codex 自身产生。结束摘要给出监控 wall time、CPU seconds
（宿主分辨率限制下可能为零）及未完成尾行字节数。Windows 可在运行期间用
`Get-Process -Id <启动时显示的PID>` 测量 CPU、WorkingSet64 和 PrivateMemorySize64。
内存和 CPU 仅描述该次采样，不能外推为所有任务的固定开销。

空输入仍产生可用的空 events.jsonl；损坏 JSON 行作为来源缺口保留。输出不能覆盖或
追加到输入源。产物可能包含原始命令、参数和工具输出，默认仅在本地供 Human 调查，
发布前另行检查；不承诺自动脱敏。工具不会读取 Codex 的配置、凭据或日志数据库。

## 验证

```powershell
python test_factmon.py
```
