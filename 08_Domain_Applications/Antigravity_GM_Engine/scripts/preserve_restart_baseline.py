"""Preserve a verified capture and runtime map before the player restarts NBA2K22."""
import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import re
import shutil
import sqlite3
import sys

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from snapshot_integrity import file_sha256, snapshot_digest, write_json_atomic


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--save-id", required=True)
    parser.add_argument("--snapshot", required=True)
    args = parser.parse_args()
    if not all(re.fullmatch(r"[A-Za-z0-9_-]+", value) for value in (args.save_id, args.snapshot)):
        raise ValueError("Invalid save ID or snapshot ID")
    save = ROOT / "database" / "saves" / args.save_id
    manifest_path = save / "snapshots" / f"ingest_manifest_{args.snapshot}.json"
    audit_path = save / "snapshots" / f"ai_sampling_audit_{args.snapshot}.json"
    manifest, audit = load_json(manifest_path), load_json(audit_path)
    runtime_path = ROOT / "database" / "runtime_memory_map.json"
    runtime = load_json(runtime_path)
    if audit["verdict"] != "PASS_VERIFIED" or not audit["checks"] or not all(audit["checks"].values()):
        raise RuntimeError("Baseline capture has not passed every audit check")
    if file_sha256(str(manifest_path)) != audit["manifest_binding"]["manifest_sha256"]:
        raise RuntimeError("Manifest changed after audit")
    if manifest["calibration"]["pid"] != runtime["pid"] or audit["live_calibration"]["pid"] != runtime["pid"]:
        raise RuntimeError("Runtime map and capture do not belong to the same PID")
    pool_source = save / "player_pool.sqlite"
    if file_sha256(str(pool_source)) != audit["player_pool_sha256"]:
        raise RuntimeError("Player pool changed after audit")
    destination = save / "validation" / "pre_restart"
    if destination.exists():
        raise FileExistsError(f"Baseline already exists; preserve it: {destination}")
    source = sqlite3.connect((save / "league_state.sqlite").as_uri() + "?mode=ro", uri=True)
    try:
        if snapshot_digest(source, args.snapshot) != audit["database_digest_sha256"]:
            raise RuntimeError("League snapshot changed after audit")
        destination.mkdir(parents=True)
        backup = sqlite3.connect(destination / "league_state.sqlite")
        try:
            source.backup(backup)
        finally:
            backup.close()
    finally:
        source.close()
    for source_path in (pool_source, manifest_path, audit_path, runtime_path):
        shutil.copy2(source_path, destination / source_path.name)
    if file_sha256(str(destination / "player_pool.sqlite")) != audit["player_pool_sha256"]:
        raise RuntimeError("Preserved player pool does not match the verified source")
    evidence = {
        "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
        "save_id": args.save_id, "snapshot_id": args.snapshot,
        "before_pid": runtime["pid"], "before_module_base": runtime["module_base"],
        "audit_checks_passed": len(audit["checks"]),
        "counts": audit["counts"],
        "player_pool_records": audit["player_pool_records"],
        "historical_rookies": audit["historical_rookie_marker_records"],
        "snapshot_digest_sha256": audit["database_digest_sha256"],
        "player_pool_sha256": audit["player_pool_sha256"],
        "real_restart_verified": False,
        "next_step": "Player restarts the game and loads the same save; capture POST_RESTART with the retained old runtime map.",
    }
    write_json_atomic(str(destination / "baseline_evidence.json"), evidence)
    print(json.dumps(evidence, ensure_ascii=True, indent=2))
    print(f"[PASS] Verified pre-restart baseline preserved: {destination}")


if __name__ == "__main__":
    main()
