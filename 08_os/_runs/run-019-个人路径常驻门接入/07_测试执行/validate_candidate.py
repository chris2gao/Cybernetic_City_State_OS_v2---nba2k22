from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys

import yaml


ROOT = Path(__file__).resolve().parents[4]
RUN = ROOT / "08_os/_runs/run-019-个人路径常驻门接入"
BASE = "d85768c18989935ea9090220ee792e02072bbf5a"


def git(*args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-c", "core.quotepath=false", *args],
        cwd=ROOT,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=check,
    )


def load_front_matter(path: Path) -> dict[str, object]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError(f"missing YAML front matter: {path}")
    front = text.split("---\n", 2)[1]
    document = yaml.safe_load(front)
    if not isinstance(document, dict):
        raise ValueError(f"invalid YAML front matter: {path}")
    return document


def main() -> int:
    expected = {
        line
        for line in (RUN / "06_执行/changed_paths.txt").read_text(encoding="utf-8").splitlines()
        if line
    }
    actual = set(git("diff", "--name-only", "--diff-filter=ACMR", BASE).stdout.splitlines())
    actual.update(git("ls-files", "--others", "--exclude-standard").stdout.splitlines())

    hook = (ROOT / ".githooks/pre-push").read_bytes()
    staged_hook = subprocess.run(
        ["git", "show", ":.githooks/pre-push"],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True,
    ).stdout
    guards = yaml.safe_load((ROOT / "08_os/05_registry/repository_guards_v1.yml").read_text(encoding="utf-8"))
    validators = yaml.safe_load((ROOT / "08_os/05_registry/repository_validation_v1.yml").read_text(encoding="utf-8"))
    run_document = yaml.safe_load((RUN / "run.yml").read_text(encoding="utf-8"))
    json.loads((ROOT / "08_os/06_execution/validators/personal_paths/patterns.json").read_text(encoding="utf-8"))
    json.loads((RUN / "07_测试执行/results.json").read_text(encoding="utf-8"))

    inbox = load_front_matter(ROOT / ".ai/INBOX.md")
    state = yaml.safe_load((ROOT / ".ai/STATE.yml").read_text(encoding="utf-8"))
    outbox = yaml.safe_load((ROOT / ".ai/OUTBOX.md").read_text(encoding="utf-8"))
    human_brief = (ROOT / ".ai/HUMAN_BRIEF.md").read_text(encoding="utf-8")

    old_run_name = "run-" + "016" + "-转义"
    rename_search = git("grep", "-n", old_run_name, "--", "08_os", check=False)
    diff_check = git("diff", "--check", check=False)
    checks = {
        "changed_paths_exact": actual == expected,
        "no_ai_changes": not any(path.startswith(".ai/") for path in actual),
        "run014_unchanged": not any(path.startswith("08_os/_runs/run-014-") for path in actual),
        "old_run_name_absent": rename_search.returncode == 1,
        "hook_lf_worktree": hook.startswith(b"#!/bin/sh\n") and b"\r\n" not in hook,
        "hook_lf_staged_blob": staged_hook.startswith(b"#!/bin/sh\n") and b"\r\n" not in staged_hook,
        "diff_check": diff_check.returncode == 0,
        "guards_registry_has_hook": any(item.get("path") == ".githooks/pre-push" for item in guards["guards"]),
        "validation_registry_has_validator": any(
            item.get("path") == "08_os/06_execution/validators/personal_paths/validate.py"
            for item in validators["validators"]
        ),
        "run_id_correct": run_document.get("run_id") == "run-019-个人路径常驻门接入",
        "inbox_neutral": inbox.get("intent") == "neutral_baseline" and inbox.get("packet_id") is None and inbox.get("task_id") is None,
        "state_neutral": state.get("status") == "neutral_baseline" and state.get("active_task") is None and state.get("report_ref") is None,
        "outbox_neutral": outbox.get("status") == "neutral_baseline" and outbox.get("packet_id") is None and outbox.get("report_ref") is None,
        "human_brief_neutral": "No active task, packet, review request, or pending Human gate" in human_brief,
    }
    summary = {
        "schema_version": "citystate.personal_path_candidate_check.v1",
        "changed_paths": sorted(actual),
        "checks": checks,
        "passed": all(checks.values()),
    }
    print(json.dumps(summary, ensure_ascii=False, sort_keys=True))
    return 0 if summary["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
