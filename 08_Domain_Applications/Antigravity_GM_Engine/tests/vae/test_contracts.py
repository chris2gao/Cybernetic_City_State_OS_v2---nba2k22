"""
Unit tests for VAE Business Contracts (R01–R09).
Specifically verifies resolutions for F02, F03, F04, F07.
"""

import pytest
from src.vae.contracts import (
    ProfileSnapshot,
    SnapshotStatus,
    IssueDiagnosis,
    DiagnosisStatus,
    TrialPreflight,
    PreflightStatus,
    ExecutionReceipt,
    ReceiptStatus,
    TechnicalReadback,
    ReadbackStatus,
    CompetitiveObservation,
    ObservationStatus,
    EffectEvaluation,
    EvaluationOutcome,
    KnowledgeRevision,
    RevisionStatus,
    DSeriesFeedback,
    EvidenceTier,
)
from src.vae.revision import VAEKnowledgeRevisionManager
from src.vae.observation import VAEObservationComparator


def test_f02_observation_comparability_strict_context():
    """
    F02 Test: R06 context must enforce side, controller, dual Normalize, quarter lengths, and base_source.
    """
    obs_base = CompetitiveObservation(
        trial_id="trial-1",
        game_id="game-1",
        save_id="save-1",
        game_date="2021-11-01",
        engine_path="3D_FAST_SIM",
        side="USER",
        controller_assigned=True,
        played_normalize_on=False,
        sim_normalize_on=False,
        played_quarter_minutes=12,
        sim_quarter_minutes=12,
        base_source_ref="settings.json",
        metrics={"team_3pt_pct": 0.40},
    )

    # 1. Identical context -> Comparable
    obs_same_ctx = CompetitiveObservation(
        trial_id="trial-1",
        game_id="game-2",
        save_id="save-1",
        game_date="2021-11-03",
        engine_path="3D_FAST_SIM",
        side="USER",
        controller_assigned=True,
        played_normalize_on=False,
        sim_normalize_on=False,
        played_quarter_minutes=12,
        sim_quarter_minutes=12,
        base_source_ref="settings.json",
        metrics={"team_3pt_pct": 0.36},
    )
    is_comp, deltas, reason = VAEObservationComparator.compare(obs_base, obs_same_ctx)
    assert is_comp is True
    assert deltas is not None
    assert deltas["delta_team_3pt_pct"] == -0.04

    # 2. Side differs -> INCOMPARABLE
    obs_diff_side = CompetitiveObservation(
        trial_id="trial-1",
        game_id="game-3",
        save_id="save-1",
        game_date="2021-11-04",
        engine_path="3D_FAST_SIM",
        side="CPU",  # Mismatch!
        controller_assigned=True,
        played_normalize_on=False,
        sim_normalize_on=False,
        played_quarter_minutes=12,
        sim_quarter_minutes=12,
        base_source_ref="settings.json",
        metrics={"team_3pt_pct": 0.36},
    )
    is_comp, _, reason = VAEObservationComparator.compare(obs_base, obs_diff_side)
    assert is_comp is False
    assert "Side mismatch" in reason

    # 3. Played Normalize switch differs -> INCOMPARABLE
    obs_diff_norm = CompetitiveObservation(
        trial_id="trial-1",
        game_id="game-4",
        save_id="save-1",
        game_date="2021-11-05",
        engine_path="3D_FAST_SIM",
        side="USER",
        controller_assigned=True,
        played_normalize_on=True,  # Mismatch!
        sim_normalize_on=False,
        played_quarter_minutes=12,
        sim_quarter_minutes=12,
        base_source_ref="settings.json",
        metrics={"team_3pt_pct": 0.36},
    )
    is_comp, _, reason = VAEObservationComparator.compare(obs_base, obs_diff_norm)
    assert is_comp is False
    assert "Played Normalize mismatch" in reason

    # 4. Quarter minutes differ -> INCOMPARABLE
    obs_diff_quarter = CompetitiveObservation(
        trial_id="trial-1",
        game_id="game-5",
        save_id="save-1",
        game_date="2021-11-06",
        engine_path="3D_FAST_SIM",
        side="USER",
        controller_assigned=True,
        played_normalize_on=False,
        sim_normalize_on=False,
        played_quarter_minutes=5,  # Mismatch!
        sim_quarter_minutes=12,
        base_source_ref="settings.json",
        metrics={"team_3pt_pct": 0.36},
    )
    is_comp, _, reason = VAEObservationComparator.compare(obs_base, obs_diff_quarter)
    assert is_comp is False
    assert "Played quarter length mismatch" in reason


def test_f03_f04_knowledge_revision_lifecycle_and_idempotency():
    """
    F03 Test: Initial status MUST be PENDING_REVISION.
    F04 Test: Idempotency key prevents duplicate append.
    """
    rev_manager = VAEKnowledgeRevisionManager()

    # 1. Propose revision -> status must be PENDING_REVISION (F03)
    rev1 = rev_manager.propose_revision(
        trial_id="trial-101",
        prior_claim_ref="CLAIM_OLD_3PT",
        new_claim="Claim that slider at 45 normalizes 3pt%",
        counterexamples=[],
        source_refs=["settings.json"],
    )
    assert rev1.status == RevisionStatus.PENDING_REVISION
    assert rev1.idempotency_key is not None
    assert rev1.revision_time is None
    assert rev1.append_receipt is None

    # 2. Commit append -> status transitions to APPENDED
    ok, committed_rev, msg = rev_manager.commit_append(rev1)
    assert ok is True
    assert committed_rev.status == RevisionStatus.APPENDED
    assert committed_rev.revision_time is not None
    assert committed_rev.append_receipt is not None

    # 3. Duplicate append attempt with identical idempotency key -> DUPLICATE_REJECTED (F04)
    rev2 = rev_manager.propose_revision(
        trial_id="trial-101",
        prior_claim_ref="CLAIM_OLD_3PT",
        new_claim="Claim that slider at 45 normalizes 3pt%",
        counterexamples=[],
        source_refs=["settings.json"],
    )
    assert rev2.status == RevisionStatus.DUPLICATE_REJECTED
    ok, rejected_rev, msg = rev_manager.commit_append(rev2)
    assert ok is False
    assert "DUPLICATE_REJECTED" in msg


def test_f07_blocked_and_not_run_nullability():
    """
    F07 Test: R03, R04, R05 specify explicit blocked-state field nullability.
    """
    # R03: BLOCKED state requires block_reason, allows restore_plan to be None
    preflight_blocked = TrialPreflight(
        trial_id="trial-201",
        target_identity="slider.invalid",
        before_ref="snap-none",
        expected_before=None,
        proposed_after=50,
        metric_primary="3pt",
        metrics_side_effect=[],
        observation_window="5_GAMES",
        restore_plan=None,
        technical_path=None,
        authorization_ref=None,
        block_reason="Target identity unverified",
        block_timestamp="2021-11-01T00:00:00Z",
        status=PreflightStatus.BLOCKED,
    )
    preflight_blocked.validate()  # Must not raise

    # Missing block_reason when BLOCKED -> ValueError
    with pytest.raises(ValueError, match="block_reason is mandatory"):
        invalid_blocked = TrialPreflight(
            trial_id="trial-202",
            target_identity="slider.invalid",
            before_ref="snap-none",
            expected_before=None,
            proposed_after=50,
            metric_primary="3pt",
            metrics_side_effect=[],
            observation_window="5_GAMES",
            status=PreflightStatus.BLOCKED,
        )
        invalid_blocked.validate()

    # R04: NOT_RUN state requires skip_or_abort_reason, allows technical_response/executed_at to be None
    receipt_not_run = ExecutionReceipt(
        trial_id="trial-201",
        action_id="WRITE_SLIDER",
        auth_ref="NO_AUTH",
        actual_scene="PREFLIGHT",
        technical_request_ref="req-201",
        technical_response=None,
        executed_at=None,
        skip_or_abort_reason="DRY_RUN_ONLY",
        status=ReceiptStatus.NOT_RUN,
    )
    receipt_not_run.validate()  # Must not raise

    # Missing skip_or_abort_reason when NOT_RUN -> ValueError
    with pytest.raises(ValueError, match="skip_or_abort_reason is mandatory"):
        invalid_receipt = ExecutionReceipt(
            trial_id="trial-201",
            action_id="WRITE_SLIDER",
            auth_ref="NO_AUTH",
            actual_scene="PREFLIGHT",
            technical_request_ref="req-201",
            status=ReceiptStatus.NOT_RUN,
        )
        invalid_receipt.validate()

    # R05: UNVERIFIED state allows getters and ui_ref to be None
    readback_unverified = TechnicalReadback(
        trial_id="trial-201",
        verification_level="L0",
        status=ReadbackStatus.UNVERIFIED,
    )
    readback_unverified.validate()  # Must not raise
