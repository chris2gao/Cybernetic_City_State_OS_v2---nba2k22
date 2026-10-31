"""
VAE Competitive Observation Engine (R06).
Fixes F02: Strictly enforces comparison context (side, controller, dual Normalize, quarter lengths, base source).
"""

from typing import Dict, Any, Tuple, Optional
from .contracts import CompetitiveObservation, ObservationStatus


class VAEObservationComparator:
    """
    Validates and compares game observations, rejecting comparisons where confounding context differs.
    """

    @staticmethod
    def compare(
        before: CompetitiveObservation,
        after: CompetitiveObservation,
    ) -> Tuple[bool, Optional[Dict[str, float]], str]:
        """
        Fixes F02: Verifies strict comparability of observation context.
        Returns: (is_comparable, delta_metrics_dict, explanation)
        """
        # Validate individual records
        before.validate()
        after.validate()

        is_comp, reason = before.is_comparable_with(after)
        if not is_comp:
            return False, None, f"INCOMPARABLE: {reason}"

        # Calculate deltas for numerical metrics
        deltas: Dict[str, float] = {}
        for key, val_after in after.metrics.items():
            if key in before.metrics and isinstance(val_after, (int, float)):
                val_before = before.metrics[key]
                if isinstance(val_before, (int, float)):
                    deltas[f"delta_{key}"] = round(float(val_after - val_before), 4)

        return True, deltas, "Observation comparison successful"
