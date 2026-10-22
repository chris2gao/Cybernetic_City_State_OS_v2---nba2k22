"""Meaningful negative checks: tampered export/audit and missing game context."""
import argparse
import base64
import contextlib
import io
import json
from pathlib import Path
import shutil
import sys
import tempfile

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))
from data_context import decode_context, PREFIX
from export_web_gm import verify_bundle
from gm_engine import GMEngine
from snapshot_integrity import file_sha256


def rejects(action):
    try:
        action()
    except (RuntimeError, ValueError):
        return
    raise AssertionError("Invalid data was accepted")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--save-id", required=True)
    save_id = parser.parse_args().save_id
    pointer_file = ROOT / "published/saves" / save_id / "latest.json"
    pointer_hash = file_sha256(str(pointer_file))
    pointer = json.loads(pointer_file.read_text(encoding="utf-8"))
    batch = ROOT / "published" / pointer["batch_path"]
    manifest = verify_bundle(batch, pointer["manifest_sha256"])
    with tempfile.TemporaryDirectory(prefix="gm_negative_checks_") as temporary:
        root = Path(temporary)
        copied = root / "bundle"
        shutil.copytree(batch, copied)
        with (copied / "SUMMARY.md").open("a", encoding="utf-8") as target:
            target.write("tampered")
        rejects(lambda: verify_bundle(copied, pointer["manifest_sha256"]))
        snapshots = root / "snapshots"
        snapshots.mkdir()
        source = ROOT / "database/saves" / save_id
        snapshot = manifest["snapshot_id"]
        for prefix in ("ingest_manifest", "ai_sampling_audit"):
            shutil.copy2(source / "snapshots" / f"{prefix}_{snapshot}.json", snapshots)
        audit_file = snapshots / f"ai_sampling_audit_{snapshot}.json"
        audit = json.loads(audit_file.read_text(encoding="utf-8"))
        audit["checks"]["negative_test"] = False
        audit_file.write_text(json.dumps(audit), encoding="utf-8")
        with contextlib.redirect_stdout(io.StringIO()):
            rejects(lambda: GMEngine(db_path=str(source / "league_state.sqlite"), snapshots_dir=str(snapshots), player_pool_db_path=str(source / "player_pool.sqlite")).verify_snapshot_gate(snapshot))
    invalid = {"trigger": "PLAYER_INITIATED", "purpose": "production", "game_date": None}
    encoded = PREFIX + base64.b64encode(json.dumps(invalid).encode()).decode()
    rejects(lambda: decode_context(encoded))
    if file_sha256(str(pointer_file)) != pointer_hash:
        raise AssertionError("Negative checks changed the real latest pointer")
    print("[PASS] Tampered file, failed audit and missing game date rejected; real latest unchanged.")


if __name__ == "__main__":
    main()
