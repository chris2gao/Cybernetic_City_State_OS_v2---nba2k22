"""Quiet unified verification entry point.

Runs a declared set of checks and prints one line per check plus one summary
line. Complete stdout/stderr are retained in an external attempt directory;
only presentation is bounded. This unbound diagnostic entry is not candidate
readiness evidence; use managed_verification for a pinned, required check chain.

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
import tempfile
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "managed_verification"))
import managed_verify as managed
from task_packet_input import load_yaml_text

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
    try:
        data = load_yaml_text(path.read_text(encoding="utf-8"))
        if type(data) is not dict or set(data) != {"checks"}:
            raise ValueError("checks_root_fields")
        checks = data["checks"]
        if type(checks) is not list or not checks:
            raise ValueError("nonempty_checks_list_required")
        normalized = []
        for check in checks:
            if type(check) is not dict or not {"name", "cmd"}.issubset(check) or not set(check).issubset({"name", "cmd", "expect_exit", "timeout_seconds"}):
                raise ValueError("check_fields")
            normalized.append({"id": check["name"], "argv": check["cmd"],
                               "expected_exit_code": check.get("expect_exit", 0),
                               "timeout_seconds": check.get("timeout_seconds", 300)})
        managed.validate_plan({"schema_version": managed.PLAN_VERSION, "checks": normalized}, diagnostic=True)
    except (ValueError, managed.VerificationError, RecursionError) as exc:
        raise RuntimeError(f"invalid_checks:{exc}") from exc
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
    normalized = {"id": check["name"], "argv": check["cmd"],
                  "expected_exit_code": check.get("expect_exit", 0),
                  "timeout_seconds": check.get("timeout_seconds", 300)}
    managed.validate_plan({"schema_version": managed.PLAN_VERSION, "checks": [normalized]}, diagnostic=True)
    temp_root = Path(tempfile.gettempdir()).resolve()
    source_root = repo_root.resolve()
    if temp_root == source_root or source_root in temp_root.parents:
        raise managed.VerificationError("diagnostic_temp_root_must_be_outside_source")
    attempt = Path(tempfile.mkdtemp(prefix="citystate-diagnostic-", dir=temp_root))
    result = managed.run_check(normalized, 1, repo_root, attempt)
    ok = result["status"] == "success"
    output = ""
    if not ok:
        # Read a bounded suffix for display. The complete byte streams stay on disk.
        for stream in ("stdout", "stderr"):
            with (attempt / f"001.{stream}.bin").open("rb") as log:
                log.seek(0, 2)
                log.seek(max(0, log.tell() - max(4096, max_chars * 4)))
                suffix = log.read().decode("utf-8", "replace")
            output += suffix
    return {
        "name": check["name"],
        "exit_code": result["exit_code"],
        "expected_exit": normalized["expected_exit_code"],
        "ok": ok,
        "status": result["status"],
        "evidence_level": "unbound_diagnostic",
        "attempt_directory": str(attempt),
        "stdout_sha256": result["stdout_sha256"],
        "stderr_sha256": result["stderr_sha256"],
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
    except (RuntimeError, OSError, UnicodeError) as exc:
        print(f"quiet_verify_error: {exc}", file=sys.stderr)
        return 3

    if args.tail < 1 or args.max_chars < 1:
        print("quiet_verify_error: positive presentation bounds required", file=sys.stderr)
        return 3
    repo_root = Path(args.repo_root).resolve()
    try:
        results = [run_check(check, repo_root, args.tail, args.max_chars) for check in checks]
    except (managed.VerificationError, OSError, ValueError, TypeError, KeyError) as exc:
        print(f"quiet_verify_error: {exc}", file=sys.stderr)
        return 3

    if args.json:
        print(json.dumps({"results": results, "summary": summarize(results)},
                         ensure_ascii=False, indent=2))
    else:
        for r in results:
            print(f"{r['name']} exit={r['exit_code']} logs={r['attempt_directory']}" + ("" if r["ok"] else " FAILED"))
        print(summarize(results))
        for r in results:
            if not r["ok"] and r["tail"]:
                print(f"--- {r['name']} tail ---", file=sys.stderr)
                print(r["tail"], file=sys.stderr)

    if any(r["status"] == "error" for r in results):
        return 3
    return 0 if all(r["ok"] for r in results) else 1


if __name__ == "__main__":
    raise SystemExit(main())
