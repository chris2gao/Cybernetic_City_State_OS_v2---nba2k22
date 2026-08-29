#!/usr/bin/env python3
"""Run the reviewer's 46 semantic cases through the accepted engine only.

This exists as a separate process on purpose, and the reason is V4-FND-01.

`semantic_acceptance_v4` registers P21..P27 into the shared REGISTRY at import
time, so once any module in the interpreter has imported it,
`semantic_acceptance.evaluate.evaluate_tree` is no longer a seven-predicate
function.  A "control measurement using the accepted engine" that runs in the
same interpreter as the v4 tests is therefore not a control at all — it is the
extension measuring itself and calling the result a baseline.

Process isolation is the only honest way to get the accepted engine's own
answer.  Import nothing from `semantic_acceptance_v4` in this file.

    python accepted_only_probe.py <output.json>
"""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

import _bootstrap_v4
from _bootstrap_v4 import BASELINE

import reviewer_corpus

from semantic_acceptance.evaluate import evaluate_tree, overall, result_vector
from semantic_acceptance.predicates import FAIL, PASS


def main(argv: list[str]) -> int:
    if "semantic_acceptance_v4" in sys.modules:
        print("contaminated: semantic_acceptance_v4 is imported", file=sys.stderr)
        return 2

    suite = reviewer_corpus.load_suite()
    reviewer_corpus.assert_engine_is_vendored()

    rows = []
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        for case in suite.SEMANTIC_CASES:
            tree = shutil.copytree(BASELINE, root / case.case_id)
            case.mutate(Path(tree))
            results = evaluate_tree(Path(tree))
            vector = result_vector(results)
            actual = overall(results)
            deciding = {pid: vector.get(pid) for pid in case.deciding_predicates}
            correct = actual == case.expected_overall
            if case.expected_overall == FAIL and case.deciding_predicates:
                correct = correct and any(v == FAIL for v in deciding.values())
            rows.append(
                {
                    "case_id": case.case_id,
                    "category": case.category,
                    "description": case.description,
                    "expected_overall": case.expected_overall,
                    "actual_overall": actual,
                    "deciding_results": deciding,
                    "correct": correct,
                    "predicate_ids": sorted(vector),
                    "nonpass": [
                        {"predicate_id": r.predicate_id, "status": r.status, "detail": r.detail}
                        for r in results
                        if r.status != PASS
                    ],
                }
            )

    predicate_id_sets = {tuple(r["predicate_ids"]) for r in rows}
    report = {
        "engine": "accepted only, semantic_acceptance_v4 never imported",
        "fixture_root": "02_acceptance/fixtures/baseline",
        "total": len(rows),
        "expected_classifications_met": sum(1 for r in rows if r["correct"]),
        "counterexample_ids": [r["case_id"] for r in rows if not r["correct"]],
        "distinct_predicate_id_sets": [list(s) for s in predicate_id_sets],
        "cases": rows,
    }
    out = Path(argv[1]) if len(argv) > 1 else None
    if out is not None:
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(
            json.dumps(report, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
            newline="\n",  # byte-reproducible; the repository is eol=lf
        )
    else:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
