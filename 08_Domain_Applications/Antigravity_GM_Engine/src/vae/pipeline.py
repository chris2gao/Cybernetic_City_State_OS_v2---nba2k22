"""
VAE E1 End-to-End Vertical Prototype Pipeline.
Orchestrates R01–R09 in an integrated, repeatable, offline dry-run workflow.
"""

from typing import Dict, Any, Optional
import datetime
import uuid

from .contracts import (
    ProfileSnapshot,
    IssueDiagnosis,
    TrialPreflight,
    ExecutionReceipt,
    TechnicalReadback,
    CompetitiveObservation,
    EffectEvaluation,
    KnowledgeRevision,
    DSeriesFeedback,
    EvidenceTier,
    PreflightStatus,
    ReceiptStatus,
    ObservationStatus,
)
from .reader_adapter import VAEReaderAdapter
from .diagnosis import VAEDiagnosisEngine
from .preflight import VAEPreflightEngine
from .simulator import VAEExecutionSimulator
from .readback_adapter import VAEReadbackAdapter
from .observation import VAEObservationComparator
from .evaluator import VAEEvaluationEngine
from .revision import VAEKnowledgeRevisionManager


class VAEE1Pipeline:
    """
    Runs the complete E1 vertical slice prototype.
    """

    def __init__(self, repo_root: str):
        self.repo_root = repo_root
        self.reader = VAEReaderAdapter(repo_root)
        self.diagnostician = VAEDiagnosisEngine()
        self.preflight_engine = VAEPreflightEngine()
        self.simulator = VAEExecutionSimulator(allow_live_writes=False)
        self.readback_adapter = VAEReadbackAdapter()
        self.observation_comparator = VAEObservationComparator()
        self.evaluator = VAEEvaluationEngine()
        self.revision_manager = VAEKnowledgeRevisionManager()

    def run_e1_slice(
        self,
        field_id: str = "three_point_success",
        observed_symptom: str = "three_point_percentage_too_high",
        proposed_after: int = 45,
        authorization_ref: str = "AUTH_OFFLINE_DEV_DRYRUN",
        dry_run: bool = True,
    ) -> Dict[str, Any]:
        """
        Executes an end-to-end E1 run and returns all 9 artifacts.
        """
        # 1. R01: ProfileSnapshot
        snapshot = self.reader.read_settings_field(field_id=field_id, side="USER")

        # 2. R02: IssueDiagnosis
        diagnosis = self.diagnostician.diagnose_issue(
            game_ref="GAME_SEASON_2021_22",
            observed_symptom=observed_symptom,
            domain="E1",
        )

        # 3. R03: TrialPreflight (Safe baseline and rollback plan)
        restore_plan = {
            "field_id": field_id,
            "rollback_value": snapshot.raw_value if snapshot.raw_value is not None else 50,
            "method": "RESTORE_ORIGINAL_SLIDER_VALUE",
        }
        preflight = self.preflight_engine.prepare_preflight(
            target_identity=f"slider.{field_id}",
            baseline_snapshot=snapshot,
            proposed_after=proposed_after,
            metric_primary="team_3pt_pct",
            metrics_side_effect=["team_fg_pct", "pace"],
            observation_window="5_GAMES",
            restore_plan=restore_plan,
            technical_path="SETTINGS_SLIDER_MOCK_WRITE",
            authorization_ref=authorization_ref,
        )

        # 4. R04: ExecutionReceipt (Honest NOT_RUN under zero game write policy)
        receipt = self.simulator.execute_trial(preflight=preflight, dry_run=dry_run)

        # 5. R05: TechnicalReadback (UNVERIFIED)
        readback = self.readback_adapter.perform_readback(receipt=receipt)

        # 6. R06: CompetitiveObservation (Strict context)
        observation = CompetitiveObservation(
            trial_id=preflight.trial_id,
            game_id="GAME_E1_SAMPLE_01",
            save_id=snapshot.save_id,
            game_date="2021-11-15",
            engine_path="3D_FAST_SIM",
            side="USER",
            controller_assigned=True,
            played_normalize_on=False,
            sim_normalize_on=False,
            played_quarter_minutes=12,
            sim_quarter_minutes=12,
            base_source_ref=snapshot.source_ref,
            metrics={"team_3pt_pct": 0.42, "team_fg_pct": 0.48, "pace": 101.2},
            human_note="Initial offline baseline observation",
            confounders=diagnosis.confounders,
            source_refs=[snapshot.source_ref],
            status=ObservationStatus.RECORDED,
        )

        # 7. R07: EffectEvaluation (INCONCLUSIVE due to dry-run / small sample)
        evaluation = self.evaluator.evaluate(
            trial_id=preflight.trial_id,
            preregistered_metric_ref=preflight.metric_primary,
            deltas=None,
            target_direction="DECREASE",
            confounders=diagnosis.confounders,
            sample_size=1,
        )

        # 8. R08: KnowledgeRevision (Strictly PENDING_REVISION with idempotency key)
        revision = self.revision_manager.propose_revision(
            trial_id=preflight.trial_id,
            prior_claim_ref="CLAIM_DEFAULT_3PT_TUNING",
            new_claim=f"Adjusting {field_id} to {proposed_after} is hypothesized to moderate 3PT% toward 35%",
            counterexamples=[],
            source_refs=[diagnosis.basketball_source_ref, snapshot.source_ref],
        )

        # 9. R09: DSeriesFeedback
        feedback = DSeriesFeedback(
            trial_id=preflight.trial_id,
            evidence_tier=EvidenceTier.OFFLINE_FIXTURE,
            d1_information="Requires real-time 3PT shooting percentage query session",
            d2_reader="Requires live settings slider reader binding in active memory",
            d3_capture="Requires multi-game box score batch aggregator",
            d4_service="Requires settings change event notification",
            d5_execution="Requires Human-confirmed live write permission for gameplay sliders",
            owner="Gemini execution / VAE Stage02",
        )

        return {
            "R01_snapshot": snapshot,
            "R02_diagnosis": diagnosis,
            "R03_preflight": preflight,
            "R04_receipt": receipt,
            "R05_readback": readback,
            "R06_observation": observation,
            "R07_evaluation": evaluation,
            "R08_revision": revision,
            "R09_feedback": feedback,
        }
