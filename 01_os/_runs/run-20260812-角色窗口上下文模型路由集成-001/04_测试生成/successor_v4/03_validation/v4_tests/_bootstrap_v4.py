"""Path and provenance bootstrap for the v4 validation suite.

Separate from `vendored_baseline_tests/_bootstrap.py` on purpose.  That file
exists only to run byte-identical accepted tests from the successor_v4 layout
and must stay minimal.  This one carries what the v4 tail additionally needs:
the second fixture root, and read-only materialisation of historical review
corpora from their exact immutable Git objects.

Nothing here writes outside the successor_v4 write boundary.  Historical
evidence is read from Git by blob SHA and materialised into a `tempfile`
directory; the working-tree copies of `08_独立审核/**` and `05_原型/**` are
never touched, which is what `00_governance/任务包_v1.yml#prohibited_actions`
requires of historical review evidence.

01_os/开发入口与单窗口任务规范_v1.md#1.2: tests import by module name after a
`sys.path` insert; the directory is not required to be a package.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

_TESTS_DIR = Path(__file__).resolve().parent
SUCCESSOR_V4_ROOT = _TESTS_DIR.parent.parent

PROTOTYPE_ROOT = SUCCESSOR_V4_ROOT / "02_acceptance" / "实现"
if str(PROTOTYPE_ROOT) not in sys.path:
    sys.path.insert(0, str(PROTOTYPE_ROOT))

# The accepted package's own baseline.  Byte-identical to
# root-cause-001/05_原型/fixtures/baseline, verified per file by blob SHA1.
BASELINE = SUCCESSOR_V4_ROOT / "02_acceptance" / "fixtures" / "baseline"

# BASELINE plus exactly one added document: mechanism/context_contract_v1.yml.
# Every other file is the same Git blob as BASELINE.  This is the conforming
# tree for the fourteen-criterion package: A04 requires a minimum-effective
# -context derivation contract that the accepted seven-predicate package had no
# predicate for and therefore never declared.
BASELINE_V4 = SUCCESSOR_V4_ROOT / "02_acceptance" / "fixtures" / "baseline_v4"

# Immutable sources of historical review evidence.
ACCEPTED_METHODOLOGY_SHA = "19c39ed37f14c97cfa132ffafabcb9afa33dd7f0"
INDEPENDENT_REVIEW_CLOSURE_SHA = "2fb7c6699fa8f6436d5d87053b841316074a7b6d"


def _git(args: list[str]) -> bytes:
    out = subprocess.run(
        ["git"] + args,
        cwd=str(SUCCESSOR_V4_ROOT),
        capture_output=True,
        check=True,
    )
    return out.stdout


def repo_root() -> Path:
    return Path(_git(["rev-parse", "--show-toplevel"]).decode("utf-8").strip())


def ls_tree(rev: str) -> list[tuple[str, str]]:
    """(blob_sha, path) for every blob in `rev`.

    `-z` is used so Git never quotes or octal-escapes a path.  This repository's
    paths are largely Chinese and the quoting default corrupts them silently;
    01_os/开发入口与单窗口任务规范_v1.md#1.2 requires that any program deriving a
    path set use NUL separation rather than trusting repository configuration.

    `--full-tree` is mandatory here and was a real defect before it was added:
    `git ls-tree` defaults its pathspec to the *current* directory prefix, so
    run from inside `successor_v4/` — a path that does not exist in the
    historical revisions this function is asked about — it returns an empty
    list with exit code 0.  An empty result from a successful command is the
    worst shape of failure available, because a caller that only checks the
    return code reads "nothing matched" as "nothing exists".
    """
    rows: list[tuple[str, str]] = []
    for record in _git(["ls-tree", "-r", "-z", "--full-tree", rev]).split(b"\x00"):
        if not record:
            continue
        meta, _, path = record.partition(b"\t")
        fields = meta.split()
        if len(fields) < 3 or fields[1] != b"blob":
            continue
        rows.append((fields[2].decode("ascii"), path.decode("utf-8")))
    return rows


def read_blob(blob_sha: str) -> bytes:
    return _git(["cat-file", "blob", blob_sha])


def find_one(rev: str, suffix: str) -> tuple[str, str]:
    """The single blob in `rev` whose path ends with `suffix`.

    Raises on zero or several.  A replay that silently took the first of many
    candidates would be measuring an unnamed file.
    """
    hits = [(sha, path) for sha, path in ls_tree(rev) if path.endswith(suffix)]
    if len(hits) != 1:
        raise AssertionError(
            f"{len(hits)} blobs end with {suffix!r} in {rev}: {[p for _, p in hits]}"
        )
    return hits[0]


def find_under(rev: str, marker: str) -> list[tuple[str, str, str]]:
    """(blob_sha, full_path, path_after_marker) for every blob under `marker`."""
    rows: list[tuple[str, str, str]] = []
    for sha, path in ls_tree(rev):
        idx = path.find(marker)
        if idx == -1:
            continue
        rows.append((sha, path, path[idx + len(marker):]))
    return rows
