"""Unit and fault-injection tests for BoundedSessionExecutor and SessionCompiler."""
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

from bulk_executor import (
    BulkBatchHeader,
    BulkBatch,
    BulkIntentItem,
    ExecutionJournal,
    PlannedChunk,
    sha256_digest
)
from bounded_session_transport import (
    BoundedSessionExecutor,
    SessionCompiler,
    SessionBatchTransport
)


@pytest.fixture
def temp_journal_dir():
    d = tempfile.mkdtemp(prefix="test_session_journal_")
    yield Path(d)
    shutil.rmtree(d, ignore_errors=True)


def make_sample_two_chunk_batch(batch_id="BATCH-TEST-SESSION-001"):
    intents = [
        # Chunk 1: Team 1 (MIL in mock VM: player 1100, 1101)
        BulkIntentItem("I-MIL-1", "PLAYER_PATCH_TENDENCIES", 1, "SHOT_TENDENCY", 50, 60, player_id=1100),
        BulkIntentItem("I-MIL-2", "PLAYER_PATCH_TENDENCIES", 1, "SHOT_TENDENCY", 50, 65, player_id=1101),
        # Chunk 2: Team 28 (POR in mock VM: player 2459 Lillard, 3801)
        BulkIntentItem("I-POR-1", "PLAYER_PATCH_TENDENCIES", 28, "SHOT_TENDENCY", 95, 80, player_id=2459),
        BulkIntentItem("I-POR-2", "PLAYER_PATCH_TENDENCIES", 28, "SHOT_TENDENCY", 50, 55, player_id=3801),
    ]
    header = BulkBatchHeader(
        batch_id=batch_id,
        save_instance_id="MyLEAGUE0003",
        game_build_sha256="1727ad72085fba39e789ee574fc15aab623ad1651cf6879e95e8cd53b6ffbbf5",
        authorization_ref="HUMAN-TEST-AUTH",
        source_snapshot_ref="snapshot_test",
        dry_run=True
    )
    return BulkBatch(header=header, intents=intents)


def test_session_compiler_compiles_source():
    """Gate G3: SessionCompiler generates valid JS embedding all chunks with single hook."""
    batch = make_sample_two_chunk_batch()
    chunks = [
        PlannedChunk("chunk-001-team-01", 1, "PLAYER_PATCH_TENDENCIES", tuple(batch.intents[:2]), 6, 500, batch.header.batch_id, "MyLEAGUE0003", batch.plan_digest, "d1"),
        PlannedChunk("chunk-002-team-28", 28, "PLAYER_PATCH_TENDENCIES", tuple(batch.intents[2:]), 6, 500, batch.header.batch_id, "MyLEAGUE0003", batch.plan_digest, "d2")
    ]
    source = SessionCompiler.compile_session(chunks, batch.header, is_live=False)
    assert "const SESSION_CHUNKS =" in source
    assert "chunk-001-team-01" in source
    assert "chunk-002-team-28" in source
    assert "PeekMessageA" in source
    assert source.count("Interceptor.attach") == 1  # Single hook only!


def test_bounded_session_executor_multi_chunk_success(temp_journal_dir):
    """Gate G3: Single session execution succeeds for >=2 chunks with single attach."""
    batch = make_sample_two_chunk_batch()

    def fake_runner(chunks, script):
        results = {}
        for c in chunks:
            receipts = []
            for it in c.intents:
                receipts.append({
                    "intent_id": it.intent_id,
                    "team_id": it.team_id,
                    "player_id": it.player_id,
                    "field_id": it.field_id,
                    "expected_before": it.expected_before,
                    "getter_before": it.expected_before,
                    "requested": it.value,
                    "getter_after": it.value,
                    "raw_after": it.value,
                    "outcome": "SUCCESS_APPLIED",
                    "unaltered_fields_check": True
                })
            results[c.chunk_id] = {
                "kind": "chunk-execution-result",
                "chunk_id": c.chunk_id,
                "chunk_digest": c.chunk_digest,
                "plan_digest": c.plan_digest,
                "action_id": c.action_id,
                "batch_id": batch.header.batch_id,
                "save_instance_id": batch.header.save_instance_id,
                "outcome": "CHUNK_SUCCESS",
                "receipts": receipts
            }
        return {
            "outcome": "SESSION_SUCCESS",
            "evidence_id": "ev_fake_test_001",
            "chunk_results": results,
            "wall_time_ms": 12.5
        }

    executor = BoundedSessionExecutor(temp_journal_dir, fake_runner=fake_runner)
    res = executor.execute_batch(batch, max_chunk_size=50)

    assert res["chunk_count"] == 2
    assert res["frida_attach_count"] == 1  # Exactly 1 attach!
    assert res["metrics"]["num_planned"] == 4
    assert res["metrics"]["num_success"] == 4
    assert res["metrics"]["conservation_holds"] is True

    # Gate G4: Verify claims were persisted before execution
    claims = list((temp_journal_dir / "claims").glob("*.json"))
    assert len(claims) == 2
    for c_file in claims:
        data = json.loads(c_file.read_text(encoding="utf-8"))
        assert data["state"] == "COMPLETED"


def test_bounded_session_fail_stop_on_cas_mismatch(temp_journal_dir):
    """Gate G5: If chunk 1 encounters CAS mismatch, chunk 2 is halted and marked NOT_EXECUTED."""
    batch = make_sample_two_chunk_batch()

    def fake_runner_with_cas_mismatch(chunks, script):
        c1, c2 = chunks[0], chunks[1]
        c1_receipts = [
            {
                "intent_id": c1.intents[0].intent_id,
                "team_id": c1.team_id,
                "player_id": c1.intents[0].player_id,
                "field_id": c1.intents[0].field_id,
                "expected_before": c1.intents[0].expected_before,
                "getter_before": 22,  # CAS Mismatch!
                "requested": c1.intents[0].value,
                "outcome": "CAS_EXPECTED_BEFORE_MISMATCH",
                "reason": "Expected 99, observed 22"
            },
            {
                "intent_id": c1.intents[1].intent_id,
                "team_id": c1.team_id,
                "player_id": c1.intents[1].player_id,
                "field_id": c1.intents[1].field_id,
                "expected_before": c1.intents[1].expected_before,
                "requested": c1.intents[1].value,
                "outcome": "NOT_EXECUTED",
                "reason": "CHUNK_HALTED_PREVIOUS_FAILURE"
            }
        ]
        c2_receipts = [
            {
                "intent_id": it.intent_id,
                "team_id": it.team_id,
                "player_id": it.player_id,
                "field_id": it.field_id,
                "expected_before": it.expected_before,
                "requested": it.value,
                "outcome": "NOT_EXECUTED",
                "reason": "SESSION_HALTED:CAS_MISMATCH"
            }
            for it in c2.intents
        ]
        return {
            "outcome": "SESSION_SUCCESS",
            "evidence_id": "ev_fake_cas_fail",
            "chunk_results": {
                c1.chunk_id: {
                    "kind": "chunk-execution-result",
                    "chunk_id": c1.chunk_id,
                    "chunk_digest": c1.chunk_digest,
                    "outcome": "CHUNK_HALTED",
                    "receipts": c1_receipts
                },
                c2.chunk_id: {
                    "kind": "chunk-execution-result",
                    "chunk_id": c2.chunk_id,
                    "chunk_digest": c2.chunk_digest,
                    "outcome": "CHUNK_HALTED",
                    "receipts": c2_receipts
                }
            },
            "wall_time_ms": 15.0
        }

    executor = BoundedSessionExecutor(temp_journal_dir, fake_runner=fake_runner_with_cas_mismatch)
    res = executor.execute_batch(batch, max_chunk_size=50)

    assert res["metrics"]["num_cas_mismatch"] == 1
    assert res["metrics"]["num_not_executed"] == 3
    assert res["metrics"]["num_success"] == 0
    assert res["metrics"]["conservation_holds"] is True


def test_session_claim_before_setter_and_unknown_lock(temp_journal_dir):
    """Gate G4: UNKNOWN outcome locks resource and blocks future execution."""
    batch = make_sample_two_chunk_batch()

    def fake_runner_abort(chunks, script):
        return {
            "outcome": "EXECUTION_RESULT_UNKNOWN_NO_AUTOMATIC_RETRY",
            "wall_time_ms": 5.0
        }

    executor = BoundedSessionExecutor(temp_journal_dir, fake_runner=fake_runner_abort)
    res = executor.execute_batch(batch, max_chunk_size=50)

    assert res["metrics"]["num_unknown"] == 4
    assert res["metrics"]["conservation_holds"] is True

    # Re-running same batch should now be blocked by prior UNKNOWN
    res2 = executor.execute_batch(batch, max_chunk_size=50)
    assert res2["metrics"]["num_blocked"] == 4
    assert res2["frida_attach_count"] == 0  # No attach allowed when blocked!


def test_session_node_vm_execution():
    """Gate G3 / G5: Compiled session script executes in synthetic Node VM."""
    batch = make_sample_two_chunk_batch("BATCH-VM-SESSION-001")
    chunks = [
        PlannedChunk("chunk-001-team-01", 1, "PLAYER_PATCH_TENDENCIES", tuple(batch.intents[:2]), 6, 500, batch.header.batch_id, "MyLEAGUE0003", batch.plan_digest, "d1"),
        PlannedChunk("chunk-002-team-28", 28, "PLAYER_PATCH_TENDENCIES", tuple(batch.intents[2:]), 6, 500, batch.header.batch_id, "MyLEAGUE0003", batch.plan_digest, "d2")
    ]
    script = SessionCompiler.compile_session(chunks, batch.header, is_live=False)

    import subprocess
    runner_js = Path(__file__).parent / "node_vm_chunk_runner.js"
    with tempfile.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as f:
        f.write(script)
        script_file = f.name

    try:
        r = subprocess.run(["node", str(runner_js), script_file], capture_output=True, text=True)
        assert r.returncode == 0, f"Node VM failed: {r.stderr}"
        data = json.loads(r.stdout)
        assert data.get("success") is True
        messages = [m for m in data.get("emitted_messages", []) if m.get("kind") == "chunk-execution-result"]
        assert len(messages) == 2, f"Expected 2 chunk results, got {len(messages)}"
        assert messages[0]["chunk_id"] == "chunk-001-team-01"
        assert messages[1]["chunk_id"] == "chunk-002-team-28"
        assert messages[0]["outcome"] == "CHUNK_SUCCESS"
        assert messages[1]["outcome"] == "CHUNK_SUCCESS"
    finally:
        os.unlink(script_file)
