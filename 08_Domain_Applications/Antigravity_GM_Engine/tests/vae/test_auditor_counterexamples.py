"""
Direct verification tests proving that all 4 auditor counterexamples
(REPRO_R06, REPRO_R03, REPRO_R08, REPRO_R07) identified during the independent review
are conclusively resolved in the candidate code.
"""

import os
import pytest
import tempfile
from src.vae.contracts import (
    CompetitiveObservation,
    ObservationStatus,
    ProfileSnapshot,
    SnapshotStatus,
    PreflightStatus,
    EvaluationOutcome,
    RevisionStatus,
)
from src.vae.preflight import VAEPreflightEngine
from src.vae.evaluator import VAEEvaluationEngine
from src.vae.revision import VAEKnowledgeRevisionManager


def test_auditor_repro_r06_fixed():
    """
    Auditor Counterexample 1 (REPRO_R06):
    Formerly, before.save_id != after.save_id and before.engine_path != after.engine_path
    were accepted as comparable because is_comparable_with() lacked save_id and engine_path checks.

    Fixed behavior:
    Comparing cross-save or cross-engine-path observations strictly returns (False, error_reason).
    """
    obs_save_a = CompetitiveObservation(
        trial_id="t1", game_id="g1", save_id="SAVE_A", game_date="2021-11-01",
        engine_path="3D_PLAYED", side="USER", controller_assigned=True,
        played_normalize_on=False, sim_normalize_on=False,
        played_quarter_minutes=12, sim_quarter_minutes=12,
        base_source_ref="ref1", metrics={"pts": 100}, status=ObservationStatus.OFFLINE_FIXTURE,
    )
    obs_save_b = CompetitiveObservation(
        trial_id="t2", game_id="g2", save_id="SAVE_B", game_date="2021-11-02",
        engine_path="CALENDAR_SIM", side="USER", controller_assigned=True,
        played_normalize_on=False, sim_normalize_on=False,
        played_quarter_minutes=12, sim_quarter_minutes=12,
        base_source_ref="ref1", metrics={"pts": 105}, status=ObservationStatus.OFFLINE_FIXTURE,
    )

    # 1. Cross-save check
    is_comp, reason = obs_save_a.is_comparable_with(obs_save_b)
    assert is_comp is False
    assert "save_id mismatch" in reason

    # 2. Same save, cross-engine-path check
    obs_same_save_diff_path = CompetitiveObservation(
        trial_id="t3", game_id="g3", save_id="SAVE_A", game_date="2021-11-03",
        engine_path="CALENDAR_SIM", side="USER", controller_assigned=True,
        played_normalize_on=False, sim_normalize_on=False,
        played_quarter_minutes=12, sim_quarter_minutes=12,
        base_source_ref="ref1", metrics={"pts": 102}, status=ObservationStatus.OFFLINE_FIXTURE,
    )
    is_comp2, reason2 = obs_save_a.is_comparable_with(obs_same_save_diff_path)
    assert is_comp2 is False
    assert "engine_path mismatch" in reason2


def test_auditor_repro_r03_fixed():
    """
    Auditor Counterexample 2 (REPRO_R03):
    Formerly, static defaults (STATIC_DEFAULT) plus arbitrary nonempty mock auth
    (AUTH_OFFLINE_DEV_DRYRUN) met READY checks.

    Fixed behavior:
    Preflight strictly verifies that baseline snapshot status is live CAPTURED and
    authorization is not a mock/dry-run token. Otherwise, status is BLOCKED.
    """
    engine = VAEPreflightEngine()

    # Static spec snapshot
    static_snapshot = ProfileSnapshot(
        snapshot_id="snap-static",
        save_id=None,
        game_build="2K22_PC",
        game_mode="MYLEAGUE",
        scene="SETTINGS",
        side="USER",
        field_id="three_point_success",
        raw_value=50,
        display_value=50,
        unit="slider_points",
        source_ref="settings.json",
        captured_at=None,
        freshness="STATIC",
        status=SnapshotStatus.STATIC_SPEC,
    )

    preflight = engine.prepare_preflight(
        target_identity="slider.three_point_success",
        baseline_snapshot=static_snapshot,
        proposed_after=45,
        metric_primary="team_3pt_pct",
        metrics_side_effect=[],
        restore_plan={"rollback_value": 50},
        authorization_ref="AUTH_OFFLINE_DEV_DRYRUN",
    )

    # Must be BLOCKED, never READY
    assert preflight.status == PreflightStatus.BLOCKED
    assert "P0-02_BLOCKED" in preflight.block_reason
    assert "STATIC_SPEC" in preflight.block_reason or "Mock authorization" in preflight.block_reason


def test_auditor_repro_r08_fixed():
    """
    Auditor Counterexample 3 (REPRO_R08):
    Formerly, fresh instance of revision manager lost in-memory ledger and duplicate protection.

    Fixed behavior:
    With durable JSONL backing, a fresh instance immediately reloads all committed
    idempotency keys and rejects duplicates.
    """
    with tempfile.NamedTemporaryFile(suffix=".jsonl", delete=False) as tf:
        ledger_file = tf.name

    try:
        manager_a = VAEKnowledgeRevisionManager(ledger_path=ledger_file)
        rev = manager_a.propose_revision(
            trial_id="t1",
            prior_claim_ref="claim_01",
            new_claim="Intervention improves 3PT percentage",
            counterexamples=[],
            source_refs=["refA"],
        )
        success_a, rev_committed, _ = manager_a.commit_append(rev)
        assert success_a is True
        assert rev_committed.status == RevisionStatus.APPENDED

        # Create fresh instance pointing to same file
        manager_b = VAEKnowledgeRevisionManager(ledger_path=ledger_file)
        assert len(manager_b.ledger) == 1
        assert rev.idempotency_key in manager_b.committed_keys

        # Fresh instance rejects duplicate commit
        success_b, rev_rejected, msg = manager_b.commit_append(rev)
        assert success_b is False
        assert rev_rejected.status == RevisionStatus.DUPLICATE_REJECTED
        assert "DUPLICATE_REJECTED" in msg
    finally:
        if os.path.exists(ledger_file):
            os.remove(ledger_file)


def test_auditor_repro_r07_fixed():
    """
    Auditor Counterexample 4 (REPRO_R07):
    Formerly, sample_size >= 5 and delta < -0.02 arbitrarily triggered causal CONFIRMED
    without baseline control or significance.

    Fixed behavior:
    Without controlled randomized experiments and controlled confounders, VAEEvaluationEngine
    returns non-causal observational trends (OBSERVED_TREND_POSITIVE), never causal CONFIRMED_CONTROLLED.
    """
    evaluator = VAEEvaluationEngine()
    deltas = {"delta_team_3pt_pct": -0.021}

    # Uncontrolled small sample test (5 games)
    eval_uncontrolled = evaluator.evaluate(
        trial_id="t1",
        preregistered_metric_ref="team_3pt_pct",
        deltas=deltas,
        target_direction="DECREASE",
        confounders=[],
        sample_size=5,
        controlled_experiment=False,
        confounders_controlled=False,
    )

    # Must be OBSERVED_TREND_POSITIVE, NOT causal CONFIRMED_CONTROLLED
    assert eval_uncontrolled.outcome == EvaluationOutcome.OBSERVED_TREND_POSITIVE
    assert eval_uncontrolled.outcome != EvaluationOutcome.CONFIRMED_CONTROLLED

    # If uncontrolled confounders exist, it must remain INCONCLUSIVE
    eval_confounded = evaluator.evaluate(
        trial_id="t1",
        preregistered_metric_ref="team_3pt_pct",
        deltas=deltas,
        target_direction="DECREASE",
        confounders=["opponent_defensive_rating"],
        sample_size=5,
        controlled_experiment=False,
        confounders_controlled=False,
    )
    assert eval_confounded.outcome == EvaluationOutcome.INCONCLUSIVE
