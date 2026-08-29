"""Path bootstrap — successor_v4 layout shim.

This is the ONLY file in `vendored_baseline_tests/` that is not byte-identical
to the independently accepted methodology package at
19c39ed37f14c97cfa132ffafabcb9afa33dd7f0.

Reason: the accepted package kept engine, fixtures and tests under one
prototype root, so its bootstrap could compute both from `parent.parent`.
successor_v4's required output layout separates them:

    02_acceptance/实现/semantic_acceptance/   engine   (byte-identical)
    02_acceptance/fixtures/baseline/          fixtures (byte-identical)
    03_validation/vendored_baseline_tests/    tests    (byte-identical except this file)

Only the two path constants change. No test logic, assertion, threshold or
expected value is redefined here. The replacement is recorded in
01_semantic_binding/vendored_methodology_ledger_v1.yml.

01_os/开发入口与单窗口任务规范_v1.md#1.2 requires that `python -m pytest <dir>`
and `python <test file>` both work without the directory being a package.
"""

from __future__ import annotations

import sys
from pathlib import Path

_TESTS_DIR = Path(__file__).resolve().parent
SUCCESSOR_V4_ROOT = _TESTS_DIR.parent.parent

PROTOTYPE_ROOT = SUCCESSOR_V4_ROOT / "02_acceptance" / "实现"
if str(PROTOTYPE_ROOT) not in sys.path:
    sys.path.insert(0, str(PROTOTYPE_ROOT))

BASELINE = SUCCESSOR_V4_ROOT / "02_acceptance" / "fixtures" / "baseline"
