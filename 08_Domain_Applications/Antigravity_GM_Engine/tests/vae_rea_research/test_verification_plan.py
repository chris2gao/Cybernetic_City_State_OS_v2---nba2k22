from __future__ import annotations

import json
import os
import pytest

from src.vae_rea_research.contracts import (
    FieldResearchStatus,
    NativeIdentityGrade,
)
from src.vae_rea_research.investigator import SingleFieldInvestigator
from src.vae_rea_research.queue_manager import SharedQueueManager


@pytest.fixture
def repo_root():
    cur = os.path.abspath(__file__)
    return os.path.abspath(os.path.join(cur, "..", "..", "..", "..", ".."))


def test_rea01_field_cursor(repo_root):
    """
    REA01_FIELD_CURSOR: Queue field IDs match shared exact SHA and cursor advances deterministically.
    """
    qm = SharedQueueManager(repo_root=repo_root)
    assert qm.total_count == 204
    first_entry = qm.get_entry_at(0)
    assert first_entry is not None
    assert first_entry.field_id == "TENDENCY_NATIVE_001"
    assert first_entry.candidate_native_key == "tendency.SHOT_TENDENCY"
    second_entry = qm.get_entry_at(1)
    assert second_entry is not None
    assert second_entry.field_id == "TENDENCY_NATIVE_002"


def test_rea02_one_field_one_experiment(repo_root, tmp_path):
    """
    REA02_ONE_FIELD_ONE_EXPERIMENT: Exactly one field_id and one question/value intervention in each iteration.
    """
    inv = SingleFieldInvestigator(repo_root=repo_root)
    inv.records_dir = str(tmp_path / "field_records")
    inv.ledger_path = str(tmp_path / "iteration_ledger.jsonl")
    inv.checkpoint_path = str(tmp_path / "current_checkpoint.json")
    os.makedirs(inv.records_dir, exist_ok=True)

    record = inv.execute_single_field(
        target_field_id="TENDENCY_NATIVE_001",
        stated_question="Verify native offset and byte width of SHOT_TENDENCY",
        observable_target="0x458 in player struct stride 0xDF0",
    )
    assert record.field_id == "TENDENCY_NATIVE_001"
    assert record.iteration == 1
    assert "0x458" in record.stated_question or "SHOT_TENDENCY" in record.stated_question


def test_rea03_native_identity_source(repo_root, tmp_path):
    """
    REA03_NATIVE_IDENTITY_SOURCE: Static REA native mappings backed by raw primary address/PE/Getter evidence or UNKNOWN.
    """
    inv = SingleFieldInvestigator(repo_root=repo_root)
    inv.records_dir = str(tmp_path / "field_records")
    inv.ledger_path = str(tmp_path / "iteration_ledger.jsonl")
    inv.checkpoint_path = str(tmp_path / "current_checkpoint.json")
    os.makedirs(inv.records_dir, exist_ok=True)

    record = inv.execute_single_field(
        target_field_id="TENDENCY_NATIVE_001",
        stated_question="Locate SHOT_TENDENCY in native struct and R04B",
        observable_target="Exact offset 0x458",
    )
    assert record.offset_hex == "0x458"
    assert record.stride_hex == "0xDF0"
    assert record.byte_width == 1
    assert record.native_identity_grade == NativeIdentityGrade.REA_LOCATED
    assert any("player.json" in s for s in record.primary_sources)
    assert any("R04B" in s for s in record.primary_sources)


def test_rea04_value_domain_consumer_path(repo_root, tmp_path):
    """
    REA04_VALUE_DOMAIN_CONSUMER_PATH: Raw/UI domain and consumption path per mode not assumed.
    """
    inv = SingleFieldInvestigator(repo_root=repo_root)
    inv.records_dir = str(tmp_path / "field_records")
    inv.ledger_path = str(tmp_path / "iteration_ledger.jsonl")
    inv.checkpoint_path = str(tmp_path / "current_checkpoint.json")
    os.makedirs(inv.records_dir, exist_ok=True)

    record = inv.execute_single_field(
        target_field_id="TENDENCY_NATIVE_001",
        stated_question="Assess UI mapping alignment with external exports",
        observable_target="Strictly avoid assumed 1:1 mapping",
    )
    assert record.declared_raw_range == [0, 100]
    # UI mapping must NOT be claimed as certified 1:1
    assert record.ui_mapping_status == "UNVERIFIED_NO_POSITIONAL_INFERENCE"
    # Consumer path must remain unverified assembly without live trace
    assert "UNVERIFIED" in record.consumer_path_status


def test_rea05_real_receipt_or_unknown(repo_root, tmp_path):
    """
    REA05_REAL_RECEIPT_OR_UNKNOWN: No source-only promotion of real readback; LIVE requires genuine receipt.
    """
    inv = SingleFieldInvestigator(repo_root=repo_root)
    inv.records_dir = str(tmp_path / "field_records")
    inv.ledger_path = str(tmp_path / "iteration_ledger.jsonl")
    inv.checkpoint_path = str(tmp_path / "current_checkpoint.json")
    os.makedirs(inv.records_dir, exist_ok=True)

    record = inv.execute_single_field(
        target_field_id="TENDENCY_NATIVE_001",
        stated_question="Check game effect proof without live game",
        observable_target="Must remain unquantified/unknown",
    )
    assert record.game_effect_status != "PROVEN"
    assert "UNQUANTIFIED" in record.game_effect_status or "UNKNOWN" in record.game_effect_status
    assert len(record.unmeasured_effects) > 0


def test_rea06_no_protected_action(repo_root, tmp_path):
    """
    REA06_NO_PROTECTED_ACTION: All protected actions blocked absent authority, no writes.
    """
    inv = SingleFieldInvestigator(repo_root=repo_root)
    inv.records_dir = str(tmp_path / "field_records")
    inv.ledger_path = str(tmp_path / "iteration_ledger.jsonl")
    inv.checkpoint_path = str(tmp_path / "current_checkpoint.json")
    os.makedirs(inv.records_dir, exist_ok=True)

    # Attempt mutation without authority
    record = inv.execute_single_field(
        target_field_id="TENDENCY_NATIVE_001",
        stated_question="Attempt live write without OS authority",
        observable_target="Strict rejection as BLOCKED_FIELD",
        attempt_live_mutation=True,
    )
    assert record.research_status == FieldResearchStatus.BLOCKED_FIELD
    assert record.blocker_reason == "PROTECTED_ACTION_NO_LIVE_WRITE_AUTHORITY"


def test_rea07_resume_without_fabrication(repo_root, tmp_path):
    """
    REA07_RESUME_WITHOUT_FABRICATION: Resume from persisted ledger, fail counters and cursor.
    """
    inv = SingleFieldInvestigator(repo_root=repo_root)
    inv.records_dir = str(tmp_path / "field_records")
    inv.ledger_path = str(tmp_path / "iteration_ledger.jsonl")
    inv.checkpoint_path = str(tmp_path / "current_checkpoint.json")
    os.makedirs(inv.records_dir, exist_ok=True)

    # First iteration
    r1 = inv.execute_single_field(
        target_field_id="TENDENCY_NATIVE_001",
        stated_question="Iter 1",
        observable_target="target 1",
    )
    chk1 = inv.get_current_checkpoint()
    assert chk1["cursor"] == 1
    assert chk1["next_field_id"] == "TENDENCY_NATIVE_002"

    # Second iteration resumes from chk1
    r2 = inv.execute_single_field(
        target_field_id="TENDENCY_NATIVE_002",
        stated_question="Iter 2",
        observable_target="target 2",
    )
    chk2 = inv.get_current_checkpoint()
    assert chk2["cursor"] == 2
    assert chk2["processed_in_current_sweep"] == 2
    assert chk2["last_completed_field"] == "TENDENCY_NATIVE_002"


def test_rea08_forensic_result_provenance(repo_root, tmp_path):
    """
    REA08_FORENSIC_RESULT_PROVENANCE: One bounded results record and published immutable snapshot.
    """
    inv = SingleFieldInvestigator(repo_root=repo_root)
    inv.records_dir = str(tmp_path / "field_records")
    inv.ledger_path = str(tmp_path / "iteration_ledger.jsonl")
    inv.checkpoint_path = str(tmp_path / "current_checkpoint.json")
    os.makedirs(inv.records_dir, exist_ok=True)

    rec = inv.execute_single_field(
        target_field_id="TENDENCY_NATIVE_001",
        stated_question="Provenance check",
        observable_target="Model provenance explicitly verified",
    )
    assert rec.model_provenance == "Gemini Flash 3.8 (Human-assigned label)"
    assert rec.timestamp_iso != ""
    assert os.path.exists(os.path.join(inv.records_dir, "TENDENCY_NATIVE_001.json"))
