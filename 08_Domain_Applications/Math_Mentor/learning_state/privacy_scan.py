"""Reproducible learner-metadata scan over tracked repository content.

The denylist is NEVER stored in this repository.  Publishing the very aliases we
are trying to keep out would defeat the scan.  Supply them at run time:

    LEARNER_DENYLIST="alias1,alias2" python privacy_scan.py <ref>
    python privacy_scan.py <ref> --denylist-file <path outside the repo>

Output is counts and file paths only - matched values are never printed, so the
log this produces is safe to commit.

Exit codes:
    0  no hits
    1  hits found
    2  usage or configuration error
"""

from __future__ import annotations

import os
from pathlib import Path
import re
import subprocess
import sys

REPO_ROOT = Path(__file__).resolve().parents[3]


def load_denylist(argv: list[str]) -> list[str]:
    if "--denylist-file" in argv:
        path = Path(argv[argv.index("--denylist-file") + 1])
        if not path.exists():
            raise SystemExit(f"denylist file not found: {path}")
        raw = path.read_text(encoding="utf-8")
    else:
        raw = os.environ.get("LEARNER_DENYLIST", "")
    values = [v.strip() for v in re.split(r"[,\n]", raw) if v.strip()]
    if not values:
        raise SystemExit(
            "no denylist supplied. Set LEARNER_DENYLIST or pass --denylist-file. "
            "Values are deliberately not stored in this repository."
        )
    return values


def scan(ref: str, denylist: list[str]) -> tuple[int, list[str]]:
    """Return (hit_count, sorted file paths). Matched text is never returned."""
    hits: set[str] = set()
    total = 0
    for value in denylist:
        result = subprocess.run(
            ["git", "grep", "-c", "-F", "-i", value, ref],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        for line in result.stdout.strip().splitlines():
            # format: <ref>:<path>:<count>
            parts = line.rsplit(":", 1)
            if len(parts) != 2:
                continue
            location, count = parts
            path = location.split(":", 1)[1] if ":" in location else location
            hits.add(path)
            total += int(count)
    return total, sorted(hits)


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 2
    ref = argv[1]
    denylist = load_denylist(argv)

    total, paths = scan(ref, denylist)
    print(f"scan_scope: tracked content at ref {ref!r}")
    print(f"denylist_terms: {len(denylist)} (values not printed by design)")
    print(f"hit_count: {total}")
    print(f"files_with_hits: {len(paths)}")
    for path in paths:
        print(f"  {path}")
    return 1 if total else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
