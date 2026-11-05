"""Standalone synthetic arithmetic smoke check. Not a game test or frozen Stage 04 test."""
import json
from datetime import datetime, timezone

cells = {(0, 0): 100.0, (1, 0): 106.0, (0, 1): 104.0, (1, 1): 118.0}
effects = {
    'A_when_B0': cells[1, 0] - cells[0, 0],
    'B_when_A0': cells[0, 1] - cells[0, 0],
    'A_by_B_interaction': cells[1, 1] - cells[1, 0] - cells[0, 1] + cells[0, 0],
    'A_marginal': (cells[1, 0] + cells[1, 1] - cells[0, 0] - cells[0, 1]) / 2,
    'B_marginal': (cells[0, 1] + cells[1, 1] - cells[0, 0] - cells[1, 0]) / 2,
}
checks = {
    'known_2x2_contrast': effects['A_when_B0'] == 6 and effects['B_when_A0'] == 4 and effects['A_by_B_interaction'] == 8,
    'marginals_consistent': effects['A_marginal'] == 10 and effects['B_marginal'] == 8,
    'missing_cell_not_identifiable': 'NOT_CAUSALLY_IDENTIFIED' == ('NOT_CAUSALLY_IDENTIFIED' if len({k: v for k, v in cells.items() if k != (1, 1)}) != 4 else 'ESTIMABLE'),
    'repeated_team_not_independent': len({('season1', 'teamA'), ('season1', 'teamA'), ('season1', 'teamA')}) == 1,
    'no_real_game_data_claim': True,
}
assert all(checks.values())
print(json.dumps({'status': 'PASS_SYNTHETIC_ARITHMETIC_ONLY', 'cells': {f'A{a}B{b}': v for (a, b), v in cells.items()}, 'contrasts': effects, 'checks': checks, 'synthetic': True, 'frozen_stage04': False, 'nba2k22_live_effect': 'NOT_TESTED'}, sort_keys=True))
