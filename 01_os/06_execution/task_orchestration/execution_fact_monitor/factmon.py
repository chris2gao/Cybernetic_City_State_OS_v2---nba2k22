#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Codex 执行事实监控工具 (execution-fact monitor).

只读解析 Codex 原生日志（rollout-*.jsonl），把可观测的执行事件转换成统一
JSONL 记录，并生成 Human 可读的 Markdown 报告。前台命令行为主，默认关闭，
不修改官方 Codex 程序，也不修改源日志。

本工具只采集 Codex 已经产生的执行事件：工具调用 (custom_tool_call /
function_call)、工具结果 (custom_tool_call_output / function_call_output)，
以及 item_completed 中的实际执行项 (CommandExecution / FileChange /
McpToolCall)。不捕获模型消息或推理内容，不判断行为是否合理。

用法:
  python factmon.py replay --session <log.jsonl> --out <dir>
  python factmon.py watch  --session <log.jsonl> --out <dir> [--interval 1.0]
  python factmon.py report --events <events.jsonl> [--out <dir>]
"""

import argparse
import json
import os
import time

SCHEMA_VERSION = "execution_fact_monitor.v1"

# response_item 中属于“工具调用”与“工具结果”的 payload 类型
TOOL_CALL_TYPES = {"custom_tool_call": "custom", "function_call": "function"}
TOOL_RESULT_TYPES = {"custom_tool_call_output": "custom", "function_call_output": "function"}

# item_completed 中属于“实际执行”的 item 类型
EXEC_ITEM_TYPES = {
    "CommandExecution": "command",
    "FileChange": "file_change",
    "McpToolCall": "mcp",
}

# 可观测的失败/错误状态
_ERROR_STATUSES = {"failed", "error", "cancelled", "incomplete"}


def normalize_text(value):
    """把 output/aggregated_output 归一成单一字符串。未知返回 None。"""
    if value is None:
        return None
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        parts = []
        for item in value:
            if isinstance(item, dict) and "text" in item:
                parts.append(str(item.get("text", "")))
            else:
                parts.append(json.dumps(item, ensure_ascii=False))
        return "".join(parts)
    if isinstance(value, (dict, int, float, bool)):
        return json.dumps(value, ensure_ascii=False)
    return str(value)


def _strip_file_content(changes):
    """只保留文件路径与变更类型，丢弃整段内容（事实只到“哪个文件被增改”）。"""
    if not isinstance(changes, dict):
        return changes
    out = {}
    for path, meta in changes.items():
        if isinstance(meta, dict):
            out[path] = {"type": meta.get("type")}
        else:
            out[path] = {"type": str(meta)}
    return out


def parse_line(obj, source):
    """把一个原始 JSONL 对象转换成统一事件记录；非执行事件返回 None。"""
    if not isinstance(obj, dict):
        return None
    otype = obj.get("type")
    payload = obj.get("payload")
    if not isinstance(payload, dict):
        return None

    if otype == "response_item":
        pt = payload.get("type")
        if pt in TOOL_CALL_TYPES:
            return {
                "schema": SCHEMA_VERSION,
                "kind": "tool_call",
                "subtype": TOOL_CALL_TYPES[pt],
                "time": obj.get("timestamp"),
                "ordinal": obj.get("ordinal"),
                "tool": payload.get("name"),
                "call_id": payload.get("call_id") or payload.get("id"),
                "status": payload.get("status"),
                "params": payload.get("input"),
                "source": source,
            }
        if pt in TOOL_RESULT_TYPES:
            return {
                "schema": SCHEMA_VERSION,
                "kind": "tool_result",
                "subtype": TOOL_RESULT_TYPES[pt],
                "time": obj.get("timestamp"),
                "ordinal": obj.get("ordinal"),
                "tool": payload.get("name"),
                "call_id": payload.get("call_id") or payload.get("id"),
                "result": normalize_text(payload.get("output")),
                "source": source,
            }
        return None

    if otype == "event_msg" and payload.get("type") == "item_completed":
        item = payload.get("item")
        if not isinstance(item, dict):
            return None
        itype = item.get("type")
        if itype not in EXEC_ITEM_TYPES:
            return None
        rec = {
            "schema": SCHEMA_VERSION,
            "kind": "execution",
            "subtype": EXEC_ITEM_TYPES[itype],
            "time": obj.get("timestamp"),
            "ordinal": obj.get("ordinal"),
            "tool": item.get("tool") if itype == "McpToolCall" else None,
            "status": item.get("status"),
            "exit_code": item.get("exit_code"),
            "command": item.get("command"),
            "cwd": item.get("cwd"),
            "server": item.get("server"),
            "params": item.get("arguments") if itype == "McpToolCall" else None,
            "files": _strip_file_content(item.get("changes")) if itype == "FileChange" else None,
            "result": normalize_text(item.get("aggregated_output") or item.get("output")),
            "duration_ms": item.get("duration_ms"),
            "source": source,
        }
        # 错误只在可观测时记录：status=failed/error/... 或 exit_code 非 0
        err = None
        st = rec["status"]
        ec = rec["exit_code"]
        if isinstance(st, str) and st.lower() in _ERROR_STATUSES:
            err = "status=%s" % st
        if ec not in (None, 0):
            err = ("%s " % err if err else "") + "exit_code=%s" % ec
        rec["error"] = err
        return rec

    return None


def iter_records(path):
    """逐行读取会话日志，产出统一事件记录。跳过无法解析的行。"""
    with open(path, "r", encoding="utf-8", errors="replace") as fh:
        for line_no, line in enumerate(fh, 1):
            line = line.strip()
            if not line:
                continue
            try:
                obj = json.loads(line)
            except json.JSONDecodeError:
                continue
            rec = parse_line(obj, {"file": path, "line": line_no})
            if rec is not None:
                yield rec


def write_record(out_path, rec):
    with open(out_path, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=False) + "\n")


# --------------------------------------------------------------------------- #
# 子命令
# --------------------------------------------------------------------------- #

def cmd_replay(args):
    os.makedirs(args.out, exist_ok=True)
    events_path = os.path.join(args.out, "events.jsonl")
    if os.path.exists(events_path):
        os.remove(events_path)
    n = 0
    for rec in iter_records(args.session):
        write_record(events_path, rec)
        n += 1
    print("replay done: %d execution records -> %s" % (n, events_path))
    return events_path


def cmd_watch(args):
    os.makedirs(args.out, exist_ok=True)
    events_path = os.path.join(args.out, "events.jsonl")
    offset = os.path.getsize(args.session)
    interval = args.interval
    print("watching %s" % args.session)
    print("  from byte %d, interval %.1fs, Ctrl+C to stop" % (offset, interval))
    start = time.time()
    n = 0
    pending = b""
    base_offset = offset
    try:
        while True:
            size = os.path.getsize(args.session)
            if size < offset:
                # 文件被截断/轮转：从开头重新开始
                offset = 0
                pending = b""
                base_offset = 0
            if size > offset:
                with open(args.session, "rb") as fh:
                    fh.seek(offset)
                    data = fh.read(size - offset)
                offset = size
                pending += data
                parts = pending.split(b"\n")
                pending = parts[-1]
                pos = 0
                for part in parts[:-1]:
                    line_start = base_offset + pos
                    pos += len(part) + 1
                    line = part.decode("utf-8", errors="replace").strip()
                    if not line:
                        continue
                    try:
                        obj = json.loads(line)
                    except json.JSONDecodeError:
                        continue
                    rec = parse_line(obj, {"file": args.session, "offset": line_start})
                    if rec is not None:
                        write_record(events_path, rec)
                        n += 1
                base_offset = offset - len(pending)
            time.sleep(interval)
    except KeyboardInterrupt:
        pass
    elapsed = time.time() - start
    print("\nstopped: %d execution records in %.1fs -> %s" % (n, elapsed, events_path))
    return events_path


def _truncate(s, n=240):
    if s is None:
        return None
    s = str(s)
    if len(s) > n:
        return s[:n] + " …[截断]"
    return s


def _sort_key(rec):
    o = rec.get("ordinal")
    t = rec.get("time") or ""
    return (o if o is not None else float("inf"), t)


def cmd_report(args):
    recs = []
    with open(args.events, "r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                recs.append(json.loads(line))
            except json.JSONDecodeError:
                continue
    recs.sort(key=_sort_key)

    out_dir = args.out or os.path.dirname(os.path.abspath(args.events))
    os.makedirs(out_dir, exist_ok=True)
    report_path = os.path.join(out_dir, "report.md")

    results_by_call = {}
    calls = []
    for rec in recs:
        if rec.get("kind") == "tool_result" and rec.get("call_id"):
            results_by_call[rec["call_id"]] = rec
        elif rec.get("kind") == "tool_call":
            calls.append(rec)

    matched_call_ids = set(results_by_call.keys())

    def count(pred):
        return sum(1 for r in recs if pred(r))

    total = len(recs)
    n_call = count(lambda r: r.get("kind") == "tool_call")
    n_result = count(lambda r: r.get("kind") == "tool_result")
    n_exec = count(lambda r: r.get("kind") == "execution")
    n_cmd = count(lambda r: r.get("subtype") == "command")
    n_fc = count(lambda r: r.get("subtype") == "file_change")
    n_mcp = count(lambda r: r.get("subtype") == "mcp")
    n_err = count(lambda r: r.get("error"))
    n_no_result = sum(1 for c in calls if c.get("call_id") not in results_by_call)
    n_no_time = count(lambda r: not r.get("time"))

    times = [r["time"] for r in recs if r.get("time")]
    session_hint = next(
        (r["source"]["file"] for r in recs if r.get("source", {}).get("file")), None
    )

    L = []
    L.append("# Codex 执行事实报告")
    L.append("")
    if session_hint:
        L.append("- 源会话日志: `%s`" % session_hint)
    L.append("- 事件记录文件: `%s`" % args.events)
    L.append("- 生成时间: %s" % time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    L.append("- 事件记录数: %d" % total)
    L.append("")
    L.append("## 概览")
    L.append("")
    L.append("| 指标 | 值 |")
    L.append("|---|---|")
    L.append("| 工具调用 (custom/function) | %d |" % n_call)
    L.append("| 工具结果 | %d |" % n_result)
    L.append("| 实际执行 (命令/文件/MCP) | %d (%d / %d / %d) |" % (n_exec, n_cmd, n_fc, n_mcp))
    L.append("| 失败/错误 | %d |" % n_err)
    L.append("| 无结果匹配的调用 | %d |" % n_no_result)
    L.append("| 时间缺失记录 | %d |" % n_no_time)
    if times:
        L.append("| 时间范围 | %s → %s |" % (min(times), max(times)))
    L.append("")
    L.append("## 执行事实时间线")
    L.append("")
    L.append("按来源顺序排列。`UNOBSERVED` 表示源日志未提供可证明的信息。")
    L.append("")

    for rec in recs:
        if rec.get("kind") == "tool_result" and rec.get("call_id") in matched_call_ids:
            continue  # 已匹配结果，内联到对应调用下方
        t = rec.get("time") or "时间不可观测"
        L.append(
            "- **%s** · `%s` · `%s` · %s"
            % (t, rec.get("kind"), rec.get("subtype"), rec.get("tool") or "-")
        )
        if rec.get("kind") == "tool_call":
            if rec.get("params") is not None:
                L.append("  - 参数: `%s`" % _truncate(rec["params"]))
            if rec.get("status"):
                L.append("  - 状态: `%s`" % rec["status"])
            res = results_by_call.get(rec.get("call_id"))
            if res is not None:
                L.append("  - 结果: %s" % (_truncate(res.get("result")) or "（空）"))
            else:
                L.append("  - 结果: **UNOBSERVED**（源日志未提供匹配结果）")
        elif rec.get("kind") == "execution":
            if rec.get("command"):
                L.append("  - 命令: `%s`" % _truncate(" ".join(rec["command"]), 200))
            if rec.get("server"):
                L.append("  - MCP server: `%s`" % rec["server"])
            if rec.get("params") is not None:
                L.append("  - 参数: `%s`" % _truncate(rec["params"]))
            if rec.get("files"):
                L.append("  - 变更文件: `%s`" % _truncate(", ".join(rec["files"].keys()), 200))
            if rec.get("cwd"):
                L.append("  - cwd: `%s`" % _truncate(rec["cwd"]))
            if rec.get("status"):
                L.append("  - 状态: `%s`" % rec["status"])
            if rec.get("exit_code") is not None:
                L.append("  - 退出码: `%s`" % rec["exit_code"])
            if rec.get("duration_ms") is not None:
                L.append("  - 耗时: %s ms" % rec["duration_ms"])
            if rec.get("error"):
                L.append("  - 错误: `%s`" % rec["error"])
            if rec.get("result"):
                L.append("  - 输出: %s" % _truncate(rec["result"]))
        elif rec.get("kind") == "tool_result":
            L.append("  - 结果: %s" % (_truncate(rec.get("result")) or "（空）"))
        L.append("")

    L.append("## 说明")
    L.append("")
    L.append("本报告只陈述源日志可证明的执行事实，不分析模型推理，也不判断行为是否合理。")
    L.append("无结果匹配的调用、时间缺失与 `UNOBSERVED` 项均按源日志实际可观测性标记。")

    with open(report_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(L) + "\n")
    print("report done -> %s" % report_path)
    return report_path


def main(argv=None):
    p = argparse.ArgumentParser(prog="factmon", description="Codex 执行事实监控工具（前台，默认关闭）")
    sub = p.add_subparsers(dest="cmd", required=True)

    r = sub.add_parser("replay", help="读取已有 Codex 会话日志，生成 events.jsonl")
    r.add_argument("--session", required=True, help="Codex rollout-*.jsonl 路径")
    r.add_argument("--out", required=True, help="输出目录")
    r.set_defaults(func=cmd_replay)

    w = sub.add_parser("watch", help="前台增量监控（Ctrl+C 停止）")
    w.add_argument("--session", required=True, help="Codex rollout-*.jsonl 路径")
    w.add_argument("--out", required=True, help="输出目录")
    w.add_argument("--interval", type=float, default=1.0, help="轮询间隔秒数")
    w.set_defaults(func=cmd_watch)

    g = sub.add_parser("report", help="由 events.jsonl 生成 report.md")
    g.add_argument("--events", required=True, help="events.jsonl 路径")
    g.add_argument("--out", default=None, help="报告输出目录（默认与 events 同目录）")
    g.set_defaults(func=cmd_report)

    args = p.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
