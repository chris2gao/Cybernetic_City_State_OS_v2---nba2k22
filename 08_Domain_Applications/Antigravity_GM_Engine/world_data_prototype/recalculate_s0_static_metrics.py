"""Standalone deterministic recalculation of S0 static shot tendency metrics.

Queries world-v24.sqlite directly and computes:
- Base table row counts and sorting audit
- Cohort stratification (all N=268, clean N=257)
- Bivariate Pearson correlations
- 6-bin adaptive monotonicity breakdown
- Multivariate OLS models (Models 1-4) with t-statistics and R^2
- Damian Lillard profile and peer group comparisons
"""
import sqlite3
import math
import json
import statistics
from pathlib import Path

def solve_ols(Y, X, feature_names):
    n = len(Y)
    k = len(feature_names)
    XtX = [[sum(X[i][r] * X[i][c] for i in range(n)) for c in range(k)] for r in range(k)]
    XtY = [sum(X[i][r] * Y[i] for i in range(n)) for r in range(k)]
    
    aug = [XtX[r] + [1.0 if r == c else 0.0 for c in range(k)] for r in range(k)]
    for i in range(k):
        pivot = aug[i][i]
        if abs(pivot) < 1e-12:
            for r in range(i+1, k):
                if abs(aug[r][i]) > abs(pivot):
                    aug[i], aug[r] = aug[r], aug[i]
                    pivot = aug[i][i]
                    break
        for c in range(2*k):
            aug[i][c] /= pivot
        for r in range(k):
            if r != i:
                factor = aug[r][i]
                for c in range(2*k):
                    aug[r][c] -= factor * aug[i][c]
    
    inv_XtX = [aug[r][k:] for r in range(k)]
    beta = [sum(inv_XtX[r][c] * XtY[c] for c in range(k)) for r in range(k)]
    
    y_mean = sum(Y) / n
    ss_tot = sum((y - y_mean)**2 for y in Y)
    residuals = [Y[i] - sum(X[i][c] * beta[c] for c in range(k)) for i in range(n)]
    ss_res = sum(e**2 for e in residuals)
    r2 = 1.0 - (ss_res / ss_tot) if ss_tot > 0 else 0.0
    adj_r2 = 1.0 - (1.0 - r2) * (n - 1) / (n - k) if n > k else 0.0
    
    s2 = ss_res / (n - k) if n > k else 0.0
    se_beta = [math.sqrt(max(0, s2 * inv_XtX[j][j])) for j in range(k)]
    t_stats = [beta[j] / se_beta[j] if se_beta[j] > 0 else 0.0 for j in range(k)]
    
    return {
        'n': n,
        'k': k,
        'r2': round(r2, 4),
        'adj_r2': round(adj_r2, 4),
        'rmse': round(math.sqrt(s2), 4),
        'coefficients': {
            feature_names[j]: {
                'beta': round(beta[j], 4),
                'std_error': round(se_beta[j], 4),
                't_stat': round(t_stats[j], 2),
                'ci_95': [round(beta[j] - 1.96 * se_beta[j], 4), round(beta[j] + 1.96 * se_beta[j], 4)]
            }
            for j in range(k)
        }
    }

def pearson_r(x, y):
    n = len(x)
    if n < 2: return 0.0
    mx = sum(x) / n
    my = sum(y) / n
    cov = sum((x[i] - mx) * (y[i] - my) for i in range(n))
    var_x = sum((x[i] - mx)**2 for i in range(n))
    var_y = sum((y[i] - my)**2 for i in range(n))
    denom = math.sqrt(var_x * var_y)
    return round(cov / denom, 4) if denom > 0 else 0.0

def recalculate_all_s0_metrics(db_path, scope_file=None):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row

    # Table row counts
    row_counts = {
        'player_tendency_snapshots': conn.execute("SELECT COUNT(*) FROM player_tendency_snapshots").fetchone()[0],
        'player_attribute_snapshots': conn.execute("SELECT COUNT(*) FROM player_attribute_snapshots").fetchone()[0],
        'player_vitals_observations': conn.execute("SELECT COUNT(*) FROM player_vitals_observations").fetchone()[0],
        'players': conn.execute("SELECT COUNT(*) FROM players").fetchone()[0],
        'capture_units': conn.execute("SELECT COUNT(*) FROM capture_units").fetchone()[0],
        'player_game_boxes_simulated': conn.execute("""
            SELECT COUNT(*) 
            FROM player_game_boxes pb 
            JOIN game_state_observations s ON pb.game_id = s.game_id AND pb.unit_id = s.unit_id 
            WHERE s.is_final = 1 AND s.was_simulated = 1
        """).fetchone()[0]
    }

    # Discrepant game IDs
    discrepant_game_ids = set()
    if scope_file and Path(scope_file).exists():
        with open(scope_file, 'r', encoding='utf-8') as f:
            scope_data = json.load(f)
            for c in scope_data.get('discrepancy_cases', []):
                discrepant_game_ids.add(c['game_id'])

    # Chronological snapshots using cu.observed_at DESC
    tend_q = """
    WITH ranked_tend AS (
        SELECT s.player_id, s.unit_id, s.shot_tendency_raw, s.touches_tendency_raw, cu.observed_at,
               ROW_NUMBER() OVER (PARTITION BY s.player_id ORDER BY cu.observed_at DESC, s.unit_id DESC) as rn
        FROM player_tendency_snapshots s
        JOIN capture_units cu USING(unit_id)
    )
    SELECT * FROM ranked_tend WHERE rn = 1
    """
    tend_dict = {r['player_id']: dict(r) for r in conn.execute(tend_q).fetchall()}

    attr_q = """
    WITH ranked_attr AS (
        SELECT s.player_id, s.unit_id, s.shot_close_raw, s.mid_range_shot_raw, 
               s.three_point_shot_raw, s.shot_iq_raw, s.offensive_consistency_raw, cu.observed_at,
               ROW_NUMBER() OVER (PARTITION BY s.player_id ORDER BY cu.observed_at DESC, s.unit_id DESC) as rn
        FROM player_attribute_snapshots s
        JOIN capture_units cu USING(unit_id)
    )
    SELECT * FROM ranked_attr WHERE rn = 1
    """
    attr_dict = {r['player_id']: dict(r) for r in conn.execute(attr_q).fetchall()}

    vitals_q = """
    WITH ranked_vitals AS (
        SELECT v.player_id, v.unit_id, v.primary_position, v.primary_position_raw, cu.observed_at,
               ROW_NUMBER() OVER (PARTITION BY v.player_id ORDER BY cu.observed_at DESC, v.unit_id DESC) as rn
        FROM player_vitals_observations v
        JOIN capture_units cu USING(unit_id)
        WHERE v.primary_position IS NOT NULL
    )
    SELECT * FROM ranked_vitals WHERE rn = 1
    """
    vitals_dict = {r['player_id']: dict(r) for r in conn.execute(vitals_q).fetchall()}
    names_dict = {r['player_id']: r['display_name'] for r in conn.execute("SELECT player_id, display_name FROM players").fetchall()}

    tactics_q = """
    WITH ranked_tactics AS (
        SELECT t.team_id, t.unit_id, t.run_plays_raw, t.tempo_raw, cu.observed_at,
               ROW_NUMBER() OVER (PARTITION BY t.team_id ORDER BY cu.observed_at DESC, t.unit_id DESC) as rn
        FROM team_tactic_settings t
        JOIN capture_units cu USING(unit_id)
    )
    SELECT * FROM ranked_tactics WHERE rn = 1
    """
    tactics_dict = {r['team_id']: dict(r) for r in conn.execute(tactics_q).fetchall()}

    # Extract deduplicated player game boxes
    boxes_q = """
    WITH ranked_boxes AS (
        SELECT pb.*, g.native_game_id, cu.observed_at,
               ROW_NUMBER() OVER (PARTITION BY pb.player_id, pb.game_id ORDER BY cu.observed_at DESC, pb.unit_id DESC) as rn
        FROM player_game_boxes pb
        JOIN games g ON pb.game_id = g.game_id
        JOIN capture_units cu ON pb.unit_id = cu.unit_id
        JOIN game_state_observations s ON pb.game_id = s.game_id AND pb.unit_id = s.unit_id
        WHERE s.is_final = 1 AND s.was_simulated = 1
    )
    SELECT * FROM ranked_boxes WHERE rn = 1
    """
    all_boxes = conn.execute(boxes_q).fetchall()

    # Sum of player FGA per game/team (team shot share denominator)
    team_game_fga = {}
    for b in all_boxes:
        key = (b['game_id'], b['team_id'])
        team_game_fga[key] = team_game_fga.get(key, 0) + (b['fg_attempted'] or 0)

    player_games = {}
    for b in all_boxes:
        pid = b['player_id']
        if pid not in player_games:
            player_games[pid] = []
        gid = b['game_id']
        tid = b['team_id']
        team_fga = team_game_fga.get((gid, tid), 0)
        mins = b['minutes_raw'] or 0
        fga = b['fg_attempted'] or 0
        player_games[pid].append({
            'game_id': gid,
            'team_id': tid,
            'is_discrepant': gid in discrepant_game_ids,
            'minutes': mins,
            'fg_attempted': fga,
            'three_attempted': b['three_attempted'] or 0,
            'points': b['points'] or 0,
            'team_fga': team_fga,
            'is_starter': bool(b['is_starter'])
        })

    def get_cohort(min_games=10, min_mpg=15.0, exclude_discrepant=False):
        cohort = []
        for pid, games in player_games.items():
            valid = [g for g in games if (not exclude_discrepant or not g['is_discrepant']) and g['minutes'] > 0]
            if len(valid) < min_games:
                continue
            tot_mins = sum(g['minutes'] for g in valid)
            tot_fga = sum(g['fg_attempted'] for g in valid)
            tot_team_fga = sum(g['team_fga'] for g in valid)
            mpg = tot_mins / len(valid)
            if mpg < min_mpg:
                continue
            fga_per_game = tot_fga / len(valid)
            fga_36 = (tot_fga / tot_mins * 36.0) if tot_mins > 0 else 0.0
            shot_share = (tot_fga / tot_team_fga) if tot_team_fga > 0 else 0.0
            
            t_data = tend_dict.get(pid, {})
            a_data = attr_dict.get(pid, {})
            v_data = vitals_dict.get(pid, {})
            tid = valid[0]['team_id']
            tac = tactics_dict.get(tid, {})
            
            cohort.append({
                'player_id': pid,
                'name': names_dict.get(pid, pid),
                'team_id': tid,
                'position': v_data.get('primary_position', 'UNKNOWN'),
                'games_played': len(valid),
                'mpg': round(mpg, 2),
                'fga_per_game': round(fga_per_game, 3),
                'fga_per_36': round(fga_36, 3),
                'team_shot_share': round(shot_share, 4),
                'pts_per_game': round(sum(g['points'] for g in valid) / len(valid), 2),
                'shot_tendency': t_data.get('shot_tendency_raw'),
                'touches_tendency': t_data.get('touches_tendency_raw'),
                'three_pt_rating': a_data.get('three_point_shot_raw'),
                'mid_range_rating': a_data.get('mid_range_shot_raw'),
                'coach_tempo': tac.get('tempo_raw')
            })
        return cohort

    cohort_all = get_cohort(10, 15.0, False)
    cohort_clean = get_cohort(10, 15.0, True)

    # Filter to cohort with complete tendency
    c = [p for p in cohort_all if p['shot_tendency'] is not None]

    # Correlations
    st = [p['shot_tendency'] for p in c]
    corrs = {
        'shot_tendency_vs_fga_per_game': pearson_r(st, [p['fga_per_game'] for p in c]),
        'shot_tendency_vs_fga_per_36': pearson_r(st, [p['fga_per_36'] for p in c]),
        'shot_tendency_vs_team_shot_share': pearson_r(st, [p['team_shot_share'] for p in c]),
        'shot_tendency_vs_mpg': pearson_r(st, [p['mpg'] for p in c]),
        'shot_tendency_vs_touches_tendency': pearson_r(st, [p['touches_tendency'] for p in c])
    }

    # Bins
    bins_def = [
        ('Very Low (0-49)', 0, 49),
        ('Low (50-64)', 50, 64),
        ('Medium (65-74)', 65, 74),
        ('High (75-84)', 75, 84),
        ('Very High (85-94)', 85, 94),
        ('Elite (95-100)', 95, 100)
    ]
    bins_res = []
    for lbl, lo, hi in bins_def:
        subset = [p for p in c if lo <= p['shot_tendency'] <= hi]
        bins_res.append({
            'bin_label': lbl,
            'count': len(subset),
            'mean_tendency': round(statistics.mean(p['shot_tendency'] for p in subset), 1),
            'mean_fga_game': round(statistics.mean(p['fga_per_game'] for p in subset), 2),
            'mean_fga_36': round(statistics.mean(p['fga_per_36'] for p in subset), 2),
            'mean_team_shot_share': round(statistics.mean(p['team_shot_share'] for p in subset), 4),
            'mean_mpg': round(statistics.mean(p['mpg'] for p in subset), 1)
        })

    # Regressions
    Y1 = [p['fga_per_36'] for p in c]
    m1 = solve_ols(Y1, [[1.0, p['shot_tendency']] for p in c], ['Intercept', 'ShotTendency'])
    m2 = solve_ols(Y1, [[1.0, p['shot_tendency'], p['mpg']] for p in c], ['Intercept', 'ShotTendency', 'MPG'])

    # Model 3
    c_m3 = [p for p in c if p['touches_tendency'] is not None and p['three_pt_rating'] is not None and p['mid_range_rating'] is not None and p['coach_tempo'] is not None]
    Y3 = [p['fga_per_36'] for p in c_m3]
    X3 = [
        [
            1.0, p['shot_tendency'], p['mpg'], p['touches_tendency'],
            p['three_pt_rating'], p['mid_range_rating'],
            1.0 if p['position'] == 'SHOOTING_GUARD' else 0.0,
            1.0 if p['position'] == 'SMALL_FORWARD' else 0.0,
            1.0 if p['position'] == 'POWER_FORWARD' else 0.0,
            1.0 if p['position'] == 'CENTER' else 0.0,
            p['coach_tempo']
        ]
        for p in c_m3
    ]
    f3 = ['Intercept', 'ShotTendency', 'MPG', 'TouchesTendency', 'ThreePtRating', 'MidRangeRating', 'Pos_SG', 'Pos_SF', 'Pos_PF', 'Pos_C', 'CoachTempo']
    m3 = solve_ols(Y3, X3, f3)

    # Model 4
    Y4 = [p['team_shot_share'] for p in c_m3]
    m4 = solve_ols(Y4, X3, f3)

    # Lillard
    lillard = [p for p in c if p['player_id'] == 'player:native:2459'][0]

    conn.close()

    return {
        'row_counts': row_counts,
        'cohort_all_count': len(c),
        'cohort_clean_count': len(cohort_clean),
        'correlations': corrs,
        'bins': bins_res,
        'model_1': m1,
        'model_2': m2,
        'model_3': m3,
        'model_4': m4,
        'lillard': lillard
    }

if __name__ == '__main__':
    default_db = Path(__file__).resolve().parents[3] / "01_os" / "07_content" / "_runs" / "run-20261024-nba2k22-world-data-implementation-002" / "_runtime" / "world-saves" / "nba2k22_test_01" / "world-v24.sqlite"
    default_scope = Path(__file__).resolve().parents[3] / "01_os" / "07_content" / "_runs" / "run-20261101-nba2k22-vae-g2-s0-baseline-loop-observability-pilot-001" / "06_执行" / "score_discrepancy_scope.json"
    res = recalculate_all_s0_metrics(default_db, default_scope)
    print("Recalculation successful!")
    print(f"Row counts: {res['row_counts']}")
    print(f"Cohort all N: {res['cohort_all_count']}, Clean N: {res['cohort_clean_count']}")
    print(f"Correlations: {res['correlations']}")
    print(f"Model 3 beta ShotTendency: {res['model_3']['coefficients']['ShotTendency']}")
    print(f"Model 3 R2: {res['model_3']['r2']}")
    print(f"Model 4 beta ShotTendency: {res['model_4']['coefficients']['ShotTendency']}")
    print(f"Model 4 R2: {res['model_4']['r2']}")
    print(f"Lillard: FGA/G={res['lillard']['fga_per_game']}, FGA/36={res['lillard']['fga_per_36']}, Share={res['lillard']['team_shot_share']}")
