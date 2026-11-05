"""Live Bulk Pilot - Stage 1: Live No-op Multi-Chunk Execution.
Executes 12 intents across 2 teams (Team 28 and Team 1) with value == currentVal.
Proves genuine game readback, 0 Setter calls, UNCHANGED_ALREADY_TARGET receipts.
"""
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import sys

_RESEARCH_DIR = Path(__file__).resolve().parent
if str(_RESEARCH_DIR) not in sys.path:
    sys.path.insert(0, str(_RESEARCH_DIR))

import contracts
from bulk_executor import (
    BulkBatch,
    BulkBatchHeader,
    BulkIntentItem,
    BulkExecutorService,
    CrossProcessFileLock,
    ReaChunkTransportAdapter,
    sha256_digest
)
import transport

def main():
    run_dir = Path("01_os/07_content/_runs/run-20261101-nba2k22-rea-controlled-live-bulk-pilot-001/07_测试执行/stage1_noop").resolve()
    run_dir.mkdir(parents=True, exist_ok=True)
    journal_dir = run_dir / "journal"
    runtime_dir = run_dir / "rea_runtime"
    lock_file = journal_dir / "live_executor.lock"

    # Preflight verification parameters
    game_build_sha = contracts.BUILD
    expected_pid = 10404
    cold_backup_sha = "363cc773f935f632785c54c4d9ab1bf73455bb625b56797823f532eafcdf02d7"
    run_root = Path("01_os/07_content/_runs/run-20261101-nba2k22-rea-controlled-live-bulk-pilot-001").resolve()
    cold_backup_path = run_root / "cold_backup" / "MyLEAGUE0003_cold_backup"
    assert cold_backup_path.is_file(), f"Cold backup missing at {cold_backup_path}"
    assert hashlib.sha256(cold_backup_path.read_bytes()).hexdigest() == cold_backup_sha, "Cold backup hash mismatch"

    header = BulkBatchHeader(
        batch_id="BATCH-PILOT-STAGE1-NOOP-20261101",
        save_instance_id="MyLEAGUE0003",
        game_build_sha256=game_build_sha,
        source_snapshot_ref="snap_live_pilot_v1",
        expected_process_name="NBA2K22.exe",
        expected_pid=expected_pid,
        authorization_ref="Human conversation instruction 2026-11-01: 批准，许可授权，直接做批量的测试吧",
        dry_run=False
    )

    intents = [
        # Chunk 1: Team 28 (POR) - 6 players
        BulkIntentItem(intent_id="I-NOOP-POR-2459", action_id="PLAYER_PATCH_TENDENCIES", team_id=28, player_id=2459, field_id="SHOT_TENDENCY", expected_before=80, value=80),
        BulkIntentItem(intent_id="I-NOOP-POR-2763", action_id="PLAYER_PATCH_TENDENCIES", team_id=28, player_id=2763, field_id="SHOT_TENDENCY", expected_before=88, value=88),
        BulkIntentItem(intent_id="I-NOOP-POR-4456", action_id="PLAYER_PATCH_TENDENCIES", team_id=28, player_id=4456, field_id="SHOT_TENDENCY", expected_before=78, value=78),
        BulkIntentItem(intent_id="I-NOOP-POR-2850", action_id="PLAYER_PATCH_TENDENCIES", team_id=28, player_id=2850, field_id="SHOT_TENDENCY", expected_before=55, value=55),
        BulkIntentItem(intent_id="I-NOOP-POR-4111", action_id="PLAYER_PATCH_TENDENCIES", team_id=28, player_id=4111, field_id="SHOT_TENDENCY", expected_before=62, value=62),
        BulkIntentItem(intent_id="I-NOOP-POR-2757", action_id="PLAYER_PATCH_TENDENCIES", team_id=28, player_id=2757, field_id="SHOT_TENDENCY", expected_before=55, value=55),

        # Chunk 2: Team 1 (MIL) - 6 players
        BulkIntentItem(intent_id="I-NOOP-MIL-1607", action_id="PLAYER_PATCH_TENDENCIES", team_id=1, player_id=1607, field_id="SHOT_TENDENCY", expected_before=70, value=70),
        BulkIntentItem(intent_id="I-NOOP-MIL-2492", action_id="PLAYER_PATCH_TENDENCIES", team_id=1, player_id=2492, field_id="SHOT_TENDENCY", expected_before=80, value=80),
        BulkIntentItem(intent_id="I-NOOP-MIL-2768", action_id="PLAYER_PATCH_TENDENCIES", team_id=1, player_id=2768, field_id="SHOT_TENDENCY", expected_before=99, value=99),
        BulkIntentItem(intent_id="I-NOOP-MIL-1516", action_id="PLAYER_PATCH_TENDENCIES", team_id=1, player_id=1516, field_id="SHOT_TENDENCY", expected_before=58, value=58),
        BulkIntentItem(intent_id="I-NOOP-MIL-4392", action_id="PLAYER_PATCH_TENDENCIES", team_id=1, player_id=4392, field_id="SHOT_TENDENCY", expected_before=35, value=35),
        BulkIntentItem(intent_id="I-NOOP-MIL-4454", action_id="PLAYER_PATCH_TENDENCIES", team_id=1, player_id=4454, field_id="SHOT_TENDENCY", expected_before=65, value=65),
    ]

    batch = BulkBatch(header=header, intents=tuple(intents))
    batch_file = run_dir / "batch_stage1_noop.json"
    batch_dict = {**asdict(batch.header), "intents": [asdict(i) for i in batch.intents]}
    batch_file.write_text(json.dumps(batch_dict, indent=2), encoding='utf-8')

    manifest = {
        "schema_version": "nba2k22.rea.live_pilot_manifest.v1",
        "task_id": "NBA2K22-REA-CONTROLLED-LIVE-BULK-PILOT-20261101-001",
        "human_authorization_ref": header.authorization_ref,
        "attempt_id": "attempt_stage1_noop_001",
        "save_instance_id": header.save_instance_id,
        "plan_digest": batch.plan_digest,
        "game_build_sha256": game_build_sha,
        "expected_pid": expected_pid,
        "allowed_action_ids": ["PLAYER_PATCH_TENDENCIES"],
        "allowed_fields": ["SHOT_TENDENCY"],
        "maximum_game_calls": 300,
        "cold_backup_sha256": cold_backup_sha,
        "cold_backup_path": str(cold_backup_path)
    }
    manifest_file = run_dir / "manifest_stage1_noop.json"
    manifest_file.write_text(json.dumps(manifest, indent=2), encoding='utf-8')

    print(f"[*] Starting Stage 1 Live No-Op Execution...")
    print(f"    Batch ID:     {header.batch_id}")
    print(f"    Plan Digest:  {batch.plan_digest}")
    print(f"    Total Items:  {len(intents)} across 2 teams")

    with CrossProcessFileLock(lock_file):
        live_ctx = transport.LiveExecutionContext(
            authorization_ref=header.authorization_ref,
            allowed_action_ids=frozenset(["PLAYER_PATCH_TENDENCIES"]),
            maximum_game_calls=300,
            enabled=True,
            expected_pid=expected_pid
        )

        adapter = ReaChunkTransportAdapter(
            runtime_directory=runtime_dir,
            live_context=live_ctx,
            verifier=manifest,
            duration_ms=15000
        )

        service = BulkExecutorService(journal_dir=journal_dir, live_context=live_ctx)
        result = service.run_with_transport(batch, transport_adapter=adapter, max_chunk_size=10)

    print("\n[+] Stage 1 Live No-Op Execution Finished!")
    print(f"    Chunks:        {result['chunk_count']}")
    print(f"    Execution Time:{result['execution_time_ms']:.2f} ms")
    print(f"    Metrics:       {json.dumps(result['metrics'], indent=2)}")

    result_file = run_dir / "execution_result.json"
    result_file.write_text(json.dumps(result, indent=2), encoding='utf-8')

    # Read back receipts
    receipts = service.journal.load_receipts()
    print(f"    Total Receipts Loaded: {len(receipts)}")
    outcomes = {}
    for r in receipts:
        outcomes[r.outcome] = outcomes.get(r.outcome, 0) + 1
    print(f"    Outcomes:      {json.dumps(outcomes, indent=2)}")
    return result

if __name__ == '__main__':
    main()
