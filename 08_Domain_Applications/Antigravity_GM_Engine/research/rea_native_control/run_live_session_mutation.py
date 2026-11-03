"""Run Live Bounded Mutation Multi-Chunk Batch via BoundedSessionExecutor (Gate G7)."""
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


def build_live_mutation_batch(batch_id: str, targets: dict, new_value: int) -> BulkBatch:
    # 12 players across MIL (Team 1, 6 players) and POR (Team 28, 6 players)
    mil_pids = [1607, 2492, 2768, 1516, 4392, 4454]
    por_pids = [2459, 2763, 4456, 2850, 4111, 2757]

    intents = []
    for pid in mil_pids:
        exp = targets.get((1, pid), 0)
        intents.append(BulkIntentItem(
            f"I-MUT-{batch_id}-MIL-{pid}",
            "PLAYER_PATCH_TENDENCIES",
            1,
            "SHOT_TENDENCY",
            exp,
            new_value,
            player_id=pid
        ))

    for pid in por_pids:
        exp = targets.get((28, pid), 0)
        intents.append(BulkIntentItem(
            f"I-MUT-{batch_id}-POR-{pid}",
            "PLAYER_PATCH_TENDENCIES",
            28,
            "SHOT_TENDENCY",
            exp,
            new_value,
            player_id=pid
        ))

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


def execute_mutation_stage(stage_name: str, batch_id: str, current_targets: dict, new_value: int) -> dict:
    run_dir = Path("01_os/07_content/_runs/run-20261101-nba2k22-rea-bulk-throughput-optimization-001")
    stage_dir = run_dir / ("07_" + "\u6d4b\u8bd5\u6267\u884c") / stage_name
    stage_dir.mkdir(parents=True, exist_ok=True)
    journal_dir = stage_dir / "journal"
    journal_dir.mkdir(parents=True, exist_ok=True)
    runtime_dir = stage_dir / "rea_runtime"
    runtime_dir.mkdir(parents=True, exist_ok=True)

    batch = build_live_mutation_batch(batch_id, current_targets, new_value)
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

    print(f"[*] Starting Execution for {stage_name} ({batch.header.batch_id})...")
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


def run():
    # Stage 2A: Mutate from current (1516=1, others=0) to 5
    cur_targets = {(1, 1516): 1}
    print("=== STAGE 2A: 12 Real Mutations to 5 ===")
    res_2a = execute_mutation_stage(
        "stage2_session_mutation",
        "BATCH-OPT-MUT-TO-5",
        cur_targets,
        5
    )

    # Stage 2B: Mutate all 12 from 5 to 0 (leaving game in 0 state per user instruction)
    cur_targets_5 = {
        (1, 1607): 5, (1, 2492): 5, (1, 2768): 5, (1, 1516): 5, (1, 4392): 5, (1, 4454): 5,
        (28, 2459): 5, (28, 2763): 5, (28, 4456): 5, (28, 2850): 5, (28, 4111): 5, (28, 2757): 5
    }
    print("\n=== STAGE 2B: 12 Real Mutations to 0 (Restoring requested minimum writable) ===")
    res_2b = execute_mutation_stage(
        "stage2b_session_mutation_to_zero",
        "BATCH-OPT-MUT-TO-0",
        cur_targets_5,
        0
    )


if __name__ == "__main__":
    run()
