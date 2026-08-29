#!/usr/bin/env python3
"""Quiet test runner.

01_os/开发入口与单窗口任务规范_v1.md#1.2: one line per check on success, tail
detail only on failure.  Never pull a full passing test list into context.

  python run_all.py            quiet summary, exit 0 or 1
  python run_all.py --json     machine result, for the evidence directory
  python run_all.py --emit DIR write the corpus result files into DIR
"""

from __future__ import annotations

import argparse
import json
import sys
import traceback
from pathlib import Path

import _bootstrap  # noqa: F401

import test_core
import test_facts_and_predicates
import test_metamorphic
import test_provenance
import test_receipt
import test_receipt_external_binding
import test_representation_boundary
import test_v3_adversarial_regression

MODULES = (
    test_core,
    test_facts_and_predicates,
    test_v3_adversarial_regression,
    test_metamorphic,
    test_receipt,
    # correction-002: the three invariants the FIX_REQUIRED review added
    test_representation_boundary,   # C-08
    test_provenance,                # C-09
    test_receipt_external_binding,  # C-10 and C-07
)

TAIL_LINES = 12


def collect():
    for module in MODULES:
        for name in sorted(dir(module)):
            if name.startswith("test_"):
                yield module.__name__, name, getattr(module, name)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--emit", type=Path, default=None)
    args = ap.parse_args(argv)

    rows = []
    for mod_name, test_name, fn in collect():
        try:
            fn()
            rows.append({"module": mod_name, "test": test_name, "passed": True, "error": ""})
        except Exception:
            rows.append(
                {
                    "module": mod_name,
                    "test": test_name,
                    "passed": False,
                    "error": traceback.format_exc(),
                }
            )

    failed = [r for r in rows if not r["passed"]]

    emitted = {}
    if args.emit is not None and not failed:
        args.emit.mkdir(parents=True, exist_ok=True)
        v3 = test_v3_adversarial_regression.write_results(
            args.emit / "v3_15_case_regression_results_v1.json"
        )
        mt = test_metamorphic.write_results(
            args.emit / "metamorphic_property_results_v1.json"
        )
        emitted = {
            "v3_correct": f"{v3['correct']}/{v3['total']}",
            "metamorphic_holding": f"{mt['holding']}/{mt['total']}",
        }

    summary = {
        "total": len(rows),
        "passed": len(rows) - len(failed),
        "failed": len(failed),
        "emitted": emitted,
        "failures": [{"module": r["module"], "test": r["test"]} for r in failed],
    }

    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        for mod_name, test_name, _ in collect():
            row = next(r for r in rows if r["module"] == mod_name and r["test"] == test_name)
            print(f"{'ok  ' if row['passed'] else 'FAIL'} {mod_name}.{test_name}")
        for r in failed:
            print(f"\n--- {r['module']}.{r['test']} ---")
            print("\n".join(r["error"].strip().splitlines()[-TAIL_LINES:]))
        print(f"\n{summary['passed']}/{summary['total']} passed")
        if emitted:
            print(f"emitted: {emitted}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
