#!/usr/bin/env python3
"""Acceptance evaluation entry point.

Quiet-output discipline (01_os/开发入口与单窗口任务规范_v1.md#1.2): one line per
predicate on success, detail only where something failed.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from .facts import build_fact_set
from .predicates import FAIL, PASS, UNSUPPORTED, PredicateResult, evaluate_all


def evaluate_tree(root: Path) -> list[PredicateResult]:
    return evaluate_all(build_fact_set(root))


def result_vector(results: list[PredicateResult]) -> dict[str, str]:
    return {r.predicate_id: r.status for r in results}


def overall(results: list[PredicateResult]) -> str:
    if any(r.status == FAIL for r in results):
        return FAIL
    if any(r.status == UNSUPPORTED for r in results):
        return UNSUPPORTED
    return PASS


def as_dict(root: Path, results: list[PredicateResult]) -> dict[str, Any]:
    return {
        "root": str(root),
        "overall": overall(results),
        "results": [
            {
                "predicate_id": r.predicate_id,
                "title": r.title,
                "a_trace": r.a_trace,
                "status": r.status,
                "detail": r.detail,
                "evidence": r.evidence,
            }
            for r in results
        ],
    }


def render(results: list[PredicateResult], verbose: bool = False) -> str:
    lines = []
    for r in results:
        mark = {PASS: "ok  ", FAIL: "FAIL", UNSUPPORTED: "UNSU"}[r.status]
        lines.append(f"{mark} {r.predicate_id} {r.title}")
        if r.status != PASS or verbose:
            lines.append(f"       -> {r.detail}")
            if verbose:
                for e in r.evidence:
                    lines.append(f"          {e}")
    lines.append(f"overall: {overall(results)}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("root", type=Path, help="candidate surface root")
    ap.add_argument("--json", action="store_true")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args(argv)

    results = evaluate_tree(args.root)
    if args.json:
        print(json.dumps(as_dict(args.root, results), ensure_ascii=False, indent=2))
    else:
        print(render(results, args.verbose))
    return 0 if overall(results) == PASS else 1


if __name__ == "__main__":
    raise SystemExit(main())
