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
from types import SimpleNamespace


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


def test_native_duration_mcp_result_and_function_arguments():
    source = {"file": "native.jsonl", "line": 7}
    item = {"type": "McpToolCall", "server": "test", "tool": "read",
            "arguments": {"path": "x"}, "status": "completed",
            "duration": {"secs": 2, "nanos": 500000000},
            "result": {"Ok": {"isError": True, "content": [{"type": "text", "text": "denied"}]}}}
    rec = factmon.parse_line({"type": "event_msg", "payload": {"type": "item_completed", "item": item}}, source)
    assert rec["duration_ms"] == 2500 and 'denied' in rec["result"]
    assert rec["error"] == "MCP result.isError=true"
    call = factmon.parse_line({"type": "response_item", "payload": {"type": "function_call", "arguments": '{"cmd":"echo test"}'}}, source)
    assert call["params"] == '{"cmd":"echo test"}'
    orphan = factmon.parse_line({'type': 'response_item', 'payload': {'type': 'function_call_output', 'id': 'item-only', 'output': 'known result'}}, source)
    assert orphan['call_id'] is None and orphan['native_item_id'] == 'item-only'


def test_report_preserves_orphan_result_source_and_timestamp_order():
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        records = [
            {"kind": "tool_result", "call_id": "orphan", "result": "ORPHAN_RESULT", "time": "2026-01-01T00:00:02Z", "source": {"line": 4}},
            {"kind": "execution", "subtype": "command", "command": "echo one", "time": "2026-01-01T01:00:00+01:00", "source": {"line": 3}},
        ]
        events = td / 'events.jsonl'
        events.write_text('\n'.join(json.dumps(r) for r in records), encoding='utf-8')
        report = Path(factmon.cmd_report(SimpleNamespace(events=str(events), out=None))).read_text(encoding='utf-8')
        assert 'ORPHAN_RESULT' in report and 'echo one' in report
        assert report.index('echo one') < report.index('ORPHAN_RESULT')
        assert '"line": 4' in report and '未提供字段' in report


def test_output_cannot_modify_source_and_empty_replay_is_usable():
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        source = td / 'events.jsonl'
        source.write_text('SOURCE_BYTES', encoding='utf-8')
        args = SimpleNamespace(session=str(source), out=str(td), interval=0.01)
        for command in (factmon.cmd_replay, factmon.cmd_watch):
            try:
                command(args)
            except ValueError:
                pass
            else:
                raise AssertionError('source alias was accepted')
            assert source.read_text(encoding='utf-8') == 'SOURCE_BYTES'
        source.write_text('', encoding='utf-8')
        args.out = str(td / 'out')
        events = factmon.cmd_replay(args)
        assert Path(events).read_bytes() == b''
        assert Path(factmon.cmd_report(SimpleNamespace(events=events, out=None))).exists()


def test_watch_only_new_complete_lines_and_reports_incomplete_tail():
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        source = td / 'source.jsonl'
        old = {'type': 'response_item', 'payload': {'type': 'custom_tool_call', 'call_id': 'old', 'name': 'exec'}}
        source.write_text(json.dumps(old) + '\n', encoding='utf-8')
        new = {'type': 'response_item', 'payload': {'type': 'function_call', 'call_id': 'new', 'name': 'read', 'arguments': '{}'}}
        raw = (json.dumps(new) + '\n').encode()
        step = 0
        def advance(_interval):
            nonlocal step
            step += 1
            if step > 2:
                raise KeyboardInterrupt
            with source.open('ab') as fh:
                fh.write(raw[:20] if step == 1 else raw[20:])
        real_sleep = factmon.time.sleep
        factmon.time.sleep = advance
        try:
            events = factmon.cmd_watch(SimpleNamespace(session=str(source), out=str(td / 'out'), interval=0.01))
        finally:
            factmon.time.sleep = real_sleep
        rows = [json.loads(line) for line in Path(events).read_text(encoding='utf-8').splitlines()]
        assert len(rows) == 1 and rows[0]['call_id'] == 'new'
        offset = rows[0]['source']['offset']
        assert source.read_bytes()[offset:] == raw


def test_corrupt_line_is_an_explicit_gap_not_a_missing_success():
    with tempfile.TemporaryDirectory() as td:
        source = Path(td) / 'source.jsonl'
        source.write_text('{invalid\n', encoding='utf-8')
        rows = list(factmon.iter_records(str(source)))
        assert len(rows) == 1 and rows[0]['kind'] == 'gap'
        assert rows[0]['source']['line'] == 1


def test_file_change_array_strips_diff_and_renders_all_paths():
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        changes = [
            {'path': 'same.txt', 'kind': {'type': 'add'}, 'diff': {'text': 'HIDDEN_NATIVE_DIFF'}, 'content': 'HIDDEN_NATIVE_CONTENT'},
            {'path': 'same.txt', 'type': 'delete', 'diff': 'HIDDEN_NATIVE_DIFF'},
        ]
        obj = {'type': 'event_msg', 'payload': {'type': 'item_completed',
               'item': {'type': 'FileChange', 'changes': changes, 'status': 'completed'}}}
        rec = factmon.parse_line(obj, {'file': 'native.jsonl', 'line': 1})
        assert rec['files'] == [{'path': 'same.txt', 'type': 'add'}, {'path': 'same.txt', 'type': 'delete'}]
        assert 'HIDDEN_NATIVE' not in json.dumps(rec)
        events = td / 'events.jsonl'
        events.write_text(json.dumps(rec), encoding='utf-8')
        report = Path(factmon.cmd_report(SimpleNamespace(events=str(events), out=None))).read_text(encoding='utf-8')
        assert 'same.txt (add)' in report and 'same.txt (delete)' in report
        assert 'HIDDEN_NATIVE' not in report


def test_mcp_native_error_is_preserved_in_event_and_report():
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        error = {'message': 'native transport refused', 'code': -32000, 'details': {'stage': 'dispatch'}}
        item = {'type': 'McpToolCall', 'server': 'test', 'tool': 'read',
                'status': 'failed', 'error': error, 'result': {'Ok': {'isError': True}}}
        rec = factmon.parse_line({'type': 'event_msg', 'payload': {'type': 'item_completed', 'item': item}}, {'file': 'native.jsonl', 'line': 2})
        assert rec['error'] == error and rec['status'] == 'failed'
        assert json.loads(rec['result'])['Ok']['isError'] is True
        events = td / 'events.jsonl'
        events.write_text(json.dumps(rec), encoding='utf-8')
        report = Path(factmon.cmd_report(SimpleNamespace(events=str(events), out=None))).read_text(encoding='utf-8')
        assert 'native transport refused' in report and '-32000' in report and 'dispatch' in report


def test_multiple_results_keep_every_result_time_and_source():
    with tempfile.TemporaryDirectory() as td:
        td = Path(td)
        native = [
            {'timestamp': '2026-01-01T00:00:00Z', 'type': 'response_item', 'payload': {'type': 'custom_tool_call', 'call_id': 'shared', 'name': 'read', 'input': 'x'}},
        ]
        for index, (call_id, value) in enumerate([('shared', 'FIRST_RESULT'), ('shared', 'SECOND_RESULT'), ('orphan', 'ORPHAN_RESULT'), (None, 'NO_ID_RESULT')], 1):
            native.append({'timestamp': '2026-01-01T00:00:0%dZ' % index, 'type': 'response_item', 'payload': {'type': 'custom_tool_call_output', 'call_id': call_id, 'output': value}})
        session = td / 'source.jsonl'
        original = '\n'.join(json.dumps(obj) for obj in native)
        session.write_text(original, encoding='utf-8')
        events = factmon.cmd_replay(SimpleNamespace(session=str(session), out=str(td / 'out')))
        rows = [json.loads(line) for line in Path(events).read_text(encoding='utf-8').splitlines()]
        assert len(rows) == 5 and sum(r['kind'] == 'tool_call' for r in rows) == 1
        assert rows[-1]['call_id'] is None
        report = Path(factmon.cmd_report(SimpleNamespace(events=events, out=None))).read_text(encoding='utf-8')
        for value in ('FIRST_RESULT', 'SECOND_RESULT', 'ORPHAN_RESULT', 'NO_ID_RESULT'):
            assert report.count(value) == 1
        for line in range(2, 6):
            assert '"line": %d' % line in report
        assert '2026-01-01T00:00:01Z' in report and '2026-01-01T00:00:02Z' in report
        assert report.index('FIRST_RESULT') < report.index('SECOND_RESULT')
        assert '| 工具调用 (custom/function) | 1 |' in report and '| 工具结果 | 4 |' in report
        assert '| 无调用匹配的结果 | 2 |' in report
        assert session.read_text(encoding='utf-8') == original


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
