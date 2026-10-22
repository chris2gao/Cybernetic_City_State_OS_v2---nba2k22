# -*- coding: utf-8 -*-
"""Read-only simulated process-change recovery; not a real restart test."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import sqlite3
import sys
import tempfile

import address_calibrator
from address_calibrator import AddressCalibrator
from memory import GameMemory
from snapshot_integrity import write_json_atomic


def valid_player(raw):
    names = [raw[start:start + 40].decode("utf-16le", errors="ignore").split("\0")[0].strip()
             for start in (40, 0)]
    return sum(c.isalpha() for c in " ".join(names)) >= 2


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--save-id", help="Existing isolated capture to compare with live memory")
    args = parser.parse_args()
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="backslashreplace")
    project = Path(__file__).resolve().parent.parent
    if args.save_id and not re.fullmatch(r"[A-Za-z0-9_-]+", args.save_id):
        raise ValueError("Invalid save ID")
    save_dir = project / "database" / "saves" / args.save_id if args.save_id else None
    pool_db = save_dir / "player_pool.sqlite" if save_dir else None
    if pool_db and not pool_db.is_file():
        raise FileNotFoundError(pool_db)
    original_map = address_calibrator.MAP_FILE
    original_bytes = Path(original_map).read_bytes()
    runtime_map = json.loads(original_bytes)
    cached_pool = int(runtime_map["player_pool"]["base_addr"], 16)
    runtime_map["pid"] = -1  # Preserve addresses: production code must discard them.
    result = {"test_kind": "SIMULATED_PROCESS_CHANGE_SAME_PID", "real_restart_verified": False}

    with tempfile.TemporaryDirectory(prefix="address_rescan_check_", dir=project / "database" / "saves") as temp_dir:
        test_map = Path(temp_dir) / "runtime_memory_map.json"
        test_map.write_text(json.dumps(runtime_map), encoding="utf-8")
        address_calibrator.MAP_FILE = str(test_map)
        try:
            with GameMemory(read_only=True) as mem:
                calibrator = AddressCalibrator(mem)
                report = calibrator.run_full_calibration()
                new_pool = int(report["player_pool"]["base_addr"], 16)
                from source_extensions import roster_directory
                directory = roster_directory(mem, new_pool)
                stride, slots = 0x4F0, directory['players']['count'] + 1
                result['directory_counts'] = {key: value['count'] for key, value in directory.items()}
                left = mem.read_bytes(cached_pool, stride * slots)
                right = mem.read_bytes(new_pool, stride * slots)
                if left is None or right is None:
                    raise RuntimeError("Could not read both complete player pools")
                valid_differences, invalid_differences, valid_slots = [], [], []
                for slot in range(slots):
                    a = left[slot * stride:(slot + 1) * stride]
                    b = right[slot * stride:(slot + 1) * stride]
                    a_valid, b_valid = valid_player(a), valid_player(b)
                    if a_valid or b_valid:
                        valid_slots.append(slot)
                        if a_valid != b_valid or a != b:
                            valid_differences.append(slot)
                    elif a != b:
                        invalid_differences.append(slot)
                db_mismatches, db_count = [], None
                if pool_db:
                    with sqlite3.connect(pool_db.resolve().as_uri() + "?mode=ro", uri=True) as conn:
                        records = conn.execute("SELECT slot_id, raw_struct FROM player_pool").fetchall()
                    db_count = len(records)
                    for slot, raw in records:
                        live = right[slot * stride:(slot + 1) * stride]
                        if not 0 <= slot < slots or raw != live or not valid_player(live):
                            db_mismatches.append(slot)
                    if {row[0] for row in records} != set(valid_slots):
                        db_mismatches.append("slot_set_differs")
                result.update({
                    "pid": mem.pid, "calibration": report,
                    "cached_pool": hex(cached_pool), "rescanned_pool": hex(new_pool),
                    "valid_player_slots": len(valid_slots),
                    "valid_slot_difference_count": len(valid_differences),
                    "valid_slot_difference_examples": valid_differences[:12],
                    "invalid_slot_differences": invalid_differences,
                    "database_records_compared": db_count,
                    "database_mismatch_count": len(db_mismatches),
                    "database_mismatch_examples": db_mismatches[:12],
                    "checks": {
                        "process_change_invalidated_cache": calibrator.process_changed,
                        "all_anchors_healthy": report["status"] == "HEALTHY",
                        "valid_player_pools_byte_identical": not valid_differences and bool(valid_slots),
                        "all_database_player_blobs_match_live": (not db_mismatches and db_count == len(valid_slots)) if pool_db else None,
                    },
                })
        finally:
            address_calibrator.MAP_FILE = original_map
    result["checks"]["authoritative_map_unchanged"] = Path(original_map).read_bytes() == original_bytes
    result["authoritative_map_sha256"] = hashlib.sha256(original_bytes).hexdigest()
    result["passed"] = all(value for value in result["checks"].values() if value is not None)
    output = (save_dir / "validation" if save_dir else project / "database" / "saves") / "forced_rescan_validation.json"
    write_json_atomic(str(output), result)
    print(f"[CHECK] Valid player slots: {len(valid_slots)}; live differences: {len(valid_differences)}; "
          f"DB records: {db_count}; DB mismatches: {len(db_mismatches)}; invalid-slot differences: {invalid_differences}")
    print(f"[{'PASS' if result['passed'] else 'FAIL'}] Same-PID simulated process-change recovery; report: {output}")
    print("[INFO] A real new-PID capture is still required after the player restarts the game.")
    if not result["passed"]:
        raise RuntimeError("Forced rescan verification failed; inspect the JSON report")


if __name__ == "__main__":
    main()
