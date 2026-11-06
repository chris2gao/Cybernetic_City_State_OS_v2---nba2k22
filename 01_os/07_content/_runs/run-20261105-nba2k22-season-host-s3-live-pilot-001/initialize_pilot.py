"""Initialize the S3 pilot after the operator identifies the loaded save."""
import argparse
import hashlib
import json
import os
import shutil
import sys
import time
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
DOMAIN = ROOT / "08_Domain_Applications/Antigravity_GM_Engine"
sys.path[:0] = [str(DOMAIN / "world_data_prototype"), str(DOMAIN / "research/rea_native_control")]
from live_world import initialize_save
from refresh import _context
from season_cycle_host import SeasonCycleHost



def sha(path):
    with path.open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def write(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--declared-loaded-filename", choices=("MyLEAGUE0003", "MyLEAGUE0005"), required=True)
    parser.add_argument("--epoch-receipt", type=Path, required=True)
    parser.add_argument("--runtime", type=Path, required=True)
    args = parser.parse_args()
    l0 = json.loads(args.epoch_receipt.read_bytes())
    assert l0["status"] == "LIVE_READ" and l0["in_progress_count"] == 0
    pid = l0["pid"]
    current = _context(pid)
    assert current["epoch"] == l0["process_epoch"], "Game process/build/season epoch changed"
    assert current["game_progress"] == l0["game_mode_progress"], "Game progress changed before baseline"
    native_root = Path(os.environ["NBA2K22_S3_NATIVE_SAVE_ROOT"])
    if not native_root.is_absolute():
        raise ValueError("NBA2K22_S3_NATIVE_SAVE_ROOT must be an absolute path")
    native = native_root / args.declared_loaded_filename
    save_id = "nba2k22_test_01" if native.name == "MyLEAGUE0003" else "s3_test_myleague0005"
    runtime = args.runtime.resolve()
    expected_parent = ROOT.parent.resolve()
    if runtime.parent != expected_parent or runtime.name != "s3-live-private":
        raise ValueError("Runtime must be the dedicated S3 directory adjacent to this worktree")
    runtime.mkdir(exist_ok=False)
    started = time.perf_counter()
    result = {"phase": "L1", "source": "Human-declared loaded filename with live epoch verification",
              "filename": native.name, "pid": pid, "process_epoch": current["epoch"]}
    native_before = None
    try:
        native_before = sha(native)
        backup = runtime / "native-disk-backup"
        backup.mkdir()
        shutil.copyfile(native, backup / native.name)
        if sha(backup / native.name) != native_before or sha(native) != native_before:
            raise RuntimeError("Save file changed during verified disk backup")
        result["disk_backup"] = {"file": str(backup / native.name), "sha256": native_before}
        save = runtime / "world"
        initialize_save(save, save_id, native)
        shutil.copyfile(save / "save.json", runtime / "save.before-host.json")
        host = SeasonCycleHost(workspace_root=ROOT, state_file=runtime / "host-state.json",
                               ledger_file=runtime / "host-ledger.jsonl", outbox_db=runtime / "outbox.sqlite")
        result["host"] = host.initialize_season(str(save), native.name, pid=pid, force_new_worldline=True)
        result["status"] = "BASELINE_RETURNED"
    except Exception as exc:
        result.update(status="FAILED", error=repr(exc), traceback=traceback.format_exc())
    finally:
        result["native_sha256_before"] = native_before
        result["native_sha256_after"] = sha(native)
        result["native_disk_unchanged"] = result["native_sha256_after"] == native_before
        result["wall_seconds"] = time.perf_counter() - started
        write(runtime / "l1-receipt.json", result)
    return 0 if result["status"] == "BASELINE_RETURNED" and result["native_disk_unchanged"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
