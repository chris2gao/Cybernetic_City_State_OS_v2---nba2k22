"""
VAE E1 End-to-End Vertical Prototype Pipeline.
Orchestrates R01–R09 in an integrated, repeatable, offline dry-run workflow.
Fixes P0-01, P0-02, P0-03: Honest labeling of static specs, preflight blocks, and unobserved metrics.
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
    Runs the complete E1 vertical slice prototype with strict empirical honesty.
    """

    def __init__(self, repo_root: str, ledger_path: Optional[str] = None):
        self.repo_root = repo_root
        self.reader = VAEReaderAdapter(repo_root)
        self.diagnostician = VAEDiagnosisEngine()
        self.preflight_engine = VAEPreflightEngine()
        self.simulator = VAEExecutionSimulator(allow_live_writes=False)
        self.readback_adapter = VAEReadbackAdapter()
        self.observation_comparator = VAEObservationComparator()
        self.evaluator = VAEEvaluationEngine()
        self.revision_manager = VAEKnowledgeRevisionManager(ledger_path=ledger_path)

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
        # 1. R01: ProfileSnapshot (P0-01: Static spec)
        snapshot = self.reader.read_settings_field(field_id=field_id, side="USER")

        # 2. R02: IssueDiagnosis
        diagnosis = self.diagnostician.diagnose_issue(
            game_ref="GAME_SEASON_2021_22",
            observed_symptom=observed_symptom,
            domain="E1",
        )

        # 3. R03: TrialPreflight (P0-02: Safety gates; mock auth or static snapshot yields BLOCKED)
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

        # 5. R05: TechnicalReadback (P1-06: Structured UNVERIFIED readback across L0-L3)
        readback = self.readback_adapter.perform_readback(receipt=receipt)

        # 6. R06: CompetitiveObservation (P0-03: NOT_OBSERVED / OFFLINE_FIXTURE, never false RECORDED)
        obs_status = ObservationStatus.NOT_OBSERVED if receipt.status == ReceiptStatus.NOT_RUN else ObservationStatus.OFFLINE_FIXTURE
        observation = CompetitiveObservation(
            trial_id=preflight.trial_id,
            game_id="GAME_E1_SAMPLE_01",
            save_id="TEST_DRYRUN_SAVE_01",
            game_date="2021-11-15",
            engine_path="3D_FAST_SIM",
            side=snapshot.side,
            controller_assigned=True,
            played_normalize_on=False,
            sim_normalize_on=False,
            played_quarter_minutes=12,
            sim_quarter_minutes=12,
            base_source_ref=snapshot.source_ref,
            metrics={"team_3pt_pct": 0.42, "team_fg_pct": 0.48, "pace": 101.2},
            human_note="Offline fixture unobserved in live match due to dry-run NOT_RUN execution receipt",
            source_refs=["SYNTHETIC_OFFLINE_FIXTURE"],
            status=obs_status,
        )

        # 7. R07: EffectEvaluation (P1-07: Inconclusive without live multi-game observations)
        evaluation = self.evaluator.evaluate(
            trial_id=preflight.trial_id,
            preregistered_metric_ref="team_3pt_pct",
            deltas=None,
            target_direction="DECREASE",
            confounders=["offline_dryrun_no_live_metrics"],
            sample_size=0,
        )

        # 8. R08: KnowledgeRevision (PENDING_REVISION)
        revision = self.revision_manager.propose_revision(
            trial_id=preflight.trial_id,
            prior_claim_ref="G01_DEFAULT_HOF_SLIDERS",
            new_claim=f"Adjusting {field_id} towards {proposed_after} is staged in dry-run; awaiting live test authorization",
            counterexamples=[],
            source_refs=[snapshot.source_ref, receipt.action_id],
        )

        # 9. R09: DSeriesFeedback
        feedback = DSeriesFeedback(
            trial_id=preflight.trial_id,
            evidence_tier=EvidenceTier.OFFLINE_FIXTURE,
            d1_information="E1 gameplay profile and slider definitions verified offline",
            d2_reader="VAEReaderAdapter read static configuration without game process attachment",
            d3_capture="Awaiting live gameplay observation stream for competitive metrics",
            d4_service="Awaiting authorized memory service for safe slider readback",
            d5_execution="Zero game write policy enforced; execution simulator produced NOT_RUN receipt",
            owner="Gemini_Flash_3_8_execution",
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
