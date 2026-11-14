"""Index visible GE-01 events/tool records, excluding private model reasoning."""
from collections import Counter
from datetime import datetime, timezone
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path("C:/Users/gk/Documents/ChatGPT/nba2k22/ge01-runtime")
SESSION = Path("C:/Users/gk/.codex/sessions/2026/11/12/rollout-2026-11-12T02-44-00-01a1cf5b-78c5-7d32-815a-a8f6a647ed38.jsonl")
START = datetime.fromtimestamp(1794641285, timezone.utc)
END = datetime.fromtimestamp((ROOT / "REPAIR_01_RESULT.json").stat().st_mtime, timezone.utc)


def timestamp(value):
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def text_of(payload):
    if isinstance(payload.get("message"), str):
        return payload["message"]
    content = payload.get("content", [])
    return "\n".join(part.get("text", "") for part in content if isinstance(part, dict))


def main():
    events, pending, durations, markers = [], {}, [], {}
    output_flags = Counter()
    with SESSION.open(encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, 1):
            row = json.loads(line)
            stamp = row.get("timestamp")
            if not stamp or timestamp(stamp) < START or timestamp(stamp) > END:
                continue
            payload = row.get("payload", {})
            kind = payload.get("type")
            event = {"timestamp": stamp, "session_line": line_number, "record_type": row.get("type"), "kind": kind,
                     "source_record_sha256": hashlib.sha256(line.encode()).hexdigest()}
            if ((row.get("type") == "event_msg" and kind == "user_message")
                    or (row.get("type") == "response_item" and kind == "message" and payload.get("role") == "user")):
                body = text_of(payload)
                if "<codex_internal_context" in body or "<environment_context>" in body:
                    continue
                event.update(role="user", text=body)
                for key, needle in (("human_rebase", "我建议就以这个为原始的，开始"),
                                    ("human_approval", '"answer":"批准封套及既有资格证据复用，开始执行"'),
                                    ("one_repair_limit", "只修复一次，如果没解决就停止任务")):
                    if needle in body.replace('"answer": "', '"answer":"'):
                        markers.setdefault(key, stamp)
            elif row.get("type") == "response_item" and kind in ("function_call", "custom_tool_call"):
                arguments = payload.get("arguments", payload.get("input", ""))
                if not isinstance(arguments, str):
                    arguments = json.dumps(arguments, ensure_ascii=False)
                event.update(tool=payload.get("name"), call_id=payload.get("call_id"), arguments=arguments)
                pending[event["call_id"]] = (stamp, event["tool"])
                if "await tools.mcp__rea__start_frida_session(" in arguments:
                    markers.setdefault("first_live_read", stamp)
                if event["tool"] == "request_user_input_async" and "f539bdbef71c324" in arguments:
                    markers.setdefault("approval_question", stamp)
            elif row.get("type") == "response_item" and kind in ("function_call_output", "custom_tool_call_output"):
                output = payload.get("output", "")
                encoded = output if isinstance(output, str) else json.dumps(output, ensure_ascii=False)
                event.update(call_id=payload.get("call_id"), output_bytes=len(encoded.encode()),
                             output_sha256=hashlib.sha256(encoded.encode()).hexdigest(),
                             content="Raw output stays at the indexed session line; no bulk source/data duplication")
                for flag in ("Cannot find path", "does not exist", "TLS handshake timeout", "Schedule fixture differs", "VALIDATION_ERROR"):
                    if flag in encoded:
                        output_flags[flag] += 1
                if event["call_id"] in pending:
                    started, name = pending.pop(event["call_id"])
                    elapsed = (timestamp(stamp) - timestamp(started)).total_seconds()
                    event["tool"] = name
                    event["call_seconds"] = elapsed
                    durations.append({"tool": name, "start": started, "stop": stamp, "seconds": elapsed})
            elif row.get("type") == "response_item" and kind == "message" and payload.get("role") == "assistant" and payload.get("channel") in ("commentary", "final"):
                event.update(role="assistant", channel=payload["channel"], text=text_of(payload))
            else:
                continue
            events.append(event)
    files = {
        "initial_capture_done": ROOT / "FRESH_BASELINE_RECEIPT.json",
        "second_capture_done": ROOT / "clean-0005-01/FRESH_BASELINE_RECEIPT.json",
        "w01_plan_ready": ROOT / "GE01_W01_PLAN.json",
        "review_envelope_ready": ROOT / "GE01_W01_REVIEW_ENVELOPE.json",
        "first_calendar_start": ROOT / "ENTRY_STARTED.json",
        "first_calendar_result": ROOT / "ENTRY_RESULT.json",
        "repair_start": ROOT / "REPAIR_01_STARTED.json",
        "repair_result": ROOT / "REPAIR_01_RESULT.json",
    }
    artifacts = []
    for name, path in files.items():
        raw = path.read_bytes()
        observed = datetime.fromtimestamp(path.stat().st_mtime, timezone.utc).isoformat()
        markers[name] = observed
        artifacts.append({"name": name, "path": str(path.relative_to(ROOT)), "last_write_utc": observed,
                          "sha256": hashlib.sha256(raw).hexdigest(), "bytes": len(raw)})
    markers["goal_start"] = START.isoformat()
    ordered = sorted(markers.items(), key=lambda item: timestamp(item[1]))
    spans = [{"from": first[0], "to": second[0], "start": first[1], "stop": second[1],
              "seconds": (timestamp(second[1]) - timestamp(first[1])).total_seconds()}
             for first, second in zip(ordered, ordered[1:])]
    report = {"start_basis": "current goal.createdAt=1794641285; session corroboration indexed", "markers": dict(ordered),
              "business_execution_cutoff": END.isoformat(),
              "seconds_to_first_calendar_attempt": (timestamp(markers["first_calendar_start"]) - START).total_seconds(),
              "seconds_to_repair_result": (timestamp(markers["repair_result"]) - START).total_seconds(),
              "events": events, "spans": spans, "artifacts": artifacts,
              "tool_calls": len(durations), "tool_call_wall_seconds_sum": sum(item["seconds"] for item in durations),
              "tool_calls_before_first_calendar": sum(timestamp(item["start"]) < timestamp(markers["first_calendar_start"]) for item in durations),
              "tool_call_wall_seconds_before_first_calendar": sum(item["seconds"] for item in durations if timestamp(item["stop"]) <= timestamp(markers["first_calendar_start"])),
              "longest_tool_calls": sorted(durations, key=lambda item: item["seconds"], reverse=True)[:12],
              "output_error_flags": dict(output_flags),
              "output_error_flag_scope": "Substring appearances in retained outputs, including quoted source and repeat reads; not unique failure counts",
              "limits": ["tool wall sums may overlap background child work", "unoccupied intervals include model generation, host scheduling, user interaction and delivery; no precise inference-only attribution", "private reasoning is excluded", "file mtime markers are executor-side artifacts, not independent signed timestamps"]}
    (ROOT / "GE01_EXECUTION_TIMELINE.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with (ROOT / "GE01_EXECUTION_EVENTS.csv").open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=("timestamp", "session_line", "kind", "tool", "role", "call_seconds", "summary"))
        writer.writeheader()
        for event in events:
            writer.writerow({key: event.get(key, "") for key in writer.fieldnames if key != "summary"} |
                            {"summary": event.get("text", event.get("arguments", event.get("content", "")))[:1000]})
    print(json.dumps({key: value for key, value in report.items() if key in ("markers", "seconds_to_first_calendar_attempt", "seconds_to_repair_result", "tool_calls", "tool_call_wall_seconds_sum", "output_error_flags")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
