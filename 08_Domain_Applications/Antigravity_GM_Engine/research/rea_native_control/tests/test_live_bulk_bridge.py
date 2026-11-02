"""Tests for Live Bulk Bridge, CrossProcessFileLock, and Preflight Manifest Verification."""
import argparse
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import sys
import pytest

_RESEARCH_DIR = Path(__file__).resolve().parent.parent
if str(_RESEARCH_DIR) not in sys.path:
    sys.path.insert(0, str(_RESEARCH_DIR))

from bulk_executor import (
    BulkBatch,
    BulkBatchHeader,
    BulkBatchPlanner,
    BulkIntentItem,
    CrossProcessFileLock,
    ReaChunkTransportAdapter,
    cli_execute_authorized,
    GAME_BUILD_SHA256
)
import contracts
import transport


@pytest.fixture
def valid_header():
    return BulkBatchHeader(
        batch_id="BATCH-BRIDGE-001",
        save_instance_id="save_bridge_001",
        game_build_sha256=GAME_BUILD_SHA256,
        source_snapshot_ref="snap_bridge_001",
        expected_process_name="NBA2K22.exe",
        expected_pid=10404,
        authorization_ref="HUMAN-AUTH-PILOT-20261101",
        dry_run=False
    )


def test_cross_process_file_lock(tmp_path):
    lock_file = tmp_path / "test.lock"
    lock1 = CrossProcessFileLock(lock_file)
    lock1.acquire()
    assert lock_file.is_file()

    lock2 = CrossProcessFileLock(lock_file)
    with pytest.raises(RuntimeError, match="CROSS_PROCESS_LOCK_HELD"):
        lock2.acquire()

    lock1.release()
    assert not lock_file.exists()

    # Context manager form
    with CrossProcessFileLock(lock_file):
        assert lock_file.is_file()
    assert not lock_file.exists()


def test_adapter_verifier_plan_mismatch(tmp_path, valid_header):
    item = BulkIntentItem(
        intent_id="I-01",
        action_id="PLAYER_PATCH_TENDENCIES",
        team_id=28,
        player_id=2459,
        field_id="SHOT_TENDENCY",
        expected_before=95,
        value=80
    )
    batch = BulkBatch(header=valid_header, intents=(item,))
    chunk = BulkBatchPlanner().plan(batch)[0]

    live_ctx = transport.LiveExecutionContext(
        authorization_ref=valid_header.authorization_ref,
        allowed_action_ids=frozenset(["PLAYER_PATCH_TENDENCIES"]),
        maximum_game_calls=100,
        enabled=True
    )
    bad_verifier = {
        "plan_digest": "different_plan_digest_12345",
        "allowed_action_ids": ["PLAYER_PATCH_TENDENCIES"]
    }
    adapter = ReaChunkTransportAdapter(tmp_path, live_context=live_ctx, verifier=bad_verifier)
    with pytest.raises(PermissionError, match="PLAN_DIGEST_MISMATCH"):
        adapter.execute_chunk(chunk, "// script")


def test_adapter_verifier_action_not_permitted(tmp_path, valid_header):
    item = BulkIntentItem(
        intent_id="I-01",
        action_id="PLAYER_PATCH_TENDENCIES",
        team_id=28,
        player_id=2459,
        field_id="SHOT_TENDENCY",
        expected_before=95,
        value=80
    )
    batch = BulkBatch(header=valid_header, intents=(item,))
    chunk = BulkBatchPlanner().plan(batch)[0]

    live_ctx = transport.LiveExecutionContext(
        authorization_ref=valid_header.authorization_ref,
        allowed_action_ids=frozenset(["PLAYER_PATCH_TENDENCIES"]),
        maximum_game_calls=100,
        enabled=True
    )
    bad_verifier = {
        "plan_digest": chunk.plan_digest,
        "allowed_action_ids": ["COACH_SET_GAMEPLAN"]
    }
    adapter = ReaChunkTransportAdapter(tmp_path, live_context=live_ctx, verifier=bad_verifier)
    with pytest.raises(PermissionError, match="ACTION_NOT_PERMITTED"):
        adapter.execute_chunk(chunk, "// script")


def test_adapter_verifier_delegation_mocked(tmp_path, valid_header, monkeypatch):
    item = BulkIntentItem(
        intent_id="I-01",
        action_id="PLAYER_PATCH_TENDENCIES",
        team_id=28,
        player_id=2459,
        field_id="SHOT_TENDENCY",
        expected_before=95,
        value=80
    )
    batch = BulkBatch(header=valid_header, intents=(item,))
    chunk = BulkBatchPlanner().plan(batch)[0]

    live_ctx = transport.LiveExecutionContext(
        authorization_ref=valid_header.authorization_ref,
        allowed_action_ids=frozenset(["PLAYER_PATCH_TENDENCIES"]),
        maximum_game_calls=100,
        enabled=True
    )
    verifier = {
        "plan_digest": chunk.plan_digest,
        "allowed_action_ids": ["PLAYER_PATCH_TENDENCIES"],
        "game_build_sha256": contracts.BUILD
    }
    adapter = ReaChunkTransportAdapter(tmp_path, live_context=live_ctx, verifier=verifier)

    executed_calls = []

    def mock_execute(self, script, *, action_id, request_id, maximum_game_calls):
        executed_calls.append((action_id, request_id, maximum_game_calls))
        return {
            "kind": "chunk-execution-result",
            "chunk_id": chunk.chunk_id,
            "chunk_digest": chunk.chunk_digest,
            "plan_digest": chunk.plan_digest,
            "action_id": chunk.action_id,
            "batch_id": batch.header.batch_id,
            "save_instance_id": batch.header.save_instance_id,
            "outcome": "CHUNK_SUCCESS",
            "receipts": [{
                "intent_id": "I-01",
                "team_id": 28,
                "player_id": 2459,
                "field_id": "SHOT_TENDENCY",
                "expected_before": 95,
                "requested": 80,
                "getter_before": 95,
                "getter_after": 80,
                "raw_after": 80,
                "outcome": "SUCCESS_APPLIED",
                "unaltered_fields_check": True
            }],
            "evidence_id": "mock_ev_01"
        }

    monkeypatch.setattr(transport.ReaCliTransport, "execute", mock_execute)
    res = adapter.execute_chunk(chunk, "// script")
    assert res["outcome"] == "CHUNK_SUCCESS"
    assert len(executed_calls) == 1
    assert executed_calls[0][0] == "PLAYER_PATCH_TENDENCIES"


def test_cli_execute_authorized_with_manifest(tmp_path, valid_header, monkeypatch):
    batch_file = tmp_path / "batch.json"
    item = BulkIntentItem(
        intent_id="I-01",
        action_id="PLAYER_PATCH_TENDENCIES",
        team_id=28,
        player_id=2459,
        field_id="SHOT_TENDENCY",
        expected_before=95,
        value=80
    )
    batch = BulkBatch(header=valid_header, intents=(item,))
    batch_dict = {
        **asdict(batch.header),
        "intents": [asdict(i) for i in batch.intents]
    }
    batch_file.write_text(json.dumps(batch_dict), encoding='utf-8')

    manifest_file = tmp_path / "manifest.json"
    manifest_data = {
        "task_id": "NBA2K22-REA-CONTROLLED-LIVE-BULK-PILOT-20261101-001",
        "human_authorization_ref": "HUMAN-AUTH-PILOT-20261101",
        "save_instance_id": "save_bridge_001",
        "plan_digest": batch.plan_digest,
        "game_build_sha256": contracts.BUILD,
        "expected_pid": 10404,
        "allowed_action_ids": ["PLAYER_PATCH_TENDENCIES"],
        "allowed_fields": ["SHOT_TENDENCY"],
        "maximum_game_calls": 200
    }
    manifest_file.write_text(json.dumps(manifest_data), encoding='utf-8')

    mock_runs = []

    def mock_run_with_transport(self, batch_in, transport_adapter, max_chunk_size=50):
        mock_runs.append(batch_in.plan_digest)
        return {
            "batch_id": batch_in.header.batch_id,
            "plan_digest": batch_in.plan_digest,
            "chunk_count": 1,
            "execution_time_ms": 12.3,
            "metrics": {"num_planned": 1, "num_success": 1, "conservation_holds": True},
            "receipt_count": 1
        }

    from bulk_executor import BulkExecutorService
    monkeypatch.setattr(BulkExecutorService, "run_with_transport", mock_run_with_transport)

    args = argparse.Namespace(
        batch_file=str(batch_file),
        allow_live_mutation=True,
        manifest=str(manifest_file),
        journal_dir=str(tmp_path / "journal"),
        runtime_dir=str(tmp_path / "runtime"),
        expected_pid=10404
    )
    cli_execute_authorized(args)
    assert len(mock_runs) == 1
    assert mock_runs[0] == batch.plan_digest
