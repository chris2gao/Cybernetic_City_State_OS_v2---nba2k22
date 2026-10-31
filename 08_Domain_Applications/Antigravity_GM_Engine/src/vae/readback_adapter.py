"""
VAE Technical Readback Adapter (R05).
Manages multi-tier verification (L0–L3) without false live claims.
Fixes F07: Explicit handling of UNVERIFIED state nullability.
"""

from typing import Optional, List
from .contracts import TechnicalReadback, ReadbackStatus, ExecutionReceipt, ReceiptStatus


class VAEReadbackAdapter:
    """
    Produces honest technical readbacks reflecting actual verification levels.
    """

    def perform_readback(
        self,
        receipt: ExecutionReceipt,
        getter_before_ref: Optional[str] = None,
        getter_after_ref: Optional[str] = None,
        ui_ref: Optional[str] = None,
        save_reload_ref: Optional[str] = None,
    ) -> TechnicalReadback:
        # If execution was NOT_RUN or REJECTED, readback is UNVERIFIED / SKIPPED
        if receipt.status in [ReceiptStatus.NOT_RUN, ReceiptStatus.REJECTED, ReceiptStatus.PERMISSION_DENIED]:
            return TechnicalReadback(
                trial_id=receipt.trial_id,
                verification_level="L0",
                getter_before_ref=None,
                getter_after_ref=None,
                ui_ref=None,
                save_reload_ref=None,
                conflicts=None,
                status=ReadbackStatus.UNVERIFIED,
            )

        # In offline testing when getter refs are provided
        if getter_before_ref and getter_after_ref:
            conflicts = []
            if getter_before_ref == getter_after_ref:
                conflicts.append("NO_CHANGE_DETECTED_BETWEEN_BEFORE_AND_AFTER")

            level = "L1"
            if ui_ref:
                level = "L2"
            if save_reload_ref:
                level = "L3"

            return TechnicalReadback(
                trial_id=receipt.trial_id,
                verification_level=level,
                getter_before_ref=getter_before_ref,
                getter_after_ref=getter_after_ref,
                ui_ref=ui_ref,
                save_reload_ref=save_reload_ref,
                conflicts=conflicts if conflicts else None,
                status=ReadbackStatus.VERIFIED if not conflicts else ReadbackStatus.INCONSISTENT,
            )

        return TechnicalReadback(
            trial_id=receipt.trial_id,
            verification_level="L0",
            getter_before_ref=None,
            getter_after_ref=None,
            ui_ref=None,
            save_reload_ref=None,
            conflicts=["MISSING_GETTER_REFERENCES"],
            status=ReadbackStatus.UNVERIFIED,
        )
