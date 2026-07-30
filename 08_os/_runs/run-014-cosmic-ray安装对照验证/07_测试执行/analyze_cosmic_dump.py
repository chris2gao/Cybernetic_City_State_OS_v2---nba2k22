from __future__ import annotations

import argparse
from collections import Counter
import hashlib
import json
from pathlib import Path
from typing import Any


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def normalize(dump_path: Path) -> dict[str, Any]:
    objects: list[dict[str, Any]] = []
    for line_number, line in enumerate(
        dump_path.read_text(encoding="utf-8").splitlines(),
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
                f"line {line_number}: expected exactly one mutation, "
                f"found {len(mutations)}"
            )
        mutation = mutations[0]
        result = result or {}
        diff = result.get("diff", "")
        output = result.get("output", "")
        test_outcome = result.get("test_outcome", "pending")
        worker_outcome = result.get("worker_outcome", "pending")
        if output.strip() == "timeout":
            semantic_outcome = "timeout_misclassified_as_killed"
        elif worker_outcome != "normal":
            semantic_outcome = f"worker_{worker_outcome}"
        else:
            semantic_outcome = test_outcome
        objects.append(
            {
                "module_path": mutation.get("module_path"),
                "operator_name": mutation.get("operator_name"),
                "occurrence": mutation.get("occurrence"),
                "start_pos": mutation.get("start_pos"),
                "end_pos": mutation.get("end_pos"),
                "definition_name": mutation.get("definition_name"),
                "worker_outcome": worker_outcome,
                "test_outcome": test_outcome,
                "semantic_outcome": semantic_outcome,
                "diff": diff,
                "output_sha256": sha256_text(output),
            }
        )
    objects.sort(
        key=lambda item: (
            item["module_path"],
            item["start_pos"],
            item["end_pos"],
            item["operator_name"],
            item["occurrence"],
        )
    )
    status_counts = Counter(item["test_outcome"] for item in objects)
    semantic_counts = Counter(item["semantic_outcome"] for item in objects)
    worker_counts = Counter(item["worker_outcome"] for item in objects)
    operator_counts = Counter(item["operator_name"] for item in objects)
    normalized_json = json.dumps(
        objects,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    semantic_objects = [
        {
            key: value
            for key, value in item.items()
            if key != "output_sha256"
        }
        for item in objects
    ]
    semantic_json = json.dumps(
        semantic_objects,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )
    return {
        "format": "cosmic-ray-normalized-v1",
        "source_dump": str(dump_path),
        "object_count": len(objects),
        "status_counts": dict(sorted(status_counts.items())),
        "semantic_outcome_counts": dict(sorted(semantic_counts.items())),
        "worker_outcome_counts": dict(sorted(worker_counts.items())),
        "operator_counts": dict(sorted(operator_counts.items())),
        "objects_sha256": sha256_text(normalized_json),
        "semantic_objects_sha256": sha256_text(semantic_json),
        "objects": objects,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("dump", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    result = normalize(args.dump)
    args.output.write_text(
        json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "object_count": result["object_count"],
                "objects_sha256": result["objects_sha256"],
                "semantic_objects_sha256": result["semantic_objects_sha256"],
                "status_counts": result["status_counts"],
                "semantic_outcome_counts": result["semantic_outcome_counts"],
                "worker_outcome_counts": result["worker_outcome_counts"],
            },
            sort_keys=True,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
