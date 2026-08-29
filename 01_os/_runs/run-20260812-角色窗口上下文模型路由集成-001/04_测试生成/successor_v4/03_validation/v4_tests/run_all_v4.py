#!/usr/bin/env python3
"""Quiet runner for the v4 validation suite.

Same shape as `vendored_baseline_tests/run_all.py`, and same reason:
01_os/开发入口与单窗口任务规范_v1.md#1.2 — one line per check on success, tail
detail only on failure, never a full passing list pulled into context.

  python run_all_v4.py            quiet summary, exit 0 or 1
  python run_all_v4.py --json     machine result, for the evidence directory
  python run_all_v4.py --emit DIR write the corpus result files into DIR

This runner does NOT replace `vendored_baseline_tests/run_all.py`.  The two are
deliberately separate processes: that suite must run in an interpreter where
`semantic_acceptance_v4` was never imported, or it stops measuring the accepted
package (V4-FND-01).  Running both is two commands, on purpose.
"""

from __future__ import annotations

import argparse
import json
import sys
import traceback
from pathlib import Path

import _bootstrap_v4  # noqa: F401

import test_v4_adapter_applicability
import test_v4_decision_provenance
import test_v4_independent_findings
import test_v4_metamorphic
import test_v4_receipt_binding
import test_v4_reviewer_replay
import test_v4_trace_and_inventory
import test_v4_v3_variants

MODULES = (
    test_v4_reviewer_replay,
    test_v4_v3_variants,
    test_v4_metamorphic,
    # P2-2 additions. Kept last so the existing three keep their ordinal
    # positions in any diff of this file's output.
    test_v4_adapter_applicability,
    test_v4_receipt_binding,
    test_v4_decision_provenance,
    test_v4_trace_and_inventory,
    # R6: the four independent parent-Stage04 findings, persisted so a future
    # round re-runs them instead of trusting that they were once fixed.
    test_v4_independent_findings,
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
        replay = test_v4_reviewer_replay.write_results(
            args.emit / "reviewer_probe_replay_v4_results_v1.json"
        )
        variants = test_v4_v3_variants.write_results(
            args.emit / "v3_15_variant_replay_v4_results_v1.json"
        )
        meta = test_v4_metamorphic.write_results(
            args.emit / "v4_metamorphic_and_adversarial_results_v1.json"
        )
        emitted = {
            "accepted_control": f"{replay['measurement_A_accepted_engine_accepted_baseline']['expected_classifications_met']}"
            f"/{replay['measurement_A_accepted_engine_accepted_baseline']['total']}",
            "v4_semantic": f"{replay['measurement_B_v4_engine_baseline_v4']['expected_classifications_met']}"
            f"/{replay['measurement_B_v4_engine_baseline_v4']['total']}",
            "receipt_attacks": f"{replay['measurement_receipt_attacks']['expected_classifications_met']}"
            f"/{replay['measurement_receipt_attacks']['total']}",
            "v3_variants": f"{variants['correct']}/{variants['total']}",
            "v4_invariants": f"{meta['invariants']['holding']}/{meta['invariants']['total']}",
            "v4_differences": f"{meta['differences']['holding']}/{meta['differences']['total']}",
            "open_holes_false_pass": meta["open_holes"]["false_pass"],
            "open_invariance_holes": meta["open_invariance_holes"]["total"],
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
