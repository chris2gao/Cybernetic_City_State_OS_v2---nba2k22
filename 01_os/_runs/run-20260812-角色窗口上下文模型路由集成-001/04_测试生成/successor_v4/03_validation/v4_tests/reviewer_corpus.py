"""Load the independent reviewer's probe corpus without editing or copying it.

`08_独立审核/independent_probe_suite.py` at
19c39ed37f14c97cfa132ffafabcb9afa33dd7f0 is historical independent-review
evidence.  `00_governance/任务包_v1.yml` forbids editing it, and
`AGENT_WORKING_DISCIPLINE.md#5` says a reviewer should be handed the primary
material rather than someone's account of it.  So the corpus is loaded from its
exact Git blob, executed as a module in a temporary directory, and only its
*case tables* are used.  Its runner is deliberately not used: the runner calls
the seven-predicate `evaluate_tree`, and the whole point of the replay is to
put the same cases through the fourteen-predicate v4 entry point.

What is imported: SEMANTIC_CASES (46), RECEIPT_CASES (17), and the mutation
callables they hold.  What is not imported: expectations restated by hand,
result files, or any conclusion the reviewer reached.  The expectations used
below are the reviewer's own `expected_overall` / `expected_valid` fields, read
out of the loaded objects.

Why the suite can be imported at all: it does
`sys.path.insert(0, RUN_ROOT/"05_原型")` and then imports `semantic_acceptance`.
Only the reviewer's *fixtures* are materialised under that root, never an
engine, so the import falls through to the vendored engine already on
`sys.path` from `_bootstrap_v4`.  `assert_engine_is_vendored()` proves that
rather than assuming it.
"""

from __future__ import annotations

import importlib.util
import sys
import tempfile
from pathlib import Path
from typing import Any

import _bootstrap_v4
from _bootstrap_v4 import (
    ACCEPTED_METHODOLOGY_SHA,
    PROTOTYPE_ROOT,
    find_one,
    find_under,
    read_blob,
)

SUITE_SUFFIX = "08_独立审核/independent_probe_suite.py"
FIXTURE_MARKER = "root-cause-001/05_原型/fixtures/baseline/"

_CACHE: dict[str, Any] = {}


def materialise(rev: str = ACCEPTED_METHODOLOGY_SHA) -> tuple[Path, str, str]:
    """Write the reviewer suite and its fixtures into a temp dir.

    Returns (suite_path, suite_blob_sha, fixture_tree_digest_source).  The temp
    directory is intentionally leaked for the process lifetime: the corpus is
    module-level state and tearing the directory down would invalidate the
    fixture root the loaded module holds.
    """
    if "root" in _CACHE:
        return _CACHE["root"], _CACHE["suite_blob"], _CACHE["fixture_count"]

    tmp = Path(tempfile.mkdtemp(prefix="v4_reviewer_corpus_"))
    suite_blob, suite_path_in_git = find_one(rev, SUITE_SUFFIX)

    run_root = tmp / "run"
    review_dir = run_root / "08_独立审核"
    review_dir.mkdir(parents=True)
    suite_path = review_dir / "independent_probe_suite.py"
    suite_path.write_bytes(read_blob(suite_blob))

    fixture_root = run_root / "05_原型" / "fixtures" / "baseline"
    fixtures = find_under(rev, FIXTURE_MARKER)
    if not fixtures:
        raise AssertionError(f"no fixtures under {FIXTURE_MARKER} in {rev}")
    for blob_sha, _full, rel in fixtures:
        dest = fixture_root / rel
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(read_blob(blob_sha))

    _CACHE.update(
        {
            "root": suite_path,
            "suite_blob": suite_blob,
            "suite_git_path": suite_path_in_git,
            "fixture_count": len(fixtures),
        }
    )
    return suite_path, suite_blob, len(fixtures)


def load_suite(rev: str = ACCEPTED_METHODOLOGY_SHA):
    if "module" in _CACHE:
        return _CACHE["module"]
    suite_path, _blob, _n = materialise(rev)
    spec = importlib.util.spec_from_file_location("reviewer_probe_suite", suite_path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"cannot load reviewer suite from {suite_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules["reviewer_probe_suite"] = module
    spec.loader.exec_module(module)
    _CACHE["module"] = module
    return module


def assert_engine_is_vendored() -> str:
    """The loaded corpus must be running the successor_v4 vendored engine.

    If the reviewer's own 05_原型 engine were ever materialised alongside the
    fixtures, its `sys.path.insert(0, ...)` would win and this replay would be
    measuring the accepted package from its original location instead of the
    vendored copy under test.  The failure would be invisible in the result
    counts, which is exactly the class of silent substitution
    `AGENT_WORKING_DISCIPLINE.md#5` is about.
    """
    import semantic_acceptance

    engine = Path(semantic_acceptance.__file__).resolve().parent
    expected = (PROTOTYPE_ROOT / "semantic_acceptance").resolve()
    if engine != expected:
        raise AssertionError(f"engine resolved to {engine}, expected {expected}")
    return str(engine)


def provenance() -> dict[str, Any]:
    load_suite()
    return {
        "source_rev": ACCEPTED_METHODOLOGY_SHA,
        "suite_blob_sha1": _CACHE["suite_blob"],
        "suite_git_path": _CACHE["suite_git_path"],
        "reviewer_fixture_files": _CACHE["fixture_count"],
        "engine_under_test": assert_engine_is_vendored(),
    }
