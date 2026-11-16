#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""execution_fact_monitor 的聚焦验证（围绕真实完成条件，不引入测试框架）。

运行方式（二者皆可）:
    python test_factmon.py
    python -m pytest test_factmon.py -q
"""

import json
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import factmon


def test_parse_custom_tool_call():
    obj = {
        "timestamp": "2026-11-15T14:19:59Z", "ordinal": 1, "type": "response_item",
        "payload": {"type": "custom_tool_call", "id": "ctc_1", "call_id": "call_1",
                    "name": "exec", "status": "completed", "input": "ls"},
    }
    rec = factmon.parse_line(obj, {"file": "x.jsonl", "line": 1})
    assert rec["kind"] == "tool_call"
    assert rec["subtype"] == "custom"
    assert rec["tool"] == "exec"
    assert rec["call_id"] == "call_1"
    assert rec["status"] == "completed"


def test_parse_command_execution_error():
    obj = {
        "timestamp": "t", "ordinal": 2, "type": "event_msg",
        "payload": {"type": "item_completed", "item": {
            "type": "CommandExecution", "command": ["pwsh", "-Command", "gh api"],
            "status": "failed", "exit_code": 1, "aggregated_output": "TLS timeout",
            "duration_ms": 500,
        }},
    }
    rec = factmon.parse_line(obj, {"file": "x.jsonl", "line": 2})
    assert rec["kind"] == "execution"
    assert rec["subtype"] == "command"
    assert rec["exit_code"] == 1
    assert rec["error"] == "status=failed exit_code=1"


def test_parse_file_change_strips_content():
    obj = {
        "type": "event_msg",
        "payload": {"type": "item_completed", "item": {
            "type": "FileChange", "changes": {"a.txt": {"type": "add", "content": "BIGSECRET"}},
        }},
    }
    rec = factmon.parse_line(obj, {"file": "x.jsonl", "line": 3})
    assert rec["kind"] == "execution"
    assert rec["subtype"] == "file_change"
    assert "content" not in rec["files"]["a.txt"]
    assert rec["files"]["a.txt"]["type"] == "add"


def test_parse_ignores_reasoning_and_message():
    for pt in ("message", "reasoning"):
        obj = {"type": "response_item", "payload": {"type": pt, "content": "x"}}
        assert factmon.parse_line(obj, {"file": "x", "line": 1}) is None
    # 非执行 event_msg 也忽略
    obj = {"type": "event_msg", "payload": {"type": "token_count", "info": {}}}
    assert factmon.parse_line(obj, {"file": "x", "line": 1}) is None


def test_replay_and_report():
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        lines = [
            json.dumps({"timestamp": "2026-11-15T00:00:00Z", "ordinal": 1, "type": "response_item",
                        "payload": {"type": "custom_tool_call", "id": "c1", "call_id": "k1",
                                    "name": "exec", "status": "completed", "input": "ls"}}),
            json.dumps({"timestamp": "2026-11-15T00:00:01Z", "ordinal": 2, "type": "response_item",
                        "payload": {"type": "custom_tool_call_output", "call_id": "k1",
                                    "output": [{"type": "input_text", "text": "done"}]}}),
            json.dumps({"timestamp": "2026-11-15T00:00:02Z", "ordinal": 3, "type": "event_msg",
                        "payload": {"type": "item_completed", "item": {
                            "type": "CommandExecution", "command": ["pwsh"], "status": "failed",
                            "exit_code": 1, "aggregated_output": "boom"}}}),
        ]
        session = td / "session.jsonl"
        session.write_text("\n".join(lines) + "\n", encoding="utf-8")

        args = type("A", (), {"session": str(session), "out": str(td / "out")})()
        events = factmon.cmd_replay(args)
        assert Path(events).exists()
        recs = [json.loads(l) for l in Path(events).read_text(encoding="utf-8").splitlines()]
        assert len(recs) == 3

        rargs = type("A", (), {"events": events, "out": str(td / "out")})()
        report = factmon.cmd_report(rargs)
        assert Path(report).exists()
        md = Path(report).read_text(encoding="utf-8")
        assert "tool_call" in md and "execution" in md


def test_watch_stops_on_keyboard_interrupt():
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        session = td / "s.jsonl"
        session.write_text(
            json.dumps({"type": "response_item",
                        "payload": {"type": "custom_tool_call", "name": "exec", "input": "x"}}) + "\n",
            encoding="utf-8",
        )
        real_sleep = factmon.time.sleep

        def fake_sleep(_interval):
            raise KeyboardInterrupt

        factmon.time.sleep = fake_sleep
        try:
            args = type("A", (), {"session": str(session), "out": str(td / "o"), "interval": 0.1})()
            events = factmon.cmd_watch(args)
        finally:
            factmon.time.sleep = real_sleep
        assert isinstance(events, str) and events.endswith("events.jsonl")


def _run():
    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    failed = 0
    import traceback
    for t in tests:
        try:
            t()
            print("PASS", t.__name__)
        except Exception:
            failed += 1
            print("FAIL", t.__name__)
            traceback.print_exc()
    return failed


if __name__ == "__main__":
    sys.exit(1 if _run() else 0)
