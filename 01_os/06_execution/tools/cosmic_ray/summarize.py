from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
from typing import Any


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def semantic_outcome(result: dict[str, Any] | None) -> str:
    if result is None:
        return "incomplete"
    output = str(result.get("output", "")).strip()
    if output == "timeout":
        return "timeout"
    worker = str(result.get("worker_outcome", "missing"))
    if worker != "normal":
        return f"worker_{worker}"
    outcome = str(result.get("test_outcome", "missing"))
    if outcome not in {"killed", "survived"}:
        return f"test_{outcome}"
    return outcome


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("dump", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    objects: list[dict[str, Any]] = []
    for line_number, line in enumerate(
        args.dump.read_text(encoding="utf-8").splitlines(),
        start=1,
    ):
        if not line.strip():
            continue
        value = json.loads(line)
        if not isinstance(value, list) or len(value) != 2:
            raise ValueError(f"line {line_number}: expected [work_item, result]")
        work_item, result = value
        mutations = work_item.get("mutations", [])
        if len(mutations) != 1:
            raise ValueError(
                f"line {line_number}: expected one mutation, got {len(mutations)}"
            )
        mutation = mutations[0]
        outcome = semantic_outcome(result)
        native_result = result or {}
        objects.append(
            {
                "definition_name": mutation.get("definition_name"),
                "diff": native_result.get("diff"),
                "end_pos": mutation.get("end_pos"),
                "module_path": mutation.get("module_path"),
                "occurrence": mutation.get("occurrence"),
                "operator_name": mutation.get("operator_name"),
                "semantic_outcome": outcome,
                "start_pos": mutation.get("start_pos"),
                "test_outcome": native_result.get("test_outcome", "pending"),
                "worker_outcome": native_result.get("worker_outcome", "pending"),
            }
        )

    objects.sort(
        key=lambda item: (
            str(item["module_path"]),
            item["start_pos"] or [-1, -1],
            str(item["operator_name"]),
            int(item["occurrence"] or 0),
        )
    )
    semantic_counts = Counter(item["semantic_outcome"] for item in objects)
    native_counts = Counter(item["test_outcome"] for item in objects)
    unsafe_outcomes = {
        outcome: count
        for outcome, count in semantic_counts.items()
        if outcome not in {"killed", "survived"}
    }
    result = {
        "format": "citystate-cosmic-ray-summary-v1",
        "cosmic_ray_version": "8.4.6",
        "object_count": len(objects),
        "native_test_outcome_counts": dict(sorted(native_counts.items())),
        "semantic_outcome_counts": dict(sorted(semantic_counts.items())),
        "unsafe_outcomes": dict(sorted(unsafe_outcomes.items())),
        "fail_closed": bool(unsafe_outcomes),
        "raw_dump_bytes": args.dump.stat().st_size,
        "raw_dump_sha256": sha256(args.dump),
        "objects": objects,
    }
    args.output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "fail_closed": result["fail_closed"],
                "object_count": result["object_count"],
                "semantic_outcome_counts": result["semantic_outcome_counts"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
