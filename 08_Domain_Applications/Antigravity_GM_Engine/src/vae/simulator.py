"""
VAE Execution Simulator & Safety Dispatcher (R04).
Enforces zero unauthorized game write policy. Produces structured ExecutionReceipt.
Fixes F07: Strict handling of NOT_RUN and REJECTED states.
"""

from typing import Dict, Any, Optional
import datetime
from .contracts import TrialPreflight, ExecutionReceipt, ReceiptStatus, PreflightStatus


class VAEExecutionSimulator:
    """
    Simulates trial dispatch in offline/dry-run mode, guaranteeing zero unauthorized writes
    to active game processes or save files.
    """

    def __init__(self, allow_live_writes: bool = False):
        # By default in this task, live writes are strictly False
        self.allow_live_writes = allow_live_writes

    def execute_trial(
        self,
        preflight: TrialPreflight,
        dry_run: bool = True,
    ) -> ExecutionReceipt:
        # Preflight gate check: in dry-run mode, blocked preflight produces honest NOT_RUN
        if preflight.status != PreflightStatus.READY:
            return ExecutionReceipt(
                trial_id=preflight.trial_id,
                action_id="DISPATCH_TRIAL_ACTION",
                auth_ref=preflight.authorization_ref or "NO_AUTH",
                actual_scene="PREFLIGHT_GATE",
                technical_request_ref=f"req-{preflight.trial_id}",
                technical_response={
                    "mode": "DRY_RUN_SIMULATION",
                    "target_identity": preflight.target_identity,
                    "simulated_before": preflight.expected_before,
                    "simulated_after": preflight.proposed_after,
                    "game_memory_modified": False,
                },
                executed_at=None,
                skip_or_abort_reason=f"OFFLINE_DRY_RUN_ONLY_PREFLIGHT_BLOCKED: {preflight.block_reason}",
                status=ReceiptStatus.NOT_RUN,
            )

        # In current environment, live writes are NOT authorized
        if not self.allow_live_writes or dry_run:
            return ExecutionReceipt(
                trial_id=preflight.trial_id,
                action_id="SIMULATED_STAGING_TRIAL",
                auth_ref=preflight.authorization_ref or "OFFLINE_AUTH",
                actual_scene="OFFLINE_SANDBOX",
                technical_request_ref=f"req-{preflight.trial_id}",
                technical_response={
                    "mode": "DRY_RUN_SIMULATION",
                    "target_identity": preflight.target_identity,
                    "simulated_before": preflight.expected_before,
                    "simulated_after": preflight.proposed_after,
                    "game_memory_modified": False,
                },
                executed_at=None,  # Intentionally None per F07 for NOT_RUN
                skip_or_abort_reason="OFFLINE_DRY_RUN_ONLY_NO_LIVE_WRITE_AUTHORIZATION",
                status=ReceiptStatus.NOT_RUN,
            )

        # Unauthorized live write request attempt
        return ExecutionReceipt(
            trial_id=preflight.trial_id,
            action_id="UNAUTHORIZED_LIVE_WRITE",
            auth_ref=preflight.authorization_ref or "UNKNOWN",
            actual_scene="SECURITY_BARRIER",
            technical_request_ref=f"req-{preflight.trial_id}",
            technical_response=None,
            executed_at=None,
            skip_or_abort_reason="PERMISSION_DENIED: Live game write authority not granted by task packet",
            status=ReceiptStatus.PERMISSION_DENIED,
        )
