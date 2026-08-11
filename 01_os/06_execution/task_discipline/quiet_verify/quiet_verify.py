"""Quiet unified verification entry point.

Runs a declared set of checks and prints one line per check plus one summary
line. Output from a passing check is discarded; a failing check gets its tail
printed. The point is that a green run costs a handful of lines instead of a
full pytest roster, while a red run still shows what broke.

It never decides anything: it reports exit codes. A passing run proves the exact
commands listed passed on this working tree in this session, and nothing wider.

Usage
    python quiet_verify.py [--checks <yaml>] [--repo-root .] [--tail 20] [--json]

With no `--checks`, the built-in repository check set is used
(`DEFAULT_CHECKS` below): the workflow static validator, the context-management
validator, the canonical-live-state guard and the stage-deliberation v2 static
validator.

Checks file format
    checks:
      - name: unit
        cmd: [python, -m, pytest, 01_os/06_execution/task_discipline, -q]
      - name: workflow_static
        cmd: [python, 01_os/.../run_minimum_operational_loop.py, static, .]
        expect_exit: 0        # optional, default 0

Exit codes
    0  every check matched its expected exit code
    1  at least one check did not
    3  bad input
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None


MOL = "01_os/06_execution/workflow/minimum_operational_loop/run_minimum_operational_loop.py"
CTX = "01_os/03_mechanisms/context_management/实现/verify_context_structure.py"
LIVE = "01_os/03_mechanisms/stage_collaborative_deliberation/实现/verify_no_canonical_live_state.py"
DELIB = "01_os/03_mechanisms/stage_collaborative_deliberation/实现/verify_stage_collaborative_deliberation_v2.py"

DEFAULT_CHECKS: list[dict] = [
    {"name": "workflow_static", "cmd": [sys.executable, MOL, "static", "."]},
    {"name": "context_structure", "cmd": [sys.executable, CTX]},
    {"name": "no_canonical_live_state", "cmd": [sys.executable, LIVE, "."]},
    {"name": "stage_deliberation_v2_static", "cmd": [sys.executable, DELIB, "static", "."]},
]


def load_checks(path: Path) -> list[dict]:
    if yaml is None:
        raise RuntimeError("PyYAML is required to read a checks file")
    data = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    checks = data.get("checks")
    if not checks:
        raise RuntimeError(f"{path}: 'checks' missing or empty")
    for check in checks:
        if not check.get("name") or not check.get("cmd"):
            raise RuntimeError(f"{path}: every check needs a name and a cmd")
    return checks


def bounded_tail(output: str, tail: int, max_chars: int) -> str:
    """Last `tail` lines, then hard-capped at `max_chars`.

    Review finding F4: bounding by lines alone is not bounding. A single
    300,000-character line satisfied `tail=20` and came back whole — in the one
    tool whose entire purpose is to cap what reaches the caller.
    """
    text = "\n".join(output.strip().splitlines()[-tail:])
    if len(text) <= max_chars:
        return text
    dropped = len(text) - max_chars
    return f"[...{dropped} characters dropped...]\n{text[-max_chars:]}"


def run_check(check: dict, repo_root: Path, tail: int, max_chars: int = 4000) -> dict:
    cmd = [str(part) for part in check["cmd"]]
    expected = check.get("expect_exit", 0)
    proc = subprocess.run(
        cmd, cwd=repo_root, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False
    )
    output = proc.stdout.decode("utf-8", "replace")
    ok = proc.returncode == expected
    return {
        "name": check["name"],
        "exit_code": proc.returncode,
        "expected_exit": expected,
        "ok": ok,
        "tail": "" if ok else bounded_tail(output, tail, max_chars),
    }


def summarize(results: list[dict]) -> str:
    passed = sum(1 for r in results if r["ok"])
    return f"checks {passed}/{len(results)} ok"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--checks", help="yaml file declaring the check set")
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--tail", type=int, default=20,
                        help="lines of output kept from a failing check")
    parser.add_argument("--max-chars", type=int, default=4000,
                        help="hard character cap applied after the line cap")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    try:
        checks = load_checks(Path(args.checks)) if args.checks else DEFAULT_CHECKS
    except (RuntimeError, OSError) as exc:
        print(f"quiet_verify_error: {exc}", file=sys.stderr)
        return 3

    repo_root = Path(args.repo_root).resolve()
    results = [run_check(check, repo_root, args.tail, args.max_chars) for check in checks]

    if args.json:
        print(json.dumps({"results": results, "summary": summarize(results)},
                         ensure_ascii=False, indent=2))
    else:
        for r in results:
            print(f"{r['name']} exit={r['exit_code']}" + ("" if r["ok"] else " FAILED"))
        print(summarize(results))
        for r in results:
            if not r["ok"] and r["tail"]:
                print(f"--- {r['name']} tail ---", file=sys.stderr)
                print(r["tail"], file=sys.stderr)

    return 0 if all(r["ok"] for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
