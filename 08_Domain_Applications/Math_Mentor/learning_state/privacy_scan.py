"""Reproducible learner-metadata scan over tracked repository content.

The denylist is NEVER stored in this repository.  Publishing the very aliases we
are trying to keep out would defeat the scan.  Supply them at run time:

    LEARNER_DENYLIST="alias1,alias2" python privacy_scan.py <ref>
    python privacy_scan.py <ref> --denylist-file <path outside the repo>

Both file CONTENT and tracked file PATHS are scanned: a learner alias in a
filename leaks just as much as one inside a file.

Output confidentiality: counts, REDACTED paths and opaque fingerprints only.
Printing a raw path was itself a leak, because a denylist term can appear in a
tracked FILENAME - the scanner would then publish the very value it exists to
keep out of the repository, straight into a committable log.  Every printed path
therefore has each denylist match replaced by [REDACTED] and carries a
sha256 prefix so an operator can still correlate hits across runs.

`--reveal-paths` prints raw paths for local diagnosis.  Its output is NOT
committable and it is never the default.

`--repo-root <path>` scans another repository; it exists so the filename case
can be tested against a synthetic throwaway repo rather than by planting a
learner-shaped term in this one.

Exit codes:
    0  scan completed, no hits
    1  scan completed, hits found
    2  usage error, unknown ref, or scan failure

A scan failure is never reported as "clean": an unverifiable result is exit 2.
"""

from __future__ import annotations

from hashlib import sha256
import os
from pathlib import Path
import re
import subprocess
import sys

REPO_ROOT = Path(__file__).resolve().parents[3]


def redact_path(path: str, denylist: list[str]) -> str:
    """A path safe to print: every denylist match replaced, plus a fingerprint.

    Redaction is case-insensitive because `scan_filenames` matches
    case-insensitively; a term found by the scan must not survive in the output
    just because its casing differs.

    The sha256 prefix is derived from the ORIGINAL path, so the same file yields
    the same identifier across runs.  That keeps the report useful for
    correlation while publishing nothing about the term itself.
    """
    redacted = path
    for term in denylist:
        if term:
            redacted = re.sub(re.escape(term), "[REDACTED]", redacted, flags=re.IGNORECASE)
    return f"{redacted}  (sha256:{sha256(path.encode('utf-8')).hexdigest()[:12]})"


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


def resolve_repo_root(argv: list[str]) -> Path:
    """Repository to scan.  Defaults to this package's own repository.

    `--repo-root` exists so the scanner can be exercised against a synthetic
    throwaway repository.  Planting a learner-shaped term in a tracked FILENAME
    is the case that leaked, and it cannot be tested by planting it in the real
    repository - that would commit the very thing the scan exists to prevent.
    """
    if "--repo-root" in argv:
        index = argv.index("--repo-root")
        if index + 1 >= len(argv):
            raise ScanError("--repo-root needs a path")
        root = Path(argv[index + 1]).resolve()
        if not root.is_dir():
            raise ScanError(f"--repo-root is not a directory: {root}")
        return root
    return REPO_ROOT


def _git(args: list[str], root: Path) -> subprocess.CompletedProcess:
    return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True)


def verify_ref(ref: str, root: Path) -> None:
    """Confirm the ref resolves. Reporting zero hits for a typo would be a lie."""
    result = _git(["rev-parse", "--verify", "--quiet", f"{ref}^{{commit}}"], root)
    if result.returncode != 0 or not result.stdout.strip():
        raise ScanError(f"ref does not resolve to a commit: {ref!r}")


def scan_content(ref: str, denylist: list[str], root: Path) -> tuple[int, set[str]]:
    """Return (matching line count, paths). Matched text is never returned."""
    total = 0
    paths: set[str] = set()
    for value in denylist:
        # `--` terminates option parsing so a denylist term starting with '-'
        # cannot be read as a git flag.
        result = _git(["grep", "-c", "-F", "-i", "-e", value, ref, "--"], root)
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


def scan_filenames(ref: str, denylist: list[str], root: Path) -> set[str]:
    """Tracked paths whose NAME contains a denylist term."""
    result = _git(["ls-tree", "-r", "--name-only", ref], root)
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
        root = resolve_repo_root(argv)
        verify_ref(ref, root)
        content_lines, content_paths = scan_content(ref, denylist, root)
        filename_paths = scan_filenames(ref, denylist, root)
    except ScanError as error:
        print(f"scan_errors: 1 ({error})", file=sys.stderr)
        print("result: SCAN FAILED - this is NOT a clean result")
        return 2

    all_paths = sorted(content_paths | filename_paths)
    reveal = "--reveal-paths" in argv
    print(f"scan_scope: tracked content and paths at ref {ref!r}")
    print(f"denylist_terms: {len(denylist)} (values not printed by design)")
    print(f"content_matching_lines: {content_lines}")
    print(f"filename_hits: {len(filename_paths)}")
    print(f"scan_errors: 0")
    print(f"files_with_hits: {len(all_paths)}")
    if reveal:
        # Local diagnosis only.  Raw paths may contain the denylist term itself,
        # which is exactly what must never reach a committed log.
        print("path_disclosure: RAW - this output is NOT committable", file=sys.stderr)
        for path in all_paths:
            print(f"  {path}")
    else:
        print("path_disclosure: redacted+fingerprint")
        for path in all_paths:
            print(f"  {redact_path(path, denylist)}")
    return 1 if (content_lines or filename_paths) else 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
