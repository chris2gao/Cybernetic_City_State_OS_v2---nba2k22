"""Run Live No-Op Multi-Chunk Batch via BoundedSessionExecutor (Gate G6)."""
from dataclasses import asdict
import json
from pathlib import Path
import sys
import time

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

import contracts
from bulk_executor import (
    BulkBatch,
    BulkBatchHeader,
    BulkIntentItem,
    CrossProcessFileLock
)
from bounded_session_transport import BoundedSessionExecutor
import transport


def build_live_noop_batch(batch_id: str = "BATCH-OPT-STAGE1-NOOP-20261101") -> BulkBatch:
    # 12 players across MIL (Team 1, 6 players) and POR (Team 28, 6 players)
    # Target: SHOT_TENDENCY with expected_before=0 and value=0 (No-op)
    intents = [
        # Milwaukee Bucks (Team 1)
        BulkIntentItem("I-NOOP-MIL-1607", "PLAYER_PATCH_TENDENCIES", 1, "SHOT_TENDENCY", 0, 0, player_id=1607),
        BulkIntentItem("I-NOOP-MIL-2492", "PLAYER_PATCH_TENDENCIES", 1, "SHOT_TENDENCY", 0, 0, player_id=2492),
        BulkIntentItem("I-NOOP-MIL-2768", "PLAYER_PATCH_TENDENCIES", 1, "SHOT_TENDENCY", 0, 0, player_id=2768),
        BulkIntentItem("I-NOOP-MIL-1516", "PLAYER_PATCH_TENDENCIES", 1, "SHOT_TENDENCY", 0, 0, player_id=1516),
        BulkIntentItem("I-NOOP-MIL-4392", "PLAYER_PATCH_TENDENCIES", 1, "SHOT_TENDENCY", 0, 0, player_id=4392),
        BulkIntentItem("I-NOOP-MIL-4454", "PLAYER_PATCH_TENDENCIES", 1, "SHOT_TENDENCY", 0, 0, player_id=4454),
        # Portland Trail Blazers (Team 28)
        BulkIntentItem("I-NOOP-POR-2459", "PLAYER_PATCH_TENDENCIES", 28, "SHOT_TENDENCY", 0, 0, player_id=2459),
        BulkIntentItem("I-NOOP-POR-2763", "PLAYER_PATCH_TENDENCIES", 28, "SHOT_TENDENCY", 0, 0, player_id=2763),
        BulkIntentItem("I-NOOP-POR-4456", "PLAYER_PATCH_TENDENCIES", 28, "SHOT_TENDENCY", 0, 0, player_id=4456),
        BulkIntentItem("I-NOOP-POR-2850", "PLAYER_PATCH_TENDENCIES", 28, "SHOT_TENDENCY", 0, 0, player_id=2850),
        BulkIntentItem("I-NOOP-POR-4111", "PLAYER_PATCH_TENDENCIES", 28, "SHOT_TENDENCY", 0, 0, player_id=4111),
        BulkIntentItem("I-NOOP-POR-2757", "PLAYER_PATCH_TENDENCIES", 28, "SHOT_TENDENCY", 0, 0, player_id=2757),
    ]

    header = BulkBatchHeader(
        batch_id=batch_id,
        save_instance_id="MyLEAGUE0003",
        game_build_sha256=contracts.BUILD,
        authorization_ref="HUMAN-AUTH-OPT-PILOT-20261101",
        source_snapshot_ref="snapshot_live_probe",
        expected_process_name="NBA2K22.exe",
        expected_pid=10404,
        dry_run=False
    )
    return BulkBatch(header=header, intents=intents)


def run_live_noop():
    run_dir = Path("01_os/07_content/_runs/run-20261101-nba2k22-rea-bulk-throughput-optimization-001")
    stage_dir = run_dir / ("07_" + "\u6d4b\u8bd5\u6267\u884c") / "stage1_session_noop"
    stage_dir.mkdir(parents=True, exist_ok=True)
    journal_dir = stage_dir / "journal"
    journal_dir.mkdir(parents=True, exist_ok=True)
    runtime_dir = stage_dir / "rea_runtime"
    runtime_dir.mkdir(parents=True, exist_ok=True)

    batch = build_live_noop_batch()
    batch_file = stage_dir / f"batch_{batch.header.batch_id}.json"
    batch_file.write_text(json.dumps({
        **asdict(batch.header),
        "intents": [asdict(i) for i in batch.intents]
    }, indent=2, ensure_ascii=False), encoding="utf-8")

    manifest = {
        "task_id": "NBA2K22-REA-BULK-THROUGHPUT-OPT-20261101-001",
        "human_authorization_ref": "HUMAN-AUTH-OPT-PILOT-20261101",
        "plan_digest": batch.plan_digest,
        "save_instance_id": "MyLEAGUE0003",
        "game_build_sha256": contracts.BUILD,
        "allowed_action_ids": ["PLAYER_PATCH_TENDENCIES", "MULTI_CHUNK_BOUNDED_SESSION"],
        "allowed_fields": ["SHOT_TENDENCY"],
        "expected_pid": 10404,
        "maximum_game_calls": 500,
        "cold_backup_path": "01_os/07_content/_runs/run-20261101-nba2k22-rea-controlled-live-bulk-pilot-001/cold_backup/MyLEAGUE0003_cold_backup",
        "cold_backup_sha256": "363cc773f935f632785c54c4d9ab1bf73455bb625b56797823f532eafcdf02d7"
    }
    manifest_file = stage_dir / f"manifest_{batch.header.batch_id}.json"
    manifest_file.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")

    live_ctx = transport.LiveExecutionContext(
        authorization_ref=manifest["human_authorization_ref"],
        allowed_action_ids=frozenset(manifest["allowed_action_ids"]),
        maximum_game_calls=manifest["maximum_game_calls"],
        enabled=True,
        expected_pid=10404
    )

    executor = BoundedSessionExecutor(
        journal_dir=journal_dir,
        live_context=live_ctx,
        verifier=manifest,
        runtime_dir=runtime_dir,
        duration_ms=2500
    )

    print(f"[*] Starting Live No-op Session Execution for batch {batch.header.batch_id}...")
    t0 = time.perf_counter()
    res = executor.execute_batch(batch, max_chunk_size=50)
    t_total_s = time.perf_counter() - t0

    print(f"[+] Execution completed in {res['execution_time_ms']:.2f} ms ({t_total_s:.3f} s total wall)")
    print(f"    Chunks:        {res['chunk_count']}")
    print(f"    Frida Attaches:{res['frida_attach_count']}")
    print(f"    Receipts:      {res['receipt_count']}")
    print(f"    Metrics:       {json.dumps(res['metrics'], indent=2)}")

    res_file = stage_dir / "execution_result.json"
    res_file.write_text(json.dumps(res, indent=2, ensure_ascii=False), encoding="utf-8")
    return res


if __name__ == "__main__":
    run_live_noop()
