"""
VAE Effect Evaluation Engine (R07).
Evaluates pre-registered metrics against competitive observations and side effects.
"""

from typing import Dict, Any, List, Optional
from .contracts import EffectEvaluation, EvaluationOutcome, CompetitiveObservation


class VAEEvaluationEngine:
    """
    Evaluates trial results against preregistered primary metrics and detects side-effects.
    """

    def evaluate(
        self,
        trial_id: str,
        preregistered_metric_ref: str,
        deltas: Optional[Dict[str, float]],
        target_direction: str,  # "DECREASE" | "INCREASE" | "NEUTRAL"
        confounders: List[str],
        sample_size: int = 1,
    ) -> EffectEvaluation:
        # Default to INCONCLUSIVE when deltas are absent or sample size is too small (<5 games)
        if not deltas or sample_size < 5:
            return EffectEvaluation(
                trial_id=trial_id,
                preregistered_metric_ref=preregistered_metric_ref,
                outcome=EvaluationOutcome.INCONCLUSIVE,
                side_effects=["Insufficient sample size for competitive significance"],
                confidence=0.3,
                competing_explanations=[
                    "Small sample variance",
                    "Game-to-game shooting luck",
                    "Opponent defensive tier variations",
                ] + confounders,
            )

        # Check primary metric delta
        primary_key = f"delta_{preregistered_metric_ref}"
        if primary_key not in deltas:
            return EffectEvaluation(
                trial_id=trial_id,
                preregistered_metric_ref=preregistered_metric_ref,
                outcome=EvaluationOutcome.INCONCLUSIVE,
                side_effects=["Primary metric delta not observed in data"],
                confidence=0.2,
                competing_explanations=["Metric tracking failure"],
            )

        delta = deltas[primary_key]
        if target_direction == "DECREASE":
            success = delta < -0.02
        elif target_direction == "INCREASE":
            success = delta > 0.02
        else:
            success = abs(delta) <= 0.02

        if success:
            confidence = min(0.9, 0.5 + (sample_size * 0.04) - (len(confounders) * 0.1))
            return EffectEvaluation(
                trial_id=trial_id,
                preregistered_metric_ref=preregistered_metric_ref,
                outcome=EvaluationOutcome.CONFIRMED,
                side_effects=[],
                confidence=round(max(0.1, confidence), 2),
                competing_explanations=confounders,
            )
        else:
            return EffectEvaluation(
                trial_id=trial_id,
                preregistered_metric_ref=preregistered_metric_ref,
                outcome=EvaluationOutcome.REFUTED,
                side_effects=[f"Metric moved counter to target: delta={delta}"],
                confidence=0.7,
                competing_explanations=["Intervention ineffective or counteracted by ACE/substitutions"],
            )
