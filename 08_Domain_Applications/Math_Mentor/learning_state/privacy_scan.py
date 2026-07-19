"""Reproducible learner-metadata scan over tracked repository content.

The denylist is NEVER stored in this repository.  Publishing the very aliases we
are trying to keep out would defeat the scan.  Supply them at run time:

    LEARNER_DENYLIST="alias1,alias2" python privacy_scan.py <ref>
    python privacy_scan.py <ref> --denylist-file <path outside the repo>

Output is counts and file paths only - matched values are never printed, so the
log this produces is safe to commit.

Both file CONTENT and tracked file PATHS are scanned: a learner alias in a
filename leaks just as much as one inside a file.

Exit codes:
    0  scan completed, no hits
    1  scan completed, hits found
    2  usage error, unknown ref, or scan failure

A scan failure is never reported as "clean": an unverifiable result is exit 2.
"""

from __future__ import annotations

import os
from pathlib import Path
import re
import subprocess
import sys

REPO_ROOT = Path(__file__).resolve().parents[3]


class ScanError(RuntimeError):
    """The scan could not be completed; the result is unknown, not clean."""


def load_denylist(argv: list[str]) -> list[str]:
    if "--denylist-file" in argv:
        index = argv.index("--denylist-file")
        if index + 1 >= len(argv):
            raise ScanError("--denylist-file needs a path")
        path = Path(argv[index + 1])
        if not path.exists():
            raise ScanError(f"denylist file not found: {path}")
        raw = path.read_text(encoding="utf-8")
    else:
        raw = os.environ.get("LEARNER_DENYLIST", "")
    values = sorted({v.strip() for v in re.split(r"[,\n]", raw) if v.strip()})
    if not values:
        raise ScanError(
            "no denylist supplied. Set LEARNER_DENYLIST or pass --denylist-file. "
            "Values are deliberately not stored in this repository."
        )
    return values


def _git(args: list[str]) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["git", *args], cwd=REPO_ROOT, capture_output=True, text=True
    )


def verify_ref(ref: str) -> None:
    """Confirm the ref resolves. Reporting zero hits for a typo would be a lie."""
    result = _git(["rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}"])
    if result.returncode != 0 or not result.stdout.strip():
        raise ScanError(f"ref does not resolve to a commit: {ref!r}")


def scan_content(ref: str, denylist: list[str]) -> tuple[int, set[str]]:
    """Return (matching line count, paths). Matched text is never returned."""
    total = 0
    paths: set[str] = set()
    for value in denylist:
        # `--` terminates option parsing so a denylist term starting with '-'
        # cannot be read as a git flag.
        result = _git(["grep", "-c", "-F", "-i", "-e", value, ref, "--"])
        if result.returncode == 1:
            continue  # no match for this term
        if result.returncode != 0:
            raise ScanError(
                f"git grep failed with code {result.returncode} while scanning content"
            )
        for line in result.stdout.strip().splitlines():
            location, _, count = line.rpartition(":")
            path = location.split(":", 1)[1] if ":" in location else location
            paths.add(path)
            total += int(count)
    return total, paths


def scan_filenames(ref: str, denylist: list[str]) -> set[str]:
    """Tracked paths whose NAME contains a denylist term."""
    result = _git(["ls-tree", "-r", "--name-only", ref])
    if result.returncode != 0:
        raise ScanError(f"git ls-tree failed with code {result.returncode}")
    lowered = [v.lower() for v in denylist]
    return {
        path
        for path in result.stdout.splitlines()
        if any(term in path.lower() for term in lowered)
    }


def main(argv: list[str]) -> int:
    if len(argv) < 2:
        print(__doc__)
        return 2
    ref = argv[1]

    try:
        denylist = load_denylist(argv)
        verify_ref(ref)
        content_lines, content_paths = scan_content(ref, denylist)
        filename_paths = scan_filenames(ref, denylist)
    except ScanError as error:
        print(f"scan_errors: 1 ({error})", file=sys.stderr)
        print("result: SCAN FAILED - this is NOT a clean result")
        return 2

    all_paths = sorted(content_paths | filename_paths)
    print(f"scan_scope: tracked content and paths at ref {ref!r}")
    print(f"denylist_terms: {len(denylist)} (values not printed by design)")
    print(f"content_matching_lines: {content_lines}")
    print(f"filename_hits: {len(filename_paths)}")
    print(f"scan_errors: 0")
    print(f"files_with_hits: {len(all_paths)}")
    for path in all_paths:
        print(f"  {path}")
    return 1 if (content_lines or filename_paths) else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
