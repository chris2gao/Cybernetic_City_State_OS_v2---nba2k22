#!/usr/bin/env python3
"""Create one atomic token_profile_run.v1 record for the current old .ai entry."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import tempfile
import time
from pathlib import Path

import yaml


OLD_ENTRY_FILES = [
    "06_Silicon_Index/AI_Bootstrap_Sequence.md",
    "AGENTS.md",
    "06_Silicon_Index/CONSTITUTION_DIGEST.md",
    ".ai/load_profiles/backend_executor.md",
    ".ai/PROTOCOL.md",
    ".ai/PROTOCOL_ADHERENCE.md",
    ".ai/HANDOFF_COMMON_CONVENTIONS.md",
    ".ai/AUTONOMOUS_HANDOFF_COMMUNICATION_v0.1.md",
    ".ai/STATE.yml",
    ".ai/INBOX.md",
]


def atomic_create(path: Path, payload: bytes) -> None:
    if path.exists():
        raise FileExistsError(f"immutable output already exists: {path.name}")
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(payload)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temp_name, path)
    finally:
        if os.path.exists(temp_name):
            os.unlink(temp_name)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo-root", required=True, type=Path)
    parser.add_argument("--run-number", required=True, type=int, choices=range(1, 6))
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    repo = args.repo_root.resolve()
    started = time.perf_counter()
    file_measurements = []
    for relative in OLD_ENTRY_FILES:
        payload = (repo / relative).read_bytes()
        file_measurements.append(
            {
                "logical_ref": relative,
                "byte_count": len(payload),
                "sha256": hashlib.sha256(payload).hexdigest(),
            }
        )

    state = yaml.safe_load((repo / ".ai/STATE.yml").read_text(encoding="utf-8"))
    inbox = (repo / ".ai/INBOX.md").read_text(encoding="utf-8")
    passed = (
        isinstance(state, dict)
        and state.get("status") == "neutral_baseline"
        and 'intent: "neutral_baseline"' in inbox
    )
    elapsed = time.perf_counter() - started

    record = {
        "schema_version": "token_profile_run.v1",
        "task_id": f"old-entry-neutral-full-init-{args.run_number:02d}",
        "task_type": "communication_context_recovery",
        "provider": "Codex",
        "model": "gpt-5.6-sol",
        "effort": "high",
        "session_mode": "cold_replay",
        "protocol_profile": "legacy_ai_full_initialization_v0.3-core",
        "input_tokens": None,
        "output_tokens": None,
        "reasoning_tokens": None,
        "cache_read_tokens": None,
        "cache_write_tokens": None,
        "tool_output_bytes": None,
        "reported_cost": None,
        "wall_seconds": round(elapsed, 9),
        "repair_attempts": 0,
        "review_rounds": 0,
        "validation_result": "pass" if passed else "fail",
        "quality_incidents": 0 if passed else 1,
        "metric_source": "host_stopwatch_and_repository_bytes; provider_token_metrics_not_observable",
        "matching_dimensions": {
            "task_type": "communication_context_recovery",
            "scale": {
                "load_profile": "backend_executor",
                "file_count": len(OLD_ENTRY_FILES),
                "required_ref_count": 0,
                "mailbox_state": "neutral_baseline",
            },
            "acceptance_standard": [
                "all fixed old-entry files readable",
                "STATE is neutral_baseline",
                "INBOX is neutral_baseline",
                "all unavailable token metrics remain null",
            ],
        },
        "measurement_detail": {
            "files": file_measurements,
            "token_metrics_status": "not_observable",
            "comparison_use": "freeze old-entry method now; collect matched new-entry runs in stage 6 and decide R8 in stage 7",
        },
    }
    output = args.output if args.output.is_absolute() else repo / args.output
    atomic_create(
        output,
        (json.dumps(record, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8"),
    )
    print(json.dumps({"status": record["validation_result"], "record": output.name}, ensure_ascii=False))
    return 0 if passed else 1


if __name__ == "__main__":
    raise SystemExit(main())
