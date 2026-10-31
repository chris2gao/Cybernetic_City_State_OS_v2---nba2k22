"""
End-to-end tests for VAE E1 Vertical Slice Prototype.
"""

import os
import pytest
from src.vae.pipeline import VAEE1Pipeline
from src.vae.contracts import ReceiptStatus, RevisionStatus, ObservationStatus, SnapshotStatus


def test_e1_vertical_slice_full_run():
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", ".."))
    pipeline = VAEE1Pipeline(repo_root=repo_root)

    results = pipeline.run_e1_slice(
        field_id="three_point_success",
        observed_symptom="three_point_percentage_too_high",
        proposed_after=45,
        authorization_ref="AUTH_OFFLINE_DEV_DRYRUN",
        dry_run=True,
    )

    # 1. Verify all 9 objects are present
    assert "R01_snapshot" in results
    assert "R02_diagnosis" in results
    assert "R03_preflight" in results
    assert "R04_receipt" in results
    assert "R05_readback" in results
    assert "R06_observation" in results
    assert "R07_evaluation" in results
    assert "R08_revision" in results
    assert "R09_feedback" in results

    # 2. Check R01 ProfileSnapshot
    snapshot = results["R01_snapshot"]
    snapshot.validate()
    assert snapshot.field_id == "three_point_success"

    # 3. Check R02 IssueDiagnosis
    diagnosis = results["R02_diagnosis"]
    diagnosis.validate()
    assert len(diagnosis.plausible_causes) > 0
    assert len(diagnosis.confounders) > 0

    # 4. Check R03 TrialPreflight
    preflight = results["R03_preflight"]
    preflight.validate()
    assert preflight.restore_plan is not None
    assert preflight.restore_plan["rollback_value"] is not None

    # 5. Check R04 ExecutionReceipt (Zero unauthorized write policy)
    receipt = results["R04_receipt"]
    receipt.validate()
    assert receipt.status == ReceiptStatus.NOT_RUN
    assert receipt.technical_response is not None
    assert receipt.technical_response["game_memory_modified"] is False
    assert "OFFLINE_DRY_RUN_ONLY" in receipt.skip_or_abort_reason

    # 6. Check R06 CompetitiveObservation
    observation = results["R06_observation"]
    observation.validate()
    assert observation.played_normalize_on is False
    assert observation.sim_normalize_on is False
    assert observation.played_quarter_minutes == 12

    # 7. Check R08 KnowledgeRevision (F03 fix: initial status is PENDING_REVISION)
    revision = results["R08_revision"]
    revision.validate()
    assert revision.status == RevisionStatus.PENDING_REVISION
    assert revision.idempotency_key is not None

    # 8. Check R09 DSeriesFeedback
    feedback = results["R09_feedback"]
    feedback.validate()
    assert feedback.d5_execution is not None
