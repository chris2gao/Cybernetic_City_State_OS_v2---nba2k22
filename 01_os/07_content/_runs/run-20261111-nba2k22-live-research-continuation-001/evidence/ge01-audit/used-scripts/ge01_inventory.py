"""Bounded inventory of this known failed Run only; no source deletion or hashing."""
from collections import Counter
from datetime import datetime, timezone
import json
from pathlib import Path

RUN = Path(__file__).resolve().parents[1]
ROOT = RUN / "_runtime"
PRIOR = RUN.parent / "run-20261107-nba2k22-vae-longrun-40-001" / "_runtime"
OUT = Path("C:/Users/gk/Documents/ChatGPT/nba2k22/ge01-runtime")
groups = {}
largest = []
for group in (entry for source in (ROOT, PRIOR) if source.is_dir() for entry in source.iterdir()):
    if not group.is_dir():
        continue
    count = size = 0
    extensions = Counter()
    for path in group.rglob("*"):
        if not path.is_file():
            continue
        length = path.stat().st_size
        count += 1
        size += length
        extensions[path.suffix or "no_suffix"] += length
        largest.append((length, path.relative_to(RUN.parent).as_posix()))
    groups[group.parent.parent.name + "/" + group.name] = {"files": count, "bytes": size, "bytes_by_extension": dict(extensions.most_common(8)),
                          "disposition": "RETAIN_HISTORICAL_EVIDENCE_NOT_CURRENT_BASELINE"}
result = {"observed_at": datetime.now(timezone.utc).isoformat(), "bounded_roots": [str(ROOT), str(PRIOR)],
          "groups": groups, "bytes": sum(row["bytes"] for row in groups.values()),
          "largest": [{"bytes": size, "path": path} for size, path in sorted(largest, reverse=True)[:12]],
          "reuse": {"static_inventory_profiles_and_decoders": "REUSE_PINNED_CURRENT_SOURCE",
                    "qualification_and_failure_receipts": "RETAIN_NO_REPLAY",
                    "old_WorldData_and_raw_captures": "HISTORICAL_COMPARISON_ONLY_NEW_EPOCH_REQUIRES_FRESH_READ",
                    "baseline": "READ_CURRENT_MEMORY_WITH_EXISTING_SIX_FAMILY_CAPTURE"},
          "cleanup": {"deleted_files": 0, "reason": "No individual duplicate proven dispensable; cleanup is unnecessary for the first W01 loop"}}
(OUT / "HISTORICAL_DATA_INVENTORY.json").write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
print(json.dumps({"bytes": result["bytes"], "group_count": len(groups),
                  "largest_groups": dict(sorted(((name, row["bytes"]) for name, row in groups.items()), key=lambda row: row[1], reverse=True)[:6]),
                  "deleted_files": 0}))
