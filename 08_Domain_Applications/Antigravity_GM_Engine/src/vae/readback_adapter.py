"""
VAE Technical Readback Adapter (R05).
Manages multi-tier verification (L0–L3) without false live claims.
Fixes F07: Explicit handling of UNVERIFIED state nullability.
Fixes P1-06: Explicitly articulates and reports verification across discrete layers:
- L0: Memory value match
- L1: Process alive / handle confirmed
- L2: UI / Settings reflection
- L3: Long-term / Save persistence
"""

from typing import Optional, List, Dict
from .contracts import TechnicalReadback, ReadbackStatus, ExecutionReceipt, ReceiptStatus


class VAEReadbackAdapter:
    """
    Produces honest technical readbacks reflecting actual verification levels across L0–L3.
    """

    def perform_readback(
        self,
        receipt: ExecutionReceipt,
        getter_before_ref: Optional[str] = None,
        getter_after_ref: Optional[str] = None,
        ui_ref: Optional[str] = None,
        save_reload_ref: Optional[str] = None,
    ) -> TechnicalReadback:
        # Default layer status for unexecuted / dry-run trials
        if receipt.status in [ReceiptStatus.NOT_RUN, ReceiptStatus.REJECTED, ReceiptStatus.PERMISSION_DENIED]:
            layers = {
                "L0_memory": "NOT_EXECUTED_DRY_RUN",
                "L1_process": "NOT_EXECUTED_DRY_RUN",
                "L2_ui_settings": "NOT_EXECUTED_DRY_RUN",
                "L3_save_reload": "NOT_EXECUTED_DRY_RUN",
            }
            return TechnicalReadback(
                trial_id=receipt.trial_id,
                verification_level="L0",
                getter_before_ref=None,
                getter_after_ref=None,
                ui_ref=None,
                save_reload_ref=None,
                conflicts=None,
                layers=layers,
                status=ReadbackStatus.UNVERIFIED,
            )

        # In trials where getter refs are provided
        layers = {
            "L0_memory": "UNVERIFIED",
            "L1_process": "VERIFIED" if receipt.actual_scene else "UNVERIFIED",
            "L2_ui_settings": "VERIFIED" if ui_ref else "UNVERIFIED",
            "L3_save_reload": "VERIFIED" if save_reload_ref else "UNVERIFIED",
        }

        if getter_before_ref and getter_after_ref:
            conflicts = []
            if getter_before_ref == getter_after_ref:
                conflicts.append("NO_CHANGE_DETECTED_BETWEEN_BEFORE_AND_AFTER")
                layers["L0_memory"] = "INCONSISTENT"
            else:
                layers["L0_memory"] = "VERIFIED"

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
                layers=layers,
                status=ReadbackStatus.VERIFIED if not conflicts else ReadbackStatus.INCONSISTENT,
            )

        layers["L0_memory"] = "MISSING_GETTER_REFERENCES"
        return TechnicalReadback(
            trial_id=receipt.trial_id,
            verification_level="L0",
            getter_before_ref=None,
            getter_after_ref=None,
            ui_ref=None,
            save_reload_ref=None,
            conflicts=["MISSING_GETTER_REFERENCES"],
            layers=layers,
            status=ReadbackStatus.UNVERIFIED,
        )
