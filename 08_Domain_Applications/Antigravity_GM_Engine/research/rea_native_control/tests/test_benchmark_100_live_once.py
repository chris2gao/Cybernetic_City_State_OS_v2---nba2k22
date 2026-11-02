"""Unit and fault-injection tests for 100-item live benchmark harness and receipt validation."""
from dataclasses import asdict
import json
import os
from pathlib import Path
import shutil
import sys
import tempfile
import pytest

_RESEARCH_DIR = Path(__file__).resolve().parent.parent
if str(_RESEARCH_DIR) not in sys.path:
    sys.path.insert(0, str(_RESEARCH_DIR))

import contracts
from bulk_executor import (
    BulkBatchHeader,
    BulkBatch,
    BulkIntentItem,
    BulkBatchPlanner,
    PlannedChunk,
    sha256_digest,
    canonical_encode
)
from bounded_session_transport import (
    BoundedSessionExecutor,
    SessionCompiler
)
from validate_100_receipts import validate_stage


def make_synthetic_100_batch(batch_id: str = "BATCH-SYNTHETIC-100") -> BulkBatch:
    """Creates 100 unique intents across 10 teams (10 players per team)."""
    intents = []
    # 10 teams: IDs 0 through 9
    for tid in range(10):
        for p_idx in range(10):
            pid = 1000 + tid * 100 + p_idx
            before_val = (tid * 10 + p_idx) % 95  # 0..94
            # Target policy: before + 1 (or 99 if 100)
            target_val = 99 if before_val == 100 else before_val + 1
            intents.append(BulkIntentItem(
                intent_id=f"I-{batch_id}-T{tid}-P{pid}",
                action_id="PLAYER_PATCH_TENDENCIES",
                team_id=tid,
                field_id="SHOT_TENDENCY",
                expected_before=before_val,
                value=target_val,
                player_id=pid
            ))

    header = BulkBatchHeader(
        batch_id=batch_id,
        save_instance_id="MyLEAGUE0003",
        game_build_sha256=contracts.BUILD,
        authorization_ref="HUMAN-AUTH-TEST-100",
        source_snapshot_ref="snapshot_synthetic_100",
        expected_process_name="NBA2K22.exe",
        expected_pid=5720,
        dry_run=True
    )
    return BulkBatch(header=header, intents=tuple(intents))


def test_100_intent_batch_planning_and_compilation():
    """Gate G3 / G5: 100 distinct targets plan into chunks and compile to single session JS."""
    batch = make_synthetic_100_batch("BATCH-TEST-PLAN-100")
    assert len(batch.intents) == 100

    # Verify uniqueness of intent IDs and target entity keys
    seen_ids = set()
    seen_keys = set()
    for it in batch.intents:
        assert it.intent_id not in seen_ids
        seen_ids.add(it.intent_id)
        k = (it.team_id, it.player_id, it.field_id)
        assert k not in seen_keys
        seen_keys.add(k)
        assert it.value == it.expected_before + 1

    planner = BulkBatchPlanner()
    chunks = planner.plan(batch, max_chunk_size=50)
    assert len(chunks) == 10  # 10 teams, 1 chunk per team

    script = SessionCompiler.compile_session(chunks, batch.header, is_live=False)
    assert "executeAction" in script
    assert "send(" in script
    assert "chunk-execution-result" in script
    assert len(script) > 5000


def test_synthetic_100_stage_validation_passes():
    """Gate G8: validate_stage passes on well-formed 100-item execution output."""
    temp_dir = Path(tempfile.mkdtemp(prefix="test_stage_valid_100_"))
    try:
        batch = make_synthetic_100_batch("BATCH-STAGE-VALID-100")

        # 1. Batch file
        batch_file = temp_dir / f"batch_{batch.header.batch_id}.json"
        batch_file.write_text(json.dumps({
            **asdict(batch.header),
            "intents": [asdict(i) for i in batch.intents]
        }, indent=2), encoding="utf-8")

        # 2. Manifest file
        manifest_file = temp_dir / f"manifest_{batch.header.batch_id}.json"
        manifest_file.write_text(json.dumps({
            "task_id": "NBA2K22-REA-100-LIVE-BENCHMARK-20261102-001",
            "game_build_sha256": contracts.BUILD,
            "plan_digest": batch.plan_digest,
            "save_instance_id": "MyLEAGUE0003",
            "expected_pid": 5720
        }, indent=2), encoding="utf-8")

        # 3. Claims & receipts
        journal_dir = temp_dir / "journal"
        claims_dir = journal_dir / "claims"
        claims_dir.mkdir(parents=True)

        planner = BulkBatchPlanner()
        chunks = planner.plan(batch, max_chunk_size=50)

        for c in chunks:
            claim_file = claims_dir / f"claim_{c.chunk_id}_{c.chunk_digest[:12]}.json"
            claim_file.write_text(json.dumps({
                "chunk_id": c.chunk_id,
                "chunk_digest": c.chunk_digest,
                "team_id": c.team_id,
                "batch_id": batch.header.batch_id,
                "claim_timestamp": "2026-11-02T03:00:00Z"
            }), encoding="utf-8")

        receipts_file = journal_dir / "receipts.jsonl"
        with receipts_file.open("w", encoding="utf-8") as f:
            for c in chunks:
                for it in c.intents:
                    rcpt = {
                        "intent_id": it.intent_id,
                        "team_id": it.team_id,
                        "player_id": it.player_id,
                        "field_id": it.field_id,
                        "expected_before": it.expected_before,
                        "requested": it.value,
                        "actual_before": it.expected_before,
                        "actual_after": it.value,
                        "outcome": "SUCCESS_APPLIED",
                        "chunk_id": c.chunk_id,
                        "timestamp": "2026-11-02T03:00:01Z",
                        "reason": "OK"
                    }
                    f.write(json.dumps(rcpt) + "\n")

        # 4. Execution result
        exec_file = temp_dir / "execution_result.json"
        exec_file.write_text(json.dumps({
            "batch_id": batch.header.batch_id,
            "chunk_count": len(chunks),
            "frida_attach_count": 1,
            "execution_time_ms": 7500.0,
            "receipt_count": 100,
            "metrics": {
                "num_planned": 100,
                "num_success": 100,
                "num_unchanged": 0,
                "num_failed": 0,
                "num_unknown": 0,
                "conservation_holds": True
            }
        }), encoding="utf-8")

        # 5. REA runtime
        rea_dir = temp_dir / "rea_runtime" / "session_001"
        rea_dir.mkdir(parents=True)
        (rea_dir / "rea-stderr.log").write_text("", encoding="utf-8")
        evidence_msgs = [
            {"kind": "chunk-execution-result", "chunk_id": c.chunk_id, "outcome": "CHUNK_SUCCESS"}
            for c in chunks
        ]
        (rea_dir / "evidence.json").write_text(json.dumps({
            "normalized_result": {"messages": evidence_msgs}
        }), encoding="utf-8")

        # Validate
        res = validate_stage(temp_dir, expected_count=100, expected_mode="mutation")
        assert res["validation_passed"] is True, f"Errors: {res['errors']}"
        assert res["checks"]["receipt_count"] == 100
        assert res["checks"]["unknown_count"] == 0
        assert res["checks"]["conservation_holds"] is True
        assert res["checks"]["plan_digest_verified"] is True
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_synthetic_100_stage_validation_detects_unknown():
    """Gate G8: Validator rejects stage containing UNKNOWN receipt (critical safety)."""
    temp_dir = Path(tempfile.mkdtemp(prefix="test_stage_unknown_"))
    try:
        batch = make_synthetic_100_batch("BATCH-STAGE-UNKNOWN-100")

        # Setup minimal stage
        (temp_dir / f"batch_{batch.header.batch_id}.json").write_text(json.dumps({
            **asdict(batch.header),
            "intents": [asdict(i) for i in batch.intents]
        }), encoding="utf-8")
        (temp_dir / f"manifest_{batch.header.batch_id}.json").write_text(json.dumps({
            "task_id": "NBA2K22-REA-100-LIVE-BENCHMARK-20261102-001",
            "game_build_sha256": contracts.BUILD,
            "plan_digest": batch.plan_digest,
            "save_instance_id": "MyLEAGUE0003"
        }), encoding="utf-8")

        journal_dir = temp_dir / "journal"
        journal_dir.mkdir(parents=True)
        receipts_file = journal_dir / "receipts.jsonl"
        with receipts_file.open("w", encoding="utf-8") as f:
            for idx, it in enumerate(batch.intents):
                outcome = "UNKNOWN" if idx == 50 else "SUCCESS_APPLIED"
                rcpt = {
                    "intent_id": it.intent_id,
                    "team_id": it.team_id,
                    "player_id": it.player_id,
                    "field_id": it.field_id,
                    "expected_before": it.expected_before,
                    "requested": it.value,
                    "actual_before": it.expected_before,
                    "actual_after": it.value if outcome == "SUCCESS_APPLIED" else None,
                    "outcome": outcome,
                    "chunk_id": "chunk-01",
                    "timestamp": "2026-11-02T03:00:01Z"
                }
                f.write(json.dumps(rcpt) + "\n")

        res = validate_stage(temp_dir, expected_count=100, expected_mode="mutation")
        assert res["validation_passed"] is False
        assert any("UNKNOWN" in err for err in res["errors"])
        assert res["checks"]["unknown_count"] == 1
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)


def test_synthetic_100_stage_validation_detects_digest_mismatch():
    """Gate G8: Validator rejects stage when manifest digest doesn't match batch."""
    temp_dir = Path(tempfile.mkdtemp(prefix="test_stage_digest_"))
    try:
        batch = make_synthetic_100_batch("BATCH-STAGE-DIGEST-100")
        (temp_dir / f"batch_{batch.header.batch_id}.json").write_text(json.dumps({
            **asdict(batch.header),
            "intents": [asdict(i) for i in batch.intents]
        }), encoding="utf-8")
        # Injected fraudulent digest
        (temp_dir / f"manifest_{batch.header.batch_id}.json").write_text(json.dumps({
            "task_id": "NBA2K22-REA-100-LIVE-BENCHMARK-20261102-001",
            "game_build_sha256": contracts.BUILD,
            "plan_digest": "0000000000000000000000000000000000000000000000000000000000000000",
            "save_instance_id": "MyLEAGUE0003"
        }), encoding="utf-8")

        journal_dir = temp_dir / "journal"
        journal_dir.mkdir(parents=True)
        (journal_dir / "receipts.jsonl").write_text("", encoding="utf-8")

        res = validate_stage(temp_dir, expected_count=100, expected_mode="mutation")
        assert res["validation_passed"] is False
        assert any("plan_digest mismatch" in err for err in res["errors"])
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)
