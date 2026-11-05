"""Offline factorial contrasts with explicit evidence and design limits."""
import math
from statistics import mean


def factorial_2x2(cells, *, synthetic, mode, confounders=(), independent_assignment=False):
    """Return marginal mean contrasts and a difference-of-differences interaction.

    Replicates must already have a defensible assignment/cluster unit. This
    function reports arithmetic, without estimating causal confidence intervals.
    """
    if type(synthetic) is not bool or type(independent_assignment) is not bool:
        raise ValueError('Evidence and assignment flags must be boolean')
    if mode not in ('SYNTHETIC', 'FAST_SIM', 'CPU_VS_CPU_3D', 'HUMAN_VS_AI_3D', 'UNKNOWN'):
        raise ValueError('Unknown mode label')
    if synthetic != (mode == 'SYNTHETIC'):
        raise ValueError('Synthetic data requires SYNTHETIC mode; real data requires a game mode or UNKNOWN')
    if set(cells) != {'00', '10', '01', '11'}:
        return {'status': 'NOT_CAUSALLY_IDENTIFIED', 'reason': 'Four treatment cells required'}
    averages = {}
    for name, observations in cells.items():
        if not observations or any(isinstance(x, bool) or not isinstance(x, (int, float)) or not math.isfinite(x) for x in observations):
            raise ValueError('Each cell needs finite numeric observations')
        averages[name] = mean(observations)
    a0 = averages['10'] - averages['00']
    a1 = averages['11'] - averages['01']
    b0 = averages['01'] - averages['00']
    b1 = averages['11'] - averages['10']
    status = 'SYNTHETIC_ARITHMETIC_ONLY' if synthetic else 'NOT_CAUSALLY_IDENTIFIED'
    return {'status': status, 'mode': mode, 'synthetic': synthetic,
            'cell_means': averages, 'factor_A': (a0 + a1) / 2,
            'factor_B': (b0 + b1) / 2, 'interaction_difference_in_differences': a1 - a0,
            'confounders': list(confounders), 'independent_assignment_claim': independent_assignment,
            'causal_review_required': not synthetic, 'confidence_interval': None,
            'limits': ['No inference from Box score to 3D tactical behavior',
                       'Repeated players and games within team/season share clusters',
                       'Assignment flag alone cannot establish independent randomization']}


def tactical_evidence_protocol(mode):
    if mode not in ('FAST_SIM', 'CPU_VS_CPU_3D', 'HUMAN_VS_AI_3D', 'UNKNOWN'):
        raise ValueError('Unknown game mode')
    return {'mode': mode, 'status': 'TACTICAL_EXECUTION_UNKNOWN',
            'required_observations': ['save/build/game/possession identity', 'basketball intent',
                                      'Native setting and readback source', 'timestamped player movement',
                                      'advantage creation', 'shot/action outcome'],
            'live_action_authorized': False}
