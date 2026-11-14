"""Retain this stopped task's small audit evidence, without copying bulk captures."""
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import sqlite3
import subprocess

REPO = Path(__file__).resolve().parents[5]
RUN = Path(__file__).resolve().parents[1]
ROOT = Path("C:/Users/gk/Documents/ChatGPT/nba2k22/ge01-runtime")
DEST = RUN / "evidence/ge01-audit"


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def main():
    actual = Path(subprocess.check_output(["git", "rev-parse", "--show-toplevel"], cwd=REPO, text=True).strip()).resolve()
    assert actual == REPO.resolve() and actual.name.startswith("Cybernetic_City_State_OS_v2 - ")
    suffix = actual.name.split(" - ", 1)[1]
    vault = Path("E:/newStand/城邦简报") / suffix / "03_决策档案/20261114-GE01-W01-执行止损与时间审计"
    DEST.mkdir(exist_ok=True)
    vault.mkdir(parents=True, exist_ok=True)
    selected = [
        "FORMAL_CONTRACT.md", "core-issue24-comment6873776739.json", "HISTORICAL_DATA_INVENTORY.json",
        "FRESH_BASELINE_RECEIPT.json", "clean-0005-01/FRESH_BASELINE_RECEIPT.json",
        "clean-0005-01/world-0005/save.json", "clean-0005-01/fresh-capture/refresh-report.json",
        "REA_NATIVE_TODAY.json", "READ_ONLY_ENGINE_FRAME.json", "read_engine_frame.js",
        "GE01_W01_PLAN.json", "GE01_W01_REVIEW_ENVELOPE.json", "GE01_W01_ENVELOPE.md",
        "GE01_QUALIFICATION_REUSE_EVIDENCE.json", "GE01_NATIVE_CALENDAR_PLANS.json", "HUMAN_APPROVAL.json",
        "ENTRY_STARTED.json", "ENTRY_APPROVAL.json", "ENTRY_RESULT.json", "ENTRY_RECONCILIATION_TODAY.json",
        "ENTRY_NO_EFFECT_PROOF.json", "ENTRY_REPAIRED_PLAN.json", "ENTRY_REPAIR_APPROVAL.json",
        "REPAIR_01_STARTED.json", "REPAIR_01_RESULT.json", "entry.stdout.log", "entry.stderr.log",
        "repair-01.stdout.log", "repair-01.stderr.log", "repair-01.exit.txt",
        "capture.stdout.log", "capture.stderr.log", "capture.exit.txt",
        "clean-capture.stdout.log", "clean-capture.stderr.log", "clean-capture.exit.txt",
        "launch_capture.ps1", "launch_entry.ps1", "launch_single_repair.ps1",
        "GE01_EXECUTION_TIMELINE.json", "GE01_EXECUTION_EVENTS.csv",
    ]
    for group in ("entry-native", "entry-repair-01-native"):
        selected.extend(path.relative_to(ROOT).as_posix() for path in (ROOT / group).glob("*/*") if path.is_file())
    outbox = RUN / "_runtime/qualification-live-fast/outbox.sqlite"
    results = [json.loads((ROOT / name).read_bytes()) for name in ("ENTRY_RESULT.json", "REPAIR_01_RESULT.json")]
    claims = []
    with sqlite3.connect(outbox.as_uri() + "?mode=ro", uri=True) as conn:
        conn.row_factory = sqlite3.Row
        for result in results:
            claims.append({"plan_digest": result["plan_digest"],
                           "claim": [dict(row) for row in conn.execute("SELECT * FROM test_calendar_claims WHERE plan_digest=?", (result["plan_digest"],))],
                           "reconciliation": [dict(row) for row in conn.execute("SELECT * FROM test_calendar_reconciliations WHERE plan_digest=?", (result["plan_digest"],))]})
    (ROOT / "OUTBOX_STOP_SNAPSHOT.json").write_text(json.dumps(claims, indent=2) + "\n", encoding="utf-8")
    selected.append("OUTBOX_STOP_SNAPSHOT.json")
    stopped = {"status": "STOPPED_BY_HUMAN_CONDITION", "human_instruction": "只修复一次，如果没解决就停止任务，并记录当前任务从开始阶段的执行",
               "condition_met": True, "repair_attempts": 1, "formal_setters": 0, "actual_calendar_dispatches": 0,
               "W01_complete": False, "further_game_work_authorized": False,
               "recorded_at": datetime.now(timezone.utc).isoformat()}
    (ROOT / "STOPPED_BY_HUMAN.json").write_text(json.dumps(stopped, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    selected.append("STOPPED_BY_HUMAN.json")
    records = []
    for name in selected:
        source = ROOT / name
        assert source.is_file(), name
        relative = Path(name)
        for target_root in (DEST, vault / "evidence"):
            target = target_root / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(source, target)
        raw = source.read_bytes()
        records.append({"path": relative.as_posix(), "source": str(source), "sha256": sha(raw), "bytes": len(raw)})
    patch = subprocess.check_output(["git", "diff", "--binary", "--", RUN.relative_to(REPO).as_posix(),
                                     "08_Domain_Applications/Antigravity_GM_Engine/research/rea_native_control"], cwd=REPO)
    (DEST / "WORKTREE_DIFF.patch").write_bytes(patch)
    (vault / "WORKTREE_DIFF.patch").write_bytes(patch)
    scripts = []
    for source in sorted((RUN / "evidence").glob("ge01_*.py")):
        raw = source.read_bytes()
        for target_root in (DEST / "used-scripts", vault / "used-scripts"):
            target_root.mkdir(exist_ok=True)
            (target_root / source.name).write_bytes(raw)
        scripts.append({"path": source.relative_to(REPO).as_posix(), "sha256": sha(raw), "bytes": len(raw)})
    head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=REPO, text=True).strip()
    manifest = {"execution_base": head, "source_state": "base_plus_retained_worktree_diff_and_untracked_used_scripts",
                "runtime_root": str(ROOT), "vault": str(vault), "evidence": records, "used_scripts": scripts,
                "worktree_diff_sha256": sha(patch), "worktree_diff_bytes": len(patch),
                "bulk_sources": "Fresh DB/captures and original historic data retained at original paths; not duplicated or deleted",
                "session": "C:/Users/gk/.codex/sessions/2026/11/12/rollout-2026-11-12T02-44-00-01a1cf5b-78c5-7d32-815a-a8f6a647ed38.jsonl",
                "private_reasoning_exported": False}
    body = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode()
    (DEST / "MANIFEST.json").write_bytes(body)
    (vault / "MANIFEST.json").write_bytes(body)
    audit = (RUN / "GE01_EXECUTION_AUDIT.md").read_bytes()
    (vault / "GE01_EXECUTION_AUDIT.md").write_bytes(audit)
    print(json.dumps({"files": len(records), "used_scripts": len(scripts), "vault": str(vault), "bytes": sum(row["bytes"] for row in records),
                      "source_patch_sha256": sha(patch), "audit_sha256": sha(audit)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
