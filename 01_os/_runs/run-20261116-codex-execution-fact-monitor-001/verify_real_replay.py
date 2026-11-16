"""Explicit NBA44 native-log verification; keeps extracted records outside Git."""
import hashlib
import json
from pathlib import Path
import sys
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / '01_os/06_execution/task_orchestration/execution_fact_monitor'))
import factmon


def main():
    source = Path(sys.argv[1])
    out = Path(sys.argv[2])
    before = hashlib.sha256(source.read_bytes()).hexdigest()
    events = factmon.cmd_replay(SimpleNamespace(session=str(source), out=str(out)))
    report = factmon.cmd_report(SimpleNamespace(events=events, out=None))
    rows = [json.loads(line) for line in Path(events).read_text(encoding='utf-8').splitlines()]
    by_line = {r['source'].get('line'): r for r in rows}
    expected_commands = expected_mcp = 0
    for line_no, line in enumerate(source.open(encoding='utf-8'), 1):
        obj = json.loads(line)
        payload = obj.get('payload', {})
        if obj.get('type') == 'response_item' and payload.get('type') in ('function_call', 'custom_tool_call', 'function_call_output', 'custom_tool_call_output'):
            assert by_line[line_no]['call_id'] == payload.get('call_id')
        if obj.get('type') != 'event_msg' or payload.get('type') != 'item_completed':
            continue
        item = payload.get('item', {})
        if item.get('type') == 'CommandExecution':
            expected_commands += 1
            rec = by_line[line_no]
            assert rec['command'] == item['command'] and rec['exit_code'] == item.get('exit_code')
            duration = item.get('duration')
            if duration:
                assert rec['duration_ms'] == duration['secs'] * 1000 + duration['nanos'] / 1000000
        elif item.get('type') == 'McpToolCall':
            expected_mcp += 1
            assert by_line[line_no]['params'] == item.get('arguments')
            assert json.loads(by_line[line_no]['result']) == item.get('result')
    assert expected_commands > 0 and expected_mcp > 0
    assert before == hashlib.sha256(source.read_bytes()).hexdigest()
    assert '模型推理' in Path(report).read_text(encoding='utf-8')
    summary = {'source': str(source), 'sha256_before_and_after': before, 'records': len(rows),
               'native_commands_verified': expected_commands, 'native_mcp_verified': expected_mcp,
               'events': events, 'report': report, 'source_modified': False}
    (out / 'verification.json').write_text(json.dumps(summary, indent=2), encoding='utf-8')
    print(json.dumps(summary))


if __name__ == '__main__':
    main()
