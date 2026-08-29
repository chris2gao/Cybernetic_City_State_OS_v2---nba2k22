"""Survey what lifecycle evidence the accumulated run groups actually carry.

Answers one question the archive design depends on: can a machine already tell
a finished run from a live one, using only what is physically in the tree?

Run from the repository root.
"""

from __future__ import annotations

import json
import re
import subprocess
import sys
from collections import Counter

RUNS = "01_os/_runs"
COMM_ACTIVE = "01_os/_communication/Cybernetic_City_State_OS_v2---core/active"

LIFECYCLE_RE = re.compile(rb"^\s*lifecycle\s*:\s*(.+?)\s*$", re.MULTILINE)
STATUS_RE = re.compile(rb"^\s*status\s*:\s*(.+?)\s*$", re.MULTILINE)


def tracked() -> list[str]:
    raw = subprocess.run(["git", "ls-files", "-z"], capture_output=True, check=True).stdout
    return [p.decode("utf-8") for p in raw.split(b"\x00") if p]


def blob(path: str) -> bytes:
    proc = subprocess.run(["git", "show", f"HEAD:{path}"], capture_output=True, check=False)
    return proc.stdout if proc.returncode == 0 else b""


def main() -> int:
    paths = tracked()
    groups: dict[str, list[str]] = {}
    for p in paths:
        if p.startswith(RUNS + "/"):
            groups.setdefault(p[len(RUNS) + 1 :].split("/")[0], []).append(p)

    lifecycle_counter: Counter[str] = Counter()
    has_runyml = 0
    has_conclusion = 0
    detail = {}
    for gid, files in sorted(groups.items()):
        runyml = f"{RUNS}/{gid}/run.yml"
        life = None
        if runyml in files:
            has_runyml += 1
            m = LIFECYCLE_RE.search(blob(runyml))
            if m:
                life = m.group(1).decode("utf-8").strip().strip("\"'")
            else:
                m = STATUS_RE.search(blob(runyml))
                if m:
                    life = "status:" + m.group(1).decode("utf-8").strip().strip("\"'")
        concl = any(f"/{gid}/08_" in f for f in files)
        if concl:
            has_conclusion += 1
        lifecycle_counter[life or "<none>"] += 1
        detail[gid] = {
            "files": len(files),
            "bytes_of_paths": sum(len(f.encode("utf-8")) + 1 for f in files),
            "run_yml": runyml in files,
            "lifecycle": life,
            "has_conclusion_dir": concl,
        }

    comm_groups: dict[str, int] = {}
    for p in paths:
        if p.startswith(COMM_ACTIVE + "/"):
            gid = p[len(COMM_ACTIVE) + 1 :].split("/")[0]
            comm_groups[gid] = comm_groups.get(gid, 0) + 1

    report = {
        "run_groups": len(groups),
        "run_groups_with_run_yml": has_runyml,
        "run_groups_with_conclusion_dir": has_conclusion,
        "lifecycle_values": dict(lifecycle_counter),
        "communication_active_groups": len(comm_groups),
        "communication_archive_groups": 0,
        "per_group": detail,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
