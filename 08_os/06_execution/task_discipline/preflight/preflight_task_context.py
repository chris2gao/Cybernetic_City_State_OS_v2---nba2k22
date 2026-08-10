"""One-shot task preflight.

Emits, in a single call, everything an executor must read before its first write:
physical remote master and work-branch SHAs, local head and ancestry, the hook
guard, worktree cleanliness, the task packet's allowlist and prohibitions, and
the state of any declared authorization gate.

It exists because that material was previously gathered over a dozen separate
tool round trips, each re-sending the whole conversation. It reads state; it
changes nothing and authorizes nothing. A green preflight means the listed facts
were true at this moment, not that an action is permitted.

Usage
    python preflight_task_context.py --packet <task packet yaml>
                                     [--repo-root .] [--no-remote] [--json]
                                     [--gate <yaml> --gate-key <dotted.path>]

Exit codes
    0  preflight complete and every hard precondition holds
    1  a hard precondition failed (dirty worktree, hook guard mismatch,
       head not descended from the packet base, master moved)
    3  input or git error
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


def git(repo_root: Path, *args: str, check: bool = True) -> tuple[int, str]:
    proc = subprocess.run(
        ["git", "-c", "core.quotepath=false", *args],
        cwd=repo_root, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False,
    )
    out = proc.stdout.decode("utf-8", "replace").strip()
    if check and proc.returncode != 0:
        raise RuntimeError(
            f"git {' '.join(args)} exited {proc.returncode}: "
            f"{proc.stderr.decode('utf-8', 'replace').strip()}"
        )
    return proc.returncode, out


def parse_ls_remote(text: str) -> dict[str, str]:
    refs = {}
    for line in text.splitlines():
        parts = line.split("\t")
        if len(parts) == 2:
            refs[parts[1]] = parts[0]
    return refs


def dotted_get(data, dotted: str):
    node = data
    for key in dotted.split("."):
        if not isinstance(node, dict) or key not in node:
            return None
        node = node[key]
    return node


def read_gate(gate_path: Path, dotted: str) -> dict:
    if yaml is None:
        raise RuntimeError("PyYAML is required to read a gate file")
    if not gate_path.exists():
        return {"path": str(gate_path).replace("\\", "/"), "present": False, "value": None,
                "open": False}
    value = dotted_get(yaml.safe_load(gate_path.read_text(encoding="utf-8")) or {}, dotted)
    return {
        "path": str(gate_path).replace("\\", "/"),
        "present": True,
        "key": dotted,
        "value": value,
        "open": value is True,
    }


def collect(repo_root: Path, packet: dict, use_remote: bool) -> dict:
    base = packet.get("exact_base_sha")
    branch = packet.get("branch")
    report: dict = {
        "task_id": packet.get("task_id"),
        "branch_declared": branch,
        "base_declared": base,
        "branch_actual": git(repo_root, "rev-parse", "--abbrev-ref", "HEAD")[1],
        "local_head": git(repo_root, "rev-parse", "HEAD")[1],
        "hooks_path": git(repo_root, "config", "--get", "core.hooksPath", check=False)[1],
        "quotepath": git(repo_root, "config", "--get", "core.quotepath", check=False)[1],
        "allowlist": packet.get("allowed_changed_paths") or [],
        "prohibitions": packet.get("explicit_prohibitions") or [],
        "required_tests": packet.get("required_tests") or [],
    }
    dirty = git(repo_root, "status", "--porcelain", "-z", "--untracked-files=all")[1]
    report["dirty_path_count"] = len([p for p in dirty.split("\0") if p])

    if base:
        rc, _ = git(repo_root, "merge-base", "--is-ancestor", base, "HEAD", check=False)
        report["head_descends_from_base"] = rc == 0
        rc, log = git(repo_root, "log", "--oneline", f"{base}..HEAD", check=False)
        report["commits_since_base"] = [l for l in log.splitlines() if l] if rc == 0 else None
    else:
        report["head_descends_from_base"] = None
        report["commits_since_base"] = None

    if use_remote:
        refs = parse_ls_remote(git(repo_root, "ls-remote", "origin", "master",
                                   f"refs/heads/{branch}" if branch else "master")[1])
        report["remote_master"] = refs.get("refs/heads/master")
        report["remote_branch"] = refs.get(f"refs/heads/{branch}") if branch else None
        expected = (packet.get("publisher") or {}).get("expected_remote_master_head")
        report["expected_remote_master"] = expected
        if not expected:
            report["master_verification"] = "no_expectation_declared"
            report["master_unchanged"] = None
        else:
            unchanged = report["remote_master"] == expected
            report["master_unchanged"] = unchanged
            report["master_verification"] = "verified_unchanged" if unchanged else "moved"
    else:
        report.update(remote_master=None, remote_branch=None,
                      expected_remote_master=None, master_unchanged=None,
                      master_verification="not_read")
    return report


def hard_failures(report: dict, require_clean: bool,
                  accept_unverified_master: bool = False) -> list[str]:
    """Conditions that must stop a write.

    Review finding F2: "not read" is not "verified". An unread master used to
    leave `master_unchanged` at None, which fell through every check and let the
    summary print `ok` for something the tool had never looked at. Unverified is
    now a failure unless the caller says in so many words that it accepts it.
    """
    failures = []
    if require_clean and report["dirty_path_count"]:
        failures.append(f"worktree_dirty:{report['dirty_path_count']}")
    if report["hooks_path"] != ".githooks":
        failures.append(f"hook_guard:{report['hooks_path'] or 'unset'}")
    if report["head_descends_from_base"] is False:
        failures.append("head_not_descended_from_declared_base")
    if report["branch_declared"] and report["branch_actual"] != report["branch_declared"]:
        failures.append(f"branch_mismatch:{report['branch_actual']}")

    verification = report.get("master_verification")
    if verification == "moved":
        failures.append(f"remote_master_moved:{report['remote_master']}")
    elif verification in {"not_read", "no_expectation_declared"} and not accept_unverified_master:
        failures.append(f"master_not_verified:{verification}")
    return failures


def render(report: dict, gate: dict | None, failures: list[str]) -> str:
    lines = [
        f"task            {report['task_id']}",
        f"branch          {report['branch_actual']}",
        f"local_head      {report['local_head']}",
        f"remote_branch   {report['remote_branch'] or '(not read)'}",
        f"remote_master   {report['remote_master'] or '(not read)'}"
        + {
            "verified_unchanged": "  verified unchanged",
            "moved": "  MOVED",
            "not_read": "  NOT VERIFIED (remote not read)",
            "no_expectation_declared": "  NOT VERIFIED (packet declares no expected head)",
        }.get(report.get("master_verification"), "  NOT VERIFIED"),
        f"base            {report['base_declared']}"
        + ("" if report["head_descends_from_base"] is None
           else "  (descends)" if report["head_descends_from_base"] else "  (NOT ancestor)"),
        f"commits_since   {len(report['commits_since_base'] or [])}",
        f"hooks_path      {report['hooks_path'] or '(unset)'}",
        f"dirty_paths     {report['dirty_path_count']}",
        f"allowlist       {len(report['allowlist'])} patterns",
        f"prohibitions    {len(report['prohibitions'])}",
        f"required_tests  {len(report['required_tests'])}",
    ]
    if gate is not None:
        state = "OPEN" if gate["open"] else ("present_but_closed" if gate["present"] else "ABSENT")
        lines.append(f"gate            {state}  {gate['path']}")
    if failures:
        summary = "BLOCKED"
    elif report.get("master_verification") != "verified_unchanged":
        # F2: never render a bare ok for a state the tool did not actually check.
        summary = "ok WITH UNVERIFIED MASTER (explicitly accepted by caller)"
    else:
        summary = "ok"
    lines.append(f"preflight       {summary}")
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--packet", required=True)
    parser.add_argument("--repo-root", default=".")
    parser.add_argument("--no-remote", action="store_true",
                        help="skip ls-remote; remote SHAs report as not read")
    parser.add_argument("--allow-dirty", action="store_true",
                        help="do not treat a dirty worktree as a hard failure")
    parser.add_argument("--accept-unverified-master", action="store_true",
                        help="proceed even though master was not verified; the summary "
                             "line will say so rather than reporting a bare ok")
    parser.add_argument("--gate", help="authorization gate yaml to inspect")
    parser.add_argument("--gate-key", default="authorization.enter_stage_06_execution")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    if yaml is None:
        print("preflight_error: PyYAML is required", file=sys.stderr)
        return 3
    try:
        repo_root = Path(args.repo_root).resolve()
        packet = yaml.safe_load(Path(args.packet).read_text(encoding="utf-8")) or {}
        report = collect(repo_root, packet, use_remote=not args.no_remote)
        gate = read_gate(repo_root / args.gate, args.gate_key) if args.gate else None
    except (RuntimeError, OSError, yaml.YAMLError) as exc:
        print(f"preflight_error: {exc}", file=sys.stderr)
        return 3

    failures = hard_failures(report, require_clean=not args.allow_dirty,
                             accept_unverified_master=args.accept_unverified_master)
    if args.json:
        print(json.dumps({"report": report, "gate": gate, "hard_failures": failures},
                         ensure_ascii=False, indent=2))
    else:
        print(render(report, gate, failures))
    for f in failures:
        print(f"preflight_blocked: {f}", file=sys.stderr)
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
