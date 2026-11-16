# execution_fact_monitor

只读解析 Codex 原生日志、生成执行事实记录的本地前台工具。默认关闭，不修改源日志，
也不修改官方 Codex 程序。只采集 Codex 已经产生的执行事件，不捕获模型消息或推理内容。

## 命令

```powershell
# 读取已有 Codex 会话（一次性回放）
python factmon.py replay --session "会话日志.jsonl" --out ".\debug_output"

# 显式开启前台增量监控（Ctrl+C 停止，退出并释放资源）
python factmon.py watch --session "会话日志.jsonl" --out ".\debug_output"

# 由事件记录生成 Human 报告
python factmon.py report --events ".\debug_output\events.jsonl"
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

## 验证

```powershell
python test_factmon.py
```
