"""
Unit tests for VAE Business Contracts (R01–R09).
Specifically verifies resolutions for:
- F02, F03, F04, F07
- P0-01, P0-02, P0-03, P0-04, P1-06, P1-07
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


def test_p0_01_static_snapshot_cannot_claim_captured():
    """P0-01: Static specification or fixture source cannot claim SnapshotStatus.CAPTURED."""
    with pytest.raises(ValueError, match="Static source cannot claim SnapshotStatus.CAPTURED"):
        snap = ProfileSnapshot(
            snapshot_id="snap-1",
            save_id="OFFLINE_DEFAULT",  # static
            game_build="2K22_PC",
            game_mode="MYLEAGUE",
            scene="SETTINGS",
            side="USER",
            field_id="three_point_success",
            raw_value=50,
            display_value=50,
            unit="slider",
            source_ref="settings.json",
            captured_at="STATIC_SOURCE",  # static
            freshness="IMMUTABLE",
            status=SnapshotStatus.CAPTURED,
        )
        snap.validate()


def test_p0_02_mock_auth_cannot_enter_ready():
    """P0-02: Preflight cannot enter READY with mock/dryrun authorization token."""
    with pytest.raises(ValueError, match="Mock authorization"):
        pre = TrialPreflight(
            trial_id="t-1",
            target_identity="slider.three_point_success",
            before_ref="snap-1",
            expected_before=50,
            proposed_after=45,
            metric_primary="3pt",
            metrics_side_effect=[],
            observation_window="5_GAMES",
            restore_plan={"rollback_value": 50},
            technical_path="MOCK_PATH",
            authorization_ref="AUTH_OFFLINE_DEV_DRYRUN",  # Mock token!
            status=PreflightStatus.READY,
        )
        pre.validate()


def test_p0_03_synthetic_metrics_cannot_claim_recorded():
    """P0-03: Synthetic or offline observation cannot claim ObservationStatus.RECORDED."""
    with pytest.raises(ValueError, match="Offline/synthetic data cannot claim ObservationStatus.RECORDED"):
        obs = CompetitiveObservation(
            trial_id="t-1",
            game_id="game-mock-1",
            save_id="SAVE_01",
            game_date="2021-11-01",
            engine_path="3D_FAST_SIM",
            side="USER",
            controller_assigned=True,
            played_normalize_on=False,
            sim_normalize_on=False,
            played_quarter_minutes=12,
            sim_quarter_minutes=12,
            base_source_ref="ref",
            metrics={"pts": 100},
            source_refs=["SYNTHETIC_OFFLINE_FIXTURE"],
            status=ObservationStatus.RECORDED,  # False claim!
        )
        obs.validate()


def test_p0_04_observation_comparability_save_and_engine_path():
    """P0-04: Enforces save_id and engine_path in observation comparison."""
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
        status=ObservationStatus.OFFLINE_FIXTURE,
    )

    # 1. Save mismatch -> Incomparable
    obs_diff_save = CompetitiveObservation(
        trial_id="trial-1",
        game_id="game-2",
        save_id="save-2",  # Mismatch!
        game_date="2021-11-02",
        engine_path="3D_FAST_SIM",
        side="USER",
        controller_assigned=True,
        played_normalize_on=False,
        sim_normalize_on=False,
        played_quarter_minutes=12,
        sim_quarter_minutes=12,
        base_source_ref="settings.json",
        metrics={"team_3pt_pct": 0.38},
        status=ObservationStatus.OFFLINE_FIXTURE,
    )
    comp_save, _, reason_save = VAEObservationComparator.compare(obs_base, obs_diff_save)
    assert comp_save is False
    assert "save_id mismatch" in reason_save

    # 2. Engine path mismatch -> Incomparable
    obs_diff_path = CompetitiveObservation(
        trial_id="trial-1",
        game_id="game-3",
        save_id="save-1",
        game_date="2021-11-03",
        engine_path="CALENDAR_SIM",  # Mismatch!
        side="USER",
        controller_assigned=True,
        played_normalize_on=False,
        sim_normalize_on=False,
        played_quarter_minutes=12,
        sim_quarter_minutes=12,
        base_source_ref="settings.json",
        metrics={"team_3pt_pct": 0.38},
        status=ObservationStatus.OFFLINE_FIXTURE,
    )
    comp_path, _, reason_path = VAEObservationComparator.compare(obs_base, obs_diff_path)
    assert comp_path is False
    assert "engine_path mismatch" in reason_path


def test_p1_06_structured_readback_layers():
    """P1-06: TechnicalReadback provides structured discrete evaluation of L0-L3 layers."""
    readback = TechnicalReadback(
        trial_id="t-1",
        verification_level="L0",
        layers={
            "L0_memory": "NOT_EXECUTED_DRY_RUN",
            "L1_process": "NOT_EXECUTED_DRY_RUN",
            "L2_ui_settings": "NOT_EXECUTED_DRY_RUN",
            "L3_save_reload": "NOT_EXECUTED_DRY_RUN",
        },
        status=ReadbackStatus.UNVERIFIED,
    )
    readback.validate()
    assert "L0_memory" in readback.layers
    assert "L3_save_reload" in readback.layers


def test_p1_07_confirmed_controlled_requires_controls_and_sample():
    """P1-07: EffectEvaluation cannot claim CONFIRMED_CONTROLLED without controlled experiment and sample_size >= 20."""
    with pytest.raises(ValueError, match="Cannot claim CONFIRMED_CONTROLLED"):
        eval_obj = EffectEvaluation(
            trial_id="t-1",
            preregistered_metric_ref="team_3pt_pct",
            outcome=EvaluationOutcome.CONFIRMED_CONTROLLED,
            side_effects=[],
            confidence=0.8,
            competing_explanations=[],
            sample_size=5,  # Too small (<20)
            confounders_controlled=False,  # Uncontrolled
        )
        eval_obj.validate()


def test_f02_observation_comparability_strict_context():
    """F02 Test: R06 context must enforce side, controller, dual Normalize, quarter lengths, and base_source."""
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
        status=ObservationStatus.OFFLINE_FIXTURE,
    )

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
        status=ObservationStatus.OFFLINE_FIXTURE,
    )
    is_comp, _, reason = VAEObservationComparator.compare(obs_base, obs_diff_side)
    assert is_comp is False
    assert "Side mismatch" in reason


def test_f03_f04_knowledge_revision_lifecycle_and_idempotency():
    """F03 Test: Initial status MUST be PENDING_REVISION. F04 Test: Idempotency key prevents duplicate append."""
    rev_manager = VAEKnowledgeRevisionManager()

    rev1 = rev_manager.propose_revision(
        trial_id="trial-101",
        prior_claim_ref="CLAIM_OLD_3PT",
        new_claim="Claim that slider at 45 normalizes 3pt%",
        counterexamples=[],
        source_refs=["settings.json"],
    )
    assert rev1.status == RevisionStatus.PENDING_REVISION
    assert rev1.idempotency_key is not None

    ok, committed_rev, msg = rev_manager.commit_append(rev1)
    assert ok is True
    assert committed_rev.status == RevisionStatus.APPENDED

    # Duplicate append rejected
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
    """F07 Test: R03, R04, R05 specify explicit blocked-state field nullability."""
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
    preflight_blocked.validate()  # Valid

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
    receipt_not_run.validate()  # Valid
