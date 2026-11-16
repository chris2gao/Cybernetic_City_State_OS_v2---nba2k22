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
from datetime import datetime

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
    if isinstance(changes, dict):
        return {path: {"type": _file_type(meta)} for path, meta in changes.items()}
    if isinstance(changes, list):
        return [{"path": item.get("path") if isinstance(item.get("path"), str) else None,
                 "type": _file_type(item)} for item in changes if isinstance(item, dict)]
    return None


def _file_type(meta):
    kind = meta.get("kind", meta.get("type")) if isinstance(meta, dict) else meta
    if isinstance(kind, dict):
        kind = kind.get("type")
    return kind if isinstance(kind, str) else None


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
                "call_id": payload.get("call_id"),
                "native_item_id": payload.get("id"),
                "status": payload.get("status"),
                "params": payload.get("arguments") if pt == "function_call" else payload.get("input"),
                "namespace": payload.get("namespace"),
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
                "call_id": payload.get("call_id"),
                "native_item_id": payload.get("id"),
                "result": normalize_text(payload.get("output")),
                "status": payload.get("status"),
                "error": payload.get("error"),
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
            "result": normalize_text(next((item[key] for key in ("aggregated_output", "output", "result", "stdout") if key in item and item[key] is not None), None)),
            "stderr": item.get("stderr"),
            "duration_ms": _duration_ms(item),
            "native_item_id": item.get("id"),
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
        result = item.get("result")
        if isinstance(result, dict):
            ok = result.get("Ok", result)
            if "Err" in result:
                err = normalize_text(result["Err"])
            elif isinstance(ok, dict) and ok.get("isError") is True:
                err = "MCP result.isError=true"
        if itype == "McpToolCall" and item.get("error") is not None:
            err = item["error"]  # 原生错误优先；状态和 result 仍分别保留。
        rec["error"] = err
        return rec

    return None


def _duration_ms(item):
    if item.get("duration_ms") is not None:
        return item["duration_ms"]
    duration = item.get("duration")
    if isinstance(duration, dict) and isinstance(duration.get("secs"), (int, float)) and isinstance(duration.get("nanos"), (int, float)):
        return duration["secs"] * 1000 + duration["nanos"] / 1_000_000
    return None


def _gap(source):
    return {"schema": SCHEMA_VERSION, "kind": "gap", "source": source,
            "time": None, "error": "INVALID_JSON_UNOBSERVED"}


def _guard_source(source, targets):
    for target in targets:
        same = os.path.normcase(os.path.realpath(source)) == os.path.normcase(os.path.realpath(target))
        if same or (os.path.exists(target) and os.path.samefile(source, target)):
            raise ValueError("output must not overwrite or append to source: %s" % target)


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
                yield _gap({"file": path, "line": line_no})
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
    _guard_source(args.session, [os.path.join(args.out, name) for name in ("events.jsonl", "report.md")])
    os.makedirs(args.out, exist_ok=True)
    events_path = os.path.join(args.out, "events.jsonl")
    with open(events_path, "w", encoding="utf-8"):
        pass
    n = 0
    for rec in iter_records(args.session):
        write_record(events_path, rec)
        n += 1
    print("replay done: %d execution records -> %s" % (n, events_path))
    return events_path


def cmd_watch(args):
    if args.interval <= 0:
        raise ValueError("interval must be positive")
    _guard_source(args.session, [os.path.join(args.out, name) for name in ("events.jsonl", "report.md")])
    os.makedirs(args.out, exist_ok=True)
    events_path = os.path.join(args.out, "events.jsonl")
    with open(events_path, "a", encoding="utf-8"):
        pass
    offset = os.path.getsize(args.session)
    interval = args.interval
    print("watching %s (pid=%d)" % (args.session, os.getpid()), flush=True)
    print("  from byte %d, interval %.1fs, Ctrl+C to stop" % (offset, interval), flush=True)
    start = time.monotonic()
    cpu_start = time.process_time()
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
                        write_record(events_path, _gap({"file": args.session, "offset": line_start}))
                        continue
                    rec = parse_line(obj, {"file": args.session, "offset": line_start})
                    if rec is not None:
                        write_record(events_path, rec)
                        n += 1
                base_offset = offset - len(pending)
            time.sleep(interval)
    except KeyboardInterrupt:
        pass
    elapsed = time.monotonic() - start
    print("\nstopped: %d execution records in %.3fs, monitor_cpu_seconds=%.6f, incomplete_tail_bytes=%d -> %s" % (n, elapsed, time.process_time() - cpu_start, len(pending), events_path))
    return events_path


def _truncate(s, n=240):
    if s is None:
        return None
    s = str(s)
    if len(s) > n:
        return s[:n] + " …[截断]"
    return s


def _sort_key(rec):
    try:
        stamp = datetime.fromisoformat(rec.get("time", "").replace("Z", "+00:00"))
        timestamp = stamp.timestamp() if stamp.utcoffset() is not None else float("inf")
    except (ValueError, TypeError, AttributeError):
        timestamp = float("inf")
    return timestamp


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
    report_path = os.path.join(out_dir, "report.md")
    _guard_source(args.events, [report_path])
    os.makedirs(out_dir, exist_ok=True)

    results_by_call = {}
    calls = []
    for rec in recs:
        if rec.get("kind") == "tool_result" and rec.get("call_id"):
            results_by_call.setdefault(rec["call_id"], []).append(rec)
        elif rec.get("kind") == "tool_call":
            calls.append(rec)

    matched_call_ids = {c.get("call_id") for c in calls} & set(results_by_call)

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
    L.append("| 无调用匹配的结果 | %d |" % sum(r.get("kind") == "tool_result" and r.get("call_id") not in matched_call_ids for r in recs))
    L.append("| JSON 无法解析的来源缺口 | %d |" % count(lambda r: r.get("kind") == "gap"))
    if times:
        L.append("| 时间范围 | %s → %s |" % (min(times), max(times)))
    L.append("")
    L.append("## 执行事实时间线")
    L.append("")
    L.append("按已知事件时间排列；无有效时间的记录保留来源顺序并列于末尾。`UNOBSERVED` 表示源日志未提供信息。")
    L.append("工具调用记录与实际执行项是不同层级，不能相加当作独立操作数。时间范围不是任务业务耗时；缺失区间不可归因。")
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
            else:
                L.append("  - 参数: UNOBSERVED")
            if rec.get("status"):
                L.append("  - 状态: `%s`" % rec["status"])
            results = results_by_call.get(rec.get("call_id"), [])
            if results:
                for res in results:
                    L.append("  - 结果: %s" % ("UNOBSERVED" if res.get("result") is None else _truncate(res["result"]) or "（空）"))
                    L.append("  - 结果时间: %s" % (res.get("time") or "UNOBSERVED"))
                    L.append("  - 结果来源: `%s`" % json.dumps(res.get("source"), ensure_ascii=False))
            else:
                L.append("  - 结果: **UNOBSERVED**（源日志未提供匹配结果）")
        elif rec.get("kind") == "execution":
            if rec.get("command"):
                command = rec["command"]
                L.append("  - 命令: `%s`" % _truncate(" ".join(command) if isinstance(command, list) else command, 200))
            if rec.get("server"):
                L.append("  - MCP server: `%s`" % rec["server"])
            if rec.get("params") is not None:
                L.append("  - 参数: `%s`" % _truncate(rec["params"]))
            if rec.get("files"):
                files = rec["files"]
                entries = files.items() if isinstance(files, dict) else ((item.get("path"), item) for item in files if isinstance(item, dict))
                L.append("  - 变更文件: `%s`" % _truncate(", ".join("%s (%s)" % (path or "UNOBSERVED", _file_type(meta) or "UNOBSERVED") for path, meta in entries), 200))
            if rec.get("cwd"):
                L.append("  - cwd: `%s`" % _truncate(rec["cwd"]))
            if rec.get("status"):
                L.append("  - 状态: `%s`" % rec["status"])
            if rec.get("exit_code") is not None:
                L.append("  - 退出码: `%s`" % rec["exit_code"])
            if rec.get("duration_ms") is not None:
                L.append("  - 耗时: %s ms" % rec["duration_ms"])
            if rec.get("error"):
                L.append("  - 错误: `%s`" % normalize_text(rec["error"]))
            if rec.get("result"):
                L.append("  - 输出: %s" % _truncate(rec["result"]))
        elif rec.get("kind") == "tool_result":
            L.append("  - 结果: %s" % ("UNOBSERVED" if rec.get("result") is None else _truncate(rec["result"]) or "（空）"))
        elif rec.get("kind") == "gap":
            L.append("  - 来源损坏/不完整：UNOBSERVED；%s" % rec.get("error"))
        if rec.get("kind") == "execution":
            L.append("  - 未提供字段: %s" % (", ".join(key for key in ("status", "duration_ms", "result") if rec.get(key) is None) or "无"))
        L.append("  - 来源: `%s`" % json.dumps(rec.get("source"), ensure_ascii=False))
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
