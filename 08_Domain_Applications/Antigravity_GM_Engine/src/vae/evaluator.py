"""
VAE Effect Evaluation Engine (R07).
Evaluates pre-registered metrics against competitive observations and side effects.
Fixes P1-07: Statistical honesty; replaces naive thresholds with non-causal trend classifications.
Never jumps to causal CONFIRMED without randomized controlled protocols and confounder controls.
"""

from typing import Dict, Any, List, Optional
from .contracts import EffectEvaluation, EvaluationOutcome, CompetitiveObservation


class VAEEvaluationEngine:
    """
    Evaluates trial results against preregistered primary metrics.
    Strictly distinguishes observational association trends from controlled causal confirmation.
    """

    def evaluate(
        self,
        trial_id: str,
        preregistered_metric_ref: str,
        deltas: Optional[Dict[str, float]],
        target_direction: str,  # "DECREASE" | "INCREASE" | "NEUTRAL"
        confounders: List[str],
        sample_size: int = 1,
        controlled_experiment: bool = False,
        confounders_controlled: bool = False,
    ) -> EffectEvaluation:
        # 1. Default to INCONCLUSIVE when deltas are absent or sample size is small (<5 games)
        if not deltas or sample_size < 5:
            return EffectEvaluation(
                trial_id=trial_id,
                preregistered_metric_ref=preregistered_metric_ref,
                outcome=EvaluationOutcome.INCONCLUSIVE,
                side_effects=["Insufficient sample size for competitive significance (< 5 games)"],
                confidence=0.2,
                competing_explanations=[
                    "Small sample variance",
                    "Game-to-game shooting luck",
                    "Opponent defensive tier variations",
                ] + confounders,
                sample_size=sample_size,
                confounders_controlled=confounders_controlled,
            )

        # 2. Check primary metric delta
        primary_key = f"delta_{preregistered_metric_ref}"
        if primary_key not in deltas:
            return EffectEvaluation(
                trial_id=trial_id,
                preregistered_metric_ref=preregistered_metric_ref,
                outcome=EvaluationOutcome.INCONCLUSIVE,
                side_effects=["Primary metric delta not observed in data"],
                confidence=0.1,
                competing_explanations=["Metric tracking failure"],
                sample_size=sample_size,
                confounders_controlled=confounders_controlled,
            )

        delta = deltas[primary_key]

        # 3. If there are active uncontrolled confounders, effect cannot be isolated
        if confounders and not confounders_controlled:
            return EffectEvaluation(
                trial_id=trial_id,
                preregistered_metric_ref=preregistered_metric_ref,
                outcome=EvaluationOutcome.INCONCLUSIVE,
                side_effects=[f"Uncontrolled confounders present: {', '.join(confounders)}"],
                confidence=0.3,
                competing_explanations=confounders,
                sample_size=sample_size,
                confounders_controlled=False,
            )

        # 4. Check for negligible change
        noise_threshold = 0.01
        if abs(delta) <= noise_threshold:
            return EffectEvaluation(
                trial_id=trial_id,
                preregistered_metric_ref=preregistered_metric_ref,
                outcome=EvaluationOutcome.NO_APPARENT_CHANGE,
                side_effects=[],
                confidence=0.6,
                competing_explanations=["Intervention delta within baseline game variance"],
                sample_size=sample_size,
                confounders_controlled=confounders_controlled,
            )

        # 5. Evaluate directional trend
        if target_direction == "DECREASE":
            aligned = delta < -noise_threshold
        elif target_direction == "INCREASE":
            aligned = delta > noise_threshold
        else:
            aligned = abs(delta) <= noise_threshold

        # 6. P1-07 Gate: Causal CONFIRMED only if controlled protocol satisfied and sample_size >= 20
        if aligned:
            if controlled_experiment and confounders_controlled and sample_size >= 20:
                outcome = EvaluationOutcome.CONFIRMED_CONTROLLED
                confidence = 0.85
            else:
                outcome = EvaluationOutcome.OBSERVED_TREND_POSITIVE
                confidence = round(min(0.65, 0.35 + (sample_size * 0.02)), 2)
            return EffectEvaluation(
                trial_id=trial_id,
                preregistered_metric_ref=preregistered_metric_ref,
                outcome=outcome,
                side_effects=[],
                confidence=confidence,
                competing_explanations=["Directional observational trend; causal isolation pending controls"] if not controlled_experiment else [],
                sample_size=sample_size,
                confounders_controlled=confounders_controlled,
            )
        else:
            if controlled_experiment and confounders_controlled and sample_size >= 20:
                outcome = EvaluationOutcome.REFUTED_CONTROLLED
                confidence = 0.80
            else:
                outcome = EvaluationOutcome.OBSERVED_TREND_NEGATIVE
                confidence = 0.55
            return EffectEvaluation(
                trial_id=trial_id,
                preregistered_metric_ref=preregistered_metric_ref,
                outcome=outcome,
                side_effects=[f"Observed metric moved counter to target: delta={delta}"],
                confidence=confidence,
                competing_explanations=["Intervention ineffective or counteracted by in-game adjustments"],
                sample_size=sample_size,
                confounders_controlled=confounders_controlled,
            )
