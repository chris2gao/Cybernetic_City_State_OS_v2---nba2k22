"""
VAE Safety Preflight Engine (R03).
Enforces safety gates, baseline verification, rollback plans, and permission checks.
Fixes F07: Explicit blocked-state nullability and reason tracking.
"""

from typing import Dict, Any, Optional
import datetime
import uuid
from .contracts import TrialPreflight, PreflightStatus, ProfileSnapshot


class VAEPreflightEngine:
    """
    Evaluates whether a planned trial satisfies all safety, rollback, and identity conditions.
    """

    def prepare_preflight(
        self,
        target_identity: str,
        baseline_snapshot: ProfileSnapshot,
        proposed_after: Any,
        metric_primary: str,
        metrics_side_effect: list[str],
        observation_window: str = "5_GAMES",
        restore_plan: Optional[Dict[str, Any]] = None,
        technical_path: Optional[str] = None,
        authorization_ref: Optional[str] = None,
        force_block_reason: Optional[str] = None,
    ) -> TrialPreflight:
        trial_id = f"trial-{uuid.uuid4().hex[:8]}"

        # Check for forced block
        if force_block_reason:
            return TrialPreflight(
                trial_id=trial_id,
                target_identity=target_identity,
                before_ref=baseline_snapshot.snapshot_id,
                expected_before=baseline_snapshot.raw_value,
                proposed_after=proposed_after,
                metric_primary=metric_primary,
                metrics_side_effect=metrics_side_effect,
                observation_window=observation_window,
                restore_plan=None,
                technical_path=None,
                authorization_ref=None,
                block_reason=force_block_reason,
                block_timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                status=PreflightStatus.BLOCKED,
            )

        # Baseline value verification
        if baseline_snapshot.raw_value is None:
            return TrialPreflight(
                trial_id=trial_id,
                target_identity=target_identity,
                before_ref=baseline_snapshot.snapshot_id,
                expected_before=None,
                proposed_after=proposed_after,
                metric_primary=metric_primary,
                metrics_side_effect=metrics_side_effect,
                observation_window=observation_window,
                restore_plan=None,
                technical_path=None,
                authorization_ref=None,
                block_reason="G01/G02_FAIL: Baseline raw value is unknown or unverified",
                block_timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                status=PreflightStatus.BLOCKED,
            )

        # Rollback plan verification (G08)
        if not restore_plan or "rollback_value" not in restore_plan:
            return TrialPreflight(
                trial_id=trial_id,
                target_identity=target_identity,
                before_ref=baseline_snapshot.snapshot_id,
                expected_before=baseline_snapshot.raw_value,
                proposed_after=proposed_after,
                metric_primary=metric_primary,
                metrics_side_effect=metrics_side_effect,
                observation_window=observation_window,
                restore_plan=None,
                technical_path=technical_path,
                authorization_ref=authorization_ref,
                block_reason="G08_FAIL: Mandatory restore_plan with rollback_value is missing",
                block_timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                status=PreflightStatus.BLOCKED,
            )

        # Authorization check
        if not authorization_ref:
            return TrialPreflight(
                trial_id=trial_id,
                target_identity=target_identity,
                before_ref=baseline_snapshot.snapshot_id,
                expected_before=baseline_snapshot.raw_value,
                proposed_after=proposed_after,
                metric_primary=metric_primary,
                metrics_side_effect=metrics_side_effect,
                observation_window=observation_window,
                restore_plan=restore_plan,
                technical_path=technical_path,
                authorization_ref=None,
                block_reason="PERMISSION_DENIED: Explicit authorization_ref is required",
                block_timestamp=datetime.datetime.now(datetime.timezone.utc).isoformat(),
                status=PreflightStatus.BLOCKED,
            )

        # All gates passed: status is READY
        return TrialPreflight(
            trial_id=trial_id,
            target_identity=target_identity,
            before_ref=baseline_snapshot.snapshot_id,
            expected_before=baseline_snapshot.raw_value,
            proposed_after=proposed_after,
            metric_primary=metric_primary,
            metrics_side_effect=metrics_side_effect,
            observation_window=observation_window,
            restore_plan=restore_plan,
            technical_path=technical_path or "OFFLINE_SIMULATION_STAGING",
            authorization_ref=authorization_ref,
            block_reason=None,
            block_timestamp=None,
            status=PreflightStatus.READY,
        )
