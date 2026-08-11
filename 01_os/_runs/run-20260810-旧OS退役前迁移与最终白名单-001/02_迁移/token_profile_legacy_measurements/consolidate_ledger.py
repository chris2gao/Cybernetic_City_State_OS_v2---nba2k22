#!/usr/bin/env python3
"""Safely aggregate de-identified token_profile_run.v1 records."""
from __future__ import annotations

import argparse, hashlib, json, os, tempfile
from collections import Counter
from pathlib import Path

DEFAULT_LEDGER = Path("C:/Users/gk/AppData/Local/CityState/token_ledger/runs/")
REQUIRED = {"schema_version", "task_id", "task_type", "provider", "model", "effort",
            "session_mode", "protocol_profile", "input_tokens", "output_tokens",
            "reasoning_tokens", "cache_read_tokens", "cache_write_tokens", "tool_output_bytes",
            "reported_cost", "wall_seconds", "repair_attempts", "review_rounds",
            "validation_result", "quality_incidents", "metric_source"}
NUMERIC = {"input_tokens", "output_tokens", "reasoning_tokens", "cache_read_tokens",
           "cache_write_tokens", "tool_output_bytes", "reported_cost", "wall_seconds",
           "repair_attempts", "review_rounds", "quality_incidents"}

def atomic_write(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data); handle.flush(); os.fsync(handle.fileno())
        os.replace(name, path)
    finally:
        if os.path.exists(name): os.unlink(name)

def valid_record(raw: object) -> bool:
    return isinstance(raw, dict) and raw.get("schema_version") == "token_profile_run.v1" and REQUIRED <= raw.keys() and all(raw[key] is None or isinstance(raw[key], (int, float)) and not isinstance(raw[key], bool) for key in NUMERIC)

def aggregate(ledger: Path) -> dict:
    valid, skipped = [], 0
    for path in sorted(ledger.glob("*.json")):
        try:
            item = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, json.JSONDecodeError):
            skipped += 1; continue
        if valid_record(item): valid.append(item)
        else: skipped += 1
    sums = {key: sum(item[key] for item in valid if item[key] is not None) for key in NUMERIC}
    return {"schema_version": "token_profile_aggregate.v1", "record_count": len(valid),
            "skipped_malformed_files": skipped, "by_provider": dict(sorted(Counter(str(x["provider"]) for x in valid).items())),
            "by_task_type": dict(sorted(Counter(str(x["task_type"]) for x in valid).items())),
            "by_protocol_profile": dict(sorted(Counter(str(x["protocol_profile"]) for x in valid).items())),
            "sums_non_null": sums}

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--ledger-dir", type=Path, default=DEFAULT_LEDGER)
    parser.add_argument("--output-dir", type=Path, default=None)
    args = parser.parse_args(); result = aggregate(args.ledger_dir)
    output = args.output_dir or args.ledger_dir
    payload = json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True).encode() + b"\n"
    digest = hashlib.sha256(payload).hexdigest()
    markdown = "# Token profile aggregate\n\n" + f"- Valid records: {result['record_count']}\n- Skipped malformed files: {result['skipped_malformed_files']}\n- JSON SHA-256: `{digest}`\n\n" + "No prompts, message bodies, paths, or personal identifiers are included.\n"
    atomic_write(output / "token_profile_aggregate.json", payload)
    atomic_write(output / "token_profile_aggregate.md", markdown.encode())
    print(json.dumps({"status": "pass", "record_count": result["record_count"], "skipped": result["skipped_malformed_files"]}, sort_keys=True))
    return 0
if __name__ == "__main__": raise SystemExit(main())
